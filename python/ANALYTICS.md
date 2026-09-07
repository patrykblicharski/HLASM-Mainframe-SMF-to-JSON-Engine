# SMF2JSON — cross-analysis & Grafana ideas (backlog)

Ideas for joining mapped SMF types into fact tables / marts and showing them in Grafana.
Not implemented yet — design notes only. Inventory of maps: [MAPS.md](MAPS.md).
Polish: [ANALITYKA.md](ANALITYKA.md).

## Join keys (“glue”)

Normalize (trim / upper) before join.

| Key | Sources |
|-----|---------|
| `date` + `time` (+ `smf_system_id` / `sys_name`) | Almost all types |
| `job_name` | 14/15/17, 30, 42, 61/65/66, 80, 92 |
| `user_id` / RACF user | 80 `user_id`, 30 `racf_user`, 119 `user_id`, 92 `saf_user` |
| `dsname` / `entry_name` / `old_resource` | 14/15/17, 42, 61/65/66, 80 |
| `volser` | 14/15/17, 42, 80 |
| `connection_id` + IP/port | 119-1 ↔ 119-2 (also 119-10) |
| `tcp_stack` / `sysplex_name` | 119 (+ 30 `sysplex_name`) |
| `fs_name` / `fs_device` / `pathname` / `file_inode` | 92 (OMVS/HFS/zFS) |
| `omvs_uid` | 92 (optional join to UID) |

## Proposed fact tables / marts

### A. `fact_job_run` — workload spine

- **Sources:** 30-1 (start) + 30-4/5 (step/job end); optional 30-2/3 intervals
- **Fields:** job, step, program, class, CPU/SRB, EXCP/I/O, storage, duration
- **Grafana:** CPU time series by job class; top-N heaviest jobs; hourly heatmap
- **Signal:** rolling CPU/elapsed baseline per `job_name` → alert if today > p95 (14d)

### B. `fact_dataset_event` — dataset lifecycle

- **Sources:** 14/15 (I/O) + 17 (scratch) + 61/65/66 (catalog) + 42-20…25 (PDS member)
- **Fields:** event_type, dsname, volser, job, user, catalog, member
- **Cross:** same DSN: DEFINE (61) → WRITE (15) → SCRATCH (17) / DELETE (65); ALTER rename (66)
- **Grafana:** lifecycle funnel/sankey; “created & scratched same day”; top volumes by EXCP
- **Signal:** scratch/DEFINE storms; DEFINE without later type-15 activity

### C. `fact_racf_event` — security

- **Sources:** 80 (EVT/EVQ, user, group, class, resource, auth req/allow)
- **Grafana:** EVT mix; violation time series; top users × class; failed logons (EVT 1)
- **Cross 30:** user/job ↔ CPU in same window (“cost after deny”)
- **Cross 14/15:** `old_resource` ≈ `dsname` (AUTH vs real I/O)
- **Signal:** rare-user / rare-resource score; failed RACINIT spike

### D. `fact_tcp_conn` — TCP connection pairs

- **Sources:** 119-1 ⋈ 119-2 on `connection_id` (+ stack, local/remote IP:port)
- **Fields:** duration, in/out bytes, term_code, job / `resource_name`
- **Grafana:** top talkers; duration histogram; term_code breakdown
- **Signal:** short-lived connection flood; outbound byte outliers per port

### E. `fact_ftp_xfer` — file transfer

- **Sources:** 119-3 (client) + 119-70 (server) + 119-72 (logon fail)
- **Fields:** cmd, bytes, duration, file_name, users, IPs
- **Cross 80:** FTP user ↔ RACF EVT ±N minutes
- **Cross 14/15/17:** file_name / DSN after transfer
- **Grafana:** GB/day; logon fail rate; largest transfers table

### F. `fact_tn_session` — TN3270 / Telnet

- **Sources:** 119-20⋈21, 119-22⋈23
- **Grafana:** approximate concurrency, duration by stack
- **Cross 80:** EVT 1 logon vs session start

### G. `fact_crypto_session` — zERT / IPSec

- **Sources:** 119-11/12, 73–80
- **Grafana:** crypto mix / tunnel churn by stack
- **Signal:** short-lived zERT or tunnel flap increase

### H. `fact_tcpip_stats` — stack / interface health

- **Sources:** 119-5/6/7; 119-8 as restart marker
- **Grafana:** interface bytes/errors over time; listen-port stats
- **Note:** weak job-level joins; strong “stack health” dashboard

### I. `fact_catalog_churn` — catalog / SMS hygiene

- **Sources:** 61 + 65 + 66 (+ 17)
- **Grafana:** define vs delete ratio; top catalogs; rename storms (66)

### J. `fact_uss_fs` — OMVS file system activity

