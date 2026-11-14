import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { saleService } from '@/services/saleService'
import { formatDateTime, formatMoney } from '@/lib/format'

export function SaleDetailPage() {
  const { id } = useParams()
  const saleId = Number(id)
  const { data: sale, isLoading, isError } = useQuery({
    queryKey: ['sales', 'detail', saleId],
    queryFn: () => saleService.get(saleId),
    enabled: Number.isFinite(saleId),
  })

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading...</p>
  if (isError || !sale) return <p className="text-sm text-destructive">Sale not found.</p>

  return (
    <div className="space-y-4">
      <Link to="/sales" className="text-sm text-primary hover:underline">
        Back to sales
      </Link>
      <Card>
        <CardHeader>
          <CardTitle>Sale #{sale.id}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">{formatDateTime(sale.sold_at)}</p>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product ID</TableHead>
                <TableHead className="text-right">Qty</TableHead>
                <TableHead className="text-right">Unit price</TableHead>
                <TableHead className="text-right">Line total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(sale.items ?? []).map((it) => (
                <TableRow key={it.id}>
                  <TableCell>{it.product_name ?? `#${it.product_id}`}</TableCell>
                  <TableCell className="text-right">{it.quantity}</TableCell>
                  <TableCell className="text-right">{formatMoney(it.unit_price)}</TableCell>
                  <TableCell className="text-right">{formatMoney(it.unit_price * it.quantity)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <div className="flex justify-between border-t pt-3 text-lg font-semibold">
            <span>Total</span>
            <span>{formatMoney(sale.total_amount)}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
