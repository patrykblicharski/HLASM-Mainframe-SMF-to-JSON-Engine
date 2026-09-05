# SMF2JSON Desktop — Python port of the HLASM engine
#
# Stdlib only (tkinter for GUI). No pip packages required.

python/
  smf2json/          # importable package
  samples/           # generated sample dumps
  tests/             # unit tests
  README.md

Quick start
-----------

# Generate a synthetic VB dump (types 30 + 80)
python3 -m smf2json --make-sample python/samples/sample.smf

# CLI conversion
python3 -m smf2json python/samples/sample.smf -o /tmp/out.json --debug
python3 -m smf2json python/samples/sample.smf -f csv -o /tmp/out.csv

# GUI (open file, debug pane, table + column tooltips, export JSON/CSV)
python3 -m smf2json
# or preload a file:
python3 -m smf2json --gui python/samples/sample.smf

Supported record types: 30 (common sections), 80 (RACF header + relocate), 89 (header).
Dump format: binary RECFM=VB / VBS (RDW-framed), as produced by IFASMFDP / IFASMFDL.
