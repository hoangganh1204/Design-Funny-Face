#!/usr/bin/env python3
"""make-v2.py — sinh figma/v2 + assets/v2 từ v1 (Plan 2 — reskin).

Luật (plan-2-reskin-v2.vi.md):
  1. Màu: xoay CẢ họ brand MỘT góc cố định. Giữ màu chức năng.
  2. Nền: retint bề mặt trung tính, giữ tông sáng (app này theme Light).
  3. Bo góc: tăng đúng MỘT bậc.
  4. Asset: ảnh nội dung KHÔNG đụng · mark brand có màu → xoay hue · trung tính → giữ.
  6. KHÔNG fork tay: mọi thay đổi sinh từ script này. Sửa v1 → chạy lại → v2 luôn khớp.

Chạy: python3 "Funny Face/script/make-v2.py"
"""

# Console Windows mac dinh cp1252 nen khong in duoc tieng Viet -> UnicodeEncodeError,
# va script chet GIUA CHUNG, de lai ket qua va do dang ma khong bao gi ro rang.
# Khong bat nguoi chay phai nho dat PYTHONUTF8=1; tu lo lay cho chac.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    if hasattr(_s, 'reconfigure'):
        _s.reconfigure(encoding='utf-8', errors='replace')
import colorsys, json, os, re, shutil, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V1, V2 = os.path.join(ROOT, 'figma/v1'), os.path.join(ROOT, 'figma/v2')
A1, A2 = os.path.join(ROOT, 'assets/v1'), os.path.join(ROOT, 'assets/v2')

# ─── Luật 1: biến đổi màu brand — chọn SAU KHI sample màu thật ────────
# Họ brand v1 đo được: hue 181-214 do, S 98-100%, L 48-52% (cyan -> xanh duong).
#
# Vi sao KHONG chi xoay hue: xoay co hoc giu nguyen S=99%. Muc do hop voi xanh
# duong (doc ra "cong nghe") nhung sang magenta/tim thi thanh neon choi, ma app
# nay nen TRANG va day ANH NGUOI THAT -- mau choi danh nhau voi tong da.
# Nen ap mot bien doi DONG NHAT tren ca ba kenh (van giu tinh nhat quan cua ho
# mau, dung tinh than Luat 1):
#   +65 do -> primary H214 -> H279 (tim violet): mau cua giai tri/sang tao, bo
#             tro tong da am; cach do chuc nang 81 do, cach xanh v1 65 do.
#   S x0.82 -> 99% -> 81%: van ruc nhung het neon.
#   L x0.90 -> 49% -> 44%: dam lai de CHU TRANG dat chuan.
# Ket qua primary #8b15ca -- tuong phan chu trang 6.87 (AA chu thuong, AAA chu
# lon), so voi v1 chu den chi 3.84 (DUOI chuan AA). Day la cai thien UX that.
HUE_SHIFT = 65
SAT_MUL   = 0.82
LIGHT_MUL = 0.90

BRAND_HUE = (165, 230)      # dải hue coi là "brand" → xoay
BRAND_MIN_SAT = 0.35        # dưới ngưỡng này là trung tính → không đụng
# Màu CHỨC NĂNG: mang ý nghĩa, KHÔNG xoay dù bão hoà cao.
KEEP = {'ff4342', 'ff0000', 'cc0000', 'ff5555',   # đỏ lỗi / xoá / cảnh báo
        'ffffff', '000000',                       # trắng/đen thật
        '1d873b', 'd93025'}                       # xanh thành công / đỏ từ chối

# ─── Luật 2: retint bề mặt trung tính SÁNG về hue mới (giữ độ sáng) ───────────
# CHỈ áp cho bề mặt gần-trắng/xám nhạt. KHÔNG đụng #ffffff, #000000, scrim, chữ.
_NEUTRAL_SURFACES = ['f4f4f4', 'f5eee9', 'e6e6e5', 'd3d3d3',
                     'fffdfb', 'e4e3e2', 'cbcac8']
_BRAND_HUE_NEW = (colorsys.rgb_to_hls(1/255, 108/255, 247/255)[0] + HUE_SHIFT / 360) % 1

