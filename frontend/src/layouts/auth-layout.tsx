import { Outlet } from 'react-router'
import { Truck } from 'lucide-react'

export function AuthLayout() {
  return (
    <div className="min-h-screen grid grid-cols-1 md:grid-cols-2">
      <div className="flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-sm space-y-6">
          <Outlet />
        </div>
      </div>
      
      <div className="hidden md:flex flex-col justify-center items-center bg-zinc-900 text-white p-8">
        <div className="max-w-md text-center space-y-6">
          <Truck className="w-16 h-16 mx-auto text-primary" />
          <h2 className="text-3xl font-bold">Transport & Tractor Management System</h2>
          <p className="text-zinc-400 text-lg">
            Streamline your fleet operations, manage trips efficiently, and optimize fuel usage with our enterprise-grade platform.
          </p>
        </div>
      </div>
    </div>
  )
}