- **Sources:** 92 subtypes **1, 2, 4–7, 10–17** (zFS perf **50–57** not mapped yet)
- **Glue:** `job_name`, `saf_user` / `omvs_uid`, `fs_name` / `fs_device`, `pathname` / `file_inode`, `event_date` + time
- **Hot volume (P1):** 92-10 open, 92-11 close (+ bytes), 92-17 access; mid: 92-14 delete/rename; rare: 92-1 mount / 92-5 unmount
- **Web / Grafana ideas:**
  1. USS activity by hour — stacked counts 10/11/17/(14)
  2. Top paths — `smf_92_11.pathname` + `bytes_read`/`bytes_written`; fallback `smf_92_17` (`access_count`, `pathname`)
  3. Top jobs / SAF users — open+close+bytes from 10+11
  4. Open≠close asymmetry — count(10) vs count(11) in window (handle leak / incomplete dump)
  5. Delete/rename audit — `smf_92_14` top `file_name`, job, user; storms in time
  6. Mount inventory / space — `smf_92_1` `fs_name`, `fs_type_name`, `fs_space_total`/`fs_space_used`
  7. Unmount I/O lifetime — `smf_92_5` (and 6/7 when present) bytes/blocks per `fs_name`
  8. Quiesce duration — 2⋈4 on `fs_name` + STCK suspend/resume (when both sides exist)
  9. Security attr changes — `smf_92_15` owner uid/gid, `security_label` (often empty in samples)
  10. Cross RACF — 92-14/15 `saf_user` ↔ 80 in ±N min window
  11. Cross Jobs — top USS bytes/job ↔ 30 CPU
  12. Cross Datasets — `fs_name` like `OMVS.*.ZFS` ↔ 14/15/17 by name (later)
- **Signals:** delete/rename storm vs 14d baseline; open/close ratio drift; space-used spike on mount
- **Defer:** socket/FIFO close (16) KPI-only; mmap 12/13 optional; zFS 50–57 after map

## Highest-value crosses (priority)

1. **30 × 80** — job/user: CPU cost vs security events
2. **119-1×2 × 30** — network bytes by workload (`resource_name` / AS ≈ job/STC)
3. **14/15 × 80** — DSN I/O vs DATASET AUTH
4. **61/65/66 × 17 × 14/15** — catalog ↔ scratch ↔ I/O lifecycle
5. **119-3/70 × 14/15** — FTP ↔ local dataset activity
6. **42 × 80** — member change vs RACF on LIBRARY/DATASET
7. **119-2 term_code × 119-11** — odd terminations vs crypto events
8. **30 × 92** — job CPU vs USS open/close bytes
9. **80 × 92-14** — RACF user vs USS delete/rename in same window

## “Predictions” (realistic signals)

SMF alone does not give supervised ML targets; prefer **baselines / anomaly scores** stored on marts (`score`, `baseline_*`, `is_outlier`):

| Signal | How | Grafana |
|--------|-----|---------|
| Job runtime / CPU drift | 30-4/5 vs per-job baseline | alert + annotation |
| Conn duration / byte anomaly | 119-2 | boxplot / outlier table |
| Security burst | 80 failed EVT rate | threshold panel |
| Dataset churn spike | 17+65 count/hour | bar + alert |
| FTP fail then success | 72 → 70 sequence | state timeline |
| Stack restart impact | 119-8 then drop in 5/6 | annotation on network panels |
| USS open≠close | count(92-10) vs count(92-11) | KPI + alert |
| USS delete storm | 92-14 count/hour vs 14d baseline | bar + alert |

## Grafana MVP dashboards

1. **Security** — 80 time series, top users/resources, failed logons
2. **Network** — 119-2 bytes/duration; 119-5/6 stack/IF
3. **Batch / CPU** — 30-4/5 top jobs, class mix
4. **Storage lifecycle** — 61/65/66 + 17 counts; optional 14/15 EXCP
5. **Cross** — job from 30 joined to 119 bytes and 80 events (table + a few series)
6. **Unix / OMVS** — 92-10/11/17 hourly; top paths/jobs; delete storm; open/close ratio

**Backend:** event SMF fits **Postgres / Timescale / ClickHouse** (or Loki for raw JSON), not Prometheus counters. Grafana SQL / Infinity / Loki panels.

## Avoid

- Joining **80 × 119** on time only (no user/IP/job) — high false positives
- Relying on **89** (header-only map today)
- Treating **119-4** partial NMTP as a metric source (OK as profile-change marker)
- One mega-table for everything — prefer narrow marts A–J
- Depending on unmapped **92-50…57** for USS analytics until maps land

## Implementation sketch (later)

1. Stream convert → land raw rows (JSON/Parquet) keyed by type/subtype
2. ETL jobs build marts A–J with normalized join keys
3. Optional rolling baselines / outlier flags
4. Grafana dashboards on marts; keep raw for drill-down
