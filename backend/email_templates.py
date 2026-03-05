#!/usr/bin/env python3
"""
QUIRRELY EMAIL SERVICE
Complete email service for partnership invitations and notifications.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_partnership_invitation_email(
    target_name: str,
    initiator_name: str,
    partnership_name: str,
    partnership_type: str,
    partnership_intention: str,
    invitation_token: str
) -> Dict[str, str]:
    """Create partnership invitation email content."""
    
    # Partnership type descriptions
    partnership_descriptions = {
        'heart': 'Life\'s most meaningful moments - wedding vows, family stories, letters to children',
        'growth': 'Supporting each other\'s journey - mentorship, accountability, creative challenges',
        'professional': 'Authentic voice at work - presentations, proposals, performance reviews', 
        'creative': 'Playing with possibilities together - fiction, poetry, blogs, creative experiments',
        'life': 'Getting important things done - family planning, community projects, legacy documentation'
    }
    
    partnership_desc = partnership_descriptions.get(partnership_type, 'A meaningful writing collaboration')
    base_url = os.environ.get('BASE_URL', 'https://quirrely.com')
    
    subject = f"💕 {initiator_name} invites you to write together on Quirrely"
    
    text_content = f"""
Hi {target_name},

{initiator_name} would like to start a writing partnership with you on Quirrely!

Partnership: "{partnership_name}"
Type: {partnership_type.title()} Partnership
Description: {partnership_desc}

{f'About this partnership: {partnership_intention}' if partnership_intention else ''}

What you'll get:
• 25,000 word shared creative space (contributed equally by both partners)
• 12,500 words for your own solo discoveries
• A safe, supportive space for vulnerable creative expression
• Growth tracking and celebration of your writing journey

Accept your invitation: {base_url}/partnerships/accept/{invitation_token}

This invitation will expire in 7 days.

Happy writing!
The Quirrely Team
"""
    
    return {
        "subject": subject,
        "text": text_content.strip(),
        "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Partnership Invitation</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #f97316; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: white; padding: 20px; border: 1px solid #ddd; }}
        .button {{ background: #f97316; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💕 Partnership Invitation</h1>
        </div>
        <div class="content">
            <p>Hi {target_name},</p>
            <p><strong>{initiator_name}</strong> would like to start a writing partnership with you on Quirrely!</p>
            <h3>"{partnership_name}"</h3>
            <p><em>{partnership_type.title()} Partnership - {partnership_desc}</em></p>
            {f'<p><strong>Their vision:</strong> {partnership_intention}</p>' if partnership_intention else ''}
            <h3>What you'll get:</h3>
            <ul>
                <li>25,000 word shared creative space</li>
                <li>12,500 words for your own discoveries</li>
                <li>Safe, supportive writing environment</li>
                <li>Growth tracking and celebration</li>
            </ul>
            <p style="text-align: center;">
                <a href="{base_url}/partnerships/accept/{invitation_token}" class="button">
                    Accept Partnership Invitation
                </a>
            </p>
            <p><small>This invitation expires in 7 days.</small></p>
        </div>
    </div>
</body>
</html>
        """
    }

async def send_partnership_invitation_email(
    target_email: str,
    target_name: str,
    initiator_name: str,
    partnership_name: str,
    partnership_type: str,
    partnership_intention: str,
    invitation_token: str
) -> bool:
    """Send partnership invitation email."""
    
    email_content = get_partnership_invitation_email(
        target_name, initiator_name, partnership_name,
        partnership_type, partnership_intention, invitation_token
    )
    
    # For now, log the email (implement actual sending later)
    logger.info(f"""
PARTNERSHIP INVITATION EMAIL
To: {target_email} ({target_name})
From: {initiator_name}
Subject: {email_content['subject']}

{email_content['text']}
""")
    
    return True