#!/usr/bin/env python3
"""
Code Verification Script
Checks for common runtime issues before demo
"""

import re
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_file_exists(filepath):
    """Check if file exists"""
    return Path(filepath).exists()

def check_st_rerun_safety(filepath):
    """Check for potential infinite rerun loops"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all st.rerun() calls
    rerun_pattern = r'st\.rerun\(\)'
    reruns = re.findall(rerun_pattern, content)
    
    # Check for safety guards before st.rerun()
    issues = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'st.rerun()' in line:
            # Look back 20 lines for safety checks
            context = '\n'.join(lines[max(0, i-20):i])
            has_guard = any([
                'if st.session_state' in context,
                'max_steps' in context,
                'simulation_running' in context
            ])
            if not has_guard:
                issues.append(f"Line {i+1}: st.rerun() may lack safety guard")
    
    return len(reruns), issues

def check_naming_consistency(filepath):
    """Check for old naming conventions"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    issues = []
    
    # Check for old names
    if 'simulator_rule' in content:
        issues.append("Found 'simulator_rule' - should be 'simulator_legacy'")
    if 'rule_controller' in content and 'legacy_controller' not in content:
        issues.append("Found 'rule_controller' without 'legacy_controller'")
    if 'GridSimulator' in content and 'MicrogridDigitalTwin' not in content:
        issues.append("Found 'GridSimulator' - should be 'MicrogridDigitalTwin'")
    
    return issues

def check_imports(filepath):
    """Check for missing imports"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    issues = []
    
    # Check for common usage without imports
    if 'np.' in content and 'import numpy' not in content:
        issues.append("Uses numpy (np.) but may not import it")
    if 'pd.' in content and 'import pandas' not in content:
        issues.append("Uses pandas (pd.) but may not import it")
    if 'torch.' in content and 'import torch' not in content:
        issues.append("Uses torch but may not import it")
    
    return issues

def verify_app():
    """Main verification function"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  AI Grid Manager - Code Verification{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    files_to_check = [
        ('app.py', True),
        ('rl_agent.py', True),
        ('grid_simulator.py', True),
        ('forecaster.py', True),
        ('requirements.txt', False)
    ]
    
    all_passed = True
    
    # Check file existence
    print(f"{Colors.BLUE}[1/5] Checking File Existence...{Colors.END}")
    for filename, critical in files_to_check:
        exists = check_file_exists(filename)
        status = f"{Colors.GREEN}✓{Colors.END}" if exists else f"{Colors.RED}✗{Colors.END}"
        print(f"  {status} {filename}")
        if not exists and critical:
            all_passed = False
    print()
    
    # Check st.rerun() safety
    print(f"{Colors.BLUE}[2/5] Checking st.rerun() Safety...{Colors.END}")
    if check_file_exists('app.py'):
        rerun_count, issues = check_st_rerun_safety('app.py')
        print(f"  Found {rerun_count} st.rerun() calls")
        if issues:
            print(f"  {Colors.YELLOW}⚠ Potential issues:{Colors.END}")
            for issue in issues:
                print(f"    - {issue}")
            all_passed = False
        else:
            print(f"  {Colors.GREEN}✓ All st.rerun() calls have safety guards{Colors.END}")
    print()
    
    # Check naming consistency
    print(f"{Colors.BLUE}[3/5] Checking Naming Consistency...{Colors.END}")
    if check_file_exists('app.py'):
        issues = check_naming_consistency('app.py')
        if issues:
            print(f"  {Colors.RED}✗ Naming issues found:{Colors.END}")
            for issue in issues:
                print(f"    - {issue}")
            all_passed = False
        else:
            print(f"  {Colors.GREEN}✓ All names consistent (simulator_legacy, etc.){Colors.END}")
    print()
    
    # Check imports
    print(f"{Colors.BLUE}[4/5] Checking Imports...{Colors.END}")
    for filename, _ in files_to_check[:4]:  # Skip requirements.txt
        if check_file_exists(filename):
            issues = check_imports(filename)
            if issues:
                print(f"  {Colors.YELLOW}⚠ {filename}:{Colors.END}")
                for issue in issues:
                    print(f"    - {issue}")
            else:
                print(f"  {Colors.GREEN}✓ {filename} - imports look good{Colors.END}")
    print()
    
    # Check for TODO/FIXME comments
    print(f"{Colors.BLUE}[5/5] Checking for TODO/FIXME...{Colors.END}")
    todo_count = 0
    for filename, _ in files_to_check[:4]:
        if check_file_exists(filename):
            with open(filename, 'r') as f:
                content = f.read()
                todos = len(re.findall(r'TODO|FIXME', content, re.IGNORECASE))
                if todos > 0:
                    print(f"  {Colors.YELLOW}⚠ {filename}: {todos} TODO/FIXME comments{Colors.END}")
                    todo_count += todos
    
    if todo_count == 0:
        print(f"  {Colors.GREEN}✓ No TODO/FIXME comments found{Colors.END}")
    print()
    
    # Final verdict
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    if all_passed:
        print(f"{Colors.GREEN}✓ VERIFICATION PASSED - Ready for demo!{Colors.END}")
        print(f"{Colors.GREEN}  All critical checks passed{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ VERIFICATION WARNINGS{Colors.END}")
        print(f"{Colors.YELLOW}  Please review issues above{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    # Recommendations
    print(f"{Colors.BLUE}Pre-Demo Recommendations:{Colors.END}")
    print(f"  1. Run Test 1: Basic Simulation")
    print(f"  2. Run Test 2: Comparison Mode (CRITICAL)")
    print(f"  3. Run Test 3: Stress Testing")
    print(f"  4. Clear browser cache")
    print(f"  5. Train AI once before demo starts")
    print()
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(verify_app())
