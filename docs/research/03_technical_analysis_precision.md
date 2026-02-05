# 03 — Technical Analysis Precision

## Goal
Quantify hallucination and calculation errors for TA-specific tasks. The focus is on high-frequency OHLCV inputs and complex indicator reasoning (divergence, order blocks, liquidity sweeps) to determine reliability for production trading workflows.

## Stress Test Design (100 prompts)
**Prompt categories:**
1. Indicator calculation (RSI, MACD, ATR, VWAP, Bollinger Bands).
2. Pattern recognition (head-and-shoulders, double tops/bottoms).
3. Divergence detection (hidden + regular divergence across timeframes).
4. Order block identification (bull/bear blocks, mitigation zones).
5. Trade plan synthesis (entry/stop/target with risk-reward check).

**Scoring metrics:**
- **Hallucination rate**: % of prompts with invented price points or indicators.
- **Calculation error rate**: % of prompts with incorrect indicator math.
- **Signal validity**: % of signals aligned with deterministic rule checks.
- **Risk accuracy**: % of outputs with correct stop/target math.

## Planned Model Coverage
- Frontier: GPT-5.2 Pro.
- Local: Qwen-3-32B (Q5_K_M or Q6_K) or DeepSeek-R1-32B.

## Result Tracking (pending execution)

| Model | Hallucination Rate | Calc Error Rate | Divergence FPs | Order Block FPs | Notes |
| --- | --- | --- | --- | --- | --- |
| GPT-5.2 Pro | TBD | TBD | TBD | TBD | Stress test pending. |
| Qwen-3-32B (local) | TBD | TBD | TBD | TBD | Stress test pending. |
| DeepSeek-R1-32B (local) | TBD | TBD | TBD | TBD | Stress test pending. |

## Hidden Divergence & Order Block Verification
To reduce false positives, all detected divergences and order blocks should be validated against deterministic rules:
- Divergence: compare higher-high/lower-high structure to oscillator trend.
- Order blocks: verify displacement candle + mitigation zone retest.

## Next Steps
- Run the 100-prompt stress test on GPT-5.2 Pro and one local 32B model.
- Store raw prompt/response pairs for manual auditing.
- Update the table with measured error rates.

## Sources Appendix (accessed 2026-02-05)

| Source | Relevance |
| --- | --- |
| https://github.com/OpenBMB/ToolBench | Agentic evaluation framework for tool-use reliability. |
| https://arxiv.org/pdf/2403.07714 | StableToolBench paper on reproducible tool-use evaluation. |
| https://openbmb.github.io/ToolBench/ | ToolBench evaluation metrics and leaderboard. |
