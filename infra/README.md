# SMF → ClickHouse → Grafana (Docker on Linux)

Stack for loading mapped SMF types into ClickHouse (10-day retention) and charting them in Grafana.

```text
infra/
  docker-compose.yml
  README.md                 ← this file (install steps)
  COMMANDS.md               ← every convert / load command
  clickhouse/
    init.sql                ← full schema (81 SMF tables + stats_*)
    schema_fields.txt       ← field snapshot used to generate init.sql
  grafana/
    provisioning/…          ← datasource + dashboard provider
    dashboards/…            ← 6 starter dashboards
  scripts/
    gen_init_sql.py
    export_csv_by_type.py
    init_db.sh
    load_all.sh
    refresh_stats.sh
    convert_and_load.sh
  data/csv/                 ← put CSV outputs here (gitignored)
```

Default passwords in compose (change them):

| Service    | User  | Password         |
|------------|-------|------------------|
| ClickHouse | `smf` | `smf_change_me`  |
| Grafana    | `admin` | `admin_change_me` |

---

## 0. Prerequisites (Linux server)

- Docker Engine + Compose plugin (`docker compose version`)
- Python **3.10+** (for `smf2json` / export script; stdlib only)
- This repository cloned on the server
- Open ports **8123** (ClickHouse HTTP) and **3000** (Grafana), or bind to localhost only

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 curl python3
sudo usermod -aG docker "$USER"   # then log out/in
```

---

## 1. Start ClickHouse + Grafana

```bash
cd /path/to/HLASM-Mainframe-SMF-to-JSON-Engine/infra

# optional: edit passwords in docker-compose.yml and
# grafana/provisioning/datasources/clickhouse.yml (must match)

docker compose up -d
docker compose ps
```

What starts:

1. **clickhouse** — database  
2. **clickhouse-init** — applies `clickhouse/init.sql` once (81 tables + stats)  
3. **grafana** — UI on port 3000, ClickHouse plugin installed  

Checks:

```bash
curl -s http://127.0.0.1:8123/ping
# → Ok.

curl -s 'http://127.0.0.1:8123/?user=smf&password=smf_change_me' \
  --data-binary "SHOW TABLES FROM smf"
```

Grafana: open http://SERVER:3000 → login `admin` / `admin_change_me`.

If init container failed (race on first boot):

```bash
chmod +x scripts/*.sh
./scripts/init_db.sh
```

---

## 2. Convert an SMF dump → CSV (one file per type/subtype)

Do **not** use a single `python -m smf2json -f csv` for ClickHouse: that mixes all types in one file. Use the splitter:

```bash
cd /path/to/HLASM-Mainframe-SMF-to-JSON-Engine

# optional smoke dump
cd python
python -m smf2json --make-sample samples/sample.smf
cd ..

python infra/scripts/export_csv_by_type.py python/samples/sample.smf -o infra/data/csv
ls infra/data/csv
```

Examples of output files:

- `smf_14.csv`, `smf_15.csv`, `smf_17.csv`, `smf_80.csv`, `smf_89.csv`
- `smf_30_1.csv` … `smf_30_6.csv`
- `smf_42_20.csv` …
- `smf_92_11.csv` …
- `smf_119_1.csv`, `smf_119_2.csv`, …

Filter types:

```bash
python infra/scripts/export_csv_by_type.py /data/dumps/today.smf \
  -o infra/data/csv --types 14,15,17,30,80,119
```

Full per-table command list: **[COMMANDS.md](COMMANDS.md)**.

---

## 3. Load all CSVs into ClickHouse

```bash
cd infra
chmod +x scripts/*.sh
./scripts/load_all.sh ./data/csv
```

Or one table manually:

```bash
export CH_URL=http://127.0.0.1:8123
export CH_USER=smf
export CH_PASSWORD=smf_change_me

curl -fsS \
  "${CH_URL}/?user=${CH_USER}&password=${CH_PASSWORD}&database=smf&query=INSERT%20INTO%20smf_14%20FORMAT%20CSVWithNames" \
  --data-binary @./data/csv/smf_14.csv
```

Every table has the same pattern — see **COMMANDS.md**.

Verify:

```bash
curl -s 'http://127.0.0.1:8123/?user=smf&password=smf_change_me' \
  --data-binary "SELECT count() FROM smf.smf_14"
```

---

## 4. Refresh small Grafana rollups

Dashboards use both raw tables and `stats_*` summaries.

```bash
cd infra
./scripts/refresh_stats.sh
```

Run this after each upload (or from cron).

---

## 5. One command for daily ops

```bash
cd infra
./scripts/convert_and_load.sh /data/dumps/halfday.smf ./data/csv
```

That exports CSV → loads ClickHouse → refreshes stats.

Example cron (every day 07:00 and 19:00):

```cron
0 7,19 * * * cd /opt/HLASM-Mainframe-SMF-to-JSON-Engine/infra && ./scripts/convert_and_load.sh /data/smf/latest.smf ./data/csv >>/var/log/smf-load.log 2>&1
```

---

## 6. Grafana dashboards (project)

After login, open folder **SMF**:

| Dashboard | UID | Purpose |
|-----------|-----|---------|
| SMF Overview | `smf-overview` | daily volumes / table mix |
| SMF Datasets (14/15/17) | `smf-datasets` | input/output/scratch |
| SMF RACF (80) | `smf-racf` | event codes, users, jobs |
| SMF TCP (119-1/2) | `smf-tcp` | connections + bytes |
| SMF FTP (119-3/70) | `smf-ftp` | transfer volume |
| SMF Jobs (30) | `smf-jobs` | job/step ends |

Datasource is provisioned as **ClickHouse** (`uid: clickhouse_smf`).

If panels are empty: load data + run `./scripts/refresh_stats.sh`.

---

## 7. Retention and compression

- Each `smf_*` table: `TTL event_date + INTERVAL 10 DAY` (auto-delete)
- ClickHouse compresses columns on disk automatically
- To change retention: edit `TTL` in `scripts/gen_init_sql.py`, regenerate, re-apply carefully (or `ALTER TABLE … MODIFY TTL`)

Regenerate schema after map changes:

```bash
# from live maps
PYTHONPATH=python python infra/scripts/gen_init_sql.py --from-maps

# or from committed field snapshot
python infra/scripts/gen_init_sql.py
```

Then re-apply (new tables only are safe with `CREATE IF NOT EXISTS`; column changes need manual `ALTER` / recreate):

```bash
./scripts/init_db.sh
```

---

## 8. Stop / reset

```bash
cd infra
docker compose down          # keep data volumes
docker compose down -v       # wipe ClickHouse + Grafana data
```

---

## Security notes

- Change default passwords before exposing ports beyond localhost.
- Prefer firewall / reverse proxy in front of Grafana.
- Do not commit real SMF dumps or production CSVs into git (`infra/data/` is for local loads).
