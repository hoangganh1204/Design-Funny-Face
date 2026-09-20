#!/usr/bin/env python3
"""Render the captured scene tree (scene.json) to PNG previews using the APK's
real TTF fonts + exported assets. Eyeball check per playbook 1.2 (visual verify).
Run after: node script/capture-scene.js figma/v1/plugin.js > scene.json
"""
import os, json, glob, math
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.environ.get('SCRATCH') or os.path.join(ROOT, 'build')
SCENE = os.environ.get('SCENE') or os.path.join(SCRATCH, 'scene.json')
OUT = os.environ.get('OUT') or os.path.join(SCRATCH, 'preview')
ASSETS = os.environ.get('ASSETS_DIR') or os.path.join(ROOT, 'assets/v1')
FONTDIR = os.path.join(ROOT, 'decompiled/resources/res/font')

# Figma family (+style) -> APK ttf file
FONT_MAP = {   # Funny Face: res/font/*.ttf (sinh từ inventory thật, không phải template)
  ('Lato','Thin'):'lato_thin_100.ttf', ('Lato','Light'):'lato_light_300.ttf',
  ('Lato','Regular'):'lato_regular_400.ttf', ('Lato','SemiBold'):'lato_semibold_600.ttf',
  ('Lato','Bold'):'lato_bold_700.ttf', ('Lato','Black'):'lato_black_900.ttf',
  ('Inter','Regular'):'inter_regular.ttf', ('Inter','Bold'):'inter_bold.ttf',
  ('Montserrat','Regular'):'montserrat_regular.ttf',
  ('Montserrat','SemiBold'):'montserrat_seminold.ttf',   # tên file sai chính tả trong APK
  ('Nunito','Bold'):'nunito_bold.ttf', ('Nunito','Black'):'nunito_black.ttf',
  ('Onest','Bold'):'onest_bold.ttf',
  ('Poppins','Regular'):'poppins_regular.ttf', ('Poppins','Medium'):'poppins_medium.ttf',
  ('Roboto','Medium'):'roboto_medium_numbers.ttf',
}
_fontcache = {}
def load_font(fam, style, size):
    size = max(6, int(round(size)))
    key = (fam, style, size)
    if key in _fontcache: return _fontcache[key]
    fn = FONT_MAP.get((fam, style)) or FONT_MAP.get((fam, 'Regular')) or 'lato_regular_400.ttf'
    try: f = ImageFont.truetype(os.path.join(FONTDIR, fn), size)
    except Exception: f = ImageFont.load_default()
    _fontcache[key] = f; return f

# --- Font APK bi SUBSET: lato_regular_400.ttf trong APK THIEU cac glyph tieng Viet
# (d-gach, a-nang, a-huyen-mu...). Figma dung Lato tu Google Fonts nen KHONG bi;
# nhung anh preview ve bang chinh TTF cua APK nen chu tieng Viet ra o .notdef.
# => Do glyph thieu, chu nao thieu thi ve bang font he thong co du tieng Viet.
_FALLBACK = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
_FALLBACK_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
_notdef_cache = {}


def _notdef_sig(font):
    k = id(font)
    if k not in _notdef_cache:
        import hashlib
        im = Image.new('L', (48, 48), 0)
        ImageDraw.Draw(im).text((4, 2), '\u6f22', font=font, fill=255)
        _notdef_cache[k] = hashlib.md5(im.tobytes()).hexdigest()
    return _notdef_cache[k]


_covers_cache = {}


def _covers(font, ch):
    key = (id(font), ch)
    if key not in _covers_cache:
        import hashlib
        im = Image.new('L', (48, 48), 0)
        ImageDraw.Draw(im).text((4, 2), ch, font=font, fill=255)
        _covers_cache[key] = hashlib.md5(im.tobytes()).hexdigest() != _notdef_sig(font)
    return _covers_cache[key]


