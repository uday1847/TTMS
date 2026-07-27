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
const DriversPage = lazy(() => import('@/features/drivers/pages/DriverListPage'))
const DriverCreatePage = lazy(() => import('@/features/drivers/pages/DriverCreatePage'))
const DriverDetailsPage = lazy(() => import('@/features/drivers/pages/DriverDetailsPage'))
const DriverEditPage = lazy(() => import('@/features/drivers/pages/DriverEditPage'))
const TractorListPage = lazy(() => import('@/features/tractors/pages/TractorListPage'))
const TractorCreatePage = lazy(() => import('@/features/tractors/pages/TractorCreatePage'))
const TractorDetailsPage = lazy(() => import('@/features/tractors/pages/TractorDetailsPage'))
const TractorEditPage = lazy(() => import('@/features/tractors/pages/TractorEditPage'))
const PartyListPage = lazy(() => import('@/features/parties/pages/PartyListPage'))
const PartyCreatePage = lazy(() => import('@/features/parties/pages/PartyCreatePage'))
const PartyDetailsPage = lazy(() => import('@/features/parties/pages/PartyDetailsPage'))
const PartyEditPage = lazy(() => import('@/features/parties/pages/PartyEditPage'))
const QuarriesPage = lazy(() => import('@/features/quarries/pages/quarries-page'))
const MaterialsPage = lazy(() => import('@/features/materials/pages/materials-page'))
const TripListPage = lazy(() => import('@/features/trips/pages/TripListPage'))
const TripCreatePage = lazy(() => import('@/features/trips/pages/TripCreatePage'))
const TripDetailsPage = lazy(() => import('@/features/trips/pages/TripDetailsPage'))
const TripEditPage = lazy(() => import('@/features/trips/pages/TripEditPage'))
const TripHistoryPage = lazy(() => import('@/features/trips/pages/TripHistoryPage'))
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
            {/* Drivers Routes */}
            <Route path="/drivers">
              <Route element={<ProtectedRoute permission="drivers:read" />}>
                <Route
                  index
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <DriversPage />
                    </Suspense>
                  }
                />
                <Route
                  path=":id"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <DriverDetailsPage />
                    </Suspense>
                  }
                />
              </Route>
              <Route element={<ProtectedRoute permission="drivers:create" />}>
                <Route
                  path="create"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <DriverCreatePage />
                    </Suspense>
                  }
                />
              </Route>
              <Route element={<ProtectedRoute permission="drivers:update" />}>
                <Route
                  path=":id/edit"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <DriverEditPage />
                    </Suspense>
                  }
                />
              </Route>
            </Route>
            {/* Tractors Routes */}
            <Route path="/tractors">
              <Route element={<ProtectedRoute permission="tractors:read" />}>
                <Route
                  index
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <TractorListPage />
                    </Suspense>
                  }
                />
                <Route
                  path=":id"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <TractorDetailsPage />
                    </Suspense>
                  }
                />
              </Route>
              <Route element={<ProtectedRoute permission="tractors:create" />}>
                <Route
                  path="create"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <TractorCreatePage />
                    </Suspense>
                  }
                />
              </Route>
              <Route element={<ProtectedRoute permission="tractors:update" />}>
                <Route
                  path=":id/edit"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <TractorEditPage />
                    </Suspense>
                  }
                />
              </Route>
            </Route>
            {/* Parties Routes */}
            <Route path="/parties">
              <Route element={<ProtectedRoute permission="parties:read" />}>
                <Route
                  index
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <PartyListPage />
                    </Suspense>
                  }
                />
                <Route
                  path=":id"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <PartyDetailsPage />
                    </Suspense>
                  }
                />
              </Route>
              <Route element={<ProtectedRoute permission="parties:create" />}>
                <Route
                  path="create"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <PartyCreatePage />
                    </Suspense>
                  }
                />
              </Route>
              <Route element={<ProtectedRoute permission="parties:update" />}>
                <Route
                  path=":id/edit"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <PartyEditPage />
                    </Suspense>
                  }
                />
              </Route>
            </Route>
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
            {/* Trips Routes */}
            <Route path="/trips">
              <Route element={<ProtectedRoute permission="trips:read" />}>
                <Route
                  index
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <TripListPage />
                    </Suspense>
                  }
                />
                <Route
                  path=":id"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <TripDetailsPage />
                    </Suspense>
                  }
                />
                <Route
                  path=":id/history"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <TripHistoryPage />
                    </Suspense>
                  }
                />
              </Route>
              <Route element={<ProtectedRoute permission="trips:create" />}>
                <Route
                  path="create"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <TripCreatePage />
                    </Suspense>
                  }
                />
              </Route>
              <Route element={<ProtectedRoute permission="trips:update" />}>
                <Route
                  path=":id/edit"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <TripEditPage />
                    </Suspense>
                  }
                />
              </Route>
            </Route>
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
