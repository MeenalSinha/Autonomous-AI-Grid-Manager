#!/bin/bash

# Autonomous AI Grid Manager - Startup Script

echo "⚡ Starting Autonomous AI Grid Manager..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if required packages are installed
echo "Checking dependencies..."

packages=("streamlit" "numpy" "pandas" "plotly" "torch")
missing=()

for package in "${packages[@]}"; do
    python3 -c "import $package" 2>/dev/null
    if [ $? -ne 0 ]; then
        missing+=("$package")
    fi
done

if [ ${#missing[@]} -ne 0 ]; then
    echo "❌ Missing packages: ${missing[*]}"
    echo ""
    echo "Installing required packages..."
    pip install --break-system-packages streamlit numpy pandas plotly torch
    echo ""
fi

echo "✓ All dependencies installed"
echo ""

# Start the application
echo "🚀 Launching Grid Manager Dashboard..."
echo ""
echo "The application will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py
