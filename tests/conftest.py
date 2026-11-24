import sys
from pathlib import Path

# qr_with_logo.py is a top-level script, not a package: make it importable from the tests.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
