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

  if (entry.type === 'combo') {
    var titleWords = entry.title.replace('Why You Like ', '');
    var authorName = titleWords.replace("'s Writing Style", '').trim();
    var lastName = authorName.split(' ').pop();
    var profile = entry.profile.toUpperCase();
    var stance = entry.stance.toUpperCase();
    var article = document.querySelector('article');
    if (article) {
      article.innerHTML = article.innerHTML.replace(
        new RegExp(profile + ' \\+ ' + stance + ' writers', 'g'),
        authorName
      );
      article.innerHTML = article.innerHTML.replace(
        new RegExp(profile + ' \\+ ' + stance + ' writing', 'g'),
        authorName + "'s writing"
      );
    }
  }
})();
