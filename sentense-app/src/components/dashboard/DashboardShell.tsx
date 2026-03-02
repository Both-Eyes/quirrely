/**
 * QUIRRELY COMPOSABLE DASHBOARD SYSTEM
 * Knight of Wands v3.0.0
 * 
 * A modular dashboard that assembles itself based on user configuration.
 * Handles all track/tier/addon permutations through composition.
 */

import React, { useState, createContext, useContext } from 'react';
import {
  Crown, Users, BookOpen, Flame, PenTool, Star, Trophy, TrendingUp,
  Settings, Bell, Moon, Sun, Menu, X, Sparkles, FileText, Route,
  BarChart3, Compass, Bookmark, HelpCircle, ChevronRight, Eye,
  Award, Heart, MessageCircle, Calendar, ArrowLeft, Filter, Search,
  Share2, Plus, Zap
} from 'lucide-react';

import type {
  UserConfig,
  FeatureAccess,
  Track,
} from './user-config';

import {
  getFeatureAccess,
  getUserBadges,
  hasWriterTrack,
  hasCuratorTrack,
  isDualTrack,
  isAuthorityTier,
  isFeaturedTier,
  hasVoiceStyle,
  canSwitchTracks,
  COUNTRY_FLAGS,
  WRITER_TIER_LEVEL,
  CURATOR_TIER_LEVEL,
} from './user-config';

// ═══════════════════════════════════════════════════════════════════════════
// CONTEXT
// ═══════════════════════════════════════════════════════════════════════════

interface DashboardContextType {
  user: UserConfig;
  features: FeatureAccess;
  darkMode: boolean;
  setDarkMode: (value: boolean) => void;
  currentView: string;
  setCurrentView: (view: string) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (value: boolean) => void;
}

const DashboardContext = createContext<DashboardContextType | null>(null);

export const useDashboard = () => {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error('useDashboard must be used within DashboardProvider');
  return ctx;
};

// ═══════════════════════════════════════════════════════════════════════════
// STYLING HELPERS
// ═══════════════════════════════════════════════════════════════════════════

const useStyles = () => {
  const { darkMode } = useDashboard();
  return {
    bg: darkMode ? 'bg-gray-950 text-gray-100' : 'bg-gray-50 text-gray-900',
    card: darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200',
    muted: darkMode ? 'text-gray-400' : 'text-gray-500',
    hover: darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-100',
    border: darkMode ? 'border-gray-800' : 'border-gray-200',
  };
};

// ═══════════════════════════════════════════════════════════════════════════
// SIDEBAR COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════

const SidebarSection: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => {
  const s = useStyles();
  return (
    <div className="mb-6">
      <h3 className={`px-3 mb-2 text-xs font-semibold ${s.muted} uppercase tracking-wider`}>{title}</h3>
      <div className="space-y-1">{children}</div>
    </div>
  );
};

