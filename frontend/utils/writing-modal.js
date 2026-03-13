/**
 * QUIRRELY WRITING MODAL v1.0
 * Unified modal for: first analysis, stretch exercises, featured submissions.
 * Same visual frame, different prompt sources and thresholds.
 *
 * Requires: writing-prompts.js (WRITING_PROMPTS)
 *
 * Usage:
 *   WritingModal.open({
 *     mode: 'first_analysis',   // 'first_analysis' | 'stretch' | 'featured'
 *     prompts: [...],           // array of {text, ...} objects
 *     minWords: 25,             // per prompt
 *     onComplete: function(entries) { ... }
 *   });
 */
var WritingModal = (function() {

  var _config = null;
  var _pos = 0;
  var _entries = [];  // {prompt, text, wordCount} per completed prompt
  var _saveTimer = null;

  // ═══════════════════════════════════════════════════════════
  // MODAL STRUCTURE
  // ═══════════════════════════════════════════════════════════

  function ensureModal() {
    if (document.getElementById('wmBg')) return;

    var html = '<div class="wm-bg" id="wmBg" style="display:none;" onclick="if(event.target===this)WritingModal.close()">' +
      '<div class="wm-box">' +
        '<button class="wm-close" onclick="WritingModal.close()">&times;</button>' +
        '<div id="wmContent"></div>' +
      '</div>' +
    '</div>';

    document.body.insertAdjacentHTML('beforeend', html);
  }

  // ═══════════════════════════════════════════════════════════
  // OPEN
  // ═══════════════════════════════════════════════════════════

  function open(config) {
    ensureModal();
    _config = config;
    _pos = 0;
    _entries = [];

    // Load saved progress if any
    var saved = loadProgress(config.mode);
    if (saved && saved.entries && saved.entries.length > 0) {
      if (confirm('Resume where you left off? (' + saved.entries.length + '/' + config.prompts.length + ' done)')) {
        _entries = saved.entries;
        _pos = saved.pos;
      } else {
        clearProgress(config.mode);
      }
    }

    var bg = document.getElementById('wmBg');
    bg.style.display = 'flex';
    requestAnimationFrame(function() { bg.classList.add('show'); });
    document.body.style.overflow = 'hidden';

    if (_pos === 0 && _entries.length === 0) {
      renderWelcome();
    } else {
      renderPrompt();
    }
  }

  // ═══════════════════════════════════════════════════════════
  // CLOSE
  // ═══════════════════════════════════════════════════════════

  function close() {
    var bg = document.getElementById('wmBg');
    bg.classList.remove('show');
    setTimeout(function() { bg.style.display = 'none'; }, 300);
    document.body.style.overflow = '';
  }

  // ═══════════════════════════════════════════════════════════
  // WELCOME SCREEN
  // ═══════════════════════════════════════════════════════════

  function renderWelcome() {
    var el = document.getElementById('wmContent');
    var titles = {
      'first_analysis': 'Let\u2019s find your writing voice.',
      'stretch': 'Ready to stretch your voice?',
      'featured': 'Write something worth featuring.',
    };
    var subs = {
      'first_analysis': 'Answer ' + _config.prompts.length + ' quick prompts \u2014 just write naturally. No right answers, only your voice.',
      'stretch': 'Push your writing into new territory with ' + _config.prompts.length + ' guided prompts.',
      'featured': 'Write your best. Featured submissions reach the whole Quirrely community.',
    };

    el.innerHTML =
      '<div class="wm-welcome">' +
        '<div class="wm-welcome-icon">' +
          '<svg viewBox="0 0 80 120" width="64" height="96">' +
            '<path d="M58 112 Q85 98,94 62 Q100 26,74 8 Q50-8,42 22 Q38 44,54 60 Q70 78,62 100 Q58 110,58 112" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.4"/>' +
            '<ellipse cx="40" cy="98" rx="22" ry="26" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.4"/>' +
            '<ellipse cx="40" cy="50" rx="22" ry="20" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.4"/>' +
            '<ellipse cx="24" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.6"/>' +
            '<ellipse cx="56" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.6"/>' +
            '<ellipse cx="32" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/><ellipse cx="48" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>' +
            '<circle cx="33" cy="46.5" r="2" fill="#FFF"/><circle cx="49" cy="46.5" r="2" fill="#FFF"/>' +
            '<ellipse cx="40" cy="60" rx="4.5" ry="3.5" fill="#4A4A4A"/>' +
            '<path d="M31 78 Q30 94,40 99 Q50 94,49 78 Z" fill="#FF5C34"/>' +
          '</svg>' +
        '</div>' +
        '<h2 class="wm-welcome-title">' + (_config.welcomeTitle || _config.welcomeTitle || titles[_config.mode] || titles.first_analysis) + '</h2>' +
        '<p class="wm-welcome-sub">' + (_config.welcomeSub || _config.welcomeSub || subs[_config.mode] || subs.first_analysis) + '</p>' +
        '<button class="wm-start-btn" onclick="WritingModal._startWriting()">Start Writing</button>' +
      '</div>';
  }

  function _startWriting() {
    renderPrompt();
  }

  // ═══════════════════════════════════════════════════════════
  // PROMPT SCREEN
  // ═══════════════════════════════════════════════════════════

  function renderPrompt() {
    if (_pos >= _config.prompts.length) {
      renderComplete();
      return;
    }

    var prompt = _config.prompts[_pos];
    var total = _config.prompts.length;
    var minW = _config.minWords || 25;
    var el = document.getElementById('wmContent');

    // Progress pips
    var pips = '<div class="wm-progress">';
    for (var i = 0; i < total; i++) {
      pips += '<div class="wm-pip' + (i < _pos ? ' done' : i === _pos ? ' active' : '') + '"></div>';
    }
    pips += '</div>';

    // Category label
    var catLabels = {opinion:'Share your take', memory:'Remember a moment', observation:'Look closely', explanation:'Explain it your way', preference:'What matters to you'};
    var catLabel = catLabels[prompt.cat] || 'Write naturally';

    // Existing text for this position
    var existing = (_entries[_pos] && _entries[_pos].text) || '';

    el.innerHTML =
      pips +
      '<div class="wm-prompt-label">' + catLabel + '</div>' +
      '<div class="wm-prompt-text">' + prompt.text + '</div>' +
      '<textarea class="wm-textarea" id="wmText" placeholder="Start writing here..." oninput="WritingModal._onInput()">' + existing + '</textarea>' +
      '<div class="wm-prompt-footer">' +
        '<span class="wm-wc" id="wmWc">0 / ' + minW + ' words minimum</span>' +
        '<div class="wm-prompt-meta">Prompt ' + (_pos + 1) + ' of ' + total + '</div>' +
        '<button class="wm-next-btn" id="wmNext" onclick="WritingModal._next()" disabled>' +
          (_pos < total - 1 ? 'Next \u2192' : 'Finish') +
        '</button>' +
      '</div>';

    // Focus textarea
    setTimeout(function() { document.getElementById('wmText').focus(); }, 100);
    _onInput();
  }

  function _onInput() {
    var textarea = document.getElementById('wmText');
    if (!textarea) return;

    var text = textarea.value.trim();
    var words = text.split(/\s+/).filter(function(w) { return w; }).length;
    var minW = _config.minWords || 25;

    var wc = document.getElementById('wmWc');
    var btn = document.getElementById('wmNext');

    wc.textContent = words + ' / ' + minW + ' words minimum';
    wc.className = 'wm-wc' + (words >= minW ? ' met' : '');
    btn.disabled = words < minW;

    // Debounced auto-save
    clearTimeout(_saveTimer);
    _saveTimer = setTimeout(function() {
      // Save current text to entries
      _entries[_pos] = {
        prompt: _config.prompts[_pos].text,
        promptId: _config.prompts[_pos].id,
        text: textarea.value,
        wordCount: words,
      };
      saveProgress(_config.mode, _pos, _entries);
    }, 800);
  }

  function _next() {
    var textarea = document.getElementById('wmText');
    var text = textarea.value.trim();
    var words = text.split(/\s+/).filter(function(w) { return w; }).length;
    var minW = _config.minWords || 25;

    if (words < minW) return;

    // Save entry
    _entries[_pos] = {
      prompt: _config.prompts[_pos].text,
      promptId: _config.prompts[_pos].id,
      text: textarea.value,
      wordCount: words,
    };

    _pos++;
    saveProgress(_config.mode, _pos, _entries);
    renderPrompt();
  }

  // ═══════════════════════════════════════════════════════════
  // COMPLETE
  // ═══════════════════════════════════════════════════════════

  function renderComplete() {
    var totalWords = 0;
    _entries.forEach(function(e) { totalWords += e.wordCount || 0; });

    var el = document.getElementById('wmContent');
    el.innerHTML =
      '<div class="wm-complete">' +
        '<div class="wm-complete-check">\u2713</div>' +
        '<h3 class="wm-complete-title">Beautiful. ' + totalWords + ' words written.</h3>' +
        '<p class="wm-complete-sub">Analyzing your writing voice...</p>' +
        '<div class="wm-spinner"></div>' +
      '</div>';

    clearProgress(_config.mode);

    // Concatenate all text and call onComplete
    var allText = _entries.map(function(e) { return e.text; }).join('\n\n');

    if (_config.onComplete) {
      _config.onComplete(_entries, allText, totalWords);
    }
  }

  // ═══════════════════════════════════════════════════════════
  // PERSISTENCE
  // ═══════════════════════════════════════════════════════════

  var STORE_KEY = 'quirrely_wm_';

  function saveProgress(mode, pos, entries) {
    try {
      localStorage.setItem(STORE_KEY + mode, JSON.stringify({
        pos: pos,
        entries: entries,
        ts: Date.now(),
      }));
    } catch(e) {}
  }

  function loadProgress(mode) {
    try {
      var d = JSON.parse(localStorage.getItem(STORE_KEY + mode));
      if (!d) return null;
      // Expire after 24 hours
      if (Date.now() - d.ts > 24 * 3600 * 1000) {
        localStorage.removeItem(STORE_KEY + mode);
        return null;
      }
      return d;
    } catch(e) { return null; }
  }

  function clearProgress(mode) {
    try { localStorage.removeItem(STORE_KEY + mode); } catch(e) {}
  }

  // ═══════════════════════════════════════════════════════════
  // CONVENIENCE: First Analysis
  // ═══════════════════════════════════════════════════════════

  function openFirstAnalysis(onComplete) {
    var isAuthed = false;
    try {
      var sess = JSON.parse(localStorage.getItem('quirrely_session'));
      isAuthed = !!(sess && sess.token);
    } catch(e) {}

    var offset = 0;
    try {
      offset = parseInt(localStorage.getItem(STORE_KEY + 'offset') || '0') || 0;
    } catch(e) {}

    var prompts;
    if (isAuthed) {
      prompts = WRITING_PROMPTS.getSequence(4, offset);
      // Advance offset for next time
      localStorage.setItem(STORE_KEY + 'offset', String(WRITING_PROMPTS.nextOffset(offset, 4)));
    } else {
      prompts = WRITING_PROMPTS.getRandom(4);
    }

    open({
      mode: 'first_analysis',
      prompts: prompts,
      minWords: 25,
      onComplete: onComplete,
    });
  }

  // ═══════════════════════════════════════════════════════════
  // PUBLIC API
  // ═══════════════════════════════════════════════════════════

  return {
    open: open,
    close: close,
    openFirstAnalysis: openFirstAnalysis,
    _startWriting: _startWriting,
    _onInput: _onInput,
    _next: _next,
  };
})();

if (typeof window !== 'undefined') window.WritingModal = WritingModal;
