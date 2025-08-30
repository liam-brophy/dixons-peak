// Minimal CameraSystem for viewport clamping and coordinate conversion
export class CameraSystem {
  constructor(viewW = 640, viewH = 480) {
    this.w = viewW;
    this.h = viewH;
    this.x = 0;
    this.y = 0;
  }

  focusOn(px, py, bgMeta = {}) {
    const bgW = bgMeta.width || (bgMeta.image && bgMeta.image.width) || 0;
    const bgH = bgMeta.height || (bgMeta.image && bgMeta.image.height) || 0;

    // center camera on player
    let tx = Math.round(px - this.w / 2);
    let ty = Math.round(py - this.h / 2);

    // clamp
    tx = Math.max(0, Math.min(tx, Math.max(0, bgW - this.w)));
    ty = Math.max(0, Math.min(ty, Math.max(0, bgH - this.h)));

    this.x = tx;
    this.y = ty;
  }

  worldToScreen(wx, wy) {
    return { x: Math.round(wx - this.x), y: Math.round(wy - this.y) };
  }

  screenToWorld(sx, sy) {
    return { x: sx + this.x, y: sy + this.y };
  }
}
