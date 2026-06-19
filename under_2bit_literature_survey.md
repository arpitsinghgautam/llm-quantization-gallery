# Sub-2-Bit LLM Quantization: A Literature Survey

*Extreme low-bit (binary, ternary, and sub-1-bit) quantization of large language models.*

**Scope:** the 15 methods in the gallery's **Extreme Low-Bit & Binary/Ternary** category (`papers/04_Extreme_Low-Bit/`), spanning 2023–2026.
**Compiled:** 2026-06-20. Quantitative figures are taken from each paper's own PDF (see `papers/04_Extreme_Low-Bit/`); arXiv IDs are listed in the references.

> **A note on cross-paper numbers.** The perplexity (PPL) and accuracy figures below are quoted from each paper individually. Different papers use different calibration sets, evaluation harnesses, sequence lengths, and "effective bit-width" accounting (some include scale/metadata bits, some do not; some hold embeddings/LM-head in FP16). Treat cross-method comparisons as *directional*, not exact — especially for the 2026 preprints whose near-FP16 results at ~1 bit are striking and await independent replication.

---

## 1. Introduction and scope

Quantization compresses a model by storing its weights (and sometimes activations) in fewer bits. Mainstream LLM deployment has converged on 4-bit weight quantization (GPTQ, AWQ) as a near-lossless sweet spot. **Sub-2-bit** quantization is the frontier *below* that: representing each weight with

- **1 bit** — *binary*, weights in {−1, +1};
- **~1.58 bits** — *ternary*, weights in {−1, 0, +1} (log₂3 ≈ 1.58); or
- **< 1 bit** — *sub-1-bit*, achieved by factorization/codebook tricks where individual weights no longer have an independent representation.

The prize is large: memory scales roughly linearly with bit-width, so going from FP16 to 1-bit is a **~16×** reduction, and ternary/binary matmuls reduce to **additions** (no floating-point multiplies), cutting arithmetic energy by an order of magnitude or more. The obstacle is equally large: naive binarization of a pretrained LLM **collapses it below random guessing** (PB-LLM, BitNet). The entire sub-field is the study of *how to avoid that collapse.*

Two structural facts shape every method in this survey:

1. **The information-theoretic tailwind.** Larger models tolerate fewer bits per weight (Spectra's entropy argument; BitNet's scaling laws). Extreme quantization works *better* at scale — the FP16-vs-low-bit quality gap shrinks as parameter count grows. This is why most strong results appear at ≥3B parameters.
2. **The central fork.** You can either **bake low precision into training** (train-from-scratch / QAT) and pay a one-time training cost for the best quality, or **convert an existing FP16 checkpoint** (post-training quantization, PTQ) cheaply but fight harder for accuracy. This fork organizes the whole field (§3 vs §4).

---

## 2. A taxonomy

Four axes separate the 15 methods:

| Axis | Options |
|---|---|
| **Paradigm** | Train-from-scratch · QAT (from pretrained) · QAT+distillation · Post-training (PTQ) |
| **Representation** | Binary {−1,+1} · Ternary {−1,0,+1} · Sub-1-bit factorization |
| **Coverage** | Weight-only (A16) · Joint weight + low-bit activation (W·Ax) |
| **Core trick** | Saliency/partial-precision · Hessian error compensation · Sign-value/factorization · Rotation (Hadamard/Kronecker) · Distribution reshaping · Distillation · Scale-overhead minimization |

### 2.1 Master table

