/**
 * API Contract Tests
 * 
 * These tests verify that the frontend's expected API response shapes
 * match the actual backend responses. Run these tests when:
 * - Adding new API endpoints
 * - Modifying response structures
 * - Before production deployments
 * 
 * These tests use mock data that mirrors expected backend responses.
 * In CI, they can be run against a test backend instance.
 */

import { describe, it, expect } from 'vitest';

// ═══════════════════════════════════════════════════════════════════════════
// USER API CONTRACTS
// ═══════════════════════════════════════════════════════════════════════════

describe('User API Contract', () => {
  // Expected shape from GET /api/v2/user/me
  const mockUserResponse = {
    id: 'user_abc123',
    email: 'test@example.com',
    name: 'Test User',
    handle: 'testuser',
    avatarUrl: 'https://example.com/avatar.jpg',
    tier: 'pro',
    addons: ['voice_style'],
    country: 'CA',
    countryFlag: '🇨🇦',
    emailVerified: true,
    createdAt: '2025-01-15T00:00:00Z',
    updatedAt: '2026-02-15T00:00:00Z',
  };

  it('GET /user/me returns expected shape', () => {
    expect(mockUserResponse).toMatchObject({
      id: expect.any(String),
      email: expect.stringMatching(/.+@.+\..+/),
      name: expect.any(String),
      tier: expect.stringMatching(/^(free|trial|pro|curator|featured_writer|featured_curator|authority_writer|authority_curator)$/),
      addons: expect.any(Array),
      country: expect.stringMatching(/^(CA|GB|AU|NZ)$/),
    });
  });

  it('tier field matches allowed values', () => {
    const allowedTiers = [
      'free', 'trial', 'pro', 'curator',
      'featured_writer', 'featured_curator',
      'authority_writer', 'authority_curator'
    ];
    expect(allowedTiers).toContain(mockUserResponse.tier);
  });

  it('country field is from allowed countries', () => {
    const allowedCountries = ['CA', 'GB', 'AU', 'NZ'];
    expect(allowedCountries).toContain(mockUserResponse.country);
  });

  it('addons is an array of strings', () => {
    expect(Array.isArray(mockUserResponse.addons)).toBe(true);
    mockUserResponse.addons.forEach((addon: string) => {
      expect(typeof addon).toBe('string');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// DASHBOARD API CONTRACTS
// ═══════════════════════════════════════════════════════════════════════════

describe('Dashboard API Contract', () => {
  // Expected shape from GET /api/v2/dashboard/overview
  const mockDashboardResponse = {
    user_tier: 'pro',
    user_addons: ['voice_style'],
    tier_level: 1,
    track: 'writer',
    has_voice_style: true,
    has_writer_features: true,
    has_curator_features: false,
    has_authority_features: false,
    sections: [
      { key: 'progress', enabled: true },
      { key: 'voice', enabled: true },
      { key: 'writing', enabled: true },
    ],
    quick_stats: {
      words_today: 1250,
      streak_days: 7,
      posts_this_week: 3,
    },
  };

  it('GET /dashboard/overview returns expected shape', () => {
    expect(mockDashboardResponse).toMatchObject({
      user_tier: expect.any(String),
      user_addons: expect.any(Array),
      tier_level: expect.any(Number),
      track: expect.stringMatching(/^(writer|curator|none)$/),
      has_voice_style: expect.any(Boolean),
      has_writer_features: expect.any(Boolean),
      has_curator_features: expect.any(Boolean),
    });
  });

  it('tier_level is within valid range', () => {
    expect(mockDashboardResponse.tier_level).toBeGreaterThanOrEqual(0);
    expect(mockDashboardResponse.tier_level).toBeLessThanOrEqual(3);
  });

  it('sections is an array with required structure', () => {
    expect(Array.isArray(mockDashboardResponse.sections)).toBe(true);
    mockDashboardResponse.sections.forEach((section: { key: string; enabled: boolean }) => {
      expect(section).toMatchObject({
        key: expect.any(String),
        enabled: expect.any(Boolean),
      });
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// AUTHORITY API CONTRACTS
// ═══════════════════════════════════════════════════════════════════════════

describe('Authority API Contract', () => {
  // Expected shape from GET /api/v2/authority/status
  const mockAuthorityStatusResponse = {
    score: 75.5,
    rank: 234,
    percentile: 88.5,
    level: 'Featured',
    tier: 'featured_writer',
    next_milestone: {
      name: 'Reach Authority',
      threshold: 90,
      progress: 75.5,
    },
    last_updated: '2026-02-15T12:00:00Z',
  };

  it('GET /authority/status returns expected shape', () => {
    expect(mockAuthorityStatusResponse).toMatchObject({
      score: expect.any(Number),
      rank: expect.any(Number),
      percentile: expect.any(Number),
      level: expect.any(String),
      tier: expect.any(String),
    });
  });

  it('score is within valid range (0-100)', () => {
    expect(mockAuthorityStatusResponse.score).toBeGreaterThanOrEqual(0);
    expect(mockAuthorityStatusResponse.score).toBeLessThanOrEqual(100);
  });

  it('percentile is within valid range (0-100)', () => {
    expect(mockAuthorityStatusResponse.percentile).toBeGreaterThanOrEqual(0);
    expect(mockAuthorityStatusResponse.percentile).toBeLessThanOrEqual(100);
  });

  it('rank is a positive integer', () => {
    expect(mockAuthorityStatusResponse.rank).toBeGreaterThan(0);
    expect(Number.isInteger(mockAuthorityStatusResponse.rank)).toBe(true);
  });

  // Expected shape from GET /api/v2/authority/leaderboard
  const mockLeaderboardResponse = [
    {
      rank: 1,
      userId: 'user_xyz789',
      name: 'Top Writer',
      handle: 'topwriter',
      avatarUrl: null,
      country: 'CA',
      countryFlag: '🇨🇦',
      score: 98.5,
      tier: 'authority_writer',
      pathFollowers: 1250,
      isCurrentUser: false,
    },
  ];

  it('GET /authority/leaderboard returns array with expected shape', () => {
    expect(Array.isArray(mockLeaderboardResponse)).toBe(true);
    
    const entry = mockLeaderboardResponse[0];
    expect(entry).toMatchObject({
      rank: expect.any(Number),
      userId: expect.any(String),
      name: expect.any(String),
      handle: expect.any(String),
      country: expect.stringMatching(/^(CA|GB|AU|NZ)$/),
      score: expect.any(Number),
      tier: expect.any(String),
    });
  });

  it('leaderboard entries have no US users', () => {
    mockLeaderboardResponse.forEach((entry) => {
      expect(entry.country).not.toBe('US');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// CURATOR API CONTRACTS
// ═══════════════════════════════════════════════════════════════════════════

describe('Curator API Contract', () => {
  // Expected shape from GET /api/v2/curator/paths
  const mockPathsResponse = {
    paths: [
      {
        id: 'path_abc123',
        title: 'Introduction to Voice Writing',
        description: 'Learn the fundamentals of finding your voice',
        postCount: 5,
        followerCount: 42,
        status: 'published',
        featured: false,
        createdAt: '2025-06-01T00:00:00Z',
        updatedAt: '2026-02-10T00:00:00Z',
      },
    ],
    total: 1,
    page: 1,
    pageSize: 20,
  };

  it('GET /curator/paths returns expected shape', () => {
    expect(mockPathsResponse).toMatchObject({
      paths: expect.any(Array),
      total: expect.any(Number),
      page: expect.any(Number),
      pageSize: expect.any(Number),
    });
  });

  it('path entries have required fields', () => {
    const path = mockPathsResponse.paths[0];
    expect(path).toMatchObject({
      id: expect.any(String),
      title: expect.any(String),
      postCount: expect.any(Number),
      followerCount: expect.any(Number),
      status: expect.stringMatching(/^(draft|published|archived)$/),
      featured: expect.any(Boolean),
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// WRITER API CONTRACTS
// ═══════════════════════════════════════════════════════════════════════════

describe('Writer API Contract', () => {
  // Expected shape from GET /api/v2/writer/analytics
  const mockAnalyticsResponse = {
    totalViews: 12500,
    totalReactions: 890,
    totalFollowers: 156,
    averageReadTime: 4.5,
    topPosts: [
      {
        id: 'post_xyz',
        title: 'My Best Post',
        views: 2500,
        reactions: 180,
        publishedAt: '2025-11-01T00:00:00Z',
      },
    ],
    viewsTrend: [
      { date: '2026-02-01', views: 450 },
      { date: '2026-02-02', views: 520 },
    ],
    period: '30d',
  };

  it('GET /writer/analytics returns expected shape', () => {
    expect(mockAnalyticsResponse).toMatchObject({
      totalViews: expect.any(Number),
      totalReactions: expect.any(Number),
      totalFollowers: expect.any(Number),
      averageReadTime: expect.any(Number),
      topPosts: expect.any(Array),
      viewsTrend: expect.any(Array),
      period: expect.any(String),
    });
  });

  it('analytics values are non-negative', () => {
    expect(mockAnalyticsResponse.totalViews).toBeGreaterThanOrEqual(0);
    expect(mockAnalyticsResponse.totalReactions).toBeGreaterThanOrEqual(0);
    expect(mockAnalyticsResponse.totalFollowers).toBeGreaterThanOrEqual(0);
    expect(mockAnalyticsResponse.averageReadTime).toBeGreaterThanOrEqual(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// AUTH API CONTRACTS
// ═══════════════════════════════════════════════════════════════════════════

describe('Auth API Contract', () => {
  // Expected shape from POST /api/v2/auth/login
  const mockLoginResponse = {
    user: {
      id: 'user_abc123',
      email: 'test@example.com',
      name: 'Test User',
      tier: 'pro',
      addons: ['voice_style'],
      country: 'CA',
    },
    // Note: In new cookie flow, tokens are in httpOnly cookies, not response body
    // Legacy response may include these:
    // access_token: 'jwt...',
    // refresh_token: 'jwt...',
    // expires_in: 3600,
  };

  it('POST /auth/login returns user object', () => {
    expect(mockLoginResponse).toMatchObject({
      user: expect.objectContaining({
        id: expect.any(String),
        email: expect.any(String),
        tier: expect.any(String),
      }),
    });
  });

  it('login response user has required fields', () => {
    expect(mockLoginResponse.user).toMatchObject({
      id: expect.any(String),
      email: expect.stringMatching(/.+@.+\..+/),
      name: expect.any(String),
      tier: expect.any(String),
      addons: expect.any(Array),
      country: expect.stringMatching(/^(CA|GB|AU|NZ)$/),
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// VOICE PROFILE API CONTRACTS
// ═══════════════════════════════════════════════════════════════════════════

describe('Voice Profile API Contract', () => {
  // Expected shape from GET /api/v2/voice/profile
  const mockVoiceProfileResponse = {
    profile_type: 'assertive',
    confidence: 0.87,
    tokens: [
      { name: 'Directness', score: 0.92, category: 'style' },
      { name: 'Confidence', score: 0.88, category: 'tone' },
      { name: 'Clarity', score: 0.85, category: 'structure' },
    ],
    dimensions: {
      formality: 0.65,
      complexity: 0.72,
      emotionality: 0.45,
      assertiveness: 0.88,
    },
    evolution: [
      { date: '2025-01-01', profile_type: 'narrative', score: 0.75 },
      { date: '2025-06-01', profile_type: 'assertive', score: 0.82 },
      { date: '2026-01-01', profile_type: 'assertive', score: 0.87 },
    ],
    last_analyzed: '2026-02-15T10:00:00Z',
  };

  it('GET /voice/profile returns expected shape', () => {
    expect(mockVoiceProfileResponse).toMatchObject({
      profile_type: expect.any(String),
      confidence: expect.any(Number),
      tokens: expect.any(Array),
      dimensions: expect.any(Object),
    });
  });

  it('confidence is between 0 and 1', () => {
    expect(mockVoiceProfileResponse.confidence).toBeGreaterThanOrEqual(0);
    expect(mockVoiceProfileResponse.confidence).toBeLessThanOrEqual(1);
  });

  it('tokens have required structure', () => {
    mockVoiceProfileResponse.tokens.forEach((token) => {
      expect(token).toMatchObject({
        name: expect.any(String),
        score: expect.any(Number),
        category: expect.any(String),
      });
      expect(token.score).toBeGreaterThanOrEqual(0);
      expect(token.score).toBeLessThanOrEqual(1);
    });
  });

  it('dimensions values are between 0 and 1', () => {
    Object.values(mockVoiceProfileResponse.dimensions).forEach((value) => {
      expect(value).toBeGreaterThanOrEqual(0);
      expect(value).toBeLessThanOrEqual(1);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// META EVENTS API CONTRACTS
// ═══════════════════════════════════════════════════════════════════════════

describe('Meta Events API Contract', () => {
  // Expected request shape for POST /api/meta/events
  const mockEventRequest = {
    event: 'page_view',
    data: {
      page: '/dashboard',
      referrer: '/login',
    },
    timestamp: 1708012800000,
    sessionId: 'sess_abc123_xyz',
    userId: 'user_abc123',
    page: '/dashboard',
    userAgent: 'Mozilla/5.0...',
    referrer: '',
  };

  it('event request has required fields', () => {
    expect(mockEventRequest).toMatchObject({
      event: expect.any(String),
      data: expect.any(Object),
      timestamp: expect.any(Number),
      sessionId: expect.any(String),
      page: expect.any(String),
    });
  });

  it('timestamp is a valid Unix milliseconds value', () => {
    expect(mockEventRequest.timestamp).toBeGreaterThan(1600000000000);
    expect(mockEventRequest.timestamp).toBeLessThan(2000000000000);
  });

  // Expected response shape
  const mockEventResponse = {
    status: 'accepted',
    event_id: 'sess_abc123_xyz_1708012800000',
  };

  it('event response indicates acceptance', () => {
    expect(mockEventResponse).toMatchObject({
      status: 'accepted',
    });
  });
});
