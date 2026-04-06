#!/usr/bin/env python3
"""
generate_diagrams.py — Creates SVG diagrams for all methods in methods.yml.

Each diagram is 800×500, transparent background, category-accent color.
Run this after adding new entries to methods.yml.

Usage:
    python scripts/generate_diagrams.py              # generate missing diagrams only
    python scripts/generate_diagrams.py --all        # regenerate all diagrams
    python scripts/generate_diagrams.py --id gptq    # regenerate one specific diagram
"""

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent

CATEGORY_COLORS = {
    "ptq_weight_only":        "#4A90D9",
    "ptq_weight_activation":  "#E87D3E",
    "qat":                    "#7B68EE",
    "extreme_lowbit":         "#E84393",
    "kv_cache":               "#3DAD78",
    "low_precision_training": "#D4A027",
    "moe":                    "#9B59B6",
    "systems":                "#607D8B",
}

# SVG template
SVG_TEMPLATE = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500">
  <!-- Title bar -->
  <rect x="0" y="0" width="800" height="60" fill="{color}" rx="4"/>
  <text x="20" y="38" font-family="monospace" font-size="22" font-weight="bold" fill="white">{name}</text>
  <text x="780" y="38" font-family="monospace" font-size="16" fill="white" text-anchor="end">{precision}</text>

  <!-- Content area -->
  <rect x="0" y="60" width="800" height="440" fill="#F8F9FA" rx="0"/>

{content}
</svg>
"""

# ============================================================
# Per-method diagram content (SVG fragment, injected into template)
# ============================================================

DIAGRAMS = {}

def d(method_id):
    """Decorator to register a diagram content function."""
    def decorator(fn):
        DIAGRAMS[method_id] = fn
        return fn
    return decorator


@d("rtn")
def rtn_diagram(color):
    return """\
  <!-- RTN: simple round-to-nearest flow -->
  <text x="400" y="110" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Round-To-Nearest (RTN) Baseline</text>

  <!-- Step boxes -->
  <rect x="60" y="140" width="160" height="50" rx="6" fill="{c}" opacity="0.15" stroke="{c}" stroke-width="1.5"/>
  <text x="140" y="160" font-family="monospace" font-size="12" fill="#222" text-anchor="middle">Weight tensor W</text>
  <text x="140" y="178" font-family="monospace" font-size="11" fill="#555" text-anchor="middle">(FP16 / BF16)</text>

  <text x="240" y="170" font-family="monospace" font-size="18" fill="{c}" text-anchor="middle">→</text>

  <rect x="270" y="140" width="170" height="50" rx="6" fill="{c}" opacity="0.15" stroke="{c}" stroke-width="1.5"/>
  <text x="355" y="160" font-family="monospace" font-size="12" fill="#222" text-anchor="middle">Compute scale</text>
  <text x="355" y="178" font-family="monospace" font-size="11" fill="#555" text-anchor="middle">s = (max−min)/(2ᵇ−1)</text>

  <text x="460" y="170" font-family="monospace" font-size="18" fill="{c}" text-anchor="middle">→</text>

  <rect x="480" y="140" width="180" height="50" rx="6" fill="{c}" opacity="0.15" stroke="{c}" stroke-width="1.5"/>
  <text x="570" y="160" font-family="monospace" font-size="12" fill="#222" text-anchor="middle">Quantize</text>
  <text x="570" y="178" font-family="monospace" font-size="11" fill="#555" text-anchor="middle">q = clip(round(W/s), qmin, qmax)</text>

  <!-- Properties -->
  <rect x="60" y="240" width="680" height="90" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="80" y="265" font-family="sans-serif" font-size="13" font-weight="bold" fill="#333">Properties</text>
  <text x="80" y="288" font-family="monospace" font-size="12" fill="#555">• No calibration data needed</text>
  <text x="80" y="308" font-family="monospace" font-size="12" fill="#555">• Per-channel or per-group scale</text>
  <text x="400" y="288" font-family="monospace" font-size="12" fill="#555">• Symmetric or asymmetric</text>
  <text x="400" y="308" font-family="monospace" font-size="12" fill="#555">• O(1) compute — instant baseline</text>

  <!-- Limitation note -->
  <rect x="60" y="360" width="680" height="60" rx="6" fill="#FFF3CD" stroke="#FBBF24" stroke-width="1"/>
  <text x="80" y="386" font-family="sans-serif" font-size="12" fill="#92400E">⚠ No error compensation: quantization error accumulates across layers.</text>
  <text x="80" y="406" font-family="sans-serif" font-size="12" fill="#92400E">   At 4-bit, ~1–3 ppl degradation on LLaMA-7B vs. FP16. All other methods beat RTN.</text>
""".replace("{c}", color)


@d("gptq")
def gptq_diagram(color):
    return """\
  <!-- GPTQ: layer-wise Hessian-based error compensation -->
  <text x="400" y="110" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Layer-wise second-order error compensation (one layer at a time)</text>

  <!-- Layer -->
  <rect x="40" y="130" width="110" height="220" rx="6" fill="{c}" opacity="0.12" stroke="{c}" stroke-width="1.5"/>
  <text x="95" y="158" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Layer input X</text>
  <text x="95" y="178" font-family="monospace" font-size="10" fill="#666" text-anchor="middle">(n×d_in)</text>
  <text x="95" y="220" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Hessian</text>
  <text x="95" y="238" font-family="monospace" font-size="10" fill="#666" text-anchor="middle">H = 2XX^T</text>
  <text x="95" y="258" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">(d_in × d_in)</text>

  <!-- Weight matrix -->
  <rect x="190" y="130" width="130" height="220" rx="6" fill="white" stroke="#ccc" stroke-width="1"/>
  <text x="255" y="158" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Weight W</text>
  <text x="255" y="178" font-family="monospace" font-size="10" fill="#666" text-anchor="middle">(d_out × d_in)</text>
  <!-- Columns -->
  <line x1="216" y1="190" x2="216" y2="340" stroke="#ccc" stroke-width="0.8"/>
  <line x1="242" y1="190" x2="242" y2="340" stroke="#ccc" stroke-width="0.8"/>
  <line x1="268" y1="190" x2="268" y2="340" stroke="#ccc" stroke-width="0.8"/>
  <line x1="294" y1="190" x2="294" y2="340" stroke="{c}" stroke-width="2"/>
  <text x="308" y="265" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">←col q</text>
  <text x="255" y="360" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">process left→right</text>

  <!-- Arrow -->
  <text x="345" y="250" font-family="monospace" font-size="22" fill="{c}" text-anchor="middle">→</text>

  <!-- Error update box -->
  <rect x="370" y="130" width="200" height="220" rx="6" fill="{c}" opacity="0.08" stroke="{c}" stroke-width="1.5"/>
  <text x="470" y="158" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Per-column update</text>
  <text x="470" y="185" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">1. Quantize column q → Wq̂</text>
  <text x="470" y="205" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">2. err = (Wq − Wq̂) / [H⁻¹]qq</text>
  <text x="470" y="225" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">3. W[:,q+1:] -= err · H⁻¹[q,q+1:]</text>
  <text x="470" y="260" font-family="monospace" font-size="10" fill="#888" text-anchor="middle">(OBS-style update)</text>
  <text x="470" y="295" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">Cholesky(H⁻¹) precomputed</text>
  <text x="470" y="313" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">for cache efficiency</text>

  <!-- Output -->
  <text x="590" y="250" font-family="monospace" font-size="22" fill="{c}" text-anchor="middle">→</text>
  <rect x="615" y="165" width="140" height="80" rx="6" fill="{c}" opacity="0.15" stroke="{c}" stroke-width="1.5"/>
  <text x="685" y="198" font-family="monospace" font-size="12" fill="#222" text-anchor="middle">Quantized</text>
  <text x="685" y="216" font-family="monospace" font-size="12" fill="#222" text-anchor="middle">Ŵ (INT4)</text>
  <text x="685" y="235" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">+scale/zp</text>

  <!-- Key numbers -->
  <rect x="40" y="375" width="720" height="55" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="60" y="397" font-family="monospace" font-size="11" fill="#555">Calibration: 128 sequences × 2048 tok  |  Group size: 128 (typical)  |  One-shot, no gradient</text>
  <text x="60" y="417" font-family="monospace" font-size="11" fill="#555">W4: &lt;0.5 ppl on LLaMA-7B  |  W3: ~1–2 ppl  |  Processes all layers in minutes on A100</text>
