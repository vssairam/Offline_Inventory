import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { saleService } from '@/services/saleService'
import { formatDateTime, formatMoney } from '@/lib/format'

const PAGE_SIZE = 20

export function SalesListPage() {
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [page, setPage] = useState(1)
  const { data, isLoading, isError } = useQuery({
    queryKey: ['sales', dateFrom, dateTo, page],
    queryFn: () =>
      saleService.list({
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        page,
        page_size: PAGE_SIZE,
      }),
  })
  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <h1 className="text-2xl font-semibold">Sales</h1>
        <Button asChild>
          <Link to="/sales/new">New sale</Link>
        </Button>
      </div>
      <div className="flex flex-wrap gap-2">
        <Input
          type="date"
          aria-label="From date"
          className="w-40"
          value={dateFrom}
          onChange={(e) => {
            setDateFrom(e.target.value)
            setPage(1)
          }}
        />
        <Input
          type="date"
          aria-label="To date"
          className="w-40"
          value={dateTo}
          onChange={(e) => {
            setDateTo(e.target.value)
            setPage(1)
          }}
        />
      </div>
      <Card>
        <CardContent className="p-0">
          {isLoading && <p className="p-4 text-sm text-muted-foreground">Loading...</p>}
          {isError && <p className="p-4 text-sm text-destructive">Failed to load sales.</p>}
          {data && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Total</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell>#{s.id}</TableCell>
                    <TableCell>{formatDateTime(s.sold_at)}</TableCell>
                    <TableCell className="text-right">{formatMoney(s.total_amount)}</TableCell>
                    <TableCell className="text-right">
                      <Link className="text-primary hover:underline" to={`/sales/${s.id}`}>
                        View
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
                {data.items.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center text-muted-foreground">
                      No sales found.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
      <div className="flex items-center justify-end gap-2 text-sm">
        <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          Previous
        </Button>
        <span>
          Page {page} of {totalPages}
        </span>
        <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
          Next
        </Button>
      </div>
    </div>
  )
}
