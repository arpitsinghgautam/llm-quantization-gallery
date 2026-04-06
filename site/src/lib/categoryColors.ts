/** Hex colors that exactly match the SVG diagram generator (generate_diagrams.py). */
export const CATEGORY_COLORS: Record<string, string> = {
  ptq_weight_only:        '#4A90D9',
  ptq_weight_activation:  '#E87D3E',
  qat:                    '#7B68EE',
  extreme_lowbit:         '#E84393',
  kv_cache:               '#3DAD78',
  low_precision_training: '#D4A027',
  moe:                    '#9B59B6',
  systems:                '#607D8B',
}

export const CATEGORY_LABELS: Record<string, string> = {
  ptq_weight_only:        'PTQ W-only',
  ptq_weight_activation:  'PTQ W+A',
  qat:                    'QAT / QFT',
  extreme_lowbit:         'Sub-2-bit',
  kv_cache:               'KV Quant',
  low_precision_training: 'LP Training',
  moe:                    'MoE Quant',
  systems:                'Systems',
}

export const CATEGORY_TITLES: Record<string, string> = {
  ptq_weight_only:        'Post-Training Quantization — Weight-Only',
  ptq_weight_activation:  'Post-Training Quantization — Weights + Activations',
  qat:                    'Quantization-Aware Training & Quantized Fine-Tuning',
  extreme_lowbit:         'Extreme Low-Bit & Binary/Ternary Quantization',
  kv_cache:               'KV-Cache Quantization',
  low_precision_training: 'Low-Precision Training & Numerical Formats',
  moe:                    'MoE-Specific Quantization',
  systems:                'Systems, Kernels & Runtimes',
}

export const CATEGORY_ORDER = [
  'ptq_weight_only',
  'ptq_weight_activation',
  'qat',
  'extreme_lowbit',
  'kv_cache',
  'low_precision_training',
  'moe',
  'systems',
]

export function categoryColor(cat: string): string {
  return CATEGORY_COLORS[cat] ?? '#607D8B'
}
