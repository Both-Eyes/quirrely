/**
 * LNCP Classifier - API Proxy v2.0.0
 * Analysis runs server-side. No IP exposed client-side.
 */

const LNCP = {
  async classifyProfile(text) {
    if (!text || text.trim().length < 20) {
      return { error: 'Text too short for analysis (minimum 20 characters)' };
    }

    try {
      const response = await fetch('https://api.quirrely.com/api/quick-analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Extension-Version': '2.0.0'
        },
        body: JSON.stringify({ text: text.trim() })
      });

      if (!response.ok) {
        if (response.status === 429) return { error: 'Daily limit reached', limitReached: true };
        if (response.status === 401) return { error: 'Authentication required', authRequired: true };
        return { error: `Analysis failed (${response.status})` };
      }

      const data = await response.json();
      const p = data.primary_profile;

      return {
        profileId:    p.profile_id,
        profileType:  p.profile_name.toUpperCase().replace(/\s+/g, '_'),
        title:        p.profile_name,
        tagline:      `${p.style} · ${p.certitude}`,
        icon:         '✦',
        stance:       p.certitude,
        confidence:   p.confidence,
        signature:    data.category_scores,
        metrics: {
          wordCount:     data.word_count,
          sentenceCount: data.sentence_count,
          textLength:    data.text_length
        },
        analyzedAt: new Date().toISOString(),
        source: 'api'
      };

    } catch (error) {
      console.warn('LNCP API error:', error);
      return { error: 'Unable to reach Quirrely API. Check your connection.' };
    }
  }
};
