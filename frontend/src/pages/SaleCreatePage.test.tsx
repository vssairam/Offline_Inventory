import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'
import { SaleCreatePage } from '@/pages/SaleCreatePage'
import api from '@/services/api'

vi.mock('@/services/api', () => ({ default: { get: vi.fn(), post: vi.fn() } }))
const get = vi.mocked(api.get)
const post = vi.mocked(api.post)

const widget = {
  id: 1, name: 'Widget', sku: 'W1', price: 10, cost: 4, quantity: 5, reorder_level: 1,
  category_id: null, image_url: null, is_active: true, created_at: '2026-01-01T00:00:00Z',
}

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={['/sales/new']}>
        <Routes>
          <Route path="/sales/new" element={<SaleCreatePage />} />
          <Route path="/sales/:id" element={<div>sale detail</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

async function addWidget() {
  await userEvent.click(await screen.findByRole('button', { name: 'Add' }))
}

describe('SaleCreatePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    get.mockResolvedValue({ data: { items: [widget], total: 1, page: 1, page_size: 20 } })
  })

  it('disables submit until a valid line exists', async () => {
    renderPage()
    expect(screen.getByRole('button', { name: 'Record sale' })).toBeDisabled()
    await addWidget()
    expect(screen.getByRole('button', { name: 'Record sale' })).toBeEnabled()
    expect(screen.getByTestId('sale-total')).toHaveTextContent('10.00')
  })

  it('shows the server error message (insufficient stock)', async () => {
    post.mockRejectedValue({
      response: { data: { error: { message: 'Insufficient stock for Widget: available 1, requested 1' } } },
    })
    renderPage()
    await addWidget()
    await userEvent.click(screen.getByRole('button', { name: 'Record sale' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Insufficient stock for')
    expect(post).toHaveBeenCalledWith('/sales', { items: [{ product_id: 1, quantity: 1 }] })
  })

  it('falls back to a generic error', async () => {
    post.mockRejectedValue(new Error('network'))
    renderPage()
    await addWidget()
    await userEvent.click(screen.getByRole('button', { name: 'Record sale' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Failed to record sale')
  })

  it('navigates to the sale on success', async () => {
    post.mockResolvedValue({ data: { id: 42 } })
    renderPage()
    await addWidget()
    await userEvent.click(screen.getByRole('button', { name: 'Record sale' }))
    await waitFor(() => expect(screen.getByText('sale detail')).toBeInTheDocument())
  })
})
