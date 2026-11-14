import api from '@/services/api'
import type { Paginated } from '@/types'

export interface AdminUser {
  id: number
  email: string
  full_name: string | null
  is_active: boolean
  is_admin: boolean
  created_at: string | null
}

export interface AdminStats {
  total_users: number
  active_users: number
  total_products: number
  total_sales: number
  total_revenue: number
}

export interface AdminUserUpdate {
  is_active?: boolean
  is_admin?: boolean
}

export interface AdminUserParams {
  page?: number
  page_size?: number
  q?: string
}

export const adminService = {
  async users(params: AdminUserParams = {}): Promise<Paginated<AdminUser>> {
    const { data } = await api.get<Paginated<AdminUser>>('/admin/users', { params })
    return data
  },
  async updateUser(id: number, payload: AdminUserUpdate): Promise<AdminUser> {
    const { data } = await api.put<AdminUser>(`/admin/users/${id}`, payload)
    return data
  },
  async stats(): Promise<AdminStats> {
    const { data } = await api.get<AdminStats>('/admin/stats')
    return data
  },
}
