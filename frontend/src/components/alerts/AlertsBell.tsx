import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Bell } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { AlertList } from '@/components/alerts/AlertList'
import { useUnreadAlertCount } from '@/hooks/useUnreadAlerts'

export function AlertsBell({ enabled }: { enabled: boolean }) {
  const [open, setOpen] = useState(false)
  const unread = useUnreadAlertCount(enabled)

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="sm"
        aria-label={`Alerts${unread > 0 ? `, ${unread} unread` : ''}`}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
      >
        <Bell className="h-4 w-4" />
        {unread > 0 && <Badge variant="destructive">{unread}</Badge>}
      </Button>
      {open && (
        <div className="absolute right-0 z-40 mt-2 w-80 rounded-md border bg-card shadow-lg" role="region" aria-label="Recent alerts">
          <div className="flex items-center justify-between border-b px-3 py-2">
            <span className="text-sm font-semibold">Unread alerts</span>
            <Link to="/alerts" className="text-xs text-primary hover:underline" onClick={() => setOpen(false)}>View all</Link>
          </div>
          <div className="max-h-80 overflow-auto">
            <AlertList unreadOnly pageSize={5} />
          </div>
        </div>
      )}
    </div>
  )
}
