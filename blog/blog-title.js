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
  var authorName = entry.title.replace('Why You Like ','').replace('Write Like ','').replace("'s Writing Style",'').trim();
  var lastName = authorName.split(' ').pop();
  var p = entry.profile, s = entry.stance;
  var PC = p.toUpperCase(), SC = s.toUpperCase();
  var PT = p.charAt(0).toUpperCase()+p.slice(1), ST = s.charAt(0).toUpperCase()+s.slice(1);
  var article = document.querySelector('article');
  if (article) {
    var h = article.innerHTML;
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers bring','g'), authorName+' brings');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers','g'), authorName);
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writing','g'), authorName+"'s writing");
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' prose','g'), authorName+"'s prose");
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' voices','g'), authorName+"'s voice");
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers bring','g'), authorName+' brings');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers','g'), authorName);
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writing','g'), authorName+"'s writing");
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' prose','g'), authorName+"'s prose");
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' voices','g'), authorName+"'s voice");
    h = h.replace(new RegExp(p+'\\s*\\+\\s*'+s+' voices','g'), authorName+"'s voice");
    h = h.replace(new RegExp(p+'\\s*\\+\\s*'+s+' writing','g'), authorName+"'s writing");
    h = h.replace(new RegExp(p+'\\s*\\+\\s*'+s+' prose','g'), authorName+"'s prose");
    h = h.replace(new RegExp('The '+PT+' element','g'), authorName+"'s "+p+" voice");
    h = h.replace(new RegExp('The '+ST+' element','g'), authorName+"'s "+s+" quality");
    h = h.replace(new RegExp('the '+p+' element','gi'), authorName+"'s "+p+" voice");
    h = h.replace(new RegExp('the '+s+' element','gi'), authorName+"'s "+s+" quality");
    h = h.replace(new RegExp(p+' writing','gi'), authorName+"'s writing");
    h = h.replace(new RegExp('the '+s+' stance','gi'), lastName+"'s openness");
    h = h.replace(/Writers in this mode are inviting you/g, authorName+' invites you');
    h = h.replace(/writers in this mode are inviting you/g, authorName+' invites you');
    h = h.replace(/Writers in this mode/g, authorName);
    h = h.replace(/writers in this mode/g, authorName);
    article.innerHTML = h;
  }

})();