(function() {
  if (typeof BLOG_DATA === 'undefined') return;
  var slug = location.pathname.replace(/^\/blog\//, '').replace(/\/$/, '');
  var key = slug.replace(/^how-(.+)-writers-write$/, 'HOW-$1').toUpperCase().replace(/-/g, '-');
  if (slug.startsWith('how-')) {
    key = 'HOW-' + slug.replace(/^how-/, '').replace(/-writers-write$/, '').toUpperCase();
  } else {
    key = slug.toUpperCase();
  }
  var entry = BLOG_DATA[key];
  if (!entry) return;
  document.title = entry.title + ' | Quirrely';
  var h1 = document.querySelector('h1');
  if (h1) h1.textContent = entry.title;
})();
