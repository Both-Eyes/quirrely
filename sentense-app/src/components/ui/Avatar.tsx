import { HTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

export interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'circle' | 'rounded';
  status?: 'online' | 'offline' | 'away' | 'busy';
  border?: boolean;
  borderColor?: 'default' | 'gold' | 'coral';
}

const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map((word) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

const getColorFromName = (name: string): string => {
  const colors = [
    'bg-coral-500',
    'bg-blue-500',
    'bg-green-500',
    'bg-purple-500',
    'bg-amber-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-teal-500',
  ];
  const index = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[index % colors.length];
};

export const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  (
    {
      className,
      src,
      alt,
      name = '',
      size = 'md',
      variant = 'circle',
      status,
      border = false,
      borderColor = 'default',
      ...props
    },
    ref
  ) => {
    const sizes = {
      xs: 'h-6 w-6 text-xs',
      sm: 'h-8 w-8 text-sm',
      md: 'h-10 w-10 text-sm',
      lg: 'h-12 w-12 text-base',
      xl: 'h-16 w-16 text-lg',
    };

    const statusSizes = {
      xs: 'h-1.5 w-1.5',
      sm: 'h-2 w-2',
      md: 'h-2.5 w-2.5',
      lg: 'h-3 w-3',
      xl: 'h-4 w-4',
    };

    const statusColors = {
      online: 'bg-green-500',
      offline: 'bg-gray-400',
      away: 'bg-amber-500',
      busy: 'bg-red-500',
    };

    const borderColors = {
      default: 'ring-2 ring-gray-200 dark:ring-gray-700',
      gold: 'ring-2 ring-gold-400',
      coral: 'ring-2 ring-coral-500',
    };

    return (
      <div
        ref={ref}
        className={clsx(
          'relative inline-flex items-center justify-center overflow-hidden',
          sizes[size],
          variant === 'circle' ? 'rounded-full' : 'rounded-lg',
          border && borderColors[borderColor],
          !src && getColorFromName(name),
          className
        )}
        {...props}
      >
        {src ? (
          <img
            src={src}
            alt={alt || name}
            className="h-full w-full object-cover"
          />
        ) : (
          <span className="font-semibold text-white">
            {getInitials(name || '?')}
          </span>
        )}
        {status && (
          <span
            className={clsx(
              'absolute bottom-0 right-0 block rounded-full ring-2 ring-white dark:ring-gray-900',
              statusSizes[size],
              statusColors[status]
            )}
          />
        )}
      </div>
    );
  }
);

Avatar.displayName = 'Avatar';
