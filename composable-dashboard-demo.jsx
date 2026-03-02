import React, { useState } from 'react';
import { 
  Crown, Users, BookOpen, Flame, PenTool, Star, Trophy, TrendingUp,
  Settings, Bell, Moon, Sun, Menu, X, Sparkles, FileText, Route,
  BarChart3, Compass, Bookmark, HelpCircle, ChevronRight, Eye,
  Award, Heart, MessageCircle, Calendar, ArrowLeft, Plus, Zap,
  ChevronDown, Check
} from 'lucide-react';

/**
 * QUIRRELY COMPOSABLE DASHBOARD DEMO
 * Knight of Wands v3.0.0
 * 
 * Interactive demo showing dashboard for ALL user permutations.
 * Click on user profile to switch between different configurations.
 */

// User configurations
const USERS = {
  free: { id: 'free', name: 'New Reader', handle: 'newreader', country: 'CA', writerTier: 'free', curatorTier: 'free', primaryTrack: 'writer', addons: [], daysInSystem: 3 },
  free_with_addon: { id: 'free_addon', name: 'Voice Explorer', handle: 'voiceexplorer', country: 'GB', writerTier: 'free', curatorTier: 'free', primaryTrack: 'writer', addons: ['voice_style'], daysInSystem: 14 },
  pro_writer: { id: 'pro_writer', name: 'Pro Writer', handle: 'prowriter', country: 'AU', writerTier: 'pro', curatorTier: 'free', primaryTrack: 'writer', addons: [], daysInSystem: 45 },
  curator: { id: 'curator', name: 'Path Curator', handle: 'pathcurator', country: 'NZ', writerTier: 'free', curatorTier: 'curator', primaryTrack: 'curator', addons: [], daysInSystem: 60 },
  dual_pro_curator: { id: 'dual', name: 'Dual Creator', handle: 'dualcreator', country: 'CA', writerTier: 'pro', curatorTier: 'curator', primaryTrack: 'writer', addons: ['voice_style'], daysInSystem: 75 },
  authority_writer: { id: 'auth_writer', name: 'Alexandra Chen', handle: 'alexwrites', country: 'CA', writerTier: 'authority_writer', curatorTier: 'free', primaryTrack: 'writer', addons: ['voice_style'], daysInSystem: 90 },
  authority_curator: { id: 'auth_curator', name: 'Marcus Webb', handle: 'marcuscurates', country: 'GB', writerTier: 'free', curatorTier: 'authority_curator', primaryTrack: 'curator', addons: [], daysInSystem: 120 },
  authority_dual: { id: 'auth_dual', name: 'Elena Vasquez', handle: 'elenavwrites', country: 'CA', writerTier: 'authority_writer', curatorTier: 'authority_curator', primaryTrack: 'writer', addons: ['voice_style'], daysInSystem: 180 },
  featured_dual: { id: 'featured_dual', name: 'Jordan Park', handle: 'jordanpark', country: 'AU', writerTier: 'featured_writer', curatorTier: 'curator', primaryTrack: 'writer', addons: ['voice_style'], daysInSystem: 100 },
};

const TIER_LEVELS = { free: 0, pro: 1, curator: 1, featured_writer: 2, featured_curator: 2, authority_writer: 3, authority_curator: 3 };
const FLAGS = { CA: '🍁', GB: '🇬🇧', AU: '🇦🇺', NZ: '🇳🇿' };

// Helpers
const hasWriterTrack = (u) => TIER_LEVELS[u.writerTier] >= 1;
const hasCuratorTrack = (u) => TIER_LEVELS[u.curatorTier] >= 1;
const isDualTrack = (u) => hasWriterTrack(u) && hasCuratorTrack(u);
const isAuthorityTier = (u) => TIER_LEVELS[u.writerTier] >= 3 || TIER_LEVELS[u.curatorTier] >= 3;
const isFeaturedTier = (u) => TIER_LEVELS[u.writerTier] >= 2 || TIER_LEVELS[u.curatorTier] >= 2;
const hasVoiceStyle = (u) => u.addons?.includes('voice_style');
const canAddTrack = (u) => TIER_LEVELS[u.writerTier] >= 1 || TIER_LEVELS[u.curatorTier] >= 1;

const getFeatures = (u) => ({
  myWriting: hasWriterTrack(u) || hasVoiceStyle(u),
  voiceProfile: hasWriterTrack(u) || hasVoiceStyle(u),
  voiceEvolution: hasVoiceStyle(u),
  writerAnalytics: hasWriterTrack(u),
  readingPaths: hasCuratorTrack(u),
  pathFollowers: hasCuratorTrack(u),
  curatorAnalytics: hasCuratorTrack(u),
  authorityHub: isFeaturedTier(u),
  leaderboard: isFeaturedTier(u),
  impactStats: isAuthorityTier(u),
});

