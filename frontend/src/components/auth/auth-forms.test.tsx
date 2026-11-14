import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AxiosError } from 'axios'
import type { ReactElement } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { LoginForm } from './LoginForm'
import { RegisterForm } from './RegisterForm'
import { validateRegister } from './validation'

const wrap = (ui: ReactElement) => render(<MemoryRouter>{ui}</MemoryRouter>)

describe('validateRegister', () => {
  it('flags short password and mismatch', () => {
    expect(validateRegister({ full_name: 'A', email: 'a@b.co', password: 'short', confirmPassword: 'short' }).password).toMatch(/8 characters/)
    expect(validateRegister({ full_name: 'A', email: 'a@b.co', password: 'longenough', confirmPassword: 'other' }).confirmPassword).toMatch(/match/)
  })
})

describe('LoginForm', () => {
  it('shows validation errors and does not submit', async () => {
    const onSubmit = vi.fn()
    wrap(<LoginForm onSubmit={onSubmit} />)
    await userEvent.type(screen.getByLabelText('Email'), 'not-an-email')
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))
    expect(await screen.findByText('Enter a valid email address')).toBeInTheDocument()
    expect(screen.getByText('Password is required')).toBeInTheDocument()
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('submits valid values', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined)
    wrap(<LoginForm onSubmit={onSubmit} />)
    await userEvent.type(screen.getByLabelText('Email'), 'a@b.co')
    await userEvent.type(screen.getByLabelText('Password'), 'secret')
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))
    await waitFor(() => expect(onSubmit).toHaveBeenCalledWith('a@b.co', 'secret'))
  })
})

describe('RegisterForm', () => {
  it('validates required fields, password length and match', async () => {
    const onSubmit = vi.fn()
    wrap(<RegisterForm onSubmit={onSubmit} />)
    await userEvent.click(screen.getByRole('button', { name: /create account/i }))
    expect(await screen.findByText('Full name is required')).toBeInTheDocument()
    expect(screen.getByText('Email is required')).toBeInTheDocument()
    expect(screen.getByText('Password is required')).toBeInTheDocument()
    await userEvent.type(screen.getByLabelText('Full name'), 'Jane')
    await userEvent.type(screen.getByLabelText('Email'), 'j@x.co')
    await userEvent.type(screen.getByLabelText('Password'), 'password1')
    await userEvent.type(screen.getByLabelText('Confirm password'), 'password2')
    await userEvent.click(screen.getByRole('button', { name: /create account/i }))
    expect(await screen.findByText('Passwords do not match')).toBeInTheDocument()
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('shows API error message on failure', async () => {
    const err = new AxiosError('x', '409', undefined, undefined, {
      status: 409,
      statusText: '',
      headers: {},
      config: {} as never,
      data: { error: { code: 'CONFLICT', message: 'Email already registered' } },
    })
    const onSubmit = vi.fn().mockRejectedValue(err)
    wrap(<RegisterForm onSubmit={onSubmit} />)
    await userEvent.type(screen.getByLabelText('Full name'), 'Jane')
    await userEvent.type(screen.getByLabelText('Email'), 'j@x.co')
    await userEvent.type(screen.getByLabelText('Password'), 'password1')
    await userEvent.type(screen.getByLabelText('Confirm password'), 'password1')
    await userEvent.click(screen.getByRole('button', { name: /create account/i }))
    expect(await screen.findByText('Email already registered')).toBeInTheDocument()
  })
})
