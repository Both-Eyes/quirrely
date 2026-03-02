import { useState } from 'react';
import { Trophy, Medal, Crown, Globe, MapPin } from 'lucide-react';
import { useLeaderboard } from '@/hooks';
import { useAuthStore } from '@/stores';
import { Card, CardHeader, CardTitle, CardContent, Button, Avatar, Badge, Skeleton } from '@/components/ui';
import { LeaderboardEntry } from '@/api';

// Mock data - Commonwealth countries only
const mockLeaderboard: LeaderboardEntry[] = [
  { rank: 1, userId: 'u1', name: 'Emma Thompson', handle: 'emmawrites', country: 'GB', countryFlag: '🇬🇧', score: 98.4, tier: 'authority_curator', pathFollowers: 2341 },
  { rank: 2, userId: 'u2', name: 'Marcus Chen', handle: 'marcusc', country: 'CA', countryFlag: '🇨🇦', score: 97.2, tier: 'authority_curator', pathFollowers: 2156 },
  { rank: 3, userId: 'u3', name: 'Olivia Mitchell', handle: 'oliviam', country: 'AU', countryFlag: '🇦🇺', score: 96.8, tier: 'authority_curator', pathFollowers: 1987 },
  { rank: 4, userId: 'u4', name: 'Liam O\'Connor', handle: 'liamoconnor', country: 'NZ', countryFlag: '🇳🇿', score: 95.9, tier: 'authority_curator', pathFollowers: 1876 },
  { rank: 5, userId: 'u5', name: 'Anika Patel', handle: 'anikap', country: 'AU', countryFlag: '🇦🇺', score: 95.3, tier: 'authority_curator', pathFollowers: 1765 },
  { rank: 6, userId: 'u6', name: 'James MacLeod', handle: 'jamesmac', country: 'CA', countryFlag: '🇨🇦', score: 95.1, tier: 'authority_curator', pathFollowers: 1698 },
  { rank: 7, userId: 'u7', name: 'Sophie Williams', handle: 'sophiew', country: 'GB', countryFlag: '🇬🇧', score: 94.9, tier: 'authority_writer', pathFollowers: 1654 },
  { rank: 8, userId: 'u8', name: 'Hannah Te Puni', handle: 'hannaht', country: 'NZ', countryFlag: '🇳🇿', score: 94.8, tier: 'authority_curator', pathFollowers: 1543 },
  // Current user
  { rank: 23, userId: 'current', name: 'Current User', handle: 'currentuser', country: 'CA', countryFlag: '🇨🇦', score: 94.7, tier: 'authority_curator', pathFollowers: 1247, isCurrentUser: true },
];

const regions = [
  { id: 'global', label: 'Global', icon: <Globe className="h-4 w-4" /> },
  { id: 'CA', label: 'Canada', icon: <span>🇨🇦</span> },
  { id: 'GB', label: 'UK', icon: <span>🇬🇧</span> },
  { id: 'AU', label: 'Australia', icon: <span>🇦🇺</span> },
  { id: 'NZ', label: 'New Zealand', icon: <span>🇳🇿</span> },
];

const getRankIcon = (rank: number) => {
  if (rank === 1) return <Trophy className="h-5 w-5 text-yellow-500" />;
  if (rank === 2) return <Medal className="h-5 w-5 text-gray-400" />;
  if (rank === 3) return <Medal className="h-5 w-5 text-amber-600" />;
  return null;
};

const getRankStyle = (rank: number) => {
  if (rank === 1) return 'bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-950/30 dark:to-amber-950/30 border-yellow-200 dark:border-yellow-800';
  if (rank === 2) return 'bg-gradient-to-r from-gray-50 to-slate-50 dark:from-gray-900 dark:to-slate-900 border-gray-200 dark:border-gray-700';
  if (rank === 3) return 'bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30 border-amber-200 dark:border-amber-800';
  return '';
};

export const Leaderboard = () => {
  const { user } = useAuthStore();
  const [selectedRegion, setSelectedRegion] = useState('global');
  
  const { data: leaderboard, isLoading } = useLeaderboard(50, selectedRegion === 'global' ? undefined : selectedRegion);
  
  const entries = leaderboard || mockLeaderboard;
  const loading = isLoading && !entries.length;

  // Find current user in leaderboard
  const currentUserEntry = entries.find((e) => e.isCurrentUser);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Trophy className="h-6 w-6 text-amber-500" />
          Leaderboard
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Top Authority Curators on Quirrely
        </p>
      </div>

      {/* Region Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {regions.map((region) => (
          <Button
            key={region.id}
            variant={selectedRegion === region.id ? 'primary' : 'outline'}
            size="sm"
            leftIcon={region.icon}
            onClick={() => setSelectedRegion(region.id)}
          >
            {region.label}
          </Button>
        ))}
      </div>

      {/* Your Position Card */}
      {currentUserEntry && (
        <Card variant="gold" padding="md">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-amber-500 text-white rounded-full flex items-center justify-center font-bold text-lg">
              #{currentUserEntry.rank}
            </div>
            <Avatar name={user?.name || 'You'} src={user?.avatarUrl} size="lg" border borderColor="gold" />
            <div className="flex-1">
              <p className="font-semibold text-gray-900 dark:text-white">{user?.name || 'You'}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Score: {currentUserEntry.score} • {currentUserEntry.pathFollowers.toLocaleString()} followers
              </p>
            </div>
            <Badge variant="gold">
              <Crown className="h-3 w-3 mr-1" />
              Your Position
            </Badge>
          </div>
        </Card>
      )}

      {/* Leaderboard Table */}
      <Card>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {Array(10).fill(0).map((_, i) => (
                <div key={i} className="flex items-center gap-4 p-3">
                  <Skeleton variant="circular" width={40} height={40} />
                  <Skeleton variant="circular" width={48} height={48} />
                  <div className="flex-1">
                    <Skeleton variant="text" width="40%" height={20} className="mb-1" />
                    <Skeleton variant="text" width="30%" height={14} />
                  </div>
                  <Skeleton variant="text" width={60} height={24} />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {entries.map((entry) => (
                <div
                  key={entry.userId}
                  className={`flex items-center gap-4 p-4 rounded-xl border transition-colors ${
                    entry.isCurrentUser
                      ? 'bg-coral-50 dark:bg-coral-950/30 border-coral-200 dark:border-coral-800'
                      : getRankStyle(entry.rank) || 'border-transparent hover:bg-gray-50 dark:hover:bg-gray-800/50'
                  }`}
                >
                  {/* Rank */}
                  <div className="w-10 text-center">
                    {getRankIcon(entry.rank) || (
                      <span className="text-lg font-bold text-gray-400">#{entry.rank}</span>
                    )}
                  </div>

                  {/* Avatar */}
                  <Avatar
                    name={entry.name}
                    src={entry.avatarUrl}
                    size="md"
                    border
                    borderColor={entry.rank <= 3 ? 'gold' : 'default'}
                  />

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-gray-900 dark:text-white">
                        {entry.name}
                      </p>
                      <span>{entry.countryFlag}</span>
                      {entry.isCurrentUser && (
                        <Badge variant="primary" size="sm">You</Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      @{entry.handle} • {entry.pathFollowers.toLocaleString()} followers
                    </p>
                  </div>

                  {/* Score */}
                  <div className="text-right">
                    <p className={`text-xl font-bold ${
                      entry.rank <= 3 ? 'text-amber-600 dark:text-amber-400' : 'text-gray-900 dark:text-white'
                    }`}>
                      {entry.score.toFixed(1)}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">authority</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
