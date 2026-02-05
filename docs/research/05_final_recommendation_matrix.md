# 05 — Final Recommendation Matrix

## TL;DR — Which Model Is Best?

| Use Case | Best Model | Runner-Up | Notes |
| --- | --- | --- | --- |
| **Highest intelligence** | **GPT-5.2 (xhigh)** | Claude Opus 4.5 | AA score 51 vs 50 |
| **Finance reasoning** | **Claude Opus 4.5** | o3 | Top FinanceArena Elo (1,093) |
| **Trading/TA** | **Kimi-K2** | Qwen3-235B-Ins | Best trading benchmark |
| **Assumption-based** | **o3** | Claude Opus 4.5 | 21.7% accuracy (highest) |
| **Budget API** | **DeepSeek V3.2** | Gemini 3 Flash | $0.32/M, score 42 |
| **Fast + cheap** | **Gemini 3 Flash** | Gemini 3 Pro | 46 score @ $1.13/M, 13 t/s |
| **Local (27GB)** | **Gemma 3 27B Q6_K** | Qwen3-32B Q5_K_M | Best VRAM fit |

---

## Decision Matrix (Detailed)

| Model | Intelligence | Finance Elo | Trading | Cost ($/M) | Speed (t/s) | Context | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **GPT-5.2 (xhigh)** | 🥇 51 | Mid | — | $4.81 | 37 | 400K | **Top intelligence** |
| **Claude Opus 4.5** | 🥈 50 | 🥇 1,093 | — | $10.00 | 1.7 | 200K | **Best finance reasoning** |
| **Gemini 3 Pro** | 48 | Mid | — | $4.50 | 32 | 1M | Large context |
| **Kimi-K2.5** | 47 | Mid | — | $1.20 | 0.8 | 256K | Great value |
| **Gemini 3 Flash** | 46 | Low | — | $1.13 | 13 | 1M | **Fast + cheap** |
| Claude 4.5 Sonnet | 43 | High | — | $6.00 | 1.2 | 1M | Mid-tier Anthropic |
| **DeepSeek V3.2** | 42 | Mid | — | **$0.32** | 1.3 | 128K | **Best budget** |
| **o3** | 41 | 🥇 54.1% | — | $3.50 | 15 | 200K | Best assumption-based |
| Kimi K2 Thinking | 41 | Mid | — | $1.07 | 0.6 | 256K | Cheap reasoning |
| **Kimi-K2** | 47 | Mid | 🥇 #1 | $1.20 | 0.8 | 256K | **Best for trading** |
| Qwen3-235B-Ins | 32 | Low | 🥈 #2 | $1.23 | 1.2 | 256K | Trading runner-up |
| **Local Gemma 3 27B** | ~25 | — | — | ~$0.005/run | 15 | 128K | **Best privacy** |
| **Local Qwen3-32B** | ~30 | — | — | ~$0.008/run | 12 | 32K | Better local reasoning |

---

## Key Insights

### 1. Trading Performance ≠ General Intelligence
GPT-5.2 has the highest intelligence score (51) but ranks **9th** on StockBench. Kimi-K2 (score 47) ranks **1st**. Trading success requires different skills than general reasoning.

### 2. Claude Opus 4 Dominates Finance Reasoning
On FinanceArena's FinanceCompare Elo (human preference for finance tasks), Claude Opus 4 leads at 1,093 — GPT-5 is at 953 (rank 15).

### 3. Reasoning Models Underperform on Trading
"Thinking" models (Qwen3-235B-Think, o3) don't consistently beat instruct variants on trading tasks. They also have higher schema error rates.

### 4. DeepSeek V3.2 Is the Value Champion
At $0.32/M tokens with a 42 intelligence score, it's ~15× cheaper than GPT-5.2 Pro with only 18% lower quality.

### 5. Local Models Are Viable for High Volume
At >100 runs/day, local inference (Gemma 3 27B on RTX 4090) costs ~$0.006/run vs. $0.014/run for DeepSeek V3.2.

---

## Recommended Strategy: Hybrid Approach

```
┌─────────────────────────────────────────────────────────────┐
│                    RECOMMENDED ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Batch TA & Signal Detection]                              │
│  └── DeepSeek V3.2 or Local Qwen3-32B                       │
│      • High volume, low cost                                │
│      • ~$0.01–0.03 per 1000 candles                        │
│                                                             │
│  [Complex Trade Decisions]                                  │
│  └── Kimi-K2 or GPT-5.2 (xhigh)                             │
│      • Kimi-K2: Best trading benchmark                      │
│      • GPT-5.2: Highest general intelligence (51)           │
│                                                             │
│  [Edge Cases & Risk Analysis]                               │
│  └── Claude Opus 4.5 or o3                                  │
│      • Best finance reasoning (Elo 1,093)                   │
│      • o3: Top assumption-based accuracy (21.7%)            │
│                                                             │
│  [Fast Prototyping / High Volume]                           │
│  └── Gemini 3 Flash                                         │
│      • 46 intelligence @ $1.13/M, 13 t/s                    │
│      • 1M context for huge analysis sets                    │
│                                                             │
│  [Deterministic Validation Layer]                           │
│  └── Rule-based checks on all LLM outputs                   │
│      • Catch hallucinations                                 │
│      • Verify calculations                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Sources Appendix (accessed 2026-02-05)

| Source | Relevance |
| --- | --- |
| https://www.financearena.ai/ | FinanceQA and FinanceCompare Elo leaderboards |
| https://arxiv.org/html/2510.02209v1 | StockBench trading profitability benchmark |
| https://artificialanalysis.ai/leaderboards/models | Intelligence/cost/speed comparisons |
| https://openai.com/api/pricing/ | Frontier model cost reference |
| https://api-docs.deepseek.com/quick_start/pricing/ | DeepSeek pricing |
