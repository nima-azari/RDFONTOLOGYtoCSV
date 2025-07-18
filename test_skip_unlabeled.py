#!/usr/bin/env python3
"""
Test script for the skip_unlabeled feature.

This script tests the new skip_unlabeled functionality to ensure
it correctly filters out nodes without RDFS/SKOS labels.
"""

from rdf_to_csv_converter import RDFToCSVConverter
from pathlib import Path

def create_test_ttl():
    """Create a test TTL file with mixed labeled and unlabeled nodes."""
    test_content = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix ex: <http://example.org/> .

# Node with SKOS label (should be included)
ex:LabeledConcept rdf:type ex:Concept ;
    skos:prefLabel "Labeled Concept"@en ;
    skos:definition "A concept with proper labeling"@en .

# Node with RDFS label (should be included)
ex:RDFSConcept rdf:type ex:Concept ;
    rdfs:label "RDFS Concept"@en .

# Node without any label (should be skipped when skip_unlabeled=True)
ex:UnlabeledConcept rdf:type ex:Concept .

# Connections between nodes
ex:LabeledConcept ex:relatesTo ex:RDFSConcept .
ex:RDFSConcept ex:relatesTo ex:UnlabeledConcept .
ex:UnlabeledConcept ex:derivedFrom ex:LabeledConcept .

# A predicate with a label
ex:relatesTo rdfs:label "relates to"@en .

# A predicate without a label
ex:derivedFrom rdf:type rdf:Property .
"""
    
    test_file = Path("test_labels.ttl")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    return str(test_file)

def test_skip_unlabeled():
    """Test the skip_unlabeled functionality."""
    print("🧪 Testing skip_unlabeled feature")
    print("=" * 40)
    
    # Create test file
    test_file = create_test_ttl()
    print(f"✅ Created test file: {test_file}")
    
    try:
        # Test 1: Convert with all nodes
        print("\n📊 Test 1: Converting with all nodes...")
        converter_all = RDFToCSVConverter(test_file)
        edges_all, nodes_all = converter_all.convert(
            edges_filename="test_all_edges.csv",
            nodes_filename="test_all_nodes.csv"
        )
        stats_all = converter_all.generate_statistics()
        
        # Test 2: Convert skipping unlabeled nodes
        print("📊 Test 2: Converting with skip_unlabeled=True...")
        converter_labeled = RDFToCSVConverter(test_file)
        edges_labeled, nodes_labeled = converter_labeled.convert(
            skip_unlabeled=True,
            edges_filename="test_labeled_edges.csv",
            nodes_filename="test_labeled_nodes.csv"
        )
        stats_labeled = converter_labeled.generate_statistics()
        
        # Compare results
        print(f"\n📈 Results Comparison:")
        print(f"All nodes:")
        print(f"  - Total edges: {stats_all['total_edges']}")
        print(f"  - Total nodes: {stats_all['total_nodes']}")
        print(f"  - SKOS labels: {stats_all.get('skos_labels_used', 0)}")
        print(f"  - RDFS labels: {stats_all.get('rdfs_labels_used', 0)}")
        print(f"  - URI fragments: {stats_all.get('uri_fragments_used', 0)}")
        
        print(f"\nLabeled nodes only:")
        print(f"  - Total edges: {stats_labeled['total_edges']}")
        print(f"  - Total nodes: {stats_labeled['total_nodes']}")
        print(f"  - SKOS labels: {stats_labeled.get('skos_labels_used', 0)}")
        print(f"  - RDFS labels: {stats_labeled.get('rdfs_labels_used', 0)}")
        print(f"  - URI fragments: {stats_labeled.get('uri_fragments_used', 0)}")
        
        # Validate results
        print(f"\n✅ Validation:")
        edges_reduced = stats_all['total_edges'] - stats_labeled['total_edges']
        nodes_reduced = stats_all['total_nodes'] - stats_labeled['total_nodes']
        
        print(f"  - Edges reduced by: {edges_reduced}")
        print(f"  - Nodes reduced by: {nodes_reduced}")
        print(f"  - URI fragments eliminated: {stats_all.get('uri_fragments_used', 0) - stats_labeled.get('uri_fragments_used', 0)}")
        
        if nodes_reduced > 0:
            print("✅ skip_unlabeled feature working correctly!")
        else:
            print("⚠️  Expected some nodes to be filtered out")
        
        print(f"\n📁 Generated files:")
        print(f"  - All nodes: {edges_all}, {nodes_all}")
        print(f"  - Labeled only: {edges_labeled}, {nodes_labeled}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test file
        try:
            Path(test_file).unlink()
            print(f"\n🧹 Cleaned up test file: {test_file}")
        except:
            pass

if __name__ == "__main__":
    test_skip_unlabeled()
