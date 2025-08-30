#!/usr/bin/env python3
"""
Enhanced Character Sheet Asset Processor
Advanced sprite detection and background removal for game assets
"""

import os
import json
import shutil
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter
import cv2
import numpy as np
import argparse
import time
from typing import List, Tuple, Dict, Optional

class EnhancedAssetProcessor:
    def __init__(self, config_file: str = "asset_config.json"):
        """Initialize the asset processor with configuration"""
        self.config = self.load_config(config_file)
        self.setup_directories()
        self.asset_manifest = {"version": "1.0", "assets": {}, "sprite_size": self.config["sprite_size"], "format": self.config["output_format"]}
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"Config file not found: {config_file}")
    
    def setup_directories(self):
        """Create necessary directories and clean existing output"""
        Path(self.config["input_dir"]).mkdir(exist_ok=True)
        
        # Clean and recreate output directory
        output_path = Path(self.config["output_dir"])
        character_path = output_path / "characters"
        
        # Create clean directories
        output_path.mkdir(exist_ok=True)
        for subdir in ["characters", "items", "ui", "backgrounds"]:
            subdir_path = output_path / subdir
            if subdir_path.exists():
                # Only clean characters directory
                if subdir == "characters":
                    shutil.rmtree(subdir_path)
            subdir_path.mkdir(exist_ok=True)
    
    def detect_sprites(self, image_path: str) -> List[Dict]:
        """
        Advanced sprite detection that finds actual sprite boundaries
        rather than just dividing by a grid
        """
        print(f"Processing image: {image_path}")
        
        # Load image and convert to RGBA
        image = Image.open(image_path)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Convert to numpy array for OpenCV processing
        img_array = np.array(image)
        
        # Convert to grayscale for contour detection
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
        
        # Apply some preprocessing to improve sprite detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 240, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours - these will be our sprite candidates
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter out very small contours (noise)
        min_area = 100  # Adjust based on your sprite size
        valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
        
        # Sort contours by position (top to bottom, left to right)
        def contour_sort_key(contour):
            x, y, w, h = cv2.boundingRect(contour)
            # Sort primarily by row (y value) and secondarily by column (x value)
            row_height = image.height // (self.config["grid_detection"]["manual_rows"] or 4)
            row = y // row_height
            return (row, x)
            
        valid_contours.sort(key=contour_sort_key)
        
        # Detect grid dimensions based on contours
        if self.config["grid_detection"]["auto_detect"]:
            rows, cols = self.detect_grid_from_contours(valid_contours, image.size)
        else:
            rows = self.config["grid_detection"]["manual_rows"]
            cols = self.config["grid_detection"]["manual_cols"]
        
        print(f"Detected grid: {rows} rows, {cols} columns")
        
        # Extract sprites based on detected contours
        sprites = []
        
        # If we have the right number of contours, use them directly
        expected_sprites = rows * cols
        if len(valid_contours) == expected_sprites:
            print(f"Found exact number of sprites: {len(valid_contours)}")
            for i, contour in enumerate(valid_contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Expand bounding box slightly to ensure we get the full sprite
                padding = self.config["padding"]
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(image.width - x, w + padding * 2)
                h = min(image.height - y, h + padding * 2)
                
                row = i // cols
                col = i % cols
                
                sprite_info = {
                    "bounds": (x, y, x + w, y + h),
                    "row": row,
                    "col": col
                }
                sprites.append(sprite_info)
        else:
            print(f"Found {len(valid_contours)} contours, expected {expected_sprites}. Using grid-based approach.")
            # Fall back to grid-based approach
            sprite_width = image.width // cols
            sprite_height = image.height // rows
            
            for row in range(rows):
                for col in range(cols):
                    x = col * sprite_width
                    y = row * sprite_height
                    
                    sprite_info = {
                        "bounds": (x, y, x + sprite_width, y + sprite_height),
                        "row": row,
                        "col": col
                    }
                    sprites.append(sprite_info)
        
        return sprites, image
    
    def detect_grid_from_contours(self, contours: List, image_size: Tuple[int, int]) -> Tuple[int, int]:
        """Determine grid dimensions from contour positions"""
        if not contours:
            return (self.config["grid_detection"]["manual_rows"], 
                   self.config["grid_detection"]["manual_cols"])
        
        # Get all bounding boxes
        bboxes = [cv2.boundingRect(c) for c in contours]
        
        # Extract all unique x and y coordinates
        x_coords = sorted(set(bbox[0] for bbox in bboxes))
        y_coords = sorted(set(bbox[1] for bbox in bboxes))
        
        # Count unique positions
        cols = len(x_coords)
        rows = len(y_coords)
        
        # Verify and adjust if needed
        if rows * cols != len(contours):
            # Fall back to default if detection seems incorrect
            rows = self.config["grid_detection"]["manual_rows"]
            cols = self.config["grid_detection"]["manual_cols"]
        
        return rows, cols
    
    def remove_background(self, sprite_img: Image.Image) -> Image.Image:
        """Remove background using improved methods with edge preservation"""
        method = self.config["background_removal"]["method"]
        
        if method == "rembg":
            try:
                from rembg import remove
                
                # Convert PIL image to bytes
                import io
                img_byte_arr = io.BytesIO()
                sprite_img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Remove background with higher alpha matting for better edge quality
                output = remove(img_byte_arr, alpha_matting=True)
                
                # Convert back to PIL image
                return Image.open(io.BytesIO(output))
            except ImportError:
                print("rembg not installed, falling back to color key method")
                return self.remove_background_color_key(sprite_img)
        else:
            return self.remove_background_color_key(sprite_img)
    
    def remove_background_color_key(self, image: Image.Image) -> Image.Image:
        """Enhanced color key background removal with edge improvements"""
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Get image data as numpy array
        data = np.array(image)
        
        # Define the color to remove and tolerance
        target_color = np.array(self.config["background_removal"]["color_key"])
        tolerance = self.config["background_removal"]["tolerance"]
        
        # Calculate color distance
        diff = np.abs(data[:, :, :3].astype(int) - target_color.astype(int))
        color_distance = np.sum(diff, axis=2)
        
        # Create mask where color distance is within tolerance
        mask = color_distance <= (tolerance * 3)  # multiply by 3 for RGB channels
        
        # Set alpha channel to 0 for matching pixels
        data[mask, 3] = 0
        
        # Convert back to PIL
        result = Image.fromarray(data, 'RGBA')
        
        # Apply slight blur to alpha channel to smooth edges
        r, g, b, a = result.split()
        a = a.filter(ImageFilter.GaussianBlur(radius=0.5))
        result = Image.merge('RGBA', (r, g, b, a))
        
        return result
    
    def trim_sprite(self, sprite_img: Image.Image) -> Image.Image:
        """Trim empty space around sprite while preserving full character proportions"""
        # Get the alpha channel
        _, _, _, alpha = sprite_img.split()
        
        # Get bounding box of non-transparent pixels
        bbox = ImageOps.invert(alpha).getbbox()
        
        if bbox:
            # Calculate padding to maintain character proportions
            target_size = tuple(self.config["sprite_size"])
            
            # Crop to bounding box with a little extra padding
            padding = 5  # Additional padding to avoid tight cropping
            x1, y1, x2, y2 = bbox
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(sprite_img.width, x2 + padding)
            y2 = min(sprite_img.height, y2 + padding)
            
            trimmed = sprite_img.crop((x1, y1, x2, y2))
            
            # Calculate positioning - we want to preserve the character's feet position
            # by aligning the bottom of the sprite with the bottom of the target
            aspect_ratio = trimmed.width / trimmed.height
            
            # Resize maintaining aspect ratio
            if trimmed.width > trimmed.height:
                # Width constrained
                new_width = target_size[0]
                new_height = int(new_width / aspect_ratio)
                if new_height > target_size[1]:
                    # Height constrained instead
                    new_height = target_size[1]
                    new_width = int(new_height * aspect_ratio)
            else:
                # Height constrained
                new_height = target_size[1]
                new_width = int(new_height * aspect_ratio)
                if new_width > target_size[0]:
                    # Width constrained instead
                    new_width = target_size[0]
                    new_height = int(new_width / aspect_ratio)
            
            # Resize with high quality
            resized = trimmed.resize((new_width, new_height), Image.LANCZOS)
            
            # Create a new image with target size
            new_img = Image.new('RGBA', target_size, (0, 0, 0, 0))
            
            # Center horizontally but align to bottom for proper "feet" placement
            paste_x = (target_size[0] - new_width) // 2
            paste_y = target_size[1] - new_height  # Align to bottom
            
            new_img.paste(resized, (paste_x, paste_y), resized)
            return new_img
        
        return sprite_img
        return sprite_img
    
    def name_sprite(self, character_name: str, row: int, col: int) -> str:
        """Generate sprite name based on its position in the sheet"""
        actions = self.config["naming"]["actions"]
        directions = self.config["naming"]["directions"]
        
        action_idx = row % len(actions)
        direction_idx = col % len(directions)
        
        action = actions[action_idx]
        direction = directions[direction_idx]
        
        return f"{character_name}_{action}_{direction}"
    
    def process_character_sheet(self, image_path: str):
        """Process a character sheet to extract sprites"""
        # Get character name from filename
        file_name = os.path.basename(image_path)
        character_name = os.path.splitext(file_name)[0]
        
        # Create character directory
        character_dir = os.path.join(self.config["output_dir"], "characters", character_name)
        os.makedirs(character_dir, exist_ok=True)
        
        # Initialize character in asset manifest
        self.asset_manifest["assets"][character_name] = {}
        
        # Detect sprites in the image
        sprites, full_image = self.detect_sprites(image_path)
        
        # Process each sprite
        for sprite_info in sprites:
            bounds = sprite_info["bounds"]
            row = sprite_info["row"]
            col = sprite_info["col"]
            
            # Extract sprite from sheet
            sprite_img = full_image.crop(bounds)
            
            # Remove background
            sprite_img = self.remove_background(sprite_img)
            
            # Trim and resize sprite
            sprite_img = self.trim_sprite(sprite_img)
            
            # Generate sprite name
            sprite_name = self.name_sprite(character_name, row, col)
            
            # Save sprite
            output_format = self.config["output_format"]
            output_path = os.path.join(character_dir, f"{sprite_name}.{output_format.lower()}")
            sprite_img.save(output_path, output_format)
            print(f"Saved sprite: {output_path}")
            
            # Add to asset manifest
            relative_path = os.path.join("assets/game/characters", character_name, f"{sprite_name}.{output_format.lower()}")
            self.asset_manifest["assets"][character_name][sprite_name] = relative_path
    
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
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(Path(input_dir).glob(ext))
        
        if not image_files:
            print(f"No image files found in {input_dir}")
            return
        
        # Process each file
        for image_path in image_files:
            self.process_character_sheet(str(image_path))
        
        # Save asset manifest
        self.save_asset_manifest()
        print("Asset processing complete!")

def main():
    parser = argparse.ArgumentParser(description="Enhanced Asset Processor for game sprites")
    parser.add_argument('--config', default='tools/asset_config.json', help='Path to config file')
    args = parser.parse_args()
    
    start_time = time.time()
    processor = EnhancedAssetProcessor(args.config)
    processor.process_all()
    print(f"Processing completed in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
