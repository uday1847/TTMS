import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/lib/query-client'
import { ThemeProvider } from '@/providers/theme-provider'
import { Suspense } from 'react'

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <Suspense 
      fallback={
        <div className="flex h-screen w-screen items-center justify-center bg-background text-foreground font-semibold">
          Loading application...
        </div>
      }
    >
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </QueryClientProvider>
    </Suspense>
  )
}
