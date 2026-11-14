import { AxiosError } from 'axios'
import api from '@/services/api'
import type { Category, Paginated, Product } from '@/types'

export interface ProductListParams {
  q?: string
  category_id?: number
  low_stock?: boolean
  page?: number
  page_size?: number
}

export interface ProductPayload {
  name: string
  sku: string
  category_id: number | null
  price: number
  cost: number
  quantity: number
  reorder_level: number
  is_active: boolean
}

export const productService = {
  list: async (params: ProductListParams = {}): Promise<Paginated<Product>> => {
    const clean = Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== '' && v !== false),
    )
    return (await api.get<Paginated<Product>>('/products', { params: clean })).data
  },
  get: async (id: number): Promise<Product> => (await api.get<Product>(`/products/${id}`)).data,
  create: async (payload: ProductPayload): Promise<Product> => (await api.post<Product>('/products', payload)).data,
  update: async (id: number, payload: Partial<ProductPayload>): Promise<Product> =>
    (await api.put<Product>(`/products/${id}`, payload)).data,
  remove: async (id: number): Promise<void> => {
    await api.delete(`/products/${id}`)
  },
  uploadImage: async (id: number, file: File): Promise<Product> => {
    const form = new FormData()
    form.append('file', file)
    // Unset the JSON content type so the browser sets the multipart boundary.
    return (await api.post<Product>(`/products/${id}/image`, form, { headers: { 'Content-Type': undefined } })).data
  },
}

export const categoryService = {
  list: async (): Promise<Category[]> => {
    const data = (await api.get<Category[] | Paginated<Category>>('/categories')).data
    return Array.isArray(data) ? data : data.items
  },
  create: async (name: string): Promise<Category> => (await api.post<Category>('/categories', { name })).data,
  update: async (id: number, name: string): Promise<Category> =>
    (await api.put<Category>(`/categories/${id}`, { name })).data,
  remove: async (id: number): Promise<void> => {
    await api.delete(`/categories/${id}`)
  },
}

export function isLowStock(p: Pick<Product, 'quantity' | 'reorder_level'>): boolean {
  return p.quantity <= p.reorder_level
}

export function apiErrorMessage(err: unknown, fallback = 'Something went wrong'): string {
  if (err instanceof AxiosError) {
    const msg = (err.response?.data as { error?: { message?: string } } | undefined)?.error?.message
    if (msg) return msg
  }
  return fallback
}

export function resolveImageUrl(url: string | null): string | null {
  if (!url) return null
  if (/^(https?:|blob:|data:)/.test(url)) return url
  const origin = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '')
  return `${origin}${url.startsWith('/') ? '' : '/'}${url}`
}
