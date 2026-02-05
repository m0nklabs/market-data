# 01 — Market Leaderboards 2026

## Scope
This document captures the most relevant leaderboards for financial reasoning, technical analysis (TA), and trading agent benchmarks. It prioritizes finance-specific leaderboards (FinanceArena, StockBench) and cross-references general reasoning benchmarks used to compare frontier and local models.

## FinanceArena Elo Leaderboard (Assumption-Based Financial Questions)
FinanceArena maintains an Elo-based ranking for finance-specific tasks, including assumption-heavy questions where the model must reason about counterfactuals, missing data, or scenario changes. The leaderboard is live and updates continuously, so we should snapshot the Elo ratings from the site before finalizing the recommendation.

**Snapshot table (manual capture required):**

| Model | Elo (Assumption-Based Financial Questions) | Notes |
| --- | --- | --- |
| GPT-5.x | TBD | Capture from FinanceArena leaderboard (dynamic). |
| Claude 4.x | TBD | Capture from FinanceArena leaderboard (dynamic). |
| Gemini 2.x | TBD | Capture from FinanceArena leaderboard (dynamic). |
| Finance-specialized (e.g., Alpha-F) | TBD | Capture from FinanceArena leaderboard (dynamic). |

*Why manual capture?* The FinanceArena site is a live leaderboard and does not expose a stable static table in this environment. Once access is available, paste the Elo values and date into the table above. FinanceArena uses Elo to rank model pairwise preference on finance tasks, including assumption-based questions.

## StockBench (Real-World Trading Profitability)
StockBench evaluates LLM trading agents on multi-month trading windows with metrics focused on profitability and risk. The benchmark reports cumulative return and maximum drawdown (MDD) for each agent. The paper highlights that many LLM agents struggle to beat a buy-and-hold baseline, and that drawdown control is a major differentiator for practical trading use.

**Key metrics to capture from StockBench:**
- Cumulative return (profitability)
- Maximum drawdown (risk exposure)
- Sortino ratio (risk-adjusted return)

**Action:** extract the per-model cumulative return and MDD from the StockBench paper or project tables once we have access to the results table.

## AIME 2025 Math Score (GPT-5.2 vs Claude 4.5 Opus)
The AIME 2025 comparison is currently a placeholder because public benchmark tables for GPT-5.2 Pro and Claude 4.5 Opus are not exposed in the sources accessible from this environment. Once the vendors publish AIME 2025 results, this section should be updated with the reported scores.

**Action:** capture AIME 2025 scores from vendor benchmarking posts or leaderboard releases, then record them here along with access date.

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
| https://www.financearena.ai/ | FinanceArena Elo leaderboard for assumption-based financial QA. |
| https://arxiv.org/pdf/2510.02209 | StockBench paper defining cumulative return + max drawdown metrics. |
| https://stockbench.github.io/ | StockBench project page for benchmark updates and tables. |
| https://artificialanalysis.ai/leaderboards/models | Cross-model quality/cost leaderboard used for frontier comparisons. |
| https://huggingface.co/spaces/finosfoundation/Open-Financial-LLM-Leaderboard | Open-weights finance leaderboard reference. |
| https://www.allganize.ai/en/blog/allganize-finance-specific-llm-leaderboard-and-test-dataset-released | Finance-specific leaderboard and dataset overview. |
| https://github.com/OpenBMB/ToolBench | Tool-use benchmark for agentic workflows. |
