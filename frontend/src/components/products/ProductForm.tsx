import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ImageUpload } from '@/components/products/ImageUpload'
import { apiErrorMessage, type ProductPayload } from '@/services/productService'
import type { Category, Product } from '@/types'

export interface ProductFormProps {
  product?: Product
  categories: Category[]
  submitting?: boolean
  serverError?: string | null
  onSubmit: (payload: ProductPayload, image: File | null) => void | Promise<void>
  onCreateCategory: (name: string) => Promise<Category>
  onCancel?: () => void
}

type Errors = Partial<Record<'name' | 'sku' | 'price' | 'cost' | 'quantity' | 'reorder_level', string>>

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring'

export function validateProduct(v: {
  name: string
  sku: string
  price: string
  cost: string
  quantity: string
  reorder_level: string
}): Errors {
  const e: Errors = {}
  if (!v.name.trim()) e.name = 'Name is required'
  if (!v.sku.trim()) e.sku = 'SKU is required'
  const num = (s: string) => (s.trim() === '' ? NaN : Number(s))
  if (!(num(v.price) >= 0)) e.price = 'Price must be 0 or more'
  if (!(num(v.cost) >= 0)) e.cost = 'Cost must be 0 or more'
  if (!Number.isInteger(num(v.quantity)) || num(v.quantity) < 0) e.quantity = 'Quantity must be a whole number, 0 or more'
  if (!Number.isInteger(num(v.reorder_level)) || num(v.reorder_level) < 0)
    e.reorder_level = 'Reorder level must be a whole number, 0 or more'
  return e
}

export function ProductForm({ product, categories, submitting, serverError, onSubmit, onCreateCategory, onCancel }: ProductFormProps) {
  const [name, setName] = useState(product?.name ?? '')
  const [sku, setSku] = useState(product?.sku ?? '')
  const [categoryId, setCategoryId] = useState<string>(product?.category_id != null ? String(product.category_id) : '')
  const [price, setPrice] = useState(product ? String(product.price) : '')
  const [cost, setCost] = useState(product ? String(product.cost) : '')
  const [quantity, setQuantity] = useState(product ? String(product.quantity) : '0')
  const [reorder, setReorder] = useState(product ? String(product.reorder_level) : '0')
  const [isActive, setIsActive] = useState(product?.is_active ?? true)
  const [image, setImage] = useState<File | null>(null)
  const [errors, setErrors] = useState<Errors>({})
  const [newCategory, setNewCategory] = useState<string | null>(null)
  const [catError, setCatError] = useState<string | null>(null)
  const [extraCats, setExtraCats] = useState<Category[]>([])

  const allCategories = [...categories, ...extraCats.filter((c) => !categories.some((x) => x.id === c.id))]

  const handleSubmit = (ev: FormEvent) => {
    ev.preventDefault()
    const errs = validateProduct({ name, sku, price, cost, quantity, reorder_level: reorder })
    setErrors(errs)
    if (Object.keys(errs).length) return
    void onSubmit(
      {
        name: name.trim(),
        sku: sku.trim(),
        category_id: categoryId ? Number(categoryId) : null,
        price: Number(price),
        cost: Number(cost),
        quantity: Number(quantity),
        reorder_level: Number(reorder),
        is_active: isActive,
      },
      image,
    )
  }

  const addCategory = async () => {
    const n = (newCategory ?? '').trim()
    if (!n) return setCatError('Category name is required')
    try {
      const created = await onCreateCategory(n)
      setExtraCats((c) => [...c, created])
      setCategoryId(String(created.id))
      setNewCategory(null)
      setCatError(null)
    } catch (err) {
      setCatError(apiErrorMessage(err, 'Could not create category'))
    }
  }

  const field = (id: keyof Errors, label: string, value: string, set: (v: string) => void, extra: Record<string, string> = {}) => (
    <div className="flex flex-col gap-2">
      <Label htmlFor={id}>{label}</Label>
      <Input id={id} value={value} onChange={(e) => set(e.target.value)} aria-invalid={!!errors[id]} {...extra} />
      {errors[id] && <p role="alert" className="text-sm text-destructive">{errors[id]}</p>}
    </div>
  )

  return (
    <form onSubmit={handleSubmit} noValidate className="flex max-w-2xl flex-col gap-4">
      <div className="grid gap-4 sm:grid-cols-2">
        {field('name', 'Name', name, setName)}
        {field('sku', 'SKU', sku, setSku)}
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="category">Category</Label>
        <div className="flex gap-2">
          <select id="category" className={selectClass} value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
            <option value="">No category</option>
            {allCategories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <Button type="button" variant="outline" onClick={() => setNewCategory(newCategory === null ? '' : null)}>
            New
          </Button>
        </div>
        {newCategory !== null && (
          <div className="flex gap-2">
            <Input aria-label="New category name" placeholder="Category name" value={newCategory} onChange={(e) => setNewCategory(e.target.value)} />
            <Button type="button" onClick={() => void addCategory()}>Add</Button>
          </div>
        )}
        {catError && <p role="alert" className="text-sm text-destructive">{catError}</p>}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {field('price', 'Price', price, setPrice, { type: 'number', step: '0.01', min: '0' })}
        {field('cost', 'Cost', cost, setCost, { type: 'number', step: '0.01', min: '0' })}
        {field('quantity', 'Quantity', quantity, setQuantity, { type: 'number', step: '1', min: '0' })}
        {field('reorder_level', 'Reorder level', reorder, setReorder, { type: 'number', step: '1', min: '0' })}
      </div>

      <div className="flex flex-col gap-2">
        <Label>Image</Label>
        <ImageUpload currentUrl={product?.image_url} file={image} onChange={setImage} />
      </div>

      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
        Active
      </label>

      {serverError && <p role="alert" className="text-sm text-destructive">{serverError}</p>}

      <div className="flex gap-2">
        <Button type="submit" disabled={submitting}>{submitting ? 'Saving...' : product ? 'Save changes' : 'Create product'}</Button>
        {onCancel && <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>}
      </div>
    </form>
  )
}
