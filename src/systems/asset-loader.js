// Asset loader to handle loading and caching game assets
export class AssetLoader {
  constructor() {
    this.assets = {};
    this.sprites = {};
    this.backgrounds = {};
    this.loaded = false;
    this.loadingPromise = null;
  }

  async loadAssets() {
    // Only load assets once
    if (this.loadingPromise) {
      return this.loadingPromise;
    }

    this.loadingPromise = new Promise(async (resolve) => {
      try {
        console.log('🎮 Starting asset loading...');
        
        // Fetch the asset manifest
        const response = await fetch('/assets/game/asset_manifest.json');
        if (!response.ok) {
          throw new Error(`Failed to fetch manifest: ${response.status} ${response.statusText}`);
        }
        
        const manifest = await response.json();
        console.log('📄 Asset manifest loaded:', manifest);
        
        // Store asset paths
        this.assets = manifest.assets;
        
        // Load all sprites and backgrounds
        await this.loadSprites();
        await this.loadBackgrounds();
        
        this.loaded = true;
        console.log('✅ All assets loaded successfully');
        console.log('🖼️  Available sprites:', Object.keys(this.sprites));
        console.log('🌄 Available backgrounds:', Object.keys(this.backgrounds));
        resolve();
      } catch (error) {
        console.error('❌ Error loading assets:', error);
        // Create fallback assets
        this.createFallbackAssets();
        resolve();
      }
    });

    return this.loadingPromise;
  }

  createFallbackAssets() {
    // Create fallback assets if loading fails
    this.assets = {
      "Dixon_Water": {},
      "Dixon_Floral": {}
    };
    this.loaded = true;
  }

  async loadSprites() {
    // Only load character assets, not backgrounds
    const characterTypes = Object.keys(this.assets).filter(key => key !== 'backgrounds');
    const loadPromises = [];
    
    for (const characterType of characterTypes) {
      const characterAssets = this.assets[characterType];
      
      // Skip if this is not a character object
      if (!characterAssets || typeof characterAssets !== 'object') {
        continue;
      }
      
      for (const [assetName, assetInfo] of Object.entries(characterAssets)) {
        // Extract the path from the asset info object
        const assetPath = assetInfo.path || assetInfo;
        loadPromises.push(this.loadSprite(assetName, assetPath));
      }
    }
    
    console.log(`🎮 Loading sprites for ${characterTypes.length} characters...`);
    
    // Wait for all sprites to load
    await Promise.allSettled(loadPromises);
  }

  async loadBackgrounds() {
    // Load background assets if they exist
    if (this.assets.backgrounds) {
      const backgroundPromises = [];
      
      for (const [bgName, bgInfo] of Object.entries(this.assets.backgrounds)) {
        const bgPath = bgInfo.path || bgInfo;
        backgroundPromises.push(this.loadBackground(bgName, bgPath));
      }
      
      await Promise.allSettled(backgroundPromises);
    } else {
      console.log('📄 No backgrounds found in manifest');
    }
  }

  async loadBackground(name, path) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        this.backgrounds[name] = img;
        console.log(`✅ Background loaded: ${name}`);
        resolve(img);
      };
      img.onerror = (error) => {
        console.warn(`⚠️  Failed to load background ${name} from ${path}:`, error);
        resolve(null);
      };
      img.src = '/assets/game/' + path;
    });
  }

  async loadSprite(name, path) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        this.sprites[name] = img;
        console.log(`✅ Loaded sprite: ${name}`);
        resolve();
      };
      img.onerror = () => {
        console.error(`❌ Failed to load sprite: ${name} from path: ${path}`);
        resolve(); // Resolve anyway to continue loading other sprites
      };
      img.src = '/assets/game/' + path;
    });
  }

  // Get a sprite by its name
  getSprite(name) {
    return this.sprites[name] || null;
  }

  getBackground(name) {
    return this.backgrounds[name] || null;
  }

  getAllBackgrounds() {
    return Object.keys(this.backgrounds);
  }
}
