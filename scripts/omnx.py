#!/usr/bin/env python3
"""Run with Python >=3.10; no pip installation or network needed."""
import sys
sys.dont_write_bytecode = True
from omnxlib.cli import main
if __name__ == '__main__':
    raise SystemExit(main())
