import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'
import { StockPage } from '@/pages/StockPage'
import { AlertsBell } from '@/components/alerts/AlertsBell'
import api from '@/services/api'

vi.mock('@/services/api', () => ({ default: { get: vi.fn(), put: vi.fn() } }))
const get = vi.mocked(api.get)
const put = vi.mocked(api.put)

function wrap(ui: React.ReactNode) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('StockPage', () => {
  it('renders rows and highlights low stock', async () => {
    get.mockResolvedValue({
      data: {
        items: [
          { id: 1, name: 'Widget', sku: 'W1', quantity: 2, reorder_level: 5, is_low: true },
          { id: 2, name: 'Gadget', sku: 'G1', quantity: 50, reorder_level: 5, is_low: false },
        ],
        total: 2, page: 1, page_size: 10,
      },
    })
    wrap(<StockPage />)
    const row = (await screen.findByText('Widget')).closest('tr')!
    expect(row).toHaveAttribute('data-low', 'true')
    expect(screen.getByText('Gadget').closest('tr')).toHaveAttribute('data-low', 'false')
    expect(screen.getByText('Low stock')).toBeInTheDocument()
  })

  it('sends low_stock filter', async () => {
    get.mockResolvedValue({ data: { items: [], total: 0, page: 1, page_size: 10 } })
    wrap(<StockPage />)
    await userEvent.click(screen.getByLabelText(/low stock only/i))
    await waitFor(() =>
      expect(get).toHaveBeenLastCalledWith('/stock', { params: { low_stock: true, page: 1, page_size: 10 } }),
    )
  })
})

describe('AlertsBell', () => {
  it('shows unread count and marks alert read', async () => {
    const alert = { id: 7, user_id: 1, product_id: 1, type: 'low_stock', message: 'Widget is low', is_read: false, email_sent: false, created_at: '2026-01-01T00:00:00Z' }
    get.mockResolvedValue({ data: { items: [alert], total: 1, page: 1, page_size: 5, unread_count: 3 } })
    put.mockResolvedValue({ data: { ...alert, is_read: true } })
    wrap(<AlertsBell enabled />)
    const bell = await screen.findByRole('button', { name: /3 unread/i })
    await userEvent.click(bell)
    expect(await screen.findByText('Widget is low')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /mark alert 7 as read/i }))
    await waitFor(() => expect(put).toHaveBeenCalledWith('/alerts/7/read'))
  })
})
