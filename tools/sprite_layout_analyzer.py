#!/usr/bin/env python3
"""
Sprite Layout Analyzer
Helps identify what sprites are in each grid position
"""

import os
from PIL import Image
import json
import sys

def analyze_sprite_layout(image_path: str):
    """Analyze and display the sprite layout"""
    
    # Load image
    image = Image.open(image_path)
    character_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Assume 4x4 grid (adjust if needed)
    rows, cols = 4, 4
    sprite_width = image.width // cols
    sprite_height = image.height // rows
    
    print(f"\n=== Sprite Layout Analysis for {character_name} ===")
    print(f"Image size: {image.width}x{image.height}")
    print(f"Grid: {rows}x{cols}")
    print(f"Each sprite: {sprite_width}x{sprite_height}")
    print("\nGrid positions (Row, Col):")
    print("┌─────┬─────┬─────┬─────┬─────┐")
    print("│     │  0  │  1  │  2  │  3  │")
    print("├─────┼─────┼─────┼─────┼─────┤")
    
    # Create output directory for debug sprites
    debug_dir = f"debug_sprites_{character_name}"
    os.makedirs(debug_dir, exist_ok=True)
    
    # Create a preview showing each sprite position
    for row in range(rows):
        print(f"│  {row}  │", end="")
        for col in range(cols):
            x = col * sprite_width
            y = row * sprite_height
            
            # Extract sprite
            sprite = image.crop((x, y, x + sprite_width, y + sprite_height))
            
            # Save larger preview for better examination
            preview_path = os.path.join(debug_dir, f"sprite_r{row}_c{col}.png")
            sprite_resized = sprite.resize((128, 128), Image.LANCZOS)  # Bigger for better viewing
            sprite_resized.save(preview_path)
            
            # Also save original size
            original_path = os.path.join(debug_dir, f"original_r{row}_c{col}.png")
            sprite.save(original_path)
            
            print(f" R{row}C{col} │", end="")
        print()
    
    print("└─────┴─────┴─────┴─────┴─────┘")
    print(f"\nPreview images saved in: {debug_dir}/")
    print("- sprite_r#_c#.png (128x128 for easy viewing)")
    print("- original_r#_c#.png (original extracted size)")
    
    # Common patterns to check
    print("\n" + "="*50)
    print("COMMON SPRITE SHEET PATTERNS:")
    print("="*50)
    print("\nPattern A - Direction by ROW:")
    print("  Row 0: Down-facing   | Row 1: Left-facing")  
    print("  Row 2: Right-facing  | Row 3: Up-facing")
    print("  Columns: idle, walk1, walk2, walk3")
    
    print("\nPattern B - Direction by ROW (RPG style):")
    print("  Row 0: Up-facing     | Row 1: Right-facing")
    print("  Row 2: Down-facing   | Row 3: Left-facing")
    print("  Columns: idle, walk1, walk2, walk3")
    
    print("\nPattern C - Direction by COLUMN:")
    print("  Col 0: Down-facing   | Col 1: Left-facing")
    print("  Col 2: Right-facing  | Col 3: Up-facing")
    print("  Rows: idle, walk1, walk2, walk3")
    
    print("\nPattern D - Action by ROW:")
    print("  Row 0: Idle/Stand    | Row 1: Walk")
    print("  Row 2: Jump/Attack   | Row 3: Fall/Special")
    print("  Columns: down, left, right, up")
    
    print("\n" + "="*50)
    print("INSTRUCTIONS:")
    print("="*50)
    print(f"1. Look at the images in '{debug_dir}/'")
    print("2. Identify the pattern your sprite sheet follows")
    print("3. Note which direction each character faces in each position")
    print("4. Note what action/animation frame each position represents")
    print("5. Report back with the pattern you observe!")
    
    return debug_dir

def create_naming_config(pattern_type: str, character_name: str):
    """Create a naming configuration based on identified pattern"""
    
    configs = {
        "direction_by_row": {
            "description": "Directions in rows, animation frames in columns",
            "row_mapping": {
                0: "down",
                1: "left", 
                2: "right",
                3: "up"
            },
            "col_mapping": {
                0: "idle",
                1: "walk1",
                2: "walk2", 
                3: "walk3"
            }
        },
        "direction_by_row_rpg": {
            "description": "RPG style - different row order",
            "row_mapping": {
                0: "up",
                1: "right",
                2: "down", 
                3: "left"
            },
            "col_mapping": {
                0: "idle",
                1: "walk1",
                2: "walk2",
                3: "walk3"
            }
        },
        "direction_by_col": {
            "description": "Directions in columns, animation frames in rows",
            "row_mapping": {
                0: "idle",
                1: "walk1",
                2: "walk2",
                3: "walk3"
            },
            "col_mapping": {
                0: "down",
                1: "left",
                2: "right",
                3: "up"
            }
        },
        "action_by_row": {
            "description": "Actions in rows, directions in columns", 
            "row_mapping": {
                0: "idle",
                1: "walk",
                2: "jump",
                3: "fall"
            },
            "col_mapping": {
                0: "down",
                1: "left",
                2: "right", 
                3: "up"
            }
        }
    }
    
    if pattern_type not in configs:
        print(f"Unknown pattern: {pattern_type}")
        print(f"Available patterns: {list(configs.keys())}")
        return None
    
    config = configs[pattern_type]
    print(f"\nGenerated naming pattern: {config['description']}")
    
    # Show what names would be generated
    print("\nSprite naming preview:")
    print("Row | Col | Generated Name")
    print("----|-----|---------------")
    
    for row in range(4):
        for col in range(4):
            row_part = config["row_mapping"][row]
            col_part = config["col_mapping"][col]
            sprite_name = f"{character_name}_{row_part}_{col_part}"
            print(f" {row:2d} | {col:2d}  | {sprite_name}")
    
    return config

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python sprite_layout_analyzer.py <sprite_sheet.png>")
        print("  python sprite_layout_analyzer.py <sprite_sheet.png> <pattern_type>")
        print("\nPattern types:")
        print("  - direction_by_row (most common)")
        print("  - direction_by_row_rpg (RPG style)")
        print("  - direction_by_col (directions in columns)")
        print("  - action_by_row (actions in rows)")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    # Analyze the sprite layout
    debug_dir = analyze_sprite_layout(image_path)
    
    # If pattern type provided, generate naming config
    if len(sys.argv) > 2:
        pattern_type = sys.argv[2]
        character_name = os.path.splitext(os.path.basename(image_path))[0]
        config = create_naming_config(pattern_type, character_name)
        
        if config:
            # Save the configuration for use in asset processor
            config_file = f"naming_config_{character_name}.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"\nNaming configuration saved to: {config_file}")
    
    print(f"\n🔍 Analysis complete! Check the images in '{debug_dir}/' to determine the pattern.")

if __name__ == "__main__":
    main()