""".replace("{c}", color)


@d("awq")
def awq_diagram(color):
    return """\
  <!-- AWQ: activation-magnitude-guided weight scaling -->
  <text x="400" y="110" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Scale salient weight channels by activation magnitude before quantization</text>

  <!-- Step 1: identify salient channels -->
  <rect x="30" y="130" width="190" height="110" rx="6" fill="{c}" opacity="0.10" stroke="{c}" stroke-width="1.5"/>
  <text x="125" y="152" font-family="monospace" font-size="11" font-weight="bold" fill="#333" text-anchor="middle">1. Identify salient channels</text>
  <text x="125" y="172" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">‖x_j‖  per input channel j</text>
  <text x="125" y="192" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">top-1% channels →</text>
  <text x="125" y="212" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">keep at higher precision</text>

  <!-- Step 2: compute scale -->
  <rect x="250" y="130" width="190" height="110" rx="6" fill="{c}" opacity="0.10" stroke="{c}" stroke-width="1.5"/>
  <text x="345" y="152" font-family="monospace" font-size="11" font-weight="bold" fill="#333" text-anchor="middle">2. Compute scale s</text>
  <text x="345" y="172" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">s_j = (‖x_j‖ / mean‖x‖)^α</text>
  <text x="345" y="192" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">α ∈ [0,1], grid-searched</text>
  <text x="345" y="212" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">per-channel scale factor</text>

  <!-- Step 3: transform -->
  <rect x="470" y="130" width="190" height="110" rx="6" fill="{c}" opacity="0.10" stroke="{c}" stroke-width="1.5"/>
  <text x="565" y="152" font-family="monospace" font-size="11" font-weight="bold" fill="#333" text-anchor="middle">3. Scale &amp; quantize W</text>
  <text x="565" y="172" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">Ŵ = Q(W · diag(s))</text>
  <text x="565" y="192" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">absorb s⁻¹ into prev. layer</text>
  <text x="565" y="212" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">mathematically equivalent</text>

  <!-- Diagram: before/after activation distribution -->
  <rect x="30" y="270" width="350" height="120" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="292" font-family="monospace" font-size="11" fill="#333">Before: unscaled activations</text>
  <!-- spike -->
  <line x1="80" y1="370" x2="80" y2="310" stroke="#E87D3E" stroke-width="2"/>
  <line x1="120" y1="370" x2="120" y2="340" stroke="#aaa" stroke-width="1"/>
  <line x1="160" y1="370" x2="160" y2="345" stroke="#aaa" stroke-width="1"/>
  <line x1="200" y1="370" x2="200" y2="338" stroke="#aaa" stroke-width="1"/>
  <line x1="240" y1="370" x2="240" y2="350" stroke="#aaa" stroke-width="1"/>
  <line x1="280" y1="370" x2="280" y2="305" stroke="#E87D3E" stroke-width="2"/>
  <text x="80" y="298" font-family="monospace" font-size="9" fill="#E87D3E" text-anchor="middle">outlier</text>
  <text x="280" y="295" font-family="monospace" font-size="9" fill="#E87D3E" text-anchor="middle">outlier</text>

  <rect x="400" y="270" width="360" height="120" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="420" y="292" font-family="monospace" font-size="11" fill="#333">After: activations ÷ s, weights × s</text>
  <line x1="450" y1="370" x2="450" y2="335" stroke="{c}" stroke-width="1.5"/>
  <line x1="490" y1="370" x2="490" y2="330" stroke="{c}" stroke-width="1.5"/>
  <line x1="530" y1="370" x2="530" y2="328" stroke="{c}" stroke-width="1.5"/>
  <line x1="570" y1="370" x2="570" y2="332" stroke="{c}" stroke-width="1.5"/>
  <line x1="610" y1="370" x2="610" y2="325" stroke="{c}" stroke-width="1.5"/>
  <line x1="650" y1="370" x2="650" y2="330" stroke="{c}" stroke-width="1.5"/>
  <text x="700" y="345" font-family="monospace" font-size="10" fill="{c}">balanced</text>

  <rect x="30" y="415" width="730" height="45" rx="6" fill="#F0F9FF" stroke="{c}" stroke-width="0.8"/>
  <text x="50" y="436" font-family="monospace" font-size="11" fill="#555">No gradient needed. Calibration: small activation sample. Group size 128. Hardware-friendly W4A16.</text>
  <text x="50" y="452" font-family="monospace" font-size="11" fill="#555">Supported by: AutoAWQ · vLLM · TGI · TensorRT-LLM · llama.cpp</text>
""".replace("{c}", color)


@d("smoothquant")
def smoothquant_diagram(color):
    return """\
  <!-- SmoothQuant: migrate quantization difficulty from activations to weights -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Migrate quantization difficulty: activations → weights via per-channel scale</text>

  <!-- Math: Y = (X diag(s)^-1)(diag(s) W) -->
  <text x="400" y="135" font-family="monospace" font-size="14" fill="#333" text-anchor="middle">Y = X W  =  (X · diag(s)⁻¹) · (diag(s) · W)</text>
  <text x="400" y="158" font-family="monospace" font-size="12" fill="{c}" text-anchor="middle">activations divided by s  |  weights multiplied by s</text>

  <!-- Before -->
  <rect x="30" y="175" width="340" height="140" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="198" font-family="monospace" font-size="12" font-weight="bold" fill="#E87D3E">Before smoothing</text>
  <text x="50" y="218" font-family="monospace" font-size="11" fill="#555">Activations: huge dynamic range</text>
  <line x1="60" y1="290" x2="60" y2="230" stroke="#E87D3E" stroke-width="3"/>
  <line x1="100" y1="290" x2="100" y2="278" stroke="#aaa" stroke-width="1"/>
  <line x1="140" y1="290" x2="140" y2="275" stroke="#aaa" stroke-width="1"/>
  <line x1="180" y1="290" x2="180" y2="228" stroke="#E87D3E" stroke-width="3"/>
  <line x1="220" y1="290" x2="220" y2="280" stroke="#aaa" stroke-width="1"/>
  <line x1="260" y1="290" x2="260" y2="270" stroke="#aaa" stroke-width="1"/>
  <line x1="300" y1="290" x2="300" y2="225" stroke="#E87D3E" stroke-width="3"/>
  <text x="200" y="310" font-family="monospace" font-size="10" fill="#E87D3E" text-anchor="middle">→ hard to quantize to INT8</text>

  <!-- After -->
  <rect x="430" y="175" width="340" height="140" rx="6" fill="{c}" opacity="0.08" stroke="{c}" stroke-width="1.5"/>
  <text x="450" y="198" font-family="monospace" font-size="12" font-weight="bold" fill="{c}">After smoothing</text>
  <text x="450" y="218" font-family="monospace" font-size="11" fill="#555">Both tensors: similar range</text>
  <line x1="460" y1="290" x2="460" y2="258" stroke="{c}" stroke-width="1.5"/>
  <line x1="500" y1="290" x2="500" y2="255" stroke="{c}" stroke-width="1.5"/>
  <line x1="540" y1="290" x2="540" y2="260" stroke="{c}" stroke-width="1.5"/>
  <line x1="580" y1="290" x2="580" y2="253" stroke="{c}" stroke-width="1.5"/>
  <line x1="620" y1="290" x2="620" y2="258" stroke="{c}" stroke-width="1.5"/>
  <line x1="660" y1="290" x2="660" y2="255" stroke="{c}" stroke-width="1.5"/>
  <line x1="700" y1="290" x2="700" y2="260" stroke="{c}" stroke-width="1.5"/>
  <text x="600" y="310" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">→ INT8 quantizable with low error</text>

  <!-- Scale selection -->
  <rect x="30" y="335" width="740" height="80" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="358" font-family="monospace" font-size="12" font-weight="bold" fill="#333">Scale selection:  s_j = max(|X_j|)^α / max(|W_j|)^(1-α)</text>
  <text x="50" y="378" font-family="monospace" font-size="11" fill="#555">α=0.5 balances difficulty equally.  α→1 shifts all difficulty to weights.  Layer-wise search for α.</text>
  <text x="50" y="398" font-family="monospace" font-size="11" fill="{c}">Scale absorbed into preceding LayerNorm weight → no runtime overhead. Enables W8A8 INT8 GEMM.</text>
