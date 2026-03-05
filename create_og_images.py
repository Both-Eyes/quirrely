#!/usr/bin/env python3
"""
Create 40 OG images for Quirrely blog posts.
Generates 1200x630px social sharing images for all profile + stance combinations.
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_og_images():
    """Create all 40 OG images for blog posts."""
    
    # Profile and stance data with colors and characteristics
    profiles = {
        'assertive': {
            'color': '#FF6B6B',
            'icon': '🎯',
            'title': 'ASSERTIVE',
            'tagline': 'Direct & Confident'
        },
        'minimal': {
            'color': '#4ECDC4', 
            'icon': '🌿',
            'title': 'MINIMAL',
            'tagline': 'Less Is More'
        },
        'poetic': {
            'color': '#A29BFE',
            'icon': '🌊', 
            'title': 'POETIC',
            'tagline': 'Lyrical & Flowing'
        },
        'dense': {
            'color': '#6C5CE7',
            'icon': '📚',
            'title': 'DENSE', 
            'tagline': 'Rich & Complex'
        },
        'conversational': {
            'color': '#FDCB6E',
            'icon': '💬',
            'title': 'CONVERSATIONAL',
            'tagline': 'Warm & Direct'
        },
        'formal': {
            'color': '#636E72',
            'icon': '📋',
            'title': 'FORMAL',
            'tagline': 'Professional & Clear'
        },
        'balanced': {
            'color': '#74B9FF',
            'icon': '⚖️',
            'title': 'BALANCED', 
            'tagline': 'Thoughtful & Fair'
        },
        'longform': {
            'color': '#FD79A8',
            'icon': '📖',
            'title': 'LONGFORM',
            'tagline': 'Deep & Thorough'
        },
        'interrogative': {
            'color': '#E17055',
            'icon': '❓',
            'title': 'INTERROGATIVE',
            'tagline': 'Curious & Probing'
        },
        'hedged': {
            'color': '#00B894',
            'icon': '🤔',
            'title': 'HEDGED',
            'tagline': 'Careful & Nuanced'
        }
    }
    
    stances = {
        'open': {
            'symbol': '⭕',
            'description': 'OPEN',
            'characteristic': 'Receptive to challenge'
        },
        'closed': {
            'symbol': '🔒',
            'description': 'CLOSED', 
            'characteristic': 'Decisive & definitive'
        },
        'balanced': {
            'symbol': '⚖️',
            'description': 'BALANCED',
            'characteristic': 'Considers all sides'
        },
        'contradictory': {
            'symbol': '⚡',
            'description': 'CONTRADICTORY',
            'characteristic': 'Embraces paradox'
        }
    }
    
    # Priority order (top 5 first)
    priority_posts = [
        ('assertive', 'open'),      # 1,247 views
        ('minimal', 'closed'),      # 987 views  
        ('conversational', 'balanced'), # 834 views
        ('poetic', 'contradictory'),    # 756 views
        ('dense', 'open')          # Next highest
    ]
    
    # Create output directory
    output_dir = Path('/root/quirrely_v313_integrated/assets/og')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎨 Creating OG images for Quirrely blog posts")
    print("=" * 50)
    
    # Create priority images first
    print("\n🚀 Creating top 5 priority images...")
    for profile, stance in priority_posts:
        create_single_og_image(profile, stance, profiles, stances, output_dir, priority=True)
    
    # Create remaining images
    print("\n📦 Creating remaining 35 images...")
    count = 0
    for profile_key, profile_data in profiles.items():
        for stance_key, stance_data in stances.items():
            if (profile_key, stance_key) not in priority_posts:
                create_single_og_image(profile_key, stance_key, profiles, stances, output_dir)
                count += 1
    
    print(f"\n✅ Created all 40 OG images successfully!")
    print(f"📁 Images saved to: {output_dir}")
    print(f"🔗 Ready for social sharing optimization")

def create_single_og_image(profile_key, stance_key, profiles, stances, output_dir, priority=False):
    """Create a single OG image for a profile + stance combination."""
    
    # Image dimensions (Facebook/LinkedIn/Twitter optimized)
    width, height = 1200, 630
    
    # Get profile and stance data
    profile = profiles[profile_key]
    stance = stances[stance_key]
    
    # Create base image with gradient background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Convert hex color to RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    profile_color = hex_to_rgb(profile['color'])
    
    # Create gradient background
    for y in range(height):
        # Gradient from profile color to lighter version
        ratio = y / height
        r = int(profile_color[0] + (255 - profile_color[0]) * ratio * 0.3)
        g = int(profile_color[1] + (255 - profile_color[1]) * ratio * 0.3) 
        b = int(profile_color[2] + (255 - profile_color[2]) * ratio * 0.3)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add semi-transparent overlay for text readability
    overlay = Image.new('RGBA', (width, height), (255, 255, 255, 40))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to load system fonts (will fall back to default if not available)
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
            tagline_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
            brand_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        except:
            # Fallback to default font with size
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            tagline_font = ImageFont.load_default()
            brand_font = ImageFont.load_default()
    except:
        # Final fallback
        title_font = subtitle_font = tagline_font = brand_font = ImageFont.load_default()
    
    # Text colors
    text_color = (255, 255, 255)  # White text
    accent_color = (0, 0, 0, 100)  # Semi-transparent black
    
    # Brand positioning
    brand_text = "QUIRRELY"
    brand_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
    brand_width = brand_bbox[2] - brand_bbox[0]
    draw.text((width - brand_width - 50, 40), brand_text, fill=text_color, font=brand_font)
    
    # Profile icon and name
    icon_text = profile['icon']
    icon_bbox = draw.textbbox((0, 0), icon_text, font=title_font) 
    icon_width = icon_bbox[2] - icon_bbox[0]
    draw.text((100, 120), icon_text, fill=text_color, font=title_font)
    
    # Profile title
    profile_title = profile['title']
    title_bbox = draw.textbbox((0, 0), profile_title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text((100 + icon_width + 30, 140), profile_title, fill=text_color, font=title_font)
    
    # Stance information
    stance_symbol = stance['symbol']
    stance_text = f"+ {stance['description']}"
    
    # Position stance below profile
    draw.text((120, 230), stance_symbol, fill=text_color, font=subtitle_font)
    stance_bbox = draw.textbbox((0, 0), stance_text, font=subtitle_font)
    draw.text((180, 240), stance_text, fill=text_color, font=subtitle_font)
    
    # Main tagline
    main_tagline = f"How {profile['title'].title()} + {stance['description'].title()} Writers Write"
    
    # Word wrap the tagline if too long
    if len(main_tagline) > 45:
        words = main_tagline.split()
        line1 = " ".join(words[:6])
        line2 = " ".join(words[6:])
        draw.text((100, 340), line1, fill=text_color, font=tagline_font)
        draw.text((100, 385), line2, fill=text_color, font=tagline_font)
    else:
        draw.text((100, 350), main_tagline, fill=text_color, font=tagline_font)
    
    # Characteristic description
    characteristic = stance['characteristic']
    draw.text((100, 480), characteristic, fill=(255, 255, 255, 180), font=tagline_font)
    
    # Decorative elements
    # Add some geometric shapes for visual interest
    accent_color_rgb = tuple(int(c * 0.7) for c in profile_color)
    
    # Circle accent
    draw.ellipse([width-200, height-150, width-50, height-50], fill=(*accent_color_rgb, 80))
    
    # Rectangle accent  
    draw.rectangle([50, height-100, 150, height-20], fill=(*accent_color_rgb, 60))
    
    # Save the image
    filename = f"how-{profile_key}-{stance_key}.png"
    filepath = output_dir / filename
    
    # Convert back to RGB for PNG saving
    if img.mode == 'RGBA':
        img = img.convert('RGB')
        
    img.save(filepath, 'PNG', quality=95, optimize=True)
    
    priority_marker = "⭐" if priority else "  "
    print(f"{priority_marker} Created: {filename}")
    
    return filepath

if __name__ == "__main__":
    create_og_images()
    
    print("\n📊 Next steps:")
    print("1. Test social previews on Twitter/LinkedIn") 
    print("2. Monitor viral coefficient improvement in qstats")
    print("3. Track social shares by platform")
    print("4. Measure impact on blog → signup conversion")
    print("\n🚀 Social sharing optimization complete!")