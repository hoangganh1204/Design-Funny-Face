#!/usr/bin/env python3
"""audit-phase6.py — 4 audit độ phủ của Plan 1 Phase 6 (suy từ CODE, không cần screenshot).
  1. Phủ destination: nav_graph vs registry screen()/dialog()
  2. Phủ resolve:     không còn raw @…/0x… trong thứ đã dựng
  3. Phủ số lượng:    count suy-từ-code vs count đã render
  4. Phủ state:       mỗi nhánh state có 1 frame
Chạy: python3 "Funny Face/script/audit-phase6.py"
(Audit 5 asset + 6 overlap do tools/verify.js lo, chạy qua build.sh)
"""

# Console Windows mac dinh cp1252 nen khong in duoc tieng Viet -> UnicodeEncodeError,
# va script chet GIUA CHUNG, de lai ket qua va do dang ma khong bao gi ro rang.
# Khong bat nguoi chay phai nho dat PYTHONUTF8=1; tu lo lay cho chac.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    if hasattr(_s, 'reconfigure'):
        _s.reconfigure(encoding='utf-8', errors='replace')
import os, re, sys, json, glob, io
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV  = os.path.join(ROOT, 'decompiled/resources/res/navigation/main_nav.xml')
SCR  = os.path.join(ROOT, 'figma/v1/screens')
fail = []

# ---- 1. phủ destination: đối chiếu với KẾT QUẢ BUILD, không phải mã nguồn ----
# Trước đây quét text của screens/*.js -> frame gắn { excluded: true } hoặc { adOnly: true }
# vẫn được TÍNH LÀ CÓ, nên audit báo ĐẠT trong khi bản dựng thật sự thiếu màn. Sai nguy hiểm:
# audit tồn tại để bắt thiếu sót, mà lại báo xanh khi đang thiếu.
nav = open(NAV, encoding='utf-8').read()
dests = re.findall(r'<(?:fragment|dialog|activity)[^>]*android:name="com\.cem\.face\.puzzle\.(?:ui\.)?([\w.]+)"', nav)
dests = [d.split('.')[-1] for d in dests]
SCENE_P = os.path.join(ROOT, 'build/scene.json')
if not os.path.exists(SCENE_P):
    print("1. PHỦ DESTINATION — ⚠ chưa có build/scene.json, chạy capture-scene trước")
else:
    pages = json.load(open(SCENE_P))
    frames = [f for p in pages for f in p['frames']]
    # Chuẩn hoá: bỏ MỌI ký tự không phải chữ/số ở cả hai vế, vì tên frame viết có dấu cách
    # ("28 · Level Picker") còn tên destination viết liền ("FragmentLevelPicker").
    norm = lambda t: re.sub(r'[^a-z0-9]', '', t.lower()).replace('fragment', '')
    blob = norm(' '.join((f['name'] + ' ' + str(f.get('note') or '')) for f in frames))
    missing = [d for d in dests if norm(d) not in blob]
    print(f"1. PHỦ DESTINATION — nav graph {len(dests)} · DỰNG RA {len(frames)} frame")
    if missing:
        print(f"   ❌ destination KHÔNG có frame nào trong bản dựng: {missing}")
        print(f"      (nếu là cố ý loại bỏ thì phải ghi rõ trong README — audit vẫn PHẢI báo)")
        fail.append('destination')
    else:
        print("   ✅ mọi destination đều có frame")

# ---- 2. phủ resolve ----
raw = []
for f in sorted(glob.glob(SCR + '/*.js')):
    for i, l in enumerate(open(f, encoding='utf-8'), 1):
        # @ref luôn là lỗi. Còn 0x7f… CHỈ là lỗi khi dùng làm GIÁ TRỊ VẼ (màu/ảnh);
        # nếu nó là chuỗi bằng chứng in lên canvas (vd "id 0x7f080248 không có trong
        # public.xml") thì đó là TÀI LIỆU, không phải ref chưa resolve.
        raw_ref = re.search(r"'@(string|color|dimen|drawable|mipmap|style)/", l)
        raw_id = re.search(r"(fill|color|stroke|image|src)\s*:\s*'0x7f[0-9a-f]{6}'", l) \
            or re.search(r"\b(img|icon|photo|svgNode)\(\s*'0x7f[0-9a-f]{6}'", l)
        if raw_ref or raw_id:
            raw.append(f"{os.path.basename(f)}:{i}")
print(f"2. PHỦ RESOLVE — {len(raw)} chỗ còn raw @…/0x…")
if raw: print("   ❌", raw[:10]); fail.append('resolve')
else:   print("   ✅ không còn ref chưa resolve")

# ---- 3. phủ số lượng: đếm THẬT trên scene.json (node có IMAGE fill / text item) ----
SCENE = os.path.join(ROOT, 'build/scene.json')
print("3. PHỦ SỐ LƯỢNG")
if not os.path.exists(SCENE):
    print("   ⚠ chưa có build/scene.json — chạy: node script/capture-scene.js figma/v1/plugin.js > build/scene.json")
