import { Card, CardContent } from '@/components/ui/card'
import { AlertList } from '@/components/alerts/AlertList'

export function AlertsPage() {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Alerts</h1>
      <Card>
        <CardContent className="p-0">
          <AlertList />
        </CardContent>
      </Card>
    </div>
  )
}
