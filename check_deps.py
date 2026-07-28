#!/usr/bin/env python3
import sys

print("Checking dependencies...")

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    print("✓ tkinterdnd2: OK")
except ImportError:
    print("✗ tkinterdnd2: MISSING (optional)")

try:
    from plyer import notification
    print("✓ plyer: OK")
except ImportError:
    print("✗ plyer: MISSING (optional)")

try:
    import keyboard
    print("✓ keyboard: OK")
except ImportError:
    print("✗ keyboard: MISSING (optional)")

try:
    import sandbox
    print("✓ sandbox: OK")
except ImportError:
    print("✗ sandbox: MISSING (optional)")
