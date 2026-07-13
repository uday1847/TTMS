export default function UsersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-red-500">User Management Console</h1>
        <p className="text-muted-foreground">Admin-restricted console. Control system login accounts and role access permissions.</p>
      </div>
      <div className="rounded-xl border bg-card p-6 shadow-sm border-red-500/20 bg-red-500/5">
        <p className="text-sm text-red-500 text-center py-10 font-medium">
          Access Granted: Secure Admin credentials verified. Users module placeholder.
        </p>
      </div>
    </div>
  )
}
