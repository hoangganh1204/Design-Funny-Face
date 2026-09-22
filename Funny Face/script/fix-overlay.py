# -*- coding: utf-8 -*-
"""Dựng lại overlay "mặt trống" cho các nhân vật mà make-characters.py làm hỏng.

Vì sao cần script riêng: `make-characters.py` khoanh vùng nét mặt bằng MẶT NẠ DA.
Cách đó chết ở hai ca này —
  * Naruto (id 19): nền lửa cam đọc ra là da, vùng khoanh phình trùm cả mặt.
  * Sasuke (id 22): da nhợt, ít bão hoà, mặt nạ không bắt được -> KHÔNG xoá gì cả.
Script này nhận toạ độ MÉP vùng mặt đo tay, nên không phụ thuộc màu nền.

Hai điều phải làm đúng, cả hai đều đã sai ở lần trước:

1. KHÔNG ĐƯỢC HÚT MÀU NGOÀI MẶT. Phép median chạy trên cả ảnh rồi mới dán theo mặt nạ
   thì ở sát biên vùng nó lấy trung vị của cả băng đô, tóc và nền lửa -> vệt lem tràn ra
   ngoài khuôn mặt (đúng thứ thấy trên máy). Nay mọi pixel NGOÀI vùng bị thay bằng màu
   trung bình TRONG vùng trước khi lọc, nên trung vị chỉ còn thấy màu da.

2. VIỀN MỀM PHẢI NẰM BÊN TRONG VÙNG. Làm mềm bằng cách blur mặt nạ sẽ đẩy vệt mờ ra
   ngoài mép đo được. Nay co vùng lại rồi mới blur, dốc chuyển nằm gọn bên trong, không
   một pixel nào ngoài hình chữ nhật đo được bị đụng tới.

Xoá nét bằng MEDIAN ở độ phân giải thấp: median loại chi tiết nhỏ (mắt, mày, mũi, miệng)
mà giữ khối sáng tối, nên da vẫn có bóng đổ. Blur thường thì hai mắt đen nhoè thành vệt xám.

    python3 script/fix-overlay.py
"""
import os
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageMath

RES = '/home/ubuntu/workspace/Mobile/funny-face/app/src/main/res/drawable-xxhdpi'
ALPHA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'art', 'alpha')

# id -> tên file ảnh gốc. Thứ tự và id lấy từ ContentCatalog.characters.
SRC = {
    2: 'leonel_messi', 4: 'cristiano_ronaldo', 3: 'erling_haaland', 1: 'kylian_mbappe',
    6: 'messi', 7: 'vinicius_junior', 5: 'jude_bellingham', 21: 'pedri', 8: 'neymar_junior',
    10: 'donald_trump', 15: 'mr_bean', 12: 'timothe_chalamet', 13: 'taylor_swift',
    14: 'leonardo_dicaprio', 11: 'jennie', 20: 'rose', 19: 'naruto', 22: 'sasuke',
}

