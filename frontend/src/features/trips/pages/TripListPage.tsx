import { useState } from 'react';
import { useNavigate } from 'react-router';
import { useTrips } from '../hooks/use-trips';
import { TripTable } from '../components/TripTable';
import { Button } from '@/shared/ui/button/button';
import { PermissionGuard } from '@/shared/auth';
import { Plus, Search, Filter } from 'lucide-react';
import { TripStatus } from '../types/trip.types';

export default function TripListPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('ALL');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const size = 10;

  const filters: Record<string, any> = {
    page,
    size,
    q: search || undefined,
  };

  if (activeTab !== 'ALL') {
    filters.status = activeTab;
  }

  const { data: response, isLoading } = useTrips(filters);

  const tabs = [
    { value: 'ALL', label: 'All Trips' },
    { value: TripStatus.PENDING, label: 'Pending' },
    { value: TripStatus.DISPATCHED, label: 'Dispatched' },
    { value: TripStatus.IN_PROGRESS, label: 'In Progress' },
    { value: TripStatus.COMPLETED, label: 'Completed' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Trips</h1>
          <p className="text-muted-foreground">Manage and track all transport trips</p>
        </div>
        <PermissionGuard permission="trips:create">
          <Button onClick={() => navigate('/trips/create')}>
            <Plus className="mr-2 h-4 w-4" /> Schedule Trip
          </Button>
        </PermissionGuard>
      </div>

      <div className="flex flex-col gap-4 bg-card border rounded-xl p-4 shadow-sm">
        <div className="flex flex-col sm:flex-row justify-between gap-4">
          <div className="flex w-full sm:w-96 items-center space-x-2 border rounded-md px-3 bg-background">
            <Search className="h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by Trip No or Route..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="flex h-10 w-full bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
          <Button variant="outline" className="sm:w-auto w-full">
            <Filter className="mr-2 h-4 w-4" /> Filters
          </Button>
        </div>

        <div className="border-b border-muted mt-2">
          <nav className="-mb-px flex space-x-6 overflow-x-auto" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.value}
                onClick={() => { setActiveTab(tab.value); setPage(1); }}
                className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.value
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
        
        <div className="mt-4">
          <TripTable
            data={response?.items || []}
            isLoading={isLoading}
          />

          {response && response.total > size && (
            <div className="flex items-center justify-between py-4 border-t mt-4">
              <div className="text-sm text-muted-foreground">
                Showing {((page - 1) * size) + 1} to {Math.min(page * size, response.total)} of {response.total} results
              </div>
              <div className="flex gap-2">
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
                  disabled={page * size >= response.total}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
