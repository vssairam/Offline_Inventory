import api from '@/services/api'

export interface TopProduct {
  name: string
  quantity: number
  revenue: number
}

export interface DailyPoint {
  date: string
  revenue?: number
  profit?: number
  sales_count?: number
  [key: string]: unknown
}

export interface SalesReport {
  total_sales_count: number
  total_revenue: number
  total_cost: number
  total_profit: number
  top_products: TopProduct[]
  daily: DailyPoint[]
}

export interface ReportParams {
  date_from?: string
  date_to?: string
}

export const reportService = {
  async sales(params: ReportParams = {}): Promise<SalesReport> {
    const { data } = await api.get<SalesReport>('/reports/sales', { params })
    return data
  },
  async exportCsv(params: ReportParams = {}): Promise<void> {
    const res = await api.get<Blob>('/reports/sales/export', { params, responseType: 'blob' })
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'sales-report.csv'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  },
}
