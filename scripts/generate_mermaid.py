#!/usr/bin/env python3
"""
generate_mermaid.py — Writes one .mmd Mermaid flowchart per method in assets/mermaid/.

Each .mmd file can be rendered in VS Code (Mermaid extension), GitHub, or embedded
in the README as a ```mermaid code block.

Usage:
    python scripts/generate_mermaid.py              # generate missing files only
    python scripts/generate_mermaid.py --all        # regenerate all
    python scripts/generate_mermaid.py --id gptq    # one specific method
"""

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
MERMAID_DIR = ROOT / "assets" / "mermaid"

# ─────────────────────────────────────────────────────────────────────────────
# Custom flowcharts for key methods
# ─────────────────────────────────────────────────────────────────────────────

CUSTOM = {

"obs": """\
flowchart LR
    A[Layer output error\\nE = trace of H * delta_W^2] --> B[Choose weight\\nwith min saliency]
    B --> C[Set weight to zero\\n/ quantize it]
    C --> D[Update remaining\\nweights via H^-1]
    D --> E{More weights?}
    E -->|yes| B
    E -->|no| F[Compressed layer\\n+ error compensation]
""",

"obq": """\
flowchart LR
    A[Weight matrix W\\n+ Hessian H] --> B[Compute per-weight\\nsaliency score]
    B --> C[Select least-salient\\nweight]
    C --> D[Quantize it to\\nlow-bit value]
    D --> E[Redistribute error:\\nW remaining -= delta * H^-1 row]
    E --> F{All weights\\nquantized?}
    F -->|no| B
    F -->|yes| G[Low-bit W\\nwith OBS error comp]
""",

"gptq": """\
flowchart LR
    A[FP16 Weight W] --> B[Compute Hessian\\nH = 2XX^T]
    B --> C[Cholesky\\ndecompose H^-1]
    C --> D{For each\\ncolumn q}
    D --> E[Quantize col\\nto INT4]
    E --> F[Redistribute error\\nto cols q+1 onward]
    F --> D
    D --> G[INT4 W\\n+ group scales]
""",

"awq": """\
flowchart LR
    A[Calibration\\nActivations X] --> B[Per-channel\\nmagnitude norm_x_j]
    B --> C[Scale s_j = norm_x_j ^ alpha]
    C --> D[W_hat = Q of W times diag_s]
    D --> E[Absorb s^-1 into\\nprevious layer]
    E --> F[W4A16\\ndeployment]
""",

"spqr": """\
flowchart LR
    A[FP16 Weight W] --> B[Sensitivity via\\nHessian H]
    B --> C{Outlier weight?}
    C -->|yes ~1%| D[Store in\\nFP16 sparse]
    C -->|no ~99%| E[Quantize to\\n3-4 bit group]
    D --> F[Sparse FP16\\n+ dense INT3/4]
    E --> F
    F --> G[~3.9 bit avg\\nnear-lossless]
""",

"squeezellm": """\
flowchart LR
    A[Weight W] --> B[Fisher info\\nsensitivity map]
    B --> C[Top-k sensitive\\nweights → sparse FP16]
    C --> D[Rest → k-means\\nclustered INT4]
    D --> E[Dense INT4\\n+ sparse FP16 residual]
    E --> F[Non-uniform quant\\nbetter than uniform at same bits]
""",

"owq": """\
flowchart LR
    A[Weight W\\n+ activation stats] --> B[Identify outlier-\\ninfluenced columns]
    B --> C[Outlier cols:\\nhigher bit width or FP16]
    C --> D[Remaining cols:\\nlow-bit GPTQ quantize]
    D --> E[Mixed-precision\\nper column]
    E --> F[Better accuracy\\nthan uniform GPTQ]
""",

"quip": """\
flowchart LR
    A[FP16 Weight W] --> B[Random orthogonal\\nrotation R]
    B --> C[Incoherent W_tilde = R W R^T]
    C --> D[Near-Gaussian\\ndistribution]
    D --> E[Uniform scalar\\nquantize W_tilde]
    E --> F[At inference:\\ndecode via R^T * Q * R]
    F --> G[Incoherence enables\\nlow-bit near-lossless]
""",

"quip-sharp": """\
flowchart LR
    A[FP16 Weight W] --> B[Random Hadamard\\nrotation H]
    B --> C[Incoherent W_tilde = HWH^T]
    C --> D[E8 lattice\\ncodebook quantize]
    D --> E[Store codebook\\nindices only]
    E --> F[Lookup-table\\ndecode at inference]
    F --> G[W2A16\\nnear-lossless]
""",

"aqlm": """\
flowchart LR
    A[Weight col w in R^d] --> B[Split into\\nm sub-vectors]
    B --> C[M learned\\ncodebooks C_1 to C_m]
    C --> D[Find nearest\\ncentroid per sub-vec]
    D --> E[Store M indices\\nper group]
    E --> F[Decode w_hat = sum C_i idx_i]
    F --> G[2-3 bit\\neffective storage]
""",

"qtip": """\
flowchart LR
    A[FP16 Weight W] --> B[Hadamard rotation\\nincoherence preprocessing]
    B --> C[Near-Gaussian\\nweight distribution]
    C --> D[Trellis-coded quant:\\ndynamic programming\\nover weight sequence]
    D --> E[Viterbi-style joint\\nerror minimization]
    E --> F[Store trellis\\nstate indices]
    F --> G[Fast CUDA\\ndecode kernel]
    G --> H[W2A16 state-of-art\\n< 0.3 ppl vs FP16]
""",

"hqq": """\
flowchart LR
    A[Weight W] --> B[Minimize L1\\nnorm W - Q W_s_z]
    B --> C[Proximal\\niterative solve]
    C --> D{Converged?}
    D -->|no| B
    D -->|yes| E[Optimal scale s\\nzero-point z]
    E --> F[No calibration data\\nW4/W2 in under 1 min]
""",

"omniquant": """\
flowchart LR
    A[Calibration data] --> B[Learnable Weight\\nClipping LWC]
    A --> C[Learnable Equiv\\nTransform LET]
    B --> D[Optimize clip\\nthresholds end-to-end]
    C --> E[Learn channel\\nscale and shift]
    D --> F[Block-wise KD\\nfrom FP16 teacher]
    E --> F
    F --> G[W4A16, W4A4\\nor W6A6 model]
""",

"autoround": """\
flowchart LR
    A[FP16 weights\\n+ calibration data] --> B[SignSGD optimizer\\nfor scale and zero-point]
    B --> C[Fake quant in\\nforward pass]
    C --> D[Gradient via\\nSTE backprop]
    D --> E{Converged?}
    E -->|no| B
    E -->|yes| F[INT4 weights\\nAutoGPTQ-compatible format]
""",

"flute": """\
flowchart LR
    A[Weight group\\ng elements] --> B[k-means cluster\\ninto 2^b centroids]
    B --> C[Store b-bit indices\\nper element]
    C --> D[FLUTE CUDA kernel:\\nlookup indices → FP16]
    D --> E[Fuse decode +\\nGEMM accumulation]
    E --> F[Single kernel\\nno separate dequant]
    F --> G[W3/W4 throughput\\nnear FP16 GEMM]
""",

"marlin": """\
flowchart LR
    A[INT4 weights\\nGPTQ format] --> B[Permute for\\nmemory coalescing]
    B --> C[Marlin kernel:\\nfuse dequant + GEMM]
    C --> D[128-thread warps\\npipeline async loads]
    D --> E[FP16 GEMM throughput\\nnear theoretical peak]
    E --> F[2.4x faster than\\ntorch W4A16 baseline]
""",

"llm-int8": """\
flowchart LR
    A[Input X] --> B{Outlier\\ndetector}
    B -->|outlier dims ~0.1%| C[FP16 matmul]
    B -->|normal dims ~99.9%| D[INT8 quantize]
    D --> E[INT8 matmul]
    C --> F[Dequant + combine]
    E --> F
    F --> G[FP16 output]
""",

"smoothquant": """\
flowchart LR
    A[FP16 Act X\\noutlier channels] --> B[Compute smooth\\nfactor s_j per channel]
    B --> C[X_tilde = X div diag_s]
    B --> D[W_tilde = diag_s times W]
    C --> E[Quantize X_tilde\\nto INT8]
    D --> F[Quantize W_tilde\\nto INT8]
    E --> G[INT8 GEMM\\ntensor cores]
    F --> G
""",

"zeroquant": """\
flowchart LR
    A[LLM layer] --> B[Token-wise\\nact quant INT8]
    A --> C[Group-wise\\nweight quant INT8]
    B --> D[INT8 GEMM\\ncustom CUDA kernel]
    C --> D
    D --> E{High degradation?}
    E -->|yes| F[Layer-wise KD\\nfrom FP16 teacher]
    F --> G[W8A8 model]
    E -->|no| G
""",

"zeroquant-v2": """\
flowchart LR
    A[Quantized model] --> B[Measure per-block\\nreconstruction error]
    B --> C{Error too high?}
    C -->|yes| D[Add low-rank\\ncompensation matrix]
    D --> E[W * A_r * B_r\\nadded to quantized W]
    C -->|no| F[Keep quantized block]
    E --> G[W4A8 or W8A8\\n+ LoRC correction]
    F --> G
""",

"zeroquant-fp": """\
flowchart LR
    A[FP16 model] --> B{Choose format}
    B -->|weights| C[FP4 vs INT4\\ncomparison]
    B -->|activations| D[FP8 vs INT8\\ncomparison]
    C --> E[FP4 wins on\\noutlier robustness]
    D --> F[FP8 E4M3 wins\\nfor activations]
    E --> G[W4A8 FP-based\\nbetter than INT at same bits]
    F --> G
""",

"zeroquant-4plus2": """\
flowchart LR
    A[All layers] --> B[Measure quantization\\nsensitivity per block]
    B --> C[Sort blocks\\nby sensitivity score]
    C --> D{Top-k%\\nsensitive?}
    D -->|yes| E[Assign FP6\\nTC-FPx kernel]
    D -->|no| F[Assign W4A8\\nZeroQuant style]
    E --> G[Mixed 4+2 model\\n~4.X bit average]
    F --> G
""",

"outlier-suppression": """\
flowchart LR
    A[LayerNorm gamma\\noutlier generator] --> B[Gamma Migration:\\nabsorb scale into\\nadjacent linear]
    B --> C[Smoother activations]
    C --> D[Token-wise clipping:\\nper-token asymmetric quant]
    D --> E[Optimal clip threshold\\nper token]
    E --> F[W8A8 / W6A6\\nno decomposition needed]
""",

"outlier-suppression-plus": """\
flowchart LR
    A[Activation channel X_j] --> B[Compute optimal\\nshift t_j and scale s_j]
    B --> C[Shifted X_j_shifted = X_j - t_j]
    C --> D[Zero-centered\\nsymmetric distribution]
    D --> E[Scale X_j_shifted / s_j]
    E --> F[INT8 quantize]
    F --> G[Absorb t_j and s_j\\ninto adjacent weights]
    G --> H[W8A8 / W4A8\\nanalytical optimal]
""",

"rptq": """\
flowchart LR
    A[Activation channels] --> B[Group channels by\\nsimilar range]
    B --> C[Channel reordering:\\noutliers grouped together]
    C --> D[Cluster-wise\\nquantization per group]
    D --> E[Outliers share\\nscale within group]
    E --> F[W4A8 / W4A4\\nno decomposition overhead]
""",

"atom": """\
flowchart LR
    A[LLM layer] --> B{Channel type}
    B -->|outlier ~1%| C[INT8 / FP16]
    B -->|normal ~99%| D[INT4 group quant]
    D --> E[Dynamic per-token\\nact quantization]
    C --> F[INT4 GEMM\\nCUTLASS kernels]
    E --> F
    F --> G[KV INT4 cache]
    G --> H[W4A4KV4 serving]
""",

"quarot": """\
flowchart LR
    A[FP16 LLM] --> B[Random Hadamard\\nmatrix R]
    B --> C[Rotate weights offline\\nW_tilde = W times R^T]
    B --> D[Rotate acts online\\nX_tilde = X times R]
    C --> E[Uniform dist\\nno outliers]
    D --> E
    E --> F[W4A4\\nquantization]
""",

"spinquant": """\
flowchart LR
    A[Random rotation R_0] --> B[Optimize via\\nCayley SGD]
    B --> C{Stiefel manifold\\nconstraint met?}
    C -->|no| B
    C -->|yes| D[Learned R*\\northogonal matrix]
    D --> E[Fold into W and X offline]
    E --> F[W4A4 / W4A8\\nlow-outlier inference]
""",

"duquant": """\
flowchart LR
    A[FP16 Activations] --> B[Stage 1: Rotation\\nHadamard spreading]
    B --> C[Reduced outliers\\nbut residuals remain]
    C --> D[Stage 2: Permutation\\nreorder channels by range]
    D --> E[Residual outliers\\ngrouped and compressed]
    E --> F[W4A4 state-of-art\\ndual transformation]
""",

"flatquant": """\
flowchart LR
    A[Layer activations] --> B[Learnable Kronecker\\naffine transform A]
    B --> C[Calibrate A per-layer\\nto flatten distribution]
    C --> D{Flat enough?}
    D -->|no| C
    D -->|yes| E[Apply A offline to W]
    E --> F[Flat activation dist\\nno rotation overhead]
    F --> G[W4A4 low-error]
""",

"qllm": """\
flowchart LR
    A[Outlier activation\\nchannel j] --> B{Action}
    B -->|large outlier| C[Channel disassembly:\\nsplit into k sub-channels]
    B -->|near-zero| D[Channel assembly:\\nmerge with neighbor]
    C --> E[Equivalent transform\\nno accuracy loss]
    D --> E
    E --> F[All channels in\\nnormal quantizable range]
    F --> G[W4A8 / W4A4]
""",

"affine-quant": """\
flowchart LR
    A[FP16 model] --> B[Optimize full affine\\ntransform matrix T]
    B --> C[W_equiv = T times W\\nX_equiv = X times T^-1]
    C --> D[Newton-step solver\\nfor T efficiently]
    D --> E{Converged?}
    E -->|no| B
    E -->|yes| F[Generalized SmoothQuant:\\nfull linear vs diagonal]
    F --> G[W4A4 / W4A8\\nbetter than SmoothQuant]
""",

"qserve": """\
flowchart LR
    A[FP16 model] --> B[GPTQ W4\\nweight quant]
    B --> C[SmoothAttention\\nfor KV4]
    C --> D[W4 to INT8\\nfused dequant kernel]
    D --> E[INT8 GEMM\\ntensor cores]
    E --> F[W4A8KV4\\n2x vs W4A16]
""",

"qlora": """\
flowchart LR
    A[FP16 base model] --> B[Quantize to NF4\\n4-bit frozen]
    B --> C[Frozen NF4\\nbase weights]
    C --> D[LoRA adapters\\ndelta W = B times A in BF16]
    D --> E[Forward: dequant NF4 to BF16 + delta W]
    E --> F[Backprop only\\nthrough adapters A, B]
    F --> G[65B model\\nfits on 48 GB GPU]
""",

"llm-qat": """\
flowchart LR
    A[FP16 pretrained\\nLLM] --> B[Insert fake quant\\nnodes throughout]
    B --> C[Forward: quantize\\nweights + activations]
    C --> D[Loss on labeled data\\nor self-supervised]
    D --> E[Backprop through\\nSTE for quant nodes]
    E --> F{Converged?}
    F -->|no| C
    F -->|yes| G[Quantized LLM\\nbetter than PTQ at same bits]
""",

"peqa": """\
flowchart LR
    A[Quantized base model\\nINT4 / INT8] --> B[Freeze quantized\\nbase weights]
    B --> C[Add task-specific\\nFP16 bias vectors]
    C --> D[Fine-tune only\\nbias parameters]
    D --> E[Tiny parameter count\\n<< full fine-tune]
    E --> F[Task-adapted\\nquantized model]
""",

"loftq": """\
flowchart LR
    A[FP16 pretrained W] --> B[SVD: W approx A times B\\nlow-rank init]
    B --> C[Quantize W - A times B\\nresidual to INT4]
    C --> D[New residual\\nR = W - Q_int4]
    D --> E[SVD of R to update\\nA and B]
    E --> F{Iterations done?}
    F -->|no| C
    F -->|yes| G[Aligned INT4 base\\n+ LoRA A, B init]
    G --> H[Fine-tune A, B\\nbetter start than random]
""",

"qa-lora": """\
flowchart LR
    A[INT4 quantized\\nbase model] --> B[Group-wise LoRA:\\nrank = group size]
    B --> C[Adapter A, B have\\nsame granularity as quant groups]
    C --> D[Fine-tune adapters\\nwith QA-aware gradients]
    D --> E[Merge A, B into\\nquantized weights]
    E --> F[No extra inference\\noverhead after merge]
""",

"bitdistiller": """\
flowchart LR
    A[FP16 teacher model] --> B[Soft targets\\n+ intermediate features]
    B --> C[Quantized student\\nINT2 / INT3]
    C --> D[Knowledge distillation\\nloss KL + MSE]
    D --> E[Student learns\\nto mimic teacher]
    E --> F{Training done?}
    F -->|no| C
    F -->|yes| G[High-quality\\nextreme-bit model]
""",

"efficientqat": """\
flowchart LR
    A[FP16 LLM] --> B[Phase 1: Block-AP\\nblock-wise quant param train]
    B --> C[Freeze surrounding blocks\\ntrain scales and zeros]
    C --> D[Phase 2: E2E-QP\\nend-to-end quant param finetune]
    D --> E{All blocks done?}
    E -->|no| B
    E -->|yes| F[W4A8 or W2A16\\nhigh-quality QAT]
""",

"pv-tuning": """\
flowchart LR
    A[AQLM codebook\\nquantized model] --> B[Directly optimize\\ncodebook entries]
    B --> C[Per-vector gradient\\nvia straight-through]
    C --> D[Update codebook\\ncentroids end-to-end]
    D --> E{Converged?}
    E -->|no| B
    E -->|yes| F[Better codebooks\\nthan init-only AQLM]
    F --> G[W2A16 state-of-art\\nvector quant]
""",

"ir-qlora": """\
flowchart LR
    A[QLoRA model\\nINT4 + LoRA] --> B[Measure inter-layer\\nfeature correlation]
    B --> C[Identify redundant\\nLoRA rank dimensions]
    C --> D[Prune redundant\\nrank components]
    D --> E[Reinitialize pruned\\nrank with new directions]
    E --> F{Iterations done?}
    F -->|no| B
    F -->|yes| G[Compact LoRA\\nbetter QLoRA baseline]
""",

"apiq": """\
flowchart LR
    A[Calibration activations] --> B[Compute activation\\ncovariance stats]
    B --> C[Design per-layer\\nquantization grid]
    C --> D[Grid aligned to\\nactivation principal components]
    D --> E[Quantize W on\\naligned grid]
    E --> F[Better W4A16\\nactivation-aware grid]
""",

"bitnet": """\
flowchart LR
    A[FP16 training] --> B[Binary weights\\n+1 or -1 via sign]
    B --> C[Straight-through\\nestimator STE]
    C --> D[Scale factor\\nalpha = mean of abs W]
    D --> E[W_tilde = alpha times sign W]
    E --> F[MatMuls replaced\\nby additions + scaling]
    F --> G[1-bit LLM\\ntraining from scratch]
""",

"bitnet-b158": """\
flowchart LR
    A[Training from scratch] --> B[Ternary weights\\n-1, 0, +1]
    B --> C[Straight-through\\nestimator STE]
    C --> D[AbsMean\\nact quantization INT8]
    D --> E[MatMuls become\\nadditions only]
    E --> F[1.58-bit model\\nmatches FP16 at 3B+]
""",

"bitnet-2b4t": """\
flowchart LR
    A[2B param architecture\\nBitNet b1.58 design] --> B[Train on 4T tokens\\nfrom scratch]
    B --> C[Ternary weights -1/0/+1\\nthroughout training]
    C --> D[INT8 activations\\nAbsMax quantization]
    D --> E[First open-source\\n1-bit 2B model]
    E --> F[Competitive with\\nFP16 Llama-3.2-1B/3B]
""",

"pb-llm": """\
flowchart LR
    A[FP16 LLM weights] --> B[Compute per-weight\\nHessian sensitivity]
    B --> C{Salient weight?}
    C -->|yes top-p%| D[Keep in FP16\\nor INT8]
    C -->|no| E[Binarize to +1/-1]
    E --> F[Scale factor\\nper group]
    D --> G[Mixed: FP16 salient\\n+ binary rest]
    F --> G
""",

"billm": """\
flowchart LR
    A[LLM weights] --> B[Bell-shaped analysis:\\nidentify salient values]
    B --> C[Salient set:\\nresidual approximation]
    C --> D[Non-salient set:\\nbinary +1/-1]
    D --> E[Optimal rescaling\\nfor binary group]
    C --> F[Store residuals\\nin sparse format]
    D --> F
    F --> G[Post-training\\n1-bit with residuals]
""",

"onebit": """\
flowchart LR
    A[Weight W] --> B[Sign-value decomp:\\nW = V times sign S]
    B --> C[V: value vectors\\nper output channel]
    C --> D[S: binary sign\\nmatrix INT1]
    D --> E[Forward: W_hat = V times S]
    E --> F[STE training\\nfrom scratch or QAT]
    F --> G[1-bit with value\\nvectors = better than plain binary]
""",

"matmul-free": """\
flowchart LR
    A[Transformer block] --> B[Replace all linear\\nlayers]
    B --> C[Ternary weights\\n-1, 0, +1]
    C --> D[Binary activations\\nHardtanh clipped]
    D --> E[Attention alternative:\\nTokenMixer replaces\\nQK^T matmul]
    E --> F[Pure additions\\nno multiplications]
    F --> G[1-bit W, 1-bit A\\ntrue integer inference]
""",

"spectra": """\
flowchart LR
    A[Train LLM from scratch\\non internet-scale data] --> B[INT4 / INT8 / FP16\\nweight formats]
    B --> C[No quantization error:\\nweights never float]
    C --> D[Release family:\\nSpectra-99M to 3.9B]
    D --> E[Benchmark across\\nbit-widths and tasks]
    E --> F[Integer-trained models\\noutperform PTQ at same bits]
""",

"kvquant": """\
flowchart LR
    A[KV tensors] --> B{Token type}
    B -->|sink + outlier tokens| C[FP16 sparse]
    B -->|normal tokens ~95%| D[Per-channel\\nnon-uniform quant]
    D --> E[NF4-style bins\\nKV2/KV3/KV4]
    C --> F[Compressed KV cache]
    E --> F
    F --> G[10M-token context\\non single GPU]
""",

"kivi": """\
flowchart LR
    A[Key cache K] --> B[Per-channel\\nINT2 quantize]
    A2[Value cache V] --> C[Per-token\\nINT2 quantize]
    B --> D[Sliding window:\\nrecent tokens FP16]
    C --> D
    D --> E[2-bit KV cache\\nno fine-tuning needed]
    E --> F[2x longer context\\nsame GPU memory]
""",

"wkvquant": """\
flowchart LR
    A[Weights W] --> B[W4 past-only quant:\\nonly prev-gen KV quantized]
    A2[KV Cache] --> C[Within-group clipping\\nfor KV INT4]
    B --> D[Joint W4KV4\\ncombined objective]
    C --> D
    D --> E[Better throughput\\nthan W4A16 alone]
""",

"gear": """\
flowchart LR
    A[KV cache] --> B[Quantize to INT4]
    B --> C[Quantization\\nerror residual E]
    C --> D[SVD low-rank\\napprox of E]
    D --> E[Store: INT4 KV\\n+ low-rank E_hat]
    E --> F[Dequant + low-rank\\ncorrection at runtime]
    F --> G[Near-lossless\\nKV at 4-bit avg]
""",

"skvq": """\
flowchart LR
    A[KV cache stream] --> B[Sliding window:\\nrecent tokens full precision]
    B --> C[Older tokens:\\nchannel reordering]
    C --> D[Similar-range channels\\ngrouped together]
    D --> E[Group quantize\\nKV2 to KV4]
    E --> F[Clipping migration\\nat window boundary]
    F --> G[Efficient long-context\\nwith sliding precision]
""",

"qaq": """\
flowchart LR
    A[KV cache entry] --> B[Compute importance:\\naccumulated attn score]
    B --> C{High attention?}
    C -->|yes| D[Assign high bit-width\\n8-bit or FP16]
    C -->|no| E[Assign low bit-width\\n2-4 bit]
    D --> F[Quality-adaptive\\nmixed KV cache]
    E --> F
    F --> G[Dynamic precision\\nper generation step]
""",

"think": """\
flowchart LR
    A[Query Q and Key K\\nfor head h] --> B[Q-K channel correlation:\\nI_j = norm Q_j hadamard K_j]
    B --> C[Rank dimensions\\nby importance I_j]
    C --> D[Prune low-importance\\nK cache dimensions]
    D --> E[20-40% key cache\\nreduction]
    E --> F[Orthogonal to\\nquantization methods]
""",

"palu": """\
flowchart LR
    A[K proj weight W_K\\nd to d] --> B[SVD: W_K approx U_r Sigma V_r^T]
    B --> C[W_K_low in R^d_times_r\\nW_K_proj in R^r_times_d]
    C --> D[k_low = x W_K_low\\nstore in R^r]
    D --> E[At attention:\\ndecode k = k_low W_K_proj]
    E --> F[r over d ratio\\n= compression factor]
    F --> G[Combinable with\\nKV quantization]
""",

"zipcache": """\
flowchart LR
    A[KV cache tokens] --> B[Accumulate attention\\nscores online]
    B --> C{Salient token?}
    C -->|high attention| D[Keep in FP16 / INT8]
    C -->|low attention| E[Quantize to INT4\\nor INT2]
    D --> F[Mixed-precision\\nKV cache]
    E --> F
    F --> G[3x KV compression\\nnear-lossless for salient]
""",

"pqcache": """\
flowchart LR
    A[Key or Value vector v] --> B[Split into m sub-vectors\\nof dimension d/m each]
    B --> C[Assign each sub-vec\\nto nearest codebook centroid]
    C --> D[Store m indices\\ninstead of full vector]
    D --> E[Asymmetric distance:\\nscore without full decode]
    E --> F[Product Quant KV\\neffective 2-4 bits]
    F --> G[Long-context inference\\nlower memory footprint]
""",

"coupled-quant": """\
flowchart LR
    A[Key K and Value V\\nfrom same token] --> B[Analyze correlation\\nbetween K and V]
    B --> C[Joint codebook\\nshared K-V pairs]
    C --> D[Quantize K and V\\ncoupled, not independent]
    D --> E[Inter-vector correlation\\nreduces joint error]
    E --> F[KV2 near-lossless\\ncoupled representation]
""",

"snapkv": """\
flowchart LR
    A[Input prompt tokens] --> B[Observation window:\\nlast W tokens]
    B --> C[Accumulate attention\\nscores over window]
    C --> D{High cumulative\\nattention?}
    D -->|yes| E[Retain KV pair\\nin cache]
    D -->|no| F[Evict KV pair]
    E --> G[Compressed KV cache\\n+ full window KV]
    F --> G
    G --> H[3.6x reduction\\nat 16K context]
""",

"sageattention": """\
flowchart LR
    A[Query Q and Key K\\nFP16] --> B[Per-token smooth\\nquantization to INT8]
    B --> C[INT8 GEMM:\\nQK^T on tensor cores]
    C --> D[Dequantize result\\nbefore softmax]
    D --> E[Softmax in FP32]
    E --> F[FP16 Value V\\nweighted sum AV]
    F --> G[2x attention speedup\\nnear-zero quality loss]
""",

"fp8-training": """\
flowchart LR
    A[BF16 training] --> B[Cast forward pass\\nto E4M3 FP8]
    B --> C[FP8 GEMM\\nH100 tensor cores]
    C --> D[Cast gradients\\nto E5M2 FP8]
    D --> E[FP32 master weights\\n+ optimizer state]
    E --> F[Loss scaling\\nprevents underflow]
    F --> G[~2x throughput\\nvs BF16]
""",

"mx-formats": """\
flowchart LR
    A[Tensor block\\n32 elements] --> B[Shared scale\\nexponent E8]
    B --> C{MX format}
    C -->|MXFP8| D[E4M3 or E5M2\\nper element]
    C -->|MXFP4| E[E2M1\\nper element]
    C -->|MXINT8| F[INT8\\nper element]
    D --> G[OCP standard\\nBlackwell / MI300X]
    E --> G
    F --> G
""",

"nvfp4": """\
flowchart LR
    A[FP16 weight tensor] --> B[Tile into 16-element\\nblocks]
    B --> C[Shared E8 scale\\nper block]
    C --> D[Each element:\\nE2M1 FP4 value]
    D --> E[NVFP4 tensor\\nBlackwell GB200 native]
    E --> F[~2x memory vs FP8\\nhigher throughput density]
""",

"deepseek-fp8": """\
flowchart LR
    A[DeepSeek-V3 training\\nBF16 baseline] --> B[Fine-grained FP8:\\n1x128 weight tiles]
    B --> C[128x128 activation\\ntiles E4M3]
    C --> D[E5M2 gradient tiles]
    D --> E[FP32 accumulators\\nprevents drift]
    E --> F[FP8 GEMM on H800\\ntensor cores]
    F --> G[671B MoE trained\\nfull FP8 pipeline]
""",

"moqe": """\
flowchart LR
    A[MoE model] --> B[Profile expert\\nactivation frequency]
    B --> C{Expert usage\\nfrequency}
    C -->|high frequency| D[Keep in INT8\\nor FP16]
    C -->|low frequency| E[Quantize to INT4\\nor INT2]
    D --> F[Mixed-precision\\nMoE inference]
    E --> F
    F --> G[Better than uniform\\nquantization of all experts]
""",

"mc-moe": """\
flowchart LR
    A[MoE experts] --> B[Compute per-expert\\nquantization sensitivity]
    B --> C[Rank experts\\nby sensitivity score]
    C --> D[High sensitivity:\\nassign more bits]
    D --> E[Low sensitivity:\\nassign fewer bits]
    E --> F[Mixed-precision\\nbit allocation per expert]
    F --> G[Better accuracy\\nthan uniform MoE quant]
""",

"bitsandbytes": """\
flowchart LR
    A[Model load] --> B{dtype param}
    B -->|load_in_8bit| C[LLM.int8\\nmixed-precision]
    B -->|load_in_4bit| D[NF4 or FP4\\nquant_type]
    D --> E[QLoRA-ready\\ncompute_dtype BF16]
    C --> F[8-bit optimizer states]
    E --> G[paged_adamw_32bit]
    F --> G
""",

"autogptq": """\
flowchart LR
    A[FP16 model] --> B[Load calibration\\ndataset]
    B --> C[Run GPTQ per layer:\\nHessian + error comp]
    C --> D[Save GPTQ weights\\n+ scales to disk]
    D --> E[Load quantized model]
    E --> F{Backend}
    F -->|ExLlamaV2| G[W4A16 fast decode]
    F -->|Marlin| H[W4A16 throughput]
    F -->|CUDA| I[Standard W4A16]
""",

"autoawq": """\
flowchart LR
    A[FP16 model] --> B[Collect activation\\nmagnitude stats]
    B --> C[AWQ: per-channel\\nscale optimization]
    C --> D[Apply scales, quantize\\nweights to INT4]
    D --> E[Save AWQ weights\\n+ metadata]
    E --> F[Fast inference:\\ngemm_a16w4 or Marlin kernel]
""",

"llama-cpp": """\
flowchart LR
    A[GGUF file] --> B[Load quantized\\nweights + metadata]
    B --> C{Quant type}
    C -->|Q4_K_M| D[K-quant:\\nImportance-weighted\\ngroup quant]
    C -->|IQ4_XS| E[I-quant:\\nLattice codebook\\nactivation-aware]
    D --> F[CPU or GPU\\nmetal / CUDA / Vulkan]
    E --> F
    F --> G[Cross-platform\\nLLM inference]
""",

"exllamav2": """\
flowchart LR
    A[EXL2 quantized\\nmodel file] --> B[Mixed-precision\\nper-layer bit assignment]
    B --> C[ExLlamaV2 kernel:\\nfused W4A16 decode]
    C --> D[Paged attention\\ncache management]
    D --> E[Speculative decoding\\noptional]
    E --> F[Highest single-GPU\\ngeneration throughput]
""",

"vllm-quant": """\
flowchart LR
    A[vLLM engine] --> B{Quant method}
    B -->|awq| C[AutoAWQ W4A16]
    B -->|gptq| D[ExLlamaV2 W4A16]
    B -->|fp8| E[Native FP8\\nH100 tensor core]
    B -->|marlin| F[Marlin INT4\\nhigh throughput]
    C --> G[PagedAttention\\ncontinuous batching]
    D --> G
    E --> G
    F --> G
""",

"mlc-llm": """\
flowchart LR
    A[Model weights\\nFP16 or quantized] --> B[TVM compilation\\ntarget-specific tuning]
    B --> C{Target platform}
    C -->|CUDA| D[GPU GEMM kernel]
    C -->|Metal| E[Apple GPU kernel]
    C -->|WebGPU| F[Browser inference]
    C -->|x86| G[CPU SIMD kernel]
    D --> H[Universal LLM\\nruntime MLC-LLM]
    E --> H
    F --> H
    G --> H
""",

"sglang-quant": """\
flowchart LR
    A[vLLM engine] --> B{Quant method}
    B -->|awq| C[AutoAWQ W4A16]
    B -->|gptq| D[ExLlamaV2 W4A16]
    B -->|fp8| E[Native FP8\\nH100 tensor core]
    B -->|marlin| F[Marlin INT4\\nhigh throughput]
    C --> G[PagedAttention\\ncontinuous batching]
    D --> G
    E --> G
    F --> G
""",

"bitsandbytes-nf4": """\
flowchart LR
    A[FP16 weight values\\nof one 64-element block] --> B[Normalize to -1 to 1\\nabs max scaling]
    B --> C[Find nearest NF4 level\\nfrom 16 non-uniform bins]
    C --> D[Store 4-bit NF4 index\\nper weight]
    D --> E[At compute time:\\ndequant to BF16]
    E --> F[Optimal for normal\\ndistribution weights]
""",

"gguf-kquants": """\
flowchart LR
    A[FP16 weight block\\n256 elements] --> B[Compute importance\\nvia activation norms]
    B --> C[Scale important\\ngroups more finely]
    C --> D[Super-block scale\\n+ sub-block scales]
    D --> E[Pack to target bit\\nQ2_K to Q8_K]
    E --> F[Better accuracy than\\nuniform at same bits]
""",

"gguf-iquants": """\
flowchart LR
    A[Weight block] --> B[Hadamard preprocess:\\nincoherence rotation]
    B --> C[Near-Gaussian\\nweight distribution]
    C --> D[E8-like lattice\\ncodebook quantize]
    D --> E[Store codebook indices\\nIQ2_XXS to IQ4_XS]
    E --> F[Best quality per bit\\nin GGUF format]
""",

"fp6-llm": """\
flowchart LR
    A[FP32/FP16 weight] --> B[Convert to FP6:\\nE3M2 or E2M3 format]
    B --> C[Pack two FP6 values\\ninto 12-bit pair]
    C --> D[TC-FPx CUDA kernel:\\nbitwise unpack + GEMM]
    D --> E[Tensor-core compatible\\nhardware efficient]
    E --> F[W6A16: better than\\nW4 accuracy near W8]
""",

"quant-llm": """\
flowchart LR
    A[FP16 weight W] --> B[Random Hadamard\\nrotation R]
    B --> C[Incoherent W_tilde]
    C --> D[FP6 quantize\\nTC-FPx kernel]
    D --> E[W6A16 Quant-LLM]
    C --> F[FP4 quantize\\nexperimental]
    F --> G[W4A16 FP4 variant]
""",

}


