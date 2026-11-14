import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ProductForm } from '@/components/products/ProductForm'
import { apiErrorMessage, categoryService, productService, type ProductPayload } from '@/services/productService'

export function ProductCreatePage() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const categories = useQuery({ queryKey: ['categories'], queryFn: categoryService.list })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (payload: ProductPayload, image: File | null) => {
    setSubmitting(true)
    setError(null)
    try {
      const created = await productService.create(payload)
      void qc.invalidateQueries({ queryKey: ['products'] })
      if (image) {
        try {
          await productService.uploadImage(created.id, image)
        } catch {
          // Product exists; send the user to edit so they can retry the image.
          navigate(`/products/${created.id}/edit`)
          return
        }
      }
      navigate('/products')
    } catch (err) {
      setError(apiErrorMessage(err, 'Failed to create product'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">New product</h1>
      <ProductForm
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