# Mép vùng nét mặt (x0, y0, x1, y1) theo tỉ lệ cạnh ảnh.
#
# Cả 18 ảnh đều là chân dung chính diện dựng cùng một khung 1024x1024, nên một vùng
# chuẩn chung phủ đúng 16/18. Kiểm bằng cách vẽ khung lên cả 18 ảnh gốc rồi soi, không
# phải suy đoán. Chỉ ba ca phải chỉnh riêng, ghi lý do ngay cạnh.
# Đo trên ảnh phóng to: chân mày ~0.40, mắt ~0.44, miệng ~0.63, cằm ~0.69. Bản trước để
# mép trên 0.435 nên sau khi co (INSET) và làm mềm viền, độ phủ đặc chỉ bắt đầu từ ~0.46
# -> xoá được mũi/miệng mà CHỪA nguyên mắt và chân mày; mép dưới 0.725 thì lại lấn xuống cổ.
# Khung rộng rãi: đã có mặt nạ da chặn hai bên nên không cần bó sát nữa. Mép trên đủ
# cao để trùm chân mày ở cả 18 ảnh, mép dưới dừng trên cằm để không lấn xuống cổ.
# Khung khuôn mặt (x0, y0, x1, y1) theo tỉ lệ cạnh ảnh — trùm CẢ khuôn mặt, từ trán
# xuống cằm, không phải chỉ dải mắt–miệng.
#
# ĐO TAY TỪNG NGƯỜI trên lưới 1/20, không suy từ công thức chung.
#
# Đã thử bốn cách tự dò (mặt nạ da theo luật màu; mặt nạ da mồi từ điểm trên má; dò chân
# mày bằng biên độ sáng theo hàng; dò hairline/cằm bằng bề rộng vệt da) — cả bốn đều
# trượt trên loạt ảnh này: nền lửa đọc ra da, da nhợt không bắt được, tóc bị nhận nhầm là
# chân mày, giá trị cằm chạm sàn quét. Và kể cả khi mép trên dò đúng, một công thức chung
# kiểu "chân mày + 0.30" vẫn sai vì kích thước mặt mỗi người một khác: Bellingham cằm ở
# 0.545 còn Sasuke ở 0.715.
#
# Mép trên = chân tóc (hoặc mép dưới băng đô với Naruto/Sasuke, mép dưới tóc mái với
# Taylor Swift). Mép dưới = cằm.
#
# Hai bên để 0.375..0.628 cho mọi người, KHÔNG lấy theo gò má: ở tầm chân mày khuôn mặt
# rộng hơn gò má, lấy theo má thì hai đuôi mày thò ra ngoài vùng xoá.
ZONES = {
    1: (0.368, 0.268, 0.635, 0.615),
    2: (0.368, 0.272, 0.635, 0.618),
    3: (0.368, 0.278, 0.635, 0.618),
    4: (0.368, 0.278, 0.635, 0.618),
    # Chân mày ở 0.275..0.295. Mép trên phải CAO HƠN chân mày ~0.025 chứ không chỉ
    # sát mép: dốc viền mềm ăn khoảng 16px, đặt sát thì nửa trên chân mày chỉ được dán mờ.
    5: (0.352, 0.248, 0.668, 0.545),
    # Chân mày trải ngang 0.36..0.66 và nằm ở 0.275..0.295 — mép trên cũ 0.282 cắt
    # ngang giữa chân mày, nên xoá xong vẫn còn một vạch đậm.
    6: (0.352, 0.264, 0.668, 0.572),
    # Chân mày trải ngang tới 0.665, rộng hơn khung chung nên hai đuôi mày thò ra.
    # Mép dưới kéo thêm xuống 0.625 (chủ sản phẩm duyệt): cằm cậu ấy dài hơn nhóm còn lại.
    7: (0.352, 0.276, 0.668, 0.625),
    # Mép trên gọt cao qua hẳn chân mày (chủ sản phẩm duyệt): 0.285 -> 0.258.
    8: (0.360, 0.258, 0.648, 0.592),
    # Mặt bè ngang 0.34..0.665 và cằm tới 0.67; khung chung hụt cả hai bên lẫn dưới.
    10: (0.338, 0.31, 0.668, 0.672),
    # Mặt rộng 0.345..0.655, tóc bắt đầu ở 0.32 nên nới trái tới 0.340 vẫn chừa được tóc.
    11: (0.34, 0.305, 0.655, 0.675),
    # Mặt 0.345..0.655, cằm tới 0.655; khung chung hụt hai bên.
    12: (0.342, 0.288, 0.66, 0.655),
    # Mép trên lấy mép dưới TÓC MÁI (0.335), không phải chân tóc. Ngang nới tới
    # 0.352..0.648: mặt rộng 0.355..0.645 còn tóc bắt đầu ở 0.335 và 0.665, nên còn chừa.
    13: (0.352, 0.335, 0.648, 0.675),
    # Mặt rộng 0.345..0.665; nới thêm và kéo xuống hết cằm (chủ sản phẩm duyệt).
    14: (0.330, 0.285, 0.680, 0.700),
    # Mặt RỘNG NHẤT bộ: 0.30..0.70. Khung chung 0.368..0.635 chỉ phủ được giữa mặt,
    # nên chân mày, đuôi mắt và miệng đều nằm ngoài.
    15: (0.302, 0.258, 0.7, 0.678),
    # Mặt rộng 0.340..0.665; nới đều hai bên.
    20: (0.335, 0.305, 0.668, 0.675),
    # Chân mày vươn tới x≈0.66, rộng hơn khung chung.
    21: (0.352, 0.27, 0.668, 0.628),
    # Băng đô che hết trán -> mép trên lấy mép dưới băng đô (0.458), cao hơn là median
    # ăn vào kim loại. Mặt bè ngang 0.31..0.70 kể cả hai má có râu mèo, rộng hơn hẳn
    # nhóm người thật, nên khung ngang phải nới tương ứng. Cằm tới 0.755.
    19: (0.312, 0.458, 0.700, 0.755),
    # Băng đô che trán -> mép trên lấy mép dưới băng đô. Mặt rộng 0.345..0.665, chân mày
    # trải 0.36..0.655, cằm tới 0.74 — khung cũ 0.372..0.642 hụt cả hai bên lẫn dưới.
    22: (0.338, 0.440, 0.672, 0.748),
}