def generic_mermaid(m: dict) -> str:
    """Generate a category-appropriate generic Mermaid flowchart from YAML fields."""
    name = m.get("name", m["id"])
    cat = m.get("category", "")
    precision = m.get("precision", "unknown")
    calib = "yes" if m.get("requires_calibration_data") else "no"
    training = "yes" if m.get("requires_training") else "no"
    outlier = m.get("handles_outliers_via", "none")[:40]

    def esc(s):
        return str(s).replace('"', "'").replace("\n", " ")

    if cat == "ptq_weight_only":
        return f"""\
flowchart LR
    A[FP16 Weights] --> B[Calibration data:\\n{esc(calib)}]
    B --> C[Compute scale\\nand zero-point]
    C --> D[Quantize weights\\nto {esc(precision)}]
    D --> E[Outlier handling:\\n{esc(outlier[:30])}]
    E --> F[Quantized model\\n{esc(precision)}]
"""
    elif cat == "ptq_weight_activation":
        return f"""\
flowchart LR
    A[FP16 Weights + Activations] --> B[Handle outliers:\\n{esc(outlier[:30])}]
    B --> C[Quantize weights\\nto low-bit]
    B --> D[Quantize activations\\nto low-bit]
    C --> E[INT GEMM\\ntensor cores]
    D --> E
    E --> F[{esc(precision)}\\nquantized inference]
"""
    elif cat == "qat":
        return f"""\
flowchart LR
    A[FP16 pretrained\\nor random init] --> B[Insert fake-quant\\nnodes]
    B --> C[Forward pass with\\nsimulated quantization]
    C --> D[Compute loss]
    D --> E[Backprop via\\nSTE for quant nodes]
    E --> F{{Converged?}}
    F -->|no| C
    F -->|yes| G[{esc(precision)}\\nquantized model]
"""
    elif cat == "extreme_lowbit":
        return f"""\
flowchart LR
    A[Training from scratch\\nor PTQ] --> B[{esc(precision)}\\ntarget format]
    B --> C[Binary or ternary\\nweight representation]
    C --> D[Scale factors\\nto compensate range]
    D --> E[Matmuls become\\nadditions or lookups]
    E --> F[Extreme compression\\nwith quality tradeoff]
"""
    elif cat == "kv_cache":
        return f"""\
flowchart LR
    A[K and V tensors\\nfrom attention] --> B[Compression strategy:\\n{esc(outlier[:30])}]
    B --> C[Quantize or prune\\nKV to {esc(precision)}]
    C --> D[Store compressed\\nKV cache]
    D --> E[Decompress during\\nattention computation]
    E --> F[Lower memory\\nlonger context]
"""
    elif cat == "low_precision_training":
        return f"""\
flowchart LR
    A[FP32 / BF16 model] --> B[Cast to\\n{esc(precision)}]
    B --> C[Low-precision GEMM\\non hardware tensor cores]
    C --> D[Cast back for\\naccumulation]
    D --> E[FP32 master weights\\noptimizer state]
    E --> F[Higher training\\nthroughput]
"""
    elif cat == "moe":
        return f"""\
flowchart LR
    A[MoE model\\nmany experts] --> B[Analyze per-expert\\nactivation frequency]
    B --> C[Assign bit-width\\nby importance]
    C --> D[High-freq experts:\\nhigher precision]
    D --> E[Low-freq experts:\\nlower precision]
    E --> F[Mixed-precision\\nMoE inference]
"""
    elif cat == "systems":
        return f"""\
flowchart LR
    A[Quantized model\\nweights on disk] --> B[Load and parse\\nquant metadata]
    B --> C[Select kernel\\nfor target hardware]
    C --> D[Fused dequant +\\nGEMM kernel]
    D --> E[Paged or continuous\\nbatching]
    E --> F[Efficient serving\\n{esc(precision)}]
"""
    else:
        return f"""\
flowchart LR
    A[FP16 model] --> B[Apply {esc(name)}\\nquantization]
    B --> C[{esc(precision)}\\nquantized model]
    C --> D[Faster inference\\nlower memory]
"""


def write_mmd(method_id: str, content: str, force: bool = False) -> bool:
    path = MERMAID_DIR / f"{method_id}.mmd"
    if path.exists() and not force:
        return False
    MERMAID_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate .mmd Mermaid files")
    parser.add_argument("--all", action="store_true", help="Regenerate all")
    parser.add_argument("--id", help="Generate for one method id")
    args = parser.parse_args()

    with open(ROOT / "methods.yml", encoding="utf-8") as f:
        methods = yaml.safe_load(f) or []

    generated = skipped = 0
    for m in methods:
        mid = m["id"]
        if args.id and mid != args.id:
            continue
        force = args.all or (args.id == mid)
        content = CUSTOM.get(mid) or generic_mermaid(m)
        if write_mmd(mid, content, force=force):
            print(f"  Generated: {mid}")
            generated += 1
        else:
            skipped += 1

    print(f"\nGenerated {generated} .mmd files, skipped {skipped} existing.")


if __name__ == "__main__":
    main()
