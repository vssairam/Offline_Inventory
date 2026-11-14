import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { vi } from 'vitest'
import { ProtectedRoute } from '@/components/layout/ProtectedRoute'
import { useAuth } from '@/context/AuthContext'

vi.mock('@/context/AuthContext', () => ({ useAuth: vi.fn() }))
const mockAuth = vi.mocked(useAuth)

function setAuth(user: { is_admin: boolean } | null, loading = false) {
  mockAuth.mockReturnValue({ user, loading } as unknown as ReturnType<typeof useAuth>)
}

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/login" element={<div>login page</div>} />
        <Route path="/dashboard" element={<div>dashboard page</div>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/products" element={<div>products page</div>} />
        </Route>
        <Route element={<ProtectedRoute adminOnly />}>
          <Route path="/admin" element={<div>admin page</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  it('shows a loading state while auth resolves', () => {
    setAuth(null, true)
    renderAt('/products')
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('redirects anonymous users to login', () => {
    setAuth(null)
    renderAt('/admin')
    expect(screen.getByText('login page')).toBeInTheDocument()
  })

  it('lets a regular user reach normal routes', () => {
    setAuth({ is_admin: false })
    renderAt('/products')
    expect(screen.getByText('products page')).toBeInTheDocument()
  })

  it('sends non-admin users away from admin routes', () => {
    setAuth({ is_admin: false })
    renderAt('/admin')
    expect(screen.getByText('dashboard page')).toBeInTheDocument()
    expect(screen.queryByText('admin page')).not.toBeInTheDocument()
  })

  it('lets admins into admin routes', () => {
    setAuth({ is_admin: true })
    renderAt('/admin')
    expect(screen.getByText('admin page')).toBeInTheDocument()
  })
})
