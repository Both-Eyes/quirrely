/**
 * QUIRRELY WRITING PROMPTS v1.0
 * 100 universal prompts for first analysis, stretch warm-ups, and general writing.
 * 5 categories × 20 prompts. All everyday-relatable, voice-revealing.
 *
 * Usage:
 *   WRITING_PROMPTS.getRandom(4)       — 4 random prompts (unauth)
 *   WRITING_PROMPTS.getSequence(4, 0)  — 4 sequential prompts starting at offset 0 (auth)
 */
var WRITING_PROMPTS = (function() {

  var prompts = [

    // ═══════════════════════════════════════════════════════════
    // OPINION — "What do you think about..."
    // Reveals: assertive vs hedged, formal vs conversational
    // ═══════════════════════════════════════════════════════════

    {id:'op01', cat:'opinion', text:'What\'s something most people get wrong about working from home?'},
    {id:'op02', cat:'opinion', text:'Is it better to be early or exactly on time? Why?'},
    {id:'op03', cat:'opinion', text:'What makes a neighbourhood feel like home?'},
    {id:'op04', cat:'opinion', text:'Should everyone learn to cook? What\'s your honest take?'},
    {id:'op05', cat:'opinion', text:'What\'s overrated that everyone seems to love?'},
    {id:'op06', cat:'opinion', text:'Is reading better than listening? Make your case.'},
    {id:'op07', cat:'opinion', text:'What\'s the most important quality in a friend?'},
    {id:'op08', cat:'opinion', text:'Do people talk too much or not enough? Explain.'},
    {id:'op09', cat:'opinion', text:'What\'s one rule everyone follows that doesn\'t actually make sense?'},
    {id:'op10', cat:'opinion', text:'Is routine a good thing or a trap?'},
    {id:'op11', cat:'opinion', text:'What matters more in a job — the work or the people?'},
    {id:'op12', cat:'opinion', text:'Should you always tell the truth, even when it\'s uncomfortable?'},
    {id:'op13', cat:'opinion', text:'What\'s the difference between being busy and being productive?'},
    {id:'op14', cat:'opinion', text:'Is social media making us more connected or more isolated?'},
    {id:'op15', cat:'opinion', text:'What makes a city worth living in?'},
    {id:'op16', cat:'opinion', text:'Is it better to plan everything or leave room for spontaneity?'},
    {id:'op17', cat:'opinion', text:'What\'s one thing schools should teach but don\'t?'},
    {id:'op18', cat:'opinion', text:'Do we need more silence in our lives?'},
    {id:'op19', cat:'opinion', text:'What makes someone good at listening?'},
    {id:'op20', cat:'opinion', text:'Is ambition always a good thing?'},

    // ═══════════════════════════════════════════════════════════
    // MEMORY — "Tell me about a time..."
    // Reveals: poetic vs minimal, longform vs conversational
    // ═══════════════════════════════════════════════════════════

    {id:'me01', cat:'memory', text:'Describe the last meal that genuinely surprised you.'},
    {id:'me02', cat:'memory', text:'What\'s a small moment from this week that stuck with you?'},
    {id:'me03', cat:'memory', text:'Tell me about a place you\'ve been that changed how you think.'},
    {id:'me04', cat:'memory', text:'What\'s the best conversation you\'ve had recently? What made it good?'},
    {id:'me05', cat:'memory', text:'Describe a morning that felt different from all the others.'},
    {id:'me06', cat:'memory', text:'What\'s something you learned the hard way?'},
    {id:'me07', cat:'memory', text:'Tell me about a time you changed your mind about something important.'},
    {id:'me08', cat:'memory', text:'What\'s a sound that takes you back to a specific moment?'},
    {id:'me09', cat:'memory', text:'Describe the last time you felt completely out of your comfort zone.'},
    {id:'me10', cat:'memory', text:'What\'s a gift someone gave you that meant more than they knew?'},
    {id:'me11', cat:'memory', text:'Tell me about a walk you remember clearly.'},
    {id:'me12', cat:'memory', text:'What\'s the most interesting stranger you\'ve ever spoken to?'},
    {id:'me13', cat:'memory', text:'Describe a weather moment that affected your mood.'},
    {id:'me14', cat:'memory', text:'What\'s something you used to believe that you no longer do?'},
    {id:'me15', cat:'memory', text:'Tell me about a time you helped someone without being asked.'},
    {id:'me16', cat:'memory', text:'What\'s a smell that immediately puts you somewhere specific?'},
    {id:'me17', cat:'memory', text:'Describe the last time you were genuinely bored. What happened?'},
    {id:'me18', cat:'memory', text:'What\'s a tradition you keep that nobody else would understand?'},
    {id:'me19', cat:'memory', text:'Tell me about a book, film, or song that arrived at exactly the right time.'},
    {id:'me20', cat:'memory', text:'What\'s the kindest thing you\'ve witnessed between two strangers?'},

    // ═══════════════════════════════════════════════════════════
    // OBSERVATION — "What do you notice..."
    // Reveals: dense vs minimal, interrogative vs balanced
    // ═══════════════════════════════════════════════════════════

    {id:'ob01', cat:'observation', text:'What\'s something you notice that most people walk past?'},
    {id:'ob02', cat:'observation', text:'Look out the nearest window. Describe exactly what you see.'},
    {id:'ob03', cat:'observation', text:'What does your neighbourhood sound like at 7am vs 7pm?'},
    {id:'ob04', cat:'observation', text:'Describe the hands of someone you know well.'},
    {id:'ob05', cat:'observation', text:'What\'s the most interesting thing about the room you\'re in right now?'},
    {id:'ob06', cat:'observation', text:'How do people in your city walk differently from elsewhere?'},
    {id:'ob07', cat:'observation', text:'What does the light look like where you are right now?'},
    {id:'ob08', cat:'observation', text:'Describe the last animal you saw. What was it doing?'},
    {id:'ob09', cat:'observation', text:'What\'s something about your daily commute that nobody else would notice?'},
    {id:'ob10', cat:'observation', text:'Describe the difference between a house that\'s lived in and one that isn\'t.'},
    {id:'ob11', cat:'observation', text:'What does your favourite coffee shop look like at its busiest?'},
    {id:'ob12', cat:'observation', text:'How do people behave differently in elevators vs staircases?'},
    {id:'ob13', cat:'observation', text:'What\'s the most beautiful ordinary thing you\'ve seen today?'},
    {id:'ob14', cat:'observation', text:'Describe how someone you know laughs.'},
    {id:'ob15', cat:'observation', text:'What do empty parking lots look like at night?'},
    {id:'ob16', cat:'observation', text:'How does rain change the way a street smells?'},
    {id:'ob17', cat:'observation', text:'What\'s something old in your home that you never think about?'},
    {id:'ob18', cat:'observation', text:'Describe the way a child and an adult approach the same situation differently.'},
    {id:'ob19', cat:'observation', text:'What does your grocery store reveal about the people who shop there?'},
    {id:'ob20', cat:'observation', text:'How does silence feel different in different places?'},

    // ═══════════════════════════════════════════════════════════
    // EXPLANATION — "How would you explain..."
    // Reveals: formal vs conversational, dense vs balanced
    // ═══════════════════════════════════════════════════════════

    {id:'ex01', cat:'explanation', text:'How would you explain your job to a curious ten-year-old?'},
    {id:'ex02', cat:'explanation', text:'What makes a good cup of coffee, and why do so many people get it wrong?'},
    {id:'ex03', cat:'explanation', text:'How does trust actually work between two people?'},
    {id:'ex04', cat:'explanation', text:'Explain why some songs get stuck in your head and others don\'t.'},
    {id:'ex05', cat:'explanation', text:'What actually happens when you fall asleep? Describe it as you experience it.'},
    {id:'ex06', cat:'explanation', text:'How would you teach someone to be a better listener?'},
    {id:'ex07', cat:'explanation', text:'Why do some places feel safe and others don\'t?'},
    {id:'ex08', cat:'explanation', text:'How does cooking for yourself differ from cooking for someone else?'},
    {id:'ex09', cat:'explanation', text:'What makes a good apology? Walk me through it.'},
    {id:'ex10', cat:'explanation', text:'How would you explain homesickness to someone who\'s never felt it?'},
    {id:'ex11', cat:'explanation', text:'Why do we keep things we\'ll never use again?'},
    {id:'ex12', cat:'explanation', text:'How does a conversation between old friends differ from one between new ones?'},
    {id:'ex13', cat:'explanation', text:'What makes a story worth telling?'},
    {id:'ex14', cat:'explanation', text:'How would you explain your taste in music to someone very different from you?'},
    {id:'ex15', cat:'explanation', text:'Why do some weekends feel long and others disappear?'},
    {id:'ex16', cat:'explanation', text:'How does the way you write differ from the way you speak?'},
    {id:'ex17', cat:'explanation', text:'What makes a house feel warm when you walk in?'},
    {id:'ex18', cat:'explanation', text:'How would you explain what it feels like to have a good idea?'},
    {id:'ex19', cat:'explanation', text:'Why do we remember some people clearly and forget others entirely?'},
    {id:'ex20', cat:'explanation', text:'How does the experience of reading a physical book differ from reading on a screen?'},

    // ═══════════════════════════════════════════════════════════
    // PREFERENCE — "What makes a good..."
    // Reveals: assertive vs hedged, interrogative vs formal
    // ═══════════════════════════════════════════════════════════

    {id:'pr01', cat:'preference', text:'What makes a perfect Sunday?'},
    {id:'pr02', cat:'preference', text:'Describe your ideal workspace. What matters most?'},
    {id:'pr03', cat:'preference', text:'What makes a book worth finishing even when it\'s difficult?'},
    {id:'pr04', cat:'preference', text:'What\'s your idea of a good conversation?'},
    {id:'pr05', cat:'preference', text:'What makes a meal memorable — the food or the company?'},
    {id:'pr06', cat:'preference', text:'Describe the kind of weather that makes you feel most alive.'},
    {id:'pr07', cat:'preference', text:'What makes someone interesting to talk to?'},
    {id:'pr08', cat:'preference', text:'What\'s your favourite time of day, and what makes it yours?'},
    {id:'pr09', cat:'preference', text:'What makes a good ending — to a book, a day, a trip?'},
    {id:'pr10', cat:'preference', text:'Describe the kind of silence you actually enjoy.'},
    {id:'pr11', cat:'preference', text:'What makes a city feel alive at night?'},
    {id:'pr12', cat:'preference', text:'What\'s the difference between a house and a home?'},
    {id:'pr13', cat:'preference', text:'What makes you trust a piece of writing?'},
    {id:'pr14', cat:'preference', text:'Describe the kind of music you reach for when you need to think.'},
    {id:'pr15', cat:'preference', text:'What makes a walk worth taking?'},
    {id:'pr16', cat:'preference', text:'What\'s more important in a place — how it looks or how it feels?'},
    {id:'pr17', cat:'preference', text:'What makes a morning routine feel right vs feel like a chore?'},
    {id:'pr18', cat:'preference', text:'Describe the kind of person you\'d want to sit next to on a long flight.'},
    {id:'pr19', cat:'preference', text:'What makes a photograph better than the moment it captured?'},
    {id:'pr20', cat:'preference', text:'What\'s the difference between being alone and being lonely?'},
  ];

  // ═══════════════════════════════════════════════════════════
  // SELECTION METHODS
  // ═══════════════════════════════════════════════════════════

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  /**
   * Get N random prompts, one per category where possible.
   * Used for unauth users.
   */
  function getRandom(n) {
    n = n || 4;
    var cats = ['opinion', 'memory', 'observation', 'explanation', 'preference'];
    var byCat = {};
    cats.forEach(function(c) { byCat[c] = []; });
    prompts.forEach(function(p) { if (byCat[p.cat]) byCat[p.cat].push(p); });

    var result = [];
    var shuffledCats = shuffle(cats);

    // One from each category first
    for (var i = 0; i < Math.min(n, cats.length); i++) {
      var catPrompts = byCat[shuffledCats[i]];
      var pick = catPrompts[Math.floor(Math.random() * catPrompts.length)];
      result.push(pick);
    }

    // If need more, pull random from remaining
    if (result.length < n) {
      var usedIds = {};
      result.forEach(function(p) { usedIds[p.id] = true; });
      var remaining = shuffle(prompts.filter(function(p) { return !usedIds[p.id]; }));
      while (result.length < n && remaining.length) {
        result.push(remaining.shift());
      }
    }

    return result;
  }

  /**
   * Get N sequential prompts starting at offset.
   * Used for auth users — deterministic progression.
   * Wraps around pool. Offset incremented per completed session.
   */
  function getSequence(n, offset) {
    n = n || 4;
    offset = (offset || 0) % prompts.length;
    var result = [];
    for (var i = 0; i < n; i++) {
      result.push(prompts[(offset + i) % prompts.length]);
    }
    return result;
  }

  /**
   * Get the next offset after completing a session.
   */
  function nextOffset(currentOffset, n) {
    return ((currentOffset || 0) + (n || 4)) % prompts.length;
  }

  /**
   * Get total prompt count.
   */
  function count() { return prompts.length; }

  /**
   * Get all prompts in a category.
   */
  function byCategory(cat) {
    return prompts.filter(function(p) { return p.cat === cat; });
  }

  return {
    getRandom: getRandom,
    getSequence: getSequence,
    nextOffset: nextOffset,
    count: count,
    byCategory: byCategory,
    all: prompts,
  };
})();

if (typeof window !== 'undefined') window.WRITING_PROMPTS = WRITING_PROMPTS;
