import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { reportService } from '@/services/reportService'
import { getApiErrorMessage } from '@/services/saleService'
import { formatMoney } from '@/lib/format'

export function ReportsPage() {
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [exporting, setExporting] = useState(false)
  const [exportError, setExportError] = useState<string | null>(null)
  const params = { date_from: dateFrom || undefined, date_to: dateTo || undefined }

  const { data, isLoading, isError } = useQuery({
    queryKey: ['reports', 'sales', dateFrom, dateTo],
    queryFn: () => reportService.sales(params),
  })

  async function handleExport() {
    setExporting(true)
    setExportError(null)
    try {
      await reportService.exportCsv(params)
    } catch (err) {
      setExportError(getApiErrorMessage(err, 'Export failed'))
    } finally {
      setExporting(false)
    }
  }

  const cards = data
    ? [
        { label: 'Sales', value: String(data.total_sales_count) },
        { label: 'Revenue', value: formatMoney(data.total_revenue) },
        { label: 'Cost', value: formatMoney(data.total_cost) },
        { label: 'Profit', value: formatMoney(data.total_profit) },
      ]
    : []

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <h1 className="text-2xl font-semibold">Reports</h1>
        <Button variant="outline" onClick={handleExport} disabled={exporting}>
          {exporting ? 'Exporting...' : 'Export CSV'}
        </Button>
      </div>
      <div className="flex flex-wrap gap-2">
        <Input type="date" aria-label="From date" className="w-40" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
        <Input type="date" aria-label="To date" className="w-40" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
      </div>
      {exportError && (
        <p role="alert" className="text-sm text-destructive">
          {exportError}
        </p>
      )}
      {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
      {isError && <p className="text-sm text-destructive">Failed to load report.</p>}
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
              <CardTitle>Daily revenue</CardTitle>
            </CardHeader>
            <CardContent className="h-72">
              {data.daily.length === 0 ? (
                <p className="text-sm text-muted-foreground">No data for this period.</p>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.daily}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(v) => formatMoney(Number(v))} />
                    <Bar dataKey="revenue" fill="#2563eb" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Top products</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Product</TableHead>
                    <TableHead className="text-right">Quantity</TableHead>
                    <TableHead className="text-right">Revenue</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.top_products.map((p) => (
                    <TableRow key={p.name}>
                      <TableCell>{p.name}</TableCell>
                      <TableCell className="text-right">{p.quantity}</TableCell>
                      <TableCell className="text-right">{formatMoney(p.revenue)}</TableCell>
                    </TableRow>
                  ))}
                  {data.top_products.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={3} className="text-center text-muted-foreground">
                        No sales in this period.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