# HAI mũ khác nhau cho nửa trên và nửa dưới — khuôn mặt không đối xứng trên/dưới.
#
# Mũ 8 cho cả hình (gần chữ nhật) thì đáy là đường ngang thẳng băng cắt qua cổ, nhìn như
# bị xén mất khúc cổ. Đổi sang elip mũ 2.4 thì đáy đẹp nhưng ĐỈNH cũng thon theo, nên trán
# chỉ được xoá ở giữa còn hai bên thái dương vẫn lộ. Nửa trên mũ 6 (gần phẳng, trùm hết bề
# ngang trán), nửa dưới mũ 2.2 (thon lại thành cằm). Mũ 6 vẫn còn hụt hai góc trên nên
# đuôi chân mày thò ra ở thái dương -> đẩy lên 12, đỉnh vuông hẳn.
POWER_TOP = 12.0
POWER_BOT = 2.2
INSET = 0.99        # co vùng trước khi blur, để dốc viền nằm trong mép đo được
# Độ mềm viền, theo cạnh ảnh. PHẢI nhỏ. GaussianBlur(r) toả ra tới ~3r, nên feather 12px
# làm dốc viền dài ~36px: đo được là ở hàng chân mày mặt nạ KHÔNG chỗ nào đạt 255, dải
# mắt–mày chỉ được dán mờ nên xoá mãi không sạch. 5px là đủ giấu mối ghép vì phần dán
# vào vốn đã là da mịn.
FEATHER = 0.005
SHRINK = 16         # median ở 1/16 (xem ghi chú trong blank())

# id -> (bán kính phép mở, y bắt đầu áp dụng). Dọn VỆT NỀN dính vào mặt nạ alpha.
#
# Ảnh gốc của Leonardo có mép nền vàng lởm chởm ăn vào vùng vai áo, và mặt nạ alpha giữ
# luôn mấy vệt đó như thể chúng là nhân vật — nên trên máy thấy mấy sợi vàng vắt qua áo.
# Không khử theo MÀU được: vệt đã khử răng cưa nên trải cả một dải màu, ngưỡng đủ rộng để
# bắt hết vệt thì đã ăn vào cả da mặt (đo: tol=60 đã xoá nhầm 6 pixel trong vùng mặt).
# Khử theo HÌNH thì được: vệt rộng ~4-8px còn thân người rộng hàng trăm px, nên phép mở
# bán kính 15 cắt sạch vệt mà mép áo và cổ vẫn nguyên. Chỉ áp từ vai trở xuống.
# id -> (bán kính phép mở, bán kính bào vành). Dọn VỆT NỀN dính vào mặt nạ alpha.
#
# Đã thử dựng lại hẳn mặt nạ từ ảnh gốc (loang nền từ viền ảnh, cả kiểu so với màu mồi lẫn
# kiểu so với pixel kề, nhiều ngưỡng, nhiều lượt) — KHÔNG tách được: nền là dải chuyển màu
# nối liền tông với da và tóc, ngưỡng thấp thì sót vòng vàng quanh vai, ngưỡng cao thì ăn
# thủng mặt. Nên giữ mặt nạ có sẵn và chỉ dọn viền.
#
# Ảnh gốc của Leonardo có mép nền vàng lởm chởm bám quanh cả tóc lẫn vai áo, và mặt nạ
# alpha giữ luôn mấy vệt đó như thể chúng là nhân vật.
# Không khử theo MÀU ở vùng gần mặt được: vệt đã khử răng cưa nên trải cả một dải màu,
# ngưỡng đủ rộng để bắt hết thì đã ăn vào da (đo: tol=60 xoá nhầm 6 pixel trong vùng mặt).
# Khử theo HÌNH thì được — vệt rộng ~4-8px, thân người rộng hàng trăm px:
#   1) phép mở bán kính 9 cắt các vệt mảnh,
#   2) bào vành alpha 2px để bỏ vành nửa trong suốt, vì ở đúng vành đó màu trong ảnh gốc
#      LÀ màu nền, lấy ra là lòi vàng,
#   3) kéo màu từ vùng đặc ra ngoài (blur(RGB*A)/blur(A)) để mép không còn vệt nền nào.
DEFRINGE = {14: (9, 5)}


