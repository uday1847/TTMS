import { useState, useEffect } from 'react'
import { Shield, X, Check, Search, Save } from 'lucide-react'
import { useUserAccessProfile, useUpdateUserRoles, useUpdateUserPermissions } from '../hooks'
import { useRoles } from '@/features/roles/hooks/use-roles'
import { usePermissions } from '@/features/permissions/hooks/use-permissions'
import { PermissionGuard } from '@/shared/auth'
import { showApiError } from '@/shared/error'

interface UserAccessProfileDrawerProps {
  userId: string | undefined
  isOpen: boolean
  onClose: () => void
}

export function UserAccessProfileDrawer({ userId, isOpen, onClose }: UserAccessProfileDrawerProps) {
  const { data: userProfile, isLoading } = useUserAccessProfile(userId)
  const { data: allRoles } = useRoles()
  const { data: allPermissions } = usePermissions()

  const { mutateAsync: updateRoles, isPending: isUpdatingRoles } = useUpdateUserRoles()
  const { mutateAsync: updatePermissions, isPending: isUpdatingPermissions } = useUpdateUserPermissions()

  const [selectedRoles, setSelectedRoles] = useState<string[]>([])
  const [grantedOverrides, setGrantedOverrides] = useState<string[]>([])
  const [revokedOverrides, setRevokedOverrides] = useState<string[]>([])
  const [search, setSearch] = useState('')

  useEffect(() => {
    if (userProfile) {
      setSelectedRoles(userProfile.roles.map(r => r.id))
      
      // Calculate what is an override
      // The userProfile.directPermissions are all direct grants
      setGrantedOverrides(userProfile.directPermissions || [])
      setRevokedOverrides([]) // We'll reset this for now.
    }
  }, [userProfile])

  if (!isOpen) return null

  const handleToggleRole = (roleId: string) => {
    if (selectedRoles.includes(roleId)) {
      setSelectedRoles(selectedRoles.filter(id => id !== roleId))
    } else {
      setSelectedRoles([...selectedRoles, roleId])
    }
  }

  const handleTogglePermission = (permName: string) => {
    // Basic 3-state toggle: Default (role-based) -> Granted (override) -> Revoked (override) -> Default
    if (grantedOverrides.includes(permName)) {
      setGrantedOverrides(grantedOverrides.filter(p => p !== permName))
      setRevokedOverrides([...revokedOverrides, permName])
    } else if (revokedOverrides.includes(permName)) {
      setRevokedOverrides(revokedOverrides.filter(p => p !== permName))
    } else {
      setGrantedOverrides([...grantedOverrides, permName])
    }
  }

  const handleSave = async () => {
    if (!userId) return
    try {
      await updateRoles({ id: userId, roleIds: selectedRoles })
      await updatePermissions({ id: userId, grantPermissions: grantedOverrides, revokePermissions: revokedOverrides })
      onClose()
    } catch (e) {
      showApiError(e, 'Failed to update access profile')
    }
  }

  const filteredPermissions = allPermissions?.filter(p => 
    p.name.toLowerCase().includes(search.toLowerCase())
  ) || []

  const isSaving = isUpdatingRoles || isUpdatingPermissions

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-background/80 backdrop-blur-sm">
      <div className="w-full max-w-2xl bg-card border-l shadow-2xl h-full flex flex-col animate-in slide-in-from-right duration-200">
        <div className="p-6 border-b flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              Access Profile
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              Manage roles and direct permission overrides for {userProfile?.email}
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-muted rounded-full">
            <X className="h-5 w-5" />
          </button>
        </div>

        {isLoading ? (
          <div className="flex-1 p-6 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-6 space-y-8">
            {/* Roles Section */}
            <section>
              <h3 className="text-lg font-semibold mb-4">Assigned Roles</h3>
              <div className="grid grid-cols-2 gap-3">
                {allRoles?.map(role => {
                  const isSelected = selectedRoles.includes(role.id)
                  return (
                    <button
                      key={role.id}
                      onClick={() => handleToggleRole(role.id)}
                      className={`flex items-center justify-between p-3 rounded-lg border text-left transition-colors ${
                        isSelected ? 'border-primary bg-primary/5' : 'hover:border-primary/50'
                      }`}
                    >
                      <div>
                        <div className="font-medium">{role.name}</div>
                        <div className="text-xs text-muted-foreground">{role.description}</div>
                      </div>
                      {isSelected && <Check className="h-4 w-4 text-primary" />}
                    </button>
                  )
                })}
              </div>
            </section>

            {/* Permissions Matrix */}
            <section>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Permission Overrides</h3>
                <div className="relative w-64">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search permissions..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-background border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
              
              <div className="bg-muted/30 rounded-lg border overflow-hidden">
                <table className="w-full text-sm text-left">
                  <thead className="bg-muted/50 border-b">
                    <tr>
                      <th className="px-4 py-3 font-medium">Module</th>
                      <th className="px-4 py-3 font-medium">Permission</th>
                      <th className="px-4 py-3 font-medium text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {filteredPermissions.map(perm => {
                      const isGranted = grantedOverrides.includes(perm.name)
                      const isRevoked = revokedOverrides.includes(perm.name)
                      const isEffective = userProfile?.effectivePermissions.includes(perm.name) || isGranted
                      
                      let statusBadge = (
                        <span className="px-2 py-1 bg-secondary text-secondary-foreground rounded-full text-xs">
                          {isEffective ? 'Inherited' : 'None'}
                        </span>
                      )
                      
                      if (isGranted) {
                        statusBadge = <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">Granted (Direct)</span>
                      } else if (isRevoked) {
                        statusBadge = <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">Revoked (Direct)</span>
                      }
                      
                      return (
                        <tr 
                          key={perm.id} 
                          className="hover:bg-muted/30 cursor-pointer transition-colors"
                          onClick={() => handleTogglePermission(perm.name)}
                        >
                          <td className="px-4 py-3 font-medium text-muted-foreground">{perm.name.split(':')[0] || 'App'}</td>
                          <td className="px-4 py-3">{perm.name}</td>
                          <td className="px-4 py-3 text-center">{statusBadge}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        )}

        <div className="p-6 border-t bg-muted/20 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded-md hover:bg-muted transition-colors text-sm font-medium"
          >
            Cancel
          </button>
          <PermissionGuard permission="users:role_assign">
            <button
              onClick={handleSave}
              disabled={isSaving || isLoading}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors text-sm font-medium flex items-center gap-2 disabled:opacity-50"
            >
              {isSaving ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground"></div>
              ) : (
                <Save className="h-4 w-4" />
              )}
              Save Changes
            </button>
          </PermissionGuard>
        </div>
      </div>
    </div>
  )
}
