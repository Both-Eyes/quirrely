import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import { Button, Input, Card } from '@/components/ui';
import { useToast } from '@/components/ui/Toast';

const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email'),
});

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

export const ForgotPassword = () => {
  const { success, error: showError } = useToast();
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues,
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true);
    try {
      // API call would go here
      // await api.auth.forgotPassword(data.email);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setIsSubmitted(true);
      success('Email sent', 'Check your inbox for password reset instructions.');
    } catch (err) {
      showError('Request failed', 'Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <Card padding="lg" className="shadow-xl">
        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mb-6">
            <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Check your email
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            We've sent password reset instructions to{' '}
            <span className="font-medium text-gray-900 dark:text-white">
              {getValues('email')}
            </span>
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
            Didn't receive the email? Check your spam folder or{' '}
            <button
              onClick={() => setIsSubmitted(false)}
              className="text-coral-500 hover:text-coral-600 font-medium"
            >
              try again
            </button>
          </p>
          <Link to="/login">
            <Button variant="outline" leftIcon={<ArrowLeft className="h-4 w-4" />}>
              Back to login
            </Button>
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <Card padding="lg" className="shadow-xl">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Forgot your password?
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          No worries! Enter your email and we'll send you reset instructions.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <Input
          label="Email address"
          type="email"
          placeholder="you@example.com"
          leftIcon={<Mail className="h-5 w-5" />}
          error={errors.email?.message}
          {...register('email')}
        />

        <Button
          type="submit"
          className="w-full"
          size="lg"
          isLoading={isLoading}
        >
          Send reset instructions
        </Button>
      </form>

      <p className="mt-8 text-center text-sm text-gray-600 dark:text-gray-400">
        Remember your password?{' '}
        <Link to="/login" className="text-coral-500 hover:text-coral-600 font-medium">
          Back to login
        </Link>
      </p>
    </Card>
  );
};
