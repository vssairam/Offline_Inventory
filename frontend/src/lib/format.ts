export function formatMoney(n: number): string {
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(n)
}

export function formatDateTime(s: string): string {
  return new Date(s).toLocaleString()
}
