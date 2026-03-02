import { useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Badge, Skeleton } from '@/components/ui';
import { RadarChart, RadarDataPoint } from '@/components/charts';
import { VoiceProfile as VoiceProfileType } from '@/types';

interface VoiceProfileProps {
  profile?: VoiceProfileType;
  loading?: boolean;
  compact?: boolean;
}

// Voice type descriptions
const voiceDescriptions: Record<string, string> = {
  assertive: 'You write with confidence and conviction. Your statements are direct and your opinions clear.',
  narrative: 'You tell stories. Your writing flows with natural rhythm and engages readers emotionally.',
  analytical: 'You break things down methodically. Your writing is precise and evidence-based.',
  poetic: 'You craft language beautifully. Your writing has rhythm, imagery, and emotional resonance.',
  conversational: 'You write like you speak. Your style is warm, approachable, and engaging.',
  minimal: 'You say more with less. Your writing is concise, clean, and impactful.',
};

// Combined voice descriptions
const getVoiceDescription = (primary: string, secondary: string): string => {
  const primaryDesc = voiceDescriptions[primary] || '';
  if (primary === secondary) return primaryDesc;
  
  const combinedDescriptions: Record<string, string> = {
    'assertive-narrative': 'You write with confidence and narrative flair. Your voice combines direct statements with rich storytelling, creating engaging content that guides readers through your ideas.',
    'assertive-analytical': 'You combine conviction with precision. Your writing is both persuasive and well-reasoned, backing up strong opinions with solid evidence.',
    'narrative-poetic': 'You weave stories with beautiful language. Your writing captures imagination while painting vivid pictures with words.',
    'conversational-narrative': 'You tell stories like chatting with a friend. Your writing is warm, engaging, and pulls readers into your world.',
  };
  
  const key = `${primary}-${secondary}`;
  const reverseKey = `${secondary}-${primary}`;
  
  return combinedDescriptions[key] || combinedDescriptions[reverseKey] || primaryDesc;
};

export const VoiceProfile = ({ profile, loading, compact = false }: VoiceProfileProps) => {
  const radarData: RadarDataPoint[] = useMemo(() => {
    if (!profile?.dimensions) return [];
    
    return [
      { subject: 'Assertive', value: Math.round(profile.dimensions.assertiveness * 100) },
      { subject: 'Formal', value: Math.round(profile.dimensions.formality * 100) },
      { subject: 'Detailed', value: Math.round(profile.dimensions.detail * 100) },
      { subject: 'Poetic', value: Math.round(profile.dimensions.poeticism * 100) },
      { subject: 'Open', value: Math.round(profile.dimensions.openness * 100) },
      { subject: 'Dynamic', value: Math.round(profile.dimensions.dynamism * 100) },
    ];
  }, [profile]);

  const voiceTitle = useMemo(() => {
    if (!profile) return '';
    const primary = profile.primary.charAt(0).toUpperCase() + profile.primary.slice(1);
    const secondary = profile.secondary.charAt(0).toUpperCase() + profile.secondary.slice(1);
    if (primary === secondary) return primary;
    return `${primary} ${secondary}`;
  }, [profile]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            📊 Your Writing Voice
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-6">
            <Skeleton variant="circular" width={200} height={200} />
            <div className="flex-1 space-y-3">
              <Skeleton variant="text" width="60%" height={28} />
              <Skeleton variant="text" width="100%" />
              <Skeleton variant="text" width="90%" />
              <div className="flex gap-2 mt-4">
                <Skeleton variant="rectangular" width={80} height={28} className="rounded-full" />
                <Skeleton variant="rectangular" width={80} height={28} className="rounded-full" />
                <Skeleton variant="rectangular" width={80} height={28} className="rounded-full" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!profile) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            📊 Your Writing Voice
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">
              Submit a writing sample to discover your voice profile.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (compact) {
    return (
      <div className="flex items-center gap-4">
        <RadarChart data={radarData} size="sm" showLabels={false} />
        <div>
          <h4 className="font-semibold text-coral-500">{voiceTitle}</h4>
          <div className="flex flex-wrap gap-1 mt-1">
            {profile.tokens.slice(0, 3).map((token) => (
              <Badge key={token.name} variant="primary" size="sm">
                {token.name}
              </Badge>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          📊 Your Writing Voice
        </CardTitle>
        <a href="/dashboard/voice" className="text-sm text-coral-500 hover:text-coral-600 font-medium">
          View Full Analysis →
        </a>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col md:flex-row gap-6 items-start">
          <div className="mx-auto md:mx-0">
            <RadarChart data={radarData} size="md" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-coral-500 mb-2">{voiceTitle}</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {getVoiceDescription(profile.primary, profile.secondary)}
            </p>
            <div className="flex flex-wrap gap-2 mb-4">
              {profile.tokens.map((token) => (
                <Badge key={token.name} variant="primary">
                  {token.name}
                </Badge>
              ))}
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
              <span>
                Confidence: <strong className="text-gray-700 dark:text-gray-300">
                  {Math.round(profile.confidence * 100)}%
                </strong>
              </span>
              <span>
                Based on <strong className="text-gray-700 dark:text-gray-300">
                  {profile.analysesCount}
                </strong> analyses
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