""".replace("{c}", color)


@d("llm-int8")
def llm_int8_diagram(color):
    return """\
  <!-- LLM.int8(): mixed-precision outlier decomposition -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Decompose matmul: outlier columns stay FP16, the rest goes INT8</text>

  <!-- Input with outlier columns highlighted -->
  <rect x="30" y="125" width="180" height="160" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="120" y="147" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Input X (FP16)</text>
  <!-- columns, outliers highlighted -->
  <rect x="45" y="155" width="20" height="120" rx="2" fill="#aaa" opacity="0.3"/>
  <rect x="70" y="155" width="20" height="120" rx="2" fill="#E84393" opacity="0.5"/>
  <rect x="95" y="155" width="20" height="120" rx="2" fill="#aaa" opacity="0.3"/>
  <rect x="120" y="155" width="20" height="120" rx="2" fill="#aaa" opacity="0.3"/>
  <rect x="145" y="155" width="20" height="120" rx="2" fill="#E84393" opacity="0.5"/>
  <rect x="170" y="155" width="20" height="120" rx="2" fill="#aaa" opacity="0.3"/>
  <text x="70" y="290" font-family="monospace" font-size="9" fill="#E84393" text-anchor="middle">out</text>
  <text x="145" y="290" font-family="monospace" font-size="9" fill="#E84393" text-anchor="middle">out</text>

  <!-- Arrow / decompose -->
  <text x="230" y="210" font-family="monospace" font-size="20" fill="{c}" text-anchor="middle">→</text>
  <text x="230" y="228" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">split</text>

  <!-- INT8 path -->
  <rect x="260" y="125" width="160" height="70" rx="6" fill="{c}" opacity="0.12" stroke="{c}" stroke-width="1.5"/>
  <text x="340" y="148" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">INT8 matmul</text>
  <text x="340" y="165" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">non-outlier cols × W</text>
  <text x="340" y="182" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">per-token × per-channel</text>

  <!-- FP16 path -->
  <rect x="260" y="215" width="160" height="70" rx="6" fill="#E84393" opacity="0.12" stroke="#E84393" stroke-width="1.5"/>
  <text x="340" y="238" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">FP16 matmul</text>
  <text x="340" y="255" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">outlier cols × W_out</text>
  <text x="340" y="272" font-family="monospace" font-size="10" fill="#E84393" text-anchor="middle">~0.1% of channels</text>

  <!-- Sum -->
  <text x="445" y="210" font-family="monospace" font-size="20" fill="{c}" text-anchor="middle">+</text>
  <rect x="475" y="160" width="130" height="70" rx="6" fill="{c}" opacity="0.15" stroke="{c}" stroke-width="1.5"/>
  <text x="540" y="190" font-family="monospace" font-size="12" fill="#222" text-anchor="middle">Output Y</text>
  <text x="540" y="210" font-family="monospace" font-size="11" fill="{c}" text-anchor="middle">(FP16)</text>

  <!-- Threshold note -->
  <rect x="630" y="130" width="150" height="80" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="705" y="152" font-family="monospace" font-size="10" fill="#333" text-anchor="middle">Threshold: 6.0</text>
  <text x="705" y="170" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">|x| &gt; 6 → outlier</text>
  <text x="705" y="188" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">Emerges at ~6.7B</text>
  <text x="705" y="205" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">params / layer</text>

  <!-- Key insight -->
  <rect x="30" y="310" width="740" height="70" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="332" font-family="monospace" font-size="11" font-weight="bold" fill="#333">Key insight:</text>
  <text x="50" y="350" font-family="monospace" font-size="11" fill="#555">Massive outliers in activations appear in the same few channels across all tokens &amp; layers (≥6.7B params).</text>
  <text x="50" y="368" font-family="monospace" font-size="11" fill="{c}">Isolating them in FP16 keeps nearly all compute in INT8 with &lt;1% ppl increase. No calibration needed.</text>
""".replace("{c}", color)


@d("kivi")
def kivi_diagram(color):
    return """\
  <!-- KIVI: per-channel K, per-token V quantization -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Asymmetric granularity: K per-channel (group), V per-token</text>

  <!-- Attention equation -->
  <text x="400" y="130" font-family="monospace" font-size="13" fill="#333" text-anchor="middle">Attention(Q, K, V)  →  Q · Q(K)ᵀ / √d  →  softmax  →  Q(V)</text>

  <!-- K quantization box -->
  <rect x="30" y="155" width="340" height="155" rx="6" fill="{c}" opacity="0.09" stroke="{c}" stroke-width="1.5"/>
  <text x="200" y="178" font-family="monospace" font-size="12" font-weight="bold" fill="#333" text-anchor="middle">Key (K) — per-channel quantization</text>
  <!-- K tensor grid -->
  <text x="55" y="200" font-family="monospace" font-size="10" fill="#555">channel →</text>
  <rect x="55" y="207" width="280" height="20" rx="2" fill="{c}" opacity="0.25"/>
  <text x="195" y="221" font-family="monospace" font-size="9" fill="#fff" text-anchor="middle">token 1</text>
  <rect x="55" y="229" width="280" height="20" rx="2" fill="{c}" opacity="0.18"/>
  <text x="195" y="243" font-family="monospace" font-size="9" fill="{c}" text-anchor="middle">token 2</text>
  <rect x="55" y="251" width="280" height="20" rx="2" fill="{c}" opacity="0.25"/>
  <!-- per-channel labels -->
  <text x="200" y="288" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">scale per group of channels (g=64/128)</text>
  <text x="200" y="303" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">channels are highly structured → low variance</text>

  <!-- V quantization box -->
  <rect x="430" y="155" width="340" height="155" rx="6" fill="#3DAD78" opacity="0.09" stroke="#3DAD78" stroke-width="1.5"/>
  <text x="600" y="178" font-family="monospace" font-size="12" font-weight="bold" fill="#333" text-anchor="middle">Value (V) — per-token quantization</text>
  <!-- V tensor grid — tall columns per token -->
  <rect x="450" y="207" width="30" height="80" rx="2" fill="#3DAD78" opacity="0.30"/>
  <rect x="490" y="207" width="30" height="80" rx="2" fill="#3DAD78" opacity="0.20"/>
  <rect x="530" y="207" width="30" height="80" rx="2" fill="#3DAD78" opacity="0.30"/>
  <rect x="570" y="207" width="30" height="80" rx="2" fill="#3DAD78" opacity="0.20"/>
  <rect x="610" y="207" width="30" height="80" rx="2" fill="#3DAD78" opacity="0.30"/>
  <text x="450" y="300" font-family="monospace" font-size="9" fill="#3DAD78">t1</text>
  <text x="490" y="300" font-family="monospace" font-size="9" fill="#3DAD78">t2</text>
  <text x="530" y="300" font-family="monospace" font-size="9" fill="#3DAD78">t3</text>
  <text x="600" y="288" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">scale per token (1 scale / token)</text>
  <text x="600" y="303" font-family="monospace" font-size="10" fill="#3DAD78" text-anchor="middle">tokens vary in norm → per-token</text>

  <!-- Residual / recent tokens -->
  <rect x="30" y="330" width="740" height="65" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="352" font-family="monospace" font-size="11" font-weight="bold" fill="#333">Residual cache:</text>
  <text x="50" y="370" font-family="monospace" font-size="11" fill="#555">Most recent r tokens kept at FP16 (r=128 typical) to avoid quantizing the sink-token and recent context.</text>
  <text x="50" y="388" font-family="monospace" font-size="11" fill="{c}">2-bit KV, group-size 16: 75% KV memory reduction. &lt;0.3 ppl on LLaMA-2-7B vs. FP16 at 2K context.</text>
