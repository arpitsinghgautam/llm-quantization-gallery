# Glossary

Definitions of terms that appear across the gallery. For notation (WxAyKVz, group size, etc.) see [notation.md](notation.md).

---

**Activation quantization** — Quantizing the intermediate tensors produced during the forward pass (outputs of attention projections, MLP layers, etc.), as opposed to the static weight tensors. Activations are harder to quantize because their distribution varies per-input and may contain large outliers.

**AQLM** — Additive Quantization for Language Models. Uses additive vector quantization (multiple codebooks whose codes are summed) to represent weights at very low bit-widths (below 2 bits per parameter average).

**AWQ** — Activation-aware Weight Quantization. Scales salient weight channels before quantization based on observed activation magnitudes, so that the channels that matter most are preserved more accurately.

**bitsandbytes** — A PyTorch library providing CUDA kernels for mixed-precision (INT8, NF4/FP4) inference and training. Home of LLM.int8() and the QLoRA NF4 format.

**Block floating point (BFP)** — A number format where a group of values shares one exponent (scale) but each has its own mantissa. The MX (Microscaling) family (MXFP8, MXFP6, MXFP4) is block floating point.

**Calibration** — Running a small sample of data through an already-trained model (no gradient updates) to collect statistics (e.g. activation ranges, Hessians) that guide quantization decisions.

**Codebook / centroid** — In vector quantization, the set of representative vectors that compressed weight blocks are mapped to. An index into the codebook replaces the original floating-point values.

**Dead weights** — Weights that are zero or negligible and do not affect outputs; important for sparse quantization (SpQR, SqueezeLLM).

**Dequantization** — The inverse of quantization: multiplying an integer (or low-bit float) by the stored scale (and adding zero-point) to recover an approximate floating-point value before arithmetic.

**ExLlama / ExLlamaV2** — A highly optimized inference engine (and quantization format, EXL2) for GPTQ-style 4-bit models, with custom CUDA kernels for W4A16 matrix-vector products.

**FP8** — An 8-bit floating-point format. Two variants: E4M3 (4 exponent bits, 3 mantissa) for weights/activations; E5M2 (5 exponent, 2 mantissa) for gradients. Used in NVIDIA H100 / H200 Tensor Cores.

**FP4 / NF4** — 4-bit floating-point. NF4 (Normal Float 4) uses a non-uniform grid optimized for normally-distributed weights (introduced in QLoRA). NVFP4 is NVIDIA's hardware FP4 format for Blackwell (B100/B200).

**GGUF** — The file format used by llama.cpp. Contains quantized weights plus model metadata. Successor to GGML. Supports K-quants (Q4_K, Q5_K, Q6_K, etc.) and I-quants (IQ2_XS, IQ3_S, etc.).

**GPTQ** — A post-training quantization algorithm that uses second-order (Hessian) information to compensate for quantization error, processing each layer independently. The basis for the majority of open-weight 4-bit model releases.

**Group quantization** — Splitting a weight tensor into blocks of *g* consecutive elements and computing an independent scale (and optionally zero-point) per block. Allows finer-grained accuracy than per-channel at moderate overhead.

**Hessian** — The second-derivative matrix of the model loss with respect to weights (or, in the PTQ context, the squared input activation covariance, which approximates the layer-wise loss Hessian). Used by GPTQ and OBQ to quantify each weight's importance.

**HQQ** — Half-Quadratic Quantization. A fast weight-only PTQ method that directly minimizes a robust (half-quadratic) loss between original and quantized weights without needing calibration data.

**I-quants** — Importance-aware quants in llama.cpp (IQ2_XS, IQ2_S, IQ3_S, IQ4_NL, etc.). Use learned importance scores and lattice codebooks to push below 4 bits while beating K-quants on perplexity.

**imatrix** — The "importance matrix" used in llama.cpp I-quants: pre-computed squared input-activation norms that guide which weights get more bits.

**INT4 / INT8** — Integer quantization to 4 or 8 bits. Standard hardware-accelerated integer formats. Most inference kernels operate in INT4 (weight) × FP16 (activation) or INT8 × INT8 modes.

**K-quants** — Quality-focused quants in llama.cpp (Q4_K, Q5_K, Q6_K, Q2_K, Q3_K_*). Use mixed-precision blocks (some layers at a higher bit-width) to improve perplexity over flat quantization.

**KV cache** — The cached key and value tensors from attention, reused across autoregressive generation steps. Grows with context length; quantizing it reduces memory bandwidth at long contexts.

**LLM.int8()** — A mixed-precision INT8 quantization scheme that isolates outlier channels and keeps them in FP16, while quantizing the rest to INT8. Enables 8-bit inference without perplexity degradation.

