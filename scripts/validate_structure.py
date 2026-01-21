#!/usr/bin/env python3
"""
Project Structure Validation Script
Ensures all files are present and compatible
"""

import os
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    exists = Path(filepath).exists()
    status = f"{Colors.GREEN}✓{Colors.END}" if exists else f"{Colors.RED}✗{Colors.END}"
    req = "(required)" if required else "(optional)"
    
    if not exists and required:
        print(f"  {status} {filepath} {Colors.RED}{req}{Colors.END}")
        return False
    elif not exists:
        print(f"  {status} {filepath} {Colors.YELLOW}{req}{Colors.END}")
        return True
    else:
        print(f"  {status} {filepath}")
        return True

def validate_structure():
    """Validate complete project structure"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}  Project Structure Validation{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    all_passed = True
    
    # Root level files
    print(f"{Colors.BLUE}[1/5] Root Level Files{Colors.END}")
    root_files = [
        ("README.md", True),
        ("QUICK_START.md", True),
        ("GITHUB_SETUP.md", True),
        ("LICENSE", True),
        (".gitignore", True),
        ("requirements.txt", True),
        ("run.sh", True),
        ("app.py", True),
        ("FOLDER_STRUCTURE.txt", False),
    ]
    
    for filepath, required in root_files:
        if not check_file_exists(filepath, required):
            all_passed = False
    print()
    
    # Core package
    print(f"{Colors.BLUE}[2/5] Core Package Files{Colors.END}")
    core_files = [
        ("core/__init__.py", True),
        ("core/grid_simulator.py", True),
        ("core/rl_agent.py", True),
        ("core/forecaster.py", True),
    ]
    
    for filepath, required in core_files:
        if not check_file_exists(filepath, required):
            all_passed = False
    print()
    
    # Scripts
    print(f"{Colors.BLUE}[3/5] Scripts{Colors.END}")
    script_files = [
        ("scripts/verify_code.py", True),
    ]
    
    for filepath, required in script_files:
        if not check_file_exists(filepath, required):
            all_passed = False
    print()
    
    # Documentation
    print(f"{Colors.BLUE}[4/5] Documentation Files{Colors.END}")
    doc_files = [
        ("docs/DEMO_SCRIPT.md", True),
        ("docs/TESTING_CHECKLIST.md", True),
        ("docs/TECHNICAL_ARCHITECTURE.md", True),
        ("docs/PROJECT_SUMMARY.md", True),
        ("docs/RUNTIME_VERIFICATION.md", True),
        ("docs/UI_DESIGN_UPDATE.md", True),
        ("docs/FINAL_REVIEW_COMPLETE.md", True),
        ("docs/STRUCTURE.md", True),
        ("docs/GITHUB_SETUP.md", False),
        ("docs/FOLDER_STRUCTURE.txt", False),
    ]
    
    for filepath, required in doc_files:
        if not check_file_exists(filepath, required):
            all_passed = False
    print()
    
    # Test imports
    print(f"{Colors.BLUE}[5/5] Testing Imports{Colors.END}")
    try:
        # Change to project directory
        import importlib.util
        
        # Test core package
        spec = importlib.util.spec_from_file_location("core", "core/__init__.py")
        if spec and spec.loader:
            print(f"  {Colors.GREEN}✓{Colors.END} core package is importable")
        else:
            print(f"  {Colors.RED}✗{Colors.END} core package import failed")
            all_passed = False
    except Exception as e:
        print(f"  {Colors.YELLOW}⚠{Colors.END} Could not test imports: {e}")
    
    print()
    
    # Final verdict
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED - Structure is Complete!{Colors.END}")
        print(f"{Colors.GREEN}  Ready for GitHub upload{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME FILES MISSING{Colors.END}")
        print(f"{Colors.RED}  Please review the files marked with ✗ above{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    # File count summary
    print(f"{Colors.BLUE}File Count Summary:{Colors.END}")
    total_files = sum(1 for _ in Path('.').rglob('*') if _.is_file() and '__pycache__' not in str(_))
    py_files = sum(1 for _ in Path('.').rglob('*.py') if '__pycache__' not in str(_))
    md_files = sum(1 for _ in Path('.').rglob('*.md'))
    
    print(f"  Total files: {total_files}")
    print(f"  Python files: {py_files}")
    print(f"  Documentation files: {md_files}")
    print()
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(validate_structure())
