#!/usr/bin/env python3
"""
QUIRRELY VOICE AUDIO v2.0
Generates a unique 10-second audio track per user, driven by their voice profile.
Every note, chord, rhythm, and texture is informed by the user's scores.

Usage:
  python3.12 voice-audio.py --profile minimal --stance open \
    --scores '{"score_minimal":61,...}' --output /tmp/audio.wav
  python3.12 voice-audio.py --profile minimal --stance open \
    --scores '{"score_minimal":61,...}' --output /tmp/audio.wav \
    --mux /tmp/video.mp4 --final /tmp/final.mp4
"""

import json, math, os, subprocess, sys, argparse
import numpy as np
import wave

SR = 44100
DURATION = 10.0
TOTAL_SAMPLES = int(SR * DURATION)

PROFILE_KEYS = [
    'poetic','conversational','interrogative','dense','longform',
    'hedged','balanced','minimal','formal','assertive'
]

# ═══════════════════════════════════════════════════════════
# VOICE → MUSIC MAPPING
# ═══════════════════════════════════════════════════════════

# Each profile maps to a root note (Hz) and mode (major/minor intervals)
PROFILE_MUSIC = {
    'poetic':        {'root': 311.13, 'mode': 'major',  'warmth': 0.9, 'complexity': 0.7},  # Eb4
    'conversational':{'root': 349.23, 'mode': 'major',  'warmth': 0.8, 'complexity': 0.4},  # F4
    'interrogative': {'root': 466.16, 'mode': 'major',  'warmth': 0.6, 'complexity': 0.6},  # Bb4
    'dense':         {'root': 293.66, 'mode': 'minor',  'warmth': 0.7, 'complexity': 0.9},  # D4
    'longform':      {'root': 293.66, 'mode': 'major',  'warmth': 0.7, 'complexity': 0.5},  # D4
    'hedged':        {'root': 329.63, 'mode': 'minor',  'warmth': 0.5, 'complexity': 0.5},  # E4
    'balanced':      {'root': 261.63, 'mode': 'major',  'warmth': 0.6, 'complexity': 0.3},  # C4
    'minimal':       {'root': 261.63, 'mode': 'major',  'warmth': 0.5, 'complexity': 0.2},  # C4
    'formal':        {'root': 220.00, 'mode': 'minor',  'warmth': 0.4, 'complexity': 0.6},  # A3
    'assertive':     {'root': 392.00, 'mode': 'major',  'warmth': 0.6, 'complexity': 0.5},  # G4
}

# Scale intervals from root (semitones)
SCALES = {
    'major':     [0, 2, 4, 5, 7, 9, 11, 12, 14, 16],
    'minor':     [0, 2, 3, 5, 7, 8, 10, 12, 14, 15],
}

STANCE_FX = {
    'open':          {'reverb': 1.4, 'attack_mult': 1.5, 'detune': 1.2},
    'closed':        {'reverb': 0.6, 'attack_mult': 0.5, 'detune': 0.7},
    'balanced':      {'reverb': 1.0, 'attack_mult': 1.0, 'detune': 1.0},
    'contradictory': {'reverb': 1.2, 'attack_mult': 0.8, 'detune': 1.5},
}

def semitone_to_freq(root, semitones):
    return root * (2 ** (semitones / 12.0))

# ═══════════════════════════════════════════════════════════
# SYNTHESIS
# ═══════════════════════════════════════════════════════════

def sine(freq, dur, sr=SR):
    t = np.linspace(0, dur, int(sr*dur), endpoint=False)
    return np.sin(2*np.pi*freq*t)

def triangle(freq, dur, sr=SR):
    t = np.linspace(0, dur, int(sr*dur), endpoint=False)
    return 2*np.abs(2*(t*freq - np.floor(t*freq+0.5))) - 1

def envelope(s, attack=0.05, decay=0.1, sustain=0.6, release=0.3):
    n = len(s); env = np.ones(n)
    a=int(attack*SR); d=int(decay*SR); r=int(release*SR)
    if a>0: env[:a] = np.linspace(0,1,a)
    if d>0 and a+d<n: env[a:a+d] = np.linspace(1,sustain,d)
    if a+d<n-r: env[a+d:n-r] = sustain
    if r>0 and n-r>=0: env[max(0,n-r):] = np.linspace(sustain,0,min(r,n))
    return s * env

