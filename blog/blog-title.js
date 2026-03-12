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
  if (hook) hook.textContent = entry.excerpt || '';
  var label = document.querySelector('.hero-label');
  if (label) label.textContent = (entry.country ? entry.country + ' · ' : '') + 'Writing Style';
  var badges = document.querySelectorAll('.hero .badges .badge');
  if (badges.length >= 1) badges[0].textContent = entry.profile ? entry.profile.toUpperCase() : '';
  if (badges.length >= 2) badges[1].textContent = entry.stance ? entry.stance.toUpperCase() : '';
  if (badges.length >= 3) badges[2].textContent = 'Reading Profile';

  // Set author color as CSS variable on article
  if (entry.color) {
    document.documentElement.style.setProperty('--author-color', entry.color);
  }
  var article = document.querySelector('article');
  if (article && typeof BLOG_BODY !== 'undefined' && BLOG_BODY[slug]) {
    article.innerHTML = '<div class="article-body">' + BLOG_BODY[slug] + '</div>';
  }

  if (entry.writers) {
    var wGrid = document.querySelector('.writers-grid');
    var flags = {CA:'🇨🇦',UK:'🇬🇧',AU:'🇦🇺',NZ:'🇳🇿',US:'🇺🇸'};
    var stores = {
      CA:'https://www.chapters.indigo.ca/en-ca/home/search/?keywords=',
      UK:'https://uk.bookshop.org/search?keywords=',
      AU:'https://www.booktopia.com.au/search.ep?keywords=',
      NZ:'https://www.fishpond.co.nz/search?keywords=',
      US:'https://bookshop.org/search?keywords='
    };
    var storeNames={CA:'Indigo',UK:'Bookshop.org',AU:'Booktopia',NZ:'Whitcoulls'};
    if (wGrid) {
      var html = '';
      Object.keys(entry.writers).forEach(function(c) {
        var w = entry.writers[c];
        var flag = flags[c] || '';
        var kw = encodeURIComponent(w.writer + ' ' + w.book);
        var url = (stores[c] || stores.UK) + kw + '&tag=quirrely';
        var storeName = storeNames[c] || 'Find Book';
        html += '<a href="' + url + '" target="_blank" rel="noopener" class="writer-card" data-country="' + c + '" style="border-left-color:' + (entry.color||'var(--primary)') + ';background:' + (entry.color||'#ccc') + '15;">' +
          '<span class="writer-flag">' + flag + '</span>' +
          '<div class="writer-info">' +
          '<span class="writer-name">' + w.writer + '</span>' +
          '<span class="writer-book">' + w.book + '</span>' +
          '</div>' +
          '<span class="writer-store">' + storeName + ' →</span>' +
          '</a>';
      });
      wGrid.innerHTML = html;
    }
  }
})();
