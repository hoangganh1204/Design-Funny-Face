#!/usr/bin/env python3
"""make-characters.py — thay bộ ảnh nhân vật Funny Puzzle bằng art mới.

Sinh RA HAI bản cho mỗi nhân vật, đúng như APK gốc:
  assets/v1/20-nhanvat-origin/<Ten>.png   — bản CÓ MẶT, nền đặc, 1024x1024 RGBA.
      Dùng cho: thumbnail trong list (màn 40), imvFunnyOrigin góc phải màn quay,
      và funnyBitmap = BitmapShader cắt từng bộ phận rơi xuống (OverlayView.java:1046).
  reference/21-nhanvat-overlay/<id>.png   — bản MẶT TRỐNG, nền TRONG SUỐT.
      Dùng cho: drawFunnyOverlay() dán đè lên khung camera (OverlayView.java:1106-1120).
      Mặt phải phẳng, không mắt/lông mày/mũi/miệng — giữ tóc, tai, phụ kiện, cổ áo.

Bố cục: KHÔNG tự bịa khung mới. Mỗi nhân vật lấy đúng bbox (vị trí + kích thước) của
ảnh CŨ cùng id, rồi đặt art mới vừa khít vào đó -> thay ảnh mà bố cục toàn màn không xê dịch.

Chạy: python3 "Funny Face/script/make-characters.py"
"""

# Console Windows mac dinh cp1252 nen khong in duoc tieng Viet -> UnicodeEncodeError,
# va script chet GIUA CHUNG, de lai ket qua va do dang ma khong bao gi ro rang.
# Khong bat nguoi chay phai nho dat PYTHONUTF8=1; tu lo lay cho chac.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    if hasattr(_s, 'reconfigure'):
        _s.reconfigure(encoding='utf-8', errors='replace')
