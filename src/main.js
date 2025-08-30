// Entry point for Dixons Peak game
import { Game } from './game.js';
import { Player } from './entities/player.js';
import { InputHandler } from './systems/input.js';
import { AssetLoader } from './systems/asset-loader.js';
import { CameraSystem } from './systems/camera-system.js';
import { CollisionSystem } from './systems/collision-system.js';
import { SceneManager } from './systems/scene-manager.js';

document.addEventListener('DOMContentLoaded', async () => {
  console.log('Welcome to Dixons Peak!');
  
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  
  // Initialize asset loader and load assets
  const assetLoader = new AssetLoader();
  await assetLoader.loadAssets();
  
  // Create player
  const player = new Player(
    canvas.width / 2 - 32, 
    canvas.height / 2 - 32, 
    assetLoader
  );
  
  // Initialize input handler
  const inputHandler = new InputHandler();
  
  // Initialize new systems: camera, collision, scene manager
  const camera = new CameraSystem(canvas.width, canvas.height);
  const collision = new CollisionSystem();
  const sceneManager = new SceneManager(assetLoader, camera, collision);
  
  // Create game instance
  const game = new Game(canvas, ctx, player, inputHandler, assetLoader, camera, collision, sceneManager);
  
  // Start the game
  game.start();
});
