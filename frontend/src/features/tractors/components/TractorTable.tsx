import { Link } from 'react-router';
import { TractorStatusSwitch } from './TractorStatusSwitch';
import type { TractorResponseDto } from '../types/tractor.types';

interface TractorTableProps {
  tractors: TractorResponseDto[];
  isLoading?: boolean;
  onDelete: (tractor: TractorResponseDto) => void;
}

export function TractorTable({ tractors, isLoading, onDelete }: TractorTableProps) {
  if (isLoading) {
    return (
      <div className="w-full p-8 text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] text-blue-600 motion-reduce:animate-[spin_1.5s_linear_infinite]" role="status">
          <span className="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
        </div>
      </div>
    );
  }

  if (tractors.length === 0) {
    return (
      <div className="w-full p-8 text-center text-gray-500 bg-white border rounded-md">
        No tractors found.
      </div>
    );
  }

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'in_maintenance':
        return 'bg-amber-100 text-amber-800';
      case 'out_of_service':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'Active';
      case 'in_maintenance': return 'In Maintenance';
      case 'out_of_service': return 'Out of Service';
      default: return status;
    }
  };

  return (
    <div className="overflow-x-auto border rounded-md shadow-sm">
      <table className="min-w-full divide-y divide-gray-200 bg-white">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tractor</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RC Number</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Odometer</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Active</th>
            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {tractors.map((tractor) => (
            <tr key={tractor.id} className="hover:bg-gray-50 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex flex-col">
                  <span className="font-semibold text-gray-900">{tractor.tractor_number}</span>
                  <span className="text-xs text-gray-500">{tractor.owner_name}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {tractor.rc_number}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(tractor.status)}`}>
                  {getStatusLabel(tractor.status)}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {tractor.current_odometer} km
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <TractorStatusSwitch tractor={tractor} />
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                <Link to={`/tractors/${tractor.id}`} className="text-blue-600 hover:text-blue-900">View</Link>
                <Link to={`/tractors/${tractor.id}/edit`} className="text-amber-600 hover:text-amber-900">Edit</Link>
                <button onClick={() => onDelete(tractor)} className="text-red-600 hover:text-red-900">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
