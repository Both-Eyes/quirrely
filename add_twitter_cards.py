#!/usr/bin/env python3
"""
Add Twitter Card meta tags to all main blog posts.
This script adds the missing Twitter Card metadata to how-*-writers-write.html files.
"""

import os
import re
from pathlib import Path

def add_twitter_cards():
    """Add Twitter Card meta tags to all main blog posts."""
    
    blog_dir = Path("/root/quirrely_v313_integrated/blog")
    
    # Find all main blog post files
    main_posts = list(blog_dir.glob("how-*-writers-write.html"))
    main_posts = [p for p in main_posts if "tracked" not in p.name]
    
    print(f"Found {len(main_posts)} main blog posts to update")
    
    for post_file in main_posts:
        print(f"Processing {post_file.name}...")
        
        # Extract profile and stance from filename
        match = re.match(r"how-(.+)-(.+)-writers-write\.html", post_file.name)
        if not match:
            print(f"  Skipping {post_file.name} - couldn't parse filename")
            continue
            
        profile, stance = match.groups()
        
        # Read current content
        try:
            content = post_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  Error reading {post_file.name}: {e}")
            continue
        
        # Check if Twitter Cards already exist
        if 'twitter:card' in content:
            print(f"  {post_file.name} already has Twitter Cards")
            continue
        
        # Extract title and description from existing meta tags
        title_match = re.search(r'<title>(.+?)</title>', content)
        desc_match = re.search(r'<meta name="description" content="(.+?)"', content)
        
        if not title_match or not desc_match:
            print(f"  Error: Couldn't find title or description in {post_file.name}")
            continue
            
        title = title_match.group(1)
        description = desc_match.group(1)
        
        # Create Twitter Card HTML
        twitter_cards = f'''
  <!-- Twitter Cards -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@quirrelyapp">
  <meta name="twitter:creator" content="@quirrelyapp">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="https://quirrely.com/assets/og/how-{profile}-{stance}.png">'''
        
        # Find insertion point (after existing meta tags, before closing </head>)
        if '<meta property="og:' in content:
            # Insert after Open Graph tags
            insertion_point = content.rfind('</head>')
            if insertion_point != -1:
                new_content = (content[:insertion_point] + 
                              twitter_cards + '\n' +
                              content[insertion_point:])
            else:
                print(f"  Error: Couldn't find </head> tag in {post_file.name}")
                continue
        else:
            # Insert before closing </head>
            insertion_point = content.rfind('</head>')
            if insertion_point != -1:
                new_content = (content[:insertion_point] + 
                              twitter_cards + '\n' +
                              content[insertion_point:])
            else:
                print(f"  Error: Couldn't find </head> tag in {post_file.name}")
                continue
        
        # Write updated content
        try:
            post_file.write_text(new_content, encoding='utf-8')
            print(f"  ✅ Added Twitter Cards to {post_file.name}")
        except Exception as e:
            print(f"  Error writing {post_file.name}: {e}")
            continue
    
    print(f"\nCompleted processing {len(main_posts)} blog posts")

def add_og_images():
    """Add OG image meta tags to main blog posts that don't have them."""
    
    blog_dir = Path("/root/quirrely_v313_integrated/blog")
    main_posts = list(blog_dir.glob("how-*-writers-write.html"))
    main_posts = [p for p in main_posts if "tracked" not in p.name]
    
    print(f"Adding OG images to {len(main_posts)} main blog posts")
    
    for post_file in main_posts:
        print(f"Processing {post_file.name}...")
        
        # Extract profile and stance from filename
        match = re.match(r"how-(.+)-(.+)-writers-write\.html", post_file.name)
        if not match:
            continue
            
        profile, stance = match.groups()
        
        # Read current content
        try:
            content = post_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  Error reading {post_file.name}: {e}")
            continue
        
        # Check if OG image already exists
        if 'og:image' in content:
            print(f"  {post_file.name} already has OG image")
            continue
        
        # Extract title and description
        title_match = re.search(r'<title>(.+?)</title>', content)
        desc_match = re.search(r'<meta name="description" content="(.+?)"', content)
        
        if not title_match or not desc_match:
            print(f"  Error: Couldn't find title or description in {post_file.name}")
            continue
            
        title = title_match.group(1)
        description = desc_match.group(1)
        
        # Create Open Graph HTML
        og_tags = f'''
  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://quirrely.com/blog/{post_file.stem}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="https://quirrely.com/assets/og/how-{profile}-{stance}.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:site_name" content="Quirrely">
  <meta property="article:author" content="Quirrely">
  <meta property="article:tag" content="{profile} writing">
  <meta property="article:tag" content="{stance} voice">'''
        
        # Find insertion point (after canonical link, before closing </head>)
        canonical_match = re.search(r'<link rel="canonical"[^>]*>', content)
        if canonical_match:
            insertion_point = canonical_match.end()
            new_content = (content[:insertion_point] + 
                          og_tags +
                          content[insertion_point:])
        else:
            # Insert before closing </head>
            insertion_point = content.rfind('</head>')
            if insertion_point != -1:
                new_content = (content[:insertion_point] + 
                              og_tags + '\n' +
                              content[insertion_point:])
            else:
                print(f"  Error: Couldn't find </head> tag in {post_file.name}")
                continue
        
        # Write updated content
        try:
            post_file.write_text(new_content, encoding='utf-8')
            print(f"  ✅ Added OG image tags to {post_file.name}")
        except Exception as e:
            print(f"  Error writing {post_file.name}: {e}")
            continue
    
    print(f"\nCompleted adding OG images to {len(main_posts)} blog posts")

if __name__ == "__main__":
    print("🚀 Adding Twitter Cards and OG Images to Quirrely Blog Posts")
    print("=" * 60)
    
    # Add OG images first
    add_og_images()
    print()
    
    # Then add Twitter Cards
    add_twitter_cards()
    
    print("\n✅ SEO optimization complete!")
    print("\nNext steps:")
    print("1. Create the actual OG images at /assets/og/")
    print("2. Test social previews on Twitter/LinkedIn")
    print("3. Monitor viral coefficient in qstats funnel analytics")