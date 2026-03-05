import { useState } from 'react';
import { BarChart3, TrendingUp, Eye, Clock, Calendar, Users, FileText } from 'lucide-react';
import { useAuthStore } from '@/stores';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge, Skeleton } from '@/components/ui';

// Date range options
const dateRanges = [
  { id: '7d', label: 'Last 7 days' },
  { id: '30d', label: 'Last 30 days' },
  { id: '90d', label: 'Last 90 days' },
  { id: 'year', label: 'This year' },
];

// Mock analytics data
const mockAnalytics = {
  totalViews: 12847,
  totalReads: 8234,
  avgReadTime: '4:32',
  completionRate: 64,
  followers: 1247,
  postsPublished: 23,
  trends: {
    views: 12,
    reads: 8,
    followers: 15,
  },
  topPosts: [
    { id: '1', title: 'Finding Your Voice in a Noisy World', views: 2341, reads: 1876, completionRate: 78 },
    { id: '2', title: 'The Art of Narrative Non-Fiction', views: 1923, reads: 1456, completionRate: 72 },
    { id: '3', title: 'Why Canadian Writers Are Leading the Literary Renaissance', views: 1654, reads: 1234, completionRate: 68 },
    { id: '4', title: 'Writing with Intention: A Guide', views: 1432, reads: 987, completionRate: 65 },
    { id: '5', title: 'The Commonwealth Connection', views: 1187, reads: 834, completionRate: 61 },
  ],
  weeklyData: [
    { day: 'Mon', views: 423, reads: 312 },
    { day: 'Tue', views: 389, reads: 287 },
    { day: 'Wed', views: 512, reads: 398 },
    { day: 'Thu', views: 478, reads: 356 },
    { day: 'Fri', views: 534, reads: 412 },
    { day: 'Sat', views: 321, reads: 234 },
    { day: 'Sun', views: 298, reads: 198 },
  ],
};

export const Analytics = () => {
  const { user } = useAuthStore();
  const [dateRange, setDateRange] = useState('30d');
  const [isLoading] = useState(false);

  const analytics = mockAnalytics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-coral-500" />
            Writing Analytics
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Track your writing performance and audience engagement
          </p>
        </div>
        
        {/* Date Range Filter */}
        <div className="flex gap-2">
          {dateRanges.map((range) => (
            <Button
              key={range.id}
              variant={dateRange === range.id ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setDateRange(range.id)}
            >
              {range.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            {isLoading ? (
              <Skeleton variant="rectangular" height={80} />
            ) : (
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Eye className="h-5 w-5 text-coral-500" />
                </div>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {analytics.totalViews.toLocaleString()}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Views</p>
                <Badge variant="success" size="sm" className="mt-2">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +{analytics.trends.views}%
                </Badge>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            {isLoading ? (
              <Skeleton variant="rectangular" height={80} />
            ) : (
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <FileText className="h-5 w-5 text-coral-500" />
                </div>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {analytics.totalReads.toLocaleString()}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Reads</p>
                <Badge variant="success" size="sm" className="mt-2">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +{analytics.trends.reads}%
                </Badge>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            {isLoading ? (
              <Skeleton variant="rectangular" height={80} />
            ) : (
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Clock className="h-5 w-5 text-coral-500" />
                </div>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {analytics.avgReadTime}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Avg. Read Time</p>
                <p className="text-xs text-gray-400 mt-2">{analytics.completionRate}% completion</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            {isLoading ? (
              <Skeleton variant="rectangular" height={80} />
            ) : (
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Users className="h-5 w-5 text-coral-500" />
                </div>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {analytics.followers.toLocaleString()}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Followers</p>
                <Badge variant="success" size="sm" className="mt-2">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +{analytics.trends.followers}%
                </Badge>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Activity Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Weekly Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton variant="rectangular" height={200} />
            ) : (
              <div className="space-y-3">
                {analytics.weeklyData.map((day) => (
                  <div key={day.day} className="flex items-center gap-3">
                    <span className="w-10 text-sm text-gray-500 dark:text-gray-400">{day.day}</span>
                    <div className="flex-1 flex gap-1">
                      <div 
                        className="h-6 bg-coral-500 rounded-l"
                        style={{ width: `${(day.views / 600) * 100}%` }}
                        title={`${day.views} views`}
                      />
                      <div 
                        className="h-6 bg-coral-300 rounded-r"
                        style={{ width: `${(day.reads / 600) * 100}%` }}
                        title={`${day.reads} reads`}
                      />
                    </div>
                    <span className="w-20 text-right text-sm text-gray-600 dark:text-gray-400">
                      {day.views} / {day.reads}
                    </span>
                  </div>
                ))}
                <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-coral-500 rounded" />
                    <span className="text-sm text-gray-500">Views</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-coral-300 rounded" />
                    <span className="text-sm text-gray-500">Reads</span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Stats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <span className="text-gray-600 dark:text-gray-400">Posts Published</span>
                <span className="text-xl font-bold text-gray-900 dark:text-white">{analytics.postsPublished}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <span className="text-gray-600 dark:text-gray-400">Avg. Views/Post</span>
                <span className="text-xl font-bold text-gray-900 dark:text-white">
                  {Math.round(analytics.totalViews / analytics.postsPublished).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <span className="text-gray-600 dark:text-gray-400">Read-to-View Ratio</span>
                <span className="text-xl font-bold text-gray-900 dark:text-white">
                  {Math.round((analytics.totalReads / analytics.totalViews) * 100)}%
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <span className="text-gray-600 dark:text-gray-400">Completion Rate</span>
                <span className="text-xl font-bold text-gray-900 dark:text-white">{analytics.completionRate}%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Posts Table */}
      <Card>
        <CardHeader>
          <CardTitle>Top Performing Posts</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} variant="rectangular" height={48} />
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-sm text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
                    <th className="pb-3 font-medium">Post Title</th>
                    <th className="pb-3 font-medium text-right">Views</th>
                    <th className="pb-3 font-medium text-right">Reads</th>
                    <th className="pb-3 font-medium text-right">Completion</th>
                  </tr>
                </thead>
                <tbody>
                  {analytics.topPosts.map((post, index) => (
                    <tr 
                      key={post.id} 
                      className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                    >
                      <td className="py-4">
                        <div className="flex items-center gap-3">
                          <span className="w-6 h-6 flex items-center justify-center bg-coral-100 dark:bg-coral-900/30 text-coral-600 dark:text-coral-400 rounded-full text-sm font-medium">
                            {index + 1}
                          </span>
                          <span className="font-medium text-gray-900 dark:text-white truncate max-w-md">
                            {post.title}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 text-right text-gray-600 dark:text-gray-400">
                        {post.views.toLocaleString()}
                      </td>
                      <td className="py-4 text-right text-gray-600 dark:text-gray-400">
                        {post.reads.toLocaleString()}
                      </td>
                      <td className="py-4 text-right">
                        <Badge variant={post.completionRate >= 70 ? 'success' : 'default'}>
                          {post.completionRate}%
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Insights Footer */}
      <Card className="bg-gradient-to-r from-coral-50 to-orange-50 dark:from-coral-950/30 dark:to-orange-950/30 border-coral-200 dark:border-coral-800">
        <CardContent className="py-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-coral-100 dark:bg-coral-900/50 rounded-full">
              <TrendingUp className="h-6 w-6 text-coral-600 dark:text-coral-400" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                Your writing is gaining momentum!
              </h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Your views are up {analytics.trends.views}% compared to last month. 
                Your narrative style posts perform best with a {analytics.completionRate}% completion rate.
                Keep writing about Canadian literature — it's resonating with your audience.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
