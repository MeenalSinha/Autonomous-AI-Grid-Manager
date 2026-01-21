#!/bin/bash

# Autonomous AI Grid Manager - Setup Script
# This script validates and sets up your environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Autonomous AI Grid Manager - Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Python version
echo -e "${BLUE}[1/5] Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
    
    # Check if version is 3.9+
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        echo -e "${GREEN}✓ Python version is compatible (3.9+)${NC}"
    else
        echo -e "${YELLOW}⚠ Python 3.9+ recommended, found $PYTHON_VERSION${NC}"
    fi
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo -e "${YELLOW}Please install Python 3.9 or higher${NC}"
    exit 1
fi
echo ""

# Check pip
echo -e "${BLUE}[2/5] Checking pip...${NC}"
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓ pip3 found${NC}"
else
    echo -e "${RED}✗ pip3 not found${NC}"
    exit 1
fi
echo ""

# Validate structure
echo -e "${BLUE}[3/5] Validating project structure...${NC}"
if [ -f "validate_structure.py" ]; then
    python3 validate_structure.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Project structure validated${NC}"
    else
        echo -e "${RED}✗ Project structure validation failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ validate_structure.py not found, skipping validation${NC}"
fi
echo ""

# Install dependencies
echo -e "${BLUE}[4/5] Installing dependencies...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}"

if pip3 install -r requirements.txt --quiet; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    echo -e "${YELLOW}Try: pip3 install -r requirements.txt${NC}"
    exit 1
fi
echo ""

# Test imports
echo -e "${BLUE}[5/5] Testing imports...${NC}"
python3 -c "from core.grid_simulator import MicrogridDigitalTwin; from core.rl_agent import RLAgent; from core.forecaster import ShortTermForecaster; print('✓ All imports successful')" 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Import test passed${NC}"
else
    echo -e "${RED}✗ Import test failed${NC}"
    echo -e "${YELLOW}Some dependencies may not be installed correctly${NC}"
fi
echo ""

# Success message
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "To run the application:"
echo -e "${YELLOW}  streamlit run app.py${NC}"
echo ""
echo -e "Or use the quick start script:"
echo -e "${YELLOW}  ./run.sh${NC}"
echo ""
echo -e "For testing:"
echo -e "${YELLOW}  python3 scripts/verify_code.py${NC}"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""
