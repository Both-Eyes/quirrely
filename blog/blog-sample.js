(function() {
  if (typeof BLOG_DATA === 'undefined' || typeof BLOG_SAMPLES === 'undefined') return;
  var slug = location.pathname.replace(/^\/blog\//, '').replace(/\/$/, '');
  var entry = null;
  Object.keys(BLOG_DATA).forEach(function(k) {
    if (BLOG_DATA[k].slug === slug) entry = BLOG_DATA[k];
  });
  if (!entry) return;
  var comboEntry = entry;
  if (entry.type === 'how') {
    Object.keys(BLOG_DATA).forEach(function(k) {
      if (BLOG_DATA[k].type==='combo' && BLOG_DATA[k].profile===entry.profile && BLOG_DATA[k].stance===entry.stance)
        comboEntry = BLOG_DATA[k];
    });
  }
  var author = comboEntry.writers && comboEntry.writers.UK ? comboEntry.writers.UK : null;
  if (!author) return;
  var sample = BLOG_SAMPLES[entry.profile+'+'+entry.stance] || '';
  if (!sample) return;
  var analysis = entry.type === 'how'
    ? 'Notice what '+author.writer+' does here: '+author.why+' Study the structure — then make it yours.'
    : 'This is the quality that draws you to '+author.writer+'. '+author.why+' Your reading instinct recognised it before your critical mind could name it.';
  var el = document.createElement('div');
  el.className = 'sample-block';
  el.innerHTML = '<h2>In the Style of '+author.writer+'</h2><blockquote class="sample-quote">'+sample+'</blockquote><p class="sample-analysis">'+analysis+'</p>';
  var article = document.querySelector('article');
  if (article) article.parentNode.insertBefore(el, article);
})();
