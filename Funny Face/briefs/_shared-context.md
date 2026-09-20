# Shared context — Funny Face Mashup Challenge → Figma v1 (Plan 1 Phase 2)

## Paths (tuyệt đối)
RES  = /home/ubuntu/workspace/Design/App 6/Funny Face/decompiled/resources/res
SRC  = /home/ubuntu/workspace/Design/App 6/Funny Face/decompiled/sources/sources/com/cem/face/puzzle
APK  = /home/ubuntu/workspace/Design/App 6/Funny Face/apk/app.apk
TOOL = python3 "/home/ubuntu/workspace/Design/App 6/tools/resolve-layout.py" "$RES" "<layout.xml>"

## App
com.filter.face.puzzle (code: com.cem.face.puzzle) — KHÔNG obfuscate, tên thật.
Single-activity MainActivity + Navigation Component (res/navigation/main_nav.xml, 18 destination).
Hilt/Dagger DI. XML layout thuần, KHÔNG Compose.
Canvas chuẩn: 360×800 dp (sdp==dp, ssp==sp). Không vẽ status bar.

## Firebase Remote Config — ĐÃ FETCH THẬT (instance mới, /tmp/rc.json)
onboarding_enabled        = false     ← onboarding BỊ TẮT mặc định
language_enabled          = false     ← language picker BỊ TẮT mặc định
level_picker_skipped      = false
onboarding_buttons_enabled= true
home_show_case            = 0
ui_home_show_case         = 1
monet / monet_v2 / monet_super = ads config thật (app_name "Face Puzzle AND")
and_ads_test              = ads config TEST (app_name "Test Ads")
⚠ ĐÂY LÀ GIÁ TRỊ FETCH ĐƯỢC, KHÔNG PHẢI GIÁ TRỊ CODE ĐỌC. Bạn PHẢI verify trong code:
  key name có khớp không, đọc bằng getBoolean/getLong nào, default khi chưa fetch là gì,
  và code dùng nó để rẽ nhánh ra sao. Nếu code không đọc key đó → nói rõ.

## Content bundled trong APK (không remote)
assets/face_funny/data_funny.json — 20 nhân vật, mỗi cái {id,name,image}
assets/face_funny/origin/<name>.png   (20 file)
assets/face_funny/overlay/<name>.png  (20 file)
assets/swipe_left.json — Lottie
(assets/template/* và assets/iads/* là của SDK quảng cáo, KHÔNG phải content app)

## Yêu cầu spec — mỗi màn PHẢI trả lời đủ 6 mục (Plan 1 Phase 2)
A. Geometry (từ resolve-layout, KHÔNG đọc raw XML): mỗi phần tử
   `vai trò · x/y dp · w/h dp · nền #hex · bo góc`; text = `chuỗi resolve THẬT · size sp ·
   font(@font đã resolve) · màu · canh`. Ghi padding/margin. KHÔNG bỏ sót phần tử nào.
B. Visibility (từ code): bảng `view | XML mặc định | setter runtime | điều kiện | KẾT QUẢ`.
   Cẩn thận helper show()/gone()/inv() và loại show(v,bool) có thể VISIBLE *hoặc* GONE.
C. List: mỗi list ghép từ đâu → ĐÚNG số lượng + tên + thứ tự, KỂ CẢ item code chèn
   (ô ad, ô "Add", promo). spanCount/layoutManager có thể set trong code khác XML.
D. Data hardcode: chép NGUYÊN VĂN, đúng thứ tự.
E. Nguồn từng view: local drawable / asset bundled / remote / theo mùa. Map model→field.
F. Nhánh remote-config / A-B: dựng nhánh MẶC ĐỊNH trước. Ghi rõ nhánh nào mặc định và vì sao.
STATE: mỗi runtime state là 1 frame riêng. Trục hay gặp: quyền (đã/chưa cấp), dữ liệu
   (rỗng/loading/có/lỗi), gói (free-có-ads / PRO), lần đầu vs quay lại, cờ tính năng.

## Cờ (ghi chú, KHÔNG bịa)
NativeAdView/banner/MAX/AppLovin → **AD SLOT** (ghi tên placement nếu biết)
Lottie/PAG/video → **animation** (ghi tên asset gốc)
ảnh runtime/camera/gallery người dùng → **runtime placeholder**
UI OS/SDK (UMP/GDPR consent, In-App Review, permission, share sheet) → **placeholder có nhãn**

## Hay bị sót — RÀ TỪNG CÁI
- res/menu/*.xml inflate qua getMenuInflater() → nút toolbar không có trong layout
- Custom view tên *View/*Layout KHÔNG thuộc android/androidx → đọc onDraw()
- RecyclerView ẩn trong 1 layout (bảng màu, list ngôn ngữ, FAQ)
- ripple/selector bọc ảnh thật (<ripple>→<item drawable="@mipmap/…">)
- include/merge/ViewStub trong layout → mở file được include

## ĐỘ CHÍNH XÁC LÀ TRÊN HẾT
Không bịa số/màu/chữ/asset. Mọi giá trị truy về file (ghi `file:dòng`). Chỗ không resolve
tĩnh được thì GẮN CỜ, đừng đoán. Đọc TRỌN file liên quan, không lướt, không suy từ tên.

## Output
Ghi spec ĐẦY ĐỦ ra: /home/ubuntu/workspace/Design/App 6/Funny Face/specs/<cụm>.md
Trả về summary NGẮN (≤15 dòng): số màn, số state, count các list chính, cờ, chỗ chưa resolve.
KHÔNG dispatch subagent. KHÔNG sửa file nào ngoài spec của bạn.
