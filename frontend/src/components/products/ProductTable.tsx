import { Link } from 'react-router-dom'
import { Pencil, Trash2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { isLowStock, resolveImageUrl } from '@/services/productService'
import type { Category, Product } from '@/types'

interface Props {
  products: Product[]
  categories: Category[]
  onDelete: (product: Product) => void
}

const money = new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' })

export function ProductTable({ products, categories, onDelete }: Props) {
  const catName = (id: number | null) => categories.find((c) => c.id === id)?.name ?? '-'
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Product</TableHead>
          <TableHead>SKU</TableHead>
          <TableHead>Category</TableHead>
          <TableHead className="text-right">Price</TableHead>
          <TableHead className="text-right">Stock</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {products.map((p) => {
          const img = resolveImageUrl(p.image_url)
          return (
            <TableRow key={p.id}>
              <TableCell>
                <div className="flex items-center gap-3">
                  {img ? (
                    <img src={img} alt="" className="h-10 w-10 rounded object-cover" />
                  ) : (
                    <div className="h-10 w-10 rounded bg-muted" />
                  )}
                  <span className="font-medium">{p.name}</span>
                  {!p.is_active && <Badge variant="outline">Inactive</Badge>}
                </div>
              </TableCell>
              <TableCell>{p.sku}</TableCell>
              <TableCell>{catName(p.category_id)}</TableCell>
              <TableCell className="text-right">{money.format(p.price)}</TableCell>
              <TableCell className="text-right">
                <span className="mr-2">{p.quantity}</span>
                {isLowStock(p) && <Badge variant="destructive">Low stock</Badge>}
              </TableCell>
              <TableCell className="text-right">
                <Button asChild variant="ghost" size="icon" aria-label={`Edit ${p.name}`}>
                  <Link to={`/products/${p.id}/edit`}><Pencil className="h-4 w-4" /></Link>
                </Button>
                <Button variant="ghost" size="icon" aria-label={`Delete ${p.name}`} onClick={() => onDelete(p)}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </TableCell>
            </TableRow>
          )
        })}
      </TableBody>
    </Table>
  )
}
