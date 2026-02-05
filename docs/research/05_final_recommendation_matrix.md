# 05 — Final Recommendation Matrix

## TL;DR — Which Model Is Best?

| Use Case | Best Model | Runner-Up | Notes |
| --- | --- | --- | --- |
| **Live Execution / Online** | **DeepSeek-R1** | QuantAgent | #1 in BizFinBench Online Tasks |
| **General Intelligence** | **GPT-5** | Claude Opus 4.5 | #1 Static QA (61.5% acc) |
| **Finance Reasoning** | **o3** | Gemini 2.0 Flash | #1 Pure Reasoning (83.6 score) |
| **Trading/TA** | **DeepSeek-R1** | Kimi-K2 | Strongest numerical calc & info extraction |
| **Budget API** | **DeepSeek V3.2** | Gemini 3 Flash | $0.32/M (DeepSeek) is unbeaten |
| **Fast + cheap** | **Gemini 3 Flash** | Gemini 3 Pro | 46 score @ $1.13/M |
| **Local (27GB)** | **Gemma 3 27B** | Qwen3-32B | Best verified local fit |

---

## Decision Matrix (Detailed)

| Model | Intelligence | Finance Leaderboard | Trading | Cost ($/M) | Verdict |
| --- | --- | --- | --- | --- | --- |
| **DeepSeek-R1** | 🥇 High | **#1 Live/Online** | **Best** | ~$0.55 | **Best for Execution** |
| **GPT-5** | 🥇 61.5% Acc | High | Mid | $4.81 | **Top General Intelligence** |
| **o3** | High | **#1 Reasoning** | Mid | $3.50 | **Best Risk/Reasoning** |
| **Claude Opus 4.5** | High | #2 Elo | — | $10.00 | Strong traditional reasoning |
| **Kimi-K2** | 47 | Mid | #1 StockBench | $1.20 | Good trading baselines |
| **DeepSeek V3.2** | 42 | Mid | — | **$0.32** | **Best Budget** |
| Gemini 3 Flash | 46 | Low | — | $1.13 | Fast volume processor |
| **Local Gemma 3** | ~25 | — | — | >$0.01 | **Best Privacy** |

---

## Key Insights

### 1. "Live" Performance Matters More Than "Static"
Benchmarks like **BizFinBench.v2** and **DeepFund** reveal that models excellent at static exams (GPT-5, Claude-3.7) can fail in live trading. **DeepSeek-R1** is currently the only model showing consistent robustness in live/online financial tasks.

### 2. DeepSeek-R1 is the Reasoning & Execution King
It leads in "Information Extraction" (crucial for reading news/docs) and "Numerical Calculation" (crucial for TA).

### 3. DeepSeek V3.2 Is the Value Champion
For bulk processing where reasoning depth is less critical, V3.2 allows for massive scale at $0.32/M.

### 4. Local Models Are Viable for High Volume
At >100 runs/day, local inference (Gemma 3 27B on RTX 4090) costs ~$0.006/run vs. $0.014/run for DeepSeek V3.2.

---

## Recommended Strategy: Hybrid Approach

```
┌─────────────────────────────────────────────────────────────┐
│                    RECOMMENDED ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Batch TA & Signal Detection]                              │
│  └── DeepSeek-R1 or DeepSeek V3.2                           │
│      • R1: Best for live online tasks & calc                │
│      • V3.2: Ultra-cheap for massive pre-filtering          │
│                                                             │
│  [Complex Trade Decisions]                                  │
│  └── DeepSeek-R1                                            │
│      • Outperforms commercial models in BizFinBench Live    │
│      • Strongest numerical calculation capabilities         │
│                                                             │
│  [Edge Cases & Risk Analysis]                               │
│  └── o3 or GPT-5                                            │
│      • o3: #1 in complex reasoning scenarios                │
│      • GPT-5: Deepest general financial knowledge base      │
│                                                             │
│  [Deterministic Validation Layer]                           │
│  └── QuantAgent Framework (Pattern/Trend Agents)            │
│      • Use specialized agents for specific patterns         │
│      • Don't rely on one single prompt                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Sources Appendix (accessed 2026-02-05)

| Source | Relevance |
| --- | --- |
| **BizFinBench.v2** | Leaderboard for Live/Online financial tasks (DeepSeek-R1 wins). |
| **DeepFund** | Live trading arena demonstrating "backtest vs reality" gap. |
| **StockBench** | Trading agent profitability benchmarks. |
