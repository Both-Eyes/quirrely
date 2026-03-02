import { Outlet, Link } from 'react-router-dom';
import { Footer } from './Footer';

export const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-coral-50 via-white to-amber-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 flex flex-col">
      {/* Skip to main content link for accessibility */}
      <a
        href="#auth-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-coral-500 focus:text-white focus:rounded-lg focus:outline-none"
      >
        Skip to main content
      </a>
      {/* Header */}
      <header className="p-6">
        <Link to="/" className="flex items-center gap-3">
          <svg viewBox="0 0 100 120" width="36" height="43">
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
          <span className="text-xl font-bold text-gray-900 dark:text-white">Quirrely</span>
        </Link>
      </header>

      {/* Main content */}
      <main id="auth-content" className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </main>

      {/* Footer with proper dark mode */}
      <Footer variant="minimal" />
    </div>
  );
};
