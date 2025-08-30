#!/bin/bash

echo "🚀 Processing ALL Dixon's Peak assets (including new characters)..."
echo

# Change to project root
cd "$(dirname "$0")/.."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Install required packages
echo "📦 Installing required Python packages..."
pip install pillow opencv-python numpy scikit-image

# Create output directories
echo "📁 Creating output directories..."
mkdir -p assets/game/characters
mkdir -p assets/game/backgrounds
mkdir -p assets/game/items
mkdir -p assets/game/ui

# Clean existing character assets
echo "🧹 Cleaning existing character assets..."
rm -rf assets/game/characters/*

# List of all characters to process
CHARACTERS=("Dixon_Water" "Dixon_Floral" "alien_dude" "ghost_dude")

echo "🎮 Processing character sprite sheets..."
for character in "${CHARACTERS[@]}"
do
    # Convert character name to match filename
    if [ "$character" = "alien_dude" ]; then
        filename="alien dude.jpeg"
    elif [ "$character" = "ghost_dude" ]; then
        filename="ghost dude.jpeg"
    else
        filename="${character}.jpeg"
    fi
    
    input_path="assets/raw/character_sheets/${filename}"
    
    if [ -f "$input_path" ]; then
        echo "  📸 Processing ${character} from ${filename}..."
        python3 tools/pattern_tester.py pattern_b "$input_path" "$character"
        
        # Check if extraction was successful
        output_dir="assets/game/characters/${character}"
        if [ -d "$output_dir" ]; then
            sprite_count=$(ls "$output_dir"/*.png 2>/dev/null | wc -l)
            echo "    ✅ Extracted ${sprite_count} sprites for ${character}"
        else
            echo "    ❌ Failed to extract sprites for ${character}"
        fi
    else
        echo "  ⚠️  Warning: ${input_path} not found, skipping..."
    fi
done

echo
echo "🖼️  Processing background assets..."
# Copy any background assets
if [ -d "assets/raw/backgrounds" ]; then
    cp -r assets/raw/backgrounds/* assets/game/backgrounds/ 2>/dev/null && echo "  ✅ Background assets copied" || echo "  📂 No background assets found in raw/backgrounds"
fi

echo
echo "🎒 Processing item assets..."
# Process any item sheets if they exist
if [ -d "assets/raw/item_sheets" ] && [ "$(ls -A assets/raw/item_sheets 2>/dev/null)" ]; then
    echo "  🎁 Item sheets found, copying..."
    # For now, just copy item assets - could add extraction logic later
    cp -r assets/raw/item_sheets/* assets/game/items/ 2>/dev/null
else
    echo "  📦 No item sheets found"
fi

echo
echo "🔧 Generating comprehensive asset manifest..."
python3 -c "
import json
import os

# Read existing manifest or create new one
manifest_path = 'assets/game/asset_manifest.json'
if os.path.exists(manifest_path):
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
else:
    manifest = {'version': '1.0', 'assets': {}}

# Add any missing backgrounds
bg_dir = 'assets/game/backgrounds'
if os.path.exists(bg_dir):
    if 'backgrounds' not in manifest['assets']:
        manifest['assets']['backgrounds'] = {}
    
    for bg_file in os.listdir(bg_dir):
        if bg_file.endswith(('.png', '.jpg', '.jpeg')):
            bg_name = os.path.splitext(bg_file)[0]
            manifest['assets']['backgrounds'][bg_name] = {
                'path': f'backgrounds/{bg_file}',
                'type': 'background'
            }
            print(f'Added background: {bg_name}')

# Add items if they exist
items_dir = 'assets/game/items'
if os.path.exists(items_dir) and os.listdir(items_dir):
    if 'items' not in manifest['assets']:
        manifest['assets']['items'] = {}
    
    for item_file in os.listdir(items_dir):
        if item_file.endswith(('.png', '.jpg', '.jpeg')):
            item_name = os.path.splitext(item_file)[0]
            manifest['assets']['items'][item_name] = {
                'path': f'items/{item_file}',
                'type': 'item'
            }
            print(f'Added item: {item_name}')

# Count total sprites
total_sprites = 0
for char_name in manifest['assets']:
    if char_name not in ['backgrounds', 'items']:
        total_sprites += len(manifest['assets'][char_name])

print(f'Total character sprites in manifest: {total_sprites}')

# Save manifest
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)

print('✅ Asset manifest updated')
"

echo
echo "✅ ALL asset processing complete!"
echo 
echo "📊 Final Summary:"
echo "  Characters: Dixon_Water, Dixon_Floral, alien_dude, ghost_dude"
echo "  Pattern: B (actions in rows, directions in columns)"
echo "  Output directory: assets/game/"
echo "  Manifest: assets/game/asset_manifest.json"

# Count total extracted files
TOTAL_SPRITES=$(find assets/game/characters -name "*.png" 2>/dev/null | wc -l)
TOTAL_BACKGROUNDS=$(find assets/game/backgrounds -type f 2>/dev/null | wc -l)
TOTAL_ITEMS=$(find assets/game/items -type f 2>/dev/null | wc -l)

echo "  📈 Total extracted:"
echo "    🎮 Sprites: ${TOTAL_SPRITES// /}"
echo "    🖼️  Backgrounds: ${TOTAL_BACKGROUNDS// /}"
echo "    🎒 Items: ${TOTAL_ITEMS// /}"

echo
echo "🎉 Ready to play!"
echo "🎮 Run 'npm run dev' to test all characters!"
echo "🎯 Controls: W/A/S/D to move, Space to switch characters"
