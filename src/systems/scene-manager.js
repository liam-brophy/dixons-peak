// SceneManager: handles loading backgrounds from AssetLoader, wiring camera and collision systems
export class SceneManager {
  constructor(assetLoader, camera, collision) {
    this.assetLoader = assetLoader;
    this.camera = camera;
    this.collision = collision;
    this.currentName = null;
    this.current = null; // { image, meta, path }
  }

  async loadScene(bgName, spawn = null) {
    const bgEntry = this.assetLoader.backgrounds[bgName] || null;

    // If asset loader hasn't loaded it yet, attempt to load from asset manifest
    if (!bgEntry) {
      const metaEntry = this.assetLoader.assets && this.assetLoader.assets.backgrounds && this.assetLoader.assets.backgrounds[bgName];
      if (!metaEntry) throw new Error('Background not found in asset manifest: ' + bgName);
      await this.assetLoader.loadBackground(bgName, metaEntry.path || metaEntry, metaEntry.meta || metaEntry.metaPath);
    }

    this.currentName = bgName;
    this.current = this.assetLoader.backgrounds[bgName];

    // if meta is present, feed into collision system
    this.collision.loadFromMeta(this.current.meta || {});

    // Configure camera clamping using meta dimensions if provided
    // (CameraSystem reads meta for width/height in focusOn)

    console.log(`📺 Scene loaded: ${bgName}`, { meta: this.current.meta });

    return { bg: this.current, spawn };
  }
}
