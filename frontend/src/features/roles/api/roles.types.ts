export interface RoleCreate {
  name: string
  display_name: string
  description: string | null
}

export interface RoleResponse {
  id: string
  name: string
  display_name: string
  description: string | null
}