import os, sys, json, zipfile, colorsys
import numpy as np
from collections import deque
from PIL import Image, ImageChops, ImageFilter, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Bộ ảnh giao: nằm trong sources/ của chính repo. (Trước đây hardcode
# /home/ubuntu/Downloads/... là đường dẫn máy tác giả, không chạy được ở nơi khác.)
# Ghi đè bằng biến môi trường SRC_IMAGES / SRC_IMAGES_3D nếu để chỗ khác.
_SOURCES = os.path.join(os.path.dirname(ROOT), 'sources')
SRC = os.environ.get('SRC_IMAGES') or os.path.join(_SOURCES, 'images', 'images')
SRC3D = os.environ.get('SRC_IMAGES_3D') or os.path.join(_SOURCES, 'images_3D', 'images_3D')
ORIGIN = os.path.join(ROOT, 'assets/v1/20-nhanvat-origin')
OVERLAY = os.path.join(ROOT, 'reference/21-nhanvat-overlay')
# Bộ ảnh GỐC trích từ APK, giữ bất biến. Bắt buộc phải có: old_box() đo khung bố cục từ
# đây chứ KHÔNG từ 20-nhanvat-origin — thư mục đó chính là thứ script ghi đè, đọc lại nó
# thì mỗi lần chạy lại lấy kết quả lần trước làm mốc, khung cứ teo dần sau mỗi lượt.
BASE = os.path.join(ROOT, 'reference/22-nhanvat-goc-apk')
SIZE = 1024

# ---- ánh xạ file mới -> nhân vật, đối chiếu bằng MẮT trên contact sheet hai bộ ----
# 19 file cho 20 slot. 3 slot Messi (id 2/6/16): messi_1 -> Messi thứ nhất,
# messi_2 -> Messi thứ hai, yamal -> Messi thứ ba (theo yêu cầu). Còn lại id=8
# Neymar_Junior không có ảnh mới (chỉ có 1 file neymar) -> GIỮ NGUYÊN ảnh cũ.
# Bộ 3D thay cho các nhân vật trước đây còn là art 2D (hoạt hoạ viền đậm) — id 1..6, 8.
# id=7 Vinicius_Junior KHÔNG có ảnh 3D trong bộ giao -> vẫn là art 2D, xem ghi chú cuối file.
USE_3D = {1, 2, 3, 4, 5, 6, 7, 8, 19, 21, 22}

# Hai nhân vật THÊM MỚI, không có trong assets/face_funny/data_funny.json của APK.
# Đây là đề xuất thiết kế: muốn chạy thật thì dev phải thêm 2 entry vào file đó.
EXTRA_CHARS = {21: ('Pedri', 'Pedri'), 22: ('Sasuke', 'Sasuke')}


# ─── Nen studio dung lai (SYNTH_BG) ──────────────────────────────────────────
# Bon anh Messi/Ronaldo/Haaland/Mbappe von co san mot nen studio dep: toi o ria, sang
# dan thanh mot quang hao phia sau nguoi. Bon anh Yamal/Vini/Bellingham/Pedri lai moi
# anh mot kieu nen khac nhau (xam phang, xanh nhat, nau...) nen dat canh nhau nhin roi.
# Bang nay dung lai DUNG kieu nen do cho tung nguoi, moi nguoi mot mau rieng.
#   id -> (hue do, nguong tach nen)
# Nguong: cang NHO cang giu nhan vat (an toan) nhung de sot quang hao cu; cang LON cang
# don sach nen nhung de an vao nhan vat. 16 hop voi hau het; rieng Vini phai ha xuong 7
# vi da va vung toi duoi cam gan nhu trung mau voi nen xam cua anh goc.
# Nhân vật có PHỤ KIỆN VẮT NGANG TRÁN (băng đô). Vùng xoá nét mặt phải bắt đầu THẤP hơn
# mặc định, không thì lọc trung vị nuốt luôn băng đô.
#   id -> mép trên vùng xoá, tính theo tỉ lệ chiều cao khung mặt (mặc định 0.10)
# Đã thử 4 kiểu luật TỰ NHẬN DIỆN phụ kiện (bề ngang vệt · tỉ lệ không-phải-da theo hàng ·
# giới hạn trong bề ngang mặt · so sắc độ sau chuẩn hoá sáng). Luật nào cũng kẹt giữa hai
# cực: chặt tay thì sót mắt Ronaldo, lỏng tay thì nuốt băng đô Naruto — vì mặt nạ da trên
# art 3D quá thất thường. Khai báo tay 2 ca thì chắc chắn đúng và sửa được trong 1 giây.
ZONE_TOP = {19: 0.44, 22: 0.44}          # Naruto, Sasuke — mép dưới băng đô

SYNTH_BG = {
    # (hue độ, ngưỡng tách nền, kiểu)
    # Hue được rải sao cho KHÔNG ô nào kề nhau trong lưới 2 cột bị trùng tông.
    # --- Cầu thủ: cùng tông trầm với 4 ảnh gốc, giữ chất poster thể thao ---
    6:  (38,  16, 'deep'),    # Lamine Yamal      — vàng hổ phách (Tây Ban Nha đỏ-vàng)
    7:  (150, 3,  'deep'),    # Vinicius Junior   — xanh lá (Brazil)
    5:  (275, 16, 'deep'),    # Jude Bellingham   — tím violet, tôn áo trắng
    21: (320, 16, 'deep'),    # Pedri             — hồng magenta, hợp áo Barça
    8:  (165, 16, 'deep'),    # Neymar Junior     — xanh ngọc, bổ túc áo vàng Brazil
    # --- Ngoài sân cỏ: rực hơn, giữ đúng sức hút của mấy ô màu phẳng trước đây ---
    10: (205, 16, 'vivid'),   # Donald Trump      — xanh trời, tách tóc vàng + vest navy
    15: (90,  16, 'vivid'),   # Mr.Bean           — xanh chanh, bổ túc vest nâu
    12: (260, 16, 'vivid'),   # Timothe Chalamet  — chàm, làm nổi tóc xoăn nâu
    13: (330, 16, 'vivid'),   # Taylor Swift      — hồng
    14: (45,  16, 'vivid'),   # Leonardo Dicaprio — vàng kim
    11: (280, 16, 'vivid'),   # Jennie            — tím, đúng tinh thần ảnh gốc
    20: (10,  16, 'vivid'),   # Rose              — cam san hô, đúng tinh thần ảnh gốc
    22: (240, 16, 'deep'),    # Sasuke            — chàm sẫm; nhân vật trầm nên giữ tông trầm
}
# Mau da dung cho bon anh goc, tranh trung: Messi 212 · Mbappe 220 · Haaland 354 · Ronaldo 5.

MAP = {
    1:  'kilyan (1).jpeg',          # Kylian_Mbappe      (3D)
    2:  'leo_messi (1).jpeg',       # Leonel_Messi       (3D)
    3:  'erling (1).jpeg',          # Erling_Haaland     (3D)
    4:  'cristiano (1).jpeg',       # Cristiano_Ronaldo  (3D)
    5:  'bellingham (1).jpeg',      # Jude_Bellingham    (3D)
    6:  'yamal (1).jpeg',           # messi -> Lamine Yamal (3D)
    7:  'vini.jpeg',               # Vinicius_Junior   (3D — thay cho art 2D 'vinicius (1).jpeg')
    8:  'neymar (1).jpeg',          # Neymar_Junior      (3D)
    # id 9 Bruno_Mars — ĐÃ BỎ khỏi bản thiết kế theo yêu cầu (khôi phục: 9: 'bruno_mars.jpeg').
    10: 'donal_trump (1).jpeg',     # Donald_Trump
    11: 'jennie (2).jpeg',          # Jennie
    12: 'timothee (1).jpeg',        # Timothe_Chalamet
    13: 'taylor_swift.png',         # Taylor_Swift
    14: 'leonardo.jpeg',            # Leonardo_Dicaprio
    15: 'mr_bean (1).jpeg',         # Mr_Bean
    # id 16 Messi_2 / 17 Ronaldo / 18 Neymar_Jr — ĐÃ BỎ khỏi bản thiết kế theo yêu cầu.
    # Không map nữa -> main() cho vào nhóm "skipped", không sinh origin/overlay cho 3 id này.
    # Muốn khôi phục: trả lại 3 dòng dưới đây rồi chạy lại script.
    #   16: 'messi_2 (1).jpeg',     17: 'ronaldo_2 (1).jpeg',     18: 'neymar_2 (1).jpeg',
    19: 'uzumaki.jpeg',             # Naruto  (art 3D nền lửa, thay 2026-09-20)
    20: 'rose (1).jpeg',            # Rose
    21: 'pedri (1).jpeg',           # Pedri   — THÊM MỚI
    22: 'uchiha.jpeg',              # Sasuke  — THÊM MỚI (art 3D nền khói tím)
}


# Ảnh Trump là thẻ có NÉT VIỀN VẼ SẴN bo góc sát rìa. peel/floodfill không vượt qua
# nét đó nên nó sót lại thành khung chữ nhật trong ảnh đích. Cắt thẳng vào trong nét.
EXTRA_CROP = {10: (26, 24, 998, 741)}

# Hệ số phóng to riêng. Khung đích lấy từ ảnh gốc APK, mà art mới của vài nhân vật lại
# BÈ NGANG hơn bản gốc nên khi fit-vào-khung sẽ bị chặn bởi chiều RỘNG, kết quả chỉ cao
# ~0.65-0.81 khung trong khi mặt bằng chung là 0.85-0.94 -> nhìn lọt thỏm so với ô bên cạnh.
# Số nhân ở đây kéo chiều cao về ~0.90, đo từ chính bảng thống kê bbox.
# Khung CHUẨN dùng chung cho mọi nhân vật: đỉnh nội dung và đáy nội dung trùng nhau hết,
# nên trong lưới không còn cảnh đầu cao đầu thấp. Trước đây mỗi người fit vào bbox của ảnh
# gốc cùng id, mà các bbox đó vốn đã lệch nhau (đỉnh 0.058..0.235) nên lỗi được nhân bản
# sang bộ mới. Bề ngang chặn ở 0.96 khung để không ai bị cắt hai bên.
TOP_FRAC, BOTTOM_FRAC, MAX_W_FRAC = 0.085, 1.0, 0.96

BOOST = {}

# Căn giữa theo KHUÔN MẶT thay vì theo bbox toàn thân. Leonardo có vai đổ mạnh sang phải
# nên bbox tuy cân nhưng ĐẦU lại lệch trái, nhìn rõ là không ở giữa ô.
FACE_CENTER = {14}


def dist(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])


