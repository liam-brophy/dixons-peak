#!/usr/bin/env python3
"""
Improved Visual-Intelligence Sprite Extractor
Better grid detection and duplicate filtering
"""

import cv2
import numpy as np
from PIL import Image
import os
import json
import argparse
from pathlib import Path
import time
from collections import defaultdict

class ImprovedVisualExtractor:
    def __init__(self, config_file: str = "asset_config.json"):
        """Initialize the improved visual sprite extractor"""
        self.load_config(config_file)
        self.min_sprite_area = 800  # Minimum area for a valid sprite
        self.max_sprite_area = 50000  # Maximum area to filter out large backgrounds
        self.padding = 5  # Reduced padding for tighter extraction
        
        # Sprite naming patterns - try different patterns to find the right one
        self.naming_patterns = {
            "pattern_a": {
                # Row = Direction, Col = Animation Frame
                "row_mapping": {0: "down", 1: "left", 2: "right", 3: "up"},
                "col_mapping": {0: "idle", 1: "walk", 2: "jump", 3: "fall"}
            },
            "pattern_b": {
                # Row = Animation Frame, Col = Direction  
                "row_mapping": {0: "idle", 1: "walk", 2: "jump", 3: "fall"},
                "col_mapping": {0: "down", 1: "left", 2: "right", 3: "up"}
            },
            "pattern_c": {
                # RPG Style: Row = Direction (different order), Col = Animation Frame
                "row_mapping": {0: "up", 1: "right", 2: "down", 3: "left"},
                "col_mapping": {0: "idle", 1: "walk", 2: "jump", 3: "fall"}
            },
            "pattern_d": {
                # Alternative: Row = Direction, Col = Animation (different order)
                "row_mapping": {0: "idle", 1: "walk", 2: "jump", 3: "fall"},
                "col_mapping": {0: "left", 1: "right", 2: "up", 3: "down"}
            }
        }
        
        # Default pattern - we'll make this configurable
        self.current_pattern = "pattern_b"  # Try pattern B first based on your feedback
        
        self.asset_manifest = {
            "version": "1.0", 
            "assets": {}, 
            "sprite_size": self.config.get("sprite_size", [96, 96]), 
            "format": "PNG"
        }
        
    def load_config(self, config_file: str):
        """Load configuration from JSON file"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "input_dir": "assets/raw/character_sheets",
                "output_dir": "assets/game",
                "sprite_size": [96, 96],
                "naming": {
                    "actions": ["idle", "walk", "jump", "fall"],
                    "directions": ["left", "right", "up", "down"]
                }
            }
    
    def detect_grid_structure(self, sprites_data):
        """Detect the actual grid structure from sprite positions"""
        if not sprites_data:
            return 4, 4  # Default fallback
            
        # Group sprites by similar Y coordinates (rows)
        y_positions = [sprite['bbox'][1] for sprite in sprites_data]
        y_positions.sort()
        
        # Find row groups with tolerance
        row_tolerance = 30
        rows = []
        current_row_y = y_positions[0]
        current_row_count = 1
        
        for y in y_positions[1:]:
            if abs(y - current_row_y) <= row_tolerance:
                current_row_count += 1
            else:
                rows.append(current_row_count)
                current_row_y = y
                current_row_count = 1
        rows.append(current_row_count)
        
        # Most common row size is likely the grid width
        grid_cols = max(set(rows), key=rows.count) if rows else 4
        grid_rows = len(rows)
        
        # Ensure we have a reasonable grid
        expected_sprites = grid_rows * grid_cols
        if abs(expected_sprites - len(sprites_data)) > len(sprites_data) * 0.3:
            # If detected grid doesn't match sprite count well, use 4x4
            grid_rows, grid_cols = 4, 4
            
        return grid_rows, grid_cols
    
    def generate_sprite_name(self, character_name: str, row: int, col: int) -> str:
        """Generate sprite name using the current naming pattern"""
        pattern = self.naming_patterns[self.current_pattern]
        
        row_name = pattern["row_mapping"].get(row, f"row{row}")
        col_name = pattern["col_mapping"].get(col, f"col{col}")
        
        return f"{character_name}_{row_name}_{col_name}"
    
    def set_naming_pattern(self, pattern_name: str):
        """Set the naming pattern to use"""
        if pattern_name in self.naming_patterns:
            self.current_pattern = pattern_name
            print(f"✅ Using naming pattern: {pattern_name}")
            pattern = self.naming_patterns[pattern_name]
            print("Row mapping:", pattern["row_mapping"])
            print("Col mapping:", pattern["col_mapping"])
        else:
            print(f"❌ Unknown pattern: {pattern_name}")
            print(f"Available patterns: {list(self.naming_patterns.keys())}")
    
    def debug_naming_patterns(self, character_name: str):
        """Show what names would be generated for each pattern"""
        print(f"\n🔍 Debugging naming patterns for {character_name}:")
        
        for pattern_name, pattern in self.naming_patterns.items():
            print(f"\n--- Pattern {pattern_name} ---")
            print("Row | Col | Generated Name")
            print("----|-----|---------------")
            
            for row in range(4):
                for col in range(4):
                    row_name = pattern["row_mapping"].get(row, f"row{row}")
                    col_name = pattern["col_mapping"].get(col, f"col{col}")
                    sprite_name = f"{character_name}_{row_name}_{col_name}"
                    print(f" {row:2d} | {col:2d}  | {sprite_name}")
    
    def try_pattern_and_extract(self, image_path: str, character_name: str, pattern_name: str):
        """Try a specific naming pattern and extract sprites"""
        print(f"\n🧪 Testing pattern '{pattern_name}' for {character_name}")
        
        # Set the pattern
        old_pattern = self.current_pattern
        self.set_naming_pattern(pattern_name)
        
        # Extract sprites
        result = self.extract_sprites_improved(image_path, character_name)
        
        # Restore old pattern
        self.current_pattern = old_pattern
        
        return result
    
    def filter_overlapping_sprites(self, sprites_data):
        """Remove sprites that significantly overlap with others"""
        filtered_sprites = []
        
        def calculate_overlap_ratio(box1, box2):
            """Calculate overlap ratio between two bounding boxes"""
            x1, y1, w1, h1 = box1
            x2, y2, w2, h2 = box2
            
            # Calculate intersection
            left = max(x1, x2)
            top = max(y1, y2)
            right = min(x1 + w1, x2 + w2)
            bottom = min(y1 + h1, y2 + h2)
            
            if left >= right or top >= bottom:
                return 0
            
            intersection_area = (right - left) * (bottom - top)
            box1_area = w1 * h1
            box2_area = w2 * h2
            
            return intersection_area / min(box1_area, box2_area)
        
        # Sort by area (keep larger sprites when there's overlap)
        sprites_data.sort(key=lambda s: s['area'], reverse=True)
        
        for sprite in sprites_data:
            # Check if this sprite significantly overlaps with any already accepted sprite
            overlaps_significantly = False
            for accepted_sprite in filtered_sprites:
                overlap_ratio = calculate_overlap_ratio(sprite['bbox'], accepted_sprite['bbox'])
                if overlap_ratio > 0.5:  # More than 50% overlap
                    overlaps_significantly = True
                    break
            
            if not overlaps_significantly:
                filtered_sprites.append(sprite)
        
        return filtered_sprites
    
    def extract_sprites_improved(self, image_path: str, character_name: str):
        """Extract sprites with improved detection and filtering"""
        
        print(f"Processing image: {image_path}")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image {image_path}")
            return 0
            
        original = img.copy()
        height, width = img.shape[:2]
        
        # Enhanced preprocessing for white background detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Multiple detection methods
        # 1. Simple thresholding for white background
        _, thresh1 = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # 2. Adaptive thresholding
        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY_INV, 11, 2)
        
        # 3. Color-based detection in original image
        # Create mask for non-white pixels
        lower_white = np.array([240, 240, 240])
        upper_white = np.array([255, 255, 255])
        white_mask = cv2.inRange(img, lower_white, upper_white)
        color_thresh = cv2.bitwise_not(white_mask)
        
        # Combine detection methods
        combined = cv2.bitwise_or(thresh1, thresh2)
        combined = cv2.bitwise_or(combined, color_thresh)
        
        # Morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours to find valid sprites
        potential_sprites = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_sprite_area <= area <= self.max_sprite_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Additional filtering
                aspect_ratio = w / h
                extent = area / (w * h)
                
                if (0.2 < aspect_ratio < 5.0 and  # Allow wider range for different poses
                    extent > 0.1 and  # At least 10% filled
                    w > 30 and h > 40 and  # Minimum meaningful size
                    w < width * 0.9 and h < height * 0.9):  # Not entire image
                    
                    potential_sprites.append({
                        'bbox': (x, y, w, h),
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'extent': extent
                    })
        
        print(f"Found {len(potential_sprites)} potential sprites")
        
        # Filter overlapping sprites
        filtered_sprites = self.filter_overlapping_sprites(potential_sprites)
        print(f"After filtering overlaps: {len(filtered_sprites)} sprites")
        
        # Detect grid structure
        grid_rows, grid_cols = self.detect_grid_structure(filtered_sprites)
        print(f"Detected grid: {grid_rows} rows x {grid_cols} cols")
        
        # Sort sprites by position (top-to-bottom, left-to-right)
        def sort_key(sprite):
            x, y, w, h = sprite['bbox']
            # Group by rows first (with some tolerance), then by columns
            row = y // (height // max(grid_rows, 1))
            col = x // (width // max(grid_cols, 1))
            return (row, col)
        
        filtered_sprites.sort(key=sort_key)
        
        # Take only the expected number of sprites
        expected_sprites = min(len(filtered_sprites), grid_rows * grid_cols)
        filtered_sprites = filtered_sprites[:expected_sprites]
        
        # Create character directory
        character_dir = os.path.join(self.config["output_dir"], "characters", character_name)
        os.makedirs(character_dir, exist_ok=True)
        
        # Initialize character in asset manifest
        self.asset_manifest["assets"][character_name] = {}
        
        # Extract and save sprites
        actions = self.config["naming"]["actions"]
        directions = self.config["naming"]["directions"]
        
        extracted_count = 0
        for i, sprite_info in enumerate(filtered_sprites):
            x, y, w, h = sprite_info['bbox']
            
            # Add minimal padding
            x1 = max(0, x - self.padding)
            y1 = max(0, y - self.padding)
            x2 = min(img.shape[1], x + w + self.padding)
            y2 = min(img.shape[0], y + h + self.padding)
            
            # Extract sprite
            sprite = original[y1:y2, x1:x2]
            
            # Convert to PIL
            sprite_pil = Image.fromarray(cv2.cvtColor(sprite, cv2.COLOR_BGR2RGB))
            
            # Make background transparent
            sprite_pil = self.make_background_transparent(sprite_pil)
            
            # Resize appropriately
            sprite_pil = self.resize_sprite_smart(sprite_pil)
            
            # Calculate grid position
            row = i // grid_cols
            col = i % grid_cols
            
            # Generate name based on grid position using current pattern
            sprite_name = self.generate_sprite_name(character_name, row, col)
            output_path = os.path.join(character_dir, f"{sprite_name}.png")
            
            sprite_pil.save(output_path)
            print(f"Extracted: {sprite_name} ({w}x{h} -> {sprite_pil.size[0]}x{sprite_pil.size[1]}) at position ({row},{col})")
            
            # Add to manifest
            self.asset_manifest["assets"][character_name][sprite_name] = {
                "path": f"characters/{character_name}/{sprite_name}.png",
                "size": list(sprite_pil.size),
                "original_bounds": [x, y, w, h],
                "grid_position": [row, col]
            }
            
            extracted_count += 1
        
        return extracted_count
    
    def make_background_transparent(self, image: Image.Image) -> Image.Image:
        """Convert white background to transparent with better edge handling"""
        image = image.convert("RGBA")
        data = np.array(image)
        
        # Create transparency for white-ish pixels
        # Use a more sophisticated approach for better edge quality
        white_threshold_high = 245  # Very white pixels
        white_threshold_low = 230   # Somewhat white pixels
        
        # Calculate "whiteness" score
        whiteness = np.minimum(np.minimum(data[:, :, 0], data[:, :, 1]), data[:, :, 2])
        
        # Fully transparent for very white pixels
        very_white_mask = whiteness >= white_threshold_high
        data[very_white_mask] = [255, 255, 255, 0]
        
        # Partially transparent for somewhat white pixels
        somewhat_white_mask = (whiteness >= white_threshold_low) & (whiteness < white_threshold_high)
        alpha_reduction = ((whiteness[somewhat_white_mask] - white_threshold_low) / 
                          (white_threshold_high - white_threshold_low) * 255).astype(np.uint8)
        data[somewhat_white_mask, 3] = 255 - alpha_reduction
        
        return Image.fromarray(data)
    
    def resize_sprite_smart(self, sprite: Image.Image) -> Image.Image:
        """Resize sprite maintaining aspect ratio and proper alignment"""
        target_size = tuple(self.config["sprite_size"])
        
        # Calculate scaling to fit within target size
        scale_x = target_size[0] / sprite.width
        scale_y = target_size[1] / sprite.height
        scale = min(scale_x, scale_y)
        
        # Calculate new size
        new_width = int(sprite.width * scale)
        new_height = int(sprite.height * scale)
        
        # Resize with high quality
        sprite_resized = sprite.resize((new_width, new_height), Image.LANCZOS)
        
        # Create result image
        result = Image.new('RGBA', target_size, (0, 0, 0, 0))
        
        # Position sprite (center horizontally, align to bottom)
        paste_x = (target_size[0] - new_width) // 2
        paste_y = target_size[1] - new_height
        
        result.paste(sprite_resized, (paste_x, paste_y), sprite_resized)
        
        return result
    
    def save_asset_manifest(self):
        """Save asset manifest"""
        output_path = os.path.join(self.config["output_dir"], "asset_manifest.json")
        with open(output_path, 'w') as f:
            json.dump(self.asset_manifest, f, indent=2)
        print(f"Asset manifest saved to: {output_path}")
    
    def process_all(self):
        """Process all character sheets"""
        input_dir = self.config["input_dir"]
        
        # Get all image files
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']:
            image_files.extend(Path(input_dir).glob(ext))
        
        if not image_files:
            print(f"No image files found in {input_dir}")
            return
        
        total_sprites = 0
        
        for image_path in image_files:
            character_name = image_path.stem
            sprite_count = self.extract_sprites_improved(str(image_path), character_name)
            total_sprites += sprite_count
            print(f"Successfully extracted {sprite_count} sprites from {character_name}")
            print("-" * 60)
        
        self.save_asset_manifest()
        print(f"\n✅ Asset processing complete! Total sprites extracted: {total_sprites}")

def main():
    parser = argparse.ArgumentParser(description="Improved Visual Sprite Extractor")
    parser.add_argument('--config', default='asset_config.json', help='Config file path')
    parser.add_argument('--input', help='Single image to process')
    
    args = parser.parse_args()
    
    start_time = time.time()
    extractor = ImprovedVisualExtractor(args.config)
    
    if args.input:
        character_name = Path(args.input).stem
        sprite_count = extractor.extract_sprites_improved(args.input, character_name)
        extractor.save_asset_manifest()
        print(f"Extracted {sprite_count} sprites from {character_name}")
    else:
        extractor.process_all()
    
    print(f"\n⏱️  Processing completed in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
