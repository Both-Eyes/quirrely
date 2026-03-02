#!/usr/bin/env python3
"""
fix_blog.py — Quirrely Blog Fix Script
Fixes 4 issues across all 51 blog HTML files:
  1. Replaces minimal headers with full nav bar (matching index.html)
  2. Removes all Twitter/X meta tags and JS references
  3. Fixes canonical URLs: quirrely.com -> quirrely.ca
  4. Injects GA4 tag (G-HQ818WM2YB) into <head> where missing
  
Skip: index.html (already correct nav), .js and .md files
"""
import os, re, glob

BLOG_DIR = "/opt/quirrely/quirrely_v313_integrated/blog"

GA4_TAG = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-HQ818WM2YB"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-HQ818WM2YB');</script>"""

# The replacement header — matches index.html exactly
NEW_HEADER = """  <header class="header">
    <div class="header-inner">
      <a href="/" class="logo"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 365 100" width="140" height="41" style="vertical-align: middle;">
      <g transform="translate(5, 2) scale(0.7)">
        <path d="M58 112 Q85 98, 94 62 Q100 26, 74 8 Q50 -8, 42 22 Q38 44, 54 60 Q70 78, 62 100 Q58 110, 58 112" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.4"/>
        <ellipse cx="40" cy="98" rx="22" ry="26" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.4"/>
        <path d="M20 68 Q12 72, 14 80 Q16 86, 24 88 L32 86" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.8"/>
        <path d="M60 68 Q68 72, 66 80 Q64 86, 56 88 L48 86" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.8"/>
        <ellipse cx="28" cy="86" rx="7" ry="5" fill="#FFFEF9"/>
        <ellipse cx="52" cy="86" rx="7" ry="5" fill="#FFFEF9"/>
        <ellipse cx="40" cy="78" rx="9" ry="4" fill="#E85A5A"/><rect x="38.5" y="74" width="3" height="4" rx="1.5" fill="#D4504A"/><path d="M31 78 Q30 94, 40 99 Q50 94, 49 78 Z" fill="#FF6B6B"/>
        <ellipse cx="40" cy="50" rx="22" ry="20" fill="#FFFEF9" stroke="#E0DBD5" stroke-width="1.4"/>
        <ellipse cx="24" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.6"/>
        <ellipse cx="56" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.6"/>
        <ellipse cx="32" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>
        <ellipse cx="48" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/>
        <circle cx="33" cy="46.5" r="2" fill="#FFF"/>
        <circle cx="49" cy="46.5" r="2" fill="#FFF"/>
        <ellipse cx="40" cy="60" rx="4.5" ry="3.5" fill="#4A4A4A"/>
      </g>
      <text x="105" y="62" font-family="system-ui, sans-serif" font-size="46" font-weight="700" fill="#2D3436">Quir<tspan fill="#FF6B6B">rel</tspan><tspan fill="#2D3436" font-style="italic" font-weight="500">ly</tspan></text>
    </svg></a>
      <nav class="nav">
        <a href="/">Home</a>
        <a href="/blog" class="active">Blog</a>
        <a href="/blog/featured">Featured</a>
        <a href="/" class="cta">Take the Test</a>
      </nav>
    </div>
  </header>"""

# CSS for the nav — injected into <style> blocks that don't already have it
NAV_CSS = """
    /* === Quirrely Blog Nav (injected by fix_blog.py) === */
    .header { background: #FFFFFF; border-bottom: 1px solid #E9ECEF; padding: 1rem 2rem; margin: -2rem -2rem 2rem -2rem; }
    .header-inner { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    .header .logo { font-size: 1.25rem; font-weight: 700; text-decoration: none; color: #2D3436; }
    .header .logo span { color: #FF6B6B; }
    .nav { display: flex; gap: 1.5rem; align-items: center; }
    .nav a { text-decoration: none; color: #636E72; font-size: 0.9rem; font-weight: 500; }
    .nav a:hover, .nav a.active { color: #2D3436; }
    .nav .cta { background: #FF6B6B; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 600; }
    .nav .cta:hover { opacity: 0.9; color: white; }
    /* === End Blog Nav CSS === */"""


stats = {"nav_replaced": 0, "nav_injected": 0, "twitter_removed": 0,
         "canonical_fixed": 0, "ga4_added": 0, "skipped": 0, "errors": []}

