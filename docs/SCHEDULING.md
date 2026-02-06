# Scheduled Jobs Documentation

This document describes the automated scheduling features for backfill and gap repair jobs in the Market Data service.

## Overview

The Market Data service uses a **long-running daemon architecture** with periodic async tasks, which is superior to cron/systemd timers for this use case because:

- ✅ No startup overhead for each run
- ✅ Better state management and context retention
- ✅ Immediate WebSocket ingestion (prevents new gaps)
- ✅ More efficient resource usage
- ✅ Simplified deployment (single systemd service)

## Scheduled Jobs

### 1. Initial Backfill (Startup)

**Purpose**: Populate historical data when the service first starts or after downtime.

**Trigger**: On daemon startup (configurable)

**Configuration**:
```bash
BACKFILL_ON_STARTUP=true     # Enable/disable (default: true)
BACKFILL_DAYS=365            # Days of history to fetch (default: 365)
```

**Implementation**: `daemon.py:run_backfill()`

**Behavior**:
- Runs once at startup in background
- Does not block other daemon operations
- Fetches historical candles for all configured symbols/timeframes
- Resumes from last known candle if data exists
- Respects rate limits with exponential backoff

---

### 2. Gap Detection & Repair Loop

**Purpose**: Continuously detect and repair missing candles in the database.

**Trigger**: Periodic (configurable interval)

**Configuration**:
```bash
GAP_REPAIR_INTERVAL_MINUTES=60        # How often to run repair cycle (default: 60)
GAP_DETECTION_INTERVAL_MINUTES=60     # How often to scan for new gaps (default: 60)
GAP_REPAIR_MAX_REPAIRS_PER_RUN=10     # Max gaps to repair per cycle (default: 10, 0=unlimited)
GAP_DETECTION_MAX_OPEN_GAPS=0         # Skip detection if backlog exceeds this (default: 0=disabled)
```

**Implementation**: `daemon.py:run_gap_repair_loop()`

**Behavior**:
- Runs continuously on a configurable interval (default: every 60 minutes)
- **Detection phase** (runs less frequently):
  - Scans all symbols/timeframes for missing candles
  - Compares actual candle intervals vs expected timeframe
  - Saves detected gaps to `data_gaps` table
  - Can be throttled if backlog is too large (`GAP_DETECTION_MAX_OPEN_GAPS`)
- **Repair phase** (runs more frequently):
  - Fetches unrepaired gaps from database
  - Limits repairs per run (`GAP_REPAIR_MAX_REPAIRS_PER_RUN`)
  - Fetches missing candles from exchange API
  - Marks gaps as repaired
  - Logs results and failures
- Creates job records in `ingestion_jobs` table for tracking
- Respects rate limits with exponential backoff

**Logs**:
```
2026-02-06 01:30:00 - Running gap detection and repair...
2026-02-06 01:30:15 - Gap detected: BTCUSD/1h from 2026-02-05 20:00:00 to 2026-02-05 23:00:00
2026-02-06 01:30:20 - Repairing gap: BTCUSD/1h from 2026-02-05 20:00:00 to 2026-02-05 23:00:00
2026-02-06 01:30:25 - Repaired gap with 3 candles
2026-02-06 01:30:30 - Gap maintenance complete: 1 new gaps, 1 repaired, 0 failures, open_gaps=0
```

---

### 3. REST Update Loop (Optional)

**Purpose**: Periodically fetch latest candles via REST API (mostly redundant when WebSocket ingestion is enabled).

**Trigger**: Periodic (configurable interval)

**Configuration**:
```bash
REST_UPDATE_ENABLED=false        # Enable/disable (default: false)
UPDATE_INTERVAL_SECONDS=60       # Fetch interval (default: 60)
```

**Implementation**: `daemon.py:run_update_loop()`

**Behavior**:
- Disabled by default (WebSocket ingestion is preferred)
- When enabled, fetches latest 10 candles per symbol/timeframe
- Useful as fallback if WebSocket ingestion fails
- Can cause rate limit issues if interval is too low

**Note**: Usually disabled when `WS_INGESTION_ENABLED=true` to avoid redundant API calls.

---

### 4. Data Retention Cleanup Loop

**Purpose**: Remove old candles based on retention policy to manage database size.

**Trigger**: Daily (runs once per day after 1-hour delay)

