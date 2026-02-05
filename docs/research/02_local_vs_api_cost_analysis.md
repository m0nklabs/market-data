# 02 — Local vs API Cost Analysis

## Summary
This document compares API pricing against local inference electricity costs for a 27GB VRAM constraint. It uses current vendor price sheets and a simple energy cost model based on GPU power draw.

---

## API Pricing Snapshot (Feb 2026)

| Model | Input $/1M | Output $/1M | Blended $/1M (3:1) | Intelligence Score | Notes |
| --- | --- | --- | --- | --- | --- |
| GPT-5.2 Pro (400k context tier) | $15.00 | $60.00 | $4.81 | 51 | Top quality, expensive |
| Claude Opus 4.5 | $15.00 | $75.00 | $10.00 | 50 | Slow (1.7 t/s), very expensive |
| Gemini 3 Flash | ~$0.50 | ~$1.50 | $1.13 | 46 | Fast, cheap, large context |
| Kimi K2.5 | ~$0.90 | ~$2.00 | $1.20 | 47 | Good value |
| **DeepSeek V3.2** | $0.28 (miss) / $0.028 (hit) | $0.42 | **$0.32** | 42 | **Best budget API** |
| Qwen3 Max (Thinking) | ~$1.80 | ~$4.00 | $2.40 | 40 | Good local-comparable |

**Key insight:** DeepSeek V3.2 is ~15× cheaper than GPT-5.2 Pro with only ~18% lower intelligence score.
**Pricing note:** GPT-5.2 Pro pricing reflects the 400k context tier; adjust if a lower tier is used.
**Blended cost formula:** Blended $/1M assumes a 3:1 input-to-output ratio (0.75 × input + 0.25 × output).

---

## Local Energy Cost Model (27GB VRAM rigs)
Assumptions:
- Electricity price: **$0.165/kWh** (US average 2024 benchmark; adjust to your current local rate).
- Power draw from GPU/system TDP.
- Hourly cost = (Watts / 1000) × $/kWh.

| Rig | Power draw (W) | Cost per hour (USD) | Tokens/sec (est.) | Notes |
| --- | --- | --- | --- | --- |
| RTX 3090 workstation | 350W | $0.058/hr | 8–15 t/s | Q5_K_M Qwen3-32B |
| RTX 4090 workstation | 450W | $0.074/hr | 15–25 t/s | Faster inference |
| Mac Studio (M2 Ultra) | 295W | $0.049/hr | 10–18 t/s | Unified memory advantage |

---

## Hourly TA Workload Cost (1,000+ OHLCV candles)

**Assumptions:**
- 1,000 candles × 40 tokens per candle ≈ 40,000 input tokens.
- 5,000 output tokens for analysis summary.
- Total: 45,000 tokens per run.

### API Cost per Workload

| Model | Cost per run | Runs per $1 | Notes |
| --- | --- | --- | --- |
| GPT-5.2 Pro | ~$1.68 | 0.6 | Expensive for batch TA |
| Claude Opus 4.5 | ~$2.00 | 0.5 | Very expensive |
| Gemini 3 Flash | ~$0.05 | 20 | Good batch option |
| **DeepSeek V3.2** | **~$0.014** | **71** | Best for high-volume TA |
| Kimi K2.5 | ~$0.05 | 20 | Similar to Gemini |

### Local Inference Cost per Workload

| Rig | Time per run (est.) | Cost per run | Runs per $1 | Notes |
| --- | --- | --- | --- | --- |
| RTX 3090 (Q5_K_M 32B) | ~8 min | ~$0.008 | 125 | Cheapest if you own hardware |
| RTX 4090 (Q5_K_M 32B) | ~5 min | ~$0.006 | 167 | Faster |
| Mac Studio (M2 Ultra) | ~6 min | ~$0.005 | 200 | Best efficiency |

**Break-even analysis:** Local inference beats API cost if you run >10 workloads/day over a year (amortizing ~$2,000 GPU cost).

---

## Token Usage Profiling (pending)
Actual token counts vary with formatting. Before finalizing cost models, run a token count on representative OHLCV payloads:
- CSV row-per-candle
- JSON array of objects
- Compact key-value format

Record input/output token counts for each formatting style and update the assumptions in this doc.

---

## Recommendation by Use Case

| Use Case | Recommended | Rationale |
| --- | --- | --- |
| **Low volume (<50 runs/day)** | DeepSeek V3.2 API | Cheapest API, no hardware cost |
| **High volume (>100 runs/day)** | Local (RTX 4090 + Qwen3-32B) | Lower marginal cost, full privacy |
| **Best quality (cost insensitive)** | GPT-5.2 Pro or Claude Opus 4.5 | Top benchmark scores |
| **Balanced quality/cost** | Gemini 3 Flash or Kimi K2.5 | Good score, low price |

---

## Sources Appendix (accessed 2026-02-05)

| Source | Relevance |
| --- | --- |
| https://artificialanalysis.ai/leaderboards/models | Current API pricing and intelligence scores |
| https://openai.com/api/pricing/ | GPT-5.2 Pro API pricing reference |
| https://api-docs.deepseek.com/quick_start/pricing/ | DeepSeek V3.2 API pricing and caching tiers |
| https://www.statista.com/statistics/200197/average-retail-price-of-electricity-in-the-us-by-sector-since-1998/ | US average electricity price reference |
| https://www.techpowerup.com/gpu-specs/geforce-rtx-3090.c3622 | RTX 3090 power specification |
| https://nvidia.custhelp.com/app/answers/detail/a_id/5396/ | RTX 4090 power specification |
| https://support.apple.com/en-us/102027 | Mac Studio power consumption reference |
