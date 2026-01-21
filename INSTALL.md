# 📦 Installation Guide

Complete installation instructions for the Autonomous AI Grid Manager.

---

## 🚀 Quick Install (Recommended)

### Method 1: Automated Setup
```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Check Python version
2. Validate project structure  
3. Install all dependencies
4. Test imports
5. Confirm everything works

**Then run:**
```bash
streamlit run app.py
```

---

## 📋 Manual Installation

### Step 1: Prerequisites

**Required:**
- Python 3.9 or higher
- pip (Python package manager)
- 2GB RAM minimum
- 500MB disk space

**Check Python version:**
```bash
python3 --version
```

Should show `Python 3.9.x` or higher.

---

### Step 2: Clone/Download Repository

**Option A: Git Clone**
```bash
git clone https://github.com/yourusername/autonomous-ai-grid-manager.git
cd autonomous-ai-grid-manager
```

**Option B: Download ZIP**
1. Download from GitHub
2. Extract to folder
3. Open terminal in that folder

---

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

Your prompt should now show `(venv)`.

---

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- streamlit (Web UI framework)
- numpy (Numerical computing)
- pandas (Data manipulation)
- plotly (Interactive graphs)
- torch (Deep learning)
- scipy (Scientific computing)

**Installation time:** 2-5 minutes depending on internet speed.

---

### Step 5: Verify Installation

```bash
# Run validation script
python3 validate_structure.py
```

Should show:
```
✓ ALL CHECKS PASSED - Structure is Complete!
```

**Test imports:**
```bash
python3 -c "from core.grid_simulator import MicrogridDigitalTwin; print('✓ Works!')"
```

---

### Step 6: Run Application

```bash
streamlit run app.py
```

Browser should open automatically to `http://localhost:8501`

If not, manually open: http://localhost:8501

---

## 🔧 Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Clone repo
git clone <repo-url>
cd autonomous-ai-grid-manager

# Setup
./setup.sh
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Clone and setup
git clone <repo-url>
cd autonomous-ai-grid-manager
./setup.sh
```

### Windows

```powershell
# Install Python from python.org (3.9+)
# Download repository

# Open PowerShell in project folder
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run app
python -m streamlit run app.py
```

**Note:** On Windows, use `python` instead of `python3`.

---

## 🐛 Troubleshooting

### Issue 1: Python version too old

**Error:** `Python 3.8 or lower`

**Solution:**
```bash
# Linux
sudo apt install python3.11

# Mac
brew install python@3.11

# Windows
# Download from python.org
```

---

### Issue 2: pip not found

**Error:** `pip: command not found`

**Solution:**
```bash
# Linux
sudo apt install python3-pip

# Mac
python3 -m ensurepip

# Windows
python -m ensurepip --upgrade
```

---

### Issue 3: Permission denied on scripts

**Error:** `Permission denied: ./setup.sh`

**Solution:**
```bash
chmod +x setup.sh
chmod +x run.sh
```

---

### Issue 4: PyTorch installation fails

**Error:** `Failed building wheel for torch`

**Solution:**
```bash
# CPU-only version (smaller, faster install)
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# Or use pre-built wheel
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

---

### Issue 5: Streamlit not found

**Error:** `streamlit: command not found`

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall streamlit
pip install streamlit

# Or run directly
python -m streamlit run app.py
```

---

### Issue 6: Import errors

**Error:** `ModuleNotFoundError: No module named 'core'`

**Solution:**
```bash
# Make sure you're in the project root directory
pwd  # Should show .../autonomous-ai-grid-manager

# Check structure
ls -la core/

# Reinstall in dev mode
pip install -e .
```

---

### Issue 7: Port already in use

**Error:** `Address already in use`

**Solution:**
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill process using port 8501
# Linux/Mac
lsof -ti:8501 | xargs kill -9

# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

---

## 📊 System Requirements

### Minimum Requirements
- **CPU:** 2 cores
- **RAM:** 2GB
- **Disk:** 500MB free
- **OS:** Linux, macOS, Windows 10+
- **Python:** 3.9+

### Recommended Requirements
- **CPU:** 4+ cores
- **RAM:** 4GB+
- **Disk:** 1GB free
- **GPU:** Optional (CUDA for faster training)
- **Python:** 3.11+

---

## 🚀 Quick Start After Install

```bash
# 1. Start application
streamlit run app.py

# 2. In browser (http://localhost:8501):
#    - Click "Train RL Agent"
#    - Wait 30 seconds
#    - Click "Start" simulation

# 3. Test features:
#    - Inject stress tests
#    - Enable comparison mode
#    - View AI insights
```

---

## 🔍 Verify Installation

Run all validation checks:

```bash
# Structure validation
python3 validate_structure.py

# Code verification
python3 scripts/verify_code.py

# Import test
python3 -c "from core import *; print('All imports OK')"

# Run tests (if available)
python3 -m pytest tests/
```

---

## 📦 Installing in Development Mode

For development with hot-reloading:

```bash
# Install in editable mode
pip install -e .

# Install dev dependencies
pip install pytest black flake8 mypy

# Run with auto-reload
streamlit run app.py --server.runOnSave true
```

---

## 🌐 Installing on Remote Server

```bash
# SSH into server
ssh user@your-server.com

# Clone repository
git clone <repo-url>
cd autonomous-ai-grid-manager

# Install dependencies
pip3 install -r requirements.txt

# Run on custom port with external access
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

**Access via:** `http://your-server-ip:8501`

---

## 🐳 Docker Installation (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t grid-manager .
docker run -p 8501:8501 grid-manager
```

---

## ✅ Installation Checklist

Before running the app, verify:

- [ ] Python 3.9+ installed
- [ ] All dependencies installed (`pip list`)
- [ ] Project structure validated
- [ ] Imports work (`python3 -c "from core import *"`)
- [ ] No errors in terminal
- [ ] Browser can access localhost:8501
- [ ] Virtual environment activated (optional but recommended)

---

## 📞 Getting Help

If installation fails:

1. **Check Python version:** `python3 --version`
2. **Check pip version:** `pip3 --version`
3. **Read error message carefully**
4. **Search error on GitHub Issues**
5. **Check troubleshooting section above**

**Still stuck?**
- Create GitHub issue with error message
- Include: OS, Python version, full error log
- Tag with `installation` label

---

## 🎯 Next Steps After Installation

1. **Read Quick Start:** `QUICK_START.md`
2. **Run Demo:** Follow `docs/DEMO_SCRIPT.md`
3. **Test Features:** Use `docs/TESTING_CHECKLIST.md`
4. **Learn Architecture:** Read `docs/TECHNICAL_ARCHITECTURE.md`

---

**Installation complete? Start the app:**
```bash
streamlit run app.py
```

**Happy experimenting! 🚀**
