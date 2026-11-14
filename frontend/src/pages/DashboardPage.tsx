import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { dashboardService } from '@/services/dashboardService'
import { formatMoney } from '@/lib/format'

export function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: dashboardService.summary,
  })

  const cards = data
    ? [
        { label: 'Products', value: String(data.total_products) },
        { label: 'Low stock', value: String(data.low_stock_count) },
        { label: 'Stock value', value: formatMoney(data.total_stock_value) },
        { label: 'Sales today', value: String(data.sales_today_count) },
        { label: 'Revenue today', value: formatMoney(data.sales_today_revenue) },
        { label: 'Revenue (30d)', value: formatMoney(data.revenue_30d) },
        { label: 'Profit (30d)', value: formatMoney(data.profit_30d) },
      ]
    : []

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
      {isError && <p className="text-sm text-destructive">Failed to load dashboard.</p>}
      {data && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {cards.map((c) => (
              <Card key={c.label}>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground">{c.label}</CardTitle>
                </CardHeader>
                <CardContent className="text-2xl font-semibold">{c.value}</CardContent>
              </Card>
            ))}
          </div>
          <Card>
            <CardHeader>
              <CardTitle>Revenue, last 30 days</CardTitle>
            </CardHeader>
            <CardContent className="h-72">
              {data.trend.length === 0 ? (
                <p className="text-sm text-muted-foreground">No sales yet.</p>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data.trend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(v) => formatMoney(Number(v))} />
                    <Area type="monotone" dataKey="revenue" stroke="#2563eb" fill="#2563eb" fillOpacity={0.2} />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Low stock</CardTitle>
            </CardHeader>
            <CardContent>
              {data.low_stock_items.length === 0 ? (
                <p className="text-sm text-muted-foreground">All products are well stocked.</p>
              ) : (
                <ul className="divide-y text-sm">
                  {data.low_stock_items.map((i) => (
                    <li key={i.id} className="flex items-center justify-between py-2">
                      <Link to="/stock" className="font-medium hover:underline">
                        {i.name}
                      </Link>
                      <span className="text-muted-foreground">
                        {i.quantity} left (reorder at {i.reorder_level})
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
