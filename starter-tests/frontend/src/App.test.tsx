import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import * as api from './api'
import type { Application, Company } from './types'

/**
 * `vi.mock('./api')` replaces every function exported by `api.ts` with
 * a mock that does nothing. No request ever leaves the test. Each test
 * then tells the mocks what to return with `vi.mocked(...)`.
 */
vi.mock('./api')

const acme: Company = { id: 1, name: 'Acme' }

const developer: Application = {
  id: 1,
  role: 'Junior Developer',
  status: 'applied',
  applied_on: '2026-10-01',
  company: acme,
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(api.fetchCompanies).mockResolvedValue([acme])
  vi.mocked(api.fetchApplications).mockResolvedValue([developer])
})

describe('App: loading', () => {
  it('shows applications from the server', async () => {
    render(<App />)

    expect(await screen.findByText('Junior Developer')).toBeInTheDocument()
  })

  it('offers companies from the server in the form', async () => {
    render(<App />)

    expect(
      await screen.findByRole('option', { name: 'Acme' }),
    ).toBeInTheDocument()
  })

  it('shows an error when loading fails', async () => {
    vi.mocked(api.fetchApplications).mockRejectedValue(
      new Error('Network down'),
    )

    render(<App />)

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Could not load',
    )
  })
})

describe('App: companies', () => {
  it('adds a new company to the company picker', async () => {
    const user = userEvent.setup()
    vi.mocked(api.createCompany).mockResolvedValue({
      id: 2,
      name: 'Globex',
    })
    render(<App />)
    await screen.findByText('Junior Developer')

    await user.type(screen.getByLabelText('Company name'), 'Globex')
    await user.click(screen.getByRole('button', { name: 'Add company' }))

    expect(api.createCompany).toHaveBeenCalledWith('Globex')
    expect(
      await screen.findByRole('option', { name: 'Globex' }),
    ).toBeInTheDocument()
  })

  it("shows the server's reason when a company can't be added", async () => {
    const user = userEvent.setup()
    vi.mocked(api.createCompany).mockRejectedValue(
      new Error('Company already exists'),
    )
    render(<App />)
    await screen.findByText('Junior Developer')

    await user.type(screen.getByLabelText('Company name'), 'Acme')
    await user.click(screen.getByRole('button', { name: 'Add company' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Company already exists',
    )
  })
})

describe('App: applications', () => {
  it('adds a new application to the list', async () => {
    const user = userEvent.setup()
    vi.mocked(api.createApplication).mockResolvedValue({
      id: 2,
      role: 'QA Analyst',
      status: 'applied',
      applied_on: '2026-10-03',
      company: acme,
    })
    render(<App />)
    await screen.findByText('Junior Developer')

    await user.selectOptions(screen.getByLabelText('Company'), 'Acme')
    await user.type(screen.getByLabelText('Role'), 'QA Analyst')
    await user.type(screen.getByLabelText('Date applied'), '2026-10-03')
    await user.click(
      screen.getByRole('button', { name: 'Add application' }),
    )

    expect(api.createApplication).toHaveBeenCalledWith({
      company_id: 1,
      role: 'QA Analyst',
      status: 'applied',
      applied_on: '2026-10-03',
    })
    expect(await screen.findByText('QA Analyst')).toBeInTheDocument()
  })

  it('shows the new status after a change', async () => {
    const user = userEvent.setup()
    vi.mocked(api.updateStatus).mockResolvedValue({
      ...developer,
      status: 'offer',
    })
    render(<App />)
    await screen.findByText('Junior Developer')

    const select = screen.getByRole('combobox', {
      name: 'Status for Junior Developer at Acme',
    })
    await user.selectOptions(select, 'offer')

    expect(api.updateStatus).toHaveBeenCalledWith(1, 'offer')
    await waitFor(() => expect(select).toHaveValue('offer'))
  })

  it('shows an error and keeps the old status if a change fails', async () => {
    const user = userEvent.setup()
    vi.mocked(api.updateStatus).mockRejectedValue(new Error('Oops'))
    render(<App />)
    await screen.findByText('Junior Developer')

    const select = screen.getByRole('combobox', {
      name: 'Status for Junior Developer at Acme',
    })
    await user.selectOptions(select, 'offer')

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Could not update',
    )
    expect(select).toHaveValue('applied')
  })

  it('removes a deleted application', async () => {
    const user = userEvent.setup()
    vi.mocked(api.deleteApplication).mockResolvedValue(undefined)
    render(<App />)
    await screen.findByText('Junior Developer')

    await user.click(
      screen.getByRole('button', {
        name: 'Delete Junior Developer at Acme',
      }),
    )

    expect(api.deleteApplication).toHaveBeenCalledWith(1)
    await waitFor(() =>
      expect(
        screen.queryByText('Junior Developer'),
      ).not.toBeInTheDocument(),
    )
  })

  it('shows an error and keeps the application if delete fails', async () => {
    const user = userEvent.setup()
    vi.mocked(api.deleteApplication).mockRejectedValue(new Error('Oops'))
    render(<App />)
    await screen.findByText('Junior Developer')

    await user.click(
      screen.getByRole('button', {
        name: 'Delete Junior Developer at Acme',
      }),
    )

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Could not delete',
    )
    expect(screen.getByText('Junior Developer')).toBeInTheDocument()
  })
})

describe('App: filtering', () => {
  it('asks the server for the chosen status', async () => {
    const user = userEvent.setup()
    render(<App />)
    await screen.findByText('Junior Developer')

    await user.selectOptions(screen.getByLabelText('Show'), 'offer')

    await waitFor(() =>
      expect(api.fetchApplications).toHaveBeenLastCalledWith('offer'),
    )
  })
})
