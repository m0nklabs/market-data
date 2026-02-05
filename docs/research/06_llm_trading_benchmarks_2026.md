# Research: LLM Trading Benchmarks & Models (2026)

**Date:** February 5, 2026
**Context:** Investigation into state-of-the-art LLM benchmarks for financial reasoning, trading, and crypto technical analysis.

## 1. Key Papers & Benchmarks

### StockBench (Oct 2025)
*   **Paper:** "StockBench: Can LLM Agents Trade Stocks Profitably In Real-world Markets?" (Chen et al.)
*   **Focus:** Realistic, multi-month stock trading environments (not just static QA).
*   **Mechanism:** Agents act on daily market signals (price, fundamentals, news).
*   **Findings:** Most LLM agents struggle to beat buy-and-hold. SOTA models (GPT-5, Claude-4) show potential but often fail to translate static knowledge into dynamic trading success.

### BizFinBench.v2 (Jan 2026)
*   **Paper:** "BizFinBench.v2: A Unified Dual-Mode Bilingual Benchmark for Expert-Level Financial Capability Alignment" (Guo et al.)
*   **Focus:** Authentic business data from Chinese and U.S. equity markets; includes "online tasks" (live/dynamic).
*   **Key Metrics:**
    *   **Main Tasks Accuracy:**
        *   **ChatGPT-5:** 61.5% (Leader)
    *   **Online/Live Tasks:**
        *   **DeepSeek-R1:** Outperforms all other commercial LLMs.
*   **Earlier Version (v1) Stats:**
    *   **Numerical Calculation:** DeepSeek-R1 (64.04), Claude-3.5-Sonnet (63.18).
    *   **Reasoning:** ChatGPT-o3 (83.58), Gemini-2.0-Flash (81.15).
    *   **Information Extraction:** DeepSeek-R1 (71.46) - gap to open-source is huge.

### DeepFund (Mar 2025 - May 2025)
*   **Paper:** "Time Travel is Cheating: Going Live with DeepFund for Real-Time Fund Investment Benchmarking"
*   **Focus:** **Live** fund benchmark to prevent "time travel" (data leakage) in backtests.
*   **Findings:**
    *   Even **DeepSeek-V3** and **Claude-3.7-Sonnet** incurred net trading losses in the live environment.
    *   Highlights the "reality gap" between backtest performance and live execution.

### QuantAgent (Sep 2025)
*   **Paper:** "QuantAgent: Price-Driven Multi-Agent LLMs for High-Frequency Trading"
*   **Focus:** High-Frequency Trading (HFT) and crypto (Bitcoin futures).
*   **Relevance:** Directly addresses **Crypto Technical Analysis**.
*   **Mechanism:** Multi-agent system (Indicator, Pattern, Trend, Risk agents).
*   **Performance:** Outperforms neural and rule-based baselines on Bitcoin and Nasdaq futures in 4-hour intervals.

## 2. Model Leaderboard Snapshot (Financial Reasoning)

Based on *BizFinBench.v2* and *DeepFund* results (Early 2026):

| Rank | Model | Strengths | Weaknesses |
| :--- | :--- | :--- | :--- |
| **1** | **DeepSeek-R1** | **#1 in Online/Live Tasks**, **#1 in Information Extraction**, **#1 in Numerical Calculation**. Best for "real world" dynamic usage. | - |
| **2** | **ChatGPT-5** | **#1 in General Financial QA** (61.5% accuracy). Strongest static knowledge base. | Slightly behind in dynamic online tasks compared to R1. |
| **3** | **ChatGPT-o3** | **#1 in Reasoning** (83.58). Excellent for logic-heavy tasks. | - |
| **4** | **Gemini-2.0-Flash** | **#2 in Reasoning** (81.15). Very fast and capable. | - |
| **5** | **Claude-3.5-Sonnet** | Strong in numerical calc (63.18). | Lagged in some v1 metrics compared to newer models. |

## 3. Best for Crypto Technical Analysis

1.  **QuantAgent Framework**: This isn't a single model but a **multi-agent framework** specifically designed for crypto/HFT. It uses specialized agents for patterns and trends.
2.  **InvestorBench**: Evaluates agents on **Cryptocurrencies** and ETFs.
3.  **DeepSeek-R1**: Given its dominance in "online tasks" and "numerical calculation" in BizFinBench, it is likely the best raw engine for technical analysis constraints.

## 4. "FinanceArena" Status
*   No direct endpoint or paper titled simply "FinanceArena" was found in the top citations.
*   References to **"LMArena"** (Large Model Arena) are common (cited in *LiveTradeBench*).
*   **DeepFund** explicitly positions itself as a "Live Arena Perspective".
*   *Interpretation:* The user likely refers to the "DeepFund" live arena or the financial subset of "LMArena".

## 5. Recommendation for `cryptotrader`
*   **Primary Reasoning Engine:** **DeepSeek-R1** (via API) seems to be the current "meta" for live/online financial tasks.
*   **Pattern Recognition:** Use established frameworks like **QuantAgent** (separate agents for indicators vs patterns) rather than asking a single LLM to do it all.
*   **Backtesting Reality Check:** Be extremely wary of backtests. *DeepFund* proves that models profitable in backtests (DeepSeek-V3, Claude-3.7) can lose money live.
