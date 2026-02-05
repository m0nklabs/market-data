# 04 — Local Optimization for 27GB VRAM

## Goal
Identify the best local model configuration that fits within a 27GB VRAM envelope while maintaining strong long-context performance for TA workflows.

## Candidate Models
- **Qwen-3-32B** (32B parameters, 32K context default; 128K supported on some stacks).
- **DeepSeek-R1-Distill-Qwen-32B** (32B parameters, 32K–128K context depending on deployment).
- **Gemma 3 27B** (27B parameters, 128K context window).

## Quantization Targets (Q5_K_M / Q6_K)
Approximate weight-only VRAM footprints using `params × bits / 8`:

| Model | Params | Q5_K_M weights | Q6_K weights | Notes |
| --- | --- | --- | --- | --- |
| Gemma 3 27B | 27B | ~16.9 GB | ~20.3 GB | Leaves headroom for KV cache. |
| Qwen-3-32B | 32B | ~20.0 GB | ~24.0 GB | Q6_K likely tight in 27GB VRAM. |
| DeepSeek-R1-32B | 32B | ~20.0 GB | ~24.0 GB | Similar footprint to Qwen-3-32B. |

**KV cache impact:** KV cache memory grows linearly with context length. Moving from 32K → 128K context requires ~4× KV cache memory, so 128K contexts are unlikely to fit comfortably in 27GB VRAM without aggressive offloading or paged attention.

## KV Cache / Context Window Performance
- **32K context**: should fit for Q5_K_M variants with moderate batch sizes.
- **128K context**: requires offloading or reduced batch size; expect latency penalties and higher memory pressure.

## VRAM Footprint Comparison (Gemma 3 27B vs Qwen 3 32B)
Gemma 3 27B has a smaller parameter count, which yields a lower base VRAM footprint for quantized weights. This makes Gemma 3 27B the safer fit for 27GB VRAM, especially when KV cache and runtime overhead are included.

## Recommendation (Local)
- Primary: **Gemma 3 27B Q6_K** (more headroom for KV cache).
- Secondary: **Qwen-3-32B Q5_K_M** (if reasoning quality is higher).

## Sources Appendix (accessed 2026-02-05)

| Source | Relevance |
| --- | --- |
| https://huggingface.co/Qwen/Qwen3-32B | Qwen-3-32B model card + context window. |
| https://console.groq.com/docs/model/qwen3-32b | Qwen-3-32B deployment specs (context). |
| https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B | DeepSeek-R1 32B model card. |
| https://community.sambanova.ai/t/deepseek-r1-context-length-is-now-32k/1121 | DeepSeek context length update (32K). |
| https://ai.google.dev/gemma/docs/core/model_card_3 | Gemma 3 model card (27B parameters, context). |
| https://huggingface.co/google/gemma-3-27b-it | Gemma 3 27B model listing. |
