"""Generate personalized OG share images for user profiles."""
from PIL import Image, ImageDraw, ImageFont
import os, re

OG_DIR = "/home/quirrely/quirrely.ca/og/users"
os.makedirs(OG_DIR, exist_ok=True)

PROFILE_COLORS = {
    "ASSERTIVE":"#E74C3C","MINIMAL":"#3498DB","POETIC":"#9B59B6",
    "DENSE":"#2C3E50","CONVERSATIONAL":"#E67E22","FORMAL":"#1ABC9C",
    "INTERROGATIVE":"#F39C12","HEDGED":"#7F8C8D","PARALLEL":"#2ECC71",
    "LONGFORM":"#8E44AD"
}
PROFILE_DESC = {
    "ASSERTIVE":"Bold & Direct","MINIMAL":"Clean & Precise",
    "POETIC":"Lyrical & Evocative","DENSE":"Complex & Layered",
    "CONVERSATIONAL":"Warm & Natural","FORMAL":"Polished & Authoritative",
    "INTERROGATIVE":"Curious & Exploratory","HEDGED":"Nuanced & Qualifying",
    "PARALLEL":"Rhythmic & Balanced","LONGFORM":"Expansive & Immersive"
}
PROFILE_TITLES = {
    "ASSERTIVE":"The Direct Voice","MINIMAL":"The Quiet Observer",
    "POETIC":"The Fragment Weaver","DENSE":"The Layered Thinker",
    "CONVERSATIONAL":"The Voice in the Room","FORMAL":"The Polished Pen",
    "INTERROGATIVE":"The Questioner","HEDGED":"The Careful Scholar",
    "PARALLEL":"The Pattern Maker","LONGFORM":"The Sentence Builder"
}

def hex_rgb(h):
    h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))

def draw_squirrel(draw, cx, cy, s=1.0):
    cr=(255,254,249); st=(224,219,213); co=(255,107,107)
    ac=(232,90,90); at=(212,80,74); dk=(26,26,26); ns=(74,74,74)
    pts=[(cx-2*s,cy+42*s),(cx-25*s,cy+48*s),(cx-30*s,cy+28*s),
         (cx-26*s,cy+8*s),(cx-14*s,cy-12*s),(cx-14*s,cy+8*s)]
    draw.polygon(pts, fill=cr, outline=st)
    draw.ellipse([cx-18*s,cy+18*s,cx+18*s,cy+48*s], fill=cr, outline=st)
    draw.ellipse([cx-20*s,cy+30*s,cx-8*s,cy+40*s], fill=cr, outline=st)
    draw.ellipse([cx+8*s,cy+30*s,cx+20*s,cy+40*s], fill=cr, outline=st)
    draw.ellipse([cx-12*s,cy+40*s,cx-2*s,cy+48*s], fill=cr)
    draw.ellipse([cx+2*s,cy+40*s,cx+12*s,cy+48*s], fill=cr)
    pts_a=[(cx-7*s,cy+28*s),(cx-8*s,cy+40*s),(cx,cy+46*s),
           (cx+8*s,cy+40*s),(cx+7*s,cy+28*s)]
    draw.polygon(pts_a, fill=co)
    draw.ellipse([cx-7*s,cy+24*s,cx+7*s,cy+32*s], fill=ac)
    draw.rectangle([cx-1*s,cy+20*s,cx+1*s,cy+25*s], fill=at)
    draw.ellipse([cx-18*s,cy-8*s,cx+18*s,cy+22*s], fill=cr, outline=st)
    draw.ellipse([cx-16*s,cy-18*s,cx-4*s,cy+2*s], fill=(212,204,196))
    draw.ellipse([cx+4*s,cy-18*s,cx+16*s,cy+2*s], fill=(212,204,196))
    draw.ellipse([cx-9*s,cy+2*s,cx-2*s,cy+12*s], fill=dk)
    draw.ellipse([cx+2*s,cy+2*s,cx+9*s,cy+12*s], fill=dk)
    draw.ellipse([cx-7*s,cy+4*s,cx-4*s,cy+7*s], fill=(255,255,255))
    draw.ellipse([cx+4*s,cy+4*s,cx+7*s,cy+7*s], fill=(255,255,255))
    draw.ellipse([cx-4*s,cy+14*s,cx+4*s,cy+19*s], fill=ns)


