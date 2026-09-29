import { describe, expect, it } from 'vitest'
import { formatStatus } from './formatStatus'

describe('formatStatus', () => {
  it('capitalizes the first letter', () => {
    expect(formatStatus('applied')).toBe('Applied')
  })

  it('leaves an empty string empty', () => {
    expect(formatStatus('')).toBe('')
  })
})
