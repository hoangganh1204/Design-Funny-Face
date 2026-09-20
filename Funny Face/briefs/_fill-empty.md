# Lấp frame trống — dữ liệu THẬT đã resolve sẵn (dùng cái này, đừng bịa)

Mục tiêu: file Figma đem trình lead. Frame nào đang là ô đen trơn + 1 dòng nhãn thì dựng
cho ra hình. NHƯNG vẫn theo Plan 1: mọi thứ vẽ ra phải truy được về code/resource, thứ nào
là mô phỏng thì GẮN NHÃN trên canvas.

## 1. Native ad — geometry THẬT, đã resolve từ res/layout

`ads_native_media_common.xml` (dùng cho native trong màn — home/detail/preview):
  NativeAdView fill_parent x wrap
    ConstraintLayout  background=@drawable/bg_ad_native_media_common  padding=12dp
      icon         AppCompatImageView  48x48dp
      ad badge     8sp  #ffffff  bg=@drawable/bg_text_view_ads  padding 8/2/8/2  text="AD"  marginStart=8dp
      primary      16sp  font lato_bold_700     ellipsize=end   marginStart=8dp
      body         12sp  font lato_regular_400  marginTop=4dp
      media_view   fill_parent x 120dp  marginTop=8dp
      cta          AppCompatButton  fill_parent  text="Install"  margin 4/8/4/4

`native_fake_full_inter.xml` (native full-screen giả dạng app):
  NativeAdView fill x fill
    ConstraintLayout fill x fill
      media_view   0x0 (giãn hết)
      ConstraintLayout  bg_r8_f4f4f4_ads + backgroundTint=#33000000 -> nen THAT DEN 20%, padding T/B 15dp
                        margin L5 T50 R5
        ad badge   10sp #ffffff  bg=@drawable/bg_text_view_ads  padding 10/2/10/2  marginStart=10dp
        primary    16sp bold #ffffff  maxLines=1  width 70%  margin L10 R10  padding 5/5
        body       14sp #ffffff  maxLines=2  margin L10 T5 R10
      cta          45dp cao  20sp #ffffff  bg=@drawable/bg_white_r16_ads  width 95%
                   margin L10 T20 R10 B20  text="Install"

QUY TẮC: dựng ĐÚNG khung này. Nội dung quảng cáo (icon/tiêu đề/mô tả cụ thể) là runtime →
điền placeholder trung tính có nhãn, vd primary = "Ad headline", body = "Ad description text",
icon = ô xám bo góc. KHÔNG bịa tên app/thương hiệu quảng cáo nào.
Badge "AD" và nút "Install" là chuỗi THẬT trong layout → viết đúng.

## 2. Nội dung Privacy Policy / Term of use — VĂN BẢN THẬT trong APK

`assets/privacy_policy.html` (89 đoạn) và `assets/term_of_use.html` (57 đoạn) —
CompanyInfoFragment.java:119,122 nạp bằng loadUrl("file:///android_asset/...").
Đã trích sẵn ra: **build/policy-text.json**  → {"privacy": [đoạn...], "term": [đoạn...]}
Dùng 12-18 đoạn đầu, wrap chữ cho vừa bề rộng, 12sp Lato Regular màu #171716,
tiêu đề đoạn in đậm nếu ngắn. Đây là NỘI DUNG THẬT, không phải placeholder — không cần nhãn.

## 3. Overlay loading — vẽ CHỒNG lên màn thật

D70 (dim full-screen) và D71 (card "Setting up") hiện là hình chữ nhật trơn. Trong app chúng
LUÔN nằm đè lên một màn. Dựng lại: vẽ màn nền thật (gọi lại builder của màn tương ứng hoặc
vẽ chrome tối giản của nó) rồi mới phủ scrim + spinner/card lên trên. Như vậy mới đọc ra
đây là một STATE chứ không phải ô đen.

## 4. Nội dung video/preview — dùng ảnh mô phỏng đã có

Đã có sẵn trong assets/v1/50-mock-ar/ (khoá dùng trực tiếp với img()/photo()):
  mock_camera_face    — khuôn mặt tổng hợp, chưa hiệu ứng
  mock_ar_facepuzzle  — mặt cắt 6 vùng (FacePuzzle mode)
  mock_ar_funny_1     — nhân vật thật trong APK + nét mặt tổng hợp (FaceFunny mode)
Dùng cho: khung preview video, player, thumbnail item trong VideoGallery.
BẮT BUỘC kèm nhãn nhỏ "MÔ PHỎNG · <lý do runtime>" như face-puzzle.js/funny-puzzle.js đang làm.
TUYỆT ĐỐI KHÔNG lấy thumbnail template CDN (30-template-v2 / 31-template-v1) làm nội dung
do người dùng tạo — đó là nội dung của người khác, Plan 1 cấm thay thế âm thầm.

## Ràng buộc chung
- KHÔNG đổi toạ độ/kích thước phần tử đã có. Chỉ THÊM chi tiết vào chỗ đang trống.
- Giữ nguyên tên frame và note nguồn (Phase 6 audit dựa vào đó).
- Nếu frame vốn dĩ trống trong app thật (vd 30b đang quay — chrome bị ẩn) thì GIỮ TRỐNG,
  ghi lý do trong note. Đầy đặn không quan trọng bằng đúng.
- Xong chạy `node --check` file của mình.

## ĐÍNH CHÍNH (sau khi dựng thật)
resolve-layout.py ban đầu KHÔNG in `backgroundTint` nên bản brief đầu ghi sai màu:
  - khối info của native_fake_full_inter: backgroundTint=#33000000 -> nền ĐEN 20%, KHÔNG phải xám f4f4f4
  - nút CTA: backgroundTint=@color/gnt_blue (#4285f4) -> nền XANH, KHÔNG phải trắng
Đã vá tools/resolve-layout.py (thêm backgroundTint/foregroundTint/drawableTint/iconTint/
elevation/alpha/strokeColor/strokeWidth/rotation vào KEEP). Với layout có tint: ĐỌC RAW XML đối chiếu.