""".replace("{c}", color)


@d("bitnet-b158")
def bitnet_b158_diagram(color):
    return """\
  <!-- BitNet b1.58: ternary {-1, 0, +1} weights -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Every weight is ternary: {-1, 0, +1} — trained from scratch, not post-hoc</text>

  <!-- Weight distribution -->
  <rect x="30" y="120" width="220" height="150" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="140" y="143" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">FP16 (standard model)</text>
  <!-- Gaussian bars -->
  <rect x="55" y="240" width="18" height="5" rx="1" fill="#aaa"/>
  <rect x="75" y="230" width="18" height="15" rx="1" fill="#aaa"/>
  <rect x="95" y="210" width="18" height="35" rx="1" fill="#aaa"/>
  <rect x="115" y="185" width="18" height="60" rx="1" fill="#aaa"/>
  <rect x="135" y="175" width="18" height="70" rx="1" fill="#aaa"/>
  <rect x="155" y="185" width="18" height="60" rx="1" fill="#aaa"/>
  <rect x="175" y="210" width="18" height="35" rx="1" fill="#aaa"/>
  <rect x="195" y="230" width="18" height="15" rx="1" fill="#aaa"/>
  <rect x="215" y="240" width="18" height="5" rx="1" fill="#aaa"/>
  <text x="140" y="262" font-family="monospace" font-size="9" fill="#555" text-anchor="middle">continuous Gaussian weights</text>

  <!-- Arrow -->
  <text x="275" y="200" font-family="monospace" font-size="20" fill="{c}" text-anchor="middle">→</text>
  <text x="275" y="218" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">absmean</text>
  <text x="275" y="233" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">quant</text>

  <!-- Ternary distribution -->
  <rect x="310" y="120" width="220" height="150" rx="6" fill="{c}" opacity="0.10" stroke="{c}" stroke-width="1.5"/>
  <text x="420" y="143" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">BitNet b1.58 weights</text>
  <!-- Three spikes -->
  <rect x="335" y="175" width="30" height="70" rx="2" fill="{c}" opacity="0.7"/>
  <rect x="405" y="150" width="30" height="95" rx="2" fill="{c}" opacity="0.9"/>
  <rect x="475" y="175" width="30" height="70" rx="2" fill="{c}" opacity="0.7"/>
  <text x="350" y="260" font-family="monospace" font-size="12" fill="{c}" text-anchor="middle">-1</text>
  <text x="420" y="260" font-family="monospace" font-size="12" fill="{c}" text-anchor="middle">0</text>
  <text x="490" y="260" font-family="monospace" font-size="12" fill="{c}" text-anchor="middle">+1</text>
  <text x="420" y="278" font-family="monospace" font-size="9" fill="#555" text-anchor="middle">1.58 bits per weight (log₂3)</text>

  <!-- Quantization formula -->
  <rect x="560" y="120" width="210" height="150" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="665" y="143" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">AbsMean quantizer</text>
  <text x="665" y="165" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">γ = mean(|W|)</text>
  <text x="665" y="185" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">W̃ = clamp(round(W/γ), -1, 1)</text>
  <text x="665" y="215" font-family="monospace" font-size="11" fill="{c}" text-anchor="middle">Inference:</text>
  <text x="665" y="233" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">XW = X·(-1) + X·(+1)</text>
  <text x="665" y="251" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">= addition only, no multiply</text>

  <!-- Properties bar -->
  <rect x="30" y="295" width="740" height="80" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="317" font-family="monospace" font-size="11" fill="#555">• 1.58 bits/weight (log₂3)   • Activations: INT8 (8-bit)   • Matmul becomes add + select</text>
  <text x="50" y="337" font-family="monospace" font-size="11" fill="#555">• Requires training from scratch (not PTQ)   • Matches full-precision LLaMA-3B quality at 3B params</text>
  <text x="50" y="357" font-family="monospace" font-size="11" fill="{c}">• Hardware: custom kernels needed; no standard INT8/INT4 kernel applies directly</text>
""".replace("{c}", color)


@d("quarot")
def quarot_diagram(color):
    return """\
  <!-- QuaRot: random Hadamard rotations to suppress outliers for W4A4 -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Hadamard rotation makes activations outlier-free → enables W4A4 with RTN</text>

  <!-- Original activations -->
  <rect x="25" y="120" width="180" height="120" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="115" y="143" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Original X</text>
  <line x1="45" y1="220" x2="45" y2="160" stroke="#E87D3E" stroke-width="4"/>
  <line x1="70" y1="220" x2="70" y2="200" stroke="#aaa" stroke-width="1.5"/>
  <line x1="95" y1="220" x2="95" y2="205" stroke="#aaa" stroke-width="1.5"/>
  <line x1="120" y1="220" x2="120" y2="155" stroke="#E87D3E" stroke-width="4"/>
  <line x1="145" y1="220" x2="145" y2="203" stroke="#aaa" stroke-width="1.5"/>
  <line x1="170" y1="220" x2="170" y2="208" stroke="#aaa" stroke-width="1.5"/>
  <text x="115" y="235" font-family="monospace" font-size="9" fill="#E87D3E" text-anchor="middle">massive outliers</text>

  <!-- Rotation -->
  <text x="228" y="186" font-family="monospace" font-size="14" fill="{c}" text-anchor="middle">H</text>
  <text x="228" y="204" font-family="monospace" font-size="22" fill="{c}" text-anchor="middle">→</text>

  <!-- Rotated activations -->
  <rect x="260" y="120" width="180" height="120" rx="6" fill="{c}" opacity="0.10" stroke="{c}" stroke-width="1.5"/>
  <text x="350" y="143" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Rotated HX</text>
  <line x1="280" y1="220" x2="280" y2="193" stroke="{c}" stroke-width="1.5"/>
  <line x1="305" y1="220" x2="305" y2="188" stroke="{c}" stroke-width="1.5"/>
  <line x1="330" y1="220" x2="330" y2="195" stroke="{c}" stroke-width="1.5"/>
  <line x1="355" y1="220" x2="355" y2="190" stroke="{c}" stroke-width="1.5"/>
  <line x1="380" y1="220" x2="380" y2="193" stroke="{c}" stroke-width="1.5"/>
  <line x1="405" y1="220" x2="405" y2="188" stroke="{c}" stroke-width="1.5"/>
  <text x="350" y="235" font-family="monospace" font-size="9" fill="{c}" text-anchor="middle">outliers spread → near-uniform</text>

  <!-- Weight rotation -->
  <text x="465" y="186" font-family="monospace" font-size="14" fill="{c}" text-anchor="middle">Hᵀ</text>
  <text x="465" y="204" font-family="monospace" font-size="22" fill="{c}" text-anchor="middle">→</text>
  <rect x="498" y="120" width="180" height="120" rx="6" fill="{c}" opacity="0.10" stroke="{c}" stroke-width="1.5"/>
  <text x="588" y="143" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">WH (rotated W)</text>
  <text x="588" y="175" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">absorbed offline</text>
  <text x="588" y="195" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">→ quantize to INT4</text>
  <text x="588" y="215" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">via RTN, no calibration</text>

  <!-- Key: mathematically exact -->
  <text x="700" y="186" font-family="monospace" font-size="14" fill="#333" text-anchor="middle">=</text>
  <rect x="716" y="148" width="60" height="64" rx="6" fill="{c}" opacity="0.2" stroke="{c}" stroke-width="1.5"/>
  <text x="746" y="175" font-family="monospace" font-size="10" fill="#333" text-anchor="middle">same</text>
  <text x="746" y="193" font-family="monospace" font-size="10" fill="#333" text-anchor="middle">output</text>

  <!-- Rotation properties -->
  <rect x="25" y="265" width="750" height="100" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="45" y="287" font-family="monospace" font-size="11" font-weight="bold" fill="#333">Why Hadamard?</text>
  <text x="45" y="305" font-family="monospace" font-size="11" fill="#555">H ∈ ℝ^{n×n}, Hᵀ H = nI  →  orthogonal (no output change).  Each output is ±avg of all inputs.</text>
  <text x="45" y="323" font-family="monospace" font-size="11" fill="#555">Outliers (one large element) get spread equally across all output dims → no single dimension dominates.</text>
  <text x="45" y="345" font-family="monospace" font-size="11" fill="{c}">Result: W4A4 RTN quality matches W4A16 GPTQ on LLaMA-2-70B. Applied at attention, FFN, and LN fusions.</text>