**Configuration**:
```bash
RETENTION_1M=30      # Days to keep 1-minute candles (default: 30)
RETENTION_1H=365     # Days to keep 1-hour candles (default: 365)
RETENTION_4H=730     # Days to keep 4-hour candles (default: 730)
RETENTION_1D=1825    # Days to keep daily candles (default: 1825 / 5 years)
```

**Implementation**: `daemon.py:run_cleanup_loop()`

**Behavior**:
- First run: 1 hour after daemon startup
- Subsequent runs: every 24 hours
- Deletes candles older than retention period per timeframe
- Logs total candles deleted

---

### 5. WebSocket Ingestion (Real-time)

**Purpose**: Stream live candles from Bitfinex WebSocket API to prevent gaps.

**Trigger**: Runs continuously from daemon startup

**Configuration**:
```bash
WS_INGESTION_ENABLED=true                      # Enable/disable (default: true)
WS_CATCHUP_LOOKBACK_MINUTES=180                # REST catch-up on startup (default: 180)
WS_MAX_SUBSCRIPTIONS_PER_CONNECTION=25         # Subscriptions per WS connection (default: 25)
WS_SAVE_BATCH_SIZE=200                         # Batch size for persistence (default: 200)
WS_SAVE_FLUSH_SECONDS=2.0                      # Flush interval (default: 2.0)
WS_RECONNECT_INITIAL_BACKOFF=1.0               # Initial reconnect delay (default: 1.0)
WS_RECONNECT_MAX_BACKOFF=60.0                  # Max reconnect delay (default: 60.0)
```

**Implementation**: `daemon.py:run_ws_ingestion()`

**Behavior**:
- Subscribes to all configured symbol/timeframe combinations
- Shards subscriptions across multiple WebSocket connections (Bitfinex limits subscriptions per connection)
- Buffers incoming candles in async queue
- Batches writes to database for efficiency
- Automatically reconnects with exponential backoff on connection loss
- On startup, runs REST catch-up to fetch last N minutes of data

**Benefits**:
- Near-zero latency for new candles
- Prevents gaps from forming (no polling delay)
- More API-efficient than REST polling
- Automatic reconnection on network issues

---

## Rate Limiting

All scheduled jobs respect Bitfinex API rate limits:

**Configuration**:
```bash
RATE_LIMIT_DELAY=6.0                    # Seconds between requests (~10 req/min)
RATE_LIMIT_MAX_RETRIES=10               # Max retries on 429 errors
RATE_LIMIT_INITIAL_BACKOFF=2.0          # Initial backoff on 429
RATE_LIMIT_MIN_BACKOFF_SECONDS=60.0     # Minimum backoff after 429
RATE_LIMIT_MAX_BACKOFF=120.0            # Maximum backoff
```

**Implementation**: Global singleton rate limiter (`rate_limiter.py`)

**Behavior**:
- Thread-safe singleton shared across all services
- Enforces minimum delay between API requests
- On 429 (rate limit) errors:
  - Exponential backoff: 2s → 4s → 8s → ... → 120s
  - Minimum 60s wait (Bitfinex blocks IPs for ~60s on rate limit)
  - Retries up to `RATE_LIMIT_MAX_RETRIES` times
  - Logs all rate limit events

---

## Observability

### Logs

All scheduled jobs log their activity:
- Info: Normal operations, job completion, summary statistics
- Warning: Rate limits, missing data, queue full
- Error: Failed jobs, API errors, database errors

**View logs** (systemd deployment):
```bash
journalctl -u market-data -f
```

### API Endpoints

Monitor scheduled jobs via REST API:

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Service health status |
| `GET /status` | Overall ingestion status (symbols, timeframes, candle counts) |
| `GET /gaps` | List detected gaps (repaired and unrepaired) |
| `GET /jobs` | List backfill/repair job history |

**Examples**:
```bash
# Check health
curl http://localhost:8100/health

# Get current status
curl http://localhost:8100/status

# List unrepaired gaps
curl "http://localhost:8100/gaps?repaired=false"

# List recent jobs
curl "http://localhost:8100/jobs?limit=20"
```

### Database Tables

Track scheduled job execution:

- **`ingestion_jobs`**: Job records (backfill, gap_repair, etc.)
  - Columns: `id`, `exchange`, `symbol`, `timeframe`, `job_type`, `status`, `started_at`, `completed_at`, `candles_fetched`, `last_error`
  - Query recent jobs: `SELECT * FROM ingestion_jobs ORDER BY started_at DESC LIMIT 10;`