def font_for(fam, style, size, chars):
    """Font cua APK neu phu du chu; thieu glyph nao thi lui ve font he thong."""
    f = load_font(fam, style, size)
    bad = [c for c in set(chars) if ord(c) > 127 and not _covers(f, c)]
    if not bad:
        return f
    path = _FALLBACK_BOLD if 'Bold' in (style or '') or 'Black' in (style or '') else _FALLBACK
    try:
        return ImageFont.truetype(path, max(6, int(round(size))))
    except Exception:
        return f


_assetcache = {}
def load_asset(name):
    if name in _assetcache: return _assetcache[name]
    hits = glob.glob(os.path.join(ASSETS, '**', name + '.png'), recursive=True)
    im = Image.open(hits[0]).convert('RGBA') if hits else None
    _assetcache[name] = im; return im

def col(paint):
    c = paint.get('color', {}); a = paint.get('opacity', 1)
    return (int(c.get('r', 0) * 255), int(c.get('g', 0) * 255), int(c.get('b', 0) * 255), int(a * 255))

def rrect(draw, box, r, fill=None, outline=None, width=1):
    r = max(0, min(int(r or 0), (box[2] - box[0]) // 2, (box[3] - box[1]) // 2))
    if box[2] <= box[0] or box[3] <= box[1]: return
    if r > 0: draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)
    else: draw.rectangle(box, fill=fill, outline=outline, width=width)

def cover_contain(im, w, h, mode):
    iw, ih = im.size; s = max(w / iw, h / ih) if mode == 'FILL' else min(w / iw, h / ih)
    nw, nh = max(1, int(iw * s)), max(1, int(ih * s))
    im = im.resize((nw, nh), Image.LANCZOS)
    if mode == 'FILL':  # center-crop
        l, t = (nw - w) // 2, (nh - h) // 2
        return im.crop((l, t, l + w, t + h))
    return im  # contain (paste centered by caller)

def wrap(draw, txt, font, maxw):
    out = []
    for para in txt.split('\n'):
        words = para.split(' '); line = ''
        for w in words:
            t = (line + ' ' + w).strip()
            if draw.textlength(t, font=font) <= maxw or not line: line = t
            else: out.append(line); line = w
        out.append(line)
    return out

def paint(node, base, draw, ox, oy):
    ax, ay = ox + node.get('x', 0), oy + node.get('y', 0)
    w, h = node.get('w', 0), node.get('h', 0)
    box = [ax, ay, ax + w, ay + h]
    t = node.get('type'); rad = node.get('cornerRadius') or node.get('topLeftRadius') or 0
    fills = node.get('fills') or []
    if t in ('FRAME', 'RECTANGLE', 'ELLIPSE'):
        for p in fills:
            if p.get('type') == 'SOLID':
                c = col(p)
                if c[3] >= 255:
                    if t == 'ELLIPSE': draw.ellipse(box, fill=c)
                    else: rrect(draw, box, rad, fill=c)
                else:
                    # ImageDraw GHI ĐÈ pixel, KHÔNG alpha-blend -> vẽ thẳng một fill bán
                    # trong suốt sẽ XOÁ ảnh bên dưới (gặp thật: lớp dim 35% ở màn Result
                    # làm ô video thành đen đặc). Phải vẽ ra lớp riêng rồi composite.
                    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
                    ld = ImageDraw.Draw(layer)
                    if t == 'ELLIPSE': ld.ellipse(box, fill=c)
                    else: rrect(ld, box, rad, fill=c)
                    base.alpha_composite(layer)
            elif p.get('type', '').startswith('GRADIENT'):
                stops = p.get('gradientStops', [])
                c0 = stops[0]['color'] if stops else {'r': .5, 'g': .5, 'b': .5}
                c1 = stops[-1]['color'] if stops else c0
                grad = Image.new('RGBA', (max(1, int(w)), max(1, int(h))))
                gd = ImageDraw.Draw(grad)
                # Alpha cua tung diem dung PHAI duoc noi suy. Truoc day ep cung 255 nen
                # moi gradient trong suot (dai chuyen lam nen chu de len anh) bi ve thanh
                # mang DAC -> anh preview khac han ket qua that trong Figma.
                a0 = c0.get('a', 1); a1 = c1.get('a', 1)
                for yy in range(int(h)):
                    f = yy / max(1, h - 1)
                    cc = (int((c0['r'] + (c1['r'] - c0['r']) * f) * 255), int((c0['g'] + (c1['g'] - c0['g']) * f) * 255), int((c0['b'] + (c1['b'] - c0['b']) * f) * 255), int((a0 + (a1 - a0) * f) * 255))
                    gd.line([(0, yy), (int(w), yy)], fill=cc)
                base.alpha_composite(grad, (int(ax), int(ay)))
            elif p.get('type') == 'IMAGE':
                im = load_asset(p.get('imageHash'))
                if im and w > 0 and h > 0:
                    mode = p.get('scaleMode', 'FILL')
                    if mode == 'TILE':
                        # Lát ảnh kín khung. Truoc day khong ho tro nen anh preview ve
                        # hoa tiet nen SAI han ket qua that trong Figma.
                        sf = p.get('scalingFactor') or 0.5
                        tw = max(1, int(im.width * sf)); th = max(1, int(im.height * sf))
                        t = im.resize((tw, th), Image.LANCZOS)
                        fitted = Image.new('RGBA', (max(1, int(w)), max(1, int(h))), (0, 0, 0, 0))
                        for yy in range(0, int(h), th):
                            for xx in range(0, int(w), tw):
                                fitted.alpha_composite(t, (xx, yy))
                    else:
                        fitted = cover_contain(im, int(w), int(h), mode)
                    rotd = node.get('rotation') or 0
                    if rotd:
                        fitted = fitted.rotate(rotd, expand=True)
                        base.alpha_composite(fitted, (int(ax), int(ay - fitted.height + h)))
                    elif mode == 'FILL':
                        m = Image.new('L', (int(w), int(h)), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, int(w) - 1, int(h) - 1], radius=int(rad), fill=255)
                        base.paste(fitted, (int(ax), int(ay)), m)
                    else:
                        px, py = int(ax + (w - fitted.width) / 2), int(ay + (h - fitted.height) / 2)
                        base.alpha_composite(fitted, (px, py))
        for s in (node.get('strokes') or []):
            if s.get('type') == 'SOLID':
                if t == 'ELLIPSE': draw.ellipse(box, outline=col(s), width=int(node.get('strokeWeight') or 1))
                else: rrect(draw, box, rad, outline=col(s), width=int(node.get('strokeWeight') or 1))
    elif t == 'SVG':
        # Không có cairosvg/rsvg trong môi trường này nên KHÔNG rasterize path thật.
        # Vẽ silhouette theo MÀU FILL thật trích từ SVG + viền, để self-check thấy được
        # icon nằm đâu, to bao nhiêu, màu gì. Đây là XẤP XỈ, không phải hình thật —
        # hình icon thật chỉ thấy đúng khi chạy plugin trong Figma.
        import re as _re
        svg = node.get('svg') or ''
        m = _re.search(r'fill="#([0-9a-fA-F]{6})"', svg)
        if m:
            r_, g_, b_ = (int(m.group(1)[i:i+2], 16) for i in (0, 2, 4))
        else:
            r_ = g_ = b_ = 130
        rrect(draw, box, 4, fill=(r_, g_, b_, 190))
        rrect(draw, box, 4, outline=(r_, g_, b_, 255), width=1)
    elif t == 'TEXT':
        chars = node.get('characters') or ''
        fam = (node.get('fontName') or {}).get('family', 'Poppins'); sty = (node.get('fontName') or {}).get('style', 'Regular')
        size = node.get('fontSize', 14); font = font_for(fam, sty, size, chars)
        fp = (fills or [{}])[0]
        if fp.get('type', '').startswith('GRADIENT'):
            st = fp.get('gradientStops', [{}]); c = st[0].get('color', {'r': 1, 'g': .7, 'b': .3}); color = (int(c['r'] * 255), int(c['g'] * 255), int(c['b'] * 255), 255)
        else: color = col(fp) if fp else (255, 255, 255, 255)
        rotd = node.get('rotation') or 0
        if rotd:
            tw = int(draw.textlength(chars, font=font)) + 4; th = sum(font.getmetrics()) + 2
            tile = Image.new('RGBA', (tw, th), (0, 0, 0, 0)); ImageDraw.Draw(tile).text((2, 0), chars, font=font, fill=color)
            tile = tile.rotate(rotd, expand=True)
            base.alpha_composite(tile, (int(ax), int(ay - tile.height + th)))
            for c in node.get('children') or []:
                paint(c, base, draw, ax, ay)
            return
        boxw = w if w and w > 2 else base.width - ax - 4
        lines = wrap(draw, chars, font, boxw)
        asc, desc = font.getmetrics(); lh = asc + desc + 2
        total = lh * len(lines)
        ty = ay + (h - total) / 2 if (node.get('valign') == 'CENTER' and h and h > total) else ay
        al = node.get('align')
        for ln in lines:
            lw = draw.textlength(ln, font=font)
            tx = ax + (boxw - lw) / 2 if al == 'CENTER' else (ax + boxw - lw if al == 'RIGHT' else ax)
            draw.text((tx, ty), ln, font=font, fill=color); ty += lh
    for c in node.get('children') or []:
        paint(c, base, draw, ax, ay)

