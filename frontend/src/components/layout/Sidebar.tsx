import { NavLink } from 'react-router-dom'
import { BarChart3, Bell, Boxes, LayoutDashboard, Package, Receipt, Shield, type LucideIcon } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { useAuth } from '@/context/AuthContext'
import { useUnreadAlertCount } from '@/hooks/useUnreadAlerts'

interface NavItem {
  to: string
  label: string
  icon: LucideIcon
  adminOnly?: boolean
  showAlertBadge?: boolean
}

const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/products', label: 'Products', icon: Package },
  { to: '/stock', label: 'Stock', icon: Boxes },
  { to: '/sales', label: 'Sales', icon: Receipt },
  { to: '/reports', label: 'Reports', icon: BarChart3 },
  { to: '/alerts', label: 'Alerts', icon: Bell, showAlertBadge: true },
  { to: '/admin', label: 'Admin', icon: Shield, adminOnly: true },
]

export function Sidebar() {
  const { user } = useAuth()
  const unread = useUnreadAlertCount(user !== null)

  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r bg-card md:flex">
      <div className="flex h-14 items-center px-5 text-lg font-semibold">Inventory</div>
      <nav className="flex flex-1 flex-col gap-1 p-3" aria-label="Main">
        {NAV_ITEMS.filter((i) => !i.adminOnly || user?.is_admin).map(({ to, label, icon: Icon, showAlertBadge }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground',
                isActive && 'bg-accent text-accent-foreground',
              )
            }
          >
            <Icon className="h-4 w-4" />
            <span className="flex-1">{label}</span>
            {showAlertBadge && unread > 0 && <Badge variant="destructive">{unread}</Badge>}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
