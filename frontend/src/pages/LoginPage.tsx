import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { LoginForm } from '@/components/auth/LoginForm'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/context/AuthContext'

export function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? '/dashboard'

  if (user) return <Navigate to={from} replace />

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Sign in</CardTitle>
        </CardHeader>
        <CardContent>
          <LoginForm
            onSubmit={async (email, password) => {
              await login(email, password)
              navigate(from, { replace: true })
            }}
          />
        </CardContent>
      </Card>
    </div>
  )
}
