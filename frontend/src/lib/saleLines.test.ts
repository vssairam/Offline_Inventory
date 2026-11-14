import { addLine, isSaleValid, lineError, removeLine, saleTotal, updateQuantity, type SaleLine } from './saleLines'

const widget = { id: 1, name: 'Widget', price: 10.1, quantity: 5 }
const gadget = { id: 2, name: 'Gadget', price: 2.5, quantity: 1 }

describe('sale line logic', () => {
  it('adds lines and increments duplicates', () => {
    let lines: SaleLine[] = addLine([], widget)
    lines = addLine(lines, widget)
    lines = addLine(lines, gadget)
    expect(lines).toHaveLength(2)
    expect(lines[0].quantity).toBe(2)
  })

  it('computes totals with rounding', () => {
    let lines = addLine([], widget)
    lines = updateQuantity(lines, 1, 3)
    lines = addLine(lines, gadget)
    expect(saleTotal(lines)).toBe(32.8)
  })

  it('validates against stock', () => {
    const lines = updateQuantity(addLine([], gadget), 2, 2)
    expect(lineError(lines[0])).toMatch(/only 1 in stock/i)
    expect(isSaleValid(lines)).toBe(false)
    expect(isSaleValid(updateQuantity(lines, 2, 1))).toBe(true)
    expect(isSaleValid([])).toBe(false)
  })

  it('rejects zero or non-integer quantity and removes lines', () => {
    const lines = addLine([], widget)
    expect(lineError(updateQuantity(lines, 1, 0)[0])).not.toBeNull()
    expect(lineError(updateQuantity(lines, 1, Number.NaN)[0])).not.toBeNull()
    expect(removeLine(lines, 1)).toEqual([])
  })
})
