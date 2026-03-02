/**
 * QUIRRELY BROWSER COMPATIBILITY JS v1.0
 * ═══════════════════════════════════════
 * Runtime cross-browser fixes. Load before body content (inline or defer).
 *
 * Handles:
 * - iOS 100vh viewport bug (--vh custom property)
 * - Safari CSS feature detection
 * - Touch event normalisation
 * - localStorage availability check
 * - Passive event listener support check
 * - IntersectionObserver polyfill detection
 * - Performance-safe resize debounce
 */

(function () {
  'use strict';

  // ─── iOS VIEWPORT HEIGHT FIX ─────────────────────────────────────────────
  // iOS Safari 100vh includes browser chrome. Override with JS-measured value.

  function setVH () {
    var vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', vh + 'px');
  }

  setVH();

  var _resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(_resizeTimer);
    _resizeTimer = setTimeout(setVH, 100);
  }, { passive: true });

  window.addEventListener('orientationchange', function () {
    setTimeout(setVH, 200); // Extra delay for orientation settle
  }, { passive: true });


  // ─── FEATURE DETECTION ───────────────────────────────────────────────────

  var html = document.documentElement;

  // CSS custom properties
  if (window.CSS && window.CSS.supports && window.CSS.supports('--a', '0')) {
    html.classList.add('css-vars');
  } else {
    html.classList.add('no-css-vars');
    console.warn('[compat] CSS custom properties not supported — IE/legacy browser?');
  }

  // CSS Grid
  if (window.CSS && window.CSS.supports && window.CSS.supports('display', 'grid')) {
    html.classList.add('css-grid');
  } else {
    html.classList.add('no-css-grid');
  }

  // CSS gap (flex gap) — Safari 14.0 doesn't support it
  if (window.CSS && window.CSS.supports && window.CSS.supports('gap', '1px')) {
    html.classList.add('flex-gap');
  } else {
    html.classList.add('no-flex-gap');
  }

  // Touch device
  if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
    html.classList.add('touch');
    html.classList.remove('no-touch');
  } else {
    html.classList.add('no-touch');
  }

  // Pointer coarse (phone/tablet finger input)
  if (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) {
    html.classList.add('pointer-coarse');
  }

  // Standalone (PWA / home screen)
  if (window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches) {
    html.classList.add('standalone');
  }

  // iOS Safari specifically
  var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  if (isIOS) {
    html.classList.add('ios');
    // iOS Safari-specific: prevent rubber-band scroll on body
    document.addEventListener('touchmove', function (e) {
      if (e.target === document.body) {
        e.preventDefault();
      }
    }, { passive: false });
  }

  // Android Chrome
  var isAndroid = /Android/.test(navigator.userAgent);
  if (isAndroid) {
    html.classList.add('android');
  }

  // macOS Safari (not iOS)
  var isMacSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
  if (isMacSafari && !isIOS) {
    html.classList.add('safari-desktop');
  }


  // ─── PASSIVE EVENT SUPPORT ───────────────────────────────────────────────
  // Detect passive event listener support (Chrome 51+ Safari 10+)

  var passiveSupported = false;
  try {
    var opts = Object.defineProperty({}, 'passive', {
      get: function () { passiveSupported = true; return false; }
    });
    window.addEventListener('testPassive', null, opts);
    window.removeEventListener('testPassive', null, opts);
  } catch (e) {}

  // Export for use by other modules
  window.Quirrely = window.Quirrely || {};
  window.Quirrely.passiveSupported = passiveSupported;
  window.Quirrely.passiveEvent = passiveSupported ? { passive: true } : false;


  // ─── STORAGE AVAILABILITY ────────────────────────────────────────────────

  window.Quirrely.storageAvailable = (function () {
    try {
      var key = '__quirrely_storage_test__';
      localStorage.setItem(key, '1');
      localStorage.removeItem(key);
      return true;
    } catch (e) {
      return false;
    }
  })();

  if (!window.Quirrely.storageAvailable) {
    console.warn('[compat] localStorage unavailable — private browsing mode?');
    html.classList.add('no-localstorage');
  }


  // ─── INTERSECTION OBSERVER CHECK ─────────────────────────────────────────

  if (!('IntersectionObserver' in window)) {
    // Load a polyfill if needed (network required; skip gracefully if offline)
    console.warn('[compat] IntersectionObserver not available — lazy loading disabled');
    window.Quirrely.noIntersectionObserver = true;
  }


  // ─── SMOOTH SCROLL POLYFILL DETECTION ────────────────────────────────────

  if (!('scrollBehavior' in document.documentElement.style)) {
    // Smooth scroll not supported (Safari < 15.4)
    html.classList.add('no-smooth-scroll');
  }


  // ─── PREVENT DOUBLE-TAP ZOOM (iOS, Android) ──────────────────────────────
  // Handled via touch-action: manipulation in compat.css.
  // Belt-and-suspenders: set meta viewport if missing.

  (function () {
    var viewport = document.querySelector('meta[name="viewport"]');
    if (!viewport) {
      viewport = document.createElement('meta');
      viewport.name = 'viewport';
      document.head.appendChild(viewport);
    }
    // Ensure maximum-scale is not set to 1 (breaks accessibility).
    // iOS zoom prevention is handled by 16px font-size on inputs, not this.
    if (!viewport.content || viewport.content.indexOf('width=device-width') === -1) {
      viewport.content = 'width=device-width, initial-scale=1.0';
    }
  })();


  // ─── FOCUS-VISIBLE POLYFILL (Safari < 15) ────────────────────────────────

  if (!CSS.supports('selector(:focus-visible)')) {
    // Minimal :focus-visible polyfill — add 'keyboard-nav' class on Tab key
    var usingKeyboard = false;

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Tab') usingKeyboard = true;
    });

    document.addEventListener('mousedown', function () {
      usingKeyboard = false;
    });

    document.addEventListener('focus', function (e) {
      if (usingKeyboard && e.target) {
        e.target.classList.add('focus-visible');
      }
    }, true);

    document.addEventListener('blur', function (e) {
      if (e.target) {
        e.target.classList.remove('focus-visible');
      }
    }, true);
  }


  // ─── REDUCED MOTION DETECTION ────────────────────────────────────────────

  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    html.classList.add('reduced-motion');
    window.Quirrely.reducedMotion = true;
  }

  // Watch for change
  if (window.matchMedia) {
    window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', function (e) {
      window.Quirrely.reducedMotion = e.matches;
      html.classList.toggle('reduced-motion', e.matches);
    });
  }


  // ─── COLOUR SCHEME ───────────────────────────────────────────────────────

  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    window.Quirrely.prefersDark = true;
    html.classList.add('prefers-dark');
  }


  // ─── EXPORT COMPAT SUMMARY ───────────────────────────────────────────────

  window.Quirrely.compat = {
    ios:              isIOS,
    android:          isAndroid,
    safariDesktop:    isMacSafari && !isIOS,
    touch:            'ontouchstart' in window,
    passiveEvents:    passiveSupported,
    storage:          window.Quirrely.storageAvailable,
    cssVars:          html.classList.contains('css-vars'),
    cssGrid:          html.classList.contains('css-grid'),
    reducedMotion:    !!window.Quirrely.reducedMotion,
  };

  // Devtools visibility
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.debug('[Quirrely compat]', window.Quirrely.compat);
  }

})();
