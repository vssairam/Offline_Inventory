import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'

export function ProtectedRoute({ adminOnly = false }: { adminOnly?: boolean }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <div className="p-8 text-muted-foreground">Loading...</div>
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />
  if (adminOnly && !user.is_admin) return <Navigate to="/dashboard" replace />
  return <Outlet />
}
