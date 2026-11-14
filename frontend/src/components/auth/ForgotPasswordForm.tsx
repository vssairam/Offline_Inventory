import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { FieldError } from './FieldError'
import { validateEmail } from './validation'

export function ForgotPasswordForm() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitted, setSubmitted] = useState(false)

  const handle = (e: FormEvent) => {
    e.preventDefault()
    const err = validateEmail(email)
    setError(err)
    if (!err) setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="flex flex-col gap-4">
        <p role="status" className="text-sm text-muted-foreground">
          Password reset by email is not available yet. Please contact your administrator to reset your password.
        </p>
        <Link to="/login" className="text-sm text-primary underline">Back to sign in</Link>
      </div>
    )
  }

  return (
    <form onSubmit={handle} noValidate className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <Label htmlFor="email">Email</Label>
        <Input id="email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <FieldError id="email-error" message={error ?? undefined} />
      </div>
      <Button type="submit">Request reset</Button>
      <Link to="/login" className="text-sm text-primary underline">Back to sign in</Link>
    </form>
  )
}
