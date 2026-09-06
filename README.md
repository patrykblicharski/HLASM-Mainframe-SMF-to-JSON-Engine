# zSMFtoJSON

SMF dump → JSON/CSV converter. The active implementation is the **stdlib-only Python desktop/CLI** under [`python/`](python/).

```text
cd python
python -m smf2json --gui
python -m smf2json samples/sample.smf -o out.json
```

Docs: [`python/README.md`](python/README.md) · [`python/AGENTS.md`](python/AGENTS.md) · [`python/ROADMAP.md`](python/ROADMAP.md) · [`python/MAPS.md`](python/MAPS.md)

ClickHouse + Grafana (Docker on Linux): [`infra/README.md`](infra/README.md)

`temp/smf119-app/` holds layout sources used by `python/tools/gen_smf119_maps.py` to regenerate SMF 119 maps.
