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
    load_from_s.sh          ← load all ~/s/t*.raw.dump
  data/csv/                 ← CSV outputs (gitignored)
```

Default passwords (everywhere):

| Service    | User    | Password     |
|------------|---------|--------------|
| ClickHouse | `smf`   | `blacha123`  |
| Grafana    | `admin` | `blacha123`  |

SMF dumps on the server live in **`~/s`**:

```text
~/s/t14.raw.dump   ~/s/t15.raw.dump   ~/s/t17.raw.dump
~/s/t30.raw.dump   ~/s/t42.raw.dump   ~/s/t61.raw.dump
~/s/t65.raw.dump   ~/s/t66.raw.dump   ~/s/t80.raw.dump
~/s/t89.raw.dump   ~/s/t92.raw.dump   ~/s/t119.raw.dump
```

---

## 0. Prerequisites (Linux server)

- Docker Engine + Compose plugin (`docker compose version`)
- Python **3.10+** (for `smf2json` / export script; stdlib only)
- This repository cloned on the server
- Dumps present in `~/s/` as above
- Open ports **8123** (ClickHouse HTTP) and **3000** (Grafana), or bind to localhost only

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 curl python3
sudo usermod -aG docker "$USER"   # then log out/in
```

---

## 1. Start ClickHouse + Grafana

```bash
cd ~/HLASM-Mainframe-SMF-to-JSON-Engine/infra   # or your clone path

docker compose up -d
docker compose ps
```

What starts:

1. **clickhouse** — database  
2. **clickhouse-init** — applies `clickhouse/init.sql` once (81 tables + stats)  
3. **grafana** — UI on port 3000, ClickHouse plugin installed  

Checks:

```bash
curl -s 'http://127.0.0.1:8123/ping'
# → Ok.

curl -s -u 'smf:blacha123' 'http://127.0.0.1:8123/' \
  --data-binary "SHOW TABLES FROM smf"
```

Grafana: open http://SERVER:3000 → login `admin` / `blacha123`.

If `init_db.sh` / curl returns **403**: password in the Docker volume is stale, or auth was using query-string. Fix:

```bash
docker compose down -v
docker compose up -d
sleep 15
./scripts/init_db.sh
```

`init_db.sh` prefers `docker exec` (`clickhouse-client --multiquery`).
HTTP fallback runs statements one-by-one (CH 24.8 has no `multiquery` HTTP setting).

If init container failed (race on first boot) **or you pulled a fixed `init.sql`**:

```bash
chmod +x scripts/*.sh
./scripts/init_db.sh
```

If tables were half-created with the old broken `event_date` expression, wipe and recreate:

```bash
docker compose down -v
docker compose up -d
sleep 15
./scripts/init_db.sh
```

---

## 2. Convert dumps from `~/s` → CSV → ClickHouse (recommended)

One command for all dumps in `~/s`:

```bash
cd ~/HLASM-Mainframe-SMF-to-JSON-Engine/infra
chmod +x scripts/*.sh
./scripts/load_from_s.sh
```

That:

1. exports each `~/s/t*.raw.dump` to `infra/data/csv/smf_*.csv` (one CSV per type/subtype)  
2. loads every CSV into ClickHouse  
3. refreshes Grafana `stats_*` tables  

Single dump only:

```bash
cd ~/HLASM-Mainframe-SMF-to-JSON-Engine
python infra/scripts/export_csv_by_type.py ~/s/t119.raw.dump -o infra/data/csv
cd infra && ./scripts/load_all.sh ./data/csv && ./scripts/refresh_stats.sh
```

Or via helper:

```bash
cd infra
./scripts/convert_and_load.sh ~/s/t80.raw.dump ./data/csv
```

Per-dump convert examples:

```bash
cd ~/HLASM-Mainframe-SMF-to-JSON-Engine
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

Do **not** use a single `python -m smf2json -f csv` for ClickHouse: that mixes all types in one file.

Full per-table curl list: **[COMMANDS.md](COMMANDS.md)**.

---

## 3. Load all CSVs into ClickHouse

```bash
cd infra
./scripts/load_all.sh ./data/csv
```

Uses `docker exec` + `clickhouse-client` when the container is up (avoids HTTP 30s socket timeouts on big files like `smf_92_*`). Override timeout:

```bash
CH_TIMEOUT=1200 ./scripts/load_all.sh ./data/csv
```

Or one table manually:

```bash
export CH_URL=http://127.0.0.1:8123
export CH_USER=smf
export CH_PASSWORD=blacha123

curl -fsS \
  -u "${CH_USER}:${CH_PASSWORD}" \
  "${CH_URL}/?database=smf&query=INSERT%20INTO%20smf_14%20FORMAT%20CSVWithNames" \
  --data-binary @./data/csv/smf_14.csv
```

Verify:

```bash
curl -s -u 'smf:blacha123' 'http://127.0.0.1:8123/' \
  --data-binary "SELECT count() FROM smf.smf_14"
```

---

## 4. Refresh small Grafana rollups

```bash
cd infra
./scripts/refresh_stats.sh
```

(`load_from_s.sh` already runs this.)

---

## 5. Cron example

```cron
0 7,19 * * * cd $HOME/HLASM-Mainframe-SMF-to-JSON-Engine/infra && ./scripts/load_from_s.sh >>/var/log/smf-load.log 2>&1
```

---

## 6. Grafana dashboards

After login (`admin` / `blacha123`), open folder **SMF**:

| Dashboard | UID | Purpose |
|-----------|-----|---------|
| SMF Overview | `smf-overview` | daily volumes / table mix |
| SMF Datasets (14/15/17) | `smf-datasets` | input/output/scratch |
| SMF RACF (80) | `smf-racf` | event codes, users, jobs |
| SMF TCP (119-1/2) | `smf-tcp` | connections + bytes |
| SMF FTP (119-3/70) | `smf-ftp` | transfer volume |
| SMF Jobs (30) | `smf-jobs` | job/step ends |

If panels are empty: run `./scripts/load_from_s.sh` (or convert+load+`refresh_stats.sh`).

---

## 7. Retention and compression

- Each `smf_*` table: `TTL event_date + INTERVAL 10 DAY`
- ClickHouse compresses on disk automatically

Regenerate schema after map changes:

```bash
PYTHONPATH=python python infra/scripts/gen_init_sql.py --from-maps
# or: python infra/scripts/gen_init_sql.py
cd infra && ./scripts/init_db.sh
```

---

## 8. Stop / reset

```bash
cd infra
docker compose down          # keep data volumes
docker compose down -v       # wipe ClickHouse + Grafana data
```

If you already started compose with the old password, wipe volumes once so `blacha123` applies:

```bash
docker compose down -v
docker compose up -d
```

---

## Security notes

- Prefer firewall / reverse proxy in front of Grafana on a public host.
- Do not commit real SMF dumps or production CSVs into git (`infra/data/` is for local loads).
