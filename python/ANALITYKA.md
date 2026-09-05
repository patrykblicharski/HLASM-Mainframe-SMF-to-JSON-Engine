# SMF2JSON — pomysły na analizę krzyżową i Grafana (backlog)

Pomysły na łączenie zmapowanych typów SMF w tabele faktów / marty i pokazywanie ich w Grafanie.
Jeszcze niezaimplementowane — tylko notatki projektowe. Inwentarz map: [MAPS.md](MAPS.md).
Wersja angielska: [ANALYTICS.md](ANALYTICS.md).

## Klucze złączeń („klej”)

Przed joinem znormalizuj (trim / upper).

| Klucz | Źródła |
|-------|--------|
| `date` + `time` (+ `smf_system_id` / `sys_name`) | Prawie wszystkie typy |
| `job_name` | 14/15/17, 30, 42, 61/65/66, 80 |
| `user_id` / użytkownik RACF | 80 `user_id`, 30 `racf_user`, 119 `user_id` |
| `dsname` / `entry_name` / `old_resource` | 14/15/17, 42, 61/65/66, 80 |
| `volser` | 14/15/17, 42, 80 |
| `connection_id` + IP/port | 119-1 ↔ 119-2 (także 119-10) |
| `tcp_stack` / `sysplex_name` | 119 (+ 30 `sysplex_name`) |

## Proponowane tabele faktów / marty

### A. `fact_job_run` — kręgosłup workloadu

- **Źródła:** 30-1 (start) + 30-4/5 (koniec stepu/joba); opcjonalnie interwały 30-2/3
- **Pola:** job, step, program, class, CPU/SRB, EXCP/I/O, storage, duration
- **Grafana:** szereg czasowy CPU wg klasy joba; top-N najcięższych jobów; heatmapa godzinowa
- **Sygnał:** rolling baseline CPU/elapsed per `job_name` → alert, jeśli dziś > p95 (14d)

### B. `fact_dataset_event` — cykl życia datasetu

- **Źródła:** 14/15 (I/O) + 17 (scratch) + 61/65/66 (katalog) + 42-20…25 (member PDS)
- **Pola:** event_type, dsname, volser, job, user, catalog, member
- **Krzyżowo:** ten sam DSN: DEFINE (61) → WRITE (15) → SCRATCH (17) / DELETE (65); ALTER rename (66)
- **Grafana:** lejek/sankey cyklu życia; „utworzony i scratchowany tego samego dnia”; top wolumeny wg EXCP
- **Sygnał:** burze scratch/DEFINE; DEFINE bez późniejszej aktywności typu 15

### C. `fact_racf_event` — bezpieczeństwo

- **Źródła:** 80 (EVT/EVQ, user, group, class, resource, auth req/allow)
- **Grafana:** mix EVT; szereg czasowy naruszeń; top users × class; nieudane logony (EVT 1)
- **Krzyż 30:** user/job ↔ CPU w tym samym oknie („koszt po deny”)
- **Krzyż 14/15:** `old_resource` ≈ `dsname` (AUTH vs realne I/O)
- **Sygnał:** score rare-user / rare-resource; spike nieudanych RACINIT

### D. `fact_tcp_conn` — pary połączeń TCP

- **Źródła:** 119-1 ⋈ 119-2 po `connection_id` (+ stack, local/remote IP:port)
- **Pola:** duration, in/out bytes, term_code, job / `resource_name`
- **Grafana:** top talkers; histogram duration; rozkład term_code
- **Sygnał:** powódź krótkich połączeń; outliery bajtów wychodzących per port

### E. `fact_ftp_xfer` — transfer plików

- **Źródła:** 119-3 (klient) + 119-70 (serwer) + 119-72 (nieudany logon)
- **Pola:** cmd, bytes, duration, file_name, users, IPs
- **Krzyż 80:** użytkownik FTP ↔ RACF EVT ±N minut
- **Krzyż 14/15/17:** file_name / DSN po transferze
- **Grafana:** GB/dzień; wskaźnik nieudanych logonów; tabela największych transferów

