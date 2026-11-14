import { useQuery } from '@tanstack/react-query'
import { alertService } from '@/services/alertService'

export function useUnreadAlertCount(enabled: boolean): number {
  const { data } = useQuery({
    queryKey: ['alerts', 'unread-count'],
    queryFn: async () => (await alertService.list({ page: 1, page_size: 1 })).unread_count,
    enabled,
    refetchInterval: 60_000,
    retry: false,
  })
  return data ?? 0
}
