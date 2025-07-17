#!/bin/bash

# RDF TTL to CSV Converter - Installation Script
# This script sets up the environment and installs dependencies

echo "🚀 RDF TTL to CSV Converter v1.0.0 Installation"
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.7+ and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip and try again."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies."
    exit 1
fi

# Test installation
echo ""
echo "🧪 Testing installation..."
python3 rdf_to_csv_converter.py --help > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Installation successful!"
    echo ""
    echo "🎉 Ready to use! Try these commands:"
    echo ""
    echo "  # Show help"
    echo "  python3 rdf_to_csv_converter.py --help"
    echo ""
    echo "  # Convert a TTL file"
    echo "  python3 rdf_to_csv_converter.py your_file.ttl"
    echo ""
    echo "  # Run example"
    echo "  python3 example_usage.py"
    echo ""
    echo "📖 Documentation: README.md"
    echo "🌐 Live Examples: cosmograph_links.txt"
else
    echo "❌ Installation test failed."
    exit 1
fi
