-- Market Data Service Schema
-- PostgreSQL 14+

-- Candles table (partitioned by exchange for scalability)
CREATE TABLE IF NOT EXISTS candles (
    id BIGSERIAL,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    open_time TIMESTAMPTZ NOT NULL,
    close_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(24, 8) NOT NULL,
    high DECIMAL(24, 8) NOT NULL,
    low DECIMAL(24, 8) NOT NULL,
    close DECIMAL(24, 8) NOT NULL,
    volume DECIMAL(24, 8) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (exchange, symbol, timeframe, open_time)
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_candles_symbol_timeframe_time 
    ON candles (symbol, timeframe, open_time DESC);

CREATE INDEX IF NOT EXISTS idx_candles_open_time 
    ON candles (open_time DESC);

-- Gap tracking table
CREATE TABLE IF NOT EXISTS candle_gaps (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    gap_start TIMESTAMPTZ NOT NULL,
    gap_end TIMESTAMPTZ NOT NULL,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    repaired_at TIMESTAMPTZ,
    UNIQUE (exchange, symbol, timeframe, gap_start, gap_end)
);

CREATE INDEX IF NOT EXISTS idx_gaps_unrepaired 
    ON candle_gaps (exchange, symbol, timeframe) 
    WHERE repaired_at IS NULL;

-- Ingestion job tracking
CREATE TABLE IF NOT EXISTS ingestion_jobs (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    job_type VARCHAR(20) NOT NULL,  -- backfill, realtime, gap_repair
    status VARCHAR(20) NOT NULL DEFAULT 'running',  -- running, success, failed
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    candles_fetched INTEGER DEFAULT 0,
    last_error TEXT
);

CREATE INDEX IF NOT EXISTS idx_jobs_status 
    ON ingestion_jobs (status, started_at DESC);

-- Ingestion state tracking (for resumable backfill)
CREATE TABLE IF NOT EXISTS ingestion_state (
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    last_candle_time TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (exchange, symbol, timeframe)
);
