# Plan 2 — Custom Figma v2 (reskin) từ v1

> Quy trình tự chứa để tạo bản "v2" khác biệt từ v1 có sẵn.
> Tiền đề: đã có `<App>/figma/v1` + `<App>/assets/v1` chạy tốt (xem Plan 1).
> Bản tiếng Anh: `plan-2-reskin-v2.en.md`.
> Kit: dùng lại `../kit/` (template make-v2.py, đoạn hue-rotate/duotone, tools build dùng chung).

## Mục tiêu
Tạo `figma/v2` **nhìn là app khác** nhưng **bố cục y hệt** v1. Chỉ đổi màu / hoạ tiết / bo góc.
Đây là *reskin*, không phải redesign.

## Luật (được / KHÔNG được đổi)
| BẮT BUỘC giữ nguyên | ĐƯỢC đổi (để khác biệt) |
|---|---|
| Mọi vị trí, toạ độ, kích thước, khoảng cách | Bảng màu thương hiệu (xoay hue cả bảng MỘT góc cố định) |
| Thứ tự layout (**KHÔNG đổi chỗ Back↔Next**, không đảo nút) | Tông nền (giữ tối nếu ảnh cần nền tối — retint, đừng đảo sáng) |
| Hình đặc trưng (nút pill, switch, chấm-step, indicator) | Bo góc — tăng đúng **một bậc** |
| Ảnh nội dung/sản phẩm (vũ khí, item, avatar, wallpaper, mascot, emoji, cờ) | Art có màu thương hiệu (wordmark, icon brand, chrome vùng chọn) |
| Số màn/dialog & mọi state | "Chrome" thẻ/khung có màu thương hiệu (khung item, thẻ hàng, tab) |

## Luật 1 — Màu: xoay cả bảng brand MỘT góc
- **Sample màu brand thật trước.** Một góc cố định áp lên hue gốc khác nhau sẽ ra màu bậy (navy ấm xoay
  cùng góc với cam ấm sẽ ra đục) — sample token thật rồi chọn góc dịch **cả họ màu** đồng bộ. Đen trung
  tính xử ở Luật 2.
- Tính hex xoay cho **mọi** token brand cùng MỘT góc:
  ```python
  import colorsys
  def rot(hex, deg):
      h,l,s = colorsys.rgb_to_hls(*[int(hex[i:i+2],16)/255 for i in (0,2,4)])
      return '%02x%02x%02x'%tuple(int(c*255) for c in colorsys.hls_to_rgb((h+deg/360)%1, l, s))
  # vd rot('ffcd6a', 150) → một màu cyan; áp CÙNG 150 cho gradient, CTA, accent.
  ```
- Giữ **màu chức năng** — chúng mang ý nghĩa, không phải brand: đỏ lỗi/đếm ngược, xanh thành công, đỏ từ
  chối, link, và màu widget của SDK bên thứ ba (vd nút rate-SDK).
- Đọc được: xoay hue **giữ độ sáng**, nên màu brand sáng vẫn sáng → chữ đen trên CTA vẫn rõ. Kiểm lại sau.

## Luật 2 — Nền: retint, giữ tối (nếu content tối)
- Ảnh sản phẩm và art thường **thiết kế cho nền tối**; nền sáng sẽ chỏi → giữ tối. (Nếu app vốn theme
  sáng thì dịch trong dải sáng.)
- Dịch đen trung tính về hue brand mới (vd gần-đen → sắc tối của hue mới), toolbar/card cũng vậy. Đủ để
  "khác app", không đủ để đánh nhau với ảnh.
- Retint cả các ô đen hardcode (ô nhập, fill card dialog, nền màn detail) — ô `#191919` trung tính trên
  màn đã ám màu sẽ lộ reskin nửa vời.

## Luật 3 — Bo góc: một bậc
- Tăng bo góc CTA/tile/list ~+4dp (nút 10→14, tile 14→18, hàng 16→20).
- **Không** đổi silhouette đặc trưng (vd nút pixel: mặt + viền đáy đen + notch góc). Một bậc, không hơn,
  kẻo thành component khác.

## Luật 4 — Asset: chỉ recolor art thương hiệu, đúng phương pháp theo loại
Ba nhóm — phân loại **từng** asset, áp đúng cách:
1. **Ảnh nội dung/sản phẩm** (vũ khí, item, avatar, wallpaper, mascot, emoji, cờ): **KHÔNG đụng.** Xoay
   hue ảnh nhiều màu ra màu bậy.
2. **Mark brand CÓ màu** (wordmark splash, thanh progress màu, radio state chọn, pointer/gợi ý): **xoay
   hue cùng góc** với bảng màu (xoay HLS từng pixel, giữ alpha).
