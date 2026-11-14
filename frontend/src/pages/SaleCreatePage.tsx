import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { SaleForm } from '@/components/sales/SaleForm'
import { getApiErrorMessage, saleService } from '@/services/saleService'

export function SaleCreatePage() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [error, setError] = useState<string | null>(null)
  const mutation = useMutation({
    mutationFn: saleService.create,
    onSuccess: (sale) => {
      void qc.invalidateQueries({ queryKey: ['sales'] })
      void qc.invalidateQueries({ queryKey: ['products'] })
      void qc.invalidateQueries({ queryKey: ['reports'] })
      navigate(`/sales/${sale.id}`)
    },
    onError: (err) => setError(getApiErrorMessage(err, 'Failed to record sale')),
  })

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">New sale</h1>
      <SaleForm
        submitting={mutation.isPending}
        serverError={error}
        onSubmit={(items) => {
          setError(null)
          mutation.mutate({ items })
        }}
      />
    </div>
  )
}
