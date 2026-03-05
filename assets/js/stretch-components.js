/**
 * STRETCH UI Components — Quirrely v3.1.3
 * ═══════════════════════════════════════
 * Portable STRETCH exercise component library.
 * Extracted from frontend/index.html for use in:
 *   - extension/pages/popup.html
 *   - Standalone stretch.html pages
 *   - Any surface embedding the STRETCH system
 *
 * Requires:
 *   - LNCP classifier available (inline or via api-client.js)
 *   - Quirrely brand CSS loaded (compat.css or inline styles)
 *
 * Usage:
 *   <script src="/assets/js/stretch-components.js"></script>
 *   <div id="stretch-mount"></div>
 *   <script>
 *     StretchComponents.mount('#stretch-mount', { apiBase: 'https://api.quirrely.com' });
 *   </script>
 */

(function (global) {
  'use strict';

  // ═══════════════════════════════════════════════════════════════════════
  // CONSTANTS
  // ═══════════════════════════════════════════════════════════════════════

  const STRETCH_BTN_COLORS = [
    'stretch-btn-coral',
    'stretch-btn-teal',
    'stretch-btn-purple',
  ];

  const PROFILE_OPPOSITES = {
    ASSERTIVE:     ['HEDGED', 'POETIC'],
    HEDGED:        ['ASSERTIVE'],
    CONVERSATIONAL:['FORMAL'],
    FORMAL:        ['CONVERSATIONAL', 'POETIC'],
    DENSE:         ['MINIMAL'],
    MINIMAL:       ['DENSE', 'INTERROGATIVE', 'LONGFORM'],
    POETIC:        ['ASSERTIVE', 'FORMAL'],
    INTERROGATIVE: ['MINIMAL'],
    LONGFORM:      ['MINIMAL'],
    ANALYTICAL:    ['CONVERSATIONAL'],
  };

  const CHALLENGE_STARTERS = {
    ASSERTIVE: [
      { text: 'Make a definitive claim about something uncertain.',    guidance: 'Choose one side. No hedging — state it plainly.' },
      { text: 'Write as if you are the only authority in the room.',   guidance: 'Drop the qualifiers. You know this.' },
      { text: 'Open with the conclusion. Put your stake in the ground.', guidance: 'Resist the urge to build up. Lead with your point.' },
    ],
    HEDGED: [
      { text: 'Qualify every statement — nothing is certain.',         guidance: 'Use "perhaps", "it seems", "one might argue".' },
      { text: 'Write from doubt. Explore, don\'t resolve.',            guidance: 'Let questions stay questions.' },
      { text: 'Acknowledge what you don\'t know first.',              guidance: 'Start from the edge of your knowledge.' },
    ],
    CONVERSATIONAL: [
      { text: 'Write exactly as you\'d say it to a friend.',           guidance: 'Contractions, natural rhythm, no formality.' },
      { text: 'Include a direct address — talk to the reader.',        guidance: '"You know that feeling when…"' },
      { text: 'Break a grammar rule on purpose. Sound like a person.', guidance: 'Fragments are fine. So is starting with "And".' },
    ],
    FORMAL: [
      { text: 'Open with an authoritative, complete sentence.',        guidance: 'Passive voice is acceptable. Precision over warmth.' },
      { text: 'Write as if for a committee that requires evidence.',   guidance: 'Cite the logic. Show your reasoning structure.' },
      { text: 'Eliminate every contraction and colloquialism.',        guidance: 'Distance is the register here.' },
    ],
    DENSE: [
      { text: 'Compress a paragraph into one sentence.',               guidance: 'No examples, no elaboration — only essence.' },
      { text: 'Pack three ideas into one clause.',                      guidance: 'Use semicolons and em-dashes to layer meaning.' },
      { text: 'Write as if word count is extremely limited.',          guidance: 'Every word must carry full weight.' },
    ],
    MINIMAL: [
      { text: 'Say the most important thing in twelve words or fewer.', guidance: 'Then stop. Don\'t explain what you just said.' },
      { text: 'Write a sentence with no adjectives or adverbs.',       guidance: 'Nouns and verbs only. Trust the image.' },
      { text: 'Leave something out that the reader can fill in.',      guidance: 'Implication is stronger than statement.' },
    ],
    POETIC: [
      { text: 'Write a sentence that uses a physical image for an idea.', guidance: 'Not a simile — let the image BE the idea.' },
      { text: 'Let sound carry meaning — read it aloud as you write.',    guidance: 'Rhythm, vowel sounds, pace all count.' },
      { text: 'Begin with something unexpected and return to it.',       guidance: 'Circular structure. Start strange, end familiar.' },
    ],
    ANALYTICAL: [
      { text: 'Break a phenomenon into its component parts.',           guidance: 'Name the mechanism, not just the result.' },
      { text: 'Identify the cause before the effect.',                  guidance: 'Build logically. Premise → conclusion.' },
      { text: 'Frame your observation as a testable proposition.',      guidance: 'Could this be proven wrong? That\'s the test.' },
    ],
    INTERROGATIVE: [
      { text: 'Ask a question you genuinely don\'t know the answer to.', guidance: 'Not rhetorical. Actually open.' },
      { text: 'Write a sentence that ends with more questions than it started.', guidance: 'Expand uncertainty. Don\'t close down.' },
      { text: 'Open a door you won\'t walk through.',                   guidance: 'Invite the reader in without following.' },
    ],
    LONGFORM: [
      { text: 'Take a simple observation and follow it to somewhere surprising.', guidance: 'Start close. Wander further than seems reasonable.' },
      { text: 'Include a digression that turns out to be the point.',    guidance: 'The aside IS the argument.' },
      { text: 'Write past the obvious ending and find the better one.', guidance: 'That first ending you thought of? Skip it.' },
    ],
  };

  // ═══════════════════════════════════════════════════════════════════════
  // KEYSTROKE TRACKER
  // Enforces anti-paste detection (mirrors stretch_api.py validation)
  // ═══════════════════════════════════════════════════════════════════════

  class KeystrokeTracker {
    constructor (targetEl) {
      this._el = targetEl;
      this._keystrokes = [];
      this._clipboardEvents = [];
      this._pasteDetected = false;
      this._startTime = null;
      this._bind();
    }

    _bind () {
      this._el.addEventListener('keydown',   (e) => this._onKeydown(e));
      this._el.addEventListener('paste',     (e) => this._onPaste(e));
      this._el.addEventListener('drop',      (e) => this._onDrop(e));
      this._el.addEventListener('contextmenu',(e) => this._onContext(e));
      this._el.addEventListener('focus',     () => { if (!this._startTime) this._startTime = Date.now(); });
    }

    _onKeydown (e) {
      // Detect keyboard-shortcut paste
      if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
        this._flagPaste('keyboard_shortcut');
        e.preventDefault();
        return;
      }
      this._keystrokes.push({ key: e.key, time: Date.now(), ctrl: e.ctrlKey, meta: e.metaKey });
    }

    _onPaste (e) {
      this._flagPaste('paste_event');
      e.preventDefault();
    }

    _onDrop (e) {
      this._flagPaste('drag_drop');
      e.preventDefault();
    }

    _onContext (e) {
      // Right-click paste attempt — log but don't block (UX)
      this._clipboardEvents.push({ type: 'context_menu', time: Date.now() });
    }

    _flagPaste (type) {
      this._pasteDetected = true;
      this._clipboardEvents.push({ type, time: Date.now() });
    }

    getPayload () {
      const content   = this._el.value || '';
      const durationMs = this._startTime ? Date.now() - this._startTime : 0;
      const wordCount = content.trim().split(/\s+/).filter(Boolean).length;
      const cps = durationMs > 0 ? (content.length / durationMs) * 1000 : 0;
      return {
        keystrokes:       this._keystrokes,
        clipboard_events: this._clipboardEvents,
        content,
        word_count:       wordCount,
        duration_ms:      durationMs,
        chars_per_second: Math.round(cps * 100) / 100,
      };
    }

    isPasteDetected () { return this._pasteDetected; }
    reset () {
      this._keystrokes      = [];
      this._clipboardEvents = [];
      this._pasteDetected   = false;
      this._startTime       = null;
      this._el.value        = '';
    }
  }

  // ═══════════════════════════════════════════════════════════════════════
  // STRETCH API CLIENT
  // ═══════════════════════════════════════════════════════════════════════

  class StretchAPIClient {
    constructor (apiBase) {
      this._base = apiBase || 'https://api.quirrely.com';
    }

    async checkEligibility (userId) {
      const r = await fetch(`${this._base}/api/stretch/eligibility/${userId}`);
      if (!r.ok) throw new Error(`eligibility check failed: ${r.status}`);
      return r.json();
    }

    async startExercise (payload) {
      const r = await fetch(`${this._base}/api/stretch/start`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });
      if (!r.ok) throw new Error(`start failed: ${r.status}`);
      return r.json();
    }

    async submitInput (exerciseId, cycleNumber, promptNumber, payload) {
      const r = await fetch(
        `${this._base}/api/stretch/input/${exerciseId}/${cycleNumber}/${promptNumber}`,
        {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify(payload),
        }
      );
      if (r.status === 422) {
        const err = await r.json();
        throw Object.assign(new Error('validation_failed'), { detail: err.detail });
      }
      if (!r.ok) throw new Error(`submit failed: ${r.status}`);
      return r.json();
    }

    async getProgress (userId) {
      const r = await fetch(`${this._base}/api/stretch/progress/${userId}`);
      if (!r.ok) return null;
      return r.json();
    }
  }

  // ═══════════════════════════════════════════════════════════════════════
  // STRETCH COMPONENT
  // The main mountable component
  // ═══════════════════════════════════════════════════════════════════════

  class StretchComponent {
    constructor (mountEl, options = {}) {
      this._mount    = typeof mountEl === 'string' ? document.querySelector(mountEl) : mountEl;
      this._api      = new StretchAPIClient(options.apiBase);
      this._userId   = options.userId || null;
      this._profile  = options.profile || 'ASSERTIVE';
      this._tracker  = null;

      this._state = {
        phase:           'idle',   // idle | select | writing | submitted | error
        selectedIdx:     -1,
        challenges:      [],
        exerciseId:      null,
        cycleNumber:     1,
        promptNumber:    1,
        pasteError:      false,
      };

      this._onComplete = options.onComplete || (() => {});
      this._onError    = options.onError    || ((e) => console.error(e));
    }

    // ── PUBLIC ──────────────────────────────────────────────────────────

    mount (profile, userProfile) {
      this._profile     = profile     || this._profile;
      this._userProfile = userProfile || null;
      this._state.challenges = this._getChallenges();
      this._render();
    }

    destroy () {
      if (this._mount) this._mount.innerHTML = '';
    }

    // ── PRIVATE ─────────────────────────────────────────────────────────

    _getChallenges () {
      const opposites = PROFILE_OPPOSITES[this._profile] || [];
      const candidates = [];

      // First: opposite profiles (highest growth value)
      for (const opp of opposites) {
        const pool = CHALLENGE_STARTERS[opp] || [];
        if (pool.length > 0) candidates.push({ ...pool[0], targetProfile: opp });
      }

      // Then: fill remaining from current profile's challenges
      const myPool = CHALLENGE_STARTERS[this._profile] || [];
      for (const c of myPool) {
        if (candidates.length >= 3) break;
        candidates.push({ ...c, targetProfile: this._profile });
      }

      return candidates.slice(0, 3);
    }

    _render () {
      const { phase, challenges, selectedIdx, pasteError } = this._state;

      this._mount.innerHTML = `
        <div class="stretch-component" role="region" aria-label="Writing stretch exercise">

          ${phase === 'idle' || phase === 'select' ? `
          <div class="stretch-challenges-phase">
            <p class="stretch-intro" id="sc-intro">
              You write as <strong>${this._profile}</strong>. Choose a stretch challenge:
            </p>
            <div class="btn-group" id="sc-challenges" role="group" aria-label="Stretch challenges">
              ${challenges.map((c, i) => `
                <button class="btn btn-small stretch-btn ${STRETCH_BTN_COLORS[i]}"
                        data-index="${i}"
                        style="${selectedIdx === i ? 'opacity:1;transform:translateY(-2px)' : selectedIdx >= 0 ? 'opacity:0.5' : ''}"
                        aria-pressed="${selectedIdx === i}">
                  ${c.text}
                </button>
              `).join('')}
            </div>

            ${selectedIdx >= 0 ? `
            <div class="stretch-input-area" id="sc-input-area">
              <div class="stretch-guidance" aria-live="polite">
                ${challenges[selectedIdx].guidance}
              </div>
              <label class="label" for="sc-textarea">Your stretch sentence</label>
              <textarea
                id="sc-textarea"
                class="textarea"
                rows="4"
                placeholder="Write one sentence — type it fresh, don't paste…"
                autocomplete="off"
                autocorrect="off"
                spellcheck="true"
              ></textarea>
              ${pasteError ? `
              <p class="error-msg" role="alert" style="color:#E74C3C;margin-top:8px;font-size:13px">
                ✗ Paste detected — please type your sentence from scratch.
              </p>` : ''}
              <div class="btn-group" style="margin-top:12px">
                <button class="btn btn-secondary" id="sc-cancel">Cancel</button>
                <button class="btn btn-primary" id="sc-submit">Submit Stretch →</button>
              </div>
            </div>` : ''}
          </div>` : ''}

          ${phase === 'submitted' ? `
          <div class="stretch-complete fade-in" role="status">
            <div style="font-size:32px;margin-bottom:8px">✓</div>
            <p style="font-weight:700;font-size:16px">Stretch complete.</p>
            <p style="color:#5A6072;font-size:13px;margin-top:4px">
              Your writing has been submitted and your session extended.
            </p>
          </div>` : ''}

          ${phase === 'error' ? `
          <div class="stretch-error fade-in" role="alert" style="color:#E74C3C">
            <p>Something went wrong. Please try again.</p>
            <button class="btn btn-secondary" id="sc-retry" style="margin-top:8px">Retry</button>
          </div>` : ''}

        </div>
      `;

      this._bindEvents();

      // Attach keystroke tracker to textarea
      const ta = this._mount.querySelector('#sc-textarea');
      if (ta) {
        this._tracker = new KeystrokeTracker(ta);
      }
    }

    _bindEvents () {
      // Challenge buttons
      this._mount.querySelectorAll('[data-index]').forEach(btn => {
        btn.addEventListener('click', () => {
          this._state.selectedIdx = parseInt(btn.dataset.index, 10);
          this._state.phase       = 'select';
          this._state.pasteError  = false;
          this._render();
        });
      });

      // Cancel
      const cancelBtn = this._mount.querySelector('#sc-cancel');
      if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
          this._state.selectedIdx = -1;
          this._state.phase       = 'idle';
          this._render();
        });
      }

      // Submit
      const submitBtn = this._mount.querySelector('#sc-submit');
      if (submitBtn) {
        submitBtn.addEventListener('click', () => this._handleSubmit());
      }

      // Retry
      const retryBtn = this._mount.querySelector('#sc-retry');
      if (retryBtn) {
        retryBtn.addEventListener('click', () => {
          this._state.phase       = 'idle';
          this._state.selectedIdx = -1;
          this._render();
        });
      }
    }

    async _handleSubmit () {
      if (!this._tracker) return;

      const payload  = this._tracker.getPayload();

      // Client-side paste check
      if (this._tracker.isPasteDetected()) {
        this._state.pasteError = true;
        this._tracker.reset();
        this._render();
        return;
      }

      if (payload.word_count < 5) {
        this._state.pasteError = false;
        const ta = this._mount.querySelector('#sc-textarea');
        if (ta) ta.focus();
        return;
      }

      try {
        // Start exercise if not started
        if (!this._state.exerciseId) {
          const challenge = this._state.challenges[this._state.selectedIdx];
          const exercise  = await this._api.startExercise({
            user_id:      this._userId,
            profile_from: this._profile,
            profile_to:   challenge.targetProfile,
          });
          this._state.exerciseId = exercise.id;
        }

        await this._api.submitInput(
          this._state.exerciseId,
          this._state.cycleNumber,
          this._state.promptNumber,
          payload
        );

        this._state.phase = 'submitted';
        this._render();
        this._onComplete({ exerciseId: this._state.exerciseId, payload });

      } catch (err) {
        if (err.message === 'validation_failed') {
          // Server rejected as paste
          this._state.pasteError = true;
          this._tracker.reset();
          this._render();
        } else {
          this._state.phase = 'error';
          this._render();
          this._onError(err);
        }
      }
    }
  }

  // ═══════════════════════════════════════════════════════════════════════
  // PUBLIC API
  // ═══════════════════════════════════════════════════════════════════════

  global.StretchComponents = {
    /**
     * Mount a STRETCH component into a DOM element.
     *
     * @param {string|Element} selector  - CSS selector or element
     * @param {object}         options   - { apiBase, userId, profile, onComplete, onError }
     * @returns {StretchComponent}
     */
    mount (selector, options = {}) {
      const component = new StretchComponent(selector, options);
      component.mount(options.profile, options.userProfile);
      return component;
    },

    KeystrokeTracker,
    StretchAPIClient,
    CHALLENGE_STARTERS,
    PROFILE_OPPOSITES,
    VERSION: '1.0.0',
  };

}(typeof window !== 'undefined' ? window : global));
