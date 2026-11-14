export interface PickableProduct {
  id: number
  name: string
  price: number
  quantity: number
}

export interface SaleLine {
  product: PickableProduct
  quantity: number
}

export function addLine(lines: SaleLine[], product: PickableProduct): SaleLine[] {
  const existing = lines.find((l) => l.product.id === product.id)
  if (existing) {
    return lines.map((l) => (l === existing ? { ...l, quantity: l.quantity + 1 } : l))
  }
  return [...lines, { product, quantity: 1 }]
}

export function updateQuantity(lines: SaleLine[], productId: number, quantity: number): SaleLine[] {
  return lines.map((l) => (l.product.id === productId ? { ...l, quantity } : l))
}

export function removeLine(lines: SaleLine[], productId: number): SaleLine[] {
  return lines.filter((l) => l.product.id !== productId)
}

export function lineTotal(line: SaleLine): number {
  return Math.round(line.product.price * line.quantity * 100) / 100
}

export function saleTotal(lines: SaleLine[]): number {
  return Math.round(lines.reduce((sum, l) => sum + lineTotal(l), 0) * 100) / 100
}

export function lineError(line: SaleLine): string | null {
  if (!Number.isInteger(line.quantity) || line.quantity < 1) return 'Quantity must be at least 1'
  if (line.quantity > line.product.quantity) return `Only ${line.product.quantity} in stock`
  return null
}

export function isSaleValid(lines: SaleLine[]): boolean {
  return lines.length > 0 && lines.every((l) => lineError(l) === null)
}