3. **"Chrome" brand gần như xám/kim loại** (khung thẻ item, thẻ hàng, tab bar): xoay hue vô hiệu trên
   xám → **duotone**: map độ sáng → gradient(shadow=brand tối → highlight=brand sáng), giữ chi tiết ánh
   kim. Tuỳ chọn: phủ **multiply** nhẹ hue mới lên texture metal lớn (vd nền splash) cho đồng bộ.

> Lớp "chrome" là cái hay quên: khung item / thẻ hàng vẫn xám trong khi mọi thứ đã đổi → nhìn reskin nửa
> vời. Recolor cả khung.

## Luật 5 — Đồng bộ thiết kế khi reskin (đừng recolor mù)
- Nút cùng 1–2 tầng chiều cao; tem trạng thái/PRO một màu xuyên suốt; feature icon **khác-nhưng-hoà**
  (hue anh em, không chỏi); đường phụ **mờ hơn** điểm nhấn (đường nối < chấm indicator). Nhất quán hơn
  đẹp lẻ.
- Nếu brief là bản **"free"** chứ không phải reskin màu: phân biệt IAP với ads — bỏ Vip/PRO/upgrade/
  Remove-Ads, nhưng **GIỮ** ads (banner/native/reward) vì đó là nguồn thu. IAP ≠ ads ≠ cross-promo ≠
  reward-ad.

## Luật 6 — Đồng bộ code + asset (script `make-v2`, không fork tay)
**Đừng** fork tay `code.js` v1. Viết `<App>/script/make-v2.py` đọc `figma/v1/code.js`, áp đúng các phép
thay chuỗi (token brand, radius, retint nền, tiêu đề page, header) và ghi `figma/v2/code.js`. Sửa gì ở
v1 → chạy lại make-v2 → v2 luôn khớp (bảo đảm layout y hệt vì chỉ token đổi). Asset: `assets/v2/` = copy
`assets/v1` + reskin (hue-rotate/duotone) trên nhóm brand đã phân loại.

## Các bước (công thức)
```
1. Sample màu brand thật; chọn góc hue                        → verify: chữ đen còn đọc được trên CTA
2. assets/v2 = copy assets/v1; xoay hue mark brand;           → verify: ảnh sản phẩm y hệt v1 (byte);
   duotone khung chrome; (tuỳ) tint texture metal lớn            mark brand + khung theo hue mới
3. Viết make-v2.py: v1/code.js → v2/code.js (token,           → verify: node --check v2/code.js
   radius +1 bậc, retint nền, tiêu đề page, id/name)
4. build: build-plugin.py --src assets/v2 --plugin figma/v2   → verify: mock xanh; số node == v1
5. Tự soi visual: capture-scene v2 + render-preview           → verify: layout y hệt, nhận diện mới,
   (ASSETS_DIR=assets/v2)                                        ảnh sản phẩm không đổi, chrome đúng tông
6. figma/v2/manifest.json: id + name khác                     → verify: chạy Figma desktop
```

## Bẫy reskin hay gặp (mỗi cái đều đã cắn 1 bản dựng thật)
- Góc hue cố định trên hue gốc khác → màu sai (ấm→đục). **Sample trước**, rồi chọn.
- Duotone ảnh chụp → phá ảnh. Chỉ duotone chrome xám, không đụng ảnh sản phẩm.
- **Quên lớp chrome** — khung item/thẻ hàng để xám. Recolor chúng.
- Đổi chỗ Back/Next hay đảo nút → thành "app khác", không phải reskin. Layout đóng băng.
- Xoay màu trung tính → màu sai: góc hợp họ này lại làm bậy họ khác (navy→nâu).
- Retint nhầm `#000000`/`#ffffff`/scrim/shadow → chỉ retint *bề mặt tối trung tính*, đừng đụng chữ nút
  đen thật, trắng thật, hay scrim overlay.
- Bo góc quá tay → mất silhouette đặc trưng. Chỉ một bậc.
- Fork tay code.js → v1 và v2 lệch nhau. Luôn regenerate v2 bằng make-v2.

## Coi là XONG khi
- Số node v2 == v1 (layout y hệt); Back/Next và mọi vị trí không đổi.
- Màu + nền + khung chrome theo tông mới; ảnh sản phẩm giống hệt v1 (byte).
- `make-v2.py` sinh lại `v2/code.js` từ `v1/code.js` một cách xác định.
- Tự soi visual: cùng màn, nhận diện khác hẳn, không còn chrome xám nửa vời.
