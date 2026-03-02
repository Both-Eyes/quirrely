/**
 * QUIRRELY QA MOCK DATA CONFIGURATION
 * 
 * This file provides consistent mock data for QA testing when the backend
 * is not available or for specific test scenarios.
 * 
 * Usage: Import and use in development/staging environments
 */

import { User, UserTier, UserAddon } from '@/types';

// ═══════════════════════════════════════════════════════════════════════════
// COUNTRY CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

export const COUNTRIES = {
  CA: { code: 'CA', name: 'Canada', flag: '🇨🇦', currency: 'CAD', currencySymbol: '$' },
  GB: { code: 'GB', name: 'United Kingdom', flag: '🇬🇧', currency: 'GBP', currencySymbol: '£' },
  AU: { code: 'AU', name: 'Australia', flag: '🇦🇺', currency: 'AUD', currencySymbol: '$' },
  NZ: { code: 'NZ', name: 'New Zealand', flag: '🇳🇿', currency: 'NZD', currencySymbol: '$' },
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// TIER CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

export const TIER_CONFIG: Record<UserTier, {
  level: number;
  track: 'none' | 'writer' | 'curator';
  badge: { label: string; variant: 'default' | 'primary' | 'gold' };
  features: string[];
}> = {
  free: {
    level: 0,
    track: 'none',
    badge: { label: 'Free', variant: 'default' },
    features: ['basic_analysis', 'writer_matches', 'discover', 'bookmarks', 'streak'],
  },
  pro: {
    level: 1,
    track: 'writer',
    badge: { label: 'Pro', variant: 'primary' },
    features: ['save_results', 'profile_history', 'analytics', 'unlimited_analyses'],
  },
  curator: {
    level: 1,
    track: 'curator',
    badge: { label: 'Curator', variant: 'primary' },
    features: ['create_paths', 'path_followers', 'analytics'],
  },
  featured_writer: {
    level: 2,
    track: 'writer',
    badge: { label: 'Featured Writer', variant: 'primary' },
    features: ['featured_submission', 'authority_hub', 'leaderboard', 'impact_stats'],
  },
  featured_curator: {
    level: 2,
    track: 'curator',
    badge: { label: 'Featured Curator', variant: 'primary' },
    features: ['featured_page', 'authority_hub', 'leaderboard', 'impact_stats'],
  },
  authority_writer: {
    level: 3,
    track: 'writer',
    badge: { label: 'Authority Writer', variant: 'gold' },
    features: ['all'],
  },
  authority_curator: {
    level: 3,
    track: 'curator',
    badge: { label: 'Authority Curator', variant: 'gold' },
    features: ['all'],
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// ADDON CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

export const ADDON_CONFIG: Record<UserAddon, {
  label: string;
  badge: { label: string; variant: 'success' };
  features: string[];
}> = {
  voice_style: {
    label: 'Voice + Style',
    badge: { label: '✨ Voice + Style', variant: 'success' },
    features: ['voice_profile', 'voice_evolution', 'create_paths', 'authority_hub', 'leaderboard', 'impact_stats', 'featured_page'],
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// QA TEST USERS
// ═══════════════════════════════════════════════════════════════════════════

type QAUserKey = `kim_${string}_${string}_${'ca' | 'uk' | 'au' | 'nz'}`;

export const QA_TEST_USERS: Record<QAUserKey, Partial<User>> = {
  // CANADA
  kim_free_none_ca: {
    id: 'qa-free-none-ca',
    email: 'kim_free_none_ca@test.quirrely.com',
    name: 'Kim Free CA',
    handle: 'kim_free_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'free',
    tierDisplay: 'Free',
    tierLevel: 0,
    addons: [],
  },
  kim_free_vs_ca: {
    id: 'qa-free-vs-ca',
    email: 'kim_free_vs_ca@test.quirrely.com',
    name: 'Kim Free+VS CA',
    handle: 'kim_free_vs_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'free',
    tierDisplay: 'Free',
    tierLevel: 0,
    addons: ['voice_style'],
  },
  kim_pro_none_ca: {
    id: 'qa-pro-none-ca',
    email: 'kim_pro_none_ca@test.quirrely.com',
    name: 'Kim Pro CA',
    handle: 'kim_pro_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'pro',
    tierDisplay: 'Pro',
    tierLevel: 1,
    addons: [],
  },
  kim_pro_vs_ca: {
    id: 'qa-pro-vs-ca',
    email: 'kim_pro_vs_ca@test.quirrely.com',
    name: 'Kim Pro+VS CA',
    handle: 'kim_pro_vs_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'pro',
    tierDisplay: 'Pro',
    tierLevel: 1,
    addons: ['voice_style'],
  },
  kim_curator_none_ca: {
    id: 'qa-curator-none-ca',
    email: 'kim_curator_none_ca@test.quirrely.com',
    name: 'Kim Curator CA',
    handle: 'kim_curator_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'curator',
    tierDisplay: 'Curator',
    tierLevel: 1,
    addons: [],
  },
  kim_curator_vs_ca: {
    id: 'qa-curator-vs-ca',
    email: 'kim_curator_vs_ca@test.quirrely.com',
    name: 'Kim Curator+VS CA',
    handle: 'kim_curator_vs_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'curator',
    tierDisplay: 'Curator',
    tierLevel: 1,
    addons: ['voice_style'],
  },
  kim_fw_none_ca: {
    id: 'qa-fw-none-ca',
    email: 'kim_fw_none_ca@test.quirrely.com',
    name: 'Kim Featured Writer CA',
    handle: 'kim_fw_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'featured_writer',
    tierDisplay: 'Featured Writer',
    tierLevel: 2,
    addons: [],
  },
  kim_fw_vs_ca: {
    id: 'qa-fw-vs-ca',
    email: 'kim_fw_vs_ca@test.quirrely.com',
    name: 'Kim Featured Writer+VS CA',
    handle: 'kim_fw_vs_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'featured_writer',
    tierDisplay: 'Featured Writer',
    tierLevel: 2,
    addons: ['voice_style'],
  },
  kim_fc_none_ca: {
    id: 'qa-fc-none-ca',
    email: 'kim_fc_none_ca@test.quirrely.com',
    name: 'Kim Featured Curator CA',
    handle: 'kim_fc_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'featured_curator',
    tierDisplay: 'Featured Curator',
    tierLevel: 2,
    addons: [],
  },
  kim_fc_vs_ca: {
    id: 'qa-fc-vs-ca',
    email: 'kim_fc_vs_ca@test.quirrely.com',
    name: 'Kim Featured Curator+VS CA',
    handle: 'kim_fc_vs_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'featured_curator',
    tierDisplay: 'Featured Curator',
    tierLevel: 2,
    addons: ['voice_style'],
  },
  kim_aw_none_ca: {
    id: 'qa-aw-none-ca',
    email: 'kim_aw_none_ca@test.quirrely.com',
    name: 'Kim Authority Writer CA',
    handle: 'kim_aw_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'authority_writer',
    tierDisplay: 'Authority Writer',
    tierLevel: 3,
    addons: [],
  },
  kim_aw_vs_ca: {
    id: 'qa-aw-vs-ca',
    email: 'kim_aw_vs_ca@test.quirrely.com',
    name: 'Kim Authority Writer+VS CA',
    handle: 'kim_aw_vs_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'authority_writer',
    tierDisplay: 'Authority Writer',
    tierLevel: 3,
    addons: ['voice_style'],
  },
  kim_ac_none_ca: {
    id: 'qa-ac-none-ca',
    email: 'kim_ac_none_ca@test.quirrely.com',
    name: 'Kim Authority Curator CA',
    handle: 'kim_ac_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'authority_curator',
    tierDisplay: 'Authority Curator',
    tierLevel: 3,
    addons: [],
  },
  kim_ac_vs_ca: {
    id: 'qa-ac-vs-ca',
    email: 'kim_ac_vs_ca@test.quirrely.com',
    name: 'Kim Authority Curator+VS CA',
    handle: 'kim_ac_vs_ca',
    country: 'CA',
    countryName: 'Canada',
    countryFlag: '🇨🇦',
    tier: 'authority_curator',
    tierDisplay: 'Authority Curator',
    tierLevel: 3,
    addons: ['voice_style'],
  },
  
  // UK (abbreviated - same pattern)
  kim_free_none_uk: { id: 'qa-free-none-uk', email: 'kim_free_none_uk@test.quirrely.com', name: 'Kim Free UK', country: 'GB', countryName: 'United Kingdom', countryFlag: '🇬🇧', tier: 'free', tierLevel: 0, addons: [] },
  kim_pro_vs_uk: { id: 'qa-pro-vs-uk', email: 'kim_pro_vs_uk@test.quirrely.com', name: 'Kim Pro+VS UK', country: 'GB', countryName: 'United Kingdom', countryFlag: '🇬🇧', tier: 'pro', tierLevel: 1, addons: ['voice_style'] },
  kim_aw_none_uk: { id: 'qa-aw-none-uk', email: 'kim_aw_none_uk@test.quirrely.com', name: 'Kim Authority Writer UK', country: 'GB', countryName: 'United Kingdom', countryFlag: '🇬🇧', tier: 'authority_writer', tierLevel: 3, addons: [] },
  
  // AU (abbreviated)
  kim_free_none_au: { id: 'qa-free-none-au', email: 'kim_free_none_au@test.quirrely.com', name: 'Kim Free AU', country: 'AU', countryName: 'Australia', countryFlag: '🇦🇺', tier: 'free', tierLevel: 0, addons: [] },
  kim_curator_vs_au: { id: 'qa-curator-vs-au', email: 'kim_curator_vs_au@test.quirrely.com', name: 'Kim Curator+VS AU', country: 'AU', countryName: 'Australia', countryFlag: '🇦🇺', tier: 'curator', tierLevel: 1, addons: ['voice_style'] },
  kim_ac_none_au: { id: 'qa-ac-none-au', email: 'kim_ac_none_au@test.quirrely.com', name: 'Kim Authority Curator AU', country: 'AU', countryName: 'Australia', countryFlag: '🇦🇺', tier: 'authority_curator', tierLevel: 3, addons: [] },
  
  // NZ (abbreviated)
  kim_free_none_nz: { id: 'qa-free-none-nz', email: 'kim_free_none_nz@test.quirrely.com', name: 'Kim Free NZ', country: 'NZ', countryName: 'New Zealand', countryFlag: '🇳🇿', tier: 'free', tierLevel: 0, addons: [] },
  kim_fw_vs_nz: { id: 'qa-fw-vs-nz', email: 'kim_fw_vs_nz@test.quirrely.com', name: 'Kim Featured Writer+VS NZ', country: 'NZ', countryName: 'New Zealand', countryFlag: '🇳🇿', tier: 'featured_writer', tierLevel: 2, addons: ['voice_style'] },
  kim_aw_none_nz: { id: 'qa-aw-none-nz', email: 'kim_aw_none_nz@test.quirrely.com', name: 'Kim Authority Writer NZ', country: 'NZ', countryName: 'New Zealand', countryFlag: '🇳🇿', tier: 'authority_writer', tierLevel: 3, addons: [] },
};

// ═══════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if a user has access to a feature based on tier and addons
 */
export function hasFeatureAccess(
  user: Pick<User, 'tier' | 'addons'>,
  requiredTiers?: UserTier[],
  requiredAddon?: UserAddon,
  tierOrAddon: boolean = false
): boolean {
  const hasTier = !requiredTiers || requiredTiers.includes(user.tier);
  const hasAddon = !requiredAddon || user.addons?.includes(requiredAddon);
  
  if (tierOrAddon) {
    const meetsTier = requiredTiers?.includes(user.tier) ?? false;
    const meetsAddon = requiredAddon ? user.addons?.includes(requiredAddon) : false;
    return meetsTier || meetsAddon;
  }
  
  return hasTier && hasAddon;
}

/**
 * Get mock user by email prefix (for QA testing)
 */
export function getMockUserByEmail(email: string): Partial<User> | undefined {
  const key = email.replace('@test.quirrely.com', '') as QAUserKey;
  return QA_TEST_USERS[key];
}

/**
 * Format currency for display
 */
export function formatCurrency(amountCents: number, country: keyof typeof COUNTRIES): string {
  const config = COUNTRIES[country];
  const amount = (amountCents / 100).toFixed(2);
  
  if (country === 'GB') {
    return `${config.currencySymbol}${amount}`;
  }
  return `${config.currencySymbol}${amount} ${config.currency}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// MOCK PRICES (in cents)
// ═══════════════════════════════════════════════════════════════════════════

export const PRICING = {
  pro: { CA: 1499, GB: 1199, AU: 1999, NZ: 2199 },
  curator: { CA: 1499, GB: 1199, AU: 1999, NZ: 2199 },
  featured_writer: { CA: 2499, GB: 1999, AU: 3499, NZ: 3799 },
  featured_curator: { CA: 2499, GB: 1999, AU: 3499, NZ: 3799 },
  authority_writer: { CA: 4999, GB: 3999, AU: 6999, NZ: 7499 },
  authority_curator: { CA: 4999, GB: 3999, AU: 6999, NZ: 7499 },
  voice_style: { CA: 999, GB: 799, AU: 1499, NZ: 1599 },
} as const;

export default {
  COUNTRIES,
  TIER_CONFIG,
  ADDON_CONFIG,
  QA_TEST_USERS,
  PRICING,
  hasFeatureAccess,
  getMockUserByEmail,
  formatCurrency,
};
