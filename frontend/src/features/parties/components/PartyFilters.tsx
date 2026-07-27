import { Search } from 'lucide-react';
import { PartyType } from '../types/party.types';

interface PartyFiltersProps {
  search: string;
  onSearchChange: (val: string) => void;
  partyType: string;
  onPartyTypeChange: (val: string) => void;
  status: string;
  onStatusChange: (val: string) => void;
}

export function PartyFilters({
  search,
  onSearchChange,
  partyType,
  onPartyTypeChange,
  status,
  onStatusChange,
}: PartyFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4 bg-card border rounded-xl p-4 shadow-sm">
      <div className="flex flex-1 items-center space-x-2 border rounded-md px-3 bg-background">
        <Search className="h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search by name, GST, mobile, city..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="flex h-10 w-full bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
        />
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <select
          value={partyType}
          onChange={(e) => onPartyTypeChange(e.target.value)}
          className="flex h-10 w-full sm:w-[180px] items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <option value="ALL">All Party Types</option>
          <option value={PartyType.CUSTOMER}>Customer</option>
          <option value={PartyType.SUPPLIER}>Supplier</option>
          <option value={PartyType.BROKER}>Broker</option>
          <option value={PartyType.OTHER}>Other</option>
        </select>

        <select
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
          className="flex h-10 w-full sm:w-[150px] items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <option value="ALL">All Statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
        </select>
      </div>
    </div>
  );
}
