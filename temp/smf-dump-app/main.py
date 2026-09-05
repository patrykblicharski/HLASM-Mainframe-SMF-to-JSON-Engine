#!/usr/bin/env python3
"""Offline SMF dump explorer — Tkinter UI over IFASMFDP binary dumps.

No z/OS Data Gatherer / smfexplorer. Discovers Gatherer-supported SMF
type/subtype pairs in a local .bin dump and decodes selected records via
OpenAPI field layouts (x-zml-offset / x-zml-size / x-zml-datatype).

Usage:
    py -3 main.py
"""
from gui.app import run

if __name__ == "__main__":
    run()
