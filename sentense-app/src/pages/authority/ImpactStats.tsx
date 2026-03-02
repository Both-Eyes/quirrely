import { TrendingUp, Users, BookOpen, Target, Award, Zap } from 'lucide-react';
import { useImpactStats } from '@/hooks';
import { Card, CardHeader, CardTitle, CardContent, Badge, Skeleton } from '@/components/ui';
import { MetricCard } from '@/components/charts';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

// Mock data
const mockImpact = {
  totalReach: 45672,
  totalInfluence: 12847,
  writersInspired: 234,
  pathsCompleted: 1567,
  topContributions: [
    { type: 'path' as const, title: 'Canadian Voices: Modern Literary Fiction', impact: 4521, date: '2025-11-01' },
    { type: 'post' as const, title: 'The Art of Confident Writing', impact: 2341, date: '2025-10-15' },
    { type: 'feature' as const, title: 'Featured in Weekly Spotlight', impact: 1876, date: '2025-09-20' },
    { type: 'path' as const, title: 'Nature Writing & Environmental Essays', impact: 1654, date: '2025-08-01' },
  ],
  impactTrend: [
    { date: 'Aug', impact: 5400 },
    { date: 'Sep', impact: 7200 },
    { date: 'Oct', impact: 9800 },
    { date: 'Nov', impact: 11200 },
    { date: 'Dec', impact: 12400 },
    { date: 'Jan', impact: 12847 },
  ],
  categoryBreakdown: [
    { category: 'Reading Paths', percentage: 45 },
    { category: 'Featured Content', percentage: 25 },
    { category: 'Community Engagement', percentage: 20 },
    { category: 'Direct Influence', percentage: 10 },
  ],
};

const COLORS = ['#FF6B6B', '#4ECDC4', '#FFD93D', '#6C5CE7'];

const contributionIcons = {
  path: '🛤️',
  post: '📝',
  feature: '⭐',
};

export const ImpactStats = () => {
  const { data: impact, isLoading } = useImpactStats();
  
  const displayImpact = impact || mockImpact;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <TrendingUp className="h-6 w-6 text-coral-500" />
          Impact Stats
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Your influence on the Quirrely community
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Total Reach"
          value={displayImpact.totalReach.toLocaleString()}
          trend={{ value: 18, direction: 'up', period: 'this month' }}
          icon={<Users className="h-6 w-6 text-coral-500" />}
          loading={isLoading}
        />
        <MetricCard
          label="Influence Score"
          value={displayImpact.totalInfluence.toLocaleString()}
          trend={{ value: 12, direction: 'up', period: 'this month' }}
          icon={<Zap className="h-6 w-6 text-coral-500" />}
          loading={isLoading}
        />
        <MetricCard
          label="Writers Inspired"
          value={displayImpact.writersInspired}
          trend={{ value: 8, direction: 'up', period: 'this month' }}
          icon={<Award className="h-6 w-6 text-coral-500" />}
          loading={isLoading}
        />
        <MetricCard
          label="Paths Completed"
          value={displayImpact.pathsCompleted.toLocaleString()}
          trend={{ value: 15, direction: 'up', period: 'this month' }}
          icon={<Target className="h-6 w-6 text-coral-500" />}
          loading={isLoading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Impact Trend Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Impact Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton variant="rectangular" height={250} />
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={displayImpact.impactTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="date" stroke="#9CA3AF" fontSize={12} />
                  <YAxis stroke="#9CA3AF" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      border: '1px solid #E5E7EB',
                      borderRadius: '8px',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="impact"
                    stroke="#FF6B6B"
                    strokeWidth={3}
                    dot={{ fill: '#FF6B6B', strokeWidth: 2 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Category Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Impact Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton variant="circular" width={200} height={200} className="mx-auto" />
            ) : (
              <>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={displayImpact.categoryBreakdown}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="percentage"
                    >
                      {displayImpact.categoryBreakdown.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value: number) => `${value}%`}
                      contentStyle={{
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        border: '1px solid #E5E7EB',
                        borderRadius: '8px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="space-y-2 mt-4">
                  {displayImpact.categoryBreakdown.map((item, index) => (
                    <div key={item.category} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: COLORS[index] }}
                        />
                        <span className="text-gray-600 dark:text-gray-400">{item.category}</span>
                      </div>
                      <span className="font-medium text-gray-900 dark:text-white">{item.percentage}%</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Top Contributions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5" />
            Top Contributions
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {Array(4).fill(0).map((_, i) => (
                <div key={i} className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <Skeleton variant="rectangular" width={48} height={48} className="rounded-xl" />
                  <div className="flex-1">
                    <Skeleton variant="text" width="60%" height={20} className="mb-1" />
                    <Skeleton variant="text" width="30%" height={14} />
                  </div>
                  <Skeleton variant="text" width={60} height={24} />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {displayImpact.topContributions.map((contribution, index) => (
                <div
                  key={index}
                  className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl"
                >
                  <div className="w-12 h-12 bg-coral-100 dark:bg-coral-900/30 rounded-xl flex items-center justify-center text-2xl">
                    {contributionIcons[contribution.type]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-gray-900 dark:text-white truncate">
                        {contribution.title}
                      </h4>
                      <Badge variant="default" size="sm" className="capitalize">
                        {contribution.type}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(contribution.date).toLocaleDateString('en-US', {
                        month: 'short',
                        year: 'numeric',
                      })}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold text-green-600 dark:text-green-400">
                      +{contribution.impact.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">impact</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Inspiration Banner */}
      <Card className="bg-gradient-to-r from-coral-50 to-amber-50 dark:from-coral-950/30 dark:to-amber-950/30 border-coral-200 dark:border-coral-800">
        <CardContent className="py-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white dark:bg-gray-900 rounded-full flex items-center justify-center text-3xl shadow-lg">
              🌟
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-gray-900 dark:text-white text-lg">
                You're making a difference!
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Your curated paths have helped {displayImpact.writersInspired} writers find their voice this month.
                Keep inspiring the community!
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
