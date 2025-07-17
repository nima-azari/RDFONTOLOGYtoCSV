# RDF TTL to CSV Converter v1.0.0 Release Notes

## 🎉 First Official Release!

We're excited to announce the first stable release of the RDF TTL to CSV Converter - a powerful tool for transforming RDF Turtle ontology files into CSV format for network visualization.

## 🚀 What's New in v1.0.0

### Core Features
- **Complete RDF to CSV Conversion**: Transform any TTL file into visualization-ready CSV files
- **Dual Output Format**: Generate both graph edges and node metadata files
- **SKOS Support**: Priority-based label extraction (`skos:prefLabel` > `rdfs:label` > URI fragment)
- **Definition Extraction**: Automatic extraction of `skos:definition` for rich node metadata
- **Smart Color Coding**: Automatic color assignment based on node types
- **Degree-based Sizing**: Node sizes calculated from connection degrees

### Visualization Integration
- **Cosmograph**: Direct web-based visualization with live demo links
- **Gephi**: Import-ready CSV files with complete metadata
- **Cytoscape**: Network and attribute file formats
- **Web Libraries**: JSON-ready data for D3.js, vis.js, etc.

### Example Data Included
- **DBpedia Ontology**: 3,807 nodes, 8,454 relationships - perfect for testing
- **IMBOR**: Infrastructure management ontology example
- **NEN2660**: Dutch construction standard ontology
- **Live Demo Links**: Pre-configured Cosmograph visualizations

## 📊 Key Statistics from Example Data

**DBpedia Example Conversion:**
- 3,807 total nodes extracted
- 8,454 relationship edges
- 788 Classes, 1,854 DatatypeProperties, 1,164 ObjectProperties
- Label extraction breakdown available in statistics

## 🛠 Installation & Usage

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Basic conversion
python rdf_to_csv_converter.py your_ontology.ttl

# Advanced usage with filtering
python rdf_to_csv_converter.py ontology.ttl --filter-predicates rdf:type rdfs:subClassOf
```

### Programmatic Usage
```python
from rdf_to_csv_converter import RDFToCSVConverter

converter = RDFToCSVConverter('ontology.ttl')
edges_file, nodes_file = converter.convert()
```

## 🎯 Perfect For

- **Ontology Visualization**: See the structure of large ontologies like DBpedia
- **Semantic Web Research**: Analyze RDF data relationships
- **Knowledge Graph Exploration**: Interactive exploration of linked data
- **Educational Purposes**: Learn about ontological structures visually
- **Data Analysis**: Convert semantic data for network analysis tools

## 📁 File Structure

The release includes:
- `rdf_to_csv_converter.py` - Main conversion tool
- `example_usage.py` - Usage examples and demonstrations
- `requirements.txt` - Python dependencies
- `README.md` - Comprehensive documentation
- `LICENSE` - MIT License
- `ttl_data/` - Example ontologies and converted CSV files
- `cosmograph_links.txt` - Direct visualization links

## 🔗 Live Examples

Try the tool immediately with our pre-converted datasets:

**DBpedia Ontology Visualization:**
[Open in Cosmograph →](https://cosmograph.app/run/?data=https://github.com/nima-azari/RDFONTOLOGYtoCSV/blob/main/ttl_data/sparql_2025-07-17_07-56-39Z_edges.csv&meta=https://github.com/nima-azari/RDFONTOLOGYtoCSV/blob/main/ttl_data/sparql_2025-07-17_07-56-39Z_nodes.csv)

**IMBOR Infrastructure Ontology:**
[Open in Cosmograph →](https://cosmograph.app/run/?data=https://github.com/nima-azari/RDFONTOLOGYtoCSV/blob/main/ttl_data/imbor_edges.csv&meta=https://github.com/nima-azari/RDFONTOLOGYtoCSV/blob/main/ttl_data/imbor_nodes.csv)

## 🐛 Bug Reports & Feature Requests

Please report issues or request features via [GitHub Issues](https://github.com/nima-azari/RDFONTOLOGYtoCSV/issues).

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This tool was created to solve the challenge of visualizing large RDF ontologies for better understanding and analysis. Special thanks to the semantic web community for their valuable ontology standards and tools.

---

**Download**: [Source Code (zip)](../../archive/refs/tags/v1.0.0.zip) | [Source Code (tar.gz)](../../archive/refs/tags/v1.0.0.tar.gz)
