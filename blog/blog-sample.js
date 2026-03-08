(function() {
  if (typeof BLOG_DATA === 'undefined') return;
  var slug = location.pathname.replace(/^\/blog\//, '').replace(/\/$/, '');
  var entry = null;
  Object.keys(BLOG_DATA).forEach(function(k) {
    if (BLOG_DATA[k].slug === slug) entry = BLOG_DATA[k];
  });
  if (!entry) return;

  var author = entry.writers && entry.writers.UK ? entry.writers.UK : null;
  if (!entry.writers && entry.type === 'how') {
    var comboKey = null;
    Object.keys(BLOG_DATA).forEach(function(k) {
      if (BLOG_DATA[k].type==='combo' && BLOG_DATA[k].profile===entry.profile && BLOG_DATA[k].stance===entry.stance)
        comboKey = k;
    });
    if (comboKey) author = BLOG_DATA[comboKey].writers && BLOG_DATA[comboKey].writers.UK ? BLOG_DATA[comboKey].writers.UK : null;
  }
  if (!author) return;

  var PROFILE_PATTERNS = {
    assertive:      ['The answer is clear.','This is what matters.','There is no ambiguity here.','The evidence points one way.'],
    minimal:        ['One word. Then silence.','Nothing wasted.','The page breathes.','Less. Always less.'],
    poetic:         ['The light fell differently that morning.','Words arrived like weather.','Something shifted in the telling.','The sentence curved back on itself.'],
    dense:          ['The argument accumulates, layer upon layer, each clause bearing the weight of what preceded it.','To understand one thing fully requires understanding everything adjacent to it.'],
    conversational: ['You know that feeling? When something just clicks?','Here\'s the thing nobody tells you.','It\'s simpler than you think — and harder.'],
    formal:         ['One must consider the implications carefully.','The matter requires sustained attention.','Precision here is not pedantry — it is respect.'],
    balanced:       ['Both things can be true.','The tension holds without resolving.','Neither side owns the full picture.'],
    longform:       ['The story accumulates slowly, finding its shape only in retrospect.','Time moves differently in this kind of writing — expansive, patient, unhurried.'],
    interrogative:  ['But why does this work? What is actually happening here?','The question opens outward rather than closing down.','What are we really asking when we ask this?'],
    hedged:         ['Perhaps. Or perhaps not.','Something like certainty, but softer.','The claim arrives gently, aware of its own limits.']
  };

  var STANCE_MODIFIERS = {
    open:           'Then the door opens. "What do you think?" The writer genuinely wants to know.',
    closed:         'The writer does not wait for your agreement. The statement stands alone.',
    balanced:       'The prose holds its ground without insisting. You may disagree. That is permitted.',
    contradictory:  'Then the opposite arrives. Both are true. Neither cancels the other.'
  };

  var profileSents = PROFILE_PATTERNS[entry.profile] || PROFILE_PATTERNS.assertive;
  var stanceMod = STANCE_MODIFIERS[entry.stance] || '';
  var seed = profileSents[Math.floor(entry.title.length % profileSents.length)];
  var why = author.why || '';
  var sample = seed + ' ' + stanceMod + ' ' + why;

  var analysis = entry.type === 'how'
    ? 'Notice the technique: ' + why + ' That\'s the move to study and make your own.'
    : 'This is what draws you to ' + author.writer + ': ' + why + ' Your reading taste recognises this pattern instinctively.';

  var container = document.createElement('div');
  container.className = 'sample-block';
  container.innerHTML =
    '<h2>A Passage in the Style of ' + author.writer + '</h2>' +
    '<blockquote class="sample-quote">' + sample + '</blockquote>' +
    '<p class="sample-analysis">' + analysis + '</p>';

  var article = document.querySelector('article');
  if (article) article.appendChild(container);
})();
