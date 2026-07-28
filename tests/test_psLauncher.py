#!/usr/bin/env python3
"""
Automated test for psLauncher basic functionality
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=10)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def test_syntax():
    """Test if psLauncher.py has valid syntax"""
    print("Testing syntax...")
    rc, stdout, stderr = run_command(f"{sys.executable} -m py_compile psLauncher.py")
    if rc == 0:
        print("✓ Syntax check passed")
        return True
    else:
        print(f"✗ Syntax check failed: {stderr}")
        return False

def test_imports():
    """Test if all imports work"""
    print("\nTesting imports...")
    
    # Create a temporary test file for imports
    test_import_file = "test_imports.py"
    with open(test_import_file, "w") as f:
        f.write("""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import shutil
import subprocess
import threading
import json
import re
import csv
import platform
import shlex
import webbrowser
from pathlib import Path
from datetime import datetime
import queue
import time
import traceback
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    print("tkinterdnd2: OK")
except ImportError:
    print("tkinterdnd2: MISSING")
try:
    from plyer import notification
    print("plyer: OK")
except ImportError:
    print("plyer: MISSING")
try:
    import keyboard
    print("keyboard: OK")
except ImportError:
    print("keyboard: MISSING")
try:
    import sandbox
    print("sandbox: OK")
except ImportError:
    print("sandbox: MISSING")
print("All core imports: OK")
""")
    
    rc, stdout, stderr = run_command(f"{sys.executable} {test_import_file}")
    
    # Clean up
    try:
        os.remove(test_import_file)
    except:
        pass
    
    if rc == 0 and "All core imports: OK" in stdout:
        print("✓ Import check passed")
        return True
    else:
        print(f"✗ Import check failed: {stdout}")
        return False

def test_config_dir():
    """Test if config directory can be created"""
    print("\nTesting config directory...")
    try:
        import platform
        if platform.system() == "Windows":
            config_dir = Path(r"C:\.polsoft\psLauncher")
        else:
            config_dir = Path.home() / ".polsoft" / "psLauncher"
        config_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Config directory: {config_dir}")
        return True
    except Exception as e:
        print(f"✗ Config directory test failed: {e}")
        return False

def test_script_execution():
    """Test if test scripts can be executed"""
    print("\nTesting script execution...")
    test_files = [
        "test_script.ps1",
        "test_script.py", 
        "test_script.bat"
    ]
    
    for script in test_files:
        if not os.path.exists(script):
            print(f"✗ Test script not found: {script}")
            return False
    
    # Test Python script
    rc, stdout, stderr = run_command(f"{sys.executable} test_script.py")
    if rc == 0:
        print(f"✓ test_script.py executed successfully")
    else:
        print(f"✗ test_script.py failed: {stderr}")
        return False
    
    # Test PowerShell script (Windows only)
    import platform
    if platform.system() == "Windows":
        rc, stdout, stderr = run_command("powershell -ExecutionPolicy Bypass -File test_script.ps1")
        if rc == 0:
            print(f"✓ test_script.ps1 executed successfully")
        else:
            print(f"✗ test_script.ps1 failed: {stderr}")
            return False
    
    # Test Batch script (Windows only)
    if platform.system() == "Windows":
        rc, stdout, stderr = run_command("test_script.bat")
        if rc == 0:
            print(f"✓ test_script.bat executed successfully")
        else:
            print(f"✗ test_script.bat failed: {stderr}")
            return False
    
    return True

def main():
    print("=" * 60)
    print("psLauncher Automated Test Suite")
    print("=" * 60)
    
    tests = [
        ("Syntax Check", test_syntax),
        ("Import Check", test_imports),
        ("Config Directory", test_config_dir),
        ("Script Execution", test_script_execution),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! psLauncher is ready to use.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please fix the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
