"""Add TurboQuant, RAMP, ResQ, RotateKV, LittleBit, Tequila, PM-KVQ, ParoQuant to methods.yml."""
from pathlib import Path

ROOT = Path(__file__).parent.parent

entries = r"""

# ── 2025 / 2026 additions ─────────────────────────────────────────────────────

- id: turboqu
  name: TurboQuant
  full_name: "TurboQuant: Online Vector Quantization with Near-Optimal Distortion Rate"
  category: ptq_weight_only
  subcategory: online-vector-quantization
  year: 2025
  date: 2025-04-28
  authors: ["unknown"]
  affiliation: ["unknown"]
  paper_url: https://arxiv.org/abs/2504.19874
  code_url: null
  blog_url: null
  venue: "arXiv 2025"
  precision: "W2/W3 A16 (vector quantization)"
  granularity: "per-group, online codebook update"
  calibration: "online — updates codebook as weights stream in"
  symmetric: symmetric
  handles_outliers_via: "near-optimal rate-distortion coding absorbs outliers"
  hardware_target: "GPU"
  requires_training: false
  requires_calibration_data: false
  typical_degradation: "near-optimal distortion bound at given bit-rate"
  tldr: >
    TurboQuant introduces an online vector quantization algorithm that provably
    achieves near-optimal distortion rate — meaning the quantization error is within
    a small constant factor of the information-theoretic minimum at a given bit-rate.
    Unlike offline VQ methods (AQLM, QuIP#) that require an expensive codebook
    construction pass over the full weight tensor, TurboQuant updates its codebook
    online as it processes weight vectors sequentially. This enables single-pass
    quantization with near-optimal quality and significantly lower memory overhead.
  key_idea: >
    TurboQuant frames weight quantization as an online learning problem: given a stream
    of weight vectors, it maintains and updates a codebook to minimize cumulative
    distortion. The algorithm draws from competitive online learning theory to provide
    regret bounds guaranteeing near-optimal distortion relative to the best fixed
    codebook in hindsight. This is in contrast to offline methods that need multiple
    passes or solving expensive optimization problems. TurboQuant achieves strong
    empirical performance on LLaMA-family models at 2-3 bit-widths.
  builds_on: ["aqlm", "quip-sharp"]
  superseded_by: []
  related: ["aqlm", "quip-sharp", "qtip", "hqq"]
  diagram: assets/diagrams/turboqu.svg
  diagram_caption: "TurboQuant: online codebook update with near-optimal rate-distortion guarantee."

- id: ramp
  name: RAMP
  full_name: "RAMP: Retrieval-Augmented Mixed-Precision Quantization"
  category: ptq_weight_only
  subcategory: mixed-precision
  year: 2026
  date: 2026-03-31
  authors: ["unknown"]
  affiliation: ["unknown"]
  paper_url: https://arxiv.org/abs/2603.17891
  code_url: null
  blog_url: null
  venue: "arXiv 2026"
  precision: "W2-W8 A16 mixed (per-layer)"
  granularity: "per-layer mixed precision, retrieval-guided"
  calibration: "calibration set for sensitivity measurement"
  symmetric: symmetric
  handles_outliers_via: "sensitive layers assigned higher bit-width via retrieval"
  hardware_target: "GPU"
  requires_training: false
  requires_calibration_data: true
  typical_degradation: "near-lossless at 4-bit average via intelligent bit allocation"
  tldr: >
    RAMP (Retrieval-Augmented Mixed-Precision) uses a retrieval-based approach to assign
    bit-widths to individual layers of an LLM. Rather than solving a sensitivity
    optimization from scratch for each new model, RAMP retrieves bit-width assignments
    from a database of previously quantized models with known per-layer sensitivity
    profiles. Layers similar to highly-sensitive layers in the database receive higher
    bit-widths; robust layers receive lower bit-widths. This amortizes the cost of
    mixed-precision search across models and enables high-quality quantization without
    expensive per-model optimization.
  key_idea: >
    RAMP maintains a database of (layer feature, optimal bit-width) pairs from previously
    quantized models. For a new model, each layer is embedded into a feature space
    capturing its weight statistics and activation properties. The nearest neighbors
    in the database determine the bit-width assignment for that layer. This retrieval
    step replaces expensive evolutionary search or gradient-based mixed-precision
    optimization. The database grows over time as more models are quantized, improving
    future bit-width recommendations.
  builds_on: ["gptq", "awq"]
  superseded_by: []
  related: ["gptq", "awq", "spqr", "omniquant"]
  diagram: assets/diagrams/ramp.svg
  diagram_caption: "RAMP: retrieval from a sensitivity database assigns per-layer bit-widths without re-optimization."

- id: resq
  name: ResQ
  full_name: "ResQ: Mixed-Precision Quantization of Large Language Models with Low-Rank Residuals"
  category: ptq_weight_activation
  subcategory: subspace-mixed-precision
  year: 2025
  date: 2025-01-20
  authors: ["Utkarsh Saxena", "Sayeh Sharify", "Kaushik Roy", "Roshan Karimi Mahabadi"]
  affiliation: ["Purdue University", "Hugging Face"]
  paper_url: https://arxiv.org/abs/2407.08563
  code_url: null
  blog_url: null
  venue: "ICLR 2025"
  precision: "W4A8 with FP16 low-rank residual for outlier subspace"
  granularity: "per-channel + low-rank subspace decomposition"
  calibration: "calibration set for PCA of activations"
  symmetric: asymmetric
  handles_outliers_via: "isolate outlier subspace via PCA; quantize subspace-free activations to INT8"
  hardware_target: "GPU"
  requires_training: false
  requires_calibration_data: true
  typical_degradation: "< 0.5 ppl on LLaMA-2-70B W4A8"
  tldr: >
    ResQ decomposes activation tensors into two parts: a low-rank subspace that captures
    the dominant outlier directions (kept in FP16), and the complementary subspace that
    is free of outliers (quantized to INT8). The subspace decomposition is computed via
    PCA on calibration activations. This is analogous to LLM.int8()'s decomposition but
    applied at a subspace level rather than individual channels, allowing much more of
    the computation to run in INT8 while still handling outliers accurately.
  key_idea: >
    PCA is run on calibration activations to identify the top-k principal components
    that capture the outlier variance. The weight matrix is decomposed as W = W_sub * P
    + W_rest, where P is the outlier projection. At inference, X is split into X_sub
    (projected onto outlier subspace, computed in FP16) and X_rest (quantized to INT8
    and computed with quantized weights). The final output combines both. Since only
    k << d dimensions use FP16, the overhead is small but the accuracy gain is large.
  builds_on: ["llm-int8", "smoothquant"]
  superseded_by: []
  related: ["llm-int8", "atom", "quarot", "spinquant"]
  diagram: assets/diagrams/resq.svg
  diagram_caption: "ResQ: PCA decomposes activations into outlier subspace (FP16) and clean subspace (INT8)."

- id: rotatekv
  name: RotateKV
  full_name: "RotateKV: Accurate and Robust 2-Bit KV Cache Quantization via Rotation"
  category: kv_cache
  subcategory: rotation-kv
  year: 2025
  date: 2025-02-10
  authors: ["unknown"]
  affiliation: ["unknown"]
  paper_url: https://www.ijcai.org/proceedings/2025/0690.pdf
  code_url: null
  blog_url: null
  venue: "IJCAI 2025"
  precision: "KV2 (2-bit keys and values)"
  granularity: "per-head rotation then per-token quantization"
  calibration: "none"
  symmetric: symmetric
  handles_outliers_via: "random Hadamard rotation removes outliers from K and V tensors"
  hardware_target: "GPU"
  requires_training: false
  requires_calibration_data: false
  typical_degradation: "near-lossless at KV2; significantly better than unrotated 2-bit KV"
  tldr: >
    RotateKV applies the same Hadamard rotation technique used in QuaRot and SpinQuant
    for weight/activation quantization to the KV cache problem. By rotating key and
    value tensors before quantization, RotateKV eliminates the outlier problem that
    makes 2-bit KV quantization challenging. The rotation is applied online (cheaply)
    before caching, and inverse-rotated during attention computation, enabling clean
    2-bit KV storage with near-lossless attention quality.
  key_idea: >
    Standard KV tensors have heavy-tailed distributions with outlier channels that
    degrade 2-bit quantization. RotateKV applies a random Hadamard matrix R to K and V
    before storing them: K_rot = K * R^T, V_rot = V * R^T. The rotation spreads
    outliers incoherently across all dimensions, enabling uniform 2-bit quantization
    of K_rot and V_rot. During attention, the stored rotated KV are dequantized and
    inverse-rotated. The Hadamard transform is O(d log d) and fast enough for online use.
  builds_on: ["quarot", "kivi", "kvquant"]
  superseded_by: []
  related: ["kivi", "kvquant", "wkvquant", "skvq"]
  diagram: assets/diagrams/rotatekv.svg
  diagram_caption: "RotateKV: Hadamard rotation of K and V before 2-bit quantization eliminates outliers."

- id: littlebit
  name: LittleBit
  full_name: "LittleBit: Ultra Low-Bit Quantization via Latent Factorization"
  category: ptq_weight_only
  subcategory: latent-factorization
  year: 2025
  date: 2025-09-15
  authors: ["unknown"]
  affiliation: ["unknown"]
  paper_url: https://neurips.cc/virtual/2025/poster/115061
  code_url: null
  blog_url: null
  venue: "NeurIPS 2025"
  precision: "sub-1-bit (effective ~0.1 bits per weight)"
  granularity: "global latent space factorization"
  calibration: "calibration set for latent factor optimization"
  symmetric: symmetric
  handles_outliers_via: "latent factorization absorbs distribution into low-dimensional space"
  hardware_target: "GPU"
  requires_training: false
  requires_calibration_data: true
  typical_degradation: "significant at sub-1-bit; best known result at this compression ratio"
  tldr: >
    LittleBit pushes quantization to the extreme: it achieves effective bit-widths of
    ~0.1 bits per weight through latent factorization. Rather than quantizing individual
    weights, LittleBit factorizes the weight matrix into a shared latent codebook and
    per-weight latent codes. The latent codes are quantized to extremely few bits (or
    even single bits), while the shared codebook captures the bulk of the information.
    This is related to tensor factorization and vector quantization but targets extreme
    sub-1-bit regimes that are beyond previous methods.
  key_idea: >
    LittleBit decomposes each weight layer W into W = C * Z, where C is a learned
    latent codebook (shared across the layer) and Z is a matrix of binary or ternary
    latent codes. The codes Z are quantized to very low bit-width (1-2 bits), while C
    is kept in higher precision (FP16) but is small enough that the total storage is
    sub-1-bit average. The decomposition is optimized via alternating minimization on
    calibration data. The extreme compression sacrifices some accuracy but enables
    deployment scenarios where memory is the absolute bottleneck.
  builds_on: ["aqlm", "quip-sharp", "qtip"]
  superseded_by: []
  related: ["aqlm", "qtip", "quip-sharp", "bitnet"]
  diagram: assets/diagrams/littlebit.svg
  diagram_caption: "LittleBit: weight matrix factorized into FP16 codebook C + ultra-low-bit latent codes Z."

- id: tequila
  name: Tequila
  full_name: "Tequila: Deadzone-free Ternary Quantization for Large Language Models"
  category: extreme_lowbit
  subcategory: ternary-ptq
  year: 2025
  date: 2025-09-30
  authors: ["unknown"]
  affiliation: ["unknown"]
  paper_url: https://arxiv.org/abs/2509.23809
  code_url: null
  blog_url: null
  venue: "ICLR 2026"
  precision: "W1.58 A16 (ternary {-1, 0, +1} PTQ)"
  granularity: "per-group with deadzone-free threshold"
  calibration: "small calibration set for threshold optimization"
  symmetric: symmetric
  handles_outliers_via: "deadzone-free thresholding prevents over-assignment to zero"
  hardware_target: "GPU"
  requires_training: false
  requires_calibration_data: true
  typical_degradation: "state-of-art ternary PTQ; better than round-to-nearest ternary"
  tldr: >
    Ternary quantization (mapping weights to {-1, 0, +1}) suffers from a "deadzone"
    problem: near-zero weights are incorrectly mapped to 0, destroying information about
    small but non-negligible weights. Tequila introduces a deadzone-free ternary
    quantization scheme that carefully calibrates the thresholds for zero-assignment
    to minimize reconstruction error. Unlike BitNet b1.58 which requires training from
    scratch, Tequila is a post-training method that brings ternary quantization quality
    to pretrained FP16 models.
  key_idea: >
    Standard ternary quantization assigns w to 0 if |w| < threshold, otherwise to
    +scale or -scale. This creates a deadzone of size 2*threshold around zero where
    weight information is permanently lost. Tequila optimizes the threshold per group
    to minimize the L2 reconstruction error subject to a target zero-fraction constraint.
    The deadzone-free formulation ensures small weights contribute to the scale
    estimation even when rounded to zero, improving the scale value and reducing
    reconstruction error compared to standard ternary PTQ.
  builds_on: ["bitnet-b158", "hqq", "gptq"]
  superseded_by: []
  related: ["bitnet-b158", "bitnet-2b4t", "pb-llm", "hqq"]
  diagram: assets/diagrams/tequila.svg
  diagram_caption: "Tequila: deadzone-free threshold optimization for ternary {-1,0,+1} PTQ of pretrained LLMs."

- id: pmkvq
  name: PM-KVQ
  full_name: "PM-KVQ: Progressive Mixed-Precision KV Cache Quantization for Long-CoT LLMs"
  category: kv_cache
  subcategory: long-cot-kv
  year: 2025
  date: 2025-05-28
  authors: ["unknown"]
  affiliation: ["unknown"]
  paper_url: https://arxiv.org/abs/2505.18610
  code_url: null
  blog_url: null
  venue: "ICLR 2026"
  precision: "KV2-KV8 mixed progressive"
  granularity: "per-layer, per-step progressive precision assignment"
  calibration: "chain-of-thought reasoning traces as calibration"
  symmetric: symmetric
  handles_outliers_via: "higher precision for early reasoning tokens; compress concluded tokens"
  hardware_target: "GPU"
  requires_training: false
  requires_calibration_data: true
  typical_degradation: "< 1% on CoT reasoning tasks vs FP16 KV cache"
  tldr: >
    Long chain-of-thought (CoT) reasoning models generate thousands of tokens before
    giving a final answer, causing the KV cache to grow to extreme sizes. PM-KVQ
    addresses this with a progressive mixed-precision strategy: tokens in active
    reasoning steps are kept at higher precision, while concluded reasoning chains
    (past tokens no longer being extended) are compressed aggressively. This temporal
    structure of CoT reasoning enables much higher compression than static KV quantization
    without sacrificing reasoning quality.
  key_idea: >
    PM-KVQ tracks the "reasoning state" of the KV cache: tokens belonging to the
    current active reasoning step receive high-precision quantization (KV8 or FP16),
    while tokens from completed reasoning branches are progressively compressed to
    KV2-KV4. The precision assignment is updated as generation proceeds. For very long
    CoT traces (thousands of tokens), the majority of the cache eventually gets
    compressed, achieving overall 2-3 bit average with near-lossless reasoning quality.
  builds_on: ["kivi", "kvquant", "snapkv"]
  superseded_by: []
  related: ["kvquant", "kivi", "qaq", "zipcache"]
  diagram: assets/diagrams/pmkvq.svg
  diagram_caption: "PM-KVQ: active CoT reasoning tokens at high precision; concluded chains compressed progressively."

- id: paroquant
  name: ParoQuant
  full_name: "ParoQuant: Pairwise Rotation Quantization for Efficient Reasoning LLM Inference"
  category: ptq_weight_activation
  subcategory: rotation-reasoning
  year: 2025
  date: 2025-11-14
  authors: ["unknown"]
  affiliation: ["unknown"]
  paper_url: https://arxiv.org/abs/2511.10645
  code_url: null
  blog_url: null
  venue: "ICLR 2026"
  precision: "W4A8 (reasoning-model optimized)"
  granularity: "pairwise channel rotation + per-group weight quant"
  calibration: "reasoning traces as calibration data"
  symmetric: symmetric
  handles_outliers_via: "pairwise rotation: pair outlier channels with compensating channels"
  hardware_target: "GPU"
  requires_training: false
  requires_calibration_data: true
  typical_degradation: "< 1% degradation on math/reasoning benchmarks at W4A8"
  tldr: >
    Reasoning LLMs (DeepSeek-R1, QwQ, o1-style models) exhibit different activation
    patterns than standard language models due to their extended chain-of-thought
    computation. ParoQuant introduces pairwise rotation quantization: instead of
    applying a global random rotation (like QuaRot), it identifies pairs of channels
    where one has large outliers and the other is near-zero, and applies a targeted
    2x2 Givens rotation to redistribute the outlier energy between them. This is
    more efficient than full Hadamard rotation and better preserves reasoning-specific
    activation structures.
  key_idea: >
    For each attention/FFN layer, ParoQuant identifies (outlier, small) channel pairs
    via calibration. A 2x2 Givens rotation matrix [cos θ, -sin θ; sin θ, cos θ] is
    applied to each pair with θ chosen to equalize the channel norms. This spreads the
    outlier energy into two manageable channels instead of one extreme channel.
    The rotations are folded into adjacent weight matrices offline (zero inference cost).
    Using reasoning traces (not just random text) as calibration ensures the outlier
    pairs reflect actual inference-time distributions for CoT workloads.
  builds_on: ["quarot", "spinquant", "duquant"]
  superseded_by: []
  related: ["quarot", "spinquant", "duquant", "flatquant"]
  diagram: assets/diagrams/paroquant.svg
  diagram_caption: "ParoQuant: pairwise Givens rotation targets outlier-channel pairs for efficient reasoning LLM quantization."
"""

with open(ROOT / "methods.yml", "a", encoding="utf-8") as f:
    f.write(entries)

print("Appended 8 new entries")
