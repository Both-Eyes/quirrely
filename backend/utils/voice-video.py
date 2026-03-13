#!/usr/bin/env python3
"""
QUIRRELY VOICE VIDEO v4.0
10s 1080x1080 MP4 — SVG-rendered Rejji + tail, identical to dashboard canvas.
Requires: cairosvg, pillow, ffmpeg
Run with: python3.12
"""

import json, math, os, subprocess, sys, io
from PIL import Image, ImageDraw, ImageFont
import cairosvg

W, H = 1080, 1080
FPS = 30
DURATION = 10
TOTAL_FRAMES = FPS * DURATION

PROFILE_KEYS = [
    'poetic','conversational','interrogative','dense','longform',
    'hedged','balanced','minimal','formal','assertive'
]
COLORS = {
    'poetic':{'a':'#A29BFE','d':'#8B7CF0'},'conversational':{'a':'#FDCB6E','d':'#F0B93D'},
    'interrogative':{'a':'#E17055','d':'#D15F44'},'dense':{'a':'#6C5CE7','d':'#5B4BD5'},
    'longform':{'a':'#0984E3','d':'#0770C4'},'hedged':{'a':'#81ECEC','d':'#6DDADA'},
    'balanced':{'a':'#00B894','d':'#00A381'},'minimal':{'a':'#4ECDC4','d':'#3BB8B0'},
    'formal':{'a':'#636E72','d':'#4A5459'},'assertive':{'a':'#FF6B6B','d':'#E55A4A'},
}
BG_CREAM = (255,251,245)
BG_BLUE = (215,239,255)
INK = (53,30,40)
MUTED = (107,91,98)
PERSIMMON = (255,92,52)
PERSIMMON_DK = (224,72,32)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def lerp_color(c1,c2,t):
    t = max(0.0,min(1.0,t))
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def ease_out(t): return 1-(1-min(1,max(0,t)))**3
def ease_in(t): return min(1,max(0,t))**2
def ease_io(t):
    t=min(1,max(0,t)); return 3*t*t-2*t*t*t

# ═══════════════════════════════════════════════════════════
# FONTS
# ═══════════════════════════════════════════════════════════
_fc={}
def _find(bold=False,italic=False):
    if bold: names=['Jost-Bold','NotoSans-Bold','LiberationSans-Bold','DejaVuSans-Bold']
    elif italic: names=['Jost-Italic','LiberationSans-Italic','DejaVuSans-Oblique']
    else: names=['Jost-Regular','NotoSans-Regular','LiberationSans-Regular','DejaVuSans']
    dirs=['/usr/share/fonts','/usr/share/fonts/truetype','/usr/share/fonts/dejavu-sans-fonts',
          '/usr/share/fonts/liberation-sans','/usr/share/fonts/google-noto']
    for d in dirs:
        for n in names:
            p=os.path.join(d,n+'.ttf')
            if os.path.exists(p): return p
    return None

def gf(sz,bold=False):
    k=(sz,bold)
    if k not in _fc:
        p=_find(bold=bold)
        _fc[k]=ImageFont.truetype(p,sz) if p else ImageFont.load_default()
    return _fc[k]

def gif(sz):
    k=(sz,'i')
    if k not in _fc:
        p=_find(italic=True)
        _fc[k]=ImageFont.truetype(p,sz) if p else gf(sz)
    return _fc[k]

# ═══════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════
def build_profiles(scores,dominant):
    dom=(dominant or 'conversational').lower()
    items=[]
    for key in PROFILE_KEYS:
        val=round(scores.get('score_'+key,scores.get(key,0)))
        c=COLORS.get(key,COLORS['conversational'])
        items.append({'name':key,'label':key.capitalize(),'score':val,
                      'color':hex_to_rgb(c['a']),'dark':hex_to_rgb(c['d']),'is_dom':key==dom})
    items.sort(key=lambda x:(-x['is_dom'],-x['score']))
    return items

# ═══════════════════════════════════════════════════════════
# SVG → PNG RENDERING
# ═══════════════════════════════════════════════════════════

