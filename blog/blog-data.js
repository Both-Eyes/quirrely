// QUIRRELY BLOG DATA — Single Source of Truth
// 40 combo + 40 HOW entries = 80 keys

const BLOG_DATA = {

  'ASSERTIVE-OPEN': {
    type: 'combo',
    slug: 'assertive-open',
    title: 'Ian McEwan\'s Writing Style',
    excerpt: 'Direct statements. Receptive to challenge. The confident conversationalist.',
    icon: '🎯',
    color: '#FF6B6B',
    profile: 'assertive',
    stance: 'open',
    body: `You state your case. Then you listen.

ASSERTIVE + OPEN writers combine conviction with curiosity. They make strong claims, but they're genuinely interested in pushback. This isn't weakness. It's intellectual confidence.

THE PATTERN

Short sentences. Clear positions. But notice the openings: "What do you think?" "I could be wrong here." "Tell me where this breaks down."

The assertive part comes first. The opening comes after. You lead with strength, then invite challenge.

WHY IT WORKS

Readers trust you because you're not hedging. They engage because you're not defensive. You've given them permission to disagree—and that makes them more likely to agree.

This is leadership voice. State your vision. Invite input. Decide.

THE RISK

Some readers miss the openness. They see the assertion and assume you're closed. Solution: make your invitations explicit. "I want to hear the counterargument."`,
    writers: {CA: { writer: 'Michael Ondaatje', book: 'Warlight', why: 'Ondaatje writes with confidence but leaves space for mystery.' },
      UK: { writer: 'Ian McEwan', book: 'Atonement', why: 'McEwan asserts his narrative while remaining open to moral complexity.' },
      AU: { writer: 'Richard Flanagan', book: 'The Narrow Road to the Deep North', why: 'Flanagan writes with conviction while exploring ambiguity.' },
      NZ: { writer: 'Eleanor Catton', book: 'The Luminaries', why: 'Catton builds assertive prose with genuine openness.' }}
  },

  'ASSERTIVE-CLOSED': {
    type: 'combo',
    slug: 'assertive-closed',
    title: 'George Orwell\'s Writing Style',
    excerpt: 'High certainty. No hedging. The definitive voice.',
    icon: '🎯',
    color: '#FF6B6B',
    profile: 'assertive',
    stance: 'closed',
    body: `This is how it is.

ASSERTIVE + CLOSED writers don't qualify. They don't hedge. They state what they know and move on. The reader follows or doesn't. That's not the writer's problem.

THE PATTERN

Short sentences. Declarative. No "I think" or "perhaps" or "it seems." Just the claim. Just the truth as the writer sees it.

Punctuation is minimal. Adjectives are rare. Every word works.

WHY IT WORKS

Certainty is magnetic. Readers want to be led. This voice leads.

In a world of endless hedging, directness stands out. It builds trust. The writer has done the thinking. The reader can rely on the conclusion.

THE RISK

Arrogance. Readers may push back not on the ideas but on the delivery. Use sparingly in collaborative contexts. Save it for when you're sure.`,
    writers: {CA: { writer: 'Margaret Atwood', book: 'The Handmaid\'s Tale', why: 'Atwood makes declarative statements without hedging.' },
      UK: { writer: 'George Orwell', book: '1984', why: 'Orwell\'s prose is direct, certain, and uncompromising.' },
      AU: { writer: 'Tim Winton', book: 'Breath', why: 'Winton writes with masculine directness and unflinching certainty.' },
      NZ: { writer: 'Lloyd Jones', book: 'Mister Pip', why: 'Jones delivers narrative with quiet but absolute confidence.' }}
  },

  'ASSERTIVE-BALANCED': {
    type: 'combo',
    slug: 'assertive-balanced',
    title: 'Hilary Mantel\'s Writing Style',
    excerpt: 'Strong voice. Multiple perspectives. The fair-minded authority.',
    icon: '🎯',
    color: '#FF6B6B',
    profile: 'assertive',
    stance: 'balanced',
    body: `Here's what I believe. Here's why reasonable people disagree.

ASSERTIVE + BALANCED writers have conviction and context. They stake a position, then show they understand the alternatives. This isn't fence-sitting. It's earned authority.

THE PATTERN

Clear thesis. Short supporting sentences. Then: acknowledgment of complexity. "Others argue X. They have a point. But here's why Y still holds."

The balance comes from structure, not hedging. The assertions remain strong.

WHY IT WORKS

Readers trust writers who show their work. Acknowledging counterarguments builds credibility. It says: I've considered this deeply. I'm not naive.

This is the voice of the best op-eds. Confident but not blind.

THE RISK

Length. Balance takes space. Know when to cut to the chase and when to show the full picture.`,
    writers: {CA: { writer: 'Joseph Boyden', book: 'Three Day Road', why: 'Boyden presents multiple perspectives with strong narrative voice.' },
      UK: { writer: 'Hilary Mantel', book: 'Wolf Hall', why: 'Mantel balances historical perspectives with assertive prose.' },
      AU: { writer: 'Kate Grenville', book: 'The Secret River', why: 'Grenville asserts narrative while acknowledging colonial complexity.' },
      NZ: { writer: 'Witi Ihimaera', book: 'The Whale Rider', why: 'Ihimaera presents tradition and change with balanced conviction.' }}
  },

  'ASSERTIVE-CONTRADICTORY': {
    type: 'combo',
    slug: 'assertive-contradictory',
    title: 'Zadie Smith\'s Writing Style',
    excerpt: 'Bold claims. Self-aware tensions. The provocateur.',
    icon: '🎯',
    color: '#FF6B6B',
    profile: 'assertive',
    stance: 'contradictory',
    body: `I believe X. I also believe not-X. Deal with it.

ASSERTIVE + CONTRADICTORY writers embrace paradox with confidence. They don't apologize for holding tensions. They assert them as features, not bugs.

THE PATTERN

Strong statement. Then its opposite, equally strong. No attempt to resolve. "Success requires focus. Success requires breadth. Both are true. Figure it out."

The contradiction is the point. The assertion is in owning it.

WHY IT WORKS

Reality is contradictory. Writers who pretend otherwise seem naive. This voice says: I see the mess. I'm not going to pretend it's tidy.

Readers who live in complexity feel seen.

THE RISK

Confusion. Some readers want resolution. They'll find this frustrating. That's fine. This voice isn't for everyone. It's for those who can hold tensions.`,
    writers: {CA: { writer: 'Mordecai Richler', book: 'Barney\'s Version', why: 'Richler\'s narrator confidently contradicts himself.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith asserts contradictory truths with equal conviction.' },
      AU: { writer: 'Peter Carey', book: 'True History of the Kelly Gang', why: 'Carey\'s Kelly is certain even when unreliable.' },
      NZ: { writer: 'Keri Hulme', book: 'The Bone People', why: 'Hulme writes with fierce conviction about irresolvable tensions.' }}
  },

  'MINIMAL-OPEN': {
    type: 'combo',
    slug: 'minimal-open',
    title: 'Alice Munro\'s Writing Style',
    excerpt: 'Sparse. Receptive. The quiet listener.',
    icon: '🪨',
    color: '#7CAE82',
    profile: 'minimal',
    stance: 'open',
    body: `Few words. Open ears.

MINIMAL + OPEN writers strip prose to essentials. What remains invites response.

THE PATTERN

Short. Spaces between thoughts. Room for the reader.

Questions appear. Not many. Enough.

WHY IT WORKS

Readers complete the thought. They participate. Engagement rises.

Silence is an invitation.

THE RISK

Too sparse. Some need more. Know your audience.`,
    writers: {CA: { writer: 'Alice Munro', book: 'Runaway', why: 'Munro says little but implies much, inviting interpretation.' },
      UK: { writer: 'Kazuo Ishiguro', book: 'Never Let Me Go', why: 'Ishiguro\'s spare prose creates space for discovery.' },
      AU: { writer: 'Gerald Murnane', book: 'The Plains', why: 'Murnane\'s minimal style opens rather than closes meaning.' },
      NZ: { writer: 'Janet Frame', book: 'Towards Another Summer', why: 'Frame\'s economy creates expansive ambiguity.' }}
  },

  'MINIMAL-CLOSED': {
    type: 'combo',
    slug: 'minimal-closed',
    title: 'Samuel Beckett\'s Writing Style',
    excerpt: 'Spare. Certain. The final word.',
    icon: '🪨',
    color: '#7CAE82',
    profile: 'minimal',
    stance: 'closed',
    body: `Said enough.

MINIMAL + CLOSED writers finish. No elaboration. No invitation. Done.

THE PATTERN

Fragments allowed. Sentences end. Period.

No questions. Statements only.

WHY IT WORKS

Authority. Confidence. Respect for reader's time.

Every word earns its place.

THE RISK

Cold. Some readers need warmth. Won't find it here.`,
    writers: {CA: { writer: 'Sheila Heti', book: 'How Should a Person Be?', why: 'Heti\'s spare prose delivers definitive observations.' },
      UK: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips language to essence with certainty.' },
      AU: { writer: 'David Malouf', book: 'An Imaginary Life', why: 'Malouf\'s minimal prose is spare and certain.' },
      NZ: { writer: 'C.K. Stead', book: 'All Visitors Ashore', why: 'Stead writes with spare, final authority.' }}
  },

  'MINIMAL-BALANCED': {
    type: 'combo',
    slug: 'minimal-balanced',
    title: 'Muriel Spark\'s Writing Style',
    excerpt: 'Brief. Fair. Both sides in few words.',
    icon: '🪨',
    color: '#7CAE82',
    profile: 'minimal',
    stance: 'balanced',
    body: `This. Also that.

MINIMAL + BALANCED writers show duality without sprawl. Economy of fairness.

THE PATTERN

Claim. Counter-claim. No elaboration needed.

The brevity is the balance.

WHY IT WORKS

Readers see both sides fast. No lecture.

Efficient wisdom.

THE RISK

Too compressed. Nuance may be lost.`,
    writers: {CA: { writer: 'Mavis Gallant', book: 'Selected Stories', why: 'Gallant\'s brevity encompasses multiple perspectives.' },
      UK: { writer: 'Muriel Spark', book: 'The Driver\'s Seat', why: 'Spark balances views in fewest possible words.' },
      AU: { writer: 'Amy Witting', book: 'I for Isobel', why: 'Witting\'s spare style presents balanced character study.' },
      NZ: { writer: 'Owen Marshall', book: 'Coming Home in the Dark', why: 'Marshall\'s minimal prose balances perspectives.' }}
  },

  'MINIMAL-CONTRADICTORY': {
    type: 'combo',
    slug: 'minimal-contradictory',
    title: 'J.M. Coetzee\'s Writing Style',
    excerpt: 'Sparse paradox. The koan.',
    icon: '🪨',
    color: '#7CAE82',
    profile: 'minimal',
    stance: 'contradictory',
    body: `Yes and no.

MINIMAL + CONTRADICTORY writers hold tension in few words. Zen approach.

THE PATTERN

Opposites. Side by side. Unexplained.

The gap is the meaning.

WHY IT WORKS

Readers think. Fill the space. Make their own meaning.

Memorable.

THE RISK

Obscure. Some readers need more. They'll leave confused.`,
    writers: {CA: { writer: 'Anne Carson', book: 'Autobiography of Red', why: 'Carson\'s spare verse holds contradictions.' },
      UK: { writer: 'Tom McCarthy', book: 'Remainder', why: 'McCarthy\'s stripped prose embodies productive contradiction.' },
      AU: { writer: 'J.M. Coetzee', book: 'Waiting for the Barbarians', why: 'Coetzee\'s spare style contains paradox.' },
      NZ: { writer: 'Bill Manhire', book: 'Selected Poems', why: 'Manhire\'s minimal verse embraces contradiction.' }}
  },

  'POETIC-OPEN': {
    type: 'combo',
    slug: 'poetic-open',
    title: 'Virginia Woolf\'s Writing Style',
    excerpt: 'Lyrical and curious. The wondering voice.',
    icon: '🌙',
    color: '#9A8EC2',
    profile: 'poetic',
    stance: 'open',
    body: `The words arrive like weather—unbidden, shifting, asking to be noticed. And what do we do with them, these syllables that choose us as much as we choose them?

POETIC + OPEN writers weave language into questions, into invitations, into doorways that swing both ways. The beauty is in the wondering.

THE PATTERN

Sentences that breathe, that pause, that turn back on themselves like rivers finding their way. Metaphor not as decoration but as discovery. And always, the openness: the willingness to be wrong, to be surprised, to let the reader in.

Questions bloom from the prose like flowers from cracks in concrete.

WHY IT WORKS

Readers feel held, not instructed. The beauty disarms. The openness invites participation. This is writing as communion, not lecture.

THE RISK

Readers seeking efficiency will grow impatient. Not every moment calls for wonder. Know when to be direct.`,
    writers: {CA: { writer: 'Michael Ondaatje', book: 'The English Patient', why: 'Ondaatje\'s lyrical prose invites multiple readings.' },
      UK: { writer: 'Virginia Woolf', book: 'To the Lighthouse', why: 'Woolf\'s poetic style opens endless interpretation.' },
      AU: { writer: 'Alexis Wright', book: 'Carpentaria', why: 'Wright\'s lyrical storytelling invites diverse readings.' },
      NZ: { writer: 'Patricia Grace', book: 'Potiki', why: 'Grace\'s poetic prose opens to multiple interpretations.' }}
  },

  'POETIC-CLOSED': {
    type: 'combo',
    slug: 'poetic-closed',
    title: 'Jeanette Winterson\'s Writing Style',
    excerpt: 'Beautiful and certain. The oracle speaks.',
    icon: '🌙',
    color: '#9A8EC2',
    profile: 'poetic',
    stance: 'closed',
    body: `The truth arrives dressed in silk. It does not argue. It simply is, and being is enough.

POETIC + CLOSED writers craft declarations that sing. There is no question here, no invitation to debate. Only the beauty of certainty, rendered in language that rewards attention.

THE PATTERN

Sentences that build like architecture, each word placed with intention, the whole structure rising toward a conclusion that feels inevitable. The imagery serves the assertion. The music reinforces the message.

No hedging. No perhaps. Only the weight of words that know themselves.

WHY IT WORKS

Authority clothed in beauty is irresistible. Readers submit to the voice because it earns submission through craft. This is the prophet's register, the poet's conviction.

THE RISK

Pretension waits at the edges. The line between oracle and pomposity is thin. Earn every flourish or cut it.`,
    writers: {CA: { writer: 'Anne Michaels', book: 'Fugitive Pieces', why: 'Michaels\' poetry is certain even when beautiful.' },
      UK: { writer: 'Jeanette Winterson', book: 'The Passion', why: 'Winterson\'s lyrical prose delivers truth with certainty.' },
      AU: { writer: 'David Malouf', book: 'Ransom', why: 'Malouf\'s poetic prose makes definitive claims.' },
      NZ: { writer: 'Elizabeth Knox', book: 'The Vintner\'s Luck', why: 'Knox\'s beautiful prose is confident in its vision.' }}
  },

  'POETIC-BALANCED': {
    type: 'combo',
    slug: 'poetic-balanced',
    title: 'Ali Smith\'s Writing Style',
    excerpt: 'Lyrical fairness. The meditative witness.',
    icon: '🌙',
    color: '#9A8EC2',
    profile: 'poetic',
    stance: 'balanced',
    body: `On one hand, the morning light through eastern windows. On the other, the same light fading west at evening. Both are true. Both illuminate. Both matter.

POETIC + BALANCED writers hold contradiction with grace, presenting multiple truths without forcing resolution. The beauty is in the holding itself.

THE PATTERN

Parallel structures that honor opposing views. Imagery that serves both sides of an argument. Sentences that acknowledge complexity without collapsing into mush.

The balance is built into the rhythm, the architecture of the prose.

WHY IT WORKS

Readers feel seen in their own ambivalence. Life is rarely simple; this voice admits it while still making the reading beautiful. Wisdom made lyrical.

THE RISK

Length. Balance and poetry both take space. Together, they can sprawl. Discipline the beauty.`,
    writers: {CA: { writer: 'Dionne Brand', book: 'A Map to the Door of No Return', why: 'Brand\'s poetic prose balances personal and historical.' },
      UK: { writer: 'Ali Smith', book: 'How to be Both', why: 'Smith balances time periods lyrically.' },
      AU: { writer: 'Kim Scott', book: 'That Deadman Dance', why: 'Scott\'s lyrical style balances perspectives.' },
      NZ: { writer: 'Paula Morris', book: 'Rangatira', why: 'Morris balances perspectives poetically.' }}
  },

  'POETIC-CONTRADICTORY': {
    type: 'combo',
    slug: 'poetic-contradictory',
    title: 'Leonard Cohen\'s Writing Style',
    excerpt: 'Beautiful paradox. The sublime tension.',
    icon: '🌙',
    color: '#9A8EC2',
    profile: 'poetic',
    stance: 'contradictory',
    body: `We are made of opposites—light that casts shadow, love that holds grief, words that mean their opposite depending on who's listening. And isn't that the terrible beauty of it all?

POETIC + CONTRADICTORY writers embrace paradox as the highest truth. Their prose doesn't resolve tension—it illuminates it, makes it luminous.

THE PATTERN

Oxymoron elevated to philosophy. Metaphors that contradict themselves. Sentences that assert and undermine in the same breath, leaving the reader suspended in beautiful uncertainty.

The contradiction is the point. The poetry is how you survive it.

WHY IT WORKS

Readers who have lived know that life contradicts itself constantly. This voice speaks to that experience, makes it bearable, even beautiful.

THE RISK

Inaccessibility. Not every reader wants to dwell in paradox. Some want answers. They'll leave frustrated and confused.`,
    writers: {CA: { writer: 'Leonard Cohen', book: 'Beautiful Losers', why: 'Cohen\'s poetic prose embraces spiritual contradiction.' },
      UK: { writer: 'Iris Murdoch', book: 'The Sea, The Sea', why: 'Murdoch\'s beautiful prose holds irreconcilable tensions.' },
      AU: { writer: 'Randolph Stow', book: 'Tourmaline', why: 'Stow\'s lyrical style contains productive paradox.' },
      NZ: { writer: 'Keri Hulme', book: 'The Bone People', why: 'Hulme\'s poetic prose embraces cultural contradiction.' }}
  },

  'DENSE-OPEN': {
    type: 'combo',
    slug: 'dense-open',
    title: 'A.S. Byatt\'s Writing Style',
    excerpt: 'Rich complexity with genuine inquiry. The scholar who still questions.',
    icon: '🔬',
    color: '#E8C875',
    profile: 'dense',
    stance: 'open',
    body: `The phenomenon under consideration—that is, the particular manner in which writers construct and deploy epistemic frameworks within their prose—invites multiple interpretative approaches, each with its own methodological merits and limitations, though one wonders whether our current analytical tools are adequate to the task.

DENSE + OPEN writers pack substantial intellectual content into their sentences while maintaining a posture of genuine inquiry. The complexity is rigorous; the conclusions remain provisional.

THE PATTERN

Subordinate clauses that qualify and contextualize. Vocabulary drawn from specialized domains but deployed with precision. And throughout, the markers of openness: "one might argue," "it remains unclear whether," "further investigation seems warranted."

The density signals expertise. The openness signals intellectual humility.

WHY IT WORKS

Sophisticated readers appreciate the rigor without feeling lectured. The writer has done the work but acknowledges limits. This builds trust among those who value nuance.

THE RISK

Accessibility suffers. Readers without relevant background knowledge may lose the thread. Consider your audience carefully.`,
    writers: {CA: { writer: 'Thomas King', book: 'Green Grass, Running Water', why: 'King\'s complex narrative remains open.' },
      UK: { writer: 'A.S. Byatt', book: 'Possession', why: 'Byatt\'s dense prose invites multiple readings.' },
      AU: { writer: 'Gerald Murnane', book: 'Border Districts', why: 'Murnane\'s complex sentences remain open-ended.' },
      NZ: { writer: 'Eleanor Catton', book: 'The Luminaries', why: 'Catton\'s intricate structure invites interpretation.' }}
  },

  'DENSE-CLOSED': {
    type: 'combo',
    slug: 'dense-closed',
    title: 'Martin Amis\'s Writing Style',
    excerpt: 'Maximum information. Maximum certainty. The definitive treatise.',
    icon: '🔬',
    color: '#E8C875',
    profile: 'dense',
    stance: 'closed',
    body: `The evidence demonstrates conclusively that the syntactic structures employed by writers with high certainty orientations differ systematically from those characteristic of more epistemically cautious authors, with the former exhibiting significantly reduced hedging frequency, elevated use of declarative constructions, and notably compressed qualification ratios.

DENSE + CLOSED writers deliver complex information with absolute confidence. Every clause adds data. Every sentence advances the argument without equivocation.

THE PATTERN

Long sentences that nevertheless drive toward conclusions. Technical vocabulary deployed without apology. Subordinate clauses that add precision, not doubt. The complexity serves certainty.

No hedging. No "perhaps." The density itself is the argument.

WHY IT WORKS

Readers seeking authoritative synthesis find it here. The writer's command of complexity signals expertise. The certainty provides actionable conclusions.

THE RISK

Intimidation or arrogance. Readers may feel excluded or talked down to. Use with appropriate expertise.`,
    writers: {CA: { writer: 'Robertson Davies', book: 'Fifth Business', why: 'Davies\' erudite prose delivers definitive insights.' },
      UK: { writer: 'Martin Amis', book: 'Money', why: 'Amis\' dense, stylized prose is supremely confident.' },
      AU: { writer: 'Patrick White', book: 'Voss', why: 'White\'s complex prose makes definitive claims.' },
      NZ: { writer: 'C.K. Stead', book: 'Mansfield', why: 'Stead\'s scholarly prose delivers authority.' }}
  },

  'DENSE-BALANCED': {
    type: 'combo',
    slug: 'dense-balanced',
    title: 'Salman Rushdie\'s Writing Style',
    excerpt: 'Comprehensive analysis. Multiple perspectives integrated. The synthesis.',
    icon: '🔬',
    color: '#E8C875',
    profile: 'dense',
    stance: 'balanced',
    body: `While proponents of the first view emphasize the structural determinants of prose style—arguing that syntactic patterns emerge primarily from cognitive constraints and genre conventions—advocates of the alternative position foreground agentive choice, suggesting that writers deliberately select from available repertoires; a complete account, however, requires integrating both perspectives.

DENSE + BALANCED writers present multiple positions with equal rigor before synthesizing. The complexity is in the comprehensiveness.

THE PATTERN

Extended comparative structures. "While X argues... Y counters... yet Z suggests..." Each position receives careful elaboration. The balance is structural, built into the architecture of the prose.

Conclusions, when they come, acknowledge what they exclude.

WHY IT WORKS

Readers gain a complete picture. The writer's fairness is evident in the treatment of each position. This builds authority through demonstrated comprehensiveness.

THE RISK

Length and potential for reader exhaustion. Not every topic requires this treatment.`,
    writers: {CA: { writer: 'Miriam Toews', book: 'Women Talking', why: 'Toews\' complex narrative balances multiple voices.' },
      UK: { writer: 'Salman Rushdie', book: 'Midnight\'s Children', why: 'Rushdie\'s dense prose balances myth and history.' },
      AU: { writer: 'Thomas Keneally', book: 'Schindler\'s Ark', why: 'Keneally\'s detailed prose balances perspectives.' },
      NZ: { writer: 'Vincent O\'Sullivan', book: 'Let the River Stand', why: 'O\'Sullivan\'s dense prose balances views.' }}
  },

  'DENSE-CONTRADICTORY': {
    type: 'combo',
    slug: 'dense-contradictory',
    title: 'Margaret Atwood\'s Writing Style',
    excerpt: 'Complex paradox fully elaborated. The philosophical puzzle.',
    icon: '🔬',
    color: '#E8C875',
    profile: 'dense',
    stance: 'contradictory',
    body: `The fundamental contradiction inheres in the phenomenon itself: the very mechanisms that enable communicative clarity simultaneously introduce interpretive instability, such that precision of expression generates multiplicity of meaning—a paradox that resists resolution and instead demands acknowledgment of irreducible tension as constitutive rather than defective.

DENSE + CONTRADICTORY writers explore paradox with scholarly rigor. The contradictions are not glossed over but elaborated in full complexity.

THE PATTERN

Extended analysis of opposing forces. Technical vocabulary for both poles of the contradiction. Explicit refusal of false resolution. The complexity honors the paradox rather than dissolving it.

WHY IT WORKS

Sophisticated readers appreciate the honest engagement with difficulty. The writer doesn't pretend to solve what cannot be solved.

THE RISK

Frustration among readers seeking practical guidance. Ensure the complexity serves genuine insight.`,
    writers: {CA: { writer: 'Margaret Atwood', book: 'Alias Grace', why: 'Atwood\'s complex narrative holds truth and lies in tension.' },
      UK: { writer: 'John Fowles', book: 'The French Lieutenant\'s Woman', why: 'Fowles\' dense metafiction embraces paradox.' },
      AU: { writer: 'Peter Carey', book: 'Oscar and Lucinda', why: 'Carey\'s intricate prose holds contradiction.' },
      NZ: { writer: 'Ian Wedde', book: 'Symmes Hole', why: 'Wedde\'s dense style embraces postmodern paradox.' }}
  },

  'CONVERSATIONAL-OPEN': {
    type: 'combo',
    slug: 'conversational-open',
    title: 'Nick Hornby\'s Writing Style',
    excerpt: 'Friendly and curious. The coffee chat.',
    icon: '☕',
    color: '#74B9FF',
    profile: 'conversational',
    stance: 'open',
    body: `So here's the thing—I've been thinking about this a lot, and I'm honestly not sure I've got it figured out. But maybe that's okay? Maybe figuring it out together is kind of the point.

CONVERSATIONAL + OPEN writers sound like your smartest friend admitting they don't have all the answers. It's warm, it's genuine, and it invites you into the process.

THE PATTERN

Contractions everywhere. Questions that aren't rhetorical—they're real. "What do you think?" isn't decoration; it's an actual invitation. Sentences that start with "And" or "But" because that's how people actually talk.

The openness isn't performed. It's just... honest.

WHY IT WORKS

Readers feel like collaborators, not audiences. The warmth builds trust. The openness builds engagement.

THE RISK

Some contexts need more authority. Know when to shift registers.`,
    writers: {CA: { writer: 'Stuart McLean', book: 'Vinyl Cafe Stories', why: 'McLean invites you in and asks what you think.' },
      UK: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s chatty prose genuinely wonders.' },
      AU: { writer: 'Tim Winton', book: 'Cloudstreet', why: 'Winton\'s vernacular storytelling invites participation.' },
      NZ: { writer: 'Carl Shuker', book: 'The Method Actors', why: 'Shuker\'s conversational style opens interpretation.' }}
  },

  'CONVERSATIONAL-CLOSED': {
    type: 'combo',
    slug: 'conversational-closed',
    title: 'Douglas Adams\'s Writing Style',
    excerpt: 'Friendly but certain. The trusted advisor.',
    icon: '☕',
    color: '#74B9FF',
    profile: 'conversational',
    stance: 'closed',
    body: `Look, I'm just going to tell you how it is, because that's what friends do, right? They don't sugarcoat things. They don't hedge. They tell you the truth.

CONVERSATIONAL + CLOSED writers combine warmth with conviction. They're approachable, sure, but they've got opinions and they're not shy about sharing them.

THE PATTERN

All the warmth of conversational writing—the contractions, the asides. But underneath that warmth? Certainty. "Here's the deal." "Trust me on this." "This is what works."

It's like advice from someone who's been there.

WHY IT WORKS

Readers get the comfort of friendship and the clarity of expertise. The warmth makes the certainty easier to receive.

THE RISK

Overconfidence. The friendly package can make certainty feel pushy. Make sure you've earned the conviction.`,
    writers: {CA: { writer: 'Will Ferguson', book: 'Happiness', why: 'Ferguson\'s chatty style delivers satirical truths.' },
      UK: { writer: 'Douglas Adams', book: 'The Hitchhiker\'s Guide', why: 'Adams\' conversational voice makes absurdist certainties.' },
      AU: { writer: 'Clive James', book: 'Unreliable Memoirs', why: 'James\' friendly voice delivers definitive observations.' },
      NZ: { writer: 'Danyl McLauchlan', book: 'Unspeakable Secrets', why: 'McLauchlan\'s chatty style makes satirical points.' }}
  },

  'CONVERSATIONAL-BALANCED': {
    type: 'combo',
    slug: 'conversational-balanced',
    title: 'David Mitchell\'s Writing Style',
    excerpt: 'Friendly and fair. The considerate friend.',
    icon: '☕',
    color: '#74B9FF',
    profile: 'conversational',
    stance: 'balanced',
    body: `Okay, so here's where it gets complicated—and I promise I'm not just fence-sitting here. I genuinely think there are good points on both sides, and I want to walk through them with you.

CONVERSATIONAL + BALANCED writers bring you into their thinking process. They show their work like a friend explaining a decision, not a professor delivering a lecture.

THE PATTERN

The warmth is there—all the "here's the thing" and "look" and "you know?" But the content is balanced. "On one hand... but then again..." The fairness is genuine.

You feel like you're thinking through something together.

WHY IT WORKS

Readers trust balanced writers. Add conversational warmth, and they also like them. That combination is powerful.

THE RISK

Can feel wishy-washy. Sometimes people need "here's what to do," not "here are the considerations."`,
    writers: {CA: { writer: 'Stuart McLean', book: 'Home from the Vinyl Cafe', why: 'McLean\'s warm style presents life\'s complications fairly.' },
      UK: { writer: 'David Mitchell', book: 'Cloud Atlas', why: 'Mitchell\'s accessible prose balances perspectives.' },
      AU: { writer: 'Charlotte Wood', book: 'The Natural Way of Things', why: 'Wood\'s readable prose balances perspectives on power.' },
      NZ: { writer: 'Rachael King', book: 'The Sound of Butterflies', why: 'King balances historical views accessibly.' }}
  },

  'CONVERSATIONAL-CONTRADICTORY': {
    type: 'combo',
    slug: 'conversational-contradictory',
    title: 'Helen Garner\'s Writing Style',
    excerpt: 'Friendly but paradoxical. The honest mess.',
    icon: '☕',
    color: '#74B9FF',
    profile: 'conversational',
    stance: 'contradictory',
    body: `Can I be honest with you? I believe two completely opposite things at the same time, and I'm pretty sure that's fine. Actually, I think that might be the healthiest way to live?

CONVERSATIONAL + CONTRADICTORY writers embrace paradox with a shrug and a smile. They don't pretend life makes sense. They just... admit it.

THE PATTERN

All the warmth you'd expect—the asides, the questions, the real person talking. But the content is full of contradictions, stated openly. "I want X. I also want not-X. What can I tell you?"

The contradiction isn't a problem to solve. It's just life.

WHY IT WORKS

Readers living in their own contradictions feel seen. The warmth makes the paradox bearable.

THE RISK

Readers seeking resolution may feel frustrated.`,
    writers: {CA: { writer: 'Sheila Heti', book: 'Motherhood', why: 'Heti\'s casual voice holds contradictory desires openly.' },
      UK: { writer: 'Geoff Dyer', book: 'Out of Sheer Rage', why: 'Dyer\'s friendly prose embraces contradictions.' },
      AU: { writer: 'Helen Garner', book: 'Everywhere I Look', why: 'Garner\'s conversational essays hold personal contradictions.' },
      NZ: { writer: 'Ashleigh Young', book: 'Can You Tolerate This?', why: 'Young\'s friendly essays embrace paradox warmly.' }}
  },

  'FORMAL-OPEN': {
    type: 'combo',
    slug: 'formal-open',
    title: 'Terry Eagleton\'s Writing Style',
    excerpt: 'Professional and receptive. The institutional inquiry.',
    icon: '🎩',
    color: '#5B7FA6',
    profile: 'formal',
    stance: 'open',
    body: `The question before us merits careful consideration from multiple perspectives, and we would welcome input from stakeholders who may bring alternative viewpoints to bear on this matter.

FORMAL + OPEN writers maintain professional register while signaling genuine receptivity to other positions. The formality establishes authority; the openness invites collaboration.

THE PATTERN

Complete sentences. No contractions. Third person or institutional "we." But within this formality, explicit invitations: "We welcome feedback." "Further perspectives would be valuable."

The openness is structured, not casual.

WHY IT WORKS

Institutional contexts require formality. But institutions that appear closed lose trust. This voice threads the needle.

THE RISK

The openness may seem token. Demonstrate genuine receptivity through action.`,
    writers: {CA: { writer: 'John Ralston Saul', book: 'Voltaire\'s Bastards', why: 'Saul\'s formal prose invites intellectual response.' },
      UK: { writer: 'Terry Eagleton', book: 'Literary Theory', why: 'Eagleton\'s academic style remains questioning.' },
      AU: { writer: 'Robert Dessaix', book: 'What Days Are For', why: 'Dessaix\'s formal essays invite reflective response.' },
      NZ: { writer: 'Brian Turner', book: 'Elemental', why: 'Turner\'s formal poetry invites contemplation.' }}
  },

  'FORMAL-CLOSED': {
    type: 'combo',
    slug: 'formal-closed',
    title: 'Simon Schama\'s Writing Style',
    excerpt: 'Professional and definitive. The official position.',
    icon: '🎩',
    color: '#5B7FA6',
    profile: 'formal',
    stance: 'closed',
    body: `The organization has determined that the following policy shall apply to all relevant circumstances. This decision is final and effective immediately.

FORMAL + CLOSED writers speak with institutional authority. There is no invitation for input. There is only the communication of a decision already made.

THE PATTERN

Passive voice where appropriate. Declarative sentences. No hedging. The formality reinforces the finality.

This is how policies are written. How verdicts are delivered.

WHY IT WORKS

Some contexts require unambiguous authority. Legal documents. Safety procedures. Final decisions.

THE RISK

Alienation. Overuse creates distance. Deploy strategically.`,
    writers: {CA: { writer: 'Northrop Frye', book: 'Anatomy of Criticism', why: 'Frye\'s scholarly prose delivers definitive framework.' },
      UK: { writer: 'Simon Schama', book: 'Citizens', why: 'Schama\'s formal history writing is authoritative.' },
      AU: { writer: 'Robert Hughes', book: 'The Fatal Shore', why: 'Hughes\' formal prose makes definitive historical claims.' },
      NZ: { writer: 'Michael King', book: 'The Penguin History of New Zealand', why: 'King\'s formal history is authoritative.' }}
  },

  'FORMAL-BALANCED': {
    type: 'combo',
    slug: 'formal-balanced',
    title: 'Isaiah Berlin\'s Writing Style',
    excerpt: 'Professional fairness. The objective report.',
    icon: '🎩',
    color: '#5B7FA6',
    profile: 'formal',
    stance: 'balanced',
    body: `The evidence supports multiple interpretations, and this analysis endeavors to present each perspective with appropriate weight before drawing provisional conclusions.

FORMAL + BALANCED writers aim for the objectivity expected in professional and academic contexts. Multiple viewpoints receive careful, impartial treatment.

THE PATTERN

Structured comparison. "Proponents argue... Critics counter..." Each position elaborated without editorial intrusion. Conclusions acknowledge limitations.

The formality reinforces the balance.

WHY IT WORKS

Contexts requiring impartiality—journalism, research, policy analysis—demand this voice.

THE RISK

False equivalence. Not all positions deserve equal weight.`,
    writers: {CA: { writer: 'Charles Taylor', book: 'Sources of the Self', why: 'Taylor\'s scholarly prose balances philosophical traditions.' },
      UK: { writer: 'Isaiah Berlin', book: 'The Hedgehog and the Fox', why: 'Berlin\'s formal essays balance intellectual traditions.' },
      AU: { writer: 'Inga Clendinnen', book: 'Dancing with Strangers', why: 'Clendinnen\'s formal prose balances colonial perspectives.' },
      NZ: { writer: 'Ranginui Walker', book: 'Ka Whawhai Tonu Matou', why: 'Walker\'s formal analysis balances perspectives.' }}
  },

  'FORMAL-CONTRADICTORY': {
    type: 'combo',
    slug: 'formal-contradictory',
    title: 'G.K. Chesterton\'s Writing Style',
    excerpt: 'Professional paradox. The institutional complexity.',
    icon: '🎩',
    color: '#5B7FA6',
    profile: 'formal',
    stance: 'contradictory',
    body: `The organization recognizes that its stated objectives may, in certain circumstances, generate conflicting imperatives, and this policy document acknowledges rather than resolves that inherent tension.

FORMAL + CONTRADICTORY writers admit institutional paradox with appropriate gravity. The contradictions are formally acknowledged.

THE PATTERN

Explicit statement of tensions. "On one hand, the organization is committed to X. Simultaneously, it must pursue Y, which may conflict with X." Formal acknowledgment of irreducible complexity.

WHY IT WORKS

Organizations that pretend away contradictions lose credibility. Formal acknowledgment demonstrates sophisticated understanding.

THE RISK

Paralysis or excuse-making. The paradox must be navigated, not merely admitted.`,
    writers: {CA: { writer: 'Mark Kingwell', book: 'In Pursuit of Happiness', why: 'Kingwell\'s formal philosophy embraces productive paradox.' },
      UK: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s formal apologetics embraces divine paradox.' },
      AU: { writer: 'David Marr', book: 'Quarterly Essay', why: 'Marr\'s formal journalism holds political contradictions.' },
      NZ: { writer: 'Jane Kelsey', book: 'The FIRE Economy', why: 'Kelsey\'s formal analysis reveals systemic contradictions.' }}
  },

  'BALANCED-OPEN': {
    type: 'combo',
    slug: 'balanced-open',
    title: 'Reni Eddo-Lodge\'s Writing Style',
    excerpt: 'Fair-minded and curious. The thoughtful explorer.',
    icon: '🔄',
    color: '#8B9E6E',
    profile: 'balanced',
    stance: 'open',
    body: `There are good arguments on multiple sides of this question, and I'm genuinely uncertain which view will prove most compelling as we learn more. What do you see that I might be missing?

BALANCED + OPEN writers combine natural fairness with genuine curiosity. They see multiple perspectives and actively invite others to contribute.

THE PATTERN

Careful presentation of multiple viewpoints. Explicit acknowledgment of uncertainty. Questions that genuinely invite input. "What am I not seeing?"

The balance is sincere. The openness is real.

WHY IT WORKS

Readers feel respected and invited. The writer's humility is evident. This builds both trust and engagement.

THE RISK

May seem indecisive in contexts requiring clear direction.`,
    writers: {CA: { writer: 'John Ibbitson', book: 'The Big Shift', why: 'Ibbitson presents political analysis with genuine inquiry.' },
      UK: { writer: 'Reni Eddo-Lodge', book: 'Why I\'m No Longer Talking', why: 'Eddo-Lodge balances perspectives while remaining curious.' },
      AU: { writer: 'Stan Grant', book: 'Talking to My Country', why: 'Grant balances Indigenous and settler views openly.' },
      NZ: { writer: 'Max Harris', book: 'The New Zealand Project', why: 'Harris balances perspectives curiously.' }}
  },

  'BALANCED-CLOSED': {
    type: 'combo',
    slug: 'balanced-closed',
    title: 'David Goodhart\'s Writing Style',
    excerpt: 'Fair analysis, firm conclusion. The judicious verdict.',
    icon: '🔄',
    color: '#8B9E6E',
    profile: 'balanced',
    stance: 'closed',
    body: `Having considered the arguments on all sides, the evidence most strongly supports the following conclusion. Other views have merit but ultimately prove less persuasive.

BALANCED + CLOSED writers do the work of considering multiple perspectives, then reach a definitive conclusion. The balance is in the process; the closure is in the outcome.

THE PATTERN

Demonstration of fairness in analysis. Then, clear pivot to conclusion. "Nevertheless." "On balance." The verdict is not tentative.

WHY IT WORKS

Readers trust conclusions that demonstrate genuine engagement with alternatives. The balance earns the closure.

THE RISK

The balance can feel performative if the conclusion was predetermined.`,
    writers: {CA: { writer: 'Jeffrey Simpson', book: 'Chronic Condition', why: 'Simpson reaches conclusions after balanced analysis.' },
      UK: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart balances then concludes definitively.' },
      AU: { writer: 'George Megalogenis', book: 'The Australian Moment', why: 'Megalogenis weighs factors then reaches firm conclusions.' },
      NZ: { writer: 'Brian Easton', book: 'Not in Narrow Seas', why: 'Easton balances views then commits to position.' }}
  },

  'BALANCED-BALANCED': {
    type: 'combo',
    slug: 'balanced-balanced',
    title: 'Kwame Anthony Appiah\'s Writing Style',
    excerpt: 'Fairness on fairness. The ultimate mediator.',
    icon: '🔄',
    color: '#8B9E6E',
    profile: 'balanced',
    stance: 'balanced',
    body: `There are compelling arguments on multiple sides, and while I have my own tentative view, I hold it with appropriate uncertainty given the genuine complexity of the question. Reasonable people continue to disagree.

BALANCED + BALANCED writers exhibit double balance: fair to all positions, and moderate in their own epistemic confidence.

THE PATTERN

Extended engagement with multiple views. Provisional conclusions. Acknowledgment that conclusions have limits. Meta-balance.

WHY IT WORKS

For genuinely complex issues, this voice is appropriate. It resists premature closure.

THE RISK

Can feel paralyzed. Sometimes readers need guidance.`,
    writers: {CA: { writer: 'Mark Kingwell', book: 'The World We Want', why: 'Kingwell remains genuinely uncertain while considering all sides.' },
      UK: { writer: 'Kwame Anthony Appiah', book: 'The Ethics of Identity', why: 'Appiah holds multiple perspectives tentatively.' },
      AU: { writer: 'Tim Soutphommasane', book: 'On Hate', why: 'Soutphommasane presents balanced analysis with appropriate uncertainty.' },
      NZ: { writer: 'Andrew Sharp', book: 'Justice and the Māori', why: 'Sharp presents balanced analysis of treaty issues carefully.' }}
  },

  'BALANCED-CONTRADICTORY': {
    type: 'combo',
    slug: 'balanced-contradictory',
    title: 'John Gray\'s Writing Style',
    excerpt: 'Fair to paradox. The complexity embracer.',
    icon: '🔄',
    color: '#8B9E6E',
    profile: 'balanced',
    stance: 'contradictory',
    body: `Each position has merit. They also contradict each other. I don't think this is a problem to solve—I think it's a tension to navigate. The contradiction might be the point.

BALANCED + CONTRADICTORY writers give fair hearing to incompatible views and refuse to force resolution.

THE PATTERN

Careful elaboration of conflicting positions. Then, explicit acknowledgment that resolution isn't available. "Both are true. We live in the tension."

WHY IT WORKS

Reality often contains irreducible contradictions. This voice honors that.

THE RISK

Readers seeking action may find this frustrating.`,
    writers: {CA: { writer: 'Thomas Homer-Dixon', book: 'The Upside of Down', why: 'Homer-Dixon holds contradictory futures in balance.' },
      UK: { writer: 'John Gray', book: 'Straw Dogs', why: 'Gray presents balanced view of humanity\'s contradictions.' },
      AU: { writer: 'Tim Flannery', book: 'The Weather Makers', why: 'Flannery balances hope and despair about climate.' },
      NZ: { writer: 'Geoff Park', book: 'Theatre Country', why: 'Park holds environmental contradictions in balance.' }}
  },

  'LONGFORM-OPEN': {
    type: 'combo',
    slug: 'longform-open',
    title: 'Olivia Laing\'s Writing Style',
    excerpt: 'Extended exploration with genuine inquiry. The deep dive that still wonders.',
    icon: '🗺️',
    color: '#6B6560',
    profile: 'longform',
    stance: 'open',
    body: `The question I want to explore with you today is one that I've been sitting with for quite some time now, and I want to be upfront about the fact that I don't have a tidy answer waiting at the end of this exploration—what I have instead is a genuine curiosity and a willingness to think through the complexity in real time, with you as my companion.

LONGFORM + OPEN writers take their time and invite the reader along for an extended journey of discovery.

THE PATTERN

Sentences that unfold gradually. Paragraphs that build on each other while acknowledging uncertainty. The extended form allows for genuine exploration.

WHY IT WORKS

Readers who want depth and nuance find it here, without the pretense of false certainty.

THE RISK

Patience required. Not all readers will follow.`,
    writers: {CA: { writer: 'Michael Ignatieff', book: 'The Russian Album', why: 'Ignatieff\'s extended meditation remains questioning.' },
      UK: { writer: 'Olivia Laing', book: 'The Lonely City', why: 'Laing\'s extended essays explore with curiosity.' },
      AU: { writer: 'Anna Krien', book: 'Night Games', why: 'Krien\'s longform journalism remains genuinely uncertain.' },
      NZ: { writer: 'Steve Braunias', book: 'Civilisation', why: 'Braunias\' extended profiles invite interpretation.' }}
  },

  'LONGFORM-CLOSED': {
    type: 'combo',
    slug: 'longform-closed',
    title: 'Patrick Leigh Fermor\'s Writing Style',
    excerpt: 'Extended argument with definitive conclusion. The comprehensive case.',
    icon: '🗺️',
    color: '#6B6560',
    profile: 'longform',
    stance: 'closed',
    body: `What follows is a thorough examination of the evidence, constructed to demonstrate conclusively that the position I advance is not merely plausible but substantially correct, and while the length of this analysis may demand patience from the reader, the comprehensiveness of the case will reward that patience with a level of certainty that briefer treatments cannot provide.

LONGFORM + CLOSED writers build extended, airtight arguments. The length is construction—each paragraph adding another brick.

THE PATTERN

Long sentences that accumulate evidence. Paragraphs that anticipate objections. By the conclusion, inevitability.

WHY IT WORKS

For readers who need to be convinced—really convinced—this voice does the work.

THE RISK

Can feel overwhelming. Ensure certainty is warranted.`,
    writers: {CA: { writer: 'John Vaillant', book: 'The Tiger', why: 'Vaillant\'s extended narrative reaches definitive conclusions.' },
      UK: { writer: 'Patrick Leigh Fermor', book: 'A Time of Gifts', why: 'Fermor\'s extended prose is confident throughout.' },
      AU: { writer: 'Chloe Hooper', book: 'The Tall Man', why: 'Hooper\'s longform reaches definitive moral conclusions.' },
      NZ: { writer: 'Ian Cross', book: 'The God Boy', why: 'Cross\' extended narrative is certain in its vision.' }}
  },

  'LONGFORM-BALANCED': {
    type: 'combo',
    slug: 'longform-balanced',
    title: 'Lawrence Hill\'s Writing Style',
    excerpt: 'Extended fairness. The comprehensive overview.',
    icon: '🗺️',
    color: '#6B6560',
    profile: 'longform',
    stance: 'balanced',
    body: `The complexity of this issue demands extended treatment, and I intend to give each major perspective the thorough consideration it deserves, presenting the strongest version of each argument before attempting to identify where the weight of reason lies—a process that cannot be rushed.

LONGFORM + BALANCED writers use extended form to ensure genuine fairness. Every position gets full elaboration.

THE PATTERN

Multiple sections devoted to different perspectives. Extended steelmanning. The balance is structural.

WHY IT WORKS

Readers seeking genuine understanding find it here.

THE RISK

Length. Readers may lose patience. Signpost clearly.`,
    writers: {CA: { writer: 'Lawrence Hill', book: 'The Book of Negroes', why: 'Hill\'s extended narrative balances historical perspectives.' },
      UK: { writer: 'Hilary Mantel', book: 'Wolf Hall', why: 'Mantel\'s extended prose balances many voices.' },
      AU: { writer: 'Kate Grenville', book: 'The Secret River', why: 'Grenville\'s extended narrative balances colonial complexity.' },
      NZ: { writer: 'Maurice Gee', book: 'Going West', why: 'Gee\'s extended narratives balance multiple perspectives.' }}
  },

  'LONGFORM-CONTRADICTORY': {
    type: 'combo',
    slug: 'longform-contradictory',
    title: 'W.G. Sebald\'s Writing Style',
    excerpt: 'Extended paradox. The full elaboration of irresolvable tension.',
    icon: '🗺️',
    color: '#6B6560',
    profile: 'longform',
    stance: 'contradictory',
    body: `What I want to do in the following extended exploration is to fully develop two positions that I believe to be both true and mutually incompatible, giving each the thorough treatment it deserves, not in order to resolve the contradiction but to honor it—to sit with the irreducible complexity long enough that we might learn something from the sitting itself.

LONGFORM + CONTRADICTORY writers use extended form to fully elaborate paradox.

THE PATTERN

Extended treatment of position A. Extended treatment of position B. Explicit discussion of the contradiction. No forced resolution.

WHY IT WORKS

For genuinely paradoxical topics, this provides appropriate treatment.

THE RISK

Reader frustration. Extended exploration with no resolution is challenging.`,
    writers: {CA: { writer: 'Michael Ondaatje', book: 'Coming Through Slaughter', why: 'Ondaatje\'s extended prose holds irresolvable tensions.' },
      UK: { writer: 'W.G. Sebald', book: 'Austerlitz', why: 'Sebald\'s extended sentences hold memory\'s contradictions.' },
      AU: { writer: 'Michelle de Kretser', book: 'Questions of Travel', why: 'de Kretser\'s longform holds belonging\'s contradictions.' },
      NZ: { writer: 'Emily Perkins', book: 'Novel About My Wife', why: 'Perkins\' extended prose holds relationship paradoxes.' }}
  },

  'INTERROGATIVE-OPEN': {
    type: 'combo',
    slug: 'interrogative-open',
    title: 'Naomi Klein\'s Writing Style',
    excerpt: 'Questions upon questions. The Socratic explorer.',
    icon: '🧩',
    color: '#00CEC9',
    profile: 'interrogative',
    stance: 'open',
    body: `What if the question itself is the point? What if we're not meant to arrive at answers but to stay with the questioning? And what does it mean that I'm asking you this—what role do you play in this exploration?

INTERROGATIVE + OPEN writers lead with questions and remain genuinely curious.

THE PATTERN

Questions that generate more questions. Few declarative statements. The openness is built into the form.

WHY IT WORKS

Readers become active participants.

THE RISK

Can feel evasive. Some readers want answers.`,
    writers: {CA: { writer: 'Naomi Klein', book: 'This Changes Everything', why: 'Klein asks genuine questions about climate solutions.' },
      UK: { writer: 'Rebecca Solnit', book: 'Hope in the Dark', why: 'Solnit asks genuine questions about activism.' },
      AU: { writer: 'Helen Garner', book: 'This House of Grief', why: 'Garner questions certainty throughout.' },
      NZ: { writer: 'Diana Wichtel', book: 'Driving to Treblinka', why: 'Wichtel questions family history openly.' }}
  },

  'INTERROGATIVE-CLOSED': {
    type: 'combo',
    slug: 'interrogative-closed',
    title: 'Malcolm Gladwell\'s Writing Style',
    excerpt: 'Rhetorical questions with predetermined answers. The leading examiner.',
    icon: '🧩',
    color: '#00CEC9',
    profile: 'interrogative',
    stance: 'closed',
    body: `Is there any doubt that this is the correct interpretation? Can anyone seriously argue otherwise? The answer, obviously, is no.

INTERROGATIVE + CLOSED writers use questions not to explore but to assert. The questions are rhetorical.

THE PATTERN

Questions that expect only one answer. "Isn't it clear that...?" The closure is embedded in the question.

WHY IT WORKS

Rhetorical questions engage while maintaining control.

THE RISK

Can feel manipulative. Skeptical readers may push back.`,
    writers: {CA: { writer: 'Malcolm Gladwell', book: 'Outliers', why: 'Gladwell poses rhetorical questions with predetermined answers.' },
      UK: { writer: 'Christopher Hitchens', book: 'God Is Not Great', why: 'Hitchens asks questions with certain answers.' },
      AU: { writer: 'Clive James', book: 'Cultural Amnesia', why: 'James asks rhetorical questions confidently.' },
      NZ: { writer: 'Chris Trotter', book: 'No Left Turn', why: 'Trotter asks leading questions about politics.' }}
  },

  'INTERROGATIVE-BALANCED': {
    type: 'combo',
    slug: 'interrogative-balanced',
    title: 'Robert Manne\'s Writing Style',
    excerpt: 'Questions that explore multiple sides. The balanced inquiry.',
    icon: '🧩',
    color: '#00CEC9',
    profile: 'interrogative',
    stance: 'balanced',
    body: `But is this view correct? What would its critics say? And don't the critics have their own weaknesses? How do we weigh these competing considerations?

INTERROGATIVE + BALANCED writers use questions to surface multiple perspectives.

THE PATTERN

Questions that represent different viewpoints. "But what about...?" followed by "And yet, couldn't one also say...?"

WHY IT WORKS

Readers see the writer genuinely grappling with complexity.

THE RISK

Can seem uncommitted. Some readers want positions.`,
    writers: {CA: { writer: 'Michael Ignatieff', book: 'The Lesser Evil', why: 'Ignatieff questions torture ethics from all angles.' },
      UK: { writer: 'Kwame Anthony Appiah', book: 'Cosmopolitanism', why: 'Appiah questions identity from multiple perspectives.' },
      AU: { writer: 'Robert Manne', book: 'The Monthly Essays', why: 'Manne questions Australian politics fairly.' },
      NZ: { writer: 'Andrew Dean', book: 'Ruth, Roger and Me', why: 'Dean questions neoliberalism from multiple angles.' }}
  },

  'INTERROGATIVE-CONTRADICTORY': {
    type: 'combo',
    slug: 'interrogative-contradictory',
    title: 'John Berger\'s Writing Style',
    excerpt: 'Questions that embrace paradox. The unresolvable inquiry.',
    icon: '🧩',
    color: '#00CEC9',
    profile: 'interrogative',
    stance: 'contradictory',
    body: `Can both be true? What if the question contains its own negation? And isn't that contradiction precisely what makes this worth exploring?

INTERROGATIVE + CONTRADICTORY writers use questions to surface and honor paradox.

THE PATTERN

Questions that highlight contradiction. "How can X be true when also not-X?" The interrogative allows paradox to remain open.

WHY IT WORKS

Questions about paradox are often more honest than statements.

THE RISK

Double frustration: questions without answers about contradictions without resolution.`,
    writers: {CA: { writer: 'Anne Carson', book: 'Nox', why: 'Carson questions grief through productive paradox.' },
      UK: { writer: 'John Berger', book: 'Ways of Seeing', why: 'Berger asks questions containing their own contradictions.' },
      AU: { writer: 'Christos Tsiolkas', book: 'The Slap', why: 'Tsiolkas questions morality through irresolvable tensions.' },
      NZ: { writer: 'Albert Wendt', book: 'Black Rainbow', why: 'Wendt questions identity through dystopian paradox.' }}
  },

  'HEDGED-OPEN': {
    type: 'combo',
    slug: 'hedged-open',
    title: 'Penelope Fitzgerald\'s Writing Style',
    excerpt: 'Tentative and curious. The genuinely uncertain explorer.',
    icon: '🔭',
    color: '#FD79A8',
    profile: 'hedged',
    stance: 'open',
    body: `I think—and I could be wrong about this—that there might be something worth exploring here, though I'm genuinely uncertain about where it leads. What's your sense of this?

HEDGED + OPEN writers combine epistemic humility with genuine curiosity.

THE PATTERN

Qualifiers throughout: "perhaps," "it seems," "I'm not certain but." Genuine questions that invite response.

WHY IT WORKS

For genuinely uncertain topics, this voice is appropriate. It models intellectual humility.

THE RISK

Can seem unconfident. Some contexts require more certainty.`,
    writers: {CA: { writer: 'Miriam Toews', book: 'All My Puny Sorrows', why: 'Toews writes with gentle uncertainty, inviting response.' },
      UK: { writer: 'Penelope Fitzgerald', book: 'The Blue Flower', why: 'Fitzgerald\'s tentative prose invites interpretation.' },
      AU: { writer: 'Sonya Hartnett', book: 'Of a Boy', why: 'Hartnett\'s uncertain narrator invites reader engagement.' },
      NZ: { writer: 'Charlotte Grimshaw', book: 'The Night Book', why: 'Grimshaw\'s tentative prose opens interpretation.' }}
  },

  'HEDGED-CLOSED': {
    type: 'combo',
    slug: 'hedged-closed',
    title: 'Kazuo Ishiguro\'s Writing Style',
    excerpt: 'Tentative but not seeking input. The private uncertainty.',
    icon: '🔭',
    color: '#FD79A8',
    profile: 'hedged',
    stance: 'closed',
    body: `It seems to me—though I recognize the limits of my perspective—that this is probably the case. I say this with appropriate tentativeness, but I am not, at present, looking for alternative viewpoints.

HEDGED + CLOSED writers qualify their claims but don't invite input.

THE PATTERN

Qualifiers present. But no questions, no invitations. The writer has reached a tentative-but-final position.

WHY IT WORKS

Some situations call for qualified positions that aren't up for debate.

THE RISK

May seem closed-minded despite the hedging.`,
    writers: {CA: { writer: 'Alice Munro', book: 'Dear Life', why: 'Munro hedges on facts but not on emotional truth.' },
      UK: { writer: 'Kazuo Ishiguro', book: 'The Remains of the Day', why: 'Stevens hedges constantly but the meaning is certain.' },
      AU: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s prose is uncertain on surface, certain beneath.' },
      NZ: { writer: 'Fiona Kidman', book: 'This Mortal Boy', why: 'Kidman hedges on interpretation but not on tragedy.' }}
  },

  'HEDGED-BALANCED': {
    type: 'combo',
    slug: 'hedged-balanced',
    title: 'Pat Barker\'s Writing Style',
    excerpt: 'Tentative fairness. The humble both-sides.',
    icon: '🔭',
    color: '#FD79A8',
    profile: 'hedged',
    stance: 'balanced',
    body: `It seems to me—though I may well be missing something important—that there are reasonable arguments on multiple sides of this question, and I'm genuinely uncertain which perspective will prove more compelling over time.

HEDGED + BALANCED writers combine epistemic humility with fairness to multiple viewpoints.

THE PATTERN

Qualifiers on everything, including the balance itself. Maximum humility.

WHY IT WORKS

For genuinely complex issues where no one should be confident, this voice is appropriate.

THE RISK

Can seem paralyzed. Double hedging may frustrate readers.`,
    writers: {CA: { writer: 'Lisa Moore', book: 'February', why: 'Moore presents uncertainty about grief from all angles.' },
      UK: { writer: 'Pat Barker', book: 'Regeneration', why: 'Barker\'s hedged prose balances perspectives on trauma.' },
      AU: { writer: 'Gail Jones', book: 'Sorry', why: 'Jones\'s uncertain prose balances reconciliation views.' },
      NZ: { writer: 'Catherine Chidgey', book: 'The Wish Child', why: 'Chidgey balances perspectives with appropriate uncertainty.' }}
  },

  'HEDGED-CONTRADICTORY': {
    type: 'combo',
    slug: 'hedged-contradictory',
    title: 'Ali Smith\'s Writing Style',
    excerpt: 'Tentatively paradoxical. The humble acceptance of mess.',
    icon: '🔭',
    color: '#FD79A8',
    profile: 'hedged',
    stance: 'contradictory',
    body: `I think—and I'm honestly not sure about this—that I might believe two contradictory things at once, and perhaps that's okay? I'm not certain what to make of it, but I suspect the contradiction might be meaningful somehow.

HEDGED + CONTRADICTORY writers acknowledge holding paradoxical views while remaining uncertain about what that means.

THE PATTERN

Qualifiers applied to the contradiction itself. Maximum tentativeness about everything.

WHY IT WORKS

For genuinely confusing situations, this voice is authentic.

THE RISK

Readers may find this exhaustingly uncertain.`,
    writers: {CA: { writer: 'Michael Ondaatje', book: 'Divisadero', why: 'Ondaatje holds contradictions tentatively.' },
      UK: { writer: 'Ali Smith', book: 'Autumn', why: 'Smith\'s uncertain prose embraces Brexit\'s contradictions.' },
      AU: { writer: 'Alexis Wright', book: 'The Swan Book', why: 'Wright holds climate contradictions in uncertain prose.' },
      NZ: { writer: 'Pip Adam', book: 'The New Animals', why: 'Adam\'s hesitant prose holds identity contradictions.' }}
  },
  'HOW-ASSERTIVE-OPEN': {
    type: 'how',
    slug: 'how-assertive-open-writers-write',
    title: 'Write Like Ian McEwan',
    excerpt: 'Direct statements. Receptive to challenge. The confident conversationalist.',
    icon: '✊',
    color: '#FF6B6B',
    profile: 'assertive',
    stance: 'open',
    body: `<p>You state your case. Then you listen.</p>
<p>ASSERTIVE + OPEN writers combine conviction with curiosity. They make strong claims, but they're genuinely interested in pushback. This isn't weakness. It's intellectual confidence.</p>
<h2>The Pattern</h2>
<p>Short sentences. Clear positions. But notice the openings: "What do you think?" "I could be wrong here." "Tell me where this breaks down."</p>
<p>The assertive part comes first. The opening comes after. You lead with strength, then invite challenge.</p>
<h2>Why It Works</h2>
<p>Readers trust you because you're not hedging. They engage because you're not defensive. You've given them permission to disagree—and that makes them more likely to agree.</p>
<h2>The Risk</h2>
<p>Some readers miss the openness. They see the assertion and assume you're closed. Solution: make your invitations explicit.</p>`
  },

  'HOW-ASSERTIVE-CLOSED': {
    type: 'how',
    slug: 'how-assertive-closed-writers-write',
    title: 'Write Like George Orwell',
    excerpt: 'High certainty. No hedging. The definitive voice.',
    icon: '✊',
    color: '#FF6B6B',
    profile: 'assertive',
    stance: 'closed',
    body: `<p>This is how it is.</p>
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

  'HOW-ASSERTIVE-BALANCED': {
    type: 'how',
    slug: 'how-assertive-balanced-writers-write',
    title: 'Write Like Hilary Mantel',
    excerpt: 'Strong voice. Multiple perspectives. The fair-minded authority.',
    icon: '✊',
    color: '#FF6B6B',
    profile: 'assertive',
    stance: 'balanced',
    body: `<p>Here's what I believe. Here's why reasonable people disagree.</p>
<p>ASSERTIVE + BALANCED writers have conviction and context. They stake a position, then show they understand the alternatives.</p>
<h2>The Pattern</h2>
<p>Clear thesis. Short supporting sentences. Then: acknowledgment of complexity. "Others argue X. They have a point. But here's why Y still holds."</p>
<h2>Why It Works</h2>
<p>Readers trust writers who show their work. Acknowledging counterarguments builds credibility.</p>
<h2>The Risk</h2>
<p>Length. Balance takes space. Know when to cut to the chase.</p>`
  },

  'HOW-ASSERTIVE-CONTRADICTORY': {
    type: 'how',
    slug: 'how-assertive-contradictory-writers-write',
    title: 'Write Like Zadie Smith',
    excerpt: 'Bold claims. Self-aware tensions. The provocateur.',
    icon: '✊',
    color: '#FF6B6B',
    profile: 'assertive',
    stance: 'contradictory',
    body: `<p>I believe X. I also believe not-X. Deal with it.</p>
<p>ASSERTIVE + CONTRADICTORY writers embrace paradox with confidence. They don't apologize for holding tensions.</p>
<h2>The Pattern</h2>
<p>Strong statement. Then its opposite, equally strong. No attempt to resolve. The contradiction is the point.</p>
<h2>Why It Works</h2>
<p>Reality is contradictory. Writers who pretend otherwise seem naive. This voice says: I see the mess.</p>
<h2>The Risk</h2>
<p>Confusion. Some readers want resolution. They'll find this frustrating. That's fine.</p>`
  },

  'HOW-MINIMAL-OPEN': {
    type: 'how',
    slug: 'how-minimal-open-writers-write',
    title: 'Write Like Alice Munro',
    excerpt: 'Sparse. Receptive. The quiet listener.',
    icon: '◾',
    color: '#7CAE82',
    profile: 'minimal',
    stance: 'open',
    body: `<p>Few words. Open ears.</p>
<p>MINIMAL + OPEN writers strip prose to essentials. What remains invites response.</p>
<h2>The Pattern</h2>
<p>Short. Spaces between thoughts. Room for the reader.</p>
<p>Questions appear. Not many. Enough.</p>
<h2>Why It Works</h2>
<p>Readers complete the thought. They participate.</p>
<h2>The Risk</h2>
<p>Too sparse. Some need more.</p>`
  },

  'HOW-MINIMAL-CLOSED': {
    type: 'how',
    slug: 'how-minimal-closed-writers-write',
    title: 'Write Like Samuel Beckett',
    excerpt: 'Spare. Certain. The final word.',
    icon: '◾',
    color: '#7CAE82',
    profile: 'minimal',
    stance: 'closed',
    body: `<p>Said enough.</p>
<p>MINIMAL + CLOSED writers finish. No elaboration. No invitation. Done.</p>
<h2>The Pattern</h2>
<p>Fragments allowed. Sentences end. Period.</p>
<h2>Why It Works</h2>
<p>Authority. Confidence. Respect for reader's time.</p>
<h2>The Risk</h2>
<p>Cold. Some readers need warmth.</p>`
  },

  'HOW-MINIMAL-BALANCED': {
    type: 'how',
    slug: 'how-minimal-balanced-writers-write',
    title: 'Write Like Muriel Spark',
    excerpt: 'Brief. Fair. Both sides in few words.',
    icon: '◾',
    color: '#7CAE82',
    profile: 'minimal',
    stance: 'balanced',
    body: `<p>This. Also that.</p>
<p>MINIMAL + BALANCED writers show duality without sprawl.</p>
<h2>The Pattern</h2>
<p>Claim. Counter-claim. No elaboration needed.</p>
<h2>Why It Works</h2>
<p>Readers see both sides fast. No lecture.</p>
<h2>The Risk</h2>
<p>Too compressed. Nuance may be lost.</p>`
  },

  'HOW-MINIMAL-CONTRADICTORY': {
    type: 'how',
    slug: 'how-minimal-contradictory-writers-write',
    title: 'Write Like J.M. Coetzee',
    excerpt: 'Sparse paradox. The koan.',
    icon: '◾',
    color: '#7CAE82',
    profile: 'minimal',
    stance: 'contradictory',
    body: `<p>Yes and no.</p>
<p>MINIMAL + CONTRADICTORY writers hold tension in few words.</p>
<h2>The Pattern</h2>
<p>Opposites. Side by side. Unexplained.</p>
<h2>Why It Works</h2>
<p>Readers think. Fill the space. Memorable.</p>
<h2>The Risk</h2>
<p>Obscure. Some readers will leave confused.</p>`
  },

  'HOW-POETIC-OPEN': {
    type: 'how',
    slug: 'how-poetic-open-writers-write',
    title: 'Write Like Virginia Woolf',
    excerpt: 'Lyrical and curious. The wondering voice.',
    icon: '🌸',
    color: '#9A8EC2',
    profile: 'poetic',
    stance: 'open',
    body: `<p>The words arrive like weather—unbidden, shifting, asking to be noticed. And what do we do with them, these syllables that choose us?</p>
<p>POETIC + OPEN writers weave language into questions, into invitations, into doorways that swing both ways.</p>
<h2>The Pattern</h2>
<p>Sentences that breathe, that pause, that turn back on themselves. Metaphor as discovery. Questions that bloom from prose.</p>
<h2>Why It Works</h2>
<p>Readers feel held, not instructed. The beauty disarms. The openness invites participation.</p>
<h2>The Risk</h2>
<p>Readers seeking efficiency will grow impatient. Know when to be direct.</p>`
  },

  'HOW-POETIC-CLOSED': {
    type: 'how',
    slug: 'how-poetic-closed-writers-write',
    title: 'Write Like Jeanette Winterson',
    excerpt: 'Beautiful and certain. The oracle speaks.',
    icon: '🌸',
    color: '#9A8EC2',
    profile: 'poetic',
    stance: 'closed',
    body: `<p>The truth arrives dressed in silk. It does not argue. It simply is.</p>
<p>POETIC + CLOSED writers craft declarations that sing. There is no question here. Only the beauty of certainty.</p>
<h2>The Pattern</h2>
<p>Sentences that build like architecture, each word placed with intention. The imagery serves the assertion.</p>
<h2>Why It Works</h2>
<p>Authority clothed in beauty is irresistible. This is the prophet's register.</p>
<h2>The Risk</h2>
<p>Pretension waits at the edges. Earn every flourish or cut it.</p>`
  },

  'HOW-POETIC-BALANCED': {
    type: 'how',
    slug: 'how-poetic-balanced-writers-write',
    title: 'Write Like Ali Smith',
    excerpt: 'Lyrical fairness. The meditative witness.',
    icon: '🌸',
    color: '#9A8EC2',
    profile: 'poetic',
    stance: 'balanced',
    body: `<p>On one hand, the morning light through eastern windows. On the other, the same light fading west. Both illuminate.</p>
<p>POETIC + BALANCED writers hold contradiction with grace, presenting multiple truths without forcing resolution.</p>
<h2>The Pattern</h2>
<p>Parallel structures that honor opposing views. Imagery that serves both sides.</p>
<h2>Why It Works</h2>
<p>Readers feel seen in their ambivalence. Wisdom made lyrical.</p>
<h2>The Risk</h2>
<p>Length. Balance and poetry together can sprawl. Discipline the beauty.</p>`
  },

  'HOW-POETIC-CONTRADICTORY': {
    type: 'how',
    slug: 'how-poetic-contradictory-writers-write',
    title: 'Write Like Leonard Cohen',
    excerpt: 'Beautiful paradox. The sublime tension.',
    icon: '🌸',
    color: '#9A8EC2',
    profile: 'poetic',
    stance: 'contradictory',
    body: `<p>We are made of opposites—light that casts shadow, love that holds grief. Isn't that the terrible beauty of it all?</p>
<p>POETIC + CONTRADICTORY writers embrace paradox as the highest truth. Their prose illuminates rather than resolves.</p>
<h2>The Pattern</h2>
<p>Oxymoron elevated to philosophy. Metaphors that contradict themselves. The contradiction is the point.</p>
<h2>Why It Works</h2>
<p>Readers who have lived know that life contradicts itself. This voice speaks to that experience.</p>
<h2>The Risk</h2>
<p>Inaccessibility. Not every reader wants to dwell in paradox.</p>`
  },

  'HOW-DENSE-OPEN': {
    type: 'how',
    slug: 'how-dense-open-writers-write',
    title: 'Write Like A.S. Byatt',
    excerpt: 'Rich complexity with genuine inquiry. The scholar who still questions.',
    icon: '📚',
    color: '#E8C875',
    profile: 'dense',
    stance: 'open',
    body: `<p>The phenomenon under consideration—that is, the particular manner in which writers deploy epistemic frameworks—invites multiple interpretative approaches, though one wonders whether our analytical tools are adequate.</p>
<p>DENSE + OPEN writers pack substantial content while maintaining genuine inquiry. The complexity is rigorous; the conclusions remain provisional.</p>
<h2>The Pattern</h2>
<p>Subordinate clauses that qualify and contextualize. Vocabulary from specialized domains. Markers of openness: "one might argue," "it remains unclear."</p>
<h2>Why It Works</h2>
<p>Sophisticated readers appreciate the rigor without feeling lectured. This builds trust among those who value nuance.</p>
<h2>The Risk</h2>
<p>Accessibility suffers. Consider your audience carefully.</p>`
  },

  'HOW-DENSE-CLOSED': {
    type: 'how',
    slug: 'how-dense-closed-writers-write',
    title: 'Write Like Martin Amis',
    excerpt: 'Maximum information. Maximum certainty. The definitive treatise.',
    icon: '📚',
    color: '#E8C875',
    profile: 'dense',
    stance: 'closed',
    body: `<p>The evidence demonstrates conclusively that syntactic structures employed by writers with high certainty orientations differ systematically from those characteristic of more epistemically cautious authors.</p>
<p>DENSE + CLOSED writers deliver complex information with absolute confidence. Every clause adds data.</p>
<h2>The Pattern</h2>
<p>Long sentences that drive toward conclusions. Technical vocabulary without apology. The complexity serves certainty.</p>
<h2>Why It Works</h2>
<p>Readers seeking authoritative synthesis find it here. The certainty provides actionable conclusions.</p>
<h2>The Risk</h2>
<p>Intimidation or arrogance. Readers may feel excluded.</p>`
  },

  'HOW-DENSE-BALANCED': {
    type: 'how',
    slug: 'how-dense-balanced-writers-write',
    title: 'Write Like Salman Rushdie',
    excerpt: 'Comprehensive analysis. Multiple perspectives integrated.',
    icon: '📚',
    color: '#E8C875',
    profile: 'dense',
    stance: 'balanced',
    body: `<p>While proponents emphasize structural determinants—arguing that syntactic patterns emerge from cognitive constraints—advocates of the alternative position foreground agentive choice; a complete account requires integrating both.</p>
<p>DENSE + BALANCED writers present multiple positions with equal rigor before synthesizing.</p>
<h2>The Pattern</h2>
<p>Extended comparative structures. Each position receives careful elaboration. The balance is structural.</p>
<h2>Why It Works</h2>
<p>Readers gain a complete picture. The writer's fairness is evident.</p>
<h2>The Risk</h2>
<p>Length and potential for reader exhaustion.</p>`
  },

  'HOW-DENSE-CONTRADICTORY': {
    type: 'how',
    slug: 'how-dense-contradictory-writers-write',
    title: 'Write Like Margaret Atwood',
    excerpt: 'Complex paradox fully elaborated. The philosophical puzzle.',
    icon: '📚',
    color: '#E8C875',
    profile: 'dense',
    stance: 'contradictory',
    body: `<p>The fundamental contradiction inheres in the phenomenon itself: the mechanisms that enable clarity simultaneously introduce instability—a paradox demanding acknowledgment of irreducible tension.</p>
<p>DENSE + CONTRADICTORY writers explore paradox with scholarly rigor. The contradictions are elaborated in full complexity.</p>
<h2>The Pattern</h2>
<p>Extended analysis of opposing forces. Explicit refusal of false resolution. The complexity honors the paradox.</p>
<h2>Why It Works</h2>
<p>Sophisticated readers appreciate the honest engagement with difficulty.</p>
<h2>The Risk</h2>
<p>Frustration among readers seeking practical guidance.</p>`
  },

  'HOW-CONVERSATIONAL-OPEN': {
    type: 'how',
    slug: 'how-conversational-open-writers-write',
    title: 'Write Like Nick Hornby',
    excerpt: 'Friendly and curious. The coffee chat.',
    icon: '💬',
    color: '#74B9FF',
    profile: 'conversational',
    stance: 'open',
    body: `<p>So here's the thing—I've been thinking about this a lot, and I'm honestly not sure I've got it figured out. But maybe that's okay? Maybe figuring it out together is the point.</p>
<p>CONVERSATIONAL + OPEN writers sound like your smartest friend admitting they don't have all the answers.</p>
<h2>The Pattern</h2>
<p>Contractions everywhere. Real questions, not rhetorical. Sentences that start with "And" or "But."</p>
<h2>Why It Works</h2>
<p>Readers feel like collaborators, not audiences. You're not being talked at; you're being talked with.</p>
<h2>The Risk</h2>
<p>Some contexts need more authority. Know when to shift registers.</p>`
  },

  'HOW-CONVERSATIONAL-CLOSED': {
    type: 'how',
    slug: 'how-conversational-closed-writers-write',
    title: 'Write Like Douglas Adams',
    excerpt: 'Friendly but certain. The trusted advisor.',
    icon: '💬',
    color: '#74B9FF',
    profile: 'conversational',
    stance: 'closed',
    body: `<p>Look, I'm just going to tell you how it is, because that's what friends do, right? They don't sugarcoat things.</p>
<p>CONVERSATIONAL + CLOSED writers combine warmth with conviction. Approachable, but with opinions.</p>
<h2>The Pattern</h2>
<p>All the warmth—contractions, asides. But underneath? Certainty. "Here's the deal." "Trust me on this."</p>
<h2>Why It Works</h2>
<p>Readers get comfort of friendship and clarity of expertise. The warmth makes certainty easier to receive.</p>
<h2>The Risk</h2>
<p>Overconfidence. The friendly package can make certainty feel pushy.</p>`
  },

  'HOW-CONVERSATIONAL-BALANCED': {
    type: 'how',
    slug: 'how-conversational-balanced-writers-write',
    title: 'Write Like David Mitchell',
    excerpt: 'Friendly and fair. The considerate friend.',
    icon: '💬',
    color: '#74B9FF',
    profile: 'conversational',
    stance: 'balanced',
    body: `<p>Okay, so here's where it gets complicated—and I promise I'm not fence-sitting. I genuinely think there are good points on both sides.</p>
<p>CONVERSATIONAL + BALANCED writers bring you into their thinking process like a friend explaining a decision.</p>
<h2>The Pattern</h2>
<p>The warmth is there—"here's the thing," "look." But the content is balanced. "On one hand... but then again..."</p>
<h2>Why It Works</h2>
<p>Readers trust balanced writers. Add warmth, and they like them too. Trusted and liked is powerful.</p>
<h2>The Risk</h2>
<p>Can feel wishy-washy to readers who want clear direction.</p>`
  },

  'HOW-CONVERSATIONAL-CONTRADICTORY': {
    type: 'how',
    slug: 'how-conversational-contradictory-writers-write',
    title: 'Write Like Helen Garner',
    excerpt: 'Friendly but paradoxical. The honest mess.',
    icon: '💬',
    color: '#74B9FF',
    profile: 'conversational',
    stance: 'contradictory',
    body: `<p>Can I be honest? I believe two opposite things at the same time, and I'm pretty sure that's fine. Actually, that might be the healthiest way to live?</p>
<p>CONVERSATIONAL + CONTRADICTORY writers embrace paradox with a shrug and a smile.</p>
<h2>The Pattern</h2>
<p>All the warmth you'd expect. But the content is full of contradictions, stated openly. "I want X. I also want not-X."</p>
<h2>Why It Works</h2>
<p>Readers living in their own contradictions feel seen. The warmth makes paradox bearable.</p>
<h2>The Risk</h2>
<p>Readers seeking resolution may feel frustrated.</p>`
  },

  'HOW-FORMAL-OPEN': {
    type: 'how',
    slug: 'how-formal-open-writers-write',
    title: 'Write Like Terry Eagleton',
    excerpt: 'Professional and receptive. The institutional inquiry.',
    icon: '📋',
    color: '#5B7FA6',
    profile: 'formal',
    stance: 'open',
    body: `<p>The question before us merits careful consideration from multiple perspectives, and we would welcome input from stakeholders who may bring alternative viewpoints.</p>
<p>FORMAL + OPEN writers maintain professional register while signaling genuine receptivity.</p>
<h2>The Pattern</h2>
<p>Complete sentences. No contractions. But within this formality, explicit invitations: "We welcome feedback." "Further perspectives would be valuable."</p>
<h2>Why It Works</h2>
<p>Institutional contexts require formality. But institutions that appear closed lose trust. This threads the needle.</p>
<h2>The Risk</h2>
<p>The openness may seem token. Demonstrate genuine receptivity through action.</p>`
  },

  'HOW-FORMAL-CLOSED': {
    type: 'how',
    slug: 'how-formal-closed-writers-write',
    title: 'Write Like Simon Schama',
    excerpt: 'Professional and definitive. The official position.',
    icon: '📋',
    color: '#5B7FA6',
    profile: 'formal',
    stance: 'closed',
    body: `<p>The organization has determined that the following policy shall apply. This decision is final and effective immediately.</p>
<p>FORMAL + CLOSED writers speak with institutional authority. There is no invitation for input.</p>
<h2>The Pattern</h2>
<p>Passive voice where appropriate. Declarative sentences. No hedging. The formality reinforces the finality.</p>
<h2>Why It Works</h2>
<p>Some contexts require unambiguous authority. Legal documents. Safety procedures. Final decisions.</p>
<h2>The Risk</h2>
<p>Alienation. Overuse creates distance. Deploy strategically.</p>`
  },

  'HOW-FORMAL-BALANCED': {
    type: 'how',
    slug: 'how-formal-balanced-writers-write',
    title: 'Write Like Isaiah Berlin',
    excerpt: 'Professional fairness. The objective report.',
    icon: '📋',
    color: '#5B7FA6',
    profile: 'formal',
    stance: 'balanced',
    body: `<p>The evidence supports multiple interpretations, and this analysis endeavors to present each perspective with appropriate weight.</p>
<p>FORMAL + BALANCED writers aim for objectivity expected in professional contexts.</p>
<h2>The Pattern</h2>
<p>Structured comparison. "Proponents argue... Critics counter..." Each position elaborated without editorial intrusion.</p>
<h2>Why It Works</h2>
<p>Contexts requiring impartiality demand this voice. Readers trust the fairness.</p>
<h2>The Risk</h2>
<p>False equivalence. Not all positions deserve equal weight.</p>`
  },

  'HOW-FORMAL-CONTRADICTORY': {
    type: 'how',
    slug: 'how-formal-contradictory-writers-write',
    title: 'Write Like G.K. Chesterton',
    excerpt: 'Professional paradox. The institutional complexity.',
    icon: '📋',
    color: '#5B7FA6',
    profile: 'formal',
    stance: 'contradictory',
    body: `<p>The organization recognizes that its stated objectives may generate conflicting imperatives, and this document acknowledges rather than resolves that tension.</p>
<p>FORMAL + CONTRADICTORY writers admit institutional paradox with appropriate gravity.</p>
<h2>The Pattern</h2>
<p>Explicit statement of tensions. No casual shrug—formal acknowledgment of irreducible complexity.</p>
<h2>Why It Works</h2>
<p>Organizations that pretend away contradictions lose credibility. Formal acknowledgment demonstrates sophistication.</p>
<h2>The Risk</h2>
<p>Paralysis or excuse-making. The paradox must be navigated, not merely admitted.</p>`
  },

  'HOW-BALANCED-OPEN': {
    type: 'how',
    slug: 'how-balanced-open-writers-write',
    title: 'Write Like Reni Eddo-Lodge',
    excerpt: 'Fair-minded and curious. The thoughtful explorer.',
    icon: '🌗',
    color: '#8B9E6E',
    profile: 'balanced',
    stance: 'open',
    body: `<p>There are good arguments on multiple sides, and I'm genuinely uncertain which view will prove most compelling. What do you see that I might be missing?</p>
<p>BALANCED + OPEN writers combine natural fairness with genuine curiosity.</p>
<h2>The Pattern</h2>
<p>Careful presentation of multiple viewpoints. Explicit acknowledgment of uncertainty. Questions that genuinely invite input.</p>
<h2>Why It Works</h2>
<p>Readers feel respected and invited. This builds both trust and engagement.</p>
<h2>The Risk</h2>
<p>May seem indecisive in contexts requiring clear direction.</p>`
  },

  'HOW-BALANCED-CLOSED': {
    type: 'how',
    slug: 'how-balanced-closed-writers-write',
    title: 'Write Like David Goodhart',
    excerpt: 'Fair analysis, firm conclusion. The judicious verdict.',
    icon: '🌗',
    color: '#8B9E6E',
    profile: 'balanced',
    stance: 'closed',
    body: `<p>Having considered the arguments on all sides, the evidence most strongly supports the following conclusion.</p>
<p>BALANCED + CLOSED writers do the work of considering multiple perspectives, then reach a definitive conclusion.</p>
<h2>The Pattern</h2>
<p>Demonstration of fairness in analysis. Then, clear pivot to conclusion. The verdict is not tentative.</p>
<h2>Why It Works</h2>
<p>Readers trust conclusions that demonstrate genuine engagement with alternatives.</p>
<h2>The Risk</h2>
<p>The balance can feel performative if the conclusion was predetermined.</p>`
  },

  'HOW-BALANCED-BALANCED': {
    type: 'how',
    slug: 'how-balanced-balanced-writers-write',
    title: 'Write Like Kwame Anthony Appiah',
    excerpt: 'Fairness on fairness. The ultimate mediator.',
    icon: '🌗',
    color: '#8B9E6E',
    profile: 'balanced',
    stance: 'balanced',
    body: `<p>There are compelling arguments on multiple sides, and while I have my own tentative view, I hold it with appropriate uncertainty given the complexity.</p>
<p>BALANCED + BALANCED writers exhibit double balance: fair to all positions, moderate in their own confidence.</p>
<h2>The Pattern</h2>
<p>Extended engagement with multiple views. Provisional conclusions. Meta-balance: being balanced about being balanced.</p>
<h2>Why It Works</h2>
<p>For genuinely complex, contested issues, this voice is appropriate.</p>
<h2>The Risk</h2>
<p>Can feel paralyzed or unhelpful. Sometimes readers need guidance.</p>`
  },

  'HOW-BALANCED-CONTRADICTORY': {
    type: 'how',
    slug: 'how-balanced-contradictory-writers-write',
    title: 'Write Like John Gray',
    excerpt: 'Fair to paradox. The complexity embracer.',
    icon: '🌗',
    color: '#8B9E6E',
    profile: 'balanced',
    stance: 'contradictory',
    body: `<p>Each position has merit. They also contradict each other. I don't think this is a problem to solve—it's a tension to navigate.</p>
<p>BALANCED + CONTRADICTORY writers give fair hearing to incompatible views and refuse to force resolution.</p>
<h2>The Pattern</h2>
<p>Careful elaboration of conflicting positions. Explicit acknowledgment that resolution isn't available—or desirable.</p>
<h2>Why It Works</h2>
<p>Reality often contains irreducible contradictions. This voice honors that honestly.</p>
<h2>The Risk</h2>
<p>Readers seeking action may find this frustrating.</p>`
  },

  'HOW-LONGFORM-OPEN': {
    type: 'how',
    slug: 'how-longform-open-writers-write',
    title: 'Write Like Olivia Laing',
    excerpt: 'Extended exploration with genuine inquiry. The deep dive.',
    icon: '📜',
    color: '#6B6560',
    profile: 'longform',
    stance: 'open',
    body: `<p>The question I want to explore with you is one I've been sitting with for quite some time, and I want to be upfront: I don't have a tidy answer waiting at the end—what I have is genuine curiosity and willingness to think through this together.</p>
<p>LONGFORM + OPEN writers take their time and invite the reader along for genuine discovery.</p>
<h2>The Pattern</h2>
<p>Sentences that unfold gradually. Paragraphs that build while acknowledging uncertainty. The extended form allows genuine exploration.</p>
<h2>Why It Works</h2>
<p>Readers who want depth find it without pretense of false certainty.</p>
<h2>The Risk</h2>
<p>Patience required. Some want answers, not journeys.</p>`
  },

  'HOW-LONGFORM-CLOSED': {
    type: 'how',
    slug: 'how-longform-closed-writers-write',
    title: 'Write Like Patrick Leigh Fermor',
    excerpt: 'Extended argument with definitive conclusion. The comprehensive case.',
    icon: '📜',
    color: '#6B6560',
    profile: 'longform',
    stance: 'closed',
    body: `<p>What follows is a thorough examination demonstrating conclusively that the position I advance is substantially correct, and while the length demands patience, the comprehensiveness will reward that patience with certainty.</p>
<p>LONGFORM + CLOSED writers build extended, airtight arguments. Each paragraph adds another brick to an edifice of certainty.</p>
<h2>The Pattern</h2>
<p>Long sentences that accumulate evidence. Paragraphs that anticipate and dismiss objections. By the conclusion, it feels inevitable.</p>
<h2>Why It Works</h2>
<p>For readers who need to be really convinced, this voice does the work.</p>
<h2>The Risk</h2>
<p>Can feel overwhelming or bullying. Ensure the certainty is warranted.</p>`
  },

  'HOW-LONGFORM-BALANCED': {
    type: 'how',
    slug: 'how-longform-balanced-writers-write',
    title: 'Write Like Lawrence Hill',
    excerpt: 'Extended fairness. The comprehensive overview.',
    icon: '📜',
    color: '#6B6560',
    profile: 'longform',
    stance: 'balanced',
    body: `<p>The complexity of this issue demands extended treatment, and I intend to give each major perspective the thorough consideration it deserves before attempting to identify where the weight of reason lies.</p>
<p>LONGFORM + BALANCED writers use extended form to ensure genuine fairness. Every position gets full elaboration.</p>
<h2>The Pattern</h2>
<p>Multiple sections for different perspectives. Extended steelmanning. The balance is structural.</p>
<h2>Why It Works</h2>
<p>Readers seeking genuine understanding of complex issues find it here.</p>
<h2>The Risk</h2>
<p>Length. Readers may lose patience. Signpost clearly.</p>`
  },

  'HOW-LONGFORM-CONTRADICTORY': {
    type: 'how',
    slug: 'how-longform-contradictory-writers-write',
    title: 'Write Like W.G. Sebald',
    excerpt: 'Extended paradox. The full elaboration of tension.',
    icon: '📜',
    color: '#6B6560',
    profile: 'longform',
    stance: 'contradictory',
    body: `<p>What I want to do is fully develop two positions that I believe to be both true and mutually incompatible, not to resolve the contradiction but to honor it—to sit with the complexity long enough that we might learn from the sitting.</p>
<p>LONGFORM + CONTRADICTORY writers use extended form to fully elaborate paradox. Both poles get comprehensive development.</p>
<h2>The Pattern</h2>
<p>Extended treatment of position A. Extended treatment of position B. Explicit discussion of contradiction. No forced resolution.</p>
<h2>Why It Works</h2>
<p>For genuinely paradoxical topics, this provides appropriate treatment.</p>
<h2>The Risk</h2>
<p>Reader frustration. Extended exploration with no resolution is challenging.</p>`
  },

  'HOW-INTERROGATIVE-OPEN': {
    type: 'how',
    slug: 'how-interrogative-open-writers-write',
    title: 'Write Like Naomi Klein',
    excerpt: 'Questions upon questions. The Socratic explorer.',
    icon: '❓',
    color: '#00CEC9',
    profile: 'interrogative',
    stance: 'open',
    body: `<p>What if the question itself is the point? What if we're not meant to arrive at answers but to stay with the questioning? And what role do you play in this exploration?</p>
<p>INTERROGATIVE + OPEN writers lead with questions and remain genuinely curious about where they lead.</p>
<h2>The Pattern</h2>
<p>Questions that generate more questions. Few declarative statements. The openness is built into the form.</p>
<h2>Why It Works</h2>
<p>Readers become active participants. This is writing as collaborative inquiry.</p>
<h2>The Risk</h2>
<p>Can feel evasive. Some readers want answers.</p>`
  },

  'HOW-INTERROGATIVE-CLOSED': {
    type: 'how',
    slug: 'how-interrogative-closed-writers-write',
    title: 'Write Like Malcolm Gladwell',
    excerpt: 'Rhetorical questions with predetermined answers. The leading examiner.',
    icon: '❓',
    color: '#00CEC9',
    profile: 'interrogative',
    stance: 'closed',
    body: `<p>Is there any doubt this is correct? Can anyone seriously argue otherwise? The answer, obviously, is no.</p>
<p>INTERROGATIVE + CLOSED writers use questions not to explore but to assert. The questions are rhetorical.</p>
<h2>The Pattern</h2>
<p>Questions that expect only one answer. "Isn't it clear that...?" The closure is embedded in the question.</p>
<h2>Why It Works</h2>
<p>Rhetorical questions engage readers while maintaining control. Readers feel they're reaching conclusions themselves.</p>
<h2>The Risk</h2>
<p>Can feel manipulative. Skeptical audiences may push back.</p>`
  },

  'HOW-INTERROGATIVE-BALANCED': {
    type: 'how',
    slug: 'how-interrogative-balanced-writers-write',
    title: 'Write Like Robert Manne',
    excerpt: 'Questions that explore multiple sides. The balanced inquiry.',
    icon: '❓',
    color: '#00CEC9',
    profile: 'interrogative',
    stance: 'balanced',
    body: `<p>But is this view correct? What would critics say? And don't the critics have their own weaknesses? How do we weigh these considerations?</p>
<p>INTERROGATIVE + BALANCED writers use questions to surface multiple perspectives.</p>
<h2>The Pattern</h2>
<p>Questions that represent different viewpoints. "But what about...?" followed by "And yet, couldn't one say...?"</p>
<h2>Why It Works</h2>
<p>Readers see the writer genuinely grappling. The questions model intellectual fairness.</p>
<h2>The Risk</h2>
<p>Can feel like lack of commitment. Some want positions, not just questions.</p>`
  },

  'HOW-INTERROGATIVE-CONTRADICTORY': {
    type: 'how',
    slug: 'how-interrogative-contradictory-writers-write',
    title: 'Write Like John Berger',
    excerpt: 'Questions that embrace paradox. The unresolvable inquiry.',
    icon: '❓',
    color: '#00CEC9',
    profile: 'interrogative',
    stance: 'contradictory',
    body: `<p>Can both be true? What if the question contains its own negation? Isn't that precisely what makes this worth exploring?</p>
<p>INTERROGATIVE + CONTRADICTORY writers use questions to surface and honor paradox.</p>
<h2>The Pattern</h2>
<p>Questions that highlight contradiction. "How can X be true when also not-X?" The interrogative allows paradox to remain alive.</p>
<h2>Why It Works</h2>
<p>Questions about paradox are often more honest than false answers.</p>
<h2>The Risk</h2>
<p>Double frustration: questions without answers about contradictions without resolution.</p>`
  },

  'HOW-HEDGED-OPEN': {
    type: 'how',
    slug: 'how-hedged-open-writers-write',
    title: 'Write Like Penelope Fitzgerald',
    excerpt: 'Tentative and curious. The genuinely uncertain explorer.',
    icon: '⚖️',
    color: '#FD79A8',
    profile: 'hedged',
    stance: 'open',
    body: `<p>I think—and I could be wrong—that there might be something worth exploring here, though I'm genuinely uncertain. What's your sense?</p>
<p>HEDGED + OPEN writers combine epistemic humility with genuine curiosity.</p>
<h2>The Pattern</h2>
<p>Qualifiers throughout: "perhaps," "it seems," "I'm not certain." Genuine questions. The hedging is honest; the openness is real.</p>
<h2>Why It Works</h2>
<p>For genuinely uncertain topics, this models intellectual humility. Readers feel like partners.</p>
<h2>The Risk</h2>
<p>Can seem unconfident. Some contexts require more certainty.</p>`
  },

  'HOW-HEDGED-CLOSED': {
    type: 'how',
    slug: 'how-hedged-closed-writers-write',
    title: 'Write Like Kazuo Ishiguro',
    excerpt: 'Tentative but not seeking input. The private uncertainty.',
    icon: '⚖️',
    color: '#FD79A8',
    profile: 'hedged',
    stance: 'closed',
    body: `<p>It seems to me—though I recognize limits of my perspective—that this is probably the case. I say this with tentativeness, but I am not seeking alternative viewpoints.</p>
<p>HEDGED + CLOSED writers qualify claims but don't invite input. Uncertain about content but certain they've thought it through.</p>
<h2>The Pattern</h2>
<p>Qualifiers present. But no questions, no invitations. The writer has reached a tentative-but-final position.</p>
<h2>Why It Works</h2>
<p>Some situations call for qualified positions that aren't up for debate.</p>
<h2>The Risk</h2>
<p>May seem closed-minded despite the hedging.</p>`
  },

  'HOW-HEDGED-BALANCED': {
    type: 'how',
    slug: 'how-hedged-balanced-writers-write',
    title: 'Write Like Pat Barker',
    excerpt: 'Tentative fairness. The humble both-sides.',
    icon: '⚖️',
    color: '#FD79A8',
    profile: 'hedged',
    stance: 'balanced',
    body: `<p>It seems to me—though I may be missing something—that there are reasonable arguments on multiple sides, and I'm genuinely uncertain which will prove more compelling.</p>
<p>HEDGED + BALANCED writers combine epistemic humility with fairness to multiple viewpoints.</p>
<h2>The Pattern</h2>
<p>Qualifiers on everything. "It seems there are good arguments on both sides, though perhaps I'm weighting them incorrectly."</p>
<h2>Why It Works</h2>
<p>For genuinely complex issues where no one should be confident, this is appropriate.</p>
<h2>The Risk</h2>
<p>Can seem paralyzed. Double hedging may frustrate readers.</p>`
  },

  'HOW-HEDGED-CONTRADICTORY': {
    type: 'how',
    slug: 'how-hedged-contradictory-writers-write',
    title: 'Write Like Ali Smith',
    excerpt: 'Tentatively paradoxical. The humble mess.',
    icon: '⚖️',
    color: '#FD79A8',
    profile: 'hedged',
    stance: 'contradictory',
    body: `<p>I think—and I'm honestly not sure—that I might believe two contradictory things, and perhaps that's okay? I suspect the contradiction might be meaningful somehow.</p>
<p>HEDGED + CONTRADICTORY writers acknowledge holding paradoxical views while remaining uncertain what that means.</p>
<h2>The Pattern</h2>
<p>Qualifiers applied to the contradiction itself. Maximum tentativeness about everything.</p>
<h2>Why It Works</h2>
<p>For genuinely confusing situations, this is authentic. It doesn't pretend to clarity that doesn't exist.</p>
<h2>The Risk</h2>
<p>Exhaustingly uncertain. At some point, thinking needs to land.</p>`
  },

};

if (typeof module !== 'undefined') module.exports = BLOG_DATA;