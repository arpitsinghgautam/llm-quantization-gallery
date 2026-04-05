# Notation Reference

This document defines all notation used on every card in the gallery. Read this once; it is never re-explained inline.

---

## Bit-width shorthand: WxAyKVz

Every method is tagged with a compact string encoding its quantization targets.

| Symbol | Meaning |
|--------|---------|
| **Wx** | Weight precision in bits. `W4` = 4-bit weights. `W1` = binary. `W1.58` = ternary {-1, 0, +1}. `Wfp8` = 8-bit floating point. `Wfp4` = 4-bit floating point. |
| **Ay** | Activation precision in bits. `A16` = 16-bit (BF16/FP16, i.e. not quantized). `A8` = 8-bit activations. Omitted if the method does not touch activations. |
| **KVz** | KV-cache precision. `KV4` = 4-bit keys and values. `KV2` = 2-bit. Omitted if the method does not touch the KV cache. |

Examples:
- `W4A16` — 4-bit weights, 16-bit activations (weight-only quantization).
- `W8A8` — 8-bit weights and activations (both quantized).
- `W4A8KV4` — 4-bit weights, 8-bit activations, 4-bit KV cache.
- `W1.58A8` — ternary weights, 8-bit activations (BitNet b1.58).

If weight and activation precisions differ per layer, the tag uses a slash: `W4/W8A16`.

---

## Granularity

How the quantization scale (and zero-point, if asymmetric) is shared across parameters.

| Term | Definition |
|------|-----------|
| **per-tensor** | One scale for the entire weight matrix. Coarsest; lowest overhead. |
| **per-channel** (output) | One scale per output channel (row of the weight matrix for a linear layer). Standard in most INT8 kernels. |
| **per-channel** (input) | One scale per input channel (column). Used for activation quantization in some W+A schemes. |
| **per-group** | One scale per contiguous block of *g* elements along the quantization axis. `g=128` is the most common default. Finer than per-channel; the dominant choice for 4-bit weight quantization. |
| **per-token** | One scale per token in the activation tensor. Used for KV-cache and activation quantization. |
| **per-head** | One scale per attention head. Coarser than per-token. |
| **vector quantization (VQ)** | Codebook-based; a group of weights maps to a single centroid. Not a simple linear scale. |

---

## Symmetric vs. asymmetric

| Term | Definition |
|------|-----------|
| **symmetric** | The quantization grid is centered on zero. Zero-point = 0. Represented as `q = clamp(round(x / s), -2^{b-1}, 2^{b-1}-1)`. Requires only one scale parameter per granularity unit. |
| **asymmetric** | An explicit zero-point `z` shifts the grid: `q = clamp(round(x / s) + z, 0, 2^b - 1)`. Uses unsigned integers; better for one-sided distributions (e.g. post-ReLU activations). Slightly higher overhead. |
| **mixed** | Some layers or tensors are symmetric, others asymmetric. |
| **NF4 / NF8** | "Normal Float" — a non-uniform grid designed for normally-distributed weights (from QLoRA). Not strictly symmetric or asymmetric in the classical sense. |

---

## Calibration

| Term | Definition |
|------|-----------|
| **calibration set** | A small unlabeled dataset (typically 128–512 sequences) used to compute activation statistics or Hessian-based correction terms. Required for PTQ methods that observe activations. |
| **no calibration** | Quantization depends only on the weights themselves (e.g. RTN, HQQ). No data is needed. |
| **training data** | QAT methods require the full (or a representative subset of the) training corpus. |

---

## Common abbreviations

| Abbreviation | Meaning |
|-------------|---------|
| **PTQ** | Post-Training Quantization — quantize after training, no gradient updates to the original weights. |
| **QAT** | Quantization-Aware Training — training (or fine-tuning) with simulated quantization in the forward pass. |
| **RTN** | Round-To-Nearest — the simplest baseline: divide by scale, round, clip. |
| **OBS** | Optimal Brain Surgeon — classic second-order weight pruning/quantization framework (Hassibi & Stork, 1992). |
| **OBQ** | Optimal Brain Quantization — the OBS-derived per-weight quantization method from Frantar & Alistarh (2022). |
| **ppl** | Perplexity — the standard LLM quality proxy. Lower is better. Reported on WikiText-2 or C4 unless noted. |
| **W-only** | Weight-only quantization — activations remain in FP16/BF16. |
| **W+A** | Weights and activations both quantized. |
| **KV** | The key-value cache in transformer attention. |
| **STE** | Straight-Through Estimator — the standard trick for backpropagating through a quantization step. |
| **LUT** | Look-Up Table — used in vector quantization to decode indices back to weight values. |
| **MX** | Microscaling — the OCP/industry-standard block floating-point format (MXFP8/MXFP6/MXFP4). |
| **GPTQ** | Generative Pre-trained Transformer Quantization. |
| **AWQ** | Activation-aware Weight Quantization. |
| **KVQ** | KV-cache Quantization (generic shorthand). |

---

## Notation used in diagrams

- **W** — weight tensor  
- **X** or **A** — input activation tensor  
- **s** — quantization scale  
- **z** — zero-point  
- **g** — group size  
- **b** — number of bits  
- **H** — Hessian matrix (second-order information about layer inputs)  
- **Q(·)** — quantization operator  
- **dequant / DQ** — dequantization (multiply by scale, add zero-point)
