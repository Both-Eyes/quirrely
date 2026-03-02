import { Shield, ShieldCheck, ShieldAlert, Info } from 'lucide-react';
import { clsx } from 'clsx';
import { Badge } from '@/components/ui';

interface SafetyBadgeProps {
  score: number;
  trustLevel?: 'new' | 'standard' | 'trusted' | 'authority';
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const getTrustConfig = (trustLevel: string) => {
  const configs = {
    new: {
      icon: Shield,
      label: 'New User',
      color: 'text-gray-500',
      bg: 'bg-gray-100 dark:bg-gray-800',
    },
    standard: {
      icon: Shield,
      label: 'Standard',
      color: 'text-blue-500',
      bg: 'bg-blue-100 dark:bg-blue-900/30',
    },
    trusted: {
      icon: ShieldCheck,
      label: 'Trusted',
      color: 'text-green-500',
      bg: 'bg-green-100 dark:bg-green-900/30',
    },
    authority: {
      icon: ShieldCheck,
      label: 'Authority',
      color: 'text-amber-500',
      bg: 'bg-amber-100 dark:bg-amber-900/30',
    },
  };
  return configs[trustLevel as keyof typeof configs] || configs.standard;
};

export const SafetyBadge = ({
  score,
  trustLevel = 'standard',
  showLabel = false,
  size = 'md',
}: SafetyBadgeProps) => {
  const config = getTrustConfig(trustLevel);
  const Icon = config.icon;

  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  if (showLabel) {
    return (
      <Badge
        variant={trustLevel === 'authority' ? 'gold' : 'default'}
        className={clsx(config.bg, config.color)}
      >
        <Icon className={clsx(sizes[size], 'mr-1')} />
        {config.label}
      </Badge>
    );
  }

  return (
    <div
      className={clsx(
        'inline-flex items-center justify-center rounded-full p-1.5',
        config.bg
      )}
      title={`Safety Score: ${score}% | Trust Level: ${config.label}`}
    >
      <Icon className={clsx(sizes[size], config.color)} />
    </div>
  );
};

interface SafetyScoreProps {
  score: number;
  showDetails?: boolean;
}

export const SafetyScore = ({ score, showDetails = false }: SafetyScoreProps) => {
  const getScoreColor = (s: number) => {
    if (s >= 90) return 'text-green-500';
    if (s >= 70) return 'text-amber-500';
    return 'text-red-500';
  };

  const getScoreLabel = (s: number) => {
    if (s >= 90) return 'Excellent';
    if (s >= 70) return 'Good';
    if (s >= 50) return 'Fair';
    return 'Needs Improvement';
  };

  return (
    <div className="flex items-center gap-2">
      <div className="relative w-12 h-12">
        <svg className="w-12 h-12 transform -rotate-90">
          <circle
            cx="24"
            cy="24"
            r="20"
            stroke="currentColor"
            strokeWidth="4"
            fill="none"
            className="text-gray-200 dark:text-gray-700"
          />
          <circle
            cx="24"
            cy="24"
            r="20"
            stroke="currentColor"
            strokeWidth="4"
            fill="none"
            strokeDasharray={`${(score / 100) * 125.6} 125.6`}
            strokeLinecap="round"
            className={getScoreColor(score)}
          />
        </svg>
        <span className={clsx(
          'absolute inset-0 flex items-center justify-center text-sm font-bold',
          getScoreColor(score)
        )}>
          {score}
        </span>
      </div>
      {showDetails && (
        <div>
          <p className="font-medium text-gray-900 dark:text-white">Safety Score</p>
          <p className={clsx('text-sm', getScoreColor(score))}>{getScoreLabel(score)}</p>
        </div>
      )}
    </div>
  );
};

interface ContentWarningProps {
  flags: Array<{
    type: string;
    severity: 'low' | 'medium' | 'high';
    message: string;
  }>;
}

export const ContentWarning = ({ flags }: ContentWarningProps) => {
  if (flags.length === 0) return null;

  const severityColors = {
    low: 'bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-400',
    medium: 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400',
    high: 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800 text-red-700 dark:text-red-400',
  };

  const severityIcons = {
    low: Info,
    medium: ShieldAlert,
    high: ShieldAlert,
  };

  return (
    <div className="space-y-2">
      {flags.map((flag, index) => {
        const Icon = severityIcons[flag.severity];
        return (
          <div
            key={index}
            className={clsx(
              'flex items-start gap-3 p-3 rounded-lg border',
              severityColors[flag.severity]
            )}
          >
            <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium capitalize">{flag.type}</p>
              <p className="text-sm opacity-90">{flag.message}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
