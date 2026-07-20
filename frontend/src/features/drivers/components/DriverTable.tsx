import { Link } from 'react-router'
import { DriverStatusSwitch } from './DriverStatusSwitch'
import type { DriverResponseDto, DriverStatus } from '../types/driver.types'

interface DriverTableProps {
  data: DriverResponseDto[]
  isLoading: boolean
  onDelete: (driver: DriverResponseDto) => void
}

const getStatusColor = (status: DriverStatus) => {
  switch (status) {
    case 'available':
      return 'bg-green-100 text-green-800'
    case 'on_trip':
      return 'bg-blue-100 text-blue-800'
    case 'on_leave':
      return 'bg-yellow-100 text-yellow-800'
    case 'inactive':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

export function DriverTable({ data, isLoading, onDelete }: DriverTableProps) {
  if (isLoading) {
    return (
      <div className="w-full h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!data.length) {
    return (
      <div className="w-full h-64 flex flex-col items-center justify-center text-gray-500">
        <svg className="w-12 h-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <p>No drivers found.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
      <table className="w-full text-sm text-left text-gray-500">
        <thead className="text-xs text-gray-700 uppercase bg-gray-50">
          <tr>
            <th className="px-6 py-3">Name</th>
            <th className="px-6 py-3">Code / License</th>
            <th className="px-6 py-3">Type</th>
            <th className="px-6 py-3">Contact</th>
            <th className="px-6 py-3">Status</th>
            <th className="px-6 py-3">Active</th>
            <th className="px-6 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.map((driver) => (
            <tr key={driver.id} className="bg-white border-b hover:bg-gray-50">
              <td className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
                {driver.name}
              </td>
              <td className="px-6 py-4">
                <div className="flex flex-col">
                  <span className="font-semibold text-gray-700">{driver.employeeCode}</span>
                  <span className="text-xs">{driver.licenseNumber}</span>
                </div>
              </td>
              <td className="px-6 py-4">{driver.driverType}</td>
              <td className="px-6 py-4">{driver.contactPhone}</td>
              <td className="px-6 py-4">
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(driver.currentStatus)}`}>
                  {driver.currentStatus.replace('_', ' ').toUpperCase()}
                </span>
              </td>
              <td className="px-6 py-4">
                <DriverStatusSwitch id={driver.id} isActive={driver.isActive} />
              </td>
              <td className="px-6 py-4 text-right space-x-2">
                <Link
                  to={`/drivers/${driver.id}`}
                  className="font-medium text-blue-600 hover:underline"
                >
                  View
                </Link>
                <Link
                  to={`/drivers/${driver.id}/edit`}
                  className="font-medium text-amber-600 hover:underline"
                >
                  Edit
                </Link>
                <button
                  onClick={() => onDelete(driver)}
                  className="font-medium text-red-600 hover:underline"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
