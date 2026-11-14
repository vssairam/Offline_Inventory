import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'
import { DashboardPage } from './DashboardPage'
import { AdminUsersPage } from './AdminUsersPage'
import { AdminDashboardPage } from './AdminDashboardPage'

vi.mock('@/services/dashboardService', () => ({
  dashboardService: {
    summary: vi.fn().mockResolvedValue({
      total_products: 12,
      low_stock_count: 1,
      total_stock_value: 500,
      sales_today_count: 3,
      sales_today_revenue: 90,
      revenue_30d: 1000,
      profit_30d: 400,
      trend: [],
      low_stock_items: [{ id: 1, name: 'Widget', sku: 'W1', quantity: 2, reorder_level: 5, deficit: 3 }],
    }),
  },
}))

const updateUser = vi.fn().mockResolvedValue({})
vi.mock('@/services/adminService', () => ({
  adminService: {
    stats: vi.fn().mockResolvedValue({
      total_users: 7,
      active_users: 6,
      total_products: 20,
      total_sales: 30,
      total_revenue: 1234,
    }),
    users: vi.fn().mockResolvedValue({
      items: [
        { id: 1, email: 'me@x.com', full_name: 'Me', is_active: true, is_admin: true, created_at: null },
        { id: 2, email: 'bob@x.com', full_name: 'Bob', is_active: true, is_admin: false, created_at: null },
      ],
      total: 2,
      page: 1,
      page_size: 20,
    }),
    updateUser: (...args: unknown[]) => updateUser(...args),
  },
}))

vi.mock('@/context/AuthContext', () => ({
  useAuth: () => ({ user: { id: 1, email: 'me@x.com', is_admin: true } }),
}))

function wrap(ui: React.ReactNode) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('DashboardPage', () => {
  it('shows stats and low-stock items', async () => {
    wrap(<DashboardPage />)
    expect(await screen.findByText('Widget')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Widget' })).toHaveAttribute('href', '/stock')
  })
})

describe('AdminDashboardPage', () => {
  it('shows platform stats', async () => {
    wrap(<AdminDashboardPage />)
    expect(await screen.findByText('Total users')).toBeInTheDocument()
    expect(screen.getByText('7')).toBeInTheDocument()
  })
})

describe('AdminUsersPage', () => {
  it('disables own row actions and confirms before updating another user', async () => {
    wrap(<AdminUsersPage />)
    await screen.findByText('bob@x.com')
    const deactivate = screen.getAllByRole('button', { name: 'Deactivate' })
    expect(deactivate[0]).toBeDisabled()
    expect(deactivate[1]).toBeEnabled()
    await userEvent.click(deactivate[1])
    expect(screen.getByRole('dialog')).toHaveTextContent('Deactivate bob@x.com?')
    await userEvent.click(screen.getByRole('button', { name: 'Confirm' }))
    await waitFor(() => expect(updateUser).toHaveBeenCalledWith(2, { is_active: false }))
  })
})