def render_frame(fr):
    w = int(round(fr.get('w') or 360)); h = int(round(fr.get('h') or 800))
    base = Image.new('RGBA', (w, h), (18, 18, 18, 255))
    draw = ImageDraw.Draw(base)
    # frame's own fill first
    tmp = dict(fr); tmp = {**fr, 'x': 0, 'y': 0}
    paint(tmp, base, draw, 0, 0)
    return base

def contact(images, cols, pad=16, label_h=18, scale=0.62):
    thumbs = [im.resize((int(im.width * scale), int(im.height * scale))) for im in images]
    cw = max(t.width for t in thumbs); rows = math.ceil(len(thumbs) / cols)
    # per-row height = tallest in row
    rowH = []
    for r in range(rows):
        rowH.append(max((thumbs[i].height for i in range(r * cols, min((r + 1) * cols, len(thumbs)))), default=0))
    W = cols * cw + (cols + 1) * pad
    H = sum(rowH) + (rows + 1) * pad
    sheet = Image.new('RGBA', (W, H), (30, 30, 34, 255))
    y = pad
    for r in range(rows):
        x = pad
        for i in range(r * cols, min((r + 1) * cols, len(thumbs))):
            sheet.alpha_composite(thumbs[i], (x + (cw - thumbs[i].width) // 2, y))
            x += cw + pad
        y += rowH[r] + pad
    return sheet

def main():
    scene = json.load(open(SCENE))
    os.makedirs(OUT, exist_ok=True)
    for pi, page in enumerate(scene):
        imgs = []
        pdir = os.path.join(OUT, 'p%d' % pi); os.makedirs(pdir, exist_ok=True)
        for fi, fr in enumerate(page['frames']):
            im = render_frame(fr)
            im.convert('RGB').save(os.path.join(pdir, '%02d_%s.png' % (fi, ''.join(ch for ch in fr['name'][:22] if ch.isalnum() or ch in ' -_').strip())))
            imgs.append(im)
        sheet = contact(imgs, cols=6 if pi == 0 else 5)
        sheet.convert('RGB').save(os.path.join(OUT, 'contact_p%d.png' % pi))
        print('page %d: %d frames → %s' % (pi, len(imgs), os.path.join(OUT, 'contact_p%d.png' % pi)))

if __name__ == '__main__':
    main()
