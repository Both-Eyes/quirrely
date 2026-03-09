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
  var profileTexture = {
    minimal: 'strips language back to what matters — no word survives that does not earn its place',
    assertive: 'takes a position and holds it — every sentence knows where it stands',
    poetic: 'moves through language the way weather moves — felt before it is understood',
    dense: 'rewards slow, careful attention — the meaning accumulates across sentences',
    conversational: 'thinks alongside you rather than at you — the distance between writer and reader disappears',
    formal: 'carries the weight of considered authority — nothing here is casual or accidental',
    balanced: 'holds competing views without flinching — it earns its conclusions by refusing the easy ones',
    longform: 'builds meaning through accumulation — each paragraph adds to something larger than itself',
    interrogative: 'opens questions rather than closing them — the asking is the point',
    hedged: 'keeps its certainty honest — it says what it knows and no more'
  };
  var stanceTexture = {
    open: 'makes space for your response — it is writing that wants to be argued with',
    closed: 'has already decided, and earns that confidence — there is no invitation to negotiate',
    balanced: 'refuses easy resolution — it holds all sides long enough to see what each one costs',
    contradictory: 'holds opposites at full strength simultaneously — the tension is the point, not a problem to solve'
  };
  var profileHow = {
    minimal: 'Every surplus word has been removed. What remains is load-bearing. The sentences do not decorate — they decide.',
    assertive: 'Claims arrive without apology. The sentences land and do not retreat. There is no hedging, no softening, no invitation to disagree.',
    poetic: 'The language draws attention to itself without becoming ornamental. Sound and rhythm carry meaning. The surface is part of the content.',
    dense: 'The sentences are built for compression. Each clause adds information. Reading slowly is not optional — it is the intended speed.',
    conversational: 'The register is informal but the thinking is precise. Contractions, asides, and direct address create intimacy without sacrificing intelligence.',
    formal: 'The structure is deliberate and the vocabulary is exact. Nothing is left to implication. The reader is addressed as a serious person.',
    balanced: 'Every significant counterargument gets its hearing. The writer does not defeat the opposition — they represent it fairly before moving on.',
    longform: 'The argument unfolds across paragraphs rather than within them. Patience is required and rewarded. The conclusion earns its weight.',
    interrogative: 'Questions do the structural work that statements do elsewhere. The form enacts the uncertainty rather than just describing it.',
    hedged: 'Qualifiers are not weakness — they are precision. The writer knows the difference between what is established and what is inferred.'
  };
  var stanceHow = {
    open: 'After every move, there is space. The prose invites response — not as a rhetorical gesture but as a genuine structural feature.',
    closed: 'The prose does not wait for agreement. It states, develops, and concludes. The reader is a witness, not a participant.',
    balanced: 'Opposing positions receive equal development. The writer does not tip their hand early. Resolution, if it comes, comes late.',
    contradictory: 'Contradictions are named and held rather than resolved. The prose treats tension as content — something to inhabit, not escape.'
  };
  var pTex = profileTexture[p] || p+' prose';
  var sTex = stanceTexture[s] || s+' orientation';
  var pHow = profileHow[p] || 'The '+p+' quality shapes every sentence.';
  var sHow = stanceHow[s] || 'The '+s+' orientation shapes how the reader is positioned.';
  if (entry.type === 'how') {
    var art = document.querySelector('article');
    if (art) {
      var P = PC+' + '+SC;
      art.innerHTML =
        '<p>'+authorName+' has a signature. Once you see it, you cannot unsee it.</p>'+
        '<h2>What '+authorName+' Actually Does</h2>'+
        '<p>This voice '+pTex+'. At the same time, it '+sTex+'. These two qualities are not in tension — they are the combination. Every sentence enacts both simultaneously, and that is what makes the mode recognisable across everything '+authorName+' writes.</p>'+
        '<p>'+pHow+' '+sHow+' The result is prose with a consistent fingerprint — one you can learn to produce deliberately once you understand how it is built.</p>'+
        '<h2>The Pattern to Study</h2>'+
        '<p>Read a paragraph of '+authorName+' aloud. Notice where the energy concentrates and where it releases. The '+p+' quality shows up in word choice, sentence length, and where claims are placed. The '+s+' orientation shows up in what happens after those claims land — what the prose invites, what it closes off, what room it leaves.</p>'+
        '<p>The ratio matters. Too much '+p+' without the '+s+' orientation and the prose becomes one-note. Too much '+s+' without the '+p+' quality and it loses its character. The best writing in this mode holds both at full strength. Study where '+authorName+' finds that balance — it will not be where you expect.</p>'+
        '<h2>Why It Works on Readers</h2>'+
        '<p>Readers respond to this voice because it is consistent. They always know what kind of attention it is asking for. The '+p+' quality establishes the register; the '+s+' orientation establishes the relationship. Together they create prose that feels both trustworthy and alive — readers know where the writer stands and how the writer wants them to feel standing there.</p>'+
        '<p>This is why '+P+' writing earns loyal readers. It does not perform its qualities. It enacts them, sentence by sentence, without slipping.</p>'+
        '<h2>How to Practice It</h2>'+
        '<p>Take a piece of your own writing. Read each sentence and ask: where is the '+p+' quality? Where is the '+s+' orientation? Mark both. Look at the ratio and the sequencing. Now rewrite one paragraph so both qualities appear in every sentence — not alternating, but simultaneous. That is the target.</p>'+
        '<p>Then read it against '+authorName+'. The gap between the two drafts is your curriculum. Do not close it too fast — understanding why the gap exists is more useful than closing it.</p>'+
        '<h2>Where It Goes Wrong</h2>'+
        '<p>Writers learning this mode tend to default to one quality under pressure. When the argument gets hard, the '+p+' softens into qualification. When the prose gets comfortable, the '+s+' orientation stiffens into something that has stopped listening. Both failures produce writing that looks like this mode but does not feel like it.</p>'+
        '<p>The test is simple: read the paragraph back and ask whether both qualities are still present at full strength. If one has retreated, the voice has collapsed. Rewrite until they are both there, together, in every sentence.</p>'
    }
  }
  var article = document.querySelector('article');
  if (article) {
    if (entry.type === 'combo') {
      var P2 = PT+' + '+ST;
      article.innerHTML =
        '<h2>What This Voice Feels Like</h2>'+
        '<p>Reading '+authorName+' does something specific: it '+pTex+'. This is not a style you stumbled into — it is one your reading instincts were already looking for. The prose '+sTex+'. Together these qualities create a reading experience that feels both deliberate and inevitable.</p>'+
        '<p>Readers who connect with this voice often describe the same thing: a sense that the writing is operating at exactly the right register. The '+p+' quality and the '+s+' orientation are calibrated to each other. That calibration is what you are responding to.</p>'+
        '<h2>Why Some Readers Are Drawn Here</h2>'+
        '<p>Not every reader finds this combination satisfying. Some want more warmth, more uncertainty, more room to push back. But you are drawn here because this voice commits. The '+p+' quality means the writing has a spine. The '+s+' orientation means it knows what to do with that spine.</p>'+
        '<p>Readers who love this mode often read widely but return to it. It is a home register — the one that feels most true, most like the inside of a mind that works the way yours does. '+authorName+' is one of its finest practitioners, but the taste runs deeper than any single writer.</p>'+
        '<h2>Your Reading Taste</h2>'+
        '<p>Knowing what draws you to '+p+' writing with a '+s+' orientation is genuinely useful. It explains why certain books grip you immediately while others, equally praised, leave you cold. The difference is usually this: the books that grip you share this structural fingerprint.</p>'+
        '<p>It also tells you where to look next. The writers below make the same fundamental choices '+authorName+' makes — not the same subjects or settings, but the same decisions about how to hold a reader. That is the thing that travels across genres and decades.</p>'+
        '<p>The fact that you are drawn to '+P2+' writing now probably means you have always been, even before you had words for it. Reading taste has a core that is more stable than most people realise.</p>'+
        '<h2>Finding More Writing Like This</h2>'+
        '<p>The fingerprint of '+p+' writing with a '+s+' orientation shows up in sentence-level decisions: how claims are made, how the reader is addressed, what the prose closes off and what it leaves open. Once you can name it, you will notice it everywhere — in journalism, in essays, in writers you have not yet read.</p>'+
        '<p>Start with the writers below. Each shares the structural DNA of this voice while bringing their own place, their own obsessions, their own rhythm. The regional links go to local booksellers. The book in your hands is always better than the book on a list.</p>';
    }
    var h = article.innerHTML;
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers bring','g'), authorName+' brings');
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writing','g'), authorName+"'s writing");
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' prose','g'), authorName+"'s prose");
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' voices','g'), authorName+"'s voice");
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers bring','g'), authorName+' brings');
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
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+" writers don't","g"), authorName+" doesn't");
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+" writers don't","g"), authorName+" doesn't");
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
    h = h.replace(new RegExp(PC+'\\s*\\+\\s*'+SC+' writers','g'), authorName);
    h = h.replace(new RegExp(PT+'\\s*\\+\\s*'+ST+' writers','g'), authorName);
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

})();