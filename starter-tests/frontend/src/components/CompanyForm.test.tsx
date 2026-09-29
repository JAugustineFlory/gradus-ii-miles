import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { CompanyForm } from './CompanyForm'

describe('CompanyForm', () => {
  it('submits the name without surrounding spaces', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<CompanyForm onSubmit={onSubmit} />)

    await user.type(screen.getByLabelText('Company name'), '  Globex  ')
    await user.click(screen.getByRole('button', { name: 'Add company' }))

    expect(onSubmit).toHaveBeenCalledWith('Globex')
  })

  it('clears the field after submitting', async () => {
    const user = userEvent.setup()
    render(<CompanyForm onSubmit={vi.fn()} />)

    await user.type(screen.getByLabelText('Company name'), 'Globex')
    await user.click(screen.getByRole('button', { name: 'Add company' }))

    expect(screen.getByLabelText('Company name')).toHaveValue('')
  })

  it('does not submit a name that is only spaces', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<CompanyForm onSubmit={onSubmit} />)

    await user.type(screen.getByLabelText('Company name'), '   ')
    await user.click(screen.getByRole('button', { name: 'Add company' }))

    expect(onSubmit).not.toHaveBeenCalled()
  })
})
