# Convert and load command reference

Prefer the helper scripts for day-to-day use. This file lists every mapped table.

Default ClickHouse password: **`blacha123`** (user `smf`).  
Grafana: **`admin` / `blacha123`**. Web analytics UI: port **8080**.  
Dumps live in **`~/s`** (`t14.raw.dump` … `t119.raw.dump`).

## Reload after git pull (server)

```bash
cd ~/HLASM-Mainframe-SMF-to-JSON-Engine
git pull
cd infra
docker compose up -d --build
docker compose restart grafana   # pick up dashboard JSON (~30s provisioning)
# optional: re-export with fixed EBCDIC scrub, then reload
# ./scripts/load_from_s.sh
```

Web app: http://SERVER:8080 — Grafana: http://SERVER:3000

Regenerate Grafana JSON locally: `python infra/scripts/gen_dashboards.py`

## One-shot — all dumps in ~/s (recommended)

```bash
cd infra
chmod +x scripts/*.sh
./scripts/load_from_s.sh
# same as: ./scripts/load_from_s.sh ~/s ./data/csv
```

## One-shot â€” single dump

```bash
cd infra
./scripts/convert_and_load.sh ~/s/t119.raw.dump ./data/csv
```

## Export from ~/s (per dump)

```bash
cd /path/to/HLASM-Mainframe-SMF-to-JSON-Engine

python infra/scripts/export_csv_by_type.py ~/s/t14.raw.dump  -o infra/data/csv
python infra/scripts/export_csv_by_type.py ~/s/t15.raw.dump  -o infra/data/csv
python infra/scripts/export_csv_by_type.py ~/s/t17.raw.dump  -o infra/data/csv
python infra/scripts/export_csv_by_type.py ~/s/t30.raw.dump  -o infra/data/csv
python infra/scripts/export_csv_by_type.py ~/s/t42.raw.dump  -o infra/data/csv
python infra/scripts/export_csv_by_type.py ~/s/t61.raw.dump  -o infra/data/csv
python infra/scripts/export_csv_by_type.py ~/s/t65.raw.dump  -o infra/data/csv
python infra/scripts/export_csv_by_type.py ~/s/t66.raw.dump  -o infra/data/csv
python infra/scripts/export_csv_by_type.py ~/s/t80.raw.dump  -o infra/data/csv
python infra/scripts/export_csv_by_type.py ~/s/t89.raw.dump  -o infra/data/csv
python infra/scripts/export_csv_by_type.py ~/s/t92.raw.dump  -o infra/data/csv
python infra/scripts/export_csv_by_type.py ~/s/t119.raw.dump -o infra/data/csv
```

Loop:

```bash
for f in ~/s/t*.raw.dump; do
  python infra/scripts/export_csv_by_type.py "$f" -o infra/data/csv
done
```

## Load all CSVs

```bash
cd infra
./scripts/load_all.sh ./data/csv
```

## Environment for manual curl loads

```bash
export CH_URL=http://127.0.0.1:8123
export CH_USER=smf
export CH_PASSWORD=blacha123
CSV=./data/csv
```

Template (replace `TABLE`):

```bash
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" \
  "${CH_URL}/?database=smf&query=INSERT%20INTO%20TABLE%20FORMAT%20CSVWithNames" \
  --data-binary @"${CSV}/TABLE.csv"
```

## Per-table load commands (all 81 mapped tables)

Use Basic auth (`-u`). Do **not** put the password in the URL (bare HTTP 403).

### Type-only

```bash
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_14%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_14.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_15%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_15.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_17%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_17.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_61%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_61.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_65%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_65.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_66%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_66.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_80%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_80.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_89%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_89.csv"
```

### SMF 30

```bash
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_30_1%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_30_1.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_30_2%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_30_2.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_30_3%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_30_3.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_30_4%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_30_4.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_30_5%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_30_5.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_30_6%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_30_6.csv"
```

### SMF 42

```bash
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_42_20%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_42_20.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_42_21%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_42_21.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_42_22%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_42_22.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_42_23%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_42_23.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_42_24%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_42_24.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_42_25%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_42_25.csv"
```

### SMF 92

```bash
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_1%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_1.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_2%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_2.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_4%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_4.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_5%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_5.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_6%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_6.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_7%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_7.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_10%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_10.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_11%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_11.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_12%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_12.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_13%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_13.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_14%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_14.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_15%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_15.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_16%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_16.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_92_17%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_92_17.csv"
```

### SMF 119

```bash
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_1%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_1.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_2%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_2.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_3%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_3.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_4%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_4.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_5%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_5.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_6%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_6.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_7%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_7.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_8%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_8.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_10%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_10.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_11%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_11.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_12%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_12.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_20%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_20.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_21%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_21.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_22%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_22.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_23%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_23.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_24%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_24.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_32%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_32.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_33%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_33.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_34%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_34.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_35%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_35.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_36%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_36.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_37%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_37.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_38%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_38.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_39%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_39.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_40%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_40.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_41%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_41.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_42%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_42.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_43%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_43.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_44%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_44.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_45%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_45.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_48%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_48.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_49%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_49.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_50%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_50.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_51%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_51.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_52%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_52.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_70%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_70.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_71%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_71.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_72%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_72.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_73%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_73.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_74%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_74.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_75%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_75.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_76%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_76.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_77%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_77.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_78%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_78.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_79%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_79.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_80%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_80.csv"
curl -fsS -u "${CH_USER}:${CH_PASSWORD}" "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_119_81%20FORMAT%20CSVWithNames" --data-binary @"${CSV}/smf_119_81.csv"
```

## Note on `python -m smf2json -f csv`

```bash
cd python
python -m smf2json ~/s/t30.raw.dump -f csv -o /tmp/all_mapped.csv
```

That writes **all** mapped types from that dump into **one** CSV. For ClickHouse always use `export_csv_by_type.py` or `load_from_s.sh`.
