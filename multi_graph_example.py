#!/usr/bin/env python3
"""
Multi-Graph RDF Converter Example

This example demonstrates how to use the RDF to CSV converter with multiple
ontology files to find connections and relationships between different
knowledge graphs.

Author: Assistant
Date: July 2025
"""

import os
from pathlib import Path
from rdf_to_csv_converter import RDFToCSVConverter

def run_multi_graph_example():
    """Demonstrate multi-graph conversion and analysis."""
    
    print("🔗 Multi-Graph RDF to CSV Converter Example")
    print("=" * 50)
    
    # Define paths to example TTL files
    ttl_data_dir = Path("ttl_data")
    
    # Primary graph
    primary_graph = ttl_data_dir / "sparql_2025-07-17_07-56-39Z.ttl"
    
    # Additional graphs to compare
    additional_graphs = []
    
    # Check which additional graphs are available
    potential_graphs = [
        ttl_data_dir / "imbor.ttl",
        ttl_data_dir / "nen2660.ttl"
    ]
    
    for graph_path in potential_graphs:
        if graph_path.exists():
            additional_graphs.append(str(graph_path))
            print(f"✅ Found additional graph: {graph_path.name}")
        else:
            print(f"⚠️  Optional graph not found: {graph_path.name}")
    
    if not primary_graph.exists():
        print(f"❌ Primary graph not found: {primary_graph}")
        print("Please ensure you have TTL files in the ttl_data directory")
        return
    
    print(f"\n📊 Analyzing graphs:")
    print(f"Primary: {primary_graph.name}")
    for graph in additional_graphs:
        print(f"Additional: {Path(graph).name}")
    
    try:
        # Create converter with multiple graphs
        print(f"\n🚀 Creating multi-graph converter...")
        converter = RDFToCSVConverter(
            str(primary_graph), 
            output_dir="output", 
            additional_graphs=additional_graphs
        )
        
        # Convert with specific filters to focus on relationships
        print("🔄 Converting graphs and finding connections...")
        edges_file, nodes_file = converter.convert(
            include_literals=False,
            filter_predicates=[
                'rdf:type', 
                'rdfs:subClassOf', 
                'rdfs:subPropertyOf',
                'owl:equivalentClass',
                'owl:equivalentProperty',
                'skos:exactMatch',
                'skos:closeMatch',
                'skos:relatedMatch'
            ]
        )
        
        # Also create a cleaner version with only labeled nodes
        print("\n🏷️ Creating labeled-only version for cleaner visualization...")
        labeled_edges, labeled_nodes = converter.convert(
            include_literals=False,
            skip_unlabeled=True,
            edges_filename="multi_graph_labeled_edges.csv",
            nodes_filename="multi_graph_labeled_nodes.csv"
        )
        
        # Get comprehensive statistics
        stats = converter.generate_statistics()
        
        print(f"\n📈 Conversion Results:")
        print(f"Total nodes extracted: {stats['total_nodes']}")
        print(f"Total edges extracted: {stats['total_edges']}")
        print(f"Output files:")
        print(f"  📄 Edges: {edges_file}")
        print(f"  📄 Nodes: {nodes_file}")
        
        # Multi-graph analysis
        if len(stats['graph_statistics']) > 1:
            print(f"\n🔗 Multi-Graph Analysis:")
            print(f"Graphs analyzed: {len(stats['graph_statistics'])}")
            
            for graph_name, graph_info in stats['graph_statistics'].items():
                print(f"\n  📊 {graph_name}:")
                print(f"    Triples: {graph_info['triples_count']:,}")
                print(f"    Unique nodes: {len(graph_info.get('nodes', []))}")
                print(f"    Unique predicates: {len(graph_info.get('predicates', []))}")
            
            # Cross-graph connections
            connections = stats['cross_graph_connections']
            if connections:
                print(f"\n🌐 Cross-Graph Connections Found: {len(connections)}")
                
                # Group by connection type
                shared_uri_connections = [c for c in connections if c.get('type') != 'similar_concept']
                similar_concept_connections = [c for c in connections if c.get('type') == 'similar_concept']
                
                if shared_uri_connections:
                    print(f"\n  🔗 Shared URI Connections:")
                    for conn in shared_uri_connections[:5]:  # Show top 5
                        print(f"    {conn['graph1']} ↔ {conn['graph2']}: {conn['connection_strength']} shared elements")
                        if conn.get('shared_nodes'):
                            print(f"      Shared nodes: {len(conn['shared_nodes'])}")
                        if conn.get('shared_predicates'):
                            print(f"      Shared predicates: {len(conn['shared_predicates'])}")
                
                if similar_concept_connections:
                    print(f"\n  🔄 Similar Concepts Across Graphs:")
                    for conn in similar_concept_connections[:5]:  # Show top 5
                        print(f"    '{conn['label']}' appears in {len(conn['graphs'])} graphs")
                        print(f"      Graphs: {', '.join(conn['graphs'])}")
            else:
                print(f"\n❌ No cross-graph connections found")
                print("This could mean:")
                print("  - Graphs are completely independent")
                print("  - Different URI schemes are used")
                print("  - Concepts are expressed differently")
        
        # Label extraction statistics
        label_stats = stats['label_statistics']
        print(f"\n🏷️  Label Extraction Summary:")
        print(f"SKOS prefLabels: {label_stats['skos_preflabels']}")
        print(f"RDFS labels: {label_stats['rdfs_labels']}")
        print(f"URI fragments: {label_stats['uri_fragments']}")
        print(f"SKOS definitions: {label_stats['skos_definitions']}")
        
        # Usage suggestions
        print(f"\n💡 Usage Suggestions:")
        print(f"1. Import {Path(edges_file).name} and {Path(nodes_file).name} into Cosmograph")
        print(f"2. Color nodes by 'graphs' column to see which graph they come from")
        print(f"3. Filter by 'source_graph' in edges to analyze specific graph relationships")
        print(f"4. Look for nodes with multiple graphs to find connection points")
        
        if len(stats['graph_statistics']) > 1:
            print(f"5. Cross-graph connections indicate potential alignment opportunities")
        
        print(f"\n✅ Multi-graph analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        raise

def demonstrate_programmatic_usage():
    """Show how to use the multi-graph converter programmatically."""
    
    print(f"\n🔧 Programmatic Usage Example:")
    print("-" * 40)
    
    code_example = '''
# Multi-graph converter usage
from rdf_to_csv_converter import RDFToCSVConverter

# Create converter with multiple graphs
converter = RDFToCSVConverter(
    'primary_ontology.ttl',
    output_dir='results',
    additional_graphs=[
        'secondary_ontology.ttl',
        'third_ontology.ttl'
    ]
)

# Convert and find connections
edges_file, nodes_file = converter.convert(
    filter_predicates=['rdf:type', 'rdfs:subClassOf', 'owl:equivalentClass']
)

# Analyze results
stats = converter.generate_statistics()
connections = stats['cross_graph_connections']

print(f"Found {len(connections)} cross-graph connections")
for conn in connections:
    if conn.get('type') == 'similar_concept':
        print(f"Similar concept: {conn['label']}")
    else:
        print(f"Shared elements between {conn['graph1']} and {conn['graph2']}")
'''
    
    print(code_example)

if __name__ == "__main__":
    run_multi_graph_example()
    demonstrate_programmatic_usage()
