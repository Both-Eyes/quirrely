import { useEffect } from 'react';
import { clsx } from 'clsx';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { useNotificationStore, Notification, NotificationType } from '@/stores';

const icons: Record<NotificationType, React.ReactNode> = {
  success: <CheckCircle className="h-5 w-5 text-green-500" />,
  error: <AlertCircle className="h-5 w-5 text-red-500" />,
  warning: <AlertTriangle className="h-5 w-5 text-amber-500" />,
  info: <Info className="h-5 w-5 text-blue-500" />,
};

const backgrounds: Record<NotificationType, string> = {
  success: 'bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800',
  error: 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800',
  warning: 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800',
  info: 'bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800',
};

interface ToastItemProps {
  notification: Notification;
  onDismiss: (id: string) => void;
}

const ToastItem = ({ notification, onDismiss }: ToastItemProps) => {
  return (
    <div
      className={clsx(
        'flex items-start gap-3 p-4 rounded-lg border shadow-lg',
        'animate-in slide-in-from-right-full duration-300',
        backgrounds[notification.type]
      )}
      role="alert"
    >
      <div className="flex-shrink-0">{icons[notification.type]}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
          {notification.title}
        </p>
        {notification.message && (
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {notification.message}
          </p>
        )}
      </div>
      {notification.dismissible && (
        <button
          onClick={() => onDismiss(notification.id)}
          className="flex-shrink-0 p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
        >
          <X className="h-4 w-4 text-gray-500" />
        </button>
      )}
    </div>
  );
};

export const ToastContainer = () => {
  const { notifications, removeNotification } = useNotificationStore();

  if (notifications.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full">
      {notifications.map((notification) => (
        <ToastItem
          key={notification.id}
          notification={notification}
          onDismiss={removeNotification}
        />
      ))}
    </div>
  );
};

// Hook for easy toast usage
export const useToast = () => {
  const { success, error, warning, info, addNotification } = useNotificationStore();
  return { success, error, warning, info, toast: addNotification };
};