""".replace("{c}", color)


@d("aqlm")
def aqlm_diagram(color):
    return """\
  <!-- AQLM: additive multi-codebook quantization -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Additive quantization: 8 weights = sum of M codebook lookups</text>

  <!-- Weight block -->
  <rect x="30" y="120" width="120" height="100" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="90" y="145" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">w ∈ ℝ⁸</text>
  <text x="90" y="163" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">FP16 weight block</text>
  <text x="90" y="183" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">(8 values)</text>
  <text x="90" y="210" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">16 bytes → 2 bytes</text>

  <!-- Codebook 1 -->
  <rect x="200" y="120" width="160" height="100" rx="6" fill="{c}" opacity="0.12" stroke="{c}" stroke-width="1.5"/>
  <text x="280" y="145" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Codebook C₁</text>
  <text x="280" y="163" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">256 entries × 8 dims</text>
  <text x="280" y="183" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">find nearest: i₁</text>
  <text x="280" y="203" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">store 8 bits</text>

  <!-- Codebook 2 -->
  <rect x="200" y="235" width="160" height="100" rx="6" fill="{c}" opacity="0.12" stroke="{c}" stroke-width="1.5"/>
  <text x="280" y="260" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Codebook C₂</text>
  <text x="280" y="278" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">256 entries × 8 dims</text>
  <text x="280" y="298" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">find nearest: i₂</text>
  <text x="280" y="318" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">store 8 bits</text>

  <!-- Plus sign -->
  <text x="390" y="185" font-family="monospace" font-size="28" fill="{c}" text-anchor="middle">+</text>

  <!-- Result -->
  <rect x="420" y="120" width="170" height="215" rx="6" fill="{c}" opacity="0.08" stroke="{c}" stroke-width="1.5"/>
  <text x="505" y="145" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Representation</text>
  <text x="505" y="165" font-family="monospace" font-size="12" fill="{c}" text-anchor="middle">ŵ = C₁[i₁] + C₂[i₂]</text>
  <text x="505" y="190" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">i₁, i₂ ∈ {0..255}</text>
  <text x="505" y="210" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">Store: 2 bytes/8 weights</text>
  <text x="505" y="230" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">= 2 bits / weight</text>
  <text x="505" y="260" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">M=2, K=256 codebooks</text>
  <text x="505" y="278" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">trained by beam search</text>
  <text x="505" y="298" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">+ GPTQ-style correction</text>

  <!-- Storage comparison -->
  <rect x="620" y="120" width="155" height="215" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="697" y="145" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">vs. FP16</text>
  <text x="697" y="170" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">FP16: 16 bytes</text>
  <text x="697" y="188" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">per 8 weights</text>
  <text x="697" y="215" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">AQLM: 2 bytes</text>
  <text x="697" y="233" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">8× smaller</text>
  <text x="697" y="260" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">+ shared codebooks</text>
  <text x="697" y="278" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">amortized over</text>
  <text x="697" y="296" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">all blocks</text>

  <!-- Bottom bar -->
  <rect x="30" y="360" width="740" height="80" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="382" font-family="monospace" font-size="11" font-weight="bold" fill="#333">Learning: alternating optimization</text>
  <text x="50" y="400" font-family="monospace" font-size="11" fill="#555">1. Fix codes (i₁, i₂): update codebooks by least squares  →  min ||W - CI||_F</text>
  <text x="50" y="418" font-family="monospace" font-size="11" fill="#555">2. Fix codebooks: update codes by beam search  →  min ||W - C[i]||_Hessian</text>
  <text x="50" y="436" font-family="monospace" font-size="11" fill="{c}">Result: 2-bit LLaMA-2-7B approaches 4-bit GPTQ quality. Supports M=1..4 codebooks.</text>
""".replace("{c}", color)


@d("spqr")
def spqr_diagram(color):
    return """\
  <!-- SpQR: sparse-quantized representation -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Hybrid: ~1% sensitive weights at FP16 sparse; the rest at INT3/4 dense</text>

  <!-- Weight matrix visualization -->
  <rect x="30" y="120" width="350" height="230" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="205" y="143" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Weight matrix W (one layer)</text>
  <!-- Dense quantized part -->
  <rect x="50" y="155" width="310" height="170" rx="3" fill="{c}" opacity="0.10"/>
  <text x="205" y="225" font-family="monospace" font-size="12" fill="{c}" text-anchor="middle">W_int (INT3/4)</text>
  <text x="205" y="243" font-family="monospace" font-size="11" fill="#555" text-anchor="middle">~99% of weights</text>
  <text x="205" y="261" font-family="monospace" font-size="11" fill="#555" text-anchor="middle">per-group quantized</text>
  <!-- Sparse overlay dots -->
  <circle cx="100" cy="175" r="5" fill="#E84393" opacity="0.9"/>
  <circle cx="250" cy="188" r="5" fill="#E84393" opacity="0.9"/>
  <circle cx="80" cy="280" r="5" fill="#E84393" opacity="0.9"/>
  <circle cx="320" cy="255" r="5" fill="#E84393" opacity="0.9"/>
  <circle cx="175" cy="303" r="5" fill="#E84393" opacity="0.9"/>
  <text x="205" y="342" font-family="monospace" font-size="10" fill="#E84393" text-anchor="middle">pink dots = sensitive weights stored as sparse FP16</text>

  <!-- Arrow -->
  <text x="410" y="240" font-family="monospace" font-size="20" fill="{c}" text-anchor="middle">→</text>

  <!-- Decomposition -->
  <rect x="440" y="120" width="335" height="230" rx="6" fill="{c}" opacity="0.06" stroke="{c}" stroke-width="1.5"/>
  <text x="607" y="143" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Storage layout</text>

  <rect x="455" y="155" width="305" height="80" rx="4" fill="{c}" opacity="0.15" stroke="{c}" stroke-width="1"/>
  <text x="607" y="183" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Dense INT3/INT4 block</text>
  <text x="607" y="201" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">+ per-group scale (FP16) + zero-pt</text>
  <text x="607" y="219" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">~3.0 bits/weight (avg)</text>

  <rect x="455" y="248" width="305" height="80" rx="4" fill="#E84393" opacity="0.12" stroke="#E84393" stroke-width="1"/>
  <text x="607" y="275" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">Sparse FP16 overlay</text>
  <text x="607" y="293" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">(row_idx, col_idx, fp16_value)</text>
  <text x="607" y="311" font-family="monospace" font-size="10" fill="#E84393" text-anchor="middle">~1% of weights, ~0.5 bits extra avg</text>

  <!-- Bottom bar -->
  <rect x="30" y="375" width="740" height="85" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="397" font-family="monospace" font-size="11" font-weight="bold" fill="#333">Sensitivity scoring:</text>
  <text x="50" y="415" font-family="monospace" font-size="11" fill="#555">S(w_ij) = w_ij² × [H]_ii  where H is the layer input Hessian (same as GPTQ).</text>
  <text x="50" y="433" font-family="monospace" font-size="11" fill="#555">Top-k% by sensitivity → FP16 sparse; remainder → GPTQ INT3/4 with error compensation.</text>
  <text x="50" y="451" font-family="monospace" font-size="11" fill="{c}">Near-lossless 3-bit: &lt;1% relative ppl increase on LLaMA-1-65B. Requires sparse matmul kernel.</text>
""".replace("{c}", color)


@d("hqq")
def hqq_diagram(color):
    return """\
  <!-- HQQ: half-quadratic quantization -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Find optimal scale s and zero-point z by minimizing a robust (Huber-like) loss — no data needed</text>

  <!-- Loss comparison: MSE vs HQQ -->
  <rect x="30" y="120" width="350" height="260" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="205" y="145" font-family="monospace" font-size="12" font-weight="bold" fill="#E87D3E">Standard (MSE loss)</text>
  <text x="205" y="163" font-family="monospace" font-size="11" fill="#555" text-anchor="middle">min_{s,z} ||W - Q(W;s,z)||²</text>
  <!-- MSE loss curve - parabolic, non-robust -->
  <polyline points="60,340 100,290 140,240 180,210 220,215 260,240 300,290 340,340"
    fill="none" stroke="#E87D3E" stroke-width="2"/>
  <text x="205" y="360" font-family="monospace" font-size="10" fill="#E87D3E" text-anchor="middle">sensitive to outlier weights (tails)</text>

  <rect x="420" y="120" width="350" height="260" rx="6" fill="{c}" opacity="0.08" stroke="{c}" stroke-width="1.5"/>
  <text x="595" y="145" font-family="monospace" font-size="12" font-weight="bold" fill="{c}">HQQ (Half-Quadratic)</text>
  <text x="595" y="163" font-family="monospace" font-size="11" fill="#555" text-anchor="middle">min_{s,z} Σ ρ(w_i - Q(w_i;s,z))</text>
  <!-- Huber-like curve - quadratic near 0, linear at tails -->
  <polyline points="440,340 480,300 520,260 560,228 600,220 640,228 680,260 720,300 760,340"
    fill="none" stroke="{c}" stroke-width="2"/>
  <polyline points="440,330 480,295 520,263"
    fill="none" stroke="{c}" stroke-width="1" stroke-dasharray="4,3" opacity="0.5"/>
  <polyline points="680,263 720,295 760,330"
    fill="none" stroke="{c}" stroke-width="1" stroke-dasharray="4,3" opacity="0.5"/>
  <text x="595" y="360" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">robust: outlier weights get less influence</text>

  <!-- Bottom bar -->
  <rect x="30" y="405" width="740" height="65" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="427" font-family="monospace" font-size="11" font-weight="bold" fill="#333">Optimization:</text>
  <text x="50" y="445" font-family="monospace" font-size="11" fill="#555">Alternating half-quadratic: fix auxiliary u_i, solve for (s, z) in closed form; update u_i from residuals.</text>
  <text x="50" y="463" font-family="monospace" font-size="11" fill="{c}">No calibration data. W4 quality competitive with GPTQ. W2 better than RTN. Runs in seconds per layer.</text>