const SidebarLink: React.FC<{
  icon: React.ReactNode;
  label: string;
  href?: string;
  onClick?: () => void;
  active?: boolean;
  badge?: string | number;
  badgeColor?: string;
}> = ({ icon, label, href = '#', onClick, active, badge, badgeColor = 'bg-[#FF6B6B]' }) => {
  const s = useStyles();
  const { setSidebarOpen } = useDashboard();
  
  const handleClick = (e: React.MouseEvent) => {
    if (onClick) {
      e.preventDefault();
      onClick();
    }
    setSidebarOpen(false);
  };
  
  return (
    <a
      href={href}
      onClick={handleClick}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors ${
        active ? 'bg-[#FF6B6B] text-white' : `${s.muted} ${s.hover}`
      }`}
    >
      {icon}
      <span className="flex-1">{label}</span>
      {badge !== undefined && (
        <span className={`text-xs ${active ? 'bg-white/20' : badgeColor} text-white px-2 py-0.5 rounded-full`}>
          {badge}
        </span>
      )}
    </a>
  );
};

const Sidebar: React.FC = () => {
  const { user, features, sidebarOpen, setSidebarOpen, currentView, setCurrentView } = useDashboard();
  const s = useStyles();
  const badges = getUserBadges(user);
  
  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 ${s.card} border-r transform transition-transform duration-300 ease-out lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        {/* Mobile close */}
        <div className={`flex items-center justify-between p-4 border-b ${s.border} lg:hidden`}>
          <span className="font-semibold">Menu</span>
          <button onClick={() => setSidebarOpen(false)} className={`p-2 rounded-lg ${s.hover}`}>
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* User profile */}
        <div className={`p-4 border-b ${s.border}`}>
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg ${
              isAuthorityTier(user) 
                ? 'bg-gradient-to-br from-amber-400 to-yellow-500 ring-2 ring-amber-400/50' 
                : 'bg-gradient-to-br from-coral-400 to-coral-500'
            }`}>
              {user.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold truncate">{user.name}</p>
              <p className={`text-sm ${s.muted} truncate`}>@{user.handle}</p>
            </div>
          </div>
          {/* Track badges */}
          {badges.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-3">
              {badges.map((badge, i) => (
                <span key={i} className={`text-xs px-2 py-0.5 rounded-full ${badge.bgColor} ${badge.color}`}>
                  {badge.icon} {badge.shortLabel}
                </span>
              ))}
              {hasVoiceStyle(user) && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  ✨ Voice+Style
                </span>
              )}
            </div>
          )}
        </div>
        
        {/* Navigation */}
        <nav className="flex-1 p-4 overflow-y-auto h-[calc(100vh-280px)]">
          {/* General - Always visible */}
          <SidebarSection title="General">
            <SidebarLink
              icon={<BarChart3 className="w-5 h-5" />}
              label="Dashboard"
              active={currentView === 'dashboard'}
              onClick={() => setCurrentView('dashboard')}
            />
            <SidebarLink
              icon={<Compass className="w-5 h-5" />}
              label="Discover"
              active={currentView === 'discover'}
              onClick={() => setCurrentView('discover')}
            />
            <SidebarLink
              icon={<Bookmark className="w-5 h-5" />}
              label="Bookmarks"
              active={currentView === 'bookmarks'}
              onClick={() => setCurrentView('bookmarks')}
            />
            <SidebarLink
              icon={<Flame className="w-5 h-5" />}
              label="Reading Streak"
              badge={23}
              active={currentView === 'streak'}
              onClick={() => setCurrentView('streak')}
            />
          </SidebarSection>
          
          {/* Writer Section - Shows if writer track OR voice_style addon */}
          {(hasWriterTrack(user) || hasVoiceStyle(user)) && (
            <SidebarSection title="Writer">
              {features.myWriting && (
                <SidebarLink
                  icon={<PenTool className="w-5 h-5" />}
                  label="My Writing"
                  active={currentView === 'writing'}
                  onClick={() => setCurrentView('writing')}
                />
              )}
              {features.drafts && (
                <SidebarLink
                  icon={<FileText className="w-5 h-5" />}
                  label="Drafts"
                  active={currentView === 'drafts'}
                  onClick={() => setCurrentView('drafts')}
                />
              )}
              {features.voiceProfile && (
                <SidebarLink
                  icon={<Sparkles className="w-5 h-5" />}
                  label="Voice Profile"
                  badge={features.voiceEvolution ? '✨' : undefined}
                  badgeColor="bg-emerald-500"
                  active={currentView === 'voice'}
                  onClick={() => setCurrentView('voice')}
                />
              )}
              {features.writerAnalytics && (
                <SidebarLink
                  icon={<BarChart3 className="w-5 h-5" />}
                  label="Writing Analytics"
                  active={currentView === 'writer-analytics'}
                  onClick={() => setCurrentView('writer-analytics')}
                />
              )}
            </SidebarSection>
          )}
          
          {/* Curator Section - Shows if curator track */}
          {hasCuratorTrack(user) && (
            <SidebarSection title="Curator">
              {features.readingPaths && (
                <SidebarLink
                  icon={<Route className="w-5 h-5" />}
                  label="Reading Paths"
                  active={currentView === 'paths'}
                  onClick={() => setCurrentView('paths')}
                />
              )}
              {features.pathFollowers && (
                <SidebarLink
                  icon={<Users className="w-5 h-5" />}
                  label="Path Followers"
                  active={currentView === 'path-followers'}
                  onClick={() => setCurrentView('path-followers')}
                />
              )}
              {features.featuredPaths && (
                <SidebarLink
                  icon={<Star className="w-5 h-5" />}
                  label="Featured"
                  active={currentView === 'featured-paths'}
                  onClick={() => setCurrentView('featured-paths')}
                />
              )}
              {features.curatorAnalytics && (
                <SidebarLink
                  icon={<BarChart3 className="w-5 h-5" />}
                  label="Path Analytics"
                  active={currentView === 'curator-analytics'}
                  onClick={() => setCurrentView('curator-analytics')}
                />
              )}
            </SidebarSection>
          )}
          
          {/* Authority Section - Shows if featured+ on either track */}
          {(isFeaturedTier(user) || isAuthorityTier(user)) && (
            <SidebarSection title="Authority">
              {features.authorityHub && (
                <SidebarLink
                  icon={<Crown className="w-5 h-5 text-amber-500" />}
                  label="Authority Hub"
                  active={currentView === 'authority-hub'}
                  onClick={() => setCurrentView('authority-hub')}
                />
              )}
              {features.leaderboard && (
                <SidebarLink
                  icon={<Trophy className="w-5 h-5" />}
                  label="Leaderboard"
                  active={currentView === 'leaderboard'}
                  onClick={() => setCurrentView('leaderboard')}
                />
              )}
              {features.impactStats && (
                <SidebarLink
                  icon={<TrendingUp className="w-5 h-5" />}
                  label="Impact Stats"
                  active={currentView === 'impact'}
                  onClick={() => setCurrentView('impact')}
                />
              )}
            </SidebarSection>
          )}
          
          {/* Add Track Prompt - Shows if can add a track */}
          {canSwitchTracks(user) && !isDualTrack(user) && (
            <div className={`mt-4 p-3 rounded-lg border ${s.border} ${s.hover} cursor-pointer`}>
              <div className="flex items-center gap-2 text-sm">
                <Plus className="w-4 h-4 text-[#FF6B6B]" />
                <span>Add {hasCuratorTrack(user) ? 'Writer' : 'Curator'} Track</span>
              </div>
            </div>
          )}
        </nav>
        
        {/* Bottom nav */}
        <div className={`absolute bottom-0 left-0 right-0 p-4 border-t ${s.border}`}>
          <SidebarLink
            icon={<Settings className="w-5 h-5" />}
            label="Settings"
            active={currentView === 'settings'}
            onClick={() => setCurrentView('settings')}
          />
          <SidebarLink
            icon={<HelpCircle className="w-5 h-5" />}
            label="Help & Support"
            active={currentView === 'help'}
            onClick={() => setCurrentView('help')}
          />
        </div>
      </aside>
    </>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// HEADER COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

