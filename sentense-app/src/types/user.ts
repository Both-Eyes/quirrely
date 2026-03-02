import { User } from './auth';

export interface UserProfile extends User {
  bio?: string;
  website?: string;
  socialLinks?: {
    twitter?: string;
    linkedin?: string;
    instagram?: string;
  };
}

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  emailNotifications: boolean;
  weeklyDigest: boolean;
  showOnLeaderboard: boolean;
  publicProfile: boolean;
}

export interface UserStats {
  followers: number;
  following: number;
  postsWritten: number;
  postsRead: number;
  deepReads: number;
  bookmarks: number;
  readingStreak: number;
  pathsCreated: number;
  pathFollowers: number;
  writingImpact: number;
}

export interface VoiceProfile {
  primary: string;
  secondary: string;
  openness: 'open' | 'balanced' | 'closed';
  mode: string;
  tokens: VoiceToken[];
  dimensions: VoiceDimensions;
  confidence: number;
  analysesCount: number;
  lastAnalysis: string;
}

export interface VoiceToken {
  name: string;
  weight: number;
}

export interface VoiceDimensions {
  assertiveness: number;
  formality: number;
  detail: number;
  poeticism: number;
  openness: number;
  dynamism: number;
}

export interface Activity {
  id: string;
  type: 'read' | 'follow' | 'badge' | 'path' | 'publish' | 'feature' | 'milestone';
  content: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}