def add_reverb(dry, sr=SR, amount=1.0):
    rev = np.zeros(len(dry))
    delays = [(int(55*amount), 0.14), (int(120*amount), 0.09),
              (int(195*amount), 0.05), (int(310*amount), 0.025)]
    for d_ms, vol in delays:
        d = int(d_ms * sr / 1000)
        if 0 < d < len(rev):
            rev[d:] += dry[:len(dry)-d] * vol * amount
    return dry + rev

def voice_pad(freq, dur, warmth=0.6, detune=1.0, attack_mult=1.0):
    """Pad shaped by voice parameters."""
    dt = 0.003 * detune
    s = sine(freq, dur) * 0.25
    s += sine(freq*(1+dt), dur) * 0.22
    s += sine(freq*(1-dt), dur) * 0.22
    s += sine(freq*(1+dt*2), dur) * 0.10
    s += sine(freq*(1-dt*2), dur) * 0.10
    # Fifth — more present with higher warmth
    s += sine(freq*1.5, dur) * 0.08 * warmth
    s += sine(freq*1.5*(1+dt), dur) * 0.06 * warmth
    # Octave shimmer
    s += sine(freq*2, dur) * 0.06 * warmth
    # Sub
    s += triangle(freq*0.5, dur) * 0.10 * warmth
    s += sine(freq*0.25, dur) * 0.04 * warmth
    att = 1.0 * attack_mult
    return envelope(s, attack=att, decay=0.6, sustain=0.72, release=1.8*attack_mult)

def voice_bell(freq, dur=1.5, warmth=0.6, reverb_amt=1.0):
    """Bell shaped by voice."""
    s = sine(freq, dur) * 0.38
    s += sine(freq*2.0, dur) * 0.20
    s += sine(freq*3.0, dur) * 0.10 * warmth
    s += sine(freq*4.2, dur) * 0.06 * warmth
    s += sine(freq*5.4, dur) * 0.03 * warmth
    dry = envelope(s, attack=0.002, decay=0.25, sustain=0.18, release=dur*0.5)
    return add_reverb(dry, amount=reverb_amt)

def voice_pluck(freq, dur=0.8, warmth=0.6, reverb_amt=1.0, attack_mult=1.0):
    """Pluck shaped by voice."""
    s = sine(freq, dur) * 0.45
    s += triangle(freq, dur) * 0.22
    s += sine(freq*2, dur) * 0.10 * warmth
    s += sine(freq*3, dur) * 0.04 * warmth
    att = 0.003 * attack_mult
    dry = envelope(s, attack=att, decay=0.10, sustain=0.22, release=dur*0.4)
    return add_reverb(dry, amount=reverb_amt)

def voice_shimmer(freq, dur=2.0, warmth=0.6):
    """High sparkle shaped by voice."""
    s = sine(freq, dur) * 0.25
    s += sine(freq*1.5, dur) * 0.18 * warmth
    s += sine(freq*2.01, dur) * 0.12 * warmth
    s += sine(freq*2.99, dur) * 0.06 * warmth
    return envelope(s, attack=0.4, decay=0.5, sustain=0.18, release=0.8)

def fade_in(s, dur_s):
    n=min(int(dur_s*SR),len(s)); s[:n]*=np.linspace(0,1,n); return s

def fade_out(s, dur_s):
    n=min(int(dur_s*SR),len(s)); s[-n:]*=np.linspace(1,0,n); return s

def mix_at(out, sig, t):
    start=int(t*SR); end=start+len(sig)
    if end>len(out): sig=sig[:len(out)-start]; end=len(out)
    if start<0: sig=sig[-start:]; start=0
    out[start:end] += sig

# ═══════════════════════════════════════════════════════════
# BUILD VOICE PROFILE
# ═══════════════════════════════════════════════════════════

