// Game class that handles the game loop and rendering
export class Game {
  constructor(canvas, ctx, player, inputHandler, assetLoader, camera = null, collision = null, sceneManager = null) {
    this.canvas = canvas;
    this.ctx = ctx;
    this.player = player;
    this.inputHandler = inputHandler;
    this.assetLoader = assetLoader;
    this.camera = camera;
    this.collision = collision;
    this.sceneManager = sceneManager;
    this.lastTime = 0;
    this.running = false;
    
    // Game state
    this.fps = 0;
    this.frameCount = 0;
    this.fpsTimer = 0;
    this.showFps = false;
    
    // Background management
    this.currentBackgroundIndex = 0;
    this.availableBackgrounds = [];
    
    // Add event listener for debug toggles
    window.addEventListener('keydown', this.handleDebugKeys.bind(this));
  }

  start() {
    this.running = true;
    
    // Initialize available backgrounds
    this.availableBackgrounds = this.assetLoader.getAllBackgrounds();
    if (this.availableBackgrounds.length > 0) {
      console.log('🌄 Available backgrounds:', this.availableBackgrounds);
    }

    // If scene manager exists, load the first scene
    if (this.sceneManager && this.availableBackgrounds.length > 0) {
      const first = this.availableBackgrounds[0];
      this.sceneManager.loadScene(first).then(() => {
        // Optionally center camera on player spawn if meta provides a spawn
      }).catch(e => console.warn('Failed to load initial scene', e));
    }
    
    requestAnimationFrame(this.gameLoop.bind(this));
  }

  stop() {
    this.running = false;
  }
  
  handleDebugKeys(e) {
    // Debug controls
    if (e.key === 'f') {
      this.showFps = !this.showFps;
    }
    
    // Background switching with B key
    if (e.key === 'b' && this.availableBackgrounds.length > 0) {
      this.currentBackgroundIndex = (this.currentBackgroundIndex + 1) % this.availableBackgrounds.length;
      const currentBg = this.availableBackgrounds[this.currentBackgroundIndex];
      console.log(`🌄 Switched to background: ${currentBg}`);
    }
  }

  gameLoop(timestamp) {
    // Calculate delta time and FPS
    const deltaTime = timestamp - this.lastTime;
    this.lastTime = timestamp;
    
    // Update FPS counter
    this.fpsTimer += deltaTime;
    this.frameCount++;
    if (this.fpsTimer >= 1000) {
      this.fps = this.frameCount;
      this.frameCount = 0;
      this.fpsTimer = 0;
    }

    // Clear the canvas
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Draw background
  this.drawBackground();

  // Update player based on input (with collision and scene interactions)
  this.updatePlayer(deltaTime);

    // Render player
    this.player.render(this.ctx);
    
    // Draw HUD and debug info
    this.drawHUD();

    // Continue the game loop if running
    if (this.running) {
      requestAnimationFrame(this.gameLoop.bind(this));
    }
  }
  
  drawBackground() {
    // Draw background image if available, otherwise use a subtle color
    if (this.sceneManager && this.sceneManager.current) {
      const bgEntry = this.sceneManager.current; // { image, meta, path }
      const img = bgEntry.image;
      const meta = bgEntry.meta || {};

      // We want to draw only the camera viewport of the background
      if (this.camera && img) {
        const sx = this.camera.x;
        const sy = this.camera.y;
        const sw = this.camera.w;
        const sh = this.camera.h;

        // Draw portion of the background to fill canvas
        this.ctx.drawImage(img, sx, sy, sw, sh, 0, 0, this.canvas.width, this.canvas.height);
        return;
      }

      // Fallback: old behavior - draw full image scaled
      if (img) {
        this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
        return;
      }

      this.drawFallbackBackground();
    } else {
      // No scene manager or scene loaded - fallback
      this.drawFallbackBackground();
    }
  }
  
  drawFallbackBackground() {
    // Draw a subtle gradient background
    const gradient = this.ctx.createLinearGradient(0, 0, 0, this.canvas.height);
    gradient.addColorStop(0, '#87CEEB');  // Sky blue
    gradient.addColorStop(1, '#98FB98');  // Pale green
    this.ctx.fillStyle = gradient;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }
  
