import { describe, it, expect } from 'vitest'
import { parsePrecision } from './precision'

describe('parsePrecision', () => {
  it('parses W4A16 (no space)', () => {
    const r = parsePrecision('W4A16')
    expect(r.wBits).toEqual([4])
    expect(r.aBits).toEqual([16])
    expect(r.kvBits).toEqual([])
  })

  it('parses W4A16KV4', () => {
    const r = parsePrecision('W4A16KV4')
    expect(r.wBits).toEqual([4])
    expect(r.aBits).toEqual([16])
    expect(r.kvBits).toEqual([4])
  })

  it('parses W8A8', () => {
    const r = parsePrecision('W8A8')
    expect(r.wBits).toEqual([8])
    expect(r.aBits).toEqual([8])
    expect(r.kvBits).toEqual([])
  })

  it('parses W1.58A8', () => {
    const r = parsePrecision('W1.58A8')
    expect(r.wBits).toEqual([1.58])
    expect(r.aBits).toEqual([8])
    expect(r.kvBits).toEqual([])
  })

  it('parses W4A16 (AWQ) — ignores parenthetical', () => {
    const r = parsePrecision('W4A16 (AWQ)')
    expect(r.wBits).toEqual([4])
    expect(r.aBits).toEqual([16])
  })

  it('parses W1.58 A16 (with space)', () => {
    const r = parsePrecision('W1.58 A16 (ternary PTQ)')
    expect(r.wBits).toEqual([1.58])
    expect(r.aBits).toEqual([16])
  })

  it('parses multi-format W2/W3 A16', () => {
    const r = parsePrecision('W2/W3 A16')
    expect(r.wBits).toContain(2)
    expect(r.wBits).toContain(3)
    expect(r.aBits).toEqual([16])
  })

  it('parses W2-W8 A16 mixed', () => {
    const r = parsePrecision('W2-W8 A16 mixed (per-layer)')
    expect(r.wBits).toContain(2)
    expect(r.wBits).toContain(8)
    expect(r.aBits).toEqual([16])
  })

  it('parses FP8 training format', () => {
    const r = parsePrecision('FP8 (E4M3 forward / E5M2 gradient)')
    expect(r.wBits).toEqual([8])
    expect(r.aBits).toEqual([8])
  })

  it('parses KV-only format', () => {
    const r = parsePrecision('KV2 (2-bit keys and values)')
    expect(r.kvBits).toContain(2)
    expect(r.wBits).toEqual([])
    expect(r.aBits).toEqual([])
  })

  it('parses W16A16KV2-4 mixed', () => {
    const r = parsePrecision('W16A16KV2/KV4')
    expect(r.wBits).toEqual([16])
    expect(r.aBits).toEqual([16])
    expect(r.kvBits).toContain(2)
    expect(r.kvBits).toContain(4)
  })

  it('returns empty for n/a', () => {
    const r = parsePrecision('n/a (pruning framework)')
    expect(r.wBits).toEqual([])
    expect(r.aBits).toEqual([])
    expect(r.kvBits).toEqual([])
  })

  it('handles empty string', () => {
    const r = parsePrecision('')
    expect(r.wBits).toEqual([])
    expect(r.aBits).toEqual([])
    expect(r.kvBits).toEqual([])
  })

  it('parses W4A8KV4', () => {
    const r = parsePrecision('W4A8KV4')
    expect(r.wBits).toEqual([4])
    expect(r.aBits).toEqual([8])
    expect(r.kvBits).toEqual([4])
  })

  it('parses MXFP8 format', () => {
    const r = parsePrecision('MXFP8 / MXFP6 / MXFP4 / MXINT8')
    expect(r.wBits.length).toBeGreaterThan(0)
  })

  it('deduplicates bits', () => {
    const r = parsePrecision('W4A16 (GPTQ/AWQ/Marlin), W4A8 (Marlin)')
    expect(r.wBits.filter(b => b === 4).length).toBe(1) // no duplicates
  })
})
