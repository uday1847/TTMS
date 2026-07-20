import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router'
import { AuthLayout } from '@/layouts/auth-layout'
import { DashboardLayout } from '@/layouts/dashboard-layout'
import { PublicRoute } from '@/routes/public-route'
import { ProtectedRoute } from '@/routes/protected-route'
import { PERMISSIONS } from '@/constants/permissions'

// Lazy loaded page components
const LoginPage = lazy(() => import('@/features/auth/pages/login-page'))
const DashboardPage = lazy(() => import('@/features/dashboard/pages/dashboard-page'))
const DriversPage = lazy(() => import('@/features/drivers/pages/drivers-page'))
const TractorsPage = lazy(() => import('@/features/tractors/pages/tractors-page'))
const PartiesPage = lazy(() => import('@/features/parties/pages/parties-page'))
const QuarriesPage = lazy(() => import('@/features/quarries/pages/quarries-page'))
const MaterialsPage = lazy(() => import('@/features/materials/pages/materials-page'))
const TripsPage = lazy(() => import('@/features/trips/pages/trips-page'))
const ExpensesPage = lazy(() => import('@/features/expenses/pages/expenses-page'))
const PaymentsPage = lazy(() => import('@/features/payments/pages/payments-page'))
const ReportsPage = lazy(() => import('@/features/reports/pages/reports-page'))
const UsersPage = lazy(() => import('@/features/users/pages/UsersPage'))
const UserDetailsPage = lazy(() => import('@/features/users/pages/UserDetailsPage'))
const SettingsPage = lazy(() => import('@/features/settings/pages/settings-page'))
const NotFoundPage = lazy(() => import('./not-found-page'))

const UnauthorizedPage = lazy(() => import('@/features/auth/pages/unauthorized-page'))
const ForgotPasswordPage = lazy(() => import('@/features/auth/pages/forgot-password-page'))

// Loader fallback spinner
function PageLoader() {
  return (
    <div className="flex h-40 w-full items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-neutral-400 border-t-transparent"></div>
    </div>
  )
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Redirect root path to dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* Public Guest Routes */}
        <Route element={<PublicRoute />}>
          <Route element={<AuthLayout />}>
            <Route
              path="/login"
              element={
                <Suspense fallback={<PageLoader />}>
                  <LoginPage />
                </Suspense>
              }
            />
            <Route
              path="/forgot-password"
              element={
                <Suspense fallback={<PageLoader />}>
                  <ForgotPasswordPage />
                </Suspense>
              }
            />
          </Route>
        </Route>

        {/* Protected Operator/Admin Routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route
              path="/dashboard"
              element={
                <Suspense fallback={<PageLoader />}>
                  <DashboardPage />
                </Suspense>
              }
            />
            <Route
              path="/drivers"
              element={
                <Suspense fallback={<PageLoader />}>
                  <DriversPage />
                </Suspense>
              }
            />
            <Route
              path="/tractors"
              element={
                <Suspense fallback={<PageLoader />}>
                  <TractorsPage />
                </Suspense>
              }
            />
            <Route
              path="/parties"
              element={
                <Suspense fallback={<PageLoader />}>
                  <PartiesPage />
                </Suspense>
              }
            />
            <Route
              path="/quarries"
              element={
                <Suspense fallback={<PageLoader />}>
                  <QuarriesPage />
                </Suspense>
              }
            />
            <Route
              path="/materials"
              element={
                <Suspense fallback={<PageLoader />}>
                  <MaterialsPage />
                </Suspense>
              }
            />
            <Route
              path="/trips"
              element={
                <Suspense fallback={<PageLoader />}>
                  <TripsPage />
                </Suspense>
              }
            />
            <Route
              path="/expenses"
              element={
                <Suspense fallback={<PageLoader />}>
                  <ExpensesPage />
                </Suspense>
              }
            />
            <Route
              path="/payments"
              element={
                <Suspense fallback={<PageLoader />}>
                  <PaymentsPage />
                </Suspense>
              }
            />
            <Route
              path="/reports"
              element={
                <Suspense fallback={<PageLoader />}>
                  <ReportsPage />
                </Suspense>
              }
            />
            <Route
              path="/settings"
              element={
                <Suspense fallback={<PageLoader />}>
                  <SettingsPage />
                </Suspense>
              }
            />

            {/* Users Routes */}
            <Route element={<ProtectedRoute permission={PERMISSIONS.USERS_READ} />}>
              <Route
                path="/users"
                element={
                  <Suspense fallback={<PageLoader />}>
                    <UsersPage />
                  </Suspense>
                }
              />
              <Route
                path="/users/:id"
                element={
                  <Suspense fallback={<PageLoader />}>
                    <UserDetailsPage />
                  </Suspense>
                }
              />
            </Route>
          </Route>
        </Route>

        {/* Global Fallback Route */}
        <Route
          path="*"
          element={
            <Suspense fallback={<PageLoader />}>
              <NotFoundPage />
            </Suspense>
          }
        />
        <Route
          path="/unauthorized"
          element={
            <Suspense fallback={<PageLoader />}>
              <UnauthorizedPage />
            </Suspense>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