def _tint(hx, sat=0.055):
    """Giữ nguyên độ sáng, gán hue brand mới với S rất thấp -> ám màu tinh tế."""
    r, g, b = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    _, l, _ = colorsys.rgb_to_hls(r, g, b)
    return '%02x%02x%02x' % tuple(
        int(round(c * 255)) for c in colorsys.hls_to_rgb(_BRAND_HUE_NEW, l, sat))

SURFACE_TINT = {h: _tint(h) for h in _NEUTRAL_SURFACES}

# ─── Luật 3: bo góc +1 bậc (pill 30 và r69 GIỮ NGUYÊN: silhouette đặc trưng) ──
# Chữ nằm TRÊN nền brand: v1 dùng #171716 trên xanh (3.84, dưới AA). Primary v2
# đậm hơn nên phải đổi sang trắng (6.87, đạt AA). Thay CÓ CHỦ ĐÍCH đúng 2 chỗ —
# C.textHi còn 39 chỗ khác là chữ trên nền trắng, tuyệt đối không đụng.
ON_BRAND_TEXT = [
    # nút Save (result-video, 2 lần) — nền C.primary
    ("text('Save', 158, 0, { size: 16, weight: 700, font: 'main', color: C.textHi,",
     "text('Save', 158, 0, { size: 16, weight: 700, font: 'main', color: C.white,"),
    # Button.Primary (Done / Try Now / Next) — nền gradient brand
    ("size: 16, weight: 700, color: C.textHi, w: w, h: 48,",
     "size: 16, weight: 700, color: C.white, w: w, h: 48,"),
    # Splash: dong "This action contain ads" nam o DAY gradient (nen tim dam).
    # Do tai dung vi tri y=758: v1 8.56 (nen cyan sang) -> v2 2.34 voi chu den.
    # Chuyen sang trang. Dong "Loading..." o tren van 8.18 nen GIU nguyen mau den.
    ("textC(STR.adsNote, noteY, { size: 20, weight: 700, font: 'main', color: C.textHi })",
     "textC(STR.adsNote, noteY, { size: 20, weight: 700, font: 'main', color: C.white })"),
]

RADIUS = {'card: 12': 'card: 16', 'tile: 16': 'tile: 20', 'sm: 8': 'sm: 10',
          'dialog: 16': 'dialog: 20', 'r12: 12': 'r12: 16'}


def rot_hex(h, deg=HUE_SHIFT):
    """Xoay hue, GIỮ nguyên L và S (và alpha nếu hex 8 ký tự)."""
    a = ''
    if len(h) == 8:
        a, h = h[:2], h[2:]
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    out = colorsys.hls_to_rgb((hh + deg / 360) % 1,
                              max(0.0, min(1.0, l * LIGHT_MUL)),
                              max(0.0, min(1.0, s * SAT_MUL)))
    return a + '%02x%02x%02x' % tuple(int(round(c * 255)) for c in out)


