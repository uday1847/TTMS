import { useState } from 'react'
import { Link } from 'react-router'
import { useDrivers } from '../hooks/use-drivers'
import { DriverTable } from '../components/DriverTable'
import { DeleteDriverDialog } from '../components/DeleteDriverDialog'
import { Pagination, SearchInput } from '@/shared/components/data-table'
import type { DriverResponseDto } from '../types/driver.types'

export default function DriverListPage() {
  const [page, setPage] = useState(1)
  const [size, setSize] = useState(10)
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('')
  const [includeDeleted, setIncludeDeleted] = useState(false)
  const [deletingDriver, setDeletingDriver] = useState<DriverResponseDto | undefined>()

  const { data, isLoading, refetch } = useDrivers({
    page,
    size,
    q: q || undefined,
    status: status || undefined,
    include_deleted: includeDeleted,
    sort_by: 'created_at',
    order: 'desc'
  })

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">Drivers</h1>
          <p className="text-sm text-gray-500">Manage all vehicle drivers and their operational status.</p>
        </div>
        <Link
          to="/drivers/create"
          className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Add Driver
        </Link>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-4 justify-between bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center gap-4 w-full sm:w-auto flex-1">
          <div className="w-full sm:w-72">
            <SearchInput
              value={q}
              onChange={(val) => {
                setQ(val)
                setPage(1)
              }}
              placeholder="Search by name, code or license..."
            />
          </div>
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value)
              setPage(1)
            }}
            className="h-10 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="AVAILABLE">Available</option>
            <option value="ON_TRIP">On Trip</option>
            <option value="ON_LEAVE">On Leave</option>
            <option value="INACTIVE">Inactive</option>
          </select>
          <label className="flex items-center space-x-2 text-sm text-gray-700 cursor-pointer">
            <input
              type="checkbox"
              checked={includeDeleted}
              onChange={(e) => {
                setIncludeDeleted(e.target.checked)
                setPage(1)
              }}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4"
            />
            <span>Include Deleted</span>
          </label>
        </div>
        <button
          onClick={() => refetch()}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
          title="Refresh"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      <DriverTable
        data={data?.items || []}
        isLoading={isLoading}
        onDelete={setDeletingDriver}
      />

      {!!data && data.total > 0 && (
        <Pagination
          page={page}
          size={size}
          total={data.total}
          onPageChange={setPage}
          onSizeChange={(newSize) => {
            setSize(newSize)
            setPage(1)
          }}
        />
      )}

      <DeleteDriverDialog
        isOpen={!!deletingDriver}
        driverId={deletingDriver?.id || ''}
        driverName={deletingDriver?.name || ''}
        onClose={() => setDeletingDriver(undefined)}
      />
    </div>
  )
}
