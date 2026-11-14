import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { adminService, type AdminUser, type AdminUserUpdate } from '@/services/adminService'
import { getApiErrorMessage } from '@/services/saleService'
import { useAuth } from '@/context/AuthContext'

const PAGE_SIZE = 20

interface PendingChange {
  user: AdminUser
  payload: AdminUserUpdate
  message: string
}

export function AdminUsersPage() {
  const { user: me } = useAuth()
  const qc = useQueryClient()
  const [q, setQ] = useState('')
  const [page, setPage] = useState(1)
  const [pending, setPending] = useState<PendingChange | null>(null)
  const [error, setError] = useState<string | null>(null)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin', 'users', page, q],
    queryFn: () => adminService.users({ page, page_size: PAGE_SIZE, q: q || undefined }),
  })

  const mutation = useMutation({
    mutationFn: (c: PendingChange) => adminService.updateUser(c.user.id, c.payload),
    onSuccess: () => {
      setError(null)
      void qc.invalidateQueries({ queryKey: ['admin'] })
    },
    onError: (err) => setError(getApiErrorMessage(err, 'Update failed')),
    onSettled: () => setPending(null),
  })

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Users</h1>
      <Input
        aria-label="Search users"
        placeholder="Search by name or email"
        className="max-w-sm"
        value={q}
        onChange={(e) => {
          setQ(e.target.value)
          setPage(1)
        }}
      />
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
      {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
      {isError && <p className="text-sm text-destructive">Failed to load users.</p>}
      {data && (
        <Card>
          <CardContent className="pt-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((u) => {
                  const isSelf = u.id === me?.id
                  return (
                    <TableRow key={u.id}>
                      <TableCell>{u.full_name ?? '-'}</TableCell>
                      <TableCell>{u.email}</TableCell>
                      <TableCell>
                        <Badge variant={u.is_active ? 'default' : 'secondary'}>{u.is_active ? 'Active' : 'Inactive'}</Badge>
                      </TableCell>
                      <TableCell>{u.is_admin ? 'Admin' : 'User'}</TableCell>
                      <TableCell className="space-x-2 text-right">
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={isSelf || mutation.isPending}
                          onClick={() =>
                            setPending({
                              user: u,
                              payload: { is_active: !u.is_active },
                              message: `${u.is_active ? 'Deactivate' : 'Activate'} ${u.email}?`,
                            })
                          }
                        >
                          {u.is_active ? 'Deactivate' : 'Activate'}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={isSelf || mutation.isPending}
                          onClick={() =>
                            setPending({
                              user: u,
                              payload: { is_admin: !u.is_admin },
                              message: `${u.is_admin ? 'Demote' : 'Promote'} ${u.email}?`,
                            })
                          }
                        >
                          {u.is_admin ? 'Demote' : 'Promote'}
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
                {data.items.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground">
                      No users found.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
            <div className="mt-4 flex items-center justify-between text-sm">
              <span className="text-muted-foreground">
                Page {data.page} of {totalPages}
              </span>
              <div className="space-x-2">
                <Button size="sm" variant="outline" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                  Previous
                </Button>
                <Button size="sm" variant="outline" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                  Next
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      {pending && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Confirm change"
            className="w-full max-w-sm space-y-4 rounded-lg bg-background p-6 shadow-lg"
          >
            <p className="text-sm">{pending.message}</p>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setPending(null)}>
                Cancel
              </Button>
              <Button onClick={() => mutation.mutate(pending)} disabled={mutation.isPending}>
                Confirm
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
