// ═══════════════════════════════════════════════════════════════════════════
// BLOG POST DATA — 40 Profile+Stance Combinations
// Each written IN THE STYLE of that combination
// ═══════════════════════════════════════════════════════════════════════════

const BLOG_CONTENT = {
  // ASSERTIVE
  'ASSERTIVE-OPEN': {
    title: 'How ASSERTIVE + OPEN Writers Write',
    meta: 'Direct statements. Receptive to challenge. The confident conversationalist.',
    content: `<p>You state your case. Then you listen.</p>
<p>ASSERTIVE + OPEN writers combine conviction with curiosity. They make strong claims, but they're genuinely interested in pushback. This isn't weakness. It's intellectual confidence.</p>
<h2>The Pattern</h2>
<p>Short sentences. Clear positions. But notice the openings: "What do you think?" "I could be wrong here." "Tell me where this breaks down."</p>
<p>The assertive part comes first. The opening comes after. You lead with strength, then invite challenge.</p>
<h2>Why It Works</h2>
<p>Readers trust you because you're not hedging. They engage because you're not defensive. You've given them permission to disagree—and that makes them more likely to agree.</p>
<h2>The Risk</h2>
<p>Some readers miss the openness. They see the assertion and assume you're closed. Solution: make your invitations explicit.</p>`
  },
  
  'ASSERTIVE-CLOSED': {
    title: 'How ASSERTIVE + CLOSED Writers Write',
    meta: 'High certainty. No hedging. The definitive voice.',
    content: `<p>This is how it is.</p>
<p>ASSERTIVE + CLOSED writers don't qualify. They don't hedge. They state what they know and move on. The reader follows or doesn't.</p>
<h2>The Pattern</h2>
<p>Short sentences. Declarative. No "I think" or "perhaps." Just the claim. Just the truth as the writer sees it.</p>
<p>Punctuation is minimal. Adjectives are rare. Every word works.</p>
<h2>Why It Works</h2>
<p>Certainty is magnetic. Readers want to be led. This voice leads.</p>
<p>In a world of endless hedging, directness stands out. It builds trust.</p>
<h2>The Risk</h2>
<p>Arrogance. Readers may push back on delivery, not ideas. Use sparingly in collaborative contexts.</p>`
  },
  
  'ASSERTIVE-BALANCED': {
    title: 'How ASSERTIVE + BALANCED Writers Write',
    meta: 'Strong voice. Multiple perspectives. The fair-minded authority.',
    content: `<p>Here's what I believe. Here's why reasonable people disagree.</p>
<p>ASSERTIVE + BALANCED writers have conviction and context. They stake a position, then show they understand the alternatives.</p>
<h2>The Pattern</h2>
<p>Clear thesis. Short supporting sentences. Then: acknowledgment of complexity. "Others argue X. They have a point. But here's why Y still holds."</p>
<h2>Why It Works</h2>
<p>Readers trust writers who show their work. Acknowledging counterarguments builds credibility.</p>
<h2>The Risk</h2>
<p>Length. Balance takes space. Know when to cut to the chase.</p>`
  },
  
  'ASSERTIVE-CONTRADICTORY': {
    title: 'How ASSERTIVE + CONTRADICTORY Writers Write',
    meta: 'Bold claims. Self-aware tensions. The provocateur.',
    content: `<p>I believe X. I also believe not-X. Deal with it.</p>
<p>ASSERTIVE + CONTRADICTORY writers embrace paradox with confidence. They don't apologize for holding tensions.</p>
<h2>The Pattern</h2>
<p>Strong statement. Then its opposite, equally strong. No attempt to resolve. The contradiction is the point.</p>
<h2>Why It Works</h2>
<p>Reality is contradictory. Writers who pretend otherwise seem naive. This voice says: I see the mess.</p>
<h2>The Risk</h2>
<p>Confusion. Some readers want resolution. They'll find this frustrating. That's fine.</p>`
  },
  
  // MINIMAL
  'MINIMAL-OPEN': {
    title: 'How MINIMAL + OPEN Writers Write',
    meta: 'Sparse. Receptive. The quiet listener.',
    content: `<p>Few words. Open ears.</p>
<p>MINIMAL + OPEN writers strip prose to essentials. What remains invites response.</p>
<h2>The Pattern</h2>
<p>Short. Spaces between thoughts. Room for the reader.</p>
<p>Questions appear. Not many. Enough.</p>
<h2>Why It Works</h2>
<p>Readers complete the thought. They participate.</p>
<h2>The Risk</h2>
<p>Too sparse. Some need more.</p>`
  },
  
  'MINIMAL-CLOSED': {
    title: 'How MINIMAL + CLOSED Writers Write',
    meta: 'Spare. Certain. The final word.',
    content: `<p>Said enough.</p>
<p>MINIMAL + CLOSED writers finish. No elaboration. No invitation. Done.</p>
<h2>The Pattern</h2>
<p>Fragments allowed. Sentences end. Period.</p>
<h2>Why It Works</h2>
<p>Authority. Confidence. Respect for reader's time.</p>
<h2>The Risk</h2>
<p>Cold. Some readers need warmth.</p>`
  },
  
  'MINIMAL-BALANCED': {
    title: 'How MINIMAL + BALANCED Writers Write',
    meta: 'Brief. Fair. Both sides in few words.',
    content: `<p>This. Also that.</p>
<p>MINIMAL + BALANCED writers show duality without sprawl.</p>
<h2>The Pattern</h2>
<p>Claim. Counter-claim. No elaboration needed.</p>
<h2>Why It Works</h2>
<p>Readers see both sides fast. No lecture.</p>
<h2>The Risk</h2>
<p>Too compressed. Nuance may be lost.</p>`
  },
  
  'MINIMAL-CONTRADICTORY': {
    title: 'How MINIMAL + CONTRADICTORY Writers Write',
    meta: 'Sparse paradox. The koan.',
    content: `<p>Yes and no.</p>
<p>MINIMAL + CONTRADICTORY writers hold tension in few words.</p>
<h2>The Pattern</h2>
<p>Opposites. Side by side. Unexplained.</p>
<h2>Why It Works</h2>
<p>Readers think. Fill the space. Memorable.</p>
<h2>The Risk</h2>
<p>Obscure. Some readers will leave confused.</p>`
  },
  
  // POETIC
  'POETIC-OPEN': {
    title: 'How POETIC + OPEN Writers Write',
    meta: 'Lyrical and curious. The wondering voice.',
    content: `<p>The words arrive like weather—unbidden, shifting, asking to be noticed. And what do we do with them, these syllables that choose us?</p>
<p>POETIC + OPEN writers weave language into questions, into invitations, into doorways that swing both ways.</p>
<h2>The Pattern</h2>
<p>Sentences that breathe, that pause, that turn back on themselves. Metaphor as discovery. Questions that bloom from prose.</p>
<h2>Why It Works</h2>
<p>Readers feel held, not instructed. The beauty disarms. The openness invites participation.</p>
<h2>The Risk</h2>
<p>Readers seeking efficiency will grow impatient. Know when to be direct.</p>`
  },
  
  'POETIC-CLOSED': {
    title: 'How POETIC + CLOSED Writers Write',
    meta: 'Beautiful and certain. The oracle speaks.',
    content: `<p>The truth arrives dressed in silk. It does not argue. It simply is.</p>
<p>POETIC + CLOSED writers craft declarations that sing. There is no question here. Only the beauty of certainty.</p>
<h2>The Pattern</h2>
<p>Sentences that build like architecture, each word placed with intention. The imagery serves the assertion.</p>
<h2>Why It Works</h2>
<p>Authority clothed in beauty is irresistible. This is the prophet's register.</p>
<h2>The Risk</h2>
<p>Pretension waits at the edges. Earn every flourish or cut it.</p>`
  },
  
  'POETIC-BALANCED': {
    title: 'How POETIC + BALANCED Writers Write',
    meta: 'Lyrical fairness. The meditative witness.',
    content: `<p>On one hand, the morning light through eastern windows. On the other, the same light fading west. Both illuminate.</p>
<p>POETIC + BALANCED writers hold contradiction with grace, presenting multiple truths without forcing resolution.</p>
<h2>The Pattern</h2>
<p>Parallel structures that honor opposing views. Imagery that serves both sides.</p>
<h2>Why It Works</h2>
<p>Readers feel seen in their ambivalence. Wisdom made lyrical.</p>
<h2>The Risk</h2>
<p>Length. Balance and poetry together can sprawl. Discipline the beauty.</p>`
  },
  
  'POETIC-CONTRADICTORY': {
    title: 'How POETIC + CONTRADICTORY Writers Write',
    meta: 'Beautiful paradox. The sublime tension.',
    content: `<p>We are made of opposites—light that casts shadow, love that holds grief. Isn't that the terrible beauty of it all?</p>
<p>POETIC + CONTRADICTORY writers embrace paradox as the highest truth. Their prose illuminates rather than resolves.</p>
<h2>The Pattern</h2>
<p>Oxymoron elevated to philosophy. Metaphors that contradict themselves. The contradiction is the point.</p>
<h2>Why It Works</h2>
<p>Readers who have lived know that life contradicts itself. This voice speaks to that experience.</p>
<h2>The Risk</h2>
<p>Inaccessibility. Not every reader wants to dwell in paradox.</p>`
  },
  
  // DENSE
  'DENSE-OPEN': {
    title: 'How DENSE + OPEN Writers Write',
    meta: 'Rich complexity with genuine inquiry. The scholar who still questions.',
    content: `<p>The phenomenon under consideration—that is, the particular manner in which writers deploy epistemic frameworks—invites multiple interpretative approaches, though one wonders whether our analytical tools are adequate.</p>
<p>DENSE + OPEN writers pack substantial content while maintaining genuine inquiry. The complexity is rigorous; the conclusions remain provisional.</p>
<h2>The Pattern</h2>
<p>Subordinate clauses that qualify and contextualize. Vocabulary from specialized domains. Markers of openness: "one might argue," "it remains unclear."</p>
<h2>Why It Works</h2>
<p>Sophisticated readers appreciate the rigor without feeling lectured. This builds trust among those who value nuance.</p>
<h2>The Risk</h2>
<p>Accessibility suffers. Consider your audience carefully.</p>`
  },
  
  'DENSE-CLOSED': {
    title: 'How DENSE + CLOSED Writers Write',
    meta: 'Maximum information. Maximum certainty. The definitive treatise.',
    content: `<p>The evidence demonstrates conclusively that syntactic structures employed by writers with high certainty orientations differ systematically from those characteristic of more epistemically cautious authors.</p>
<p>DENSE + CLOSED writers deliver complex information with absolute confidence. Every clause adds data.</p>
<h2>The Pattern</h2>
<p>Long sentences that drive toward conclusions. Technical vocabulary without apology. The complexity serves certainty.</p>
<h2>Why It Works</h2>
<p>Readers seeking authoritative synthesis find it here. The certainty provides actionable conclusions.</p>
<h2>The Risk</h2>
<p>Intimidation or arrogance. Readers may feel excluded.</p>`
  },
  
  'DENSE-BALANCED': {
    title: 'How DENSE + BALANCED Writers Write',
    meta: 'Comprehensive analysis. Multiple perspectives integrated.',
    content: `<p>While proponents emphasize structural determinants—arguing that syntactic patterns emerge from cognitive constraints—advocates of the alternative position foreground agentive choice; a complete account requires integrating both.</p>
<p>DENSE + BALANCED writers present multiple positions with equal rigor before synthesizing.</p>
<h2>The Pattern</h2>
<p>Extended comparative structures. Each position receives careful elaboration. The balance is structural.</p>
<h2>Why It Works</h2>
<p>Readers gain a complete picture. The writer's fairness is evident.</p>
<h2>The Risk</h2>
<p>Length and potential for reader exhaustion.</p>`
  },
  
  'DENSE-CONTRADICTORY': {
    title: 'How DENSE + CONTRADICTORY Writers Write',
    meta: 'Complex paradox fully elaborated. The philosophical puzzle.',
    content: `<p>The fundamental contradiction inheres in the phenomenon itself: the mechanisms that enable clarity simultaneously introduce instability—a paradox demanding acknowledgment of irreducible tension.</p>
<p>DENSE + CONTRADICTORY writers explore paradox with scholarly rigor. The contradictions are elaborated in full complexity.</p>
<h2>The Pattern</h2>
<p>Extended analysis of opposing forces. Explicit refusal of false resolution. The complexity honors the paradox.</p>
<h2>Why It Works</h2>
<p>Sophisticated readers appreciate the honest engagement with difficulty.</p>
<h2>The Risk</h2>
<p>Frustration among readers seeking practical guidance.</p>`
  },
  
  // CONVERSATIONAL
  'CONVERSATIONAL-OPEN': {
    title: 'How CONVERSATIONAL + OPEN Writers Write',
    meta: 'Friendly and curious. The coffee chat.',
    content: `<p>So here's the thing—I've been thinking about this a lot, and I'm honestly not sure I've got it figured out. But maybe that's okay? Maybe figuring it out together is the point.</p>
<p>CONVERSATIONAL + OPEN writers sound like your smartest friend admitting they don't have all the answers.</p>
<h2>The Pattern</h2>
<p>Contractions everywhere. Real questions, not rhetorical. Sentences that start with "And" or "But."</p>
<h2>Why It Works</h2>
<p>Readers feel like collaborators, not audiences. You're not being talked at; you're being talked with.</p>
<h2>The Risk</h2>
<p>Some contexts need more authority. Know when to shift registers.</p>`
  },
  
  'CONVERSATIONAL-CLOSED': {
    title: 'How CONVERSATIONAL + CLOSED Writers Write',
    meta: 'Friendly but certain. The trusted advisor.',
    content: `<p>Look, I'm just going to tell you how it is, because that's what friends do, right? They don't sugarcoat things.</p>
<p>CONVERSATIONAL + CLOSED writers combine warmth with conviction. Approachable, but with opinions.</p>
<h2>The Pattern</h2>
<p>All the warmth—contractions, asides. But underneath? Certainty. "Here's the deal." "Trust me on this."</p>
<h2>Why It Works</h2>
<p>Readers get comfort of friendship and clarity of expertise. The warmth makes certainty easier to receive.</p>
<h2>The Risk</h2>
<p>Overconfidence. The friendly package can make certainty feel pushy.</p>`
  },
  
  'CONVERSATIONAL-BALANCED': {
    title: 'How CONVERSATIONAL + BALANCED Writers Write',
    meta: 'Friendly and fair. The considerate friend.',
    content: `<p>Okay, so here's where it gets complicated—and I promise I'm not fence-sitting. I genuinely think there are good points on both sides.</p>
<p>CONVERSATIONAL + BALANCED writers bring you into their thinking process like a friend explaining a decision.</p>
<h2>The Pattern</h2>
<p>The warmth is there—"here's the thing," "look." But the content is balanced. "On one hand... but then again..."</p>
<h2>Why It Works</h2>
<p>Readers trust balanced writers. Add warmth, and they like them too. Trusted and liked is powerful.</p>
<h2>The Risk</h2>
<p>Can feel wishy-washy to readers who want clear direction.</p>`
  },
  
  'CONVERSATIONAL-CONTRADICTORY': {
    title: 'How CONVERSATIONAL + CONTRADICTORY Writers Write',
    meta: 'Friendly but paradoxical. The honest mess.',
    content: `<p>Can I be honest? I believe two opposite things at the same time, and I'm pretty sure that's fine. Actually, that might be the healthiest way to live?</p>
<p>CONVERSATIONAL + CONTRADICTORY writers embrace paradox with a shrug and a smile.</p>
<h2>The Pattern</h2>
<p>All the warmth you'd expect. But the content is full of contradictions, stated openly. "I want X. I also want not-X."</p>
<h2>Why It Works</h2>
<p>Readers living in their own contradictions feel seen. The warmth makes paradox bearable.</p>
<h2>The Risk</h2>
<p>Readers seeking resolution may feel frustrated.</p>`
  }
};
