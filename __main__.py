"""
Main entry point for the Unified Dubbing System CLI
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from interfaces.cli.main import main_cli

if __name__ == "__main__":
    asyncio.run(main_cli())