import { describe, it, expect } from 'vitest'
import { applyFilters, defaultFilters, filterSummary, isDefaultFilters } from './filters'
import type { Method } from '../data/schema'

function makeMethod(overrides: Partial<Method>): Method {
  return {
    id: 'test',
    name: 'Test',
    full_name: 'Test Method',
    category: 'ptq_weight_only',
    subcategory: '',
    year: 2023,
    date: '2023-01-01',
    authors: ['Author A'],
    affiliation: [],
    paper_url: null,
    code_url: null,
    blog_url: null,
    venue: '',
    precision: 'W4A16',
    granularity: 'per-group',
    calibration: 'yes',
    symmetric: 'true',
    handles_outliers_via: 'none',
    hardware_target: 'GPU',
    requires_training: false,
    requires_calibration_data: true,
    typical_degradation: '<1 ppl',
    tldr: 'A test method',
    key_idea: 'Key idea here',
    builds_on: [],
    superseded_by: [],
    related: [],
    diagram: '',
    diagram_caption: '',
    ...overrides,
  }
}

const FIXTURE: Method[] = [
  makeMethod({ id: 'gptq',      name: 'GPTQ',      year: 2022, category: 'ptq_weight_only',       precision: 'W4A16', requires_calibration_data: true }),
  makeMethod({ id: 'smoothq',   name: 'SmoothQ',   year: 2023, category: 'ptq_weight_activation', precision: 'W8A8',  requires_calibration_data: true }),
  makeMethod({ id: 'qlora',     name: 'QLoRA',     year: 2023, category: 'qat',                   precision: 'W4A16 (NF4)', requires_training: true, requires_calibration_data: false }),
  makeMethod({ id: 'bitnet',    name: 'BitNet',    year: 2023, category: 'extreme_lowbit',         precision: 'W1 A16', requires_training: true }),
  makeMethod({ id: 'kivi',      name: 'KIVI',      year: 2024, category: 'kv_cache',              precision: 'W16A16KV2', requires_calibration_data: false }),
]

const YEAR_MIN = 2022
const YEAR_MAX = 2024

describe('applyFilters', () => {
  it('returns all methods with default filters', () => {
    const f = defaultFilters(YEAR_MIN, YEAR_MAX)
    expect(applyFilters(FIXTURE, f, 'newest')).toHaveLength(5)
  })

  it('filters by category', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), categories: ['ptq_weight_only'] }
    const result = applyFilters(FIXTURE, f, 'newest')
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('gptq')
  })

  it('filters by multiple categories', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), categories: ['ptq_weight_only', 'qat'] }
    const result = applyFilters(FIXTURE, f, 'newest')
    expect(result).toHaveLength(2)
  })

  it('filters by W bits', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), wBits: [1] }
    const result = applyFilters(FIXTURE, f, 'newest')
    expect(result.some(m => m.id === 'bitnet')).toBe(true)
    expect(result.every(m => m.id === 'bitnet')).toBe(true)
  })

  it('filters by KV bits', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), kvBits: [2], kvNa: false }
    const result = applyFilters(FIXTURE, f, 'newest')
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('kivi')
  })

  it('filters by calibration = yes', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), calibration: 'yes' as const }
    const result = applyFilters(FIXTURE, f, 'newest')
    expect(result.every(m => m.requires_calibration_data)).toBe(true)
  })

  it('filters by calibration = no', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), calibration: 'no' as const }
    const result = applyFilters(FIXTURE, f, 'newest')
    expect(result.every(m => !m.requires_calibration_data)).toBe(true)
    expect(result.length).toBeGreaterThan(0)
  })

  it('filters by requires_training = yes', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), training: 'yes' as const }
    const result = applyFilters(FIXTURE, f, 'newest')
    expect(result.every(m => m.requires_training)).toBe(true)
    expect(result.length).toBe(2) // qlora + bitnet
  })

  it('filters by year range', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), yearMin: 2024, yearMax: 2024 }
    const result = applyFilters(FIXTURE, f, 'newest')
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('kivi')
  })

  it('filters by text search (name)', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), search: 'bitnet' }
    const result = applyFilters(FIXTURE, f, 'newest')
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('bitnet')
  })

  it('filters by text search (author)', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), search: 'author a' }
    const result = applyFilters(FIXTURE, f, 'newest')
    expect(result).toHaveLength(5)
  })

  it('returns empty array when nothing matches', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), search: 'zzznomatch' }
    expect(applyFilters(FIXTURE, f, 'newest')).toHaveLength(0)
  })
})

describe('sort', () => {
  it('sorts newest first', () => {
    const result = applyFilters(FIXTURE, defaultFilters(YEAR_MIN, YEAR_MAX), 'newest')
    expect(result[0].year).toBeGreaterThanOrEqual(result[result.length - 1].year)
  })

  it('sorts oldest first', () => {
    const result = applyFilters(FIXTURE, defaultFilters(YEAR_MIN, YEAR_MAX), 'oldest')
    expect(result[0].year).toBeLessThanOrEqual(result[result.length - 1].year)
  })

  it('sorts alphabetically', () => {
    const result = applyFilters(FIXTURE, defaultFilters(YEAR_MIN, YEAR_MAX), 'alpha')
    const names = result.map(m => m.name)
    expect(names).toEqual([...names].sort())
  })
})

describe('filterSummary', () => {
  it('returns empty array for default filters', () => {
    const f = defaultFilters(YEAR_MIN, YEAR_MAX)
    expect(filterSummary(f, YEAR_MIN, YEAR_MAX)).toHaveLength(0)
  })

  it('includes category in summary', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), categories: ['ptq_weight_only'] }
    expect(filterSummary(f, YEAR_MIN, YEAR_MAX).some(s => s.includes('ptq'))).toBe(true)
  })

  it('includes search in summary', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), search: 'gptq' }
    expect(filterSummary(f, YEAR_MIN, YEAR_MAX).some(s => s.includes('gptq'))).toBe(true)
  })
})

describe('isDefaultFilters', () => {
  it('returns true for fresh defaults', () => {
    expect(isDefaultFilters(defaultFilters(YEAR_MIN, YEAR_MAX), YEAR_MIN, YEAR_MAX)).toBe(true)
  })

  it('returns false after category selection', () => {
    const f = { ...defaultFilters(YEAR_MIN, YEAR_MAX), categories: ['qat'] }
    expect(isDefaultFilters(f, YEAR_MIN, YEAR_MAX)).toBe(false)
  })
})
