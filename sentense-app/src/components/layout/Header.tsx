import { Link } from 'react-router-dom';
import { Menu, Moon, Sun, Bell, LogOut, Settings, User as UserIcon } from 'lucide-react';
import { clsx } from 'clsx';
import { useAuthStore, useUIStore } from '@/stores';
import { Avatar, Badge, Button } from '@/components/ui';

// Logo component
const Logo = () => (
  <Link to="/" className="flex items-center gap-3">
    <svg viewBox="0 0 100 120" width="36" height="43" className="flex-shrink-0">
      <path d="M58 112 Q85 98, 94 62 Q100 26, 74 8 Q50 -8, 42 22 Q38 44, 54 60 Q70 78, 62 100 Q58 110, 58 112" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
      <ellipse cx="40" cy="98" rx="22" ry="26" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
      <ellipse cx="40" cy="78" rx="9" ry="4" fill="#E85A5A"/>
      <path d="M31 78 Q30 94, 40 99 Q50 94, 49 78 Z" fill="#FF6B6B"/>
      <ellipse cx="40" cy="50" rx="22" ry="20" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
      <ellipse cx="32" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>
      <ellipse cx="48" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>
      <circle cx="33" cy="46.5" r="2" fill="#FFF"/>
      <circle cx="49" cy="46.5" r="2" fill="#FFF"/>
      <ellipse cx="40" cy="60" rx="4.5" ry="3.5" fill="#4A4A4A"/>
    </svg>
    <span className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
      Quirrely
    </span>
  </Link>
);

// Tier badge mapping
const tierBadges: Record<string, { label: string; variant: 'default' | 'primary' | 'gold' | 'success' }> = {
  free: { label: 'Free', variant: 'default' },
  pro: { label: 'Pro', variant: 'primary' },
  curator: { label: 'Curator', variant: 'primary' },
  featured_writer: { label: 'Featured Writer', variant: 'primary' },
  featured_curator: { label: 'Featured Curator', variant: 'primary' },
  authority_writer: { label: 'Authority Writer', variant: 'gold' },
  authority_curator: { label: 'Authority Curator', variant: 'gold' },
};

// Addon badges shown alongside tier
const addonBadges: Record<string, { label: string; variant: 'success' }> = {
  voice_style: { label: 'Voice + Style', variant: 'success' },
};

interface HeaderProps {
  variant?: 'public' | 'dashboard';
}

export const Header = ({ variant = 'dashboard' }: HeaderProps) => {
  const { user, isAuthenticated, logout } = useAuthStore();
  const { toggleTheme, effectiveTheme, toggleSidebar } = useUIStore();

  const tierBadge = user?.tier ? tierBadges[user.tier] : null;
  const userAddons = user?.addons || [];

  return (
    <header
      className={clsx(
        'sticky top-0 z-40 h-16 flex items-center justify-between px-4 lg:px-6',
        'border-b transition-colors duration-200',
        variant === 'dashboard'
          ? 'bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800'
          : 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-transparent'
      )}
    >
      {/* Left section */}
      <div className="flex items-center gap-4">
        {variant === 'dashboard' && (
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 lg:hidden"
            aria-label="Toggle sidebar"
          >
            <Menu className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          </button>
        )}
        <Logo />
        <div className="hidden sm:flex items-center gap-2">
          {tierBadge && (
            <Badge variant={tierBadge.variant} size="sm">
              {tierBadge.variant === 'gold' && '👑 '}
              {tierBadge.label}
            </Badge>
          )}
          {userAddons.map((addon) => {
            const addonBadge = addonBadges[addon];
            return addonBadge ? (
              <Badge key={addon} variant={addonBadge.variant} size="sm">
                ✨ {addonBadge.label}
              </Badge>
            ) : null;
          })}
        </div>
      </div>

      {/* Right section */}
      <div className="flex items-center gap-2">
        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          aria-label="Toggle theme"
        >
          {effectiveTheme === 'dark' ? (
            <Sun className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          ) : (
            <Moon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          )}
        </button>

        {isAuthenticated && user ? (
          <>
            {/* Notifications */}
            <button
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors relative"
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 bg-coral-500 rounded-full" />
            </button>

            {/* Country flag */}
            {user.countryFlag && (
              <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-lg bg-gray-100 dark:bg-gray-800 text-sm">
                <span>{user.countryFlag}</span>
                <span className="text-gray-600 dark:text-gray-400">{user.country}</span>
              </div>
            )}

            {/* User menu */}
            <div className="relative group">
              <button className="flex items-center gap-2 p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                <Avatar
                  name={user.name}
                  src={user.avatarUrl}
                  size="sm"
                  border
                  borderColor={(user.tier === 'authority_curator' || user.tier === 'authority_writer') ? 'gold' : 'default'}
                />
              </button>

              {/* Dropdown */}
              <div className="absolute right-0 mt-2 w-56 py-2 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-800">
                  <p className="font-medium text-gray-900 dark:text-white">{user.name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{user.email}</p>
                </div>
                <Link
                  to="/dashboard/settings"
                  className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  <Settings className="h-4 w-4" />
                  Settings
                </Link>
                <Link
                  to="/dashboard"
                  className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  <UserIcon className="h-4 w-4" />
                  Profile
                </Link>
                <hr className="my-2 border-gray-200 dark:border-gray-800" />
                <button
                  onClick={() => logout()}
                  className="flex items-center gap-3 w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30"
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex items-center gap-2">
            <Link to="/login">
              <Button variant="ghost" size="sm">
                Log in
              </Button>
            </Link>
            <Link to="/signup">
              <Button size="sm">Sign up</Button>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
