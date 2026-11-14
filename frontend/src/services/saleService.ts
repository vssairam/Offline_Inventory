import api from '@/services/api'
import type { Paginated, Product, Sale } from '@/types'

export interface SaleLineInput {
  product_id: number
  quantity: number
}

export interface SaleCreateInput {
  items: SaleLineInput[]
  sold_at?: string
}

export interface SaleListParams {
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}

export const saleService = {
  async create(input: SaleCreateInput): Promise<Sale> {
    const { data } = await api.post<Sale>('/sales', input)
    return data
  },
  async list(params: SaleListParams = {}): Promise<Paginated<Sale>> {
    const { data } = await api.get<Paginated<Sale>>('/sales', { params })
    return data
  },
  async get(id: number): Promise<Sale> {
    const { data } = await api.get<Sale>(`/sales/${id}`)
    return data
  },
  async searchProducts(q: string): Promise<Product[]> {
    const { data } = await api.get<Product[] | Paginated<Product>>('/products', {
      params: { q: q || undefined, page_size: 20 },
    })
    return Array.isArray(data) ? data : data.items
  },
}

export function getApiErrorMessage(err: unknown, fallback = 'Something went wrong'): string {
  const e = err as { response?: { data?: { error?: { message?: string }; detail?: unknown } } }
  const msg = e?.response?.data?.error?.message
  if (typeof msg === 'string') return msg
  const detail = e?.response?.data?.detail
  if (typeof detail === 'string') return detail
  return fallback
}
