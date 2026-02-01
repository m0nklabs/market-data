"""Status and health check routes."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from market_data.storage.postgres import PostgresStorage

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/status")
def get_status():
    """Get ingestion status summary."""
    storage = PostgresStorage()
    status = storage.get_ingestion_status()
    
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **status,
    }


@router.get("/jobs")
def get_recent_jobs(limit: int = 20):
    """Get recent ingestion jobs."""
    storage = PostgresStorage()
    jobs = storage.get_recent_jobs(limit=limit)
    
    return {
        "jobs": [
            {
                "id": job.id,
                "exchange": job.exchange,
                "symbol": job.symbol,
                "timeframe": job.timeframe,
                "job_type": job.job_type,
                "status": job.status,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "candles_fetched": job.candles_fetched,
                "last_error": job.last_error,
            }
            for job in jobs
        ]
    }


@router.get("/gaps")
def get_gaps():
    """Get unrepaired gaps."""
    storage = PostgresStorage()
    gaps = storage.get_unrepaired_gaps()
    
    return {
        "gaps": [
            {
                "id": gap.id,
                "exchange": gap.exchange,
                "symbol": gap.symbol,
                "timeframe": gap.timeframe,
                "gap_start": gap.gap_start.isoformat(),
                "gap_end": gap.gap_end.isoformat(),
                "detected_at": gap.detected_at.isoformat() if gap.detected_at else None,
            }
            for gap in gaps
        ],
        "total": len(gaps),
    }
