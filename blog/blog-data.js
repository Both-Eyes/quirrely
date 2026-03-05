// ═══════════════════════════════════════════════════════════════════════════
// QUIRRELY BLOG DATA — 40 Profile+Stance Combinations
// Each written IN THE STYLE of that combination
// 160 Writer/Book pairs (40 × 4 countries)
// ═══════════════════════════════════════════════════════════════════════════

const BLOG_DATA = {
  
  // ─────────────────────────────────────────────────────────────────────────
  // BLOG CONTENT — Written in the style described
  // ─────────────────────────────────────────────────────────────────────────
  
  content: {
    'ASSERTIVE-OPEN': {
      title: 'How ASSERTIVE + OPEN Writers Write',
      meta: 'Direct statements. Receptive to challenge. The confident conversationalist.',
      body: `You state your case. Then you listen.

ASSERTIVE + OPEN writers combine conviction with curiosity. They make strong claims, but they're genuinely interested in pushback. This isn't weakness. It's intellectual confidence.

THE PATTERN

Short sentences. Clear positions. But notice the openings: "What do you think?" "I could be wrong here." "Tell me where this breaks down."

The assertive part comes first. The opening comes after. You lead with strength, then invite challenge.

WHY IT WORKS

Readers trust you because you're not hedging. They engage because you're not defensive. You've given them permission to disagree—and that makes them more likely to agree.

This is leadership voice. State your vision. Invite input. Decide.

THE RISK

Some readers miss the openness. They see the assertion and assume you're closed. Solution: make your invitations explicit. "I want to hear the counterargument."`
    },
    
    'ASSERTIVE-CLOSED': {
      title: 'How ASSERTIVE + CLOSED Writers Write',
      meta: 'High certainty. No hedging. The definitive voice.',
      body: `This is how it is.

ASSERTIVE + CLOSED writers don't qualify. They don't hedge. They state what they know and move on. The reader follows or doesn't. That's not the writer's problem.

THE PATTERN

Short sentences. Declarative. No "I think" or "perhaps" or "it seems." Just the claim. Just the truth as the writer sees it.

Punctuation is minimal. Adjectives are rare. Every word works.

WHY IT WORKS

Certainty is magnetic. Readers want to be led. This voice leads.

In a world of endless hedging, directness stands out. It builds trust. The writer has done the thinking. The reader can rely on the conclusion.

THE RISK

Arrogance. Readers may push back not on the ideas but on the delivery. Use sparingly in collaborative contexts. Save it for when you're sure.`
    },
    
    'ASSERTIVE-BALANCED': {
      title: 'How ASSERTIVE + BALANCED Writers Write',
      meta: 'Strong voice. Multiple perspectives. The fair-minded authority.',
      body: `Here's what I believe. Here's why reasonable people disagree.

ASSERTIVE + BALANCED writers have conviction and context. They stake a position, then show they understand the alternatives. This isn't fence-sitting. It's earned authority.

THE PATTERN

Clear thesis. Short supporting sentences. Then: acknowledgment of complexity. "Others argue X. They have a point. But here's why Y still holds."

The balance comes from structure, not hedging. The assertions remain strong.

WHY IT WORKS

Readers trust writers who show their work. Acknowledging counterarguments builds credibility. It says: I've considered this deeply. I'm not naive.

This is the voice of the best op-eds. Confident but not blind.

THE RISK

Length. Balance takes space. Know when to cut to the chase and when to show the full picture.`
    },
    
    'ASSERTIVE-CONTRADICTORY': {
      title: 'How ASSERTIVE + CONTRADICTORY Writers Write',
      meta: 'Bold claims. Self-aware tensions. The provocateur.',
      body: `I believe X. I also believe not-X. Deal with it.

ASSERTIVE + CONTRADICTORY writers embrace paradox with confidence. They don't apologize for holding tensions. They assert them as features, not bugs.

THE PATTERN

Strong statement. Then its opposite, equally strong. No attempt to resolve. "Success requires focus. Success requires breadth. Both are true. Figure it out."

The contradiction is the point. The assertion is in owning it.

WHY IT WORKS

Reality is contradictory. Writers who pretend otherwise seem naive. This voice says: I see the mess. I'm not going to pretend it's tidy.

Readers who live in complexity feel seen.

THE RISK

Confusion. Some readers want resolution. They'll find this frustrating. That's fine. This voice isn't for everyone. It's for those who can hold tensions.`
    },
    
    'MINIMAL-OPEN': {
      title: 'How MINIMAL + OPEN Writers Write',
      meta: 'Sparse. Receptive. The quiet listener.',
      body: `Few words. Open ears.

MINIMAL + OPEN writers strip prose to essentials. What remains invites response.

THE PATTERN

Short. Spaces between thoughts. Room for the reader.

Questions appear. Not many. Enough.

WHY IT WORKS

Readers complete the thought. They participate. Engagement rises.

Silence is an invitation.

THE RISK

Too sparse. Some need more. Know your audience.`
    },
    
    'MINIMAL-CLOSED': {
      title: 'How MINIMAL + CLOSED Writers Write',
      meta: 'Spare. Certain. The final word.',
      body: `Said enough.

MINIMAL + CLOSED writers finish. No elaboration. No invitation. Done.

THE PATTERN

Fragments allowed. Sentences end. Period.

No questions. Statements only.

WHY IT WORKS

Authority. Confidence. Respect for reader's time.

Every word earns its place.

THE RISK

Cold. Some readers need warmth. Won't find it here.`
    },
    
    'MINIMAL-BALANCED': {
      title: 'How MINIMAL + BALANCED Writers Write',
      meta: 'Brief. Fair. Both sides in few words.',
      body: `This. Also that.

MINIMAL + BALANCED writers show duality without sprawl. Economy of fairness.

THE PATTERN

Claim. Counter-claim. No elaboration needed.

The brevity is the balance.

WHY IT WORKS

Readers see both sides fast. No lecture.

Efficient wisdom.

THE RISK

Too compressed. Nuance may be lost.`
    },
    
    'MINIMAL-CONTRADICTORY': {
      title: 'How MINIMAL + CONTRADICTORY Writers Write',
      meta: 'Sparse paradox. The koan.',
      body: `Yes and no.

MINIMAL + CONTRADICTORY writers hold tension in few words. Zen approach.

THE PATTERN

Opposites. Side by side. Unexplained.

The gap is the meaning.

WHY IT WORKS

Readers think. Fill the space. Make their own meaning.

Memorable.

THE RISK

Obscure. Some readers need more. They'll leave confused.`
    },
    
    'POETIC-OPEN': {
      title: 'How POETIC + OPEN Writers Write',
      meta: 'Lyrical and curious. The wondering voice.',
      body: `The words arrive like weather—unbidden, shifting, asking to be noticed. And what do we do with them, these syllables that choose us as much as we choose them?

POETIC + OPEN writers weave language into questions, into invitations, into doorways that swing both ways. The beauty is in the wondering.

THE PATTERN

Sentences that breathe, that pause, that turn back on themselves like rivers finding their way. Metaphor not as decoration but as discovery. And always, the openness: the willingness to be wrong, to be surprised, to let the reader in.

Questions bloom from the prose like flowers from cracks in concrete.

WHY IT WORKS

Readers feel held, not instructed. The beauty disarms. The openness invites participation. This is writing as communion, not lecture.

THE RISK

Readers seeking efficiency will grow impatient. Not every moment calls for wonder. Know when to be direct.`
    },
    
    'POETIC-CLOSED': {
      title: 'How POETIC + CLOSED Writers Write',
      meta: 'Beautiful and certain. The oracle speaks.',
      body: `The truth arrives dressed in silk. It does not argue. It simply is, and being is enough.

POETIC + CLOSED writers craft declarations that sing. There is no question here, no invitation to debate. Only the beauty of certainty, rendered in language that rewards attention.

THE PATTERN

Sentences that build like architecture, each word placed with intention, the whole structure rising toward a conclusion that feels inevitable. The imagery serves the assertion. The music reinforces the message.

No hedging. No perhaps. Only the weight of words that know themselves.

WHY IT WORKS

Authority clothed in beauty is irresistible. Readers submit to the voice because it earns submission through craft. This is the prophet's register, the poet's conviction.

THE RISK

Pretension waits at the edges. The line between oracle and pomposity is thin. Earn every flourish or cut it.`
    },
    
    'POETIC-BALANCED': {
      title: 'How POETIC + BALANCED Writers Write',
      meta: 'Lyrical fairness. The meditative witness.',
      body: `On one hand, the morning light through eastern windows. On the other, the same light fading west at evening. Both are true. Both illuminate. Both matter.

POETIC + BALANCED writers hold contradiction with grace, presenting multiple truths without forcing resolution. The beauty is in the holding itself.

THE PATTERN

Parallel structures that honor opposing views. Imagery that serves both sides of an argument. Sentences that acknowledge complexity without collapsing into mush.

The balance is built into the rhythm, the architecture of the prose.

WHY IT WORKS

Readers feel seen in their own ambivalence. Life is rarely simple; this voice admits it while still making the reading beautiful. Wisdom made lyrical.

THE RISK

Length. Balance and poetry both take space. Together, they can sprawl. Discipline the beauty.`
    },
    
    'POETIC-CONTRADICTORY': {
      title: 'How POETIC + CONTRADICTORY Writers Write',
      meta: 'Beautiful paradox. The sublime tension.',
      body: `We are made of opposites—light that casts shadow, love that holds grief, words that mean their opposite depending on who's listening. And isn't that the terrible beauty of it all?

POETIC + CONTRADICTORY writers embrace paradox as the highest truth. Their prose doesn't resolve tension—it illuminates it, makes it luminous.

THE PATTERN

Oxymoron elevated to philosophy. Metaphors that contradict themselves. Sentences that assert and undermine in the same breath, leaving the reader suspended in beautiful uncertainty.

The contradiction is the point. The poetry is how you survive it.

WHY IT WORKS

Readers who have lived know that life contradicts itself constantly. This voice speaks to that experience, makes it bearable, even beautiful.

THE RISK

Inaccessibility. Not every reader wants to dwell in paradox. Some want answers. They'll leave frustrated and confused.`
    },
    
    'DENSE-OPEN': {
      title: 'How DENSE + OPEN Writers Write',
      meta: 'Rich complexity with genuine inquiry. The scholar who still questions.',
      body: `The phenomenon under consideration—that is, the particular manner in which writers construct and deploy epistemic frameworks within their prose—invites multiple interpretative approaches, each with its own methodological merits and limitations, though one wonders whether our current analytical tools are adequate to the task.

DENSE + OPEN writers pack substantial intellectual content into their sentences while maintaining a posture of genuine inquiry. The complexity is rigorous; the conclusions remain provisional.

THE PATTERN

Subordinate clauses that qualify and contextualize. Vocabulary drawn from specialized domains but deployed with precision. And throughout, the markers of openness: "one might argue," "it remains unclear whether," "further investigation seems warranted."

The density signals expertise. The openness signals intellectual humility.

WHY IT WORKS

Sophisticated readers appreciate the rigor without feeling lectured. The writer has done the work but acknowledges limits. This builds trust among those who value nuance.

THE RISK

Accessibility suffers. Readers without relevant background knowledge may lose the thread. Consider your audience carefully.`
    },
    
    'DENSE-CLOSED': {
      title: 'How DENSE + CLOSED Writers Write',
      meta: 'Maximum information. Maximum certainty. The definitive treatise.',
      body: `The evidence demonstrates conclusively that the syntactic structures employed by writers with high certainty orientations differ systematically from those characteristic of more epistemically cautious authors, with the former exhibiting significantly reduced hedging frequency, elevated use of declarative constructions, and notably compressed qualification ratios.

DENSE + CLOSED writers deliver complex information with absolute confidence. Every clause adds data. Every sentence advances the argument without equivocation.

THE PATTERN

Long sentences that nevertheless drive toward conclusions. Technical vocabulary deployed without apology. Subordinate clauses that add precision, not doubt. The complexity serves certainty.

No hedging. No "perhaps." The density itself is the argument.

WHY IT WORKS

Readers seeking authoritative synthesis find it here. The writer's command of complexity signals expertise. The certainty provides actionable conclusions.

THE RISK

Intimidation or arrogance. Readers may feel excluded or talked down to. Use with appropriate expertise.`
    },
    
    'DENSE-BALANCED': {
      title: 'How DENSE + BALANCED Writers Write',
      meta: 'Comprehensive analysis. Multiple perspectives integrated. The synthesis.',
      body: `While proponents of the first view emphasize the structural determinants of prose style—arguing that syntactic patterns emerge primarily from cognitive constraints and genre conventions—advocates of the alternative position foreground agentive choice, suggesting that writers deliberately select from available repertoires; a complete account, however, requires integrating both perspectives.

DENSE + BALANCED writers present multiple positions with equal rigor before synthesizing. The complexity is in the comprehensiveness.

THE PATTERN

Extended comparative structures. "While X argues... Y counters... yet Z suggests..." Each position receives careful elaboration. The balance is structural, built into the architecture of the prose.

Conclusions, when they come, acknowledge what they exclude.

WHY IT WORKS

Readers gain a complete picture. The writer's fairness is evident in the treatment of each position. This builds authority through demonstrated comprehensiveness.

THE RISK

Length and potential for reader exhaustion. Not every topic requires this treatment.`
    },
    
    'DENSE-CONTRADICTORY': {
      title: 'How DENSE + CONTRADICTORY Writers Write',
      meta: 'Complex paradox fully elaborated. The philosophical puzzle.',
      body: `The fundamental contradiction inheres in the phenomenon itself: the very mechanisms that enable communicative clarity simultaneously introduce interpretive instability, such that precision of expression generates multiplicity of meaning—a paradox that resists resolution and instead demands acknowledgment of irreducible tension as constitutive rather than defective.

DENSE + CONTRADICTORY writers explore paradox with scholarly rigor. The contradictions are not glossed over but elaborated in full complexity.

THE PATTERN

Extended analysis of opposing forces. Technical vocabulary for both poles of the contradiction. Explicit refusal of false resolution. The complexity honors the paradox rather than dissolving it.

WHY IT WORKS

Sophisticated readers appreciate the honest engagement with difficulty. The writer doesn't pretend to solve what cannot be solved.

THE RISK

Frustration among readers seeking practical guidance. Ensure the complexity serves genuine insight.`
    },
    
    'CONVERSATIONAL-OPEN': {
      title: 'How CONVERSATIONAL + OPEN Writers Write',
      meta: 'Friendly and curious. The coffee chat.',
      body: `So here's the thing—I've been thinking about this a lot, and I'm honestly not sure I've got it figured out. But maybe that's okay? Maybe figuring it out together is kind of the point.

CONVERSATIONAL + OPEN writers sound like your smartest friend admitting they don't have all the answers. It's warm, it's genuine, and it invites you into the process.

THE PATTERN

Contractions everywhere. Questions that aren't rhetorical—they're real. "What do you think?" isn't decoration; it's an actual invitation. Sentences that start with "And" or "But" because that's how people actually talk.

The openness isn't performed. It's just... honest.

WHY IT WORKS

Readers feel like collaborators, not audiences. The warmth builds trust. The openness builds engagement.

THE RISK

Some contexts need more authority. Know when to shift registers.`
    },
    
    'CONVERSATIONAL-CLOSED': {
      title: 'How CONVERSATIONAL + CLOSED Writers Write',
      meta: 'Friendly but certain. The trusted advisor.',
      body: `Look, I'm just going to tell you how it is, because that's what friends do, right? They don't sugarcoat things. They don't hedge. They tell you the truth.

CONVERSATIONAL + CLOSED writers combine warmth with conviction. They're approachable, sure, but they've got opinions and they're not shy about sharing them.

THE PATTERN

All the warmth of conversational writing—the contractions, the asides. But underneath that warmth? Certainty. "Here's the deal." "Trust me on this." "This is what works."

It's like advice from someone who's been there.

WHY IT WORKS

Readers get the comfort of friendship and the clarity of expertise. The warmth makes the certainty easier to receive.

THE RISK

Overconfidence. The friendly package can make certainty feel pushy. Make sure you've earned the conviction.`
    },
    
    'CONVERSATIONAL-BALANCED': {
      title: 'How CONVERSATIONAL + BALANCED Writers Write',
      meta: 'Friendly and fair. The considerate friend.',
      body: `Okay, so here's where it gets complicated—and I promise I'm not just fence-sitting here. I genuinely think there are good points on both sides, and I want to walk through them with you.

CONVERSATIONAL + BALANCED writers bring you into their thinking process. They show their work like a friend explaining a decision, not a professor delivering a lecture.

THE PATTERN

The warmth is there—all the "here's the thing" and "look" and "you know?" But the content is balanced. "On one hand... but then again..." The fairness is genuine.

You feel like you're thinking through something together.

WHY IT WORKS

Readers trust balanced writers. Add conversational warmth, and they also like them. That combination is powerful.

THE RISK

Can feel wishy-washy. Sometimes people need "here's what to do," not "here are the considerations."`
    },
    
    'CONVERSATIONAL-CONTRADICTORY': {
      title: 'How CONVERSATIONAL + CONTRADICTORY Writers Write',
      meta: 'Friendly but paradoxical. The honest mess.',
      body: `Can I be honest with you? I believe two completely opposite things at the same time, and I'm pretty sure that's fine. Actually, I think that might be the healthiest way to live?

CONVERSATIONAL + CONTRADICTORY writers embrace paradox with a shrug and a smile. They don't pretend life makes sense. They just... admit it.

THE PATTERN

All the warmth you'd expect—the asides, the questions, the real person talking. But the content is full of contradictions, stated openly. "I want X. I also want not-X. What can I tell you?"

The contradiction isn't a problem to solve. It's just life.

WHY IT WORKS

Readers living in their own contradictions feel seen. The warmth makes the paradox bearable.

THE RISK

Readers seeking resolution may feel frustrated.`
    },
    
    'FORMAL-OPEN': {
      title: 'How FORMAL + OPEN Writers Write',
      meta: 'Professional and receptive. The institutional inquiry.',
      body: `The question before us merits careful consideration from multiple perspectives, and we would welcome input from stakeholders who may bring alternative viewpoints to bear on this matter.

FORMAL + OPEN writers maintain professional register while signaling genuine receptivity to other positions. The formality establishes authority; the openness invites collaboration.

THE PATTERN

Complete sentences. No contractions. Third person or institutional "we." But within this formality, explicit invitations: "We welcome feedback." "Further perspectives would be valuable."

The openness is structured, not casual.

WHY IT WORKS

Institutional contexts require formality. But institutions that appear closed lose trust. This voice threads the needle.

THE RISK

The openness may seem token. Demonstrate genuine receptivity through action.`
    },
    
    'FORMAL-CLOSED': {
      title: 'How FORMAL + CLOSED Writers Write',
      meta: 'Professional and definitive. The official position.',
      body: `The organization has determined that the following policy shall apply to all relevant circumstances. This decision is final and effective immediately.

FORMAL + CLOSED writers speak with institutional authority. There is no invitation for input. There is only the communication of a decision already made.

THE PATTERN

Passive voice where appropriate. Declarative sentences. No hedging. The formality reinforces the finality.

This is how policies are written. How verdicts are delivered.

WHY IT WORKS

Some contexts require unambiguous authority. Legal documents. Safety procedures. Final decisions.

THE RISK

Alienation. Overuse creates distance. Deploy strategically.`
    },
    
    'FORMAL-BALANCED': {
      title: 'How FORMAL + BALANCED Writers Write',
      meta: 'Professional fairness. The objective report.',
      body: `The evidence supports multiple interpretations, and this analysis endeavors to present each perspective with appropriate weight before drawing provisional conclusions.

FORMAL + BALANCED writers aim for the objectivity expected in professional and academic contexts. Multiple viewpoints receive careful, impartial treatment.

THE PATTERN

Structured comparison. "Proponents argue... Critics counter..." Each position elaborated without editorial intrusion. Conclusions acknowledge limitations.

The formality reinforces the balance.

WHY IT WORKS

Contexts requiring impartiality—journalism, research, policy analysis—demand this voice.

THE RISK

False equivalence. Not all positions deserve equal weight.`
    },
    
    'FORMAL-CONTRADICTORY': {
      title: 'How FORMAL + CONTRADICTORY Writers Write',
      meta: 'Professional paradox. The institutional complexity.',
      body: `The organization recognizes that its stated objectives may, in certain circumstances, generate conflicting imperatives, and this policy document acknowledges rather than resolves that inherent tension.

FORMAL + CONTRADICTORY writers admit institutional paradox with appropriate gravity. The contradictions are formally acknowledged.

THE PATTERN

Explicit statement of tensions. "On one hand, the organization is committed to X. Simultaneously, it must pursue Y, which may conflict with X." Formal acknowledgment of irreducible complexity.

WHY IT WORKS

Organizations that pretend away contradictions lose credibility. Formal acknowledgment demonstrates sophisticated understanding.

THE RISK

Paralysis or excuse-making. The paradox must be navigated, not merely admitted.`
    },
    
    'BALANCED-OPEN': {
      title: 'How BALANCED + OPEN Writers Write',
      meta: 'Fair-minded and curious. The thoughtful explorer.',
      body: `There are good arguments on multiple sides of this question, and I'm genuinely uncertain which view will prove most compelling as we learn more. What do you see that I might be missing?

BALANCED + OPEN writers combine natural fairness with genuine curiosity. They see multiple perspectives and actively invite others to contribute.

THE PATTERN

Careful presentation of multiple viewpoints. Explicit acknowledgment of uncertainty. Questions that genuinely invite input. "What am I not seeing?"

The balance is sincere. The openness is real.

WHY IT WORKS

Readers feel respected and invited. The writer's humility is evident. This builds both trust and engagement.

THE RISK

May seem indecisive in contexts requiring clear direction.`
    },
    
    'BALANCED-CLOSED': {
      title: 'How BALANCED + CLOSED Writers Write',
      meta: 'Fair analysis, firm conclusion. The judicious verdict.',
      body: `Having considered the arguments on all sides, the evidence most strongly supports the following conclusion. Other views have merit but ultimately prove less persuasive.

BALANCED + CLOSED writers do the work of considering multiple perspectives, then reach a definitive conclusion. The balance is in the process; the closure is in the outcome.

THE PATTERN

Demonstration of fairness in analysis. Then, clear pivot to conclusion. "Nevertheless." "On balance." The verdict is not tentative.

WHY IT WORKS

Readers trust conclusions that demonstrate genuine engagement with alternatives. The balance earns the closure.

THE RISK

The balance can feel performative if the conclusion was predetermined.`
    },
    
    'BALANCED-BALANCED': {
      title: 'How BALANCED + BALANCED Writers Write',
      meta: 'Fairness on fairness. The ultimate mediator.',
      body: `There are compelling arguments on multiple sides, and while I have my own tentative view, I hold it with appropriate uncertainty given the genuine complexity of the question. Reasonable people continue to disagree.

BALANCED + BALANCED writers exhibit double balance: fair to all positions, and moderate in their own epistemic confidence.

THE PATTERN

Extended engagement with multiple views. Provisional conclusions. Acknowledgment that conclusions have limits. Meta-balance.

WHY IT WORKS

For genuinely complex issues, this voice is appropriate. It resists premature closure.

THE RISK

Can feel paralyzed. Sometimes readers need guidance.`
    },
    
    'BALANCED-CONTRADICTORY': {
      title: 'How BALANCED + CONTRADICTORY Writers Write',
      meta: 'Fair to paradox. The complexity embracer.',
      body: `Each position has merit. They also contradict each other. I don't think this is a problem to solve—I think it's a tension to navigate. The contradiction might be the point.

BALANCED + CONTRADICTORY writers give fair hearing to incompatible views and refuse to force resolution.

THE PATTERN

Careful elaboration of conflicting positions. Then, explicit acknowledgment that resolution isn't available. "Both are true. We live in the tension."

WHY IT WORKS

Reality often contains irreducible contradictions. This voice honors that.

THE RISK

Readers seeking action may find this frustrating.`
    },
    
    'LONGFORM-OPEN': {
      title: 'How LONGFORM + OPEN Writers Write',
      meta: 'Extended exploration with genuine inquiry. The deep dive that still wonders.',
      body: `The question I want to explore with you today is one that I've been sitting with for quite some time now, and I want to be upfront about the fact that I don't have a tidy answer waiting at the end of this exploration—what I have instead is a genuine curiosity and a willingness to think through the complexity in real time, with you as my companion.

LONGFORM + OPEN writers take their time and invite the reader along for an extended journey of discovery.

THE PATTERN

Sentences that unfold gradually. Paragraphs that build on each other while acknowledging uncertainty. The extended form allows for genuine exploration.

WHY IT WORKS

Readers who want depth and nuance find it here, without the pretense of false certainty.

THE RISK

Patience required. Not all readers will follow.`
    },
    
    'LONGFORM-CLOSED': {
      title: 'How LONGFORM + CLOSED Writers Write',
      meta: 'Extended argument with definitive conclusion. The comprehensive case.',
      body: `What follows is a thorough examination of the evidence, constructed to demonstrate conclusively that the position I advance is not merely plausible but substantially correct, and while the length of this analysis may demand patience from the reader, the comprehensiveness of the case will reward that patience with a level of certainty that briefer treatments cannot provide.

LONGFORM + CLOSED writers build extended, airtight arguments. The length is construction—each paragraph adding another brick.

THE PATTERN

Long sentences that accumulate evidence. Paragraphs that anticipate objections. By the conclusion, inevitability.

WHY IT WORKS

For readers who need to be convinced—really convinced—this voice does the work.

THE RISK

Can feel overwhelming. Ensure certainty is warranted.`
    },
    
    'LONGFORM-BALANCED': {
      title: 'How LONGFORM + BALANCED Writers Write',
      meta: 'Extended fairness. The comprehensive overview.',
      body: `The complexity of this issue demands extended treatment, and I intend to give each major perspective the thorough consideration it deserves, presenting the strongest version of each argument before attempting to identify where the weight of reason lies—a process that cannot be rushed.

LONGFORM + BALANCED writers use extended form to ensure genuine fairness. Every position gets full elaboration.

THE PATTERN

Multiple sections devoted to different perspectives. Extended steelmanning. The balance is structural.

WHY IT WORKS

Readers seeking genuine understanding find it here.

THE RISK

Length. Readers may lose patience. Signpost clearly.`
    },
    
    'LONGFORM-CONTRADICTORY': {
      title: 'How LONGFORM + CONTRADICTORY Writers Write',
      meta: 'Extended paradox. The full elaboration of irresolvable tension.',
      body: `What I want to do in the following extended exploration is to fully develop two positions that I believe to be both true and mutually incompatible, giving each the thorough treatment it deserves, not in order to resolve the contradiction but to honor it—to sit with the irreducible complexity long enough that we might learn something from the sitting itself.

LONGFORM + CONTRADICTORY writers use extended form to fully elaborate paradox.

THE PATTERN

Extended treatment of position A. Extended treatment of position B. Explicit discussion of the contradiction. No forced resolution.

WHY IT WORKS

For genuinely paradoxical topics, this provides appropriate treatment.

THE RISK

Reader frustration. Extended exploration with no resolution is challenging.`
    },
    
    'INTERROGATIVE-OPEN': {
      title: 'How INTERROGATIVE + OPEN Writers Write',
      meta: 'Questions upon questions. The Socratic explorer.',
      body: `What if the question itself is the point? What if we're not meant to arrive at answers but to stay with the questioning? And what does it mean that I'm asking you this—what role do you play in this exploration?

INTERROGATIVE + OPEN writers lead with questions and remain genuinely curious.

THE PATTERN

Questions that generate more questions. Few declarative statements. The openness is built into the form.

WHY IT WORKS

Readers become active participants.

THE RISK

Can feel evasive. Some readers want answers.`
    },
    
    'INTERROGATIVE-CLOSED': {
      title: 'How INTERROGATIVE + CLOSED Writers Write',
      meta: 'Rhetorical questions with predetermined answers. The leading examiner.',
      body: `Is there any doubt that this is the correct interpretation? Can anyone seriously argue otherwise? The answer, obviously, is no.

INTERROGATIVE + CLOSED writers use questions not to explore but to assert. The questions are rhetorical.

THE PATTERN

Questions that expect only one answer. "Isn't it clear that...?" The closure is embedded in the question.

WHY IT WORKS

Rhetorical questions engage while maintaining control.

THE RISK

Can feel manipulative. Skeptical readers may push back.`
    },
    
    'INTERROGATIVE-BALANCED': {
      title: 'How INTERROGATIVE + BALANCED Writers Write',
      meta: 'Questions that explore multiple sides. The balanced inquiry.',
      body: `But is this view correct? What would its critics say? And don't the critics have their own weaknesses? How do we weigh these competing considerations?

INTERROGATIVE + BALANCED writers use questions to surface multiple perspectives.

THE PATTERN

Questions that represent different viewpoints. "But what about...?" followed by "And yet, couldn't one also say...?"

WHY IT WORKS

Readers see the writer genuinely grappling with complexity.

THE RISK

Can seem uncommitted. Some readers want positions.`
    },
    
    'INTERROGATIVE-CONTRADICTORY': {
      title: 'How INTERROGATIVE + CONTRADICTORY Writers Write',
      meta: 'Questions that embrace paradox. The unresolvable inquiry.',
      body: `Can both be true? What if the question contains its own negation? And isn't that contradiction precisely what makes this worth exploring?

INTERROGATIVE + CONTRADICTORY writers use questions to surface and honor paradox.

THE PATTERN

Questions that highlight contradiction. "How can X be true when also not-X?" The interrogative allows paradox to remain open.

WHY IT WORKS

Questions about paradox are often more honest than statements.

THE RISK

Double frustration: questions without answers about contradictions without resolution.`
    },
    
    'HEDGED-OPEN': {
      title: 'How HEDGED + OPEN Writers Write',
      meta: 'Tentative and curious. The genuinely uncertain explorer.',
      body: `I think—and I could be wrong about this—that there might be something worth exploring here, though I'm genuinely uncertain about where it leads. What's your sense of this?

HEDGED + OPEN writers combine epistemic humility with genuine curiosity.

THE PATTERN

Qualifiers throughout: "perhaps," "it seems," "I'm not certain but." Genuine questions that invite response.

WHY IT WORKS

For genuinely uncertain topics, this voice is appropriate. It models intellectual humility.

THE RISK

Can seem unconfident. Some contexts require more certainty.`
    },
    
    'HEDGED-CLOSED': {
      title: 'How HEDGED + CLOSED Writers Write',
      meta: 'Tentative but not seeking input. The private uncertainty.',
      body: `It seems to me—though I recognize the limits of my perspective—that this is probably the case. I say this with appropriate tentativeness, but I am not, at present, looking for alternative viewpoints.

HEDGED + CLOSED writers qualify their claims but don't invite input.

THE PATTERN

Qualifiers present. But no questions, no invitations. The writer has reached a tentative-but-final position.

WHY IT WORKS

Some situations call for qualified positions that aren't up for debate.

THE RISK

May seem closed-minded despite the hedging.`
    },
    
    'HEDGED-BALANCED': {
      title: 'How HEDGED + BALANCED Writers Write',
      meta: 'Tentative fairness. The humble both-sides.',
      body: `It seems to me—though I may well be missing something important—that there are reasonable arguments on multiple sides of this question, and I'm genuinely uncertain which perspective will prove more compelling over time.

HEDGED + BALANCED writers combine epistemic humility with fairness to multiple viewpoints.

THE PATTERN

Qualifiers on everything, including the balance itself. Maximum humility.

WHY IT WORKS

For genuinely complex issues where no one should be confident, this voice is appropriate.

THE RISK

Can seem paralyzed. Double hedging may frustrate readers.`
    },
    
    'HEDGED-CONTRADICTORY': {
      title: 'How HEDGED + CONTRADICTORY Writers Write',
      meta: 'Tentatively paradoxical. The humble acceptance of mess.',
      body: `I think—and I'm honestly not sure about this—that I might believe two contradictory things at once, and perhaps that's okay? I'm not certain what to make of it, but I suspect the contradiction might be meaningful somehow.

HEDGED + CONTRADICTORY writers acknowledge holding paradoxical views while remaining uncertain about what that means.

THE PATTERN

Qualifiers applied to the contradiction itself. Maximum tentativeness about everything.

WHY IT WORKS

For genuinely confusing situations, this voice is authentic.

THE RISK

Readers may find this exhaustingly uncertain.`
    }
  },
  
  // ─────────────────────────────────────────────────────────────────────────
  // WRITER/BOOK DATABASE — 160 pairs (40 combinations × 4 countries)
  // ─────────────────────────────────────────────────────────────────────────
  
  writers: {
    'ASSERTIVE-OPEN': {
      CA: { writer: 'Michael Ondaatje', book: 'Warlight', why: 'Ondaatje writes with confidence but leaves space for mystery.' },
      UK: { writer: 'Ian McEwan', book: 'Atonement', why: 'McEwan asserts his narrative while remaining open to moral complexity.' },
      AU: { writer: 'Richard Flanagan', book: 'The Narrow Road to the Deep North', why: 'Flanagan writes with conviction while exploring ambiguity.' },
      NZ: { writer: 'Eleanor Catton', book: 'The Luminaries', why: 'Catton builds assertive prose with genuine openness.' }
    },
    'ASSERTIVE-CLOSED': {
      CA: { writer: 'Margaret Atwood', book: 'The Handmaid\'s Tale', why: 'Atwood makes declarative statements without hedging.' },
      UK: { writer: 'George Orwell', book: '1984', why: 'Orwell\'s prose is direct, certain, and uncompromising.' },
      AU: { writer: 'Tim Winton', book: 'Breath', why: 'Winton writes with masculine directness and unflinching certainty.' },
      NZ: { writer: 'Lloyd Jones', book: 'Mister Pip', why: 'Jones delivers narrative with quiet but absolute confidence.' }
    },
    'ASSERTIVE-BALANCED': {
      CA: { writer: 'Joseph Boyden', book: 'Three Day Road', why: 'Boyden presents multiple perspectives with strong narrative voice.' },
      UK: { writer: 'Hilary Mantel', book: 'Wolf Hall', why: 'Mantel balances historical perspectives with assertive prose.' },
      AU: { writer: 'Kate Grenville', book: 'The Secret River', why: 'Grenville asserts narrative while acknowledging colonial complexity.' },
      NZ: { writer: 'Witi Ihimaera', book: 'The Whale Rider', why: 'Ihimaera presents tradition and change with balanced conviction.' }
    },
    'ASSERTIVE-CONTRADICTORY': {
      CA: { writer: 'Mordecai Richler', book: 'Barney\'s Version', why: 'Richler\'s narrator confidently contradicts himself.' },
      UK: { writer: 'Zadie Smith', book: 'White Teeth', why: 'Smith asserts contradictory truths with equal conviction.' },
      AU: { writer: 'Peter Carey', book: 'True History of the Kelly Gang', why: 'Carey\'s Kelly is certain even when unreliable.' },
      NZ: { writer: 'Keri Hulme', book: 'The Bone People', why: 'Hulme writes with fierce conviction about irresolvable tensions.' }
    },
    'MINIMAL-OPEN': {
      CA: { writer: 'Alice Munro', book: 'Runaway', why: 'Munro says little but implies much, inviting interpretation.' },
      UK: { writer: 'Kazuo Ishiguro', book: 'Never Let Me Go', why: 'Ishiguro\'s spare prose creates space for discovery.' },
      AU: { writer: 'Gerald Murnane', book: 'The Plains', why: 'Murnane\'s minimal style opens rather than closes meaning.' },
      NZ: { writer: 'Janet Frame', book: 'Towards Another Summer', why: 'Frame\'s economy creates expansive ambiguity.' }
    },
    'MINIMAL-CLOSED': {
      CA: { writer: 'Sheila Heti', book: 'How Should a Person Be?', why: 'Heti\'s spare prose delivers definitive observations.' },
      UK: { writer: 'Samuel Beckett', book: 'Molloy', why: 'Beckett strips language to essence with certainty.' },
      AU: { writer: 'David Malouf', book: 'An Imaginary Life', why: 'Malouf\'s minimal prose is spare and certain.' },
      NZ: { writer: 'C.K. Stead', book: 'All Visitors Ashore', why: 'Stead writes with spare, final authority.' }
    },
    'MINIMAL-BALANCED': {
      CA: { writer: 'Mavis Gallant', book: 'Selected Stories', why: 'Gallant\'s brevity encompasses multiple perspectives.' },
      UK: { writer: 'Muriel Spark', book: 'The Driver\'s Seat', why: 'Spark balances views in fewest possible words.' },
      AU: { writer: 'Amy Witting', book: 'I for Isobel', why: 'Witting\'s spare style presents balanced character study.' },
      NZ: { writer: 'Owen Marshall', book: 'Coming Home in the Dark', why: 'Marshall\'s minimal prose balances perspectives.' }
    },
    'MINIMAL-CONTRADICTORY': {
      CA: { writer: 'Anne Carson', book: 'Autobiography of Red', why: 'Carson\'s spare verse holds contradictions.' },
      UK: { writer: 'Tom McCarthy', book: 'Remainder', why: 'McCarthy\'s stripped prose embodies productive contradiction.' },
      AU: { writer: 'J.M. Coetzee', book: 'Waiting for the Barbarians', why: 'Coetzee\'s spare style contains paradox.' },
      NZ: { writer: 'Bill Manhire', book: 'Selected Poems', why: 'Manhire\'s minimal verse embraces contradiction.' }
    },
    'POETIC-OPEN': {
      CA: { writer: 'Michael Ondaatje', book: 'The English Patient', why: 'Ondaatje\'s lyrical prose invites multiple readings.' },
      UK: { writer: 'Virginia Woolf', book: 'To the Lighthouse', why: 'Woolf\'s poetic style opens endless interpretation.' },
      AU: { writer: 'Alexis Wright', book: 'Carpentaria', why: 'Wright\'s lyrical storytelling invites diverse readings.' },
      NZ: { writer: 'Patricia Grace', book: 'Potiki', why: 'Grace\'s poetic prose opens to multiple interpretations.' }
    },
    'POETIC-CLOSED': {
      CA: { writer: 'Anne Michaels', book: 'Fugitive Pieces', why: 'Michaels\' poetry is certain even when beautiful.' },
      UK: { writer: 'Jeanette Winterson', book: 'The Passion', why: 'Winterson\'s lyrical prose delivers truth with certainty.' },
      AU: { writer: 'David Malouf', book: 'Ransom', why: 'Malouf\'s poetic prose makes definitive claims.' },
      NZ: { writer: 'Elizabeth Knox', book: 'The Vintner\'s Luck', why: 'Knox\'s beautiful prose is confident in its vision.' }
    },
    'POETIC-BALANCED': {
      CA: { writer: 'Dionne Brand', book: 'A Map to the Door of No Return', why: 'Brand\'s poetic prose balances personal and historical.' },
      UK: { writer: 'Ali Smith', book: 'How to be Both', why: 'Smith balances time periods lyrically.' },
      AU: { writer: 'Kim Scott', book: 'That Deadman Dance', why: 'Scott\'s lyrical style balances perspectives.' },
      NZ: { writer: 'Paula Morris', book: 'Rangatira', why: 'Morris balances perspectives poetically.' }
    },
    'POETIC-CONTRADICTORY': {
      CA: { writer: 'Leonard Cohen', book: 'Beautiful Losers', why: 'Cohen\'s poetic prose embraces spiritual contradiction.' },
      UK: { writer: 'Iris Murdoch', book: 'The Sea, The Sea', why: 'Murdoch\'s beautiful prose holds irreconcilable tensions.' },
      AU: { writer: 'Randolph Stow', book: 'Tourmaline', why: 'Stow\'s lyrical style contains productive paradox.' },
      NZ: { writer: 'Keri Hulme', book: 'The Bone People', why: 'Hulme\'s poetic prose embraces cultural contradiction.' }
    },
    'DENSE-OPEN': {
      CA: { writer: 'Thomas King', book: 'Green Grass, Running Water', why: 'King\'s complex narrative remains open.' },
      UK: { writer: 'A.S. Byatt', book: 'Possession', why: 'Byatt\'s dense prose invites multiple readings.' },
      AU: { writer: 'Gerald Murnane', book: 'Border Districts', why: 'Murnane\'s complex sentences remain open-ended.' },
      NZ: { writer: 'Eleanor Catton', book: 'The Luminaries', why: 'Catton\'s intricate structure invites interpretation.' }
    },
    'DENSE-CLOSED': {
      CA: { writer: 'Robertson Davies', book: 'Fifth Business', why: 'Davies\' erudite prose delivers definitive insights.' },
      UK: { writer: 'Martin Amis', book: 'Money', why: 'Amis\' dense, stylized prose is supremely confident.' },
      AU: { writer: 'Patrick White', book: 'Voss', why: 'White\'s complex prose makes definitive claims.' },
      NZ: { writer: 'C.K. Stead', book: 'Mansfield', why: 'Stead\'s scholarly prose delivers authority.' }
    },
    'DENSE-BALANCED': {
      CA: { writer: 'Miriam Toews', book: 'Women Talking', why: 'Toews\' complex narrative balances multiple voices.' },
      UK: { writer: 'Salman Rushdie', book: 'Midnight\'s Children', why: 'Rushdie\'s dense prose balances myth and history.' },
      AU: { writer: 'Thomas Keneally', book: 'Schindler\'s Ark', why: 'Keneally\'s detailed prose balances perspectives.' },
      NZ: { writer: 'Vincent O\'Sullivan', book: 'Let the River Stand', why: 'O\'Sullivan\'s dense prose balances views.' }
    },
    'DENSE-CONTRADICTORY': {
      CA: { writer: 'Margaret Atwood', book: 'Alias Grace', why: 'Atwood\'s complex narrative holds truth and lies in tension.' },
      UK: { writer: 'John Fowles', book: 'The French Lieutenant\'s Woman', why: 'Fowles\' dense metafiction embraces paradox.' },
      AU: { writer: 'Peter Carey', book: 'Oscar and Lucinda', why: 'Carey\'s intricate prose holds contradiction.' },
      NZ: { writer: 'Ian Wedde', book: 'Symmes Hole', why: 'Wedde\'s dense style embraces postmodern paradox.' }
    },
    'CONVERSATIONAL-OPEN': {
      CA: { writer: 'Stuart McLean', book: 'Vinyl Cafe Stories', why: 'McLean invites you in and asks what you think.' },
      UK: { writer: 'Nick Hornby', book: 'High Fidelity', why: 'Hornby\'s chatty prose genuinely wonders.' },
      AU: { writer: 'Tim Winton', book: 'Cloudstreet', why: 'Winton\'s vernacular storytelling invites participation.' },
      NZ: { writer: 'Carl Shuker', book: 'The Method Actors', why: 'Shuker\'s conversational style opens interpretation.' }
    },
    'CONVERSATIONAL-CLOSED': {
      CA: { writer: 'Will Ferguson', book: 'Happiness', why: 'Ferguson\'s chatty style delivers satirical truths.' },
      UK: { writer: 'Douglas Adams', book: 'The Hitchhiker\'s Guide', why: 'Adams\' conversational voice makes absurdist certainties.' },
      AU: { writer: 'Clive James', book: 'Unreliable Memoirs', why: 'James\' friendly voice delivers definitive observations.' },
      NZ: { writer: 'Danyl McLauchlan', book: 'Unspeakable Secrets', why: 'McLauchlan\'s chatty style makes satirical points.' }
    },
    'CONVERSATIONAL-BALANCED': {
      CA: { writer: 'Stuart McLean', book: 'Home from the Vinyl Cafe', why: 'McLean\'s warm style presents life\'s complications fairly.' },
      UK: { writer: 'David Mitchell', book: 'Cloud Atlas', why: 'Mitchell\'s accessible prose balances perspectives.' },
      AU: { writer: 'Charlotte Wood', book: 'The Natural Way of Things', why: 'Wood\'s readable prose balances perspectives on power.' },
      NZ: { writer: 'Rachael King', book: 'The Sound of Butterflies', why: 'King balances historical views accessibly.' }
    },
    'CONVERSATIONAL-CONTRADICTORY': {
      CA: { writer: 'Sheila Heti', book: 'Motherhood', why: 'Heti\'s casual voice holds contradictory desires openly.' },
      UK: { writer: 'Geoff Dyer', book: 'Out of Sheer Rage', why: 'Dyer\'s friendly prose embraces contradictions.' },
      AU: { writer: 'Helen Garner', book: 'Everywhere I Look', why: 'Garner\'s conversational essays hold personal contradictions.' },
      NZ: { writer: 'Ashleigh Young', book: 'Can You Tolerate This?', why: 'Young\'s friendly essays embrace paradox warmly.' }
    },
    'FORMAL-OPEN': {
      CA: { writer: 'John Ralston Saul', book: 'Voltaire\'s Bastards', why: 'Saul\'s formal prose invites intellectual response.' },
      UK: { writer: 'Terry Eagleton', book: 'Literary Theory', why: 'Eagleton\'s academic style remains questioning.' },
      AU: { writer: 'Robert Dessaix', book: 'What Days Are For', why: 'Dessaix\'s formal essays invite reflective response.' },
      NZ: { writer: 'Brian Turner', book: 'Elemental', why: 'Turner\'s formal poetry invites contemplation.' }
    },
    'FORMAL-CLOSED': {
      CA: { writer: 'Northrop Frye', book: 'Anatomy of Criticism', why: 'Frye\'s scholarly prose delivers definitive framework.' },
      UK: { writer: 'Simon Schama', book: 'Citizens', why: 'Schama\'s formal history writing is authoritative.' },
      AU: { writer: 'Robert Hughes', book: 'The Fatal Shore', why: 'Hughes\' formal prose makes definitive historical claims.' },
      NZ: { writer: 'Michael King', book: 'The Penguin History of New Zealand', why: 'King\'s formal history is authoritative.' }
    },
    'FORMAL-BALANCED': {
      CA: { writer: 'Charles Taylor', book: 'Sources of the Self', why: 'Taylor\'s scholarly prose balances philosophical traditions.' },
      UK: { writer: 'Isaiah Berlin', book: 'The Hedgehog and the Fox', why: 'Berlin\'s formal essays balance intellectual traditions.' },
      AU: { writer: 'Inga Clendinnen', book: 'Dancing with Strangers', why: 'Clendinnen\'s formal prose balances colonial perspectives.' },
      NZ: { writer: 'Ranginui Walker', book: 'Ka Whawhai Tonu Matou', why: 'Walker\'s formal analysis balances perspectives.' }
    },
    'FORMAL-CONTRADICTORY': {
      CA: { writer: 'Mark Kingwell', book: 'In Pursuit of Happiness', why: 'Kingwell\'s formal philosophy embraces productive paradox.' },
      UK: { writer: 'G.K. Chesterton', book: 'Orthodoxy', why: 'Chesterton\'s formal apologetics embraces divine paradox.' },
      AU: { writer: 'David Marr', book: 'Quarterly Essay', why: 'Marr\'s formal journalism holds political contradictions.' },
      NZ: { writer: 'Jane Kelsey', book: 'The FIRE Economy', why: 'Kelsey\'s formal analysis reveals systemic contradictions.' }
    },
    'BALANCED-OPEN': {
      CA: { writer: 'John Ibbitson', book: 'The Big Shift', why: 'Ibbitson presents political analysis with genuine inquiry.' },
      UK: { writer: 'Reni Eddo-Lodge', book: 'Why I\'m No Longer Talking', why: 'Eddo-Lodge balances perspectives while remaining curious.' },
      AU: { writer: 'Stan Grant', book: 'Talking to My Country', why: 'Grant balances Indigenous and settler views openly.' },
      NZ: { writer: 'Max Harris', book: 'The New Zealand Project', why: 'Harris balances perspectives curiously.' }
    },
    'BALANCED-CLOSED': {
      CA: { writer: 'Jeffrey Simpson', book: 'Chronic Condition', why: 'Simpson reaches conclusions after balanced analysis.' },
      UK: { writer: 'David Goodhart', book: 'The Road to Somewhere', why: 'Goodhart balances then concludes definitively.' },
      AU: { writer: 'George Megalogenis', book: 'The Australian Moment', why: 'Megalogenis weighs factors then reaches firm conclusions.' },
      NZ: { writer: 'Brian Easton', book: 'Not in Narrow Seas', why: 'Easton balances views then commits to position.' }
    },
    'BALANCED-BALANCED': {
      CA: { writer: 'Mark Kingwell', book: 'The World We Want', why: 'Kingwell remains genuinely uncertain while considering all sides.' },
      UK: { writer: 'Kwame Anthony Appiah', book: 'The Ethics of Identity', why: 'Appiah holds multiple perspectives tentatively.' },
      AU: { writer: 'Tim Soutphommasane', book: 'On Hate', why: 'Soutphommasane presents balanced analysis with appropriate uncertainty.' },
      NZ: { writer: 'Andrew Sharp', book: 'Justice and the Māori', why: 'Sharp presents balanced analysis of treaty issues carefully.' }
    },
    'BALANCED-CONTRADICTORY': {
      CA: { writer: 'Thomas Homer-Dixon', book: 'The Upside of Down', why: 'Homer-Dixon holds contradictory futures in balance.' },
      UK: { writer: 'John Gray', book: 'Straw Dogs', why: 'Gray presents balanced view of humanity\'s contradictions.' },
      AU: { writer: 'Tim Flannery', book: 'The Weather Makers', why: 'Flannery balances hope and despair about climate.' },
      NZ: { writer: 'Geoff Park', book: 'Theatre Country', why: 'Park holds environmental contradictions in balance.' }
    },
    'LONGFORM-OPEN': {
      CA: { writer: 'Michael Ignatieff', book: 'The Russian Album', why: 'Ignatieff\'s extended meditation remains questioning.' },
      UK: { writer: 'Olivia Laing', book: 'The Lonely City', why: 'Laing\'s extended essays explore with curiosity.' },
      AU: { writer: 'Anna Krien', book: 'Night Games', why: 'Krien\'s longform journalism remains genuinely uncertain.' },
      NZ: { writer: 'Steve Braunias', book: 'Civilisation', why: 'Braunias\' extended profiles invite interpretation.' }
    },
    'LONGFORM-CLOSED': {
      CA: { writer: 'John Vaillant', book: 'The Tiger', why: 'Vaillant\'s extended narrative reaches definitive conclusions.' },
      UK: { writer: 'Patrick Leigh Fermor', book: 'A Time of Gifts', why: 'Fermor\'s extended prose is confident throughout.' },
      AU: { writer: 'Chloe Hooper', book: 'The Tall Man', why: 'Hooper\'s longform reaches definitive moral conclusions.' },
      NZ: { writer: 'Ian Cross', book: 'The God Boy', why: 'Cross\' extended narrative is certain in its vision.' }
    },
    'LONGFORM-BALANCED': {
      CA: { writer: 'Lawrence Hill', book: 'The Book of Negroes', why: 'Hill\'s extended narrative balances historical perspectives.' },
      UK: { writer: 'Hilary Mantel', book: 'Wolf Hall', why: 'Mantel\'s extended prose balances many voices.' },
      AU: { writer: 'Kate Grenville', book: 'The Secret River', why: 'Grenville\'s extended narrative balances colonial complexity.' },
      NZ: { writer: 'Maurice Gee', book: 'Going West', why: 'Gee\'s extended narratives balance multiple perspectives.' }
    },
    'LONGFORM-CONTRADICTORY': {
      CA: { writer: 'Michael Ondaatje', book: 'Coming Through Slaughter', why: 'Ondaatje\'s extended prose holds irresolvable tensions.' },
      UK: { writer: 'W.G. Sebald', book: 'Austerlitz', why: 'Sebald\'s extended sentences hold memory\'s contradictions.' },
      AU: { writer: 'Michelle de Kretser', book: 'Questions of Travel', why: 'de Kretser\'s longform holds belonging\'s contradictions.' },
      NZ: { writer: 'Emily Perkins', book: 'Novel About My Wife', why: 'Perkins\' extended prose holds relationship paradoxes.' }
    },
    'INTERROGATIVE-OPEN': {
      CA: { writer: 'Naomi Klein', book: 'This Changes Everything', why: 'Klein asks genuine questions about climate solutions.' },
      UK: { writer: 'Rebecca Solnit', book: 'Hope in the Dark', why: 'Solnit asks genuine questions about activism.' },
      AU: { writer: 'Helen Garner', book: 'This House of Grief', why: 'Garner questions certainty throughout.' },
      NZ: { writer: 'Diana Wichtel', book: 'Driving to Treblinka', why: 'Wichtel questions family history openly.' }
    },
    'INTERROGATIVE-CLOSED': {
      CA: { writer: 'Malcolm Gladwell', book: 'Outliers', why: 'Gladwell poses rhetorical questions with predetermined answers.' },
      UK: { writer: 'Christopher Hitchens', book: 'God Is Not Great', why: 'Hitchens asks questions with certain answers.' },
      AU: { writer: 'Clive James', book: 'Cultural Amnesia', why: 'James asks rhetorical questions confidently.' },
      NZ: { writer: 'Chris Trotter', book: 'No Left Turn', why: 'Trotter asks leading questions about politics.' }
    },
    'INTERROGATIVE-BALANCED': {
      CA: { writer: 'Michael Ignatieff', book: 'The Lesser Evil', why: 'Ignatieff questions torture ethics from all angles.' },
      UK: { writer: 'Kwame Anthony Appiah', book: 'Cosmopolitanism', why: 'Appiah questions identity from multiple perspectives.' },
      AU: { writer: 'Robert Manne', book: 'The Monthly Essays', why: 'Manne questions Australian politics fairly.' },
      NZ: { writer: 'Andrew Dean', book: 'Ruth, Roger and Me', why: 'Dean questions neoliberalism from multiple angles.' }
    },
    'INTERROGATIVE-CONTRADICTORY': {
      CA: { writer: 'Anne Carson', book: 'Nox', why: 'Carson questions grief through productive paradox.' },
      UK: { writer: 'John Berger', book: 'Ways of Seeing', why: 'Berger asks questions containing their own contradictions.' },
      AU: { writer: 'Christos Tsiolkas', book: 'The Slap', why: 'Tsiolkas questions morality through irresolvable tensions.' },
      NZ: { writer: 'Albert Wendt', book: 'Black Rainbow', why: 'Wendt questions identity through dystopian paradox.' }
    },
    'HEDGED-OPEN': {
      CA: { writer: 'Miriam Toews', book: 'All My Puny Sorrows', why: 'Toews writes with gentle uncertainty, inviting response.' },
      UK: { writer: 'Penelope Fitzgerald', book: 'The Blue Flower', why: 'Fitzgerald\'s tentative prose invites interpretation.' },
      AU: { writer: 'Sonya Hartnett', book: 'Of a Boy', why: 'Hartnett\'s uncertain narrator invites reader engagement.' },
      NZ: { writer: 'Charlotte Grimshaw', book: 'The Night Book', why: 'Grimshaw\'s tentative prose opens interpretation.' }
    },
    'HEDGED-CLOSED': {
      CA: { writer: 'Alice Munro', book: 'Dear Life', why: 'Munro hedges on facts but not on emotional truth.' },
      UK: { writer: 'Kazuo Ishiguro', book: 'The Remains of the Day', why: 'Stevens hedges constantly but the meaning is certain.' },
      AU: { writer: 'J.M. Coetzee', book: 'Disgrace', why: 'Coetzee\'s prose is uncertain on surface, certain beneath.' },
      NZ: { writer: 'Fiona Kidman', book: 'This Mortal Boy', why: 'Kidman hedges on interpretation but not on tragedy.' }
    },
    'HEDGED-BALANCED': {
      CA: { writer: 'Lisa Moore', book: 'February', why: 'Moore presents uncertainty about grief from all angles.' },
      UK: { writer: 'Pat Barker', book: 'Regeneration', why: 'Barker\'s hedged prose balances perspectives on trauma.' },
      AU: { writer: 'Gail Jones', book: 'Sorry', why: 'Jones\'s uncertain prose balances reconciliation views.' },
      NZ: { writer: 'Catherine Chidgey', book: 'The Wish Child', why: 'Chidgey balances perspectives with appropriate uncertainty.' }
    },
    'HEDGED-CONTRADICTORY': {
      CA: { writer: 'Michael Ondaatje', book: 'Divisadero', why: 'Ondaatje holds contradictions tentatively.' },
      UK: { writer: 'Ali Smith', book: 'Autumn', why: 'Smith\'s uncertain prose embraces Brexit\'s contradictions.' },
      AU: { writer: 'Alexis Wright', book: 'The Swan Book', why: 'Wright holds climate contradictions in uncertain prose.' },
      NZ: { writer: 'Pip Adam', book: 'The New Animals', why: 'Adam\'s hesitant prose holds identity contradictions.' }
    }
  }
};

// Export for use in template
if (typeof module !== 'undefined') module.exports = BLOG_DATA;
