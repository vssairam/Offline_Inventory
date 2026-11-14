import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { alertService } from '@/services/alertService'
import { apiErrorMessage } from '@/services/productService'
import { cn } from '@/lib/utils'

interface Props {
  unreadOnly?: boolean
  pageSize?: number
}

export function AlertList({ unreadOnly = false, pageSize = 20 }: Props) {
  const qc = useQueryClient()
  const alerts = useQuery({
    queryKey: ['alerts', 'list', { unreadOnly, pageSize }],
    queryFn: () => alertService.list({ unread_only: unreadOnly, page: 1, page_size: pageSize }),
  })
  const markRead = useMutation({
    mutationFn: (id: number) => alertService.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['alerts'] }),
  })

  if (alerts.isLoading) return <p className="p-4 text-sm text-muted-foreground">Loading alerts...</p>
  if (alerts.isError)
    return <p role="alert" className="p-4 text-sm text-destructive">{apiErrorMessage(alerts.error, 'Failed to load alerts')}</p>
  const items = alerts.data?.items ?? []
  if (items.length === 0) return <p className="p-4 text-sm text-muted-foreground">No alerts.</p>

  return (
    <ul className="divide-y">
      {items.map((a) => (
        <li key={a.id} className={cn('flex items-start justify-between gap-3 p-3 text-sm', !a.is_read && 'bg-muted/50')}>
          <div>
            <p className={cn(!a.is_read && 'font-medium')}>{a.message}</p>
            <p className="text-xs text-muted-foreground">{new Date(a.created_at).toLocaleString()}</p>
          </div>
          {!a.is_read && (
            <Button
              variant="outline"
              size="sm"
              disabled={markRead.isPending}
              onClick={() => markRead.mutate(a.id)}
              aria-label={`Mark alert ${a.id} as read`}
            >
              Mark read
            </Button>
          )}
        </li>
      ))}
    </ul>
  )
}
