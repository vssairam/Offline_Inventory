import axios from 'axios'
import api, { tokenStore } from '@/services/api'
import type { TokenPair, User } from '@/types'

export interface RegisterInput {
  email: string
  password: string
  full_name: string
}

/** Extracts a human-readable message from the backend error envelope. */
export function getApiErrorMessage(error: unknown, fallback = 'Something went wrong. Please try again.'): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { error?: { message?: string }; detail?: unknown } | undefined
    if (data?.error?.message) return data.error.message
    if (typeof data?.detail === 'string') return data.detail
    if (!error.response) return 'Unable to reach the server. Check your connection.'
  }
  return fallback
}

export const authService = {
  async login(email: string, password: string): Promise<User> {
    const { data } = await api.post<TokenPair & { user?: User }>('/auth/login', { email, password })
    tokenStore.set(data.access_token, data.refresh_token)
    if (data.user) return data.user
    return authService.me()
  },
  async register(input: RegisterInput): Promise<User> {
    await api.post('/auth/register', input)
    return authService.login(input.email, input.password)
  },
  async me(): Promise<User> {
    const { data } = await api.get<User>('/auth/me')
    return data
  },
  async updateProfile(payload: { full_name: string }): Promise<User> {
    const { data } = await api.put<User>('/auth/me', payload)
    return data
  },
  async logout(): Promise<void> {
    const refresh = tokenStore.getRefresh()
    try {
      if (refresh) await api.post('/auth/logout', { refresh_token: refresh })
    } catch {
      // local logout proceeds regardless
    }
    tokenStore.clear()
  },
}
