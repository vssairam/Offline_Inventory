import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { FieldError } from '@/components/auth/FieldError'
import { useAuth } from '@/context/AuthContext'
import { getApiErrorMessage } from '@/services/authService'

export function ProfilePage() {
  const { user, updateProfile } = useAuth()
  const [fullName, setFullName] = useState(user?.full_name ?? '')
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  if (!user) return null

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSaved(false)
    setError(null)
    if (!fullName.trim()) {
      setError('Full name is required')
      return
    }
    setSubmitting(true)
    try {
      await updateProfile({ full_name: fullName.trim() })
      setSaved(true)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not update profile'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-lg">
      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" value={user.email} disabled readOnly />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="full_name">Full name</Label>
              <Input id="full_name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
              <FieldError id="full_name-error" message={error ?? undefined} />
            </div>
            {saved && <p role="status" className="text-sm text-muted-foreground">Profile updated.</p>}
            <Button type="submit" disabled={submitting}>{submitting ? 'Saving...' : 'Save changes'}</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
