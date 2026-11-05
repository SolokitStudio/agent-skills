#!/usr/bin/env python3
"""Convenience entry: ./check.py [args] → python -m agent_skill_check."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_skill_check.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
