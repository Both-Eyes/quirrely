// QUIRRELY BLOG DATA — Single Source of Truth
// 40 combo + 40 HOW entries = 80 keys

const BLOG_DATA = {

  'ASSERTIVE-OPEN': {
    type: 'combo',
    slug: 'ian-mcewan-writing-style',
    title: 'Why You Like Ian McEwan\'s Writing Style',
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
    slug: 'george-orwell-writing-style',
    title: 'Why You Like George Orwell\'s Writing Style',
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
    slug: 'hilary-mantel-writing-style',
    title: 'Why You Like Hilary Mantel\'s Writing Style',
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
    slug: 'zadie-smith-writing-style',
    title: 'Why You Like Zadie Smith\'s Writing Style',
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
    slug: 'alice-munro-writing-style',
    title: 'Why You Like Alice Munro\'s Writing Style',
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
    slug: 'samuel-beckett-writing-style',
    title: 'Why You Like Samuel Beckett\'s Writing Style',
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
    slug: 'muriel-spark-writing-style',
    title: 'Why You Like Muriel Spark\'s Writing Style',
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
    slug: 'jm-coetzee-writing-style',
    title: 'Why You Like J.M. Coetzee\'s Writing Style',
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
    slug: 'virginia-woolf-writing-style',
    title: 'Why You Like Virginia Woolf\'s Writing Style',
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
    slug: 'jeanette-winterson-writing-style',
    title: 'Why You Like Jeanette Winterson\'s Writing Style',
    excerpt: 'Language as contradiction. The body and the word.',
    icon: '🌙',
    color: '#9A8EC2',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.85,
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
    slug: 'ali-smith-writing-style',
    title: 'Why You Like Ali Smith\'s Writing Style',
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
    slug: 'leonard-cohen-writing-style',
    title: 'Why You Like Leonard Cohen\'s Writing Style',
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
    slug: 'as-byatt-writing-style',
    title: 'Why You Like A.S. Byatt\'s Writing Style',
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
    slug: 'martin-amis-writing-style',
    title: 'Why You Like Martin Amis\'s Writing Style',
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
    slug: 'salman-rushdie-writing-style',
    title: 'Why You Like Salman Rushdie\'s Writing Style',
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
    slug: 'margaret-atwood-writing-style',
    title: 'Why You Like Margaret Atwood\'s Writing Style',
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
    slug: 'nick-hornby-writing-style',
    title: 'Why You Like Nick Hornby\'s Writing Style',
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
    slug: 'douglas-adams-writing-style',
    title: 'Why You Like Douglas Adams\'s Writing Style',
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
    slug: 'david-mitchell-writing-style',
    title: 'Why You Like David Mitchell\'s Writing Style',
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
    slug: 'helen-garner-writing-style',
    title: 'Why You Like Helen Garner\'s Writing Style',
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
    slug: 'terry-eagleton-writing-style',
    title: 'Why You Like Terry Eagleton\'s Writing Style',
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
    slug: 'simon-schama-writing-style',
    title: 'Why You Like Simon Schama\'s Writing Style',
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
    slug: 'isaiah-berlin-writing-style',
    title: 'Why You Like Isaiah Berlin\'s Writing Style',
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
    slug: 'gk-chesterton-writing-style',
    title: 'Why You Like G.K. Chesterton\'s Writing Style',
    excerpt: 'Paradox as argument. The orthodox rebel.',
    icon: '🎩',
    color: '#5B7FA6',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.88,
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
    slug: 'reni-eddo-lodge-writing-style',
    title: 'Why You Like Reni Eddo-Lodge\'s Writing Style',
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
    slug: 'david-goodhart-writing-style',
    title: 'Why You Like David Goodhart\'s Writing Style',
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
    slug: 'kwame-anthony-appiah-writing-style',
    title: 'Why You Like Kwame Anthony Appiah\'s Writing Style',
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
    slug: 'john-gray-writing-style',
    title: 'Why You Like John Gray\'s Writing Style',
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
    slug: 'olivia-laing-writing-style',
    title: 'Why You Like Olivia Laing\'s Writing Style',
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
    slug: 'patrick-leigh-fermor-writing-style',
    title: 'Why You Like Patrick Leigh Fermor\'s Writing Style',
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
    slug: 'lawrence-hill-writing-style',
    title: 'Why You Like Lawrence Hill\'s Writing Style',
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
    slug: 'wg-sebald-writing-style',
    title: 'Why You Like W.G. Sebald\'s Writing Style',
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
    slug: 'naomi-klein-writing-style',
    title: 'Why You Like Naomi Klein\'s Writing Style',
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
    slug: 'malcolm-gladwell-writing-style',
    title: 'Why You Like Malcolm Gladwell\'s Writing Style',
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
    slug: 'robert-manne-writing-style',
    title: 'Why You Like Robert Manne\'s Writing Style',
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
    slug: 'john-berger-writing-style',
    title: 'Why You Like John Berger\'s Writing Style',
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
    slug: 'penelope-fitzgerald-writing-style',
    title: 'Why You Like Penelope Fitzgerald\'s Writing Style',
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
    slug: 'kazuo-ishiguro-writing-style',
    title: 'Why You Like Kazuo Ishiguro\'s Writing Style',
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
    slug: 'pat-barker-writing-style',
    title: 'Why You Like Pat Barker\'s Writing Style',
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
    slug: 'ali-smith-hedged-writing-style',
    title: 'Why You Like Ali Smith\'s Writing Style',
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
    slug: 'write-like-ian-mcewan',
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
    slug: 'write-like-george-orwell',
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
    slug: 'write-like-hilary-mantel',
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
    slug: 'write-like-zadie-smith',
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
    slug: 'write-like-alice-munro',
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
    slug: 'write-like-samuel-beckett',
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
    slug: 'write-like-muriel-spark',
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
    slug: 'write-like-jm-coetzee',
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
    slug: 'write-like-virginia-woolf',
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
    slug: 'write-like-jeanette-winterson',
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
    slug: 'write-like-ali-smith',
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
    slug: 'write-like-leonard-cohen',
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
    slug: 'write-like-as-byatt',
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
    slug: 'write-like-martin-amis',
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
    slug: 'write-like-salman-rushdie',
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
    slug: 'write-like-margaret-atwood',
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
    slug: 'write-like-nick-hornby',
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
    slug: 'write-like-douglas-adams',
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
    slug: 'write-like-david-mitchell',
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
    slug: 'write-like-helen-garner',
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
    slug: 'write-like-terry-eagleton',
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
    slug: 'write-like-simon-schama',
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
    slug: 'write-like-isaiah-berlin',
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
    slug: 'write-like-gk-chesterton',
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
    slug: 'write-like-reni-eddo-lodge',
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
    slug: 'write-like-david-goodhart',
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
    slug: 'write-like-kwame-anthony-appiah',
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
    slug: 'write-like-john-gray',
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
    slug: 'write-like-olivia-laing',
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
    slug: 'write-like-patrick-leigh-fermor',
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
    slug: 'write-like-lawrence-hill',
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
    slug: 'write-like-wg-sebald',
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
    slug: 'write-like-naomi-klein',
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
    slug: 'write-like-malcolm-gladwell',
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
    slug: 'write-like-robert-manne',
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
    slug: 'write-like-john-berger',
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
    slug: 'write-like-penelope-fitzgerald',
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
    slug: 'write-like-kazuo-ishiguro',
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
    slug: 'write-like-pat-barker',
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
    slug: 'write-like-ali-smith-hedged',
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

  // ── SESSION 15: 106 NEW AUTHOR ENTRIES ──────────────────────────────────

  'STYLE-ALBERT-WENDT': {
    type: 'combo',
    slug: 'albert-wendt-writing-style',
    title: 'Why You Like Albert Wendt\'s Writing Style',
    excerpt: 'Lyrical and curious. The Wendt way.',
    icon: '🌊',
    color: '#7BA7BC',
    profile: 'poetic',
    stance: 'open',
    confidence: 0.82,
    writers: {
      CA: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      UK: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      AU: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      NZ: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
    },
  },

  'HOW-ALBERT-WENDT': {
    type: 'how',
    slug: 'write-like-albert-wendt',
    title: 'Write Like Albert Wendt',
    excerpt: 'Let language lead. Invite response.',
    icon: '🌊',
    color: '#7BA7BC',
    profile: 'poetic',
    stance: 'open',
    confidence: 0.82,
  },

  'STYLE-ALEXIS-WRIGHT': {
    type: 'combo',
    slug: 'alexis-wright-writing-style',
    title: 'Why You Like Alexis Wright\'s Writing Style',
    excerpt: 'Complex and unresolved. The Wright way.',
    icon: '🌀',
    color: '#8B6F8B',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      UK: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      AU: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      NZ: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
    },
  },

  'HOW-ALEXIS-WRIGHT': {
    type: 'how',
    slug: 'write-like-alexis-wright',
    title: 'Write Like Alexis Wright',
    excerpt: 'Build through compression. Hold the tension.',
    icon: '🌀',
    color: '#8B6F8B',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-AMY-WITTING': {
    type: 'combo',
    slug: 'amy-witting-writing-style',
    title: 'Why You Like Amy Witting\'s Writing Style',
    excerpt: 'Warm and certain. The Witting way.',
    icon: '📖',
    color: '#C4956A',
    profile: 'conversational',
    stance: 'closed',
    confidence: 0.65,
    writers: {
      CA: { writer: 'Douglas Adams', book: 'The Hitchhiker\'s Guide', why: 'Adams\'s wit arrives at absurdist certainty.' },
      UK: { writer: 'Douglas Adams', book: 'The Hitchhiker\'s Guide', why: 'Adams\'s wit arrives at absurdist certainty.' },
      AU: { writer: 'Douglas Adams', book: 'The Hitchhiker\'s Guide', why: 'Adams\'s wit arrives at absurdist certainty.' },
      NZ: { writer: 'Douglas Adams', book: 'The Hitchhiker\'s Guide', why: 'Adams\'s wit arrives at absurdist certainty.' },
    },
  },

  'HOW-AMY-WITTING': {
    type: 'how',
    slug: 'write-like-amy-witting',
    title: 'Write Like Amy Witting',
    excerpt: 'Think alongside. Arrive at certainty.',
    icon: '📖',
    color: '#C4956A',
    profile: 'conversational',
    stance: 'closed',
    confidence: 0.65,
  },

  'STYLE-ANDREW-DEAN': {
    type: 'combo',
    slug: 'andrew-dean-writing-style',
    title: 'Why You Like Andrew Dean\'s Writing Style',
    excerpt: 'Questioning and curious. The Dean way.',
    icon: '🔍',
    color: '#7A9E9F',
    profile: 'interrogative',
    stance: 'open',
    confidence: 0.6,
    writers: {
      CA: { writer: 'Reni Eddo-Lodge', book: 'Why I\'m No Longer Talking', why: 'Eddo-Lodge\'s questions open the most closed spaces.' },
      UK: { writer: 'Reni Eddo-Lodge', book: 'Why I\'m No Longer Talking', why: 'Eddo-Lodge\'s questions open the most closed spaces.' },
      AU: { writer: 'Reni Eddo-Lodge', book: 'Why I\'m No Longer Talking', why: 'Eddo-Lodge\'s questions open the most closed spaces.' },
      NZ: { writer: 'Reni Eddo-Lodge', book: 'Why I\'m No Longer Talking', why: 'Eddo-Lodge\'s questions open the most closed spaces.' },
    },
  },

  'HOW-ANDREW-DEAN': {
    type: 'how',
    slug: 'write-like-andrew-dean',
    title: 'Write Like Andrew Dean',
    excerpt: 'Ask the hard question. Invite response.',
    icon: '🔍',
    color: '#7A9E9F',
    profile: 'interrogative',
    stance: 'open',
    confidence: 0.6,
  },

  'STYLE-ANDREW-SHARP': {
    type: 'combo',
    slug: 'andrew-sharp-writing-style',
    title: 'Why You Like Andrew Sharp\'s Writing Style',
    excerpt: 'Precise and fair. The Sharp way.',
    icon: '⚖️',
    color: '#8B7355',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.62,
    writers: {
      CA: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      UK: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      AU: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      NZ: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
    },
  },

  'HOW-ANDREW-SHARP': {
    type: 'how',
    slug: 'write-like-andrew-sharp',
    title: 'Write Like Andrew Sharp',
    excerpt: 'Earn authority. Weigh fairly.',
    icon: '⚖️',
    color: '#8B7355',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.62,
  },

  'STYLE-ANNA-KRIEN': {
    type: 'combo',
    slug: 'anna-krien-writing-style',
    title: 'Why You Like Anna Krien\'s Writing Style',
    excerpt: 'Direct and curious. The Krien way.',
    icon: '🦁',
    color: '#C17F5A',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.78,
    writers: {
      CA: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      UK: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      AU: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      NZ: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
    },
  },

  'HOW-ANNA-KRIEN': {
    type: 'how',
    slug: 'write-like-anna-krien',
    title: 'Write Like Anna Krien',
    excerpt: 'Take a position. Invite response.',
    icon: '🦁',
    color: '#C17F5A',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.78,
  },

  'STYLE-ANNE-CARSON': {
    type: 'combo',
    slug: 'anne-carson-writing-style',
    title: 'Why You Like Anne Carson\'s Writing Style',
    excerpt: 'Lyrical and unresolved. The Carson way.',
    icon: '✨',
    color: '#9A8EC2',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.92,
    writers: {
      CA: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      UK: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      AU: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      NZ: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
    },
  },

  'HOW-ANNE-CARSON': {
    type: 'how',
    slug: 'write-like-anne-carson',
    title: 'Write Like Anne Carson',
    excerpt: 'Let language lead. Hold the tension.',
    icon: '✨',
    color: '#9A8EC2',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.92,
  },

  'STYLE-ANNE-MICHAELS': {
    type: 'combo',
    slug: 'anne-michaels-writing-style',
    title: 'Why You Like Anne Michaels\'s Writing Style',
    excerpt: 'Lyrical and certain. The Michaels way.',
    icon: '🕯️',
    color: '#7B8FA6',
    profile: 'poetic',
    stance: 'closed',
    confidence: 0.8,
    writers: {
      CA: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
      UK: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
      AU: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
      NZ: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
    },
  },

  'HOW-ANNE-MICHAELS': {
    type: 'how',
    slug: 'write-like-anne-michaels',
    title: 'Write Like Anne Michaels',
    excerpt: 'Let language lead. Arrive at certainty.',
    icon: '🕯️',
    color: '#7B8FA6',
    profile: 'poetic',
    stance: 'closed',
    confidence: 0.8,
  },

  'STYLE-ASHLEIGH-YOUNG': {
    type: 'combo',
    slug: 'ashleigh-young-writing-style',
    title: 'Why You Like Ashleigh Young\'s Writing Style',
    excerpt: 'Questioning and curious. The Young way.',
    icon: '🌿',
    color: '#7A9E7A',
    profile: 'interrogative',
    stance: 'open',
    confidence: 0.7,
    writers: {
      CA: { writer: 'Reni Eddo-Lodge', book: 'Why I\'m No Longer Talking', why: 'Eddo-Lodge\'s questions open the most closed spaces.' },
      UK: { writer: 'Reni Eddo-Lodge', book: 'Why I\'m No Longer Talking', why: 'Eddo-Lodge\'s questions open the most closed spaces.' },
      AU: { writer: 'Reni Eddo-Lodge', book: 'Why I\'m No Longer Talking', why: 'Eddo-Lodge\'s questions open the most closed spaces.' },
      NZ: { writer: 'Reni Eddo-Lodge', book: 'Why I\'m No Longer Talking', why: 'Eddo-Lodge\'s questions open the most closed spaces.' },
    },
  },

  'HOW-ASHLEIGH-YOUNG': {
    type: 'how',
    slug: 'write-like-ashleigh-young',
    title: 'Write Like Ashleigh Young',
    excerpt: 'Ask the hard question. Invite response.',
    icon: '🌿',
    color: '#7A9E7A',
    profile: 'interrogative',
    stance: 'open',
    confidence: 0.7,
  },

  'STYLE-BILL-MANHIRE': {
    type: 'combo',
    slug: 'bill-manhire-writing-style',
    title: 'Why You Like Bill Manhire\'s Writing Style',
    excerpt: 'Spare and curious. The Manhire way.',
    icon: '🌙',
    color: '#6B8CAE',
    profile: 'minimal',
    stance: 'open',
    confidence: 0.75,
    writers: {
      CA: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
      UK: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
      AU: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
      NZ: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
    },
  },

  'HOW-BILL-MANHIRE': {
    type: 'how',
    slug: 'write-like-bill-manhire',
    title: 'Write Like Bill Manhire',
    excerpt: 'Strip to essentials. Invite response.',
    icon: '🌙',
    color: '#6B8CAE',
    profile: 'minimal',
    stance: 'open',
    confidence: 0.75,
  },

  'STYLE-BRIAN-EASTON': {
    type: 'combo',
    slug: 'brian-easton-writing-style',
    title: 'Why You Like Brian Easton\'s Writing Style',
    excerpt: 'Precise and fair. The Easton way.',
    icon: '📊',
    color: '#7A8B7A',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.65,
    writers: {
      CA: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      UK: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      AU: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      NZ: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
    },
  },

  'HOW-BRIAN-EASTON': {
    type: 'how',
    slug: 'write-like-brian-easton',
    title: 'Write Like Brian Easton',
    excerpt: 'Earn authority. Weigh fairly.',
    icon: '📊',
    color: '#7A8B7A',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.65,
  },

  'STYLE-BRIAN-TURNER': {
    type: 'combo',
    slug: 'brian-turner-writing-style',
    title: 'Why You Like Brian Turner\'s Writing Style',
    excerpt: 'Spare and curious. The Turner way.',
    icon: '🏔️',
    color: '#8B9E8B',
    profile: 'minimal',
    stance: 'open',
    confidence: 0.72,
    writers: {
      CA: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
      UK: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
      AU: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
      NZ: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
    },
  },

  'HOW-BRIAN-TURNER': {
    type: 'how',
    slug: 'write-like-brian-turner',
    title: 'Write Like Brian Turner',
    excerpt: 'Strip to essentials. Invite response.',
    icon: '🏔️',
    color: '#8B9E8B',
    profile: 'minimal',
    stance: 'open',
    confidence: 0.72,
  },

  'STYLE-CK-STEAD': {
    type: 'combo',
    slug: 'ck-stead-writing-style',
    title: 'Why You Like C.K. Stead\'s Writing Style',
    excerpt: 'Direct and unresolved. The Stead way.',
    icon: '⚡',
    color: '#B8860B',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.8,
    writers: {
      CA: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      UK: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      AU: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      NZ: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
    },
  },

  'HOW-CK-STEAD': {
    type: 'how',
    slug: 'write-like-ck-stead',
    title: 'Write Like C.K. Stead',
    excerpt: 'Take a position. Hold the tension.',
    icon: '⚡',
    color: '#B8860B',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.8,
  },

  'STYLE-CARL-SHUKER': {
    type: 'combo',
    slug: 'carl-shuker-writing-style',
    title: 'Why You Like Carl Shuker\'s Writing Style',
    excerpt: 'Complex and unresolved. The Shuker way.',
    icon: '🔬',
    color: '#7A7A8B',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.68,
    writers: {
      CA: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      UK: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      AU: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      NZ: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
    },
  },

  'HOW-CARL-SHUKER': {
    type: 'how',
    slug: 'write-like-carl-shuker',
    title: 'Write Like Carl Shuker',
    excerpt: 'Build through compression. Hold the tension.',
    icon: '🔬',
    color: '#7A7A8B',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.68,
  },

  'STYLE-CATHERINE-CHIDGEY': {
    type: 'combo',
    slug: 'catherine-chidgey-writing-style',
    title: 'Why You Like Catherine Chidgey\'s Writing Style',
    excerpt: 'Lyrical and certain. The Chidgey way.',
    icon: '🎭',
    color: '#9A7A9A',
    profile: 'poetic',
    stance: 'closed',
    confidence: 0.78,
    writers: {
      CA: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
      UK: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
      AU: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
      NZ: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
    },
  },

  'HOW-CATHERINE-CHIDGEY': {
    type: 'how',
    slug: 'write-like-catherine-chidgey',
    title: 'Write Like Catherine Chidgey',
    excerpt: 'Let language lead. Arrive at certainty.',
    icon: '🎭',
    color: '#9A7A9A',
    profile: 'poetic',
    stance: 'closed',
    confidence: 0.78,
  },

  'STYLE-CHARLES-TAYLOR': {
    type: 'combo',
    slug: 'charles-taylor-writing-style',
    title: 'Why You Like Charles Taylor\'s Writing Style',
    excerpt: 'Precise and fair. The Taylor way.',
    icon: '🏛️',
    color: '#7A8B9A',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.88,
    writers: {
      CA: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      UK: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      AU: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      NZ: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
    },
  },

  'HOW-CHARLES-TAYLOR': {
    type: 'how',
    slug: 'write-like-charles-taylor',
    title: 'Write Like Charles Taylor',
    excerpt: 'Earn authority. Weigh fairly.',
    icon: '🏛️',
    color: '#7A8B9A',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.88,
  },

  'STYLE-CHARLOTTE-GRIMSHAW': {
    type: 'combo',
    slug: 'charlotte-grimshaw-writing-style',
    title: 'Why You Like Charlotte Grimshaw\'s Writing Style',
    excerpt: 'Warm and unresolved. The Grimshaw way.',
    icon: '🪞',
    color: '#B87A7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.8,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-CHARLOTTE-GRIMSHAW': {
    type: 'how',
    slug: 'write-like-charlotte-grimshaw',
    title: 'Write Like Charlotte Grimshaw',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '🪞',
    color: '#B87A7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.8,
  },

  'STYLE-CHARLOTTE-WOOD': {
    type: 'combo',
    slug: 'charlotte-wood-writing-style',
    title: 'Why You Like Charlotte Wood\'s Writing Style',
    excerpt: 'Careful and unresolved. The Wood way.',
    icon: '🌱',
    color: '#8B9A7A',
    profile: 'hedged',
    stance: 'contradictory',
    confidence: 0.75,
    writers: {
      CA: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      UK: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      AU: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      NZ: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
    },
  },

  'HOW-CHARLOTTE-WOOD': {
    type: 'how',
    slug: 'write-like-charlotte-wood',
    title: 'Write Like Charlotte Wood',
    excerpt: 'Stay honest about limits. Hold the tension.',
    icon: '🌱',
    color: '#8B9A7A',
    profile: 'hedged',
    stance: 'contradictory',
    confidence: 0.75,
  },

  'STYLE-CHLOE-HOOPER': {
    type: 'combo',
    slug: 'chloe-hooper-writing-style',
    title: 'Why You Like Chloe Hooper\'s Writing Style',
    excerpt: 'Direct and curious. The Hooper way.',
    icon: '🔦',
    color: '#C4956A',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.8,
    writers: {
      CA: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      UK: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      AU: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      NZ: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
    },
  },

  'HOW-CHLOE-HOOPER': {
    type: 'how',
    slug: 'write-like-chloe-hooper',
    title: 'Write Like Chloe Hooper',
    excerpt: 'Take a position. Invite response.',
    icon: '🔦',
    color: '#C4956A',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.8,
  },

  'STYLE-CHRIS-TROTTER': {
    type: 'combo',
    slug: 'chris-trotter-writing-style',
    title: 'Why You Like Chris Trotter\'s Writing Style',
    excerpt: 'Direct and unresolved. The Trotter way.',
    icon: '📢',
    color: '#B8860B',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.72,
    writers: {
      CA: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      UK: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      AU: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      NZ: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
    },
  },

  'HOW-CHRIS-TROTTER': {
    type: 'how',
    slug: 'write-like-chris-trotter',
    title: 'Write Like Chris Trotter',
    excerpt: 'Take a position. Hold the tension.',
    icon: '📢',
    color: '#B8860B',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.72,
  },

  'STYLE-CHRISTOPHER-HITCHENS': {
    type: 'combo',
    slug: 'christopher-hitchens-writing-style',
    title: 'Why You Like Christopher Hitchens\'s Writing Style',
    excerpt: 'Direct and unresolved. The Hitchens way.',
    icon: '⚔️',
    color: '#8B4513',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.92,
    writers: {
      CA: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      UK: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      AU: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      NZ: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
    },
  },

  'HOW-CHRISTOPHER-HITCHENS': {
    type: 'how',
    slug: 'write-like-christopher-hitchens',
    title: 'Write Like Christopher Hitchens',
    excerpt: 'Take a position. Hold the tension.',
    icon: '⚔️',
    color: '#8B4513',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.92,
  },

  'STYLE-CHRISTOS-TSIOLKAS': {
    type: 'combo',
    slug: 'christos-tsiolkas-writing-style',
    title: 'Why You Like Christos Tsiolkas\'s Writing Style',
    excerpt: 'Direct and unresolved. The Tsiolkas way.',
    icon: '🔥',
    color: '#B85A5A',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      UK: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      AU: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      NZ: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
    },
  },

  'HOW-CHRISTOS-TSIOLKAS': {
    type: 'how',
    slug: 'write-like-christos-tsiolkas',
    title: 'Write Like Christos Tsiolkas',
    excerpt: 'Take a position. Hold the tension.',
    icon: '🔥',
    color: '#B85A5A',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-CLIVE-JAMES': {
    type: 'combo',
    slug: 'clive-james-writing-style',
    title: 'Why You Like Clive James\'s Writing Style',
    excerpt: 'Warm and unresolved. The James way.',
    icon: '🎪',
    color: '#C4956A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-CLIVE-JAMES': {
    type: 'how',
    slug: 'write-like-clive-james',
    title: 'Write Like Clive James',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '🎪',
    color: '#C4956A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-DANYL-MCLAUCHLAN': {
    type: 'combo',
    slug: 'danyl-mclauchlan-writing-style',
    title: 'Why You Like Danyl McLauchlan\'s Writing Style',
    excerpt: 'Warm and unresolved. The McLauchlan way.',
    icon: '😈',
    color: '#8B7A6B',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.7,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-DANYL-MCLAUCHLAN': {
    type: 'how',
    slug: 'write-like-danyl-mclauchlan',
    title: 'Write Like Danyl McLauchlan',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '😈',
    color: '#8B7A6B',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.7,
  },

  'STYLE-DAVID-MALOUF': {
    type: 'combo',
    slug: 'david-malouf-writing-style',
    title: 'Why You Like David Malouf\'s Writing Style',
    excerpt: 'Lyrical and curious. The Malouf way.',
    icon: '🌅',
    color: '#C4A882',
    profile: 'poetic',
    stance: 'open',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      UK: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      AU: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      NZ: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
    },
  },

  'HOW-DAVID-MALOUF': {
    type: 'how',
    slug: 'write-like-david-malouf',
    title: 'Write Like David Malouf',
    excerpt: 'Let language lead. Invite response.',
    icon: '🌅',
    color: '#C4A882',
    profile: 'poetic',
    stance: 'open',
    confidence: 0.85,
  },

  'STYLE-DAVID-MARR': {
    type: 'combo',
    slug: 'david-marr-writing-style',
    title: 'Why You Like David Marr\'s Writing Style',
    excerpt: 'Direct and curious. The Marr way.',
    icon: '📰',
    color: '#7A9AAA',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.8,
    writers: {
      CA: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      UK: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      AU: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      NZ: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
    },
  },

  'HOW-DAVID-MARR': {
    type: 'how',
    slug: 'write-like-david-marr',
    title: 'Write Like David Marr',
    excerpt: 'Take a position. Invite response.',
    icon: '📰',
    color: '#7A9AAA',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.8,
  },

  'STYLE-DIANA-WICHTEL': {
    type: 'combo',
    slug: 'diana-wichtel-writing-style',
    title: 'Why You Like Diana Wichtel\'s Writing Style',
    excerpt: 'Warm and unresolved. The Wichtel way.',
    icon: '🎬',
    color: '#9A8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.72,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-DIANA-WICHTEL': {
    type: 'how',
    slug: 'write-like-diana-wichtel',
    title: 'Write Like Diana Wichtel',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '🎬',
    color: '#9A8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.72,
  },

  'STYLE-DIONNE-BRAND': {
    type: 'combo',
    slug: 'dionne-brand-writing-style',
    title: 'Why You Like Dionne Brand\'s Writing Style',
    excerpt: 'Lyrical and unresolved. The Brand way.',
    icon: '🌊',
    color: '#6B7A9A',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      UK: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      AU: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      NZ: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
    },
  },

  'HOW-DIONNE-BRAND': {
    type: 'how',
    slug: 'write-like-dionne-brand',
    title: 'Write Like Dionne Brand',
    excerpt: 'Let language lead. Hold the tension.',
    icon: '🌊',
    color: '#6B7A9A',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-ELEANOR-CATTON': {
    type: 'combo',
    slug: 'eleanor-catton-writing-style',
    title: 'Why You Like Eleanor Catton\'s Writing Style',
    excerpt: 'Complex and unresolved. The Catton way.',
    icon: '🌑',
    color: '#6B6B8B',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.88,
    writers: {
      CA: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      UK: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      AU: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      NZ: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
    },
  },

  'HOW-ELEANOR-CATTON': {
    type: 'how',
    slug: 'write-like-eleanor-catton',
    title: 'Write Like Eleanor Catton',
    excerpt: 'Build through compression. Hold the tension.',
    icon: '🌑',
    color: '#6B6B8B',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.88,
  },

  'STYLE-ELIZABETH-KNOX': {
    type: 'combo',
    slug: 'elizabeth-knox-writing-style',
    title: 'Why You Like Elizabeth Knox\'s Writing Style',
    excerpt: 'Complex and unresolved. The Knox way.',
    icon: '🌐',
    color: '#8B7A9A',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.75,
    writers: {
      CA: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      UK: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      AU: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      NZ: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
    },
  },

  'HOW-ELIZABETH-KNOX': {
    type: 'how',
    slug: 'write-like-elizabeth-knox',
    title: 'Write Like Elizabeth Knox',
    excerpt: 'Build through compression. Hold the tension.',
    icon: '🌐',
    color: '#8B7A9A',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.75,
  },

  'STYLE-EMILY-PERKINS': {
    type: 'combo',
    slug: 'emily-perkins-writing-style',
    title: 'Why You Like Emily Perkins\'s Writing Style',
    excerpt: 'Careful and unresolved. The Perkins way.',
    icon: '🌫️',
    color: '#9A9AB8',
    profile: 'hedged',
    stance: 'contradictory',
    confidence: 0.72,
    writers: {
      CA: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      UK: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      AU: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      NZ: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
    },
  },

  'HOW-EMILY-PERKINS': {
    type: 'how',
    slug: 'write-like-emily-perkins',
    title: 'Write Like Emily Perkins',
    excerpt: 'Stay honest about limits. Hold the tension.',
    icon: '🌫️',
    color: '#9A9AB8',
    profile: 'hedged',
    stance: 'contradictory',
    confidence: 0.72,
  },

  'STYLE-FIONA-KIDMAN': {
    type: 'combo',
    slug: 'fiona-kidman-writing-style',
    title: 'Why You Like Fiona Kidman\'s Writing Style',
    excerpt: 'Warm and curious. The Kidman way.',
    icon: '🌸',
    color: '#C4957A',
    profile: 'conversational',
    stance: 'open',
    confidence: 0.72,
    writers: {
      CA: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      UK: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      AU: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      NZ: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
    },
  },

  'HOW-FIONA-KIDMAN': {
    type: 'how',
    slug: 'write-like-fiona-kidman',
    title: 'Write Like Fiona Kidman',
    excerpt: 'Think alongside. Invite response.',
    icon: '🌸',
    color: '#C4957A',
    profile: 'conversational',
    stance: 'open',
    confidence: 0.72,
  },

  'STYLE-GAIL-JONES': {
    type: 'combo',
    slug: 'gail-jones-writing-style',
    title: 'Why You Like Gail Jones\'s Writing Style',
    excerpt: 'Lyrical and unresolved. The Jones way.',
    icon: '🎨',
    color: '#9A7A8B',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.8,
    writers: {
      CA: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      UK: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      AU: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      NZ: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
    },
  },

  'HOW-GAIL-JONES': {
    type: 'how',
    slug: 'write-like-gail-jones',
    title: 'Write Like Gail Jones',
    excerpt: 'Let language lead. Hold the tension.',
    icon: '🎨',
    color: '#9A7A8B',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.8,
  },

  'STYLE-GEOFF-DYER': {
    type: 'combo',
    slug: 'geoff-dyer-writing-style',
    title: 'Why You Like Geoff Dyer\'s Writing Style',
    excerpt: 'Warm and unresolved. The Dyer way.',
    icon: '📸',
    color: '#8B8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-GEOFF-DYER': {
    type: 'how',
    slug: 'write-like-geoff-dyer',
    title: 'Write Like Geoff Dyer',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '📸',
    color: '#8B8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-GEOFF-PARK': {
    type: 'combo',
    slug: 'geoff-park-writing-style',
    title: 'Why You Like Geoff Park\'s Writing Style',
    excerpt: 'Expansive and curious. The Park way.',
    icon: '🌿',
    color: '#7A9A7A',
    profile: 'longform',
    stance: 'open',
    confidence: 0.72,
    writers: {
      CA: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      UK: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      AU: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      NZ: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
    },
  },

  'HOW-GEOFF-PARK': {
    type: 'how',
    slug: 'write-like-geoff-park',
    title: 'Write Like Geoff Park',
    excerpt: 'Commit to depth. Invite response.',
    icon: '🌿',
    color: '#7A9A7A',
    profile: 'longform',
    stance: 'open',
    confidence: 0.72,
  },

  'STYLE-GEORGE-MEGALOGENIS': {
    type: 'combo',
    slug: 'george-megalogenis-writing-style',
    title: 'Why You Like George Megalogenis\'s Writing Style',
    excerpt: 'Precise and curious. The Megalogenis way.',
    icon: '📊',
    color: '#7A8B9A',
    profile: 'formal',
    stance: 'open',
    confidence: 0.78,
    writers: {
      CA: { writer: 'Isaiah Berlin', book: 'The Hedgehog and the Fox', why: 'Berlin\'s formality opens to genuine intellectual hospitality.' },
      UK: { writer: 'Isaiah Berlin', book: 'The Hedgehog and the Fox', why: 'Berlin\'s formality opens to genuine intellectual hospitality.' },
      AU: { writer: 'Isaiah Berlin', book: 'The Hedgehog and the Fox', why: 'Berlin\'s formality opens to genuine intellectual hospitality.' },
      NZ: { writer: 'Isaiah Berlin', book: 'The Hedgehog and the Fox', why: 'Berlin\'s formality opens to genuine intellectual hospitality.' },
    },
  },

  'HOW-GEORGE-MEGALOGENIS': {
    type: 'how',
    slug: 'write-like-george-megalogenis',
    title: 'Write Like George Megalogenis',
    excerpt: 'Earn authority. Invite response.',
    icon: '📊',
    color: '#7A8B9A',
    profile: 'formal',
    stance: 'open',
    confidence: 0.78,
  },

  'STYLE-GERALD-MURNANE': {
    type: 'combo',
    slug: 'gerald-murnane-writing-style',
    title: 'Why You Like Gerald Murnane\'s Writing Style',
    excerpt: 'Complex and certain. The Murnane way.',
    icon: '🏜️',
    color: '#9A8B7A',
    profile: 'dense',
    stance: 'closed',
    confidence: 0.82,
    writers: {
      CA: { writer: 'A.S. Byatt', book: 'Possession', why: 'Byatt\'s compression arrives at a considered verdict.' },
      UK: { writer: 'A.S. Byatt', book: 'Possession', why: 'Byatt\'s compression arrives at a considered verdict.' },
      AU: { writer: 'A.S. Byatt', book: 'Possession', why: 'Byatt\'s compression arrives at a considered verdict.' },
      NZ: { writer: 'A.S. Byatt', book: 'Possession', why: 'Byatt\'s compression arrives at a considered verdict.' },
    },
  },

  'HOW-GERALD-MURNANE': {
    type: 'how',
    slug: 'write-like-gerald-murnane',
    title: 'Write Like Gerald Murnane',
    excerpt: 'Build through compression. Arrive at certainty.',
    icon: '🏜️',
    color: '#9A8B7A',
    profile: 'dense',
    stance: 'closed',
    confidence: 0.82,
  },

  'STYLE-IAN-CROSS': {
    type: 'combo',
    slug: 'ian-cross-writing-style',
    title: 'Why You Like Ian Cross\'s Writing Style',
    excerpt: 'Spare and certain. The Cross way.',
    icon: '🗿',
    color: '#8B8B8B',
    profile: 'minimal',
    stance: 'closed',
    confidence: 0.65,
    writers: {
      CA: { writer: 'Samuel Beckett', book: 'Endgame', why: 'Nothing surplus. The conclusion was always already there.' },
      UK: { writer: 'Samuel Beckett', book: 'Endgame', why: 'Nothing surplus. The conclusion was always already there.' },
      AU: { writer: 'Samuel Beckett', book: 'Endgame', why: 'Nothing surplus. The conclusion was always already there.' },
      NZ: { writer: 'Samuel Beckett', book: 'Endgame', why: 'Nothing surplus. The conclusion was always already there.' },
    },
  },

  'HOW-IAN-CROSS': {
    type: 'how',
    slug: 'write-like-ian-cross',
    title: 'Write Like Ian Cross',
    excerpt: 'Strip to essentials. Arrive at certainty.',
    icon: '🗿',
    color: '#8B8B8B',
    profile: 'minimal',
    stance: 'closed',
    confidence: 0.65,
  },

  'STYLE-IAN-WEDDE': {
    type: 'combo',
    slug: 'ian-wedde-writing-style',
    title: 'Why You Like Ian Wedde\'s Writing Style',
    excerpt: 'Lyrical and unresolved. The Wedde way.',
    icon: '🌊',
    color: '#7A8B9A',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.7,
    writers: {
      CA: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      UK: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      AU: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      NZ: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
    },
  },

  'HOW-IAN-WEDDE': {
    type: 'how',
    slug: 'write-like-ian-wedde',
    title: 'Write Like Ian Wedde',
    excerpt: 'Let language lead. Hold the tension.',
    icon: '🌊',
    color: '#7A8B9A',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.7,
  },

  'STYLE-INGA-CLENDINNEN': {
    type: 'combo',
    slug: 'inga-clendinnen-writing-style',
    title: 'Why You Like Inga Clendinnen\'s Writing Style',
    excerpt: 'Expansive and curious. The Clendinnen way.',
    icon: '🏺',
    color: '#C4A882',
    profile: 'longform',
    stance: 'open',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      UK: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      AU: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      NZ: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
    },
  },

  'HOW-INGA-CLENDINNEN': {
    type: 'how',
    slug: 'write-like-inga-clendinnen',
    title: 'Write Like Inga Clendinnen',
    excerpt: 'Commit to depth. Invite response.',
    icon: '🏺',
    color: '#C4A882',
    profile: 'longform',
    stance: 'open',
    confidence: 0.85,
  },

  'STYLE-IRIS-MURDOCH': {
    type: 'combo',
    slug: 'iris-murdoch-writing-style',
    title: 'Why You Like Iris Murdoch\'s Writing Style',
    excerpt: 'Complex and unresolved. The Murdoch way.',
    icon: '🦋',
    color: '#8B7A9A',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.9,
    writers: {
      CA: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      UK: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      AU: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      NZ: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
    },
  },

  'HOW-IRIS-MURDOCH': {
    type: 'how',
    slug: 'write-like-iris-murdoch',
    title: 'Write Like Iris Murdoch',
    excerpt: 'Build through compression. Hold the tension.',
    icon: '🦋',
    color: '#8B7A9A',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.9,
  },

  'STYLE-JANE-KELSEY': {
    type: 'combo',
    slug: 'jane-kelsey-writing-style',
    title: 'Why You Like Jane Kelsey\'s Writing Style',
    excerpt: 'Precise and unresolved. The Kelsey way.',
    icon: '⚖️',
    color: '#7A8B7A',
    profile: 'formal',
    stance: 'contradictory',
    confidence: 0.72,
    writers: {
      CA: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      UK: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      AU: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      NZ: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
    },
  },

  'HOW-JANE-KELSEY': {
    type: 'how',
    slug: 'write-like-jane-kelsey',
    title: 'Write Like Jane Kelsey',
    excerpt: 'Earn authority. Hold the tension.',
    icon: '⚖️',
    color: '#7A8B7A',
    profile: 'formal',
    stance: 'contradictory',
    confidence: 0.72,
  },

  'STYLE-JANET-FRAME': {
    type: 'combo',
    slug: 'janet-frame-writing-style',
    title: 'Why You Like Janet Frame\'s Writing Style',
    excerpt: 'Lyrical and unresolved. The Frame way.',
    icon: '🪶',
    color: '#9A8B9A',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.9,
    writers: {
      CA: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      UK: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      AU: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      NZ: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
    },
  },

  'HOW-JANET-FRAME': {
    type: 'how',
    slug: 'write-like-janet-frame',
    title: 'Write Like Janet Frame',
    excerpt: 'Let language lead. Hold the tension.',
    icon: '🪶',
    color: '#9A8B9A',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.9,
  },

  'STYLE-JEFFREY-SIMPSON': {
    type: 'combo',
    slug: 'jeffrey-simpson-writing-style',
    title: 'Why You Like Jeffrey Simpson\'s Writing Style',
    excerpt: 'Precise and fair. The Simpson way.',
    icon: '🍁',
    color: '#8B9A8B',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.75,
    writers: {
      CA: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      UK: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      AU: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      NZ: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
    },
  },

  'HOW-JEFFREY-SIMPSON': {
    type: 'how',
    slug: 'write-like-jeffrey-simpson',
    title: 'Write Like Jeffrey Simpson',
    excerpt: 'Earn authority. Weigh fairly.',
    icon: '🍁',
    color: '#8B9A8B',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.75,
  },

  'STYLE-JOHN-FOWLES': {
    type: 'combo',
    slug: 'john-fowles-writing-style',
    title: 'Why You Like John Fowles\'s Writing Style',
    excerpt: 'Complex and unresolved. The Fowles way.',
    icon: '🌀',
    color: '#7A8B9A',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      UK: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      AU: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      NZ: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
    },
  },

  'HOW-JOHN-FOWLES': {
    type: 'how',
    slug: 'write-like-john-fowles',
    title: 'Write Like John Fowles',
    excerpt: 'Build through compression. Hold the tension.',
    icon: '🌀',
    color: '#7A8B9A',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-JOHN-IBBITSON': {
    type: 'combo',
    slug: 'john-ibbitson-writing-style',
    title: 'Why You Like John Ibbitson\'s Writing Style',
    excerpt: 'Precise and curious. The Ibbitson way.',
    icon: '🍁',
    color: '#8B9A8B',
    profile: 'formal',
    stance: 'open',
    confidence: 0.72,
    writers: {
      CA: { writer: 'Isaiah Berlin', book: 'The Hedgehog and the Fox', why: 'Berlin\'s formality opens to genuine intellectual hospitality.' },
      UK: { writer: 'Isaiah Berlin', book: 'The Hedgehog and the Fox', why: 'Berlin\'s formality opens to genuine intellectual hospitality.' },
      AU: { writer: 'Isaiah Berlin', book: 'The Hedgehog and the Fox', why: 'Berlin\'s formality opens to genuine intellectual hospitality.' },
      NZ: { writer: 'Isaiah Berlin', book: 'The Hedgehog and the Fox', why: 'Berlin\'s formality opens to genuine intellectual hospitality.' },
    },
  },

  'HOW-JOHN-IBBITSON': {
    type: 'how',
    slug: 'write-like-john-ibbitson',
    title: 'Write Like John Ibbitson',
    excerpt: 'Earn authority. Invite response.',
    icon: '🍁',
    color: '#8B9A8B',
    profile: 'formal',
    stance: 'open',
    confidence: 0.72,
  },

  'STYLE-JOHN-RALSTON-SAUL': {
    type: 'combo',
    slug: 'john-ralston-saul-writing-style',
    title: 'Why You Like John Ralston Saul\'s Writing Style',
    excerpt: 'Direct and unresolved. The Saul way.',
    icon: '🍁',
    color: '#8B7A6B',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.8,
    writers: {
      CA: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      UK: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      AU: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      NZ: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
    },
  },

  'HOW-JOHN-RALSTON-SAUL': {
    type: 'how',
    slug: 'write-like-john-ralston-saul',
    title: 'Write Like John Ralston Saul',
    excerpt: 'Take a position. Hold the tension.',
    icon: '🍁',
    color: '#8B7A6B',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.8,
  },

  'STYLE-JOHN-VAILLANT': {
    type: 'combo',
    slug: 'john-vaillant-writing-style',
    title: 'Why You Like John Vaillant\'s Writing Style',
    excerpt: 'Expansive and curious. The Vaillant way.',
    icon: '🐅',
    color: '#C4956A',
    profile: 'longform',
    stance: 'open',
    confidence: 0.82,
    writers: {
      CA: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      UK: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      AU: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      NZ: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
    },
  },

  'HOW-JOHN-VAILLANT': {
    type: 'how',
    slug: 'write-like-john-vaillant',
    title: 'Write Like John Vaillant',
    excerpt: 'Commit to depth. Invite response.',
    icon: '🐅',
    color: '#C4956A',
    profile: 'longform',
    stance: 'open',
    confidence: 0.82,
  },

  'STYLE-JOSEPH-BOYDEN': {
    type: 'combo',
    slug: 'joseph-boyden-writing-style',
    title: 'Why You Like Joseph Boyden\'s Writing Style',
    excerpt: 'Lyrical and unresolved. The Boyden way.',
    icon: '🦅',
    color: '#8B7A6B',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.78,
    writers: {
      CA: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      UK: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      AU: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      NZ: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
    },
  },

  'HOW-JOSEPH-BOYDEN': {
    type: 'how',
    slug: 'write-like-joseph-boyden',
    title: 'Write Like Joseph Boyden',
    excerpt: 'Let language lead. Hold the tension.',
    icon: '🦅',
    color: '#8B7A6B',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.78,
  },

  'STYLE-KATE-GRENVILLE': {
    type: 'combo',
    slug: 'kate-grenville-writing-style',
    title: 'Why You Like Kate Grenville\'s Writing Style',
    excerpt: 'Warm and curious. The Grenville way.',
    icon: '🌏',
    color: '#7AA87A',
    profile: 'conversational',
    stance: 'open',
    confidence: 0.8,
    writers: {
      CA: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      UK: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      AU: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      NZ: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
    },
  },

  'HOW-KATE-GRENVILLE': {
    type: 'how',
    slug: 'write-like-kate-grenville',
    title: 'Write Like Kate Grenville',
    excerpt: 'Think alongside. Invite response.',
    icon: '🌏',
    color: '#7AA87A',
    profile: 'conversational',
    stance: 'open',
    confidence: 0.8,
  },

  'STYLE-KERI-HULME': {
    type: 'combo',
    slug: 'keri-hulme-writing-style',
    title: 'Why You Like Keri Hulme\'s Writing Style',
    excerpt: 'Complex and unresolved. The Hulme way.',
    icon: '🌊',
    color: '#6B8B9A',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      UK: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      AU: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      NZ: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
    },
  },

  'HOW-KERI-HULME': {
    type: 'how',
    slug: 'write-like-keri-hulme',
    title: 'Write Like Keri Hulme',
    excerpt: 'Build through compression. Hold the tension.',
    icon: '🌊',
    color: '#6B8B9A',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-KIM-SCOTT': {
    type: 'combo',
    slug: 'kim-scott-writing-style',
    title: 'Why You Like Kim Scott\'s Writing Style',
    excerpt: 'Lyrical and curious. The Scott way.',
    icon: '🌅',
    color: '#C4956A',
    profile: 'poetic',
    stance: 'open',
    confidence: 0.8,
    writers: {
      CA: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      UK: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      AU: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      NZ: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
    },
  },

  'HOW-KIM-SCOTT': {
    type: 'how',
    slug: 'write-like-kim-scott',
    title: 'Write Like Kim Scott',
    excerpt: 'Let language lead. Invite response.',
    icon: '🌅',
    color: '#C4956A',
    profile: 'poetic',
    stance: 'open',
    confidence: 0.8,
  },

  'STYLE-LISA-MOORE': {
    type: 'combo',
    slug: 'lisa-moore-writing-style',
    title: 'Why You Like Lisa Moore\'s Writing Style',
    excerpt: 'Careful and unresolved. The Moore way.',
    icon: '❄️',
    color: '#8B9AB8',
    profile: 'hedged',
    stance: 'contradictory',
    confidence: 0.78,
    writers: {
      CA: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      UK: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      AU: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      NZ: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
    },
  },

  'HOW-LISA-MOORE': {
    type: 'how',
    slug: 'write-like-lisa-moore',
    title: 'Write Like Lisa Moore',
    excerpt: 'Stay honest about limits. Hold the tension.',
    icon: '❄️',
    color: '#8B9AB8',
    profile: 'hedged',
    stance: 'contradictory',
    confidence: 0.78,
  },

  'STYLE-LLOYD-JONES': {
    type: 'combo',
    slug: 'lloyd-jones-writing-style',
    title: 'Why You Like Lloyd Jones\'s Writing Style',
    excerpt: 'Careful and curious. The Jones way.',
    icon: '🌊',
    color: '#7A9AB8',
    profile: 'hedged',
    stance: 'open',
    confidence: 0.75,
    writers: {
      CA: { writer: 'Penelope Fitzgerald', book: 'The Bookshop', why: 'Fitzgerald\'s tentativeness is an invitation.' },
      UK: { writer: 'Penelope Fitzgerald', book: 'The Bookshop', why: 'Fitzgerald\'s tentativeness is an invitation.' },
      AU: { writer: 'Penelope Fitzgerald', book: 'The Bookshop', why: 'Fitzgerald\'s tentativeness is an invitation.' },
      NZ: { writer: 'Penelope Fitzgerald', book: 'The Bookshop', why: 'Fitzgerald\'s tentativeness is an invitation.' },
    },
  },

  'HOW-LLOYD-JONES': {
    type: 'how',
    slug: 'write-like-lloyd-jones',
    title: 'Write Like Lloyd Jones',
    excerpt: 'Stay honest about limits. Invite response.',
    icon: '🌊',
    color: '#7A9AB8',
    profile: 'hedged',
    stance: 'open',
    confidence: 0.75,
  },

  'STYLE-MARK-KINGWELL': {
    type: 'combo',
    slug: 'mark-kingwell-writing-style',
    title: 'Why You Like Mark Kingwell\'s Writing Style',
    excerpt: 'Precise and unresolved. The Kingwell way.',
    icon: '🏙️',
    color: '#8B8B9A',
    profile: 'formal',
    stance: 'contradictory',
    confidence: 0.8,
    writers: {
      CA: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      UK: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      AU: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      NZ: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
    },
  },

  'HOW-MARK-KINGWELL': {
    type: 'how',
    slug: 'write-like-mark-kingwell',
    title: 'Write Like Mark Kingwell',
    excerpt: 'Earn authority. Hold the tension.',
    icon: '🏙️',
    color: '#8B8B9A',
    profile: 'formal',
    stance: 'contradictory',
    confidence: 0.8,
  },

  'STYLE-MAURICE-GEE': {
    type: 'combo',
    slug: 'maurice-gee-writing-style',
    title: 'Why You Like Maurice Gee\'s Writing Style',
    excerpt: 'Spare and unresolved. The Gee way.',
    icon: '🌿',
    color: '#7A9A7A',
    profile: 'minimal',
    stance: 'contradictory',
    confidence: 0.75,
    writers: {
      CA: { writer: 'W.G. Sebald', book: 'The Rings of Saturn', why: 'Sebald\'s minimalism enacts the contradictions it describes.' },
      UK: { writer: 'W.G. Sebald', book: 'The Rings of Saturn', why: 'Sebald\'s minimalism enacts the contradictions it describes.' },
      AU: { writer: 'W.G. Sebald', book: 'The Rings of Saturn', why: 'Sebald\'s minimalism enacts the contradictions it describes.' },
      NZ: { writer: 'W.G. Sebald', book: 'The Rings of Saturn', why: 'Sebald\'s minimalism enacts the contradictions it describes.' },
    },
  },

  'HOW-MAURICE-GEE': {
    type: 'how',
    slug: 'write-like-maurice-gee',
    title: 'Write Like Maurice Gee',
    excerpt: 'Strip to essentials. Hold the tension.',
    icon: '🌿',
    color: '#7A9A7A',
    profile: 'minimal',
    stance: 'contradictory',
    confidence: 0.75,
  },

  'STYLE-MAVIS-GALLANT': {
    type: 'combo',
    slug: 'mavis-gallant-writing-style',
    title: 'Why You Like Mavis Gallant\'s Writing Style',
    excerpt: 'Precise and unresolved. The Gallant way.',
    icon: '🥐',
    color: '#9A8B7A',
    profile: 'formal',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      UK: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      AU: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      NZ: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
    },
  },

  'HOW-MAVIS-GALLANT': {
    type: 'how',
    slug: 'write-like-mavis-gallant',
    title: 'Write Like Mavis Gallant',
    excerpt: 'Earn authority. Hold the tension.',
    icon: '🥐',
    color: '#9A8B7A',
    profile: 'formal',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-MAX-HARRIS': {
    type: 'combo',
    slug: 'max-harris-writing-style',
    title: 'Why You Like Max Harris\'s Writing Style',
    excerpt: 'Direct and curious. The Harris way.',
    icon: '🌞',
    color: '#C4A87A',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.68,
    writers: {
      CA: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      UK: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      AU: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      NZ: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
    },
  },

  'HOW-MAX-HARRIS': {
    type: 'how',
    slug: 'write-like-max-harris',
    title: 'Write Like Max Harris',
    excerpt: 'Take a position. Invite response.',
    icon: '🌞',
    color: '#C4A87A',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.68,
  },

  'STYLE-MICHAEL-IGNATIEFF': {
    type: 'combo',
    slug: 'michael-ignatieff-writing-style',
    title: 'Why You Like Michael Ignatieff\'s Writing Style',
    excerpt: 'Precise and fair. The Ignatieff way.',
    icon: '🕊️',
    color: '#8B9AAA',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.85,
    writers: {
      CA: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      UK: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      AU: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      NZ: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
    },
  },

  'HOW-MICHAEL-IGNATIEFF': {
    type: 'how',
    slug: 'write-like-michael-ignatieff',
    title: 'Write Like Michael Ignatieff',
    excerpt: 'Earn authority. Weigh fairly.',
    icon: '🕊️',
    color: '#8B9AAA',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.85,
  },

  'STYLE-MICHAEL-KING': {
    type: 'combo',
    slug: 'michael-king-writing-style',
    title: 'Why You Like Michael King\'s Writing Style',
    excerpt: 'Expansive and fair. The King way.',
    icon: '🌿',
    color: '#7A9A8B',
    profile: 'longform',
    stance: 'balanced',
    confidence: 0.8,
    writers: {
      CA: { writer: 'Patrick Leigh Fermor', book: 'A Time of Gifts', why: 'Fermor\'s longform holds every perspective with equal care.' },
      UK: { writer: 'Patrick Leigh Fermor', book: 'A Time of Gifts', why: 'Fermor\'s longform holds every perspective with equal care.' },
      AU: { writer: 'Patrick Leigh Fermor', book: 'A Time of Gifts', why: 'Fermor\'s longform holds every perspective with equal care.' },
      NZ: { writer: 'Patrick Leigh Fermor', book: 'A Time of Gifts', why: 'Fermor\'s longform holds every perspective with equal care.' },
    },
  },

  'HOW-MICHAEL-KING': {
    type: 'how',
    slug: 'write-like-michael-king',
    title: 'Write Like Michael King',
    excerpt: 'Commit to depth. Weigh fairly.',
    icon: '🌿',
    color: '#7A9A8B',
    profile: 'longform',
    stance: 'balanced',
    confidence: 0.8,
  },

  'STYLE-MICHAEL-ONDAATJE': {
    type: 'combo',
    slug: 'michael-ondaatje-writing-style',
    title: 'Why You Like Michael Ondaatje\'s Writing Style',
    excerpt: 'Lyrical and curious. The Ondaatje way.',
    icon: '🌺',
    color: '#B87A6B',
    profile: 'poetic',
    stance: 'open',
    confidence: 0.88,
    writers: {
      CA: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      UK: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      AU: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      NZ: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
    },
  },

  'HOW-MICHAEL-ONDAATJE': {
    type: 'how',
    slug: 'write-like-michael-ondaatje',
    title: 'Write Like Michael Ondaatje',
    excerpt: 'Let language lead. Invite response.',
    icon: '🌺',
    color: '#B87A6B',
    profile: 'poetic',
    stance: 'open',
    confidence: 0.88,
  },

  'STYLE-MICHELLE-DE-KRETSER': {
    type: 'combo',
    slug: 'michelle-de-kretser-writing-style',
    title: 'Why You Like Michelle de Kretser\'s Writing Style',
    excerpt: 'Complex and unresolved. The Kretser way.',
    icon: '🌏',
    color: '#8B7A8B',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.8,
    writers: {
      CA: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      UK: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      AU: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      NZ: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
    },
  },

  'HOW-MICHELLE-DE-KRETSER': {
    type: 'how',
    slug: 'write-like-michelle-de-kretser',
    title: 'Write Like Michelle de Kretser',
    excerpt: 'Build through compression. Hold the tension.',
    icon: '🌏',
    color: '#8B7A8B',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.8,
  },

  'STYLE-MIRIAM-TOEWS': {
    type: 'combo',
    slug: 'miriam-toews-writing-style',
    title: 'Why You Like Miriam Toews\'s Writing Style',
    excerpt: 'Warm and unresolved. The Toews way.',
    icon: '❄️',
    color: '#9AB8C4',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-MIRIAM-TOEWS': {
    type: 'how',
    slug: 'write-like-miriam-toews',
    title: 'Write Like Miriam Toews',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '❄️',
    color: '#9AB8C4',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-MORDECAI-RICHLER': {
    type: 'combo',
    slug: 'mordecai-richler-writing-style',
    title: 'Why You Like Mordecai Richler\'s Writing Style',
    excerpt: 'Direct and unresolved. The Richler way.',
    icon: '🍁',
    color: '#B86B6B',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.88,
    writers: {
      CA: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      UK: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      AU: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      NZ: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
    },
  },

  'HOW-MORDECAI-RICHLER': {
    type: 'how',
    slug: 'write-like-mordecai-richler',
    title: 'Write Like Mordecai Richler',
    excerpt: 'Take a position. Hold the tension.',
    icon: '🍁',
    color: '#B86B6B',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.88,
  },

  'STYLE-NORTHROP-FRYE': {
    type: 'combo',
    slug: 'northrop-frye-writing-style',
    title: 'Why You Like Northrop Frye\'s Writing Style',
    excerpt: 'Precise and fair. The Frye way.',
    icon: '📚',
    color: '#8B8B7A',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.88,
    writers: {
      CA: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      UK: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      AU: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      NZ: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
    },
  },

  'HOW-NORTHROP-FRYE': {
    type: 'how',
    slug: 'write-like-northrop-frye',
    title: 'Write Like Northrop Frye',
    excerpt: 'Earn authority. Weigh fairly.',
    icon: '📚',
    color: '#8B8B7A',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.88,
  },

  'STYLE-OWEN-MARSHALL': {
    type: 'combo',
    slug: 'owen-marshall-writing-style',
    title: 'Why You Like Owen Marshall\'s Writing Style',
    excerpt: 'Spare and fair. The Marshall way.',
    icon: '🌾',
    color: '#C4B882',
    profile: 'minimal',
    stance: 'balanced',
    confidence: 0.72,
    writers: {
      CA: { writer: 'Alice Munro', book: 'Lives of Girls and Women', why: 'Munro\'s restraint holds all sides without declaring a winner.' },
      UK: { writer: 'Alice Munro', book: 'Lives of Girls and Women', why: 'Munro\'s restraint holds all sides without declaring a winner.' },
      AU: { writer: 'Alice Munro', book: 'Lives of Girls and Women', why: 'Munro\'s restraint holds all sides without declaring a winner.' },
      NZ: { writer: 'Alice Munro', book: 'Lives of Girls and Women', why: 'Munro\'s restraint holds all sides without declaring a winner.' },
    },
  },

  'HOW-OWEN-MARSHALL': {
    type: 'how',
    slug: 'write-like-owen-marshall',
    title: 'Write Like Owen Marshall',
    excerpt: 'Strip to essentials. Weigh fairly.',
    icon: '🌾',
    color: '#C4B882',
    profile: 'minimal',
    stance: 'balanced',
    confidence: 0.72,
  },

  'STYLE-PATRICIA-GRACE': {
    type: 'combo',
    slug: 'patricia-grace-writing-style',
    title: 'Why You Like Patricia Grace\'s Writing Style',
    excerpt: 'Warm and curious. The Grace way.',
    icon: '🌿',
    color: '#7AB87A',
    profile: 'conversational',
    stance: 'open',
    confidence: 0.8,
    writers: {
      CA: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      UK: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      AU: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      NZ: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
    },
  },

  'HOW-PATRICIA-GRACE': {
    type: 'how',
    slug: 'write-like-patricia-grace',
    title: 'Write Like Patricia Grace',
    excerpt: 'Think alongside. Invite response.',
    icon: '🌿',
    color: '#7AB87A',
    profile: 'conversational',
    stance: 'open',
    confidence: 0.8,
  },

  'STYLE-PATRICK-WHITE': {
    type: 'combo',
    slug: 'patrick-white-writing-style',
    title: 'Why You Like Patrick White\'s Writing Style',
    excerpt: 'Complex and unresolved. The White way.',
    icon: '🌵',
    color: '#8B8B6B',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.9,
    writers: {
      CA: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      UK: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      AU: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
      NZ: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s compression holds opposites without resolution.' },
    },
  },

  'HOW-PATRICK-WHITE': {
    type: 'how',
    slug: 'write-like-patrick-white',
    title: 'Write Like Patrick White',
    excerpt: 'Build through compression. Hold the tension.',
    icon: '🌵',
    color: '#8B8B6B',
    profile: 'dense',
    stance: 'contradictory',
    confidence: 0.9,
  },

  'STYLE-PAULA-MORRIS': {
    type: 'combo',
    slug: 'paula-morris-writing-style',
    title: 'Why You Like Paula Morris\'s Writing Style',
    excerpt: 'Warm and curious. The Morris way.',
    icon: '🌺',
    color: '#C4957A',
    profile: 'conversational',
    stance: 'open',
    confidence: 0.72,
    writers: {
      CA: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      UK: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      AU: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      NZ: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
    },
  },

  'HOW-PAULA-MORRIS': {
    type: 'how',
    slug: 'write-like-paula-morris',
    title: 'Write Like Paula Morris',
    excerpt: 'Think alongside. Invite response.',
    icon: '🌺',
    color: '#C4957A',
    profile: 'conversational',
    stance: 'open',
    confidence: 0.72,
  },

  'STYLE-PETER-CAREY': {
    type: 'combo',
    slug: 'peter-carey-writing-style',
    title: 'Why You Like Peter Carey\'s Writing Style',
    excerpt: 'Warm and unresolved. The Carey way.',
    icon: '🐊',
    color: '#8B9A6B',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.88,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-PETER-CAREY': {
    type: 'how',
    slug: 'write-like-peter-carey',
    title: 'Write Like Peter Carey',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '🐊',
    color: '#8B9A6B',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.88,
  },

  'STYLE-PIP-ADAM': {
    type: 'combo',
    slug: 'pip-adam-writing-style',
    title: 'Why You Like Pip Adam\'s Writing Style',
    excerpt: 'Questioning and unresolved. The Adam way.',
    icon: '🔮',
    color: '#8B8BA8',
    profile: 'interrogative',
    stance: 'contradictory',
    confidence: 0.72,
    writers: {
      CA: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
      UK: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
      AU: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
      NZ: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
    },
  },

  'HOW-PIP-ADAM': {
    type: 'how',
    slug: 'write-like-pip-adam',
    title: 'Write Like Pip Adam',
    excerpt: 'Ask the hard question. Hold the tension.',
    icon: '🔮',
    color: '#8B8BA8',
    profile: 'interrogative',
    stance: 'contradictory',
    confidence: 0.72,
  },

  'STYLE-RACHAEL-KING': {
    type: 'combo',
    slug: 'rachael-king-writing-style',
    title: 'Why You Like Rachael King\'s Writing Style',
    excerpt: 'Careful and unresolved. The King way.',
    icon: '🌑',
    color: '#8B8B9A',
    profile: 'hedged',
    stance: 'contradictory',
    confidence: 0.68,
    writers: {
      CA: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      UK: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      AU: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      NZ: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
    },
  },

  'HOW-RACHAEL-KING': {
    type: 'how',
    slug: 'write-like-rachael-king',
    title: 'Write Like Rachael King',
    excerpt: 'Stay honest about limits. Hold the tension.',
    icon: '🌑',
    color: '#8B8B9A',
    profile: 'hedged',
    stance: 'contradictory',
    confidence: 0.68,
  },

  'STYLE-RANDOLPH-STOW': {
    type: 'combo',
    slug: 'randolph-stow-writing-style',
    title: 'Why You Like Randolph Stow\'s Writing Style',
    excerpt: 'Spare and unresolved. The Stow way.',
    icon: '🏜️',
    color: '#C4A882',
    profile: 'minimal',
    stance: 'contradictory',
    confidence: 0.75,
    writers: {
      CA: { writer: 'W.G. Sebald', book: 'The Rings of Saturn', why: 'Sebald\'s minimalism enacts the contradictions it describes.' },
      UK: { writer: 'W.G. Sebald', book: 'The Rings of Saturn', why: 'Sebald\'s minimalism enacts the contradictions it describes.' },
      AU: { writer: 'W.G. Sebald', book: 'The Rings of Saturn', why: 'Sebald\'s minimalism enacts the contradictions it describes.' },
      NZ: { writer: 'W.G. Sebald', book: 'The Rings of Saturn', why: 'Sebald\'s minimalism enacts the contradictions it describes.' },
    },
  },

  'HOW-RANDOLPH-STOW': {
    type: 'how',
    slug: 'write-like-randolph-stow',
    title: 'Write Like Randolph Stow',
    excerpt: 'Strip to essentials. Hold the tension.',
    icon: '🏜️',
    color: '#C4A882',
    profile: 'minimal',
    stance: 'contradictory',
    confidence: 0.75,
  },

  'STYLE-RANGINUI-WALKER': {
    type: 'combo',
    slug: 'ranginui-walker-writing-style',
    title: 'Why You Like Ranginui Walker\'s Writing Style',
    excerpt: 'Direct and curious. The Walker way.',
    icon: '✊',
    color: '#8B7A6B',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.78,
    writers: {
      CA: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      UK: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      AU: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      NZ: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
    },
  },

  'HOW-RANGINUI-WALKER': {
    type: 'how',
    slug: 'write-like-ranginui-walker',
    title: 'Write Like Ranginui Walker',
    excerpt: 'Take a position. Invite response.',
    icon: '✊',
    color: '#8B7A6B',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.78,
  },

  'STYLE-REBECCA-SOLNIT': {
    type: 'combo',
    slug: 'rebecca-solnit-writing-style',
    title: 'Why You Like Rebecca Solnit\'s Writing Style',
    excerpt: 'Expansive and curious. The Solnit way.',
    icon: '🗺️',
    color: '#7A9AB8',
    profile: 'longform',
    stance: 'open',
    confidence: 0.9,
    writers: {
      CA: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      UK: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      AU: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      NZ: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
    },
  },

  'HOW-REBECCA-SOLNIT': {
    type: 'how',
    slug: 'write-like-rebecca-solnit',
    title: 'Write Like Rebecca Solnit',
    excerpt: 'Commit to depth. Invite response.',
    icon: '🗺️',
    color: '#7A9AB8',
    profile: 'longform',
    stance: 'open',
    confidence: 0.9,
  },

  'STYLE-RICHARD-FLANAGAN': {
    type: 'combo',
    slug: 'richard-flanagan-writing-style',
    title: 'Why You Like Richard Flanagan\'s Writing Style',
    excerpt: 'Expansive and unresolved. The Flanagan way.',
    icon: '🌊',
    color: '#6B8B9A',
    profile: 'longform',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Helen Garner', book: 'The First Stone', why: 'Garner\'s patience with contradiction is structural.' },
      UK: { writer: 'Helen Garner', book: 'The First Stone', why: 'Garner\'s patience with contradiction is structural.' },
      AU: { writer: 'Helen Garner', book: 'The First Stone', why: 'Garner\'s patience with contradiction is structural.' },
      NZ: { writer: 'Helen Garner', book: 'The First Stone', why: 'Garner\'s patience with contradiction is structural.' },
    },
  },

  'HOW-RICHARD-FLANAGAN': {
    type: 'how',
    slug: 'write-like-richard-flanagan',
    title: 'Write Like Richard Flanagan',
    excerpt: 'Commit to depth. Hold the tension.',
    icon: '🌊',
    color: '#6B8B9A',
    profile: 'longform',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-ROBERT-DESSAIX': {
    type: 'combo',
    slug: 'robert-dessaix-writing-style',
    title: 'Why You Like Robert Dessaix\'s Writing Style',
    excerpt: 'Warm and unresolved. The Dessaix way.',
    icon: '🥂',
    color: '#9A8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.72,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-ROBERT-DESSAIX': {
    type: 'how',
    slug: 'write-like-robert-dessaix',
    title: 'Write Like Robert Dessaix',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '🥂',
    color: '#9A8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.72,
  },

  'STYLE-ROBERT-HUGHES': {
    type: 'combo',
    slug: 'robert-hughes-writing-style',
    title: 'Why You Like Robert Hughes\'s Writing Style',
    excerpt: 'Direct and unresolved. The Hughes way.',
    icon: '🎨',
    color: '#B87A5A',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.88,
    writers: {
      CA: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      UK: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      AU: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      NZ: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
    },
  },

  'HOW-ROBERT-HUGHES': {
    type: 'how',
    slug: 'write-like-robert-hughes',
    title: 'Write Like Robert Hughes',
    excerpt: 'Take a position. Hold the tension.',
    icon: '🎨',
    color: '#B87A5A',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.88,
  },

  'STYLE-ROBERTSON-DAVIES': {
    type: 'combo',
    slug: 'robertson-davies-writing-style',
    title: 'Why You Like Robertson Davies\'s Writing Style',
    excerpt: 'Warm and fair. The Davies way.',
    icon: '🎭',
    color: '#9A8B6B',
    profile: 'conversational',
    stance: 'balanced',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Malcolm Gladwell', book: 'Outliers', why: 'Gladwell gives every argument its fair hearing.' },
      UK: { writer: 'Malcolm Gladwell', book: 'Outliers', why: 'Gladwell gives every argument its fair hearing.' },
      AU: { writer: 'Malcolm Gladwell', book: 'Outliers', why: 'Gladwell gives every argument its fair hearing.' },
      NZ: { writer: 'Malcolm Gladwell', book: 'Outliers', why: 'Gladwell gives every argument its fair hearing.' },
    },
  },

  'HOW-ROBERTSON-DAVIES': {
    type: 'how',
    slug: 'write-like-robertson-davies',
    title: 'Write Like Robertson Davies',
    excerpt: 'Think alongside. Weigh fairly.',
    icon: '🎭',
    color: '#9A8B6B',
    profile: 'conversational',
    stance: 'balanced',
    confidence: 0.85,
  },

  'STYLE-SHEILA-HETI': {
    type: 'combo',
    slug: 'sheila-heti-writing-style',
    title: 'Why You Like Sheila Heti\'s Writing Style',
    excerpt: 'Questioning and unresolved. The Heti way.',
    icon: '🪞',
    color: '#9A9AAA',
    profile: 'interrogative',
    stance: 'contradictory',
    confidence: 0.82,
    writers: {
      CA: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
      UK: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
      AU: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
      NZ: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
    },
  },

  'HOW-SHEILA-HETI': {
    type: 'how',
    slug: 'write-like-sheila-heti',
    title: 'Write Like Sheila Heti',
    excerpt: 'Ask the hard question. Hold the tension.',
    icon: '🪞',
    color: '#9A9AAA',
    profile: 'interrogative',
    stance: 'contradictory',
    confidence: 0.82,
  },

  'STYLE-SONYA-HARTNETT': {
    type: 'combo',
    slug: 'sonya-hartnett-writing-style',
    title: 'Why You Like Sonya Hartnett\'s Writing Style',
    excerpt: 'Lyrical and certain. The Hartnett way.',
    icon: '🌑',
    color: '#8B8BA8',
    profile: 'poetic',
    stance: 'closed',
    confidence: 0.78,
    writers: {
      CA: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
      UK: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
      AU: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
      NZ: { writer: 'Penelope Fitzgerald', book: 'The Gate of Angels', why: 'Fitzgerald\'s lyricism arrives at quiet certainty.' },
    },
  },

  'HOW-SONYA-HARTNETT': {
    type: 'how',
    slug: 'write-like-sonya-hartnett',
    title: 'Write Like Sonya Hartnett',
    excerpt: 'Let language lead. Arrive at certainty.',
    icon: '🌑',
    color: '#8B8BA8',
    profile: 'poetic',
    stance: 'closed',
    confidence: 0.78,
  },

  'STYLE-STAN-GRANT': {
    type: 'combo',
    slug: 'stan-grant-writing-style',
    title: 'Why You Like Stan Grant\'s Writing Style',
    excerpt: 'Direct and unresolved. The Grant way.',
    icon: '🌏',
    color: '#8B7A6B',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.82,
    writers: {
      CA: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      UK: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      AU: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
      NZ: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s paradoxes are arguments, not ornaments.' },
    },
  },

  'HOW-STAN-GRANT': {
    type: 'how',
    slug: 'write-like-stan-grant',
    title: 'Write Like Stan Grant',
    excerpt: 'Take a position. Hold the tension.',
    icon: '🌏',
    color: '#8B7A6B',
    profile: 'assertive',
    stance: 'contradictory',
    confidence: 0.82,
  },

  'STYLE-STEVE-BRAUNIAS': {
    type: 'combo',
    slug: 'steve-braunias-writing-style',
    title: 'Why You Like Steve Braunias\'s Writing Style',
    excerpt: 'Warm and unresolved. The Braunias way.',
    icon: '📰',
    color: '#9A8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.75,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-STEVE-BRAUNIAS': {
    type: 'how',
    slug: 'write-like-steve-braunias',
    title: 'Write Like Steve Braunias',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '📰',
    color: '#9A8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.75,
  },

  'STYLE-STUART-MCLEAN': {
    type: 'combo',
    slug: 'stuart-mclean-writing-style',
    title: 'Why You Like Stuart McLean\'s Writing Style',
    excerpt: 'Warm and curious. The McLean way.',
    icon: '🍁',
    color: '#C4A882',
    profile: 'conversational',
    stance: 'open',
    confidence: 0.78,
    writers: {
      CA: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      UK: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      AU: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
      NZ: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s warmth keeps the door permanently open.' },
    },
  },

  'HOW-STUART-MCLEAN': {
    type: 'how',
    slug: 'write-like-stuart-mclean',
    title: 'Write Like Stuart McLean',
    excerpt: 'Think alongside. Invite response.',
    icon: '🍁',
    color: '#C4A882',
    profile: 'conversational',
    stance: 'open',
    confidence: 0.78,
  },

  'STYLE-THOMAS-HOMER-DIXON': {
    type: 'combo',
    slug: 'thomas-homer-dixon-writing-style',
    title: 'Why You Like Thomas Homer-Dixon\'s Writing Style',
    excerpt: 'Expansive and fair. The Homer-Dixon way.',
    icon: '🌍',
    color: '#7A9A8B',
    profile: 'longform',
    stance: 'balanced',
    confidence: 0.8,
    writers: {
      CA: { writer: 'Patrick Leigh Fermor', book: 'A Time of Gifts', why: 'Fermor\'s longform holds every perspective with equal care.' },
      UK: { writer: 'Patrick Leigh Fermor', book: 'A Time of Gifts', why: 'Fermor\'s longform holds every perspective with equal care.' },
      AU: { writer: 'Patrick Leigh Fermor', book: 'A Time of Gifts', why: 'Fermor\'s longform holds every perspective with equal care.' },
      NZ: { writer: 'Patrick Leigh Fermor', book: 'A Time of Gifts', why: 'Fermor\'s longform holds every perspective with equal care.' },
    },
  },

  'HOW-THOMAS-HOMER-DIXON': {
    type: 'how',
    slug: 'write-like-thomas-homer-dixon',
    title: 'Write Like Thomas Homer-Dixon',
    excerpt: 'Commit to depth. Weigh fairly.',
    icon: '🌍',
    color: '#7A9A8B',
    profile: 'longform',
    stance: 'balanced',
    confidence: 0.8,
  },

  'STYLE-THOMAS-KENEALLY': {
    type: 'combo',
    slug: 'thomas-keneally-writing-style',
    title: 'Why You Like Thomas Keneally\'s Writing Style',
    excerpt: 'Expansive and curious. The Keneally way.',
    icon: '🌏',
    color: '#8B9A7A',
    profile: 'longform',
    stance: 'open',
    confidence: 0.82,
    writers: {
      CA: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      UK: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      AU: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      NZ: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
    },
  },

  'HOW-THOMAS-KENEALLY': {
    type: 'how',
    slug: 'write-like-thomas-keneally',
    title: 'Write Like Thomas Keneally',
    excerpt: 'Commit to depth. Invite response.',
    icon: '🌏',
    color: '#8B9A7A',
    profile: 'longform',
    stance: 'open',
    confidence: 0.82,
  },

  'STYLE-THOMAS-KING': {
    type: 'combo',
    slug: 'thomas-king-writing-style',
    title: 'Why You Like Thomas King\'s Writing Style',
    excerpt: 'Warm and unresolved. The King way.',
    icon: '🦅',
    color: '#9A8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-THOMAS-KING': {
    type: 'how',
    slug: 'write-like-thomas-king',
    title: 'Write Like Thomas King',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '🦅',
    color: '#9A8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-TIM-FLANNERY': {
    type: 'combo',
    slug: 'tim-flannery-writing-style',
    title: 'Why You Like Tim Flannery\'s Writing Style',
    excerpt: 'Expansive and curious. The Flannery way.',
    icon: '🦘',
    color: '#8B9A7A',
    profile: 'longform',
    stance: 'open',
    confidence: 0.82,
    writers: {
      CA: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      UK: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      AU: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
      NZ: { writer: 'Robert Manne', book: 'Left Right Left', why: 'Manne\'s patience with the reader is genuine.' },
    },
  },

  'HOW-TIM-FLANNERY': {
    type: 'how',
    slug: 'write-like-tim-flannery',
    title: 'Write Like Tim Flannery',
    excerpt: 'Commit to depth. Invite response.',
    icon: '🦘',
    color: '#8B9A7A',
    profile: 'longform',
    stance: 'open',
    confidence: 0.82,
  },

  'STYLE-TIM-SOUTPHOMMASANE': {
    type: 'combo',
    slug: 'tim-soutphommasane-writing-style',
    title: 'Why You Like Tim Soutphommasane\'s Writing Style',
    excerpt: 'Precise and fair. The Soutphommasane way.',
    icon: '🌏',
    color: '#7A8B9A',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.75,
    writers: {
      CA: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      UK: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      AU: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      NZ: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
    },
  },

  'HOW-TIM-SOUTPHOMMASANE': {
    type: 'how',
    slug: 'write-like-tim-soutphommasane',
    title: 'Write Like Tim Soutphommasane',
    excerpt: 'Earn authority. Weigh fairly.',
    icon: '🌏',
    color: '#7A8B9A',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.75,
  },

  'STYLE-TIM-WINTON': {
    type: 'combo',
    slug: 'tim-winton-writing-style',
    title: 'Why You Like Tim Winton\'s Writing Style',
    excerpt: 'Warm and unresolved. The Winton way.',
    icon: '🌊',
    color: '#6B8B9A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.9,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-TIM-WINTON': {
    type: 'how',
    slug: 'write-like-tim-winton',
    title: 'Write Like Tim Winton',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '🌊',
    color: '#6B8B9A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.9,
  },

  'STYLE-TOM-MCCARTHY': {
    type: 'combo',
    slug: 'tom-mccarthy-writing-style',
    title: 'Why You Like Tom McCarthy\'s Writing Style',
    excerpt: 'Complex and certain. The McCarthy way.',
    icon: '⚙️',
    color: '#7A7A8B',
    profile: 'dense',
    stance: 'closed',
    confidence: 0.82,
    writers: {
      CA: { writer: 'A.S. Byatt', book: 'Possession', why: 'Byatt\'s compression arrives at a considered verdict.' },
      UK: { writer: 'A.S. Byatt', book: 'Possession', why: 'Byatt\'s compression arrives at a considered verdict.' },
      AU: { writer: 'A.S. Byatt', book: 'Possession', why: 'Byatt\'s compression arrives at a considered verdict.' },
      NZ: { writer: 'A.S. Byatt', book: 'Possession', why: 'Byatt\'s compression arrives at a considered verdict.' },
    },
  },

  'HOW-TOM-MCCARTHY': {
    type: 'how',
    slug: 'write-like-tom-mccarthy',
    title: 'Write Like Tom McCarthy',
    excerpt: 'Build through compression. Arrive at certainty.',
    icon: '⚙️',
    color: '#7A7A8B',
    profile: 'dense',
    stance: 'closed',
    confidence: 0.82,
  },

  'STYLE-VINCENT-OSULLIVAN': {
    type: 'combo',
    slug: 'vincent-osullivan-writing-style',
    title: 'Why You Like Vincent O\'Sullivan\'s Writing Style',
    excerpt: 'Lyrical and unresolved. The O'Sullivan way.',
    icon: '🪶',
    color: '#9A8BA8',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.75,
    writers: {
      CA: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      UK: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      AU: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
      NZ: { writer: 'Jeanette Winterson', book: 'Written on the Body', why: 'Winterson\'s language enacts the contradictions it explores.' },
    },
  },

  'HOW-VINCENT-OSULLIVAN': {
    type: 'how',
    slug: 'write-like-vincent-osullivan',
    title: 'Write Like Vincent O\'Sullivan',
    excerpt: 'Let language lead. Hold the tension.',
    icon: '🪶',
    color: '#9A8BA8',
    profile: 'poetic',
    stance: 'contradictory',
    confidence: 0.75,
  },

  'STYLE-WILL-FERGUSON': {
    type: 'combo',
    slug: 'will-ferguson-writing-style',
    title: 'Why You Like Will Ferguson\'s Writing Style',
    excerpt: 'Warm and unresolved. The Ferguson way.',
    icon: '🍁',
    color: '#9A8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.75,
    writers: {
      CA: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      AU: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
      NZ: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith\'s voice embodies the contradictions it explores.' },
    },
  },

  'HOW-WILL-FERGUSON': {
    type: 'how',
    slug: 'write-like-will-ferguson',
    title: 'Write Like Will Ferguson',
    excerpt: 'Think alongside. Hold the tension.',
    icon: '🍁',
    color: '#9A8B7A',
    profile: 'conversational',
    stance: 'contradictory',
    confidence: 0.75,
  },

  'STYLE-WITI-IHIMAERA': {
    type: 'combo',
    slug: 'witi-ihimaera-writing-style',
    title: 'Why You Like Witi Ihimaera\'s Writing Style',
    excerpt: 'Lyrical and curious. The Ihimaera way.',
    icon: '🌺',
    color: '#C4957A',
    profile: 'poetic',
    stance: 'open',
    confidence: 0.82,
    writers: {
      CA: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      UK: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      AU: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
      NZ: { writer: 'Virginia Woolf', book: 'The Waves', why: 'Woolf\'s language opens outward, always.' },
    },
  },

  'HOW-WITI-IHIMAERA': {
    type: 'how',
    slug: 'write-like-witi-ihimaera',
    title: 'Write Like Witi Ihimaera',
    excerpt: 'Let language lead. Invite response.',
    icon: '🌺',
    color: '#C4957A',
    profile: 'poetic',
    stance: 'open',
    confidence: 0.82,
  },

  'STYLE-CORMAC-MCCARTHY': {
    type: 'combo',
    slug: 'cormac-mccarthy-writing-style',
    title: 'Why You Like Cormac McCarthy\'s Writing Style',
    excerpt: 'Spare and certain. The McCarthy way.',
    icon: '🌵',
    color: '#8B7355',
    profile: 'minimal',
    stance: 'closed',
    confidence: 0.95,
    writers: {
      CA: { writer: 'Samuel Beckett', book: 'Endgame', why: 'Nothing surplus. The conclusion was always already there.' },
      UK: { writer: 'Samuel Beckett', book: 'Endgame', why: 'Nothing surplus. The conclusion was always already there.' },
      AU: { writer: 'Samuel Beckett', book: 'Endgame', why: 'Nothing surplus. The conclusion was always already there.' },
      NZ: { writer: 'Samuel Beckett', book: 'Endgame', why: 'Nothing surplus. The conclusion was always already there.' },
    },
  },

  'HOW-CORMAC-MCCARTHY': {
    type: 'how',
    slug: 'write-like-cormac-mccarthy',
    title: 'Write Like Cormac McCarthy',
    excerpt: 'Strip to essentials. Arrive at certainty.',
    icon: '🌵',
    color: '#8B7355',
    profile: 'minimal',
    stance: 'closed',
    confidence: 0.95,
  },

  'STYLE-TONY-JUDT': {
    type: 'combo',
    slug: 'tony-judt-writing-style',
    title: 'Why You Like Tony Judt\'s Writing Style',
    excerpt: 'Precise and fair. The Judt way.',
    icon: '🏛️',
    color: '#7A8B9A',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.9,
    writers: {
      CA: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      UK: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      AU: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
      NZ: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart\'s formal register gives all sides serious treatment.' },
    },
  },

  'HOW-TONY-JUDT': {
    type: 'how',
    slug: 'write-like-tony-judt',
    title: 'Write Like Tony Judt',
    excerpt: 'Earn authority. Weigh fairly.',
    icon: '🏛️',
    color: '#7A8B9A',
    profile: 'formal',
    stance: 'balanced',
    confidence: 0.9,
  },

  'STYLE-AMARTYA-SEN': {
    type: 'combo',
    slug: 'amartya-sen-writing-style',
    title: 'Why You Like Amartya Sen\'s Writing Style',
    excerpt: 'Precise and unresolved. The Sen way.',
    icon: '⚖️',
    color: '#8B9A8B',
    profile: 'formal',
    stance: 'contradictory',
    confidence: 0.88,
    writers: {
      CA: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      UK: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      AU: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
      NZ: { writer: 'Martin Amis', book: 'Experience', why: 'Amis\'s formal surface holds irresolvable tensions.' },
    },
  },

  'HOW-AMARTYA-SEN': {
    type: 'how',
    slug: 'write-like-amartya-sen',
    title: 'Write Like Amartya Sen',
    excerpt: 'Earn authority. Hold the tension.',
    icon: '⚖️',
    color: '#8B9A8B',
    profile: 'formal',
    stance: 'contradictory',
    confidence: 0.88,
  },

  'STYLE-JAMES-WOOD': {
    type: 'combo',
    slug: 'james-wood-writing-style',
    title: 'Why You Like James Wood\'s Writing Style',
    excerpt: 'Questioning and fair. The Wood way.',
    icon: '📖',
    color: '#8B8B7A',
    profile: 'interrogative',
    stance: 'balanced',
    confidence: 0.85,
    writers: {
      CA: { writer: 'John Berger', book: 'G.', why: 'Berger interrogates every position with equal rigour.' },
      UK: { writer: 'John Berger', book: 'G.', why: 'Berger interrogates every position with equal rigour.' },
      AU: { writer: 'John Berger', book: 'G.', why: 'Berger interrogates every position with equal rigour.' },
      NZ: { writer: 'John Berger', book: 'G.', why: 'Berger interrogates every position with equal rigour.' },
    },
  },

  'HOW-JAMES-WOOD': {
    type: 'how',
    slug: 'write-like-james-wood',
    title: 'Write Like James Wood',
    excerpt: 'Ask the hard question. Weigh fairly.',
    icon: '📖',
    color: '#8B8B7A',
    profile: 'interrogative',
    stance: 'balanced',
    confidence: 0.85,
  },

  'STYLE-ROBERT-CARO': {
    type: 'combo',
    slug: 'robert-caro-writing-style',
    title: 'Why You Like Robert Caro\'s Writing Style',
    excerpt: 'Expansive and certain. The Caro way.',
    icon: '🏛️',
    color: '#8B7A6B',
    profile: 'longform',
    stance: 'closed',
    confidence: 0.92,
    writers: {
      CA: { writer: 'Hilary Mantel', book: 'Wolf Hall', why: 'Mantel\'s accumulation arrives at total certainty.' },
      UK: { writer: 'Hilary Mantel', book: 'Wolf Hall', why: 'Mantel\'s accumulation arrives at total certainty.' },
      AU: { writer: 'Hilary Mantel', book: 'Wolf Hall', why: 'Mantel\'s accumulation arrives at total certainty.' },
      NZ: { writer: 'Hilary Mantel', book: 'Wolf Hall', why: 'Mantel\'s accumulation arrives at total certainty.' },
    },
  },

  'HOW-ROBERT-CARO': {
    type: 'how',
    slug: 'write-like-robert-caro',
    title: 'Write Like Robert Caro',
    excerpt: 'Commit to depth. Arrive at certainty.',
    icon: '🏛️',
    color: '#8B7A6B',
    profile: 'longform',
    stance: 'closed',
    confidence: 0.92,
  },

  'STYLE-SUSAN-SONTAG': {
    type: 'combo',
    slug: 'susan-sontag-writing-style',
    title: 'Why You Like Susan Sontag\'s Writing Style',
    excerpt: 'Direct and curious. The Sontag way.',
    icon: '📷',
    color: '#8B8B9A',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.92,
    writers: {
      CA: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      UK: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      AU: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
      NZ: { writer: 'Ian McEwan', book: 'Saturday', why: 'McEwan\'s prose holds conviction and curiosity in equal measure.' },
    },
  },

  'HOW-SUSAN-SONTAG': {
    type: 'how',
    slug: 'write-like-susan-sontag',
    title: 'Write Like Susan Sontag',
    excerpt: 'Take a position. Invite response.',
    icon: '📷',
    color: '#8B8B9A',
    profile: 'assertive',
    stance: 'open',
    confidence: 0.92,
  },

  'STYLE-MICHAEL-FRAYN': {
    type: 'combo',
    slug: 'michael-frayn-writing-style',
    title: 'Why You Like Michael Frayn\'s Writing Style',
    excerpt: 'Questioning and fair. The Frayn way.',
    icon: '🎭',
    color: '#9A8B7A',
    profile: 'interrogative',
    stance: 'balanced',
    confidence: 0.82,
    writers: {
      CA: { writer: 'John Berger', book: 'G.', why: 'Berger interrogates every position with equal rigour.' },
      UK: { writer: 'John Berger', book: 'G.', why: 'Berger interrogates every position with equal rigour.' },
      AU: { writer: 'John Berger', book: 'G.', why: 'Berger interrogates every position with equal rigour.' },
      NZ: { writer: 'John Berger', book: 'G.', why: 'Berger interrogates every position with equal rigour.' },
    },
  },

  'HOW-MICHAEL-FRAYN': {
    type: 'how',
    slug: 'write-like-michael-frayn',
    title: 'Write Like Michael Frayn',
    excerpt: 'Ask the hard question. Weigh fairly.',
    icon: '🎭',
    color: '#9A8B7A',
    profile: 'interrogative',
    stance: 'balanced',
    confidence: 0.82,
  },

  'STYLE-ANNE-ENRIGHT': {
    type: 'combo',
    slug: 'anne-enright-writing-style',
    title: 'Why You Like Anne Enright\'s Writing Style',
    excerpt: 'Careful and unresolved. The Enright way.',
    icon: '🍀',
    color: '#8B9A7A',
    profile: 'hedged',
    stance: 'contradictory',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      UK: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      AU: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
      NZ: { writer: 'Muriel Spark', book: 'The Prime of Miss Jean Brodie', why: 'Spark\'s precision enacts the contradictions it names.' },
    },
  },

  'HOW-ANNE-ENRIGHT': {
    type: 'how',
    slug: 'write-like-anne-enright',
    title: 'Write Like Anne Enright',
    excerpt: 'Stay honest about limits. Hold the tension.',
    icon: '🍀',
    color: '#8B9A7A',
    profile: 'hedged',
    stance: 'contradictory',
    confidence: 0.85,
  },

  'STYLE-COLM-TOIBIN': {
    type: 'combo',
    slug: 'colm-toibin-writing-style',
    title: 'Why You Like Colm Toibin\'s Writing Style',
    excerpt: 'Careful and certain. The Toibin way.',
    icon: '🌊',
    color: '#7A8B9A',
    profile: 'hedged',
    stance: 'closed',
    confidence: 0.88,
    writers: {
      CA: { writer: 'Kazuo Ishiguro', book: 'The Remains of the Day', why: 'Ishiguro\'s qualifications arrive at devastating certainty.' },
      UK: { writer: 'Kazuo Ishiguro', book: 'The Remains of the Day', why: 'Ishiguro\'s qualifications arrive at devastating certainty.' },
      AU: { writer: 'Kazuo Ishiguro', book: 'The Remains of the Day', why: 'Ishiguro\'s qualifications arrive at devastating certainty.' },
      NZ: { writer: 'Kazuo Ishiguro', book: 'The Remains of the Day', why: 'Ishiguro\'s qualifications arrive at devastating certainty.' },
    },
  },

  'HOW-COLM-TOIBIN': {
    type: 'how',
    slug: 'write-like-colm-toibin',
    title: 'Write Like Colm Toibin',
    excerpt: 'Stay honest about limits. Arrive at certainty.',
    icon: '🌊',
    color: '#7A8B9A',
    profile: 'hedged',
    stance: 'closed',
    confidence: 0.88,
  },

  'STYLE-RACHEL-CUSK': {
    type: 'combo',
    slug: 'rachel-cusk-writing-style',
    title: 'Why You Like Rachel Cusk\'s Writing Style',
    excerpt: 'Questioning and unresolved. The Cusk way.',
    icon: '🪞',
    color: '#9A9AB8',
    profile: 'interrogative',
    stance: 'contradictory',
    confidence: 0.88,
    writers: {
      CA: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
      UK: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
      AU: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
      NZ: { writer: 'Samuel Beckett', book: 'Waiting for Godot', why: 'Beckett\'s questions resist every resolution.' },
    },
  },

  'HOW-RACHEL-CUSK': {
    type: 'how',
    slug: 'write-like-rachel-cusk',
    title: 'Write Like Rachel Cusk',
    excerpt: 'Ask the hard question. Hold the tension.',
    icon: '🪞',
    color: '#9A9AB8',
    profile: 'interrogative',
    stance: 'contradictory',
    confidence: 0.88,
  },

  'STYLE-LIONEL-SHRIVER': {
    type: 'combo',
    slug: 'lionel-shriver-writing-style',
    title: 'Why You Like Lionel Shriver\'s Writing Style',
    excerpt: 'Direct and certain. The Shriver way.',
    icon: '⚡',
    color: '#B87A7A',
    profile: 'assertive',
    stance: 'closed',
    confidence: 0.82,
    writers: {
      CA: { writer: 'George Orwell', book: 'Essays', why: 'Orwell\'s clarity is absolute — he has decided and he tells you.' },
      UK: { writer: 'George Orwell', book: 'Essays', why: 'Orwell\'s clarity is absolute — he has decided and he tells you.' },
      AU: { writer: 'George Orwell', book: 'Essays', why: 'Orwell\'s clarity is absolute — he has decided and he tells you.' },
      NZ: { writer: 'George Orwell', book: 'Essays', why: 'Orwell\'s clarity is absolute — he has decided and he tells you.' },
    },
  },

  'HOW-LIONEL-SHRIVER': {
    type: 'how',
    slug: 'write-like-lionel-shriver',
    title: 'Write Like Lionel Shriver',
    excerpt: 'Take a position. Arrive at certainty.',
    icon: '⚡',
    color: '#B87A7A',
    profile: 'assertive',
    stance: 'closed',
    confidence: 0.82,
  },

  'STYLE-JOHN-MCGAHERN': {
    type: 'combo',
    slug: 'john-mcgahern-writing-style',
    title: 'Why You Like John McGahern\'s Writing Style',
    excerpt: 'Spare and curious. The McGahern way.',
    icon: '🌾',
    color: '#8B9A7A',
    profile: 'minimal',
    stance: 'open',
    confidence: 0.85,
    writers: {
      CA: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
      UK: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
      AU: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
      NZ: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips to the bone and leaves room for the reader.' },
    },
  },

  'HOW-JOHN-MCGAHERN': {
    type: 'how',
    slug: 'write-like-john-mcgahern',
    title: 'Write Like John McGahern',
    excerpt: 'Strip to essentials. Invite response.',
    icon: '🌾',
    color: '#8B9A7A',
    profile: 'minimal',
    stance: 'open',
    confidence: 0.85,
  },

};

if (typeof module !== 'undefined') module.exports = BLOG_DATA;