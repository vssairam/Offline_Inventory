import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { resolveImageUrl } from '@/services/productService'

const MAX_BYTES = 5 * 1024 * 1024
const ALLOWED = ['image/jpeg', 'image/png', 'image/webp']

interface Props {
  currentUrl?: string | null
  file: File | null
  onChange: (file: File | null) => void
}

export function ImageUpload({ currentUrl, file, onChange }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [preview, setPreview] = useState<string | null>(null)

  useEffect(() => {
    if (!file) {
      setPreview(null)
      return
    }
    const url = URL.createObjectURL(file)
    setPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  const handle = (f: File | undefined) => {
    setError(null)
    if (!f) return
    if (!ALLOWED.includes(f.type)) return setError('Use a JPEG, PNG or WebP image')
    if (f.size > MAX_BYTES) return setError('Image must be 5 MB or smaller')
    onChange(f)
  }

  const shown = preview ?? resolveImageUrl(currentUrl ?? null)

  return (
    <div className="flex items-center gap-4">
      <div className="flex h-24 w-24 items-center justify-center overflow-hidden rounded-md border bg-muted text-xs text-muted-foreground">
        {shown ? <img src={shown} alt="Product preview" className="h-full w-full object-cover" /> : 'No image'}
      </div>
      <div className="flex flex-col gap-2">
        <input
          ref={inputRef}
          type="file"
          accept={ALLOWED.join(',')}
          aria-label="Product image"
          className="hidden"
          onChange={(e) => handle(e.target.files?.[0])}
        />
        <div className="flex gap-2">
          <Button type="button" variant="outline" size="sm" onClick={() => inputRef.current?.click()}>
            {shown ? 'Change image' : 'Upload image'}
          </Button>
          {file && (
            <Button type="button" variant="ghost" size="sm" onClick={() => onChange(null)}>
              Remove
            </Button>
          )}
        </div>
        {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
      </div>
    </div>
  )
}
