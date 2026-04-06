export interface ParsedPrecision {
  wBits: number[]
  aBits: number[]
  kvBits: number[]
}

const EMPTY: ParsedPrecision = { wBits: [], aBits: [], kvBits: [] }

/** Parse a precision string like "W4A16KV4" into numeric bit arrays. */
export function parsePrecision(s: string): ParsedPrecision {
  if (!s || s === 'n/a' || s.startsWith('n/a')) return EMPTY

  // KV bits: "KV" followed by a number
  const kvBits = uniq(
    [...s.matchAll(/KV(\d+(?:\.\d+)?)/g)].map(m => parseFloat(m[1]))
  )

  // KV-only notations: "KV2 (2-bit keys...)"
  if (s.startsWith('KV') && !/W\d/.test(s)) {
    return { wBits: [], aBits: [], kvBits }
  }

  // Weight bits: "W" followed by a number
  const wBits = uniq(
    [...s.matchAll(/W(\d+(?:\.\d+)?)/g)].map(m => parseFloat(m[1]))
  )

  // Activation bits: "A" preceded by digit/./space/slash, followed by digits
  // Lookbehind ensures we don't match "AQLM", "QAT" etc.
  const aBits = uniq(
    [...s.matchAll(/(?<=[\d.\s\/])A(\d+(?:\.\d+)?)/g)].map(m => parseFloat(m[1])).filter(v => v <= 32)
  )

  // FP8 without explicit W/A notation
  if (wBits.length === 0 && /FP8/i.test(s)) {
    return { wBits: [8], aBits: aBits.length ? aBits : [8], kvBits }
  }

  // MXFP / NVFP formats — extract the highest fp bits
  if (wBits.length === 0 && /MXFP|NVFP/i.test(s)) {
    const fpNums = [...s.matchAll(/(?:MX|NV)FP(\d+)/gi)].map(m => parseFloat(m[1]))
    return { wBits: uniq(fpNums), aBits: aBits.length ? aBits : uniq(fpNums), kvBits }
  }

  // "Q8K8V16" style — treat as A8
  if (wBits.length === 0 && /Q8K8V16/i.test(s)) {
    return { wBits: [], aBits: [8], kvBits: [16] }
  }

  return { wBits, aBits, kvBits }
}

function uniq(arr: number[]): number[] {
  return [...new Set(arr)]
}

/** True if any of methodBits are in the selectedBits set. */
export function bitsMatch(methodBits: number[], selectedBits: number[]): boolean {
  if (selectedBits.length === 0) return true
  return methodBits.some(b => selectedBits.includes(b))
}

/** All distinct W-bit values present in the dataset. */
export const ALL_W_BITS  = [1, 1.58, 2, 3, 4, 6, 8, 16]
export const ALL_A_BITS  = [1, 4, 8, 16]
export const ALL_KV_BITS = [2, 4, 8]
