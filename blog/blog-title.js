(function() {
  if (typeof BLOG_DATA === 'undefined') return;
  var slug = location.pathname.replace(/^\/blog\//, '').replace(/\/$/, '');
  var entry = null;
  Object.keys(BLOG_DATA).forEach(function(k) {
    if (BLOG_DATA[k].slug === slug) entry = BLOG_DATA[k];
  });
  if (!entry) return;
  document.title = entry.title + ' | Quirrely';
  var h1 = document.querySelector('h1');
  if (h1) h1.textContent = entry.title;
  var hook = document.querySelector('.hero .hook');
  if (hook) hook.textContent = entry.excerpt;
  var label = document.querySelector('.hero-label');
  if (label) label.textContent = entry.type === 'how' ? 'Write Like' : 'Your Reading Taste';
  var badges = document.querySelectorAll('.hero .badges .badge');
  if (badges.length >= 3) {
    badges[0].textContent = entry.profile ? entry.profile.toUpperCase() : '';
    badges[1].textContent = entry.stance ? entry.stance.toUpperCase() : '';
    badges[2].textContent = entry.type === 'how' ? 'Writing Voice' : 'Reading Profile';
  }
})();
