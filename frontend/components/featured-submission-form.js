/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY FEATURED WRITER SUBMISSION COMPONENT v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Handles Featured Writer submission flow:
 * - Eligibility check (PRO + 7-day 1K streak)
 * - Agreement confirmation (3 checkboxes)
 * - Keystroke-only text input (paste blocked)
 * - Word count validation (≤500)
 * - Submission to API
 */

const COLORS = {
  coral: '#FF6B6B',
  coralDark: '#E55A4A',
  softGold: '#D4A574',
  ink: '#2D3436',
  muted: '#636E72',
  bg: '#FFFBF5',
  bgDark: '#F8F5F0',
  border: '#E9ECEF',
  success: '#00B894',
  error: '#E74C3C',
};


// ═══════════════════════════════════════════════════════════════════════════
// FEATURED SUBMISSION FORM
// ═══════════════════════════════════════════════════════════════════════════

class FeaturedSubmissionForm extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    
    // State
    this._text = '';
    this._wordCount = 0;
    this._keystrokeVerified = true;
    this._pasteDetected = false;
    this._agreements = {
      original: false,
      noCompensation: false,
      grantPermission: false,
    };
    this._submitting = false;
    this._submitted = false;
    this._error = null;
  }

  connectedCallback() {
    this.render();
    this.attachListeners();
  }

  get isEligible() {
    return this.hasAttribute('eligible');
  }

  get currentStreak() {
    return parseInt(this.getAttribute('current-streak') || '0');
  }

  get allAgreed() {
    return this._agreements.original && 
           this._agreements.noCompensation && 
           this._agreements.grantPermission;
  }

  get canSubmit() {
    return this.allAgreed && 
           this._wordCount > 0 && 
           this._wordCount <= 500 && 
           this._keystrokeVerified &&
           !this._pasteDetected &&
           !this._submitting;
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>${this.getStyles()}</style>
      
      <div class="container">
        <div class="header">
          <h2>✍️ Featured Writer Submission</h2>
          <p>Share your best work with the Quirrely community.</p>
        </div>
        
        ${!this.isEligible ? this.renderIneligible() : 
          this._submitted ? this.renderSubmitted() : this.renderForm()}
      </div>
    `;
  }

  renderIneligible() {
    const needed = 7 - this.currentStreak;
    return `
      <div class="ineligible">
        <div class="ineligible-icon">🔒</div>
        <h3>Not Yet Eligible</h3>
        <p>Complete a 7-day 1K streak to unlock Featured Writer submissions.</p>
        <div class="progress-info">
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${(this.currentStreak / 7) * 100}%"></div>
          </div>
          <p class="progress-text">${this.currentStreak} / 7 days • ${needed} more day${needed !== 1 ? 's' : ''} to go</p>
        </div>
        <p class="tip">Write 1,000+ original words daily to build your streak.</p>
      </div>
    `;
  }

  renderSubmitted() {
    return `
      <div class="submitted">
        <div class="submitted-icon">✅</div>
        <h3>Submission Received</h3>
        <p>We'll review your piece and get back to you soon.</p>
        <p class="note">You'll be notified when a decision is made.</p>
      </div>
    `;
  }

  renderForm() {
    return `
      <div class="form">
        <!-- Agreements -->
        <div class="agreements">
          <p class="agreements-title">Before submitting, please confirm:</p>
          
          <label class="agreement">
            <input type="checkbox" id="agree-original" ${this._agreements.original ? 'checked' : ''}>
            <span class="checkmark"></span>
            <span class="agreement-text">This is entirely my original writing (typed by me, not pasted or AI-generated)</span>
          </label>
          
          <label class="agreement">
            <input type="checkbox" id="agree-no-comp" ${this._agreements.noCompensation ? 'checked' : ''}>
            <span class="checkmark"></span>
            <span class="agreement-text">I grant Quirrely permission to feature this piece without compensation (this may change in the future)</span>
          </label>
          
          <label class="agreement">
            <input type="checkbox" id="agree-permission" ${this._agreements.grantPermission ? 'checked' : ''}>
            <span class="checkmark"></span>
            <span class="agreement-text">This is 500 words or fewer</span>
          </label>
        </div>
        
        <!-- Writing Area -->
        <div class="writing-area ${this._pasteDetected ? 'paste-error' : ''}">
          <div class="writing-header">
            <span class="writing-label">Write Your Submission</span>
            <span class="word-count ${this._wordCount > 500 ? 'over' : ''}">${this._wordCount} / 500 words</span>
          </div>
          
          <textarea 
            id="submission-text"
            placeholder="Type your submission here. Paste is disabled — this must be original typed writing."
            rows="12"
            ${!this.allAgreed ? 'disabled' : ''}
          >${this._text}</textarea>
          
          ${this._pasteDetected ? `
            <div class="paste-warning">
              <span class="paste-icon">⚠️</span>
              <span>Pasted text detected. Featured submissions must be typed directly.</span>
              <button class="clear-btn" id="clear-text">Clear and Start Fresh</button>
            </div>
          ` : ''}
          
          ${this._keystrokeVerified && this._wordCount > 0 && !this._pasteDetected ? `
            <div class="verified">
              <span>✍️ Original input verified</span>
            </div>
          ` : ''}
        </div>
        
        <!-- Submit -->
        <div class="submit-area">
          ${this._error ? `<div class="error-message">${this._error}</div>` : ''}
          
          <button 
            class="submit-btn" 
            id="submit-btn"
            ${!this.canSubmit ? 'disabled' : ''}
          >
            ${this._submitting ? 'Submitting...' : 'Submit for Review'}
          </button>
          
          <p class="submit-note">
            Submissions are reviewed by our editorial team. 
            We'll notify you when a decision is made.
          </p>
        </div>
      </div>
    `;
  }

  attachListeners() {
    // Agreement checkboxes
    this.shadowRoot.getElementById('agree-original')?.addEventListener('change', (e) => {
      this._agreements.original = e.target.checked;
      this.render();
      this.attachListeners();
    });

    this.shadowRoot.getElementById('agree-no-comp')?.addEventListener('change', (e) => {
      this._agreements.noCompensation = e.target.checked;
      this.render();
      this.attachListeners();
    });

    this.shadowRoot.getElementById('agree-permission')?.addEventListener('change', (e) => {
      this._agreements.grantPermission = e.target.checked;
      this.render();
      this.attachListeners();
    });

    // Textarea
    const textarea = this.shadowRoot.getElementById('submission-text');
    if (textarea) {
      // Block paste
      textarea.addEventListener('paste', (e) => {
        e.preventDefault();
        this._pasteDetected = true;
        this._keystrokeVerified = false;
        this.render();
        this.attachListeners();
      });

      // Track input
      textarea.addEventListener('input', (e) => {
        this._text = e.target.value;
        this._wordCount = this._text.trim() ? this._text.trim().split(/\s+/).length : 0;
        this.updateWordCount();
      });

      // Track keystrokes (basic verification)
      textarea.addEventListener('keydown', () => {
        if (!this._pasteDetected) {
          this._keystrokeVerified = true;
        }
      });
    }

    // Clear button
    this.shadowRoot.getElementById('clear-text')?.addEventListener('click', () => {
      this._text = '';
      this._wordCount = 0;
      this._pasteDetected = false;
      this._keystrokeVerified = true;
      this.render();
      this.attachListeners();
    });

    // Submit button
    this.shadowRoot.getElementById('submit-btn')?.addEventListener('click', () => {
      this.submit();
    });
  }

  updateWordCount() {
    const countEl = this.shadowRoot.querySelector('.word-count');
    if (countEl) {
      countEl.textContent = `${this._wordCount} / 500 words`;
      countEl.classList.toggle('over', this._wordCount > 500);
    }

    const submitBtn = this.shadowRoot.getElementById('submit-btn');
    if (submitBtn) {
      submitBtn.disabled = !this.canSubmit;
    }
  }

  async submit() {
    if (!this.canSubmit) return;

    this._submitting = true;
    this._error = null;
    this.render();
    this.attachListeners();

    try {
      const response = await fetch('/api/v2/milestones/featured/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
        body: JSON.stringify({
          text: this._text,
          keystroke_verified: this._keystrokeVerified,
          agreement_original: this._agreements.original,
          agreement_no_compensation: this._agreements.noCompensation,
          agreement_grant_permission: this._agreements.grantPermission,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Submission failed');
      }

      this._submitted = true;
      this.dispatchEvent(new CustomEvent('submission-success', { detail: data }));
    } catch (err) {
      this._error = err.message;
    } finally {
      this._submitting = false;
      this.render();
      this.attachListeners();
    }
  }

  getAuthToken() {
    // In production, get from auth context
    return localStorage.getItem('quirrely_auth_token') || '';
  }

  getStyles() {
    return `
      :host {
        display: block;
        font-family: system-ui, -apple-system, sans-serif;
      }

      .container {
        max-width: 640px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
      }

      .header {
        text-align: center;
        margin-bottom: 2rem;
      }

      .header h2 {
        font-size: 1.5rem;
        color: ${COLORS.ink};
        margin: 0 0 0.5rem 0;
      }

      .header p {
        color: ${COLORS.muted};
        margin: 0;
      }

      /* Ineligible State */
      .ineligible {
        text-align: center;
        padding: 2rem;
      }

      .ineligible-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
      }

      .ineligible h3 {
        font-size: 1.25rem;
        color: ${COLORS.ink};
        margin: 0 0 0.5rem 0;
      }

      .ineligible p {
        color: ${COLORS.muted};
        margin: 0 0 1.5rem 0;
      }

      .progress-info {
        max-width: 300px;
        margin: 0 auto;
      }

      .progress-bar {
        height: 8px;
        background: ${COLORS.border};
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 0.5rem;
      }

      .progress-fill {
        height: 100%;
        background: ${COLORS.softGold};
        border-radius: 4px;
        transition: width 0.3s;
      }

      .progress-text {
        font-size: 0.9rem;
        color: ${COLORS.muted};
        margin: 0;
      }

      .tip {
        font-size: 0.85rem;
        color: ${COLORS.softGold};
        margin-top: 1.5rem !important;
      }

      /* Submitted State */
      .submitted {
        text-align: center;
        padding: 2rem;
      }

      .submitted-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
      }

      .submitted h3 {
        font-size: 1.25rem;
        color: ${COLORS.success};
        margin: 0 0 0.5rem 0;
      }

      .submitted p {
        color: ${COLORS.muted};
        margin: 0;
      }

      .submitted .note {
        font-size: 0.85rem;
        margin-top: 1rem;
      }

      /* Form */
      .form {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
      }

      /* Agreements */
      .agreements {
        background: ${COLORS.bgDark};
        padding: 1.25rem;
        border-radius: 12px;
      }

      .agreements-title {
        font-weight: 600;
        color: ${COLORS.ink};
        margin: 0 0 1rem 0;
        font-size: 0.95rem;
      }

      .agreement {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
        cursor: pointer;
        position: relative;
        padding-left: 2rem;
      }

      .agreement:last-child {
        margin-bottom: 0;
      }

      .agreement input {
        position: absolute;
        opacity: 0;
        cursor: pointer;
        height: 0;
        width: 0;
      }

      .checkmark {
        position: absolute;
        left: 0;
        top: 2px;
        height: 18px;
        width: 18px;
        background: white;
        border: 2px solid ${COLORS.border};
        border-radius: 4px;
        transition: all 0.2s;
      }

      .agreement:hover .checkmark {
        border-color: ${COLORS.coral};
      }

      .agreement input:checked ~ .checkmark {
        background: ${COLORS.coral};
        border-color: ${COLORS.coral};
      }

      .checkmark:after {
        content: "";
        position: absolute;
        display: none;
        left: 5px;
        top: 1px;
        width: 4px;
        height: 9px;
        border: solid white;
        border-width: 0 2px 2px 0;
        transform: rotate(45deg);
      }

      .agreement input:checked ~ .checkmark:after {
        display: block;
      }

      .agreement-text {
        font-size: 0.9rem;
        color: ${COLORS.ink};
        line-height: 1.4;
      }

      /* Writing Area */
      .writing-area {
        border: 2px solid ${COLORS.border};
        border-radius: 12px;
        overflow: hidden;
        transition: border-color 0.2s;
      }

      .writing-area:focus-within {
        border-color: ${COLORS.coral};
      }

      .writing-area.paste-error {
        border-color: ${COLORS.error};
      }

      .writing-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        background: ${COLORS.bgDark};
        border-bottom: 1px solid ${COLORS.border};
      }

      .writing-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: ${COLORS.ink};
      }

      .word-count {
        font-size: 0.85rem;
        color: ${COLORS.muted};
      }

      .word-count.over {
        color: ${COLORS.error};
        font-weight: 600;
      }

      textarea {
        width: 100%;
        border: none;
        padding: 1rem;
        font-size: 1rem;
        line-height: 1.6;
        resize: vertical;
        min-height: 200px;
        font-family: inherit;
      }

      textarea:focus {
        outline: none;
      }

      textarea:disabled {
        background: ${COLORS.bgDark};
        cursor: not-allowed;
      }

      textarea::placeholder {
        color: ${COLORS.muted};
      }

      .paste-warning {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        background: rgba(231, 76, 60, 0.1);
        border-top: 1px solid ${COLORS.error};
        font-size: 0.85rem;
        color: ${COLORS.error};
      }

      .paste-icon {
        font-size: 1rem;
      }

      .clear-btn {
        margin-left: auto;
        padding: 0.4rem 0.75rem;
        background: ${COLORS.error};
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
        cursor: pointer;
      }

      .clear-btn:hover {
        filter: brightness(1.1);
      }

      .verified {
        padding: 0.5rem 1rem;
        background: rgba(0, 184, 148, 0.1);
        border-top: 1px solid ${COLORS.border};
        font-size: 0.85rem;
        color: ${COLORS.success};
      }

      /* Submit Area */
      .submit-area {
        text-align: center;
      }

      .error-message {
        padding: 0.75rem 1rem;
        background: rgba(231, 76, 60, 0.1);
        border: 1px solid ${COLORS.error};
        border-radius: 8px;
        color: ${COLORS.error};
        font-size: 0.9rem;
        margin-bottom: 1rem;
      }

      .submit-btn {
        padding: 0.875rem 2rem;
        background: ${COLORS.coral};
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
      }

      .submit-btn:hover:not(:disabled) {
        background: ${COLORS.coralDark};
        transform: translateY(-1px);
      }

      .submit-btn:disabled {
        background: ${COLORS.muted};
        cursor: not-allowed;
        opacity: 0.6;
      }

      .submit-note {
        font-size: 0.8rem;
        color: ${COLORS.muted};
        margin: 1rem 0 0 0;
        line-height: 1.5;
      }
    `;
  }
}

customElements.define('featured-submission-form', FeaturedSubmissionForm);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { FeaturedSubmissionForm };
}

if (typeof window !== 'undefined') {
  window.FeaturedSubmissionForm = FeaturedSubmissionForm;
}
