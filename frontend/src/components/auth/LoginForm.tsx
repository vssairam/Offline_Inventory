import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getApiErrorMessage } from '@/services/authService'
import { FieldError } from './FieldError'
import { validateLogin, type LoginErrors } from './validation'

interface Props {
  onSubmit: (email: string, password: string) => Promise<void>
}

export function LoginForm({ onSubmit }: Props) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<LoginErrors>({})
  const [apiError, setApiError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handle = async (e: FormEvent) => {
    e.preventDefault()
    setApiError(null)
    const found = validateLogin({ email, password })
    setErrors(found)
    if (Object.keys(found).length > 0) return
    setSubmitting(true)
    try {
      await onSubmit(email.trim(), password)
    } catch (err) {
      setApiError(getApiErrorMessage(err, 'Invalid email or password'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handle} noValidate className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <Label htmlFor="email">Email</Label>
        <Input id="email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} aria-invalid={!!errors.email} />
        <FieldError id="email-error" message={errors.email} />
      </div>
      <div className="flex flex-col gap-2">
        <Label htmlFor="password">Password</Label>
        <Input id="password" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} aria-invalid={!!errors.password} />
        <FieldError id="password-error" message={errors.password} />
      </div>
      {apiError && <p role="alert" className="text-sm text-destructive">{apiError}</p>}
      <Button type="submit" disabled={submitting}>{submitting ? 'Signing in...' : 'Sign in'}</Button>
      <div className="flex justify-between text-sm text-muted-foreground">
        <Link to="/forgot-password" className="text-primary underline">Forgot password?</Link>
        <span>
          No account? <Link to="/register" className="text-primary underline">Register</Link>
        </span>
      </div>
    </form>
  )
}
