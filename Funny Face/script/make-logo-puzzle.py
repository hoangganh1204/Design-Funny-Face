# -*- coding: utf-8 -*-
"""Logo "FACE SCRAMBLE" dựng theo đúng font + màu của logo Face Puzzle gốc.

Chủ sản phẩm chọn giữ ngôn ngữ thị giác của bản gốc (2026-09-22), chỉ đổi chữ.
Số liệu bên dưới ĐO từ `build/logo/ORIGINAL_clone_splash.png`, không ước lượng:

    FACE      #FD2C69 -> #F7D460   (hồng sang vàng)
    PUZZLE    #C6F2EC -> #3B7CF1   (bạc hà sang xanh dương)
    nét ngoài #51116E
    viền trắng ~4px và nét tím ~4px ở cỡ 334x181

Font gốc là một bubble font không có trong máy. Gần nhất trong bộ font của APK là
Nunito Black — cùng kiểu sans đầu tròn, cùng độ đậm. Đã thử nở béo để bo tròn thêm
cho giống, nhưng nở >4px là bít bụng chữ E/A và dính các chữ vào nhau, nên giữ
nguyên dáng và bù độ "nhún nhảy" bằng xoay/lệch dòng từng ký tự như bản gốc.

Viền vẽ bằng dilation trên HỢP của cả từ, không stroke từng glyph.
"""
import os
from PIL import Image, ImageFont, ImageChops, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTDIR = '/home/ubuntu/workspace/Design/App 6/Funny Face/decompiled/resources/res/font'
F_NUNITO = os.path.join(FONTDIR, 'nunito_black.ttf')
OUT = os.path.join(ROOT, 'build', 'logo')

FACE_G = ((0xFD, 0x2C, 0x69), (0xF7, 0xD4, 0x60))
SCR_G  = ((0xC6, 0xF2, 0xEC), (0x3B, 0x7C, 0xF1))
PURPLE = (0x51, 0x11, 0x6E)
WHITE  = (255, 255, 255)

# Xuất ở 3x. `drawable-xxhdpi` là mật độ 3x, nên xuất đúng 334x181 (cỡ 1x) là ảnh
# bị kéo giãn 3 lần trên máy -> vỡ hạt. Figma cũng nhận ảnh nét hơn vì fill co lại
# chứ không phóng lên.
OUT_SCALE = 3
BOX_SPLASH = (334 * OUT_SCALE, 181 * OUT_SCALE)     # 1002 x 543
BOX_WORD   = (558 * OUT_SCALE,  84 * OUT_SCALE)     # 1674 x 252

K = 6                     # dựng nội bộ ~2.7x cỡ xuất rồi thu xuống, cho biên mượt
# Bản gốc có viền trắng ~4px và nét tím ~4px ở cỡ 334x181, tức ~12px ở cỡ xuất 1002.
# Lockup nội bộ rộng ~2726 -> hệ số thu về 1002 là ~0.3675, nên viền nội bộ phải là
# 12 / 0.3675 ≈ 32. (SCRAMBLE 8 ký tự rộng hơn PUZZLE 6 ký tự nên hệ số này nhỏ hơn
# tỉ lệ khung; đừng suy ra từ khung.)
WHITE_W  = 32
PURPLE_W = 32
SH_OFF   = (0, 32)

_disc = {}
def disc(r):
    if r not in _disc:
        _disc[r] = [(dx, dy) for dy in range(-r, r+1) for dx in range(-r, r+1)
                    if dx*dx + dy*dy <= r*r and (dx or dy)]
    return _disc[r]

def dilate(m, r):
    if r <= 0: return m
    o = m
    for dx, dy in disc(r):
        o = ImageChops.lighter(o, ImageChops.offset(m, dx, dy))
    return o

