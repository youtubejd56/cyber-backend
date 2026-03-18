#!/usr/bin/env python3
"""
Seed script to create frame rewards for the cyber training platform.
Run this after migrating the database to populate the frames.

Usage:
    cd backend
    python seed_frames.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybertraining.settings')
django.setup()

from api.models import Frame


def seed_frames():
    """Create all the frame rewards"""
    
    frames_data = [
        {
            'frame_id': 'bronze',
            'name': 'Bronze',
            'description': 'Earn 50 points to unlock this frame',
            'required_points': 50,
            'border_color': '#cd7f32',
            'gradient_start': '#cd7f32',
            'gradient_end': '#8b4513',
            'icon': '🥉',
            'is_active': True,
        },
        {
            'frame_id': 'silver',
            'name': 'Silver',
            'description': 'Earn 200 points to unlock this frame',
            'required_points': 200,
            'border_color': '#c0c0c0',
            'gradient_start': '#e8e8e8',
            'gradient_end': '#a8a8a8',
            'icon': '🥈',
            'is_active': True,
        },
        {
            'frame_id': 'gold',
            'name': 'Gold',
            'description': 'Earn 400 points to unlock this frame',
            'required_points': 400,
            'border_color': '#ffd700',
            'gradient_start': '#ffd700',
            'gradient_end': '#ffaa00',
            'icon': '🥇',
            'is_active': True,
        },
        {
            'frame_id': 'platinum',
            'name': 'Platinum',
            'description': 'Earn 600 points to unlock this frame',
            'required_points': 600,
            'border_color': '#e5e4e2',
            'gradient_start': '#e5e4e2',
            'gradient_end': '#8e8e8e',
            'icon': '💎',
            'is_active': True,
        },
        {
            'frame_id': 'diamond',
            'name': 'Diamond',
            'description': 'Earn 800 points to unlock this frame',
            'required_points': 800,
            'border_color': '#4fc3f7',
            'gradient_start': '#b9f2ff',
            'gradient_end': '#4fc3f7',
            'icon': '💠',
            'is_active': True,
        },
        {
            'frame_id': 'conqueror',
            'name': 'Conqueror',
            'description': 'Earn 1000 points to unlock the ultimate frame - PUBG style!',
            'required_points': 1000,
            'border_color': '#ff4060',
            'gradient_start': '#ff4060',
            'gradient_end': '#ffd700',
            'icon': '👑',
            'is_active': True,
        },
    ]
    
    print("🌟 Seeding frame rewards...")
    
    created_count = 0
    updated_count = 0
    
    for frame_data in frames_data:
        frame, created = Frame.objects.update_or_create(
            frame_id=frame_data['frame_id'],
            defaults=frame_data
        )
        
        if created:
            print(f"  ✅ Created: {frame.name} frame ({frame.required_points} pts)")
            created_count += 1
        else:
            print(f"  🔄 Updated: {frame.name} frame ({frame.required_points} pts)")
            updated_count += 1
    
    print(f"\n✨ Done! Created {created_count} new frames, updated {updated_count} existing frames.")
    print("\n📊 Frame Rewards Summary:")
    print("=" * 50)
    
    all_frames = Frame.objects.filter(is_active=True).order_by('required_points')
    for frame in all_frames:
        print(f"  {frame.icon} {frame.name:12} - {frame.required_points:4} points")
    
    print("=" * 50)
    print("\n🎮 Users will automatically unlock frames when they reach these point thresholds!")
    print("   The system checks and unlocks frames automatically when users earn points.")


if __name__ == '__main__':
    seed_frames()
