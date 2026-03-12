/**
 * QUIRRELY VOICE DESIGN SYSTEM v1.0
 * 10 profiles x 4 stances -> CSS design tokens
 * Load after profile-system.js. Standalone, no imports.
 */
const VOICE_DESIGN = (function() {
  var P = {
    assertive:     {a:'#FF6B6B',d:'#E55A4A',l:'#FFF0EE'},
    minimal:       {a:'#4ECDC4',d:'#3BB8B0',l:'#EEFBFA'},
    poetic:        {a:'#A29BFE',d:'#8B7CF0',l:'#F3F1FF'},
    dense:         {a:'#6C5CE7',d:'#5B4BD5',l:'#EFEAFF'},
    conversational:{a:'#FDCB6E',d:'#F0B93D',l:'#FFF8E7'},
    formal:        {a:'#636E72',d:'#4A5459',l:'#F0F1F2'},
    balanced:      {a:'#00B894',d:'#00A381',l:'#E8F8F3'},
    longform:      {a:'#0984E3',d:'#0770C4',l:'#E8F4FD'},
    interrogative: {a:'#E17055',d:'#D15F44',l:'#FDF0ED'},
    hedged:        {a:'#81ECEC',d:'#6DDADA',l:'#EEFCFC'},
  };
  var S = {
    open:         {w:400,den:'relaxed',bdr:'dashed', r:'14px'},
    closed:       {w:600,den:'tight',  bdr:'solid',  r:'6px'},
    balanced:     {w:500,den:'normal', bdr:'solid',  r:'10px'},
    contradictory:{w:500,den:'normal', bdr:'double', r:'10px'},
  };
  var D = {
    relaxed:{cp:'2rem',   lh:'1.85',gap:'1.5rem', hs:'1.75rem'},
    normal: {cp:'1.5rem', lh:'1.7', gap:'1.25rem',hs:'1.5rem'},
    tight:  {cp:'1.25rem',lh:'1.55',gap:'1rem',   hs:'1.35rem'},
  };
  function getTokens(profile, stance) {
    var p=P[profile]||P.conversational, s=S[stance]||S.balanced, d=D[s.den];
    return {
      '--voice-accent':p.a,'--voice-accent-dark':p.d,
      '--voice-accent-light':p.l,'--voice-accent-10':p.a+'1A',
      '--voice-accent-20':p.a+'33',
      '--voice-weight':String(s.w),'--voice-border-style':s.bdr,
      '--voice-radius':s.r,
      '--voice-card-pad':d.cp,'--voice-line-height':d.lh,
      '--voice-gap':d.gap,'--voice-header-size':d.hs,
    };
  }
  function apply(profile, stance) {
    var t=getTokens(profile,stance), r=document.documentElement;
    for(var k in t) r.style.setProperty(k,t[k]);
    r.setAttribute('data-voice-profile',profile);
    r.setAttribute('data-voice-stance',stance);
  }
  function getComboKey(p,s) {
    return (p||'conversational').toUpperCase()+'-'+(s||'balanced').toUpperCase();
  }

  var CTA = {
    assertive:     {upgrade:'Unlock your full voice breakdown',share:'Show them your voice'},
    minimal:       {upgrade:'See the full picture',share:'Share your voice'},
    poetic:        {upgrade:'Discover the deeper layers of your voice',share:'Let your voice be heard'},
    dense:         {upgrade:'Access comprehensive voice analytics',share:'Share your detailed profile'},
    conversational:{upgrade:'Want to see what else your writing says about you?',share:'Share your voice with friends'},
    formal:        {upgrade:'Unlock detailed professional voice analysis',share:'Share your professional profile'},
    balanced:      {upgrade:'Explore every dimension of your voice',share:'Share your balanced perspective'},
    longform:      {upgrade:'There is more to your voice — explore the full picture',share:'Share your writing journey'},
    interrogative: {upgrade:'What else might your voice reveal?',share:'What does your voice say?'},
    hedged:        {upgrade:'There might be more to discover about your voice',share:'Share what you have found so far'},
  };
  function getContent(profile, stance) {
    var key = (profile||'conversational').toUpperCase()+'-'+(stance||'balanced').toUpperCase();
    var meta = (typeof PROFILE_META!=='undefined') ? PROFILE_META[key] : null;
    var pt = (typeof PROFILE_TYPES!=='undefined') ? PROFILE_TYPES[(profile||'conversational').toUpperCase()] : null;
    var cta = CTA[profile] || CTA.conversational;
    return {
      title: meta ? meta.title : (profile||'conversational'),
      tagline: meta ? meta.tagline : '',
      icon: meta ? meta.icon : '',
      color: pt ? pt.color : '#FDCB6E',
      gradient: pt ? pt.gradient : '',
      traits: pt ? pt.traits : [],
      writers: meta ? meta.famousWriters : [],
      upgradeText: cta.upgrade,
      shareText: cta.share,
    };
  }
  return {P:P,S:S,D:D,CTA:CTA,getTokens:getTokens,apply:apply,getComboKey:getComboKey,getContent:getContent};
})();
if(typeof module!=="undefined"&&module.exports)module.exports=VOICE_DESIGN;
if(typeof window!=="undefined")window.VOICE_DESIGN=VOICE_DESIGN;