""".replace("{c}", color)


@d("qlora")
def qlora_diagram(color):
    return """\
  <!-- QLoRA: quantized base + LoRA adapters -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Frozen 4-bit NF4 base model + trainable BF16 LoRA adapters = fine-tune 65B on 1 GPU</text>

  <!-- Forward pass diagram -->
  <!-- Input -->
  <rect x="25" y="130" width="80" height="50" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="65" y="160" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">x (BF16)</text>

  <!-- Main weight -->
  <rect x="150" y="115" width="170" height="80" rx="6" fill="{c}" opacity="0.12" stroke="{c}" stroke-width="2"/>
  <text x="235" y="142" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">W (NF4, frozen)</text>
  <text x="235" y="162" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">dequant → BF16 × x</text>
  <text x="235" y="180" font-family="monospace" font-size="9" fill="#888" text-anchor="middle">no gradients flow here</text>

  <!-- LoRA adapters -->
  <rect x="150" y="220" width="80" height="60" rx="6" fill="#7B68EE" opacity="0.2" stroke="#7B68EE" stroke-width="1.5"/>
  <text x="190" y="245" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">A (BF16)</text>
  <text x="190" y="263" font-family="monospace" font-size="10" fill="#7B68EE" text-anchor="middle">rank r</text>

  <rect x="250" y="220" width="70" height="60" rx="6" fill="#7B68EE" opacity="0.2" stroke="#7B68EE" stroke-width="1.5"/>
  <text x="285" y="245" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">B (BF16)</text>
  <text x="285" y="263" font-family="monospace" font-size="10" fill="#7B68EE" text-anchor="middle">rank r</text>

  <!-- Scale -->
  <text x="340" y="160" font-family="monospace" font-size="18" fill="{c}" text-anchor="middle">+</text>

  <!-- Output sum -->
  <rect x="370" y="130" width="130" height="80" rx="6" fill="{c}" opacity="0.10" stroke="{c}" stroke-width="1.5"/>
  <text x="435" y="155" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">h = Wx + BAx</text>
  <text x="435" y="173" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">W frozen (NF4)</text>
  <text x="435" y="191" font-family="monospace" font-size="10" fill="#7B68EE" text-anchor="middle">BA trained (BF16)</text>

  <!-- Innovations panel -->
  <rect x="530" y="115" width="245" height="225" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="550" y="140" font-family="monospace" font-size="11" font-weight="bold" fill="#333">QLoRA innovations:</text>
  <text x="550" y="162" font-family="monospace" font-size="11" fill="{c}">NF4 data type:</text>
  <text x="550" y="179" font-family="monospace" font-size="10" fill="#555">quantile-spaced 4-bit normal float</text>
  <text x="550" y="197" font-family="monospace" font-size="10" fill="#555">optimal for Gaussian weight distrib.</text>
  <text x="550" y="220" font-family="monospace" font-size="11" fill="{c}">Double quantization:</text>
  <text x="550" y="237" font-family="monospace" font-size="10" fill="#555">quantize the scales themselves to FP8</text>
  <text x="550" y="255" font-family="monospace" font-size="10" fill="#555">saves 0.125 bits/weight extra</text>
  <text x="550" y="278" font-family="monospace" font-size="11" fill="{c}">Paged optimizers:</text>
  <text x="550" y="295" font-family="monospace" font-size="10" fill="#555">offload optim. states to CPU RAM</text>
  <text x="550" y="313" font-family="monospace" font-size="10" fill="#555">on OOM spikes during checkpointing</text>

  <!-- Bottom -->
  <rect x="25" y="365" width="750" height="95" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="45" y="387" font-family="monospace" font-size="11" font-weight="bold" fill="#333">Key: NF4 dequantize before multiply (not INT4 Tensor Core):</text>
  <text x="45" y="405" font-family="monospace" font-size="11" fill="#555">  W_NF4  →  [dequant to BF16]  →  W_BF16 × x  +  B × A × x</text>
  <text x="45" y="423" font-family="monospace" font-size="11" fill="#555">Inference uses same NF4 base. LoRA adapters optionally merged post-fine-tuning (re-quantize required).</text>
  <text x="45" y="441" font-family="monospace" font-size="11" fill="{c}">Fine-tunes Guanaco-65B (4-bit) to near-ChatGPT quality on 1x A100 80GB using 24h training.</text>
""".replace("{c}", color)


@d("fp8-training")
def fp8_training_diagram(color):
    return """\
  <!-- FP8 training: format comparison -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">FP8 training: E4M3 for forward pass, E5M2 for gradients, delayed per-tensor scaling</text>

  <!-- Format comparison table -->
  <rect x="25" y="115" width="750" height="160" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="45" y="140" font-family="monospace" font-size="12" font-weight="bold" fill="#333">Format comparison (8-bit floating point)</text>

  <!-- Headers -->
  <text x="45" y="165" font-family="monospace" font-size="11" fill="#555">Format</text>
  <text x="185" y="165" font-family="monospace" font-size="11" fill="#555">Sign</text>
  <text x="235" y="165" font-family="monospace" font-size="11" fill="#555">Exponent</text>
  <text x="330" y="165" font-family="monospace" font-size="11" fill="#555">Mantissa</text>
  <text x="430" y="165" font-family="monospace" font-size="11" fill="#555">Max value</text>
  <text x="530" y="165" font-family="monospace" font-size="11" fill="#555">Use case</text>

  <!-- E4M3 -->
  <text x="45" y="188" font-family="monospace" font-size="11" fill="{c}">FP8 E4M3</text>
  <text x="185" y="188" font-family="monospace" font-size="11" fill="#555">1</text>
  <text x="235" y="188" font-family="monospace" font-size="11" fill="#555">4 bits</text>
  <text x="330" y="188" font-family="monospace" font-size="11" fill="#555">3 bits</text>
  <text x="430" y="188" font-family="monospace" font-size="11" fill="#555">448</text>
  <text x="530" y="188" font-family="monospace" font-size="11" fill="{c}">Weights, activations</text>

  <!-- E5M2 -->
  <text x="45" y="211" font-family="monospace" font-size="11" fill="{c}">FP8 E5M2</text>
  <text x="185" y="211" font-family="monospace" font-size="11" fill="#555">1</text>
  <text x="235" y="211" font-family="monospace" font-size="11" fill="#555">5 bits</text>
  <text x="330" y="211" font-family="monospace" font-size="11" fill="#555">2 bits</text>
  <text x="430" y="211" font-family="monospace" font-size="11" fill="#555">57344</text>
  <text x="530" y="211" font-family="monospace" font-size="11" fill="{c}">Gradients (wide range)</text>

  <!-- BF16 -->
  <text x="45" y="234" font-family="monospace" font-size="11" fill="#aaa">BF16</text>
  <text x="185" y="234" font-family="monospace" font-size="11" fill="#aaa">1</text>
  <text x="235" y="234" font-family="monospace" font-size="11" fill="#aaa">8 bits</text>
  <text x="330" y="234" font-family="monospace" font-size="11" fill="#aaa">7 bits</text>
  <text x="430" y="234" font-family="monospace" font-size="11" fill="#aaa">~3.4×10³⁸</text>
  <text x="530" y="234" font-family="monospace" font-size="11" fill="#aaa">Weight update, master</text>

  <text x="45" y="258" font-family="monospace" font-size="11" fill="#aaa">FP32</text>
  <text x="185" y="258" font-family="monospace" font-size="11" fill="#aaa">1</text>
  <text x="235" y="258" font-family="monospace" font-size="11" fill="#aaa">8 bits</text>
  <text x="330" y="258" font-family="monospace" font-size="11" fill="#aaa">23 bits</text>
  <text x="430" y="258" font-family="monospace" font-size="11" fill="#aaa">~3.4×10³⁸</text>
  <text x="530" y="258" font-family="monospace" font-size="11" fill="#aaa">Accumulation, loss</text>

  <!-- Training pipeline -->
  <rect x="25" y="295" width="750" height="100" rx="6" fill="{c}" opacity="0.07" stroke="{c}" stroke-width="1.5"/>
  <text x="45" y="318" font-family="monospace" font-size="11" font-weight="bold" fill="#333">FP8 training pipeline (forward):</text>
  <text x="45" y="338" font-family="monospace" font-size="11" fill="#555">  BF16 weight  →  [cast E4M3 + scale]  →  FP8 matmul  →  [accumulate FP32]  →  BF16 output</text>
  <text x="45" y="358" font-family="monospace" font-size="11" fill="#555">  scale_t = max(|tensor_{t-1}|) / 448  (delayed scaling — reuse prev. step, avoid sync barrier)</text>
  <text x="45" y="378" font-family="monospace" font-size="11" fill="{c}">H100 FP8 Tensor Core: 2x throughput vs BF16 at same accuracy on GPT-3 scale training.</text>

  <!-- Bottom: backward -->
  <rect x="25" y="415" width="750" height="55" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="45" y="437" font-family="monospace" font-size="11" fill="#555">Backward: gradient cast to E5M2 (wider range for small grad values), accumulate in FP32, weight update in BF16.</text>
  <text x="45" y="455" font-family="monospace" font-size="11" fill="{c}">Key: weight master copy stays BF16/FP32; FP8 is only the compute format, not the storage format for gradients.</text>
