# 02 — Local vs API Cost Analysis

## Summary
This document compares API pricing against local inference electricity costs for a 27GB VRAM constraint. It uses vendor price sheets for GPT-5.2 Pro and DeepSeek V3.2, and a simple energy cost model based on GPU power draw.

## API Pricing Snapshot

| Model | Input $/1M tokens | Output $/1M tokens | Notes |
| --- | --- | --- | --- |
| GPT-5.2 Pro | $21.00 | $168.00 | Frontier model pricing (API). |
| DeepSeek V3.2 | $0.28 (cache miss), $0.028 (cache hit) | $0.42 | Low-cost API option with caching. |

## Local Energy Cost Model (27GB VRAM rigs)
Assumptions:
- Electricity price: **$0.165/kWh** (US average in 2024).
- Power draw is approximated from GPU/system TDP.
- Hourly cost = (Watts / 1000) × $/kWh.

| Rig | Power draw (W) | Cost per hour (USD) | Notes |
| --- | --- | --- | --- |
| RTX 3090 workstation | 350W | $0.058/hr | 350W TDP reference. |
| RTX 4090 workstation | 450W | $0.074/hr | 450W TDP reference. |
| Mac Studio (M2 Ultra) | 295W | $0.049/hr | Max power draw estimate. |

## Hourly TA Workload Cost (1,000+ OHLCV candles)
**Assumptions (adjust as needed):**
- 1,000 candles × 40 tokens per candle ≈ 40,000 input tokens.
- 5,000 output tokens for analysis summary.

**Estimated API cost per workload:**
- GPT-5.2 Pro: **~$1.68** per run (40k input + 5k output).
- DeepSeek V3.2: **~$0.013** per run (cache miss rates).

**Local inference cost per workload:**
- If a run takes 1 hour, cost is the hourly energy price above.
- If a run takes 10 minutes, divide hourly cost by 6 (e.g., 3090 ≈ $0.010/run).

## Notes for Updating
- Recompute with actual prompt tokenization once the prompt template is finalized.
- Capture actual throughput (tokens/sec) from inference logs to replace the runtime assumptions.

## Sources Appendix (accessed 2026-02-05)

| Source | Relevance |
| --- | --- |
| https://openai.com/api/pricing/ | GPT-5.2 Pro API pricing reference. |
| https://api-docs.deepseek.com/quick_start/pricing/ | DeepSeek V3.2 API pricing and caching tiers. |
| https://www.statista.com/statistics/200197/average-retail-price-of-electricity-in-the-us-by-sector-since-1998/ | US average electricity price reference (2024). |
| https://www.techpowerup.com/gpu-specs/geforce-rtx-3090.c3622 | RTX 3090 power specification. |
| https://nvidia.custhelp.com/app/answers/detail/a_id/5396/~/geforce-rtx-40-series-%26-power-specifications | RTX 4090 power specification. |
| https://support.apple.com/en-us/102027 | Mac Studio power consumption reference. |
