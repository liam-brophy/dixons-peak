# Dixon's Peak - Final Asset Processing Tools

## 🛠️ Tools Overview

This directory contains the final, optimized tools for sprite extraction and processing:

### Core Tools

1. **`improved_sprite_extractor.py`** - Main sprite extraction engine
   - Advanced computer vision with OpenCV
   - Multiple naming patterns support
   - Overlap filtering and grid detection
   - Smart background removal and transparency

2. **`pattern_tester.py`** - Pattern testing and extraction utility
   - Test different sprite naming patterns
   - Extract sprites with specific pattern (Pattern B is correct)
   - Clean extraction workflow

3. **`sprite_layout_analyzer.py`** - Debug and analysis tool
   - Analyze sprite sheet layouts
   - Generate preview images for manual inspection
   - Identify correct naming patterns

4. **`process_assets.sh`** - One-command asset processing
   - Complete automated workflow
   - Uses Pattern B (correct pattern)
   - Validates output and provides feedback

5. **`verify_sprites.py`** - Quality verification
   - Check extracted sprite quality
   - Verify transparency and sizing
   - Quick health check for assets

## 🚀 Usage

### Quick Start (Recommended)
```bash
./tools/process_assets.sh
```

### Manual Extraction with Specific Pattern
```bash
python3 tools/pattern_tester.py pattern_b
```

### Analyze Sprite Sheets (for debugging)
```bash
python3 tools/sprite_layout_analyzer.py assets/raw/character_sheets/Dixon_Water.jpeg
```

### Verify Quality
```bash
python3 tools/verify_sprites.py
```

## 📋 Pattern Information

**Current Pattern: Pattern B** ✅
- Row 0: idle sprites (all directions)
- Row 1: walk sprites (all directions)
- Row 2: jump sprites (all directions)  
- Row 3: fall sprites (all directions)
- Col 0: down | Col 1: left | Col 2: right | Col 3: up

## 🎯 Output

- **Location**: `assets/game/characters/`
- **Format**: PNG with transparency
- **Size**: 96x96 pixels
- **Naming**: `CharacterName_action_direction.png`
- **Example**: `Dixon_Water_walk_down.png`

## 🔧 Requirements

- Python 3.9+
- OpenCV: `pip install opencv-python`
- Pillow: `pip install pillow`
- NumPy: `pip install numpy`
- Scikit-image: `pip install scikit-image`
