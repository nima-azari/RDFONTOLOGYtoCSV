#!/usr/bin/env python3
"""
RDF TTL to CSV Converter for Network Visualization

This script converts RDF Turtle (.ttl) ontology files into CSV format
suitable for network visualization tools. It generates two files:
1. Graph edges file (required): Contains source-target relationships
2. Graph metadata file (optional): Contains node properties for styling

Features:
- SKOS prefLabel support with priority over rdfs:label
- Automatic color coding by node type
- Node sizing based on connection degree
- Flexible predicate filtering
- Support for multiple namespaces (RDF, RDFS, OWL, SKOS, DBpedia, etc.)

Requirements:
- rdflib: pip install rdflib
- pandas: pip install pandas

Author: Assistant
Date: July 2025
"""

import argparse
import csv
import logging
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from urllib.parse import urlparse

import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # Fallback progress indicator
    class tqdm:
        def __init__(self, iterable=None, total=None, desc="Processing", **kwargs):
            self.iterable = iterable
            self.total = total or (len(iterable) if iterable else 0)
            self.desc = desc
            self.count = 0
            self.start_time = time.time()
            print(f"🔄 {self.desc}: Starting...")
        
        def __iter__(self):
            for item in self.iterable:
                yield item
                self.update(1)
            self.close()
        
        def update(self, n=1):
            self.count += n
            if self.count % max(1, self.total // 20) == 0 or self.count == self.total:
                elapsed = time.time() - self.start_time
                rate = self.count / elapsed if elapsed > 0 else 0
                percent = (self.count / self.total * 100) if self.total > 0 else 0
                print(f"   Progress: {self.count}/{self.total} ({percent:.1f}%) - {rate:.1f} items/sec")
        
        def close(self):
            elapsed = time.time() - self.start_time
            print(f"✅ {self.desc}: Completed {self.count} items in {elapsed:.1f}s")
        
        def set_description(self, desc):
            self.desc = desc

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RDFToCSVConverter:
    """Convert RDF TTL files to CSV format for network visualization."""
    
    def __init__(self, ttl_file_path: str, output_dir: str = None, additional_graphs: List[str] = None):
        """
        Initialize the converter.
        
        Args:
            ttl_file_path: Path to the primary input TTL file
            output_dir: Output directory for CSV files (default: same as input file)
            additional_graphs: List of additional TTL file paths to merge and compare
        """
        self.ttl_file_path = Path(ttl_file_path)
        self.output_dir = Path(output_dir) if output_dir else self.ttl_file_path.parent
        self.output_dir.mkdir(exist_ok=True)
        
        # Store additional graphs info
        self.additional_graphs = additional_graphs or []
        self.graph_sources = {}  # Track which graph each triple comes from
        
        # Initialize RDF graph
        self.graph = Graph()
        
        # Data storage
        self.edges = []
        self.nodes = {}
        self.node_types = defaultdict(set)
        self.predicates_count = defaultdict(int)
        
        # Multi-graph statistics
        self.graph_statistics = {}
        self.cross_graph_connections = []
        
        # Label statistics
        self.skos_labels_count = 0
        self.rdfs_labels_count = 0
        self.uri_fragments_count = 0
        self.skos_definitions_count = 0
        
        # Common namespaces
        self.namespaces = {
            'rdf': RDF,
            'rdfs': RDFS,
            'owl': OWL,
            'xsd': XSD,
            'skos': Namespace('http://www.w3.org/2004/02/skos/core#'),
            'dbo': Namespace('http://dbpedia.org/ontology/'),
            'dbr': Namespace('http://dbpedia.org/resource/'),
            'foaf': Namespace('http://xmlns.com/foaf/0.1/'),
            'dc': Namespace('http://purl.org/dc/elements/1.1/'),
            'dcterms': Namespace('http://purl.org/dc/terms/'),
        }
    
    def load_ttl_file(self) -> bool:
        """Load the primary TTL file and any additional graphs into RDF graph."""
        try:
            # Load primary graph
            logger.info(f"Loading primary TTL file: {self.ttl_file_path}")
            primary_graph = Graph()
            primary_graph.parse(self.ttl_file_path, format='turtle')
            
            # Track source for each triple in primary graph
            primary_name = self.ttl_file_path.stem
            for triple in primary_graph:
                self.graph_sources[triple] = primary_name
            
            # Add to main graph
            self.graph += primary_graph
            self.graph_statistics[primary_name] = {
                'file_path': str(self.ttl_file_path),
                'triples_count': len(primary_graph),
                'nodes': set(),
                'predicates': set()
            }
            
            logger.info(f"Primary graph loaded: {len(primary_graph)} triples")
            
            # Load additional graphs
            for additional_path in self.additional_graphs:
                additional_path = Path(additional_path)
                logger.info(f"Loading additional graph: {additional_path}")
                
                additional_graph = Graph()
                additional_graph.parse(additional_path, format='turtle')
                
                # Track source for each triple
                graph_name = additional_path.stem
                for triple in additional_graph:
                    self.graph_sources[triple] = graph_name
                
                # Add to main graph
                self.graph += additional_graph
                self.graph_statistics[graph_name] = {
                    'file_path': str(additional_path),
                    'triples_count': len(additional_graph),
                    'nodes': set(),
                    'predicates': set()
                }
                
                logger.info(f"Additional graph '{graph_name}' loaded: {len(additional_graph)} triples")
            
            logger.info(f"Total graphs loaded: {len(self.graph_statistics)}")
            logger.info(f"Combined graph size: {len(self.graph)} triples")
            return True
            
        except Exception as e:
            logger.error(f"Error loading TTL files: {e}")
            return False
    
    def extract_uri_label(self, uri: URIRef, skip_unlabeled: bool = False) -> str:
        """Extract a readable label from URI with priority: skos:prefLabel > rdfs:label > URI fragment.
        
        Args:
            uri: The URI to extract label from
            skip_unlabeled: If True, return None for URIs without RDFS/SKOS labels
        
        Returns:
            Label string or None if skip_unlabeled=True and no RDFS/SKOS label found
        """
        # First try to get skos:prefLabel (highest priority)
        for label in self.graph.objects(uri, self.namespaces['skos'].prefLabel):
            if isinstance(label, Literal):
                self.skos_labels_count += 1
                return str(label)
        
        # Then try rdfs:label
        for label in self.graph.objects(uri, RDFS.label):
            if isinstance(label, Literal):
                self.rdfs_labels_count += 1
                return str(label)
        
        # If skip_unlabeled is True and no RDFS/SKOS label found, return None
        if skip_unlabeled:
            return None
        
        # If no label, extract from URI
        self.uri_fragments_count += 1
        uri_str = str(uri)
        
        # Handle common URI patterns
        if '#' in uri_str:
            return uri_str.split('#')[-1]
        elif '/' in uri_str:
            return uri_str.split('/')[-1]
        else:
            return uri_str
    
    def extract_uri_definition(self, uri: URIRef) -> str:
        """Extract SKOS definition for a URI."""
        # Try to get skos:definition
        for definition in self.graph.objects(uri, self.namespaces['skos'].definition):
            if isinstance(definition, Literal):
                self.skos_definitions_count += 1
                return str(definition)
        return ""
    
    def find_cross_graph_connections(self) -> None:
        """Find connections between different graphs based on shared URIs and similar concepts."""
        if len(self.graph_statistics) <= 1:
            return
        
        logger.info("Finding cross-graph connections...")
        
        # Collect nodes from each graph
        for graph_name in self.graph_statistics:
            self.graph_statistics[graph_name]['nodes'] = set()
            self.graph_statistics[graph_name]['predicates'] = set()
        
        # Categorize nodes and predicates by source graph
        for triple in self.graph:
            subject, predicate, obj = triple
            source_graph = self.graph_sources[triple]
            
            # Add nodes to graph statistics
            if isinstance(subject, URIRef):
                self.graph_statistics[source_graph]['nodes'].add(subject)
            if isinstance(obj, URIRef):
                self.graph_statistics[source_graph]['nodes'].add(obj)
            
            # Add predicates
            self.graph_statistics[source_graph]['predicates'].add(predicate)
        
        # Find shared URIs between graphs
        graph_names = list(self.graph_statistics.keys())
        for i, graph1 in enumerate(graph_names):
            for graph2 in graph_names[i+1:]:
                shared_nodes = (self.graph_statistics[graph1]['nodes'] & 
                               self.graph_statistics[graph2]['nodes'])
                shared_predicates = (self.graph_statistics[graph1]['predicates'] & 
                                   self.graph_statistics[graph2]['predicates'])
                
                if shared_nodes or shared_predicates:
                    connection = {
                        'graph1': graph1,
                        'graph2': graph2,
                        'shared_nodes': list(shared_nodes),
                        'shared_predicates': list(shared_predicates),
                        'connection_strength': len(shared_nodes) + len(shared_predicates)
                    }
                    self.cross_graph_connections.append(connection)
                    
                    logger.info(f"Found {len(shared_nodes)} shared nodes and {len(shared_predicates)} shared predicates between '{graph1}' and '{graph2}'")
        
        # Find similar concepts (same labels, different URIs)
        self._find_similar_concepts()
    
    def _find_similar_concepts(self) -> None:
        """Find concepts with similar labels across different graphs."""
        logger.info("Finding similar concepts across graphs...")
        
        # Group nodes by their labels
        label_groups = defaultdict(list)
        all_nodes = set().union(*[stats['nodes'] for stats in self.graph_statistics.values()])
        
        print(f"🔍 Analyzing {len(all_nodes)} unique nodes for similar concepts...")
        
        # Use progress bar for label extraction
        with tqdm(all_nodes, desc="Extracting labels", unit="nodes") as pbar:
            for node_uri in pbar:
                label = self.extract_uri_label(node_uri)
                if label and len(label) > 2:  # Ignore very short labels
                    label_groups[label.lower()].append(node_uri)
        
        logger.info(f"Found {len(label_groups)} unique labels")
        
        # Find labels that appear in multiple graphs
        similar_concepts_found = 0
        with tqdm(label_groups.items(), desc="Finding cross-graph concepts", unit="labels") as pbar:
            for label, nodes in pbar:
                if len(nodes) > 1:
                    # Check if nodes come from different graphs
                    node_sources = []
                    for node in nodes:
                        for triple in self.graph:
                            if (triple[0] == node or triple[2] == node) and triple in self.graph_sources:
                                source = self.graph_sources[triple]
                                if source not in node_sources:
                                    node_sources.append(source)
                                break
                    
                    if len(node_sources) > 1:
                        # Add as potential cross-graph connection
                        connection = {
                            'type': 'similar_concept',
                            'label': label,
                            'nodes': [str(node) for node in nodes],
                            'graphs': node_sources,
                            'connection_strength': len(nodes)
                        }
                        self.cross_graph_connections.append(connection)
                        similar_concepts_found += 1
                        
                        if similar_concepts_found <= 5:  # Log first few for feedback
                            logger.info(f"Similar concept found: '{label}' in graphs {node_sources}")
        
        logger.info(f"Found {similar_concepts_found} similar concepts across different graphs")
    
    def get_node_type(self, node: URIRef) -> str:
        """Get the type of a node."""
        types = list(self.graph.objects(node, RDF.type))
        if types:
            # Get the most specific type
            type_uri = types[0]
            return self.extract_uri_label(type_uri)
        return "Unknown"
    
    def get_node_color_by_type(self, node_type: str) -> str:
        """Assign colors based on node type."""
        color_map = {
            'Class': '#FF6B6B',
            'Property': '#4ECDC4',
            'Individual': '#45B7D1',
            'Ontology': '#96CEB4',
            'Concept': '#FFEAA7',
            'Person': '#DDA0DD',
            'Place': '#98D8C8',
            'Organization': '#F7DC6F',
            'Event': '#BB8FCE',
            'Thing': '#85C1E9',
            'Unknown': '#BDC3C7'
        }
        return color_map.get(node_type, '#BDC3C7')
    
    def extract_graph_data(self, include_literals: bool = False, 
                          filter_predicates: List[str] = None,
                          skip_unlabeled: bool = False) -> None:
        """
        Extract graph edges and node metadata from RDF graph.
        
        Args:
            include_literals: Whether to include literal values as nodes
            filter_predicates: List of predicates to include (if None, include all)
            skip_unlabeled: If True, skip nodes without RDFS/SKOS labels
        """
        logger.info("Extracting graph data...")
        
        # Find cross-graph connections if multiple graphs are loaded
        if self.additional_graphs:
            self.find_cross_graph_connections()
        
        # Convert filter predicates to URIRefs
        filter_uris = set()
        if filter_predicates:
            for pred in filter_predicates:
                if pred.startswith('http'):
                    filter_uris.add(URIRef(pred))
                else:
                    # Try to resolve with known namespaces
                    for ns_prefix, ns_uri in self.namespaces.items():
                        if pred.startswith(f"{ns_prefix}:"):
                            pred_local = pred.split(':', 1)[1]
                            filter_uris.add(ns_uri[pred_local])
                            break
        
        processed_edges = set()
        total_triples = len(self.graph)
        
        print(f"🔄 Processing {total_triples:,} triples...")
        
        with tqdm(self.graph, desc="Processing triples", unit="triples", total=total_triples) as pbar:
            for subject, predicate, obj in pbar:
                # Skip if filtering predicates and this predicate is not included
                if filter_uris and predicate not in filter_uris:
                    continue
                
                # Skip blank nodes unless specifically handling them
                if isinstance(subject, BNode) or isinstance(obj, BNode):
                    continue
                
                # Handle literals
                if isinstance(obj, Literal):
                    if not include_literals:
                        continue
                    # Create a simplified literal node
                    obj_label = f'"{str(obj)[:50]}..."' if len(str(obj)) > 50 else f'"{str(obj)}"'
                    obj_id = f"literal_{hash(str(obj))}"
                else:
                    obj_label = self.extract_uri_label(obj, skip_unlabeled)
                    if skip_unlabeled and obj_label is None:
                        continue  # Skip this edge if object has no RDFS/SKOS label
                    obj_id = str(obj)
                
                # Extract labels
                subject_label = self.extract_uri_label(subject, skip_unlabeled)
                if skip_unlabeled and subject_label is None:
                    continue  # Skip this edge if subject has no RDFS/SKOS label
                
                predicate_label = self.extract_uri_label(predicate, skip_unlabeled)
                if skip_unlabeled and predicate_label is None:
                    continue  # Skip this edge if predicate has no RDFS/SKOS label
                
                # Create edge tuple to avoid duplicates
                edge_tuple = (str(subject), obj_id, str(predicate))
                if edge_tuple in processed_edges:
                    continue
                processed_edges.add(edge_tuple)
                
                # Add edge
                source_graph = self.graph_sources.get((subject, predicate, obj), 'unknown')
                edge = {
                    'source': str(subject),
                    'target': obj_id,
                    'source_label': subject_label,
                    'target_label': obj_label,
                    'predicate': str(predicate),
                    'predicate_label': predicate_label,
                    'edge_type': predicate_label,
                    'source_graph': source_graph
                }
                self.edges.append(edge)
                
                # Count predicates for statistics
                self.predicates_count[predicate_label] += 1
                
                # Add nodes to metadata
                if str(subject) not in self.nodes:
                    subject_type = self.get_node_type(subject)
                    subject_definition = self.extract_uri_definition(subject)
                    # Find which graphs contain this node
                    subject_graphs = [graph for graph, stats in self.graph_statistics.items() 
                                    if subject in stats.get('nodes', set())]
                    self.nodes[str(subject)] = {
                        'id': str(subject),
                        'label': subject_label,
                        'type': subject_type,
                        'definition': subject_definition,
                        'color': self.get_node_color_by_type(subject_type),
                        'size': 10,  # Default size
                        'graphs': ','.join(subject_graphs) if subject_graphs else source_graph
                    }
                    self.node_types[subject_type].add(str(subject))
                
                if obj_id not in self.nodes and not isinstance(obj, Literal):
                    obj_type = self.get_node_type(obj) if isinstance(obj, URIRef) else "Literal"
                    obj_definition = self.extract_uri_definition(obj) if isinstance(obj, URIRef) else ""
                    # Find which graphs contain this node
                    obj_graphs = [graph for graph, stats in self.graph_statistics.items() 
                                if isinstance(obj, URIRef) and obj in stats.get('nodes', set())]
                    self.nodes[obj_id] = {
                        'id': obj_id,
                        'label': obj_label,
                        'type': obj_type,
                        'definition': obj_definition,
                        'color': self.get_node_color_by_type(obj_type),
                        'size': 10,  # Default size
                        'graphs': ','.join(obj_graphs) if obj_graphs else source_graph
                    }
                    self.node_types[obj_type].add(obj_id)
                
                # Update progress description periodically
                if len(self.edges) % 1000 == 0:
                    pbar.set_description(f"Processing triples (Found {len(self.edges)} edges, {len(self.nodes)} nodes)")
        
        logger.info(f"Extracted {len(self.edges)} edges and {len(self.nodes)} nodes")
        
        # Adjust node sizes based on degree (number of connections)
        self._calculate_node_degrees()
    
    def _calculate_node_degrees(self) -> None:
        """Calculate node degrees and adjust sizes accordingly."""
        print("📊 Calculating node degrees and setting sizes...")
        
        try:
            degree_count = defaultdict(int)
            
            # Count degrees
            for edge in tqdm(self.edges, desc="Counting node degrees", unit="edges"):
                degree_count[edge['source']] += 1
                degree_count[edge['target']] += 1
            
            # Normalize sizes (between 5 and 50)
            if degree_count:
                max_degree = max(degree_count.values())
                min_degree = min(degree_count.values())
                
                for node_id in tqdm(self.nodes, desc="Setting node sizes", unit="nodes"):
                    degree = degree_count.get(node_id, 0)
                    if max_degree > min_degree:
                        normalized_size = 5 + (degree - min_degree) / (max_degree - min_degree) * 45
                    else:
                        normalized_size = 10
                    self.nodes[node_id]['size'] = int(normalized_size)
                    self.nodes[node_id]['degree'] = degree
                
                print(f"✅ Calculated degrees for {len(self.nodes):,} nodes")
                print(f"   Min degree: {min_degree}, Max degree: {max_degree}")
            else:
                print("⚠️  No degrees to calculate (no edges found)")
        except Exception as e:
            print(f"❌ Error calculating degrees: {e}")
            # Set defaults if calculation fails
            for node_id in self.nodes:
                self.nodes[node_id]['size'] = 10
                self.nodes[node_id]['degree'] = 0
    
    def save_edges_csv(self, filename: str = None) -> str:
        """Save edges to CSV file."""
        if not filename:
            filename = f"{self.ttl_file_path.stem}_edges.csv"
        
        filepath = self.output_dir / filename
        
        logger.info(f"Saving edges to: {filepath}")
        
        df = pd.DataFrame(self.edges)
        df.to_csv(filepath, index=False)
        
        logger.info(f"Saved {len(self.edges)} edges to {filepath}")
        return str(filepath)
    
    def save_nodes_csv(self, filename: str = None) -> str:
        """Save node metadata to CSV file."""
        if not filename:
            filename = f"{self.ttl_file_path.stem}_nodes.csv"
        
        filepath = self.output_dir / filename
        
        logger.info(f"Saving node metadata to: {filepath}")
        
        nodes_list = list(self.nodes.values())
        df = pd.DataFrame(nodes_list)
        df.to_csv(filepath, index=False)
        
        logger.info(f"Saved {len(nodes_list)} nodes to {filepath}")
        return str(filepath)
    
    def generate_statistics(self) -> Dict:
        """Generate statistics about the converted graph."""
        stats = {
            'total_triples': len(self.graph),
            'total_edges': len(self.edges),
            'total_nodes': len(self.nodes),
            'node_types': dict(self.node_types),
            'node_type_counts': {k: len(v) for k, v in self.node_types.items()},
            'predicate_counts': dict(self.predicates_count),
            'top_predicates': sorted(self.predicates_count.items(), 
                                   key=lambda x: x[1], reverse=True)[:10],
            'label_statistics': {
                'skos_preflabels': self.skos_labels_count,
                'rdfs_labels': self.rdfs_labels_count,
                'uri_fragments': self.uri_fragments_count,
                'skos_definitions': self.skos_definitions_count,
                'total_labels': self.skos_labels_count + self.rdfs_labels_count + self.uri_fragments_count
            },
            'graph_statistics': self.graph_statistics,
            'cross_graph_connections': self.cross_graph_connections
        }
        return stats
    
    def save_statistics(self, filename: str = None) -> str:
        """Save statistics to a text file."""
        if not filename:
            filename = f"{self.ttl_file_path.stem}_statistics.txt"
        
        filepath = self.output_dir / filename
        stats = self.generate_statistics()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("RDF to CSV Conversion Statistics\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Source file: {self.ttl_file_path}\n")
            f.write(f"Total RDF triples: {stats['total_triples']}\n")
            f.write(f"Extracted edges: {stats['total_edges']}\n")
            f.write(f"Extracted nodes: {stats['total_nodes']}\n\n")
            
            # Multi-graph statistics
            if len(stats['graph_statistics']) > 1:
                f.write("Multi-Graph Analysis:\n")
                f.write("-" * 25 + "\n")
                f.write(f"Number of graphs: {len(stats['graph_statistics'])}\n")
                for graph_name, graph_stats in stats['graph_statistics'].items():
                    f.write(f"  {graph_name}: {graph_stats['triples_count']} triples, {len(graph_stats.get('nodes', []))} nodes\n")
                
                f.write(f"\nCross-Graph Connections: {len(stats['cross_graph_connections'])}\n")
                for i, connection in enumerate(stats['cross_graph_connections'][:10]):  # Show top 10
                    if connection.get('type') == 'similar_concept':
                        f.write(f"  {i+1}. Similar concept '{connection['label']}' across {len(connection['graphs'])} graphs\n")
                    else:
                        f.write(f"  {i+1}. {connection['graph1']} ↔ {connection['graph2']}: {connection['connection_strength']} shared elements\n")
                f.write("\n")
            
            f.write("Label Extraction Statistics:\n")
            f.write("-" * 30 + "\n")
            f.write(f"SKOS prefLabels: {stats['label_statistics']['skos_preflabels']}\n")
            f.write(f"RDFS labels: {stats['label_statistics']['rdfs_labels']}\n")
            f.write(f"URI fragments: {stats['label_statistics']['uri_fragments']}\n")
            f.write(f"SKOS definitions: {stats['label_statistics']['skos_definitions']}\n")
            f.write(f"Total labels: {stats['label_statistics']['total_labels']}\n\n")
            
            f.write("Node Types:\n")
            f.write("-" * 20 + "\n")
            for node_type, count in stats['node_type_counts'].items():
                f.write(f"{node_type}: {count}\n")
            
            f.write("\nTop 10 Predicates:\n")
            f.write("-" * 20 + "\n")
            for predicate, count in stats['top_predicates']:
                f.write(f"{predicate}: {count}\n")
        
        logger.info(f"Statistics saved to: {filepath}")
        return str(filepath)
    
    def convert(self, include_literals: bool = False, 
                filter_predicates: List[str] = None,
                skip_unlabeled: bool = True,
                edges_filename: str = None,
                nodes_filename: str = None) -> Tuple[str, str]:
        """
        Complete conversion process.
        
        Args:
            include_literals: Whether to include literal values as nodes
            filter_predicates: List of predicates to filter by
            skip_unlabeled: If True, skip nodes without RDFS/SKOS labels
            edges_filename: Custom filename for edges CSV
            nodes_filename: Custom filename for nodes CSV
        
        Returns:
            Tuple of (edges_file_path, nodes_file_path)
        """
        if not self.load_ttl_file():
            raise ValueError("Failed to load TTL file")
        
        self.extract_graph_data(include_literals, filter_predicates, skip_unlabeled)
        
        edges_file = self.save_edges_csv(edges_filename)
        nodes_file = self.save_nodes_csv(nodes_filename)
        self.save_statistics()
        
        return edges_file, nodes_file


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Convert RDF TTL files to CSV for network visualization"
    )
    parser.add_argument("ttl_file", help="Path to primary input TTL file")
    parser.add_argument("--additional-graphs", nargs="+", 
                       help="Additional TTL files to merge and find connections with")
    parser.add_argument("-o", "--output-dir", help="Output directory for CSV files")
    parser.add_argument("--include-literals", action="store_true",
                       help="Include literal values as nodes")
    parser.add_argument("--filter-predicates", nargs="+",
                       help="List of predicates to include (e.g., rdf:type rdfs:subClassOf)")
    parser.add_argument("--edges-file", help="Custom filename for edges CSV")
    parser.add_argument("--nodes-file", help="Custom filename for nodes CSV")
    
    args = parser.parse_args()
    
    try:
        converter = RDFToCSVConverter(args.ttl_file, args.output_dir, args.additional_graphs)
        edges_file, nodes_file = converter.convert(
            include_literals=args.include_literals,
            filter_predicates=args.filter_predicates,
            edges_filename=args.edges_file,
            nodes_filename=args.nodes_file
        )
        
        print(f"Conversion completed successfully!")
        print(f"Edges file: {edges_file}")
        print(f"Nodes file: {nodes_file}")
        
        # Print statistics
        stats = converter.generate_statistics()
        print(f"\nStatistics:")
        print(f"Total edges: {stats['total_edges']}")
        print(f"Total nodes: {stats['total_nodes']}")
        print(f"Node types: {len(stats['node_type_counts'])}")
        
        # Multi-graph statistics
        if len(stats['graph_statistics']) > 1:
            print(f"\nMulti-Graph Analysis:")
            print(f"Graphs loaded: {len(stats['graph_statistics'])}")
            for graph_name, graph_stats in stats['graph_statistics'].items():
                print(f"  {graph_name}: {graph_stats['triples_count']} triples")
            print(f"Cross-graph connections found: {len(stats['cross_graph_connections'])}")
        
        print(f"\nLabel Extraction:")
        print(f"SKOS prefLabels: {stats['label_statistics']['skos_preflabels']}")
        print(f"RDFS labels: {stats['label_statistics']['rdfs_labels']}")
        print(f"URI fragments: {stats['label_statistics']['uri_fragments']}")
        print(f"SKOS definitions: {stats['label_statistics']['skos_definitions']}")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
