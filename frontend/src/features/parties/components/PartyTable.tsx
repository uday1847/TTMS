import { useState } from 'react';
import { Link } from 'react-router';
import type { PartyResponseDto } from '../types/party.types';
import { PartyType } from '../types/party.types';
import { PartyStatusSwitch } from './PartyStatusSwitch';
import { DeletePartyDialog } from './DeletePartyDialog';
import { PermissionGuard } from '@/shared/auth';
import dayjs from 'dayjs';
import { MoreHorizontal, Edit, Eye, Trash2 } from 'lucide-react';
import { Button } from '@/shared/ui/button/button';

interface PartyTableProps {
  data: PartyResponseDto[];
  isLoading?: boolean;
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
  }).format(amount);
};

export function PartyTable({ data, isLoading }: PartyTableProps) {
  const [deleteParty, setDeleteParty] = useState<PartyResponseDto | null>(null);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="w-full h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="w-full h-64 flex flex-col items-center justify-center text-muted-foreground border rounded-md bg-card mt-4">
        <p>No parties found.</p>
      </div>
    );
  }

  const toggleMenu = (id: string) => {
    setOpenMenuId(openMenuId === id ? null : id);
  };

  const getPartyTypeBadgeColor = (type: PartyType) => {
    switch (type) {
      case PartyType.CUSTOMER:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 border-blue-200 dark:border-blue-800';
      case PartyType.SUPPLIER:
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 border-green-200 dark:border-green-800';
      case PartyType.BROKER:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800';
      case PartyType.OTHER:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-700';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-700';
    }
  };

  return (
    <>
      <div className="overflow-x-auto rounded-lg border shadow-sm bg-card mt-4">
        <table className="w-full text-sm text-left text-muted-foreground">
          <thead className="text-xs text-foreground uppercase bg-muted/50 border-b">
            <tr>
              <th className="px-4 py-3 font-medium">Name & Type</th>
              <th className="px-4 py-3 font-medium">Contact</th>
              <th className="px-4 py-3 font-medium">Location</th>
              <th className="px-4 py-3 font-medium text-right">Balance & Credit</th>
              <th className="px-4 py-3 font-medium text-center">Active</th>
              <th className="px-4 py-3 font-medium">Created At</th>
              <th className="px-4 py-3 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.map((party) => (
              <tr key={party.id} className="border-b hover:bg-muted/20">
                <td className="px-4 py-3">
                  <div className="flex flex-col space-y-1 items-start">
                    <span className="font-semibold text-foreground">{party.name}</span>
                    <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${getPartyTypeBadgeColor(party.party_type)}`}>
                      {party.party_type}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-col">
                    <span className="font-medium text-foreground">{party.mobile_number}</span>
                    {party.contact_person && (
                      <span className="text-xs">{party.contact_person}</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-col">
                    <span className="text-foreground font-medium">{party.city || '-'}</span>
                    <span className="text-xs">{party.state || '-'}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex flex-col items-end">
                    <span className="font-medium text-foreground">{formatCurrency(party.opening_balance)}</span>
                    <span className="text-xs">Limit: {formatCurrency(party.credit_limit)}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <PermissionGuard permission="parties:update" fallback={
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      party.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {party.is_active ? 'Active' : 'Inactive'}
                    </span>
                  }>
                    <PartyStatusSwitch partyId={party.id} initialStatus={party.is_active} />
                  </PermissionGuard>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  {dayjs(party.created_at).format('DD MMM YYYY')}
                </td>
                <td className="px-4 py-3 text-right relative">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => toggleMenu(party.id)}
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                  
                  {openMenuId === party.id && (
                    <>
                      <div 
                        className="fixed inset-0 z-40" 
                        onClick={() => setOpenMenuId(null)}
                      ></div>
                      <div className="absolute right-8 top-10 z-50 w-48 bg-card border rounded-md shadow-lg py-1 text-left">
                        <Link 
                          to={`/parties/${party.id}`}
                          className="flex items-center px-4 py-2 text-sm hover:bg-accent"
                          onClick={() => setOpenMenuId(null)}
                        >
                          <Eye className="mr-2 h-4 w-4" /> View Details
                        </Link>
                        
                        <PermissionGuard permission="parties:update">
                          <Link 
                            to={`/parties/${party.id}/edit`}
                            className="flex items-center px-4 py-2 text-sm hover:bg-accent"
                            onClick={() => setOpenMenuId(null)}
                          >
                            <Edit className="mr-2 h-4 w-4" /> Edit Party
                          </Link>
                        </PermissionGuard>
                        
                        <PermissionGuard permission="parties:delete">
                          <button
                            onClick={() => { setDeleteParty(party); setOpenMenuId(null); }}
                            className="w-full flex items-center px-4 py-2 text-sm hover:bg-accent text-destructive text-left"
                          >
                            <Trash2 className="mr-2 h-4 w-4" /> Delete Party
                          </button>
                        </PermissionGuard>
                      </div>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {deleteParty && (
        <DeletePartyDialog
          partyId={deleteParty.id}
          partyName={deleteParty.name}
          isOpen={!!deleteParty}
          onClose={() => setDeleteParty(null)}
        />
      )}
    </>
  );
}
