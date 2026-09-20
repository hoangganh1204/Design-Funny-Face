// Minimal Figma plugin API mock — exercises code.js end to end in Node.
let nodeCount = 0, imageCount = 0, textCount = 0, svgCount = 0;
const pages = [];

function baseNode(type) {
  return {
    type, name: '', x: 0, y: 0, width: 0, height: 0,
    _children: [],
    fills: [], strokes: [], strokeWeight: 1, strokeAlign: 'INSIDE', opacity: 1,
    resize(w, h) {
      if (typeof w !== 'number' || typeof h !== 'number' || Number.isNaN(w) || Number.isNaN(h))
        throw new Error(`${this.name}: bad resize(${w}, ${h})`);
      if (w <= 0 || h <= 0) throw new Error(`${this.name}: non-positive resize(${w}, ${h})`);
      this.width = w; this.height = h;
    },
    appendChild(n) {
      if (!n) throw new Error(`${this.name}: appendChild(null)`);
      n._parent = this; this._children.push(n); nodeCount++;
    },
    findOne() { return null; },
    remove() { const a = this._parent && this._parent._children; if (a) { const i = a.indexOf(this); if (i >= 0) a.splice(i, 1); } },
    loadAsync() { return Promise.resolve(); },
    setPluginData(k,v){ this._pd=this._pd||{}; this._pd[k]=v; },
    getPluginData(k){ return (this._pd||{})[k]||''; },
    get children() { return this._children; },
  };
}

const figma = {
  createFrame() { return baseNode('FRAME'); },
  createRectangle() { return baseNode('RECTANGLE'); },
  createEllipse() { return baseNode('ELLIPSE'); },
  createText() {
    const n = baseNode('TEXT');
    n._chars = '';
    Object.defineProperty(n, 'characters', {
      get() { return this._chars; },
      set(v) {
        if (!this.fontName) throw new Error('characters set before fontName');
        this._chars = v; textCount++;
      },
    });
    n.textAutoResize = 'NONE';
    return n;
  },
  createNodeFromSvg(svg) {
    if (typeof svg !== 'string' || svg.indexOf('<svg') !== 0)
      throw new Error('createNodeFromSvg: not an svg string');
    if (svg.indexOf('</svg>') === -1) throw new Error('createNodeFromSvg: unterminated svg');
    svgCount++;
    return baseNode('FRAME');
  },
  createPage() { const p = baseNode('PAGE'); pages.push(p); return p; },
  // figma.root — plugin dùng để dò/xoá frame của lần chạy trước (chạy lại phải idempotent).
  // Mock thiếu cái này thì plugin nào gọi figma.root sẽ crash trong verify.
  get root() { return { children: pages, name: 'Document', type: 'DOCUMENT' }; },
  createImage(bytes) {
    if (!(bytes instanceof Uint8Array) || bytes.length < 8)
      throw new Error('createImage: bad bytes');
    const isPng = bytes[0]===0x89 && bytes[1]===0x50 && bytes[2]===0x4e && bytes[3]===0x47;
    const isJpg = bytes[0]===0xff && bytes[1]===0xd8 && bytes[2]===0xff;
    if (!isPng && !isJpg) throw new Error('createImage: not a PNG/JPEG');
    imageCount++;
    return { hash: 'hash' + imageCount };
  },
  base64Decode(s) { return new Uint8Array(Buffer.from(s, 'base64')); },
  loadFontAsync: async () => {},
  loadAllPagesAsync: async () => {},
  setCurrentPageAsync: async () => {},
  viewport: { scrollAndZoomIntoView() {} },
  closePlugin(msg) { console.log('closePlugin:', msg); },
};

global.figma = figma;
global.__report = () => ({ nodeCount, imageCount, textCount, svgCount, pages });
