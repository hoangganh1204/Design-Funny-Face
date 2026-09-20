// Capture the plugin's scene tree to JSON (no real Figma). Runs plugin.js against
// a recording mock so we can render PNG previews with real fonts/assets.
// Usage: node capture-scene.js <plugin.js> > scene.json
const fs = require('fs');
const target = process.argv[2];
let src = fs.readFileSync(target, 'utf8');
// tag image fills with their asset name (imageFill knows the name)
src = src.replace(/function\s+imageFill\s*\([^)]*\)\s*\{/,
  (hit) => hit + ' global.__curImg = name;');   // regex: code.js viết dạng nén, không có dấu cách
// don't actually close
let PAGES = [];
function node(type) {
  return { type, name: '', x: 0, y: 0, width: 0, height: 0, fills: [], strokes: [],
    strokeWeight: 0, cornerRadius: undefined, topLeftRadius: undefined, children: [],
    characters: undefined, fontSize: undefined, fontName: undefined,
    textAlignHorizontal: undefined, textAlignVertical: undefined, opacity: 1, svg: undefined,
    appendChild(c) { this.children.push(c); },
    resize(w, h) { this.width = w; this.height = h; },
    set cornerRadiusAll(v) {}, setPluginData() {}, getPluginData() { return ''; }, remove() {} };
}
global.figma = {
  createFrame() { return node('FRAME'); },
  createRectangle() { return node('RECTANGLE'); },
  createEllipse() { return node('ELLIPSE'); },
  createText() { const n = node('TEXT'); return n; },
  createImage(bytes) { return { hash: global.__curImg }; },
  createNodeFromSvg(svg) { const n = node('SVG'); n.svg = svg; return n; },
  createPage() { const p = { name: '', children: [], appendChild(c) { this.children.push(c); }, setPluginData() {}, getPluginData() { return ''; }, loadAsync() { return Promise.resolve(); } }; PAGES.push(p); return p; },
  // figma.root — plugin dùng để dò/xoá frame của lần chạy trước (chạy lại phải idempotent).
  get root() { return { children: PAGES, name: 'Document', type: 'DOCUMENT' }; },
  base64Decode(s) { return Buffer.from(s, 'base64'); },
  loadFontAsync() { return Promise.resolve(); },
  loadAllPagesAsync() { return Promise.resolve(); },
  setCurrentPageAsync() { return Promise.resolve(); },
  viewport: { scrollAndZoomIntoView() {} },
  closePlugin() {},
};
// TEXT nodes need settable props; our node() already has plain fields. Figma uses
// assignment (t.characters=…, t.fontName=…) which just sets fields — fine.
// serialize after main() resolves
eval(src);
setTimeout(() => {
  const clean = (n) => ({ type: n.type, name: n.name, x: n.x, y: n.y, w: n.width, h: n.height,
    fills: n.fills, strokes: n.strokes, strokeWeight: n.strokeWeight,
    cornerRadius: n.cornerRadius, topLeftRadius: n.topLeftRadius,
    characters: n.characters, fontSize: n.fontSize, fontName: n.fontName,
    align: n.textAlignHorizontal, valign: n.textAlignVertical, opacity: n.opacity,
    rotation: n.rotation || 0, svg: n.svg, children: (n.children || []).map(clean) });
  const out = PAGES.map((p) => ({ name: p.name, frames: p.children.map(clean) }));
  process.stdout.write(JSON.stringify(out));
}, 300);
