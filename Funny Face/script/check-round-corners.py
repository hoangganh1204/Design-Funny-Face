#!/usr/bin/env python3
"""check-round-corners.py — canh cho fill_round_corners() khong an vao nhan vat.

Chay: python "Funny Face/script/check-round-corners.py"

Vi sao co file nay. fill_round_corners() to loang tu 4 goc anh de xoa tam giac trang
con lai sau khi cat the bo goc. Nguong 75 la co y — de 45 thi con sot mot net vien
manh (ca Trump). Nhung nguong rong do da hai lan tran ra ngoai goc:

  - Haaland mat nua mat: goc toi cung thoa "khac mau nen" -> da vá bang cach chi xu ly
    goc THAT SU trang.
  - Leonardo mat mot ben ao (2026-09-22): ao phong TRANG chay xuong sat canh duoi, cham
    vao goc trang cua trang giay. Ben phai duoc chieu sang do trang cach trang 64 —
    lot vao nguong 75 — nen mach loang di tu goc thang vao ao va to no thanh mau the.
    Ben trai nam trong bong, cach trang 158, nen thoat. Do la ly do chi mat MOT ben.

Hai phep do, chay tren chinh bo anh nguon:

  1. Khong anh nao bi to loang qua rong. Tam giac goc that chiem 0.26%-0.42% anh.
     Trump la ngoai le co that: the cua anh nay co net vien ve san, vung trang ngoai
     vien chiem ~5.2% o ca bon goc — va con so do gan nhu khong doi khi siet nguong,
     dung dau hieu cua mot vung that chu khong phai mach ro ri.
  2. Ao cua Leonardo phai con nguyen sau khi chay.
"""

import importlib.util
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOURCES = os.path.join(os.path.dirname(ROOT), 'sources')


def _load_maker():
    spec = importlib.util.spec_from_file_location(
        'make_characters', os.path.join(HERE, 'make-characters.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mc = _load_maker()

# Bo anh nguon 2D. Bo images_3D khong co goc trang nen fill_round_corners khong dong
# vao chung — kiem tra van quet qua cho chac.
SRC_DIRS = [os.path.join(SOURCES, 'images', 'images'),
            os.path.join(SOURCES, 'images_3D', 'images_3D')]

# Tran lon nhat cho mot goc. Tam giac goc that do duoc 0.26%-0.42%; 1% da rat rong rai.
MAX_CORNER = 0.01
# Trump: the TRANG co net vien ve san — ca bon canh deu trang, khong phai goc bo, nen
# _fill_corner roi ve duong lui to loang va phu ~5.2% moi goc. Co that, khong phai ro ri;
# mien ca hai phep do cho anh nay.
KNOWN_WIDE = {'donal_trump (1).jpeg': 0.06}

DIRS = {'TL': (1, 1), 'TR': (-1, 1), 'BL': (1, -1), 'BR': (-1, -1)}
# Vet to xa nhat cho phep, theo canh trung binh. Goc bo do duoc r=100-147 tren anh
# 1024 (~14%); 0.6 la rat rong rai va van bat duoc mot mach chay doc canh.
MAX_REACH = 0.6

# Diem tren ao Leonardo, o ben BI MAT truoc khi sua. Phai con la vai trang.
LEO = 'leonardo.jpeg'
LEO_SHIRT = [(800, 900), (860, 960), (760, 860)]


def corner_fill(im, corner, d, bgc):
    """Vung bi to khi to tu `corner`: (ti le anh, khoang cach xa nhat tinh tu goc).

    Goi dung _fill_corner() — tuc la ca phan do hinh hoc — chu khong goi floodfill
    tho, vi floodfill tho chinh la thu dang duoc canh.
    """
    after = im.copy()
    mc._fill_corner(after, corner, d, bgc)
    a, b = np.asarray(im, dtype=np.int16), np.asarray(after, dtype=np.int16)
    changed = np.abs(a - b).sum(axis=2) > 0
    if not changed.any():
        return 0.0, 0
    ys, xs = np.nonzero(changed)
    reach = int(np.max(np.abs(xs - corner[0]) + np.abs(ys - corner[1])))
    return float(changed.mean()), reach


def sources():
    for d in SRC_DIRS:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                yield f, os.path.join(d, f)


def check_no_corner_runs_away():
    """Khong goc nao bi to qua MAX_CORNER, tru cac ca da biet."""
    bad = []
    for name, path in sources():
        im = Image.open(path).convert('RGB')
        w, h = im.size
        bgc = mc.border_color(im)
        px = im.load()
        cap = KNOWN_WIDE.get(name, MAX_CORNER)
        for label, c in (('TL', (0, 0)), ('TR', (w - 1, 0)),
                         ('BL', (0, h - 1)), ('BR', (w - 1, h - 1))):
            cc = px[c]
            if not (mc.dist(cc, (255, 255, 255)) < 70 and mc.dist(cc, bgc) > 60):
                continue
            frac, reach = corner_fill(im, c, DIRS[label], bgc)
            if frac > cap:
                bad.append('%s goc %s: to loang %.2f%% anh (tran cho phep %.2f%%)'
                           % (name, label, frac * 100, cap * 100))
            elif name not in KNOWN_WIDE and reach > MAX_REACH * (w + h) / 2:
                bad.append('%s goc %s: vet to voi toi %d px tinh tu goc — da ra khoi goc'
                           % (name, label, reach))
    return bad


def check_leonardo_keeps_his_shirt():
    """Chay that fill_round_corners roi soi lai may diem tren ao."""
    path = next((p for n, p in sources() if n == LEO), None)
    if path is None:
        return ['khong tim thay %s trong sources/' % LEO]
    im = Image.open(path).convert('RGB')
    out = mc.fill_round_corners(im.copy()).load()
    bad = []
    for p in LEO_SHIRT:
        c = out[p]
        if mc.dist(c, (255, 255, 255)) > 120:
            bad.append('Leonardo: diem ao %s thanh %s — ao bi to mat mot ben' % (p, c))
    return bad


def main():
    fails = check_no_corner_runs_away() + check_leonardo_keeps_his_shirt()
    for f in fails:
        print('  FAIL  ' + f)
    if fails:
        print('\n%d loi.' % len(fails))
        return 1
    print('OK — khong goc nao tran ra ngoai, ao Leonardo con nguyen.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
