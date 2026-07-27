import { useNavigate, useParams } from 'react-router';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { Link } from 'react-router';
import { PartyForm } from '../components/PartyForm';
import { useParty, useUpdateParty } from '../hooks/use-parties';
import { showApiError } from '@/shared/error';
import { useNotificationStore } from '@/stores/notification-store';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card/card';

export default function PartyEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addNotification } = useNotificationStore();
  
  const { data: party, isLoading: isFetching, error } = useParty(id!);
  const { mutateAsync: updateParty, isPending } = useUpdateParty(id!);

  const handleSubmit = async (data: any) => {
    try {
      await updateParty(data);
      addNotification({
        type: 'success',
        title: 'Party Updated',
        message: 'The party has been successfully updated.',
      });
      navigate('/parties');
    } catch (error: any) {
      showApiError(error, 'Failed to update party');
    }
  };

  if (isFetching) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !party) {
    return (
      <div className="flex h-[400px] flex-col items-center justify-center space-y-4">
        <div className="text-xl font-medium text-destructive">Failed to load party</div>
        <p className="text-muted-foreground">The party you are trying to edit could not be found or an error occurred.</p>
        <Link to="/parties" className="text-primary hover:underline">Return to Parties</Link>
      </div>
    );
  }

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
          <h1 className="text-2xl font-bold tracking-tight">Edit Party</h1>
          <p className="text-muted-foreground">Update details for {party.name}</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Party Details</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">Modify the information below to update the party profile.</p>
        </CardHeader>
        <CardContent>
          <PartyForm 
            initialData={party}
            onSubmit={handleSubmit} 
            isLoading={isPending} 
            onCancel={() => navigate('/parties')}
          />
        </CardContent>
      </Card>
    </div>
  );
}
