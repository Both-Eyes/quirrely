import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userApi } from '@/api';
import { useToast } from '@/components/ui/Toast';
import { UserProfile, UserSettings, UserStats, VoiceProfile, Activity } from '@/types';

// Query keys
export const userKeys = {
  all: ['user'] as const,
  profile: () => [...userKeys.all, 'profile'] as const,
  settings: () => [...userKeys.all, 'settings'] as const,
  stats: () => [...userKeys.all, 'stats'] as const,
  voice: () => [...userKeys.all, 'voice'] as const,
  activity: (limit?: number) => [...userKeys.all, 'activity', limit] as const,
};

// Fetch user profile
export const useUserProfile = () => {
  return useQuery({
    queryKey: userKeys.profile(),
    queryFn: () => userApi.getProfile(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// Fetch user settings
export const useUserSettings = () => {
  return useQuery({
    queryKey: userKeys.settings(),
    queryFn: () => userApi.getSettings(),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
};

// Update user settings
export const useUpdateSettings = () => {
  const queryClient = useQueryClient();
  const { success, error } = useToast();

  return useMutation({
    mutationFn: (data: Partial<UserSettings>) => userApi.updateSettings(data),
    onSuccess: (data) => {
      queryClient.setQueryData(userKeys.settings(), data);
      success('Settings saved', 'Your settings have been updated.');
    },
    onError: (err: Error) => {
      error('Failed to save settings', err.message);
    },
  });
};

// Update user profile
export const useUpdateProfile = () => {
  const queryClient = useQueryClient();
  const { success, error } = useToast();

  return useMutation({
    mutationFn: (data: Partial<UserProfile>) => userApi.updateProfile(data),
    onSuccess: (data) => {
      queryClient.setQueryData(userKeys.profile(), data);
      success('Profile updated', 'Your profile has been saved.');
    },
    onError: (err: Error) => {
      error('Failed to update profile', err.message);
    },
  });
};

// Fetch user stats
export const useUserStats = () => {
  return useQuery({
    queryKey: userKeys.stats(),
    queryFn: () => userApi.getStats(),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
};

// Fetch voice profile
export const useVoiceProfile = () => {
  return useQuery({
    queryKey: userKeys.voice(),
    queryFn: () => userApi.getVoiceProfile(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// Fetch activity feed
export const useActivity = (limit: number = 10) => {
  return useQuery({
    queryKey: userKeys.activity(limit),
    queryFn: () => userApi.getActivity(limit),
    staleTime: 1000 * 60 * 1, // 1 minute
  });
};

// Upload avatar
export const useUploadAvatar = () => {
  const queryClient = useQueryClient();
  const { success, error } = useToast();

  return useMutation({
    mutationFn: (file: File) => userApi.uploadAvatar(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.profile() });
      success('Avatar uploaded', 'Your new avatar has been saved.');
    },
    onError: (err: Error) => {
      error('Upload failed', err.message);
    },
  });
};
