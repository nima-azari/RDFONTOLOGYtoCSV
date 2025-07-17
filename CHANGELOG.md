# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-17

### Added
- **RDF TTL to CSV Converter**: Complete conversion tool for transforming RDF Turtle files into network visualization formats
- **SKOS Support**: Priority-based label extraction with support for `skos:prefLabel` over `rdfs:label`
- **Definition Extraction**: Automatic extraction of `skos:definition` for enhanced node metadata
- **Multi-format Output**: 
  - Graph edges CSV (source-target relationships)
  - Node metadata CSV (labels, types, colors, sizes, definitions)
  - Statistics file with conversion summary
- **Intelligent Color Coding**: Automatic color assignment based on node types (Classes, Properties, etc.)
- **Size Scaling**: Node sizes based on connection degree for better visualization
- **Flexible Filtering**: Support for predicate filtering to focus on specific relationship types
- **Comprehensive Documentation**: Full README with examples, use cases, and visualization tool integration
- **Example Data**: Complete DBpedia ontology example with 8,454 edges and 3,807 nodes
- **Cosmograph Integration**: Pre-configured visualization links for immediate use
- **Command Line Interface**: Full CLI support with multiple options
- **Programmatic API**: Python class interface for integration into other projects

### Features
- Support for multiple RDF namespaces (RDF, RDFS, OWL, SKOS, DBpedia, FOAF, Dublin Core)
- Label extraction statistics (SKOS prefLabels, RDFS labels, URI fragments, definitions)
- Automatic duplicate edge detection and removal
- Configurable output directories and filenames
- Comprehensive error handling and logging
- Cross-platform compatibility (Windows, macOS, Linux)

### Example Datasets
- **DBpedia Ontology**: 3,807 nodes, 8,454 relationships
- **IMBOR**: Infrastructure management ontology
- **NEN2660**: Dutch construction standard ontology

### Visualization Support
- **Gephi**: Direct CSV import with styling metadata
- **Cytoscape**: Network and attribute file formats
- **Cosmograph**: Web-based visualization with live demo links
- **D3.js/vis.js**: JSON-ready data structures

### Technical Specifications
- **Python 3.7+** compatible
- **Dependencies**: rdflib, pandas
- **Input Formats**: Turtle (.ttl), RDF/XML, N-Triples
- **Output Formats**: CSV, TSV, SSV
- **Memory Efficient**: Optimized for large ontologies
- **Performance**: Handles millions of triples

## [Unreleased]

### Planned
- Support for additional RDF serialization formats (JSON-LD, N-Quads)
- Multi-language label support
- Custom color scheme configuration
- Interactive web interface
- Batch processing capabilities
