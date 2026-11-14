import { ForgotPasswordForm } from '@/components/auth/ForgotPasswordForm'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function ForgotPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Forgot password</CardTitle>
        </CardHeader>
        <CardContent>
          <ForgotPasswordForm />
        </CardContent>
      </Card>
    </div>
  )
}
