#!/usr/bin/env python3
"""Offline SMF Type 119 dump explorer.

Standalone from Gatherer / smfexplorer / smf-explorer-app.
Layouts derived from IBM ezasmf.h + ezbnmmpc.h (ZCSV2R5) field maps.

Usage:
    py -3 main.py
"""
from gui.app import run

if __name__ == "__main__":
    run()
