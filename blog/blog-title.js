(function() {
  if (typeof BLOG_DATA === 'undefined') return;
  var slug = location.pathname.replace(/^\/blog\//, '').replace(/\/$/, '');
  var entry = null;
  Object.keys(BLOG_DATA).forEach(function(k) {
    if (BLOG_DATA[k].slug === slug) entry = BLOG_DATA[k];
  });
  if (!entry) return;

  // ═══════════════════════════════════════════════════════════
  // SEO META INJECTION
  // ═══════════════════════════════════════════════════════════

  var pageTitle = entry.title + ' | Quirrely';
  var pageDesc = entry.excerpt || 'Explore this writing voice profile on Quirrely.';
  var pageUrl = 'https://quirrely.ca/blog/' + entry.slug;
  var profileKey = (entry.profile || 'conversational').toLowerCase();
  var ogImage = 'https://quirrely.ca/og/' + profileKey + '.png';
  var authorName = entry.title.replace(/^In the Style of /, '');

  // Title
  document.title = pageTitle;

  // Helper: set or create meta tag
  function setMeta(attr, attrVal, content) {
    var sel = 'meta[' + attr + '="' + attrVal + '"]';
    var el = document.querySelector(sel);
    if (!el) {
      el = document.createElement('meta');
      el.setAttribute(attr, attrVal);
      document.head.appendChild(el);
    }
    el.setAttribute('content', content);
  }

  // Meta description
  setMeta('name', 'description', pageDesc);

  // Open Graph
  setMeta('property', 'og:title', pageTitle);
  setMeta('property', 'og:description', pageDesc);
  setMeta('property', 'og:url', pageUrl);
  setMeta('property', 'og:image', ogImage);
  setMeta('property', 'og:image:width', '1200');
  setMeta('property', 'og:image:height', '630');
  setMeta('property', 'og:type', 'article');
  setMeta('property', 'og:site_name', 'Quirrely');
  setMeta('property', 'og:locale', 'en_CA');

  // Twitter Card
  setMeta('name', 'twitter:card', 'summary_large_image');
  setMeta('name', 'twitter:title', pageTitle);
  setMeta('name', 'twitter:description', pageDesc);
  setMeta('name', 'twitter:image', ogImage);
  setMeta('name', 'twitter:site', '@quirrelyca');

  // Canonical URL
  var canonical = document.querySelector('link[rel="canonical"]');
  if (!canonical) {
    canonical = document.createElement('link');
    canonical.setAttribute('rel', 'canonical');
    document.head.appendChild(canonical);
  }
  canonical.setAttribute('href', pageUrl);

  // Robots
  setMeta('name', 'robots', 'index, follow');

  // JSON-LD Structured Data — Article schema
  var jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    'headline': entry.title,
    'description': pageDesc,
    'url': pageUrl,
    'image': ogImage,
    'author': {
      '@type': 'Organization',
      'name': 'Quirrely',
      'url': 'https://quirrely.ca'
    },
    'publisher': {
      '@type': 'Organization',
      'name': 'Quirrely',
      'url': 'https://quirrely.ca',
      'logo': {
        '@type': 'ImageObject',
        'url': 'https://quirrely.ca/assets/logo/favicon.svg'
      }
    },
    'mainEntityOfPage': {
      '@type': 'WebPage',
      '@id': pageUrl
    },
    'about': {
      '@type': 'Thing',
      'name': authorName + ' writing style',
      'description': 'Analysis of ' + authorName + '\'s writing voice: ' + (entry.profile || '') + ', ' + (entry.stance || '') + ' stance.'
    },
    'keywords': [
      authorName,
      'writing style',
      'voice profile',
      entry.profile || '',
      entry.stance || '',
      'writing analysis',
      'Quirrely'
    ].filter(function(k) { return k; }).join(', '),
    'inLanguage': 'en',
    'isAccessibleForFree': true,
  };

  // Add country if available
  var countryNames = {CA:'Canada',UK:'United Kingdom',AU:'Australia',NZ:'New Zealand',US:'United States',IE:'Ireland',ZA:'South Africa',IN:'India',WS:'Samoa'};
  if (entry.country && countryNames[entry.country]) {
    jsonLd.about.description += ' ' + countryNames[entry.country] + ' literature.';
    jsonLd.keywords += ', ' + countryNames[entry.country] + ' literature';
  }

  var ldScript = document.createElement('script');
  ldScript.type = 'application/ld+json';
  ldScript.textContent = JSON.stringify(jsonLd);
  document.head.appendChild(ldScript);

  // ═══════════════════════════════════════════════════════════
  // VISUAL CONTENT (existing engine logic)
  // ═══════════════════════════════════════════════════════════

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
