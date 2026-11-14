import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getApiErrorMessage, type RegisterInput } from '@/services/authService'
import { FieldError } from './FieldError'
import { validateRegister, type RegisterErrors } from './validation'

interface Props {
  onSubmit: (input: RegisterInput) => Promise<void>
}

export function RegisterForm({ onSubmit }: Props) {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errors, setErrors] = useState<RegisterErrors>({})
  const [apiError, setApiError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handle = async (e: FormEvent) => {
    e.preventDefault()
    setApiError(null)
    const found = validateRegister({ full_name: fullName, email, password, confirmPassword })
    setErrors(found)
    if (Object.keys(found).length > 0) return
    setSubmitting(true)
    try {
      await onSubmit({ full_name: fullName.trim(), email: email.trim(), password })
    } catch (err) {
      setApiError(getApiErrorMessage(err, 'Registration failed'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handle} noValidate className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <Label htmlFor="full_name">Full name</Label>
        <Input id="full_name" autoComplete="name" value={fullName} onChange={(e) => setFullName(e.target.value)} aria-invalid={!!errors.full_name} />
        <FieldError id="full_name-error" message={errors.full_name} />
      </div>
      <div className="flex flex-col gap-2">
        <Label htmlFor="email">Email</Label>
        <Input id="email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} aria-invalid={!!errors.email} />
        <FieldError id="email-error" message={errors.email} />
      </div>
      <div className="flex flex-col gap-2">
        <Label htmlFor="password">Password</Label>
        <Input id="password" type="password" autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} aria-invalid={!!errors.password} />
        <FieldError id="password-error" message={errors.password} />
      </div>
      <div className="flex flex-col gap-2">
        <Label htmlFor="confirmPassword">Confirm password</Label>
        <Input id="confirmPassword" type="password" autoComplete="new-password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} aria-invalid={!!errors.confirmPassword} />
        <FieldError id="confirmPassword-error" message={errors.confirmPassword} />
      </div>
      {apiError && <p role="alert" className="text-sm text-destructive">{apiError}</p>}
      <Button type="submit" disabled={submitting}>{submitting ? 'Creating account...' : 'Create account'}</Button>
      <p className="text-sm text-muted-foreground">
        Already have an account? <Link to="/login" className="text-primary underline">Sign in</Link>
      </p>
    </form>
  )
}
