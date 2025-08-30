#!/usr/bin/env python3
"""
Quick sprite verification tool
"""

from PIL import Image
import os

def check_sprite_quality(sprite_path: str):
    """Check if a sprite looks good"""
    if not os.path.exists(sprite_path):
        print(f"❌ Sprite not found: {sprite_path}")
        return False
    
    try:
        img = Image.open(sprite_path)
        print(f"✅ Sprite loaded: {os.path.basename(sprite_path)}")
        print(f"   Size: {img.size}")
        print(f"   Mode: {img.mode}")
        
        # Check if it has transparency
        if img.mode == 'RGBA':
            # Count transparent pixels
            import numpy as np
            data = np.array(img)
            transparent_pixels = np.sum(data[:, :, 3] == 0)
            total_pixels = img.size[0] * img.size[1]
            transparency_ratio = transparent_pixels / total_pixels
            
            print(f"   Transparency: {transparency_ratio*100:.1f}% transparent pixels")
            
            if transparency_ratio > 0.1:  # At least 10% transparent
                print("   ✅ Good transparency (background removed)")
            else:
                print("   ⚠️  Low transparency (background may not be fully removed)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading sprite: {e}")
        return False

# Test a few sprites
sprites_to_check = [
    "assets/game/characters/Dixon_Water/Dixon_Water_idle_down.png",
    "assets/game/characters/Dixon_Water/Dixon_Water_walk_right.png", 
    "assets/game/characters/Dixon_Floral/Dixon_Floral_idle_down.png",
    "assets/game/characters/Dixon_Floral/Dixon_Floral_jump_up.png"
]

print("🔍 Checking sprite extraction quality...\n")

for sprite_path in sprites_to_check:
    check_sprite_quality(sprite_path)
    print()

print("🎮 Sprite extraction verification complete!")
print("💡 You can now test the game at http://localhost:3000")
print("🎯 Look for:")
print("   • Complete character sprites (not cropped)")
print("   • Transparent backgrounds") 
print("   • Smooth idle breathing animation")
print("   • Clean UI without debug text")