def build_voice_music(profile, stance, scores):
    """Extract all musical parameters from voice data."""
    dom = (profile or 'conversational').lower()
    st = (stance or 'balanced').lower()
    pm = PROFILE_MUSIC.get(dom, PROFILE_MUSIC['conversational'])
    fx = STANCE_FX.get(st, STANCE_FX['balanced'])

    # Parse scores and sort
    parsed = []
    for key in PROFILE_KEYS:
        val = scores.get('score_'+key, scores.get(key, 0))
        parsed.append((key, round(val)))
    parsed.sort(key=lambda x: -x[1])

    # Build scale from dominant profile's mode
    root = pm['root']
    mode = pm['mode']
    scale_intervals = SCALES[mode]
    scale = [semitone_to_freq(root, s) for s in scale_intervals]

    # Score distribution affects rhythm
    vals = [v for _, v in parsed]
    spread = max(vals) - min(vals) if vals else 50
    avg_score = sum(vals) / len(vals) if vals else 50

    # Top 3 determine chord richness
    top3_avg = sum(v for _, v in parsed[:3]) / 3

    # Contradictory stance adds tension intervals
    tension_intervals = []
    if st == 'contradictory':
        tension_intervals = [6, 10]  # tritone, minor 7th

    return {
        'root': root,
        'scale': scale,
        'mode': mode,
        'warmth': pm['warmth'],
        'complexity': pm['complexity'],
        'reverb': fx['reverb'],
        'attack_mult': fx['attack_mult'],
        'detune': fx['detune'],
        'spread': spread,
        'avg_score': avg_score,
        'top3_avg': top3_avg,
        'tension_intervals': tension_intervals,
        'sorted_scores': parsed,
        'dom_score': parsed[0][1] if parsed else 50,
    }

# ═══════════════════════════════════════════════════════════
# COMPOSITION
# ═══════════════════════════════════════════════════════════

def compose(vm):
    """Build unique 10-second track from voice music parameters."""
    out = np.zeros(TOTAL_SAMPLES)
    sc = vm['scale']
    root = vm['root']
    w = vm['warmth']
    rev = vm['reverb']
    att = vm['attack_mult']
    det = vm['detune']
    cpx = vm['complexity']

    # Tempo feel from dominant score (higher = slightly more energy)
    pluck_spacing = 0.22 - (vm['dom_score'] / 100) * 0.06  # 0.16-0.22s

    # === PHASE 1: 0-2.8s — Wordmark pad swell ===
    # Root chord: root + 3rd + 5th
    mix_at(out, fade_in(voice_pad(root*0.5, 3.8, w, det, att)*0.24, 1.5), 0.0)
    mix_at(out, fade_in(voice_pad(sc[2]*0.5, 3.8, w, det, att)*0.18, 1.8), 0.15)
    mix_at(out, fade_in(voice_pad(sc[4]*0.5, 3.5, w, det, att)*0.14, 2.0), 0.3)

    # Opening bell — root note
    mix_at(out, voice_bell(sc[7], 2.2, w, rev)*0.11, 0.8)  # octave
    mix_at(out, voice_bell(sc[9], 1.6, w, rev)*0.06, 1.0)  # 10th

    # Tension note for contradictory stance
    for ti in vm['tension_intervals']:
        tf = semitone_to_freq(root, ti)
        mix_at(out, voice_bell(tf, 1.8, w*0.5, rev)*0.04, 1.2)

    # === PHASE 2: 2.8-3.8s — Transition ===
    # Move to IV chord feel
    iv_root = sc[3]  # 4th degree
    mix_at(out, voice_pad(iv_root*0.5, 3.0, w, det, att)*0.18, 2.5)
    mix_at(out, voice_pad(sc[5]*0.5, 3.0, w, det, att)*0.13, 2.7)

    # Rejji arrival — 5th degree bell
    mix_at(out, voice_bell(sc[4], 1.8, w, rev)*0.14, 3.0)

    # === PHASE 3: 3.5-5.5s — Lines grow ===
    # One pluck per voice dimension, pitch from scale, timing from score ranking
    sorted_scores = vm['sorted_scores']
    for i, (name, score) in enumerate(sorted_scores):
        # Map each dimension to a scale degree
        note_idx = i % len(sc)
        freq = sc[note_idx]
        # Volume scales with score
        vol = 0.06 + (score / 100) * 0.08
        # Timing: staggered with voice-driven spacing
        t = 3.5 + i * pluck_spacing
        # Duration varies with complexity
        dur = 0.5 + cpx * 0.4
        mix_at(out, voice_pluck(freq, dur, w, rev, att)*vol, t)

    # Continuing pad
    mix_at(out, voice_pad(root*0.5, 4.0, w, det, att)*0.16, 3.2)
    mix_at(out, voice_pad(sc[4]*0.5, 4.0, w, det, att)*0.10, 3.4)

    # === PHASE 4: 5-7s — Labels + shimmer ===
    # Shimmer pitch from scale
    mix_at(out, voice_shimmer(sc[7], 2.5, w)*0.07, 5.0)
    mix_at(out, voice_shimmer(sc[9] if len(sc)>9 else sc[7]*1.5, 2.0, w)*0.04, 5.3)

    # Resolving pad — back to I chord
    mix_at(out, voice_pad(root*0.5, 3.5, w, det, att)*0.20, 5.5)
    mix_at(out, voice_pad(sc[2]*0.5, 3.5, w, det, att)*0.14, 5.7)
    mix_at(out, voice_pad(sc[4]*0.5, 3.0, w, det, att)*0.10, 5.9)

    # Title bells — I chord arpeggio
    mix_at(out, voice_bell(sc[7], 2.0, w, rev)*0.12, 6.0)
    mix_at(out, voice_bell(sc[9] if len(sc)>9 else sc[7]*1.26, 1.5, w, rev)*0.07, 6.2)

    # Contradictory: add dissonant shimmer
    for ti in vm['tension_intervals']:
        tf = semitone_to_freq(root*2, ti)
        mix_at(out, voice_shimmer(tf, 1.5, w*0.4)*0.03, 6.1)

    # === PHASE 5: 7-8.5s — Resolution ===
    # Descending pluck pattern — scale degrees 5, 3, 1
    mix_at(out, voice_pluck(sc[4], 1.0, w, rev, att)*0.09, 7.2)
    mix_at(out, voice_pluck(sc[2], 0.8, w, rev, att)*0.07, 7.5)
    mix_at(out, voice_pluck(root, 0.8, w, rev, att)*0.06, 7.7)

    # CTA bell — octave
    mix_at(out, voice_bell(sc[7], 2.5, w, rev)*0.11, 8.2)

    # === PHASE 6: Fade ===
    p_end = voice_pad(root*0.5, 2.5, w, det, att)*0.13
    mix_at(out, fade_out(p_end, 1.5), 7.5)

    # Sub bass presence scales with warmth
    if w > 0.6:
        sub = sine(root*0.25, 8.0) * 0.04 * w
        mix_at(out, fade_in(fade_out(sub, 2.0), 2.0), 1.0)

    # === MASTER ===
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.85
    out = fade_out(out, 1.0)
    out = fade_in(out, 0.1)
    return out

