import { useParams, Link, useNavigate } from 'react-router';
import { useTractor } from '../hooks/use-tractors';
import { TractorStatusSwitch } from '../components/TractorStatusSwitch';

export default function TractorDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: tractor, isLoading } = useTractor(id as string);

  if (isLoading) {
    return (
      <div className="flex justify-center p-12">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent text-blue-600"></div>
      </div>
    );
  }

  if (!tractor) {
    return (
      <div className="text-center p-12">
        <h2 className="text-xl font-semibold text-gray-900">Tractor not found</h2>
        <button onClick={() => navigate('/tractors')} className="mt-4 text-blue-600 hover:underline">
          Back to list
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">Tractor: {tractor.tractor_number}</h1>
          <p className="text-sm text-gray-500">Asset details, status, and performance metrics.</p>
        </div>
        <div className="flex gap-2">
          <Link
            to={`/tractors/${tractor.id}/edit`}
            className="px-4 py-2 text-sm font-medium text-amber-700 bg-amber-100 rounded-md hover:bg-amber-200"
          >
            Edit Tractor
          </Link>
          <button
            onClick={() => navigate('/tractors')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
          >
            Back to List
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white shadow-sm border rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 border-b pb-2">General Information</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Tractor Number</dt>
                <dd className="mt-1 text-sm text-gray-900 font-semibold">{tractor.tractor_number}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Owner Name</dt>
                <dd className="mt-1 text-sm text-gray-900">{tractor.owner_name}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">RC Number</dt>
                <dd className="mt-1 text-sm text-gray-900">{tractor.rc_number}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Registration Date</dt>
                <dd className="mt-1 text-sm text-gray-900">{tractor.registration_date || 'N/A'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Manufacturer</dt>
                <dd className="mt-1 text-sm text-gray-900">{tractor.manufacturer || 'N/A'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Model</dt>
                <dd className="mt-1 text-sm text-gray-900">{tractor.model || 'N/A'}</dd>
              </div>
            </div>
          </div>

          <div className="bg-white shadow-sm border rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 border-b pb-2">Insurance Details</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Insurance Number</dt>
                <dd className="mt-1 text-sm text-gray-900">{tractor.insurance_number || 'N/A'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Insurance Expiry</dt>
                <dd className="mt-1 text-sm text-gray-900">{tractor.insurance_expiry}</dd>
              </div>
            </div>
          </div>
          
          {tractor.remarks && (
            <div className="bg-white shadow-sm border rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2 border-b pb-2">Remarks</h3>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{tractor.remarks}</p>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white shadow-sm border rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 border-b pb-2">Current Status</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-500">Is Active</span>
                <TractorStatusSwitch tractor={tractor} />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-500">State</span>
                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 uppercase tracking-wider">
                  {tractor.status.replace('_', ' ')}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white shadow-sm border rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 border-b pb-2">Metrics</h3>
            <div className="space-y-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Odometer</dt>
                <dd className="mt-1 text-xl font-semibold text-gray-900">{tractor.current_odometer} km</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Fuel Capacity</dt>
                <dd className="mt-1 text-sm text-gray-900">{tractor.fuel_capacity ? `${tractor.fuel_capacity} L` : 'N/A'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Total Fuel Logged</dt>
                <dd className="mt-1 text-sm text-gray-900">{tractor.total_fuel_amount.toFixed(2)} L</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Average Efficiency</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {tractor.average_kmpl !== null ? `${tractor.average_kmpl.toFixed(2)} km/L` : 'Not calculated'}
                </dd>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
