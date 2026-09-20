#!/usr/bin/env python3
"""make-mock-ar.py — sinh ảnh MÔ PHỎNG cho vùng camera AR (Plan 1 Phụ lục E).

Vì sao cần: 2 màn quay (FragmentFacePuzzle, FragmentFunnyPuzzle) hiển thị camera
TRỰC TIẾP + lớp AR dựng theo landmark mỗi khung hình. Không có asset tĩnh nào
trong APK để trích -> trước đây là ô placeholder trống.

Script này KHÔNG bịa dữ liệu app. Nó:
  - dựng một khuôn mặt TỔNG HỢP (hình khối phẳng, rõ ràng là giả, không dùng ảnh
    người thật nào) để đóng vai "mặt người dùng qua camera";
  - áp đúng cơ chế đọc được từ code lên khuôn mặt đó.

Hai cơ chế KHÁC NHAU, đọc từ OverlayView.java:
  FacePuzzle mode -> drawFacePuzzleComponent: cắt mặt thành 6 vùng rồi dịch/xoay.
                     KHÔNG có art nhân vật.
  FaceFunny  mode -> draw() nhánh Mode.FaceFunny (OverlayView.java:700-712):
                     1. drawBitmap(processBitmap)  -> khung camera
                     2. drawFunnyOverlay           -> overlay nhân vật, MẶT TRỐNG
                        (asset 21-nhanvat-overlay/<id>.png vốn đã không có mắt
                         mũi miệng), canh giữa, vẽ nguyên xi
                     3. drawFunnyComponent         -> cắt MỘT bộ phận từ ảnh
                        nhân vật gốc (funnyBitmap = getOriginImagePath) bằng
                        BitmapShader rồi TRỊNH dần xuống theo frameCount.
                     => mặt nhân vật LUÔN TRỐNG trong lúc chơi. App KHÔNG vẽ nét
                        mặt người dùng vào lỗ. Khớp ảnh chụp máy thật của user.

Mọi ảnh sinh ra PHẢI được gắn nhãn "mô phỏng" ở nơi dùng.
Chạy: python3 "Funny Face/script/make-mock-ar.py"
"""

# Console Windows mac dinh cp1252 nen khong in duoc tieng Viet -> UnicodeEncodeError,
# va script chet GIUA CHUNG, de lai ket qua va do dang ma khong bao gi ro rang.
# Khong bat nguoi chay phai nho dat PYTHONUTF8=1; tu lo lay cho chac.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    if hasattr(_s, 'reconfigure'):
        _s.reconfigure(encoding='utf-8', errors='replace')
import json, math, os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets/v1/50-mock-ar')
OVERLAY_DIR = os.path.join(ROOT, 'reference/21-nhanvat-overlay')

W = H = 512
SKIN = (214, 176, 148, 255)
SKIN_DARK = (186, 148, 122, 255)
HAIR = (72, 60, 56, 255)
SHIRT = (108, 116, 130, 255)
BG = (34, 34, 34, 255)


def synth_face(size=(W, H), bg=BG):
    """Khuôn mặt tổng hợp — phẳng, hiển nhiên là giả, không phải ảnh người thật."""
    im = Image.new('RGBA', size, bg)
    d = ImageDraw.Draw(im)
    w, h = size
    cx = w // 2
    # vai
    d.ellipse([cx - w * .46, h * .78, cx + w * .46, h * 1.45], fill=SHIRT)
    # cổ
    d.rounded_rectangle([cx - w * .09, h * .60, cx + w * .09, h * .84], radius=int(w * .05), fill=SKIN_DARK)
    # đầu
    d.ellipse([cx - w * .235, h * .16, cx + w * .235, h * .72], fill=SKIN)
    # tóc
    d.chord([cx - w * .245, h * .13, cx + w * .245, h * .56], 180, 360, fill=HAIR)
    # tai
    d.ellipse([cx - w * .265, h * .385, cx - w * .215, h * .475], fill=SKIN_DARK)
    d.ellipse([cx + w * .215, h * .385, cx + w * .265, h * .475], fill=SKIN_DARK)
    # mắt
    for sx in (-1, 1):
        ex = cx + sx * w * .095
        d.ellipse([ex - w * .045, h * .375, ex + w * .045, h * .425], fill=(250, 250, 250, 255))
        d.ellipse([ex - w * .018, h * .388, ex + w * .018, h * .414], fill=(48, 44, 42, 255))
    # lông mày
    for sx in (-1, 1):
        ex = cx + sx * w * .095
        d.rounded_rectangle([ex - w * .052, h * .338, ex + w * .052, h * .354],
                            radius=int(w * .008), fill=HAIR)
    # mũi
    d.polygon([(cx, h * .44), (cx - w * .035, h * .53), (cx + w * .035, h * .53)], fill=SKIN_DARK)
    # miệng
    d.chord([cx - w * .085, h * .545, cx + w * .085, h * .625], 10, 170, fill=(150, 82, 78, 255))
    return im



W2, H2 = 540, 1200          # tỉ lệ 360x800 -> đặt full-bleed vào frame


