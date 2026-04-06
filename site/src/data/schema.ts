import { z } from 'zod'

export const MethodSchema = z.object({
  id:                       z.string(),
  name:                     z.string(),
  full_name:                z.string(),
  category:                 z.string(),
  subcategory:              z.string(),
  year:                     z.number(),
  date:                     z.string(),
  authors:                  z.array(z.string()),
  affiliation:              z.array(z.string()),
  paper_url:                z.string().url().nullable(),
  code_url:                 z.string().url().nullable(),
  blog_url:                 z.string().url().nullable(),
  venue:                    z.string(),
  precision:                z.string(),
  granularity:              z.string(),
  calibration:              z.string(),
  symmetric:                z.string(),
  handles_outliers_via:     z.string(),
  hardware_target:          z.string(),
  requires_training:        z.boolean(),
  requires_calibration_data: z.boolean(),
  typical_degradation:      z.string(),
  tldr:                     z.string(),
  key_idea:                 z.string(),
  builds_on:                z.array(z.string()),
  superseded_by:            z.array(z.string()),
  related:                  z.array(z.string()),
  diagram:                  z.string(),
  diagram_caption:          z.string(),
})

export type Method = z.infer<typeof MethodSchema>

export const MetaCategorySchema = z.object({
  id:    z.string(),
  title: z.string(),
  abbr:  z.string(),
  color: z.string(),
  count: z.number(),
})

export const MetaSchema = z.object({
  count:       z.number(),
  lastUpdated: z.string(),
  categories:  z.array(MetaCategorySchema),
})

export type Meta = z.infer<typeof MetaSchema>
export type MetaCategory = z.infer<typeof MetaCategorySchema>
