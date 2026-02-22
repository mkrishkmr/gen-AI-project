"""
Pytest configuration - ensures project root is on PYTHONPATH.
"""

import sys
import os

# Add project root so src.* imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