def generate_og_image(slug, name, profile, scores, total_words=0, total_analyses=0):
    slug = re.sub(r'[^a-z0-9\-]', '', slug.lower())[:30]
    if not slug:
        raise ValueError("Invalid slug")

    # Render at 2x for retina clarity, then downscale
    S = 2
    W, H = 1200 * S, 630 * S
    profile = (profile or "UNKNOWN").upper()
    color = hex_rgb(PROFILE_COLORS.get(profile, "#666666"))
    bg = hex_rgb("#FFFBF5")
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    try:
        fb  = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 88)
        fm  = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", 48)
        fs  = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", 38)
        fbr = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 52)
        fti = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", 42)
    except:
        fb = fm = fs = fbr = fti = ImageFont.load_default()

    # Card background
    draw.rounded_rectangle([60, 60, W-60, H-60], radius=48, fill=(255, 255, 255))
    # Top accent bar
    draw.rounded_rectangle([60, 60, W-60, 76], radius=8, fill=color)

    # Squirrel (right side)
    draw_squirrel(draw, 1960, 240, s=5.0)

    # Brand "Quirrely"
    bx, by = 140, 110
    draw.text((bx, by), "Quir", fill=(45, 52, 54), font=fbr)
    qw = draw.textlength("Quir", font=fbr)
    draw.text((bx + qw, by), "re", fill=(255, 107, 107), font=fbr)
    rw = draw.textlength("re", font=fbr)
    draw.text((bx + qw + rw, by), "ly", fill=(45, 52, 54), font=fbr)

    # User name (large)
    draw.text((140, 200), name, fill=(45, 52, 54), font=fb)

    # Voice title (e.g. "The Sentence Builder") — italic style
    vtitle = PROFILE_TITLES.get(profile, "")
    if vtitle:
        draw.text((140, 310), vtitle, fill=(120, 120, 120), font=fti)

    # Profile badge pill
    desc = PROFILE_DESC.get(profile, profile)
    bt = profile + "  \u00b7  " + desc
    tw_ = draw.textlength(bt, font=fm)
    badge_y = 380
    draw.rounded_rectangle([132, badge_y, 160 + tw_ + 56, badge_y + 72], radius=36, fill=color)
    draw.text((160, badge_y + 12), bt, fill=(255, 255, 255), font=fm)

    # Acorn fill meters (top 5)
    SCORE_COLORS = {
        "assertive":(255,107,107),"minimal":(91,155,213),"poetic":(155,89,182),
        "analytical":(78,205,196),"conversational":(255,179,71),"provocative":(231,76,60),
        "reflective":(107,203,119),"technical":(52,152,219),"narrative":(243,156,18),
        "persuasive":(230,126,34),"dense":(78,205,196),"formal":(26,188,156),
        "interrogative":(243,156,18),"hedged":(127,140,141),"parallel":(46,204,113),
        "longform":(142,68,173),"parenthetical":(230,126,34)
    }
    SHORT_LABELS = {
        "interrogative":"Interrog.","conversational":"Convo",
        "parenthetical":"Parens","analytical":"Analytical"
    }

    top5 = sorted(scores.items(), key=lambda x: x[1] or 0, reverse=True)[:5] if scores else []
    n5 = len(top5)
    total_w = 1400
    slot_w = total_w // max(n5, 1)
    ax0 = 140
    ay = 500
    ah = 190

    for i, (sn, sv) in enumerate(top5):
        pct = min(int(float(sv)), 100) if sv else 0
        sc = SCORE_COLORS.get(sn.lower(), color)
        cx = ax0 + i * slot_w + slot_w // 2

        # Stem
        draw.rounded_rectangle([cx-6, ay, cx+6, ay+20], radius=4, fill=(212,204,196))
        # Cap
        draw.ellipse([cx-44, ay+16, cx+44, ay+44], fill=(232,228,223), outline=(224,219,213))
        # Body (teardrop)
        body_top = ay + 40
        body_bot = ay + ah
        body_mid = body_top + int((body_bot - body_top) * 0.55)

        # Background body
        draw.ellipse([cx-48, body_top, cx+48, body_mid+32], fill=(240,238,235), outline=(224,219,213))
        draw.polygon([(cx-34, body_mid+8), (cx, body_bot), (cx+34, body_mid+8)], fill=(240,238,235))
        draw.line([(cx-34, body_mid+8), (cx, body_bot)], fill=(224,219,213), width=2)
        draw.line([(cx+34, body_mid+8), (cx, body_bot)], fill=(224,219,213), width=2)

        # Filled portion
        fill_h = int((body_bot - body_top) * pct / 100)
        if fill_h > 0:
            fill_top = body_bot - fill_h
            if fill_top < body_mid + 32:
                draw.ellipse([cx-47, max(fill_top, body_top+1), cx+47, body_mid+31], fill=sc)
            tri_top = max(fill_top, body_mid+8)
            if tri_top < body_bot:
                ratio_t = (tri_top - (body_mid+8)) / (body_bot - (body_mid+8)) if body_bot > body_mid+8 else 0
                w_top = int(34 * (1 - ratio_t))
                draw.polygon([(cx-w_top, tri_top), (cx, body_bot), (cx+w_top, tri_top)], fill=sc)

        # Score (bold, colored)
        score_y = body_bot + 16
        st_ = str(pct)
        stw = draw.textlength(st_, font=fbr)
        draw.text((cx - stw/2, score_y), st_, fill=sc, font=fbr)

        # Label
        label = SHORT_LABELS.get(sn.lower(), sn.capitalize())
        lw = draw.textlength(label, font=fs)
        draw.text((cx - lw/2, score_y + 58), label, fill=(120,120,120), font=fs)

    # Stats
    draw.text((140, 860), f"{total_words:,} words", fill=(150, 150, 150), font=fm)
    draw.text((560, 860), f"{total_analyses} analyses", fill=(150, 150, 150), font=fm)

    # CTA button
    draw.rounded_rectangle([120, 1000, 1040, 1110], radius=54, fill=hex_rgb("#FF6B6B"))
    draw.text((164, 1020), "Discover your voice at quirrely.ca", fill=(255, 255, 255), font=fs)

    # Downscale 2x → 1x with high-quality resampling
    img = img.resize((1200, 630), Image.LANCZOS)

    path = os.path.join(OG_DIR, f"{slug}.png")
    img.save(path, "PNG", optimize=True)
    return path