def portrait_camera(effect=None):
    """Khung camera DOC phu KIN khung, dung nhu app that: camera/video full-bleed,
    UI chong len tren. Ban cu chi ve mat o ~40% tren roi to den tu y=62% xuong ->
    frame Figma ra mot mang den lon o duoi, trong nhu thieu noi dung.
    effect(img_selfie) -> anh da ap hieu ung, dan de len nen.
    """
    out = Image.new('RGBA', (W2, H2), BG)
    d = ImageDraw.Draw(out)
    for i in range(H2):                      # nen phong, sang dan len tren
        t = i / H2
        v = int(30 + 26 * (1 - t))
        d.line([(0, i), (W2, i)], fill=(v, v, v + 3, 255))
    # selfie o khoang cach tay: dau + vai TRAN qua canh duoi, khong de ho day khung
    sz = int(W2 * 1.45)
    sel = synth_face((sz, sz), bg=(0, 0, 0, 0))
    if effect is not None:
        sel = effect(sel)
    y0 = int(H2 * 0.06)
    out.alpha_composite(sel, ((W2 - sz) // 2, y0))
    # Anh selfie bi cat o canh duoi cua chinh no (sz < H2) -> truoc day lo ra mot duong cat
    # ngang roi den tuyen. Noi tiep mang ao xuong het khung cho lien mach.
    if y0 + sz < H2:
        d.rectangle([0, y0 + sz - 1, W2, H2], fill=SHIRT)
    # scrim day RAT NHE cho chip thoi gian/nut record con doc duoc — khong to den dac
    scrim = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    top = int(H2 * 0.74)
    for i in range(H2 - top):
        sd.line([(0, top + i), (W2, top + i)], fill=(0, 0, 0, int(150 * i / (H2 - top))))
    out.alpha_composite(scrim)
    return out


def facepuzzle(face):
    """FacePuzzle mode: cắt mặt thành 6 vùng, dịch + xoay nhẹ (drawFacePuzzleComponent).
    6 vùng suy từ code: 2 mắt, mũi, miệng, 2 má/viền."""
    w, h = face.size
    out = Image.new('RGBA', face.size, BG)
    # nền: phần thân/tóc giữ nguyên để thấy vùng mặt bị tách ra
    # KHONG khoet lo giua mat: draw() ve drawBitmap(camera) TRUOC roi moi drawFaceComponent,
    # va componentPaint dung SRC_IN + BitmapShader nen cac manh duoc ve THEM vao vi tri lech —
    # mat goc van con nguyen ben duoi. Ban mock cu khoet ellipse trong suot -> lo den giua mat,
    # sai co che va nhin rat xau. (OverlayView.java:713-723, 935-974)
    out.alpha_composite(face)
    cx = w // 2
    regions = [   # (box, dịch x, dịch y, xoay độ)
        ((cx - int(w * .155), int(h * .355), cx - int(w * .035), int(h * .445)), -46, -30, -14),
        ((cx + int(w * .035), int(h * .355), cx + int(w * .155), int(h * .445)),  48, -22,  11),
        ((cx - int(w * .06),  int(h * .42),  cx + int(w * .06),  int(h * .545)),   6,  40,  -7),
        ((cx - int(w * .10),  int(h * .53),  cx + int(w * .10),  int(h * .64)),  -30,  56,  16),
        ((cx - int(w * .205), int(h * .42),  cx - int(w * .13),  int(h * .58)),  -62,  18,  -9),
        ((cx + int(w * .13),  int(h * .42),  cx + int(w * .205), int(h * .58)),   64,  26,   8),
    ]
    for box, dx, dy, ang in regions:
        piece = face.crop(box).rotate(ang, expand=True, resample=Image.BICUBIC)
        out.alpha_composite(piece, (box[0] + dx, box[1] + dy))
    return out


def synth_features(size=(W, H)):
    """CHỈ nét mặt (lông mày, mắt, mũi, miệng) trên nền trong suốt.
    Tương ứng cai ma drawFunnyComponent ve LEN TREN overlay."""
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w, h = size
    cx = w // 2
    for sx in (-1, 1):
        ex = cx + sx * w * .095
        d.rounded_rectangle([ex - w * .052, h * .338, ex + w * .052, h * .354],
                            radius=int(w * .008), fill=HAIR)
        d.ellipse([ex - w * .045, h * .375, ex + w * .045, h * .425], fill=(250, 250, 250, 255))
        d.ellipse([ex - w * .018, h * .388, ex + w * .018, h * .414], fill=(48, 44, 42, 255))
    d.polygon([(cx, h * .44), (cx - w * .035, h * .53), (cx + w * .035, h * .53)], fill=SKIN_DARK)
    d.chord([cx - w * .085, h * .545, cx + w * .085, h * .625], 10, 170, fill=(150, 82, 78, 255))
    return im


def blank_face_box(ov, tol=26):
    """Tim VUNG MAT TRONG cua overlay: mang mau PHANG lon nhat o nua tren.
    (mat nhan vat duoc to mot mau da dac, khong co net)."""
    from collections import deque
    w, h = ov.size
    px = ov.convert('RGB').load()
    a = ov.getchannel('A').load()
    best = None
    for sy in (0.28, 0.34, 0.40, 0.46):
        for sx in (0.42, 0.50, 0.58):
            x0, y0 = int(w * sx), int(h * sy)
            if a[x0, y0] < 200:
                continue
            c0 = px[x0, y0]
            seen = set([(x0, y0)])
            q = deque([(x0, y0)])
            minx = maxx = x0; miny = maxy = y0
            while q and len(seen) < w * h // 3:
                x, y = q.popleft()
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and a[nx, ny] > 200:
                        c = px[nx, ny]
                        if abs(c[0]-c0[0]) + abs(c[1]-c0[1]) + abs(c[2]-c0[2]) <= tol:
                            seen.add((nx, ny)); q.append((nx, ny))
            if best is None or len(seen) > best[0]:
                best = (len(seen), (minx, miny, maxx + 1, maxy + 1))
    return None if best is None else best[1]


# vung NET MAT cua khuon mat tong hop (long may -> cam), ti le theo anh
FEATURE_BOX = (0.295, 0.325, 0.705, 0.655)


def funnyface(face, overlay_path):
    """FaceFunny — dựng đúng draw() nhánh Mode.FaceFunny (OverlayView.java:700-712),
    đối chiếu ảnh chụp máy thật user gửi:
      - camera chiếm trọn khung dọc (dùng chung portrait_camera với 2 mock kia)
      - overlay nhân vật vẽ NGUYÊN XI, ~55% bề ngang, canh giữa theo
        drawFunnyOverlay (postTranslate canh giữa ngang + dọc)
      - MẶT NHÂN VẬT ĐỂ TRỐNG: asset overlay không có mắt/mũi/miệng và app
        không vẽ nét mặt người dùng vào đó. Thứ động duy nhất là 1 bộ phận rơi
        xuống (drawFunnyComponent) — không vẽ ở mock vì nó là animation runtime,
        vị trí phụ thuộc frameCount.
    Khung dọc 540x1200 = tỉ lệ 360x800, để đặt full-bleed vào frame.
    """
    # nen camera: theo anh chup may that -> mat nguoi dung o SAT DAY (gan ong kinh),
    # phia tren la khong gian phong. Khong dat dau to giua khung nhu ban cu, vi
    # nhu vay mat tong hop se tho ra hai ben dau nhan vat.
    out = Image.new('RGBA', (W2, H2), BG)
    d = ImageDraw.Draw(out)
    for i in range(H2):                       # nen chuyen dan, gia lap anh sang phong
        t = i / H2
        v = int(30 + 26 * (1 - t))
        d.line([(0, i), (W2, i)], fill=(v, v, v + 3, 255))
    sel = synth_face((int(W2 * 1.25), int(W2 * 1.25)), bg=(0, 0, 0, 0))
    out.alpha_composite(sel, ((W2 - sel.width) // 2, int(H2 * 0.72)))
    ov = Image.open(overlay_path).convert('RGBA')
    ow = int(W2 * 0.74)                       # do tu anh chup may: ~74% be ngang
    ov = ov.resize((ow, int(ov.height * ow / ov.width)), Image.LANCZOS)
    out.alpha_composite(ov, ((W2 - ov.width) // 2, int(H2 * 0.24)))
    return out


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    face = synth_face()
    # Cả 3 mock dùng KHUNG DỌC full-bleed cho khớp app thật (camera phủ toàn màn).
    portrait_camera().save(os.path.join(OUT, 'mock_camera_face.png'))
    portrait_camera(effect=facepuzzle).save(os.path.join(OUT, 'mock_ar_facepuzzle.png'))
    made = ['mock_camera_face', 'mock_ar_facepuzzle']
    # Nhan vat cho mock AR phai TRUNG voi anh thumbnail imvFunnyOrigin dung trong
    # screens/funny-puzzle.js, neu khong se mau thuan: thumbnail mot nguoi, lop AR nguoi khac.
    # Doc id tu data_funny.json (overlay dat ten theo id) thay vi lay file dau thu muc.
    import zipfile
    MOCK_CHARACTER = 'Cristiano_Ronaldo'      # = photo(...) trong fnp_drawChrome()
    data = json.loads(zipfile.ZipFile(os.path.join(ROOT, 'apk/app.apk'))
                      .read('assets/face_funny/data_funny.json'))
    entry = next(x for x in data if x['image'] == MOCK_CHARACTER)
    ov = os.path.join(OVERLAY_DIR, f"{entry['id']}.png")
    funnyface(face, ov).save(os.path.join(OUT, 'mock_ar_ronaldo.png'))
    made.append('mock_ar_ronaldo')
    n = 3
    print(f"  nhan vat AR = {entry['name']} (id={entry['id']}, overlay {entry['id']}.png)")
    print(f'sinh {n} ảnh mô phỏng -> assets/v1/50-mock-ar/')
    for m in made:
        print('  ', m)
    print('LƯU Ý: đây là MÔ PHỎNG (mặt tổng hợp + cơ chế đọc từ code), KHÔNG phải')
    print('ảnh chụp app thật. Nơi dùng phải gắn nhãn rõ.')
