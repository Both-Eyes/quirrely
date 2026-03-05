import { Link } from 'react-router-dom';
import { Heart } from 'lucide-react';

interface FooterProps {
  variant?: 'minimal' | 'full';
}

export const Footer = ({ variant = 'minimal' }: FooterProps) => {
  const currentYear = new Date().getFullYear();

  if (variant === 'minimal') {
    return (
      <footer className="py-6 px-4 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              © {currentYear} Quirrely. All rights reserved.
            </p>
            <nav className="flex items-center gap-6">
              <Link
                to="/privacy"
                className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors"
              >
                Privacy
              </Link>
              <Link
                to="/terms"
                className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors"
              >
                Terms
              </Link>
              <Link
                to="/help"
                className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors"
              >
                Help
              </Link>
            </nav>
          </div>
        </div>
      </footer>
    );
  }

  // Full footer for public pages
  return (
    <footer className="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
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
              <span className="text-lg font-bold text-gray-900 dark:text-white">Quirrely</span>
            </Link>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Discover your unique writing voice with AI-powered analysis.
            </p>
            <p className="text-sm text-gray-400 dark:text-gray-500 flex items-center gap-1">
              Made with <Heart className="h-4 w-4 text-coral-500 fill-coral-500" /> for writers
            </p>
          </div>

          {/* Product */}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Product</h3>
            <ul className="space-y-3">
              <li>
                <Link to="/features" className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link to="/pricing" className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link to="/voice-analysis" className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors">
                  Voice Analysis
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Support</h3>
            <ul className="space-y-3">
              <li>
                <Link to="/help" className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors">
                  Help Center
                </Link>
              </li>
              <li>
                <a href="mailto:support@quirrely.com" className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors">
                  Contact Us
                </a>
              </li>
              <li>
                <Link to="/status" className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors">
                  Status
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Legal</h3>
            <ul className="space-y-3">
              <li>
                <Link to="/privacy" className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link to="/cookies" className="text-sm text-gray-500 dark:text-gray-400 hover:text-coral-500 dark:hover:text-coral-400 transition-colors">
                  Cookie Policy
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-800">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              © {currentYear} Quirrely. All rights reserved.
            </p>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400 dark:text-gray-500">
                Available in 🍁 CA · 🇬🇧 GB · 🇦🇺 AU · 🇳🇿 NZ
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
