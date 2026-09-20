#!/usr/bin/env python3
"""
build-plugin.py — quét thư mục asset rồi dựng lại plugin Figma.

    python3 tools/build-plugin.py --src "Air Horn/assets/v2" --plugin "Air Horn/figma/v2"

Việc nó làm:
  1. Quét mọi ảnh trong --src (kể cả thư mục con), nhúng base64 vào assets.js
  2. Quét mọi .svg, nhúng vào icons.js
  3. Ghép assets.js + icons.js + code.js thành plugin.js
  4. Đối chiếu với code.js: báo asset code cần mà thư mục không có, và ngược lại

Quy ước: KHOÁ là tên file không đuôi. Thay ảnh thì giữ nguyên tên, đổi đuôi thoải
mái (.png/.jpg/.webp đều được — Figma đọc PNG và JPEG; WEBP sẽ được cảnh báo).
"""

# Console Windows mac dinh cp1252 nen khong in duoc tieng Viet -> UnicodeEncodeError,
# va script chet GIUA CHUNG, de lai ket qua va do dang ma khong bao gi ro rang.
# Khong bat nguoi chay phai nho dat PYTHONUTF8=1; tu lo lay cho chac.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    if hasattr(_s, 'reconfigure'):
        _s.reconfigure(encoding='utf-8', errors='replace')
import argparse, base64, glob, io, os, re, sys

try:
    from PIL import Image
except ImportError:
    Image = None

IMG_EXT = ('.png', '.jpg', '.jpeg', '.webp')

# Trần cạnh dài (px) theo thư mục = 2× kích thước hiển thị lớn nhất của nhóm đó.
# Ảnh gốc trong folder KHÔNG bị sửa; chỉ bản nhúng vào plugin được thu nhỏ.
# 2× là đủ nét cho màn retina — mắt không phân biệt được ở mọi mức zoom thực tế.
MAXDIM = {
    '01-nen-va-khung': 1600,   # nền toàn màn, khung 360×800
    '02-o-danh-muc':    320,   # ô lưới Home 148×152
    '03-anh-item':      600,   # lớn nhất ở màn Play Sound (ivSound 300×300)
    '04-man-hinh-vo':   480,   # ô Broken 148×224
    '05-co-quoc-gia':    96,   # cờ tròn 24dp
    '06-nut-bam':       420,   # nút ~204dp
    '07-logo':          720,   # logo Splash 300dp
    '09-khac':          720,
}
DEFAULT_MAXDIM = 720


# Nhóm được chuẩn hoá lề: crop về chủ thể rồi căn giữa sao cho cạnh dài của chủ
# thể lấp NORM_FILL cạnh ô. Khắc phục việc ảnh nguồn có lề trong suốt không đều
# (kéo lấp 100% canvas trong khi tông đơ có lề -> kéo trông to hơn hẳn).
NORM_GROUPS = {'03-anh-item', '02-o-danh-muc'}
NORM_FILL = 0.80


