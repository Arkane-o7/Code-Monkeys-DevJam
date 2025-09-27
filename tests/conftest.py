"""
Test configuration for pytest.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ.setdefault("GEMINI_API_KEY", "test_key_for_unit_tests")