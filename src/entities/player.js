// Player class that handles player movement and rendering
export class Player {
  constructor(x, y, assetLoader) {
    this.x = x;
    this.y = y;
    this.width = 96;
    this.height = 96;
    this.speed = 0.2;
    this.direction = 'down'; // down, up, left, right
    this.state = 'idle'; // idle, walk, jump, fall
    
    // All available characters
    this.availableCharacters = ['Dixon_Water', 'Dixon_Floral', 'alien_dude', 'ghost_dude'];
    this.currentCharacterIndex = 0;
    this.characterType = this.availableCharacters[this.currentCharacterIndex];
    
    this.assetLoader = assetLoader;
    this.animationFrame = 0;
    this.animationTimer = 0;
    this.animationSpeed = 150; // milliseconds per frame
    
    // Idle animation properties
    this.idleTimer = 0;
    this.idlePhase = 0;
    this.idleFrames = 3;
    this.idleAnimationSpeed = 800; // slower for breathing effect
    
    // Scale for idle "breathing" animation
    this.idleScale = 1.0;
    this.minIdleScale = 0.98;
    this.maxIdleScale = 1.02;
    
    // Debug info
    this.debug = false;
  }

  // Movement methods
  moveUp(deltaTime) {
    this.y -= this.speed * deltaTime;
    this.direction = 'up';
    this.state = 'walk';
  }

  moveDown(deltaTime) {
    this.y += this.speed * deltaTime;
    this.direction = 'down';
    this.state = 'walk';
  }

  moveLeft(deltaTime) {
    this.x -= this.speed * deltaTime;
    this.direction = 'left';
    this.state = 'walk';
  }

  moveRight(deltaTime) {
    this.x += this.speed * deltaTime;
    this.direction = 'right';
    this.state = 'walk';
  }

  // Switch between character types
  switchCharacter() {
    this.currentCharacterIndex = (this.currentCharacterIndex + 1) % this.availableCharacters.length;
    this.characterType = this.availableCharacters[this.currentCharacterIndex];
    console.log(`Switched to ${this.characterType} (${this.currentCharacterIndex + 1}/${this.availableCharacters.length})`);
  }

  // Update animation frame
  updateAnimation(deltaTime) {
    this.animationTimer += deltaTime;
    
    if (this.state === 'idle') {
      // Update idle animation (breathing effect)
      this.idleTimer += deltaTime;
      if (this.idleTimer >= this.idleAnimationSpeed) {
        this.idleTimer = 0;
        this.idlePhase = (this.idlePhase + 1) % this.idleFrames;
        
        // Calculate a smooth sine wave for the idle scale
        const phase = this.idlePhase / this.idleFrames * Math.PI * 2;
        this.idleScale = this.minIdleScale + 
                         (Math.sin(phase) + 1) / 2 * 
                         (this.maxIdleScale - this.minIdleScale);
      }
      this.animationFrame = 0;
    } else {
      // Regular walking animation
      if (this.animationTimer >= this.animationSpeed) {
        this.animationTimer = 0;
        this.animationFrame = (this.animationFrame + 1) % 4; // 4 frames per animation
      }
      // Reset idle animation when moving
      this.idleScale = 1.0;
      this.idleTimer = 0;
    }
  }

  // Reset state to idle (called each frame before processing movement)
  resetState() {
    this.state = 'idle';
  }

  // Get the sprite name based on current state
  getSpriteName() {
    return `${this.characterType}_${this.state}_${this.direction}`;
  }

  // Render the player
  render(ctx) {
    // Update animation
    this.updateAnimation(16); // Use a fixed deltaTime for simplicity

    // Get the current sprite
    const spriteName = this.getSpriteName();
    const sprite = this.assetLoader.getSprite(spriteName);
    
    // Debug: Log sprite requests
    if (!sprite && this._lastLoggedSprite !== spriteName) {
      console.log(`🔍 Requesting sprite: "${spriteName}"`);
      console.log('Available sprites:', Object.keys(this.assetLoader.sprites));
      this._lastLoggedSprite = spriteName;
    }
    
    if (sprite) {
      // Calculate scaled dimensions for idle breathing animation
      let renderWidth = this.width;
      let renderHeight = this.height;
      
      if (this.state === 'idle') {
        // Apply slight scaling for breathing effect
        renderWidth = this.width * this.idleScale;
        renderHeight = this.height * this.idleScale;
      }
      
      // Calculate position adjustments to keep character centered during scaling
      const xOffset = (this.width - renderWidth) / 2;
      const yOffset = (this.height - renderHeight) / 2;
      
      ctx.drawImage(sprite, 
                   this.x + xOffset, 
                   this.y + yOffset, 
                   renderWidth, 
                   renderHeight);
      
      if (this.debug) {
        // Draw sprite name for debugging
        ctx.font = '10px Arial';
        ctx.fillStyle = 'black';
        ctx.fillText(spriteName, this.x, this.y - 5);
        
        // Draw bounding box
        ctx.strokeStyle = 'red';
        ctx.strokeRect(this.x, this.y, this.width, this.height);
      }
    } else {
      // Fallback if sprite not loaded - color-coded based on character type
      let color;
      switch (this.characterType) {
        case 'Dixon_Water':
          color = 'rgba(0, 100, 255, 0.7)'; // Blue
          break;
        case 'Dixon_Floral':
          color = 'rgba(50, 200, 50, 0.7)'; // Green
          break;
        case 'alien_dude':
          color = 'rgba(128, 0, 128, 0.7)'; // Purple
          break;
        case 'ghost_dude':
          color = 'rgba(255, 255, 255, 0.7)'; // White
          break;
        default:
          color = 'rgba(128, 128, 128, 0.7)'; // Gray
      }
      ctx.fillStyle = color;
      ctx.fillRect(this.x, this.y, this.width, this.height);
      
      // Draw directional indicator
      ctx.fillStyle = 'black';
      
      // Position indicator based on direction
      const center = {
        x: this.x + this.width / 2,
        y: this.y + this.height / 2
      };
      const radius = this.width / 6;
      
      switch (this.direction) {
        case 'up':
          ctx.beginPath();
          ctx.moveTo(center.x, center.y - radius);
          ctx.lineTo(center.x - radius, center.y + radius);
          ctx.lineTo(center.x + radius, center.y + radius);
          ctx.fill();
          break;
        case 'down':
          ctx.beginPath();
          ctx.moveTo(center.x, center.y + radius);
          ctx.lineTo(center.x - radius, center.y - radius);
          ctx.lineTo(center.x + radius, center.y - radius);
          ctx.fill();
          break;
        case 'left':
          ctx.beginPath();
          ctx.moveTo(center.x - radius, center.y);
          ctx.lineTo(center.x + radius, center.y - radius);
          ctx.lineTo(center.x + radius, center.y + radius);
          ctx.fill();
          break;
        case 'right':
          ctx.beginPath();
          ctx.moveTo(center.x + radius, center.y);
          ctx.lineTo(center.x - radius, center.y - radius);
          ctx.lineTo(center.x - radius, center.y + radius);
          ctx.fill();
          break;
      }
    }

    // Reset state to idle for next frame (will be set to walk again if moving)
    this.resetState();
  }
}
