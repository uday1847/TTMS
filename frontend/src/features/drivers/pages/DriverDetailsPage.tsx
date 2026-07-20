import { useParams, Link, useNavigate } from 'react-router'
import { useDriver } from '../hooks/use-drivers'
import { DriverStatusSwitch } from '../components/DriverStatusSwitch'

export default function DriverDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: driver, isLoading } = useDriver(id!)

  if (isLoading) {
    return (
      <div className="p-6 max-w-5xl mx-auto flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!driver) {
    return (
      <div className="p-6 max-w-5xl mx-auto flex flex-col items-center justify-center min-h-[50vh] text-center">
        <h2 className="text-xl font-bold text-gray-900">Driver Not Found</h2>
        <p className="text-gray-500 mt-2">The driver you are looking for does not exist or has been deleted.</p>
        <button onClick={() => navigate('/drivers')} className="mt-4 text-blue-600 hover:underline">
          Return to Drivers List
        </button>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">{driver.name}</h1>
          <p className="text-sm text-gray-500">Employee Code: {driver.employeeCode}</p>
        </div>
        <div className="flex space-x-3">
          <Link
            to={`/drivers/${driver.id}/edit`}
            className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Edit Driver
          </Link>
          <button
            onClick={() => navigate('/drivers')}
            className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Back to List
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-medium leading-6 text-gray-900">Profile Information</h3>
          </div>
          <div className="px-4 py-5 sm:p-6 space-y-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Full Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{driver.name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Address</dt>
              <dd className="mt-1 text-sm text-gray-900">{driver.address || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Contact Phone</dt>
              <dd className="mt-1 text-sm text-gray-900">{driver.contactPhone}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Emergency Contact</dt>
              <dd className="mt-1 text-sm text-gray-900">{driver.emergencyContactPhone || 'N/A'}</dd>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-medium leading-6 text-gray-900">License Information</h3>
          </div>
          <div className="px-4 py-5 sm:p-6 space-y-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">License Number</dt>
              <dd className="mt-1 text-sm font-mono text-gray-900">{driver.licenseNumber}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">License Class</dt>
              <dd className="mt-1 text-sm text-gray-900">{driver.licenseClass}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Expiry Date</dt>
              <dd className="mt-1 text-sm text-gray-900">{driver.licenseExpiry}</dd>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-medium leading-6 text-gray-900">Employment</h3>
          </div>
          <div className="px-4 py-5 sm:p-6 space-y-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Driver Type</dt>
              <dd className="mt-1 text-sm text-gray-900">{driver.driverType}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Fixed Salary</dt>
              <dd className="mt-1 text-sm text-gray-900">${driver.fixedSalary}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Commission Rate</dt>
              <dd className="mt-1 text-sm text-gray-900">{driver.commissionPercentage}%</dd>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-medium leading-6 text-gray-900">Status & System</h3>
          </div>
          <div className="px-4 py-5 sm:p-6 space-y-4">
            <div>
              <dt className="text-sm font-medium text-gray-500 mb-1">Active Status</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center space-x-2">
                <DriverStatusSwitch id={driver.id} isActive={driver.isActive} />
                <span className={driver.isActive ? 'text-green-600' : 'text-red-600'}>
                  {driver.isActive ? 'Active Account' : 'Inactive Account'}
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Operational Status</dt>
              <dd className="mt-1 text-sm text-gray-900 capitalize">{driver.currentStatus.replace('_', ' ')}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created At</dt>
              <dd className="mt-1 text-sm text-gray-900">{new Date(driver.createdAt).toLocaleString()}</dd>
            </div>
            {driver.updatedAt && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                <dd className="mt-1 text-sm text-gray-900">{new Date(driver.updatedAt).toLocaleString()}</dd>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