// Settings View Component with tabs
const SettingsView = ({ user, darkMode, card, border, muted, hover, setCurrentView, hasVoiceStyle, isAuthorityTier, formatTier }) => {
  const [activeTab, setActiveTab] = useState('profile');
  
  const tabs = ['Profile', 'Preferences', 'Notifications', 'Billing'];
  
  return (
    <>
      <button onClick={() => setCurrentView('dashboard')} className={`flex items-center gap-2 ${muted} hover:text-[#FF6B6B] transition-colors`}>
        <ArrowLeft className="w-4 h-4" />Back to Dashboard
      </button>
      
      <h1 className="text-2xl font-bold">Settings</h1>
      
      {/* Settings Tabs */}
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-800">
        {tabs.map((tab) => (
          <button 
            key={tab} 
            onClick={() => setActiveTab(tab.toLowerCase())}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === tab.toLowerCase() ? 'border-[#FF6B6B] text-[#FF6B6B]' : `border-transparent ${muted} hover:text-[#FF6B6B]`}`}
          >
            {tab}
          </button>
        ))}
      </div>
      
      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <>
          <div className={`${card} border rounded-xl overflow-hidden`}>
            <div className={`p-4 border-b ${border}`}>
              <h2 className="font-semibold">Profile Information</h2>
            </div>
            <div className="p-6 space-y-6">
              <div className="flex items-center gap-6">
                <div className={`w-20 h-20 rounded-full flex items-center justify-center text-white font-bold text-2xl ${isAuthorityTier(user) ? 'bg-gradient-to-br from-amber-400 to-yellow-500' : 'bg-gradient-to-br from-red-400 to-red-500'}`}>
                  {user.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <button className="px-4 py-2 bg-[#FF6B6B] text-white rounded-lg text-sm hover:bg-[#ff5252]">Upload Photo</button>
                  <p className={`text-xs ${muted} mt-1`}>JPG, PNG. Max 2MB.</p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className={`block text-sm font-medium mb-1 ${muted}`}>Display Name</label>
                  <input type="text" defaultValue={user.name} className={`w-full px-3 py-2 rounded-lg border ${border} ${darkMode ? 'bg-gray-800' : 'bg-white'}`} />
                </div>
                <div>
                  <label className={`block text-sm font-medium mb-1 ${muted}`}>Username</label>
                  <input type="text" defaultValue={`@${user.handle}`} className={`w-full px-3 py-2 rounded-lg border ${border} ${darkMode ? 'bg-gray-800' : 'bg-white'}`} />
                </div>
                <div className="md:col-span-2">
                  <label className={`block text-sm font-medium mb-1 ${muted}`}>Bio</label>
                  <textarea rows={3} placeholder="Tell readers about yourself..." className={`w-full px-3 py-2 rounded-lg border ${border} ${darkMode ? 'bg-gray-800' : 'bg-white'}`} />
                </div>
                <div>
                  <label className={`block text-sm font-medium mb-1 ${muted}`}>Country</label>
                  <select defaultValue={user.country} className={`w-full px-3 py-2 rounded-lg border ${border} ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
                    <option value="CA">🍁 Canada</option>
                    <option value="GB">🇬🇧 United Kingdom</option>
                    <option value="AU">🇦🇺 Australia</option>
                    <option value="NZ">🇳🇿 New Zealand</option>
                  </select>
                </div>
                <div>
                  <label className={`block text-sm font-medium mb-1 ${muted}`}>Website</label>
                  <input type="url" placeholder="https://yoursite.com" className={`w-full px-3 py-2 rounded-lg border ${border} ${darkMode ? 'bg-gray-800' : 'bg-white'}`} />
                </div>
              </div>
              
              <div className="flex justify-end">
                <button className="px-6 py-2 bg-[#FF6B6B] text-white rounded-lg hover:bg-[#ff5252]">Save Changes</button>
              </div>
            </div>
          </div>
          
          {/* Danger Zone */}
          <div className={`${card} border border-red-200 rounded-xl overflow-hidden`}>
            <div className="p-4 border-b border-red-200 bg-red-50 dark:bg-red-950/20">
              <h2 className="font-semibold text-red-600">Danger Zone</h2>
            </div>
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Delete Account</p>
                  <p className={`text-sm ${muted}`}>Permanently delete your account and all data</p>
                </div>
                <button className="px-4 py-2 rounded-lg border border-red-300 text-red-600 hover:bg-red-50">Delete Account</button>
              </div>
            </div>
          </div>
        </>
      )}
      
      {/* Preferences Tab */}
      {activeTab === 'preferences' && (
        <>
          <div className={`${card} border rounded-xl overflow-hidden`}>
            <div className={`p-4 border-b ${border}`}>
              <h2 className="font-semibold">Display Preferences</h2>
            </div>
            <div className="p-6 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Dark Mode</p>
                  <p className={`text-sm ${muted}`}>Use dark theme across Quirrely</p>
                </div>
                <button className={`w-12 h-6 rounded-full transition-colors ${darkMode ? 'bg-[#FF6B6B]' : 'bg-gray-300'} relative`}>
                  <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${darkMode ? 'right-1' : 'left-1'}`} />
                </button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Compact View</p>
                  <p className={`text-sm ${muted}`}>Show more content with less spacing</p>
                </div>
                <button className="w-12 h-6 rounded-full bg-gray-300 relative">
                  <span className="absolute top-1 left-1 w-4 h-4 bg-white rounded-full" />
                </button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Show Reading Time</p>
                  <p className={`text-sm ${muted}`}>Display estimated reading time on posts</p>
                </div>
                <button className="w-12 h-6 rounded-full bg-[#FF6B6B] relative">
                  <span className="absolute top-1 right-1 w-4 h-4 bg-white rounded-full" />
                </button>
              </div>
            </div>
          </div>
          
          <div className={`${card} border rounded-xl overflow-hidden`}>
            <div className={`p-4 border-b ${border}`}>
              <h2 className="font-semibold">Content Preferences</h2>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <label className={`block text-sm font-medium mb-2 ${muted}`}>Default Feed</label>
                <select className={`w-full px-3 py-2 rounded-lg border ${border} ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
                  <option>Following</option>
                  <option>Discover</option>
                  <option>Trending</option>
                </select>
              </div>
              <div>
                <label className={`block text-sm font-medium mb-2 ${muted}`}>Content Language</label>
                <select className={`w-full px-3 py-2 rounded-lg border ${border} ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
                  <option>English</option>
                  <option>French</option>
                  <option>Spanish</option>
                </select>
              </div>
            </div>
          </div>
        </>
      )}
      
      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <>
          <div className={`${card} border rounded-xl overflow-hidden`}>
            <div className={`p-4 border-b ${border}`}>
              <h2 className="font-semibold">Email Notifications</h2>
            </div>
            <div className="p-6 space-y-4">
              {[
                { title: 'New Followers', desc: 'When someone follows you', enabled: true },
                { title: 'Comments', desc: 'When someone comments on your posts', enabled: true },
                { title: 'Mentions', desc: 'When someone mentions you', enabled: true },
                { title: 'Weekly Digest', desc: 'Summary of your weekly activity', enabled: false },
                { title: 'Product Updates', desc: 'New features and announcements', enabled: true },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{item.title}</p>
                    <p className={`text-sm ${muted}`}>{item.desc}</p>
                  </div>
                  <button className={`w-12 h-6 rounded-full transition-colors ${item.enabled ? 'bg-[#FF6B6B]' : 'bg-gray-300'} relative`}>
                    <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${item.enabled ? 'right-1' : 'left-1'}`} />
                  </button>
                </div>
              ))}
            </div>
          </div>
          
          <div className={`${card} border rounded-xl overflow-hidden`}>
            <div className={`p-4 border-b ${border}`}>
              <h2 className="font-semibold">Push Notifications</h2>
            </div>
            <div className="p-6 space-y-4">
              {[
                { title: 'Mobile Push', desc: 'Receive notifications on your phone', enabled: true },
                { title: 'Desktop Push', desc: 'Receive notifications in browser', enabled: false },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{item.title}</p>
                    <p className={`text-sm ${muted}`}>{item.desc}</p>
                  </div>
                  <button className={`w-12 h-6 rounded-full transition-colors ${item.enabled ? 'bg-[#FF6B6B]' : 'bg-gray-300'} relative`}>
                    <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${item.enabled ? 'right-1' : 'left-1'}`} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
      
      {/* Billing Tab */}
      {activeTab === 'billing' && (() => {
        // FINAL PRICING - CAD BASE
        // Monthly: Pro/Curator $4.99, Featured $7.99, Authority $8.99, V+S $9.99
        // 🟡 P2: Annual now 25% discount (was ~17%)
        // Annual: Pro/Curator $44.99, Featured $71.99, Authority $80.99, V+S $89.99
        // NOTE: USA is excluded from the system
        const PRICING = {
          CAD: { 
            pro: { monthly: 4.99, annual: 44.99 },      // 25% off ($59.88 → $44.99)
            featured: { monthly: 7.99, annual: 71.99 }, // 25% off ($95.88 → $71.99)
            authority: { monthly: 8.99, annual: 80.99 }, // 25% off ($107.88 → $80.99)
            addon: { monthly: 9.99, annual: 89.99 }     // 25% off ($119.88 → $89.99)
          },
          GBP: { 
            pro: { monthly: 2.49, annual: 22.49 },
            featured: { monthly: 3.99, annual: 35.99 },
            authority: { monthly: 4.49, annual: 40.49 },
            addon: { monthly: 4.99, annual: 44.99 }
          },
          AUD: { 
            pro: { monthly: 4.99, annual: 44.99 },
            featured: { monthly: 7.99, annual: 71.99 },
            authority: { monthly: 8.99, annual: 80.99 },
            addon: { monthly: 9.99, annual: 89.99 }
          },
          NZD: { 
            pro: { monthly: 5.49, annual: 49.49 },
            featured: { monthly: 8.99, annual: 80.99 },
            authority: { monthly: 9.99, annual: 89.99 },
            addon: { monthly: 10.99, annual: 98.99 }
          },
        };
        
        const currencyMap = { CA: 'CAD', GB: 'GBP', AU: 'AUD', NZ: 'NZD' };
        const symbolMap = { CAD: '$', GBP: '£', AUD: 'A$', NZD: 'NZ$' };
        const currency = currencyMap[user.country] || 'CAD';
        const symbol = symbolMap[currency];
        const prices = PRICING[currency];
        
        const getTierKey = (writerTier, curatorTier) => {
          if (writerTier.includes('authority') || curatorTier.includes('authority')) return 'authority';
          if (writerTier.includes('featured') || curatorTier.includes('featured')) return 'featured';
          if (writerTier === 'pro' || curatorTier === 'curator') return 'pro';
          return null;
        };
        
        // Round combined prices to .99 or .49 only
        const roundToNineNine = (price) => {
          const whole = Math.floor(price);
          const decimal = price - whole;
          if (decimal <= 0.49) return whole + 0.49;
          return whole + 0.99;
        };
        
        const tierKey = getTierKey(user.writerTier, user.curatorTier);
        const baseTierPrice = tierKey ? prices[tierKey].monthly : 0;
        const baseTierAnnual = tierKey ? prices[tierKey].annual : 0;
        const addonPrice = hasVoiceStyle(user) ? prices.addon.monthly : 0;
        const addonAnnual = hasVoiceStyle(user) ? prices.addon.annual : 0;
        const rawTotal = baseTierPrice + addonPrice;
        const totalPrice = (baseTierPrice > 0 && addonPrice > 0) ? roundToNineNine(rawTotal) : rawTotal;
        const totalAnnual = baseTierAnnual + addonAnnual;
        const annualSavings = (totalPrice * 12) - totalAnnual;
        const isFreeUser = user.writerTier === 'free' && user.curatorTier === 'free' && !hasVoiceStyle(user);
        
        return (
        <>
          <div className={`${card} border rounded-xl overflow-hidden`}>
            <div className={`p-4 border-b ${border}`}>
              <h2 className="font-semibold">Current Plan</h2>
            </div>
            <div className="p-6">
              {isFreeUser ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-100'} flex items-center justify-center`}>
                        <BookOpen className="w-6 h-6 text-gray-500" />
                      </div>
                      <div>
                        <p className="font-semibold">Free Reader</p>
                        <p className={`text-sm ${muted}`}>Basic access to Quirrely</p>
                      </div>
                    </div>
                  </div>
                  
                  {/* 🟢 QUICK WIN #1: Addon Bundling + 🟡 P2: Middle Tier */}
                  <div className={`mt-4 p-4 rounded-xl border-2 border-[#FF6B6B] bg-gradient-to-br ${darkMode ? 'from-red-950/30 to-orange-950/30' : 'from-red-50 to-orange-50'}`}>
                    <div className="flex items-center gap-2 mb-3">
                      <Zap className="w-5 h-5 text-[#FF6B6B]" />
                      <span className="font-bold text-[#FF6B6B]">Choose Your Plan</span>
                      <span className="text-xs px-2 py-0.5 bg-[#FF6B6B] text-white rounded-full">25% off annual</span>
                    </div>
                    
                    {/* 🟡 P2: Standalone Tiers with Middle Tier */}
                    <p className={`text-xs font-semibold ${muted} uppercase mb-2`}>Standalone Plans</p>
                    <div className="space-y-2 mb-4">
                      <button className={`w-full p-3 rounded-lg border ${border} ${hover} flex items-center justify-between text-left`}>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center">
                            <PenTool className="w-5 h-5 text-[#FF6B6B]" />
                          </div>
                          <div>
                            <p className="font-semibold">Pro Writer</p>
                            <p className={`text-xs ${muted}`}>Full voice analysis + history</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-[#FF6B6B]">{symbol}{prices.pro.monthly}<span className="text-xs font-normal">/mo</span></p>
                          <p className={`text-xs text-emerald-600`}>{symbol}{prices.pro.annual}/yr</p>
                        </div>
                      </button>
                      
                      {/* 🟡 P2: NEW Middle Tier - Growth */}
                      <button className={`w-full p-3 rounded-lg border-2 border-purple-400 bg-gradient-to-r ${darkMode ? 'from-purple-950/30 to-indigo-950/30' : 'from-purple-50 to-indigo-50'} flex items-center justify-between text-left`}>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                            <TrendingUp className="w-5 h-5 text-purple-600" />
                          </div>
                          <div>
                            <p className="font-semibold flex items-center gap-2">
                              Growth
                              <span className="text-xs px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded">Popular</span>
                            </p>
                            <p className={`text-xs ${muted}`}>Pro + comparison tools + priority support</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-purple-600">{symbol}6.99<span className="text-xs font-normal">/mo</span></p>
                          <p className={`text-xs text-emerald-600`}>{symbol}62.99/yr</p>
                        </div>
                      </button>
                      
                      <button className={`w-full p-3 rounded-lg border ${border} ${hover} flex items-center justify-between text-left`}>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                            <Star className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <p className="font-semibold">Featured</p>
                            <p className={`text-xs ${muted}`}>2x visibility + priority placement</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-blue-600">{symbol}{prices.featured.monthly}<span className="text-xs font-normal">/mo</span></p>
                          <p className={`text-xs text-emerald-600`}>{symbol}{prices.featured.annual}/yr</p>
                        </div>
                      </button>
                    </div>
                    
                    {/* Bundle Options */}
                    <p className={`text-xs font-semibold ${muted} uppercase mb-2`}>Best Value Bundles</p>
                    <div className="space-y-2">
                      <button className={`w-full p-3 rounded-lg border ${border} ${hover} flex items-center justify-between text-left`}>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center">
                            <Crown className="w-5 h-5 text-[#FF6B6B]" />
                          </div>
                          <div>
                            <p className="font-semibold flex items-center gap-2">
                              Pro + Voice+Style
                              <span className="text-xs px-1.5 py-0.5 bg-emerald-100 text-emerald-700 rounded">Save {symbol}2/mo</span>
                            </p>
                            <p className={`text-xs ${muted}`}>Full writing tools + voice evolution</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-[#FF6B6B]">{symbol}12.99<span className="text-xs font-normal">/mo</span></p>
                          <p className={`text-xs ${muted} line-through`}>{symbol}{(prices.pro.monthly + prices.addon.monthly).toFixed(2)}</p>
                        </div>
                      </button>
                      <button className={`w-full p-3 rounded-lg border-2 border-amber-400 bg-gradient-to-r ${darkMode ? 'from-amber-950/30 to-yellow-950/30' : 'from-amber-50 to-yellow-50'} flex items-center justify-between text-left`}>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
                            <Crown className="w-5 h-5 text-amber-600" />
                          </div>
                          <div>
                            <p className="font-semibold flex items-center gap-2">
                              Authority + Voice+Style
                              <span className="text-xs px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded">Best Value</span>
                            </p>
                            <p className={`text-xs ${muted}`}>Full authority status + all voice features</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-amber-600">{symbol}16.99<span className="text-xs font-normal">/mo</span></p>
                          <p className={`text-xs ${muted} line-through`}>{symbol}{(prices.authority.monthly + prices.addon.monthly).toFixed(2)}</p>
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-lg ${tierKey === 'authority' ? 'bg-amber-100' : tierKey === 'featured' ? 'bg-blue-100' : 'bg-[#FF6B6B]/10'} flex items-center justify-center`}>
                        <Crown className={`w-6 h-6 ${tierKey === 'authority' ? 'text-amber-600' : tierKey === 'featured' ? 'text-blue-600' : 'text-[#FF6B6B]'}`} />
                      </div>
                      <div>
                        <p className="font-semibold">{formatTier(user.writerTier !== 'free' ? user.writerTier : user.curatorTier)}</p>
                        <p className={`text-sm ${muted}`}>{symbol}{baseTierPrice.toFixed(2)}/month • Renews March 15, 2026</p>
                      </div>
                    </div>
                    <button className={`px-4 py-2 rounded-lg border ${border} ${hover}`}>Change Plan</button>
                  </div>
                  {hasVoiceStyle(user) && (
                    <div className={`pt-4 border-t ${border} flex items-center justify-between`}>
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-lg bg-emerald-100 flex items-center justify-center">
                          <Sparkles className="w-6 h-6 text-emerald-600" />
                        </div>
                        <div>
                          <p className="font-semibold">Voice + Style</p>
                          <p className={`text-sm ${muted}`}>{symbol}{addonPrice.toFixed(2)}/month</p>
                        </div>
                      </div>
                      <span className="text-emerald-600 text-sm font-medium">Active</span>
                    </div>
                  )}
                  {(hasVoiceStyle(user) && baseTierPrice > 0) && (
                    <div className={`mt-4 pt-4 border-t ${border} flex justify-between`}>
                      <span className="font-semibold">Monthly Total</span>
                      <span className="font-bold text-lg">{symbol}{totalPrice.toFixed(2)}/month</span>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
          
          {!isFreeUser && (
            <>
              {/* 🟡 P2: Annual Discount Upgrade Prompt (25% off) */}
              <div className={`${card} border-2 border-emerald-400 rounded-xl overflow-hidden bg-gradient-to-r ${darkMode ? 'from-emerald-950/30 to-teal-950/30' : 'from-emerald-50 to-teal-50'}`}>
                <div className="p-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-4">
                      <div className="w-14 h-14 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                        <TrendingUp className="w-7 h-7 text-emerald-600" />
                      </div>
                      <div>
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <h3 className="font-bold text-emerald-800">Switch to Annual & Save 25%</h3>
                          <span className="text-xs px-2 py-0.5 bg-emerald-500 text-white rounded-full whitespace-nowrap">Limited Time</span>
                        </div>
                        <p className={`text-sm ${muted} mb-2`}>
                          You're currently paying {symbol}{(totalPrice * 12).toFixed(2)}/year on monthly billing.
                        </p>
                        <div className="flex flex-wrap items-center gap-4">
                          <div>
                            <p className="text-2xl font-bold text-emerald-600">{symbol}{totalAnnual.toFixed(2)}<span className="text-sm font-normal">/year</span></p>
                            <p className="text-xs text-emerald-600">Save {symbol}{annualSavings.toFixed(2)} per year</p>
                          </div>
                          <LoadingButton id="switch-annual" variant="emerald" className="px-4 py-2 rounded-lg font-medium">
                            <Zap className="w-4 h-4" />
                            Switch to Annual
                          </LoadingButton>
                        </div>
                      </div>
                    </div>
                    <button className={`text-sm ${muted} hover:text-gray-700`}>✕</button>
                  </div>
                </div>
              </div>
              
              <div className={`${card} border rounded-xl overflow-hidden`}>
                <div className={`p-4 border-b ${border}`}>
                  <h2 className="font-semibold">Payment Method</h2>
                </div>
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-100'} flex items-center justify-center text-lg`}>
                        💳
                      </div>
                      <div>
                        <p className="font-medium">•••• •••• •••• 4242</p>
                        <p className={`text-sm ${muted}`}>Expires 12/2027</p>
                      </div>
                    </div>
                    <button className={`px-4 py-2 rounded-lg border ${border} ${hover}`}>Update</button>
                  </div>
                </div>
              </div>
              
              <div className={`${card} border rounded-xl overflow-hidden`}>
                <div className={`p-4 border-b ${border}`}>
                  <h2 className="font-semibold">Billing History</h2>
                </div>
                <div className={`divide-y ${border}`}>
                  {[
                    { date: 'Feb 15, 2026', amount: `${symbol}${totalPrice.toFixed(2)}`, status: 'Paid' },
                    { date: 'Jan 15, 2026', amount: `${symbol}${totalPrice.toFixed(2)}`, status: 'Paid' },
                    { date: 'Dec 15, 2025', amount: `${symbol}${totalPrice.toFixed(2)}`, status: 'Paid' },
                  ].map((invoice, i) => (
                    <div key={i} className="p-4 flex items-center justify-between">
                      <div>
                        <p className="font-medium">{invoice.date}</p>
                        <p className={`text-sm ${muted}`}>Monthly subscription</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{invoice.amount}</p>
                        <p className="text-sm text-emerald-600">{invoice.status}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* 🟢 QUICK WIN #2: Downgrade Prevention */}
              <div className={`${card} border rounded-xl overflow-hidden`}>
                <div className={`p-4 border-b ${border}`}>
                  <h2 className="font-semibold">Subscription Management</h2>
                </div>
                <div className="p-6 space-y-4">
                  <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
                    <p className="font-medium mb-2">Need a break? Consider these options:</p>
                    <div className="space-y-2">
                      <button className={`w-full p-3 rounded-lg border-2 border-blue-400 bg-blue-50 ${darkMode ? 'bg-blue-950/30' : ''} flex items-center justify-between text-left group hover:border-blue-500`}>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <Calendar className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <p className="font-semibold text-blue-700">Pause Subscription</p>
                            <p className={`text-xs ${muted}`}>Take 1-3 months off, keep your data & settings</p>
                          </div>
                        </div>
                        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">Recommended</span>
                      </button>
                      
                      <button className={`w-full p-3 rounded-lg border ${border} ${hover} flex items-center justify-between text-left`}>
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} flex items-center justify-center`}>
                            <ChevronDown className="w-5 h-5 text-gray-500" />
                          </div>
                          <div>
                            <p className="font-medium">Downgrade to {tierKey === 'authority' ? 'Featured' : tierKey === 'featured' ? 'Pro' : 'Free'}</p>
                            <p className={`text-xs ${muted}`}>Keep some features at a lower price</p>
                          </div>
                        </div>
                        <span className={`text-sm ${muted}`}>{tierKey === 'authority' ? `${symbol}${prices.featured.monthly}/mo` : tierKey === 'featured' ? `${symbol}${prices.pro.monthly}/mo` : 'Free'}</span>
                      </button>
                      
                      <button className={`w-full p-3 rounded-lg border border-orange-300 bg-orange-50 ${darkMode ? 'bg-orange-950/30' : ''} flex items-center justify-between text-left`}>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                            <Zap className="w-5 h-5 text-orange-600" />
                          </div>
                          <div>
                            <p className="font-semibold text-orange-700">Stay & Save 50%</p>
                            <p className={`text-xs ${muted}`}>Get 2 months at half price</p>
                          </div>
                        </div>
                        <span className="text-xs px-2 py-1 bg-orange-100 text-orange-700 rounded-full">{symbol}{(baseTierPrice * 0.5).toFixed(2)}/mo</span>
                      </button>
                    </div>
                  </div>
                  
                  <div className={`pt-4 border-t ${border}`}>
                    <button className={`text-sm ${muted} hover:text-red-500 transition-colors`}>
                      Cancel subscription (access ends March 15, 2026)
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}
        </>
        );
      })()}
    </>
  );
};

const ComposableDashboard = () => {
  const [selectedUser, setSelectedUser] = useState('authority_writer');
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showUserPicker, setShowUserPicker] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');
  const [loadingAction, setLoadingAction] = useState(null); // M4: Loading states
  
  const user = USERS[selectedUser];
  const features = getFeatures(user);
  
  const bg = darkMode ? 'bg-gray-950 text-gray-100' : 'bg-gray-50 text-gray-900';
  const card = darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200';
  const muted = darkMode ? 'text-gray-400' : 'text-gray-500';
  const hover = darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-100';
  const border = darkMode ? 'border-gray-800' : 'border-gray-200';
  
  // M4: LoadingButton component for CTA feedback
  const LoadingButton = ({ id, onClick, children, className, variant = 'coral' }) => {
    const isLoading = loadingAction === id;
    const variants = {
      coral: 'bg-[#FF6B6B] hover:bg-[#ff5252] text-white',
      emerald: 'bg-emerald-500 hover:bg-emerald-600 text-white',
      amber: 'bg-amber-100 hover:bg-amber-200 text-amber-700',
      purple: 'bg-purple-500 hover:bg-purple-600 text-white',
      blue: 'bg-blue-500 hover:bg-blue-600 text-white',
    };
    const handleClick = async () => {
      setLoadingAction(id);
      if (onClick) await onClick();
      setTimeout(() => setLoadingAction(null), 1500);
    };
    return (
      <button 
        onClick={handleClick}
        disabled={isLoading}
        className={`${className} ${variants[variant]} flex items-center justify-center gap-2 transition-all disabled:opacity-70 disabled:cursor-not-allowed`}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span>Processing...</span>
          </>
        ) : children}
      </button>
    );
  };
  
  const stats = {
    authorityScore: 94.7, followers: 2341, totalReads: 12847, postsWritten: 47,
    pathFollowers: 1247, pathsCreated: 8, readingStreak: 23,
  };
  
  const voiceProfile = { primary: 'Assertive', secondary: 'Narrative', confidence: 87.2,
    tokens: ['Confident 89%', 'Narrative 91%', 'Engaged 85%', 'Structured 82%', 'Warm 76%'] };
  
  const posts = [
    { title: 'The Weight of Winter Words', reads: 1247, featured: true },
    { title: 'Mapping the Canadian Literary Landscape', reads: 2341, featured: false },
    { title: 'Northern Lights of the Mind', reads: 1893, featured: true },
  ];
  
  const paths = [
    { title: 'Canadian Voices: Modern Literary Fiction', followers: 438 },
    { title: 'Nature Writing & Environmental Essays', followers: 312 },
    { title: "Finding Your Voice: A Writer's Journey", followers: 297 },
  ];
  
  const activities = [
    ...(isAuthorityTier(user) ? [{ title: 'Reached Top 25 globally!', icon: Trophy, type: 'authority' }] : []),
    ...(hasWriterTrack(user) ? [{ title: '89 new followers this week', icon: Users, type: 'followers' }] : []),
    { title: 'Earned Consistency Badge', icon: Award, type: 'badge' },
    ...(hasCuratorTrack(user) ? [{ title: 'Path featured in Weekly Picks', icon: Route, type: 'path' }] : []),
    ...(hasVoiceStyle(user) ? [{ title: 'Voice confidence reached 87%', icon: Sparkles, type: 'voice' }] : []),
  ].slice(0, 4);
  
  const getBadgeStyle = (color) => {
    const styles = {
      coral: 'bg-red-100 text-red-800', blue: 'bg-blue-100 text-blue-800',
      amber: 'bg-amber-100 text-amber-800', purple: 'bg-purple-100 text-purple-800',
      indigo: 'bg-indigo-100 text-indigo-800',
    };
    return styles[color] || 'bg-gray-100 text-gray-800';
  };
  
  const badges = [];
  if (user.writerTier !== 'free') {
    const map = { pro: ['Pro Writer', 'coral'], featured_writer: ['Featured Writer', 'blue'], authority_writer: ['👑 Authority Writer', 'amber'] };
    if (map[user.writerTier]) badges.push({ label: map[user.writerTier][0], color: map[user.writerTier][1] });
  }
  if (user.curatorTier !== 'free') {
    const map = { curator: ['Curator', 'purple'], featured_curator: ['Featured Curator', 'indigo'], authority_curator: ['👑 Authority Curator', 'amber'] };
    if (map[user.curatorTier]) badges.push({ label: map[user.curatorTier][0], color: map[user.curatorTier][1] });
  }
  
  // Helper to format tier labels nicely
  const formatTier = (tier) => {
    const labels = {
      free: 'Free',
      pro: 'Pro Writer',
      curator: 'Curator',
      featured_writer: 'Featured Writer',
      featured_curator: 'Featured Curator',
      authority_writer: 'Authority Writer',
      authority_curator: 'Authority Curator',
    };
    return labels[tier] || tier;
  };
  
  return (
    <div className={`min-h-screen ${bg} transition-colors`}>
      {/* User Picker Modal */}
      {showUserPicker && (
        <div className="fixed inset-0 bg-black/50 z-[100] flex items-center justify-center p-4" onClick={() => setShowUserPicker(false)}>
          <div className={`${card} border rounded-xl w-full max-w-md max-h-[80vh] overflow-auto`} onClick={e => e.stopPropagation()}>
            <div className={`p-4 border-b ${border} font-semibold`}>Switch User Profile</div>
            <div className="p-2">
              {Object.entries(USERS).map(([key, u]) => (
                <button key={key} onClick={() => { setSelectedUser(key); setShowUserPicker(false); }}
                  className={`w-full p-3 rounded-lg text-left ${hover} flex items-center gap-3 ${selectedUser === key ? 'ring-2 ring-[#FF6B6B]' : ''}`}>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                    TIER_LEVELS[u.writerTier] >= 3 || TIER_LEVELS[u.curatorTier] >= 3 ? 'bg-gradient-to-br from-amber-400 to-yellow-500' : 'bg-gradient-to-br from-red-400 to-red-500'
                  }`}>{u.name.split(' ').map(n => n[0]).join('').slice(0, 2)}</div>
                  <div className="flex-1">
                    <p className="font-medium">{u.name}</p>
                    <p className={`text-xs ${muted}`}>
                      {u.writerTier !== 'free' ? formatTier(u.writerTier) : ''}
                      {u.writerTier !== 'free' && u.curatorTier !== 'free' ? ' + ' : ''}
                      {u.curatorTier !== 'free' ? formatTier(u.curatorTier) : ''}
                      {u.writerTier === 'free' && u.curatorTier === 'free' ? 'Free Reader' : ''}
                      {u.addons?.includes('voice_style') ? ' + Voice+Style' : ''}
                    </p>
                  </div>
                  {selectedUser === key && <Check className="w-5 h-5 text-[#FF6B6B]" />}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {sidebarOpen && <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />}
      
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 ${card} border-r transform transition-transform duration-300 lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className={`p-4 border-b ${border} lg:hidden flex justify-between`}>
          <span className="font-semibold">Menu</span>
          <button onClick={() => setSidebarOpen(false)}><X className="w-5 h-5" /></button>
        </div>
        
        <button onClick={() => setShowUserPicker(true)} className={`w-full p-4 border-b ${border} ${hover} text-left`}>
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold ${
              isAuthorityTier(user) ? 'bg-gradient-to-br from-amber-400 to-yellow-500 ring-2 ring-amber-400/50' : 'bg-gradient-to-br from-red-400 to-red-500'
            }`}>{user.name.split(' ').map(n => n[0]).join('').slice(0, 2)}</div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold truncate">{user.name}</p>
              <p className={`text-sm ${muted} truncate`}>@{user.handle}</p>
            </div>
            <ChevronDown className={`w-4 h-4 ${muted}`} />
          </div>
          {badges.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {badges.map((b, i) => <span key={i} className={`text-xs px-2 py-0.5 rounded-full ${getBadgeStyle(b.color)}`}>{b.label}</span>)}
              {hasVoiceStyle(user) && <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">✨ V+S</span>}
            </div>
          )}
        </button>
        
        <nav className="p-3 space-y-1 overflow-y-auto h-[calc(100vh-250px)]">
          {/* General */}
          <p className={`text-xs font-semibold ${muted} uppercase mt-2 mb-1 px-3`}>General</p>
          <button onClick={() => { setCurrentView('dashboard'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'dashboard' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
            <BarChart3 className="w-4 h-4" />Dashboard
          </button>
          <button onClick={() => { setCurrentView('discover'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'discover' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
            <Compass className="w-4 h-4" />Discover
          </button>
          <button onClick={() => { setCurrentView('streak'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'streak' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
            <Flame className="w-4 h-4" />Streak <span className={`ml-auto text-xs ${currentView === 'streak' ? 'bg-white/20' : 'bg-[#FF6B6B]'} text-white px-1.5 py-0.5 rounded-full`}>{stats.readingStreak}</span>
          </button>
          
          {/* Writer */}
          {(hasWriterTrack(user) || hasVoiceStyle(user)) && (
            <>
              <p className={`text-xs font-semibold ${muted} uppercase mt-4 mb-1 px-3`}>Writer</p>
              {features.myWriting && (
                <button onClick={() => { setCurrentView('writing'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'writing' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
                  <PenTool className="w-4 h-4" />My Writing
                </button>
              )}
              {features.voiceProfile && (
                <button onClick={() => { setCurrentView('voice'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'voice' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
                  <Sparkles className="w-4 h-4" />Voice Profile {features.voiceEvolution && <span className={`ml-auto text-xs ${currentView === 'voice' ? 'bg-white/20' : 'bg-emerald-500'} text-white px-1.5 py-0.5 rounded-full`}>✨</span>}
                </button>
              )}
              {features.writerAnalytics && (
                <button onClick={() => { setCurrentView('writer-analytics'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'writer-analytics' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
                  <BarChart3 className="w-4 h-4" />Analytics
                </button>
              )}
            </>
          )}
          
          {/* Curator */}
          {hasCuratorTrack(user) && (
            <>
              <p className={`text-xs font-semibold ${muted} uppercase mt-4 mb-1 px-3`}>Curator</p>
              <button onClick={() => { setCurrentView('paths'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'paths' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
                <Route className="w-4 h-4" />Reading Paths
              </button>
              <button onClick={() => { setCurrentView('path-followers'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'path-followers' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
                <Users className="w-4 h-4" />Path Followers
              </button>
            </>
          )}
          
          {/* Authority */}
          {isFeaturedTier(user) && (
            <>
              <p className={`text-xs font-semibold ${muted} uppercase mt-4 mb-1 px-3`}>Authority</p>
              <button onClick={() => { setCurrentView('authority-hub'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'authority-hub' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
                <Crown className="w-4 h-4 text-amber-500" />Authority Hub
              </button>
              <button onClick={() => { setCurrentView('leaderboard'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'leaderboard' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
                <Trophy className="w-4 h-4" />Leaderboard
              </button>
            </>
          )}
          
          {/* Add Track */}
          {canAddTrack(user) && !isDualTrack(user) && (
            <button className={`w-full mt-4 p-2.5 rounded-lg border ${border} ${hover} text-left`}>
              <div className="flex items-center gap-2 text-sm"><Plus className="w-4 h-4 text-[#FF6B6B]" />Add {hasCuratorTrack(user) ? 'Writer' : 'Curator'} Track</div>
            </button>
          )}
        </nav>
        
        <div className={`absolute bottom-0 left-0 right-0 p-3 border-t ${border}`}>
          <button onClick={() => { setCurrentView('settings'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'settings' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
            <Settings className="w-4 h-4" />Settings
          </button>
          <button onClick={() => { setCurrentView('help'); setSidebarOpen(false); }} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm ${currentView === 'help' ? 'bg-[#FF6B6B] text-white' : `${muted} ${hover}`}`}>
            <HelpCircle className="w-4 h-4" />Help
          </button>
        </div>
      </aside>
      
      {/* Main */}
      <div className="lg:pl-64">
        <header className={`sticky top-0 z-30 h-16 flex items-center justify-between px-4 lg:px-6 ${card} border-b`}>
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(true)} className={`p-2 rounded-lg ${hover} lg:hidden`}><Menu className="w-5 h-5" /></button>
            <svg viewBox="0 0 100 120" width="32" height="38">
              <path d="M58 112 Q85 98, 94 62 Q100 26, 74 8 Q50 -8, 42 22 Q38 44, 54 60 Q70 78, 62 100 Q58 110, 58 112" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
              <ellipse cx="40" cy="98" rx="22" ry="26" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
              <ellipse cx="40" cy="78" rx="9" ry="4" fill="#E85A5A"/><path d="M31 78 Q30 94, 40 99 Q50 94, 49 78 Z" fill="#FF6B6B"/>
              <ellipse cx="40" cy="50" rx="22" ry="20" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
              <ellipse cx="32" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/><ellipse cx="48" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>
              <circle cx="33" cy="46.5" r="2" fill="#FFF"/><circle cx="49" cy="46.5" r="2" fill="#FFF"/>
              <ellipse cx="40" cy="60" rx="4.5" ry="3.5" fill="#4A4A4A"/>
            </svg>
            <span className="text-xl font-bold hidden sm:block">Quirrely</span>
            <div className="hidden md:flex items-center gap-2">
              {badges.map((b, i) => <span key={i} className={`text-xs px-2.5 py-1 rounded-full font-medium ${getBadgeStyle(b.color)}`}>{b.label}</span>)}
              {hasVoiceStyle(user) && <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-emerald-100 text-emerald-800">✨ Voice+Style</span>}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setDarkMode(!darkMode)} className={`p-2 rounded-lg ${hover}`}>{darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}</button>
            <button className={`p-2 rounded-lg ${hover} relative`}><Bell className="w-5 h-5" /><span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#FF6B6B] rounded-full" /></button>
            <span className={`hidden sm:flex items-center gap-1 px-2 py-1 rounded-lg text-sm ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}>{FLAGS[user.country]} {user.country}</span>
            <div className={`w-9 h-9 rounded-full flex items-center justify-center text-white font-bold text-sm ${isAuthorityTier(user) ? 'bg-gradient-to-br from-amber-400 to-yellow-500 ring-2 ring-amber-400/30' : 'bg-gradient-to-br from-red-400 to-red-500'}`}>
              {user.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
            </div>
          </div>
        </header>
        
        <main className="p-4 lg:p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Voice Profile Detail View */}
            {currentView === 'voice' && (
              <>
                <button onClick={() => setCurrentView('dashboard')} className={`flex items-center gap-2 ${muted} hover:text-[#FF6B6B] transition-colors`}>
                  <ArrowLeft className="w-4 h-4" />Back to Dashboard
                </button>
                
                <div>
                  <h1 className="text-2xl font-bold flex items-center gap-2">
                    <Sparkles className="w-6 h-6 text-emerald-500" />
                    Your Writing Voice
                    {features.voiceEvolution && <span className="text-sm px-2 py-1 bg-emerald-100 text-emerald-800 rounded-full">✨ Evolution Tracking</span>}
                  </h1>
                  <p className={muted}>Deep analysis of your unique writing style</p>
                </div>
                
                {/* Voice Overview Card */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className="p-6 bg-gradient-to-br from-emerald-50 to-teal-50">
                    <div className="flex flex-col lg:flex-row gap-8">
                      {/* Confidence Circle */}
                      <div className="flex flex-col items-center">
                        <div className="w-48 h-48 rounded-full border-8 border-emerald-500/30 flex items-center justify-center bg-emerald-100/50 relative">
                          <div className="text-center">
                            <p className="text-5xl font-bold text-emerald-600">{voiceProfile.confidence}%</p>
                            <p className="text-sm text-emerald-600 mt-1">Confidence</p>
                          </div>
                          <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
                            <circle cx="50" cy="50" r="45" fill="none" stroke="#10B98133" strokeWidth="8" />
                            <circle cx="50" cy="50" r="45" fill="none" stroke="#10B981" strokeWidth="8" 
                              strokeDasharray={`${voiceProfile.confidence * 2.83} 283`} strokeLinecap="round" />
                          </svg>
                        </div>
                        <p className={`text-sm ${muted} mt-4`}>Based on 67 analyses</p>
                      </div>
                      
                      {/* Voice Type */}
                      <div className="flex-1">
                        <h2 className="text-3xl font-bold text-emerald-600 mb-2">{voiceProfile.primary} {voiceProfile.secondary}</h2>
                        <p className={`${muted} text-lg mb-6`}>
                          You write with confidence and narrative flair. Your voice combines direct statements with rich storytelling, 
                          creating an engaging and authoritative presence on the page.
                        </p>
                        
                        <h3 className="font-semibold mb-3">Voice Tokens</h3>
                        <div className="flex flex-wrap gap-2">
                          {voiceProfile.tokens.map((t, i) => (
                            <span key={i} className="px-4 py-2 rounded-full text-sm bg-emerald-100 text-emerald-800 font-medium">{t}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Voice Dimensions */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold">Voice Dimensions</h2>
                  </div>
                  <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[
                      { name: 'Assertiveness', value: 87, desc: 'Confident vs. Tentative' },
                      { name: 'Formality', value: 62, desc: 'Professional vs. Casual' },
                      { name: 'Detail', value: 74, desc: 'Comprehensive vs. Concise' },
                      { name: 'Poeticism', value: 68, desc: 'Lyrical vs. Direct' },
                      { name: 'Openness', value: 55, desc: 'Personal vs. Reserved' },
                      { name: 'Dynamism', value: 81, desc: 'Energetic vs. Measured' },
                    ].map((dim, i) => (
                      <div key={i}>
                        <div className="flex justify-between mb-1">
                          <span className="font-medium">{dim.name}</span>
                          <span className="text-emerald-600 font-semibold">{dim.value}%</span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden mb-1">
                          <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${dim.value}%` }} />
                        </div>
                        <p className={`text-xs ${muted}`}>{dim.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Voice Evolution (if addon) */}
                {features.voiceEvolution && (
                  <div className={`${card} border rounded-xl overflow-hidden`}>
                    <div className={`p-4 border-b ${border}`}>
                      <h2 className="font-semibold flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-emerald-500" />
                        Voice Evolution
                        <span className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full">Voice+Style</span>
                      </h2>
                    </div>
                    <div className="p-6">
                      <div className="flex items-center gap-8 mb-6">
                        <div className="text-center">
                          <p className="text-3xl font-bold text-emerald-600">+12%</p>
                          <p className={`text-sm ${muted}`}>Confidence growth</p>
                        </div>
                        <div className="text-center">
                          <p className="text-3xl font-bold">67</p>
                          <p className={`text-sm ${muted}`}>Analyses completed</p>
                        </div>
                        <div className="text-center">
                          <p className="text-3xl font-bold">90</p>
                          <p className={`text-sm ${muted}`}>Days tracked</p>
                        </div>
                      </div>
                      <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
                        <p className={`text-sm ${muted}`}>
                          Your voice has become more assertive over the past 3 months, with a notable increase in narrative 
                          elements. Your confidence score has grown steadily as you've submitted more writing samples.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
            
            {/* My Writing View */}
            {currentView === 'writing' && (
              <>
                <button onClick={() => setCurrentView('dashboard')} className={`flex items-center gap-2 ${muted} hover:text-[#FF6B6B] transition-colors`}>
                  <ArrowLeft className="w-4 h-4" />Back to Dashboard
                </button>
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold">My Writing</h1>
                    <p className={muted}>{posts.length} published posts</p>
                  </div>
                  <button className="px-4 py-2 bg-[#FF6B6B] text-white rounded-lg hover:bg-[#ff5252] flex items-center gap-2">
                    <Plus className="w-4 h-4" />New Post
                  </button>
                </div>
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`divide-y ${border}`}>
                    {posts.map((p, i) => (
                      <button key={i} className={`w-full p-4 flex items-center gap-4 text-left ${hover}`}>
                        <div className="w-12 h-12 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center">
                          {p.featured ? <Star className="w-6 h-6 text-[#FF6B6B]" /> : <FileText className="w-6 h-6 text-[#FF6B6B]" />}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-medium">{p.title}</p>
                            {p.featured && <span className="px-2 py-0.5 text-xs bg-amber-100 text-amber-800 rounded">Featured</span>}
                          </div>
                          <p className={`text-sm ${muted}`}>{p.reads.toLocaleString()} reads</p>
                        </div>
                        <ChevronRight className={`w-5 h-5 ${muted}`} />
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
            
            {/* Reading Paths View */}
            {currentView === 'paths' && (
              <>
                <button onClick={() => setCurrentView('dashboard')} className={`flex items-center gap-2 ${muted} hover:text-[#FF6B6B] transition-colors`}>
                  <ArrowLeft className="w-4 h-4" />Back to Dashboard
                </button>
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold">Reading Paths</h1>
                    <p className={muted}>{paths.length} paths curated</p>
                  </div>
                  <button className="px-4 py-2 bg-[#FF6B6B] text-white rounded-lg hover:bg-[#ff5252] flex items-center gap-2">
                    <Plus className="w-4 h-4" />New Path
                  </button>
                </div>
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`divide-y ${border}`}>
                    {paths.map((p, i) => (
                      <button key={i} className={`w-full p-4 flex items-center gap-4 text-left ${hover}`}>
                        <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center">
                          <Route className="w-6 h-6 text-purple-600" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium mb-1">{p.title}</p>
                          <p className={`text-sm ${muted}`}>{p.followers} followers</p>
                        </div>
                        <span className="text-sm text-emerald-600 flex items-center gap-1"><TrendingUp className="w-4 h-4" />+12</span>
                        <ChevronRight className={`w-5 h-5 ${muted}`} />
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
            
            {/* Discover View */}
            {currentView === 'discover' && (
              <>
                <button onClick={() => setCurrentView('dashboard')} className={`flex items-center gap-2 ${muted} hover:text-[#FF6B6B] transition-colors`}>
                  <ArrowLeft className="w-4 h-4" />Back to Dashboard
                </button>
                
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold">Discover</h1>
                    <p className={muted}>Find new writers and reading paths</p>
                  </div>
                  <div className="flex gap-2">
                    <button className={`px-3 py-1.5 rounded-lg text-sm ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}>All</button>
                    <button className={`px-3 py-1.5 rounded-lg text-sm ${muted} ${hover}`}>Writers</button>
                    <button className={`px-3 py-1.5 rounded-lg text-sm ${muted} ${hover}`}>Paths</button>
                    <button className={`px-3 py-1.5 rounded-lg text-sm ${muted} ${hover}`}>Topics</button>
                  </div>
                </div>
                
                {/* Featured Section */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold flex items-center gap-2"><Star className="w-5 h-5 text-amber-500" />Featured This Week</h2>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
                    {[
                      { type: 'writer', name: 'Sarah Mitchell', handle: 'sarahwrites', bio: 'Essays on climate and nature', followers: 3420 },
                      { type: 'path', name: 'Philosophy for Beginners', curator: 'David Chen', posts: 24, followers: 1890 },
                      { type: 'writer', name: 'James Okonkwo', handle: 'jamesokonkwo', bio: 'Tech culture and society', followers: 5670 },
                    ].map((item, i) => (
                      <button key={i} onClick={() => alert(`${item.type === 'writer' ? 'Writer' : 'Path'} profiles coming soon!`)} className={`p-4 rounded-lg border ${border} ${hover} text-left transition-all hover:border-[#FF6B6B]/50`}>
                        <div className="flex items-start gap-3">
                          <div className={`w-12 h-12 rounded-full flex items-center justify-center ${item.type === 'writer' ? 'bg-[#FF6B6B]/10' : 'bg-purple-100'}`}>
                            {item.type === 'writer' ? <PenTool className="w-5 h-5 text-[#FF6B6B]" /> : <Route className="w-5 h-5 text-purple-600" />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium">{item.name}</p>
                            <p className={`text-sm ${muted} truncate`}>{item.type === 'writer' ? `@${item.handle}` : `by ${item.curator}`}</p>
                            <p className={`text-xs ${muted} mt-1`}>{item.followers.toLocaleString()} followers</p>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
                
                {/* Trending Topics */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold flex items-center gap-2"><TrendingUp className="w-5 h-5 text-emerald-500" />Trending Topics</h2>
                  </div>
                  <div className="p-4 flex flex-wrap gap-2">
                    {['Climate Writing', 'AI & Creativity', 'Personal Essays', 'Book Reviews', 'Science Communication', 'Poetry', 'Travel Writing', 'Philosophy', 'Tech Culture', 'Food Writing'].map((topic, i) => (
                      <button key={i} onClick={() => alert(`Topic search for "${topic}" coming soon!`)} className={`px-4 py-2 rounded-full text-sm ${hover} border ${border} hover:border-[#FF6B6B]/50 transition-all`}>{topic}</button>
                    ))}
                  </div>
                </div>
                
                {/* Recent Posts */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold">Recent from Writers You Follow</h2>
                  </div>
                  <div className={`divide-y ${border}`}>
                    {[
                      { title: 'The Art of Slow Reading', author: 'Maria Santos', time: '2 hours ago', reads: 342 },
                      { title: 'Why We Need More Nature Writing', author: 'Tom Harris', time: '5 hours ago', reads: 891 },
                      { title: 'Digital Minimalism in Practice', author: 'Anna Lee', time: '1 day ago', reads: 1203 },
                    ].map((post, i) => (
                      <button key={i} onClick={() => alert(`Post reader coming soon!`)} className={`w-full p-4 flex items-center gap-4 text-left ${hover}`}>
                        <div className="w-10 h-10 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center">
                          <FileText className="w-5 h-5 text-[#FF6B6B]" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{post.title}</p>
                          <p className={`text-sm ${muted}`}>{post.author} • {post.time}</p>
                        </div>
                        <span className={`text-sm ${muted}`}>{post.reads} reads</span>
                        <ChevronRight className={`w-5 h-5 ${muted}`} />
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
            
            {/* 🟠 P3: Achievement System - Enhanced Streak View */}
            {currentView === 'streak' && (
              <>
                <button onClick={() => setCurrentView('dashboard')} className={`flex items-center gap-2 ${muted} hover:text-[#FF6B6B] transition-colors`}>
                  <ArrowLeft className="w-4 h-4" />Back to Dashboard
                </button>
                
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                      <Trophy className="w-6 h-6 text-amber-500" />
                      Achievements & Streaks
                    </h1>
                    <p className={muted}>Track your progress and unlock rewards</p>
                  </div>
                  <div className={`px-4 py-2 rounded-full ${darkMode ? 'bg-amber-900/30' : 'bg-amber-100'} text-amber-700 font-semibold`}>
                    Level 7 • 2,340 XP
                  </div>
                </div>
                
                {/* 🟠 P3: XP Progress Bar */}
                <div className={`${card} border rounded-xl p-6`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold">Level 7 Progress</span>
                    <span className={`text-sm ${muted}`}>2,340 / 3,000 XP to Level 8</span>
                  </div>
                  <div className="h-4 bg-gray-200 rounded-full overflow-hidden mb-2">
                    <div className="h-full bg-gradient-to-r from-amber-400 to-yellow-500 rounded-full transition-all" style={{ width: '78%' }} />
                  </div>
                  <p className={`text-sm ${muted}`}>660 XP until next level • Unlock: "Elite Writer" badge + Featured placement priority</p>
                </div>
                
                {/* Streak Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className={`${card} border rounded-xl p-6 text-center`}>
                    <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center">
                      <Flame className="w-8 h-8 text-[#FF6B6B]" />
                    </div>
                    <p className="text-3xl font-bold text-[#FF6B6B]">{stats.readingStreak}</p>
                    <p className={`text-sm ${muted}`}>Day Streak</p>
                    <p className="text-xs text-emerald-600 mt-1">+50 XP/day</p>
                  </div>
                  <div className={`${card} border rounded-xl p-6 text-center`}>
                    <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-amber-100 flex items-center justify-center">
                      <Trophy className="w-8 h-8 text-amber-600" />
                    </div>
                    <p className="text-3xl font-bold">47</p>
                    <p className={`text-sm ${muted}`}>Longest Streak</p>
                    <p className="text-xs text-amber-600 mt-1">Personal Best</p>
                  </div>
                  <div className={`${card} border rounded-xl p-6 text-center`}>
                    <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-emerald-100 flex items-center justify-center">
                      <BookOpen className="w-8 h-8 text-emerald-600" />
                    </div>
                    <p className="text-3xl font-bold">312</p>
                    <p className={`text-sm ${muted}`}>Total Reading Days</p>
                    <p className="text-xs text-emerald-600 mt-1">Top 5% of readers</p>
                  </div>
                  <div className={`${card} border rounded-xl p-6 text-center`}>
                    <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-purple-100 flex items-center justify-center">
                      <Award className="w-8 h-8 text-purple-600" />
                    </div>
                    <p className="text-3xl font-bold">12</p>
                    <p className={`text-sm ${muted}`}>Badges Earned</p>
                    <p className="text-xs text-purple-600 mt-1">4 more available</p>
                  </div>
                </div>
                
                {/* 🟠 P3: Weekly Challenge */}
                <div className={`${card} border-2 border-purple-400 rounded-xl overflow-hidden bg-gradient-to-r ${darkMode ? 'from-purple-950/30 to-indigo-950/30' : 'from-purple-50 to-indigo-50'}`}>
                  <div className={`p-4 border-b border-purple-200`}>
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h2 className="font-semibold flex flex-wrap items-center gap-2">
                        <Zap className="w-5 h-5 text-purple-600 flex-shrink-0" />
                        <span>Weekly Challenge</span>
                        <span className="text-xs px-2 py-0.5 bg-purple-500 text-white rounded-full whitespace-nowrap">Ends in 3 days</span>
                      </h2>
                      <span className="text-sm font-bold text-purple-600 whitespace-nowrap">500 XP Reward</span>
                    </div>
                  </div>
                  <div className="p-6">
                    <div className="flex items-center gap-6">
                      <div className="flex-1">
                        <h3 className="font-bold text-lg mb-1">Voice Evolution Week</h3>
                        <p className={`text-sm ${muted} mb-3`}>Complete 5 voice analyses this week to earn bonus XP and unlock the "Voice Explorer" badge</p>
                        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
                          <div className="flex-1">
                            <div className="flex justify-between text-sm mb-1">
                              <span>Progress</span>
                              <span className="font-semibold">3/5 analyses</span>
                            </div>
                            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-purple-500 rounded-full" style={{ width: '60%' }} />
                            </div>
                          </div>
                          <LoadingButton id="challenge-analyze" variant="purple" className="px-4 py-2 rounded-lg font-medium">
                            Analyze Now
                          </LoadingButton>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Calendar */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold">February 2026</h2>
                  </div>
                  <div className="p-4">
                    <div className="grid grid-cols-7 gap-2 text-center mb-2">
                      {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => (
                        <div key={d} className={`text-xs font-medium ${muted}`}>{d}</div>
                      ))}
                    </div>
                    <div className="grid grid-cols-7 gap-2">
                      {Array.from({ length: 28 }, (_, i) => {
                        const day = i + 1;
                        const isToday = day === 15;
                        const hasStreak = day <= 15 && day > 15 - stats.readingStreak;
                        return (
                          <div key={i} className={`aspect-square rounded-lg flex items-center justify-center text-sm ${
                            isToday ? 'bg-[#FF6B6B] text-white font-bold' :
                            hasStreak ? 'bg-[#FF6B6B]/20 text-[#FF6B6B]' :
                            day <= 15 ? `${darkMode ? 'bg-gray-800' : 'bg-gray-100'}` : ''
                          }`}>
                            {day <= 28 ? day : ''}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
                
                {/* 🟠 P3: Full Badge Collection */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border} flex items-center justify-between`}>
                    <h2 className="font-semibold">Badge Collection</h2>
                    <span className={`text-sm ${muted}`}>12/16 Earned</span>
                  </div>
                  <div className="p-4">
                    {/* Reading Badges */}
                    <p className={`text-xs font-semibold ${muted} uppercase mb-3`}>Reading Streaks</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                      {[
                        { name: 'First Week', icon: '🌱', desc: '7 day streak', xp: 100, earned: true },
                        { name: 'Committed', icon: '📚', desc: '14 day streak', xp: 200, earned: true },
                        { name: 'Dedicated', icon: '🔥', desc: '21 day streak', xp: 300, earned: true },
                        { name: 'Bookworm', icon: '📖', desc: '30 day streak', xp: 500, earned: false, progress: '23/30' },
                      ].map((badge, i) => (
                        <div key={i} className={`p-4 rounded-lg text-center relative ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
                          {badge.earned && <div className="absolute top-2 right-2 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center"><Check className="w-3 h-3 text-white" /></div>}
                          <div className={`text-3xl mb-2 ${!badge.earned && 'grayscale opacity-60'}`}>{badge.icon}</div>
                          <p className={`font-medium text-sm ${!badge.earned && (darkMode ? 'text-gray-400' : 'text-gray-500')}`}>{badge.name}</p>
                          <p className={`text-xs ${muted}`}>{badge.desc}</p>
                          <p className={`text-xs mt-1 ${badge.earned ? 'text-emerald-600' : (darkMode ? 'text-amber-400' : 'text-amber-600')}`}>
                            {badge.earned ? `+${badge.xp} XP` : badge.progress}
                          </p>
                        </div>
                      ))}
                    </div>
                    
                    {/* Writing Badges */}
                    <p className={`text-xs font-semibold ${muted} uppercase mb-3`}>Writing Achievements</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                      {[
                        { name: 'First Analysis', icon: '✍️', desc: 'Complete 1 analysis', xp: 50, earned: true },
                        { name: 'Voice Found', icon: '🎯', desc: 'Reach 70% confidence', xp: 150, earned: true },
                        { name: 'Prolific', icon: '📝', desc: '50 analyses', xp: 400, earned: false, progress: '48/50' },
                        { name: 'Voice Master', icon: '👑', desc: '90% confidence', xp: 1000, earned: false, progress: '87%' },
                      ].map((badge, i) => (
                        <div key={i} className={`p-4 rounded-lg text-center relative ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
                          {badge.earned && <div className="absolute top-2 right-2 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center"><Check className="w-3 h-3 text-white" /></div>}
                          <div className={`text-3xl mb-2 ${!badge.earned && 'grayscale opacity-60'}`}>{badge.icon}</div>
                          <p className={`font-medium text-sm ${!badge.earned && (darkMode ? 'text-gray-400' : 'text-gray-500')}`}>{badge.name}</p>
                          <p className={`text-xs ${muted}`}>{badge.desc}</p>
                          <p className={`text-xs mt-1 ${badge.earned ? 'text-emerald-600' : (darkMode ? 'text-amber-400' : 'text-amber-600')}`}>
                            {badge.earned ? `+${badge.xp} XP` : badge.progress}
                          </p>
                        </div>
                      ))}
                    </div>
                    
                    {/* Community Badges */}
                    <p className={`text-xs font-semibold ${muted} uppercase mb-3`}>Community</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                      {[
                        { name: 'Social', icon: '👋', desc: 'Follow 10 writers', xp: 100, earned: true },
                        { name: 'Engaged', icon: '💬', desc: '25 comments', xp: 150, earned: true },
                        { name: 'Influencer', icon: '⭐', desc: '100 followers', xp: 300, earned: true },
                        { name: 'Thought Leader', icon: '🏆', desc: '1000 followers', xp: 1000, earned: false, progress: '234/1000' },
                      ].map((badge, i) => (
                        <div key={i} className={`p-4 rounded-lg text-center relative ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
                          {badge.earned && <div className="absolute top-2 right-2 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center"><Check className="w-3 h-3 text-white" /></div>}
                          <div className={`text-3xl mb-2 ${!badge.earned && 'grayscale opacity-60'}`}>{badge.icon}</div>
                          <p className={`font-medium text-sm ${!badge.earned && (darkMode ? 'text-gray-400' : 'text-gray-500')}`}>{badge.name}</p>
                          <p className={`text-xs ${muted}`}>{badge.desc}</p>
                          <p className={`text-xs mt-1 ${badge.earned ? 'text-emerald-600' : (darkMode ? 'text-amber-400' : 'text-amber-600')}`}>
                            {badge.earned ? `+${badge.xp} XP` : badge.progress}
                          </p>
                        </div>
                      ))}
                    </div>
                    
                    {/* Special Badges */}
                    <p className={`text-xs font-semibold ${muted} uppercase mb-3`}>Special & Seasonal</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {[
                        { name: 'Early Adopter', icon: '🚀', desc: 'Joined in 2025', xp: 500, earned: true },
                        { name: 'Beta Tester', icon: '🧪', desc: 'Tested new features', xp: 250, earned: true },
                        { name: 'Referrer', icon: '🎁', desc: 'Invite 3 friends', xp: 300, earned: false, progress: '1/3' },
                        { name: 'Annual Pro', icon: '💎', desc: 'Subscribe annually', xp: 500, earned: false, progress: 'Upgrade' },
                      ].map((badge, i) => (
                        <div key={i} className={`p-4 rounded-lg text-center relative ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
                          {badge.earned && <div className="absolute top-2 right-2 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center"><Check className="w-3 h-3 text-white" /></div>}
                          <div className={`text-3xl mb-2 ${!badge.earned && 'grayscale opacity-60'}`}>{badge.icon}</div>
                          <p className={`font-medium text-sm ${!badge.earned && (darkMode ? 'text-gray-400' : 'text-gray-500')}`}>{badge.name}</p>
                          <p className={`text-xs ${muted}`}>{badge.desc}</p>
                          <p className={`text-xs mt-1 ${badge.earned ? 'text-emerald-600' : (darkMode ? 'text-amber-400' : 'text-amber-600')}`}>
                            {badge.earned ? `+${badge.xp} XP` : badge.progress}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                {/* 🟠 P3: Leaderboard Teaser */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border} flex items-center justify-between`}>
                    <h2 className="font-semibold flex items-center gap-2">
                      <Crown className="w-5 h-5 text-amber-500" />
                      Weekly Leaderboard
                    </h2>
                    <button onClick={() => setCurrentView('leaderboard')} className="text-sm text-[#FF6B6B] hover:underline">View Full →</button>
                  </div>
                  <div className={`divide-y ${border}`}>
                    {[
                      { rank: 1, name: 'Elena V.', xp: 4520, change: '+2', you: false },
                      { rank: 2, name: 'Marcus W.', xp: 3890, change: '-1', you: false },
                      { rank: 3, name: 'You', xp: 2340, change: '+5', you: true },
                    ].map((person, i) => (
                      <div key={i} className={`p-4 flex items-center gap-4 ${person.you ? 'bg-amber-50' : ''}`}>
                        <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                          person.rank === 1 ? 'bg-amber-100 text-amber-700' :
                          person.rank === 2 ? 'bg-gray-200 text-gray-700' :
                          'bg-orange-100 text-orange-700'
                        }`}>{person.rank}</span>
                        <div className="flex-1">
                          <p className={`font-medium ${person.you ? 'text-amber-700' : ''}`}>{person.name}</p>
                          <p className={`text-sm ${muted}`}>{person.xp.toLocaleString()} XP this week</p>
                        </div>
                        <span className={`text-sm ${parseInt(person.change) > 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                          {parseInt(person.change) > 0 ? '↑' : '↓'} {Math.abs(parseInt(person.change))}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
            
            {/* Writer Analytics View */}
            {currentView === 'writer-analytics' && (
              <>
                <button onClick={() => setCurrentView('dashboard')} className={`flex items-center gap-2 ${muted} hover:text-[#FF6B6B] transition-colors`}>
                  <ArrowLeft className="w-4 h-4" />Back to Dashboard
                </button>
                
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold">Writing Analytics</h1>
                    <p className={muted}>Track your writing performance</p>
                  </div>
                  <select className={`px-3 py-2 rounded-lg border ${border} ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
                    <option>Last 30 days</option>
                    <option>Last 90 days</option>
                    <option>Last year</option>
                    <option>All time</option>
                  </select>
                </div>
                
                {/* Overview Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: 'Total Reads', value: '12,847', trend: '+15%', icon: Eye },
                    { label: 'Followers', value: '2,341', trend: '+89', icon: Users },
                    { label: 'Comments', value: '487', trend: '+23', icon: MessageCircle },
                    { label: 'Saves', value: '1,203', trend: '+12%', icon: Bookmark },
                  ].map((stat, i) => (
                    <div key={i} className={`${card} border rounded-xl p-4`}>
                      <div className="flex items-center justify-between mb-2">
                        <stat.icon className={`w-5 h-5 ${muted}`} />
                        <span className="text-xs text-emerald-600">{stat.trend}</span>
                      </div>
                      <p className="text-2xl font-bold">{stat.value}</p>
                      <p className={`text-sm ${muted}`}>{stat.label}</p>
                    </div>
                  ))}
                </div>
                
                {/* Chart Placeholder */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold">Reads Over Time</h2>
                  </div>
                  <div className="p-6">
                    <div className="h-48 flex items-end justify-between gap-2">
                      {[65, 45, 78, 52, 90, 68, 85, 72, 95, 88, 76, 100].map((h, i) => (
                        <div key={i} className="flex-1 flex flex-col items-center gap-2">
                          <div className="w-full bg-[#FF6B6B]/20 rounded-t" style={{ height: `${h}%` }}>
                            <div className="w-full bg-[#FF6B6B] rounded-t" style={{ height: '60%' }} />
                          </div>
                          <span className={`text-xs ${muted}`}>{['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'][i]}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                {/* Top Posts */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold">Top Performing Posts</h2>
                  </div>
                  <div className={`divide-y ${border}`}>
                    {posts.map((p, i) => (
                      <div key={i} className="p-4 flex items-center gap-4">
                        <span className={`text-lg font-bold ${muted}`}>#{i + 1}</span>
                        <div className="flex-1">
                          <p className="font-medium">{p.title}</p>
                          <p className={`text-sm ${muted}`}>{p.reads.toLocaleString()} reads</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-emerald-600">+{Math.floor(p.reads * 0.15)}</p>
                          <p className={`text-xs ${muted}`}>this month</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
            
            {/* Path Followers View */}
            {currentView === 'path-followers' && (
              <>
                <button onClick={() => setCurrentView('dashboard')} className={`flex items-center gap-2 ${muted} hover:text-[#FF6B6B] transition-colors`}>
                  <ArrowLeft className="w-4 h-4" />Back to Dashboard
                </button>
                
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold">Path Followers</h1>
                    <p className={muted}>People following your reading paths</p>
                  </div>
                  <div className={`px-4 py-2 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}>
                    <span className="text-2xl font-bold">1,247</span>
                    <span className={`ml-2 ${muted}`}>total followers</span>
                  </div>
                </div>
                
                {/* Growth Chart */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold">Follower Growth</h2>
                  </div>
                  <div className="p-6">
                    <div className="flex items-center gap-8 mb-6">
                      <div>
                        <p className="text-3xl font-bold text-emerald-600">+127</p>
                        <p className={`text-sm ${muted}`}>This month</p>
                      </div>
                      <div>
                        <p className="text-3xl font-bold">+11.3%</p>
                        <p className={`text-sm ${muted}`}>Growth rate</p>
                      </div>
                    </div>
                    <div className="h-32 flex items-end gap-1">
                      {[20, 25, 22, 30, 28, 35, 32, 40, 38, 45, 50, 55, 52, 60].map((h, i) => (
                        <div key={i} className="flex-1 bg-purple-500 rounded-t" style={{ height: `${h}%` }} />
                      ))}
                    </div>
                  </div>
                </div>
                
                {/* Recent Followers */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold">Recent Followers</h2>
                  </div>
                  <div className={`divide-y ${border}`}>
                    {[
                      { name: 'Emily Watson', handle: 'emilyw', path: 'Canadian Voices', time: '2 hours ago' },
                      { name: 'Michael Brown', handle: 'mikebrown', path: 'Nature Writing', time: '5 hours ago' },
                      { name: 'Lisa Chen', handle: 'lisareads', path: 'Canadian Voices', time: '1 day ago' },
                      { name: 'David Kim', handle: 'davidk', path: "Finding Your Voice", time: '2 days ago' },
                      { name: 'Rachel Green', handle: 'rachelg', path: 'Nature Writing', time: '3 days ago' },
                    ].map((follower, i) => (
                      <div key={i} className={`p-4 flex items-center gap-4 ${hover}`}>
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center text-white font-bold">
                          {follower.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium">{follower.name}</p>
                          <p className={`text-sm ${muted}`}>@{follower.handle} • followed {follower.path}</p>
                        </div>
                        <span className={`text-sm ${muted}`}>{follower.time}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* By Path */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold">Followers by Path</h2>
                  </div>
                  <div className="p-4 space-y-4">
                    {paths.map((path, i) => (
                      <div key={i}>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium">{path.title}</span>
                          <span className="text-sm text-purple-600">{path.followers}</span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full bg-purple-500 rounded-full" style={{ width: `${(path.followers / 438) * 100}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
            
            {/* Authority Hub View */}
            {currentView === 'authority-hub' && (
              <>
                <button onClick={() => setCurrentView('dashboard')} className={`flex items-center gap-2 ${muted} hover:text-[#FF6B6B] transition-colors`}>
                  <ArrowLeft className="w-4 h-4" />Back to Dashboard
                </button>
                
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-amber-400 to-yellow-500 flex items-center justify-center">
                    <Crown className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold">Authority Hub</h1>
                    <p className={muted}>Exclusive features for Authority members</p>
                  </div>
                </div>
                
                {/* Authority Stats */}
                <div className={`${card} border rounded-xl p-6 bg-gradient-to-br from-amber-50 to-yellow-50 border-amber-200`}>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="text-center">
                      <p className="text-4xl font-bold text-amber-600">{stats.authorityScore}</p>
                      <p className={muted}>Authority Score</p>
                    </div>
                    <div className="text-center">
                      <p className="text-4xl font-bold">#23</p>
                      <p className={muted}>Global Rank</p>
                    </div>
                    <div className="text-center">
                      <p className="text-4xl font-bold">99.2%</p>
                      <p className={muted}>Percentile</p>
                    </div>
                    <div className="text-center">
                      <p className="text-4xl font-bold text-emerald-600">+2.3</p>
                      <p className={muted}>This Month</p>
                    </div>
                  </div>
                </div>
                
                {/* Exclusive Features */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold">Your Authority Perks</h2>
                  </div>
                  <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      { icon: Star, title: 'Featured Placement', desc: 'Your content gets priority in discovery', active: true },
                      { icon: Award, title: 'Authority Badge', desc: 'Visible on your profile and posts', active: true },
                      { icon: TrendingUp, title: 'Advanced Analytics', desc: 'Deep insights into your audience', active: true },
                      { icon: Users, title: 'Priority Support', desc: 'Direct line to the Quirrely team', active: true },
                      { icon: Zap, title: 'Early Access', desc: 'Try new features before anyone else', active: true },
                      { icon: Crown, title: 'Authority Events', desc: 'Exclusive meetups and workshops', active: false },
                    ].map((perk, i) => (
                      <div key={i} className={`p-4 rounded-lg border ${border} ${perk.active ? '' : 'opacity-50'}`}>
                        <div className="flex items-start gap-3">
                          <div className={`w-10 h-10 rounded-lg ${perk.active ? 'bg-amber-100' : 'bg-gray-100'} flex items-center justify-center`}>
                            <perk.icon className={`w-5 h-5 ${perk.active ? 'text-amber-600' : 'text-gray-400'}`} />
                          </div>
                          <div>
                            <p className="font-medium">{perk.title}</p>
                            <p className={`text-sm ${muted}`}>{perk.desc}</p>
                            {!perk.active && <span className="text-xs text-amber-600">Coming soon</span>}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Recent Achievements */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold">Recent Achievements</h2>
                  </div>
                  <div className={`divide-y ${border}`}>
                    {[
                      { title: 'Reached Top 25', desc: 'You broke into the top 25 Authority Writers globally', time: '2 days ago' },
                      { title: 'Authority Status Achieved', desc: 'Congratulations on reaching Authority tier!', time: '1 week ago' },
                      { title: '90% Authority Score', desc: 'Your score crossed the 90 point threshold', time: '2 weeks ago' },
                    ].map((achievement, i) => (
                      <div key={i} className="p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center">
                          <Trophy className="w-5 h-5 text-amber-600" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium">{achievement.title}</p>
                          <p className={`text-sm ${muted}`}>{achievement.desc}</p>
                        </div>
                        <span className={`text-sm ${muted}`}>{achievement.time}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
            
            {/* Leaderboard View */}
            {currentView === 'leaderboard' && (
              <>
                <button onClick={() => setCurrentView('dashboard')} className={`flex items-center gap-2 ${muted} hover:text-[#FF6B6B] transition-colors`}>
                  <ArrowLeft className="w-4 h-4" />Back to Dashboard
                </button>
                
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                      <Trophy className="w-6 h-6 text-amber-500" />
                      Leaderboard
                    </h1>
                    <p className={muted}>Top Authority Writers & Curators</p>
                  </div>
                  <div className="flex gap-2">
                    <button className={`px-3 py-1.5 rounded-lg text-sm bg-[#FF6B6B] text-white`}>Writers</button>
                    <button className={`px-3 py-1.5 rounded-lg text-sm ${muted} ${hover}`}>Curators</button>
                    <button className={`px-3 py-1.5 rounded-lg text-sm ${muted} ${hover}`}>All</button>
                  </div>
                </div>
                
                {/* Top 3 - Stacks on mobile */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {[
                    { rank: 2, name: 'James Chen', score: 97.8, avatar: 'JC' },
                    { rank: 1, name: 'Sofia Rodriguez', score: 98.9, avatar: 'SR' },
                    { rank: 3, name: 'Michael Park', score: 96.2, avatar: 'MP' },
                  ].sort((a, b) => a.rank - b.rank).map((leader, i) => (
                    <div key={i} className={`${card} border rounded-xl p-4 sm:p-6 text-center ${leader.rank === 1 ? 'ring-2 ring-amber-400 sm:order-first sm:-order-none' : ''} ${leader.rank === 1 ? 'order-first sm:order-none' : ''}`}>
                      <div className="flex sm:flex-col items-center sm:items-center gap-4 sm:gap-0">
                        <div className={`w-12 h-12 sm:w-16 sm:h-16 sm:mx-auto sm:mb-3 rounded-full flex items-center justify-center text-white font-bold text-lg sm:text-xl ${
                          leader.rank === 1 ? 'bg-gradient-to-br from-amber-400 to-yellow-500' :
                          leader.rank === 2 ? 'bg-gradient-to-br from-gray-300 to-gray-400' :
                          'bg-gradient-to-br from-amber-600 to-amber-700'
                        }`}>
                          {leader.avatar}
                        </div>
                        <div className="flex-1 sm:flex-none text-left sm:text-center">
                          <div className="text-xl sm:text-2xl sm:mb-1">{leader.rank === 1 ? '🥇' : leader.rank === 2 ? '🥈' : '🥉'}</div>
                          <p className="font-semibold">{leader.name}</p>
                          <p className="text-amber-600 font-bold">{leader.score}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Full Leaderboard */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`divide-y ${border}`}>
                    {[
                      { rank: 4, name: 'Anna Schmidt', score: 95.8, change: '+2' },
                      { rank: 5, name: 'David Wilson', score: 95.4, change: '-1' },
                      { rank: 6, name: 'Emma Thompson', score: 95.1, change: '+3' },
                      { rank: 23, name: user.name, score: stats.authorityScore, change: '+5', isYou: true },
                      { rank: 24, name: 'Chris Taylor', score: 94.5, change: '-2' },
                      { rank: 25, name: 'Nina Patel', score: 94.2, change: '0' },
                    ].map((person, i) => (
                      <div key={i} className={`p-4 flex items-center gap-4 ${person.isYou ? 'bg-[#FF6B6B]/5' : ''}`}>
                        <span className={`w-8 text-center font-bold ${person.rank <= 3 ? 'text-amber-600' : muted}`}>#{person.rank}</span>
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${person.isYou ? 'bg-gradient-to-br from-amber-400 to-yellow-500' : 'bg-gray-400'}`}>
                          {person.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium">{person.name} {person.isYou && <span className="text-xs text-[#FF6B6B]">(You)</span>}</p>
                        </div>
                        <span className={`text-sm ${parseInt(person.change) > 0 ? 'text-emerald-600' : parseInt(person.change) < 0 ? 'text-red-500' : muted}`}>
                          {parseInt(person.change) > 0 ? '↑' : parseInt(person.change) < 0 ? '↓' : '–'} {Math.abs(parseInt(person.change)) || ''}
                        </span>
                        <span className="font-bold text-amber-600">{person.score}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
            
            {/* Settings View */}
            {currentView === 'settings' && (
              <SettingsView user={user} darkMode={darkMode} card={card} border={border} muted={muted} hover={hover} setCurrentView={setCurrentView} hasVoiceStyle={hasVoiceStyle} isAuthorityTier={isAuthorityTier} formatTier={formatTier} />
            )}
            
            {/* Help View */}
            {currentView === 'help' && (
              <>
                <button onClick={() => setCurrentView('dashboard')} className={`flex items-center gap-2 ${muted} hover:text-[#FF6B6B] transition-colors`}>
                  <ArrowLeft className="w-4 h-4" />Back to Dashboard
                </button>
                
                <div>
                  <h1 className="text-2xl font-bold">Help & Support</h1>
                  <p className={muted}>Get answers and connect with our team</p>
                </div>
                
                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { icon: MessageCircle, title: 'Contact Support', desc: 'Get help from our team', action: 'Email Us' },
                    { icon: BookOpen, title: 'Documentation', desc: 'Learn how to use Quirrely', action: 'View Docs' },
                    { icon: Users, title: 'Community', desc: 'Join our Discord server', action: 'Join Discord' },
                  ].map((item, i) => (
                    <div key={i} className={`${card} border rounded-xl p-6 text-center`}>
                      <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center">
                        <item.icon className="w-6 h-6 text-[#FF6B6B]" />
                      </div>
                      <h3 className="font-semibold mb-1">{item.title}</h3>
                      <p className={`text-sm ${muted} mb-4`}>{item.desc}</p>
                      <button className="px-4 py-2 bg-[#FF6B6B] text-white rounded-lg text-sm hover:bg-[#ff5252]">{item.action}</button>
                    </div>
                  ))}
                </div>
                
                {/* FAQ */}
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}>
                    <h2 className="font-semibold">Frequently Asked Questions</h2>
                  </div>
                  <div className={`divide-y ${border}`}>
                    {[
                      { q: 'How do I upgrade my subscription?', a: 'Go to Settings > Billing and select "Change Plan" to view upgrade options.' },
                      { q: 'What is the Voice + Style addon?', a: 'Voice + Style provides advanced voice analysis including evolution tracking and style recommendations.' },
                      { q: 'How do reading streaks work?', a: 'Read at least one post per day to maintain your streak. Streaks reset at midnight in your local timezone.' },
                      { q: 'Can I have both Writer and Curator tracks?', a: 'Yes! At Pro/Curator level and above, you can add the other track to access both feature sets.' },
                      { q: 'How is Authority Score calculated?', a: 'Authority Score combines factors like content quality, engagement, consistency, and community impact.' },
                      { q: 'How do I cancel my subscription?', a: 'Go to Settings > Billing and select "Cancel Subscription". Your access continues until the billing period ends.' },
                    ].map((faq, i) => (
                      <details key={i} className="group">
                        <summary className={`p-4 cursor-pointer font-medium flex items-center justify-between ${hover}`}>
                          {faq.q}
                          <ChevronRight className={`w-5 h-5 ${muted} group-open:rotate-90 transition-transform`} />
                        </summary>
                        <div className={`px-4 pb-4 text-sm ${muted}`}>{faq.a}</div>
                      </details>
                    ))}
                  </div>
                </div>
                
                {/* Contact */}
                <div className={`${card} border rounded-xl p-6`}>
                  <h2 className="font-semibold mb-4">Still need help?</h2>
                  <p className={`${muted} mb-4`}>Our support team is available Monday-Friday, 9am-6pm EST.</p>
                  <div className="flex gap-4">
                    <button className="px-4 py-2 bg-[#FF6B6B] text-white rounded-lg hover:bg-[#ff5252]">Email support@quirrely.com</button>
                    <button className={`px-4 py-2 rounded-lg border ${border} ${hover}`}>@quirrely on Twitter</button>
                  </div>
                </div>
              </>
            )}
            
            {/* Dashboard View */}
            {currentView === 'dashboard' && (
              <>
            <div>
              <h1 className="text-2xl font-bold">Welcome back, {user.name.split(' ')[0]}! {FLAGS[user.country]}</h1>
              <p className={muted}>{isDualTrack(user) ? "Here's what's happening across your writing and curation" : hasWriterTrack(user) ? "Here's what's happening with your writing" : hasCuratorTrack(user) ? "Here's what's happening with your paths" : "Here's what's happening on Quirrely"}</p>
            </div>
            
            {/* 🟢 QUICK WIN #3: First Analysis Hook - Voice Match */}
            {(user.writerTier === 'free' && user.curatorTier === 'free' && user.daysInSystem <= 7) && (
              <div className={`${card} border-2 border-emerald-400 rounded-xl overflow-hidden bg-gradient-to-br from-emerald-50 to-teal-50`}>
                <div className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                      <Sparkles className="w-7 h-7 text-emerald-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-bold text-emerald-800 mb-1">🎉 Your Voice Analysis Results!</h3>
                      <p className="text-emerald-700 mb-4">Based on your writing sample, here's who you write like:</p>
                      
                      {/* M2 Fix: Horizontal scroll on mobile, grid on desktop */}
                      <div className="flex gap-2 mb-4 overflow-x-auto pb-2 sm:pb-0 sm:grid sm:grid-cols-3 sm:overflow-visible -mx-1 px-1">
                        <div className={`flex-shrink-0 w-[130px] sm:w-auto p-2 sm:p-3 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} border border-emerald-200`}>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xl sm:text-2xl">📚</span>
                            <span className="font-bold text-emerald-600 text-sm sm:text-base">78%</span>
                          </div>
                          <p className="font-semibold text-xs sm:text-sm">Ernest Hemingway</p>
                          <p className={`text-xs ${muted}`}>Assertive, Direct</p>
                        </div>
                        <div className={`flex-shrink-0 w-[130px] sm:w-auto p-2 sm:p-3 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} border border-emerald-200`}>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xl sm:text-2xl">✍️</span>
                            <span className="font-bold text-emerald-600 text-sm sm:text-base">65%</span>
                          </div>
                          <p className="font-semibold text-xs sm:text-sm">George Orwell</p>
                          <p className={`text-xs ${muted}`}>Clear, Purposeful</p>
                        </div>
                        <div className={`flex-shrink-0 w-[130px] sm:w-auto p-2 sm:p-3 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} border border-emerald-200`}>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xl sm:text-2xl">🌟</span>
                            <span className="font-bold text-emerald-600 text-sm sm:text-base">62%</span>
                          </div>
                          <p className="font-semibold text-xs sm:text-sm">Joan Didion</p>
                          <p className={`text-xs ${muted}`}>Observant, Intimate</p>
                        </div>
                      </div>
                      
                      <div className={`p-3 rounded-lg ${darkMode ? 'bg-gray-800/50' : 'bg-white/70'} border border-emerald-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3`}>
                        <div>
                          <p className="font-medium text-sm">🔓 Unlock 10 more author comparisons</p>
                          <p className={`text-xs ${muted}`}>Plus voice evolution tracking & style recommendations</p>
                        </div>
                        <LoadingButton id="first-analysis-upgrade" variant="emerald" className="px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap">
                          <Zap className="w-4 h-4" />
                          Upgrade to Pro
                        </LoadingButton>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* 🟠 P3: Progressive Feature Unlocks (for free users) */}
            {(user.writerTier === 'free' && user.curatorTier === 'free' && user.daysInSystem > 0) && (
              <div className={`${card} border rounded-xl overflow-hidden`}>
                <div className={`p-4 border-b ${border} flex items-center justify-between`}>
                  <h2 className="font-semibold flex items-center gap-2">
                    <Zap className="w-5 h-5 text-purple-600" />
                    Your Feature Journey
                  </h2>
                  <span className={`text-sm ${muted}`}>Day {user.daysInSystem} of 7</span>
                </div>
                <div className="p-4">
                  {/* Progress bar */}
                  <div className="flex items-center gap-2 mb-4">
                    {[1, 2, 3, 4, 5, 6, 7].map((day) => (
                      <div key={day} className="flex-1 flex flex-col items-center">
                        <div className={`w-full h-2 rounded-full ${
                          day <= user.daysInSystem 
                            ? 'bg-purple-500' 
                            : day === user.daysInSystem + 1 
                              ? 'bg-purple-200' 
                              : 'bg-gray-200'
                        }`} />
                        <span className={`text-xs mt-1 ${day <= user.daysInSystem ? 'text-purple-600 font-medium' : muted}`}>
                          Day {day}
                        </span>
                      </div>
                    ))}
                  </div>
                  
                  {/* Unlocked features */}
                  <div className="space-y-3">
                    {/* Day 1: Basic analysis - always unlocked */}
                    <div className={`p-3 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-50'} flex items-center gap-3`}>
                      <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center">
                        <Check className="w-4 h-4 text-emerald-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">Basic Voice Analysis</p>
                        <p className={`text-xs ${muted}`}>Analyze your writing style</p>
                      </div>
                      <span className="text-xs text-emerald-600">✓ Unlocked</span>
                    </div>
                    
                    {/* Day 3: Voice profile */}
                    <div className={`p-3 rounded-lg ${user.daysInSystem >= 3 ? (darkMode ? 'bg-gray-800' : 'bg-gray-50') : 'bg-gray-100 opacity-60'} flex items-center gap-3`}>
                      <div className={`w-8 h-8 rounded-full ${user.daysInSystem >= 3 ? 'bg-emerald-100' : 'bg-gray-200'} flex items-center justify-center`}>
                        {user.daysInSystem >= 3 ? <Check className="w-4 h-4 text-emerald-600" /> : <span className="text-xs">🔒</span>}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">Voice Profile</p>
                        <p className={`text-xs ${muted}`}>See your unique voice dimensions</p>
                      </div>
                      <span className={`text-xs ${user.daysInSystem >= 3 ? 'text-emerald-600' : 'text-purple-600'}`}>
                        {user.daysInSystem >= 3 ? '✓ Unlocked' : 'Day 3'}
                      </span>
                    </div>
                    
                    {/* Day 5: Comparison feature */}
                    <div className={`p-3 rounded-lg ${user.daysInSystem >= 5 ? (darkMode ? 'bg-gray-800' : 'bg-gray-50') : 'bg-gray-100 opacity-60'} flex items-center gap-3`}>
                      <div className={`w-8 h-8 rounded-full ${user.daysInSystem >= 5 ? 'bg-emerald-100' : 'bg-gray-200'} flex items-center justify-center`}>
                        {user.daysInSystem >= 5 ? <Check className="w-4 h-4 text-emerald-600" /> : <span className="text-xs">🔒</span>}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">Author Comparison (3 authors)</p>
                        <p className={`text-xs ${muted}`}>Compare your voice to famous writers</p>
                      </div>
                      <span className={`text-xs ${user.daysInSystem >= 5 ? 'text-emerald-600' : 'text-purple-600'}`}>
                        {user.daysInSystem >= 5 ? '✓ Unlocked' : 'Day 5'}
                      </span>
                    </div>
                    
                    {/* Day 7: History + Upgrade prompt */}
                    <div className={`p-3 rounded-lg border-2 ${user.daysInSystem >= 7 ? 'border-emerald-400 bg-emerald-50' : 'border-purple-400 bg-purple-50'} flex items-center gap-3`}>
                      <div className={`w-8 h-8 rounded-full ${user.daysInSystem >= 7 ? 'bg-emerald-100' : 'bg-purple-100'} flex items-center justify-center`}>
                        {user.daysInSystem >= 7 ? <Check className="w-4 h-4 text-emerald-600" /> : <Zap className="w-4 h-4 text-purple-600" />}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">Analysis History + Upgrade Offer</p>
                        <p className={`text-xs ${muted}`}>Track progress over time + special discount</p>
                      </div>
                      {user.daysInSystem >= 7 ? (
                        <LoadingButton id="claim-discount" variant="emerald" className="px-3 py-1 rounded text-xs font-medium">
                          Claim 20% Off
                        </LoadingButton>
                      ) : (
                        <span className="text-xs text-purple-600 font-medium whitespace-nowrap">Day 7 🎁</span>
                      )}
                    </div>
                  </div>
                  
                  {/* Teaser for Pro */}
                  <div className={`mt-4 p-3 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-100'} border border-dashed ${border}`}>
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                      <div>
                        <p className="font-medium text-sm flex items-center gap-2">
                          <Crown className="w-4 h-4 text-amber-500" />
                          Pro Features
                        </p>
                        <p className={`text-xs ${muted}`}>Unlimited analyses, 10+ authors, voice evolution, history</p>
                      </div>
                      <LoadingButton id="progressive-upgrade" variant="coral" className="px-3 py-1.5 rounded-lg text-xs font-medium">
                        Upgrade Now
                      </LoadingButton>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* 🟡 P2: Smart Notifications */}
            {(hasWriterTrack(user) || hasCuratorTrack(user) || hasVoiceStyle(user)) && (
              <div className="space-y-2">
                {/* Voice Evolution Notification */}
                {hasVoiceStyle(user) && (
                  <div className={`${card} border border-emerald-200 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3`}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                        <Sparkles className="w-5 h-5 text-emerald-600" />
                      </div>
                      <div>
                        <p className="font-medium">Your voice evolved 12% this week! 📈</p>
                        <p className={`text-sm ${muted}`}>Confidence score increased from 75% to 87%</p>
                      </div>
                    </div>
                    <button onClick={() => setCurrentView('voice')} className="px-3 py-1.5 bg-emerald-100 text-emerald-700 rounded-lg text-sm font-medium hover:bg-emerald-200 whitespace-nowrap">
                      View Details
                    </button>
                  </div>
                )}
                
                {/* Social Proof Notification */}
                {hasWriterTrack(user) && !isAuthorityTier(user) && (
                  <div className={`${card} border border-[#FF6B6B]/30 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3`}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center flex-shrink-0">
                        <Users className="w-5 h-5 text-[#FF6B6B]" />
                      </div>
                      <div>
                        <p className="font-medium">3 writers similar to you just upgraded to Featured 🚀</p>
                        <p className={`text-sm ${muted}`}>Get 2x visibility and priority placement</p>
                      </div>
                    </div>
                    <LoadingButton id="explore-featured" variant="coral" className="px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap">
                      Explore Featured
                    </LoadingButton>
                  </div>
                )}
                
                {/* Gamification Notification */}
                {hasWriterTrack(user) && (
                  <div className={`${card} border border-amber-200 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3`}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
                        <Award className="w-5 h-5 text-amber-600" />
                      </div>
                      <div>
                        <p className="font-medium">You're 2 analyses away from "Prolific Writer" badge! 🏆</p>
                        <p className={`text-sm ${muted}`}>Complete 50 voice analyses to unlock</p>
                      </div>
                    </div>
                    <LoadingButton id="badge-analyze" variant="amber" className="px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap">
                      Analyze Now
                    </LoadingButton>
                  </div>
                )}
              </div>
            )}
            
            {/* 🟡 P2: Social Proof Counter (for free/trial users) */}
            {(user.writerTier === 'free' && user.curatorTier === 'free') && (
              <div className={`${card} border rounded-xl p-4`}>
                <div className="flex items-center justify-center gap-8 text-center">
                  <div>
                    <p className="text-2xl font-bold text-[#FF6B6B]">4,271</p>
                    <p className={`text-xs ${muted}`}>writers upgraded this month</p>
                  </div>
                  <div className="w-px h-10 bg-gray-200" />
                  <div>
                    <p className="text-2xl font-bold text-emerald-600">12,847</p>
                    <p className={`text-xs ${muted}`}>analyses completed today</p>
                  </div>
                  <div className="w-px h-10 bg-gray-200" />
                  <div>
                    <p className="text-2xl font-bold text-blue-600">89%</p>
                    <p className={`text-xs ${muted}`}>of {FLAGS[user.country]} writers recommend Pro</p>
                  </div>
                </div>
              </div>
            )}
            
            {/* Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {isAuthorityTier(user) && (
                <div className={`${card} border rounded-xl p-4 bg-gradient-to-br from-amber-50 to-yellow-50 border-amber-200`}>
                  <div className="flex items-start justify-between">
                    <div><p className={`text-sm ${muted}`}>Authority Score</p><p className="text-3xl font-bold text-amber-600 mt-1">{stats.authorityScore}</p><p className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" />+2.3</p></div>
                    <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center"><Crown className="w-5 h-5 text-amber-600" /></div>
                  </div>
                </div>
              )}
              {hasWriterTrack(user) && (<>
                <div className={`${card} border rounded-xl p-4`}>
                  <div className="flex items-start justify-between">
                    <div><p className={`text-sm ${muted}`}>Followers</p><p className="text-3xl font-bold mt-1">{stats.followers.toLocaleString()}</p><p className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" />+89</p></div>
                    <div className="w-10 h-10 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center"><Users className="w-5 h-5 text-[#FF6B6B]" /></div>
                  </div>
                </div>
                <div className={`${card} border rounded-xl p-4`}>
                  <div className="flex items-start justify-between">
                    <div><p className={`text-sm ${muted}`}>Total Reads</p><p className="text-3xl font-bold mt-1">{stats.totalReads.toLocaleString()}</p><p className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" />+15%</p></div>
                    <div className="w-10 h-10 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center"><Eye className="w-5 h-5 text-[#FF6B6B]" /></div>
                  </div>
                </div>
                <div className={`${card} border rounded-xl p-4`}>
                  <div className="flex items-start justify-between">
                    <div><p className={`text-sm ${muted}`}>Posts Written</p><p className="text-3xl font-bold mt-1">{stats.postsWritten}</p><p className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" />+3</p></div>
                    <div className="w-10 h-10 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center"><PenTool className="w-5 h-5 text-[#FF6B6B]" /></div>
                  </div>
                </div>
              </>)}
              {hasCuratorTrack(user) && (<>
                <div className={`${card} border rounded-xl p-4`}>
                  <div className="flex items-start justify-between">
                    <div><p className={`text-sm ${muted}`}>Path Followers</p><p className="text-3xl font-bold mt-1">{stats.pathFollowers.toLocaleString()}</p><p className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" />+12</p></div>
                    <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center"><Users className="w-5 h-5 text-purple-600" /></div>
                  </div>
                </div>
                <div className={`${card} border rounded-xl p-4`}>
                  <div className="flex items-start justify-between">
                    <div><p className={`text-sm ${muted}`}>Paths Created</p><p className="text-3xl font-bold mt-1">{stats.pathsCreated}</p><p className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" />+1</p></div>
                    <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center"><Route className="w-5 h-5 text-purple-600" /></div>
                  </div>
                </div>
              </>)}
              {!isAuthorityTier(user) && (
                <div className={`${card} border rounded-xl p-4`}>
                  <div className="flex items-start justify-between">
                    <div><p className={`text-sm ${muted}`}>Reading Streak</p><p className="text-3xl font-bold mt-1">{stats.readingStreak} days</p><p className="text-xs text-[#FF6B6B] mt-1">🔥 Keep going!</p></div>
                    <div className="w-10 h-10 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center"><Flame className="w-5 h-5 text-[#FF6B6B]" /></div>
                  </div>
                </div>
              )}
            </div>
            
            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {features.voiceProfile && (
                <div className={`lg:col-span-2 ${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border} flex items-center justify-between`}>
                    <h2 className="font-semibold flex items-center gap-2"><Sparkles className="w-5 h-5 text-emerald-500" />Your Writing Voice {features.voiceEvolution && <span className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full">✨ Evolution</span>}</h2>
                    <button onClick={() => setCurrentView('voice')} className="text-sm text-[#FF6B6B] hover:underline">View Details</button>
                  </div>
                  <div className={`p-6 ${darkMode ? 'bg-gradient-to-br from-emerald-950/40 to-teal-950/40' : 'bg-gradient-to-br from-emerald-50 to-teal-50'}`}>
                    <div className="flex flex-col md:flex-row gap-6">
                      <div className={`w-40 h-40 mx-auto md:mx-0 rounded-full border-4 border-emerald-500/30 flex items-center justify-center ${darkMode ? 'bg-emerald-900/30' : 'bg-emerald-100/50'}`}>
                        <div className="text-center"><p className="text-3xl font-bold text-emerald-500">{voiceProfile.confidence}%</p><p className="text-xs text-emerald-500">Confidence</p></div>
                      </div>
                      <div className="flex-1">
                        <h3 className="text-2xl font-bold text-emerald-500 mb-2">{voiceProfile.primary} {voiceProfile.secondary}</h3>
                        <p className={`${muted} mb-4`}>You write with confidence and narrative flair.</p>
                        <div className="flex flex-wrap gap-2">{voiceProfile.tokens.map((t, i) => <span key={i} className={`px-3 py-1 rounded-full text-sm ${darkMode ? 'bg-emerald-900/50 text-emerald-300' : 'bg-emerald-100 text-emerald-800'}`}>{t}</span>)}</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div className={`space-y-6 ${!features.voiceProfile ? 'lg:col-span-2' : ''}`}>
                {isFeaturedTier(user) && (
                  <div className={`${card} border rounded-xl overflow-hidden ${darkMode ? 'bg-gradient-to-br from-amber-950/30 to-yellow-950/30 border-amber-800' : 'bg-gradient-to-br from-amber-50 to-yellow-50 border-amber-200'}`}>
                    <div className={`p-4 border-b ${darkMode ? 'border-amber-800' : 'border-amber-200'}`}><h2 className="font-semibold">👑 Authority Status</h2></div>
                    <div className="p-4 space-y-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-12 h-12 rounded-full ${darkMode ? 'bg-amber-900/50' : 'bg-amber-100'} flex items-center justify-center`}><Crown className="w-6 h-6 text-amber-500" /></div>
                        <div><p className="font-bold text-amber-500">{isAuthorityTier(user) ? (TIER_LEVELS[user.writerTier] >= TIER_LEVELS[user.curatorTier] ? 'Authority Writer' : 'Authority Curator') : 'Featured'}</p><p className={`text-sm ${muted}`}>{isDualTrack(user) ? 'Dual Track' : user.primaryTrack === 'writer' ? 'Writer Track' : 'Curator Track'}</p></div>
                      </div>
                      {isAuthorityTier(user) && (<>
                        <div><div className="flex justify-between text-sm mb-1"><span className={muted}>Score</span><span className="font-semibold text-amber-500">{stats.authorityScore}/100</span></div><div className={`h-2 ${darkMode ? 'bg-amber-900/50' : 'bg-amber-200'} rounded-full overflow-hidden`}><div className="h-full bg-gradient-to-r from-amber-400 to-yellow-500 rounded-full" style={{ width: `${stats.authorityScore}%` }} /></div></div>
                        <div className="flex gap-6"><div><p className="text-2xl font-bold">#23</p><p className={`text-xs ${muted}`}>Rank</p></div><div><p className="text-2xl font-bold">99.2%</p><p className={`text-xs ${muted}`}>Percentile</p></div></div>
                      </>)}
                    </div>
                  </div>
                )}
                
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border}`}><h2 className="font-semibold">Recent Activity</h2></div>
                  <div className={`divide-y ${border}`}>
                    {activities.map((a, i) => (
                      <button key={i} className={`w-full p-3 flex gap-3 text-left ${hover}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${a.type === 'authority' ? 'bg-amber-100 text-amber-600' : a.type === 'badge' ? 'bg-purple-100 text-purple-600' : a.type === 'path' ? 'bg-indigo-100 text-indigo-600' : a.type === 'voice' ? 'bg-emerald-100 text-emerald-600' : 'bg-[#FF6B6B]/10 text-[#FF6B6B]'}`}><a.icon className="w-4 h-4" /></div>
                        <div className="flex-1 min-w-0"><p className="text-sm font-medium truncate">{a.title}</p><p className={`text-xs ${muted}`}>Recently</p></div>
                        <ChevronRight className={`w-4 h-4 ${muted}`} />
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Track Sections */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {features.myWriting && (
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border} flex justify-between`}><h2 className="font-semibold">My Writing</h2><button className="text-sm text-[#FF6B6B] hover:underline">View all</button></div>
                  <div className={`divide-y ${border}`}>
                    {posts.map((p, i) => (
                      <button key={i} className={`w-full p-4 flex items-center gap-4 text-left ${hover}`}>
                        <div className="w-10 h-10 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center">{p.featured ? <Star className="w-5 h-5 text-[#FF6B6B]" /> : <FileText className="w-5 h-5 text-[#FF6B6B]" />}</div>
                        <div className="flex-1 min-w-0"><div className="flex items-center gap-2"><p className="font-medium truncate">{p.title}</p>{p.featured && <span className="px-1.5 py-0.5 text-xs bg-amber-100 text-amber-800 rounded">Featured</span>}</div><p className={`text-sm ${muted}`}>{p.reads.toLocaleString()} reads</p></div>
                        <ChevronRight className={`w-5 h-5 ${muted}`} />
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {features.readingPaths && (
                <div className={`${card} border rounded-xl overflow-hidden`}>
                  <div className={`p-4 border-b ${border} flex justify-between`}><h2 className="font-semibold">Your Reading Paths</h2><button className="text-sm text-[#FF6B6B] hover:underline">View all</button></div>
                  <div className={`divide-y ${border}`}>
                    {paths.map((p, i) => (
                      <button key={i} className={`w-full p-4 flex items-center gap-4 text-left ${hover}`}>
                        <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center"><Route className="w-5 h-5 text-purple-600" /></div>
                        <div className="flex-1 min-w-0"><p className="font-medium truncate">{p.title}</p><p className={`text-sm ${muted}`}>{p.followers} followers</p></div>
                        <span className="text-sm text-emerald-600 flex items-center gap-1"><TrendingUp className="w-4 h-4" />+12</span>
                        <ChevronRight className={`w-5 h-5 ${muted}`} />
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <p className={`text-center text-sm ${muted} py-4`}>
              Quirrely v3.0.0 "Knight of Wands" • {isDualTrack(user) ? 'Dual Track' : hasWriterTrack(user) ? 'Writer Track' : hasCuratorTrack(user) ? 'Curator Track' : 'Free'} • Day {user.daysInSystem} • {FLAGS[user.country]} {user.country}
            </p>
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default ComposableDashboard;
