import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export const DashboardLayout = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Skip to main content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-coral-500 focus:text-white focus:rounded-lg focus:outline-none"
      >
        Skip to main content
      </a>
      <Header variant="dashboard" />
      <div className="flex">
        <Sidebar />
        <main id="main-content" className="flex-1 p-4 lg:p-6 overflow-auto">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
