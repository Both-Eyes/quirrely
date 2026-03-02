import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@/api';
import { useAuthStore } from '@/stores';
import { useToast } from '@/components/ui/Toast';
import { LoginCredentials, SignupData } from '@/types';

export const useLogin = () => {
  const navigate = useNavigate();
  const { setUser } = useAuthStore();
  const { success, error } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: LoginCredentials) => authApi.login(credentials),
    onSuccess: (data) => {
      setUser(data.user);
      queryClient.invalidateQueries({ queryKey: ['user'] });
      success('Welcome back!', 'You have successfully logged in.');
      navigate('/dashboard');
    },
    onError: (err: Error) => {
      error('Login failed', err.message || 'Please check your credentials.');
    },
  });
};

export const useSignup = () => {
  const navigate = useNavigate();
  const { setUser } = useAuthStore();
  const { success, error } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SignupData) => authApi.signup(data),
    onSuccess: (data) => {
      setUser(data.user);
      queryClient.invalidateQueries({ queryKey: ['user'] });
      success('Welcome to Quirrely!', 'Your account has been created.');
      navigate('/dashboard');
    },
    onError: (err: Error) => {
      error('Signup failed', err.message || 'Please try again.');
    },
  });
};

export const useLogout = () => {
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  const { success } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      logout();
      queryClient.clear();
      success('Signed out', 'You have been logged out.');
      navigate('/login');
    },
  });
};