def normalize_pad(im):
    """Căn giữa chủ thể vào canvas vuông, chủ thể lấp NORM_FILL cạnh."""
    bb = im.getchannel('A').getbbox()
    if not bb:
        return im
    crop = im.crop(bb)
    bw, bh = crop.size
    side = max(1, int(round(max(bw, bh) / NORM_FILL)))
    canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(crop, ((side - bw) // 2, (side - bh) // 2))
    return canvas


def encode_image(path, maxdim, normalize=False):
    """Trả về (bytes, ext). Thu nhỏ nếu vượt trần, chuẩn hoá lề nếu yêu cầu.
    Không chạm file gốc."""
    raw = open(path, 'rb').read()
    if Image is None:
        return raw, os.path.splitext(path)[1]
    im = Image.open(io.BytesIO(raw))
    changed = False
    if normalize:
        im = im.convert('RGBA')
        # chỉ chuẩn hoá ảnh có nền trong suốt; ảnh đục (meme) bbox = cả ảnh, bỏ qua
        if im.getchannel('A').getextrema()[0] < 250:
            im = normalize_pad(im)
            changed = True
    w, h = im.size
    if maxdim > 0 and max(w, h) > maxdim:
        scale = maxdim / max(w, h)
        im = im.convert('RGBA').resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        changed = True
    if not changed:
        return raw, os.path.splitext(path)[1]           # không đổi gì, giữ bytes gốc
    im = im.convert('RGBA')
    buf = io.BytesIO()
    if im.getchannel('A').getextrema()[0] >= 250:       # đục -> JPEG cho nhẹ
        im.convert('RGB').save(buf, 'JPEG', quality=88, optimize=True)
        return buf.getvalue(), '.jpg'
    # có alpha -> PNG. Quantize bảng màu để nhẹ (ảnh vẽ giảm ~80%, mắt không thấy).
    try:
        q = im.quantize(colors=192, method=Image.FASTOCTREE)
        q.save(buf, 'PNG', optimize=True)
        if buf.getbuffer().nbytes and buf.getbuffer().nbytes < 400_000:
            return buf.getvalue(), '.png'
    except Exception:
        pass
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.getvalue(), '.png'


def collect(src, exts):
    out = {}
    dup = []
    for f in sorted(glob.glob(os.path.join(src, '**', '*'), recursive=True)):
        if not f.lower().endswith(exts) or os.path.isdir(f):
            continue
        key = os.path.splitext(os.path.basename(f))[0]
        if key in out:
            dup.append(key)
        out[key] = f
    return out, dup


def run_verify(plugin_dir):
    """Kiểm tra bằng cách CHẠY THẬT plugin, không đoán qua chuỗi trong code.

    Kiểm tra tĩnh từng sai: nó bắt nhầm tên layer, mảnh chuỗi ghép động
    ('broken' + n), và asset của skin không được dựng. Chỉ chạy thật mới biết
    asset nào thực sự thiếu.
    """
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    verify = os.path.join(here, 'verify.js')
    if not os.path.exists(verify):
        return None
    try:
        r = subprocess.run(['node', verify, os.path.join(plugin_dir, 'plugin.js')],
                           capture_output=True, text=True, timeout=180)
    except Exception as e:
        print('  (bỏ qua kiểm tra thực thi: %s)' % e)
        return None
    for line in r.stdout.splitlines():
        if line.startswith(('nodes', '✓', '✗', '⚠')):
            print('  ' + line)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True, help='thư mục asset đã sửa')
    ap.add_argument('--plugin', required=True, help='thư mục plugin đích (chứa code.js)')
    ap.add_argument('--full', action='store_true',
                    help='nhúng ảnh nguyên bản, KHÔNG thu nhỏ (file rất nặng, plugin chạy chậm)')
    ap.add_argument('--no-normalize', action='store_true',
                    help='không chuẩn hoá lề ảnh item (giữ y như app, kéo sẽ to hơn tông đơ)')
    a = ap.parse_args()

    code_path = os.path.join(a.plugin, 'code.js')
    if not os.path.exists(code_path):
        sys.exit('Không thấy %s' % code_path)

    imgs, dup_i = collect(a.src, IMG_EXT)
    svgs, dup_s = collect(a.src, ('.svg',))
    if dup_i or dup_s:
        print('CẢNH BÁO trùng tên (file sau ghi đè file trước):', ', '.join(dup_i + dup_s))

    webp = [k for k, v in imgs.items() if v.lower().endswith('.webp')]
    if webp:
        print('CẢNH BÁO Figma không đọc WEBP, hãy đổi sang PNG/JPG:', ', '.join(webp[:8]))

    # assets.js — thu nhỏ về trần 2× rồi mới nhúng
    src_bytes = out_bytes = shrunk = 0
    with open(os.path.join(a.plugin, 'assets.js'), 'w', encoding='utf-8') as f:
        f.write('// Sinh tự động bởi tools/build-plugin.py — đừng sửa tay.\n')
        f.write('// Nguồn: %s (ảnh thu nhỏ về 2× kích thước hiển thị)\n' % a.src)
        f.write('const ASSETS = {\n')
        for k in sorted(imgs):
            grp = os.path.basename(os.path.dirname(imgs[k]))
            maxdim = 0 if a.full else MAXDIM.get(grp, DEFAULT_MAXDIM)
            norm = (not a.no_normalize) and grp in NORM_GROUPS
            data, _ = encode_image(imgs[k], maxdim, normalize=norm)
            src_bytes += os.path.getsize(imgs[k])
            out_bytes += len(data)
            if len(data) < os.path.getsize(imgs[k]):
                shrunk += 1
            f.write('  "%s": "%s",\n' % (k, base64.b64encode(data).decode()))
        f.write('};\n')
        # video (mp4/mov/webm) nhúng nguyên bản — dùng cho Figma Pro (video fill)
        vids, _ = collect(a.src, ('.mp4', '.mov', '.webm'))
        f.write('const VIDEOS = {\n')
        for k in sorted(vids):
            b = open(vids[k], 'rb').read()
            f.write('  "%s": "%s",\n' % (k, base64.b64encode(b).decode()))
        f.write('};\n')
        if vids:
            print('  video : %d (%s)' % (len(vids), ', '.join(vids)))

    # icons.js
    with open(os.path.join(a.plugin, 'icons.js'), 'w', encoding='utf-8') as f:
        f.write('// Sinh tự động bởi tools/build-plugin.py — đừng sửa tay.\n')
        f.write('const ICONS = {\n')
        for k in sorted(svgs):
            svg = open(svgs[k], encoding='utf-8').read().replace('\\', '\\\\').replace('"', '\\"')
            svg = ' '.join(svg.split())
            f.write('  "%s": "%s",\n' % (k, svg))
        f.write('};\n')

    # plugin.js
    parts = []
    # code.js = helper + registry (KHÔNG gọi main). screens/*.js = builder mỗi màn,
    # nhiều tác giả viết song song không đụng nhau. main.js = điểm chạy, ghép cuối cùng.
    for n in ('assets.js', 'icons.js', 'code.js'):
        parts.append(open(os.path.join(a.plugin, n), encoding='utf-8').read())
    screens_dir = os.path.join(a.plugin, 'screens')
    if os.path.isdir(screens_dir):
        for fn in sorted(os.listdir(screens_dir)):
            if fn.endswith('.js'):
                parts.append('// ===== screens/%s =====' % fn)
                parts.append(open(os.path.join(screens_dir, fn), encoding='utf-8').read())
    main_js = os.path.join(a.plugin, 'main.js')
    if os.path.exists(main_js):
        parts.append(open(main_js, encoding='utf-8').read())
    open(os.path.join(a.plugin, 'plugin.js'), 'w', encoding='utf-8').write('\n'.join(parts))

    size = os.path.getsize(os.path.join(a.plugin, 'plugin.js'))
    print('  ảnh   : %d  (thu nhỏ %d file: %.0f→%.0f MB ảnh gốc)'
          % (len(imgs), shrunk, src_bytes / 1024 / 1024, out_bytes / 1024 / 1024))
    print('  icon  : %d' % len(svgs))
    print('  plugin: %.1f MB%s' % (size / 1024 / 1024, '  (--full: nguyên bản)' if a.full else ''))
    ok = run_verify(a.plugin)
    if ok is False:
        sys.exit(1)


if __name__ == '__main__':
    main()
