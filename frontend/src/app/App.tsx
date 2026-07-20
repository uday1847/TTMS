import { AppProviders } from './providers'
import { AppRouter } from './router'
import { AuthBootstrap } from './AuthBootstrap'

export default function App() {
  return (
    <AppProviders>
      <AuthBootstrap>
        <AppRouter />
      </AuthBootstrap>
    </AppProviders>
  )
}
