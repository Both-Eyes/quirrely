/**
 * QUIRRELY USER CONFIGURATION SYSTEM
 * Knight of Wands v3.0.0
 * 
 * Defines user profile types, track logic, and feature access rules.
 * This is the single source of truth for what features a user can access.
 */

// ═══════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════

export type Country = 'CA' | 'GB' | 'AU' | 'NZ';

export type WriterTier = 'free' | 'pro' | 'featured_writer';
export type CuratorTier = 'free' | 'curator' | 'featured_curator';

export type Addon = 'voice_style';

export type Track = 'writer' | 'curator';

export interface UserConfig {
  // Identity
  id: string;
  name: string;
  handle: string;
  email: string;
  avatarUrl?: string;
  
  // Location
  country: Country;
  
  // Track & Tier
  writerTier: WriterTier;
  curatorTier: CuratorTier;
  primaryTrack: Track; // Which track they started on / prioritize
  
  // Addons
  addons: Addon[];
  
  // Trial status
  trialActive: boolean;
  trialDaysRemaining?: number;
  
  // Engagement
  daysInSystem: number;
  
  // Timestamps
  createdAt: string;
  lastActiveAt: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// TIER HIERARCHY
// ═══════════════════════════════════════════════════════════════════════════

export const WRITER_TIER_LEVEL: Record<WriterTier, number> = {
  free: 0,
  pro: 1,
  featured_writer: 2,
  authority_writer: 3,
};

export const CURATOR_TIER_LEVEL: Record<CuratorTier, number> = {
  free: 0,
  curator: 1,
  featured_curator: 2,
  authority_curator: 3,
};

// ═══════════════════════════════════════════════════════════════════════════
// COUNTRY FLAGS
// ═══════════════════════════════════════════════════════════════════════════

export const COUNTRY_FLAGS: Record<Country, string> = {
  CA: '🍁',
  GB: '🇬🇧',
  AU: '🇦🇺',
  NZ: '🇳🇿',
};

export const COUNTRY_NAMES: Record<Country, string> = {
  CA: 'Canada',
  GB: 'United Kingdom',
  AU: 'Australia',
  NZ: 'New Zealand',
};

// ═══════════════════════════════════════════════════════════════════════════
// ACCESS HELPERS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if user has an active writer track (beyond free)
 */
export function hasWriterTrack(user: UserConfig): boolean {
  return WRITER_TIER_LEVEL[user.writerTier] >= 1;
}

/**
 * Check if user has an active curator track (beyond free)
 */
export function hasCuratorTrack(user: UserConfig): boolean {
  return CURATOR_TIER_LEVEL[user.curatorTier] >= 1;
}

/**
 * Check if user is on dual tracks
 */
export function isDualTrack(user: UserConfig): boolean {
  return hasWriterTrack(user) && hasCuratorTrack(user);
}

/**
 * Check if user can switch/add tracks (Pro/Curator and above)
 */
export function canSwitchTracks(user: UserConfig): boolean {
  return WRITER_TIER_LEVEL[user.writerTier] >= 1 || CURATOR_TIER_LEVEL[user.curatorTier] >= 1;
}

/**
 * Check if user has a specific addon
 */
export function hasAddon(user: UserConfig, addon: Addon): boolean {
  return user.addons.includes(addon);
}

/**
 * Check if user has Voice + Style addon
 */
export function hasVoiceStyle(user: UserConfig): boolean {
  return hasAddon(user, 'voice_style');
}

/**
 * Check if user is at Featured level on either track
 */
export function isFeaturedTier(user: UserConfig): boolean {
  return WRITER_TIER_LEVEL[user.writerTier] >= 2 || CURATOR_TIER_LEVEL[user.curatorTier] >= 2;
}

/**
 * Check if user is at Authority level on either track
 */
export function isAuthorityTier(user: UserConfig): boolean {
  return WRITER_TIER_LEVEL[user.writerTier] >= 3 || CURATOR_TIER_LEVEL[user.curatorTier] >= 3;
}

/**
 * Check if user is Authority on Writer track specifically
 */
export function isAuthorityWriter(user: UserConfig): boolean {
  return user.writerTier === 'authority_writer';
}

/**
 * Check if user is Authority on Curator track specifically
 */
export function isAuthorityCurator(user: UserConfig): boolean {
  return user.curatorTier === 'authority_curator';
}

/**
 * Get user's highest tier level (across both tracks)
 */
export function getHighestTierLevel(user: UserConfig): number {
  return Math.max(
    WRITER_TIER_LEVEL[user.writerTier],
    CURATOR_TIER_LEVEL[user.curatorTier]
  );
}

/**
 * Check if user is a paid user (any paid tier on any track)
 */
export function isPaidUser(user: UserConfig): boolean {
  return getHighestTierLevel(user) >= 1;
}

/**
 * Check if user is completely free (no paid tiers, no addons)
 */
export function isFreeUser(user: UserConfig): boolean {
  return !isPaidUser(user) && user.addons.length === 0;
}

// ═══════════════════════════════════════════════════════════════════════════
// FEATURE ACCESS
// ═══════════════════════════════════════════════════════════════════════════

export interface FeatureAccess {
  // Writer Track Features
  myWriting: boolean;
  drafts: boolean;
  writerAnalytics: boolean;
  voiceProfile: boolean;
  voiceEvolution: boolean; // requires voice_style addon
  
