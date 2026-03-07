"""OG image generator — screenshots the live /voice/{slug} page via puppeteer."""
import os, re, subprocess, tempfile
from pathlib import Path

OG_DIR = "/home/quirrely/quirrely.ca/og/users"
SCRIPT  = "/opt/quirrely/quirrely_v313_integrated/backend/og_screenshot.js"
os.makedirs(OG_DIR, exist_ok=True)

def generate_og_image(slug, name, profile, scores,
                      total_words=0, total_analyses=0, stance=None):
    slug = re.sub(r"[^a-z0-9\-]", "", (slug or "").lower())[:30]
    if not slug:
        raise ValueError("Invalid slug")
    out = os.path.join(OG_DIR, f"{slug}.png")
    result = subprocess.run(
        ["node", SCRIPT, slug, out],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0 or not os.path.exists(out):
        raise RuntimeError(f"Screenshot failed: {result.stderr}")
    return out