const Header: React.FC = () => {
  const { user, darkMode, setDarkMode, setSidebarOpen } = useDashboard();
  const s = useStyles();
  const badges = getUserBadges(user);
  
  return (
    <header className={`sticky top-0 z-30 h-16 flex items-center justify-between px-4 lg:px-6 ${s.card} border-b`}>
      <div className="flex items-center gap-4">
        <button
          onClick={() => setSidebarOpen(true)}
          className={`p-2 rounded-lg ${s.hover} lg:hidden`}
        >
          <Menu className="w-5 h-5" />
        </button>
        
        {/* Logo */}
        <div className="flex items-center gap-3">
          <svg viewBox="0 0 100 120" width="32" height="38">
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
          <span className="text-xl font-bold hidden sm:block">Quirrely</span>
        </div>
        
        {/* Badges */}
        <div className="hidden sm:flex items-center gap-2">
          {badges.map((badge, i) => (
            <span key={i} className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${badge.bgColor} ${badge.color}`}>
              {badge.icon} {badge.label}
            </span>
          ))}
          {hasVoiceStyle(user) && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
              ✨ Voice + Style
            </span>
          )}
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <button
          onClick={() => setDarkMode(!darkMode)}
          className={`p-2 rounded-lg ${s.hover}`}
        >
          {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
        
        <button className={`p-2 rounded-lg ${s.hover} relative`}>
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#FF6B6B] rounded-full" />
        </button>
        
        <span className={`hidden sm:flex items-center gap-1 px-2 py-1 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-100'} text-sm`}>
          {COUNTRY_FLAGS[user.country]} {user.country}
        </span>
        
        <div className={`w-9 h-9 rounded-full flex items-center justify-center text-white font-bold text-sm ${
          isAuthorityTier(user)
            ? 'bg-gradient-to-br from-amber-400 to-yellow-500 ring-2 ring-amber-400/30'
            : 'bg-gradient-to-br from-coral-400 to-coral-500'
        }`}>
          {user.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
        </div>
      </div>
    </header>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// METRIC CARD COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

interface MetricCardProps {
  label: string;
  value: string | number;
  trend?: { value: number; direction: 'up' | 'down'; label: string };
  icon: React.ReactNode;
  variant?: 'default' | 'gold';
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, trend, icon, variant = 'default' }) => {
  const s = useStyles();
  
  const variantStyles = variant === 'gold'
    ? 'bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-950/30 dark:to-yellow-950/30 border-amber-200 dark:border-amber-800'
    : '';
  
  return (
    <div className={`${s.card} border rounded-xl p-4 ${variantStyles}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className={`text-sm ${s.muted}`}>{label}</p>
          <p className={`text-3xl font-bold mt-1 ${variant === 'gold' ? 'text-amber-600' : ''}`}>
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          {trend && (
            <p className={`text-xs mt-1 flex items-center gap-1 ${
              trend.direction === 'up' ? 'text-emerald-600' : 'text-red-500'
            }`}>
              <TrendingUp className={`w-3 h-3 ${trend.direction === 'down' ? 'rotate-180' : ''}`} />
              {trend.direction === 'up' ? '+' : ''}{trend.value} {trend.label}
            </p>
          )}
        </div>
        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
          variant === 'gold' ? 'bg-amber-100' : 'bg-[#FF6B6B]/10'
        }`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// DASHBOARD METRICS MODULE
// ═══════════════════════════════════════════════════════════════════════════

const DashboardMetrics: React.FC = () => {
  const { user, features } = useDashboard();
  
  // Mock stats - in real app would come from API
  const stats = {
    authorityScore: 94.7,
    authorityTrend: 2.3,
    followers: 2341,
    followersTrend: 89,
    totalReads: 12847,
    readsTrend: 15,
    postsWritten: 47,
    postsTrend: 3,
    pathFollowers: 1247,
    pathFollowersTrend: 12,
    pathsCreated: 8,
    pathsTrend: 1,
    readingStreak: 23,
  };
  
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Authority Score - shows if authority tier */}
      {isAuthorityTier(user) && (
        <MetricCard
          label="Authority Score"
          value={stats.authorityScore}
          trend={{ value: stats.authorityTrend, direction: 'up', label: 'this month' }}
          icon={<Crown className="w-5 h-5 text-amber-600" />}
          variant="gold"
        />
      )}
      
      {/* Writer Metrics - shows if writer track */}
      {hasWriterTrack(user) && (
        <>
          <MetricCard
            label="Followers"
            value={stats.followers}
            trend={{ value: stats.followersTrend, direction: 'up', label: 'this week' }}
            icon={<Users className="w-5 h-5 text-[#FF6B6B]" />}
          />
          <MetricCard
            label="Total Reads"
            value={stats.totalReads}
            trend={{ value: stats.readsTrend, direction: 'up', label: '% this month' }}
            icon={<Eye className="w-5 h-5 text-[#FF6B6B]" />}
          />
          <MetricCard
            label="Posts Written"
            value={stats.postsWritten}
            trend={{ value: stats.postsTrend, direction: 'up', label: 'this month' }}
            icon={<PenTool className="w-5 h-5 text-[#FF6B6B]" />}
          />
        </>
      )}
      
      {/* Curator Metrics - shows if curator track */}
      {hasCuratorTrack(user) && (
        <>
          <MetricCard
            label="Path Followers"
            value={stats.pathFollowers}
            trend={{ value: stats.pathFollowersTrend, direction: 'up', label: 'this week' }}
            icon={<Users className="w-5 h-5 text-[#FF6B6B]" />}
          />
          <MetricCard
            label="Paths Created"
            value={stats.pathsCreated}
            trend={{ value: stats.pathsTrend, direction: 'up', label: 'this month' }}
            icon={<Route className="w-5 h-5 text-[#FF6B6B]" />}
          />
        </>
      )}
      
      {/* Reading Streak - universal */}
      {!isAuthorityTier(user) && (
        <MetricCard
          label="Reading Streak"
          value={`${stats.readingStreak} days`}
          icon={<Flame className="w-5 h-5 text-[#FF6B6B]" />}
        />
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// VOICE PROFILE MODULE
// ═══════════════════════════════════════════════════════════════════════════

const VoiceProfileModule: React.FC = () => {
  const { user, features, setCurrentView } = useDashboard();
  const s = useStyles();
  
  if (!features.voiceProfile) return null;
  
  const profile = {
    primary: 'Assertive',
    secondary: 'Narrative',
    confidence: 87.2,
    analysesCount: 67,
    tokens: [
      { name: 'Confident', weight: 89 },
      { name: 'Narrative', weight: 91 },
      { name: 'Engaged', weight: 85 },
      { name: 'Structured', weight: 82 },
      { name: 'Warm', weight: 76 },
    ],
  };
  
  return (
    <div className={`${s.card} border rounded-xl overflow-hidden`}>
      <div className={`p-4 border-b ${s.border} flex items-center justify-between`}>
        <h2 className="font-semibold flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-emerald-500" />
          Your Writing Voice
          {features.voiceEvolution && (
            <span className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full">✨ Evolution</span>
          )}
        </h2>
        <button
          onClick={() => setCurrentView('voice')}
          className="text-sm text-[#FF6B6B] hover:underline"
        >
          View Details
        </button>
      </div>
      <div className="p-6 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="w-40 h-40 mx-auto md:mx-0 rounded-full border-4 border-emerald-500/30 flex items-center justify-center bg-emerald-100/50 dark:bg-emerald-900/30">
            <div className="text-center">
              <p className="text-3xl font-bold text-emerald-600">{profile.confidence}%</p>
              <p className="text-xs text-emerald-600">Confidence</p>
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-emerald-600 mb-2">
              {profile.primary} {profile.secondary}
            </h3>
            <p className={`${s.muted} mb-4`}>
              You write with confidence and narrative flair. Your voice combines direct statements with rich storytelling.
            </p>
            <div className="flex flex-wrap gap-2 mb-4">
              {profile.tokens.map((token, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300"
                >
                  {token.name} <span className="opacity-70">{token.weight}%</span>
                </span>
              ))}
            </div>
            <p className={`text-sm ${s.muted}`}>Based on <strong>{profile.analysesCount}</strong> analyses</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// AUTHORITY STATUS MODULE
// ═══════════════════════════════════════════════════════════════════════════

const AuthorityStatusModule: React.FC = () => {
  const { user } = useDashboard();
  const s = useStyles();
  
  if (!isAuthorityTier(user) && !isFeaturedTier(user)) return null;
  
  const writerLevel = WRITER_TIER_LEVEL[user.writerTier];
  const curatorLevel = CURATOR_TIER_LEVEL[user.curatorTier];
  
  const stats = {
    score: 94.7,
    rank: 23,
    percentile: 99.2,
  };
  
  const tierLabel = writerLevel >= curatorLevel
    ? (writerLevel === 3 ? 'Authority Writer' : 'Featured Writer')
    : (curatorLevel === 3 ? 'Authority Curator' : 'Featured Curator');
  
  const showDualBadge = isDualTrack(user) && (writerLevel >= 2 || curatorLevel >= 2);
  
  return (
    <div className={`${s.card} border rounded-xl overflow-hidden bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-950/20 dark:to-yellow-950/20 border-amber-200 dark:border-amber-800`}>
      <div className="p-4 border-b border-amber-200 dark:border-amber-800">
        <h2 className="font-semibold">👑 Authority Status</h2>
      </div>
      <div className="p-4 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center">
            <Crown className="w-6 h-6 text-amber-500" />
          </div>
          <div>
            <p className="font-bold text-amber-600">{tierLabel}</p>
            <p className={`text-sm ${s.muted}`}>
              {showDualBadge ? 'Dual Track' : `${user.primaryTrack === 'writer' ? 'Writer' : 'Curator'} Track`}
            </p>
          </div>
        </div>
        
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className={s.muted}>Authority Score</span>
            <span className="font-semibold text-amber-600">{stats.score} / 100</span>
          </div>
          <div className="h-2 bg-amber-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-amber-400 to-yellow-500 rounded-full"
              style={{ width: `${stats.score}%` }}
            />
          </div>
        </div>
        
        <div className="flex gap-6 pt-2">
          <div>
            <p className="text-2xl font-bold">#{stats.rank}</p>
            <p className={`text-xs ${s.muted}`}>Global Rank</p>
          </div>
          <div>
            <p className="text-2xl font-bold">{stats.percentile}%</p>
            <p className={`text-xs ${s.muted}`}>Percentile</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// ACTIVITY FEED MODULE
// ═══════════════════════════════════════════════════════════════════════════

const ActivityFeedModule: React.FC = () => {
  const { user, setCurrentView } = useDashboard();
  const s = useStyles();
  
  // Activities vary based on user's tracks
  const activities = [
    ...(isAuthorityTier(user) ? [{
      id: 1,
      type: 'authority',
      title: 'Reached Top 25 globally!',
      time: '2 hours ago',
      Icon: Trophy,
    }] : []),
    ...(hasWriterTrack(user) ? [{
      id: 2,
      type: 'followers',
      title: '89 new followers this week',
      time: '5 hours ago',
      Icon: Users,
    }] : []),
    {
      id: 3,
      type: 'badge',
      title: 'Earned Consistency Badge',
      time: 'Yesterday',
      Icon: Award,
    },
    ...(hasCuratorTrack(user) ? [{
      id: 4,
      type: 'path',
      title: 'Path featured in Weekly Picks',
      time: '2 days ago',
      Icon: Route,
    }] : []),
    ...(hasWriterTrack(user) ? [{
      id: 5,
      type: 'featured',
      title: 'Essay featured in Weekly Picks',
      time: '2 days ago',
      Icon: Star,
    }] : []),
    ...(hasVoiceStyle(user) ? [{
      id: 6,
      type: 'voice',
      title: 'Voice confidence reached 87%',
      time: '3 days ago',
      Icon: Sparkles,
    }] : []),
  ].slice(0, 4);
  
  return (
    <div className={`${s.card} border rounded-xl overflow-hidden`}>
      <div className={`p-4 border-b ${s.border} flex items-center justify-between`}>
        <h2 className="font-semibold">Recent Activity</h2>
        <button
          onClick={() => setCurrentView('activity')}
          className="text-sm text-[#FF6B6B] hover:underline"
        >
          View all
        </button>
      </div>
      <div className={`divide-y ${s.border}`}>
        {activities.map((a) => (
          <button
            key={a.id}
            onClick={() => setCurrentView('activity-detail')}
            className={`w-full p-3 flex gap-3 text-left ${s.hover} transition-colors`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              a.type === 'authority' ? 'bg-amber-100 text-amber-600' :
              a.type === 'badge' ? 'bg-purple-100 text-purple-600' :
              a.type === 'featured' || a.type === 'path' ? 'bg-blue-100 text-blue-600' :
              a.type === 'voice' ? 'bg-emerald-100 text-emerald-600' :
              'bg-[#FF6B6B]/10 text-[#FF6B6B]'
            }`}>
              <a.Icon className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{a.title}</p>
              <p className={`text-xs ${s.muted}`}>{a.time}</p>
            </div>
            <ChevronRight className={`w-4 h-4 ${s.muted} flex-shrink-0`} />
          </button>
        ))}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// MY WRITING MODULE (Writer Track)
// ═══════════════════════════════════════════════════════════════════════════

const MyWritingModule: React.FC = () => {
  const { features, setCurrentView } = useDashboard();
  const s = useStyles();
  
  if (!features.myWriting) return null;
  
  const posts = [
    { id: 1, title: 'The Weight of Winter Words', reads: 1247, comments: 34, featured: true },
    { id: 2, title: 'Mapping the Canadian Literary Landscape', reads: 2341, comments: 42, featured: false },
    { id: 3, title: 'Northern Lights of the Mind', reads: 1893, comments: 28, featured: true },
  ];
  
  return (
    <div className={`${s.card} border rounded-xl overflow-hidden`}>
      <div className={`p-4 border-b ${s.border} flex justify-between items-center`}>
        <h2 className="font-semibold">My Writing</h2>
        <button
          onClick={() => setCurrentView('writing')}
          className="text-sm text-[#FF6B6B] hover:underline"
        >
          View all
        </button>
      </div>
      <div className={`divide-y ${s.border}`}>
        {posts.map((post) => (
          <button
            key={post.id}
            onClick={() => setCurrentView('post-detail')}
            className={`w-full p-4 flex items-center gap-4 text-left ${s.hover} transition-colors`}
          >
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 bg-[#FF6B6B]/10 text-[#FF6B6B]`}>
              {post.featured ? <Star className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <p className="font-medium truncate">{post.title}</p>
                {post.featured && <span className="px-1.5 py-0.5 text-xs bg-amber-100 text-amber-800 rounded">Featured</span>}
              </div>
              <p className={`text-sm ${s.muted}`}>{post.reads.toLocaleString()} reads • {post.comments} comments</p>
            </div>
            <ChevronRight className={`w-5 h-5 ${s.muted} flex-shrink-0`} />
          </button>
        ))}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// READING PATHS MODULE (Curator Track)
// ═══════════════════════════════════════════════════════════════════════════

const ReadingPathsModule: React.FC = () => {
  const { features, setCurrentView } = useDashboard();
  const s = useStyles();
  
  if (!features.readingPaths) return null;
  
  const paths = [
    { id: 1, title: 'Canadian Voices: Modern Literary Fiction', posts: 12, followers: 438, trend: 15 },
    { id: 2, title: 'Nature Writing & Environmental Essays', posts: 8, followers: 312, trend: 8 },
    { id: 3, title: "Finding Your Voice: A Writer's Journey", posts: 15, followers: 297, trend: 12 },
  ];
  
  return (
    <div className={`${s.card} border rounded-xl overflow-hidden`}>
      <div className={`p-4 border-b ${s.border} flex justify-between items-center`}>
        <h2 className="font-semibold">Your Reading Paths</h2>
        <button
          onClick={() => setCurrentView('paths')}
          className="text-sm text-[#FF6B6B] hover:underline"
        >
          View all
        </button>
      </div>
      <div className={`divide-y ${s.border}`}>
        {paths.map((path) => (
          <button
            key={path.id}
            onClick={() => setCurrentView('path-detail')}
            className={`w-full p-4 flex items-center gap-4 text-left ${s.hover} transition-colors`}
          >
            <div className="w-10 h-10 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center">
              <Route className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{path.title}</p>
              <p className={`text-sm ${s.muted}`}>{path.posts} posts • {path.followers} followers</p>
            </div>
            <span className="text-sm text-emerald-600 flex items-center gap-1">
              <TrendingUp className="w-4 h-4" />+{path.trend}
            </span>
            <ChevronRight className={`w-5 h-5 ${s.muted} flex-shrink-0`} />
          </button>
        ))}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// MAIN DASHBOARD VIEW
// ═══════════════════════════════════════════════════════════════════════════

const DashboardMainView: React.FC = () => {
  const { user, features } = useDashboard();
  const s = useStyles();
  
  const firstName = user.name.split(' ')[0];
  const flag = COUNTRY_FLAGS[user.country];
  
  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-bold">Welcome back, {firstName}! {flag}</h1>
        <p className={s.muted}>
          {isDualTrack(user)
            ? "Here's what's happening across your writing and curation"
            : hasWriterTrack(user)
              ? "Here's what's happening with your writing"
              : hasCuratorTrack(user)
                ? "Here's what's happening with your paths"
                : "Here's what's happening on Quirrely"
          }
        </p>
      </div>
      
      {/* Metrics */}
      <DashboardMetrics />
      
      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Voice Profile - 2 columns if writer track or voice_style */}
        {features.voiceProfile && (
          <div className="lg:col-span-2">
            <VoiceProfileModule />
          </div>
        )}
        
        {/* Right column */}
        <div className="space-y-6">
          {/* Authority Status */}
          <AuthorityStatusModule />
          
          {/* Activity Feed */}
          <ActivityFeedModule />
        </div>
        
        {/* If no voice profile, activity takes the 2-col space */}
        {!features.voiceProfile && (
          <div className="lg:col-span-2">
            <ActivityFeedModule />
          </div>
        )}
      </div>
      
      {/* Track-specific content sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* My Writing - Writer Track */}
        <MyWritingModule />
        
        {/* Reading Paths - Curator Track */}
        <ReadingPathsModule />
      </div>
      
      {/* Footer */}
      <p className={`text-center text-sm ${s.muted} py-4`}>
        Quirrely v3.0.0 "Knight of Wands" • 
        {isDualTrack(user) ? ' Dual Track' : hasWriterTrack(user) ? ' Writer Track' : hasCuratorTrack(user) ? ' Curator Track' : ''} • 
        Day {user.daysInSystem} • 
        {flag} {user.country}
      </p>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// DASHBOARD SHELL (Main Export)
// ═══════════════════════════════════════════════════════════════════════════

interface DashboardShellProps {
  user: UserConfig;
}

export const DashboardShell: React.FC<DashboardShellProps> = ({ user }) => {
  const [darkMode, setDarkMode] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const features = getFeatureAccess(user);
  
  const contextValue: DashboardContextType = {
    user,
    features,
    darkMode,
    setDarkMode,
    currentView,
    setCurrentView,
    sidebarOpen,
    setSidebarOpen,
  };
  
  const bgClass = darkMode ? 'bg-gray-950 text-gray-100' : 'bg-gray-50 text-gray-900';
  
  return (
    <DashboardContext.Provider value={contextValue}>
      <div className={`min-h-screen ${bgClass} transition-colors duration-200`}>
        <Sidebar />
        <div className="lg:pl-64">
          <Header />
          <main className="p-4 lg:p-6">
            <div className="max-w-7xl mx-auto">
              {currentView === 'dashboard' && <DashboardMainView />}
              {currentView !== 'dashboard' && (
                <div className="text-center py-12">
                  <p className="text-lg font-medium">View: {currentView}</p>
                  <button
                    onClick={() => setCurrentView('dashboard')}
                    className="mt-4 text-[#FF6B6B] hover:underline"
                  >
                    Back to Dashboard
                  </button>
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
    </DashboardContext.Provider>
  );
};

export default DashboardShell;
