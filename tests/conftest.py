#!/usr/bin/env python
"""
Pytest configuration for Deep-Sea Nexus v2.0
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

pytest_plugins = ["pytest_asyncio"]