def render_tail_png(dom_hex, sec_hex, w=400, h=500):
    """Render the exact SVG tail path with voice-colour gradient to a PIL RGBA image."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 130" width="{w}" height="{h}">
  <defs>
    <linearGradient id="tg" x1="0.58" y1="1" x2="0.74" y2="0">
      <stop offset="0" stop-color="#FFFEF9"/>
      <stop offset="0.35" stop-color="{dom_hex}"/>
      <stop offset="0.7" stop-color="{sec_hex}"/>
      <stop offset="1" stop-color="{dom_hex}" stop-opacity="0.85"/>
    </linearGradient>
  </defs>
  <path d="M58 112 Q85 98,94 62 Q100 26,74 8 Q50-8,42 22 Q38 44,54 60 Q70 78,62 100 Q58 110,58 112Z"
        fill="url(#tg)" fill-opacity="0.78"
        stroke="{dom_hex}" stroke-width="0.8" stroke-opacity="0.45"/>
</svg>'''
    png_data = cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h)
    return Image.open(io.BytesIO(png_data)).convert('RGBA')

def render_rejji_png(w=320, h=480):
    """Render the exact Rejji SVG (body only, no tail) to a PIL RGBA image."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 120" width="{w}" height="{h}">
  <ellipse cx="40" cy="98" rx="22" ry="26" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.4"/>
  <path d="M20 68 Q12 72,14 80 Q16 86,24 88 L32 86" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.8"/>
  <path d="M60 68 Q68 72,66 80 Q64 86,56 88 L48 86" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.8"/>
  <ellipse cx="28" cy="86" rx="7" ry="5" fill="#FFFEF9"/>
  <ellipse cx="52" cy="86" rx="7" ry="5" fill="#FFFEF9"/>
  <ellipse cx="40" cy="78" rx="9" ry="4" fill="#E85A5A"/>
  <rect x="38.5" y="74" width="3" height="4" rx="1.5" fill="#D4504A"/>
  <path d="M31 78 Q30 94,40 99 Q50 94,49 78 Z" fill="#FF5C34"/>
  <ellipse cx="40" cy="50" rx="22" ry="20" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.4"/>
  <ellipse cx="24" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.6"/>
  <ellipse cx="56" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.6"/>
  <ellipse cx="32" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>
  <ellipse cx="48" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>
  <circle cx="33" cy="46.5" r="2" fill="#FFF"/>
  <circle cx="49" cy="46.5" r="2" fill="#FFF"/>
  <ellipse cx="40" cy="60" rx="4.5" ry="3.5" fill="#4A4A4A"/>
