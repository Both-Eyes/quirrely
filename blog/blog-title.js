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
  if (entry.type === 'how') {
    var art = document.querySelector('article');
    if (art) {
      var P = PC+' + '+SC;
      art.innerHTML =
'<p>This voice has a signature. Once you see it, you cannot unsee it.</p>'+
        '<h2>What '+P+' Writers Actually Do</h2>'+
        '<p>This writing mode controls two things simultaneously: the strength of its claims and how much space it leaves for the reader. Every sentence is a decision about both. Study any paragraph and you will find the same move repeated — the '+p+' quality establishing the ground, the '+s+' orientation shaping how readers are invited to stand on it.</p>'+
        '<p>This is not accidental. The rhythm has been internalized so completely it feels natural. Your job is to make it conscious before it becomes instinct.</p>'+
        '<h2>The Pattern to Study</h2>'+
        '<p>Read a paragraph of '+P+' writing aloud. Notice where the energy concentrates. Notice what the sentences do after they land. The '+p+' quality shows up in word choice, sentence length, and where claims are placed. The '+s+' orientation shows up in how those claims are framed — what they invite, what they close off, what they leave open.</p>'+
        '<p>The ratio matters. Too much '+p+' without '+s+' and the prose becomes exhausting. Too much '+s+' without '+p+' and it loses its spine. The best writing in this mode holds both at full strength. Find that balance before you make it your own.</p>'+
        '<h2>Why It Works on Readers</h2>'+
        '<p>Readers respond to '+p+' writing because it is clear. They respond to '+authorName+'\'s '+s+' quality because it is honest about what it is doing. Together, these qualities create prose that feels both trustworthy and alive. The reader knows where the writer stands. They also know how the writer wants them to feel standing there.</p>'+
        '<p>This is why '+P+' writing earns loyal readers. It does not perform certainty or perform openness. It enacts both at once.</p>'+
        '<h2>How to Practice It</h2>'+
        '<p>Take a piece of your own writing. Mark every sentence where the '+p+' quality is present. Mark every sentence where the '+s+' orientation is present. Look at the ratio and the sequencing. Now rewrite one paragraph so both qualities appear in every sentence — not alternating, but simultaneous. That is the target.</p>'+
        '<p>Then read it against '+P+' writing you admire. The gap between the two is your curriculum.</p>'+
        '<h2>Where It Goes Wrong</h2>'+
        '<p>Most writers learning this mode default to one quality or the other under pressure. When the argument gets hard, the '+p+' collapses into hedging. When the prose gets comfortable, the '+s+' orientation hardens into something that stops listening. Watch for both failures. The voice only works when both are present at full strength.</p>';
    }
  }
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
    h = h.replace(new RegExp('What '+PC+'\\s*\\+\\s*'+SC+' Writers Actually Do','g'), 'What '+authorName+' Actually Does');
    article.innerHTML = h;
  }


  // Remove duplicate opening hook para (already in hero)
  if (entry.type !== 'how') {
    var firstP = article.querySelector('p');
    if (firstP) firstP.remove();
  }
})();