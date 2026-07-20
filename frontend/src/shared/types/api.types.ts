export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  size: number
}

export interface APIResponse<T> {
  success: boolean
  message: string
  data: T
}
