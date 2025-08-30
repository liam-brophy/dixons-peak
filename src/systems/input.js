// Input handler class to manage keyboard input
export class InputHandler {
  constructor() {
    this.keys = {
      w: false,
      a: false,
      s: false,
      d: false,
      space: false
    };
    
    // Previous state of keys for detecting key presses
    this.keysPrevious = {
      w: false,
      a: false,
      s: false,
      d: false,
      space: false
    };

    // Add event listeners
    window.addEventListener('keydown', this.handleKeyDown.bind(this));
    window.addEventListener('keyup', this.handleKeyUp.bind(this));
  }

  handleKeyDown(e) {
    switch (e.key.toLowerCase()) {
      case 'w':
        this.keys.w = true;
        break;
      case 'a':
        this.keys.a = true;
        break;
      case 's':
        this.keys.s = true;
        break;
      case 'd':
        this.keys.d = true;
        break;
      case ' ':
        this.keys.space = true;
        break;
    }
  }

  handleKeyUp(e) {
    switch (e.key.toLowerCase()) {
      case 'w':
        this.keys.w = false;
        break;
      case 'a':
        this.keys.a = false;
        break;
      case 's':
        this.keys.s = false;
        break;
      case 'd':
        this.keys.d = false;
        break;
      case ' ':
        this.keys.space = false;
        break;
    }
  }

  // Update previous keys state (called at the end of each frame)
  updatePreviousKeys() {
    this.keysPrevious.w = this.keys.w;
    this.keysPrevious.a = this.keys.a;
    this.keysPrevious.s = this.keys.s;
    this.keysPrevious.d = this.keys.d;
    this.keysPrevious.space = this.keys.space;
  }
}
