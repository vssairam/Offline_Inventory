export interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  is_verified: boolean
  is_admin: boolean
  created_at: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Category {
  id: number
  user_id: number
  name: string
  created_at: string
}

export interface Product {
  id: number
  user_id: number
  category_id: number | null
  name: string
  sku: string
  price: number
  cost: number
  quantity: number
  reorder_level: number
  image_url: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SaleItem {
  id: number
  sale_id: number
  product_id: number
  product_name?: string | null
  line_total?: number
  quantity: number
  unit_price: number
  unit_cost: number
}

export interface Sale {
  id: number
  user_id: number
  total_amount: number
  sold_at: string
  created_at: string
  items?: SaleItem[]
}

export type AlertType = 'low_stock'

export interface Alert {
  id: number
  user_id: number
  product_id: number
  type: AlertType
  message: string
  is_read: boolean
  email_sent: boolean
  created_at: string
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