| Method | Year | Venue | Paradigm | Weights | Activations | Family |
|---|---|---|---|---|---|---|
| **PB-LLM** | 2023 | ICLR'24 | PTQ + QAT | partial-binary (~2.7–5 eff. bit) | FP16 | salient-weight mixed precision |
| **BitNet** | 2023 | preprint | train-from-scratch | 1-bit binary | INT8 | binary BitLinear |
| **OneBit** | 2024 | NeurIPS'24 | QAT + KD | ~1.01-bit | FP16 | sign-value decomposition |
| **BitNet b1.58** | 2024 | preprint | train-from-scratch | 1.58-bit ternary | INT8 | ternary BitLinear |
| **BiLLM** | 2024 | ICML'24 | PTQ | ~1.1-bit binary | FP16 | salient + residual binarization |
| **MatMul-free LM** | 2024 | preprint | train-from-scratch | 1.58-bit ternary | BF16/INT8 | ternary + matmul-free architecture |
| **Spectra (TriLM)** | 2024 | preprint | train-from-scratch | 1.58-bit ternary | FP16 | ternary pretraining suite |
| **Tequila** | 2025 | ICLR'26 | QAT | 1.58-bit ternary | FP16 | deadzone-free ternary |
| **LittleBit** | 2025 | NeurIPS'25 | QAT + KD | **sub-1-bit (0.1–1.0 BPW)** | FP16 | latent factorization + binarization |
| **BitNet b1.58 2B4T** | 2025 | tech report | train-from-scratch | 1.58-bit ternary | INT8 | open 2B/4T ternary model |
| **SAGE-PTQ** | 2026 | preprint | PTQ | ~1.03-bit | FP16 | scale-overhead-minimizing dual-mode |
| **TWLA** | 2026 | ICML'26 | PTQ | 1.58-bit ternary | **4-bit** | ternary W + low-bit A (rotation) |
| **Spectral-LLM** | 2026 | preprint | PTQ | 2-bit | FP16 | Hadamard rotation + spectral scaling |
| **LBLLM** | 2026 | preprint | PTQ + distillation | W(1+1) ≈ 2-bit | **4-bit** | binary + bitmap, 3-stage distillation |
| **BWLA** | 2026 | ACL'26 | PTQ | ~1.16-bit binary | **6-bit** | orthogonal reshaping + low-rank residual |

Two macro-trends are visible in the table: (a) the field **pivoted from binary to ternary** in early 2024 (the {0} state matters — see §5.6), and (b) the 2026 work **moves activations down too** (TWLA, BWLA, LBLLM), because a 1-bit weight is wasted if activations stay FP16 and bottleneck the matmul.

---

## 3. The train-from-scratch / QAT lineage

These methods accept training cost to reach the best quality. They dominate the *quality* leaderboard but cannot be applied to an already-trained checkpoint.

### 3.1 BitNet → the binary origin (2023)

**BitNet** introduced **BitLinear**, a drop-in replacement for `nn.Linear` that stores weights as 1-bit signs (with a per-tensor scale β = ‖W‖₁/nm) and quantizes activations to INT8, trained *from scratch* with the straight-through estimator (STE) and a deliberately large learning rate (tiny latent-weight updates rarely flip a 1-bit weight). Its central result was that **billion-scale 1-bit LLMs follow the same power-law scaling as FP16 Transformers**, and that 1-bit weights trained from scratch crush every post-hoc baseline: at 6.7B, BitNet reaches 17.07 validation PPL (vs FP16 15.19), while at the same bit-width GPTQ explodes to 1032 PPL and SmoothQuant to ~3×10²¹. It also reframed efficiency around **inference energy**, projecting up to ~38× matmul-energy reduction at 30B.

### 3.2 BitNet b1.58 → the ternary pivot (2024)

**BitNet b1.58** ("The Era of 1-bit LLMs") added a third weight state, {−1, **0**, +1} = 1.58 bits, via an **absmean** quantizer (scale by mean-absolute-value, round-clip to {−1,0,1}). The zero enables explicit feature filtering, and the gain is decisive: at **3B parameters it matches FP16 LLaMA in perplexity** (9.91 vs 10.04) while being **2.71× faster and using 3.55× less memory**, rising to ~4.1× speed and 8.9× throughput at 70B. This is the field's reference point — the first demonstration that extreme low-bit is **Pareto-optimal** (better quality *and* efficiency), not merely a compression compromise. It also fixed the now-standard recipe: LLaMA-style architecture (RMSNorm, SwiGLU, RoPE, no bias) for tooling compatibility.

