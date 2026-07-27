import { useState } from 'react';
import { Link } from 'react-router';
import { Plus } from 'lucide-react';
import { useParties } from '../hooks/use-parties';
import { PartyTable } from '../components/PartyTable';
import { PartyFilters } from '../components/PartyFilters';
import { Button } from '@/shared/ui/button/button';
import { PermissionGuard } from '@/shared/auth';

export default function PartyListPage() {
  const [page, setPage] = useState(1);
  const size = 10;
  const [search, setSearch] = useState('');
  const [partyType, setPartyType] = useState('ALL');
  const [status, setStatus] = useState('ALL');

  const filters = {
    page,
    size,
    ...(search && { q: search }),
    ...(partyType !== 'ALL' && { party_type: partyType }),
    ...(status !== 'ALL' && { status }),
  };

  const { data, isLoading, error } = useParties(filters);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Parties Management</h1>
          <p className="text-muted-foreground">Manage your customers, suppliers, and brokers.</p>
        </div>
        <PermissionGuard permission="parties:create">
          <Button asChild>
            <Link to="/parties/create">
              <Plus className="mr-2 h-4 w-4" /> Add Party
            </Link>
          </Button>
        </PermissionGuard>
      </div>

      <PartyFilters
        search={search}
        onSearchChange={setSearch}
        partyType={partyType}
        onPartyTypeChange={setPartyType}
        status={status}
        onStatusChange={setStatus}
      />

      {error ? (
        <div className="p-4 rounded-md bg-destructive/10 text-destructive border border-destructive/20 text-center">
          Error loading parties: {(error as any).response?.data?.detail || error.message}
        </div>
      ) : (
        <div className="bg-card rounded-xl border shadow-sm p-4">
          <PartyTable data={data?.items || []} isLoading={isLoading} />
          
          {!isLoading && data && data.total > 0 && (
            <div className="mt-4 flex items-center justify-between border-t pt-4">
              <p className="text-sm text-muted-foreground">
                Showing {((page - 1) * size) + 1} to {Math.min(page * size, data.total)} of {data.total} entries
              </p>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page * size >= data.total}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
