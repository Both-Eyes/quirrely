/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY EXTENSION - Content Script
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Runs on all pages. Handles:
 * - Text selection detection
 * - Floating analyze button
 * - Inline result display
 * - Text area monitoring (optional auto-analyze)
 */

(function() {
  'use strict';
  
  // ═══════════════════════════════════════════════════════════════════
  // Configuration
  // ═══════════════════════════════════════════════════════════════════
  
  const CONFIG = {
    minTextLength: 50,
    buttonShowDelay: 300,
    buttonHideDelay: 200,
    resultDisplayDuration: 8000
  };
  
  // ═══════════════════════════════════════════════════════════════════
  // State
  // ═══════════════════════════════════════════════════════════════════
  
  let floatingButton = null;
  let resultPopup = null;
  let hideButtonTimeout = null;
  let settings = null;
  
  // ═══════════════════════════════════════════════════════════════════
  // Initialization
  // ═══════════════════════════════════════════════════════════════════
  
  async function initialize() {
    // Load settings
    settings = await getSettings();
    
    // Create floating button
    if (settings.showFloatingButton) {
      createFloatingButton();
    }
    
    // Listen for selection changes
    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('keyup', handleKeyUp);
    
    // Listen for settings changes
    chrome.storage.onChanged.addListener((changes) => {
      if (changes.quirrely_settings) {
        settings = changes.quirrely_settings.newValue;
        updateUIForSettings();
      }
    });
  }
  
  async function getSettings() {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ type: 'GET_SETTINGS' }, (response) => {
        resolve(response || {
          showFloatingButton: true,
          minTextLength: 50,
          autoAnalyze: false
        });
      });
    });
  }
  
  function updateUIForSettings() {
    if (settings.showFloatingButton && !floatingButton) {
      createFloatingButton();
    } else if (!settings.showFloatingButton && floatingButton) {
      floatingButton.remove();
      floatingButton = null;
    }
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // Floating Button
  // ═══════════════════════════════════════════════════════════════════
  
  function createFloatingButton() {
    if (floatingButton) return;
    
    floatingButton = document.createElement('div');
    floatingButton.id = 'quirrely-floating-button';
    floatingButton.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="8" r="5" fill="#FF6B5A"/>
        <path d="M12 14C8 14 5 17 5 21H19C19 17 16 14 12 14Z" fill="#2D3748"/>
        <circle cx="12" cy="8" r="2" fill="white"/>
      </svg>
      <span>Analyze</span>
    `;
    
    floatingButton.addEventListener('click', handleButtonClick);
    floatingButton.addEventListener('mouseenter', () => clearTimeout(hideButtonTimeout));
    floatingButton.addEventListener('mouseleave', () => scheduleHideButton());
    
    document.body.appendChild(floatingButton);
  }
  
  function showFloatingButton(x, y) {
    if (!floatingButton || !settings.showFloatingButton) return;
    
    clearTimeout(hideButtonTimeout);
    
    // Position near selection
    const buttonWidth = 100;
    const buttonHeight = 32;
    
    let left = x - buttonWidth / 2;
    let top = y - buttonHeight - 10;
    
    // Keep on screen
    left = Math.max(10, Math.min(left, window.innerWidth - buttonWidth - 10));
    top = Math.max(10, top);
    
    floatingButton.style.left = `${left}px`;
    floatingButton.style.top = `${top}px`;
    floatingButton.classList.add('visible');
  }
  
  function hideFloatingButton() {
    if (floatingButton) {
      floatingButton.classList.remove('visible');
    }
  }
  
  function scheduleHideButton() {
    clearTimeout(hideButtonTimeout);
    hideButtonTimeout = setTimeout(hideFloatingButton, CONFIG.buttonHideDelay);
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // Selection Handling
  // ═══════════════════════════════════════════════════════════════════
  
  function handleMouseUp(event) {
    // Ignore if clicking the button or popup
    if (event.target.closest('#quirrely-floating-button') ||
        event.target.closest('#quirrely-result-popup')) {
      return;
    }
    
    setTimeout(() => {
      const selection = window.getSelection();
      const text = selection.toString().trim();
      
      if (text.length >= (settings.minTextLength || CONFIG.minTextLength)) {
        // Get selection position
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        
        const x = rect.left + rect.width / 2 + window.scrollX;
        const y = rect.top + window.scrollY;
        
        showFloatingButton(x, y);
      } else {
        scheduleHideButton();
      }
    }, CONFIG.buttonShowDelay);
  }
  
  function handleKeyUp(event) {
    // Handle Escape to close popup
    if (event.key === 'Escape') {
      hideResultPopup();
      hideFloatingButton();
    }
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // Analysis
  // ═══════════════════════════════════════════════════════════════════
  
  async function handleButtonClick(event) {
    event.preventDefault();
    event.stopPropagation();
    
    const selection = window.getSelection();
    const text = selection.toString().trim();
    
    if (text.length < (settings.minTextLength || CONFIG.minTextLength)) {
      showError('Please select more text (at least 50 characters)');
      return;
    }
    
    // Show loading state
    floatingButton.classList.add('loading');
    
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'ANALYZE_TEXT',
        text: text,
        options: {
          source: 'content_script',
          url: window.location.href
        }
      });
      
      if (response.success) {
        showResult(response.analysis);
      } else {
        showError(response.error || 'Analysis failed');
      }
    } catch (error) {
      showError('Unable to analyze text');
      console.error('Quirrely analysis error:', error);
    } finally {
      floatingButton.classList.remove('loading');
      hideFloatingButton();
    }
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // Result Popup
  // ═══════════════════════════════════════════════════════════════════
  
  function showResult(analysis) {
    hideResultPopup();
    
    resultPopup = document.createElement('div');
    resultPopup.id = 'quirrely-result-popup';
    resultPopup.innerHTML = `
      <div class="quirrely-popup-header">
        <span class="quirrely-popup-icon">${analysis.icon}</span>
        <div class="quirrely-popup-title-group">
          <h3 class="quirrely-popup-title">${analysis.title}</h3>
          <p class="quirrely-popup-tagline">${analysis.tagline}</p>
        </div>
        <button class="quirrely-popup-close" title="Close">×</button>
      </div>
      
      <div class="quirrely-popup-body">
        <div class="quirrely-popup-badges">
          <span class="quirrely-badge profile">${analysis.profileType}</span>
          <span class="quirrely-badge stance">${analysis.stance}</span>
          <span class="quirrely-badge confidence">${Math.round(analysis.confidence * 100)}%</span>
        </div>
        
        <div class="quirrely-popup-traits">
          ${analysis.traits.slice(0, 3).map(t => `<span class="quirrely-trait">${t}</span>`).join('')}
        </div>
        
        <div class="quirrely-popup-metrics">
          <div class="quirrely-metric">
            <span class="quirrely-metric-value">${analysis.metrics.wordCount}</span>
            <span class="quirrely-metric-label">words</span>
          </div>
          <div class="quirrely-metric">
            <span class="quirrely-metric-value">${analysis.metrics.sentenceCount}</span>
            <span class="quirrely-metric-label">sentences</span>
          </div>
          <div class="quirrely-metric">
            <span class="quirrely-metric-value">${analysis.metrics.questionRate}%</span>
            <span class="quirrely-metric-label">questions</span>
          </div>
        </div>
      </div>
      
      <div class="quirrely-popup-footer">
        <a href="#" class="quirrely-popup-link" data-action="full-results">View full results →</a>
        <span class="quirrely-popup-brand">Powered by Quirrely</span>
      </div>
    `;
    
    // Position in top-right corner
    document.body.appendChild(resultPopup);
    
    // Event listeners
    resultPopup.querySelector('.quirrely-popup-close').addEventListener('click', hideResultPopup);
    resultPopup.querySelector('[data-action="full-results"]').addEventListener('click', (e) => {
      e.preventDefault();
      chrome.runtime.sendMessage({ type: 'OPEN_POPUP' });
    });
    
    // Auto-hide after duration
    setTimeout(hideResultPopup, CONFIG.resultDisplayDuration);
    
    // Animate in
    requestAnimationFrame(() => {
      resultPopup.classList.add('visible');
    });
  }
  
  function showError(message) {
    hideResultPopup();
    
    resultPopup = document.createElement('div');
    resultPopup.id = 'quirrely-result-popup';
    resultPopup.classList.add('error');
    resultPopup.innerHTML = `
      <div class="quirrely-popup-header">
        <span class="quirrely-popup-icon">⚠️</span>
        <div class="quirrely-popup-title-group">
          <h3 class="quirrely-popup-title">Analysis Error</h3>
          <p class="quirrely-popup-tagline">${message}</p>
        </div>
        <button class="quirrely-popup-close" title="Close">×</button>
      </div>
    `;
    
    document.body.appendChild(resultPopup);
    
    resultPopup.querySelector('.quirrely-popup-close').addEventListener('click', hideResultPopup);
    
    setTimeout(hideResultPopup, 4000);
    
    requestAnimationFrame(() => {
      resultPopup.classList.add('visible');
    });
  }
  
  function hideResultPopup() {
    if (resultPopup) {
      resultPopup.classList.remove('visible');
      setTimeout(() => {
        if (resultPopup) {
          resultPopup.remove();
          resultPopup = null;
        }
      }, 300);
    }
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // Initialize
  // ═══════════════════════════════════════════════════════════════════
  
  // Wait for DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
})();