### 3.3 Spectra / TriLM → the scaling study (2024)

**Spectra** is the rigorous empirical backbone: an open suite of 54 models (99M–3.9B) trained on the same 300B tokens across FP16 (FloatLM), GPTQ (QuantLM), and ternary (TriLM). Its headline: **TriLM-3.9B matches FloatLM-3.9B downstream while being 5.9× smaller in bits** — fewer bits than even FloatLM-830M. It showed ternary and FP16 share the same scaling exponent (α=0.26) with converging offsets, and argued from entropy that larger models *need* fewer bits/weight. It also simplified the architecture vs BitNet (pre-norm twice per block, activations left FP16) for stability. Caveat: parity only emerges at ~2B+; below that TriLM trails FP16 at equal parameter count.

### 3.4 BitNet b1.58 2B4T → the production model (2025)

The lineage's maturation: Microsoft's **first openly-released native 1.58-bit LLM at 2B parameters trained on 4T tokens**, with open weights, training code, and the `bitnet.cpp` CPU runtime. It reaches an **0.4 GB non-embedding footprint, 29 ms CPU latency, ~0.028 J/token energy**, and an 11-benchmark average of **54.19 — second only to Qwen2.5-1.5B (55.23)** among 1–2B peers, beating full-precision LLaMA-3.2-1B (44.90), Gemma-3-1B, SmolLM2, and MiniCPM. Crucially it **beats INT4 PTQ** (Qwen2.5-1.5B GPTQ-int4 52.15, AWQ-int4 51.17) at *lower* memory, and tops all other 1-bit models including 7–8B models PTQ'd to 1.58-bit (avg 60.68 vs Falcon3-1.58bit-7B 50.76).

### 3.5 MatMul-free LM → architectural co-design (2024)

**MatMul-free LM** takes the ternary idea to its logical end: if weights are ternary, matmuls become add/subtract — so **remove matrix multiplication entirely.** Dense layers use ternary BitLinear; self-attention (which diverges under ternary Q/K) is replaced by an **MLGRU**, a linearized GRU token-mixer using only element-wise products. The result rivals Transformer++ up to 2.7B (49.9 vs 50.7 avg at 2.7B) with **>10× inference memory savings** and a fused SRAM kernel that cuts training memory 61%; it even runs on Intel Loihi 2 neuromorphic hardware at ~10× lower energy/token than an edge GPU. It signals that the ultimate payoff of low-bit weights may require **rethinking the architecture and the hardware**, not just the quantizer.

### 3.6 Converting pretrained models with QAT + distillation: OneBit & LittleBit

Two methods keep QAT's quality but start from a *pretrained* model via knowledge distillation:

- **OneBit (2024)** decomposes each weight matrix as a 1-bit **sign matrix** plus **two FP16 value vectors** (W ≈ diag(h)·sign(W)·diag(g)), so the sign preserves rank/capacity while the value vectors restore floating-point scale at ~1.01 bits/weight. Its **Sign-Value-Independent Decomposition (SVID)** initializes this structure from a pretrained model (provably tighter than rank-1 SVD on W directly), and quantization-aware distillation transfers the teacher. On LLaMA-7B it reaches **10.19 WikiText-2 PPL at 1-bit** (FP16 5.68) — retaining ≥81% of FP16 accuracy and beating 2-bit OmniQuant (15.34), where GPTQ/LLM-QAT collapse — while compressing LLaMA-7B by ~90% (13.5 GB → 1.3 GB).

