import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { Application } from '../types'
import { ApplicationList } from './ApplicationList'

const developer: Application = {
  id: 1,
  role: 'Junior Developer',
  status: 'applied',
  applied_on: '2026-10-01',
  company: { id: 1, name: 'Acme' },
}

const analyst: Application = {
  id: 2,
  role: 'QA Analyst',
  status: 'interviewing',
  applied_on: '2026-10-03',
  company: { id: 1, name: 'Acme' },
}

function doNothing() {}

function renderList(
  applications: Application[],
  handlers: {
    onDelete?: (id: number) => void
    onStatusChange?: (id: number, status: string) => void
  } = {},
) {
  render(
    <ApplicationList
      applications={applications}
      onDelete={handlers.onDelete ?? doNothing}
      onStatusChange={handlers.onStatusChange ?? doNothing}
    />,
  )
}

describe('ApplicationList', () => {
  it('invites you to add one when empty', () => {
    renderList([])

    expect(
      screen.getByText('No applications yet. Add your first one above.'),
    ).toBeInTheDocument()
  })

  it('shows the role, company, and date of each application', () => {
    renderList([developer, analyst])

    expect(screen.getAllByRole('listitem')).toHaveLength(2)
    expect(screen.getByText('Junior Developer')).toBeInTheDocument()
    expect(screen.getByText('QA Analyst')).toBeInTheDocument()
    expect(screen.getAllByText('Acme')).toHaveLength(2)
    expect(screen.getByText('2026-10-03')).toBeInTheDocument()
  })

  it('selects each application\u2019s current status', () => {
    renderList([developer, analyst])

    expect(
      screen.getByRole('combobox', {
        name: 'Status for QA Analyst at Acme',
      }),
    ).toHaveValue('interviewing')
  })

  it('calls onDelete with the id', async () => {
    const user = userEvent.setup()
    const onDelete = vi.fn()
    renderList([developer, analyst], { onDelete })

    await user.click(
      screen.getByRole('button', {
        name: 'Delete QA Analyst at Acme',
      }),
    )

    expect(onDelete).toHaveBeenCalledWith(2)
  })

  it('calls onStatusChange with the id and new status', async () => {
    const user = userEvent.setup()
    const onStatusChange = vi.fn()
    renderList([developer, analyst], { onStatusChange })

    await user.selectOptions(
      screen.getByRole('combobox', {
        name: 'Status for Junior Developer at Acme',
      }),
      'offer',
    )

    expect(onStatusChange).toHaveBeenCalledWith(1, 'offer')
  })
})
