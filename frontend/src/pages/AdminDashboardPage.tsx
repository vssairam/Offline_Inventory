import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { adminService } from '@/services/adminService'
import { formatMoney } from '@/lib/format'

export function AdminDashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: adminService.stats,
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Admin dashboard</h1>
        <Link to="/admin/users" className="text-sm font-medium hover:underline">
          Manage users
        </Link>
      </div>
      {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
      {isError && <p className="text-sm text-destructive">Failed to load stats.</p>}
      {data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {[
            { label: 'Total users', value: String(data.total_users) },
            { label: 'Active users', value: String(data.active_users) },
            { label: 'Total products', value: String(data.total_products) },
            { label: 'Total sales', value: String(data.total_sales) },
            { label: 'Total revenue', value: formatMoney(data.total_revenue) },
          ].map((c) => (
            <Card key={c.label}>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">{c.label}</CardTitle>
              </CardHeader>
              <CardContent className="text-2xl font-semibold">{c.value}</CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
