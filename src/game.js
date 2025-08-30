// Game class that handles the game loop and rendering
export class Game {
  constructor(canvas, ctx, player, inputHandler, assetLoader) {
    this.canvas = canvas;
    this.ctx = ctx;
    this.player = player;
    this.inputHandler = inputHandler;
    this.assetLoader = assetLoader;
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

    // Update player based on input
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
    if (this.availableBackgrounds.length > 0) {
      const backgroundName = this.availableBackgrounds[this.currentBackgroundIndex];
      const backgroundImg = this.assetLoader.getBackground(backgroundName);
      
      if (backgroundImg) {
        // Scale background to fit canvas while maintaining aspect ratio
        const canvasAspect = this.canvas.width / this.canvas.height;
        const imgAspect = backgroundImg.width / backgroundImg.height;
        
        let drawWidth, drawHeight, offsetX = 0, offsetY = 0;
        
        if (imgAspect > canvasAspect) {
          // Image is wider - scale to match height
          drawHeight = this.canvas.height;
          drawWidth = drawHeight * imgAspect;
          offsetX = (this.canvas.width - drawWidth) / 2;
        } else {
          // Image is taller - scale to match width
          drawWidth = this.canvas.width;
          drawHeight = drawWidth / imgAspect;
          offsetY = (this.canvas.height - drawHeight) / 2;
        }
        
        this.ctx.drawImage(backgroundImg, offsetX, offsetY, drawWidth, drawHeight);
      } else {
        // Fallback to gradient background
        this.drawFallbackBackground();
      }
    } else {
      // No backgrounds available - use fallback
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
    // Handle movement input
    if (this.inputHandler.keys.w) {
      this.player.moveUp(deltaTime);
    }
    if (this.inputHandler.keys.s) {
      this.player.moveDown(deltaTime);
    }
    if (this.inputHandler.keys.a) {
      this.player.moveLeft(deltaTime);
    }
    if (this.inputHandler.keys.d) {
      this.player.moveRight(deltaTime);
    }

    // Handle character switch
    if (this.inputHandler.keys.space && !this.inputHandler.keysPrevious.space) {
      this.player.switchCharacter();
    }

    // Update the previous keys state
    this.inputHandler.updatePreviousKeys();
    
    // Keep player within canvas bounds
    if (this.player.x < 0) this.player.x = 0;
    if (this.player.y < 0) this.player.y = 0;
    if (this.player.x > this.canvas.width - this.player.width) {
      this.player.x = this.canvas.width - this.player.width;
    }
    if (this.player.y > this.canvas.height - this.player.height) {
      this.player.y = this.canvas.height - this.player.height;
    }
  }
}
