# RDF TTL to CSV Converter for Network Visualization

This tool converts RDF Turtle (.ttl) ontology files (like DBpedia) into CSV format suitable for network visualization tools such as Gephi, Cytoscape, or web-based visualization libraries.

## Features

- **Graph Edges**: Extracts subject-predicate-object relationships as network edges
- **Node Metadata**: Generates node properties including labels, types, colors, and sizes
- **Flexible Filtering**: Option to filter by specific predicates or relationship types
- **Statistics**: Provides detailed conversion statistics and summaries
- **Color Coding**: Automatic color assignment based on node types
- **Size Scaling**: Node sizes based on degree (number of connections)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- `rdflib>=6.0.0` - For parsing RDF/TTL files
- `pandas>=1.3.0` - For CSV generation and data manipulation

## Usage

### Command Line Usage

```bash
# Basic conversion
python rdf_to_csv_converter.py input_file.ttl

# With output directory
python rdf_to_csv_converter.py input_file.ttl -o output_directory

# Include literal values as nodes
python rdf_to_csv_converter.py input_file.ttl --include-literals

# Filter specific predicates
python rdf_to_csv_converter.py input_file.ttl --filter-predicates rdf:type rdfs:subClassOf

# Custom output filenames
python rdf_to_csv_converter.py input_file.ttl --edges-file custom_edges.csv --nodes-file custom_nodes.csv
```

### Programmatic Usage

```python
from rdf_to_csv_converter import RDFToCSVConverter

# Basic conversion
converter = RDFToCSVConverter('dbpedia_sample.ttl')
edges_file, nodes_file = converter.convert()

# Advanced options
converter = RDFToCSVConverter('dbpedia_sample.ttl', output_dir='network_data')
edges_file, nodes_file = converter.convert(
    include_literals=False,
    filter_predicates=['rdf:type', 'rdfs:subClassOf', 'dbo:birthPlace'],
    edges_filename='relationships.csv',
    nodes_filename='entities.csv'
)

# Get statistics
stats = converter.generate_statistics()
print(f"Converted {stats['total_edges']} edges and {stats['total_nodes']} nodes")
```

## Output Files

### 1. Graph Edges File (*_edges.csv)

Contains the network relationships with the following columns:

| Column | Description | Required for Visualization |
|--------|-------------|---------------------------|
| `source` | Source node URI | ✅ Required |
| `target` | Target node URI | ✅ Required |
| `source_label` | Human-readable source label | ❌ Optional |
| `target_label` | Human-readable target label | ❌ Optional |
| `predicate` | Full predicate URI | ❌ Optional |
| `predicate_label` | Human-readable predicate label | ❌ Optional |
| `edge_type` | Edge type for styling | ❌ Optional |

Example:
```csv
source,target,source_label,target_label,predicate,predicate_label,edge_type
http://dbpedia.org/resource/Albert_Einstein,http://dbpedia.org/ontology/Person,Albert Einstein,Person,http://www.w3.org/1999/02/22-rdf-syntax-ns#type,type,type
http://dbpedia.org/resource/Albert_Einstein,http://dbpedia.org/resource/Ulm,Albert Einstein,Ulm,http://dbpedia.org/ontology/birthPlace,birth place,birth place
```

### 2. Node Metadata File (*_nodes.csv)

Contains node properties for visualization styling:

| Column | Description | Use for Visualization |
|--------|-------------|----------------------|
| `id` | Node URI (matches source/target in edges) | ✅ Required |
| `label` | Human-readable node label | Node labels |
| `type` | Node type/category | Grouping/filtering |
| `color` | Hex color code | Node coloring |
| `size` | Numeric size value | Node sizing |
| `degree` | Number of connections | Alternative sizing |

Example:
```csv
id,label,type,color,size,degree
http://dbpedia.org/resource/Albert_Einstein,Albert Einstein,Person,#DDA0DD,25,3
http://dbpedia.org/ontology/Person,Person,Class,#FF6B6B,45,12
http://dbpedia.org/resource/Ulm,Ulm,City,#98D8C8,15,2
```

