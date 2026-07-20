import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react'

interface PaginationProps {
  page: number
  size: number
  total: number
  onPageChange: (page: number) => void
  onSizeChange: (size: number) => void
}

export function Pagination({ page, size, total, onPageChange, onSizeChange }: PaginationProps) {
  const totalPages = Math.ceil(total / size) || 1

  return (
    <div className="flex items-center justify-between px-2 py-4">
      <div className="flex-1 text-sm text-muted-foreground">
        Showing {total === 0 ? 0 : (page - 1) * size + 1} to {Math.min(page * size, total)} of {total} entries
      </div>
      <div className="flex items-center space-x-6 lg:space-x-8">
        <div className="flex items-center space-x-2">
          <p className="text-sm font-medium">Rows per page</p>
          <select
            className="h-8 w-[70px] rounded-md border border-input bg-transparent px-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            value={size}
            onChange={(e) => {
              onSizeChange(Number(e.target.value))
            }}
          >
            {[10, 20, 30, 40, 50].map((pageSize) => (
              <option key={pageSize} value={pageSize}>
                {pageSize}
              </option>
            ))}
          </select>
        </div>
        <div className="flex w-[100px] items-center justify-center text-sm font-medium">
          Page {page} of {totalPages}
        </div>
        <div className="flex items-center space-x-2">
          <button
            className="h-8 w-8 p-0 flex items-center justify-center rounded-md border border-input bg-transparent hover:bg-accent disabled:opacity-50"
            onClick={() => onPageChange(1)}
            disabled={page === 1}
          >
            <span className="sr-only">Go to first page</span>
            <ChevronsLeft className="h-4 w-4" />
          </button>
          <button
            className="h-8 w-8 p-0 flex items-center justify-center rounded-md border border-input bg-transparent hover:bg-accent disabled:opacity-50"
            onClick={() => onPageChange(page - 1)}
            disabled={page === 1}
          >
            <span className="sr-only">Go to previous page</span>
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            className="h-8 w-8 p-0 flex items-center justify-center rounded-md border border-input bg-transparent hover:bg-accent disabled:opacity-50"
            onClick={() => onPageChange(page + 1)}
            disabled={page === totalPages}
          >
            <span className="sr-only">Go to next page</span>
            <ChevronRight className="h-4 w-4" />
          </button>
          <button
            className="h-8 w-8 p-0 flex items-center justify-center rounded-md border border-input bg-transparent hover:bg-accent disabled:opacity-50"
            onClick={() => onPageChange(totalPages)}
            disabled={page === totalPages}
          >
            <span className="sr-only">Go to last page</span>
            <ChevronsRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