- **`data_gaps`**: Detected gaps
  - Columns: `id`, `exchange`, `symbol`, `timeframe`, `gap_start`, `gap_end`, `detected_at`, `repaired_at`
  - Query unrepaired gaps: `SELECT * FROM data_gaps WHERE repaired_at IS NULL;`

---

## Deployment

### Systemd Service

The daemon runs as a systemd service (`/etc/systemd/system/market-data.service`):

```bash
# Start service
sudo systemctl start market-data

# Enable auto-start on boot
sudo systemctl enable market-data

# View status
sudo systemctl status market-data

# View logs
journalctl -u market-data -f

# Restart service
sudo systemctl restart market-data
```

**Service configuration**: See `systemd/market-data.service`

### Manual Run (Development)

```bash
# Activate virtualenv
source .venv/bin/activate

# Run daemon
python -m market_data.daemon
```

---

## Why Not Cron/Systemd Timers?

While the original issue mentioned systemd timers/cron, the **long-running daemon architecture is superior** for this use case:

### Advantages of Daemon Approach:

1. **No startup overhead**: Each cron run would need to:
   - Initialize Python interpreter
   - Load dependencies
   - Connect to database
   - Initialize exchange adapters
   - This adds 2-5 seconds per run

2. **State retention**: 
   - WebSocket connections stay alive
   - Rate limiter maintains global state
   - Database connection pooling
   - No redundant API calls on each run

3. **Real-time ingestion**:
   - WebSocket subscriptions require persistent connection
   - Cannot be done with cron/timers

4. **Flexible scheduling**:
   - Async loops can adjust timing dynamically
   - Gap detection can be throttled based on backlog
   - Intervals can be changed without modifying systemd timers

5. **Simpler deployment**:
   - Single systemd service
   - Single log stream
   - Easier to manage

### When to Use Systemd Timers:

Systemd timers would be appropriate for:
- One-off administrative tasks
- Infrequent operations (e.g., weekly reports)
- Independent jobs that don't share state
- Jobs that should run even if daemon is stopped

For this service, **the daemon approach is the correct choice** and fully implements the requirements.

---

## Configuration Summary

**Minimal production config** (`.env`):
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/marketdata

# Exchanges
BITFINEX_SYMBOLS=BTCUSD,ETHUSD,SOLUSD
BITFINEX_TIMEFRAMES=1h,4h,1d

# Scheduling
BACKFILL_ON_STARTUP=true
BACKFILL_DAYS=365
GAP_REPAIR_INTERVAL_MINUTES=60
GAP_DETECTION_INTERVAL_MINUTES=60
GAP_REPAIR_MAX_REPAIRS_PER_RUN=10

# WebSocket (prevents new gaps)
WS_INGESTION_ENABLED=true
WS_CATCHUP_LOOKBACK_MINUTES=180

# REST update (usually disabled when WS enabled)
REST_UPDATE_ENABLED=false
```

**Full configuration**: See `.env.example` and `src/market_data/config.py`

---

## Related Files

- `src/market_data/daemon.py` - Main daemon and scheduling loops
- `src/market_data/services/gap_repair.py` - Gap detection and repair logic
- `src/market_data/services/backfill.py` - Backfill and update logic
- `src/market_data/config.py` - Configuration settings
- `systemd/market-data.service` - Systemd service definition
- `src/market_data/rate_limiter.py` - Global rate limiting

---

## Issue Resolution

This implementation fully satisfies the acceptance criteria from issues #185 and #179:

- ✅ **Periodic backfill runs without manual triggers**: Implemented via `run_backfill()` on startup and optional `run_update_loop()`
- ✅ **Gap repair runs on a configurable cadence**: Implemented via `run_gap_repair_loop()` with `GAP_REPAIR_INTERVAL_MINUTES`
- ✅ **Jobs are observable (logs + basic health signal)**: Comprehensive logging + REST API endpoints (`/health`, `/status`, `/gaps`, `/jobs`)
- ✅ **Rate limits respected with backoff**: Global rate limiter with exponential backoff and configurable delays

The daemon architecture provides superior scheduling compared to cron/systemd timers for this real-time data ingestion use case.
