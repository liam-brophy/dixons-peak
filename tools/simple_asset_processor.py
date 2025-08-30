#!/usr/bin/env python3
"""
Simple Character Sheet Asset Processor
Extracts sprites from character sheets without relying on rembg
"""

import os
import json
from pathlib import Path
from PIL import Image
import cv2
import numpy as np
import argparse
from typing import List, Tuple, Dict

class SimpleAssetProcessor:
    def __init__(self, config_file: str = "asset_config.json"):
        """Initialize the asset processor with configuration"""
        self.config = self.load_config(config_file)
        self.setup_directories()
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file or create default"""
        default_config = {
            "input_dir": "assets/raw/character_sheets",
            "output_dir": "assets/game",
            "sprite_size": [64, 64],  # [width, height] in pixels
            "grid_detection": {
                "auto_detect": False,
                "manual_rows": 4,
                "manual_cols": 4
            },
            "naming": {
                "character_name": "character",
                "actions": ["idle", "walk", "jump", "fall"],
                "directions": ["left", "right", "up", "down"]
            },
            "background_removal": {
                "method": "color_key",
                "color_key": [255, 255, 255],
                "tolerance": 30
            },
            "output_format": "PNG",
            "padding": 2  # pixels of padding around each sprite
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults for missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            # Create default config file
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default config file: {config_file}")
            return default_config
    
    def setup_directories(self):
        """Create necessary directories"""
        Path(self.config["input_dir"]).mkdir(exist_ok=True)
        Path(self.config["output_dir"]).mkdir(exist_ok=True)
        
        # Create subdirectories for different asset types
        for subdir in ["characters", "items", "ui", "backgrounds"]:
            Path(self.config["output_dir"], subdir).mkdir(exist_ok=True)
    
    def remove_background_color_key(self, image: Image.Image) -> Image.Image:
        """Remove background using color key method"""
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
        
        return Image.fromarray(data, 'RGBA')
    
    def detect_grid(self, image: Image.Image) -> Tuple[int, int]:
        """Automatically detect grid dimensions in character sheet"""
        if not self.config["grid_detection"]["auto_detect"]:
            return (self.config["grid_detection"]["manual_rows"], 
                   self.config["grid_detection"]["manual_cols"])
        
        # Simple grid detection based on manual settings
        return (self.config["grid_detection"]["manual_rows"], 
               self.config["grid_detection"]["manual_cols"])
    
    def extract_sprites(self, image: Image.Image, rows: int, cols: int) -> List[Image.Image]:
        """Extract individual sprites from character sheet grid"""
        sprites = []
        width, height = image.size
        sprite_width = width // cols
        sprite_height = height // rows
        
        for row in range(rows):
            for col in range(cols):
                x = col * sprite_width
                y = row * sprite_height
                
                # Extract sprite with padding
                sprite = image.crop((
                    x + self.config["padding"],
                    y + self.config["padding"],
                    x + sprite_width - self.config["padding"],
                    y + sprite_height - self.config["padding"]
                ))
                
                # Resize to target size if specified
                target_size = tuple(self.config["sprite_size"])
                if target_size != (sprite_width, sprite_height):
                    sprite = sprite.resize(target_size, Image.Resampling.LANCZOS)
                
                sprites.append(sprite)
        
        return sprites
    
    def generate_sprite_names(self, num_sprites: int, character_name: str) -> List[str]:
        """Generate consistent names for sprites based on configuration"""
        names = []
        actions = self.config["naming"]["actions"]
        directions = self.config["naming"]["directions"]
        
        # Simple naming strategy: cycle through actions and directions
        for i in range(num_sprites):
            action_idx = i // len(directions)
            direction_idx = i % len(directions)
            
            if action_idx < len(actions):
                action = actions[action_idx]
                direction = directions[direction_idx]
                name = f"{character_name}_{action}_{direction}"
            else:
                # Fallback for extra sprites
                name = f"{character_name}_sprite_{i:03d}"
            
            names.append(name)
        
        return names
    
    def process_character_sheet(self, image_path: str, character_name: str = None) -> Dict[str, str]:
        """Process a single character sheet"""
        print(f"Processing: {image_path}")
        
        # Load image
        image = Image.open(image_path)
        
        # Extract character name from filename if not provided
        if character_name is None:
            character_name = Path(image_path).stem
        
        # Remove background
        print("Removing background...")
        processed_image = self.remove_background_color_key(image)
        
        # Detect grid dimensions
        print("Detecting grid...")
        rows, cols = self.detect_grid(processed_image)
        print(f"Detected grid: {rows}x{cols}")
        
        # Extract sprites
        print("Extracting sprites...")
        sprites = self.extract_sprites(processed_image, rows, cols)
        
        # Generate names
        sprite_names = self.generate_sprite_names(len(sprites), character_name)
        
        # Save sprites
        output_paths = {}
        character_dir = Path(self.config["output_dir"], "characters", character_name)
        character_dir.mkdir(exist_ok=True)
        
        for sprite, name in zip(sprites, sprite_names):
            output_path = character_dir / f"{name}.png"
            sprite.save(output_path, self.config["output_format"])
            output_paths[name] = str(output_path)
            print(f"Saved: {output_path}")
        
        return output_paths
    
    def batch_process(self, input_directory: str = None) -> Dict[str, Dict[str, str]]:
        """Process all character sheets in input directory"""
        if input_directory is None:
            input_directory = self.config["input_dir"]
        
        input_path = Path(input_directory)
        if not input_path.exists():
            print(f"Input directory {input_directory} does not exist!")
            return {}
        
        # Find all image files
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        image_files = [f for f in input_path.iterdir() 
                      if f.suffix.lower() in image_extensions]
        
        if not image_files:
            print(f"No image files found in {input_directory}")
            return {}
        
        print(f"Found {len(image_files)} image files to process")
        
        all_results = {}
        for image_file in image_files:
            try:
                character_name = image_file.stem
                results = self.process_character_sheet(str(image_file), character_name)
                all_results[character_name] = results
            except Exception as e:
                print(f"Error processing {image_file}: {e}")
        
        return all_results
    
    def create_asset_manifest(self, processed_assets: Dict[str, Dict[str, str]]):
        """Create a JSON manifest of all processed assets for game code"""
        manifest = {
            "version": "1.0",
            "assets": processed_assets,
            "sprite_size": self.config["sprite_size"],
            "format": self.config["output_format"]
        }
        
        manifest_path = Path(self.config["output_dir"], "asset_manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"Asset manifest created: {manifest_path}")

def main():
    parser = argparse.ArgumentParser(description="Process character sheets for game development")
    parser.add_argument("--input", "-i", help="Input directory containing character sheets")
    parser.add_argument("--character", "-c", help="Process single character sheet file")
    parser.add_argument("--name", "-n", help="Character name for single file processing")
    parser.add_argument("--config", help="Configuration file path", default="asset_config.json")
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = SimpleAssetProcessor(args.config)
    
    if args.character:
        # Process single file
        results = processor.process_character_sheet(args.character, args.name)
        print(f"Processed {len(results)} sprites")
    else:
        # Batch process
        input_dir = args.input or processor.config["input_dir"]
        results = processor.batch_process(input_dir)
        
        if results:
            processor.create_asset_manifest(results)
            total_sprites = sum(len(sprites) for sprites in results.values())
            print(f"\nProcessing complete!")
            print(f"Characters processed: {len(results)}")
            print(f"Total sprites created: {total_sprites}")
        else:
            print("No assets were processed.")

if __name__ == "__main__":
    main()
