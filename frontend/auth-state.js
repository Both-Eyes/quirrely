/**
 * QUIRRELY AUTH STATE MANAGER
 * ===========================
 * Shared authentication and session state across all screens.
 * 
 * Usage: Include this script in every page, then call:
 *   - AuthState.init() on page load
 *   - AuthState.isLoggedIn() to check auth
 *   - AuthState.getUser() to get user data
 *   - AuthState.requireAuth() to guard protected pages
 *   - AuthState.redirectIfLoggedIn() for landing page
 */

const AuthState = (function() {
  'use strict';
  
  const STORAGE_KEY = 'quirrely_session';
  const USER_KEY = 'quirrely_user';
  
  // ═══════════════════════════════════════════════════════════════
  // CORE STATE
  // ═══════════════════════════════════════════════════════════════
  
  function getSession() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      if (!data) return null;
      
      const session = JSON.parse(data);
      
      // Check if session expired
      if (session.expiresAt && new Date(session.expiresAt) < new Date()) {
        clearSession();
        return null;
      }
      
      return session;
    } catch (e) {
      return null;
    }
  }
  
  function getUser() {
    try {
      const data = localStorage.getItem(USER_KEY);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      return null;
    }
  }
  
  function setSession(sessionData, userData) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      ...sessionData,
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // 30 days
    }));
    
    if (userData) {
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
    }
  }
  
  function clearSession() {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(USER_KEY);
  }
  
  function isLoggedIn() {
    return getSession() !== null && getUser() !== null;
  }
  
  function isPro() {
    const user = getUser();
    return user && user.subscription && user.subscription.status === 'active';
  }
  
  // ═══════════════════════════════════════════════════════════════
  // PAGE GUARDS
  // ═══════════════════════════════════════════════════════════════
  
  /**
   * Redirect to dashboard if user is logged in
   * Use on: Landing page, login, signup
   */
  function redirectIfLoggedIn(destination) {
    if (isLoggedIn()) {
      if (!destination) {
        const user = getUser();
        destination = (user && user.share_slug) ? '/user/' + user.share_slug : '/dashboard';
      }
      window.location.href = destination;
      return true;
    }
    return false;
  }
  
  /**
   * Require authentication, redirect to login if not
   * Use on: Dashboard, settings, export, etc.
   */
  function requireAuth(loginUrl = '/auth/login.html') {
    if (!isLoggedIn()) {
      // Save intended destination
      sessionStorage.setItem('quirrely_redirect', window.location.href);
      window.location.href = loginUrl;
      return false;
    }
    return true;
  }
  
  /**
   * Require Pro subscription
   * Use on: Pro-only features
   */
  function requirePro(upgradeUrl = '/payment/upgrade.html') {
    if (!requireAuth()) return false;
    
    if (!isPro()) {
      window.location.href = upgradeUrl;
      return false;
    }
    return true;
  }
  
  // ═══════════════════════════════════════════════════════════════
  // UI HELPERS
  // ═══════════════════════════════════════════════════════════════
  
  /**
   * Update navigation based on auth state
   */
  function updateNav() {
    const user = getUser();
    const loggedIn = isLoggedIn();
    
    // Find nav containers
    const authNav = document.getElementById('auth-nav');
    const userNav = document.getElementById('user-nav');
    
    if (authNav && userNav) {
      if (loggedIn) {
        authNav.style.display = 'none';
        userNav.style.display = 'flex';
        
        // Update user info
        const userName = userNav.querySelector('.user-name');
        const userAvatar = userNav.querySelector('.user-avatar');
        
        if (userName && user) {
          userName.textContent = user.name || user.email.split('@')[0];
        }
        if (userAvatar && user) {
          userAvatar.textContent = (user.name || user.email).substring(0, 2).toUpperCase();
        }
      } else {
        authNav.style.display = 'flex';
        userNav.style.display = 'none';
      }
    }
  }
  
  /**
   * Get redirect URL after login
   */
  function getPostLoginRedirect() {
    const saved = sessionStorage.getItem('quirrely_redirect');
    if (saved) return saved;
    const user = getUser();
    return (user && user.share_slug) ? '/user/' + user.share_slug : '/dashboard';
  }
  
  function clearPostLoginRedirect() {
    sessionStorage.removeItem('quirrely_redirect');
  }
  
  // ═══════════════════════════════════════════════════════════════
  // INIT
  // ═══════════════════════════════════════════════════════════════
  
  function getDashboardUrl() {
    const user = getUser();
    return (user && user.share_slug) ? '/user/' + user.share_slug : '/dashboard';
  }

  function rewriteDashboardLinks() {
    if (!isLoggedIn()) return;
    const url = getDashboardUrl();
    if (url === '/dashboard') return;
    document.querySelectorAll('a[href="/dashboard"]').forEach(function(a) {
      a.href = url;
    });
  }

  function init() {
    // Update nav on every page
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function() { updateNav(); rewriteDashboardLinks(); });
    } else {
      updateNav();
      rewriteDashboardLinks();
    }
  }
  
  // ═══════════════════════════════════════════════════════════════
  // MOCK AUTH (for demo - replace with real API)
  // ═══════════════════════════════════════════════════════════════
  
  function login(email, password) {
    // Mock login - replace with real API call
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email && password) {
          const userData = {
            id: 'usr_' + Math.random().toString(36).substr(2, 9),
            email: email,
            name: email.split('@')[0],
            country: 'CA',
            profile: {
              type: 'POETIC',
              stance: 'OPEN',
              testsCompleted: 3
            },
            subscription: {
              status: 'active',
              plan: 'monthly',
              since: '2026-01-15'
            }
          };
          
          setSession({ token: 'mock_token_' + Date.now() }, userData);
          resolve(userData);
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 500);
    });
  }
  
  function signup(email, password, name) {
    // Mock signup - replace with real API call
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email && password) {
          const userData = {
            id: 'usr_' + Math.random().toString(36).substr(2, 9),
            email: email,
            name: name || email.split('@')[0],
            country: 'CA',
            profile: null,
            subscription: null
          };
          
          setSession({ token: 'mock_token_' + Date.now() }, userData);
          resolve(userData);
        } else {
          reject(new Error('Invalid data'));
        }
      }, 500);
    });
  }
  
  function logout() {
    clearSession();
    window.location.href = '/';
  }
  
  // ═══════════════════════════════════════════════════════════════
  // PUBLIC API
  // ═══════════════════════════════════════════════════════════════
  
  return {
    init,
    isLoggedIn,
    isPro,
    getUser,
    getSession,
    setSession,
    clearSession,
    redirectIfLoggedIn,
    requireAuth,
    requirePro,
    updateNav,
    getPostLoginRedirect,
    clearPostLoginRedirect,
    getDashboardUrl,
    rewriteDashboardLinks,
    login,
    signup,
    logout
  };
})();

// Auto-init
AuthState.init();
