import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ProductForm } from '@/components/products/ProductForm'
import { apiErrorMessage, categoryService, productService, type ProductPayload } from '@/services/productService'

export function ProductEditPage() {
  const { id } = useParams()
  const productId = Number(id)
  const navigate = useNavigate()
  const qc = useQueryClient()
  const product = useQuery({
    queryKey: ['product', productId],
    queryFn: () => productService.get(productId),
    enabled: Number.isFinite(productId),
  })
  const categories = useQuery({ queryKey: ['categories'], queryFn: categoryService.list })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (payload: ProductPayload, image: File | null) => {
    setSubmitting(true)
    setError(null)
    try {
      await productService.update(productId, payload)
      if (image) await productService.uploadImage(productId, image)
      void qc.invalidateQueries({ queryKey: ['products'] })
      void qc.invalidateQueries({ queryKey: ['product', productId] })
      navigate('/products')
    } catch (err) {
      setError(apiErrorMessage(err, 'Failed to save product'))
    } finally {
      setSubmitting(false)
    }
  }

  if (product.isLoading) return <p className="text-sm text-muted-foreground">Loading product...</p>
  if (product.isError || !product.data)
    return <p role="alert" className="text-sm text-destructive">{apiErrorMessage(product.error, 'Product not found')}</p>

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Edit product</h1>
      <ProductForm
        product={product.data}
        categories={categories.data ?? []}
        submitting={submitting}
        serverError={error}
        onSubmit={onSubmit}
        onCreateCategory={async (name) => {
          const c = await categoryService.create(name)
          void qc.invalidateQueries({ queryKey: ['categories'] })
          return c
        }}
        onCancel={() => navigate('/products')}
      />
    </div>
  )
}
