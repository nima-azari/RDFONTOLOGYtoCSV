#!/usr/bin/env python3
"""
Example usage of the RDF to CSV converter for network visualization.

This script demonstrates how to use the RDFToCSVConverter class
to convert DBpedia or other RDF TTL files to CSV format.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import our converter
sys.path.append(str(Path(__file__).parent))

from rdf_to_csv_converter import RDFToCSVConverter

def example_basic_conversion(ttl_file_path: str):
    """Basic example: Convert entire TTL file to CSV."""
    print("=== Basic Conversion Example ===")
    
    converter = RDFToCSVConverter(ttl_file_path)
    edges_file, nodes_file = converter.convert()
    
    print(f"Generated files:")
    print(f"  Edges: {edges_file}")
    print(f"  Nodes: {nodes_file}")
    
    # Show statistics
    stats = converter.generate_statistics()
    print(f"\nConversion Statistics:")
    print(f"  Total edges: {stats['total_edges']}")
    print(f"  Total nodes: {stats['total_nodes']}")
    print(f"  Node types: {list(stats['node_type_counts'].keys())}")


def example_filtered_conversion(ttl_file_path: str):
    """Example: Convert only specific relationships."""
    print("\n=== Filtered Conversion Example ===")
    
    # Only include type relationships and subclass relationships
    filter_predicates = [
        "rdf:type",
        "rdfs:subClassOf",
        "rdfs:subPropertyOf",
        "owl:equivalentClass"
    ]
    
    converter = RDFToCSVConverter(ttl_file_path)
    edges_file, nodes_file = converter.convert(
        filter_predicates=filter_predicates,
        edges_filename="filtered_edges.csv",
        nodes_filename="filtered_nodes.csv"
    )
    
    print(f"Generated filtered files:")
    print(f"  Edges: {edges_file}")
    print(f"  Nodes: {nodes_file}")
    
    stats = converter.generate_statistics()
    print(f"\nFiltered Statistics:")
    print(f"  Total edges: {stats['total_edges']}")
    print(f"  Total nodes: {stats['total_nodes']}")


def example_dbpedia_subset():
    """Example: Create a sample DBpedia TTL file and convert it."""
    print("\n=== Creating Sample DBpedia Data ===")
    
    # Create a sample DBpedia-style TTL file
    sample_ttl = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix dbo: <http://dbpedia.org/ontology/> .
@prefix dbr: <http://dbpedia.org/resource/> .

# Classes
dbo:Person rdf:type owl:Class ;
    rdfs:label "Person"@en ;
    rdfs:comment "A human being"@en .

dbo:City rdf:type owl:Class ;
    rdfs:label "City"@en ;
    rdfs:comment "A large settlement"@en .

dbo:Country rdf:type owl:Class ;
    rdfs:label "Country"@en ;
    rdfs:comment "A nation state"@en .

# Properties
dbo:birthPlace rdf:type owl:ObjectProperty ;
    rdfs:label "birth place"@en ;
    rdfs:domain dbo:Person ;
    rdfs:range dbo:Place .

dbo:location rdf:type owl:ObjectProperty ;
    rdfs:label "location"@en .

# Instances
dbr:Albert_Einstein rdf:type dbo:Person ;
    rdfs:label "Albert Einstein"@en ;
    dbo:birthPlace dbr:Ulm .

dbr:Ulm rdf:type dbo:City ;
    rdfs:label "Ulm"@en ;
    dbo:location dbr:Germany .

dbr:Germany rdf:type dbo:Country ;
    rdfs:label "Germany"@en .

dbr:Marie_Curie rdf:type dbo:Person ;
    rdfs:label "Marie Curie"@en ;
    dbo:birthPlace dbr:Warsaw .

dbr:Warsaw rdf:type dbo:City ;
    rdfs:label "Warsaw"@en ;
    dbo:location dbr:Poland .

dbr:Poland rdf:type dbo:Country ;
    rdfs:label "Poland"@en .
"""
    
    # Save sample data
    sample_file = Path("sample_dbpedia.ttl")
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_ttl)
    
    print(f"Created sample file: {sample_file}")
    
    # Convert the sample
    converter = RDFToCSVConverter(str(sample_file))
    edges_file, nodes_file = converter.convert(
        edges_filename="sample_edges.csv",
        nodes_filename="sample_nodes.csv"
    )
    
    print(f"Converted sample to:")
    print(f"  Edges: {edges_file}")
    print(f"  Nodes: {nodes_file}")
    
    # Show some sample data
    import pandas as pd
    
    print("\nSample Edges (first 5 rows):")
    edges_df = pd.read_csv(edges_file)
    print(edges_df.head().to_string(index=False))
    
    print("\nSample Nodes (first 5 rows):")
    nodes_df = pd.read_csv(nodes_file)
    print(nodes_df.head().to_string(index=False))


def main():
    """Main demonstration function."""
    print("RDF to CSV Converter - Examples and Usage")
    print("=" * 50)
    
    # Check if a TTL file was provided as argument
    if len(sys.argv) > 1:
        ttl_file = sys.argv[1]
        if Path(ttl_file).exists():
            example_basic_conversion(ttl_file)
            example_filtered_conversion(ttl_file)
        else:
            print(f"Error: File {ttl_file} not found!")
            sys.exit(1)
    else:
        print("No TTL file provided. Creating sample data for demonstration...")
        example_dbpedia_subset()
    
    print("\n=== Usage Instructions ===")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run converter: python rdf_to_csv_converter.py your_file.ttl")
    print("3. Or use programmatically:")
    print("   from rdf_to_csv_converter import RDFToCSVConverter")
    print("   converter = RDFToCSVConverter('your_file.ttl')")
    print("   edges_file, nodes_file = converter.convert()")
    
    print("\n=== Output Files ===")
    print("The converter generates these files:")
    print("1. *_edges.csv - Graph edges (source, target, predicate, labels)")
    print("2. *_nodes.csv - Node metadata (id, label, type, color, size)")
    print("3. *_statistics.txt - Conversion statistics and summary")


if __name__ == "__main__":
    main()
