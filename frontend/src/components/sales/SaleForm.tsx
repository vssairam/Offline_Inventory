import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { saleService } from '@/services/saleService'
import { formatMoney } from '@/lib/format'
import {
  addLine,
  isSaleValid,
  lineError,
  lineTotal,
  removeLine,
  saleTotal,
  updateQuantity,
  type SaleLine,
} from '@/lib/saleLines'

interface Props {
  onSubmit: (items: { product_id: number; quantity: number }[]) => void
  submitting?: boolean
  serverError?: string | null
}

export function SaleForm({ onSubmit, submitting, serverError }: Props) {
  const [search, setSearch] = useState('')
  const [lines, setLines] = useState<SaleLine[]>([])
  const { data: products = [], isFetching } = useQuery({
    queryKey: ['products', 'sale-search', search],
    queryFn: () => saleService.searchProducts(search),
  })

  const valid = isSaleValid(lines)

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Products</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input
            placeholder="Search products by name or SKU"
            aria-label="Search products"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {isFetching && <p className="text-sm text-muted-foreground">Searching...</p>}
          <ul className="divide-y rounded-md border">
            {products.map((p) => (
              <li key={p.id} className="flex items-center justify-between gap-2 p-2 text-sm">
                <div>
                  <div className="font-medium">{p.name}</div>
                  <div className="text-muted-foreground">
                    {p.sku} · {formatMoney(p.price)} · {p.quantity} in stock
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={p.quantity < 1}
                  onClick={() => setLines((ls) => addLine(ls, p))}
                >
                  {p.quantity < 1 ? 'Out of stock' : 'Add'}
                </Button>
              </li>
            ))}
            {!isFetching && products.length === 0 && (
              <li className="p-2 text-sm text-muted-foreground">No products found.</li>
            )}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Sale items</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {lines.length === 0 ? (
            <p className="text-sm text-muted-foreground">Add products to start a sale.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Product</TableHead>
                  <TableHead className="w-28">Qty</TableHead>
                  <TableHead className="text-right">Total</TableHead>
                  <TableHead className="w-10" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {lines.map((l) => {
                  const err = lineError(l)
                  return (
                    <TableRow key={l.product.id}>
                      <TableCell>
                        {l.product.name}
                        {err && <div className="text-xs text-destructive">{err}</div>}
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          min={1}
                          max={l.product.quantity}
                          aria-label={`Quantity for ${l.product.name}`}
                          value={Number.isNaN(l.quantity) ? '' : l.quantity}
                          onChange={(e) =>
                            setLines((ls) => updateQuantity(ls, l.product.id, e.target.valueAsNumber))
                          }
                        />
                      </TableCell>
                      <TableCell className="text-right">
                        {formatMoney(Number.isNaN(l.quantity) ? 0 : lineTotal(l))}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="icon"
                          variant="ghost"
                          aria-label={`Remove ${l.product.name}`}
                          onClick={() => setLines((ls) => removeLine(ls, l.product.id))}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          )}
          <div className="flex items-center justify-between border-t pt-3 text-lg font-semibold">
            <span>Total</span>
            <span data-testid="sale-total">{formatMoney(valid ? saleTotal(lines) : 0)}</span>
          </div>
          {serverError && (
            <p role="alert" className="text-sm text-destructive">
              {serverError}
            </p>
          )}
          <Button
            className="w-full"
            disabled={!valid || submitting}
            onClick={() => onSubmit(lines.map((l) => ({ product_id: l.product.id, quantity: l.quantity })))}
          >
            {submitting ? 'Recording...' : 'Record sale'}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
