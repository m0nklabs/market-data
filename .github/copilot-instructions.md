# Repository custom instructions (Copilot)

These instructions apply to GitHub Copilot in the context of this repository.

## Project Overview

- **Repo name**: market-data
- **Purpose**: Standalone microservice for OHLCV candle ingestion from cryptocurrency exchanges
- **Primary exchange**: Bitfinex (REST API)
- **Storage**: PostgreSQL (shared with cryptotrader)

## Host: ai-kvm2 Port Management

When running on host **ai-kvm2** (192.168.1.6):
- **ALWAYS** update `/home/flip/caramba/docs/PORTS.md` when claiming or changing a port
- This is the authoritative port inventory for all projects on this server
- Check for conflicts before assigning new ports

### Project-Specific Ports

| Service | Port | Description |
|---------|------|-------------|
| market-data API | 8100 | FastAPI daemon (OHLCV ingestion, gap repair) |
| PostgreSQL | 5432 | Shared database (Docker container on cryptotrader) |

## Technical Stack

- **Python**: 3.12+
- **Framework**: FastAPI
- **HTTP Client**: httpx (async)
- **Database**: asyncpg / SQLAlchemy 2.0
- **Rate Limiting**: Global singleton with exponential backoff (~30 req/min for Bitfinex)

## Key Components

- `src/market_data/daemon.py` - Main daemon entry point
- `src/market_data/exchanges/bitfinex.py` - Bitfinex REST API client
- `src/market_data/services/gap_repair.py` - Automatic gap detection and repair
- `src/market_data/rate_limiter.py` - Global rate limiter (thread-safe singleton)

## Systemd Service

The daemon runs as a systemd service:
- Service file: `/etc/systemd/system/market-data.service`
- Source: `systemd/market-data.service`
- User: flip
- Auto-restart on failure

Commands:
```bash
sudo systemctl status market-data
sudo systemctl restart market-data
journalctl -u market-data -f
```

## Engineering Rules

- Respect Bitfinex rate limits (~40 requests/minute)
- Use the global rate limiter for all API calls
- Handle gaps gracefully - don't fail on missing data
- Log all API errors with full context
- Never commit secrets - use environment variables

## Safety

- This service only reads data, no trading functionality
- Database writes are INSERT-only for candles (no updates/deletes)
- Gap repair is non-destructive (skips existing candles)
