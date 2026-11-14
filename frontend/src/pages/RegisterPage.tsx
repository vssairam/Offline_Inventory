import { Navigate, useNavigate } from 'react-router-dom'
import { RegisterForm } from '@/components/auth/RegisterForm'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/context/AuthContext'

export function RegisterPage() {
  const { user, register } = useAuth()
  const navigate = useNavigate()
  if (user) return <Navigate to="/dashboard" replace />
  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Create account</CardTitle>
        </CardHeader>
        <CardContent>
          <RegisterForm
            onSubmit={async (input) => {
              await register(input)
              navigate('/dashboard', { replace: true })
            }}
          />
        </CardContent>
      </Card>
    </div>
  )
}
