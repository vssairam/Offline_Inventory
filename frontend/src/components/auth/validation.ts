const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function validateEmail(email: string): string | null {
  if (!email.trim()) return 'Email is required'
  if (!EMAIL_RE.test(email.trim())) return 'Enter a valid email address'
  return null
}

export function validatePassword(password: string): string | null {
  if (!password) return 'Password is required'
  if (password.length < 8) return 'Password must be at least 8 characters'
  return null
}

export interface LoginErrors {
  email?: string
  password?: string
}

export function validateLogin(v: { email: string; password: string }): LoginErrors {
  const errors: LoginErrors = {}
  const e = validateEmail(v.email)
  if (e) errors.email = e
  if (!v.password) errors.password = 'Password is required'
  return errors
}

export interface RegisterErrors extends LoginErrors {
  full_name?: string
  confirmPassword?: string
}

export function validateRegister(v: {
  full_name: string
  email: string
  password: string
  confirmPassword: string
}): RegisterErrors {
  const errors: RegisterErrors = {}
  if (!v.full_name.trim()) errors.full_name = 'Full name is required'
  const e = validateEmail(v.email)
  if (e) errors.email = e
  const p = validatePassword(v.password)
  if (p) errors.password = p
  if (!errors.password && v.confirmPassword !== v.password) errors.confirmPassword = 'Passwords do not match'
  return errors
}