- **LittleBit (2025)** pushes furthest of any method: **sub-1-bit, tunably down to 0.1 bits/weight (BPW).** It factorizes W ≈ U Vᵀ, **binarizes both factors**, and restores magnitude with three FP16 scales — row (h), column (g), and a novel **latent scale (λ)** per rank dimension — initialized by a dual-SVID scheme and trained with KD and a `SmoothSign` gradient. A residual path splits the bit budget into two low-rank corrections. At ~1 BPW it is competitive with OneBit (9.08 vs 8.36 PPL on Llama2-7B); at 0.3 BPW it holds 12.00 PPL where the prior sub-1-bit method STBLLM explodes to ~1800; and it delivers **up to 69.7× memory reduction and 11.6× kernel speedup** at 0.1 BPW. The factorization also compresses the KV cache up to 21.3×.

---

## 4. The post-training quantization (PTQ) lineage

These methods convert an existing FP16 checkpoint without (or with minimal) retraining — the practical path for the millions of already-trained models.

### 4.1 Salient-weight binary, weight-only: PB-LLM → BiLLM → SAGE-PTQ

This is the field's "main sequence" of weight-only binary PTQ, each generation pushing the effective bit-width lower while *raising* quality.

- **PB-LLM (2023)** was the first to bring binarization to LLMs, and the first to show **naive binarization collapses LLMs below random** (BNN/XNOR mean ≈0.30 vs random 0.36). Its fix — *partial binarization* — keeps a small **salient** fraction (selected element-wise by magnitude/Hessian) in high precision (8-bit) and binarizes the rest with a closed-form optimal scale α = ‖w‖₁/n. It offers both a GPTQ-based PTQ recovery (**PB-GPTQ**) and a QAT mode that freezes salient weights (converging in ~10K iters vs LLM-QAT's 100K). Its honest limitation defined the next problem: genuine sub-2-bit (5–10% salient) still degrades sharply (LLaMA-7B PPL 85.78 at 10%); usable quality lived at 30–50% salient (≈3–5 effective bits).

- **BiLLM (2024)** closed that gap, reaching **~1.1 effective bits with usable accuracy** and no training. Two ideas: (1) **residual binarization** of Hessian-salient *columns* (binarize, then binarize the residual — effectively 2 bits there, provably lower error than one sign); (2) an **optimal-split** of the bell-shaped non-salient weights into a concentrated and a sparse region, each binarized separately. Run inside GPTQ-style error compensation, it binarizes a 7B model in ~30 min and beats PB-LLM and 2-bit GPTQ at lower bit-width — e.g. LLaMA-2-7B 32.48 PPL at 1.08-bit (vs PB-LLM 69.20, GPTQ-2bit 60.45), and at 70B scale it even undercuts FP16 OPT-66B's perplexity.

- **SAGE-PTQ (2026)** attacks an overlooked cost: the **bits spent on the scales themselves.** Prior binary methods spend ~1 bit/weight on group scales; SAGE-PTQ gets that to **0.004 bit/weight** via a single per-channel scale for salient weights and one scalar per ternary-binarized unsalient group, choosing the number of groups per layer by treating subsampled weights as a sparse graph (spectral clustering + silhouette score) and setting the salient ratio by convex optimization. The result is **~1.03 bits with near-FP16 quality**: LLaMA-3-8B 6.74 PPL (BiLLM 55.80, PB-LLM 73.08), LLaMA-2-7B 5.87 (FP16 5.47), with ~50% less GPU memory than BiLLM and 1.5× faster decoding — a remarkable claim (≈5× lower PPL than BiLLM) for a recent preprint.

### 4.2 Rotation, reshaping, and joint weight+activation low-bit (2026)

The newest wave recognizes that **binary/ternary weights only speed up inference if activations are also low-bit**, and uses *transforms* to make heavy-tailed weights and activations quantization-friendly.

- **Spectral-LLM (2026)** is a drop-in, **math-invariant pre-quantization transform** for 2-bit weight-only: a fixed **Walsh-Hadamard rotation** plus closed-form **spectral-energy per-channel scaling** that steers the rounding budget toward high-energy coordinates before feeding off-the-shelf AutoRound. It cuts W2A16 WikiText-2 PPL by **15–58%** over vanilla AutoRound on small Llama/Qwen models, argues that learned-rotation methods' adaptivity is largely recoverable in *closed form*, and deploys via OpenVINO on Intel CPU/NPU/GPU. (Caveat: compared only against AutoRound, on perplexity, on ≤1.5B models.)

- **TWLA (2026)** is the **first PTQ recipe to pair ternary (1.58-bit) weights with 4-bit activations.** Three coupled modules: a calibration-aware asymmetric ternary quantizer (E2M-ATQ) that minimizes true *layer-output* error; a **Kronecker orthogonal rotation** (KOTMS) optimized to reshape unimodal weights into a ternary-friendly *tri-modal* distribution while the same rotation suppresses activation outliers; and an **inter-layer-aware mixed-precision** allocator (ILA-AMP) solved by dynamic programming. It keeps LLaMA-2-70B W1.58A4 at 4.77 PPL / 71.1% avg (>92% of FP16) and delivers **3.64× end-to-end speedup** over FP16 via llama.cpp ternary kernels — all without gradient retraining (vs BitNet v2's >10⁴ GPU-hours).

- **BWLA (2026)** is the analogous breakthrough for **binary** weights + low-bit activations (W1Ax). Its **Orthogonal-Kronecker Transformation** *provably* converts unimodal Gaussian weight rows into a symmetric **bimodal** mixture that binarizes cleanly, while (being orthogonal) the same transform flattens activation tails; a **low-rank proximal-SVD residual** recovers the rest. At ~1.16-bit it reaches LLaMA-2-7B 9.96 PPL (W1A16) / 12.19 (W1A6) — >70% below BiLLM — and gives 3.26× speedup with >80% memory savings, holding up on the Qwen3 family where BiLLM/ARB-LLM collapse.

- **LBLLM (2026)** reaches **W(1+1)A4** (a binary weight plus a 1-bit group bitmap ≈ 2 effective bits, *no* high-precision channels and *no* rotations) through a **three-stage distillation** that decouples the work: PTQ warm-start → layer-wise distillation of binary weights with FP activations → a learnable distribution-aware 4-bit activation quantizer. Decoupling avoids the gradient interference that sinks naive joint training. It beats prior binarization in the same regime by >10 PPL (LLaMA-2-7B 9.18 vs BiLLM 32.48, QuaRot-W2A4 49.98) while training on only **0.016B tokens on a single GPU** (vs FBI-LLM's 108.5B tokens / 22,599 GPU-hours).

### 4.3 Improving ternary training cheaply: Tequila (2025)

Sitting between the paradigms, **Tequila** is a QAT method that diagnoses **"deadzone trapping"**: under ternary QAT, weights near zero get rounded to {0}, receive only noisy STE gradients, and stay permanently inactive. It **reactivates** them as a differentiable adaptive bias (λ·wᵢ, bypassing the STE) that — exploiting symmetric activations — folds into an offline per-channel bias with <0.1% inference overhead. The payoff is **training efficiency**: it closes most of the ternary-to-FP gap (<1% on ARC) with only **10B QAT tokens**, beating BitNet, Spectra, and ParetoQ that used 100B+ tokens, and matching ternary BitNet's 3× CPU speedup.

---

## 5. Cross-cutting techniques

The 15 methods recombine a compact toolkit. Reading the field as *techniques* rather than papers clarifies what actually makes sub-2-bit work.

| Technique | Methods using it |
|---|---|
| **Saliency / partial precision** (keep a few important weights high-bit) | PB-LLM, BiLLM, SAGE-PTQ |
| **Hessian / error compensation** (GPTQ-OBC lineage) | PB-LLM, BiLLM, SAGE-PTQ |
| **Sign-value / low-rank factorization** | OneBit, LittleBit |
| **Orthogonal rotation** (Hadamard / Kronecker) | Spectral-LLM, TWLA, BWLA |
| **Distribution reshaping** (toward bi-/tri-modal) | TWLA, BWLA |
| **Knowledge distillation** | OneBit, LittleBit, LBLLM, (PB-LLM QAT) |
| **Train-from-scratch QAT** | BitNet, BitNet b1.58, Spectra, BitNet 2B4T, MatMul-free |
| **Joint weight + low-bit activation** | TWLA, BWLA, LBLLM, (BitNet family A8) |
| **Scale/metadata-overhead minimization** | SAGE-PTQ, BWLA, TWLA (Kronecker) |
| **Sub-1-bit factorization** | LittleBit |

A few deserve emphasis:

- **5.1 Saliency.** The founding insight (PB-LLM) that a tiny fraction of weights carry disproportionate importance recurs everywhere. The trajectory PB-LLM → BiLLM → SAGE-PTQ is essentially *how to spend ever fewer bits on the salient set and its bookkeeping.*
- **5.2 Hessian error compensation.** GPTQ/OBC second-order compensation (rooted in classical Optimal Brain Surgeon) is the workhorse of every strong weight-only PTQ method here.
- **5.3 Sign-value decomposition & factorization.** Separating a 1-bit *sign* from a few FP16 *magnitude* parameters (OneBit) — or binarizing the *factors* of a low-rank decomposition (LittleBit) — is what makes ~1-bit and sub-1-bit representable at all.
- **5.4 Rotations.** Hadamard/Kronecker orthogonal transforms (from QuaRot/QuIP# lineage) are the 2026 enabler for joint W+A low-bit: one transform simultaneously reshapes weights toward a binarization-friendly distribution *and* suppresses activation outliers, at near-zero stored overhead via Kronecker factorization.
- **5.5 Distillation.** Whenever a *pretrained* model is pushed to ~1 bit, KD from the FP16 teacher (logit + hidden-state matching) is what recovers usable quality (OneBit, LittleBit, LBLLM).
- **5.6 The zero state.** The single most consequential design choice in the field: moving from binary {−1,+1} to ternary {−1,0,+1} (BitNet → BitNet b1.58). The extra 0.58 bits buys feature *filtering* and is what lifted from-scratch models to FP16 parity.

---

## 6. Comparative analysis

### 6.1 PTQ on LLaMA-2-7B (WikiText-2 perplexity, FP16 = 5.47)

Apples-to-apples is impossible (different W/A and bit accounting), so W/A and effective bits are annotated.

| Method | Eff. weight bits | Activations | WikiText-2 PPL | Notes |
|---|---|---|---|---|
| SAGE-PTQ | ~1.03 | FP16 | **5.87** | weight-only; near-lossless claim |
| TWLA | 1.58 | FP16 | 6.97 | ternary |
| TWLA | 1.58 | 4-bit | 8.31 | joint W+A (mixed) |
| LittleBit | ~1.0 BPW | FP16 | 9.08 | factorized |
| LBLLM | ~2 (1+1) | 4-bit | 9.18 | distillation |
| OneBit | ~1.01 | FP16 | 9.73 | sign-value (QAT+KD) |
| BWLA | ~1.16 | FP16 | 9.96 | rotation |
| LittleBit | 0.3 BPW | FP16 | 12.00 | sub-1-bit |
| BWLA | ~1.16 | 6-bit | 12.19 | joint W+A |
| BiLLM | ~1.08 | FP16 | 32.48 | 2024 binary SOTA |
| PB-LLM (PB-GPTQ 10%) | ~2.7 | FP16 | 85.78† | †LLaMA-1-7B |

**Reading:** at ~1-bit weight-only, the field improved roughly **BiLLM (32) → OneBit (9.7) → BWLA (10) → TWLA (7.0) → SAGE-PTQ (5.9)** in two years. The 2026 PTQ results approaching FP16 at ~1 bit are the most surprising development — and the most in need of independent confirmation.

### 6.2 Train-from-scratch models (own training, ≠ PTQ above)

| Model | Bits | Result |
|---|---|---|
| BitNet b1.58 (3B) | 1.58 / A8 | Matches FP16 LLaMA-3B PPL (9.91 vs 10.04); 2.71× faster, 3.55× less memory |
| Spectra TriLM (3.9B) | 1.58 | Matches FloatLM-3.9B downstream at **5.9× fewer bits** |
| BitNet b1.58 2B4T | 1.58 / A8 | 11-bench avg **54.19** (2nd of 6 among 1–2B peers); beats INT4 PTQ at lower memory |
| MatMul-free (2.7B) | 1.58 | 49.9 vs Transformer++ 50.7 avg; >10× inference memory savings |

**Reading:** from-scratch ternary models reach **FP16 parity at ~3B** and are clearly the quality leaders — at the cost of being un-applicable to existing checkpoints.

### 6.3 Where each paradigm wins

- **Best quality, have the training budget / building a new model →** ternary train-from-scratch (BitNet b1.58 → 2B4T).
- **Must quantize an existing FP16 model, weight-only →** SAGE-PTQ (2026) or BiLLM (battle-tested 2024).
- **Want real end-to-end speedup (low-bit activations too) →** TWLA (ternary W + A4) or BWLA (binary W + A6).
- **Maximum compression, sub-1-bit →** LittleBit.
- **~1-bit from a pretrained model with strong quality →** OneBit (mature) or LittleBit at ~1 BPW.

---

## 7. Open challenges and future directions

1. **Activations are the remaining wall.** Even the best models keep activations at INT8 (BitNet family) or FP16 (most PTQ). True W1A4 is only just emerging (TWLA, BWLA, LBLLM) and degrades at A4 (BWLA explicitly weakens at W1A4). Co-designing weight *and* activation quantization is the open frontier.
2. **Hardware is the bottleneck for realized gains.** Almost every reported speedup needs custom kernels (`bitnet.cpp`, BitBLAS, Marlin-style) or non-commodity hardware (Loihi 2); commodity GPUs have no native W1.58A8 path. The energy/latency promise is real but **hardware-gated**.
3. **PTQ vs train-from-scratch is converging — verify it.** 2026 PTQ methods claim near-FP16 at ~1 bit (SAGE-PTQ 5.87 on LLaMA-2-7B), rivaling from-scratch QAT without its cost. If replicated, this is field-changing; these are recent, single-team preprints and warrant independent reproduction.
4. **Small/newer models are harder.** Across the board (Tequila, LBLLM, Spectra), parity needs scale (≥3B); newer dense models (LLaMA-3/Qwen3) degrade more than LLaMA-1/2 at the same bit-width.
5. **Evaluation gaps.** Several strong 2026 entries report perplexity on subsets, single seeds, or limited baselines (Spectral-LLM vs only AutoRound; no FP16-gap-closure metric). The field needs standardized sub-2-bit benchmarks (consistent harness, full WikiText-2/C4 + downstream + reasoning, multiple seeds).
6. **Theory lags practice.** Why native 1-bit training works at scale (BitNet 2B4T), and why closed-form rotations recover learned-rotation gains (Spectral-LLM), remain open. The information-theoretic "bigger ⇒ fewer bits" story (Spectra) is suggestive but not yet a predictive theory.

---

## 8. Conclusion

In roughly three years the sub-2-bit field matured from "binarization destroys LLMs" (PB-LLM, 2023) to **ternary models that match FP16 from scratch** (BitNet b1.58 / 2B4T) and **post-training methods that approach FP16 at ~1 bit** (SAGE-PTQ, BWLA, TWLA, 2026). The decisive ideas were the **ternary {0} state**, **saliency-aware mixed precision**, **sign-value/factorized representations**, and — most recently — **orthogonal rotations that make both weights and activations quantization-friendly at once**. The two paradigms are converging: from-scratch QAT still leads on quality, but PTQ is closing the gap fast and is the only route for existing models. The binding constraints going forward are **low-bit activations** and **hardware support** — the algorithms are increasingly ahead of the silicon that can cash in their gains.

---

## References

All PDFs are in `papers/04_Extreme_Low-Bit/`. arXiv IDs verified against the downloaded papers.

1. **PB-LLM: Partially Binarized Large Language Models.** Shang, Yuan, Wu, Dong. ICLR 2024. arXiv:[2310.00034](https://arxiv.org/abs/2310.00034) — `pb-llm.pdf`
2. **BitNet: Scaling 1-bit Transformers for LLMs.** Wang et al. 2023. arXiv:[2310.11453](https://arxiv.org/abs/2310.11453) — `bitnet.pdf`
3. **OneBit: Towards Extremely Low-bit Large Language Models.** Xu et al. NeurIPS 2024. arXiv:[2402.11295](https://arxiv.org/abs/2402.11295) — `onebit.pdf`
4. **The Era of 1-bit LLMs: All LLMs are in 1.58 Bits (BitNet b1.58).** Ma et al. 2024. arXiv:[2402.17764](https://arxiv.org/abs/2402.17764) — `bitnet-b158.pdf`
5. **BiLLM: Pushing the Limit of Post-Training Quantization for LLMs.** Huang et al. ICML 2024. arXiv:[2402.04291](https://arxiv.org/abs/2402.04291) — `billm.pdf`
6. **Scalable MatMul-free Language Modeling.** Zhu et al. 2024. arXiv:[2406.02528](https://arxiv.org/abs/2406.02528) — `matmul-free.pdf`
7. **Spectra: A Comprehensive Study of Ternary, Quantized, and FP16 Language Models (TriLM).** Kaushal, Vaidhya, Garg. 2024. arXiv:[2407.12327](https://arxiv.org/abs/2407.12327) — `spectra.pdf`
8. **Tequila: Deadzone-free Ternary Quantization for LLMs.** Huang et al. ICLR 2026. arXiv:[2509.23809](https://arxiv.org/abs/2509.23809) — `tequila.pdf`
9. **LittleBit: Ultra Low-Bit Quantization via Latent Factorization.** Lee, Kim, You, Kim. NeurIPS 2025. arXiv:[2506.13771](https://arxiv.org/abs/2506.13771) — `littlebit.pdf`
10. **BitNet b1.58 2B4T Technical Report.** Ma et al. 2025. arXiv:[2504.12285](https://arxiv.org/abs/2504.12285) — `bitnet-2b4t.pdf`
11. **Minimizing the Hidden Cost of Scales: Graph-Guided Ultra-Low-Bit Quantization (SAGE-PTQ).** Abdalla et al. 2026. arXiv:[2606.05429](https://arxiv.org/abs/2606.05429) — `sage-ptq.pdf`
12. **TWLA: Ternary Weights and Low-Bit Activations for LLMs via PTQ.** Zhao et al. ICML 2026. arXiv:[2606.13054](https://arxiv.org/abs/2606.13054) — `twla.pdf`
13. **Influence-Inspired Spectral Rotations for Extreme Low-Bit LLM Quantization.** Pavlov. 2026. arXiv:[2605.25203](https://arxiv.org/abs/2605.25203) — `spectral-llm.pdf`
14. **LBLLM: Lightweight Binarization of LLMs via Three-Stage Distillation.** Song et al. 2026. arXiv:[2604.19167](https://arxiv.org/abs/2604.19167) — `lbllm.pdf`
15. **BWLA: Breaking the Barrier of W1AX Post-Training Quantization for LLMs.** Zhao, Xu, Yang. ACL 2026. arXiv:[2605.00422](https://arxiv.org/abs/2605.00422) — `bwla.pdf`
