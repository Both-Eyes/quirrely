import { Skeleton } from './Skeleton';

export const PageLoader = () => (
  <div className="space-y-6 animate-pulse">
    {/* Header skeleton */}
    <div className="flex items-center justify-between">
      <div>
        <Skeleton variant="text" width={200} height={32} className="mb-2" />
        <Skeleton variant="text" width={300} height={20} />
      </div>
      <Skeleton variant="rectangular" width={120} height={40} className="rounded-lg" />
    </div>

    {/* Stats grid skeleton */}
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array(4).fill(0).map((_, i) => (
        <div key={i} className="p-5 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
          <Skeleton variant="text" width="60%" height={16} className="mb-3" />
          <Skeleton variant="text" width="40%" height={32} className="mb-2" />
          <Skeleton variant="text" width="50%" height={14} />
        </div>
      ))}
    </div>

    {/* Content skeleton */}
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
        <Skeleton variant="text" width={150} height={24} className="mb-4" />
        <div className="flex gap-6">
          <Skeleton variant="circular" width={200} height={200} />
          <div className="flex-1 space-y-3">
            <Skeleton variant="text" width="70%" height={24} />
            <Skeleton variant="text" width="100%" height={16} />
            <Skeleton variant="text" width="90%" height={16} />
            <Skeleton variant="text" width="80%" height={16} />
          </div>
        </div>
      </div>
      <div className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
        <Skeleton variant="text" width={120} height={24} className="mb-4" />
        <div className="space-y-4">
          {Array(4).fill(0).map((_, i) => (
            <div key={i} className="flex items-start gap-3">
              <Skeleton variant="circular" width={40} height={40} />
              <div className="flex-1">
                <Skeleton variant="text" width="80%" height={16} className="mb-1" />
                <Skeleton variant="text" width="40%" height={12} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

export const CardLoader = () => (
  <div className="p-5 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 animate-pulse">
    <div className="flex items-center gap-3 mb-4">
      <Skeleton variant="circular" width={40} height={40} />
      <div>
        <Skeleton variant="text" width={120} height={16} className="mb-1" />
        <Skeleton variant="text" width={80} height={12} />
      </div>
    </div>
    <Skeleton variant="text" width="80%" height={20} className="mb-2" />
    <Skeleton variant="text" width="100%" height={14} className="mb-1" />
    <Skeleton variant="text" width="90%" height={14} className="mb-4" />
    <div className="flex gap-2">
      <Skeleton variant="rectangular" width={60} height={24} className="rounded-full" />
      <Skeleton variant="rectangular" width={60} height={24} className="rounded-full" />
    </div>
  </div>
);

export const TableLoader = ({ rows = 5 }: { rows?: number }) => (
  <div className="animate-pulse">
    {/* Header */}
    <div className="flex items-center gap-4 p-4 border-b border-gray-200 dark:border-gray-800">
      <Skeleton variant="text" width="20%" height={16} />
      <Skeleton variant="text" width="30%" height={16} />
      <Skeleton variant="text" width="15%" height={16} />
      <Skeleton variant="text" width="15%" height={16} />
    </div>
    {/* Rows */}
    {Array(rows).fill(0).map((_, i) => (
      <div key={i} className="flex items-center gap-4 p-4 border-b border-gray-100 dark:border-gray-800">
        <Skeleton variant="circular" width={32} height={32} />
        <div className="flex-1">
          <Skeleton variant="text" width="60%" height={16} className="mb-1" />
          <Skeleton variant="text" width="40%" height={12} />
        </div>
        <Skeleton variant="text" width={60} height={16} />
        <Skeleton variant="text" width={80} height={16} />
      </div>
    ))}
  </div>
);