  // Curator Track Features
  readingPaths: boolean;
  pathFollowers: boolean;
  curatorAnalytics: boolean;
  featuredPaths: boolean;
  
  // Authority Features (either track at authority level)
  authorityHub: boolean;
  leaderboard: boolean;
  impactStats: boolean;
  
  // Universal Features
  discover: boolean;
  bookmarks: boolean;
  readingStreak: boolean;
  activityFeed: boolean;
  
  // Settings & Account
  settings: boolean;
  billing: boolean;
  
  // Track Management
  canAddTrack: boolean;
  canSwitchPrimaryTrack: boolean;
}

/**
 * Calculate feature access for a user
 */
export function getFeatureAccess(user: UserConfig): FeatureAccess {
  const writerLevel = WRITER_TIER_LEVEL[user.writerTier];
  const curatorLevel = CURATOR_TIER_LEVEL[user.curatorTier];
  const hasVS = hasVoiceStyle(user);
  
  return {
    // Writer Track Features
    myWriting: writerLevel >= 1 || hasVS, // Pro+ or voice_style
    drafts: writerLevel >= 1 || hasVS,
    writerAnalytics: writerLevel >= 1,
    voiceProfile: writerLevel >= 1 || hasVS, // Core writer feature or addon
    voiceEvolution: hasVS, // Addon exclusive
    
    // Curator Track Features
    readingPaths: curatorLevel >= 1,
    pathFollowers: curatorLevel >= 1,
    curatorAnalytics: curatorLevel >= 1,
    featuredPaths: curatorLevel >= 2, // Featured Curator+
    
    // Authority Features
    authorityHub: writerLevel >= 2 || curatorLevel >= 2, // Featured+
    leaderboard: writerLevel >= 2 || curatorLevel >= 2,
    impactStats: writerLevel >= 3 || curatorLevel >= 3, // Authority only
    
    // Universal Features (always available)
    discover: true,
    bookmarks: true,
    readingStreak: true,
    activityFeed: true,
    
    // Settings
    settings: true,
    billing: writerLevel >= 1 || curatorLevel >= 1 || hasVS,
    
    // Track Management
    canAddTrack: writerLevel >= 1 || curatorLevel >= 1,
    canSwitchPrimaryTrack: writerLevel >= 1 || curatorLevel >= 1,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// DISPLAY HELPERS
// ═══════════════════════════════════════════════════════════════════════════

export interface TierDisplay {
  label: string;
  shortLabel: string;
  color: string;
  bgColor: string;
  icon: string;
}

export const WRITER_TIER_DISPLAY: Record<WriterTier, TierDisplay> = {
  free: {
    label: 'Free',
    shortLabel: 'Free',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    icon: '📝',
  },
  pro: {
    label: 'Pro Writer',
    shortLabel: 'Pro',
    color: 'text-coral-600',
    bgColor: 'bg-coral-100',
    icon: '✍️',
  },
  featured_writer: {
    label: 'Featured Writer',
    shortLabel: 'Featured',
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    icon: '⭐',
  },
  authority_writer: {
    label: 'Authority Writer',
    shortLabel: 'Authority',
    color: 'text-amber-600',
    bgColor: 'bg-amber-100',
    icon: '👑',
  },
};

export const CURATOR_TIER_DISPLAY: Record<CuratorTier, TierDisplay> = {
  free: {
    label: 'Free',
    shortLabel: 'Free',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    icon: '📚',
  },
  curator: {
    label: 'Curator',
    shortLabel: 'Curator',
    color: 'text-purple-600',
    bgColor: 'bg-purple-100',
    icon: '📖',
  },
  featured_curator: {
    label: 'Featured Curator',
    shortLabel: 'Featured',
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-100',
    icon: '⭐',
  },
  authority_curator: {
    label: 'Authority Curator',
    shortLabel: 'Authority',
    color: 'text-amber-600',
    bgColor: 'bg-amber-100',
    icon: '👑',
  },
};

/**
 * Get display badges for a user (returns array of badges to show)
 */
export function getUserBadges(user: UserConfig): TierDisplay[] {
  const badges: TierDisplay[] = [];
  
  // Add writer tier badge if not free
  if (WRITER_TIER_LEVEL[user.writerTier] >= 1) {
    badges.push(WRITER_TIER_DISPLAY[user.writerTier]);
  }
  
  // Add curator tier badge if not free
  if (CURATOR_TIER_LEVEL[user.curatorTier] >= 1) {
    badges.push(CURATOR_TIER_DISPLAY[user.curatorTier]);
  }
  
  return badges;
}

/**
 * Get the user's "primary" display tier (highest tier for display purposes)
 */
export function getPrimaryTierDisplay(user: UserConfig): TierDisplay {
  const writerLevel = WRITER_TIER_LEVEL[user.writerTier];
  const curatorLevel = CURATOR_TIER_LEVEL[user.curatorTier];
  
  if (writerLevel >= curatorLevel) {
    return WRITER_TIER_DISPLAY[user.writerTier];
  } else {
    return CURATOR_TIER_DISPLAY[user.curatorTier];
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// SAMPLE USERS (for testing)
// ═══════════════════════════════════════════════════════════════════════════

export const SAMPLE_USERS: Record<string, UserConfig> = {
  // Free user
  free_user: {
    id: 'user_free_001',
    name: 'New Reader',
    handle: 'newreader',
    email: 'new@example.com',
    country: 'CA',
    writerTier: 'free',
    curatorTier: 'free',
    primaryTrack: 'writer',
    addons: [],
    trialActive: false,
    daysInSystem: 3,
    createdAt: '2026-02-12T00:00:00Z',
    lastActiveAt: '2026-02-15T00:00:00Z',
  },
  
  // Trial user
  trial_user: {
    id: 'user_trial_001',
    name: 'Trial Writer',
    handle: 'trialwriter',
    email: 'trial@example.com',
    country: 'GB',
    writerTier: 'pro',
    curatorTier: 'free',
    primaryTrack: 'writer',
    addons: [],
    trialActive: true,
    trialDaysRemaining: 7,
    daysInSystem: 7,
    createdAt: '2026-02-08T00:00:00Z',
    lastActiveAt: '2026-02-15T00:00:00Z',
  },
  
  // Pro Writer only
  pro_writer: {
    id: 'user_pro_001',
    name: 'Pro Writer',
    handle: 'prowriter',
    email: 'pro@example.com',
    country: 'AU',
    writerTier: 'pro',
    curatorTier: 'free',
    primaryTrack: 'writer',
    addons: [],
    trialActive: false,
    daysInSystem: 45,
    createdAt: '2026-01-01T00:00:00Z',
    lastActiveAt: '2026-02-15T00:00:00Z',
  },
  
  // Curator only
  curator_only: {
    id: 'user_curator_001',
    name: 'Path Curator',
    handle: 'pathcurator',
    email: 'curator@example.com',
    country: 'NZ',
    writerTier: 'free',
    curatorTier: 'curator',
    primaryTrack: 'curator',
    addons: [],
    trialActive: false,
    daysInSystem: 60,
    createdAt: '2025-12-17T00:00:00Z',
    lastActiveAt: '2026-02-15T00:00:00Z',
  },
  
  // Dual track: Pro + Curator
  dual_pro_curator: {
    id: 'user_dual_001',
    name: 'Dual Creator',
    handle: 'dualcreator',
    email: 'dual@example.com',
    country: 'CA',
    writerTier: 'pro',
    curatorTier: 'curator',
    primaryTrack: 'writer',
    addons: ['voice_style'],
    trialActive: false,
    daysInSystem: 75,
    createdAt: '2025-12-02T00:00:00Z',
    lastActiveAt: '2026-02-15T00:00:00Z',
  },
  
  // Authority Writer (single track)
  authority_writer: {
    id: 'user_auth_writer_001',
    name: 'Alexandra Chen',
    handle: 'alexwrites',
    email: 'alex@example.com',
    country: 'CA',
    writerTier: 'authority_writer',
    curatorTier: 'free',
    primaryTrack: 'writer',
    addons: ['voice_style'],
    trialActive: false,
    daysInSystem: 90,
    createdAt: '2025-11-17T00:00:00Z',
    lastActiveAt: '2026-02-15T00:00:00Z',
  },
  
  // Authority Curator (single track)
  authority_curator: {
    id: 'user_auth_curator_001',
    name: 'Marcus Webb',
    handle: 'marcuscurates',
    email: 'marcus@example.com',
    country: 'GB',
    writerTier: 'free',
    curatorTier: 'authority_curator',
    primaryTrack: 'curator',
    addons: [],
    trialActive: false,
    daysInSystem: 120,
    createdAt: '2025-10-18T00:00:00Z',
    lastActiveAt: '2026-02-15T00:00:00Z',
  },
  
  // Authority Writer + Authority Curator (dual max)
  authority_dual: {
    id: 'user_auth_dual_001',
    name: 'Elena Vasquez',
    handle: 'elenavwrites',
    email: 'elena@example.com',
    country: 'CA',
    writerTier: 'authority_writer',
    curatorTier: 'authority_curator',
    primaryTrack: 'writer',
    addons: ['voice_style'],
    trialActive: false,
    daysInSystem: 180,
    createdAt: '2025-08-19T00:00:00Z',
    lastActiveAt: '2026-02-15T00:00:00Z',
  },
  
  // Featured Writer + Curator
  featured_writer_curator: {
    id: 'user_feat_001',
    name: 'Jordan Park',
    handle: 'jordanpark',
    email: 'jordan@example.com',
    country: 'AU',
    writerTier: 'featured_writer',
    curatorTier: 'curator',
    primaryTrack: 'writer',
    addons: ['voice_style'],
    trialActive: false,
    daysInSystem: 100,
    createdAt: '2025-11-07T00:00:00Z',
    lastActiveAt: '2026-02-15T00:00:00Z',
  },
  
  // Pro Writer + Voice Style (addon only, no curator)
  pro_with_addon: {
    id: 'user_addon_001',
    name: 'Sam Torres',
    handle: 'samtorres',
    email: 'sam@example.com',
    country: 'NZ',
    writerTier: 'pro',
    curatorTier: 'free',
    primaryTrack: 'writer',
    addons: ['voice_style'],
    trialActive: false,
    daysInSystem: 55,
    createdAt: '2025-12-22T00:00:00Z',
    lastActiveAt: '2026-02-15T00:00:00Z',
  },
};

export default {
  SAMPLE_USERS,
  getFeatureAccess,
  getUserBadges,
  hasWriterTrack,
  hasCuratorTrack,
  isDualTrack,
  isAuthorityTier,
  hasVoiceStyle,
};
