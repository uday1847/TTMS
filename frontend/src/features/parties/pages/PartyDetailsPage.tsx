import { useParams, Link } from 'react-router';
import { ArrowLeft, Loader2, Building2, MapPin, CreditCard, Clock } from 'lucide-react';
import { useParty } from '../hooks/use-parties';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card/card';
import { PartyStatusSwitch } from '../components/PartyStatusSwitch';
import { PermissionGuard } from '@/shared/auth';
import dayjs from 'dayjs';

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
  }).format(amount);
};

export default function PartyDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const { data: party, isLoading, error } = useParty(id!);

  if (isLoading) {
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
        <p className="text-muted-foreground">The party you are looking for could not be found.</p>
        <Link to="/parties" className="text-primary hover:underline">Return to Parties</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-4">
          <Link 
            to="/parties" 
            className="p-2 rounded-full hover:bg-accent transition-colors border"
            aria-label="Back to parties"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{party.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary border">
                {party.party_type}
              </span>
              <span className="text-sm text-muted-foreground">Party Profile</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium">Status:</span>
          <PermissionGuard permission="parties:update" fallback={
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              party.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {party.is_active ? 'Active' : 'Inactive'}
            </span>
          }>
            <div className="flex items-center gap-2">
              <span className={`text-sm ${party.is_active ? 'text-green-600' : 'text-muted-foreground'}`}>
                {party.is_active ? 'Active' : 'Inactive'}
              </span>
              <PartyStatusSwitch partyId={party.id} initialStatus={party.is_active} />
            </div>
          </PermissionGuard>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column (Main Details) */}
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader className="pb-3 border-b">
              <CardTitle className="text-lg flex items-center gap-2">
                <Building2 className="h-5 w-5 text-muted-foreground" />
                Contact & Tax Information
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-6">
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Contact Person</dt>
                  <dd className="mt-1 text-sm font-medium">{party.contact_person || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Email Address</dt>
                  <dd className="mt-1 text-sm font-medium">{party.email || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Primary Mobile</dt>
                  <dd className="mt-1 text-sm font-medium">{party.mobile_number}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Alternate Mobile</dt>
                  <dd className="mt-1 text-sm font-medium">{party.alternate_mobile || 'N/A'}</dd>
                </div>
                <div className="sm:col-span-2 border-t pt-4 mt-2">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm font-medium text-muted-foreground">GSTIN</dt>
                      <dd className="mt-1 text-sm font-medium font-mono bg-muted/50 p-1.5 rounded inline-block">
                        {party.gst_number || 'N/A'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-muted-foreground">PAN</dt>
                      <dd className="mt-1 text-sm font-medium font-mono bg-muted/50 p-1.5 rounded inline-block">
                        {party.pan_number || 'N/A'}
                      </dd>
                    </div>
                  </div>
                </div>
              </dl>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3 border-b">
              <CardTitle className="text-lg flex items-center gap-2">
                <MapPin className="h-5 w-5 text-muted-foreground" />
                Location & Address
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-6">
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-muted-foreground">Street Address</dt>
                  <dd className="mt-1 text-sm">{party.address || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">City</dt>
                  <dd className="mt-1 text-sm">{party.city || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">State</dt>
                  <dd className="mt-1 text-sm">{party.state || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Pincode</dt>
                  <dd className="mt-1 text-sm">{party.pincode || 'N/A'}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>
        </div>

        {/* Right Column (Financials & Meta) */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-3 border-b bg-muted/20">
              <CardTitle className="text-lg flex items-center gap-2">
                <CreditCard className="h-5 w-5 text-muted-foreground" />
                Financial Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-6">
              <div>
                <dt className="text-sm font-medium text-muted-foreground mb-1">Opening Balance</dt>
                <dd className="text-2xl font-bold text-foreground">
                  {formatCurrency(party.opening_balance)}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground mb-1">Credit Limit</dt>
                <dd className="text-xl font-semibold text-foreground">
                  {formatCurrency(party.credit_limit)}
                </dd>
              </div>
              
              <div className="border-t pt-4 space-y-3">
                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Live Metrics</h4>
                <div className="flex justify-between items-center p-3 bg-accent/50 rounded-lg border">
                  <span className="text-sm font-medium">Linked Trips</span>
                  <span className="text-sm font-bold">--</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-accent/50 rounded-lg border">
                  <span className="text-sm font-medium">Outstanding Balance</span>
                  <span className="text-sm font-bold">--</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3 border-b">
              <CardTitle className="text-lg flex items-center gap-2">
                <Clock className="h-5 w-5 text-muted-foreground" />
                Audit Trail
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Created On</dt>
                <dd className="mt-1 text-sm">{dayjs(party.created_at).format('DD MMM YYYY, hh:mm A')}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Last Updated</dt>
                <dd className="mt-1 text-sm">{dayjs(party.updated_at).format('DD MMM YYYY, hh:mm A')}</dd>
              </div>
              {party.remarks && (
                <div className="pt-2 border-t">
                  <dt className="text-sm font-medium text-muted-foreground">Remarks</dt>
                  <dd className="mt-1 text-sm italic bg-muted/30 p-2 rounded">{party.remarks}</dd>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
