import { useEffect, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { apiErrorMessage } from '@/services/productService'
import { stockService } from '@/services/stockService'
import { cn } from '@/lib/utils'

const PAGE_SIZE = 10

export function StockPage() {
  const [search, setSearch] = useState('')
  const [q, setQ] = useState('')
  const [lowStock, setLowStock] = useState(false)
  const [page, setPage] = useState(1)

  useEffect(() => {
    const t = setTimeout(() => {
      setQ(search)
      setPage(1)
    }, 300)
    return () => clearTimeout(t)
  }, [search])

  const params = { q, low_stock: lowStock, page, page_size: PAGE_SIZE }
  const stock = useQuery({
    queryKey: ['stock', params],
    queryFn: () => stockService.list(params),
    placeholderData: keepPreviousData,
  })

  const total = stock.data?.total ?? 0
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Stock</h1>

      <div className="flex flex-wrap items-center gap-3">
        <Input className="max-w-xs" placeholder="Search name or SKU" aria-label="Search stock" value={search} onChange={(e) => setSearch(e.target.value)} />
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={lowStock} onChange={(e) => { setLowStock(e.target.checked); setPage(1) }} />
          Low stock only
        </label>
      </div>

      <Card>
        <CardContent className="p-0">
          {stock.isLoading ? (
            <p className="p-6 text-sm text-muted-foreground">Loading stock...</p>
          ) : stock.isError ? (
            <p role="alert" className="p-6 text-sm text-destructive">{apiErrorMessage(stock.error, 'Failed to load stock')}</p>
          ) : stock.data && stock.data.items.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Product</TableHead>
                  <TableHead>SKU</TableHead>
                  <TableHead className="text-right">Quantity</TableHead>
                  <TableHead className="text-right">Reorder level</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {stock.data.items.map((s) => (
                  <TableRow key={s.id} data-low={s.is_low} className={cn(s.is_low && 'bg-destructive/10')}>
                    <TableCell className="font-medium">{s.name}</TableCell>
                    <TableCell>{s.sku}</TableCell>
                    <TableCell className={cn('text-right', s.is_low && 'font-semibold text-destructive')}>{s.quantity}</TableCell>
                    <TableCell className="text-right">{s.reorder_level}</TableCell>
                    <TableCell>{s.is_low ? <Badge variant="destructive">Low stock</Badge> : <Badge variant="secondary">OK</Badge>}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="p-6 text-sm text-muted-foreground">No stock records found.</p>
          )}
        </CardContent>
      </Card>

      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">{total} item{total === 1 ? '' : 's'}</span>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</Button>
          <span>Page {page} of {pages}</span>
          <Button variant="outline" size="sm" disabled={page >= pages} onClick={() => setPage((p) => p + 1)}>Next</Button>
        </div>
      </div>
    </div>
  )
}
