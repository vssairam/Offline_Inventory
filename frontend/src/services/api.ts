import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { TokenPair } from '@/types'

const ACCESS_KEY = 'access_token'
const REFRESH_KEY = 'refresh_token'

const baseURL = `${(import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '')}/api/v1`

export const tokenStore = {
  getAccess: (): string | null => localStorage.getItem(ACCESS_KEY),
  getRefresh: (): string | null => localStorage.getItem(REFRESH_KEY),
  set: (access: string, refresh?: string): void => {
    localStorage.setItem(ACCESS_KEY, access)
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear: (): void => {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

export const api = axios.create({ baseURL, headers: { 'Content-Type': 'application/json' } })

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStore.getAccess()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

type RetryableConfig = InternalAxiosRequestConfig & { _retry?: boolean }

let refreshPromise: Promise<string> | null = null

async function refreshAccessToken(): Promise<string> {
  const refresh = tokenStore.getRefresh()
  if (!refresh) throw new Error('No refresh token')
  // Bare axios call so this request skips our interceptors.
  const { data } = await axios.post<TokenPair>(`${baseURL}/auth/refresh`, { refresh_token: refresh })
  tokenStore.set(data.access_token, data.refresh_token)
  return data.access_token
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryableConfig | undefined
    const isAuthCall = original?.url?.includes('/auth/login') || original?.url?.includes('/auth/refresh')
    if (error.response?.status === 401 && original && !original._retry && !isAuthCall) {
      original._retry = true
      try {
        refreshPromise ??= refreshAccessToken().finally(() => {
          refreshPromise = null
        })
        const token = await refreshPromise
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      } catch {
        tokenStore.clear()
        if (window.location.pathname !== '/login') window.location.assign('/login')
      }
    }
    return Promise.reject(error)
  },
)

export default api
