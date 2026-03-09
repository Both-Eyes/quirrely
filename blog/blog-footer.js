(function() {
  if (typeof BLOG_DATA === 'undefined') return;
  var slug = location.pathname.replace(/^\/blog\//, '').replace(/\/$/, '');
  var entry = null;
  Object.keys(BLOG_DATA).forEach(function(k) {
    if (BLOG_DATA[k].slug === slug) entry = BLOG_DATA[k];
  });
  if (!entry) return;

  // Remove old hardcoded HOW- footer elements
  var oldCta = document.querySelector('.cta');
  if (oldCta) oldCta.remove();
  var oldRelated = document.querySelector('.related-posts')||document.querySelector('.related');
  var oldCtaRow = document.querySelector('.cta-row');
  if (oldCtaRow) oldCtaRow.remove();
  if (oldRelated) oldRelated.remove();

  // Find paired combo entry
  var comboEntry = entry;
  if (entry.type === 'how') {
    Object.keys(BLOG_DATA).forEach(function(k) {
      if (BLOG_DATA[k].type==='combo' && BLOG_DATA[k].profile===entry.profile && BLOG_DATA[k].stance===entry.stance)
        comboEntry = BLOG_DATA[k];
    });
  }

  var authorName = entry.title.replace('Why You Like ','').replace('Write Like ','').replace("'s Writing Style",'').trim();

  // Build related voices from BLOG_DATA
  var related = [];
  Object.keys(BLOG_DATA).forEach(function(k) {
    var e = BLOG_DATA[k];
    if (e.type !== entry.type) return;
    if (e.slug === entry.slug) return;
    if (e.profile === entry.profile && related.length < 3) related.push(e);
  });
  Object.keys(BLOG_DATA).forEach(function(k) {
    var e = BLOG_DATA[k];
    if (e.type !== entry.type) return;
    if (e.slug === entry.slug) return;
    if (e.profile !== entry.profile && related.length < 6) related.push(e);
  });
  var relHtml = '';
  related.forEach(function(e) {
    var n = e.profile.toUpperCase()+' + '+e.stance.toUpperCase();
    relHtml += '<a href="/blog/'+e.slug+'" class="related-pill" style="background:'+e.color+'20;border:1px solid '+e.color+'40;color:'+e.color+'">'+n+'</a>';
  });

  // Writers link for HOW- posts
  var writersHtml = '';
  if (entry.type === 'how') {
    writersHtml = '<div class="bf-writers-link"><a href="/blog/'+comboEntry.slug+'">📚 See writers in '+authorName+'\'s style →</a></div>';
  }

  // CTA based on auth state
  var ctaHtml = '<div class="bf-cta bf-cta-unauthed"><p>Discover your unique writing voice.</p><a href="/" class="bf-cta-btn">Take the Free Test →</a></div>';
  var s = localStorage.getItem('quirrely_session');
  if (s) {
    ctaHtml = '<div class="bf-cta bf-cta-free"><p>Ready to go deeper?</p><a href="/billing/upgrade.html" class="bf-cta-btn">Upgrade to Pro →</a></div>';
    fetch('/api/v2/user/tier', {headers:{'Authorization':'Bearer '+s}})
      .then(function(r){return r.json();})
      .then(function(d){
        if (d.effective_tier==='pro'||d.effective_tier==='trial') {
          var c = document.getElementById('bf-cta-wrap');
          if (c) c.innerHTML = '<div class="bf-cta bf-cta-pro"><p>Think you write like '+authorName+'?</p><a href="/auth/signup.html?ref=featured" class="bf-cta-btn">Submit to Be a Featured Writer →</a></div>';
        }
      }).catch(function(){});
  }

  var footer = document.createElement('div');
  footer.className = 'blog-footer-block';
  footer.innerHTML = writersHtml +
    '<div class="bf-dowrite"><h2>Do You Write Like You Read?</h2><p>Here\'s an interesting question: does your writing voice match your reading taste? Some people write exactly how they love to read. Others produce prose that surprises them\u2014different from what they consume. If you're curious, analyze your writing — you might discover a perfect match, or a fascinating gap.</p></div>'+'<div id="bf-cta-wrap">'+ctaHtml+'</div>';

  var siteFooter = document.querySelector('.site-footer');
  if (siteFooter) siteFooter.parentNode.insertBefore(footer, siteFooter);
  var writers = document.querySelector('.writers');
  if (writers) {
    var relDiv = document.createElement('div');
    relDiv.innerHTML = '<div class="bf-related"><h3>Explore Related Voices</h3><div class="bf-pills">'+relHtml+'</div></div>';
    writers.parentNode.insertBefore(relDiv, writers);
  }
})();
// Nav auth state
(function(){
  var s=localStorage.getItem('quirrely_session');
  if(!s){
    var si=document.querySelector('.signin-link');
    if(si) si.style.display='none';
  } else {
    var su=document.querySelector('.signup-btn');
    if(su) su.style.display='none';
  }
})();
