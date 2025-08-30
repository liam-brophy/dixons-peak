// Game class that handles the game loop and rendering
export class Game {
  constructor(canvas, ctx, player, inputHandler) {
    this.canvas = canvas;
    this.ctx = ctx;
    this.player = player;
    this.inputHandler = inputHandler;
    this.lastTime = 0;
    this.running = false;
    
    // Game state
    this.fps = 0;
    this.frameCount = 0;
    this.fpsTimer = 0;
    this.showFps = false;
    
    // Add event listener for debug toggles
    window.addEventListener('keydown', this.handleDebugKeys.bind(this));
  }

  start() {
    this.running = true;
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
    
    // Draw checkerboard pattern to make transparency obvious
    this.drawCheckerboard();

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
  
  drawCheckerboard() {
    // Draw a subtle checkerboard pattern as background
    const tileSize = 20;
    this.ctx.fillStyle = '#f5f5f5';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    
    this.ctx.fillStyle = '#ebebeb';
    for (let y = 0; y < this.canvas.height; y += tileSize) {
      for (let x = 0; x < this.canvas.width; x += tileSize) {
        if ((x / tileSize + y / tileSize) % 2 === 0) {
          this.ctx.fillRect(x, y, tileSize, tileSize);
        }
      }
    }
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
    this.ctx.fillText('WASD: Move | Space: Switch Character', 10, this.canvas.height - 10);
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