  drawHUD() {
    // Only show FPS if debug is enabled
    if (this.showFps) {
      this.ctx.font = '12px Arial';
      this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      this.ctx.fillText(`FPS: ${this.fps}`, this.canvas.width - 70, 20);
    }
    
    // Draw minimal controls reminder at the bottom
    this.ctx.font = '12px Arial';
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
    this.ctx.fillText('WASD: Move | Space: Switch Character | B: Switch Background', 10, this.canvas.height - 10);
    
    // Show current character info at the top
    this.ctx.font = '14px Arial';
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
    const charIndex = this.player.currentCharacterIndex + 1;
    const totalChars = this.player.availableCharacters.length;
    const characterName = this.player.characterType.replace(/_/g, ' ');
    this.ctx.fillText(`Character: ${characterName} (${charIndex}/${totalChars})`, 10, 25);
    
    // Show background info if available
    if (this.availableBackgrounds.length > 0) {
      const bgIndex = this.currentBackgroundIndex + 1;
      const totalBgs = this.availableBackgrounds.length;
      const bgName = this.availableBackgrounds[this.currentBackgroundIndex].replace(/_/g, ' ');
      this.ctx.fillText(`Background: ${bgName} (${bgIndex}/${totalBgs})`, 10, 45);
    }
  }

  updatePlayer(deltaTime) {
    // Handle movement input - compute tentative movement and test collision
    const move = { x: 0, y: 0 };
    if (this.inputHandler.keys.w) move.y -= 1;
    if (this.inputHandler.keys.s) move.y += 1;
    if (this.inputHandler.keys.a) move.x -= 1;
    if (this.inputHandler.keys.d) move.x += 1;

    // Normalize diagonal movement
    if (move.x !== 0 && move.y !== 0) {
      const inv = Math.sqrt(0.5);
      move.x *= inv;
      move.y *= inv;
    }

    // Compute candidate position
    const candidateX = this.player.x + move.x * this.player.speed * deltaTime;
    const candidateY = this.player.y + move.y * this.player.speed * deltaTime;
    const candidateRect = { x: candidateX, y: candidateY, w: this.player.width, h: this.player.height };

    let blocked = false;
    if (this.collision) {
      blocked = this.collision.checkMovement(candidateRect);
    }

    if (!blocked) {
      // Apply movement
      this.player.x = candidateX;
      this.player.y = candidateY;

      // Update player direction/state
      if (move.x !== 0 || move.y !== 0) {
        this.player.state = 'walk';
        if (Math.abs(move.x) > Math.abs(move.y)) {
          this.player.direction = move.x > 0 ? 'right' : 'left';
        } else if (move.y !== 0) {
          this.player.direction = move.y > 0 ? 'down' : 'up';
        }
      }
    } else {
      this.player.state = 'idle';
    }

    // Interaction / scene transitions
    if (this.collision && this.sceneManager) {
      const playerRect = { x: this.player.x, y: this.player.y, w: this.player.width, h: this.player.height };
      const interactive = this.collision.findInteractiveOverlap(playerRect);
      if (interactive) {
        // If space pressed (or auto-enter), transition
        if (this.inputHandler.keys.space && !this.inputHandler.keysPrevious.space) {
          if (interactive.type === 'door' && interactive.dest) {
            // Load destination scene and move player to spawn
            this.sceneManager.loadScene(interactive.dest, interactive.spawn).then(({ bg, spawn }) => {
              if (spawn) {
                this.player.x = spawn.x;
                this.player.y = spawn.y;
              }
            }).catch(e => console.warn('Failed to load scene from door', e));
          }
        }
      }
    }

    // Handle character switch
    if (this.inputHandler.keys.space && !this.inputHandler.keysPrevious.space) {
      this.player.switchCharacter();
    }

    // Update the previous keys state
    this.inputHandler.updatePreviousKeys();
    
    // Keep player within canvas bounds
    // If camera exists, convert world limits using camera's current scene meta as bounds
    if (this.camera && this.sceneManager && this.sceneManager.current && this.sceneManager.current.meta) {
      const meta = this.sceneManager.current.meta;
      // Clamp player to background bounds
      this.player.x = Math.max(0, Math.min(this.player.x, (meta.width || this.canvas.width) - this.player.width));
      this.player.y = Math.max(0, Math.min(this.player.y, (meta.height || this.canvas.height) - this.player.height));
      // Update camera to follow player
      this.camera.focusOn(this.player.x + this.player.width / 2, this.player.y + this.player.height / 2, meta);
    } else {
      if (this.player.x < 0) this.player.x = 0;
      if (this.player.y < 0) this.player.y = 0;
      if (this.player.x > this.canvas.width - this.player.width) {
        this.player.x = this.canvas.width - this.player.width;
      }
      if (this.player.y > this.canvas.height - this.player.height) {
        this.player.y = this.canvas.height - this.player.height;
      }
      // If camera exists but no meta, center camera at player's position (no clamping)
      if (this.camera) {
        this.camera.focusOn(this.player.x + this.player.width / 2, this.player.y + this.player.height / 2, {});
      }
    }
  }
}
