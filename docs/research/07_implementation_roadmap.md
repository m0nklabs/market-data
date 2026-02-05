# 07 — Implementation Roadmap: Multi-Model Trading Architecture

**Context:** Translating the research findings (DeepSeek-R1 for execution, Grok for news, o3-mini for reasoning) into a concrete software architecture for `cryptotrader`.

## 1. The "Multi-Brain" Architecture

Instead of a single monolithic model, we will implement a **Role-Based Mixture of Agents (MoA)** system. This optimizes for cost, speed, and specialization.

### Architecture Diagram

```mermaid
graph TD
    Market[Market Data Stream] -->|OHLCV / Ticks| SignalDetector
    Market -->|News Feed| NewsAnalyzer
    
    subgraph "Layer 1: Filtering (Low Cost)"
        SignalDetector[Algorithmic Signal Detector] -->|Raw Signal| QuantFilter
        QuantFilter[DeepSeek V3.2 / QuantAgent] -->|Probable Setup| Router
    end
    
    subgraph "Layer 2: Evaluation (Specialized)"
        Router{Router} -->|Chart & Levels| TacticalAgent[Tactical (DeepSeek-R1)]
        Router -->|News Context| FundamentalAgent[Fundamental (Grok 4)]
        Router -->|Macro/Risk| StrategistAgent[Strategist (o3-mini)]
    end
    
    subgraph "Layer 3:  Consensus & Execution"
        TacticalAgent --> ConsensusEngine
        FundamentalAgent --> ConsensusEngine
        StrategistAgent --> ConsensusEngine
        
        ConsensusEngine[Weighted Voting] -->|Decision| RiskGuard[Hard Risk Rules]
        RiskGuard -->|Approved| ExecutionAlgo
    end
```

---

## 2. Agent Roles & Tech Stack

| Role | Responsibility | Engine | Why? |
| :--- | :--- | :--- | :--- |
| **Screener** | Initial filtering of 100+ pairs. | **DeepSeek V3.2** | Lowest cost (/bin/bash.32/M), good enough to say "No". |
| **Tactical** | Price action, levels, entry/exit math. | **DeepSeek-R1** | Best numerical calculation & live task performance. |
| **Fundamental** | Sentiment, news correlation, narrative check. | **Grok 4 (Web)** | Only model with expert-level real-time search. |
| **Strategist** | Portfolio fit, macro context, "sanity check". | **o3-mini / o3** | High reasoning capability to detect traps. |
| **Risk Guard** | Hard limits (max drawdown, size). | **Python Code** | Deterministic code is safer than ANY LLM. |

---

## 3. Implementation Steps in `cryptotrader`

### Phase 1: The `LLMRouter` Service
Create a unified interface that abstracts away different providers.

*   **File:** `core/ai/router.py`
*   **Config:** Store API keys for OpenAI, XAI, DeepSeek.
*   **Logic:**
    *   `router.chat(model="deepseek-r1", prompt=...)`
    *   `router.search(model="grok-4", query=...)`

### Phase 2: Role-Based Evaluation Pipeline
Extend `core/opportunities/evaluator.py` to support LLM augmentation.

```python
# Pseudo-code concept
class MultiAgentEvaluator:
    async def evaluate(self, opportunity):
        # 1. Parallel Request
        tactical_task = self.tactical.analyze(opportunity.chart_data)
        fundamental_task = self.fundamental.analyze(opportunity.symbol)
        
        # 2. Gather Results
        tech_score, tech_reason = await tactical_task
        fund_score, fund_reason = await fundamental_task
        
        # 3. Weighted Consensus
        final_score = (tech_score * 0.7) + (fund_score * 0.3)
        
        return Decision(
            action="BUY" if final_score > 0.8 else "PASS",
            reasoning=f"Tech: {tech_reason} | Fund: {fund_reason}"
        )
```

### Phase 3: The "DeepSeek V3.2" Screen
Implement a cost-effective filter.
*   **Input:** 4h candle data for 20 assets.
*   **Prompt:** "Identify patterns matching [Criteria]. Return JSON list of Tickers. Do not reason deeply, just filter."
*   **Cost:** ~/bin/bash.01 per run for the whole market.

---

## 4. Operational Cost Estimate (Per Day)

Assuming 50 signals filtered -> 5 high-quality evaluations:

1.  **Screening (V3.2)**: 100 calls x /bin/bash.0001 = /bin/bash.01
2.  **Tactical Analysis (R1)**: 10 calls x /bin/bash.01 = /bin/bash.10
3.  **Fundamental Search (Grok)**: 10 calls x /bin/bash.03 = /bin/bash.30
4.  **Strategy Check (o3-mini)**: 5 calls x /bin/bash.01 = /bin/bash.05

**Total Daily AI Cost:** ~/bin/bash.46
**Potential Upside:** Massively reduced false positives compared to single-model systems.

## 5. Next Actions
1.  [ ] Setup `core/ai` module in `cryptotrader`.
2.  [ ] Implement generic `LLMProvider` with DeepSeek & OpenAI support.
3.  [ ] Build the "Screener" agent using DeepSeek V3.2.
