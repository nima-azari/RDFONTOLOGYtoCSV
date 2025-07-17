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
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from urllib.parse import urlparse

import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RDFToCSVConverter:
    """Convert RDF TTL files to CSV format for network visualization."""
    
    def __init__(self, ttl_file_path: str, output_dir: str = None):
        """
        Initialize the converter.
        
        Args:
            ttl_file_path: Path to the input TTL file
            output_dir: Output directory for CSV files (default: same as input file)
        """
        self.ttl_file_path = Path(ttl_file_path)
        self.output_dir = Path(output_dir) if output_dir else self.ttl_file_path.parent
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize RDF graph
        self.graph = Graph()
        
        # Data storage
        self.edges = []
        self.nodes = {}
        self.node_types = defaultdict(set)
        self.predicates_count = defaultdict(int)
        
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
        """Load the TTL file into RDF graph."""
        try:
            logger.info(f"Loading TTL file: {self.ttl_file_path}")
            self.graph.parse(self.ttl_file_path, format='turtle')
            logger.info(f"Successfully loaded {len(self.graph)} triples")
            return True
        except Exception as e:
            logger.error(f"Error loading TTL file: {e}")
            return False
    
    def extract_uri_label(self, uri: URIRef) -> str:
        """Extract a readable label from URI with priority: skos:prefLabel > rdfs:label > URI fragment."""
        # First try to get skos:prefLabel (highest priority)
        for label in self.graph.objects(uri, self.namespaces['skos'].prefLabel):
            if isinstance(label, Literal):
                return str(label)
        
        # Then try rdfs:label
        for label in self.graph.objects(uri, RDFS.label):
            if isinstance(label, Literal):
                return str(label)
        
        # If no label, extract from URI
        uri_str = str(uri)
        
        # Handle common URI patterns
        if '#' in uri_str:
            return uri_str.split('#')[-1]
        elif '/' in uri_str:
            return uri_str.split('/')[-1]
        else:
            return uri_str
    
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
                          filter_predicates: List[str] = None) -> None:
        """
        Extract graph edges and node metadata from RDF graph.
        
        Args:
            include_literals: Whether to include literal values as nodes
            filter_predicates: List of predicates to include (if None, include all)
        """
        logger.info("Extracting graph data...")
        
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
        
        for subject, predicate, obj in self.graph:
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
                obj_label = self.extract_uri_label(obj)
                obj_id = str(obj)
            
            # Extract labels
            subject_label = self.extract_uri_label(subject)
            predicate_label = self.extract_uri_label(predicate)
            
            # Create edge tuple to avoid duplicates
            edge_tuple = (str(subject), obj_id, str(predicate))
            if edge_tuple in processed_edges:
                continue
            processed_edges.add(edge_tuple)
            
            # Add edge
            edge = {
                'source': str(subject),
                'target': obj_id,
                'source_label': subject_label,
                'target_label': obj_label,
                'predicate': str(predicate),
                'predicate_label': predicate_label,
                'edge_type': predicate_label
            }
            self.edges.append(edge)
            
            # Count predicates for statistics
            self.predicates_count[predicate_label] += 1
            
            # Add nodes to metadata
            if str(subject) not in self.nodes:
                subject_type = self.get_node_type(subject)
                self.nodes[str(subject)] = {
                    'id': str(subject),
                    'label': subject_label,
                    'type': subject_type,
                    'color': self.get_node_color_by_type(subject_type),
                    'size': 10  # Default size
                }
                self.node_types[subject_type].add(str(subject))
            
            if obj_id not in self.nodes and not isinstance(obj, Literal):
                obj_type = self.get_node_type(obj) if isinstance(obj, URIRef) else "Literal"
                self.nodes[obj_id] = {
                    'id': obj_id,
                    'label': obj_label,
                    'type': obj_type,
                    'color': self.get_node_color_by_type(obj_type),
                    'size': 10  # Default size
                }
                self.node_types[obj_type].add(obj_id)
        
        logger.info(f"Extracted {len(self.edges)} edges and {len(self.nodes)} nodes")
        
        # Adjust node sizes based on degree (number of connections)
        self._calculate_node_degrees()
    
    def _calculate_node_degrees(self) -> None:
        """Calculate node degrees and adjust sizes accordingly."""
        degree_count = defaultdict(int)
        
        # Count degrees
        for edge in self.edges:
            degree_count[edge['source']] += 1
            degree_count[edge['target']] += 1
        
        # Normalize sizes (between 5 and 50)
        if degree_count:
            max_degree = max(degree_count.values())
            min_degree = min(degree_count.values())
            
            for node_id in self.nodes:
                degree = degree_count.get(node_id, 0)
                if max_degree > min_degree:
                    normalized_size = 5 + (degree - min_degree) / (max_degree - min_degree) * 45
                else:
                    normalized_size = 10
                self.nodes[node_id]['size'] = int(normalized_size)
                self.nodes[node_id]['degree'] = degree
    
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
                                   key=lambda x: x[1], reverse=True)[:10]
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
                edges_filename: str = None,
                nodes_filename: str = None) -> Tuple[str, str]:
        """
        Complete conversion process.
        
        Args:
            include_literals: Whether to include literal values as nodes
            filter_predicates: List of predicates to filter by
            edges_filename: Custom filename for edges CSV
            nodes_filename: Custom filename for nodes CSV
        
        Returns:
            Tuple of (edges_file_path, nodes_file_path)
        """
        if not self.load_ttl_file():
            raise ValueError("Failed to load TTL file")
        
        self.extract_graph_data(include_literals, filter_predicates)
        
        edges_file = self.save_edges_csv(edges_filename)
        nodes_file = self.save_nodes_csv(nodes_filename)
        self.save_statistics()
        
        return edges_file, nodes_file


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Convert RDF TTL files to CSV for network visualization"
    )
    parser.add_argument("ttl_file", help="Path to input TTL file")
    parser.add_argument("-o", "--output-dir", help="Output directory for CSV files")
    parser.add_argument("--include-literals", action="store_true",
                       help="Include literal values as nodes")
    parser.add_argument("--filter-predicates", nargs="+",
                       help="List of predicates to include (e.g., rdf:type rdfs:subClassOf)")
    parser.add_argument("--edges-file", help="Custom filename for edges CSV")
    parser.add_argument("--nodes-file", help="Custom filename for nodes CSV")
    
    args = parser.parse_args()
    
    try:
        converter = RDFToCSVConverter(args.ttl_file, args.output_dir)
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
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
