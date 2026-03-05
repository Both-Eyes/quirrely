/**
 * ProfileTab.jsx - Your Evolving Writer Profile
 * 
 * Displays the user's evolving narrator profile built from their writing history.
 * v0.7.0 - New tab for personalized profile sketches
 */

import React from 'react';

// =============================================================================
// SUBCOMPONENTS
// =============================================================================

const ProfileHeader = ({ header }) => {
  const maturityColors = {
    EMERGING: 'bg-amber-50 border-amber-200 text-amber-800',
    DEVELOPING: 'bg-blue-50 border-blue-200 text-blue-800',
    ESTABLISHED: 'bg-green-50 border-green-200 text-green-800',
    MATURE: 'bg-purple-50 border-purple-200 text-purple-800',
  };
  
  const maturityEmoji = {
    EMERGING: '🌱',
    DEVELOPING: '📈',
    ESTABLISHED: '✨',
    MATURE: '🎯',
  };
  
  return (
    <div className="mb-6">
      {/* Title and maturity badge */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h2 className="text-2xl font-semibold text-stone-800">{header.title}</h2>
          <p className="text-stone-500 italic mt-1">{header.essence}</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm border ${maturityColors[header.maturity] || maturityColors.EMERGING}`}>
          {maturityEmoji[header.maturity]} {header.maturity}
        </div>
      </div>
      
      {/* Session count and maturity description */}
      <p className="text-sm text-stone-600">
        {header.maturity_description}
      </p>
      <p className="text-xs text-stone-400 mt-1">
        Based on {header.session_count} writing session{header.session_count !== 1 ? 's' : ''}
      </p>
    </div>
  );
};


const PersonalizedSketch = ({ sketch }) => {
  // Parse markdown-like bold text
  const formatSketch = (text) => {
    const parts = text.split(/\*\*(.*?)\*\*/g);
    return parts.map((part, i) => 
      i % 2 === 1 ? <strong key={i} className="text-stone-900">{part}</strong> : part
    );
  };
  
  return (
    <div className="bg-stone-50 rounded-lg p-5 mb-6 border border-stone-200">
      <h3 className="text-sm font-medium text-stone-500 uppercase tracking-wide mb-3">
        Your Writing Portrait
      </h3>
      <div className="prose prose-stone prose-sm">
        {sketch.split('\n\n').map((para, i) => (
          <p key={i} className="mb-3 text-stone-700 leading-relaxed">
            {formatSketch(para)}
          </p>
        ))}
      </div>
    </div>
  );
};


const ModeBreakdown = ({ modes }) => {
  const modeColors = {
    MINIMAL: 'bg-stone-100',
    DENSE: 'bg-amber-100',
    POETIC: 'bg-violet-100',
    INTERROGATIVE: 'bg-sky-100',
    ASSERTIVE: 'bg-red-100',
    HEDGED: 'bg-green-100',
    PARENTHETICAL: 'bg-orange-100',
    PARALLEL: 'bg-pink-100',
    LONGFORM: 'bg-indigo-100',
    CONVERSATIONAL: 'bg-yellow-100',
  };
  
  // Sort distribution by count
  const sortedModes = Object.entries(modes.distribution || {})
    .sort((a, b) => b[1] - a[1]);
  
  const total = sortedModes.reduce((sum, [, count]) => sum + count, 0);
  
  return (
    <div className="mb-6">
      <h3 className="text-sm font-medium text-stone-500 uppercase tracking-wide mb-3">
        Mode Distribution
      </h3>
      
      {/* Primary mode highlight */}
      <div className="flex items-center gap-3 mb-4">
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${modeColors[modes.primary] || 'bg-stone-100'}`}>
          {modes.primary}
        </span>
        <span className="text-sm text-stone-500">
          {modes.confidence} confidence · {modes.consistency} of sessions
        </span>
      </div>
      
      {/* Bar chart of modes */}
      <div className="space-y-2">
        {sortedModes.map(([mode, count]) => (
          <div key={mode} className="flex items-center gap-2">
            <span className="text-xs text-stone-500 w-28 truncate">{mode}</span>
            <div className="flex-1 bg-stone-100 rounded-full h-2 overflow-hidden">
              <div 
                className={`h-full ${modeColors[mode] || 'bg-stone-300'}`}
                style={{ width: `${(count / total) * 100}%` }}
              />
            </div>
            <span className="text-xs text-stone-400 w-8 text-right">{count}</span>
          </div>
        ))}
      </div>
      
      {/* Secondary modes */}
      {modes.secondary && modes.secondary.length > 0 && (
        <p className="text-sm text-stone-500 mt-3">
          Secondary tendencies: {modes.secondary.join(', ')}
        </p>
      )}
    </div>
  );
};


const MetricsGrid = ({ metrics }) => {
  const metricLabels = {
    words_per_session: 'Words/Session',
    words_per_sentence: 'Words/Sentence',
    markers_per_session: 'Markers/Session',
    epistemic_openness: 'Openness',
    structural_density: 'Density',
    informality: 'Informality',
  };
  
  return (
    <div className="mb-6">
      <h3 className="text-sm font-medium text-stone-500 uppercase tracking-wide mb-3">
        Your Numbers
      </h3>
      <div className="grid grid-cols-3 gap-3">
        {Object.entries(metrics).map(([key, value]) => (
          <div key={key} className="bg-white border border-stone-200 rounded-lg p-3 text-center">
            <div className="text-xl font-semibold text-stone-800">{value}</div>
            <div className="text-xs text-stone-500">{metricLabels[key] || key}</div>
          </div>
        ))}
      </div>
    </div>
  );
};


