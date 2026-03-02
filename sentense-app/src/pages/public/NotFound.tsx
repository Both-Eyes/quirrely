import { useNavigate } from 'react-router-dom';
import { Home, ArrowLeft, Search } from 'lucide-react';
import { Button } from '@/components/ui';

export const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
      <div className="text-center max-w-md">
        {/* 404 Illustration */}
        <div className="mb-8">
          <div className="text-9xl font-bold text-gradient mb-4">404</div>
          <div className="w-32 h-32 mx-auto">
            <svg viewBox="0 0 100 120" className="w-full h-full opacity-50">
              <path d="M58 112 Q85 98, 94 62 Q100 26, 74 8 Q50 -8, 42 22 Q38 44, 54 60 Q70 78, 62 100 Q58 110, 58 112" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
              <ellipse cx="40" cy="98" rx="22" ry="26" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
              <ellipse cx="40" cy="50" rx="22" ry="20" fill="#FFFEF9" stroke="#E0DBD5" strokeWidth="1.4"/>
              {/* Confused eyes */}
              <ellipse cx="32" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>
              <ellipse cx="48" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>
              <circle cx="33" cy="46.5" r="2" fill="#FFF"/>
              <circle cx="49" cy="46.5" r="2" fill="#FFF"/>
              {/* Question mark instead of beak */}
              <text x="40" y="65" textAnchor="middle" fill="#FF6B6B" fontSize="12" fontWeight="bold">?</text>
            </svg>
          </div>
        </div>

        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Page not found
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8">
          The page you're looking for doesn't exist or has been moved.
          Let's get you back on track.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button
            variant="outline"
            leftIcon={<ArrowLeft className="h-4 w-4" />}
            onClick={() => navigate(-1)}
          >
            Go Back
          </Button>
          <Button
            leftIcon={<Home className="h-4 w-4" />}
            onClick={() => navigate('/dashboard')}
          >
            Go to Dashboard
          </Button>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-800">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Looking for something specific?
          </p>
          <div className="flex justify-center gap-4 text-sm">
            <a href="/reader/discover" className="text-coral-500 hover:text-coral-600">
              Discover Posts
            </a>
            <a href="/writer/posts" className="text-coral-500 hover:text-coral-600">
              My Writing
            </a>
            <a href="/help" className="text-coral-500 hover:text-coral-600">
              Help Center
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
