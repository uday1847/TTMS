import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { driverApi } from '../api/driver.api'
import { useNotificationStore } from '@/stores/notification-store'
import type { DriverCreateDto, DriverUpdateDto } from '../types/driver.types'

export function useDrivers(params?: {
  page?: number
  size?: number
  q?: string
  status?: string
  sort_by?: string
  order?: string
  include_deleted?: boolean
}) {
  return useQuery({
    queryKey: ['drivers', params],
    queryFn: () => driverApi.list(params),
  })
}

export function useDriver(id: string) {
  return useQuery({
    queryKey: ['driver', id],
    queryFn: () => driverApi.get(id),
    enabled: !!id,
  })
}

export function useCreateDriver() {
  const queryClient = useQueryClient()
  const { addNotification } = useNotificationStore()

  return useMutation({
    mutationFn: (data: DriverCreateDto) => driverApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] })
      addNotification({ title: 'Success', message: 'Driver created successfully', type: 'success' })
    },
    onError: (error: any) => {
      addNotification({ title: 'Error', message: error?.response?.data?.message || 'Failed to create driver', type: 'error' })
    },
  })
}

export function useUpdateDriver() {
  const queryClient = useQueryClient()
  const { addNotification } = useNotificationStore()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DriverUpdateDto }) => driverApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] })
      queryClient.invalidateQueries({ queryKey: ['driver', variables.id] })
      addNotification({ title: 'Success', message: 'Driver updated successfully', type: 'success' })
    },
    onError: (error: any) => {
      addNotification({ title: 'Error', message: error?.response?.data?.message || 'Failed to update driver', type: 'error' })
    },
  })
}

export function useDeleteDriver() {
  const queryClient = useQueryClient()
  const { addNotification } = useNotificationStore()

  return useMutation({
    mutationFn: (id: string) => driverApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] })
      addNotification({ title: 'Success', message: 'Driver deleted successfully', type: 'success' })
    },
    onError: (error: any) => {
      addNotification({ title: 'Error', message: error?.response?.data?.message || 'Failed to delete driver', type: 'error' })
    },
  })
}

export function useUpdateDriverStatus() {
  const queryClient = useQueryClient()
  const { addNotification } = useNotificationStore()

  return useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) => driverApi.updateStatus(id, isActive),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] })
      queryClient.invalidateQueries({ queryKey: ['driver', variables.id] })
      addNotification({ title: 'Success', message: 'Driver status updated successfully', type: 'success' })
    },
    onError: (error: any) => {
      addNotification({ title: 'Error', message: error?.response?.data?.message || 'Failed to update driver status', type: 'error' })
    },
  })
}
