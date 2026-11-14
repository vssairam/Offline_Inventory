import { Outlet } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { Sidebar } from './Sidebar'
import { AlertsBell } from '@/components/alerts/AlertsBell'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/context/AuthContext'

export function AppLayout() {
  const { user, logout } = useAuth()
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center justify-end gap-3 border-b px-6">
          <AlertsBell enabled={user !== null} />
          <span className="text-sm text-muted-foreground">{user?.full_name ?? user?.email}</span>
          <Button variant="ghost" size="sm" onClick={() => void logout()}>
            <LogOut className="h-4 w-4" /> Logout
          </Button>
        </header>
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
