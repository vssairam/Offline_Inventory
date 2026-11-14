import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import { AuthProvider } from './context/AuthContext'

describe('App', () => {
  it('redirects unauthenticated users to login', () => {
    localStorage.clear()
    render(
      <QueryClientProvider client={new QueryClient()}>
        <MemoryRouter initialEntries={['/products']}>
          <AuthProvider>
            <App />
          </AuthProvider>
        </MemoryRouter>
      </QueryClientProvider>,
    )
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })
})