const EvolutionSection = ({ evolution }) => {
  const trendIcons = {
    INCREASING: '📈',
    SLIGHTLY_INCREASING: '↗️',
    STABLE: '➡️',
    SLIGHTLY_DECREASING: '↘️',
    DECREASING: '📉',
    INSUFFICIENT_DATA: '⏳',
  };
  
  const trendColors = {
    INCREASING: 'text-green-600',
    SLIGHTLY_INCREASING: 'text-green-500',
    STABLE: 'text-stone-500',
    SLIGHTLY_DECREASING: 'text-amber-500',
    DECREASING: 'text-red-500',
    INSUFFICIENT_DATA: 'text-stone-400',
  };
  
  return (
    <div className="mb-6">
      <h3 className="text-sm font-medium text-stone-500 uppercase tracking-wide mb-3">
        How You're Evolving
      </h3>
      <div className="space-y-3">
        {Object.entries(evolution).map(([metric, data]) => (
          <div key={metric} className="flex items-start gap-3 bg-white border border-stone-200 rounded-lg p-3">
            <span className="text-xl">{trendIcons[data.trend] || '➡️'}</span>
            <div>
              <div className={`font-medium ${trendColors[data.trend] || 'text-stone-600'}`}>
                {data.description}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};


const InsightsSection = ({ insights }) => {
  if (!insights || insights.length === 0) return null;
  
  return (
    <div className="mb-6">
      <h3 className="text-sm font-medium text-stone-500 uppercase tracking-wide mb-3">
        Insights
      </h3>
      <div className="space-y-2">
        {insights.map((insight, i) => (
          <div key={i} className="flex items-start gap-2 text-sm text-stone-700">
            <span className="text-amber-500">◆</span>
            <span>{insight}</span>
          </div>
        ))}
      </div>
    </div>
  );
};


const GrowthEdgesSection = ({ edges, ancestors }) => {
  return (
    <div className="border-t border-stone-200 pt-6">
      <h3 className="text-sm font-medium text-stone-500 uppercase tracking-wide mb-3">
        Growth Edges
      </h3>
      <div className="space-y-2 mb-6">
        {edges.map((edge, i) => (
          <div key={i} className="flex items-start gap-2 text-sm text-stone-600">
            <span className="text-green-500">→</span>
            <span>{edge}</span>
          </div>
        ))}
      </div>
      
      <h3 className="text-sm font-medium text-stone-500 uppercase tracking-wide mb-2">
        Writing Ancestors
      </h3>
      <p className="text-sm text-stone-600 italic">{ancestors}</p>
    </div>
  );
};


const NoHistoryState = ({ message, cta }) => {
  return (
    <div className="text-center py-12">
      <div className="text-6xl mb-4">📝</div>
      <h3 className="text-xl font-medium text-stone-700 mb-2">Your Profile Awaits</h3>
      <p className="text-stone-500 mb-4 max-w-md mx-auto">
        {message}
      </p>
      <p className="text-sm text-stone-400">{cta}</p>
    </div>
  );
};


// =============================================================================
// MAIN COMPONENT
// =============================================================================

const ProfileTab = ({ userProfile }) => {
  // Handle missing or error states
  if (!userProfile) {
    return (
      <div className="p-4">
        <NoHistoryState 
          message="Loading your profile..."
          cta="Please wait"
        />
      </div>
    );
  }
  
  if (userProfile.status === 'NO_HISTORY') {
    return (
      <div className="p-4">
        <NoHistoryState 
          message={userProfile.message}
          cta={userProfile.cta}
        />
      </div>
    );
  }
  
  if (userProfile.status === 'ERROR') {
    return (
      <div className="p-4 text-center text-red-500">
        <p>Error loading profile: {userProfile.message}</p>
      </div>
    );
  }
  
  // Active profile state
  return (
    <div className="p-4 max-w-2xl mx-auto">
      {/* Header with title and maturity */}
      <ProfileHeader header={userProfile.header} />
      
      {/* Main personalized sketch */}
      <PersonalizedSketch sketch={userProfile.sketch} />
      
      {/* Two-column layout for details */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Left column */}
        <div>
          <ModeBreakdown modes={userProfile.modes} />
          <MetricsGrid metrics={userProfile.metrics} />
        </div>
        
        {/* Right column */}
        <div>
          <EvolutionSection evolution={userProfile.evolution} />
          <InsightsSection insights={userProfile.insights} />
        </div>
      </div>
      
      {/* Growth section */}
      <GrowthEdgesSection 
        edges={userProfile.growth_edges}
        ancestors={userProfile.writing_ancestors}
      />
      
      {/* Footer with session info */}
      <div className="mt-8 pt-4 border-t border-stone-100 text-xs text-stone-400 text-center">
        First session: {userProfile.meta?.first_session?.slice(0, 10) || 'Unknown'} · 
        Latest: {userProfile.meta?.latest_session?.slice(0, 10) || 'Unknown'}
      </div>
    </div>
  );
};

export default ProfileTab;
