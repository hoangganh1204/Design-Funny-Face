# -*- coding: utf-8 -*-
"""Sinh logo Face Scramble — nhiều phương án để A/B, chấm điểm rồi chọn.

Hai file ra cho MỖI phương án, vì app dùng logo ở hai chỗ có nền trái ngược nhau:

  ic_splash.png    334x181  — splash, nền tím gradient #5B21B6 -> #C4B0FF (logo nằm ~#6732BE)
  img_app_name.png 558x84   — header Home, v4 nền TÍM NHẠT #DCD2FF, v3 nền TỐI #2B2252

Cùng một lockup cho cả hai chỗ là lý do logo cũ nát ở header: xếp 2 dòng nhét vào khung
tỉ lệ 6.64 thì mỗi dòng còn ~30px, viền trắng ăn hết nét. Nên bản wordmark ở đây là lockup
MỘT DÒNG riêng, không phải bản splash thu nhỏ.

Viền vẽ bằng DILATION trên hợp của toàn chữ (không phải stroke từng glyph) — stroke từng
glyph để lộ đường nối giữa các chữ chồng nhau.
"""
import os, math, json
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTDIR = '/home/ubuntu/workspace/Design/App 6/Funny Face/decompiled/resources/res/font'
OUT = os.path.join(ROOT, 'build', 'logo')
os.makedirs(OUT, exist_ok=True)

SS = 3  # supersample

F_NUNITO = os.path.join(FONTDIR, 'nunito_black.ttf')
F_LATO   = os.path.join(FONTDIR, 'lato_black_900.ttf')
F_ONEST  = os.path.join(FONTDIR, 'onest_bold.ttf')

# --- bảng màu Tier 3 -------------------------------------------------------
BRAND   = (0x9A, 0x6C, 0xFF)
DEEP    = (0x5B, 0x21, 0xB6)
SOFT    = (0xC4, 0xB0, 0xFF)
ACTION  = (0xF5, 0x61, 0x2B)
AEDGE   = (0xFF, 0x8A, 0x3D)
SHADOW  = (0x3B, 0x14, 0x70)
WHITE   = (0xFF, 0xFF, 0xFF)
INK     = (0x24, 0x10, 0x46)

BG_SPLASH = ((0x5B, 0x21, 0xB6), (0xC4, 0xB0, 0xFF))
BG_V4_HDR = (0xDC, 0xD2, 0xFF)
BG_V3_HDR = (0x2B, 0x22, 0x52)


# --- hạ tầng vẽ ------------------------------------------------------------
_disc_cache = {}
def _disc(r):
    if r in _disc_cache: return _disc_cache[r]
    pts = [(dx, dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1)
           if dx * dx + dy * dy <= r * r]
    _disc_cache[r] = pts
    return pts

def dilate(mask, r):
    """Nở mặt nạ theo đĩa bán kính r. Hợp của các bản dịch — viền bo tròn thật."""
    if r <= 0: return mask
    out = mask
    for dx, dy in _disc(r):
        if dx == 0 and dy == 0: continue
        out = ImageChops.lighter(out, ImageChops.offset(mask, dx, dy))
    return out

def letter_mask(ch, font):
    """Một glyph trên nền trong suốt, đã cắt sát."""
    tmp = Image.new('L', (font.size * 3, font.size * 3), 0)
    ImageDraw.Draw(tmp).text((font.size, font.size), ch, font=font, fill=255)
    bb = tmp.getbbox()
    return tmp.crop(bb) if bb else None

