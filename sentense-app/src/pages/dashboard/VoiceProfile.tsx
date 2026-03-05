import { Sparkles, TrendingUp, Download, Share2, History, Lightbulb } from 'lucide-react';
import { useVoiceProfile } from '@/hooks';
import { useAuthStore } from '@/stores';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge, Skeleton } from '@/components/ui';
import { RadarChart } from '@/components/charts';

// Mock data
const mockVoiceProfile = {
  primary: 'assertive',
  secondary: 'narrative',
  openness: 'balanced' as const,
  mode: 'ASSERTIVE_BALANCED',
  tokens: [
    { name: 'Confident', weight: 0.89 },
    { name: 'Warm', weight: 0.76 },
    { name: 'Structured', weight: 0.82 },
    { name: 'Narrative', weight: 0.91 },
    { name: 'Engaged', weight: 0.85 },
  ],
  dimensions: {
    assertiveness: 0.87,
    formality: 0.62,
    detail: 0.74,
    poeticism: 0.68,
    openness: 0.55,
    dynamism: 0.81,
  },
  confidence: 0.872,
  analysesCount: 47,
  lastAnalysis: new Date().toISOString(),
};

const mockHistory = [
  { date: '2026-01-15', primary: 'assertive', confidence: 0.87 },
  { date: '2025-12-15', primary: 'assertive', confidence: 0.84 },
  { date: '2025-11-15', primary: 'narrative', confidence: 0.79 },
  { date: '2025-10-15', primary: 'narrative', confidence: 0.72 },
];

const mockInsights = [
  { type: 'strength', title: 'Strong narrative voice', description: 'Your storytelling captivates readers and keeps them engaged.' },
  { type: 'growth', title: 'Growing confidence', description: 'Your voice confidence has increased 15% over the last 3 months.' },
  { type: 'tip', title: 'Try more poetic elements', description: 'Adding metaphors could enhance your already engaging style.' },
];

export const VoiceProfilePage = () => {
  const { user } = useAuthStore();
  const { data: voiceProfile, isLoading } = useVoiceProfile();
  
  const profile = voiceProfile || mockVoiceProfile;
  // Voice + Style addon unlocks premium features regardless of track
  const hasVoiceStyle = user?.addons?.includes('voice_style') ?? false;

  const radarData = [
    { subject: 'Assertive', value: Math.round(profile.dimensions.assertiveness * 100) },
    { subject: 'Formal', value: Math.round(profile.dimensions.formality * 100) },
    { subject: 'Detailed', value: Math.round(profile.dimensions.detail * 100) },
    { subject: 'Poetic', value: Math.round(profile.dimensions.poeticism * 100) },
    { subject: 'Open', value: Math.round(profile.dimensions.openness * 100) },
    { subject: 'Dynamic', value: Math.round(profile.dimensions.dynamism * 100) },
  ];

  const voiceTitle = `${profile.primary.charAt(0).toUpperCase() + profile.primary.slice(1)} ${profile.secondary.charAt(0).toUpperCase() + profile.secondary.slice(1)}`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-emerald-500" />
            Your Writing Voice
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Deep analysis of your unique writing style
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" leftIcon={<Share2 className="h-4 w-4" />}>
            Share
          </Button>
          <Button variant="outline" leftIcon={<Download className="h-4 w-4" />}>
            Export
          </Button>
        </div>
      </div>

      {/* Main Profile Card */}
      <Card className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/30 border-emerald-200 dark:border-emerald-800">
        <CardContent className="py-8">
          {isLoading ? (
            <div className="flex flex-col md:flex-row gap-8 items-center">
              <Skeleton variant="circular" width={250} height={250} />
              <div className="flex-1 space-y-4">
                <Skeleton variant="text" width="60%" height={36} />
                <Skeleton variant="text" width="100%" height={20} />
                <Skeleton variant="text" width="90%" height={20} />
              </div>
            </div>
          ) : (
            <div className="flex flex-col md:flex-row gap-8 items-center">
              <RadarChart data={radarData} size="lg" color="#10B981" />
              <div className="flex-1">
                <h2 className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 mb-3">
                  {voiceTitle}
                </h2>
                <p className="text-gray-600 dark:text-gray-400 text-lg mb-4">
                  You write with confidence and narrative flair. Your voice combines direct statements 
                  with rich storytelling, creating engaging content that guides readers through your ideas.
                </p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {profile.tokens.map((token) => (
                    <Badge key={token.name} variant="success" size="lg">
                      {token.name}
                      <span className="ml-1 opacity-70">{Math.round(token.weight * 100)}%</span>
                    </Badge>
                  ))}
                </div>
                <div className="flex items-center gap-6 text-sm text-gray-500 dark:text-gray-400">
                  <span>
                    Confidence: <strong className="text-emerald-600">{Math.round(profile.confidence * 100)}%</strong>
                  </span>
                  <span>
                    Based on <strong>{profile.analysesCount}</strong> analyses
                  </span>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Dimensions Breakdown */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Voice Dimensions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(profile.dimensions).map(([key, value]) => (
                <div key={key}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="capitalize text-gray-700 dark:text-gray-300">{key}</span>
                    <span className="font-medium text-gray-900 dark:text-white">{Math.round(value * 100)}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full transition-all"
                      style={{ width: `${value * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5" />
              AI Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockInsights.map((insight, i) => (
                <div key={i} className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge
                      variant={insight.type === 'strength' ? 'success' : insight.type === 'growth' ? 'primary' : 'default'}
                      size="sm"
                    >
                      {insight.type}
                    </Badge>
                  </div>
                  <p className="font-medium text-gray-900 dark:text-white text-sm">{insight.title}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{insight.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Voice History */}
      {hasVoiceStyle && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              Voice Evolution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {mockHistory.map((entry, i) => (
                <div key={i} className="flex items-center gap-4 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <div className="text-sm text-gray-500 dark:text-gray-400 w-24">
                    {new Date(entry.date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                  </div>
                  <Badge variant="primary" className="capitalize">{entry.primary}</Badge>
                  <div className="flex-1">
                    <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full"
                        style={{ width: `${entry.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {Math.round(entry.confidence * 100)}%
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-4 text-center">
              Your voice has become more confident and consistent over time
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
