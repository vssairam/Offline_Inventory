import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ProductForm } from './ProductForm'
import type { Category } from '@/types'

const cats: Category[] = [{ id: 1, user_id: 1, name: 'Drinks', created_at: '' }]

function setup() {
  const onSubmit = vi.fn()
  const onCreateCategory = vi.fn(async (name: string) => ({ id: 2, user_id: 1, name, created_at: '' }))
  render(<ProductForm categories={cats} onSubmit={onSubmit} onCreateCategory={onCreateCategory} />)
  return { onSubmit, onCreateCategory }
}

describe('ProductForm', () => {
  it('shows validation errors and does not submit empty form', async () => {
    const { onSubmit } = setup()
    await userEvent.click(screen.getByRole('button', { name: /create product/i }))
    expect(screen.getByText('Name is required')).toBeInTheDocument()
    expect(screen.getByText('SKU is required')).toBeInTheDocument()
    expect(screen.getByText('Price must be 0 or more')).toBeInTheDocument()
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('rejects negative price', async () => {
    const { onSubmit } = setup()
    await userEvent.type(screen.getByLabelText('Name'), 'Cola')
    await userEvent.type(screen.getByLabelText('SKU'), 'C1')
    await userEvent.type(screen.getByLabelText('Price'), '-1')
    await userEvent.type(screen.getByLabelText('Cost'), '1')
    await userEvent.click(screen.getByRole('button', { name: /create product/i }))
    expect(screen.getByText('Price must be 0 or more')).toBeInTheDocument()
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('submits a valid payload with numeric values', async () => {
    const { onSubmit } = setup()
    await userEvent.type(screen.getByLabelText('Name'), ' Cola ')
    await userEvent.type(screen.getByLabelText('SKU'), 'C1')
    await userEvent.selectOptions(screen.getByLabelText('Category'), '1')
    await userEvent.type(screen.getByLabelText('Price'), '2.5')
    await userEvent.type(screen.getByLabelText('Cost'), '1')
    await userEvent.clear(screen.getByLabelText('Quantity'))
    await userEvent.type(screen.getByLabelText('Quantity'), '10')
    await userEvent.click(screen.getByRole('button', { name: /create product/i }))
    expect(onSubmit).toHaveBeenCalledWith(
      { name: 'Cola', sku: 'C1', category_id: 1, price: 2.5, cost: 1, quantity: 10, reorder_level: 0, is_active: true },
      null,
    )
  })

  it('creates a category inline and selects it', async () => {
    const { onCreateCategory } = setup()
    await userEvent.click(screen.getByRole('button', { name: 'New' }))
    await userEvent.type(screen.getByLabelText('New category name'), 'Snacks')
    await userEvent.click(screen.getByRole('button', { name: 'Add' }))
    await waitFor(() => expect(onCreateCategory).toHaveBeenCalledWith('Snacks'))
    await waitFor(() => expect((screen.getByLabelText('Category') as HTMLSelectElement).value).toBe('2'))
  })
})