### F. `fact_tn_session` — TN3270 / Telnet

- **Źródła:** 119-20⋈21, 119-22⋈23
- **Grafana:** przybliżona współbieżność, duration wg stacka
- **Krzyż 80:** EVT 1 logon vs start sesji

### G. `fact_crypto_session` — zERT / IPSec

- **Źródła:** 119-11/12, 73–80
- **Grafana:** mix crypto / churn tuneli wg stacka
- **Sygnał:** wzrost krótkich sesji zERT lub flapów tuneli

### H. `fact_tcpip_stats` — zdrowie stacka / interfejsu

- **Źródła:** 119-5/6/7; 119-8 jako znacznik restartu
- **Grafana:** bajty/błędy interfejsu w czasie; statystyki listen-port
- **Uwaga:** słabe joiny na poziomie joba; mocny dashboard „zdrowie stacka”

### I. `fact_catalog_churn` — higiena katalogu / SMS

- **Źródła:** 61 + 65 + 66 (+ 17)
- **Grafana:** stosunek define vs delete; top katalogi; burze rename (66)

## Najcenniejsze krzyżówki (priorytet)

1. **30 × 80** — job/user: koszt CPU vs zdarzenia bezpieczeństwa
2. **119-1×2 × 30** — bajty sieci wg workloadu (`resource_name` / AS ≈ job/STC)
3. **14/15 × 80** — I/O na DSN vs AUTH DATASET
4. **61/65/66 × 17 × 14/15** — katalog ↔ scratch ↔ cykl I/O
5. **119-3/70 × 14/15** — FTP ↔ lokalna aktywność datasetów
6. **42 × 80** — zmiana membera vs RACF na LIBRARY/DATASET
7. **119-2 term_code × 119-11** — dziwne zakończenia vs zdarzenia crypto

## „Predykcje” (realistyczne sygnały)

Sam SMF nie daje etykiet do uczenia nadzorowanego; lepiej **baseline / score anomalii** na martach (`score`, `baseline_*`, `is_outlier`):

| Sygnał | Jak | Grafana |
|--------|-----|---------|
| Dryf runtime / CPU joba | 30-4/5 vs baseline per job | alert + adnotacja |
| Anomalia duration / bajtów połączenia | 119-2 | boxplot / tabela outlierów |
| Burst bezpieczeństwa | 80 failed EVT rate | panel progowy |
| Spike churnu datasetów | 17+65 count/hour | słupki + alert |
| Fail FTP, potem sukces | sekwencja 72 → 70 | state timeline |
| Wpływ restartu stacka | 119-8, potem spadek w 5/6 | adnotacja na panelach sieci |

## Dashboardy Grafana MVP

1. **Security** — szereg czasowy 80, top users/resources, nieudane logony
2. **Network** — bajty/duration 119-2; stack/IF 119-5/6
3. **Batch / CPU** — top joby 30-4/5, mix klas
4. **Storage lifecycle** — zliczenia 61/65/66 + 17; opcjonalnie EXCP 14/15
5. **Cross** — job z 30 złączony z bajtami 119 i zdarzeniami 80 (tabela + kilka szeregów)

**Backend:** eventowy SMF pasuje do **Postgres / Timescale / ClickHouse** (albo Loki na surowy JSON), nie do liczników Prometheus. Panele Grafana SQL / Infinity / Loki.

## Unikać

- Join **80 × 119** tylko po czasie (bez user/IP/job) — dużo fałszywych trafień
- Polegania na **89** (dziś mapa tylko nagłówka)
- Traktowania częściowego NMTP **119-4** jako źródła metryk (OK jako znacznik zmiany profilu)
- Jednej mega-tabeli na wszystko — lepiej wąskie marty A–I

## Szkic implementacji (później)

1. Stream convert → lądowanie surowych wierszy (JSON/Parquet) wg typu/subtypu
2. Joby ETL budują marty A–I ze znormalizowanymi kluczami join
3. Opcjonalnie rolling baseline / flagi outlierów
4. Dashboardy Grafana na martach; surowe dane zostają do drill-down
