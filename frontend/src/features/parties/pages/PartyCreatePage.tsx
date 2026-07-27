import { useNavigate } from 'react-router';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router';
import { PartyForm } from '../components/PartyForm';
import { useCreateParty } from '../hooks/use-parties';
import { showApiError } from '@/shared/error';
import { useNotificationStore } from '@/stores/notification-store';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card/card';

export default function PartyCreatePage() {
  const navigate = useNavigate();
  const { addNotification } = useNotificationStore();
  const { mutateAsync: createParty, isPending } = useCreateParty();

  const handleSubmit = async (data: any) => {
    try {
      await createParty(data);
      addNotification({
        type: 'success',
        title: 'Party Created',
        message: 'The party has been successfully created.',
      });
      navigate('/parties');
    } catch (error: any) {
      showApiError(error, 'Failed to create party');
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-4">
        <Link 
          to="/parties" 
          className="p-2 rounded-full hover:bg-accent transition-colors"
          aria-label="Back to parties"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Create New Party</h1>
          <p className="text-muted-foreground">Add a new customer, supplier, or broker to your network.</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Party Details</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">Fill in the details to create a new party profile.</p>
        </CardHeader>
        <CardContent>
          <PartyForm 
            onSubmit={handleSubmit} 
            isLoading={isPending} 
            onCancel={() => navigate('/parties')}
          />
        </CardContent>
      </Card>
    </div>
  );
}
