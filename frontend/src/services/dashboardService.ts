import api from '@/services/api'

export interface TrendPoint {
  date: string
  revenue: number
}

export interface LowStockItem {
  id: number
  name: string
  sku: string
  quantity: number
  reorder_level: number
  deficit: number
}

export interface DashboardSummary {
  total_products: number
  low_stock_count: number
  total_stock_value: number
  sales_today_count: number
  sales_today_revenue: number
  revenue_30d: number
  profit_30d: number
  trend: TrendPoint[]
  low_stock_items: LowStockItem[]
}

export const dashboardService = {
  async summary(): Promise<DashboardSummary> {
    const { data } = await api.get<DashboardSummary>('/dashboard/summary')
    return data
  },
}
