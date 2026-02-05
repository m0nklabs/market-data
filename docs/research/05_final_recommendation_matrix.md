# 05 — Final Recommendation Matrix

## TL;DR — Which Model Is Best?

| Use Case | Best Model | Runner-Up | Notes |
| --- | --- | --- | --- |
| **Trading/TA (production)** | **Kimi-K2** | Qwen3-235B-Ins | Best StockBench composite score |
| **Finance reasoning** | **Claude Opus 4** | o3 | Top FinanceArena Elo (1,093) |
| **Assumption-based analysis** | **o3** | Claude Opus 4 | o3 leads at 21.7% accuracy |
| **Budget API** | **DeepSeek V3.2** | Gemini 3 Flash | Best $/quality ratio |
| **Local inference (27GB)** | **Gemma 3 27B Q6_K** | Qwen3-32B Q5_K_M | Fits with KV cache headroom |
| **Balanced quality/cost** | **Gemini 3 Flash** | Kimi K2.5 | Good scores @ ~$1/M |

---

## Decision Matrix (Detailed)

| Model | Trading (StockBench) | Finance (FinanceArena) | Intelligence | Cost ($/M) | Speed (t/s) | Privacy | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Kimi-K2** | 🥇 Rank 1 | Mid | 47 | $1.20 | 0.8 | Low | **Best for trading** |
| **Claude Opus 4** | 🥉 Rank 7 | 🥇 Elo 1,093 | 50 | $10.00 | 1.7 | Low | **Best for finance reasoning** |
| **o3** | Rank 5 | 🥇 54.1% overall | 41 | $3.50 | 15 | Low | **Best assumption-based** |
| GPT-5.2 Pro | Rank 9 | Mid | 51 | $4.81 | 37 | Low | Top intelligence, weak trading |
| **DeepSeek V3.2** | Rank 8 | Mid | 42 | **$0.32** | 1.3 | Low | **Best budget** |
| Qwen3-235B-Ins | 🥈 Rank 2 | Low-Mid | 32 | $1.23 | 1.2 | Low | Strong trading |
| Gemini 3 Flash | N/A | Low | 46 | $1.13 | 13 | Low | Fast, cheap |
| **Local Gemma 3 27B** | N/A | N/A | ~25 | ~$0.005/run | 15 | 🥇 High | **Best privacy** |
| **Local Qwen3-32B** | N/A | N/A | ~30 | ~$0.008/run | 12 | 🥇 High | Better reasoning |

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
│  └── Kimi-K2 or Qwen3-235B-Ins                              │
│      • Best StockBench scores                               │
│      • Use for entry/exit decisions                         │
│                                                             │
│  [Edge Cases & Risk Analysis]                               │
│  └── Claude Opus 4 or o3                                    │
│      • Best assumption-based reasoning                      │
│      • Use sparingly (expensive)                            │
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
