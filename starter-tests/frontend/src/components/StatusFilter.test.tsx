import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { StatusFilter } from './StatusFilter'

describe('StatusFilter', () => {
  it('shows the current choice', () => {
    render(<StatusFilter value="all" onChange={vi.fn()} />)

    expect(screen.getByLabelText('Show')).toHaveValue('all')
  })

  it('offers "All" plus every status', () => {
    render(<StatusFilter value="all" onChange={vi.fn()} />)

    const names = screen
      .getAllByRole('option')
      .map((option) => option.textContent)
    expect(names).toEqual([
      'All',
      'Applied',
      'Interviewing',
      'Offer',
      'Rejected',
    ])
  })

  it('calls onChange with the chosen value', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(<StatusFilter value="all" onChange={onChange} />)

    await user.selectOptions(screen.getByLabelText('Show'), 'offer')

    expect(onChange).toHaveBeenCalledWith('offer')
  })
})