def word_mask(text, font, tracking=0, jitter=None, baseline_jitter=None):
    """Hợp mặt nạ cả từ. jitter = list độ xoay (độ) theo từng ký tự."""
    glyphs = []
    for i, ch in enumerate(text):
        if ch == ' ':
            glyphs.append((None, int(font.size * 0.30)))
            continue
        g = letter_mask(ch, font)
        if g is None: continue
        if jitter:
            ang = jitter[i % len(jitter)]
            if ang:
                g = g.rotate(ang, resample=Image.BICUBIC, expand=True)
        glyphs.append((g, g.width))

    total = sum(w for _, w in glyphs) + tracking * (len(glyphs) - 1)
    maxh = max((g.height for g, _ in glyphs if g), default=1)
    pad = maxh  # chỗ cho xoay + lệch dòng
    canvas = Image.new('L', (total + pad * 2, maxh + pad * 2), 0)
    x = pad
    for i, (g, w) in enumerate(glyphs):
        if g is not None:
            dy = 0
            if baseline_jitter:
                dy = baseline_jitter[i % len(baseline_jitter)]
            canvas.paste(ImageChops.lighter(canvas.crop((x, pad + dy, x + w, pad + dy + g.height)), g),
                         (x, pad + dy))
        x += w + tracking
    bb = canvas.getbbox()
    return canvas.crop(bb)

