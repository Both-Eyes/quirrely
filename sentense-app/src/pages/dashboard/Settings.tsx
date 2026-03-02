import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { User, Bell, Moon, Sun, Globe, Shield, Trash2, Camera } from 'lucide-react';
import { useAuthStore, useUIStore } from '@/stores';
import { useUserSettings, useUpdateSettings, useUpdateProfile, useUploadAvatar } from '@/hooks';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Avatar, Badge } from '@/components/ui';
import { useToast } from '@/components/ui/Toast';

const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  handle: z.string().min(3, 'Handle must be at least 3 characters').regex(/^[a-z0-9_]+$/, 'Handle can only contain lowercase letters, numbers, and underscores'),
  bio: z.string().max(160, 'Bio must be 160 characters or less').optional(),
  website: z.string().url('Please enter a valid URL').optional().or(z.literal('')),
});

type ProfileFormData = z.infer<typeof profileSchema>;

const countries = [
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' },
  { code: 'NZ', name: 'New Zealand', flag: '🇳🇿' },
];

export const Settings = () => {
  const { user } = useAuthStore();
  const { theme, setTheme } = useUIStore();
  const { success } = useToast();
  
  const { data: settings } = useUserSettings();
  const updateSettings = useUpdateSettings();
  const updateProfile = useUpdateProfile();
  const uploadAvatar = useUploadAvatar();

  const [activeTab, setActiveTab] = useState<'profile' | 'preferences' | 'notifications' | 'privacy'>('profile');

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: user?.name || '',
      handle: user?.handle || '',
      bio: '',
      website: '',
    },
  });

  const onProfileSubmit = async (data: ProfileFormData) => {
    await updateProfile.mutateAsync(data);
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadAvatar.mutate(file);
    }
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
    success('Theme updated', `Theme set to ${newTheme}`);
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: <User className="h-4 w-4" /> },
    { id: 'preferences', label: 'Preferences', icon: <Globe className="h-4 w-4" /> },
    { id: 'notifications', label: 'Notifications', icon: <Bell className="h-4 w-4" /> },
    { id: 'privacy', label: 'Privacy', icon: <Shield className="h-4 w-4" /> },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-800">
        <nav className="flex gap-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex items-center gap-2 pb-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-coral-500 text-coral-500'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Avatar Section */}
          <Card>
            <CardHeader>
              <CardTitle>Profile Photo</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center">
                <div className="relative">
                  <Avatar
                    name={user?.name || ''}
                    src={user?.avatarUrl}
                    size="xl"
                    border
                    borderColor={user?.tier === 'authority_curator' ? 'gold' : 'default'}
                  />
                  <label className="absolute bottom-0 right-0 p-2 bg-coral-500 rounded-full cursor-pointer hover:bg-coral-600 transition-colors">
                    <Camera className="h-4 w-4 text-white" />
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarChange}
                      className="hidden"
                    />
                  </label>
                </div>
                <p className="mt-3 text-sm text-gray-500 dark:text-gray-400 text-center">
                  Click the camera icon to upload a new photo
                </p>
                {user?.tier && (
                  <Badge
                    variant={user.tier === 'authority_curator' ? 'gold' : 'primary'}
                    className="mt-3"
                  >
                    {user.tier === 'authority_curator' && '👑 '}
                    {user.tierDisplay || user.tier}
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Profile Form */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onProfileSubmit)} className="space-y-5">
                <Input
                  label="Full Name"
                  {...register('name')}
                  error={errors.name?.message}
                />
                <Input
                  label="Handle"
                  leftIcon={<span className="text-gray-400">@</span>}
                  {...register('handle')}
                  error={errors.handle?.message}
                  hint="Your unique username on Quirrely"
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                    Bio
                  </label>
                  <textarea
                    {...register('bio')}
                    rows={3}
                    className="block w-full px-4 py-2.5 text-sm rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500"
                    placeholder="Tell us about yourself..."
                  />
                  {errors.bio && (
                    <p className="mt-1.5 text-sm text-red-500">{errors.bio.message}</p>
                  )}
                </div>
                <Input
                  label="Website"
                  type="url"
                  placeholder="https://yoursite.com"
                  {...register('website')}
                  error={errors.website?.message}
                />
                <div className="flex justify-end">
                  <Button
                    type="submit"
                    disabled={!isDirty}
                    isLoading={updateProfile.isPending}
                  >
                    Save Changes
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Preferences Tab */}
      {activeTab === 'preferences' && (
        <div className="space-y-6">
          {/* Theme */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {theme === 'dark' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
                Appearance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Choose how Quirrely looks for you
                </p>
                <div className="flex gap-3">
                  {(['light', 'dark', 'system'] as const).map((t) => (
                    <button
                      key={t}
                      onClick={() => handleThemeChange(t)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-colors ${
                        theme === t
                          ? 'border-coral-500 bg-coral-50 dark:bg-coral-950/30 text-coral-600'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                    >
                      {t === 'light' && <Sun className="h-4 w-4" />}
                      {t === 'dark' && <Moon className="h-4 w-4" />}
                      {t === 'system' && <Globe className="h-4 w-4" />}
                      <span className="capitalize">{t}</span>
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Country */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Region
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Your region affects content recommendations and community features
                </p>
                <select className="block w-full max-w-xs px-4 py-2.5 text-sm rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500">
                  {countries.map((country) => (
                    <option key={country.code} value={country.code}>
                      {country.flag} {country.name}
                    </option>
                  ))}
                </select>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <Card>
          <CardHeader>
            <CardTitle>Email Notifications</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { id: 'followers', label: 'New followers', description: 'When someone follows you or your paths' },
                { id: 'features', label: 'Featured content', description: 'When your content is featured' },
                { id: 'weekly', label: 'Weekly digest', description: 'A summary of your activity and recommendations' },
                { id: 'updates', label: 'Product updates', description: 'New features and improvements' },
              ].map((item) => (
                <label key={item.id} className="flex items-start gap-4 p-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="mt-1 rounded border-gray-300 text-coral-500 focus:ring-coral-500"
                  />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{item.label}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{item.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Privacy Tab */}
      {activeTab === 'privacy' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile Visibility</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <label className="flex items-start gap-4 p-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="mt-1 rounded border-gray-300 text-coral-500 focus:ring-coral-500"
                  />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Public profile</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Allow others to see your profile and writing</p>
                  </div>
                </label>
                <label className="flex items-start gap-4 p-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="mt-1 rounded border-gray-300 text-coral-500 focus:ring-coral-500"
                  />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Show on leaderboard</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Appear in community rankings</p>
                  </div>
                </label>
              </div>
            </CardContent>
          </Card>

          {/* Danger Zone */}
          <Card className="border-red-200 dark:border-red-900/50">
            <CardHeader>
              <CardTitle className="text-red-600 dark:text-red-400 flex items-center gap-2">
                <Trash2 className="h-5 w-5" />
                Danger Zone
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Once you delete your account, there is no going back. Please be certain.
                </p>
                <Button variant="danger">
                  Delete Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