def fix_file(filepath):
    fname = os.path.basename(filepath)
    
    # Skip index.html (already has correct nav) and non-HTML
    if fname == "index.html":
        stats["skipped"] += 1
        return
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = original = f.read()
    
    # --- FIX 1: Header/Nav replacement ---
    # Pattern A: <header class="header">...</header> (profile posts)
    header_a = re.search(r'(\s*)<header\s+class="header">\s*.*?</header>', content, re.DOTALL)
    # Pattern B: <header>...</header> (SVG-header posts)  
    header_b = re.search(r'(\s*)<header>\s*.*?</header>', content, re.DOTALL)
    
    if header_a:
        content = content[:header_a.start()] + "\n" + NEW_HEADER + "\n" + content[header_a.end():]
        stats["nav_replaced"] += 1
    elif header_b:
        content = content[:header_b.start()] + "\n" + NEW_HEADER + "\n" + content[header_b.end():]
        stats["nav_replaced"] += 1
    else:
        # Pattern C: No <header> tag (featured.html, submit-writing.html)
        # These have <div class="logo"> as first child of <div class="container">
        # Inject header right after <body> or right after opening <div class="container">
        container_match = re.search(r'(<div\s+class="container">)', content)
        if container_match:
            insert_pos = container_match.end()
            content = content[:insert_pos] + "\n" + NEW_HEADER + "\n" + content[insert_pos:]
            stats["nav_injected"] += 1
            # Remove the old standalone <div class="logo">...</div> block
            # Match from <div class="logo"> through the closing </div> that contains the SVG
            old_logo = re.search(r'\s*<div class="logo">.*?</svg>\s*</a>\s*</div>\s*', content, re.DOTALL)
            if not old_logo:
                old_logo = re.search(r'\s*<div class="logo">.*?</svg>\s*</div>\s*', content, re.DOTALL)
            if old_logo:
                # Make sure we don't remove the one inside our NEW_HEADER
                if old_logo.start() > content.find('<!-- === End Blog Nav CSS === -->') if '<!-- === End Blog Nav CSS === -->' in content else old_logo.start() > content.find('</nav>'):
                    content = content[:old_logo.start()] + "\n" + content[old_logo.end():]
        else:
            stats["errors"].append(f"{fname}: No header or container found")

    # --- FIX 2: Remove Twitter/X meta tags ---
    twitter_count_before = len(re.findall(r'twitter', content, re.IGNORECASE))
    # Remove twitter meta tags (full lines)
    content = re.sub(r'\s*<!-- Twitter -->\s*\n', '\n', content)
    content = re.sub(r'\s*<meta\s+name="twitter:[^"]*"[^>]*>\s*\n?', '', content)
    # Remove twitter JS update block in blog-post.html
    content = re.sub(r'\s*// Twitter\s*\n(\s*document\.getElementById\("tw-[^"]*"\)\.setAttribute\([^)]*\);\s*\n)+', '\n', content)
    twitter_count_after = len(re.findall(r'twitter', content, re.IGNORECASE))
    if twitter_count_before > twitter_count_after:
        stats["twitter_removed"] += 1

    # --- FIX 3: Canonical URL fix (.com -> .ca) ---
    if 'quirrely.com' in content:
        # Fix canonical links
        content = re.sub(
            r'(<link\s+rel="canonical"\s+href="https://)quirrely\.com/',
            r'\1quirrely.ca/', content)
        # Fix og:url and any other meta references to quirrely.com
        content = re.sub(
            r'(content="https://)quirrely\.com/',
            r'\1quirrely.ca/', content)
        # Fix schema.org URLs
        content = re.sub(
            r'("url"\s*:\s*"https://)quirrely\.com/',
            r'\1quirrely.ca/', content)
        # Fix any remaining quirrely.com in href attributes (but NOT email addresses)
        content = re.sub(
            r'(href="https://)quirrely\.com/',
            r'\1quirrely.ca/', content)
        if content != original or 'quirrely.com' not in content:
            stats["canonical_fixed"] += 1


    # --- FIX 4: Inject GA4 tag if missing ---
    if "G-HQ818WM2YB" not in content:
        # Insert after <head> or after first <meta charset>
        head_match = re.search(r'(<head>)', content)
        if head_match:
            insert_after = head_match.end()
            content = content[:insert_after] + "\n" + GA4_TAG + "\n" + content[insert_after:]
            stats["ga4_added"] += 1
        else:
            stats["errors"].append(f"{fname}: No <head> tag found for GA4")

    # --- Inject nav CSS into <style> if not already present ---
    if "Quirrely Blog Nav" not in content:
        style_match = re.search(r'(<style[^>]*>)', content)
        if style_match:
            insert_pos = style_match.end()
            content = content[:insert_pos] + NAV_CSS + content[insert_pos:]
        else:
            # No <style> tag — inject one before </head>
            head_close = content.find('</head>')
            if head_close != -1:
                content = content[:head_close] + "  <style>" + NAV_CSS + "\n  </style>\n" + content[head_close:]

    # Write if changed
    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ Fixed: {fname}")
    else:
        print(f"  ⏭️  No changes: {fname}")


def main():
    print("=" * 60)
    print("Quirrely Blog Fix Script")
    print("=" * 60)
    
    html_files = sorted(glob.glob(os.path.join(BLOG_DIR, "*.html")))
    print(f"\nFound {len(html_files)} HTML files in {BLOG_DIR}\n")
    
    for f in html_files:
        try:
            fix_file(f)
        except Exception as e:
            stats["errors"].append(f"{os.path.basename(f)}: {e}")
            print(f"  ❌ Error: {os.path.basename(f)}: {e}")
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    print(f"  Nav replaced:    {stats['nav_replaced']}")
    print(f"  Nav injected:    {stats['nav_injected']}")
    print(f"  Twitter removed: {stats['twitter_removed']}")
    print(f"  Canonicals fixed:{stats['canonical_fixed']}")
    print(f"  GA4 added:       {stats['ga4_added']}")
    print(f"  Skipped:         {stats['skipped']}")
    if stats["errors"]:
        print(f"\n  ERRORS ({len(stats['errors'])}):")
        for e in stats["errors"]:
            print(f"    ⚠️  {e}")
    print("=" * 60)

if __name__ == "__main__":
    main()