def tint(mask, color):
    """color = (r,g,b) hoặc (r,g,b,a); a<255 thì làm mờ chính mặt nạ."""
    if len(color) == 4:
        rgb, a = color[:3], color[3]
        if a < 255:
            mask = mask.point(lambda v: v * a // 255)
    else:
        rgb = color
    img = Image.new('RGBA', mask.size, rgb + (0,))
    img.putalpha(mask)
    return img

def tint_grad(mask, c_top, c_bot):
    w, h = mask.size
    grad = Image.new('RGBA', (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        grad.putpixel((0, y), tuple(int(a + (b - a) * t) for a, b in zip(c_top, c_bot)) + (255,))
    grad = grad.resize((w, h))
    grad.putalpha(mask)
    return grad

def over(base, layer, pos=(0, 0)):
    tmp = Image.new('RGBA', base.size, (0, 0, 0, 0))
    tmp.paste(layer, pos)
    return Image.alpha_composite(base, tmp)


def build_layer(mask, *, fill, outline=None, out_w=0, shadow=None, sh_off=(0, 0), sh_blur=0,
                inner=None, inner_off=(0, 0)):
    """Dựng một cụm chữ: bóng -> viền -> nền chữ -> highlight trong."""
    pad = out_w + max(abs(sh_off[0]), abs(sh_off[1])) + sh_blur + 4
    W, H = mask.width + pad * 2, mask.height + pad * 2
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    m = Image.new('L', (W, H), 0); m.paste(mask, (pad, pad))

    outm = dilate(m, out_w) if out_w else m

    if shadow is not None:
        sm = ImageChops.offset(outm, sh_off[0], sh_off[1])
        canvas = Image.alpha_composite(canvas, tint(sm, shadow))
    if outline is not None and out_w:
        canvas = Image.alpha_composite(canvas, tint(outm, outline))
    if isinstance(fill, tuple) and len(fill) == 2:
        canvas = Image.alpha_composite(canvas, tint_grad(m, fill[0], fill[1]))
    else:
        canvas = Image.alpha_composite(canvas, tint(m, fill))
    if inner is not None:
        im = ImageChops.subtract(m, ImageChops.offset(m, inner_off[0], inner_off[1]))
        canvas = Image.alpha_composite(canvas, tint(im, inner))
    return canvas


def fit(img, box_w, box_h, pad=2):
    """Thu ảnh vào khung, canh giữa, giữ tỉ lệ."""
    img = img.crop(img.getbbox())
    s = min((box_w - pad * 2) / img.width, (box_h - pad * 2) / img.height)
    nw, nh = max(1, int(img.width * s)), max(1, int(img.height * s))
    img = img.resize((nw, nh), Image.LANCZOS)
    out = Image.new('RGBA', (box_w, box_h), (0, 0, 0, 0))
    out.paste(img, ((box_w - nw) // 2, (box_h - nh) // 2))
    return out


# ===========================================================================
#  PHƯƠNG ÁN
#  Mỗi phương án dựng 2 lockup: 'stack' (splash 334x181) và 'line' (header 558x84).
#  Ràng buộc chung: chỉ tím + cam + trắng; phải đọc được trên CẢ nền tím đậm
#  (#6732BE, splash) lẫn nền tím nhạt (#DCD2FF, header v4).
# ===========================================================================
S = 170 * SS          # cỡ font cơ sở
OUTW = int(7 * SS)    # bề dày viền

def _f(path, k=1.0): return ImageFont.truetype(path, int(S * k))


def _stack(top_layer, bot_layer, overlap=0.06, dx=0):
    """Xếp hai cụm chữ thành khối hai dòng, canh giữa."""
    W = max(top_layer.width, bot_layer.width) + abs(dx) + 4
    gap = -int(min(top_layer.height, bot_layer.height) * overlap)
    H = top_layer.height + bot_layer.height + gap
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    c = over(c, top_layer, ((W - top_layer.width) // 2, 0))
    c = over(c, bot_layer, ((W - bot_layer.width) // 2 + dx, top_layer.height + gap))
    return c.crop(c.getbbox())


def _row(parts, gap):
    """Ghép các cụm chữ thành một hàng, canh theo đáy chữ."""
    W = sum(p.width for p in parts) + gap * (len(parts) - 1)
    H = max(p.height for p in parts)
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    x = 0
    for p in parts:
        c = over(c, p, (x, H - p.height))
        x += p.width + gap
    return c.crop(c.getbbox())


# --- A · Split Solid — cam/tím, viền trắng (bản đối chứng, gần v4 hiện tại) --
def var_A(mode):
    f = _f(F_NUNITO)
    face = build_layer(word_mask('FACE', f, tracking=int(2 * SS)),
                       fill=(AEDGE, ACTION), outline=WHITE, out_w=OUTW,
                       shadow=SHADOW, sh_off=(0, int(9 * SS)))
    scr = build_layer(word_mask('SCRAMBLE', _f(F_NUNITO, .78), tracking=int(2 * SS)),
                      fill=(SOFT, BRAND), outline=WHITE, out_w=OUTW,
                      shadow=SHADOW, sh_off=(0, int(9 * SS)))
    return _stack(face, scr) if mode == 'stack' else _row([face, scr], int(16 * SS))


# --- B · Scramble Jitter — chữ SCRAMBLE xô lệch, đúng nghĩa "scramble" ------
def var_B(mode):
    f = _f(F_NUNITO)
    face = build_layer(word_mask('FACE', f, tracking=int(3 * SS)),
                       fill=(AEDGE, ACTION), outline=WHITE, out_w=OUTW,
                       shadow=SHADOW, sh_off=(0, int(9 * SS)))
    jm = word_mask('SCRAMBLE', _f(F_NUNITO, .76), tracking=int(5 * SS),
                   jitter=[-9, 6, -4, 9, -7, 4, -9, 6],
                   baseline_jitter=[0, int(7 * SS), -int(4 * SS), int(5 * SS),
                                    -int(6 * SS), int(3 * SS), -int(5 * SS), int(6 * SS)])
    scr = build_layer(jm, fill=(SOFT, BRAND), outline=WHITE, out_w=OUTW,
                      shadow=SHADOW, sh_off=(0, int(9 * SS)))
    return _stack(face, scr, overlap=0.02) if mode == 'stack' else _row([face, scr], int(16 * SS))


# --- C · Slab Badge — nằm trên nền tím đậm riêng, nên nền nào cũng như nhau --
def var_C(mode):
    f = _f(F_NUNITO, .92)
    face = build_layer(word_mask('FACE', f, tracking=int(2 * SS)), fill=(AEDGE, ACTION),
                       outline=None, out_w=0, shadow=None)
    scr = build_layer(word_mask('SCRAMBLE', _f(F_NUNITO, .72), tracking=int(3 * SS)),
                      fill=WHITE, outline=None, out_w=0, shadow=None)
    inner = _stack(face, scr, overlap=0.10) if mode == 'stack' else _row([face, scr], int(14 * SS))
    padx, pady = int(34 * SS), int(24 * SS)
    W, H = inner.width + padx * 2, inner.height + pady * 2
    r = int(min(W, H) * (0.24 if mode == 'stack' else 0.42))
    slab = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(slab)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=r, fill=DEEP + (255,),
                        outline=AEDGE + (255,), width=int(5 * SS))
    return over(slab, inner, (padx, pady))


# --- D · Duotone viền tối — viền tím thẫm nên nền sáng hay tối đều cắt được --
def var_D(mode):
    f = _f(F_NUNITO)
    face = build_layer(word_mask('FACE', f, tracking=int(2 * SS)),
                       fill=(AEDGE, ACTION), outline=SHADOW, out_w=OUTW,
                       shadow=None, inner=(255, 255, 255, 110), inner_off=(0, int(5 * SS)))
    scr = build_layer(word_mask('SCRAMBLE', _f(F_NUNITO, .78), tracking=int(2 * SS)),
                      fill=(WHITE, SOFT), outline=SHADOW, out_w=OUTW,
                      shadow=None, inner=(255, 255, 255, 110), inner_off=(0, int(5 * SS)))
    return _stack(face, scr) if mode == 'stack' else _row([face, scr], int(16 * SS))


# --- E · Gradient sweep — một từ liền, cam đổ xuống tím ---------------------
def var_E(mode):
    if mode == 'stack':
        top = build_layer(word_mask('FACE', _f(F_LATO, 1.0), tracking=int(6 * SS)),
                          fill=(AEDGE, ACTION), outline=WHITE, out_w=int(5 * SS),
                          shadow=SHADOW, sh_off=(int(4 * SS), int(7 * SS)))
        bot = build_layer(word_mask('SCRAMBLE', _f(F_LATO, .72), tracking=int(3 * SS)),
                          fill=(BRAND, DEEP), outline=WHITE, out_w=int(5 * SS),
                          shadow=SHADOW, sh_off=(int(4 * SS), int(7 * SS)))
        return _stack(top, bot, overlap=0.04)
    m = word_mask('FACE SCRAMBLE', _f(F_LATO, .95), tracking=int(3 * SS))
    return build_layer(m, fill=(AEDGE, BRAND), outline=WHITE, out_w=int(5 * SS),
                       shadow=SHADOW, sh_off=(int(4 * SS), int(7 * SS)))


VARIANTS = {'A': var_A, 'B': var_B, 'C': var_C, 'D': var_D, 'E': var_E}
NAMES = {
    'A': 'Split Solid — cam/tím, viền trắng',
    'B': 'Scramble Jitter — chữ xô lệch',
    'C': 'Slab Badge — nền tím riêng',
    'D': 'Duotone viền tím thẫm',
    'E': 'Gradient sweep — một từ liền',
}


# ===========================================================================
#  XUẤT + DỰNG BỐI CẢNH THẬT
# ===========================================================================
def vgrad(w, h, c0, c1):
    g = Image.new('RGB', (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        g.putpixel((0, y), tuple(int(a + (b - a) * t) for a, b in zip(c0, c1)))
    return g.resize((w, h))

def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def lum(rgb):
    r, g, b = (_lin(v) for v in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def splash_ctx(splash_png):
    """Màn splash thật: 360x800, gradient #5B21B6 -> #C4B0FF, logo 334x181 tại y=93.5."""
    W, H = 360, 800
    bg = vgrad(W, H, *BG_SPLASH).convert('RGBA')
    lw, lh = 334, 181
    lx, ly = (W - lw) // 2, int((H * 0.46 - lh) / 2)
    bg = over(bg, splash_png, (lx, ly))
    d = ImageDraw.Draw(bg)
    py = ly + lh + 16
    d.rounded_rectangle([72, py, 72 + 216, py + 10], radius=5, fill=(255, 255, 255, 80))
    d.rounded_rectangle([72, py, 72 + 108, py + 10], radius=5, fill=ACTION + (255,))
    return bg.convert('RGB')


def header_ctx(word_png, bg_rgb, label_dark):
    """Header Home thật: wordmark cao đúng 24dp, canh giữa hàng 48dp."""
    W, H = 360, 72
    im = Image.new('RGBA', (W, H), bg_rgb + (255,))
    hh = 24
    ww = int(round(hh * (558 / 84)))
    w = word_png.resize((ww, hh), Image.LANCZOS)
    im = over(im, w, ((W - ww) // 2, 12 + (48 - hh) // 2))
    d = ImageDraw.Draw(im)
    box = (24, 210, 60) if label_dark else (255, 255, 255)
    d.rounded_rectangle([12, 12, 60, 60], radius=12, outline=box + (90,), width=1)
    d.rounded_rectangle([300, 12, 348, 60], radius=12, outline=box + (90,), width=1)
    return im.convert('RGB')


def main():
    report = {}
    for vid, fn in VARIANTS.items():
        stack = fit(fn('stack'), 334, 181)
        line = fit(fn('line'), 558, 84)
        stack.save(f'{OUT}/{vid}_splash.png')
        line.save(f'{OUT}/{vid}_word.png')

        sp = splash_ctx(stack)
        h4 = header_ctx(line, BG_V4_HDR, True)
        h3 = header_ctx(line, BG_V3_HDR, False)
        sp.save(f'{OUT}/{vid}_ctx_splash.png')
        h4.save(f'{OUT}/{vid}_ctx_hdr_v4.png')
        h3.save(f'{OUT}/{vid}_ctx_hdr_v3.png')

        # tấm tổng cho mỗi phương án
        sheet = Image.new('RGB', (360, 800 + 8 + 72 + 8 + 72), (18, 14, 32))
        sheet.paste(sp, (0, 0)); sheet.paste(h4, (0, 808)); sheet.paste(h3, (0, 888))
        sheet.save(f'{OUT}/{vid}_sheet.png')

        # đo: tỉ lệ phủ nét ở cỡ header thật (proxy cho "còn đọc được không")
        small = line.resize((int(24 * 558 / 84), 24), Image.LANCZOS)
        a = small.split()[-1]
        ink = sum(1 for p in a.getdata() if p > 128) / (small.width * small.height)
        report[vid] = {
            'name': NAMES[vid],
            'ink_at_24dp': round(ink, 4),
            'cr_action_on_splash': round(ratio(ACTION, (0x67, 0x32, 0xBE)), 2),
            'cr_brand_on_v4hdr': round(ratio(BRAND, BG_V4_HDR), 2),
            'cr_deep_on_v4hdr': round(ratio(DEEP, BG_V4_HDR), 2),
        }
    json.dump(report, open(f'{OUT}/report.json', 'w'), indent=1, ensure_ascii=False)
    for k, v in report.items():
        print(f"{k}  {v['name']:<38} ink@24dp {v['ink_at_24dp']*100:5.1f}%")
    print('->', OUT)





# ===========================================================================
#  VÒNG 2 — sửa đúng lỗi mà hai giám khảo chỉ ra
#
#  Phát hiện chặn đường: đo được luminance nền sáng #DCD2FF = 0.685 và nền
#  splash #6732BE = 0.089, nên để đạt 3:1 với nền sáng thì mực phải có
#  L <= 0.195, còn để đạt 3:1 với nền splash thì L >= 0.367. Hai điều kiện
#  loại trừ nhau -> MỘT màu chữ duy nhất không thể sống ở cả hai nền.
#
#  Lối ra: ic_splash và img_app_name VỐN ĐÃ là hai file khác nhau, và v3/v4
#  vốn đã có hai cây asset riêng. Nên mực sáng cho nền tối, mực tối cho nền
#  sáng — không phát sinh asset mới, chỉ là tô đúng chỗ.
# ===========================================================================
DEEPER = (0x24, 0x10, 0x46)   # thân badge: 11.88:1 vs header sáng, 2.24:1 vs splash
ORANGE_HI = (0xFF, 0xA0, 0x4D)  # cam trên thân badge: 8.39:1 (AA cho chữ nhỏ)
INK_D  = (0x3B, 0x14, 0x70)

def _scramble_cue(font, k=.78, tracking=2):
    """Đúng MỘT ký tự bị xô — đủ để nói 'scramble', không phá độ đọc."""
    return word_mask('SCRAMBLE', _f(F_NUNITO, k), tracking=int(tracking * SS),
                     jitter=[0, 0, 0, -13, 0, 0, 0, 0],
                     baseline_jitter=[0, 0, 0, int(5 * SS), 0, 0, 0, 0])


def var_C2(mode):
    """C + khoảng trắng thật giữa hai từ, nền badge tối hơn, bớt giống nút bấm."""
    face = build_layer(word_mask('FACE', _f(F_NUNITO, .92), tracking=int(2 * SS)),
                       fill=(ORANGE_HI, ACTION), outline=None, out_w=0)
    scr = build_layer(_scramble_cue(_f(F_NUNITO, .72), .72, 3), fill=WHITE, outline=None, out_w=0)
    inner = (_stack(face, scr, overlap=0.10) if mode == 'stack'
             else _row([face, scr], int(34 * SS)))       # 34dp: khoảng trắng THẬT giữa hai từ
    padx, pady = int(30 * SS), int(22 * SS)
    W, H = inner.width + padx * 2, inner.height + pady * 2
    r = int(min(W, H) * (0.22 if mode == 'stack' else 0.26))   # bớt bo -> bớt giống nút CTA
    # Viền dày: trên header tối v3 thân badge chỉ 1.17:1 so với nền, nên chính đường
    # viền cam gánh việc tách khối. Mỏng thì rasterize ở mdpi/hdpi là mất.
    ew = int((13 if mode == 'line' else 11) * SS)   # 13dp: dò được, cân giữa nền sáng và nền tối
    slab = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(slab).rounded_rectangle(
        [0, 0, W - 1, H - 1], radius=r, fill=DEEPER + (255,),
        outline=AEDGE + (255,), width=ew)
    return over(slab, inner, (padx, pady))


def _var_D2(mode, light_ink):
    """D + một ký tự xô. light_ink=True: mực sáng cho nền tối. False: mực tối cho nền sáng."""
    face_fill = (AEDGE, ACTION)
    if light_ink:
        scr_fill, out_c = (WHITE, SOFT), INK_D
    else:
        scr_fill, out_c = (BRAND, DEEP), WHITE
    ow = int(8 * SS)
    face = build_layer(word_mask('FACE', _f(F_NUNITO), tracking=int(2 * SS)),
                       fill=face_fill, outline=out_c, out_w=ow,
                       inner=(255, 255, 255, 110), inner_off=(0, int(5 * SS)))
    scr = build_layer(_scramble_cue(_f(F_NUNITO, .78)),
                      fill=scr_fill, outline=out_c, out_w=ow,
                      inner=(255, 255, 255, 90), inner_off=(0, int(5 * SS)))
    return _stack(face, scr) if mode == 'stack' else _row([face, scr], int(18 * SS))


def var_D2(mode):  return _var_D2(mode, light_ink=True)
def var_D2d(mode): return _var_D2(mode, light_ink=False)


def round2():
    """Xuất C2 / D2 và dựng bối cảnh: splash + header tối (v3) + header sáng (v4)."""
    out = {}
    for vid, stack_fn, word_light_fn, word_dark_fn in [
        ('C2', var_C2, var_C2, var_C2),          # badge: một artwork cho mọi nền
        ('D2', var_D2, var_D2, var_D2d),         # duotone: hai bản mực
    ]:
        stack = fit(stack_fn('stack'), 334, 181)
        wl = fit(word_light_fn('line'), 558, 84)
        wd = fit(word_dark_fn('line'), 558, 84)
        stack.save(f'{OUT}/{vid}_splash.png')
        wl.save(f'{OUT}/{vid}_word_light.png')
        wd.save(f'{OUT}/{vid}_word.png')          # bản dùng cho header sáng v4
        splash_ctx(stack).save(f'{OUT}/{vid}_ctx_splash.png')
        header_ctx(wd, BG_V4_HDR, True).save(f'{OUT}/{vid}_ctx_hdr_v4.png')
        header_ctx(wl, BG_V3_HDR, False).save(f'{OUT}/{vid}_ctx_hdr_v3.png')
        out[vid] = True
    print('vòng 2 xong:', ', '.join(out))


if __name__ == '__main__':
    import sys as _s
    (round2 if len(_s.argv) > 1 and _s.argv[1] == 'round2' else main)()