""".replace("{c}", color)


@d("mx-formats")
def mx_formats_diagram(color):
    return """\
  <!-- MX Formats: block floating point -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Microscaling: 32 elements share one 8-bit exponent; each element stores its own mantissa</text>

  <!-- Block layout -->
  <rect x="25" y="115" width="750" height="130" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="45" y="140" font-family="monospace" font-size="11" font-weight="bold" fill="#333">MX block structure (32 elements)</text>

  <!-- Shared exponent -->
  <rect x="45" y="153" width="80" height="75" rx="4" fill="{c}" opacity="0.25" stroke="{c}" stroke-width="2"/>
  <text x="85" y="178" font-family="monospace" font-size="11" fill="#333" text-anchor="middle">E8M0</text>
  <text x="85" y="196" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">shared</text>
  <text x="85" y="212" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">8-bit exp</text>

  <!-- Element mantissas -->
  <text x="145" y="175" font-family="monospace" font-size="18" fill="#aaa" text-anchor="middle">×</text>

  <!-- 8 sample element boxes -->
  <rect x="165" y="153" width="30" height="75" rx="2" fill="{c}" opacity="0.12" stroke="{c}" stroke-width="0.8"/>
  <text x="180" y="190" font-family="monospace" font-size="9" fill="#333" text-anchor="middle">e₁</text>
  <rect x="200" y="153" width="30" height="75" rx="2" fill="{c}" opacity="0.12" stroke="{c}" stroke-width="0.8"/>
  <text x="215" y="190" font-family="monospace" font-size="9" fill="#333" text-anchor="middle">e₂</text>
  <rect x="235" y="153" width="30" height="75" rx="2" fill="{c}" opacity="0.12" stroke="{c}" stroke-width="0.8"/>
  <text x="250" y="190" font-family="monospace" font-size="9" fill="#333" text-anchor="middle">e₃</text>
  <rect x="270" y="153" width="30" height="75" rx="2" fill="{c}" opacity="0.12" stroke="{c}" stroke-width="0.8"/>
  <text x="285" y="190" font-family="monospace" font-size="9" fill="#333" text-anchor="middle">e₄</text>
  <text x="325" y="192" font-family="monospace" font-size="14" fill="#aaa" text-anchor="middle">···</text>
  <rect x="348" y="153" width="30" height="75" rx="2" fill="{c}" opacity="0.12" stroke="{c}" stroke-width="0.8"/>
  <text x="363" y="190" font-family="monospace" font-size="9" fill="#333" text-anchor="middle">e₃₂</text>

  <!-- Format table -->
  <rect x="420" y="153" width="340" height="75" rx="4" fill="white" stroke="#eee" stroke-width="1"/>
  <text x="435" y="172" font-family="monospace" font-size="10" fill="#555">MXFP8:  8-bit exp + 3-bit mantissa/element</text>
  <text x="435" y="189" font-family="monospace" font-size="10" fill="#555">MXFP6:  8-bit exp + 2-bit mantissa/element</text>
  <text x="435" y="206" font-family="monospace" font-size="10" fill="{c}">MXFP4:  8-bit exp + 0-bit mantissa (sign only)</text>
  <text x="435" y="223" font-family="monospace" font-size="10" fill="#555">MXINT8: 8-bit exp + 7-bit signed int/element</text>

  <!-- Advantage over per-tensor -->
  <rect x="25" y="263" width="750" height="110" rx="6" fill="{c}" opacity="0.07" stroke="{c}" stroke-width="1.5"/>
  <text x="45" y="286" font-family="monospace" font-size="11" font-weight="bold" fill="#333">Why block scaling beats per-tensor FP8:</text>
  <text x="45" y="306" font-family="monospace" font-size="11" fill="#555">Per-tensor: one scale for the whole matrix → must cover the dynamic range of ALL elements → precision wasted on small values</text>
  <text x="45" y="324" font-family="monospace" font-size="11" fill="#555">MX block: scale per 32 elements → captures local dynamic range → better precision for each cluster of values</text>
  <text x="45" y="344" font-family="monospace" font-size="11" fill="{c}">MX = OCP standard; hardware support: NVIDIA B100/B200 (Blackwell), AMD MI300X, Intel Gaudi 3</text>
  <text x="45" y="362" font-family="monospace" font-size="11" fill="#555">32-element block = one warp × one cycle on hardware; E8M0 scale is 1 byte per 32 elements (~3% overhead)</text>

  <!-- MXFP4 bit layout detail -->
  <rect x="25" y="393" width="750" height="77" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="45" y="415" font-family="monospace" font-size="11" font-weight="bold" fill="#333">MXFP4 element format (E2M1): 4 bits per weight</text>
  <text x="45" y="433" font-family="monospace" font-size="11" fill="#555">  [S] [E1 E0] [M0]  →  value = (-1)^S × 2^{E-1} × (1 + M/2)  (subnormal: E=0 → value = (-1)^S × 0.5 × M)</text>
  <text x="45" y="451" font-family="monospace" font-size="11" fill="{c}">  Representable values: 0, ±0.5, ±1.0, ±1.5, ±2.0, ±3.0, ±4.0, ±6.0  (7 non-zero values + 0)</text>
  <text x="45" y="469" font-family="monospace" font-size="11" fill="#555">  MXFP4 throughput on B100: ~2× MXFP8; enables W4A4-equivalent with Tensor Core hardware support</text>
