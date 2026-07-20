import { useNavigate, useParams } from 'react-router';
import { TractorForm } from '../components/TractorForm';
import { useTractor, useUpdateTractor } from '../hooks/use-tractors';
import type { TractorFormValues } from '../schemas/tractor.schema';

export default function TractorEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: tractor, isLoading } = useTractor(id as string);
  const updateTractor = useUpdateTractor();

  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] text-blue-600"></div>
      </div>
    );
  }

  if (!tractor) {
    return <div className="p-8 text-center text-red-500">Tractor not found</div>;
  }

  const handleSubmit = async (data: TractorFormValues) => {
    try {
      await updateTractor.mutateAsync({
        id: tractor.id,
        data,
      });
      navigate('/tractors');
    } catch (error) {
      console.error('Failed to update tractor', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">Edit Tractor: {tractor.tractor_number}</h1>
        <p className="text-sm text-gray-500">Update details for this tractor asset.</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <TractorForm
          initialData={tractor}
          onSubmit={handleSubmit}
          isLoading={updateTractor.isPending}
          onCancel={() => navigate('/tractors')}
        />
      </div>
    </div>
  );
}
