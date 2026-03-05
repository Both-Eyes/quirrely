import { NavLink, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import {
  LayoutDashboard,
  BookOpen,
  Bookmark,
  Flame,
  Compass,
  PenTool,
  FileText,
  BarChart3,
  Route,
  Users,
  Star,
  Crown,
  Trophy,
  TrendingUp,
  Settings,
  HelpCircle,
  Heart,
  X,
} from 'lucide-react';
import { useUIStore, useAuthStore } from '@/stores';
import { Avatar, Badge } from '@/components/ui';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  badge?: string | number;
  requiredTier?: string[];
  requiredAddon?: string;
  tierOrAddon?: boolean; // If true, user needs tier OR addon (not both)
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const navigation: NavSection[] = [
  {
    title: 'Reader',
    items: [
      { label: 'Dashboard', href: '/dashboard', icon: <LayoutDashboard className="h-5 w-5" /> },
      { label: 'Discover', href: '/reader/discover', icon: <Compass className="h-5 w-5" /> },
      { label: 'Bookmarks', href: '/reader/bookmarks', icon: <Bookmark className="h-5 w-5" /> },
      { label: 'Reading Streak', href: '/reader/streak', icon: <Flame className="h-5 w-5" /> },
    ],
  },
  {
    title: 'Writer',
    items: [
      { label: 'My Writing', href: '/writer/posts', icon: <PenTool className="h-5 w-5" /> },
      { label: 'Drafts', href: '/writer/drafts', icon: <FileText className="h-5 w-5" /> },
      { label: 'Voice Profile', href: '/dashboard/voice', icon: <Star className="h-5 w-5" />, requiredAddon: 'voice_style' },
      { label: 'Writing Partnership', href: '/dashboard/partnership', icon: <Heart className="h-5 w-5" />, requiredTier: ['pro', 'curator', 'featured_writer', 'featured_curator', 'authority_writer', 'authority_curator'] },
      { label: 'Analytics', href: '/writer/analytics', icon: <BarChart3 className="h-5 w-5" />, requiredTier: ['pro', 'curator', 'featured_writer', 'featured_curator', 'authority_writer', 'authority_curator'] },
    ],
  },
  {
    title: 'Curator',
    items: [
      { label: 'My Paths', href: '/curator/paths', icon: <Route className="h-5 w-5" />, requiredTier: ['curator', 'featured_curator', 'authority_curator'], requiredAddon: 'voice_style', tierOrAddon: true },
      { label: 'Path Followers', href: '/curator/followers', icon: <Users className="h-5 w-5" />, requiredTier: ['curator', 'featured_curator', 'authority_curator'], requiredAddon: 'voice_style', tierOrAddon: true },
      { label: 'Featured', href: '/curator/featured', icon: <Star className="h-5 w-5" />, requiredTier: ['featured_curator', 'authority_curator'], requiredAddon: 'voice_style', tierOrAddon: true },
    ],
  },
  {
    title: 'Authority',
    items: [
      { label: 'Authority Hub', href: '/authority/hub', icon: <Crown className="h-5 w-5" />, requiredTier: ['featured_writer', 'featured_curator', 'authority_writer', 'authority_curator'], requiredAddon: 'voice_style', tierOrAddon: true },
      { label: 'Leaderboard', href: '/authority/leaderboard', icon: <Trophy className="h-5 w-5" />, requiredTier: ['featured_writer', 'featured_curator', 'authority_writer', 'authority_curator'], requiredAddon: 'voice_style', tierOrAddon: true },
      { label: 'Impact Stats', href: '/authority/impact', icon: <TrendingUp className="h-5 w-5" />, requiredTier: ['featured_writer', 'featured_curator', 'authority_writer', 'authority_curator'], requiredAddon: 'voice_style', tierOrAddon: true },
    ],
  },
];

const bottomNav: NavItem[] = [
  { label: 'Settings', href: '/dashboard/settings', icon: <Settings className="h-5 w-5" /> },
  { label: 'Help & Support', href: '/help', icon: <HelpCircle className="h-5 w-5" /> },
];

export const Sidebar = () => {
  const { sidebarOpen, sidebarCollapsed, setSidebarOpen } = useUIStore();
  const { user } = useAuthStore();
  const location = useLocation();

  const userTier = user?.tier || 'free';
  const userAddons = user?.addons || [];

  const hasAccess = (item: NavItem) => {
    const hasTier = !item.requiredTier || item.requiredTier.includes(userTier);
    const hasAddon = !item.requiredAddon || userAddons.includes(item.requiredAddon as any);
    
    // If tierOrAddon is true, user needs EITHER the tier OR the addon
    if (item.tierOrAddon) {
      const meetsTier = item.requiredTier?.includes(userTier) ?? false;
      const meetsAddon = item.requiredAddon ? userAddons.includes(item.requiredAddon as any) : false;
      return meetsTier || meetsAddon;
    }
    
    // Otherwise, user needs to meet BOTH requirements (if specified)
    return hasTier && hasAddon;
  };

  const filteredNavigation = navigation.map((section) => ({
    ...section,
    items: section.items.filter((item) => hasAccess(item)),
  })).filter((section) => section.items.length > 0);

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden transition-opacity duration-300 ease-out"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800',
          'transition-transform duration-300 ease-out will-change-transform lg:translate-x-0 lg:static lg:z-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Mobile close button */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800 lg:hidden">
          <span className="font-semibold text-gray-900 dark:text-white">Menu</span>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Profile card */}
        {user && (
          <div className="p-4 border-b border-gray-200 dark:border-gray-800">
            <div className="flex items-center gap-3">
              <Avatar
                name={user.name}
                src={user.avatarUrl}
                size="lg"
                border
                borderColor={user.tier === 'authority_curator' || user.tier === 'authority_writer' ? 'gold' : 'default'}
              />
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-900 dark:text-white truncate">
                  {user.name}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                  @{user.handle}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-6">
          {filteredNavigation.map((section) => (
            <div key={section.title}>
              <h3 className="px-3 mb-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {section.title}
              </h3>
              <ul className="space-y-1">
                {section.items.map((item) => (
                  <li key={item.href}>
                    <NavLink
                      to={item.href}
                      onClick={() => setSidebarOpen(false)}
                      className={({ isActive }) =>
                        clsx(
                          'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                          isActive
                            ? 'bg-coral-500 text-white'
                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                        )
                      }
                    >
                      {item.icon}
                      <span className="flex-1">{item.label}</span>
                      {item.badge && (
                        <Badge
                          variant="primary"
                          size="sm"
                          className={clsx(
                            location.pathname === item.href && 'bg-white/20 text-white'
                          )}
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        {/* Bottom navigation */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-800">
          <ul className="space-y-1">
            {bottomNav.map((item) => (
              <li key={item.href}>
                <NavLink
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    clsx(
                      'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                    )
                  }
                >
                  {item.icon}
                  <span>{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      </aside>
    </>
  );
};
