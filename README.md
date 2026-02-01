# Market Data Service

Standalone microservice for continuous market data ingestion. Fetches OHLCV candles from crypto exchanges and stores them in PostgreSQL.

**Status**: ✅ Running in production

## Features

- **Historical Backfill**: Fetch and store historical candles from exchanges
- **Gap Detection & Repair**: Automatically detect and fill missing data
- **REST API**: Query candles, status, and health (port 8100)
- **Rate Limit Compliant**: Respects exchange API limits (~40 req/min for Bitfinex)
- **Multi-Exchange**: Pluggable exchange adapters (Bitfinex implemented)

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your DATABASE_URL

# Run daemon
python -m market_data.daemon
```

## Configuration

Environment variables (`.env`):

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/cryptotrader
API_HOST=0.0.0.0
API_PORT=8100

# Exchanges
BITFINEX_SYMBOLS=BTCUSD,ETHUSD,SOLUSD
BITFINEX_TIMEFRAMES=1h,4h,1d

# Daemon
BACKFILL_ON_STARTUP=true
BACKFILL_DAYS=365
GAP_REPAIR_INTERVAL_MINUTES=60
UPDATE_INTERVAL_SECONDS=60
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/status` | GET | Ingestion status (symbols, timeframes, candle counts) |
| `/candles` | GET | Query candles with filters |
| `/candles/latest` | GET | Get N most recent candles |
| `/gaps` | GET | List detected data gaps |
| `/jobs` | GET | List backfill/repair jobs |

### Example Queries

```bash
# Health check
curl http://localhost:8100/health

# Get status
curl http://localhost:8100/status

# Get latest BTC candles
curl "http://localhost:8100/candles?symbol=BTCUSD&timeframe=1h&limit=10"
```

## Architecture

```
market-data/
├── src/market_data/
│   ├── api/              # FastAPI REST endpoints
│   │   ├── main.py       # App factory
│   │   └── routes/       # Route handlers
│   ├── exchanges/        # Exchange adapters
│   │   ├── base.py       # Abstract interface
│   │   └── bitfinex.py   # Bitfinex implementation
│   ├── services/         # Business logic
│   │   ├── backfill.py   # Historical data fetching
│   │   └── gap_repair.py # Gap detection & repair
│   ├── storage/          # Persistence layer
│   │   ├── postgres.py   # PostgreSQL operations
│   │   └── schema.sql    # DB schema
│   ├── config.py         # Pydantic settings
│   ├── types.py          # Data models
│   └── daemon.py         # Main entry point
└── tests/
```

## Rate Limiting

Bitfinex API limits: 10-90 requests/minute depending on endpoint.

Our implementation:
- 1.5s delay between requests (~40 req/min)
- Exponential backoff on 429 responses (1s → 60s max)
- Respects 60s block duration on rate limit violations

## Database Schema

Uses shared PostgreSQL with cryptotrader. Tables:
- `candles` - OHLCV data
- `data_gaps` - Detected gaps for repair
- `ingestion_jobs` - Backfill/repair job tracking

## Running as Service

```bash
# Systemd (create service file)
sudo systemctl enable market-data
sudo systemctl start market-data

# Or with nohup
nohup python -m market_data.daemon > /var/log/market-data.log 2>&1 &
```

## License

MIT
