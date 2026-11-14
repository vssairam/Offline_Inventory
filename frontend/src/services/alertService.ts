import api from '@/services/api'
import type { Alert, Paginated } from '@/types'

export interface AlertListResponse extends Paginated<Alert> {
  unread_count: number
}

export interface AlertListParams {
  unread_only?: boolean
  page?: number
  page_size?: number
}

export const alertService = {
  list: async (params: AlertListParams = {}): Promise<AlertListResponse> => {
    const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v !== undefined && v !== false))
    return (await api.get<AlertListResponse>('/alerts', { params: clean })).data
  },
  markRead: async (id: number): Promise<Alert> => (await api.put<Alert>(`/alerts/${id}/read`)).data,
}
