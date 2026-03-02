import { HTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'shimmer' | 'none';
}

export const Skeleton = forwardRef<HTMLDivElement, SkeletonProps>(
  (
    {
      className,
      variant = 'text',
      width,
      height,
      animation = 'pulse',
      style,
      ...props
    },
    ref
  ) => {
    const variants = {
      text: 'rounded',
      circular: 'rounded-full',
      rectangular: 'rounded-lg',
    };

    const animations = {
      pulse: 'animate-pulse',
      shimmer: 'animate-shimmer bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%]',
      none: '',
    };

    return (
      <div
        ref={ref}
        className={clsx(
          'bg-gray-200 dark:bg-gray-800',
          variants[variant],
          animations[animation],
          className
        )}
        style={{
          width: width,
          height: height || (variant === 'text' ? '1em' : undefined),
          ...style,
        }}
        {...props}
      />
    );
  }
);

Skeleton.displayName = 'Skeleton';

// Preset skeleton components
export const SkeletonText = ({ lines = 3 }: { lines?: number }) => (
  <div className="space-y-2">
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton
        key={i}
        variant="text"
        width={i === lines - 1 ? '75%' : '100%'}
        height="0.875rem"
      />
    ))}
  </div>
);

export const SkeletonCard = () => (
  <div className="p-5 rounded-xl border border-gray-200 dark:border-gray-800">
    <div className="flex items-center gap-3 mb-4">
      <Skeleton variant="circular" width={40} height={40} />
      <div className="flex-1">
        <Skeleton variant="text" width="50%" height="1rem" className="mb-1" />
        <Skeleton variant="text" width="30%" height="0.75rem" />
      </div>
    </div>
    <SkeletonText lines={3} />
  </div>
);

export const SkeletonAvatar = ({ size = 40 }: { size?: number }) => (
  <Skeleton variant="circular" width={size} height={size} />
);
