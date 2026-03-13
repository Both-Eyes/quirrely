/**
 * QUIRRELY STRETCH ENGINE v1.0
 * 3 cycles x 3 prompts, powered by AUTHOR_VOICE
 * Requires: blog-author-voice.js (AUTHOR_VOICE), dashboard-books.js (DASH_BOOKS)
 */
var STRETCH_ENGINE = (function(){
  var STARTERS = [
    "The morning began the way most mornings do — with a small lie.",
    "She had not planned to return, but the letter changed everything.",
    "There is a particular quality to light just before it rains.",
    "The house had been empty for years, though no one could say exactly how many.",
    "He spoke carefully, the way people do when they know they are being recorded.",
    "What I remember most is not the event itself but the silence after.",
    "The town was the kind of place people described by what it lacked.",
    "It was the sort of decision that only makes sense in retrospect.",
    "They met at the wrong time, which is to say they met at the only time possible.",
  ];
  var INSTRUCTIONS = {
    1: [
      "Read the technique below. Then write 2-3 sentences (30-50 words) that attempt this quality. Don't force it — just notice what changes in your writing when you try.",
      "Write a short paragraph (50-80 words) using the story starter. Let the technique guide how you shape the sentences, not what you say.",
      "Now write freely (80-120 words) continuing from where you left off. The technique should feel less like a rule and more like a habit forming.",
    ],
    2: [
      "This is a different aspect of the same voice. Write 2-3 sentences (30-50 words) experimenting with this quality. Notice how it feels different from Cycle 1.",
      "Use the story starter below. Write 50-80 words where this technique drives the rhythm and structure of your prose.",
      "Continue writing (80-120 words). Try to let both techniques — this one and the previous cycle's — coexist in your writing naturally.",
    ],
    3: [
      "Final cycle. This technique completes the voice. Write 2-3 sentences (30-50 words) trying it on.",
      "Use the story starter. Write 50-80 words blending all three techniques you've practised. This is where the voice comes together.",
      "Write 100-150 words in this author's full voice. Use everything you've practised. The goal isn't imitation — it's expansion. You're adding range.",
    ],
  };

  function matchAction(sent, cycleIdx) {
    if (typeof STRETCH_ACTIONS === 'undefined') return null;
    for (var i = 0; i < STRETCH_ACTIONS.length; i++) {
      if (STRETCH_ACTIONS[i].p.test(sent)) {
        return {name: STRETCH_ACTIONS[i].t, action: STRETCH_ACTIONS[i].a[cycleIdx] || STRETCH_ACTIONS[i].a[0]};
      }
    }
    return null;
  }

  function getPrompts(authorName) {
    if (typeof AUTHOR_VOICE === 'undefined') return null;
    var sents = AUTHOR_VOICE[authorName];
    if (!sents || sents.length < 3) return null;

    var cycles = [];
    for (var cy = 0; cy < 3; cy++) {
      var technique = sents[Math.min(cy, sents.length - 1)];
      var matched = matchAction(technique, cy);
      var prompts = [];
      for (var pr = 0; pr < 3; pr++) {
        var si = (cy * 3 + pr) % STARTERS.length;
        prompts.push({
          cycle: cy + 1,
          prompt: pr + 1,
          technique: technique,
          techniqueName: matched ? matched.name : 'Voice Technique',
          action: matched ? matched.action : INSTRUCTIONS[cy + 1][pr],
          instruction: INSTRUCTIONS[cy + 1][pr],
          starter: STARTERS[si],
          wordMin: [30, 50, 80][pr] + (cy * 20),
          wordTarget: [50, 80, 120][pr] + (cy * 30),
        });
      }
      cycles.push({cycle: cy + 1, technique: technique, techniqueName: matched ? matched.name : 'Voice Technique', prompts: prompts});
    }
    return {author: authorName, cycles: cycles, totalPrompts: 9};
  }

  function findAuthorName(slug) {
    if (typeof AUTHOR_VOICE === 'undefined') return null;
    var target = slug.replace(/-writing-style$/, '');
    for (var name in AUTHOR_VOICE) {
      var ns = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      if (ns === target) return name;
    }
    return null;
  }


  // === PERSISTENCE ===
  var SK = 'quirrely_stretch_';
  function _k(a){return SK+a.replace(/[^a-zA-Z0-9]/g,'_');}
  function saveProgress(a,pos,inputs){
    try{localStorage.setItem(_k(a),JSON.stringify({pos:pos,inputs:inputs,ts:Date.now()}));}catch(e){}
  }
  function loadProgress(a){
    try{var d=JSON.parse(localStorage.getItem(_k(a)));
    if(!d||!d.pos)return null;
    if(Date.now()-d.ts>7*24*3600*1000){localStorage.removeItem(_k(a));return null;}
    return d;}catch(e){return null;}
  }
  function clearProgress(a){try{localStorage.removeItem(_k(a));}catch(e){}}
  function markComplete(a){
    try{var done=JSON.parse(localStorage.getItem(SK+'_done')||'[]');
    if(done.indexOf(a)===-1)done.push(a);
    localStorage.setItem(SK+'_done',JSON.stringify(done));
    clearProgress(a);}catch(e){}
  }
  function getCompleted(){
    try{return JSON.parse(localStorage.getItem(SK+'_done')||'[]');}catch(e){return[];}
  }
  function isCompleted(a){return getCompleted().indexOf(a)!==-1;}

  return {getPrompts:getPrompts,findAuthorName:findAuthorName,saveProgress:saveProgress,loadProgress:loadProgress,clearProgress:clearProgress,markComplete:markComplete,getCompleted:getCompleted,isCompleted:isCompleted};
})();
