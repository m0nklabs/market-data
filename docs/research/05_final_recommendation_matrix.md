# 05 — Final Recommendation Matrix

## Decision Matrix

| Option | Accuracy (TA) | Cost | Latency | Privacy | Operational Complexity | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Frontier API (GPT-5.2 Pro) | High (pending stress test) | High | Medium | Low | Low | Best for complex reasoning; expensive at scale. |
| Local 32B (Gemma/Qwen/DeepSeek) | Medium–High (pending stress test) | Low | Medium–High | High | Medium | Cost-effective for batch TA; requires tuning. |
| Hybrid (Frontier + Local) | High | Medium | Medium | Medium | Medium | Use frontier for edge cases, local for bulk. |

## Recommendation (current)
**Adopt a hybrid strategy.** Use GPT-5.2 Pro for complex or high-risk TA workflows and local 32B models for routine batch analytics where cost efficiency matters most. This balances accuracy with operational cost while retaining privacy controls for sensitive datasets.

## Follow-Up Actions
- Populate TA precision metrics from the 100-prompt stress test.
- Capture FinanceArena Elo snapshot and StockBench results once accessible.
- Re-score the matrix after benchmark updates.

## Sources Appendix (accessed 2026-02-05)

| Source | Relevance |
| --- | --- |
| https://openai.com/api/pricing/ | Frontier model cost reference. |
| https://api-docs.deepseek.com/quick_start/pricing/ | Low-cost API pricing benchmark. |
| https://artificialanalysis.ai/leaderboards/models | Cross-model quality/latency comparisons. |
| https://arxiv.org/pdf/2510.02209 | StockBench benchmark definition (profit + drawdown). |
