/**
 * STRETCH ACTIONS v1.0 — technique pattern → actionable writing guidance
 * First match wins. 3 actions per pattern (one per cycle).
 */
var STRETCH_ACTIONS = [
  {p:/withhold|unsaid|absence|omit|not said|silence/i, t:'Strategic Withholding', a:[
    'Write a scene where the most important thing is never directly stated. Let the reader feel it through what surrounds it.',
    'Remove the most revealing sentence from your paragraph. Does the meaning still come through? Strengthen what remains.',
    'Write a conversation where both speakers avoid the real subject. Let the subtext carry the weight.',
  ]},
  {p:/register|shift|vernacular|formal to|tonal/i, t:'Register Shifting', a:[
    'Start a sentence in formal language. Mid-sentence, drop into casual rhythm. Let the shift do the work.',
    'Write a paragraph that moves between two registers — intellectual and domestic, or poetic and blunt. Just shift.',
    'Write a passage where each sentence occupies a different register. The music should feel deliberate.',
  ]},
  {p:/rhythm|cadence|beat|pulse|music|sound/i, t:'Prose Rhythm', a:[
    'Write three sentences: one long, one very short, one medium. Feel how pacing changes emotional weight.',
    'Write a paragraph where sentence lengths mirror the content — quick for urgency, slow for reflection.',
    'Read your paragraph aloud. Rewrite any sentence where your voice stumbles. The ear knows first.',
  ]},
  {p:/accumulat|layer|density|dense|pile|catalogue/i, t:'Accumulation', a:[
    'List three concrete details about a place without explaining why they matter. Trust the pile to generate meaning.',
    'Write a sentence that keeps adding — clause after clause — until the accumulation becomes the point.',
    'Build a paragraph where each sentence adds one element to an image. Do not summarise. Let the weight arrive.',
  ]},
  {p:/contradict|paradox|simultane|tension|oppose|both.*once|irresolution|complexity/i, t:'Holding Contradictions', a:[
    'Write a sentence containing two true things that seem to oppose each other. Do not resolve the tension.',
    'Describe a person who is two contradictory things at once. Hold both as equally real.',
    'Write a paragraph where argument and counter-argument coexist. The reader should feel the pull both ways.',
  ]},
  {p:/image|imagery|visual|sensory|concrete|physical/i, t:'Sensory Precision', a:[
    'Describe one moment using only what the body senses — sight, sound, texture, smell. No abstractions.',
    'Replace every abstract word with something physical. "Sadness" becomes what sadness looks like in the room.',
    'Write a paragraph grounded in the material world. Let emotion arrive through objects, not labels.',
  ]},
  {p:/question|interrogat|ask|inquiry/i, t:'Interrogative Drive', a:[
    'Write a paragraph that asks more than it answers. Let the questions do the thinking.',
    'Start with a statement. Question it. Then question the question. Follow the doubt wherever it leads.',
    'Write a passage where every other sentence is a question. Notice how inquiry changes what feels certain.',
  ]},
  {p:/precise|precision|exact|economy|spare|earn/i, t:'Economy of Language', a:[
    'Write a sentence. Now cut it in half. Keep the meaning. This is the discipline.',
    'Describe a complex emotion in under fifteen words. Every word must be load-bearing.',
    'Write a paragraph, then remove every adjective. Add back only the ones the meaning cannot survive without.',
  ]},
  {p:/long|extend|sustain|elaborate|expand|subordinat/i, t:'Sustained Sentence', a:[
    'Write one sentence at least 40 words long. Use commas, dashes, semicolons to keep it moving.',
    'Extend a simple observation into a long sentence by adding layers — qualifications, asides, second thoughts.',
    'Write a paragraph that is a single sentence. The reader should arrive breathless but fully oriented.',
  ]},
  {p:/interrupt|fragment|break|disrupt|digress/i, t:'Deliberate Disruption', a:[
    'Write a calm sentence. Then break it with a fragment. The fragment carries the real weight.',
    'Start one story. Interrupt it with another. Return to the first. The gap is where the meaning lives.',
    'Write a paragraph with one sentence that does not belong. The disruption was the point.',
  ]},
  {p:/irony|ironic|comic|humour|humor|joke|play|wit(?!h)/i, t:'Tonal Irony', a:[
    'Write a sentence that means the opposite of what it says. The reader should smile, then think.',
    'Describe something serious with a light touch. The comedy should illuminate, not diminish.',
    'Write a passage where the surface is funny and the underneath is not. Do not signal which is real.',
  ]},
  {p:/repeat|repetition|pattern|refrain|return/i, t:'Strategic Repetition', a:[
    'Use one phrase three times in a paragraph, each time with a slightly different meaning.',
    'Write a passage with a refrain — a sentence that returns, changed by what surrounds it.',
    'Repeat a structural pattern three times, varying the content. Let the pattern carry argument.',
  ]},
  {p:/personal|intimate|confess|vulnerab|honest/i, t:'Controlled Intimacy', a:[
    'Write one true sentence about yourself that makes you slightly uncomfortable. That is the material.',
    'Share a small, specific memory. Do not explain why it matters. Specificity is the explanation.',
    'Move between "I" and a larger observation. The personal and the general should feel inseparable.',
  ]},
  {p:/observe|detail|notice|attend|specific|civilisation/i, t:'Radical Attention', a:[
    'Look at one object for thirty seconds. Write exactly what you see — no metaphor, just the thing itself.',
    'Describe a familiar place as if you have never been there. Notice what habit normally erases.',
    'Write a paragraph where every sentence contains one detail so specific it could only be true.',
  ]},
  {p:/argument|assert|conviction|declare|position|command/i, t:'Assertive Stance', a:[
    'Write a sentence that takes a clear position. No hedging, no "perhaps." Say the thing directly.',
    'Make an argument in three sentences: claim, evidence, implication. No qualifiers.',
    'Write a paragraph that leads with conviction. The reader knows where you stand by sentence two.',
  ]},
  {p:/time|temporal|chronolog|memory|retrospect|past|tense/i, t:'Temporal Movement', a:[
    'Write two sentences: one present tense, one past. Place them together without transition.',
    'Start in the present. Slip into a memory mid-sentence. Return without announcing the shift.',
    'Write a passage where three time periods coexist. Time should fold, not jump.',
  ]},
  {p:/metaphor|analogy|figure|symbolic|compare/i, t:'Figurative Precision', a:[
    'Compare one thing to another it should not resemble. Make the comparison feel inevitable.',
    'Write a paragraph with exactly one metaphor. Place it where it does the most work.',
    'Build an extended comparison across three sentences. It should deepen, not repeat.',
  ]},
  {p:/simple|plain|clear|direct|unadorned|trust/i, t:'Plain Force', a:[
    'Write five short declarative sentences about one subject. No ornament. Plainness is the style.',
    'Say a complex idea in words a twelve-year-old would understand. Clarity is not simplification.',
    'Write a paragraph using only common words. The constraint should make the writing stronger.',
  ]},
  {p:/destabili|unsettle|reframe|reassembl|subvert|reverse/i, t:'Subverting Expectations', a:[
    'Write a paragraph that seems to head one direction, then quietly arrives somewhere else entirely.',
    'Set up a familiar expectation in your first two sentences. In the third, undo it without announcing the turn.',
    'Write a passage where the ending reframes everything before it. The reader should want to re-read the opening.',
  ]},
  {p:/state|declarati|verdict|confident|unhedged|does not qualify/i, t:'Declarative Authority', a:[
    'Write three statements with no qualifiers. No "perhaps", no "it seems". Just say what you mean.',
    'Take a position and hold it for a full paragraph without hedging. Confidence is a rhythm, not just a word choice.',
    'Write as if the reader already agrees with you. The prose should move forward, not argue backward.',
  ]},
  {p:/stripped|skeletal|removed|spare|bare|austere/i, t:'Radical Compression', a:[
    'Write a sentence, then delete half of it. What survives is what matters.',
    'Describe an intense moment in under 20 words. Every word carries weight or it goes.',
    'Write a paragraph with no sentence longer than 10 words. Let the white space do the emotional work.',
  ]},
  {p:/perspective|angle|fairness|balance|multiple.*view|each.*version|pluralism/i, t:'Generous Perspective', a:[
    'Write two sentences about the same event from two opposing viewpoints. Give each its full weight.',
    'Describe a disagreement where both sides are right. Do not resolve it — just render it honestly.',
    'Write a paragraph that holds three perspectives simultaneously without ranking them.',
  ]},
  {p:/structur|architect|organis|formal premise|arrange|sweep|synthesis/i, t:'Structural Thinking', a:[
    'Before writing, choose a shape: circular, telescoping, or mirrored. Let the structure carry meaning.',
    'Write a paragraph where the arrangement of ideas matters as much as the ideas themselves.',
    'Organise three observations so their sequence creates an argument the sentences never state directly.',
  ]},
  {p:/invit|open|generous|warmth|welcome|access/i, t:'Deliberate Openness', a:[
    'Write a sentence that creates space for the reader to bring their own experience into the text.',
    'Write a paragraph that poses a problem without solving it. Invite the reader to sit with the difficulty.',
    'Write as if speaking to someone you respect but have never met. Warmth without presumption.',
  ]},
  {p:/genuine|authenticity|not perform|actual(?:ly)?|real(?:ly)?.*uncertain/i, t:'Genuine Uncertainty', a:[
    'Write a paragraph where you do not know the answer. Let the not-knowing be the engine, not an apology.',
    'Start with a confident claim. By the third sentence, let honest doubt erode it. Do not rescue the claim.',
    'Write as someone thinking in real time. No thesis, no conclusion — just the mind moving through difficulty.',
  ]},
  {p:/boundary|threshold|between.*and|neither.*nor|settle|dissolv/i, t:'Threshold Writing', a:[
    'Write two sentences that each belong to a different genre or mode. Place them together without transition.',
    'Describe a moment that is neither one thing nor another — dawn, an ending that is also a beginning.',
    'Write a paragraph that refuses to land. Let the reader feel the ground shifting beneath each sentence.',
  ]},
  {p:/landscape|place|terrain|geography|territory|Australian|Canadian|Zealand/i, t:'Place as Structure', a:[
    'Describe a place so precisely that it carries emotional weight without any stated feeling.',
    'Write a paragraph where the setting is not background but the thing the sentences are actually about.',
    'Name three physical details of a landscape. Let them accumulate until they become an argument.',
  ]},
  {p:/damage|trauma|surviv|difficult|hard subject|serious.*subject|does not compress|resist/i, t:'Facing Difficulty', a:[
    'Write about something painful without flinching and without dramatising. Just say what happened.',
    'Take a subject that resists easy summary. Give it the space it demands — do not compress.',
    'Write a paragraph about loss where the restraint of the prose is what makes it land.',
  ]},
  {p:/persist|keeps going|despite|impossib|what survives|endur|refuse.*consolation/i, t:'Persistence Against Limits', a:[
    'Write a sentence that reaches for meaning and fails. Then write the next sentence anyway.',
    'Describe something that endures despite every reason it should not. Let survival be the point.',
    'Write a paragraph that acknowledges impossibility in the first sentence and keeps building regardless.',
  ]},
  {p:/erudition|intellectual.*weight|curiosity.*genuine|enthusiasm|lightly|capacious/i, t:'Learned Lightness', a:[
    'Share a complex idea as if telling a friend something fascinating. Warmth, not authority.',
    'Write a sentence containing a genuinely surprising fact. Let the surprise do the work — no underlining.',
    'Write a paragraph moving across three fields of knowledge. The connections should feel inevitable.',
  ]},
  {p:/absurd|rigour|logic.*follow|internal.*logic|construct.*scenario/i, t:'Rigorous Absurdity', a:[
    'Write a premise that makes no sense. Now follow it with complete logical seriousness for three sentences.',
    'Build an absurd situation with real internal rules. The comedy comes from the rigour, not the silliness.',
    'Write a paragraph where the conclusion is ridiculous but the reasoning is airtight.',
  ]},
  {p:/negation|reversal|counter-intuitive|overturn|invert|not comfort/i, t:'Productive Negation', a:[
    'Write a sentence that negates the obvious reading. "It was not X — it was Y." Let the reversal carry weight.',
    'Take a familiar idea and turn it inside out in one paragraph. The reversal should feel earned, not clever.',
    'Write three sentences where each undoes the expectation set by the one before it.',
  ]},
  {p:/hedge|unhedged|does not qualify|fundamental claim|definitive judgment/i, t:'Unhedged Conviction', a:[
    'Write three statements with zero qualifiers. No "perhaps", no "it seems". Just say what you mean.',
    'Take a position you believe and defend it in one paragraph without softening. Confidence is a style choice.',
    'Remove every hedge from a paragraph you have written. What survives is what you actually think.',
  ]},
  {p:/form |genre refusal|new form|essay form|first person.*exposure|testimony|archive/i, t:'Form as Meaning', a:[
    'Choose an unusual structure for a paragraph — a list, a letter, a transcript. Let the form carry the argument.',
    'Write about one subject in two different forms. Notice what each form reveals and conceals.',
    'Write a paragraph where how it is organised matters as much as what it says.',
  ]},
  {p:/prose|sentence|write|voice|style|word/i, t:'Voice Craft', a:[
    'Write a sentence you admire. Then write the same idea in your own natural voice. Notice the difference.',
    'Choose one quality from this author and apply it to a paragraph about your own life.',
    'Write freely for 60 words, then revise with this author in mind. What changes? What stays?',
  ]},
];
if(typeof window!=='undefined')window.STRETCH_ACTIONS=STRETCH_ACTIONS;