def glyph(ch, font):
    t = Image.new('L', (font.size*3, font.size*3), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(t).text((font.size, font.size), ch, font=font, fill=255)
    bb = t.getbbox()
    return t.crop(bb) if bb else None

def word(text, font, tracking, rot=None, dy=None, xs=1.0):
    """Hợp mặt nạ cả từ, có nhún nhảy từng ký tự như bản gốc."""
    gs = []
    for i, ch in enumerate(text):
        gl = glyph(ch, font)
        if gl is None: continue
        if rot and rot[i % len(rot)]:
            gl = gl.rotate(rot[i % len(rot)], resample=Image.BICUBIC, expand=True)
        gs.append((gl, dy[i % len(dy)] if dy else 0))
    total = sum(g.width for g, _ in gs) + tracking*(len(gs)-1)
    mh = max(g.height for g, _ in gs)
    pad = mh
    c = Image.new('L', (total + pad*2, mh + pad*2), 0)
    x = pad
    for gl, off in gs:
        box = (x, pad + off, x + gl.width, pad + off + gl.height)
        c.paste(ImageChops.lighter(c.crop(box), gl), (x, pad + off))
        x += gl.width + tracking
    c = c.crop(c.getbbox())
    if xs != 1.0:
        c = c.resize((int(c.width*xs), c.height), Image.LANCZOS)
    return c

def tint(m, col):
    im = Image.new('RGBA', m.size, col + (0,)); im.putalpha(m); return im

def grad(m, c0, c1):
    """Dải màu chạy trên đúng bbox của chữ. Tính trên cả canvas (có vùng đệm)
    thì chữ chỉ nhận khúc giữa dải -> màu nhạt đi trông thấy."""
    w, h = m.size
    bb = m.getbbox(); y0, y1 = bb[1], bb[3] - 1
    g = Image.new('RGBA', (1, h))
    for y in range(h):
        t = min(1.0, max(0.0, (y - y0) / max(1, y1 - y0)))
        g.putpixel((0, y), tuple(int(a+(b-a)*t) for a, b in zip(c0, c1)) + (255,))
    g = g.resize((w, h)); g.putalpha(m); return g

def layer(m, g0, g1):
    pad = WHITE_W + PURPLE_W + SH_OFF[1] + 6*K
    W, H = m.width + pad*2, m.height + pad*2
    base = Image.new('L', (W, H), 0); base.paste(m, (pad, pad))
    wm = dilate(base, WHITE_W)
    pm = dilate(wm, PURPLE_W)
    sh = ImageChops.offset(pm, *SH_OFF).filter(ImageFilter.GaussianBlur(2*K))
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    c = Image.alpha_composite(c, tint(sh.point(lambda v: v*90//255), (0x2A, 0x06, 0x45)))
    c = Image.alpha_composite(c, tint(pm, PURPLE))
    c = Image.alpha_composite(c, tint(wm, WHITE))
    c = Image.alpha_composite(c, grad(base, g0, g1))
    return c.crop(c.getbbox())

def fit(img, bw, bh, pad=2):
    img = img.crop(img.getbbox())
    s = min((bw-pad*2)/img.width, (bh-pad*2)/img.height)
    r = img.resize((max(1, round(img.width*s)), max(1, round(img.height*s))), Image.LANCZOS)
    o = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    o.paste(r, ((bw-r.width)//2, (bh-r.height)//2)); return o

def build():
    fb = ImageFont.truetype(F_NUNITO, 86*K)
    fs = ImageFont.truetype(F_NUNITO, 70*K)
    face = layer(word('FACE', fb, tracking=5*K, rot=[-3, 2, -2, 3],
                      dy=[0, 3*K, -2*K, 2*K], xs=1.10), *FACE_G)
    # Wordmark giữ là SCRAMBLE (chủ sản phẩm chốt 2026-09-22). Tên trên Play là
    # "Face Mashup - Funny Challenge" — hai thứ khác nhau, xem ghi chú ở CLAUDE.md.
    scr  = layer(word('SCRAMBLE', fs, tracking=4*K, rot=[-2, 2, -3, 2, -2, 3, -2, 2],
                      dy=[0, 2*K, -2*K, 2*K, -1*K, 2*K, -2*K, 1*K], xs=1.10), *SCR_G)
    # xếp chồng, SCRAMBLE đè lên như bản gốc
    ov = int(min(face.height, scr.height) * 0.10)
    W = max(face.width, scr.width); H = face.height + scr.height - ov
    st = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    st.paste(face, ((W-face.width)//2, 0), face)
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    tmp.paste(scr, ((W-scr.width)//2, face.height-ov), scr)
    st = Image.alpha_composite(st, tmp).crop(Image.alpha_composite(st, tmp).getbbox())

    gap = int(scr.height*0.16); hh = max(face.height, scr.height)
    ln = Image.new('RGBA', (face.width+gap+scr.width, hh), (0, 0, 0, 0))
    ln.paste(face, (0, (hh-face.height)//2), face)
    ln.paste(scr, (face.width+gap, (hh-scr.height)//2), scr)
    ln = ln.crop(ln.getbbox())

    st.save(f'{OUT}/PUZZLE_stack_full.png')
    fit(ln, *BOX_WORD).save(f'{OUT}/PUZZLEDECO_word.png')
    deco(st)
    print('lockup noi bo', st.size, '· line', ln.size, '->', OUT)


# --- hoa văn quanh logo ----------------------------------------------------
# Cắt từ chính ảnh sticker chủ sản phẩm gửi (script/make-logo.py không dựng được
# mấy hình này). Nguồn: art/deco/*.png, sinh bằng tách thành phần liên thông.
DECO_DIR = os.path.join(ROOT, 'art', 'deco')

# (tên, x, y, chiều cao, góc xoay) — toạ độ theo hệ 334x181 rồi nhân OUT_SCALE.
# Chủ sản phẩm duyệt 2026-09-22: bỏ dấu hỏi đen (trái trên) và đôi môi (giữa dưới),
# giữ dấu hỏi, con mắt, nốt nhạc.
# Con mắt là ảnh minh hoạ thật, không vẽ lại bằng font được. Ảnh nguồn chỉ 64x62px,
# nên ở 3x chiều cao tối đa còn NÉT là 62/3 ≈ 20.7dp. Đặt 21dp = gần đúng 1:1, không
# phóng to một pixel nào. Trước để 26dp tức phóng 1.26x -> đó là chỗ trông vỡ.
DECO = [
    ('d6',   26, 120, 21,   8),   # con mắt, trái dưới — đúng cỡ gốc
]

# Dấu hỏi KHÔNG dùng ảnh emoji nữa. Bản emoji trong ảnh nguồn chỉ 42x57px, phóng lên
# 28dp@3x là nhoè hẳn so với chữ đã dựng ở 3x — đó chính là chỗ trông xấu. Vẽ lại bằng
# đúng font + viền của logo thì nét ngang với chữ. Màu xanh lá giữ theo bản Face Puzzle gốc.
GREEN_G = ((0x8B, 0xD6, 0x2A), (0x5F, 0xA8, 0x12))

# Nốt nhạc cũng vẽ chứ không dán ảnh: bản emoji 85x73px, phóng lên 30dp@3x là nhoè.
# Glyph ♫ (U+266B) có trong DejaVu Sans Bold, dựng cùng viền trắng + nét tím như chữ.
F_SYMBOL = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

# x, y, chiều cao (dp), góc xoay.
# Đo trên lockup SCRAMBLE (không ước lượng): mép phải FACE ở x=246, FACE trải y=36..88,
# mép trên SCRAMBLE ở y=88. Dấu hỏi tựa ngay vào chữ E nên tâm ở x=264; y=68 đẩy xuống
# nửa dưới FACE mà vẫn chừa ~6dp trước khi chạm SCRAMBLE.
QMARK = (264, 68, 28, 12)
NOTE  = (308, 120, 30, -8)

def deco(stack):
    W, H = BOX_SPLASH
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    wm = fit(stack, 262 * OUT_SCALE, 124 * OUT_SCALE)
    c.alpha_composite(wm, ((W - wm.width)//2, (H - wm.height)//2 - 4*OUT_SCALE))
    def put(d, x, y, rot):
        if rot: d = d.rotate(rot, resample=Image.BICUBIC, expand=True)
        px, py = int(x*OUT_SCALE - d.width/2), int(y*OUT_SCALE - d.height/2)
        px = max(0, min(px, W - d.width)); py = max(0, min(py, H - d.height))
        c.alpha_composite(d, (px, py))

    for name, x, y, h, rot in DECO:
        f = os.path.join(DECO_DIR, name + '.png')
        if not os.path.exists(f):
            print('  thiếu', f); continue
        d = Image.open(f).convert('RGBA')
        hh = h * OUT_SCALE
        put(d.resize((max(1, round(d.width * hh / d.height)), hh), Image.LANCZOS), x, y, rot)

    for ch, font_path, size, spec in (('?', F_NUNITO, 52, QMARK),
                                      ('\u266b', F_SYMBOL, 46, NOTE)):
        x, y, h, rot = spec
        g = layer(word(ch, ImageFont.truetype(font_path, size*K), tracking=0), *GREEN_G)
        hh = h * OUT_SCALE
        put(g.resize((max(1, round(g.width * hh / g.height)), hh), Image.LANCZOS), x, y, rot)

    c.save(f'{OUT}/PUZZLEDECO_splash.png')

if __name__ == '__main__':
    build()
