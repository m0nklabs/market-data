# 01 — Market Leaderboards 2026

## Scope
This document captures the most relevant leaderboards for financial reasoning, technical analysis (TA), and trading agent benchmarks. It prioritizes finance-specific leaderboards (FinanceArena, StockBench) and cross-references general reasoning benchmarks used to compare frontier and local models.

---

## Model Name Glossary
- **GPT-5**: Benchmark name used in StockBench/BizFinBench; **GPT-5.2 Pro** is the current API pricing tier.
- **o3**: OpenAI reasoning model used in several benchmark leaderboards.
- **o3-mini**: Cost-reduced o3 variant for lower-latency/price tiers.
- **Claude Opus 4 / 4.5**: Anthropic releases; 4.5 refers to the newest Opus tier.
- **DeepSeek V3.1 / V3.2**: V3.1 appears in older benchmark snapshots; V3.2 is the current API release.
- **Qwen2.5-30B-A3B**: MoE model with ~3B active parameters; distinct from Qwen3 dense models.

---

## FinanceArena Leaderboards (snapshot 2026-02-05)

### FinanceQA Leaderboard (accuracy on professional finance tasks)

| Model | Overall | Basic Tactical | Assumption-Based | Conceptual |
| --- | --- | --- | --- | --- |
| **o3** | 🥇 54.1% | 🥇 55.3% | 🥇 21.7% | 🥇 76.6% |
| Grok 4 | 🥈 49.3% | 🥈 52.6% | 🥉 10.9% | 🥈 75.0% |
| o3-mini | 🥉 48.6% | 🥈 52.6% | 8.7% | 🥈 75.0% |
| Gemini 2.5 Pro | 45.3% | 🥇 55.3% | 6.5% | 67.2% |
| Llama 4 Maverick | 44.6% | 39.5% | 8.7% | 🥉 73.4% |
| **Claude Opus 4** | 44.6% | 44.7% | 🥈 13.0% | 67.2% |
| Grok 3 | 44.6% | 47.4% | 8.7% | 68.8% |
| Claude Sonnet 4 | 43.9% | 🥈 52.6% | 6.5% | 65.6% |
| Phi 4 Reasoning Plus | 43.2% | 39.5% | 8.7% | 70.3% |
| DeepSeek-R1-0528 | 42.9% | 🥉 50.0% | 6.5% | 65.1% |
| QwQ-32B | 42.6% | 44.7% | 🥉 10.9% | 64.1% |
| GPT-4.1 Mini | 41.9% | 39.5% | 🥉 10.9% | 65.6% |
| Qwen2.5-30B-A3B | 37.2% | 42.1% | 2.2% | 59.4% |
| Gemini 2.5 Flash | 32.4% | 31.6% | 6.5% | 51.6% |

**Key insight:** Assumption-Based accuracy (the hardest category) is <22% even for the best model; Claude Opus 4 ranks #2 on this category (13%).

### FinanceCompare Elo Leaderboard (pairwise preference on finance reasoning)

| Rank | Model | Elo |
| --- | --- | --- |
| 1 | **Claude Opus 4** | 1,093 |
| 2 | Llama 4 Maverick | 1,058 |
| 3 | Gemini 2.5 Flash | 1,054 |
| 4 | Phi 4 | 1,039 |
| 5 | DeepSeek V3.1 (FinanceArena snapshot) | 1,038 |
| 6 | Claude Sonnet 4 | 1,018 |
| 7 | Claude Opus 4.1 | 1,017 |
| 8 | GPT-4o | 1,004 |
| 11 | Grok 4 | 982 |
| 13 | o3 | 970 |
| 15 | GPT-5 | 953 |
| 16 | Gemini 2.5 Pro | 940 |

**Key insight:** Claude Opus 4 leads the Elo ranking for finance reasoning preference, but GPT-5 trails significantly (rank 15).
**Note:** Models like **o3** may rank high in one leaderboard (FinanceQA) and lower in another (FinanceCompare) because the datasets and scoring methods differ.

---

## StockBench (Real-World Trading Profitability)

StockBench evaluates LLM trading agents on 4-month DJIA trading. Metrics: cumulative return, max drawdown (MDD), Sortino ratio. Baseline: equal-weight buy-and-hold (+0.4%, MDD −15.2%).

### StockBench Results Table (composite rank by z-score)

