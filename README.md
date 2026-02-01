# Market Data Service

Continuous market data ingestion service for crypto OHLCV candles.

## Features

- **Historical Backfill**: Fetch and store historical candles from exchanges
- **Realtime Streaming**: WebSocket-based live candle updates
- **Gap Detection & Repair**: Automatically detect and fill missing data
- **REST API**: Query candles, status, and health
- **Multi-Exchange**: Pluggable exchange adapters (Bitfinex first)

## Quick Start

\`\`\`bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your DATABASE_URL

# Initialize database
python -m market_data.storage.init_db

# Run daemon
python -m market_data.daemon
\`\`\`

## Configuration

Environment variables (\`.env\`):

\`\`\`bash
DATABASE_URL=postgresql://user:pass@localhost:5432/marketdata
API_HOST=0.0.0.0
API_PORT=8100

# Exchanges
BITFINEX_SYMBOLS=BTCUSD,ETHUSD,SOLUSD
BITFINEX_TIMEFRAMES=1m,5m,1h,1d

# Daemon
BACKFILL_ON_STARTUP=true
BACKFILL_DAYS=365
GAP_REPAIR_INTERVAL_MINUTES=60
\`\`\`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| \`/health\` | GET | Health check |
| \`/status\` | GET | Ingestion status |
| \`/candles\` | GET | Query candles |
| \`/candles/latest\` | GET | Get N most recent |
| \`/gaps\` | GET | List detected gaps |

## License

MIT
