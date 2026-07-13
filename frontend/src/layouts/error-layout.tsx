import { Link } from 'react-router'

interface ErrorLayoutProps {
  error?: Error
  resetErrorBoundary?: () => void
}

export function ErrorLayout({ error, resetErrorBoundary }: ErrorLayoutProps) {
  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center bg-background text-foreground px-4 text-center">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl text-destructive mb-4">
        Something went wrong
      </h1>
      <p className="text-muted-foreground max-w-md mb-6">
        {error?.message || 'An unexpected runtime crash occurred. Please reload or try again.'}
      </p>
      <div className="flex gap-4">
        {resetErrorBoundary && (
          <button
            onClick={resetErrorBoundary}
            className="px-4 py-2 bg-primary text-primary-foreground font-semibold rounded-md hover:bg-primary/90 transition-colors"
          >
            Try Again
          </button>
        )}
        <Link
          to="/"
          className="px-4 py-2 border font-semibold rounded-md hover:bg-muted transition-colors"
        >
          Return Home
        </Link>
      </div>
    </div>
  )
}
