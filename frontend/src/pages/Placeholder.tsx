import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function Placeholder({ title }: { title: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">Coming soon.</CardContent>
    </Card>
  )
}
