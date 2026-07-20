import { useParams, Link } from 'react-router'
import { useUser } from '../hooks'
import { ArrowLeft, Loader2 } from 'lucide-react'


export default function UserDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const { data: user, isLoading, error } = useUser(id || '')

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[50vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error || !user) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] space-y-4">
        <p className="text-destructive font-medium">Failed to load user details.</p>
        <Link to="/users" className="text-sm text-primary hover:underline">
          Return to Users
        </Link>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center space-x-4">
        <Link to="/users" className="p-2 hover:bg-muted rounded-full transition-colors">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">User Details</h1>
          <p className="text-sm text-muted-foreground">View read-only information for {user.username}.</p>
        </div>
      </div>

      <div className="bg-card border border-border rounded-lg shadow-sm overflow-hidden">
        <div className="p-6">
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-8">
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-muted-foreground">Username</dt>
              <dd className="mt-1 text-sm text-foreground">{user.username}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-muted-foreground">Email</dt>
              <dd className="mt-1 text-sm text-foreground">{user.email}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-muted-foreground">First Name</dt>
              <dd className="mt-1 text-sm text-foreground">{user.firstName}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-muted-foreground">Last Name</dt>
              <dd className="mt-1 text-sm text-foreground">{user.lastName}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-muted-foreground">Phone</dt>
              <dd className="mt-1 text-sm text-foreground">{user.phone || 'N/A'}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-muted-foreground">Status</dt>
              <dd className="mt-1 text-sm text-foreground">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${user.isActive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                  {user.isActive ? 'Active' : 'Inactive'}
                </span>
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-muted-foreground">Roles</dt>
              <dd className="mt-1 text-sm text-foreground">
                {user.roles.length > 0 ? (
                  <div className="flex gap-2 flex-wrap mt-2">
                    {user.roles.map(r => (
                      <span key={r.id} className="bg-primary/10 text-primary text-sm px-3 py-1 rounded-full font-medium">
                        {r.name}
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-muted-foreground italic">No roles assigned</span>
                )}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  )
}
