import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'
import { ProductListPage } from '@/pages/ProductListPage'
import api from '@/services/api'

vi.mock('@/services/api', () => ({ default: { get: vi.fn(), delete: vi.fn() } }))
const get = vi.mocked(api.get)
const del = vi.mocked(api.delete)

const product = (id: number, name: string, quantity: number, reorder_level = 5) => ({
  id, name, sku: `SKU${id}`, price: 10, cost: 4, quantity, reorder_level,
  category_id: null, image_url: null, is_active: true, created_at: '2026-01-01T00:00:00Z',
})

function mockApi(items: ReturnType<typeof product>[]) {
  get.mockImplementation(async (url: string) => {
    if (url === '/categories') return { data: [{ id: 1, name: 'Tools' }] }
    return { data: { items, total: items.length, page: 1, page_size: 10 } }
  })
}

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter><ProductListPage /></MemoryRouter>
    </QueryClientProvider>,
  )
}

const productCalls = () => get.mock.calls.filter(([u]) => u === '/products')

describe('ProductListPage', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders products and flags low stock', async () => {
    mockApi([product(1, 'Widget', 2), product(2, 'Gadget', 50)])
    renderPage()
    expect(await screen.findByText('Widget')).toBeInTheDocument()
    expect(screen.getByText('Gadget')).toBeInTheDocument()
    expect(screen.getAllByText('Low stock')).toHaveLength(1)
    expect(screen.getByText('2 products')).toBeInTheDocument()
  })

  it('shows empty state', async () => {
    mockApi([])
    renderPage()
    expect(await screen.findByText('No products found.')).toBeInTheDocument()
  })

  it('shows an error message when loading fails', async () => {
    get.mockImplementation(async (url: string) => {
      if (url === '/categories') return { data: [] }
      throw new Error('boom')
    })
    renderPage()
    expect(await screen.findByRole('alert')).toHaveTextContent('Failed to load products')
  })

  it('debounces search and sends the filters', async () => {
    mockApi([product(1, 'Widget', 2)])
    renderPage()
    await screen.findByText('Widget')
    await userEvent.type(screen.getByLabelText('Search products'), 'wid')
    await waitFor(() =>
      expect(productCalls().at(-1)?.[1]).toEqual({ params: { q: 'wid', page: 1, page_size: 10 } }),
    )
    await userEvent.click(screen.getByLabelText(/low stock only/i))
    await waitFor(() =>
      expect(productCalls().at(-1)?.[1]).toEqual({
        params: { q: 'wid', low_stock: true, page: 1, page_size: 10 },
      }),
    )
    await userEvent.selectOptions(screen.getByLabelText('Filter by category'), '1')
    await waitFor(() =>
      expect((productCalls().at(-1)?.[1] as { params: Record<string, unknown> }).params.category_id).toBe(1),
    )
  })

  it('confirms and deletes a product', async () => {
    mockApi([product(1, 'Widget', 20)])
    del.mockResolvedValue({ data: {} })
    renderPage()
    await userEvent.click(await screen.findByRole('button', { name: 'Delete Widget' }))
    expect(screen.getByRole('dialog')).toHaveTextContent('Widget')
    await userEvent.click(screen.getByRole('button', { name: 'Delete' }))
    await waitFor(() => expect(del).toHaveBeenCalledWith('/products/1'))
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('cancel closes the dialog without deleting; failures are shown', async () => {
    mockApi([product(1, 'Widget', 20)])
    renderPage()
    await userEvent.click(await screen.findByRole('button', { name: 'Delete Widget' }))
    await userEvent.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(del).not.toHaveBeenCalled()

    del.mockRejectedValue(new Error('nope'))
    await userEvent.click(screen.getByRole('button', { name: 'Delete Widget' }))
    await userEvent.click(screen.getByRole('button', { name: 'Delete' }))
    expect(await screen.findByText('Delete failed')).toBeInTheDocument()
  })
})
