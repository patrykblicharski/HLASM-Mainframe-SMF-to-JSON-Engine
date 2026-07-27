# IBM Docs SMF scraper (Playwright)

IBM Docs HTML is an SPA — plain `curl`/`WebFetch` returns a shell without field tables.
Use headless Chrome via `playwright-core` against the classic `ieag200` package URLs.

## Setup

```bash
cd tools/ibm_docs
npm install
# requires google-chrome (or chromium) on PATH /usr/local/bin/google-chrome
```

## Scrape SMF type 42 (DFSMS)

```bash
node crawl_smf42.mjs /path/to/out-dir
# then copy into the repo:
cp /path/to/out-dir/_all_pages.json ../../catalog/smf42/raw/all_pages.json
cp /path/to/out-dir/_summary.json ../../catalog/smf42/raw/scrape_summary.json
python3 ../build_smf42_catalog.py
```

Root page:

`https://www.ibm.com/docs/en/SSLTBW_3.2.0/com.ibm.zos.v3r2.ieag200/rec42.htm`

Carbon topic IDs like `configuration-subtype-1` are **ambiguous** and resolve to the wrong page — prefer the classic `ieag200/*.htm` paths.
