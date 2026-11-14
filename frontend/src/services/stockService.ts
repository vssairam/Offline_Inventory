import api from '@/services/api'
import type { Paginated } from '@/types'

export interface StockItem {
  id: number
  name: string
  sku: string
  quantity: number
  reorder_level: number
  is_low: boolean
}

export interface StockListParams {
  q?: string
  low_stock?: boolean
  page?: number
  page_size?: number
}

export const stockService = {
  list: async (params: StockListParams = {}): Promise<Paginated<StockItem>> => {
    const clean = Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== '' && v !== false),
    )
    return (await api.get<Paginated<StockItem>>('/stock', { params: clean })).data
  },
}