""".replace("{c}", color)


@d("kivi")
def kivi_diagram_v2(color):
    return """\
  <!-- KIVI: per-channel K, per-token V quantization -->
  <text x="400" y="100" font-family="sans-serif" font-size="13" fill="#555" text-anchor="middle">Asymmetric granularity: K quantized per-group (g=16 channels), V per-token</text>

  <!-- Attention equation -->
  <text x="400" y="130" font-family="monospace" font-size="13" fill="#333" text-anchor="middle">Attention(Q, K, V)  →  Q · Q(K)ᵀ / √d  →  softmax  →  Q(V)</text>

  <!-- K quantization box -->
  <rect x="30" y="155" width="340" height="155" rx="6" fill="{c}" opacity="0.09" stroke="{c}" stroke-width="1.5"/>
  <text x="200" y="178" font-family="monospace" font-size="12" font-weight="bold" fill="#333" text-anchor="middle">Key (K) — per-group-channel quantization</text>
  <!-- K tensor grid -->
  <text x="55" y="200" font-family="monospace" font-size="10" fill="#555">channel →</text>
  <rect x="55" y="207" width="280" height="20" rx="2" fill="{c}" opacity="0.25"/>
  <text x="195" y="221" font-family="monospace" font-size="9" fill="#fff" text-anchor="middle">token 1</text>
  <rect x="55" y="229" width="280" height="20" rx="2" fill="{c}" opacity="0.18"/>
  <text x="195" y="243" font-family="monospace" font-size="9" fill="{c}" text-anchor="middle">token 2</text>
  <rect x="55" y="251" width="280" height="20" rx="2" fill="{c}" opacity="0.25"/>
  <!-- per-channel labels -->
  <text x="200" y="288" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">scale per group of 16 channels</text>
  <text x="200" y="303" font-family="monospace" font-size="10" fill="{c}" text-anchor="middle">channels stable across tokens → low-variance scale</text>

  <!-- V quantization box -->
  <rect x="430" y="155" width="340" height="155" rx="6" fill="#3DAD78" opacity="0.09" stroke="#3DAD78" stroke-width="1.5"/>
  <text x="600" y="178" font-family="monospace" font-size="12" font-weight="bold" fill="#333" text-anchor="middle">Value (V) — per-token quantization</text>
  <!-- V tensor grid — tall columns per token -->
  <rect x="450" y="207" width="30" height="80" rx="2" fill="#3DAD78" opacity="0.30"/>
  <rect x="490" y="207" width="30" height="80" rx="2" fill="#3DAD78" opacity="0.20"/>
  <rect x="530" y="207" width="30" height="80" rx="2" fill="#3DAD78" opacity="0.30"/>
  <rect x="570" y="207" width="30" height="80" rx="2" fill="#3DAD78" opacity="0.20"/>
  <rect x="610" y="207" width="30" height="80" rx="2" fill="#3DAD78" opacity="0.30"/>
  <text x="450" y="300" font-family="monospace" font-size="9" fill="#3DAD78">t1</text>
  <text x="490" y="300" font-family="monospace" font-size="9" fill="#3DAD78">t2</text>
  <text x="530" y="300" font-family="monospace" font-size="9" fill="#3DAD78">t3</text>
  <text x="600" y="288" font-family="monospace" font-size="10" fill="#555" text-anchor="middle">scale per token (1 scale / token)</text>
  <text x="600" y="303" font-family="monospace" font-size="10" fill="#3DAD78" text-anchor="middle">token norms vary → per-token scale</text>

  <!-- Residual / recent tokens -->
  <rect x="30" y="330" width="740" height="65" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="352" font-family="monospace" font-size="11" font-weight="bold" fill="#333">Residual (sliding) cache:</text>
  <text x="50" y="370" font-family="monospace" font-size="11" fill="#555">Most recent r=32 tokens kept at FP16 (not quantized). Protects attention sink + recency. Concatenated before attention.</text>
  <text x="50" y="388" font-family="monospace" font-size="11" fill="{c}">2-bit K+V (g=16): 75% KV memory cut. LLaMA-2-7B: &lt;0.3 ppl vs FP16 at 2K context. 2.35× throughput.</text>

  <!-- Implementation note -->
  <rect x="30" y="415" width="740" height="55" rx="6" fill="{c}" opacity="0.07" stroke="{c}" stroke-width="0.8"/>
  <text x="50" y="437" font-family="monospace" font-size="11" fill="#555">Implemented as a FlashAttention-2 plugin. Dequantization fused into attention kernel — &lt;5% compute overhead.</text>
  <text x="50" y="455" font-family="monospace" font-size="11" fill="{c}">No calibration needed. Works with any model out-of-the-box. INT2 and INT4 both supported.</text>
""".replace("{c}", color)


def generic_diagram(m, color):
    """Fallback generic diagram for any method."""
    name = m.get("name", m["id"])
    precision = m.get("precision", "")
    tldr = m.get("tldr", "") if m.get("tldr") else ""
    key_idea = m.get("key_idea", "") if m.get("key_idea") else ""
    category = m.get("category", "")
    calibration = m.get("calibration", "unknown")
    granularity = m.get("granularity", "unknown")
    hardware = m.get("hardware_target", "unknown")

    def safe(text):
        """Escape XML special characters."""
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def trunc(text, n=34):
        """Truncate to n chars with ellipsis."""
        s = str(text) if text else ""
        return s if len(s) <= n else s[:n - 1] + "\u2026"

    # Right panel is 355px wide, text starts at x=435 inside rect at x=415+355=770.
    # Available: 770-435-10 = 325px. Monospace 11px ≈ 6.6px/char → 49 chars max.
    # Use 46 to be safe with variable glyph widths.
    def wrap(text, width=46, max_lines=6):
        words = str(text).split()
        lines = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 <= width:
                current = current + " " + word if current else word
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines[:max_lines]

    tldr_lines = wrap(tldr, width=46, max_lines=6)
    key_lines = wrap(key_idea, width=46, max_lines=5)

    # Dynamic layout: boxes grow to fit content, capped at SVG height.
    tldr_h = max(40 + len(tldr_lines) * 20 + 10, 70)
    mech_y = 80 + tldr_h + 10
    mech_h = max(40 + len(key_lines) * 20 + 10, 60)
    bottom_y = min(mech_y + mech_h + 10, 437)
    left_h = bottom_y - 80

    content = f"""
  <!-- Generic diagram for {name} -->
  <!-- Fact panel (left) -->
  <rect x="30" y="80" width="355" height="{left_h}" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="108" font-family="monospace" font-size="12" font-weight="bold" fill="#333">Method Properties</text>
  <text x="50" y="132" font-family="monospace" font-size="11" fill="#555">Precision:    {safe(trunc(precision))}</text>
  <text x="50" y="152" font-family="monospace" font-size="11" fill="#555">Granularity:  {safe(trunc(granularity))}</text>
  <text x="50" y="172" font-family="monospace" font-size="11" fill="#555">Calibration:  {safe(trunc(calibration))}</text>
  <text x="50" y="192" font-family="monospace" font-size="11" fill="#555">Hardware:     {safe(trunc(hardware))}</text>
  <text x="50" y="212" font-family="monospace" font-size="11" fill="#555">Training:     {"yes" if m.get("requires_training") else "no"}</text>
  <text x="50" y="232" font-family="monospace" font-size="11" fill="#555">Category:     {safe(category)}</text>
"""

    # TL;DR box (right, top)
    content += f"""
  <!-- TL;DR -->
  <rect x="415" y="80" width="355" height="{tldr_h}" rx="6" fill="{color}" opacity="0.08" stroke="{color}" stroke-width="1.5"/>
  <text x="435" y="105" font-family="monospace" font-size="12" font-weight="bold" fill="#333">TL;DR</text>
"""
    for i, line in enumerate(tldr_lines):
        y = 125 + i * 20
        content += f'  <text x="435" y="{y}" font-family="monospace" font-size="11" fill="#555">{safe(line)}</text>\n'

    # Mechanism box (right, below TL;DR)
    content += f"""
  <!-- Key idea -->
  <rect x="415" y="{mech_y}" width="355" height="{mech_h}" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="435" y="{mech_y + 25}" font-family="monospace" font-size="12" font-weight="bold" fill="#333">Mechanism</text>
"""
    for i, line in enumerate(key_lines):
        y = mech_y + 45 + i * 20
        content += f'  <text x="435" y="{y}" font-family="monospace" font-size="11" fill="#555">{safe(line)}</text>\n'

    # Bottom bar
    paper_url = m.get("paper_url") or ""
    authors_str = trunc(", ".join((m.get("authors") or [])[:3]), 60)
    content += f"""
  <!-- Bottom -->
  <rect x="30" y="{bottom_y}" width="740" height="55" rx="6" fill="white" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="{bottom_y + 22}" font-family="monospace" font-size="11" fill="{color}">{safe(trunc(str(paper_url), 75))}</text>
  <text x="50" y="{bottom_y + 42}" font-family="monospace" font-size="11" fill="#555">Year: {m.get("year", "?")}  |  Authors: {safe(authors_str)}</text>
"""
    return content


def generate_svg(m, force=False):
    mid = m.get("id", "unknown")
    diag_path = ROOT / m.get("diagram", f"assets/diagrams/{mid}.svg")

    if diag_path.exists() and not force:
        return False  # already exists

    color = CATEGORY_COLORS.get(m.get("category", ""), "#607D8B")
    name = m.get("name", mid)
    precision = m.get("precision", "")
    # Truncate title-bar precision so it doesn't overlap the method name
    precision_title = precision if len(precision) <= 45 else precision[:44] + "\u2026"

    # Get content from specific or generic
    if mid in DIAGRAMS:
        content = DIAGRAMS[mid](color)
    else:
        content = generic_diagram(m, color)

    svg = SVG_TEMPLATE.format(
        color=color,
        name=name,
        precision=precision_title,
        content=content,
    )

    diag_path.parent.mkdir(parents=True, exist_ok=True)
    diag_path.write_text(svg, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate SVG diagrams")
    parser.add_argument("--all", action="store_true", help="Regenerate all diagrams")
    parser.add_argument("--id", help="Generate diagram for a specific method id")
    args = parser.parse_args()

    with open(ROOT / "methods.yml", encoding="utf-8") as f:
        methods = yaml.safe_load(f) or []

    generated = 0
    skipped = 0

    for m in methods:
        mid = m.get("id", "")
        if args.id and mid != args.id:
            continue
        created = generate_svg(m, force=args.all or bool(args.id))
        if created:
            print(f"  Generated: {mid}")
            generated += 1
        else:
            skipped += 1

    print(f"\nGenerated {generated} diagrams, skipped {skipped} existing.")


if __name__ == "__main__":
    main()
