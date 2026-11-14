import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ProductTable } from '@/components/products/ProductTable'
import { apiErrorMessage, categoryService, productService } from '@/services/productService'
import type { Product } from '@/types'

const PAGE_SIZE = 10

export function ProductListPage() {
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [q, setQ] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [lowStock, setLowStock] = useState(false)
  const [page, setPage] = useState(1)
  const [toDelete, setToDelete] = useState<Product | null>(null)

  useEffect(() => {
    const t = setTimeout(() => {
      setQ(search)
      setPage(1)
    }, 300)
    return () => clearTimeout(t)
  }, [search])

  const params = { q, category_id: categoryId ? Number(categoryId) : undefined, low_stock: lowStock, page, page_size: PAGE_SIZE }
  const products = useQuery({
    queryKey: ['products', params],
    queryFn: () => productService.list(params),
    placeholderData: keepPreviousData,
  })
  const categories = useQuery({ queryKey: ['categories'], queryFn: categoryService.list })

  const del = useMutation({
    mutationFn: (id: number) => productService.remove(id),
    onSuccess: () => {
      setToDelete(null)
      void qc.invalidateQueries({ queryKey: ['products'] })
    },
  })

  const total = products.data?.total ?? 0
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Products</h1>
        <Button asChild><Link to="/products/new">Add product</Link></Button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Input className="max-w-xs" placeholder="Search name or SKU" aria-label="Search products" value={search} onChange={(e) => setSearch(e.target.value)} />
        <select
          aria-label="Filter by category"
          className="h-9 rounded-md border border-input bg-transparent px-3 text-sm"
          value={categoryId}
          onChange={(e) => { setCategoryId(e.target.value); setPage(1) }}
        >
          <option value="">All categories</option>
          {(categories.data ?? []).map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={lowStock} onChange={(e) => { setLowStock(e.target.checked); setPage(1) }} />
          Low stock only
        </label>
      </div>

      <Card>
        <CardContent className="p-0">
          {products.isLoading ? (
            <p className="p-6 text-sm text-muted-foreground">Loading products...</p>
          ) : products.isError ? (
            <p role="alert" className="p-6 text-sm text-destructive">{apiErrorMessage(products.error, 'Failed to load products')}</p>
          ) : products.data && products.data.items.length > 0 ? (
            <ProductTable products={products.data.items} categories={categories.data ?? []} onDelete={setToDelete} />
          ) : (
            <p className="p-6 text-sm text-muted-foreground">No products found.</p>
          )}
        </CardContent>
      </Card>

      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">{total} product{total === 1 ? '' : 's'}</span>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</Button>
          <span>Page {page} of {pages}</span>
          <Button variant="outline" size="sm" disabled={page >= pages} onClick={() => setPage((p) => p + 1)}>Next</Button>
        </div>
      </div>

      {toDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" role="dialog" aria-modal="true" aria-labelledby="del-title">
          <Card className="w-full max-w-sm">
            <CardContent className="flex flex-col gap-4 p-6">
              <h2 id="del-title" className="text-lg font-semibold">Delete product?</h2>
              <p className="text-sm text-muted-foreground">
                "{toDelete.name}" will be removed. This cannot be undone.
              </p>
              {del.isError && <p role="alert" className="text-sm text-destructive">{apiErrorMessage(del.error, 'Delete failed')}</p>}
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => { setToDelete(null); del.reset() }}>Cancel</Button>
                <Button variant="destructive" disabled={del.isPending} onClick={() => del.mutate(toDelete.id)}>
                  {del.isPending ? 'Deleting...' : 'Delete'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