# ═══════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════

def write_wav(samples, path):
    pcm = np.int16(samples * 32767)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    print(f"WAV: {path} ({os.path.getsize(path)} bytes)")

def mux(wav_path, mp4_path, output_path):
    cmd = [
        'ffmpeg','-y','-i',mp4_path,'-i',wav_path,
        '-c:v','copy','-c:a','aac','-b:a','128k',
        '-shortest','-movflags','+faststart',output_path
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"Mux error: {r.stderr[-300:]}"); return False
    sz = os.path.getsize(output_path)
    print(f"Final: {output_path} ({sz} bytes, {sz/1024/1024:.1f} MB)")
    return True

if __name__ == '__main__':
    pa = argparse.ArgumentParser()
    pa.add_argument('--profile', required=True)
    pa.add_argument('--stance', default='balanced')
    pa.add_argument('--scores', required=True)
    pa.add_argument('--output', default='/tmp/voice-audio.wav')
    pa.add_argument('--mux', default='')
    pa.add_argument('--final', default='/tmp/voice-final.mp4')
    a = pa.parse_args()

    scores = json.loads(a.scores)
    vm = build_voice_music(a.profile, a.stance, scores)
    print(f"Voice music: root={vm['root']:.1f}Hz, mode={vm['mode']}, warmth={vm['warmth']}, "
          f"complexity={vm['complexity']}, reverb={vm['reverb']}, spread={vm['spread']}")

    audio = compose(vm)
    write_wav(audio, a.output)

    if a.mux:
        mux(a.output, a.mux, a.final)
