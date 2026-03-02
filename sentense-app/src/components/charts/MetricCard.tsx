import { clsx } from 'clsx';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card } from '@/components/ui';

export interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
    period?: string;
  };
  icon?: React.ReactNode;
  variant?: 'default' | 'gold' | 'success' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export const MetricCard = ({
  label,
  value,
  unit,
  trend,
  icon,
  variant = 'default',
  size = 'md',
  loading = false,
}: MetricCardProps) => {
  const variants = {
    default: {
      card: '',
      value: 'text-gray-900 dark:text-white',
      icon: 'bg-coral-100 dark:bg-coral-900/30 text-coral-500',
    },
    gold: {
      card: 'bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-950/30 dark:to-yellow-950/30 border-amber-300 dark:border-amber-700',
      value: 'text-amber-700 dark:text-amber-400',
      icon: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600',
    },
    success: {
      card: '',
      value: 'text-green-600 dark:text-green-400',
      icon: 'bg-green-100 dark:bg-green-900/30 text-green-500',
    },
    warning: {
      card: '',
      value: 'text-amber-600 dark:text-amber-400',
      icon: 'bg-amber-100 dark:bg-amber-900/30 text-amber-500',
    },
  };

  const sizes = {
    sm: {
      value: 'text-2xl',
      label: 'text-xs',
      icon: 'p-2',
      padding: 'p-4',
    },
    md: {
      value: 'text-3xl',
      label: 'text-sm',
      icon: 'p-3',
      padding: 'p-5',
    },
    lg: {
      value: 'text-4xl',
      label: 'text-base',
      icon: 'p-4',
      padding: 'p-6',
    },
  };

  const trendColors = {
    up: 'text-green-600 dark:text-green-400',
    down: 'text-red-500 dark:text-red-400',
    neutral: 'text-gray-500 dark:text-gray-400',
  };

  const TrendIcon = {
    up: TrendingUp,
    down: TrendingDown,
    neutral: Minus,
  };

  if (loading) {
    return (
      <Card className={clsx(sizes[size].padding, variants[variant].card, 'animate-pulse')}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-3" />
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-16 mb-2" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20" />
          </div>
          <div className="h-12 w-12 bg-gray-200 dark:bg-gray-700 rounded-xl" />
        </div>
      </Card>
    );
  }

  return (
    <Card className={clsx(sizes[size].padding, variants[variant].card)}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className={clsx(
            'font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide',
            sizes[size].label
          )}>
            {label}
          </p>
          <p className={clsx(
            'font-bold mt-1 truncate',
            sizes[size].value,
            variants[variant].value
          )}>
            {value}
            {unit && (
              <span className="text-lg font-normal text-gray-500 dark:text-gray-400 ml-1">
                {unit}
              </span>
            )}
          </p>
          {trend && (
            <div className={clsx(
              'flex items-center gap-1 mt-2 text-sm',
              trendColors[trend.direction]
            )}>
              {(() => {
                const Icon = TrendIcon[trend.direction];
                return <Icon className="h-4 w-4" />;
              })()}
              <span>
                {trend.direction !== 'neutral' && (trend.direction === 'up' ? '+' : '-')}
                {Math.abs(trend.value)}%
                {trend.period && ` ${trend.period}`}
              </span>
            </div>
          )}
        </div>
        {icon && (
          <div className={clsx(
            'rounded-xl flex-shrink-0',
            sizes[size].icon,
            variants[variant].icon
          )}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};
