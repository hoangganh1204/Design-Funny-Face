#!/usr/bin/env python3
"""audit-contrast.py — soát tương phản chữ/nền trên TOÀN BỘ frame, theo WCAG 2.1.

Vì sao cần: hệ màu dùng token dùng chung, nên đổi nghĩa một token (ví dụ chữ mặc định
từ tối sang sáng) là ảnh hưởng mọi nơi tham chiếu nó. Soát bằng mắt qua 41 frame thì
chắc chắn sót — đã sót thật: đổi C.textHi sang màu sáng rồi chỉ sửa lại một file, để
lọt màn Language Picker thành chữ trắng trên ô trắng.

Cách làm: duyệt cây node theo ĐÚNG THỨ TỰ VẼ, quy mọi toạ độ về tuyệt đối. Với mỗi
node chữ, tìm ngược lại node phủ dưới nó gần nhất có nền đục -> đó là nền thật sự nằm
sau chữ. Rồi tính tỉ lệ tương phản.

Ngưỡng WCAG 2.1 AA: 4.5:1 cho chữ thường, 3.0:1 cho chữ lớn (>=18pt, hoặc >=14pt đậm).

Chạy: PYTHONUTF8=1 python "Funny Face/script/audit-contrast.py" build/scene-v3.json
"""
import json
import sys


def lum_channel(c):
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def rel_lum(rgb):
    r, g, b = (lum_channel(rgb[i]) for i in range(3))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    l1, l2 = rel_lum(fg), rel_lum(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def blend(fg, alpha, bg):
    """Chữ/nền bán trong suốt phải trộn với lớp dưới trước khi tính, không thì kết quả
    lạc quan giả — ví dụ scrim đen 40% trên ảnh sáng thực tế vẫn sáng."""
    return tuple(fg[i] * alpha + bg[i] * (1 - alpha) for i in range(3))


def fill_of(node, y_frac):
    """Trả về (rgb, alpha) của nền node, hoặc None nếu node không tô nền.
    Gradient: lấy màu tại vị trí y_frac dọc theo dải, vì chữ nằm ở đâu thì nền sau nó
    là màu ở đúng chỗ đó — lấy điểm dừng đầu là sai với dải chuyển dài."""
    fills = node.get('fills') or []
    if not fills:
        return None
    f = fills[-1]
    t = f.get('type')
    if t == 'SOLID':
        c = f['color']
        return (c['r'], c['g'], c['b']), f.get('opacity', 1.0) * node.get('opacity', 1.0)
    if t and t.startswith('GRADIENT'):
        stops = f.get('gradientStops') or []
        if not stops:
            return None
        c0, c1 = stops[0]['color'], stops[-1]['color']
        k = min(max(y_frac, 0.0), 1.0)
        rgb = tuple(c0[ch] + (c1[ch] - c0[ch]) * k for ch in ('r', 'g', 'b'))
        a = c0.get('a', 1) + (c1.get('a', 1) - c0.get('a', 1)) * k
        return rgb, a * node.get('opacity', 1.0)
    if t == 'IMAGE':
        return 'IMAGE', 1.0
    return None


def flatten(node, ox, oy, out, depth=0):
    x = ox + node.get('x', 0)
    y = oy + node.get('y', 0)
    out.append((node, x, y))
    for ch in node.get('children') or []:
        flatten(ch, x, y, out, depth + 1)


def audit(path, strict=4.5, large=3.0):
    pages = json.load(open(path, encoding='utf-8'))
    problems = []
    n_text = 0
    for page in pages:
        for fr in page['frames']:
            flat = []
            flatten(fr, 0, 0, flat)
            for i, (node, nx, ny) in enumerate(flat):
                if node.get('type') != 'TEXT':
                    continue
                fills = node.get('fills') or []
                if not fills or fills[0].get('type') != 'SOLID':
                    continue      # chữ tô gradient — bỏ qua, hiếm và phải xem bằng mắt
                n_text += 1
                fc = fills[0]['color']
                fg = (fc['r'], fc['g'], fc['b'])
                fa = fills[0].get('opacity', 1.0)
                cx = nx + (node.get('w') or 0) / 2
                cy = ny + (node.get('h') or 0) / 2

                # Lớp nền: quét NGƯỢC trong thứ tự vẽ, lấy node đầu tiên phủ điểm giữa
                # chữ và có nền đủ đục. Gặp ảnh thì dừng và báo riêng — không đoán màu
                # ảnh, phải xem bằng mắt.
                # Gom các lớp BÁN TRONG SUỐT vào chồng, đi tiếp cho tới khi gặp lớp ĐỤC,
                # rồi mới trộn chồng đó LÊN TRÊN lớp đục. Trước đây trộn ngay tại chỗ rồi
                # vẫn quét tiếp, nên lớp đục phía sau ghi đè mất kết quả đã trộn — gặp
                # đúng ca pill scrim 80% nằm trên thẻ trắng: báo trắng-trên-trắng dù thực
                # tế nền sau chữ là xám đậm.
                stack = []          # [(rgb, alpha)] — gần chữ nhất đứng trước
                base = None
                over_image = False
                for j in range(i - 1, -1, -1):
                    other, oxx, oyy = flat[j]
                    ow, oh = other.get('w') or 0, other.get('h') or 0
                    if not (oxx <= cx <= oxx + ow and oyy <= cy <= oyy + oh):
                        continue
                    got = fill_of(other, (cy - oyy) / oh if oh else 0.5)
                    if not got:
                        continue
                    rgb, a = got
                    if rgb == 'IMAGE':
                        over_image = True
                        break
                    if a >= 0.95:
                        base = rgb
                        break
                    stack.append((rgb, a))
                if over_image or base is None:
                    continue
                bg = base
                for rgb, a in reversed(stack):      # xa -> gần
                    bg = blend(rgb, a, bg)

                eff_fg = blend(fg, fa, bg) if fa < 1 else fg
                ratio = contrast(eff_fg, bg)
                size = node.get('fontSize') or 14
                bold = 'Bold' in str(node.get('fontName') or '') or (node.get('fontWeight') or 400) >= 700
                need = large if (size >= 18 or (size >= 14 and bold)) else strict
                if ratio < need:
                    problems.append({
                        'frame': fr['name'], 'text': (node.get('name') or '')[:32],
                        'ratio': round(ratio, 2), 'need': need, 'size': size,
                        'fg': '#%02x%02x%02x' % tuple(int(c * 255) for c in eff_fg),
                        'bg': '#%02x%02x%02x' % tuple(int(c * 255) for c in bg),
                    })
    return problems, n_text


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'build/scene-v3.json'
    probs, total = audit(src)
    print('Đã soát %d node chữ.' % total)
    if not probs:
        print('✓ Không node nào dưới ngưỡng AA.')
        sys.exit(0)
    print('✗ %d node DƯỚI ngưỡng AA:\n' % len(probs))
    cur = None
    for p in sorted(probs, key=lambda x: (x['frame'], x['ratio'])):
        if p['frame'] != cur:
            cur = p['frame']
            print('  ' + cur)
        print('     %5.2f:1 (cần %.1f) · %-32s %s trên %s · %dsp'
              % (p['ratio'], p['need'], p['text'], p['fg'], p['bg'], p['size']))
    sys.exit(1)
