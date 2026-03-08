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
  if (label) label.textContent = entry.type === 'how' ? 'Write Like' : 'Why You\'ll Love This';
  var badges = document.querySelectorAll('.hero .badges .badge');
  if (badges.length >= 3) {
    badges[0].textContent = entry.profile ? entry.profile.toUpperCase() : '';
    badges[1].textContent = entry.stance ? entry.stance.toUpperCase() : '';
    badges[2].textContent = entry.type === 'how' ? 'Writing Voice' : 'Reading Profile';
  }

  var authorName = entry.title
    .replace('Why You Like ', '')
    .replace('Write Like ', '')
    .replace("'s Writing Style", '').trim();
  var lastName = authorName.split(' ').pop();
  var p = entry.profile, s = entry.stance;
  var article = document.querySelector('article');
  if (article) {
    var h = article.innerHTML;
    var caps = p.toUpperCase() + ' \\+ ' + s.toUpperCase();
    var title = p.charAt(0).toUpperCase()+p.slice(1) + ' \\+ ' + s.charAt(0).toUpperCase()+s.slice(1);
    var lower = p + ' \\+ ' + s;
    h = h.replace(new RegExp(caps + ' writers', 'g'), authorName);
    h = h.replace(new RegExp(caps + ' writing', 'g'), authorName + "'s writing");
    h = h.replace(new RegExp(title + ' writers', 'g'), authorName);
    h = h.replace(new RegExp(title + ' writing', 'g'), authorName + "'s writing");
    h = h.replace(new RegExp(title + ' prose', 'g'), authorName + "'s prose");
    h = h.replace(new RegExp(title + ' voices', 'g'), authorName + "'s voice");
    h = h.replace(new RegExp(lower + ' voices', 'g'), authorName + "'s voice");
    h = h.replace(new RegExp(lower + ' writing', 'g'), authorName + "'s writing");
    h = h.replace(new RegExp(lower + ' prose', 'g'), authorName + "'s prose");
    h = h.replace(new RegExp('assertive writing', 'gi'), lastName + "'s writing");
    h = h.replace(new RegExp('the open stance', 'gi'), lastName + "'s openness");
    article.innerHTML = h;
  }
})();
