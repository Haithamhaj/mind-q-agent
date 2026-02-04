#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from mind_q_agent.cli import MindQCli

if __name__ == "__main__":
    cli = MindQCli()
    cli.run()
