import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/context/AuthContext'

export function SettingsPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  if (!user) return null

  async function handleSignOut() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Settings</h1>
      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <dl className="grid grid-cols-[8rem_1fr] gap-y-2">
            <dt className="text-muted-foreground">Name</dt>
            <dd>{user.full_name}</dd>
            <dt className="text-muted-foreground">Email</dt>
            <dd>{user.email}</dd>
            <dt className="text-muted-foreground">Role</dt>
            <dd>{user.is_admin ? 'Administrator' : 'User'}</dd>
          </dl>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate('/profile')}>
              Edit profile
            </Button>
            <Button variant="destructive" onClick={handleSignOut}>
              Sign out
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
