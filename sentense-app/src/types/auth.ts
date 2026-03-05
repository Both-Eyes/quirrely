export interface User {
  id: string;
  email: string;
  name: string;
  handle: string;
  country: string;
  countryName: string;
  countryFlag: string;
  tier: UserTier;
  tierDisplay: string;
  tierLevel: number;
  addons: UserAddon[];
  avatarUrl?: string;
  createdAt: string;
  lastActive: string;
}

export type UserTier = 
  | 'free'
  | 'pro'                   // Writer track - Paid Tier 1
  | 'curator'               // Reader track - Paid Tier 1
  | 'featured_writer'       // Writer track - Paid Tier 2
  | 'featured_curator'      // Reader track - Paid Tier 2
  | 'authority_writer'      // Writer track - Paid Tier 3
  | 'authority_curator';    // Reader track - Paid Tier 3

export type UserAddon = 
  | 'voice_style';          // Voice + Style analysis (available to pro OR curator)

// Tier hierarchy for permission checks
export const TIER_LEVELS: Record<UserTier, number> = {
  free: 0,
  pro: 1,
  curator: 1,
  featured_writer: 2,
  featured_curator: 2,
  authority_writer: 3,
  authority_curator: 3,
};

// Display names
export const TIER_DISPLAY: Record<UserTier, string> = {
  free: 'Free',
  pro: 'Pro',
  curator: 'Curator',
  featured_writer: 'Featured Writer',
  featured_curator: 'Featured Curator',
  authority_writer: 'Authority Writer',
  authority_curator: 'Authority Curator',
};

// Addon display names
export const ADDON_DISPLAY: Record<UserAddon, string> = {
  voice_style: 'Voice + Style',
};

// Helper to check if user has an addon
export const hasAddon = (user: User | null, addon: UserAddon): boolean => {
  return user?.addons?.includes(addon) ?? false;
};

// Helper to check if user meets tier requirement
export const hasTierAccess = (user: User | null, requiredTiers: UserTier[]): boolean => {
  if (!user) return false;
  return requiredTiers.includes(user.tier);
};

// Helper to check if user is on paid tier (either track)
export const isPaidTier = (user: User | null): boolean => {
  if (!user) return false;
  return TIER_LEVELS[user.tier] >= 1;
};

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  password: string;
  name: string;
  country?: string;
}

export interface AuthResponse {
  token: string;
  refreshToken: string;
  user: User;
}

export interface TokenPayload {
  sub: string;
  email: string;
  exp: number;
  iat: number;
}
