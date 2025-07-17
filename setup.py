#!/usr/bin/env python3
"""
Setup configuration for RDF TTL to CSV Converter
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="rdf-ttl-to-csv",
    version="1.0.0",
    author="Nima Azari",
    author_email="your-email@example.com",  # Update with your email
    description="Convert RDF Turtle ontology files to CSV format for network visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nima-azari/RDFONTOLOGYtoCSV",
    packages=find_packages(),
    py_modules=["rdf_to_csv_converter"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    python_requires=">=3.7",
    install_requires=[
        "rdflib>=6.0.0",
        "pandas>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "rdf-to-csv=rdf_to_csv_converter:main",
        ],
    },
    keywords="rdf, turtle, ttl, csv, network, visualization, ontology, skos, dbpedia, gephi, cytoscape, cosmograph",
    project_urls={
        "Bug Reports": "https://github.com/nima-azari/RDFONTOLOGYtoCSV/issues",
        "Source": "https://github.com/nima-azari/RDFONTOLOGYtoCSV",
        "Documentation": "https://github.com/nima-azari/RDFONTOLOGYtoCSV#readme",
        "Examples": "https://github.com/nima-azari/RDFONTOLOGYtoCSV/tree/main/ttl_data",
    },
    include_package_data=True,
    zip_safe=False,
)
