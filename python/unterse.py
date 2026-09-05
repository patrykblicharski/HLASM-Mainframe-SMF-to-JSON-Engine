#!/usr/bin/env python3
"""Standalone AMATERSE/TERSE unpacker.

    python unterse.py FILE.TRS
    python unterse.py FILE.TRS -o FILE.raw.dump

Same codec as: python -m smf2json.terse
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from smf2json.terse import main

if __name__ == "__main__":
    raise SystemExit(main())
