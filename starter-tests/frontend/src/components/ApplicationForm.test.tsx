import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { Company } from '../types'
import { ApplicationForm } from './ApplicationForm'

const companies: Company[] = [
  { id: 1, name: 'Acme' },
  { id: 2, name: 'Globex' },
]

async function fillAndSubmit(user: UserEvent) {
  await user.selectOptions(screen.getByLabelText('Company'), 'Globex')
  await user.type(screen.getByLabelText('Role'), 'QA Analyst')
  await user.type(screen.getByLabelText('Date applied'), '2026-10-03')
  await user.click(screen.getByRole('button', { name: 'Add application' }))
}

describe('ApplicationForm', () => {
  it('asks for a company first when there are none', () => {
    render(<ApplicationForm companies={[]} onSubmit={vi.fn()} />)

    expect(screen.getByText('Add a company first.')).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Add application' }),
    ).not.toBeInTheDocument()
  })

  it('lists every company as an option', () => {
    render(<ApplicationForm companies={companies} onSubmit={vi.fn()} />)

    expect(screen.getByRole('option', { name: 'Acme' })).toBeInTheDocument()
    expect(
      screen.getByRole('option', { name: 'Globex' }),
    ).toBeInTheDocument()
  })

  it('submits the chosen company id as a number', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<ApplicationForm companies={companies} onSubmit={onSubmit} />)

    await fillAndSubmit(user)

    expect(onSubmit).toHaveBeenCalledWith({
      company_id: 2,
      role: 'QA Analyst',
      status: 'applied',
      applied_on: '2026-10-03',
    })
  })

  it('clears the fields after submitting', async () => {
    const user = userEvent.setup()
    render(<ApplicationForm companies={companies} onSubmit={vi.fn()} />)

    await fillAndSubmit(user)

    expect(screen.getByLabelText('Role')).toHaveValue('')
    expect(screen.getByLabelText('Date applied')).toHaveValue('')
  })
})
