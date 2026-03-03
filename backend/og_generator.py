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
    # Sanitize slug to prevent path traversal
    slug = re.sub(r'[^a-z0-9\-]', '', slug.lower())[:30]
    if not slug:
        raise ValueError("Invalid slug")
    W, H = 1200, 630
    profile = (profile or "UNKNOWN").upper()
    color = hex_rgb(PROFILE_COLORS.get(profile, "#666666"))
    bg = hex_rgb("#FFFBF5")
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    try:
        fb = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 44)
        fm = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", 26)
        fs = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", 20)
        fbr = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 28)
    except:
        fb = fm = fs = fbr = ImageFont.load_default()
    # Card
    draw.rounded_rectangle([30, 30, 1170, 600], radius=24, fill=(255, 255, 255))
    # Top accent bar
    draw.rounded_rectangle([30, 30, 1170, 38], radius=4, fill=color)
    # Squirrel (right side)
    draw_squirrel(draw, 980, 120, s=2.5)
    # Brand "Quirrely"
    bx, by = 70, 55
    draw.text((bx, by), "Quir", fill=(45, 52, 54), font=fbr)
    qw = draw.textlength("Quir", font=fbr)
    draw.text((bx + qw, by), "re", fill=(255, 107, 107), font=fbr)
    rw = draw.textlength("re", font=fbr)
    draw.text((bx + qw + rw, by), "ly", fill=(45, 52, 54), font=fbr)
    # User name
    draw.text((70, 115), name, fill=(45, 52, 54), font=fb)
    # Profile badge
    desc = PROFILE_DESC.get(profile, profile)
    bt = profile + "  \u00b7  " + desc
    tw_ = draw.textlength(bt, font=fm)
    draw.rounded_rectangle([66, 180, 76 + tw_ + 28, 228], radius=24, fill=color)
    draw.text((80, 190), bt, fill=(255, 255, 255), font=fm)
    # Score bars (top 3)
    top3 = sorted(scores.items(), key=lambda x: x[1] or 0, reverse=True)[:3] if scores else []
    by_ = 265
    bw = 420
    for sn, sv in top3:
        pct = min(int(float(sv)), 100) if sv else 0
        draw.text((70, by_), sn.capitalize(), fill=(120, 120, 120), font=fs)
        x0 = 240
        draw.rounded_rectangle([x0, by_ + 3, x0 + bw, by_ + 23], radius=10, fill=(240, 238, 235))
        fw = max(int(bw * pct / 100), 6)
        draw.rounded_rectangle([x0, by_ + 3, x0 + fw, by_ + 23], radius=10, fill=color)
        draw.text((x0 + bw + 14, by_), str(pct), fill=(80, 80, 80), font=fs)
        by_ += 44
    # Stats
    draw.text((70, 430), f"{total_words:,} words", fill=(150, 150, 150), font=fm)
    draw.text((280, 430), f"{total_analyses} analyses", fill=(150, 150, 150), font=fm)
    # CTA button
    draw.rounded_rectangle([60, 500, 520, 555], radius=27, fill=hex_rgb("#FF6B6B"))
    draw.text((82, 510), "Discover your voice at quirrely.ca", fill=(255, 255, 255), font=fs)
    path = os.path.join(OG_DIR, f"{slug}.png")
    img.save(path, "PNG", optimize=True)
    return path
