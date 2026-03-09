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
  var stanceLabelMap = {open:'openness',closed:'certainty',balanced:'balance',contradictory:'complexity'};
  var stanceLabel = stanceLabelMap[s] || s+' quality';
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
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers acknowledge','g'), authorName+' acknowledges');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers acknowledge','g'), authorName+' acknowledges');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers admit','g'), authorName+' admits');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers admit','g'), authorName+' admits');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers aim','g'), authorName+' aims');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers aim','g'), authorName+' aims');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers bring','g'), authorName+' brings');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers bring','g'), authorName+' brings');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers build','g'), authorName+' builds');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers build','g'), authorName+' builds');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers combine','g'), authorName+' combines');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers combine','g'), authorName+' combines');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers craft','g'), authorName+' crafts');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers craft','g'), authorName+' crafts');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers deliver','g'), authorName+' delivers');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers deliver','g'), authorName+' delivers');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers do','g'), authorName+' does');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers do','g'), authorName+' does');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers don't','g'), authorName+' doesn't');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers don't','g'), authorName+' doesn't');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers embrace','g'), authorName+' embraces');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers embrace','g'), authorName+' embraces');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers exhibit','g'), authorName+' exhibits');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers exhibit','g'), authorName+' exhibits');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers explore','g'), authorName+' explores');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers explore','g'), authorName+' explores');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers finish','g'), authorName+' finishes');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers finish','g'), authorName+' finishes');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers give','g'), authorName+' gives');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers give','g'), authorName+' gives');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers have','g'), authorName+' has');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers have','g'), authorName+' has');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers hold','g'), authorName+' holds');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers hold','g'), authorName+' holds');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers lead','g'), authorName+' leads');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers lead','g'), authorName+' leads');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers maintain','g'), authorName+' maintains');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers maintain','g'), authorName+' maintains');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers pack','g'), authorName+' packs');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers pack','g'), authorName+' packs');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers present','g'), authorName+' presents');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers present','g'), authorName+' presents');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers qualify','g'), authorName+' qualifies');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers qualify','g'), authorName+' qualifies');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers show','g'), authorName+' shows');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers show','g'), authorName+' shows');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers sound','g'), authorName+' sounds');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers sound','g'), authorName+' sounds');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers speak','g'), authorName+' speaks');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers speak','g'), authorName+' speaks');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers strip','g'), authorName+' strips');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers strip','g'), authorName+' strips');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers take','g'), authorName+' takes');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers take','g'), authorName+' takes');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers use','g'), authorName+' uses');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers use','g'), authorName+' uses');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers weave','g'), authorName+' weaves');
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers weave','g'), authorName+' weaves');
    h = h.replace(new RegExp('The '+PT+' element','g'), authorName+"'s "+p+" voice");
    h = h.replace(new RegExp('The '+ST+' element','g'), authorName+"'s "+stanceLabel);
    h = h.replace(new RegExp('the '+p+' element','gi'), authorName+"'s "+p+" voice");
    h = h.replace(new RegExp('the '+s+' element','gi'), authorName+"'s "+stanceLabel);
    h = h.replace(new RegExp(p+' writing','gi'), authorName+"'s writing");
    var stanceNouns = {open:'openness',closed:'certainty',balanced:'balance',contradictory:'complexity'};
    var stanceNoun = stanceNouns[s] || s;
    h = h.replace(new RegExp('the '+s+' stance','gi'), lastName+"'s "+stanceNoun);
    h = h.replace(/Writers in this mode are inviting you/g, authorName+' invites you');
    h = h.replace(/writers in this mode are inviting you/g, authorName+' invites you');
    h = h.replace(/Writers in this mode/g, authorName);
    h = h.replace(/writers in this mode/g, authorName);
    h = h.replace(new RegExp('What '+PC+'\\s*\\+\\s*'+SC+' Writers Actually Do','g'), 'What '+authorName+' Actually Does');
    article.innerHTML = h;
  }


  // Render writers section from blog-data.js
  if (entry.type === 'combo' && entry.writers) {
    var wGrid = document.querySelector('.writers-grid');
    var wSect = document.querySelector('.writers');
    var flags = {CA:'🇨🇦',UK:'🇬🇧',AU:'🇦🇺',NZ:'🇳🇿',US:'🇺🇸'};
    var stores = {
      CA:'https://www.chapters.indigo.ca/en-ca/home/search/?keywords=',
      UK:'https://uk.bookshop.org/search?keywords=',
      AU:'https://www.booktopia.com.au/search.ep?keywords=',
      NZ:'https://www.fishpond.co.nz/search?keywords=',
      US:'https://bookshop.org/search?keywords='
    };
    if (!wGrid && wSect) {
      wGrid = document.createElement('div');
      wGrid.className = 'writers-grid';
      wSect.appendChild(wGrid);
    }
    if (wGrid && wSect) {
      var html = '';
      Object.keys(entry.writers).forEach(function(c) {
        var w = entry.writers[c];
        var flag = flags[c] || '';
        var kw = encodeURIComponent(w.writer+' '+w.book);
        var url = (stores[c] || stores.UK) + kw + '&tag=quirrely';
        html += '<div class="writer-card" data-country="'+c+'">'+
          '<span class="writer-flag">'+flag+'</span>'+
          '<div class="writer-info">'+
          '<span class="writer-name">'+w.writer+'</span>'+
          '<span class="writer-book">'+w.book+'</span>'+
          '</div>'+
          '<a href="'+url+'" target="_blank" rel="noopener" class="writer-link">Find Book →</a>'+
          '</div>';
      });
      wGrid.innerHTML = html;
      var note = wSect.querySelector('.writers-note');
      if (note) note.remove();
    }
  }
  // Remove duplicate opening hook para (already in hero)
  if (entry.type !== 'how') {
    var firstP = article.querySelector('p');
    if (firstP) firstP.remove();
  }
})();