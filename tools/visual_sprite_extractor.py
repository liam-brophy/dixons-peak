#!/usr/bin/env python3
"""
Visual-Intelligence Sprite Extractor using OpenCV
Better detection for sprites with white backgrounds
"""

import cv2
import numpy as np
from PIL import Image
import os
import json
import argparse
from pathlib import Path
import time

class VisualSpriteExtractor:
    def __init__(self, config_file: str = "asset_config.json"):
        """Initialize the visual sprite extractor with configuration"""
        self.load_config(config_file)
        self.min_sprite_area = 1000  # Minimum area for a valid sprite
        self.padding = 10  # Padding around detected sprites
        self.white_threshold = 240  # Threshold for white background detection
        
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
    
    def extract_sprites_smart(self, image_path: str, character_name: str):
        """Extract sprites using advanced computer vision techniques"""
        
        print(f"Processing image: {image_path}")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image {image_path}")
            return 0
            
        original = img.copy()
        height, width = img.shape[:2]
        
        # Convert to different color spaces for better detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Method 1: Edge detection with multiple scales
        edges1 = cv2.Canny(gray, 30, 100)
        edges2 = cv2.Canny(gray, 50, 150)
        edges3 = cv2.Canny(gray, 100, 200)
        edges_combined = cv2.bitwise_or(cv2.bitwise_or(edges1, edges2), edges3)
        
        # Method 2: Enhanced color-based segmentation for white backgrounds
        # More sophisticated white detection
        lower_white = np.array([235, 235, 235])
        upper_white = np.array([255, 255, 255])
        white_mask = cv2.inRange(img, lower_white, upper_white)
        non_white_mask = cv2.bitwise_not(white_mask)
        
        # Method 3: HSV-based detection (helps with slight color variations)
        # Detect very light colors that might be "almost white"
        lower_hsv_white = np.array([0, 0, 240])
        upper_hsv_white = np.array([180, 30, 255])
        hsv_white_mask = cv2.inRange(hsv, lower_hsv_white, upper_hsv_white)
        hsv_non_white_mask = cv2.bitwise_not(hsv_white_mask)
        
        # Method 4: Adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 15, 3
        )
        
        # Method 5: Morphological gradient to detect object boundaries
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
        _, gradient_thresh = cv2.threshold(gradient, 10, 255, cv2.THRESH_BINARY)
        
        # Combine all methods for robust detection
        combined = cv2.bitwise_or(edges_combined, non_white_mask)
        combined = cv2.bitwise_or(combined, hsv_non_white_mask)
        combined = cv2.bitwise_or(combined, adaptive_thresh)
        combined = cv2.bitwise_or(combined, gradient_thresh)
        
        # Morphological operations to clean up and connect nearby components
        # Close small gaps
        kernel_close = np.ones((5, 5), np.uint8)
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel_close)
        
        # Remove small noise
        kernel_open = np.ones((3, 3), np.uint8)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel_open)
        
        # Dilate to ensure we capture full sprite boundaries
        kernel_dilate = np.ones((2, 2), np.uint8)
        combined = cv2.dilate(combined, kernel_dilate, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Advanced filtering and sorting of contours
        valid_sprites = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_sprite_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Additional filtering criteria
                aspect_ratio = w / h
                extent = area / (w * h)  # How much of the bounding rect is filled
                
                # Filter out very thin rectangles and very sparse areas
                if (0.3 < aspect_ratio < 3.0 and  # Reasonable aspect ratio
                    extent > 0.1 and  # At least 10% filled
                    w > 20 and h > 20 and  # Minimum size
                    w < width * 0.8 and h < height * 0.8):  # Not the entire image
                    
                    valid_sprites.append({
                        'bbox': (x, y, w, h),
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'extent': extent
                    })
        
        print(f"Found {len(valid_sprites)} potential sprites")
        
        # Intelligent sorting: group by rows, then by columns
        # Estimate grid dimensions based on sprite positions
        if valid_sprites:
            # Sort by y-coordinate to find rows
            sorted_by_y = sorted(valid_sprites, key=lambda s: s['bbox'][1])
            
            # Group sprites into rows (sprites with similar y-coordinates)
            rows = []
            current_row = [sorted_by_y[0]]
            row_tolerance = 20  # pixels
            
            for sprite in sorted_by_y[1:]:
                if abs(sprite['bbox'][1] - current_row[0]['bbox'][1]) < row_tolerance:
                    current_row.append(sprite)
                else:
                    rows.append(sorted(current_row, key=lambda s: s['bbox'][0]))  # Sort row by x
                    current_row = [sprite]
            rows.append(sorted(current_row, key=lambda s: s['bbox'][0]))  # Don't forget last row
            
            # Flatten back to a single list, now properly sorted
            valid_sprites = [sprite for row in rows for sprite in row]
        
        # Create character directory
        character_dir = os.path.join(self.config["output_dir"], "characters", character_name)
        os.makedirs(character_dir, exist_ok=True)
        
        # Initialize character in asset manifest
        self.asset_manifest["assets"][character_name] = {}
        
        # Extract and save sprites with intelligent naming
        extracted_count = 0
        actions = self.config["naming"]["actions"]
        directions = self.config["naming"]["directions"]
        
        for i, sprite_info in enumerate(valid_sprites):
            x, y, w, h = sprite_info['bbox']
            
            # Add padding but stay within image bounds
            x1 = max(0, x - self.padding)
            y1 = max(0, y - self.padding)
            x2 = min(img.shape[1], x + w + self.padding)
            y2 = min(img.shape[0], y + h + self.padding)
            
            # Extract sprite
            sprite = original[y1:y2, x1:x2]
            
            # Convert to PIL for processing
            sprite_pil = Image.fromarray(cv2.cvtColor(sprite, cv2.COLOR_BGR2RGB))
            
            # Make background transparent
            sprite_pil = self.make_background_transparent(sprite_pil)
            
            # Resize to target sprite size while maintaining aspect ratio
            sprite_pil = self.resize_sprite_smart(sprite_pil)
            
            # Generate intelligent name based on position
            row = i // len(directions) if len(directions) > 0 else 0
            col = i % len(directions) if len(directions) > 0 else 0
            
            action = actions[row % len(actions)] if actions else "sprite"
            direction = directions[col % len(directions)] if directions else f"{col:02d}"
            
            sprite_name = f"{character_name}_{action}_{direction}"
            output_path = os.path.join(character_dir, f"{sprite_name}.png")
            
            sprite_pil.save(output_path)
            print(f"Extracted: {sprite_name} ({w}x{h} -> {sprite_pil.size[0]}x{sprite_pil.size[1]})")
            
            # Add to manifest
            self.asset_manifest["assets"][character_name][sprite_name] = {
                "path": f"characters/{character_name}/{sprite_name}.png",
                "size": list(sprite_pil.size),
                "original_bounds": [x, y, w, h]
            }
            
            extracted_count += 1
        
        return extracted_count
    
    def make_background_transparent(self, image: Image.Image) -> Image.Image:
        """Convert white background to transparent with edge smoothing"""
        image = image.convert("RGBA")
        data = np.array(image)
        
        # Multiple thresholds for better edge handling
        # Very white pixels -> fully transparent
        very_white_mask = (data[:, :, 0] > 250) & (data[:, :, 1] > 250) & (data[:, :, 2] > 250)
        data[very_white_mask] = [255, 255, 255, 0]
        
        # Nearly white pixels -> partially transparent
        nearly_white_mask = ((data[:, :, 0] > 240) & (data[:, :, 1] > 240) & (data[:, :, 2] > 240) & 
                           ~very_white_mask)
        data[nearly_white_mask, 3] = data[nearly_white_mask, 3] // 3  # Reduce alpha
        
        result = Image.fromarray(data)
        
        # Apply slight gaussian blur to alpha channel for smoother edges
        r, g, b, a = result.split()
        # Convert alpha to numpy for processing
        a_array = np.array(a)
        # Apply slight blur using opencv
        a_blurred = cv2.GaussianBlur(a_array, (3, 3), 0.5)
        a_smooth = Image.fromarray(a_blurred)
        
        return Image.merge('RGBA', (r, g, b, a_smooth))
    
    def resize_sprite_smart(self, sprite: Image.Image) -> Image.Image:
        """Resize sprite to target size while maintaining aspect ratio and proper alignment"""
        target_size = tuple(self.config["sprite_size"])
        
        # Calculate scaling to fit within target size
        scale_x = target_size[0] / sprite.width
        scale_y = target_size[1] / sprite.height
        scale = min(scale_x, scale_y)  # Use smaller scale to fit within bounds
        
        # Calculate new size
        new_width = int(sprite.width * scale)
        new_height = int(sprite.height * scale)
        
        # Resize with high quality
        sprite_resized = sprite.resize((new_width, new_height), Image.LANCZOS)
        
        # Create new image with target size
        result = Image.new('RGBA', target_size, (0, 0, 0, 0))
        
        # Center horizontally, align to bottom (for character sprites)
        paste_x = (target_size[0] - new_width) // 2
        paste_y = target_size[1] - new_height  # Align to bottom for proper feet placement
        
        result.paste(sprite_resized, (paste_x, paste_y), sprite_resized)
        
        return result
    
    def save_asset_manifest(self):
        """Save the asset manifest to JSON"""
        output_path = os.path.join(self.config["output_dir"], "asset_manifest.json")
        with open(output_path, 'w') as f:
            json.dump(self.asset_manifest, f, indent=2)
        print(f"Asset manifest saved to: {output_path}")
    
    def process_all(self):
        """Process all character sheets in the input directory"""
        input_dir = self.config["input_dir"]
        
        # Get all image files
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']:
            image_files.extend(Path(input_dir).glob(ext))
        
        if not image_files:
            print(f"No image files found in {input_dir}")
            return
        
        total_sprites = 0
        
        # Process each file
        for image_path in image_files:
            character_name = image_path.stem
            sprite_count = self.extract_sprites_smart(str(image_path), character_name)
            total_sprites += sprite_count
            print(f"Extracted {sprite_count} sprites from {character_name}")
            print("-" * 50)
        
        # Save asset manifest
        self.save_asset_manifest()
        print(f"\nAsset processing complete! Total sprites extracted: {total_sprites}")

def main():
    parser = argparse.ArgumentParser(description="Visual Intelligence Sprite Extractor")
    parser.add_argument('--config', default='asset_config.json', 
                       help='Path to config file')
    parser.add_argument('--input', 
                       help='Single image file to process')
    parser.add_argument('--min-area', type=int, default=1000,
                       help='Minimum sprite area in pixels')
    parser.add_argument('--padding', type=int, default=10,
                       help='Padding around detected sprites')
    parser.add_argument('--white-threshold', type=int, default=240,
                       help='Threshold for white background detection')
    
    args = parser.parse_args()
    
    start_time = time.time()
    extractor = VisualSpriteExtractor(args.config)
    
    # Override settings if provided
    if args.min_area:
        extractor.min_sprite_area = args.min_area
    if args.padding:
        extractor.padding = args.padding
    if args.white_threshold:
        extractor.white_threshold = args.white_threshold
    
    if args.input:
        # Process single file
        character_name = Path(args.input).stem
        sprite_count = extractor.extract_sprites_smart(args.input, character_name)
        extractor.save_asset_manifest()
        print(f"Extracted {sprite_count} sprites from {character_name}")
    else:
        # Process all files
        extractor.process_all()
    
    print(f"Processing completed in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
