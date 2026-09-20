#!/usr/bin/env python3
"""Android VectorDrawable XML -> SVG.

Handles: <path> fill/stroke, #AARRGGBB alpha, fillType, <group> transforms,
inline <aapt:attr> gradients, and @drawable/... gradient refs written out as
sibling files by the decompiler.
"""
import os, re, sys, json, xml.etree.ElementTree as ET

A = '{http://schemas.android.com/apk/res/android}'
AAPT = '{http://schemas.android.com/aapt}'
DRAWABLE_DIR = sys.argv[1]

def av(el, name, default=None):
    return el.get(A + name, default)

def color(c):
    """Android colour -> (svg_hex, opacity)."""
    if not c or not c.startswith('#'):
        return None, 1.0
    h = c[1:]
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    if len(h) == 4:
        h = ''.join(ch * 2 for ch in h)
    if len(h) == 8:  # AARRGGBB
        return '#' + h[2:], int(h[:2], 16) / 255.0
    return '#' + h, 1.0

grad_counter = [0]

def gradient_svg(g, defs):
    """<gradient> element -> defs entry, returns url(#id)."""
    grad_counter[0] += 1
    gid = 'g%d' % grad_counter[0]
    gtype = av(g, 'type', 'linear')
    stops = []
    for item in g.findall('item'):
        col, op = color(av(item, 'color'))
        off = float(av(item, 'offset', '0') or 0)
        stops.append('<stop offset="%g" stop-color="%s" stop-opacity="%g"/>' % (off, col or '#000', op))
    if not stops:
        return None
    if gtype == 'radial':
        cx, cy = av(g, 'centerX', '0'), av(g, 'centerY', '0')
        r = av(g, 'gradientRadius', '1')
        defs.append('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s">%s</radialGradient>'
                    % (gid, cx, cy, r, ''.join(stops)))
    else:
        x1, y1 = av(g, 'startX', '0'), av(g, 'startY', '0')
        x2, y2 = av(g, 'endX', '1'), av(g, 'endY', '0')
        defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>'
                    % (gid, x1, y1, x2, y2, ''.join(stops)))
    return 'url(#%s)' % gid

def resolve_paint(el, attr, defs):
    """Return (paint, opacity) for fillColor / strokeColor."""
    # 1. inline <aapt:attr name="android:fillColor"><gradient .../></aapt:attr>
    for sub in el.findall(AAPT + 'attr'):
        if sub.get('name') == 'android:' + attr:
            g = sub.find('gradient')
            if g is not None:
                return gradient_svg(g, defs), 1.0
    raw = av(el, attr)
    if not raw:
        return None, 1.0
    # 2. @drawable/xxx -> sibling gradient file
    if raw.startswith('@drawable/'):
        ref = raw.split('/', 1)[1]
        p = os.path.join(DRAWABLE_DIR, ref + '.xml')
        if os.path.exists(p):
            try:
                g = ET.parse(p).getroot()
                if g.tag == 'gradient':
                    return gradient_svg(g, defs), 1.0
            except Exception:
                pass
        return '#888888', 1.0
    if raw.startswith('@'):
        return '#888888', 1.0
    # 3. plain colour
    return color(raw)

def group_transform(el):
    parts = []
    tx, ty = av(el, 'translateX'), av(el, 'translateY')
    px, py = av(el, 'pivotX', '0'), av(el, 'pivotY', '0')
    rot, sx, sy = av(el, 'rotation'), av(el, 'scaleX'), av(el, 'scaleY')
    if tx or ty:
        parts.append('translate(%s,%s)' % (tx or 0, ty or 0))
    if rot and float(rot) != 0:
        parts.append('rotate(%s,%s,%s)' % (rot, px, py))
    if sx or sy:
        parts.append('translate(%s,%s) scale(%s,%s) translate(-%s,-%s)'
                     % (px, py, sx or 1, sy or 1, px, py))
    return ' '.join(parts)

def emit(el, defs, out):
    for child in el:
        tag = child.tag
        if tag == 'path':
            d = av(child, 'pathData')
            if not d:
                continue
            attrs = ['d="%s"' % d.replace('"', "'")]
            fill, fop = resolve_paint(child, 'fillColor', defs)
            attrs.append('fill="%s"' % (fill if fill else 'none'))
            fa = av(child, 'fillAlpha')
            eff = fop * (float(fa) if fa else 1.0)
            if eff < 0.999:
                attrs.append('fill-opacity="%g"' % eff)
            stroke, sop = resolve_paint(child, 'strokeColor', defs)
            if stroke:
                attrs.append('stroke="%s"' % stroke)
                sw = av(child, 'strokeWidth')
                if sw:
                    attrs.append('stroke-width="%s"' % sw)
                sa = av(child, 'strokeAlpha')
                se = sop * (float(sa) if sa else 1.0)
                if se < 0.999:
                    attrs.append('stroke-opacity="%g"' % se)
                cap, join = av(child, 'strokeLineCap'), av(child, 'strokeLineJoin')
                if cap:
                    attrs.append('stroke-linecap="%s"' % cap)
                if join:
                    attrs.append('stroke-linejoin="%s"' % join)
            if av(child, 'fillType', '').lower() == 'evenodd':
                attrs.append('fill-rule="evenodd"')
            out.append('<path %s/>' % ' '.join(attrs))
        elif tag == 'group':
            t = group_transform(child)
            out.append('<g transform="%s">' % t if t else '<g>')
            emit(child, defs, out)
            out.append('</g>')
        elif tag == 'clip-path':
            continue  # rare here; skipping is visually safe for these icons

def convert(path):
    root = ET.parse(path).getroot()
    if root.tag != 'vector':
        return None
    vw = av(root, 'viewportWidth', '24')
    vh = av(root, 'viewportHeight', '24')
    defs, out = [], []
    emit(root, defs, out)
    if not out:
        return None
    body = ''.join(out)
    d = '<defs>%s</defs>' % ''.join(defs) if defs else ''
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%s" height="%s">%s%s</svg>'
            % (vw, vh, vw, vh, d, body))

if __name__ == '__main__':
    names = sys.argv[2:]
    result = {}
    for n in names:
        p = os.path.join(DRAWABLE_DIR, n + '.xml')
        if not os.path.exists(p):
            print('MISS %s' % n, file=sys.stderr)
            continue
        try:
            svg = convert(p)
            if svg:
                result[n] = svg
                print('OK   %s (%d bytes)' % (n, len(svg)), file=sys.stderr)
            else:
                print('EMPTY %s' % n, file=sys.stderr)
        except Exception as e:
            print('FAIL %s: %s' % (n, e), file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False))
