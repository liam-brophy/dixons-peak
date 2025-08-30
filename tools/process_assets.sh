#!/bin/bash
# Final Asset Processing Script - Dixon's Peak
# Uses the improved sprite extractor with correct pattern matching

# Change to project root directory
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "🎮 === Dixon's Peak Final Asset Processing ==="
echo "Project root: $PROJECT_ROOT"

# Check for required Python packages
echo "📦 Checking for required Python packages..."
pip install pillow opencv-python numpy scikit-image

echo "🧹 Cleaning existing extracted assets..."
rm -rf $PROJECT_ROOT/assets/game/characters/*
rm -f $PROJECT_ROOT/assets/game/asset_manifest.json

echo "🚀 Processing character sheets with Pattern B (final version)..."
python3 $PROJECT_ROOT/tools/pattern_tester.py pattern_b

# Validate the output
if [ -f "$PROJECT_ROOT/assets/game/asset_manifest.json" ]; then
    echo "✅ Asset processing completed successfully!"
    echo "📄 Asset manifest created at: assets/game/asset_manifest.json"
    
    # Count extracted sprites
    SPRITE_COUNT=$(find $PROJECT_ROOT/assets/game/characters -name "*.png" | wc -l | tr -d ' ')
    echo "🖼️  Total sprites extracted: $SPRITE_COUNT"
else
    echo "❌ Error: Asset processing failed. Manifest not created."
    exit 1
fi

echo ""
echo "🎉 === Asset Processing Complete ==="
echo "Your game assets are ready with correct sprite mapping!"
echo "🎮 Run 'npm run dev' to start the game."
echo "🎯 Movement controls: W/A/S/D"
echo "🔄 Character switch: Space"
