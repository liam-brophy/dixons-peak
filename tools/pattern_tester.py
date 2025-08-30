#!/usr/bin/env python3
"""
Test different naming patterns for sprite extraction
"""

import sys
import os
from pathlib import Path

# Add the tools directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__)))

from improved_sprite_extractor import ImprovedVisualExtractor

def test_patterns():
    """Test different naming patterns and show results"""
    
    extractor = ImprovedVisualExtractor("asset_config.json")
    
    # Test patterns
    test_character = "Dixon_Water"
    print("🧪 Testing different naming patterns...")
    
    print("\n" + "="*60)
    extractor.debug_naming_patterns(test_character)
    
    # Based on your feedback, let's try pattern B first
    print("\n" + "="*60)
    print("🎯 RECOMMENDED: Trying Pattern B (actions in rows, directions in columns)")
    print("This pattern might fix your issue where 'moving down shows idle sprite'")
    
    # Set pattern B and show what it would generate
    extractor.set_naming_pattern("pattern_b")
    
    return extractor

def extract_with_pattern(pattern_name: str):
    """Extract sprites using a specific pattern"""
    
    print(f"\n🚀 Extracting sprites with pattern: {pattern_name}")
    
    extractor = ImprovedVisualExtractor("asset_config.json")
    extractor.set_naming_pattern(pattern_name)
    
    # Clean and process
    import shutil
    output_dir = "assets/game/characters"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Process both character sheets
    image_files = [
        "assets/raw/character_sheets/Dixon_Water.jpeg",
        "assets/raw/character_sheets/Dixon_Floral.jpeg"
    ]
    
    total_sprites = 0
    for image_path in image_files:
        if os.path.exists(image_path):
            character_name = Path(image_path).stem
            sprite_count = extractor.extract_sprites_improved(image_path, character_name)
            total_sprites += sprite_count
            print(f"✅ Extracted {sprite_count} sprites from {character_name}")
        else:
            print(f"❌ Image not found: {image_path}")
    
    # Save manifest
    extractor.save_asset_manifest()
    
    print(f"\n🎉 Total sprites extracted: {total_sprites}")
    print("🎮 Start your game to test the new sprite naming!")
    
    return total_sprites

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Extract with specific pattern
        pattern_name = sys.argv[1]
        extract_with_pattern(pattern_name)
    else:
        # Just test and show patterns
        extractor = test_patterns()
        
        print("\n" + "="*60)
        print("USAGE:")
        print("  python pattern_tester.py pattern_b    # Extract with pattern B")
        print("  python pattern_tester.py pattern_a    # Extract with pattern A") 
        print("  python pattern_tester.py pattern_c    # Extract with pattern C")
        print("  python pattern_tester.py pattern_d    # Extract with pattern D")
        
        print("\n🎯 RECOMMENDATION:")
        print("Based on your feedback, try pattern_b first:")
        print("  python pattern_tester.py pattern_b")
        
        print("\nThis should fix the issue where moving down shows idle sprite!")
