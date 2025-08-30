// Simple CollisionSystem: loads collision boxes and interactive zones from background meta
export class CollisionSystem {
  constructor() {
    this.colliders = [];
    this.interactives = [];
  }

  loadFromMeta(meta = {}) {
    this.colliders = (meta.collision || []).map(c => ({
      x: c.x, y: c.y, w: c.w || c.width, h: c.h || c.height
    }));

    this.interactives = (meta.interactive || []).map(it => ({
      ...it,
      rect: it.rect || it.area || it.zone
    }));
  }

  // axis-aligned bounding box intersection
  intersectsRect(a, b) {
    return !(a.x + a.w <= b.x || a.x >= b.x + b.w || a.y + a.h <= b.y || a.y >= b.y + b.h);
  }

  checkMovement(playerRect) {
    for (const col of this.colliders) {
      if (this.intersectsRect(playerRect, col)) return true;
    }
    return false;
  }

  findInteractiveOverlap(playerRect) {
    for (const it of this.interactives) {
      const rect = it.rect || it;
      if (this.intersectsRect(playerRect, rect)) return it;
    }
    return null;
  }
}
