#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""resolve-layout.py — đọc layout Android bị obfuscate, thay @string/@color/@dimen/
@drawable/@style obfuscate bằng GIÁ TRỊ THẬT, in ra cây phần tử dễ đọc.

    python3 resolve-layout.py <res_dir> <layout_name|layout_file> [--raw]

Dùng cho app bị AndResGuard obfuscate (tên resource thành a,b,c...). Không đoán:
mọi giá trị tra thẳng từ res/values/*.xml.
"""
import sys, os, re
import xml.etree.ElementTree as ET

AND = '{http://schemas.android.com/apk/res/android}'
APP = '{http://schemas.android.com/apk/res-auto}'


def load_values(res):
    """name->value cho color/dimen/string/drawable/style/bool/integer."""
    tables = {}
    for kind in ('color', 'dimen', 'string', 'bool', 'integer'):
        tables[kind] = {}
    vdir = os.path.join(res, 'values')
    for fn in os.listdir(vdir):
        if not fn.endswith('.xml'):
            continue
        try:
            root = ET.parse(os.path.join(vdir, fn)).getroot()
        except Exception:
            continue
        for el in root:
            tag = el.tag
            name = el.get('name')
            if not name:
                continue
            if tag in ('color', 'dimen', 'string', 'bool', 'integer'):
                tables[tag][name] = ''.join(el.itertext())
    return tables


def resolve(val, tables, depth=0):
    """Giải @color/x, @dimen/x, @string/x... (đệ quy) -> giá trị cuối."""
    if val is None or depth > 8:
        return val
    m = re.match(r'@(?:android:)?(\w+)/(\w+)', val)
    if not m:
        return val
    kind, name = m.group(1), m.group(2)
    if val.startswith('@android:'):
        return val  # màu/hằng hệ thống, giữ nguyên
    if kind in tables and name in tables[kind]:
        return resolve(tables[kind][name], tables, depth + 1)
    return val


# thuộc tính đáng quan tâm khi dựng lại UI
KEEP = ['id', 'layout_width', 'layout_height', 'text', 'hint', 'textColor',
        'textSize', 'textStyle', 'background', 'src', 'srcCompat', 'tint',
        'gravity', 'orientation', 'padding', 'paddingLeft', 'paddingTop',
        'paddingRight', 'paddingBottom', 'paddingStart', 'paddingEnd',
        'layout_margin', 'layout_marginTop', 'layout_marginBottom',
        'layout_marginStart', 'layout_marginEnd', 'layout_marginLeft',
        'layout_marginRight', 'layout_gravity', 'visibility', 'cardBackgroundColor',
        'cardCornerRadius', 'cardElevation', 'scaleType', 'drawableStart',
        'drawableEnd', 'drawableTop', 'contentDescription', 'lineHeight',
        'layout_constraintWidth_percent', 'fontFamily', 'ellipsize', 'maxLines']


def short_tag(t):
    return t.rsplit('.', 1)[-1].rsplit('}', 1)[-1]


def dump(el, tables, raw, indent=0):
    pad = '  ' * indent
    attrs = []
    for a in list(el.attrib):
        short = a.replace(AND, '').replace(APP, '')
        key = short.rsplit('}', 1)[-1]
        if key not in KEEP:
            continue
        v = el.attrib[a]
        if not raw:
            v = resolve(v, tables)
        attrs.append(f'{key}={v}')
    line = pad + short_tag(el.tag)
    if attrs:
        line += '  [' + ' · '.join(attrs) + ']'
    print(line)
    for c in list(el):
        dump(c, tables, raw, indent + 1)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    res, target = sys.argv[1], sys.argv[2]
    raw = '--raw' in sys.argv
    path = target if os.path.isfile(target) else os.path.join(res, 'layout', target + '.xml')
    if not os.path.isfile(path):
        sys.exit('không thấy layout: ' + path)
    tables = load_values(res)
    root = ET.parse(path).getroot()
    print(f'# {os.path.basename(path)}')
    dump(root, tables, raw)


if __name__ == '__main__':
    main()
