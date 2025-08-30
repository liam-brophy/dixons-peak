// Asset loader to handle loading and caching game assets
export class AssetLoader {
  constructor() {
    this.assets = {};
    this.sprites = {};
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
        
        // Load all sprites
        await this.loadSprites();
        
        this.loaded = true;
        console.log('✅ All assets loaded successfully');
        console.log('🖼️  Available sprites:', Object.keys(this.sprites));
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
    const characterTypes = Object.keys(this.assets);
    const loadPromises = [];
    
    for (const characterType of characterTypes) {
      const characterAssets = this.assets[characterType];
      
      for (const [assetName, assetInfo] of Object.entries(characterAssets)) {
        // Extract the path from the asset info object
        const assetPath = assetInfo.path || assetInfo;
        loadPromises.push(this.loadSprite(assetName, assetPath));
      }
    }
    
    // Wait for all sprites to load
    await Promise.allSettled(loadPromises);
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
  getSprite(spriteName) {
    // Return the sprite if it exists
    if (this.sprites[spriteName]) {
      return this.sprites[spriteName];
    }
    
    return null;
  }
}