### 3. Statistics File (*_statistics.txt)

Contains conversion summary and analysis.

## Visualization Integration

### For Gephi
1. Import the edges CSV as "Data Table" 
2. Import the nodes CSV as "Nodes Table"
3. Use the `color` column for node coloring
4. Use the `size` column for node sizing
5. Use the `type` column for grouping/filtering

### For Cytoscape
1. Import edges CSV as "Network"
2. Import nodes CSV as "Node Attributes"
3. Map visual properties to the metadata columns

### For Web Visualization (D3.js, vis.js, etc.)
The CSV files can be easily converted to JSON format for web-based visualizations.

## Filtering Options

### Predicate Filtering
Filter by specific relationship types:

```python
# Only structural relationships
structural_predicates = [
    'rdf:type',
    'rdfs:subClassOf', 
    'rdfs:subPropertyOf',
    'owl:equivalentClass'
]

# Only DBpedia domain relationships
domain_predicates = [
    'dbo:birthPlace',
    'dbo:deathPlace', 
    'dbo:spouse',
    'dbo:occupation'
]
```

### Common DBpedia Predicates
- `rdf:type` - Entity classification
- `dbo:birthPlace` - Birth location
- `dbo:deathPlace` - Death location
- `dbo:spouse` - Marriage relationships
- `dbo:occupation` - Professions
- `dbo:location` - Geographic relationships
- `rdfs:label` - Human-readable names

## Node Type Color Scheme

The converter automatically assigns colors based on node types:

| Node Type | Color | Hex Code |
|-----------|-------|----------|
| Class | Red | #FF6B6B |
| Property | Teal | #4ECDC4 |
| Individual | Blue | #45B7D1 |
| Person | Plum | #DDA0DD |
| Place | Green | #98D8C8 |
| Organization | Yellow | #F7DC6F |
| Event | Purple | #BB8FCE |
| Unknown | Gray | #BDC3C7 |

## Performance Considerations

- **Large Files**: For files with millions of triples, consider filtering by predicates
- **Memory Usage**: The converter loads the entire graph into memory
- **Literals**: Including literals (`--include-literals`) significantly increases node count
- **Output Size**: Use predicate filtering to reduce output file sizes

## Examples

### Example 1: DBpedia Person Networks
```python
# Extract person-related networks from DBpedia
converter = RDFToCSVConverter('dbpedia_persons.ttl')
edges_file, nodes_file = converter.convert(
    filter_predicates=[
        'rdf:type',
        'dbo:birthPlace',
        'dbo:deathPlace',
        'dbo:spouse',
        'dbo:child',
        'dbo:parent'
    ]
)
```

### Example 2: Ontology Structure
```python
# Extract just the ontological structure
converter = RDFToCSVConverter('ontology.ttl')
edges_file, nodes_file = converter.convert(
    filter_predicates=[
        'rdf:type',
        'rdfs:subClassOf',
        'rdfs:subPropertyOf',
        'owl:equivalentClass',
        'owl:equivalentProperty'
    ]
)
```

### Example 3: Geographic Networks
```python
# Extract geographic relationships
converter = RDFToCSVConverter('dbpedia_places.ttl')
edges_file, nodes_file = converter.convert(
    filter_predicates=[
        'rdf:type',
        'dbo:location',
        'dbo:country',
        'dbo:city',
        'dbo:region'
    ]
)
```

## Troubleshooting

### Common Issues

1. **"No module named 'rdflib'"**
   - Solution: Install dependencies with `pip install -r requirements.txt`

2. **"Error loading TTL file"**
   - Check file format and encoding
   - Ensure the file is valid Turtle syntax

3. **Empty output files**
   - Check if predicate filters are too restrictive
   - Verify the input file contains the expected data

4. **Memory errors with large files**
   - Use predicate filtering to reduce data size
   - Process files in smaller chunks

### Getting Help

Run the example script to see the converter in action:
```bash
python example_usage.py
```

This will create sample data and demonstrate the conversion process.

## License

This tool is provided as-is for educational and research purposes.