| Rank | Model | Return (%) | MDD (%) | Sortino | Variance | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Kimi-K2** | ~2.5+ | −11–14% | High | 1.87 | Best overall composite |
| 2 | **Qwen3-235B-Ins** | ~2.5+ | −11.2% | High | 0.28 | Lower MDD than Think variant |
| 3 | GLM-4.5 | ~2+ | −12% | Good | 0.10 | Stable performer |
| 4 | Qwen3-235B-Think | 2.5 | −14.9% | Med | 0.32 | Higher MDD than Ins |
| 5 | o3 | ~2+ | −13% | Med | 3.25 | High variance |
| 6 | Qwen3-30B-Think | ~1.5+ | −13% | Med | 0.12 | Local-viable |
| 7 | Claude-4-Sonnet | ~1.5+ | −13% | Med | 0.15 | Midpack |
| 8 | DeepSeek V3.1 | ~1+ | −14% | Low | 0.20 | |
| 9 | GPT-5 | ~1+ | −14% | Low | 0.21 | Below baseline in downturn |
| — | Passive Baseline | 0.4 | −15.2% | 0.016 | — | Buy-and-hold |
| — | GPT-OSS-120B | <0 | −15%+ | Low | 10.19 | High variance, underperforms |

**Key insights:**
1. Most LLMs beat the passive baseline in **upturn** markets, but **fail in downturn** periods.
2. **Kimi-K2** and **Qwen3-235B-Ins** show the best risk-adjusted returns.
3. "Thinking" (reasoning) models do not guarantee better trading performance; Qwen3-235B-Ins outperforms the Think variant.
4. DeepSeek V3.1 and GPT-5 rank in the lower half despite strong general benchmarks.

**Benchmark reconciliation note:** StockBench measures **profitability in live DJIA trading**, while BizFinBench/DeepFund focus on **online task accuracy and live financial reasoning**. These can yield different “best” models, so we treat them as complementary signals rather than a single ranking.

---

## Artificial Analysis Intelligence Leaderboard (quality/cost/latency)

Top models by "Intelligence Score" (higher = better reasoning quality):

| Model | Context | Score | Price ($/M) | Speed (t/s) | Notes |
| --- | --- | --- | --- | --- | --- |
| **GPT-5.2 (extra-high context tier)** | 400k | 51 | $4.81 | 37 | Top intelligence |
| **Claude Opus 4.5** | 200k | 50 | $10.00 | 1.7 | Very slow, very expensive |
| GPT-5.2 Codex (xhigh) | 400k | 49 | $4.81 | 24 | Coding focus |
| Gemini 3 Pro Preview | 1m | 48 | $4.50 | 32 | Large context |
| Kimi K2.5 | 256k | 47 | $1.20 | 0.8 | Good value |
| Gemini 3 Flash | 1m | 46 | $1.13 | 13 | Fast & cheap |
| **DeepSeek V3.2** | 128k | 42 | $0.32 | 1.3 | **Best budget option** |
| Grok 4 | 256k | 41 | $6.00 | 14 | Expensive |
| o3 | 200k | 41 | $3.50 | 15 | Reasoning model |
| **Qwen3 Max (Thinking)** | 256k | 40 | $2.40 | 1.6 | Local-comparable quality |
| Kimi K2 Thinking | 256k | 41 | $1.07 | 0.6 | Cheap reasoning |
| Claude 4.5 Sonnet | 1m | 43 | $6.00 | 1.2 | Mid-tier Anthropic |

**Best value picks (score / price):**
1. **DeepSeek V3.2**: Score 42 @ $0.32/M → 131 score/$
2. **Gemini 3 Flash**: Score 46 @ $1.13/M → 41 score/$
3. **Kimi K2 Thinking**: Score 41 @ $1.07/M → 38 score/$

---

## Additional Leaderboards to Cross-Reference
These leaderboards broaden the comparison beyond finance-only tasks:

- **Artificial Analysis model leaderboard** (cost/quality and latency comparisons across frontier and open models).
- **Open Financial LLM Leaderboard** (open-weights finance-specific evaluations).
- **Allganize finance leaderboard** (finance QA + terminology focus).
- **MMLU, GSM8K, MATH, GPQA, and AIME** (general reasoning benchmarks widely used in model cards).
- **ToolBench / StableToolBench** (agentic tool-use evaluation for multi-step workflows).

## Sources Appendix (accessed 2026-02-05)

| Source | Relevance |
| --- | --- |
| https://www.financearena.ai/ | FinanceArena Elo + FinanceQA leaderboards for finance tasks. |
| https://arxiv.org/html/2510.02209v1 | StockBench paper with cumulative return + MDD results. |
| https://stockbench.github.io/ | StockBench project page. |
| https://artificialanalysis.ai/leaderboards/models | Cross-model intelligence/cost/latency leaderboard. |
| https://huggingface.co/spaces/finosfoundation/Open-Financial-LLM-Leaderboard | Open-weights finance leaderboard reference. |
| https://www.allganize.ai/en/blog/allganize-finance-specific-llm-leaderboard-and-test-dataset-released | Finance-specific leaderboard and dataset overview. |
| https://github.com/OpenBMB/ToolBench | Tool-use benchmark for agentic workflows. |
