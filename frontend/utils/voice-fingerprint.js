/**
 * QUIRRELY VOICE FINGERPRINT v3.0
 * Canvas renderer: real Rejji + score-length voice lines + dominant at top
 * Requires: voice-design.js (VOICE_DESIGN.P for colours)
 */
var VoiceFingerprint = (function () {
  'use strict';

  var PROFILE_KEYS = [
    'poetic','conversational','interrogative','dense','longform',
    'hedged','balanced','minimal','formal','assertive'
  ];

  var FALLBACK_COLORS = {
    poetic:        {a:'#A29BFE',d:'#8B7CF0'},
    conversational:{a:'#FDCB6E',d:'#F0B93D'},
    interrogative: {a:'#E17055',d:'#D15F44'},
    dense:         {a:'#6C5CE7',d:'#5B4BD5'},
    longform:      {a:'#0984E3',d:'#0770C4'},
    hedged:        {a:'#81ECEC',d:'#6DDADA'},
    balanced:      {a:'#00B894',d:'#00A381'},
    minimal:       {a:'#4ECDC4',d:'#3BB8B0'},
    formal:        {a:'#636E72',d:'#4A5459'},
    assertive:     {a:'#FF6B6B',d:'#E55A4A'},
  };

  function getColor(key) {
    if (typeof VOICE_DESIGN !== 'undefined' && VOICE_DESIGN.P && VOICE_DESIGN.P[key]) {
      return VOICE_DESIGN.P[key];
    }
    return FALLBACK_COLORS[key] || {a:'#FDCB6E', d:'#F0B93D'};
  }

  function buildProfiles(scores, dominantProfile) {
    var dom = (dominantProfile || 'conversational').toLowerCase();
    var list = [];
    for (var i = 0; i < PROFILE_KEYS.length; i++) {
      var key = PROFILE_KEYS[i];
      var scoreKey = 'score_' + key;
      var val = 0;
      if (scores && scores[scoreKey] !== undefined) val = Math.round(scores[scoreKey]);
      else if (scores && scores[key] !== undefined) val = Math.round(scores[key]);
      var c = getColor(key);
      list.push({name: key, label: key.charAt(0).toUpperCase() + key.slice(1), score: val, color: c.a, dark: c.d, isDom: key === dom});
    }
    list.sort(function (a, b) {
      if (a.isDom) return -1;
      if (b.isDom) return 1;
      return b.score - a.score;
    });
    return list;
  }

  function drawBg(ctx, W, H, cx, cy) {
    // Transparent — card background shows through
    ctx.clearRect(0, 0, W, H);
    // Subtle radial glow behind Rejji
    var g = ctx.createRadialGradient(cx, cy, 20, cx, cy, Math.min(W, H) * 0.42);
    g.addColorStop(0, 'rgba(215,239,255,0.35)');
    g.addColorStop(0.5, 'rgba(215,239,255,0.12)');
    g.addColorStop(1, 'rgba(215,239,255,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  }

  function drawLines(ctx, profiles, cx, cy, ease) {
    if (ease < 0.02) return;
    var n = profiles.length;
    var innerR = 80;
    var baseLen = 110;
    var maxExtra = 195;

    for (var i = 0; i < n; i++) {
      var p = profiles[i];
      var angle = -Math.PI / 2 + (i / n) * Math.PI * 2;
      var maxLen = baseLen + (p.score / 100) * maxExtra;
      var len = maxLen * ease;
      var cosA = Math.cos(angle);
      var sinA = Math.sin(angle);
      var sx = cx + cosA * innerR;
      var sy = cy + sinA * innerR;
      var ex = cx + cosA * len;
      var ey = cy + sinA * len;
      var norm = p.score / 100;

      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.lineTo(ex, ey);
      ctx.strokeStyle = p.color;
      ctx.lineWidth = 2 + norm * 1.5;
      ctx.globalAlpha = (0.4 + norm * 0.45) * ease;
      ctx.lineCap = 'round';
      ctx.stroke();

      var dotR = 4 + norm * 9;
      ctx.beginPath();
      ctx.arc(ex, ey, dotR * ease, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = (0.6 + norm * 0.35) * ease;
      ctx.fill();
      ctx.strokeStyle = p.dark;
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.6 * ease;
      ctx.stroke();

      ctx.globalAlpha = ease;
      ctx.textAlign = cosA < -0.15 ? 'right' : cosA > 0.15 ? 'left' : 'center';
      ctx.textBaseline = 'middle';
      var lbR = len + dotR + 14;
      var lx = cx + cosA * lbR;
      var ly = cy + sinA * lbR;

      if (p.isDom) {
        ctx.font = '700 26px Jost, -apple-system, sans-serif';
        ctx.fillStyle = p.dark;
        ctx.fillText(p.label, lx, ly - 12);
        ctx.font = '700 20px Jost, -apple-system, sans-serif';
        var scoreText = String(p.score);
        var sw = ctx.measureText(scoreText).width;
        var pillX = ctx.textAlign === 'right' ? lx - sw / 2 - 8 : ctx.textAlign === 'left' ? lx + sw / 2 + 8 : lx;
        var pillY = ly + 14;
        ctx.globalAlpha = 0.15 * ease;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.roundRect(pillX - sw / 2 - 10, pillY - 13, sw + 20, 26, 13);
        ctx.fill();
        ctx.globalAlpha = ease;
        ctx.fillStyle = p.dark;
        ctx.textAlign = 'center';
        ctx.fillText(scoreText, pillX, pillY);
      } else {
        ctx.font = '500 21px Jost, -apple-system, sans-serif';
        ctx.fillStyle = '#351E28';
        ctx.fillText(p.label, lx, ly - 8);
        ctx.font = '600 16px Jost, -apple-system, sans-serif';
        ctx.fillStyle = p.dark;
        ctx.fillText(p.score, lx, ly + 13);
      }
    }
    ctx.globalAlpha = 1;
  }

  function drawRejji(ctx, profiles, cx, cy, scale, ease) {
    if (ease < 0.02) return;
    var sc = scale * ease;
    var dom = profiles[0];
    var sec = profiles.length > 1 ? profiles[1] : dom;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(sc, sc);
    ctx.translate(-40, -65);
    ctx.globalAlpha = ease;

    // Tail
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(58, 112);
    ctx.quadraticCurveTo(85, 98, 94, 62);
    ctx.quadraticCurveTo(100, 26, 74, 8);
    ctx.quadraticCurveTo(50, -8, 42, 22);
    ctx.quadraticCurveTo(38, 44, 54, 60);
    ctx.quadraticCurveTo(70, 78, 62, 100);
    ctx.quadraticCurveTo(58, 110, 58, 112);
    ctx.closePath();
    var tg = ctx.createLinearGradient(58, 112, 74, 8);
    tg.addColorStop(0, '#FFFEF9');
    tg.addColorStop(0.35, dom.color);
    tg.addColorStop(0.7, sec.color);
    tg.addColorStop(1, dom.dark);
    ctx.fillStyle = tg;
    ctx.globalAlpha = 0.75 * ease;
    ctx.fill();
    ctx.strokeStyle = dom.dark;
    ctx.lineWidth = 0.8;
    ctx.globalAlpha = 0.45 * ease;
    ctx.stroke();
    ctx.restore();

    ctx.globalAlpha = ease;

    // Body
    ctx.fillStyle = '#FFFEF9';
    ctx.strokeStyle = '#E0DBD5';
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.ellipse(40, 98, 22, 26, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Arms
    ctx.lineWidth = 1.8;
    ctx.fillStyle = '#FFFEF9';
    ctx.beginPath();
    ctx.moveTo(20, 68);
    ctx.quadraticCurveTo(12, 72, 14, 80);
    ctx.quadraticCurveTo(16, 86, 24, 88);
    ctx.lineTo(32, 86);
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(60, 68);
    ctx.quadraticCurveTo(68, 72, 66, 80);
    ctx.quadraticCurveTo(64, 86, 56, 88);
    ctx.lineTo(48, 86);
    ctx.fill();
    ctx.stroke();

    // Paws
    ctx.fillStyle = '#FFFEF9';
    ctx.beginPath();
    ctx.ellipse(28, 86, 7, 5, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(52, 86, 7, 5, 0, 0, Math.PI * 2);
    ctx.fill();

    // Acorn
    ctx.fillStyle = '#FF5C34';
    ctx.beginPath();
    ctx.ellipse(40, 82, 6, 8, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#E04820';
    ctx.lineWidth = 0.6;
    ctx.stroke();
    ctx.fillStyle = '#E04820';
    ctx.beginPath();
    ctx.moveTo(34, 78);
    ctx.quadraticCurveTo(34, 74, 40, 72);
    ctx.quadraticCurveTo(46, 74, 46, 78);
    ctx.closePath();
    ctx.fill();
    ctx.fillStyle = '#8B6914';
    ctx.beginPath();
    ctx.arc(40, 70, 1.8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillRect(39, 70, 2, 3);

    // Head
    ctx.fillStyle = '#FFFEF9';
    ctx.strokeStyle = '#E0DBD5';
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.ellipse(40, 50, 22, 20, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Ears
    ctx.fillStyle = '#D4CCC4';
    ctx.globalAlpha = 0.6 * ease;
    ctx.beginPath();
    ctx.ellipse(24, 30, 8, 14, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(56, 30, 8, 14, 0, 0, Math.PI * 2);
    ctx.fill();

    // Eyes
    ctx.globalAlpha = ease;
    ctx.fillStyle = '#1a1a1a';
    ctx.beginPath();
    ctx.ellipse(32, 48, 5.5, 6, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(48, 48, 5.5, 6, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#FFF';
    ctx.beginPath();
    ctx.arc(33, 46.5, 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(49, 46.5, 2, 0, Math.PI * 2);
    ctx.fill();

    // Nose
    ctx.fillStyle = '#4A4A4A';
    ctx.beginPath();
    ctx.ellipse(40, 60, 4.5, 3.5, 0, 0, Math.PI * 2);
    ctx.fill();

    // Redraw ears on top of tail
    ctx.fillStyle = '#D4CCC4';
    ctx.globalAlpha = 0.7 * ease;
    ctx.beginPath();
    ctx.ellipse(24, 30, 8, 14, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(56, 30, 8, 14, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = ease;

    ctx.restore();
  }

  function drawChrome(ctx, W, H, cx, domLabel, ease, opts) {
    if (ease < 0.1) return;
    ctx.globalAlpha = ease;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // === TITLE — big, bold, persimmon ===
    var title = (opts && opts.title) ? opts.title : 'Your Voice Fingerprint';
    ctx.font = '700 52px Jost, -apple-system, sans-serif';
    ctx.fillStyle = '#FF5C34';
    ctx.fillText(title, cx, 48);

    // === SUBTITLE — italic tagline ===
    var sub = (opts && opts.subtitle) ? opts.subtitle : 'Dominant: ' + domLabel;
    ctx.font = 'italic 500 30px Jost, -apple-system, sans-serif';
    ctx.fillStyle = '#6B5B62';
    ctx.fillText(sub, cx, 92);

    // === WORDMARK — "Quirrely" with persimmon "re" ===
    var wmY = H - 62;
    ctx.font = '600 48px Jost, -apple-system, sans-serif';
    var partA = 'Quir';
    var partB = 're';
    var partC = 'ly';
    var wA = ctx.measureText(partA).width;
    var wB = ctx.measureText(partB).width;
    var wC = ctx.measureText(partC).width;
    var totalW = wA + wB + wC;
    var startX = cx - totalW / 2;

    ctx.textAlign = 'left';
    ctx.fillStyle = '#351E28';
    ctx.fillText(partA, startX, wmY);
    ctx.fillStyle = '#FF5C34';
    ctx.fillText(partB, startX + wA, wmY);
    ctx.fillStyle = '#351E28';
    ctx.fillText(partC, startX + wA + wB, wmY);

    ctx.textAlign = 'center';
    ctx.font = 'italic 500 20px Jost, -apple-system, sans-serif';
    ctx.fillStyle = '#6B5B62';
    ctx.fillText('Find your voice. Feed your curiosity.', cx, wmY + 38);

    ctx.globalAlpha = 1;
  }

  function render(canvasId, scores, profile, stance, options) {
    var canvas = document.getElementById(canvasId);
    if (!canvas || !canvas.getContext) return;

    var opts = options || {};
    var W = opts.width || 1080;
    var H = opts.height || 1000;
    var animated = opts.animated !== false;
    var rejjiScale = opts.rejjiScale || 1.8;
    var onComplete = opts.onComplete || null;

    canvas.width = W;
    canvas.height = H;
    var ctx = canvas.getContext('2d');
    var cx = W / 2;
    var cy = H * 0.47;

    var dom = (profile || 'conversational').toLowerCase();
    var profs = buildProfiles(scores, dom);

    if (!animated) {
      drawBg(ctx, W, H, cx, cy);
      drawLines(ctx, profs, cx, cy, 1);
      drawRejji(ctx, profs, cx, cy, rejjiScale, 1);
      drawChrome(ctx, W, H, cx, profs[0].label, 1, opts);
      if (onComplete) onComplete();
      return;
    }

    var start = null;
    var dur = opts.duration || 1600;

    function ease(delay, length, t) {
      var raw = Math.min(1, Math.max(0, (t - delay) / length));
      return 1 - Math.pow(1 - raw, 3);
    }

    function frame(ts) {
      if (!start) start = ts;
      var t = Math.min(1, (ts - start) / dur);

      ctx.clearRect(0, 0, W, H);
      drawBg(ctx, W, H, cx, cy);
      drawLines(ctx, profs, cx, cy, ease(0.3, 0.5, t));
      drawRejji(ctx, profs, cx, cy, rejjiScale, ease(0, 0.5, t));
      drawChrome(ctx, W, H, cx, profs[0].label, ease(0.5, 0.4, t), opts);

      if (t < 1) {
        requestAnimationFrame(frame);
      } else {
        if (onComplete) onComplete();
      }
    }

    requestAnimationFrame(frame);
  }

  function toPNG(canvasId) {
    var canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    return canvas.toDataURL('image/png');
  }

  return {
    render: render,
    toPNG: toPNG,
    buildProfiles: buildProfiles,
  };
})();

if (typeof window !== 'undefined') window.VoiceFingerprint = VoiceFingerprint;
