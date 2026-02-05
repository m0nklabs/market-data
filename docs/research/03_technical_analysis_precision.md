# 03 — Technical Analysis Precision

## Goal
Quantify hallucination and calculation errors for TA-specific tasks. The focus is on high-frequency OHLCV inputs and complex indicator reasoning (divergence, order blocks, liquidity sweeps) to determine reliability for production trading workflows.

---

## Benchmark Evidence from StockBench

StockBench (arXiv:2510.02209) provides error analysis for LLM trading agents:

### Error Types Observed

| Error Type | Description | Thinking Models | Instruct Models |
| --- | --- | --- | --- |
| **Arithmetic Error** | Incorrect share calculations from budget/price | 5.7% (lower) | 14.5% (higher) |
| **Schema Error** | Invalid JSON output format | 6.4% (higher) | 0.4% (lower) |

**Key insight:** Thinking/reasoning models make fewer arithmetic errors but more schema/format errors due to "overthinking" (they deviate from expected output structure).

### Model-Specific Error Patterns

| Model | Arithmetic Error | Schema Error | Notes |
| --- | --- | --- | --- |
| Qwen3-235B-Think | 5.7% | 14.5% | Fewer calc errors, more format issues |
| Qwen3-235B-Ins | 6.4% | 0.4% | Better schema compliance |
| DeepSeek-V3.1-Think | 4% | 5.2% | Balanced |
| DeepSeek-V3-Ins | 2% | 0.4% | Best schema compliance |

---

## Stress Test Design (100 prompts)

**Prompt categories:**
1. Indicator calculation (RSI, MACD, ATR, VWAP, Bollinger Bands)
2. Pattern recognition (head-and-shoulders, double tops/bottoms)
3. Divergence detection (hidden + regular divergence across timeframes)
4. Order block identification (bull/bear blocks, mitigation zones)
5. Trade plan synthesis (entry/stop/target with risk-reward check)

**Scoring metrics:**
- **Hallucination rate**: % of prompts with invented price points or indicators
- **Calculation error rate**: % of prompts with incorrect indicator math
- **Signal validity**: % of signals aligned with deterministic rule checks
- **Risk accuracy**: % of outputs with correct stop/target math

---

## Expected Performance by Model (based on benchmarks)

| Model | Expected Calc Error | Expected Hallucination | Notes |
| --- | --- | --- | --- |
| **o3** | Low (<5%) | Low | Top FinanceArena scores |
| **Claude Opus 4** | Low (<5%) | Low | Strong assumption-based reasoning |
| GPT-5.2 | Medium (5-10%) | Low | General strong performer |
| Kimi-K2 | Low (<5%) | Medium | Best StockBench composite |
| Qwen3-235B-Ins | Low (<5%) | Medium | Good for batch processing |
| DeepSeek V3.2 | Medium (5-10%) | Medium | Good budget option |
| Local 32B (Q5_K_M) | Medium-High (10-15%) | Medium-High | Trade-off for cost savings |

---

## Hidden Divergence & Order Block Verification

To reduce false positives, all detected divergences and order blocks should be validated against deterministic rules:
- **Divergence**: compare higher-high/lower-high structure to oscillator trend
- **Order blocks**: verify displacement candle + mitigation zone retest

### Recommended Validation Pipeline

```
1. LLM generates signal (divergence, order block, etc.)
2. Deterministic validator checks against rule-based criteria
3. Only validated signals pass to execution layer
4. Log all discrepancies for hallucination tracking
```

---

## Recommendations

1. **For production TA workflows**: Use Claude Opus 4 or o3 for complex reasoning tasks (lowest expected error rates)
2. **For batch processing**: Use Qwen3-235B-Ins or DeepSeek V3.2 (good cost/accuracy balance)
3. **Always pair LLM analysis with deterministic validation** to catch hallucinations
4. **Prefer Instruct models over Thinking models** for TA tasks requiring structured output

---

## Sources Appendix (accessed 2026-02-05)

| Source | Relevance |
| --- | --- |
| https://arxiv.org/html/2510.02209v1 | StockBench error analysis (arithmetic/schema errors) |
| https://www.financearena.ai/ | FinanceArena accuracy benchmarks |
| https://github.com/OpenBMB/ToolBench | Agentic evaluation framework for tool-use reliability |
| https://arxiv.org/pdf/2403.07714 | StableToolBench paper on reproducible tool-use evaluation |