**LoRA** — Low-Rank Adaptation. Fine-tuning method that adds small rank-decomposed matrices to frozen weights. The QLoRA family combines LoRA fine-tuning with pre-quantized (NF4) base weights.

**Marlin** — A CUDA kernel library for W4A16 and W4A8 grouped-quantized matrix multiplication. Achieves near-theoretical memory bandwidth efficiency on A100/H100. Used by vLLM and other frameworks.

**MoE** — Mixture of Experts. A sparse model architecture where only a subset of "expert" sub-networks activates per token. MoE quantization must handle the large total parameter count but sparsely-activated nature.

**MXFP4 / MXFP6 / MXFP8** — Microscaling floating-point formats standardized by the Open Compute Project (OCP). Blocks of 32 elements share one 8-bit exponent scale. Supported in NVIDIA Blackwell (B100/B200) and AMD MI300.

**NF4** — Normal Float 4-bit. A 4-bit data type with quantile-spaced grid points optimized for normally-distributed weights. Introduced in QLoRA (bitsandbytes implementation). Not INT4; uses a look-up table.

**Outliers** — Weights or activations that are much larger in magnitude than the bulk. A small fraction of outlier channels can dominate quantization error and are the central challenge in W+A quantization.

**OWQ** — Outlier-aware Weight Quantization. Identifies the most sensitive weight columns (those corresponding to large activation channels) using the Hessian and keeps them at higher precision (FP16), quantizing the rest.

**Perplexity (ppl)** — The standard proxy metric for language model quality under quantization. Measured on WikiText-2 or C4. A 4-bit quantized model with ppl within 0.1–0.5 of FP16 is generally considered high quality.

**PTQ** — Post-Training Quantization. Quantization applied after a model is fully trained. No gradient updates to the original weights. Typically involves calibration data (for Hessian or range estimation) but not training.

**QAT** — Quantization-Aware Training. Training or fine-tuning with a "fake quantization" step inserted into the forward pass. The model learns to be robust to quantization noise. Requires gradient updates.

**QLoRA** — Quantized Low-Rank Adaptation. Fine-tunes a 4-bit (NF4) quantized base model using LoRA adapters, with LoRA weights remaining in BF16. The adapter is merged (or not) at inference.

**QuIP** — Quantization with Incoherence Processing. Applies random orthogonal transformations to weights and activations before quantization to make them more incoherent (closer to uniform distribution), then quantizes.

**QuIP#** — Extension of QuIP using lattice codebooks (E8 lattice) for even higher quality at 2-bit and 3-bit precision.

**Rotation-based quantization** — A family of methods (QuaRot, SpinQuant, QuIP, DuQuant) that apply learned or random orthogonal/Hadamard rotations to the weight/activation space to reduce outliers before quantization.

**Round-to-nearest (RTN)** — The simplest quantization: compute scale = (max - min) / (2^b - 1), divide weights by scale, round to nearest integer, clip. Zero calibration needed. Baseline for all other methods.

**SmoothQuant** — Migrates quantization difficulty from activations to weights by multiplying activations by a per-channel smoothing factor and dividing the corresponding weight column by the same factor.

**SpQR** — Sparse-Quantized Representation. Stores a small fraction of sensitive weights (identified by Hessian norm) in FP16 as a sparse matrix, and quantizes the rest to 3–4 bits.

**SqueezeLLM** — Combines dense-and-sparse decomposition (sensitive weights kept sparse-FP16, rest quantized) with non-uniform quantization via k-means clustering.

**Straight-Through Estimator (STE)** — A gradient approximation used in QAT: during backpropagation, the gradient of the quantization rounding step is treated as 1 (identity), allowing gradients to flow through.

**TinyChat / MLC-LLM** — Machine Learning Compilation framework for LLM deployment. Supports quantization formats including AWQ and supports compilation to CUDA, Metal, Vulkan, WASM.

**Vector quantization (VQ)** — Compressing a group of values to a single codebook index. The codebook is learned (k-means or otherwise). Used in AQLM, QuIP#, I-quants.

**vLLM** — A high-throughput LLM serving framework. Supports GPTQ, AWQ, Marlin, FP8, and other quantization formats natively.

**W4A16** — Standard notation for 4-bit weight, 16-bit (BF16/FP16) activation. The dominant open-source inference format as of 2024–2025.

**W8A8** — 8-bit weights and 8-bit activations. Used in throughput-optimized datacenter inference (TensorRT-LLM, vLLM FP8 mode).

**ZeroQuant** — Microsoft's W8A8 PTQ framework with per-token activation quantization and per-group weight quantization, integrated into the DeepSpeed inference engine.
