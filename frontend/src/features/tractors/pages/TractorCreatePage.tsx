import { useNavigate } from 'react-router';
import { TractorForm } from '../components/TractorForm';
import { useCreateTractor } from '../hooks/use-tractors';
import { showApiError } from '@/shared/error';
import type { TractorFormValues } from '../schemas/tractor.schema';

export default function TractorCreatePage() {
  const navigate = useNavigate();
  const createTractor = useCreateTractor();

  const handleSubmit = async (data: TractorFormValues) => {
    try {
      await createTractor.mutateAsync({
        ...data,
      });
      navigate('/tractors');
    } catch (error: any) {
      showApiError(error, 'Failed to create tractor');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">Add Tractor</h1>
        <p className="text-sm text-gray-500">Register a new tractor to your fleet.</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <TractorForm
          onSubmit={handleSubmit}
          isLoading={createTractor.isPending}
          onCancel={() => navigate('/tractors')}
        />
      </div>
    </div>
  );
}
