import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores';
import { Skeleton } from '@/components/ui';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredTier?: string[];
  requiredAddon?: string;
  tierOrAddon?: boolean; // If true, user needs tier OR addon (not both)
}

export const ProtectedRoute = ({ 
  children, 
  requiredTier, 
  requiredAddon,
  tierOrAddon = false,
}: ProtectedRouteProps) => {
  const { isAuthenticated, isInitialized, isLoading, user } = useAuthStore();
  const location = useLocation();

  // Show loading while checking auth
  if (!isInitialized || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="w-full max-w-md p-8 space-y-4">
          <Skeleton variant="rectangular" height={48} />
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="80%" />
          <Skeleton variant="text" width="40%" />
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check access requirements
  if (user && (requiredTier || requiredAddon)) {
    const hasTier = !requiredTier || requiredTier.includes(user.tier);
    const hasAddon = !requiredAddon || user.addons?.includes(requiredAddon as any);
    
    let hasAccess: boolean;
    
    if (tierOrAddon) {
      // User needs tier OR addon
      const meetsTier = requiredTier?.includes(user.tier) ?? false;
      const meetsAddon = requiredAddon ? user.addons?.includes(requiredAddon as any) : false;
      hasAccess = meetsTier || meetsAddon;
    } else {
      // User needs both (if both specified)
      hasAccess = hasTier && hasAddon;
    }
    
    if (!hasAccess) {
      return <Navigate to="/dashboard" replace />;
    }
  }

  return <>{children}</>;
};