def border_color(im):
    """Màu nền = màu PHỔ BIẾN NHẤT trên viền ảnh.

    Trước đây lấy đúng một điểm im[w//2, 2]; điểm đó hay rơi trúng đường viền sẫm của
    thẻ bo góc, thế là canvas tô một màu còn art mang màu khác -> ảnh ra hai tông và
    remove_bg không bóc nổi lớp trong (ca Trump).
    """
    w, h = im.size
    px = im.load()
    cnt = {}
    step = max(1, w // 200)
    # BỎ hai đầu mỗi cạnh: thẻ bo góc để lại tam giác trắng ở 4 góc, nếu tính cả thì
    # mode ra TRẮNG thay vì màu thẻ -> fill_round_corners lấy chính màu trắng làm đích
    # nên không tô gì, rồi build_origin tô canvas trắng. Đúng lỗi ảnh Trump.
    mx, my = int(w * 0.14), int(h * 0.14)
    # Lùi vào trong một chút: thẻ thường có nét viền/bóng đổ sẫm ngay sát mép, lấy đúng
    # mép sẽ ra màu nét viền chứ không phải màu nền thẻ.
    ix, iy = max(3, int(w * 0.015)), max(3, int(h * 0.015))
    for i in range(mx, w - mx, step):
        for y in (iy, iy + 1, h - 1 - iy, h - 2 - iy):
            c = px[i, y]
            cnt[c] = cnt.get(c, 0) + 1
    for i in range(my, h - my, step):
        for x in (ix, ix + 1, w - 1 - ix, w - 2 - ix):
            c = px[x, i]
            cnt[c] = cnt.get(c, 0) + 1
    return max(cnt, key=cnt.get) if cnt else px[w // 2, 2]


# To goc bo: hinh hoc la chinh, to loang chi la duong lui.
CORNER_THRESH = 75          # nguong to loang cho duong lui
CORNER_MAX_R = 0.25         # ban kinh bo toi da, theo canh ngan
CORNER_SKEW = 1.35          # rx/ry lech qua muc nay = mot phia da chay vao nhan vat
CORNER_BITE = 2             # an them vao trong cung mot chut de nuot dai chuyen tiep mem


def _corner_radius(im, c, d):
    """Do ban kinh bo tai mot goc: di doc HAI canh cho den khi het trang."""
    w, h = im.size
    px = im.load()
    (cx, cy), (dx, dy) = c, d
    lim = min(w, h) // 2
    rx = ry = 0
    while rx < lim and dist(px[cx + dx * rx, cy], (255, 255, 255)) < 70:
        rx += 1
    while ry < lim and dist(px[cx, cy + dy * ry], (255, 255, 255)) < 70:
        ry += 1
    return rx, ry


def _fill_corner(im, c, d, bgc):
    """To tam giac trang o mot goc bo, KHONG dung mau lam duong di.

    Ban cu to loang tu goc voi nguong rong. Cach do coi mau la duong di, nen khi nhan
    vat mac do CUNG MAU voi trang giay ma the dan len thi mach loang chui thang vao
    quan ao: ao phong TRANG cua Leonardo chay xuong sat canh duoi, cham vao goc trang,
    va ca ben vai bi to thanh mau the. Siet nguong chi thu hep thiet hai thanh mot net
    vien manh chay doc mep sang nhat cua ao — van la loi.

    Goc bo la chuyen HINH HOC, nen do bang hinh hoc: di doc hai canh tu goc cho den khi
    het trang. Voi goc bo that, hai so do bang nhau (do duoc 100-147 px, lech duoi 10%
    tren ca bo anh nguon). Khi mot phia chay vao nhan vat no dai vot len — Leonardo BR
    do 387 ngang so voi 121 doc — nen lay so NHO khi hai so lech qua CORNER_SKEW.

    Ca the trang co net vien ve san (anh Trump) thi ca hai canh deu trang het nua anh;
    do khong phai goc bo, va van can to loang nhu cu.
    """
    w, h = im.size
    rx, ry = _corner_radius(im, c, d)
    lim = int(min(w, h) * CORNER_MAX_R)
    # Ca hai canh deu trang het nua anh -> khong phai goc bo ma la the TRANG co net
    # vien ve san (anh Trump). To loang van dung cho ca do.
    both_wide = rx >= lim and ry >= lim
    if both_wide or max(rx, ry) <= min(rx, ry) * CORNER_SKEW:
        ImageDraw.floodfill(im, c, bgc, thresh=CORNER_THRESH)
        return
    # Hai so do lech nhau -> phia dai hon da chay ra khoi goc. Lay phia ngan.
    r = min(rx, ry)
    if r <= 0:
        return
    (cx, cy), (dx, dy) = c, d
    x0, y0 = min(cx, cx + dx * (r - 1)), min(cy, cy + dy * (r - 1))
    box = (x0, y0, x0 + r, y0 + r)
    ox, oy = cx + dx * (r - 1) - x0, cy + dy * (r - 1) - y0      # tam cung, trong box
    yy, xx = np.ogrid[:r, :r]
    outside = ((xx - ox) ** 2 + (yy - oy) ** 2) > (r - CORNER_BITE) ** 2
    tile = np.asarray(im.crop(box)).copy()
    tile[outside] = bgc[:tile.shape[2]]
    im.paste(Image.fromarray(tile, im.mode), box)


def fill_round_corners(im):
    """Thẻ BO GÓC -> sau khi cắt, 4 góc còn tam giác trắng. Tô loang bằng màu nền của thẻ."""
    w, h = im.size
    bgc = border_color(im)
    # Ngưỡng rộng (75) để nuốt luôn dải chuyển tiếp mềm giữa viền trắng và màu thẻ —
    # để 45 thì còn sót một nét viền mảnh, nét đó lọt vào content_box rồi bị dán vào
    # ảnh đích thành khung chữ nhật bo góc lạ (ca Trump).
    # CHỈ xử lý khi góc thật sự TRẮNG (đặc trưng của thẻ bo góc trên nền trắng). Bản
    # trước chỉ kiểm tra "góc khác màu nền" -> với ảnh nền chuyển màu, góc tối cũng thoả,
    # rồi tô loang ngưỡng 75 chui thẳng vào vùng tối trên mặt (ảnh Haaland mất nửa mặt).
    dirs = {(0, 0): (1, 1), (w - 1, 0): (-1, 1),
            (0, h - 1): (1, -1), (w - 1, h - 1): (-1, -1)}
    for c in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        cc = im.load()[c]
        if dist(cc, (255, 255, 255)) < 70 and dist(cc, bgc) > 60:
            _fill_corner(im, c, dirs[c], bgc)
    return im


def peel(im):
    """Bóc các lớp khung lồng nhau.

    Ảnh nguồn hay có dạng: nền trắng -> thẻ bo góc màu -> (đôi khi) thêm một thẻ nữa
    nhạt hơn -> mới tới nhân vật (ảnh Trump đúng kiểu này). Nếu chỉ bóc một lớp thì
    lớp trong còn lại sẽ thành mảng màu lạ nằm giữa ảnh và remove_bg không ăn được.
    Quy tắc: nếu vùng-khác-màu-viền vẫn chiếm >=85% cả hai chiều thì đó là MỘT LỚP KHUNG
    nữa chứ không phải nhân vật -> cắt vào rồi lặp. Tối đa 3 lớp, và phải nhỏ đi thật sự
    thì mới lặp tiếp (tránh lặp vô hạn).
    """
    for _ in range(3):
        w, h = im.size
        bg = border_color(im)
        bb = content_box(im, bg)
        if not bb:
            break
        bw, bh = bb[2] - bb[0], bb[3] - bb[1]
        # Lớp khung thật thì lề ĐỀU cả bốn phía và đều khác 0. Dải chuyển màu mềm chỉ
        # đẩy bbox lệch MỘT phía (Trump: lề = 0/68/0/0) — trước đây bị nhận nhầm là khung
        # nên peel cứ gọt dần ảnh, nhân vật cuối cùng teo lại.
        mar = [bb[0], bb[1], w - bb[2], h - bb[3]]
        even = min(mar) >= 1 and max(mar) <= 0.08 * min(w, h)
        if bw >= w * 0.85 and bh >= h * 0.85 and (bw < w or bh < h) and even:
            im = im.crop(bb)
            im = fill_round_corners(im.copy())
            continue
        break
    return fill_round_corners(im.copy())


def content_box(im, bg, erode=0):
    d = ImageChops.difference(im, Image.new('RGB', im.size, bg)).convert('L')
    m = d.point(lambda v: 255 if v > 30 else 0)
    if erode:
        m = m.filter(ImageFilter.MinFilter(erode))    # giết vành mảnh, giữ khối đặc
    return m.getbbox()


def old_box(name):
    """bbox của ảnh GỐC APK cùng id — khung đích để art mới lấp vào."""
    p = os.path.join(BASE, name + '.png')
    im = Image.open(p).convert('RGB')
    bb = content_box(im, im.load()[2, 2])
    return bb or (0, 0, SIZE, SIZE)



# ─────────────────────────────────────────────────── nen studio dung lai
def _local_grad(a):
    """Chenh lech lon nhat giua moi diem va 4 diem ke ben — do 'ram rap' cuc bo."""
    h, w, _ = a.shape
    gx = np.zeros((h, w), np.float32); gy = np.zeros((h, w), np.float32)
    d = np.abs(a[:, 1:, :] - a[:, :-1, :]).max(axis=2)
    gx[:, :-1] = d; gx[:, 1:] = np.maximum(gx[:, 1:], d)
    d = np.abs(a[1:, :, :] - a[:-1, :, :]).max(axis=2)
    gy[:-1, :] = d; gy[1:, :] = np.maximum(gy[1:, :], d)
    return np.maximum(gx, gy)


def _bg_basis(x, y):
    """Co so ham de khop mat cong cua nen: da thuc bac 5 + so hang ban kinh quanh HAI tam
    (duoi-giua va sau-dau). Khong co nhom ban kinh sau-dau thi quang hao phia sau nguoi
    khong khop duoc, bi cham nham thanh nhan vat va sot lai thanh mot mang mau cu."""
    out = []
    for i in range(6):
        for j in range(6 - i):
            out.append(x ** i * y ** j)
    for cx, cy in ((.5, 1.02), (.5, .35)):
        r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        out += [r, r * r, r ** 3, np.exp(-r * 3.0)]
    return np.stack(out, axis=-1)


def _flood_from_border(ok):
    """Vung True noi lien voi vien TREN/TRAI/PHAI. Khong lay vien duoi — nhan vat chay
    ra khoi canh duoi nen vien do khong phai lúc nào cũng là nền."""
    h, w = ok.shape
    cur = np.zeros((h, w), bool)
    cur[0, :] = True; cur[:, 0] = True; cur[:, -1] = True
    cur &= ok
    n = -1
    while cur.sum() != n:
        n = cur.sum()
        nxt = cur.copy()
        nxt[1:, :] |= cur[:-1, :]; nxt[:-1, :] |= cur[1:, :]
        nxt[:, 1:] |= cur[:, :-1]; nxt[:, :-1] |= cur[:, 1:]
        cur = nxt & ok
    return cur


def subject_alpha(rgb, thr=16, ring=14, iters=4, scale=2, gtol=8):
    """Mat na nhan vat. Khop mot mat cong muot cho NEN roi lay phan sai lech lam nguoi.

    Hai tin hieu phai thoa DONG THOI moi duoc coi la nen:
      1. sai lech so voi mo hinh nen <= thr  -> chan ao trang / toc sang (sai lech lon)
      2. do ram rap cuc bo <= gtol           -> chan vung toi muot cua da (sai lech nho)
    Chi mot trong hai deu tung thu va deu hong: (1) mot minh an mat cam cua Vini, (2) mot
    minh lan xuyen qua ao trang cua Bellingham.

    Lap lai `iters` lan, moi lan huan luyen lai mo hinh bang chinh cac diem vua nhan la
    nen -> quang hao sau dau dan dan duoc mo hinh hoa thay vi bi nham la nhan vat.
    """
    small = rgb.filter(ImageFilter.GaussianBlur(1.0)).resize(
        (rgb.width // scale, rgb.height // scale), Image.BILINEAR)
    a = np.asarray(small, np.float32)
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    Ball = _bg_basis((xx / w).ravel(), (yy / h).ravel())
    smooth = _local_grad(a) <= gtol

    train = np.zeros((h, w), bool)
    train[:ring, :] = True; train[:, :ring] = True; train[:, -ring:] = True
    bgm = None
    for it in range(iters):
        B = Ball.reshape(h, w, -1)[train]
        fit = np.zeros_like(a)
        for c in range(3):
            coef, *_ = np.linalg.lstsq(B, a[..., c][train], rcond=None)
            fit[..., c] = (Ball @ coef).reshape(h, w)
        bgm = _flood_from_border((np.abs(a - fit).max(axis=2) <= thr) & smooth)
        if it < iters - 1:
            train = bgm.copy()
            train[:ring, :] = True; train[:, :ring] = True; train[:, -ring:] = True
    # Chi giu KHOI LIEN MACH chua nhan vat. Anh nguon kieu the bo goc con sot mot net
    # vien manh chay quanh ria; net do khong dinh vao nguoi nhung van la 'khac nen' nen
    # loc theo khoi lien mach moi bo duoc. Mam gieo o day-giua: nhan vat luon dung day,
    # canh giua khung (py = bot_y - nh, px canh giua) nen vung do chac chan la nguoi.
    fgm = ~bgm
    seed = np.zeros_like(fgm)
    seed[int(h * .85):, int(w * .40):int(w * .60)] = True
    cur = fgm & seed
    n = -1
    while cur.sum() != n:
        n = cur.sum()
        nxt = cur.copy()
        nxt[1:, :] |= cur[:-1, :]; nxt[:-1, :] |= cur[1:, :]
        nxt[:, 1:] |= cur[:, :-1]; nxt[:, :-1] |= cur[:, 1:]
        cur = nxt & fgm
    if cur.sum() > fgm.sum() * 0.5:      # chi ap khi mam that su bat duoc than nguoi
        fgm = cur
    fg = Image.fromarray((fgm * 255).astype(np.uint8)).resize(rgb.size, Image.BILINEAR)
    fg = fg.point(lambda v: 255 if v > 127 else 0)
    fg = fg.filter(ImageFilter.MaxFilter(5))      # bit lo nho trong nguoi
    fg = fg.filter(ImageFilter.MinFilter(9))      # co lai, cat vien con lem mau nen cu
    return fg.filter(ImageFilter.GaussianBlur(1.3))


# Hai tang mau. HINH DANG anh sang giong het nhau (cung mot quang sang, cung huong toi
# dan) nen ca luoi van doc nhu MOT bo; chi khac do ruc:
#   deep  — dung y profile do duoc tu bon anh goc. Dam, bac, kieu poster the thao.
#   vivid — dau toi sang hon va dau sang GIU BAO HOA (0.70 thay vi 0.38). Dung cho nhom
#           ngoai san co: o cua ho von la nhung mang mau ruc (vang, cam, cyan, hong), ha
#           bao hoa xuong 0.38 la thanh khaki/nau duc — mat dung cai bat mat can co.
STYLES = {
    'deep':  ((0.13, 0.84), (0.74, 0.38)),
    'vivid': ((0.34, 0.90), (0.82, 0.70)),
}


def studio_bg(hue, style='deep'):
    """Nen studio dung lai theo dung profile do duoc tu bon anh dep: mot quang sang lon
    tam o duoi-giua, toi dan ve phia tren va ra ria."""
    (dl, ds), (ll, ls) = STYLES[style]
    dark = colorsys.hls_to_rgb(hue / 360.0, dl, ds)
    light = colorsys.hls_to_rgb(hue / 360.0, ll, ls)
    y, x = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
    d = np.sqrt((x - SIZE / 2) ** 2 + (y - SIZE * 1.02) ** 2) / (SIZE * 1.12)
    t = np.clip(1.0 - d, 0, 1) ** 1.45 * 0.97 + 0.03
    out = np.stack([(dark[c] + (light[c] - dark[c]) * t) * 255 for c in range(3)], axis=-1)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def finish(org, cfg):
    """Tra ve (origin, cut) cuoi cung tu canvas tho.

    Dung MOT mat na duy nhat cho ca hai: anh origin (nen studio moi, neu co) va ban
    trong suot `cut` (nguon cua overlay AR). Truoc day `cut` di duong rieng qua
    remove_bg() — bo tach cu — nen overlay con nguyen mot mang nen chu nhat, keo theo
    anh mo phong vung camera AR nhin nhu bi loi."""
    rgb = org.convert('RGB')
    alpha = subject_alpha(rgb, thr=cfg[1] if cfg else 16)
    cut = rgb.convert('RGBA')
    cut.putalpha(alpha)
    if cfg:
        out = studio_bg(cfg[0], cfg[2]).convert('RGBA')
        out.paste(rgb, (0, 0), alpha)
        org = out
    return org, cut


def cover_canvas(im, k, bb, px, py, bg):
    """Khung SIZE×SIZE cắt ra từ CHÍNH ảnh nguồn đã phóng theo hệ số k, canh sao cho vùng
    `bb` (bbox nhân vật trong ảnh nguồn) rơi đúng vào toạ độ (px, py) của khung đích.

    Vì sao cần: trước đây nền là MỘT MÀU PHẲNG lấy ở viền ảnh nguồn (border_color), rồi
    dán ảnh đã cắt — vốn mang sẵn dải chuyển màu sáng dần vào giữa — đè lên. Hai thứ đó
    không bao giờ khớp, nên quanh nhân vật luôn lộ một KHUNG CHỮ NHẬT đổi màu (rõ nhất ở
    Haaland/Ronaldo: viền đỏ đậm bọc quanh vùng đỏ nhạt). Lấy nền từ chính ảnh nguồn thì
    dải chuyển màu chạy liền mạch ra tới mép, không còn đường gãy nào.

    Chỗ nào ảnh nguồn phóng lên vẫn không phủ tới thì KÉO DÀI hàng/cột ngoài cùng ra
    (edge-replicate) — vẫn đúng tông của dải chuyển màu, thay vì tô đè một màu phẳng.
    """
    fw = max(1, int(round(im.width * k)))
    fh = max(1, int(round(im.height * k)))
    full = im.resize((fw, fh), Image.LANCZOS)
    ox = int(round(bb[0] * k)) - px
    oy = int(round(bb[1] * k)) - py
    sx0, sy0 = max(0, ox), max(0, oy)
    sx1, sy1 = min(fw, ox + SIZE), min(fh, oy + SIZE)
    canvas = Image.new('RGB', (SIZE, SIZE), bg)
    if sx1 <= sx0 or sy1 <= sy0:
        return canvas
    part = full.crop((sx0, sy0, sx1, sy1))
    dx, dy = sx0 - ox, sy0 - oy
    canvas.paste(part, (dx, dy))
    pw, ph = part.size
    if dy > 0:                                    # kéo dài hàng trên cùng lên
        canvas.paste(part.crop((0, 0, pw, 1)).resize((pw, dy)), (dx, 0))
    if dy + ph < SIZE:                            # kéo dài hàng dưới cùng xuống
        canvas.paste(part.crop((0, ph - 1, pw, ph)).resize((pw, SIZE - dy - ph)), (dx, dy + ph))
    if dx > 0:                                    # kéo dài cột trái (đã gồm phần trên/dưới)
        canvas.paste(canvas.crop((dx, 0, dx + 1, SIZE)).resize((dx, SIZE)), (0, 0))
    if dx + pw < SIZE:                            # kéo dài cột phải
        canvas.paste(canvas.crop((dx + pw - 1, 0, dx + pw, SIZE)).resize((SIZE - dx - pw, SIZE)),
                     (dx + pw, 0))
    return canvas


def build_origin(path, target, crop=None, boost=1.0, face_center=False):
    """1024x1024 RGBA: nền đặc màu của art mới, nhân vật đặt vừa khung target."""
    im = Image.open(path).convert('RGB')
    if crop:
        im = im.crop(crop)
    im = peel(im)
    # Ảnh nguồn kiểu THẺ BO GÓC (Jennie…): 4 góc là tam giác trắng. Trước đây nền đích tô
    # một màu phẳng nên góc trắng bị che mất; nay nền lấy từ chính ảnh nguồn nên phải tô
    # loang 4 góc trước, không thì lộ 4 mảng trắng ở rìa ảnh. Hàm tự bỏ qua ảnh không phải
    # thẻ bo góc (chỉ chạy khi góc gần TRẮNG và khác màu nền).
    im = fill_round_corners(im.copy())
    w, h = im.size
    bg = border_color(im)
    bb = content_box(im, bg) or (0, 0, w, h)
    # Vài ảnh còn một vành sáng mỏng sát mép (rìa thẻ bo góc không tô hết) -> bbox phồng
    # ra gần bằng cả khung, kéo theo cả nét viền thẻ vào ảnh đích. Nếu bbox phủ >=95%
    # cả hai chiều thì đo lại sau khi CO mặt nạ: vành mảnh chết, nhân vật còn nguyên.
    # MỘT chiều phủ >=95% là đủ nghi: thẻ có dải chuyển màu mềm chạy hết bề ngang cũng
    # lọt ngưỡng 30 và kéo bbox ra sát mép (ca Trump, cao 0.90 nên điều kiện AND trượt).
    # Với nhân vật đặc thì phép co gần như không đổi bbox, nên nới sang OR là an toàn.
    if bb[2] - bb[0] >= w * 0.95 or bb[3] - bb[1] >= h * 0.95:
        bb2 = content_box(im, bg, erode=9)
        if bb2 and (bb2[2] - bb2[0]) * (bb2[3] - bb2[1]) > w * h * 0.04:
            bb = bb2
    sub = im.crop(bb)
    sub_cut = remove_bg(sub.convert('RGBA'))     # cắt nền NGAY trên ảnh nguồn
    # Bỏ qua `target` (bbox ảnh gốc cùng id) — xem chú thích ở TOP_FRAC. Giữ tham số để
    # không phá chữ ký hàm và để tra cứu khi cần đối chiếu bố cục cũ.
    top_y = int(SIZE * TOP_FRAC)
    bot_y = int(SIZE * BOTTOM_FRAC)
    k = (bot_y - top_y) / sub.height * boost
    if sub.width * k > SIZE * MAX_W_FRAC:            # quá bè -> chặn theo bề ngang
        k = SIZE * MAX_W_FRAC / sub.width
    nw, nh = max(1, int(sub.width * k)), max(1, int(sub.height * k))
    sub_full = sub
    sub = sub.resize((nw, nh), Image.LANCZOS)
    px = (SIZE - nw) // 2
    if face_center:
        fm = skin_mask(sub.convert('RGB'))
        fb, _ = largest_blob(fm, (0, 0, nw, int(nh * 0.72)), prefer=(0.20, 0.05, 0.80, 0.60))
        bbf = fb.getbbox()
        if bbf:
            S = fb.size[0]
            cx = (bbf[0] + bbf[2]) / 2 / S * nw
            px = int(SIZE / 2 - cx)
    py = bot_y - nh
    # Nền = chính ảnh nguồn, cắt liền mạch (xem cover_canvas). KHÔNG tô màu phẳng rồi
    # dán đè nữa — đó là nguyên nhân của khung viền lệch màu quanh nhân vật.
    out = cover_canvas(im, k, bb, px, py, bg).convert('RGBA')
    # Bản ĐÃ CẮT NỀN, cùng hệ toạ độ. Phải cắt trên ẢNH NGUỒN chứ không phải trên canvas:
    # canvas được tô một màu phẳng nên biên của nó luôn phẳng, còn dải chuyển màu của ảnh
    # nguồn lại nằm LỌT BÊN TRONG -> mọi phép dò nền đo ở biên canvas đều vô hiệu.
    cut = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    cut.paste(sub_cut.resize((nw, nh), Image.LANCZOS), (px, py))
    return out, cut


# ------------------------------------------------------------------ mặt trống
def skin_mask(rgb, alpha=None):
    """Mặt nạ da — luật ngưỡng kinh điển, làm bằng phép kênh của PIL (tốc độ C)."""
    R, G, B = rgb.split()
    m = R.point(lambda v: 255 if v > 90 else 0)
    m = ImageChops.multiply(m, G.point(lambda v: 255 if v > 38 else 0))
    m = ImageChops.multiply(m, B.point(lambda v: 255 if v > 18 else 0))
    m = ImageChops.multiply(m, ImageChops.subtract(R, G).point(lambda v: 255 if v > 12 else 0))
    m = ImageChops.multiply(m, ImageChops.subtract(R, B).point(lambda v: 255 if v > 20 else 0))
    # Cam rực (áo Naruto 246,129,34) và tóc vàng (250,210,80) lọt hết 5 luật trên vì
    # chúng cũng "đỏ hơn xanh". Khác biệt thật: da người có G-B hẹp (~15..70), còn cam
    # và vàng thì G-B rất lớn. Thêm ràng buộc này mới tách được.
    gb = ImageChops.subtract(G, B)
    m = ImageChops.multiply(m, gb.point(lambda v: 255 if 8 < v < 78 else 0))
    if alpha is not None:
        # Sau remove_bg, vùng nền tuy alpha=0 nhưng RGB vẫn giữ màu nền cũ. Màu cam/hồng
        # của nền lọt hết luật da -> largest_blob bắt nhầm NỀN làm khuôn mặt. Phải chặn.
        m = ImageChops.multiply(m, alpha.point(lambda v: 255 if v > 200 else 0))
    return m


def largest_blob(mask, box=None, prefer=None):
    """Thành phần liên thông lớn nhất, chạy trên bản thu nhỏ cho nhanh (thuần Python).

    320 chứ không phải 160: ở 160 khuôn mặt chỉ còn ~47px, hốc mắt ~4px và khe da giữa
    mắt với tóc mỏng hơn 1px nên biến mất -> hốc mắt "thông" ra ngoài, fill_holes không
    coi là lỗ nữa, thế là mắt không bị xoá (ca Jennie / Timothée).
    """
    S = 320
    small = mask.resize((S, S), Image.NEAREST)
    px = small.load()
    if box:
        x0, y0, x1, y1 = [int(v * S / mask.size[0]) for v in box]
    else:
        x0, y0, x1, y1 = 0, 0, S, S
    seen = [[False] * S for _ in range(S)]
    best, bestpix = 0, None
    for sy in range(y0, min(y1, S)):
        for sx in range(x0, min(x1, S)):
            if px[sx, sy] < 128 or seen[sy][sx]:
                continue
            q = deque([(sx, sy)])
            seen[sy][sx] = True
            comp = []
            while q:
                x, y = q.popleft()
                comp.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < S and 0 <= ny < S and not seen[ny][nx] and px[nx, ny] >= 128:
                        seen[ny][nx] = True
                        q.append((nx, ny))
            if prefer is None:
                score = len(comp)
            else:
                # Ưu tiên thành phần nằm trong Ô MẶT (giữa-trên khung) thay vì thành
                # phần to nhất — nếu không, mảng áo/tay lớn hơn mặt sẽ bị chọn nhầm.
                px0, py0, px1, py1 = [int(v * S) for v in prefer]
                score = sum(1 for (x, y) in comp if px0 <= x < px1 and py0 <= y < py1)
            if score > best:
                best, bestpix = score, comp
    out = Image.new('L', (S, S), 0)
    if bestpix:
        d = out.load()
        for x, y in bestpix:
            d[x, y] = 255
    return out, S


def fill_holes(m):
    """Lấp lỗ: tô loang từ NGOÀI vào phần nền, phần nền không chạm tới = lỗ."""
    S = m.size[0]
    px = m.load()
    seen = [[False] * S for _ in range(S)]
    q = deque()
    for i in range(S):
        for (x, y) in ((i, 0), (i, S - 1), (0, i), (S - 1, i)):
            if px[x, y] < 128 and not seen[y][x]:
                seen[y][x] = True
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < S and 0 <= ny < S and not seen[ny][nx] and px[nx, ny] < 128:
                seen[ny][nx] = True
                q.append((nx, ny))
    out = Image.new('L', (S, S), 0)
    d = out.load()
    for y in range(S):
        for x in range(S):
            if px[x, y] >= 128 or not seen[y][x]:
                d[x, y] = 255
    return out


BG_DIFF = 34          # lệch tối đa so với nền nội suy
BG_COL_FILL = 0.45    # chỉ vá theo cột từ mốc này xuống (che phần thân)


def border_is_flat(im, S=96, tol=26):
    """Nền PHẲNG hay CHUYỂN MÀU? Đo độ tản của màu trên vành biên."""
    sm = im.convert('RGB').resize((S, S), Image.BILINEAR)
    px = sm.load()
    # CHỈ lấy cạnh TRÊN và phần trên hai cạnh bên. Sau khi chuẩn hoá khung, nhân vật chạm
    # đáy và gần chạm hai mép, nên lấy cả vành biên sẽ nhặt phải điểm trên người -> kết
    # luận nhầm "nền chuyển màu" rồi đi nhánh an toàn, để lại quầng cho cả ảnh nền phẳng.
    up = int(S * 0.40)
    vals = [px[i, 0] for i in range(S)] + [px[i, 1] for i in range(S)] + \
           [px[0, i] for i in range(up)] + [px[S - 1, i] for i in range(up)]
    lo = [min(v[c] for v in vals) for c in range(3)]
    hi = [max(v[c] for v in vals) for c in range(3)]
    return max(hi[c] - lo[c] for c in range(3)) <= tol


def remove_bg_flat(origin):
    """Nền một tông: loang từ các điểm biên đúng màu nền. Sạch tuyệt đối, dùng cho
    bộ ảnh nền phẳng (Trump, Jennie, Mr Bean, Sasuke...). Mô hình khuếch tán tuy tổng
    quát hơn nhưng luôn để lại một quầng mỏng nên không dùng ở đây."""
    S = 384
    small = origin.convert('RGB').resize((S, S), Image.BILINEAR)
    SENT = (1, 254, 2)
    px = small.load()
    bg = border_color(small.crop((0, 0, S, int(S * 0.40))))   # lấy màu nền ở NỬA TRÊN
    border = [(i, 0) for i in range(S)] + [(i, S - 1) for i in range(S)] + \
             [(0, i) for i in range(S)] + [(S - 1, i) for i in range(S)]
    for (x, y) in border:
        if dist(px[x, y], bg) > 46 or px[x, y] == SENT:
            continue
        ImageDraw.floodfill(small, (x, y), SENT, thresh=30)
        px = small.load()
    R, G, B = small.split()
    m = ImageChops.multiply(R.point(lambda v: 255 if abs(v - SENT[0]) < 3 else 0),
                            G.point(lambda v: 255 if abs(v - SENT[1]) < 3 else 0))
    m = ImageChops.multiply(m, B.point(lambda v: 255 if abs(v - SENT[2]) < 3 else 0))
    bgmask = m.resize(origin.size, Image.BILINEAR).point(lambda v: 255 if v > 128 else 0)
    bgmask = bgmask.filter(ImageFilter.MaxFilter(3))
    alpha = ImageChops.invert(bgmask).filter(ImageFilter.GaussianBlur(1.2))
    alpha = alpha.point(lambda v: 0 if v < 90 else (255 if v > 170 else v))
    out = origin.copy()
    out.putalpha(ImageChops.multiply(origin.split()[3], alpha))
    return out


def remove_bg(origin, bg=None):
    if border_is_flat(origin):
        return remove_bg_flat(origin)
    return remove_bg_gradient(origin)


def remove_bg_gradient(origin):
    """Nền CHUYỂN MÀU -> trong suốt.

    Ghi lại vì đã thử hỏng nhiều cách: floodfill theo hạt giống, lan theo bước cục bộ,
    mô hình nền bằng khuếch tán, chặn theo biên cạnh — tất cả đều hoặc ăn thủng nhân vật
    (áo gần trùng màu nền), hoặc để lại quầng dày (ảnh 3D có viền sáng ôm quanh người).

    Cách chốt ở đây ưu tiên AN TOÀN: ước lượng nền hai chiều — nội suy trái↔phải theo
    HÀNG và trên↔dưới theo CỘT — rồi coi là nền nếu khớp MỘT trong hai (đủ để tả dải toả
    tròn). Sau đó chỉ giữ phần nối với biên, và vá theo cột ở NỬA DƯỚI để bảo vệ thân áo.

    Đánh đổi có chủ ý: cách này KHÔNG BAO GIỜ ăn thủng nhân vật, nhưng có thể còn sót
    một ít nền. Sót nền là lỗi nhìn thấy và sửa được; thủng người thì hỏng hẳn asset.
    Muốn sạch tuyệt đối thì xuất lại ảnh nguồn với NỀN PHẲNG — khi đó nhánh
    remove_bg_flat() ở trên xử lý sạch 100%.
    """
    S = 256
    im = origin.convert('RGB').resize((S, S), Image.BILINEAR)
    px = im.load()
    keep = bytearray(S * S)
    for y in range(S):
        L, R = px[0, y], px[S - 1, y]
        fy = y / (S - 1)
        for x in range(S):
            Tp, Bp = px[x, 0], px[x, S - 1]
            fx = x / (S - 1)
            p = px[x, y]
            dr = sum(abs(p[c] - (L[c] * (1 - fx) + R[c] * fx)) for c in range(3))
            dc = sum(abs(p[c] - (Tp[c] * (1 - fy) + Bp[c] * fy)) for c in range(3))
            if dr < BG_DIFF or dc < BG_DIFF:
                keep[y * S + x] = 1
    seen = bytearray(S * S)
    q = deque()
    for i in range(S):
        for (x, y) in ((i, 0), (i, S - 1), (0, i), (S - 1, i)):
            k = y * S + x
            if not seen[k]:
                seen[k] = 1; q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < S and 0 <= ny < S:
                k = ny * S + nx
                if keep[k] and not seen[k]:
                    seen[k] = 1; q.append((nx, ny))
    m = Image.new('L', (S, S), 0)
    md = m.load()
    for y in range(S):
        row = y * S
        for x in range(S):
            if seen[row + x]:
                md[x, y] = 255
    y0 = int(S * BG_COL_FILL)
    for x in range(S):
        first = None
        for y in range(y0, S):
            if not md[x, y] and all(not md[x, yy] for yy in range(y, min(y + 4, S))):
                first = y; break
        if first is not None:
            for y in range(first, S):
                md[x, y] = 0
    bgmask = m.resize(origin.size, Image.BILINEAR).point(lambda v: 255 if v > 128 else 0)
    bgmask = bgmask.filter(ImageFilter.MaxFilter(3))
    alpha = ImageChops.invert(bgmask).filter(ImageFilter.GaussianBlur(1.2))
    alpha = alpha.point(lambda v: 0 if v < 90 else (255 if v > 170 else v))
    out = origin.copy()
    out.putalpha(ImageChops.multiply(origin.split()[3], alpha))
    return out


def blank_face(img, zone_top=0.10):
    """Xoá nét mặt, trám bằng da.

    Cách cũ đi tìm LỖ trong mặt nạ da (mắt/mũi/miệng là lỗ nằm lọt trong da) rồi tô đè
    màu da trung bình. Nó phụ thuộc hoàn toàn vào `skin_mask`, mà mặt nạ da trên art 3D
    render thì rất thất thường: kết quả hay sót hẳn một bên mắt, miệng nhoè, và để lại
    các mảng lem vuông vức — nhìn như ảnh lỗi chứ không ra "mặt trống".

    Cách này không đi tìm từng nét nữa. Nó khoanh VÙNG NÉT MẶT (elip nội tiếp khung mặt,
    phủ từ chân mày xuống quá miệng) rồi thay cả vùng đó bằng chính khuôn mặt này đã lọc
    trung vị mạnh: phép lọc trung vị xoá các chi tiết nhỏ (mắt, mũi, miệng) nhưng GIỮ khối
    sáng tối, nên da vẫn có bóng đổ, không bị bệt phẳng. Biên vùng làm mềm nên không thấy
    đường ghép.

    Cằm và hai bên quai hàm nằm NGOÀI elip nên râu (Messi/Neymar) và râu mèo (Naruto)
    vẫn còn — đúng quy ước overlay gốc của APK.
    """
    rgb = img.convert('RGB')
    alpha = img.split()[3]
    W, H = rgb.size
    sk = skin_mask(rgb, alpha)
    blob, S = largest_blob(sk, (0, 0, W, int(H * 0.72)), prefer=(0.30, 0.14, 0.70, 0.56))
    closed = blob.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
    face = fill_holes(closed).resize((W, H), Image.BILINEAR).point(lambda v: 255 if v > 110 else 0)
    fb = face.getbbox()
    if not fb:
        return img
    fx0, fy0, fx1, fy1 = fb
    fw, fh = fx1 - fx0, fy1 - fy0
    if fw < W * 0.12 or fh < H * 0.12:
        return img

    # SIÊU-ELIP (|dx/a|^4 + |dy/b|^4 <= 1) chứ không phải elip thường. Elip thóp rất nhanh
    # về hai đầu, mà khung mặt thì kéo dài xuống tận cổ nên MẮT nằm gần ĐỈNH elip — đúng
    # chỗ hẹp nhất. Đo ra: ở tầm mắt, elip chỉ phủ x=425..655 trong khi mắt trái ở
    # x=400..490 -> lọt ra ngoài vùng xoá, và đó mới là lý do thật của việc sót mắt
    # (không phải mặt nạ da như hai lần đoán trước). Siêu-elip mũ 4 gần như chữ nhật bo
    # góc: ở cùng độ cao đó phủ x=374..706, trùm hết bề ngang mặt.
    top, bot = fy0 + fh * zone_top, fy0 + fh * 0.90
    cy = (top + bot) / 2
    a, b = fw * 0.60, (bot - top) / 2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    se = (np.abs((xx - (fx0 + fx1) / 2) / a) ** 6 + np.abs((yy - cy) / b) ** 6) <= 1.0
    zone = Image.fromarray((se * 255).astype(np.uint8))
    # Chặn bằng mặt nạ da ĐÃ LẤP LỖ RỒI GIÃN RỘNG, giao thêm với mặt nạ nhân vật:
    #  - lấp lỗ + giãn: bịt các lỗ mà mặt nạ da để lại đúng chỗ con mắt (không thì sót
    #    nguyên một bên mắt như ca Ronaldo);
    #  - vẫn là mặt nạ DA nên phụ kiện không phải da bị loại — băng đô Naruto giữ nguyên
    #    thay vì bị lọc trung vị nhoè thành một vệt tối.
    # KHÔNG dùng mặt nạ da để PHỦ nữa. Mặt nạ da trên art 3D hay khuyết hẳn một mảng ở
    # ngang tầm mắt (mặt hơi nghiêng thì phía ngoài lông mày là tóc chứ không có da),
    # mà mảng khuyết đó lại HỞ ra ngoài nên không phép lấp lỗ nào bịt được — kết quả sót
    # nguyên một bên mắt. Vùng phủ giờ chỉ là elip ∩ mặt nạ nhân vật.
    #
    zone = ImageChops.multiply(zone, alpha)
    zone = zone.filter(ImageFilter.GaussianBlur(11))

    # Trường da mượt dựng bằng TÍCH CHẬP CHUẨN HOÁ: làm mờ (ảnh × mặt nạ da) rồi chia cho
    # (mặt nạ da đã làm mờ). Nhờ phép chia, chỉ điểm DA mới đóng góp — màu tóc/băng đô
    # không lọt vào. Trước đây dùng lọc trung vị trên ảnh gốc: ở sát chân tóc, cửa sổ lọc
    # quá nửa là tóc nên trám ra một VỆT TỐI đúng chỗ đuôi lông mày.
    def _blur(arr8, r):    # làm mờ trên ảnh 8-bit (PIL không nhận mode 'F' cho phép này)
        return np.asarray(Image.fromarray(arr8, mode='L')
                          .filter(ImageFilter.GaussianBlur(r)), np.float32)

    R = 32
    skm = (np.asarray(sk.resize((W, H), Image.BILINEAR), np.float32) > 110)
    src = np.asarray(rgb, np.float32)
    den = _blur((skm * 255).astype(np.uint8), R)
    ok = den > 8                                   # còn đủ điểm da quanh đây để tin
    fallback = [float(src[..., c][skm].mean()) if skm.any() else 128.0 for c in range(3)]
    chans = []
    for c in range(3):
        num = _blur((src[..., c] * skm).astype(np.uint8), R)
        chans.append(np.where(ok, num * 255.0 / np.maximum(den, 1.0), fallback[c]))
    smooth = Image.fromarray(np.clip(np.stack(chans, -1), 0, 255).astype(np.uint8))

    res = rgb.copy()
    res.paste(smooth, (0, 0), zone)
    out = res.convert('RGBA')
    out.putalpha(alpha)
    return out

def main():
    only = {int(a) for a in sys.argv[1:] if a.isdigit()}   # vd: python make-characters.py 7
    data = json.loads(zipfile.ZipFile(os.path.join(ROOT, 'apk/app.apk'))
                      .read('assets/face_funny/data_funny.json'))
    by_id = {x['id']: x['image'] for x in data}
    for cid, (img, _name) in EXTRA_CHARS.items():
        by_id[cid] = img
    os.makedirs(ORIGIN, exist_ok=True)
    os.makedirs(OVERLAY, exist_ok=True)
    done, skipped = [], []
    for cid in sorted(by_id):
        if only and cid not in only:
            continue
        name = by_id[cid]
        src = MAP.get(cid)
        if not src:
            skipped.append('id=%d %s' % (cid, name))
            continue
        path = os.path.join(SRC3D if cid in USE_3D else SRC, src)
        target = old_box(name) if os.path.exists(os.path.join(BASE, name + '.png')) else (0, 0, SIZE, SIZE)
        org, _ = build_origin(path, target, EXTRA_CROP.get(cid),
                              BOOST.get(cid, 1.0), cid in FACE_CENTER)
        org, cut = finish(org, SYNTH_BG.get(cid))
        org.save(os.path.join(ORIGIN, name + '.png'))
        ov = blank_face(cut, ZONE_TOP.get(cid, 0.10))
        ov.save(os.path.join(OVERLAY, '%d.png' % cid))
        done.append('id=%-3d %-20s <- %s' % (cid, name, src))
        print('  ' + done[-1])
    print('\nxong %d nhân vật (origin + overlay).' % len(done))
    if skipped:
        print('KHÔNG có ảnh mới, giữ nguyên bản cũ: ' + ', '.join(skipped))


if __name__ == '__main__':
    main()
