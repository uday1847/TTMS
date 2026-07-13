import { Link } from 'react-router'

export default function NotFoundPage() {
  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center bg-background text-foreground px-4 text-center">
      <h1 className="text-6xl font-extrabold tracking-tight mb-2">404</h1>
      <h2 className="text-xl font-semibold mb-4">Page Not Found</h2>
      <p className="text-muted-foreground max-w-sm mb-6">
        The route path you requested does not exist or you lack navigation authorization permissions.
      </p>
      <Link
        to="/"
        className="px-4 py-2 bg-black text-white dark:bg-white dark:text-black font-semibold rounded-md hover:opacity-90 transition-opacity cursor-pointer"
      >
        Return to Portal
      </Link>
    </div>
  )
}
