import React, { useState } from 'react';
import { 
  Crown, Users, BookOpen, Flame, PenTool, Star, Trophy, TrendingUp,
  Settings, Bell, Moon, Sun, Menu, X, Sparkles, FileText,
  BarChart3, Compass, Bookmark, HelpCircle, ChevronRight,
  Award, Eye, Heart, MessageCircle, Share2, Calendar, Clock,
  ArrowLeft, Filter, Search, MoreHorizontal, ExternalLink
} from 'lucide-react';

/**
 * AUTHORITY WRITER DASHBOARD - Knight of Wands v3.0.0
 * 
 * TRACK: Writer (NOT Curator)
 * TIER: Authority Writer (Highest Writer tier)
 * ADDON: Voice + Style
 * 
 * Writer Track Features:
 * - Voice Profile & Analysis
 * - My Writing / Posts
 * - Writing Analytics
 * - Authority Hub (at Authority level)
 * 
 * NOT Curator Track Features (these should NOT appear):
 * - Reading Paths (Curator only)
 * - Path Followers (Curator only)
 * - Curation tools (Curator only)
 */

const AuthorityWriterDashboard = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, activity, writing, activity-detail
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [selectedPost, setSelectedPost] = useState(null);
  
  // User profile - Authority Writer (Writer Track, NOT Curator)
  const user = {
    name: "Alexandra Chen",
    handle: "alexwrites",
    email: "alex@example.com",
    tier: "authority_writer", // Writer track, NOT curator
    track: "writer", // Explicit track
    country: "CA",
    countryFlag: "🍁",
    daysInSystem: 90,
    addons: ["voice_style"], // Addon enhances voice, doesn't add curator features
  };
  
  // Writer Track Stats (NO path followers - that's Curator)
  const stats = {
    authorityScore: 94.7,
    authorityTrend: +2.3,
    globalRank: 23,
    percentile: 99.2,
    postsWritten: 47,
    postsTrend: +3,
    totalReads: 12847, // Reads OF their writing
    readsTrend: +15,
    readingStreak: 23, // Personal reading streak (universal feature)
    analysesCompleted: 67,
    followers: 2341, // People following THEM as a writer
    followersTrend: +89,
  };
  
  // Voice profile (Writer Track core feature)
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
  };
  
  // Activity feed - Writer Track activities
  const activities = [
    { 
      id: 1, 
      type: "authority", 
      title: "Reached Top 25 Authority Writers",
      content: "Your consistent quality and engagement has elevated you to the top 25 Authority Writers globally. You're now in the 99.2nd percentile.",
      time: "2 hours ago",
      date: "February 15, 2026",
      icon: Trophy,
      actionable: true,
      action: "View Leaderboard",
      actionLink: "/authority/leaderboard"
    },
    { 
      id: 2, 
      type: "followers", 
      title: "89 new followers this week",
      content: "Writers and readers are discovering your work. Your essay 'Northern Lights of the Mind' brought in 34 new followers alone.",
      time: "5 hours ago",
      date: "February 15, 2026",
      icon: Users,
      actionable: true,
      action: "View Followers",
      actionLink: "/writer/followers"
    },
    { 
      id: 3, 
      type: "badge", 
      title: "Earned Consistency Badge",
      content: "23 day reading streak! You've maintained a consistent reading habit, which research shows improves your own writing voice.",
      time: "Yesterday",
      date: "February 14, 2026",
      icon: Award,
      actionable: false
    },
    { 
      id: 4, 
      type: "featured", 
      title: "Featured in Weekly Picks",
      content: "Your essay 'The Weight of Winter Words' was selected for this week's Featured Writing. It's been read 1,247 times.",
      time: "2 days ago",
      date: "February 13, 2026",
      icon: Star,
      actionable: true,
      action: "View Post",
      actionLink: "/writer/posts/weight-of-winter-words"
    },
    { 
      id: 5, 
      type: "voice", 
      title: "Voice confidence reached 87%",
      content: "After 67 analyses, your voice profile has stabilized at 87% confidence. Your Assertive Narrative style is now clearly defined.",
      time: "3 days ago",
      date: "February 12, 2026",
      icon: Sparkles,
      actionable: true,
      action: "View Voice Profile",
      actionLink: "/dashboard/voice"
    },
    { 
      id: 6, 
      type: "engagement", 
      title: "High engagement on recent post",
      content: "'Mapping the Canadian Literary Landscape' received 42 comments and 187 saves. Your readers are deeply engaged.",
      time: "4 days ago",
      date: "February 11, 2026",
      icon: Heart,
      actionable: true,
      action: "View Post",
      actionLink: "/writer/posts/mapping-canadian-landscape"
    },
  ];
  
  // My Writing - Writer Track (NOT Reading Paths)
  const myWriting = [
    { 
      id: 1, 
      title: "The Weight of Winter Words", 
      excerpt: "In the quiet months when snow blankets the northern landscape, something shifts in the way we write...",
      status: "published",
      reads: 1247, 
      comments: 34,
      saves: 89,
      publishedAt: "February 13, 2026",
      featured: true
    },
    { 
      id: 2, 
      title: "Mapping the Canadian Literary Landscape", 
      excerpt: "From Atwood to the new voices emerging from every province, Canadian literature carries a weight...",
      status: "published",
      reads: 2341, 
      comments: 42,
      saves: 187,
      publishedAt: "February 11, 2026",
      featured: false
    },
    { 
      id: 3, 
      title: "Northern Lights of the Mind", 
      excerpt: "The aurora borealis has inspired writers for centuries. But what does it mean to write under those lights...",
      status: "published",
      reads: 1893, 
      comments: 28,
      saves: 156,
      publishedAt: "February 8, 2026",
      featured: true
    },
    { 
      id: 4, 
      title: "Voice as Landscape", 
      excerpt: "Every writer's voice is a terrain to be mapped. Some voices are mountains, others are prairies...",
      status: "draft",
      reads: 0, 
      comments: 0,
      saves: 0,
      publishedAt: null,
      featured: false
    },
  ];

  const bgClass = darkMode ? 'bg-gray-950 text-gray-100' : 'bg-gray-50 text-gray-900';
  const cardClass = darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200';
  const mutedClass = darkMode ? 'text-gray-400' : 'text-gray-500';
  const hoverClass = darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-100';
  
  // Activity Detail View
  const ActivityDetailView = ({ activity, onBack }) => (
    <div className="space-y-6">
      <button 
        onClick={onBack}
        className={`flex items-center gap-2 ${mutedClass} hover:text-[#FF6B6B] transition-colors`}
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </button>
      
      <div className={`${cardClass} border rounded-xl overflow-hidden`}>
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${
              activity.type === 'authority' ? 'bg-amber-100 text-amber-600' :
              activity.type === 'badge' ? 'bg-purple-100 text-purple-600' :
              activity.type === 'featured' ? 'bg-blue-100 text-blue-600' :
              activity.type === 'voice' ? 'bg-emerald-100 text-emerald-600' :
              'bg-[#FF6B6B]/10 text-[#FF6B6B]'
            }`}>
              <activity.icon className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold mb-2">{activity.title}</h1>
              <p className={`${mutedClass} text-sm mb-4`}>{activity.date}</p>
              <p className="text-lg leading-relaxed mb-6">{activity.content}</p>
              {activity.actionable && (
                <button className="inline-flex items-center gap-2 px-4 py-2 bg-[#FF6B6B] text-white rounded-lg hover:bg-[#ff5252] transition-colors">
                  {activity.action}
                  <ChevronRight className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  // All Activity View
  const AllActivityView = ({ onBack, onSelectActivity }) => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button 
          onClick={onBack}
          className={`flex items-center gap-2 ${mutedClass} hover:text-[#FF6B6B] transition-colors`}
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </button>
        <div className="flex items-center gap-2">
          <button className={`p-2 rounded-lg ${hoverClass}`}>
            <Filter className="w-5 h-5" />
          </button>
          <button className={`p-2 rounded-lg ${hoverClass}`}>
            <Search className="w-5 h-5" />
          </button>
        </div>
      </div>
      
      <div>
        <h1 className="text-2xl font-bold">All Activity</h1>
        <p className={mutedClass}>Your complete activity history</p>
      </div>
      
      <div className={`${cardClass} border rounded-xl overflow-hidden`}>
        <div className="divide-y divide-gray-200 dark:divide-gray-800">
          {activities.map((activity) => (
            <button
              key={activity.id}
              onClick={() => onSelectActivity(activity)}
              className={`w-full p-4 flex items-start gap-4 text-left ${hoverClass} transition-colors`}
            >
              <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                activity.type === 'authority' ? 'bg-amber-100 text-amber-600' :
                activity.type === 'badge' ? 'bg-purple-100 text-purple-600' :
                activity.type === 'featured' ? 'bg-blue-100 text-blue-600' :
                activity.type === 'voice' ? 'bg-emerald-100 text-emerald-600' :
                'bg-[#FF6B6B]/10 text-[#FF6B6B]'
              }`}>
                <activity.icon className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium">{activity.title}</p>
                <p className={`text-sm ${mutedClass} truncate`}>{activity.content}</p>
                <p className={`text-xs ${mutedClass} mt-1`}>{activity.time}</p>
              </div>
              <ChevronRight className={`w-5 h-5 ${mutedClass} flex-shrink-0`} />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
  
  // All Writing View
  const AllWritingView = ({ onBack, onSelectPost }) => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button 
          onClick={onBack}
          className={`flex items-center gap-2 ${mutedClass} hover:text-[#FF6B6B] transition-colors`}
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </button>
        <button className="px-4 py-2 bg-[#FF6B6B] text-white rounded-lg hover:bg-[#ff5252] transition-colors flex items-center gap-2">
          <PenTool className="w-4 h-4" />
          New Post
        </button>
      </div>
      
      <div>
        <h1 className="text-2xl font-bold">My Writing</h1>
        <p className={mutedClass}>{myWriting.length} posts • {myWriting.filter(p => p.status === 'draft').length} drafts</p>
      </div>
      
      <div className={`${cardClass} border rounded-xl overflow-hidden`}>
        <div className="divide-y divide-gray-200 dark:divide-gray-800">
          {myWriting.map((post) => (
            <button
              key={post.id}
              onClick={() => onSelectPost(post)}
              className={`w-full p-4 flex items-start gap-4 text-left ${hoverClass} transition-colors`}
            >
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                post.status === 'draft' ? 'bg-gray-100 text-gray-500' : 'bg-[#FF6B6B]/10 text-[#FF6B6B]'
              }`}>
                {post.featured ? <Star className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <p className="font-medium">{post.title}</p>
                  {post.featured && (
                    <span className="px-2 py-0.5 text-xs bg-amber-100 text-amber-800 rounded-full">Featured</span>
                  )}
                  {post.status === 'draft' && (
                    <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full">Draft</span>
                  )}
                </div>
                <p className={`text-sm ${mutedClass} truncate`}>{post.excerpt}</p>
                {post.status === 'published' && (
                  <div className={`flex items-center gap-4 text-xs ${mutedClass} mt-2`}>
                    <span className="flex items-center gap-1"><Eye className="w-3 h-3" />{post.reads.toLocaleString()}</span>
                    <span className="flex items-center gap-1"><MessageCircle className="w-3 h-3" />{post.comments}</span>
                    <span className="flex items-center gap-1"><Bookmark className="w-3 h-3" />{post.saves}</span>
                  </div>
                )}
              </div>
              <ChevronRight className={`w-5 h-5 ${mutedClass} flex-shrink-0`} />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
  
  // Post Detail View
  const PostDetailView = ({ post, onBack }) => (
    <div className="space-y-6">
      <button 
        onClick={onBack}
        className={`flex items-center gap-2 ${mutedClass} hover:text-[#FF6B6B] transition-colors`}
      >
        <ArrowLeft className="w-4 h-4" />
        Back to My Writing
      </button>
      
      <div className={`${cardClass} border rounded-xl overflow-hidden`}>
        <div className="p-6">
          <div className="flex items-center gap-2 mb-4">
            {post.featured && (
              <span className="px-2 py-1 text-xs bg-amber-100 text-amber-800 rounded-full flex items-center gap-1">
                <Star className="w-3 h-3" /> Featured
              </span>
            )}
            {post.status === 'draft' && (
              <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">Draft</span>
            )}
          </div>
          <h1 className="text-2xl font-bold mb-2">{post.title}</h1>
          {post.publishedAt && (
            <p className={`${mutedClass} text-sm mb-4 flex items-center gap-2`}>
              <Calendar className="w-4 h-4" />
              Published {post.publishedAt}
            </p>
          )}
          <p className="text-lg leading-relaxed mb-6">{post.excerpt}</p>
          
          {post.status === 'published' && (
            <div className="flex items-center gap-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="text-center">
                <p className="text-2xl font-bold">{post.reads.toLocaleString()}</p>
                <p className={`text-xs ${mutedClass}`}>Reads</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{post.comments}</p>
                <p className={`text-xs ${mutedClass}`}>Comments</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{post.saves}</p>
                <p className={`text-xs ${mutedClass}`}>Saves</p>
              </div>
            </div>
          )}
          
          <div className="flex gap-3 mt-6">
            <button className="px-4 py-2 bg-[#FF6B6B] text-white rounded-lg hover:bg-[#ff5252] transition-colors">
              {post.status === 'draft' ? 'Continue Editing' : 'Edit Post'}
            </button>
            {post.status === 'published' && (
              <button className={`px-4 py-2 border rounded-lg ${hoverClass} transition-colors flex items-center gap-2`}>
                <Share2 className="w-4 h-4" />
                Share
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
  
  // Render current view
  const renderView = () => {
    if (currentView === 'activity-detail' && selectedActivity) {
      return <ActivityDetailView activity={selectedActivity} onBack={() => { setCurrentView('dashboard'); setSelectedActivity(null); }} />;
    }
    if (currentView === 'activity') {
      return <AllActivityView 
        onBack={() => setCurrentView('dashboard')} 
        onSelectActivity={(a) => { setSelectedActivity(a); setCurrentView('activity-detail'); }}
      />;
    }
    if (currentView === 'post-detail' && selectedPost) {
      return <PostDetailView post={selectedPost} onBack={() => { setCurrentView('writing'); setSelectedPost(null); }} />;
    }
    if (currentView === 'writing') {
      return <AllWritingView 
        onBack={() => setCurrentView('dashboard')} 
        onSelectPost={(p) => { setSelectedPost(p); setCurrentView('post-detail'); }}
      />;
    }
    
    // Dashboard View
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Welcome back, Alexandra! 🍁</h1>
          <p className={mutedClass}>Here's what's happening with your writing</p>
        </div>
        
        {/* Metrics - WRITER TRACK (no path followers) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Authority Score */}
          <div className={`${cardClass} border rounded-xl p-4 bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-950/30 dark:to-yellow-950/30 border-amber-200 dark:border-amber-800`}>
            <div className="flex items-start justify-between">
              <div>
                <p className={`text-sm ${mutedClass}`}>Authority Score</p>
                <p className="text-3xl font-bold text-amber-600 mt-1">{stats.authorityScore}</p>
                <p className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" />+{stats.authorityTrend} this month</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center"><Crown className="w-5 h-5 text-amber-600" /></div>
            </div>
          </div>
          
          {/* Writer Followers (people following THIS writer) */}
          <div className={`${cardClass} border rounded-xl p-4`}>
            <div className="flex items-start justify-between">
              <div>
                <p className={`text-sm ${mutedClass}`}>Followers</p>
                <p className="text-3xl font-bold mt-1">{stats.followers.toLocaleString()}</p>
                <p className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" />+{stats.followersTrend} this week</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center"><Users className="w-5 h-5 text-[#FF6B6B]" /></div>
            </div>
          </div>
          
          {/* Total Reads (of their writing) */}
          <div className={`${cardClass} border rounded-xl p-4`}>
            <div className="flex items-start justify-between">
              <div>
                <p className={`text-sm ${mutedClass}`}>Total Reads</p>
                <p className="text-3xl font-bold mt-1">{stats.totalReads.toLocaleString()}</p>
                <p className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" />+{stats.readsTrend}% this month</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center"><Eye className="w-5 h-5 text-[#FF6B6B]" /></div>
            </div>
          </div>
          
          {/* Posts Written (Writer track metric) */}
          <div className={`${cardClass} border rounded-xl p-4`}>
            <div className="flex items-start justify-between">
              <div>
                <p className={`text-sm ${mutedClass}`}>Posts Written</p>
                <p className="text-3xl font-bold mt-1">{stats.postsWritten}</p>
                <p className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" />+{stats.postsTrend} this month</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center"><PenTool className="w-5 h-5 text-[#FF6B6B]" /></div>
            </div>
          </div>
        </div>
        
        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Voice Profile */}
          <div className={`lg:col-span-2 ${cardClass} border rounded-xl overflow-hidden`}>
            <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
              <h2 className="font-semibold flex items-center gap-2"><Sparkles className="w-5 h-5 text-emerald-500" />Your Writing Voice</h2>
              <button className="text-sm text-[#FF6B6B] hover:underline">View Details</button>
            </div>
            <div className="p-6 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20">
              <div className="flex flex-col md:flex-row gap-6">
                <div className="w-40 h-40 mx-auto md:mx-0 rounded-full border-4 border-emerald-500/30 flex items-center justify-center bg-emerald-100/50 dark:bg-emerald-900/30">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-emerald-600">{voiceProfile.confidence}%</p>
                    <p className="text-xs text-emerald-600">Confidence</p>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-emerald-600 mb-2">{voiceProfile.primary} {voiceProfile.secondary}</h3>
                  <p className={`${mutedClass} mb-4`}>You write with confidence and narrative flair. Your voice combines direct statements with rich storytelling.</p>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {voiceProfile.tokens.map((token, i) => (
                      <span key={i} className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300">
                        {token.name} <span className="opacity-70">{token.weight}%</span>
                      </span>
                    ))}
                  </div>
                  <p className={`text-sm ${mutedClass}`}>Based on <strong>{stats.analysesCompleted}</strong> analyses</p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Right column */}
          <div className="space-y-6">
            {/* Authority Progress */}
            <div className={`${cardClass} border rounded-xl overflow-hidden bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-950/20 dark:to-yellow-950/20 border-amber-200 dark:border-amber-800`}>
              <div className="p-4 border-b border-amber-200 dark:border-amber-800">
                <h2 className="font-semibold">👑 Authority Status</h2>
              </div>
              <div className="p-4 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center"><Crown className="w-6 h-6 text-amber-500" /></div>
                  <div>
                    <p className="font-bold text-amber-600">Authority Writer</p>
                    <p className={`text-sm ${mutedClass}`}>Writer Track • Highest Tier</p>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className={mutedClass}>Authority Score</span>
                    <span className="font-semibold text-amber-600">{stats.authorityScore} / 100</span>
                  </div>
                  <div className="h-2 bg-amber-200 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-amber-400 to-yellow-500 rounded-full" style={{ width: `${stats.authorityScore}%` }} />
                  </div>
                </div>
                <div className="flex gap-6 pt-2">
                  <div><p className="text-2xl font-bold">#{stats.globalRank}</p><p className={`text-xs ${mutedClass}`}>Global Rank</p></div>
                  <div><p className="text-2xl font-bold">{stats.percentile}%</p><p className={`text-xs ${mutedClass}`}>Percentile</p></div>
                </div>
              </div>
            </div>
            
            {/* Activity Feed - CLICKABLE */}
            <div className={`${cardClass} border rounded-xl overflow-hidden`}>
              <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
                <h2 className="font-semibold">Recent Activity</h2>
                <button 
                  onClick={() => setCurrentView('activity')}
                  className="text-sm text-[#FF6B6B] hover:underline"
                >
                  View all
                </button>
              </div>
              <div className="divide-y divide-gray-200 dark:divide-gray-800">
                {activities.slice(0, 4).map((a) => (
                  <button
                    key={a.id}
                    onClick={() => { setSelectedActivity(a); setCurrentView('activity-detail'); }}
                    className={`w-full p-3 flex gap-3 text-left ${hoverClass} transition-colors`}
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      a.type === 'authority' ? 'bg-amber-100 text-amber-600' :
                      a.type === 'badge' ? 'bg-purple-100 text-purple-600' :
                      a.type === 'featured' ? 'bg-blue-100 text-blue-600' :
                      a.type === 'voice' ? 'bg-emerald-100 text-emerald-600' :
                      'bg-[#FF6B6B]/10 text-[#FF6B6B]'
                    }`}><a.icon className="w-4 h-4" /></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{a.title}</p>
                      <p className={`text-xs ${mutedClass}`}>{a.time}</p>
                    </div>
                    <ChevronRight className={`w-4 h-4 ${mutedClass} flex-shrink-0`} />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
        
        {/* My Writing - WRITER TRACK (replaces Reading Paths) */}
        <div className={`${cardClass} border rounded-xl overflow-hidden`}>
          <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
            <h2 className="font-semibold">My Writing</h2>
            <button 
              onClick={() => setCurrentView('writing')}
              className="text-sm text-[#FF6B6B] hover:underline"
            >
              View all
            </button>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-800">
            {myWriting.slice(0, 3).map((post) => (
              <button
                key={post.id}
                onClick={() => { setSelectedPost(post); setCurrentView('post-detail'); }}
                className={`w-full p-4 flex items-center gap-4 text-left ${hoverClass} transition-colors`}
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                  post.status === 'draft' ? 'bg-gray-100 text-gray-500' : 'bg-[#FF6B6B]/10 text-[#FF6B6B]'
                }`}>
                  {post.featured ? <Star className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium truncate">{post.title}</p>
                    {post.featured && <span className="px-1.5 py-0.5 text-xs bg-amber-100 text-amber-800 rounded">Featured</span>}
                  </div>
                  {post.status === 'published' ? (
                    <p className={`text-sm ${mutedClass}`}>{post.reads.toLocaleString()} reads • {post.comments} comments</p>
                  ) : (
                    <p className={`text-sm ${mutedClass}`}>Draft</p>
                  )}
                </div>
                <ChevronRight className={`w-5 h-5 ${mutedClass} flex-shrink-0`} />
              </button>
            ))}
          </div>
        </div>
        
        <p className={`text-center text-sm ${mutedClass} py-4`}>
          Quirrely v3.0.0 "Knight of Wands" • Writer Track • Day 90 • 🍁 Canada
        </p>
      </div>
    );
  };
  
  return (
    <div className={`min-h-screen ${bgClass} transition-colors duration-200`}>
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}
      
      {/* Sidebar - WRITER TRACK NAVIGATION (no Curator section) */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 ${cardClass} border-r transform transition-transform duration-300 lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="p-4 border-b border-gray-200 dark:border-gray-800 lg:hidden flex justify-between">
          <span className="font-semibold">Menu</span>
          <button onClick={() => setSidebarOpen(false)}><X className="w-5 h-5" /></button>
        </div>
        
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-amber-400 to-yellow-500 flex items-center justify-center text-white font-bold text-lg ring-2 ring-amber-400/50">AC</div>
            <div>
              <p className="font-semibold">{user.name}</p>
              <p className={`text-sm ${mutedClass}`}>@{user.handle}</p>
            </div>
          </div>
        </div>
        
        <nav className="p-4 space-y-6 overflow-y-auto h-[calc(100vh-200px)]">
          {/* General */}
          <div>
            <h3 className={`px-3 mb-2 text-xs font-semibold ${mutedClass} uppercase`}>General</h3>
            <button onClick={() => setCurrentView('dashboard')} className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg ${currentView === 'dashboard' ? 'bg-[#FF6B6B] text-white' : `${mutedClass} ${hoverClass}`} font-medium mb-1`}>
              <BarChart3 className="w-5 h-5" />Dashboard
            </button>
            <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} ${hoverClass}`}>
              <Compass className="w-5 h-5" />Discover
            </a>
            <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} ${hoverClass}`}>
              <Flame className="w-5 h-5" />Reading Streak <span className="ml-auto text-xs bg-[#FF6B6B] text-white px-2 py-0.5 rounded-full">{stats.readingStreak}</span>
            </a>
          </div>
          
          {/* Writer Section - PRIMARY for Writer Track */}
          <div>
            <h3 className={`px-3 mb-2 text-xs font-semibold ${mutedClass} uppercase`}>Writer</h3>
            <button onClick={() => setCurrentView('writing')} className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg ${currentView === 'writing' || currentView === 'post-detail' ? 'bg-[#FF6B6B] text-white' : `${mutedClass} ${hoverClass}`}`}>
              <PenTool className="w-5 h-5" />My Writing
            </button>
            <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} ${hoverClass}`}>
              <FileText className="w-5 h-5" />Drafts
            </a>
            <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} ${hoverClass}`}>
              <Sparkles className="w-5 h-5" />Voice Profile <span className="ml-auto text-xs bg-emerald-500 text-white px-2 py-0.5 rounded-full">✨</span>
            </a>
            <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} ${hoverClass}`}>
              <BarChart3 className="w-5 h-5" />Analytics
            </a>
          </div>
          
          {/* Authority Section - Available at Authority tier */}
          <div>
            <h3 className={`px-3 mb-2 text-xs font-semibold ${mutedClass} uppercase`}>Authority</h3>
            <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} ${hoverClass}`}>
              <Crown className="w-5 h-5 text-amber-500" />Authority Hub
            </a>
            <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} ${hoverClass}`}>
              <Trophy className="w-5 h-5" />Leaderboard
            </a>
            <a href="#" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg ${mutedClass} ${hoverClass}`}>
              <TrendingUp className="w-5 h-5" />Impact Stats
            </a>
          </div>
          
          {/* NO CURATOR SECTION - Writer Track doesn't have Curator features */}
        </nav>
        
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-800">
          <a href="#" className={`flex items-center gap-3 px-3 py-2 rounded-lg ${mutedClass} ${hoverClass}`}>
            <Settings className="w-5 h-5" />Settings
          </a>
          <a href="#" className={`flex items-center gap-3 px-3 py-2 rounded-lg ${mutedClass} ${hoverClass}`}>
            <HelpCircle className="w-5 h-5" />Help
          </a>
        </div>
      </aside>
      
      {/* Main */}
      <div className="lg:pl-64">
        {/* Header */}
        <header className={`sticky top-0 z-30 h-16 flex items-center justify-between px-4 lg:px-6 ${cardClass} border-b`}>
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(true)} className={`p-2 rounded-lg ${hoverClass} lg:hidden`}>
              <Menu className="w-5 h-5" />
            </button>
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
            <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">👑 Authority Writer</span>
            <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">✨ Voice + Style</span>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setDarkMode(!darkMode)} className={`p-2 rounded-lg ${hoverClass}`}>
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <button className={`p-2 rounded-lg ${hoverClass} relative`}>
              <Bell className="w-5 h-5" /><span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#FF6B6B] rounded-full" />
            </button>
            <span className={`hidden sm:flex items-center gap-1 px-2 py-1 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-100'} text-sm`}>🍁 CA</span>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-400 to-yellow-500 flex items-center justify-center text-white font-bold ring-2 ring-amber-400/30">AC</div>
          </div>
        </header>
        
        <main className="p-4 lg:p-6">
          <div className="max-w-7xl mx-auto">
            {renderView()}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AuthorityWriterDashboard;