else:
    pages = json.load(open(SCENE))
    frames = {f['name']: f for p in pages for f in p['frames']}
    def walk(n):
        yield n
        for c in (n.get('children') or []): yield from walk(c)
    A = os.path.join(ROOT, 'assets/v1')
    pool = lambda d: {os.path.splitext(x)[0] for x in os.listdir(os.path.join(A, d))}
    tpl, tv1, chars = pool('30-template-v2'), pool('31-template-v1'), pool('20-nhanvat-origin')
    def find(pfx):
        c = [k for k in frames if k.startswith(pfx)]
        return frames[c[0]] if c else None
    def tiles(f, keys):   # CHỈ node có IMAGE fill — KHÔNG tính TEXT (tên hiển thị có thể
        return sum(1 for n in walk(f) for fl in (n.get('fills') or [])   # trùng tên file ảnh!)
                   if fl.get('type') == 'IMAGE' and fl.get('imageHash') in keys)
    def texts(f, wants):
        t = {(n.get('characters') or '') for n in walk(f) if n.get('type') == 'TEXT'}
        return sum(1 for w in wants if any(w.lower() in x.lower() for x in t))
    SONGS = ['Greedy', 'Jingle', 'Original Sound', 'Spring Snow']
    LANGS = ['English', 'Hindi', 'Spanish', 'French', 'Portug', 'Vietnam', 'Japan']
    checks = [('20a', 40, tpl | chars),   # 38 + 2 nhân vật thêm mới (Pedri, Sasuke) ('20b', 6, tpl), ('20c', 6, tpl), ('20d', 6, tpl),
              ('20e', 22, chars), ('21', 28, tv1 | chars), ('40', 22, chars)]
    # Frame gắn { excluded: true } thì KHÔNG có trong bản dựng. Đó không phải "sai số lượng"
    # mà là loại có chủ ý -> audit 3 bỏ qua. Audit 1 VẪN báo đỏ destination thiếu, nên việc
    # loại bỏ không bị giấu đi ở chỗ nào cả.
    def report(pfx, exp, got):
        if got < 0:
            print(f"   ⏭  {pfx:4s} bỏ qua — frame đã loại khỏi bản dựng (xem audit 1)")
            return 0
        print(f"   {'✅' if got == exp else '❌'} {pfx:4s} kỳ vọng {exp:3d} · render {got:3d}")
        return got != exp

    bad3 = 0
    for pfx, exp, keys in checks:
        f = find(pfx)
        bad3 += report(pfx, exp, tiles(f, keys) if f else -1)
    f = find('28')
    got = sum(1 for n in walk(f) for fl in (n.get('fills') or [])
              if fl.get('type') == 'IMAGE' and str(fl.get('imageHash', '')).startswith('bg_level_')) if f else -1
    bad3 += report('28', 3, got)
    for pfx, exp, w in [('52', 4, SONGS), ('12', 7, LANGS)]:
        f = find(pfx)
        bad3 += report(pfx, exp, texts(f, w) if f else -1)
    if bad3: fail.append('count')

# ---- 4. phủ state ----
# `regs` (quét mã nguồn) đã bị bỏ khi sửa Audit 1 sang đối chiếu KẾT QUẢ BUILD.
# Dựng lại ở đây từ chính scene.json -> audit 4 nói về cái THỰC SỰ được dựng,
# nhất quán với audit 1. Note không nằm trong scene.json (capture-scene.js có
# setPluginData rỗng) nên audit 5 quét thẳng mã nguồn, xem bên dưới.
regs = []
if os.path.exists(SCENE_P):
    for _p in json.load(open(SCENE_P)):
        kind_ = 'dialog' if 'Dialog' in _p['name'] else 'screen'
        for _f in _p['frames']:
            regs.append((kind_, _f['name'], ''))

by = {}
for kind, name, note in regs:
    base = re.sub(r'^[A-Z]?\d+[a-z]?\s*·\s*', '', name).split('·')[0].strip()
    by.setdefault(base, []).append(name)
multi = {k: v for k, v in by.items() if len(v) > 1}
print(f"4. PHỦ STATE — {len(by)} màn gốc, {len(multi)} màn có >1 state")
for k, v in sorted(multi.items()): print(f"   · {k}: {len(v)} state")
single = [k for k, v in by.items() if len(v) == 1]
print(f"   màn chỉ 1 state ({len(single)}): {', '.join(sorted(single)[:12])}")

# ---- 5. note truy vết — quét MÃ NGUỒN screens/*.js ----
# Không dùng scene.json: capture-scene.js có setPluginData() rỗng nên 0/N frame
# mang note trong scene. Ở đây bắt cặp tên frame -> đối số thứ 2 của screen()/dialog().
src = '\n'.join(io.open(f, encoding='utf-8').read() for f in sorted(glob.glob(os.path.join(SCR, '*.js'))))
built = {n for _, n, _ in regs}
nonote = []
for m in re.finditer(r"(screen|dialog)\(\s*'((?:[^'\\]|\\.)*)'\s*,\s*(.)", src):
    nm = m.group(2).replace("\\'", "'")
    if nm not in built:
        continue                      # frame bị loại bằng cờ -> không tính
    if m.group(3) not in ("'", '"'):  # đối số 2 không phải chuỗi note
        nonote.append(nm)
        continue
    q = m.group(3); i = m.end(3); buf = []
    while i < len(src) and src[i] != q:
        if src[i] == '\\': buf.append(src[i+1]); i += 2; continue
        buf.append(src[i]); i += 1
    if len(''.join(buf).strip()) < 8:
        nonote.append(nm)
print(f"5. TRUY VẾT — {len(nonote)}/{len(built)} frame thiếu note nguồn")
if nonote:
    print("   ⚠", nonote[:8])
    fail.append('note')

print()
print("KẾT QUẢ:", "❌ FAIL: " + ', '.join(fail) if fail else "✅ audit 1+2 đạt")
sys.exit(1 if fail else 0)
