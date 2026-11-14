import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { tokenStore } from '@/services/api'
import { authService, type RegisterInput } from '@/services/authService'
import type { User } from '@/types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (input: RegisterInput) => Promise<void>
  updateProfile: (payload: { full_name: string }) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState<boolean>(() => tokenStore.getAccess() !== null)

  useEffect(() => {
    if (!tokenStore.getAccess()) return
    authService
      .me()
      .then(setUser)
      .catch(() => tokenStore.clear())
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const u = await authService.login(email, password)
    queryClient.clear() // never show a previous user's cached data
    setUser(u)
  }, [queryClient])

  const register = useCallback(async (input: RegisterInput) => {
    const u = await authService.register(input)
    queryClient.clear()
    setUser(u)
  }, [queryClient])

  const updateProfile = useCallback(async (payload: { full_name: string }) => {
    setUser(await authService.updateProfile(payload))
  }, [])

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } finally {
      queryClient.clear()
      setUser(null)
    }
  }, [queryClient])

  const value = useMemo(
    () => ({ user, loading, login, register, updateProfile, logout }),
    [user, loading, login, register, updateProfile, logout],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
