import { ReactNode } from 'react';
import { clsx } from 'clsx';
import { Button } from './Button';

// Quirrely squirrel mascot variants for empty states
const SquirrelMascot = ({ variant = 'default' }: { variant?: 'default' | 'searching' | 'thinking' | 'happy' }) => {
  // Different expressions based on variant
  const expressions = {
    default: { leftEyeY: 48, rightEyeY: 48, beakSymbol: null },
    searching: { leftEyeY: 46, rightEyeY: 50, beakSymbol: '🔍' },
    thinking: { leftEyeY: 48, rightEyeY: 48, beakSymbol: '?' },
    happy: { leftEyeY: 48, rightEyeY: 48, beakSymbol: '♥' },
  };

  const expr = expressions[variant];

  return (
    <svg viewBox="0 0 100 120" className="w-full h-full">
      {/* Tail */}
      <path 
        d="M58 112 Q85 98, 94 62 Q100 26, 74 8 Q50 -8, 42 22 Q38 44, 54 60 Q70 78, 62 100 Q58 110, 58 112" 
        fill="#FFFEF9" 
        stroke="#E0DBD5" 
        strokeWidth="1.4"
      />
      {/* Body */}
      <ellipse cx="40" cy="98" rx="22" ry="26" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
      {/* Cheeks - coral brand color */}
      <ellipse cx="40" cy="78" rx="9" ry="4" fill="#E85A5A"/>
      <path d="M31 78 Q30 94, 40 99 Q50 94, 49 78 Z" fill="#FF6B6B"/>
      {/* Head */}
      <ellipse cx="40" cy="50" rx="22" ry="20" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
      {/* Eyes */}
      <ellipse cx="32" cy={expr.leftEyeY} rx="5.5" ry="6" fill="#1a1a1a"/>
      <ellipse cx="48" cy={expr.rightEyeY} rx="5.5" ry="6" fill="#1a1a1a"/>
      {/* Eye highlights */}
      <circle cx="33" cy={expr.leftEyeY - 1.5} r="2" fill="#FFF"/>
      <circle cx="49" cy={expr.rightEyeY - 1.5} r="2" fill="#FFF"/>
      {/* Nose or symbol */}
      {expr.beakSymbol ? (
        <text x="40" y="65" textAnchor="middle" fill="#FF6B6B" fontSize="12" fontWeight="bold">
          {expr.beakSymbol}
        </text>
      ) : (
        <ellipse cx="40" cy="60" rx="4.5" ry="3.5" fill="#4A4A4A"/>
      )}
    </svg>
  );
};

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
    variant?: 'primary' | 'outline';
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
  /** Use Quirrely squirrel instead of custom icon */
  useSquirrel?: boolean;
  /** Squirrel expression variant */
  squirrelVariant?: 'default' | 'searching' | 'thinking' | 'happy';
}

export const EmptyState = ({
  icon,
  title,
  description,
  action,
  secondaryAction,
  className,
  useSquirrel = false,
  squirrelVariant = 'default',
}: EmptyStateProps) => {
  return (
    <div className={clsx('text-center py-12 px-4', className)}>
      {useSquirrel ? (
        <div className="w-24 h-28 mx-auto mb-4 opacity-60">
          <SquirrelMascot variant={squirrelVariant} />
        </div>
      ) : icon ? (
        <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
          <div className="text-gray-400 dark:text-gray-500">{icon}</div>
        </div>
      ) : null}
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        {title}
      </h3>
      {description && (
        <p className="text-gray-500 dark:text-gray-400 max-w-sm mx-auto mb-6">
          {description}
        </p>
      )}
      {(action || secondaryAction) && (
        <div className="flex gap-3 justify-center">
          {action && (
            <Button
              variant={action.variant || 'primary'}
              onClick={action.onClick}
            >
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button variant="ghost" onClick={secondaryAction.onClick}>
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

// Export squirrel for use in other components
export { SquirrelMascot };