</svg>'''.replace('{w}', str(w)).replace('{h}', str(h))
    png_data = cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h)
    return Image.open(io.BytesIO(png_data)).convert('RGBA')

def render_ears_png(w=320, h=480):
    """Render just the ears as separate PNG to composite on top of tail."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 120" width="{w}" height="{h}">
  <ellipse cx="24" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.75"/>
  <ellipse cx="56" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.75"/>
</svg>""".replace('{w}', str(w)).replace('{h}', str(h))
    png_data = cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h)
    return Image.open(io.BytesIO(png_data)).convert('RGBA')


# Pre-render at video init
_tail_img = None
_rejji_img = None
_ears_img = None

def init_assets(profiles):
    global _tail_img, _rejji_img
    dom = profiles[0]
    sec = profiles[1] if len(profiles) > 1 else dom
    dom_hex = '#{:02x}{:02x}{:02x}'.format(*dom['color'])
    sec_hex = '#{:02x}{:02x}{:02x}'.format(*sec['color'])
    _tail_img = render_tail_png(dom_hex, sec_hex, w=400, h=500)
    _rejji_img = render_rejji_png(w=320, h=480)
    global _ears_img
    _ears_img = render_ears_png(w=320, h=480)
    print(f"  Assets: tail {_tail_img.size}, rejji {_rejji_img.size}, ears {_ears_img.size}")

# ═══════════════════════════════════════════════════════════
# DRAWING HELPERS
# ═══════════════════════════════════════════════════════════

def text_c(draw,text,y,font,fill):
    bb=draw.textbbox((0,0),text,font=font)
    draw.text(((W-bb[2]+bb[0])//2,y),text,font=font,fill=fill)

def draw_dot(draw,cx,cy,r,fc,sc):
    if r<1: return
    draw.ellipse([cx-r,cy-r,cx+r,cy+r],fill=fc,outline=sc,width=1)

def draw_bg(img):
    draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,W,H],fill=BG_CREAM)
    for y in range(min(420,H)):
        t=y/420
        c=lerp_color(BG_BLUE,BG_CREAM,ease_io(t))
        draw.line([(0,y),(W,y)],fill=c)
    draw.rectangle([0,0,W,4],fill=PERSIMMON)

def draw_glow(img,cx,cy,r,s):
    ov=Image.new('RGBA',(W,H),(0,0,0,0))
    od=ImageDraw.Draw(ov)
    for i in range(20,0,-1):
        ri=int(r*i/20)
        a=int(s*(1-i/20)*255)
        od.ellipse([cx-ri,cy-ri,cx+ri,cy+ri],fill=BG_BLUE+(a,))
    img.paste(Image.alpha_composite(img.convert('RGBA'),ov).convert('RGB'))

def draw_wm(draw,y,font_size,alpha=1.0):
    font=gf(font_size,bold=True)
    parts=[('Quir',INK),('re',PERSIMMON),('ly',INK)]
    tw=sum(draw.textbbox((0,0),p[0],font=font)[2]-draw.textbbox((0,0),p[0],font=font)[0] for p in parts)
    x=(W-tw)//2
    for text,color in parts:
        c=lerp_color(BG_CREAM,color,alpha)
        draw.text((x,y),text,font=font,fill=c)
        x+=draw.textbbox((0,0),text,font=font)[2]-draw.textbbox((0,0),text,font=font)[0]

def draw_cta(draw,y,alpha):
    font=gf(28,bold=True)
    text='Find your voice \u2192'
    bb=draw.textbbox((0,0),text,font=font)
    tw,th=bb[2]-bb[0],bb[3]-bb[1]
    px,py=40,16
    bw,bh=tw+px*2,th+py*2
    bx,by=(W-bw)//2,y
    c=lerp_color(BG_CREAM,PERSIMMON,alpha)
    draw.rounded_rectangle([bx,by,bx+bw,by+bh],radius=bh//2,fill=c)
    tc=lerp_color(BG_CREAM,(255,255,255),alpha)
    draw.text((bx+px,by+py-2),text,font=font,fill=tc)

def composite_sprite(img, sprite, cx, cy, scale, alpha=1.0):
    """Composite a pre-rendered RGBA sprite onto img at given center/scale/alpha."""
    sw = int(sprite.width * scale)
    sh = int(sprite.height * scale)
    if sw < 1 or sh < 1: return
    resized = sprite.resize((sw, sh), Image.LANCZOS)
    if alpha < 1.0:
        # Reduce alpha channel
        r, g, b, a = resized.split()
        a = a.point(lambda x: int(x * alpha))
        resized = Image.merge('RGBA', (r, g, b, a))
    paste_x = cx - sw // 2
    paste_y = cy - sh // 2
    img_rgba = img.convert('RGBA')
    img_rgba.paste(resized, (paste_x, paste_y), resized)
    img.paste(img_rgba.convert('RGB'))

# ═══════════════════════════════════════════════════════════
# FRAME GENERATION
# ═══════════════════════════════════════════════════════════

def generate_frame(fnum, profiles, username, tagline):
    t = fnum / TOTAL_FRAMES
    img = Image.new('RGB', (W, H), BG_CREAM)
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, int(H * 0.47)
    n = len(profiles)

    # === TIMELINE ===
    # 0.00-0.12: Wordmark fades in on cream
    # 0.12-0.22: Wordmark holds
    # 0.22-0.28: Wordmark fades out
    # 0.28+:     Full scene

    if t < 0.28:
        fade_in = ease_out(t / 0.12)
        fade_out = 1 - ease_in((t - 0.22) / 0.06) if t >= 0.22 else 1
        wm_a = max(0, min(fade_in, fade_out))
        if wm_a > 0.01:
            draw_wm(draw, H//2 - 60, 80, wm_a)
            sf = gif(26)
            sc = lerp_color(BG_CREAM, MUTED, wm_a)
            text_c(draw, 'Writing Voice, Examined.', H//2 + 30, sf, sc)
        return img

    # Scene phase (0.28 → 1.0 mapped to 0 → 1)
    st = (t - 0.28) / 0.72
    draw_bg(img)

    rejji_e = ease_out(st / 0.18)
    line_e = ease_out((st - 0.10) / 0.28) if st >= 0.10 else 0
    label_e = ease_out((st - 0.30) / 0.20) if st >= 0.30 else 0
    title_e = ease_out((st - 0.44) / 0.14) if st >= 0.44 else 0
    bwm_e = ease_out((st - 0.60) / 0.10) if st >= 0.60 else 0
    cta_e = ease_out((st - 0.74) / 0.12) if st >= 0.74 else 0

    if rejji_e > 0.02:
        draw_glow(img, cx, cy, 250, 0.3 * rejji_e)

    draw = ImageDraw.Draw(img)

    # === LINES (drawn first — underneath tail and Rejji) ===
    if line_e > 0.02:
        bl, me = 160, 185
        for i in range(n):
            p = profiles[i]
            ang = -math.pi/2 + (i/n)*math.pi*2
            nm = p['score']/100
            dl = i * 0.05
            le = ease_out(min(1, max(0, (line_e - dl) / 0.5)))
            ml = bl + nm * me
            ln = ml * le
            # Dominant at top can start closer (more room above Rejji's head)
            # Others stay at 175 to clear body/tail
            ir = 145 if p['is_dom'] else 175
            ca, sa = math.cos(ang), math.sin(ang)
            # Dominant line ends 30px shorter to clear label
            draw_ln = ln - 30 if p['is_dom'] else ln
            if draw_ln > ir + 10:
                x1, y1 = int(cx+ca*ir), int(cy+sa*ir)
                x2, y2 = int(cx+ca*draw_ln), int(cy+sa*draw_ln)
                lw = max(1, int(2+nm*2))
                draw.line([(x1,y1),(x2,y2)], fill=p['color'], width=lw)
            else:
                x2, y2 = int(cx+ca*max(draw_ln, ir+15)), int(cy+sa*max(draw_ln, ir+15))
            dr = max(1, int((4+nm*9)*le))
            draw_dot(draw, x2, y2, dr, p['color'], p['dark'])

    # === TAIL (SVG-rendered, over lines, under body) ===
    if rejji_e > 0.05 and _tail_img:
        # Tail SVG viewBox is 0,0,100,130 — anchor point is bottom-center
        # At scale 1.0, tail is 400x500. We scale with rejji_e
        ts = rejji_e * 0.8
        # Tail center offset: in SVG coords, tail center is roughly (68, 60)
        # Rejji center is at (40, 65) in SVG coords
        # Offset tail to the right and up from Rejji center
        tail_cx = cx + int(44 * rejji_e)
        tail_cy = cy - int(32 * rejji_e)
        composite_sprite(img, _tail_img, tail_cx, tail_cy, ts, rejji_e)
        draw = ImageDraw.Draw(img)

    # === EARS (on top of tail, under body) ===
    if rejji_e > 0.05 and _ears_img:
        composite_sprite(img, _ears_img, cx, cy, rejji_e * 0.8, rejji_e)

    # === REJJI (SVG-rendered, on top of everything) ===
    if rejji_e > 0.05 and _rejji_img:
        composite_sprite(img, _rejji_img, cx, cy, rejji_e * 0.8, rejji_e)

    # === EARS again (on top of everything to ensure visible) ===
    if rejji_e > 0.05 and _ears_img:
        composite_sprite(img, _ears_img, cx, cy, rejji_e * 0.8, rejji_e * 0.9)
        draw = ImageDraw.Draw(img)

    # === LABELS ===
    if label_e > 0.05:
        bl, me = 160, 185
        for i in range(n):
            p = profiles[i]
            ang = -math.pi/2 + (i/n)*math.pi*2
            nm = p['score']/100
            ml = bl + nm*me
            dr = 4 + nm*9
            ca, sa = math.cos(ang), math.sin(ang)
            lr = ml + dr + 30
            lx, ly = cx+ca*lr, cy+sa*lr
            dl = i*0.04
            le = min(1, max(0, (label_e-dl)/0.5))
            if le < 0.05: continue

            f = gf(26 if p['is_dom'] else 21, bold=p['is_dom'])
            col = lerp_color(BG_CREAM, p['dark'] if p['is_dom'] else INK, le)
            sf = gf(17, bold=True)
            st_t = str(p['score'])
            # Measure both
            nbb = draw.textbbox((0,0), p['label'], font=f)
            ntw = nbb[2] - nbb[0]
            sbb = draw.textbbox((0,0), st_t, font=sf)
            stw = sbb[2] - sbb[0]
            # Align: right for left side, left for right side, center for top/bottom
            if ca < -0.15:
                ntx = int(lx - ntw)
                stx = int(lx - stw)
            elif ca > 0.15:
                ntx = int(lx)
                stx = int(lx)
            else:
                ntx = int(lx - ntw // 2)
                stx = int(lx - stw // 2)
            # Name at -12, score at +12 — consistent 24px gap
            # Dominant label raised extra; wider gap between name and score
            y_off = -24 if p['is_dom'] else 0
            score_gap = 16 if p['is_dom'] else 10
            name_y = int(ly) - 14 + y_off
            # Never overlap title area (subtitle ends ~y=135)
            if name_y < 145:
                name_y = 145
            draw.text((ntx, name_y), p['label'], font=f, fill=col)
            draw.text((stx, name_y + 24 + (6 if p['is_dom'] else 0)), st_t, font=sf, fill=lerp_color(BG_CREAM, p['dark'], le))

    # === TITLE ===
    if title_e > 0.05:
        tf = gf(48,bold=True)
        tc = lerp_color(BG_CREAM,PERSIMMON,title_e)
        text_c(draw,f"{username}\u2019s Writing Voice",50,tf,tc)
        if tagline:
            sf = gif(24)
            sc = lerp_color(BG_CREAM,MUTED,title_e)
            text_c(draw,tagline,108,sf,sc)

    # === BOTTOM WORDMARK ===
    if bwm_e > 0.05:
        draw_wm(draw,H-90,42,bwm_e)
        sf = gif(18)
        sc = lerp_color(BG_CREAM,MUTED,bwm_e)
        text_c(draw,'Find your voice. Feed your curiosity.',H-48,sf,sc)

    # === CTA BUTTON ===
    if cta_e > 0.05:
        draw_cta(draw,H-160,cta_e)

    return img

# ═══════════════════════════════════════════════════════════
# ENCODING
# ═══════════════════════════════════════════════════════════

def generate_video(username,profile,stance,tagline,scores,output_path):
    profiles = build_profiles(scores,profile)
    print(f"Generating {TOTAL_FRAMES} frames at {W}x{H}...")
    init_assets(profiles)
    cmd = [
        'ffmpeg','-y','-f','rawvideo','-vcodec','rawvideo',
        '-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),
        '-i','-','-c:v','libx264','-preset','medium','-crf','23',
        '-pix_fmt','yuv420p','-movflags','+faststart',output_path
    ]
    proc = subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
    for f in range(TOTAL_FRAMES):
        img = generate_frame(f,profiles,username,tagline)
        proc.stdin.write(img.tobytes())
        if f % 30 == 0:
            print(f"  Frame {f}/{TOTAL_FRAMES} ({f*100//TOTAL_FRAMES}%)")
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        print('ffmpeg error'); return False
    sz = os.path.getsize(output_path)
    print(f"Done: {output_path} ({sz} bytes, {sz/1024/1024:.1f} MB)")
    return True

if __name__ == '__main__':
    import argparse
    pa = argparse.ArgumentParser()
    pa.add_argument('--username',required=True)
    pa.add_argument('--profile',required=True)
    pa.add_argument('--stance',default='balanced')
    pa.add_argument('--tagline',default='')
    pa.add_argument('--scores',required=True)
    pa.add_argument('--output',default='/tmp/voice-video.mp4')
    a = pa.parse_args()
    ok = generate_video(a.username,a.profile,a.stance,a.tagline,json.loads(a.scores),a.output)
    sys.exit(0 if ok else 1)