def classify(h):
    """'brand' → xoay · 'surface' → retint · 'keep' → giữ nguyên."""
    raw = h[2:] if len(h) == 8 else h
    if raw in KEEP:
        return 'keep'
    if raw in SURFACE_TINT:
        return 'surface'
    r, g, b = [int(raw[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    if s < BRAND_MIN_SAT:
        return 'keep'            # trung tính: xám, đen, trắng, scrim
    return 'brand' if BRAND_HUE[0] <= hh * 360 <= BRAND_HUE[1] else 'keep'


def map_hex(h):
    k = classify(h)
    if k == 'brand':
        return rot_hex(h)
    if k == 'surface':
        raw = h[2:] if len(h) == 8 else h
        return (h[:2] if len(h) == 8 else '') + SURFACE_TINT[raw]
    return h


def transform_js(src):
    stats = {'brand': 0, 'surface': 0, 'keep': 0}

    def sub(m):
        h = m.group(1)
        stats[classify(h)] += 1
        return "'" + map_hex(h) + "'"

    # chỉ thay hex nằm trong chuỗi nháy đơn (tránh đụng số/tên biến)
    out = re.sub(r"'([0-9a-f]{6}|[0-9a-f]{8})'", sub, src)
    for a, b in RADIUS.items():
        out = out.replace(a, b)
    for a, b in ON_BRAND_TEXT:
        out = out.replace(a, b)
    out = out.replace('Funny Face · Screens', 'Funny Face v2 · Screens')
    out = out.replace('Funny Face · Dialogs', 'Funny Face v2 · Dialogs')
    out = out.replace("closePlugin('Funny Face: '", "closePlugin('Funny Face v2: '")
    return out, stats


def do_code():
    os.makedirs(os.path.join(V2, 'screens'), exist_ok=True)
    total = {'brand': 0, 'surface': 0, 'keep': 0}
    files = ['code.js', 'main.js'] + [
        'screens/' + f for f in sorted(os.listdir(os.path.join(V1, 'screens'))) if f.endswith('.js')]
    for rel in files:
        src = open(os.path.join(V1, rel), encoding='utf-8').read()
        out, st = transform_js(src)
        open(os.path.join(V2, rel), 'w', encoding='utf-8').write(out)
        for k in total:
            total[k] += st[k]
    man = json.load(open(os.path.join(V1, 'manifest.json')))
    man['name'] = man['name'].replace('v1', 'v2')
    man['id'] = man['id'].replace('v1', 'v2')
    json.dump(man, open(os.path.join(V2, 'manifest.json'), 'w'), indent=2, ensure_ascii=False)
    print(f"code : {len(files)} file -> figma/v2   "
          f"(brand xoay {total['brand']} · nen retint {total['surface']} · giu {total['keep']})")


# ─── Luật 4: asset — phân loại rồi áp đúng phương pháp cho từng nhóm ──────────
# Nhóm 1 — ảnh NỘI DUNG (người thật, ảnh chụp): KHÔNG ĐỤNG. Xoay hue ảnh nhiều
#          màu ra màu bậy (mặt người thành tím).
UNTOUCHED = {'20-nhanvat-origin', '30-template-v2', '31-template-v1'}
# Nhóm 2 — art thương hiệu CÓ MÀU: xoay hue từng pixel, cùng góc, giữ alpha.
#          Pixel trung tính (S thấp) và pixel ngoài họ brand đều GIỮ, nên hoạ tiết
#          xám không bị ám màu và màu cam/đỏ trong art không lệch.
BRANDED = {'40-anh-app', '10-icons'}


def rot_image(path):
    im = Image.open(path).convert('RGBA')
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            hh, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if s < BRAND_MIN_SAT:
                continue                    # trung tính → giữ
            if not (BRAND_HUE[0] <= hh * 360 <= BRAND_HUE[1]):
                continue                    # ngoài họ brand → giữ (đỏ, cam, vàng…)
            nr, ng, nb = colorsys.hls_to_rgb((hh + HUE_SHIFT / 360) % 1,
                                             max(0.0, min(1.0, l * LIGHT_MUL)),
                                             max(0.0, min(1.0, s * SAT_MUL)))
            px[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)
    im.save(path)


def rot_svg(path):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'#([0-9a-fA-F]{6})', lambda m: '#' + map_hex(m.group(1).lower()), s)
    open(path, 'w', encoding='utf-8').write(s)


def do_assets():
    if os.path.isdir(A2):
        shutil.rmtree(A2)
    shutil.copytree(A1, A2)
    n_img = n_svg = n_skip = 0
    for grp in sorted(os.listdir(A2)):
        d = os.path.join(A2, grp)
        if not os.path.isdir(d):
            continue
        if grp in UNTOUCHED:
            n_skip += len(os.listdir(d))
            continue
        if grp not in BRANDED:
            continue
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            if fn.endswith('.svg'):
                rot_svg(p); n_svg += 1
            elif fn.endswith('.png'):
                rot_image(p); n_img += 1
    print(f"asset: xoay {n_img} PNG + {n_svg} SVG · giu nguyen {n_skip} anh noi dung")


if __name__ == '__main__':
    if not os.path.isdir(V1):
        sys.exit('khong thay figma/v1 — chay Plan 1 truoc')
    do_code()
    do_assets()
    print(f"\nxong. goc xoay = +{HUE_SHIFT} do")
