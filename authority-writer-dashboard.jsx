import React, { useState } from 'react';
import { 
  Crown, Users, BookOpen, Flame, PenTool, Star, Trophy, TrendingUp,
  Settings, Bell, Moon, Sun, Menu, X, ChevronDown, Sparkles,
  BarChart3, Compass, Bookmark, Route, HelpCircle, LogOut,
  Award, Target, Zap, Heart, MessageCircle, Share2, ExternalLink
} from 'lucide-react';

// Authority Writer Dashboard - Knight of Wands v3.0.0
// User: Canadian Authority Writer, 90 days in system

const AuthorityWriterDashboard = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  // User profile data
  const user = {
    name: "Alexandra Chen",
    handle: "alexwrites",
    email: "alex@example.com",
    tier: "authority_writer",
    country: "CA",
    countryFlag: "🍁",
    daysInSystem: 90,
    addons: ["voice_style"],
    avatarUrl: null,
  };
  
  // Stats
  const stats = {
    authorityScore: 94.7,
    authorityTrend: +2.3,
    globalRank: 23,
    percentile: 99.2,
    pathFollowers: 1247,
    followersTrend: +12,
    totalReads: 3842,
    readsTrend: +8,
    readingStreak: 23,
    postsWritten: 47,
    analysesCompleted: 67,
  };
  
  // Voice profile
  const voiceProfile = {
    primary: "Assertive",
    secondary: "Narrative",
    confidence: 87.2,
    tokens: [
      { name: "Confident", weight: 89 },
      { name: "Narrative", weight: 91 },
      { name: "Engaged", weight: 85 },
      { name: "Structured", weight: 82 },
      { name: "Warm", weight: 76 },
    ],
    dimensions: {
      assertiveness: 87,
      formality: 62,
      detail: 74,
      poeticism: 68,
      openness: 55,
      dynamism: 81,
    },
  };
  
  // Activity feed
  const activities = [
    { id: 1, type: "award", content: "Reached Top 25 Authority Writers globally!", time: "2 hours ago", icon: Trophy },
    { id: 2, type: "follow", content: "23 new followers on your Canadian Voices path", time: "5 hours ago", icon: Users },
    { id: 3, type: "badge", content: "Earned Consistency Badge — 23 day reading streak!", time: "Yesterday", icon: Award },
    { id: 4, type: "feature", content: "Your essay was featured in Weekly Picks", time: "2 days ago", icon: Star },
    { id: 5, type: "milestone", content: "Voice confidence reached 87%!", time: "3 days ago", icon: Sparkles },
  ];
  
  // Reading paths
  const paths = [
    { id: 1, title: "Canadian Voices: Modern Literary Fiction", posts: 12, followers: 438, trend: +15 },
    { id: 2, title: "Nature Writing & Environmental Essays", posts: 8, followers: 312, trend: +8 },
    { id: 3, title: "Finding Your Voice: A Writer's Journey", posts: 15, followers: 297, trend: +12 },
  ];

  const bgClass = darkMode ? 'bg-gray-950 text-gray-100' : 'bg-gray-50 text-gray-900';
  const cardClass = darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200';
  const mutedClass = darkMode ? 'text-gray-400' : 'text-gray-500';
  
  return (
    <div className={`min-h-screen ${bgClass} transition-colors duration-200`}>
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 ${cardClass} border-r transform transition-transform duration-300 ease-out lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        {/* Mobile close */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800 lg:hidden">
          <span className="font-semibold">Menu</span>
          <button onClick={() => setSidebarOpen(false)} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Profile */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-amber-400 to-yellow-500 flex items-center justify-center text-white font-bold text-lg ring-2 ring-amber-400/50">
              AC
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold truncate">{user.name}</p>
              <p className={`text-sm ${mutedClass} truncate`}>@{user.handle}</p>
            </div>
          </div>
        </div>
        
        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-6 overflow-y-auto">
          {/* Reader Section */}
          <div>
            <h3 className={`px-3 mb-2 text-xs font-semibold ${mutedClass} uppercase tracking-wider`}>Reader</h3>
            <ul className="space-y-1">
              <li>
                <a href="#" className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-[#FF6B6B] text-white font-medium">
                  <BarChart3 className="w-5 h-5" />
                  <span>Dashboard</span>
                </a>
              </li>
              <li>
                <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} hover:bg-gray-100 dark:hover:bg-gray-800`}>
                  <Compass className="w-5 h-5" />
                  <span>Discover</span>
                </a>
              </li>
              <li>
                <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} hover:bg-gray-100 dark:hover:bg-gray-800`}>
                  <Bookmark className="w-5 h-5" />
                  <span>Bookmarks</span>
                </a>
              </li>
              <li>
                <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} hover:bg-gray-100 dark:hover:bg-gray-800`}>
                  <Flame className="w-5 h-5" />
                  <span>Reading Streak</span>
                  <span className="ml-auto text-xs bg-[#FF6B6B] text-white px-2 py-0.5 rounded-full">23</span>
                </a>
              </li>
            </ul>
          </div>
          
          {/* Writer Section */}
          <div>
            <h3 className={`px-3 mb-2 text-xs font-semibold ${mutedClass} uppercase tracking-wider`}>Writer</h3>
            <ul className="space-y-1">
              <li>
                <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} hover:bg-gray-100 dark:hover:bg-gray-800`}>
                  <PenTool className="w-5 h-5" />
                  <span>My Writing</span>
                </a>
              </li>
              <li>
                <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} hover:bg-gray-100 dark:hover:bg-gray-800`}>
                  <Sparkles className="w-5 h-5" />
                  <span>Voice Profile</span>
                  <span className="ml-auto text-xs bg-emerald-500 text-white px-2 py-0.5 rounded-full">✨</span>
                </a>
              </li>
              <li>
                <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} hover:bg-gray-100 dark:hover:bg-gray-800`}>
                  <BarChart3 className="w-5 h-5" />
                  <span>Analytics</span>
                </a>
              </li>
            </ul>
          </div>
          
          {/* Authority Section */}
          <div>
            <h3 className={`px-3 mb-2 text-xs font-semibold ${mutedClass} uppercase tracking-wider`}>Authority</h3>
            <ul className="space-y-1">
              <li>
                <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} hover:bg-gray-100 dark:hover:bg-gray-800`}>
                  <Crown className="w-5 h-5 text-amber-500" />
                  <span>Authority Hub</span>
                </a>
              </li>
              <li>
                <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} hover:bg-gray-100 dark:hover:bg-gray-800`}>
                  <Trophy className="w-5 h-5" />
                  <span>Leaderboard</span>
                </a>
              </li>
              <li>
                <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} hover:bg-gray-100 dark:hover:bg-gray-800`}>
                  <TrendingUp className="w-5 h-5" />
                  <span>Impact Stats</span>
                </a>
              </li>
            </ul>
          </div>
        </nav>
        
        {/* Bottom nav */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-800">
          <ul className="space-y-1">
            <li>
              <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} hover:bg-gray-100 dark:hover:bg-gray-800`}>
                <Settings className="w-5 h-5" />
                <span>Settings</span>
              </a>
            </li>
            <li>
              <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} hover:bg-gray-100 dark:hover:bg-gray-800`}>
                <HelpCircle className="w-5 h-5" />
                <span>Help & Support</span>
              </a>
            </li>
          </ul>
        </div>
      </aside>
      
      {/* Main content */}
      <div className="lg:pl-64">
        {/* Header */}
        <header className={`sticky top-0 z-30 h-16 flex items-center justify-between px-4 lg:px-6 ${cardClass} border-b`}>
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(true)} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 lg:hidden">
              <Menu className="w-5 h-5" />
            </button>
            
            {/* Logo */}
            <div className="flex items-center gap-3">
              <svg viewBox="0 0 100 120" width="32" height="38">
                <path d="M58 112 Q85 98, 94 62 Q100 26, 74 8 Q50 -8, 42 22 Q38 44, 54 60 Q70 78, 62 100 Q58 110, 58 112" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
                <ellipse cx="40" cy="98" rx="22" ry="26" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
                <ellipse cx="40" cy="78" rx="9" ry="4" fill="#E85A5A"/>
                <path d="M31 78 Q30 94, 40 99 Q50 94, 49 78 Z" fill="#FF6B6B"/>
                <ellipse cx="40" cy="50" rx="22" ry="20" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
                <ellipse cx="32" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>
                <ellipse cx="48" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>
                <circle cx="33" cy="46.5" r="2" fill="#FFF"/>
                <circle cx="49" cy="46.5" r="2" fill="#FFF"/>
                <ellipse cx="40" cy="60" rx="4.5" ry="3.5" fill="#4A4A4A"/>
              </svg>
              <span className="text-xl font-bold hidden sm:block">Quirrely</span>
            </div>
            
            {/* Tier badges */}
            <div className="hidden sm:flex items-center gap-2">
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300">
                👑 Authority Writer
              </span>
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300">
                ✨ Voice + Style
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            
            <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#FF6B6B] rounded-full" />
            </button>
            
            <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-lg bg-gray-100 dark:bg-gray-800 text-sm">
              <span>🍁</span>
              <span className={mutedClass}>CA</span>
            </div>
            
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-400 to-yellow-500 flex items-center justify-center text-white font-bold text-sm ring-2 ring-amber-400/30">
              AC
            </div>
          </div>
        </header>
        
        {/* Dashboard content */}
        <main className="p-4 lg:p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Welcome */}
            <div>
              <h1 className="text-2xl font-bold">Welcome back, Alexandra! 🍁</h1>
              <p className={mutedClass}>Here's what's happening with your writing journey</p>
            </div>
            
            {/* Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Authority Score - Gold */}
              <div className={`${cardClass} border rounded-xl p-4 bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-950/30 dark:to-yellow-950/30 border-amber-200 dark:border-amber-800`}>
                <div className="flex items-start justify-between">
                  <div>
                    <p className={`text-sm ${mutedClass}`}>Authority Score</p>
                    <p className="text-3xl font-bold text-amber-600 dark:text-amber-400 mt-1">{stats.authorityScore}</p>
                    <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1 flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" />
                      +{stats.authorityTrend} this month
                    </p>
                  </div>
                  <div className="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-900/50 flex items-center justify-center">
                    <Crown className="w-5 h-5 text-amber-600" />
                  </div>
                </div>
              </div>
              
              {/* Path Followers */}
              <div className={`${cardClass} border rounded-xl p-4`}>
                <div className="flex items-start justify-between">
                  <div>
                    <p className={`text-sm ${mutedClass}`}>Path Followers</p>
                    <p className="text-3xl font-bold mt-1">{stats.pathFollowers.toLocaleString()}</p>
                    <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1 flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" />
                      +{stats.followersTrend} this week
                    </p>
                  </div>
                  <div className="w-10 h-10 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center">
                    <Users className="w-5 h-5 text-[#FF6B6B]" />
                  </div>
                </div>
              </div>
              
              {/* Total Reads */}
              <div className={`${cardClass} border rounded-xl p-4`}>
                <div className="flex items-start justify-between">
                  <div>
                    <p className={`text-sm ${mutedClass}`}>Total Reads</p>
                    <p className="text-3xl font-bold mt-1">{stats.totalReads.toLocaleString()}</p>
                    <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1 flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" />
                      +{stats.readsTrend}% this month
                    </p>
                  </div>
                  <div className="w-10 h-10 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center">
                    <BookOpen className="w-5 h-5 text-[#FF6B6B]" />
                  </div>
                </div>
              </div>
              
              {/* Reading Streak */}
              <div className={`${cardClass} border rounded-xl p-4`}>
                <div className="flex items-start justify-between">
                  <div>
                    <p className={`text-sm ${mutedClass}`}>Reading Streak</p>
                    <p className="text-3xl font-bold mt-1">{stats.readingStreak} days</p>
                    <p className="text-xs text-[#FF6B6B] mt-1">🔥 Keep it going!</p>
                  </div>
                  <div className="w-10 h-10 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center">
                    <Flame className="w-5 h-5 text-[#FF6B6B]" />
                  </div>
                </div>
              </div>
            </div>
            
            {/* Main grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Voice Profile - 2 columns */}
              <div className={`lg:col-span-2 ${cardClass} border rounded-xl overflow-hidden`}>
                <div className="p-4 border-b border-gray-200 dark:border-gray-800">
                  <h2 className="font-semibold flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-emerald-500" />
                    Your Writing Voice
                  </h2>
                </div>
                <div className="p-6 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20">
                  <div className="flex flex-col md:flex-row gap-6">
                    {/* Radar visualization */}
                    <div className="w-48 h-48 mx-auto md:mx-0 relative">
                      <svg viewBox="0 0 200 200" className="w-full h-full">
                        {/* Background hexagon */}
                        <polygon 
                          points="100,20 170,60 170,140 100,180 30,140 30,60" 
                          fill="none" 
                          stroke={darkMode ? '#374151' : '#E5E7EB'} 
                          strokeWidth="1"
                        />
                        <polygon 
                          points="100,50 145,75 145,125 100,150 55,125 55,75" 
                          fill="none" 
                          stroke={darkMode ? '#374151' : '#E5E7EB'} 
                          strokeWidth="1"
                        />
                        {/* Data polygon */}
                        <polygon 
                          points="100,30 158,68 155,132 100,162 48,122 45,68" 
                          fill="rgba(16, 185, 129, 0.2)" 
                          stroke="#10B981" 
                          strokeWidth="2"
                        />
                        {/* Center */}
                        <circle cx="100" cy="100" r="4" fill="#10B981" />
                      </svg>
                      {/* Labels */}
                      <span className="absolute top-0 left-1/2 -translate-x-1/2 text-xs font-medium">Assertive</span>
                      <span className="absolute top-1/4 right-0 text-xs font-medium">Formal</span>
                      <span className="absolute bottom-1/4 right-0 text-xs font-medium">Detailed</span>
                      <span className="absolute bottom-0 left-1/2 -translate-x-1/2 text-xs font-medium">Poetic</span>
                      <span className="absolute bottom-1/4 left-0 text-xs font-medium">Open</span>
                      <span className="absolute top-1/4 left-0 text-xs font-medium">Dynamic</span>
                    </div>
                    
                    {/* Voice details */}
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mb-2">
                        {voiceProfile.primary} {voiceProfile.secondary}
                      </h3>
                      <p className={`${mutedClass} mb-4`}>
                        You write with confidence and narrative flair. Your voice combines direct statements with rich storytelling.
                      </p>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {voiceProfile.tokens.map((token, i) => (
                          <span 
                            key={i}
                            className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300"
                          >
                            {token.name}
                            <span className="opacity-70">{token.weight}%</span>
                          </span>
                        ))}
                      </div>
                      <div className={`text-sm ${mutedClass}`}>
                        Confidence: <strong className="text-emerald-600">{voiceProfile.confidence}%</strong>
                        <span className="mx-2">•</span>
                        Based on <strong>{stats.analysesCompleted}</strong> analyses
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Right column */}
              <div className="space-y-6">
                {/* Authority Progress */}
                <div className={`${cardClass} border rounded-xl overflow-hidden bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-950/20 dark:to-yellow-950/20 border-amber-200 dark:border-amber-800`}>
                  <div className="p-4 border-b border-amber-200 dark:border-amber-800">
                    <h2 className="font-semibold flex items-center gap-2">
                      👑 Authority Status
                    </h2>
                  </div>
                  <div className="p-4 space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-full bg-amber-100 dark:bg-amber-900/50 flex items-center justify-center">
                        <Crown className="w-6 h-6 text-amber-500" />
                      </div>
                      <div>
                        <p className="font-bold text-amber-600 dark:text-amber-400">Authority Writer</p>
                        <p className={`text-sm ${mutedClass}`}>Highest Tier Achieved</p>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className={mutedClass}>Authority Score</span>
                        <span className="font-semibold text-amber-600 dark:text-amber-400">{stats.authorityScore} / 100</span>
                      </div>
                      <div className="h-2 bg-amber-200 dark:bg-amber-900/50 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-amber-400 to-yellow-500 rounded-full"
                          style={{ width: `${stats.authorityScore}%` }}
                        />
                      </div>
                    </div>
                    
                    <div className="flex gap-6 pt-2">
                      <div>
                        <p className="text-2xl font-bold">#{stats.globalRank}</p>
                        <p className={`text-xs ${mutedClass}`}>Global Rank</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold">{stats.percentile}%</p>
                        <p className={`text-xs ${mutedClass}`}>Percentile</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Activity Feed */}
                <div className={`${cardClass} border rounded-xl overflow-hidden`}>
                  <div className="p-4 border-b border-gray-200 dark:border-gray-800">
                    <h2 className="font-semibold">Recent Activity</h2>
                  </div>
                  <div className="divide-y divide-gray-200 dark:divide-gray-800">
                    {activities.slice(0, 4).map((activity) => (
                      <div key={activity.id} className="p-4 flex gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          activity.type === 'award' ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-600' :
                          activity.type === 'badge' ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600' :
                          activity.type === 'feature' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600' :
                          'bg-[#FF6B6B]/10 text-[#FF6B6B]'
                        }`}>
                          <activity.icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm">{activity.content}</p>
                          <p className={`text-xs ${mutedClass} mt-0.5`}>{activity.time}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Reading Paths */}
            <div className={`${cardClass} border rounded-xl overflow-hidden`}>
              <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
                <h2 className="font-semibold">Your Popular Reading Paths</h2>
                <a href="#" className="text-sm text-[#FF6B6B] hover:underline">View all</a>
              </div>
              <div className="divide-y divide-gray-200 dark:divide-gray-800">
                {paths.map((path) => (
                  <div key={path.id} className="p-4 flex items-center gap-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    <div className="w-10 h-10 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center">
                      <Route className="w-5 h-5 text-[#FF6B6B]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{path.title}</p>
                      <p className={`text-sm ${mutedClass}`}>{path.posts} posts • {path.followers} followers</p>
                    </div>
                    <div className="text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                      <TrendingUp className="w-4 h-4" />
                      +{path.trend}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Footer info */}
            <div className={`text-center text-sm ${mutedClass} py-4`}>
              <p>Quirrely v3.0.0 "Knight of Wands" • Day 90 of your writing journey • 🍁 Canada</p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default AuthorityWriterDashboard;