# Những nhân vật KHÔNG làm mềm mép trên. Naruto và Sasuke có chân mày nằm ngay sát mép
# dưới băng đô, tức đúng mép trên của vùng xoá. Dốc viền mềm ăn khoảng 16px nên dải chân
# mày chỉ được dán mờ, còn lại một vệt đen mảnh. Với hai ca khác thì nâng mép trên lên là
# xong, nhưng ở đây nâng là median ăn vào kim loại băng đô. Nên cắt thẳng: mép trên của
# băng đô vốn đã là một đường cứng trong tranh, cắt trùng vào đó thì không thấy mối ghép.
HARD_TOP = {19, 22}


def superellipse(W, H, x0, y0, x1, y1, power=None, inset=1.0):
    """Hình khuôn mặt: nửa trên gần phẳng, nửa dưới thon thành cằm."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    a, b = (x1 - x0) / 2 * inset, (y1 - y0) / 2 * inset
    m = Image.new('L', (W, H), 0)
    px = m.load()
    for y in range(max(0, int(cy - b - 2)), min(H, int(cy + b + 3))):
        pw = POWER_TOP if y < cy else POWER_BOT
        dy = abs((y - cy) / b) ** pw
        if dy > 1.0:
            continue
        for x in range(max(0, int(cx - a - 2)), min(W, int(cx + a + 3))):
            if abs((x - cx) / a) ** pw + dy <= 1.0:
                px[x, y] = 255
    return m


def skin_filled(rgb, cx_r=0.50, cy_r=0.55, tol=110):
    """Vùng da của nhân vật, đã lấp lỗ. Thuần PIL.

    Mồi màu lấy ngay trên má (giữa ngang, 55% cao) — điểm này rơi vào da ở cả 18 ảnh,
    nên ngưỡng tự thích nghi theo từng nhân vật: hợp cả da sẫm của Vinicius lẫn da vẽ
    của Naruto. `make-characters.py` dùng một luật màu da chung cho mọi ảnh, và đó là
    lý do nó trượt ở Sasuke (da nhợt) rồi phình ở Naruto (nền lửa cam giống da).

    LẤP LỖ là phần bắt buộc: mắt, chân mày, miệng là những lỗ nằm lọt trong da. Không
    lấp thì mặt nạ da lại chính là thứ chừa nguyên mấy nét cần xoá.
    """
    W, H = rgb.size
    px = rgb.load()
    sx, sy = int(cx_r * W), int(cy_r * H)
    patch = sorted((px[x, y] for y in range(sy - 12, sy + 13, 3)
                    for x in range(sx - 12, sx + 13, 3)), key=sum)
    seed = patch[len(patch) // 2]
    m = Image.new('L', (W, H), 0)
    mp = m.load()
    for y in range(H):
        for x in range(W):
            p = px[x, y]
            if abs(p[0]-seed[0]) + abs(p[1]-seed[1]) + abs(p[2]-seed[2]) < tol:
                mp[x, y] = 255
    m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    # lấp lỗ: tô nền từ viền ảnh trên ảnh đảo, phần không tô tới chính là lỗ
    inv = m.point(lambda v: 0 if v else 255)
    ImageDraw.floodfill(inv, (0, 0), 0)
    ImageDraw.floodfill(inv, (W - 1, 0), 0)
    ImageDraw.floodfill(inv, (0, H - 1), 0)
    ImageDraw.floodfill(inv, (W - 1, H - 1), 0)
    return ImageChops.lighter(m, inv)


def mean_inside(rgb, mask):
    stat = rgb.copy()
    h = stat.histogram(mask)
    tot = sum(h[0:256]) or 1
    return tuple(sum(i * h[c * 256 + i] for i in range(256)) // tot for c in range(3))


def blank(rgb, hard, soft):
    """Xoá nét trong vùng. `hard` chặn nguồn màu, `soft` là mặt nạ dán."""
    W, H = rgb.size
    # Mọi thứ ngoài vùng -> màu trung bình trong vùng, để median không hút màu lạ vào.
    flat = Image.new('RGB', (W, H), mean_inside(rgb, hard))
    src = Image.composite(rgb, flat, hard)
    small = src.resize((max(1, W // SHRINK), max(1, H // SHRINK)), Image.LANCZOS)
    # 1/12 + median 9 rồi 7 là mức dò được: ở 1/8 con mắt còn ~4px nên median 7 chưa nuốt
    # hết, mắt xanh vẫn hằn; ở 1/24 thì mặt bệt phẳng, mất bóng đổ.
    small = (small.filter(ImageFilter.MedianFilter(9))
                  .filter(ImageFilter.MedianFilter(9))
                  .filter(ImageFilter.MedianFilter(7)))
    out = rgb.copy()
    out.paste(small.resize((W, H), Image.BICUBIC), (0, 0), soft)
    return out


def main():
    for cid in sorted(SRC):
        x0, y0, x1, y1 = ZONES[cid]
        src = Image.open(os.path.join(RES, SRC[cid] + '.webp')).convert('RGB')
        ov_p = os.path.join(RES, f'funny_overlay_{cid}.webp')
        ov = Image.open(ov_p).convert('RGBA')
        if ov.size != src.size:
            ov = ov.resize(src.size, Image.LANCZOS)
        W, H = src.size
        # Alpha đọc từ BẢN GỐC cất riêng, không đọc từ chính file sắp ghi đè.
        #
        # Script này ghi đè lên đúng file nó vừa đọc, nên nếu lấy alpha từ đó thì mỗi lần
        # chạy lại bào thêm một lớp: chạy vài lần là mặt nạ Leonardo mất hẳn một bên vai
        # rồi rỗng luôn. Bản gốc tách ra art/alpha/ một lần, từ đó mọi lần chạy đều cho
        # cùng kết quả.
        alpha = Image.open(os.path.join(ALPHA_DIR, f'{cid}.png')).convert('L')
        if cid in DEFRINGE:
            k, er = DEFRINGE[cid]
            alpha = (alpha.filter(ImageFilter.MinFilter(k))
                          .filter(ImageFilter.MaxFilter(k))
                          .filter(ImageFilter.MinFilter(er))
                          .filter(ImageFilter.GaussianBlur(1)))

        box = (x0 * W, y0 * H, x1 * W, y1 * H)
        # Chỉ dùng khung đo được. Đã thử ba cách tự dò vùng mặt (mặt nạ da theo luật màu,
        # mặt nạ da mồi từ điểm trên má, và dò chân mày/miệng bằng biên độ sáng theo hàng)
        # — cả ba đều trượt trên loạt ảnh này: nền lửa đọc ra da, da nhợt không bắt được,
        # tóc bị nhận nhầm là chân mày. Khung đo tay tuy thủ công nhưng đúng và kiểm được.
        hard = superellipse(W, H, *box)
        soft = superellipse(W, H, *box, inset=INSET).filter(
            ImageFilter.GaussianBlur(FEATHER * W))
        if cid in HARD_TOP:
            band_h = int(y0 * H) + int(0.06 * H)
            top = Image.new('L', (W, H), 0)
            top.paste(hard.crop((0, 0, W, band_h)), (0, 0))
            soft = ImageChops.lighter(soft, top)

        # Nền là ảnh GỐC ở những chỗ alpha ĐẶC, và giữ overlay cũ ở mép alpha mềm.
        #
        # Lấy tất từ ảnh gốc thì mọi hư hỏng cũ (bôi lan xuống cổ, vào tóc) biến mất —
        # đó là lý do phải dựng lại từ gốc. Nhưng ~2.5% pixel ở mép cắt có alpha 1..254,
        # và ở đó màu gốc là MÀU NỀN (vàng với Leonardo), nên lấy từ gốc là lòi vệt vàng
        # dọc cổ áo và vai. Overlay cũ đã trung hoà màu nền ở đúng mép đó, nên giữ lại.
        # Hư hỏng cũ nằm trong vùng alpha đặc nên không theo vào.
        solid = alpha.point(lambda v: 255 if v >= 250 else 0)
        if cid in DEFRINGE:
            # Kéo màu từ vùng LÀNH ra chỗ vành mềm và chỗ rác: blur(RGB*w)/blur(w).
            w = ImageChops.multiply(alpha, solid)
            wf = w.filter(ImageFilter.GaussianBlur(10))
            bled = Image.merge('RGB', [
                ImageMath.eval("convert(float(a)*255.0/float(max(b,1)), 'L')",
                               a=ImageChops.multiply(ch, w).filter(ImageFilter.GaussianBlur(10)),
                               b=wf)
                for ch in src.split()])
            base = Image.composite(src, bled, solid)
        else:
            base = Image.composite(src, ov.convert('RGB'), solid)
        out = blank(base, hard, soft).convert('RGBA')
        out.putalpha(alpha)
        out.save(ov_p, 'WEBP', lossless=True, quality=100)
        print(f'  funny_overlay_{cid:<2} {SRC[cid]:<20} y {y0}-{y1}')


if __name__ == '__main__':
    main()
