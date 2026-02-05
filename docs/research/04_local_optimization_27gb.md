# 04 — Local Optimization for 27GB VRAM

## Goal
Identify the best local model configuration that fits within a 27GB VRAM envelope while maintaining strong long-context performance for TA workflows.

---

## Candidate Models Comparison

| Model | Params | Context | Intelligence Score | Best For |
| --- | --- | --- | --- | --- |
| **Gemma 3 27B** | 27B | 128K | ~25 | VRAM headroom, good speed |
| **Qwen3-32B** | 32B | 32K–128K | ~30 | Better reasoning quality |
| DeepSeek-R1-Distill-Qwen-32B | 32B | 32K | ~27 | Reasoning-focused |
| Qwen2.5-30B-A3B (MoE) | 30B (3B active) | 262K | ~22 | Very long context |

---

## Quantization & VRAM Footprint

Approximate weight-only VRAM using `params × bits / 8` as a rough baseline. Actual VRAM usage varies by quantization scheme, metadata overhead, and activation/KV cache requirements (for example, Q5_K_M uses mixed 5–6 bit weights, not a flat 5-bit footprint).

| Model | Q5_K_M | Q6_K | Q8 | Notes |
| --- | --- | --- | --- | --- |
| **Gemma 3 27B** | ~16.9 GB | ~20.3 GB | ~27 GB | ✅ Best fit for 27GB |
| Qwen3-32B | ~20.0 GB | ~24.0 GB | ~32 GB | Q6_K tight, Q8 won't fit |
| DeepSeek-R1-32B | ~20.0 GB | ~24.0 GB | ~32 GB | Same as Qwen3-32B |

**KV cache impact:**
- 32K context: +2–4 GB KV cache
- 128K context: +8–16 GB KV cache (won't fit with Q6_K 32B models)

### VRAM Budget Breakdown (27GB target)

| Component | Gemma 3 27B Q6_K | Qwen3-32B Q5_K_M |
| --- | --- | --- |
| Model weights | 20.3 GB | 20.0 GB |
| KV cache (32K) | ~3 GB | ~3 GB |
| Runtime overhead | ~2 GB | ~2 GB |
| **Total** | **~25.3 GB** ✅ | **~25 GB** ✅ |

---

## Performance Benchmarks

| Model | Tokens/sec (RTX 4090) | Quality vs Frontier | Notes |
| --- | --- | --- | --- |
| Gemma 3 27B Q6_K | 18–25 t/s | ~50% of GPT-5.2 | Good for batch TA |
| Qwen3-32B Q5_K_M | 12–18 t/s | ~60% of GPT-5.2 | Better reasoning |
| DeepSeek-R1-32B Q5_K_M | 10–15 t/s | ~55% of GPT-5.2 | Slower, chain-of-thought |

---

## StockBench-Comparable Local Models

From StockBench results, **Qwen3-30B-Think** ranked 6th with low variance (0.12), suggesting local Qwen variants are viable for trading tasks.

---

## Recommendation

### Primary: Gemma 3 27B Q6_K
- **Why:** Most VRAM headroom, fast inference, 128K context viable with paged attention
- **Use case:** High-volume batch TA, signal scanning
- **Setup:** `ollama run gemma3:27b-instruct-q6_K`

### Secondary: Qwen3-32B Q5_K_M
- **Why:** Higher reasoning quality, better StockBench performance
- **Use case:** Complex trade decisions, divergence analysis
- **Trade-off:** Tighter VRAM fit, limit to 32K context
- **Setup:** `ollama run qwen3:32b-q5_K_M`

### For Extended Context (128K+): Use API
- Local 128K context is impractical with 27GB VRAM
- Fall back to DeepSeek V3.2 API ($0.32/M) for long-context tasks

---

## Fine-Tuning Option (future)
Consider fine-tuning a smaller local model (e.g., Qwen3-32B or Phi-4) on crypto-specific signal data. A targeted fine-tune could outperform frontier models on our exact indicators while keeping inference local.

---

## Sources Appendix (accessed 2026-02-05)

| Source | Relevance |
| --- | --- |
| https://huggingface.co/Qwen/Qwen3-32B | Qwen-3-32B model card + context window |
| https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B | DeepSeek-R1 32B model card |
| https://ai.google.dev/gemma/docs/core/model_card_3 | Gemma 3 model card (27B parameters) |
| https://huggingface.co/google/gemma-3-27b-it | Gemma 3 27B model listing |
| https://arxiv.org/html/2510.02209v1 | StockBench local model performance (Qwen3-30B-Think) |
| https://artificialanalysis.ai/leaderboards/models | Local model speed/quality benchmarks |
