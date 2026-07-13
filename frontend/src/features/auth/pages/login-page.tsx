import { useNavigate } from 'react-router'
import { useAuthStore } from '@/stores/auth-store'

export default function LoginPage() {
  const navigate = useNavigate()
  const setCredentials = useAuthStore((state) => state.setCredentials)

  const handleTestLogin = (role: 'Admin' | 'Operator') => {
    // Boilerplate state modifier strictly to allow verification of routing guards
    setCredentials({
      user: {
        id: 'usr_dev',
        email: `${role.toLowerCase()}@ttms.com`,
        name: `Test ${role}`,
        role,
      },
      accessToken: 'auth-session-valid',
      refreshToken: 'refresh-session-valid',
    })
    navigate('/dashboard')
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold tracking-tight">TTMS Enterprise Portal</h2>
        <p className="text-sm text-muted-foreground mt-2">Architecture Authentication Shell</p>
      </div>
      <div className="space-y-2">
        <button
          onClick={() => handleTestLogin('Admin')}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md text-sm font-medium text-white bg-black hover:bg-black/90 dark:bg-white dark:text-black focus:outline-none cursor-pointer"
        >
          Authenticate as Admin
        </button>
        <button
          onClick={() => handleTestLogin('Operator')}
          className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md text-sm font-medium text-foreground bg-gray-100 hover:bg-gray-200 dark:bg-neutral-800 dark:hover:bg-neutral-700 focus:outline-none cursor-pointer"
        >
          Authenticate as Operator
        </button>
      </div>
    </div>
  )
}
