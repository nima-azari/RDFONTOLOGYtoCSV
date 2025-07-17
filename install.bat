@echo off
REM RDF TTL to CSV Converter - Installation Script for Windows
REM This script sets up the environment and installs dependencies

echo 🚀 RDF TTL to CSV Converter v1.0.0 Installation
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3 is required but not installed.
    echo Please install Python 3.7+ and try again.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is required but not installed.
    echo Please install pip and try again.
    pause
    exit /b 1
)

echo ✅ pip found
pip --version

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully!
) else (
    echo ❌ Failed to install dependencies.
    pause
    exit /b 1
)

REM Test installation
echo.
echo 🧪 Testing installation...
python rdf_to_csv_converter.py --help >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ Installation successful!
    echo.
    echo 🎉 Ready to use! Try these commands:
    echo.
    echo   # Show help
    echo   python rdf_to_csv_converter.py --help
    echo.
    echo   # Convert a TTL file
    echo   python rdf_to_csv_converter.py your_file.ttl
    echo.
    echo   # Run example
    echo   python example_usage.py
    echo.
    echo 📖 Documentation: README.md
    echo 🌐 Live Examples: cosmograph_links.txt
) else (
    echo ❌ Installation test failed.
    pause
    exit /b 1
)

echo.
echo Press any key to continue...
pause >nul
