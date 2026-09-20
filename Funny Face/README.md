# Funny Face — Mashup Challenge → Figma v1

Dựng lại giao diện app Android **Funny Face Mashup Challenge** thành plugin Figma, theo
`Figma version 1/plan-1-apk-to-figma-v1.vi.md`.

| | |
|---|---|
| APK | `apk/app.apk` — 115 MB, universal (không split) |
| Package khai báo | `com.filter.face.puzzle` |
| Package code | `com.cem.face.puzzle` ← **khác nhau: APK này đã là một bản reskin** |
| compileSdk | 36 · Hilt/Dagger · Navigation Component · XML layout (không Compose) |
| Obfuscate | **Không** — đọc được tên thật, bỏ được toàn bộ Phụ lục C của plan |
| Kết quả | **41 frame** (36 màn + 5 dialog/state), 989 node, plugin ~4.1 MB |
| Bản v2 | reskin tím violet, cùng 41 frame / 989 node, layout y hệt |

## Chạy trong Figma

```
Figma desktop → Plugins → Development → Import plugin from manifest…
→ chọn: Funny Face/figma/v1/manifest.json
```

Plugin dev **chỉ chạy được trên Figma desktop**, không chạy trên figma.com. Chạy một lần
trên desktop là file tự sync lên figma.com.

Plugin tạo 2 trang: `📱 Funny Face · Screens` (49) và `💬 Funny Face · Dialogs & States` (10).
Mỗi frame có `pluginData['source']` ghi `file:dòng` nơi số liệu được lấy ra.

## Build lại

```sh
sh "Funny Face/script/build.sh"                                  # asset → plugin.js + verify
python3 "Funny Face/script/audit-phase6.py"                      # 4 audit độ phủ
node script/capture-scene.js figma/v1/plugin.js > build/scene.json
SCENE=build/scene.json OUT=build/preview ASSETS_DIR=assets/v1 \
  python3 "Funny Face/script/render-preview.py"                  # ảnh self-check
```

Thay ảnh: giữ nguyên **tên file** (khoá = tên không đuôi), đổi đuôi thoải mái, rồi build lại.

---

## Luồng màn (suy từ `res/navigation/main_nav.xml`, 18 destination)

```
Splash ──── nhánh MẶC ĐỊNH ───────────────────────────────► Home (UI mới)
  │                                                            │
  └─ Intro (3 trang) ─► Language Picker (7)                     │  5 tab
     ▲ CHỈ khi RC bật lại — mặc định BỊ TẮT                     │  All(38) FacePuzzle(6)
                                                                │  FacePop(6) WhirlFace(6)
                                                                │  FunnyPuzzle(20)
                                                                └─ Home cũ: grid 28 ô (fallback)
Level Picker (3) ─► Face Puzzle  ─┐
List Funny (20)  ─► Funny Puzzle ─┴─► Preview ─► Sound Picker (4) ─► Result
                                                                       ├─► Play Video
                                                                       └─► Video Gallery
Settings (4 hàng) ─► Company Info (Privacy / Term)
```

**Nhánh mặc định quan trọng:** Remote Config trả `onboarding_enabled=false` và
`language_enabled=false` (default khi chưa fetch cũng là `false`) → **user mới vào là đi
thẳng từ Splash sang Home**, không qua onboarding, không chọn ngôn ngữ. Intro và Language
Picker vẫn được dựng đủ nhưng **không phải luồng mặc định**.

`ui_home_show_case=1` → dùng `FragmentHome` (UI mới). `FragmentHomeOldUI` chỉ chạy khi
RC = 0 hoặc chưa fetch được lần đầu.

---

## Số liệu đều truy được về nguồn

| Nội dung | Số lượng | Nguồn |
|---|---|---|
| Nhân vật Funny Puzzle | **18 trong bản thiết kế** (APK vẫn 20) | `assets/face_funny/data_funny.json` — bản thiết kế đã BỎ id 16 Messi / 17 Ronaldo / 18 Neymar Jr / 9 Bruno Mars, và THÊM 2 đề xuất Pedri + Sasuke |
| Template Face Puzzle (v2) | **18** = 3 category × 6 | CDN `ios_data_facepuzzle_v2.json` |
| Template (v1, Home cũ) | **8** | CDN `ios_data_facepuzzle.json` |
| Bài nhạc | **4** | `AppSetting.kt` (`res/raw/` có 5 `.aac`, `audio.aac` không ai dùng) |
| Ngôn ngữ | **7** | `AppSetting.kt` — en/hi/es/fr/pt/vi/ja, hardcode |
| Level | **3** | Easy / Intermediate / Difficulty |
| Thời lượng quay | **3** | 15s / 30s / 1m |

Nhãn "**Nk uses**" tính từ field `likes` của CDN theo công thức `round(likes/1000, 1)` trong
`MapperKt` — ví dụ `716845` → `"716.8k uses"`.

**Lưới Home KHÔNG có ô quảng cáo chèn.** `item_face_puzzle_ad.xml` và `item_funny_puzzle_ad.xml`
tồn tại và code path còn đó, nhưng `FragmentHome.java:292` truyền `showAdsInList = false`.

---

## Hai bản: v1 (1:1) và v2 (reskin)

| | v1 | v2 |
|---|---|---|
| Plugin | `Funny Face — APK to Figma v1` | `Funny Face — APK to Figma v2` |
| Thư mục | `figma/v1` + `assets/v1` | `figma/v2` + `assets/v2` |
| Brand | `#016cf7` xanh dương (đúng app gốc) | `#8b15ca` tím violet |
| Sinh ra bằng | Plan 1 | `script/make-v2.py` (chạy lại bất cứ lúc nào) |

v2 **không fork tay file nào** — sửa v1 rồi chạy `make-v2.py` là v2 tự khớp lại.
Biến đổi màu: hue **+65°**, S **×0.82**, L **×0.90** áp đồng nhất cho cả họ brand.
Giữ nguyên màu chức năng (đỏ lỗi/xoá) và màu thang độ khó của Level Picker.
Chữ trên nền brand đổi sang trắng: tương phản **3.84 → 6.87** (v1 vốn dưới chuẩn AA).

Kiểm chứng v2: 41/41 frame · 989/989 node · **0 lệch toạ độ** · ảnh nội dung khớp từng byte.

## Ảnh MÔ PHỎNG vùng camera AR

2 màn quay hiển thị camera trực tiếp + lớp AR dựng theo landmark mỗi khung hình — không có
asset tĩnh nào trong APK. `script/make-mock-ar.py` sinh 3 ảnh minh hoạ, **mọi frame dùng chúng
đều in nhãn `MÔ PHỎNG` ngay trên canvas**:

- Khuôn mặt là **hình khối tổng hợp do script vẽ**, không phải ảnh người thật nào
- Cơ chế áp theo đúng code: `drawFacePuzzleComponent` cắt mặt thành 6 vùng (màn Face Puzzle);
  `OverlayView.java:1311-1317` vẽ overlay nhân vật trước rồi nét mặt lên trên (màn Funny Puzzle)
- Overlay nhân vật là **asset thật trích từ APK**
- **Không** dùng thumbnail CDN làm nội dung người dùng tạo

Có ảnh chụp app thật thì thả vào `assets/v1/50-mock-ar/` đúng tên khoá rồi build lại là thay được.

## ⚠ Những gì KHÔNG lấy được từ APK (đọc kỹ phần này)

### 1. Ba ảnh onboarding không tồn tại
`img_intro_1/2/3` được `FragmentIntro.java:118` gọi tới, nhưng **không có trong APK**:

- `R.java:157-159` có hằng số `0x7f080248/249/24a`
- `values/public.xml` **nhảy thẳng** từ `0x7f080247` sang `0x7f08024b`
- `resources.arsc` trả `NULL in every config` cho cả 3 id
- không file nào tên `img_intro*` ở bất kỳ bucket `res/` nào
- **không phải** split APK (đã loại trừ: không có `lib/`, không có `split_*`, có `resources.arsc`)

Nhiều khả năng là resource shrinking hoặc dấu vết của chính quá trình reskin.
→ 3 frame Intro dùng **placeholder có nhãn**, **không thay bằng ảnh khác**. Nếu sau này có
bản APK đủ asset, thả file đúng tên vào `assets/v1/` rồi build lại là xong.

### 1a. Bộ nhân vật Funny Puzzle đã THAY bằng art mới

`script/make-characters.py` sinh lại cả hai bản mà APK cần cho mỗi nhân vật:

| Đầu ra | Dùng ở đâu |
|---|---|
| `assets/v1/20-nhanvat-origin/<Tên>.png` — 1024×1024 RGBA, nền đặc, **có mặt** | thumbnail màn 40, `imvFunnyOrigin` góc phải màn quay, và `funnyBitmap` = nguồn `BitmapShader` cắt từng bộ phận rơi xuống (`OverlayView.java:1046`) |
| `reference/21-nhanvat-overlay/<id>.png` — nền **trong suốt**, **mặt trống** | `drawFunnyOverlay()` dán đè khung camera (`OverlayView.java:1106-1120`) |

Quy ước "mặt trống" đọc từ chính bộ overlay gốc của APK: xoá **mắt, lông mày, mũi, miệng**;
**giữ** tóc, tai, phụ kiện, cổ áo, **râu** (Messi/Neymar) và **râu mèo** (Naruto).

- Bố cục không tự bịa: mỗi nhân vật lấy đúng bbox của ảnh gốc cùng id trong
  `reference/22-nhanvat-goc-apk/` (bộ trích từ APK, **giữ bất biến**) rồi đặt art mới vừa khít.
  Nhờ vậy thay ảnh mà bố cục các màn không xê dịch một pixel.
- `id=16` đổi ảnh sang **Lamine Yamal**; nhãn trong bản thiết kế đã đổi theo. Nhưng
  `assets/face_funny/data_funny.json` trong APK **vẫn ghi "Messi"** — phía dev phải sửa entry đó.
- `id=8 Neymar_Junior` **không có ảnh mới** (bộ giao chỉ có 1 file Neymar cho 2 slot) → giữ ảnh cũ.

### 1b. Frame bị loại khỏi bản giao (có chủ đích, đảo ngược được)

Không có gì bị xoá — tất cả đều nằm sau cờ trong mã nguồn, bật lại là hiện lại.

| Frame | Cờ | Lý do |
|---|---|---|
| `11a/11b/11c` Intro | `{ excluded: true }` | Design lead yêu cầu bỏ. Đây là lý do audit 1 báo ĐỎ `FragmentIntro` — **không phải sót**. |
| `21` Home Old UI | `{ excluded: true }` | Không phải nhánh mặc định: `FragmentSplash.java:43` chọn Home theo RC `ui_home_show_case`; **RC thật của app trả `1`** → người dùng luôn vào Home mới (`20a…20e`). Màn cũ chỉ hiện khi máy không fetch được RC. Đây là lý do audit 1 báo ĐỎ `FragmentHomeOldUI`. Bỏ frame này khiến 10 asset chỉ nó dùng (`img_banner_*`, `v1_Video1…8`) thành thừa trong bundle — **cố ý giữ lại** để bật lại chỉ cần gỡ 1 cờ. |
| `90` / `91` | `{ excluded: true }` | `FragmentTabHome` / `FragmentTabGallery` là dead code: 0 lần xuất hiện trong nav graph, chỉ còn tham chiếu do Hilt sinh. |
| `30c` / `41f` | `{ excluded: true }` | Màn "tạm dừng quay" KHÔNG tồn tại: `pause()` chỉ được gọi từ `Fragment.onPause()` (lifecycle), không nút nào kích hoạt. Phát hiện khi người dùng chơi app thật. |
| `41d` | `{ excluded: true }` | Màn đếm ngược không tồn tại: `recordingManager.start(0L, …)` nên `onStartWaitingRecord()`/`onFinishWaitingRecord()` chạy đồng bộ tức thời. |
| `10c`, `30e`, `41g`, `D60`, `D61`, `D72`, `D73` | `{ adOnly: true }` | Toàn bộ màn quảng cáo — mentor yêu cầu bỏ. Tắt bằng `SHOW_ADS = false` trong `figma/v1/code.js`. |
| `31b`, `51`, `60` | `{ adDup: true }` | Bản trùng chỉ khác ở khối quảng cáo. |

Bật lại: đặt `SHOW_ADS = true` (cho nhóm ad) hoặc bỏ `{ excluded: true }` ở `screen()` tương ứng.

### 2. Nội dung runtime — placeholder có nhãn, không phải ảnh thật
- **Camera trực tiếp + lớp AR**: 2 màn "puzzle" thực chất là **quay video AR thời gian thực**
  (MediaPipe FaceLandmarker, `OverlayView` 1495 dòng), không phải trò ghép hình. Toàn bộ
  khung hình là runtime.
- **Video/ảnh người dùng tạo**: Result, Play Video, Video Gallery.
- **Thời lượng bài nhạc**: tính lúc chạy bằng `MediaMetadataRetriever` → để `runtime`, không bịa số.
- ~~WebView (Privacy Policy / Term of use)~~ — **đã lấp bằng nội dung THẬT**: app nạp
  `assets/privacy_policy.html` (89 đoạn) và `term_of_use.html` (57 đoạn) qua
  `CompanyInfoFragment.java:119,122`. Đã trích ra `build/policy-text.json` và đổ 16 đoạn
  đầu vào 2 frame. Đây là văn bản thật của app, **không phải placeholder**.

### 3. Nội dung từ server — snapshot, có thể đổi bất cứ lúc nào
18 template + thumbnail lấy từ `wallpaperhd.nyc3.cdn.digitaloceanspaces.com` tại thời điểm
dựng. **Server đổi nội dung là file Figma lệch.** Ảnh nhân vật thì an toàn — bundled trong APK.

### 4. Quảng cáo và UI của SDK/OS — `AD SLOT` có nhãn
Placement thật: `inter_splash · native_onboard/2/3 · native_language/2 · native_home ·
native_collapsible_home · native_collapsible_detail · native_collapsible_preview ·
inter_record · inter_save · native_collapsible_result · native_fullscreen_save`.
Dialog xin quyền, In-App Review, share sheet là UI hệ điều hành → placeholder có nhãn.

### 5. Animation
`swipe_left.json` (Lottie) chỉ vẽ khung tĩnh. Figma không có animation.

---

## Ghi chú về chính app này

**Không có IAP / paywall nào.** Qonversion SDK nằm trong APK nhưng app code không gọi tới;
Settings chỉ 4 hàng (Language / Privacy Policy / Term of use / Share), không có hàng PRO hay
Remove Ads. Doanh thu thuần từ quảng cáo.

**Hai dark pattern đã dựng kèm chú thích đúng bản chất:**
- `activity_native_show_open_fake` — màn quảng cáo **giả dạng app**, lấy icon và tên thật của
  chính Funny Face qua `PackageManager` để trông như màn "tiếp tục vào app".
- Ở màn đó, nút mũi tên đóng (`imgViewClose`) **không có `onClick`** — chỉ `imgDismissNative`
  vô hình mới đóng được thật.

**Code chết vẫn dựng nhưng gắn nhãn:** `FragmentTabHome` và `FragmentTabGallery` không có
trong nav graph, không ai gọi `newInstance()`, chỉ được Hilt sinh DI tham chiếu → 2 frame
`90`/`91` gắn nhãn *DEAD CODE (unreachable)*, **loại khỏi phép diff phủ destination**.

---

## Kiểm chứng — 6 audit Phase 6 đều đạt

| Audit | Kết quả |
|---|---|
| 1. Phủ destination | ⚠ 16/18 — `FragmentIntro` và `FragmentHomeOldUI` CỐ Ý loại (bảng 1b). Audit vẫn báo ĐỎ, không sửa cho qua. |
| 2. Phủ resolve | ✅ 0 chỗ còn raw `@…` / `0x…` |
| 3. Phủ số lượng | ✅ 10/10 mốc khớp (đếm thật trên `scene.json`) |
| 4. Phủ state | ✅ 18 màn gốc, 11 màn nhiều state |
| 5. Audit asset | ✅ không thiếu; 1 thừa hợp lệ (`ic_launcher_foreground`, icon launcher) |
| 6. Overlap + text rỗng | ✅ không frame đè nhau, không text rỗng |
| 7. Render self-check | ✅ 41 frame render bằng font TTF gốc của APK |

**Giới hạn của ảnh self-check:** môi trường không có `cairosvg`/`rsvg-convert` nên node SVG
render thành **silhouette đúng màu fill**, không phải hình icon thật. Hình icon chỉ đúng khi
chạy plugin trong Figma. 26 icon SVG đều có mặt trong bundle.

---

## Cấu trúc thư mục

```
Funny Face/
├─ apk/app.apk
├─ decompiled/{resources,sources}    # apktool 2.12.0 + jadx 1.5.1
├─ assets/v1/                        # 79 asset nhúng — KHOÁ = tên file không đuôi
│   ├─ 10-icons/           26 SVG
│   ├─ 20-nhanvat-origin/  18 PNG   (16 từ APK + Pedri/Sasuke đề xuất)
│   ├─ 30-template-v2/     18 PNG   (CDN, ảnh thật)
│   ├─ 31-template-v1/      8 PNG   (CDN, ảnh thật)
│   └─ 40-anh-app/         11 PNG
├─ reference/21-nhanvat-overlay/     # 18 bitmap AR — KHÔNG hiển thị trực tiếp, không nhúng
├─ figma/v1/
│   ├─ manifest.json  code.js  main.js   # code.js = helper + registry
│   ├─ screens/*.js                      # 7 file, mỗi cụm 1 file
│   └─ assets.js  icons.js  plugin.js    # sinh ra, đừng sửa tay
├─ script/                           # build.sh · export-assets.py · audit-phase6.py
│                                    # capture-scene.js · render-preview.py · make-v2.py
├─ specs/                            # 7 spec Phase 2 + progress.md (ledger + mọi ruling)
└─ build/                            # scene.json + ảnh preview
```

## Sáu lỗi của `kit/` đã vá (ảnh hưởng mọi app dùng kit)

1. `render-preview.py` — `SCRATCH` hardcode đường dẫn máy tác giả → đổi về `<App>/build/`
2. `build.sh` — còn placeholder `<App>` → dùng đường dẫn thật
3. `export-assets.py` — `BUCKETS` chỉ quét `drawable-*`; **app này để ảnh nội dung trong
   `mipmap-*`** → thêm 5 bucket mipmap (lưu ý apktool cắt hậu tố `-v4`)
4. `render-preview.py` — `FONT_MAP` còn font của app cũ → thay bằng 7 họ font thật
5. **`verify.js` hỏng âm thầm** — hook bằng chuỗi *có dấu cách*
   (`'function imageFill(name, scaleMode) {'`) trong khi `code.js` mà chính kit ship lại viết
   dạng nén (`function imageFill(name,scaleMode){`). Cả 3 phép thay đều trượt → **audit asset
   của Phase 6 không bao giờ chạy mà verify vẫn báo xanh**. Đã thay bằng regex + in cảnh báo
   khi không hook được. `capture-scene.js` dính cùng lỗi, đã sửa.
6. `build-plugin.py` — chỉ ghép `code.js`, nhiều người viết song song sẽ đè nhau → ghép thêm
   `screens/*.js` + `main.js` (thuần bổ sung, không có `screens/` thì hành xử y như cũ)
7. **`resolve-layout.py` nuốt mất `backgroundTint`** — `KEEP` thiếu thuộc tính này nên output chỉ
   có `background=`, **mất trọn lớp tint đè lên**. Gặp thật: `native_fake_full_inter.xml` có
   `backgroundTint="#33000000"` (nền đen 20%, không phải xám `f4f4f4`) và
   `backgroundTint=@color/gnt_blue` (nút xanh `#4285f4`, không phải trắng). Thiếu thuộc tính
   trong `KEEP` = **mất thông tin trong im lặng**, không cảnh báo gì. Đã thêm 9 thuộc tính.
8. **Font APK bị subset** — `lato_regular_400.ttf` thiếu glyph tiếng Việt (`đ ạ ầ ă ả Ậ ừ`).
   Không ảnh hưởng Figma (dùng Lato của Google Fonts) nhưng ảnh preview vẽ bằng TTF của APK nên
   chữ Việt ra ô vuông. Đã vá `render-preview.py` tự lùi sang DejaVu cho ký tự thiếu.

---

## Thay đổi sau bản giao (2026-09-20)

1. **Bỏ 3 nhân vật khỏi bản thiết kế** theo yêu cầu: `id 16 Messi` (`Messi_2.png`),
   `id 17 Ronaldo` (`Ronaldo.png`), `id 18 Neymar Jr` (`Neymar_Jr.png`).
   Gỡ khỏi `figma/v1/screens/funny-puzzle.js` + `home.js`, xoá ảnh trong
   `assets/v1/20-nhanvat-origin/` và overlay `reference/21-nhanvat-overlay/{16,17,18}.png`,
   gỡ khỏi `MAP` của `script/make-characters.py`.
   Danh sách Funny Puzzle: 22 → **19 ô** (màn 40 và tab Funny của Home tự dồn lại).
   Node: 1037 → **1001**. Số frame KHÔNG đổi (41).
   ⚠ `assets/face_funny/data_funny.json` trong APK **vẫn còn 3 entry đó** — phía dev phải xoá
   nếu muốn app khớp bản thiết kế. Ảnh nguồn (`messi_2/ronaldo_2/neymar_2 (1).jpeg`) vẫn nằm
   trong `sources/` để khôi phục được.

2. **id 7 Vinicius_Junior đổi sang art 3D** (`sources/images_3D/images_3D/vini.jpeg`),
   thay cho art 2D cũ — nay cả bộ cầu thủ đồng nhất phong cách 3D.
   `USE_3D` thêm id 7, `MAP[7] = 'vini.jpeg'`.

3. **Vá `script/make-characters.py` để chạy được ngoài máy tác giả:**
   `SRC`/`SRC3D` không còn hardcode `/home/ubuntu/Downloads/...` mà trỏ vào `sources/` của
   chính repo (ghi đè được bằng env `SRC_IMAGES` / `SRC_IMAGES_3D`), và thêm tham số lọc id:
   `python script/make-characters.py 7` chỉ sinh lại nhân vật id=7 thay vì ghi đè cả bộ.

4. **Sắp lại thứ tự hiển thị các nhân vật** theo chỉ định của design lead — áp cho cả màn 40
   (List Funny Puzzle) và tab Funny của Home. Dãy id mới:
   `2, 4, 3, 1, 6, 7, 5, 21, 8, 10, 15, 12, 13, 14, 11, 20, 19, 22`
   (Messi · Ronaldo · Haaland · Mbappe · Yamal · Vini · Bellingham · Pedri · Neymar ·
   Trump · Mr.Bean · Timothée · Taylor · Leonardo · Jennie · Rosé · Naruto · Sasuke).
   Trường `id` giữ nguyên id gốc của APK để truy ngược được, chỉ đổi THỨ TỰ trong mảng.
   ⚠ Spec `specs/funny-puzzle.md` và `specs/home.md` vẫn ghi thứ tự GỐC của
   `data_funny.json` — cố ý, vì spec là bằng chứng về APK, không phải mô tả bản thiết kế.
   Muốn app khớp bản thiết kế thì dev phải sắp lại `data_funny.json` theo dãy id trên.

5. **Bỏ thêm `id 9 Bruno Mars`** (cùng cách với 3 nhân vật ở mục 1) → danh sách còn
   **18 ô**, lưới 2 cột vừa đúng 9 hàng, không còn ô lẻ. Node: 1001 → **989**.

6. **`id 22 Sasuke` đổi sang ảnh 3D mới** `sources/images_3D/images_3D/sasue.jpeg`
   (file `sasuke (1).jpeg` cũ không còn trong thư mục nguồn, `MAP[22]` đã trỏ lại).

7. **Sửa lỗi nền ảnh nhân vật bị lệch màu** (`script/make-characters.py`).
   *Triệu chứng:* quanh mỗi nhân vật lộ một khung chữ nhật đổi màu — rõ nhất ở Haaland và
   Ronaldo: viền đỏ ĐẬM bọc quanh vùng đỏ NHẠT bên trong, nhìn như ảnh bị dán vá.
   *Nguyên nhân:* `build_origin()` tạo canvas tô **một màu phẳng** lấy ở viền ảnh nguồn
   (`border_color`), rồi dán ảnh đã cắt — vốn mang sẵn **dải chuyển màu** sáng dần vào giữa —
   đè lên. Màu phẳng không bao giờ khớp được với dải chuyển màu, nên biên vùng dán thành
   một đường gãy thấy rõ.
   *Cách sửa:* thêm `cover_canvas()` — phóng **cả ảnh nguồn** theo đúng hệ số `k` rồi cắt
   một khung 1024×1024 sao cho nhân vật rơi đúng vị trí chuẩn. Nền vì thế CHÍNH LÀ nền gốc,
   liền mạch tới mép, không còn đường gãy. Chỗ ảnh nguồn không phủ tới thì kéo dài hàng/cột
   ngoài cùng (edge-replicate) thay vì tô màu phẳng. Khung đặt nhân vật (`TOP_FRAC`,
   `MAX_W_FRAC`, `face_center`) giữ nguyên nên đầu các nhân vật vẫn thẳng hàng như cũ.
   *Kèm theo:* gọi `fill_round_corners()` ngay sau `peel()`. Ảnh nguồn kiểu thẻ bo góc
   (Jennie) có 4 góc trắng — trước đây bị màu phẳng che mất, nay nền lấy từ ảnh nguồn nên
   phải tô loang trước, không thì lộ 4 mảng trắng ở rìa.
   Đã sinh lại toàn bộ 18 nhân vật; kiểm bằng script so màu 4 góc với viền kề bên: không
   ảnh nào còn lệch bất thường.

8. **Dựng lại nền studio cho 4 cầu thủ** Yamal / Vini / Bellingham / Pedri, để cả 8 cầu thủ
   đồng bộ một kiểu nền (`SYNTH_BG` trong `script/make-characters.py`).
   *Vấn đề:* Messi/Ronaldo/Haaland/Mbappe vốn có sẵn nền studio đẹp — tối ở rìa, sáng dần
   thành quầng hào sau người. Bốn ảnh còn lại mỗi ảnh một kiểu nền (xám phẳng, xanh nhạt,
   nâu) nên xếp cạnh nhau nhìn rời rạc.
   *Cách làm:* tách nhân vật rồi ghép lên nền dựng lại đúng profile đo được từ 4 ảnh đẹp,
   mỗi người một màu riêng — Yamal `hue 38` vàng hổ phách · Vini `150` xanh lá ·
   Bellingham `275` tím violet · Pedri `320` hồng magenta (tránh trùng Messi 212 ·
   Mbappe 220 · Haaland 354 · Ronaldo 5). Đổi màu = sửa số trong bảng `SYNTH_BG` rồi
   chạy lại `python script/make-characters.py <id>`.
   *Tách nền:* `subject_alpha()` khớp một mặt cong mượt (đa thức bậc 5 + nhóm hàm bán kính
   quanh hai tâm) cho NỀN rồi lấy phần sai lệch làm người, lặp 4 lần để quầng hào được mô
   hình hoá dần thay vì bị nhầm là nhân vật. Phải thoả **đồng thời** hai điều kiện mới
   tính là nền: sai lệch nhỏ **và** vùng đó mượt — thiếu một trong hai đều hỏng
   (chỉ độ mượt → lan xuyên áo trắng Bellingham; chỉ sai lệch → ăn mất cằm Vini).
   ⚠ Ngưỡng của Vini phải hạ xuống `7` (các người khác `16`) vì da và vùng tối dưới cằm
   gần như trùng màu với nền xám của ảnh gốc. Ở ngưỡng này vẫn còn **một khuyết nhỏ ở
   quai hàm trái** — cỡ ~3px khi hiển thị trong ô 148dp, gần như không thấy, nhưng có thật.
   *Chưa đụng tới:* `cut` (bản trong suốt dùng cho overlay AR) vẫn dùng `remove_bg()` cũ.
   `subject_alpha()` tách sạch hơn hẳn, chuyển sang dùng nó sẽ cải thiện luôn
   `reference/21-nhanvat-overlay/` — để lần sau.

9. **Hai tầng màu + sửa overlay AR.**
   *Hai tầng (`STYLES`):* cùng một hình dạng ánh sáng để cả lưới đọc như một bộ, chỉ khác
   độ rực. `deep` = đúng profile 4 ảnh gốc, dùng cho cầu thủ (chất poster thể thao).
   `vivid` = đầu tối sáng hơn và đầu sáng giữ bão hoà 0.70 thay vì 0.38, dùng cho nhóm
   ngoài sân cỏ — ô của họ vốn là mảng màu rực (vàng, cam, cyan, hồng), để bão hoà 0.38
   là thành khaki/nâu đục, mất đúng cái bắt mắt cần có. `SYNTH_BG` nay phủ 14 nhân vật;
   4 ảnh gốc Messi/Ronaldo/Haaland/Mbappe **không đụng tới** vì chúng là bản chuẩn.
   Hue được rải sao cho không ô nào kề nhau trong lưới 2 cột bị trùng tông.

   *Lọc khối liền mạch:* mặt nạ nhân vật nay chỉ giữ khối liền mạch chứa thân người
   (gieo mầm ở đáy-giữa). Ảnh nguồn kiểu thẻ bo góc (Mr.Bean) còn một nét viền mảnh chạy
   quanh rìa — không dính vào người nhưng vẫn "khác nền" nên lọt mặt nạ; lọc theo khối
   liền mạch mới bỏ được.

   *`cut` dùng chung mặt na với origin:* trước đây bản trong suốt (nguồn của overlay AR)
   đi đường riêng qua `remove_bg()` cũ, nên `reference/21-nhanvat-overlay/*.png` còn
   nguyên một mảng nền chữ nhật → `mock_ar_ronaldo` nhìn như ảnh lỗi. Nay dùng chung
   `subject_alpha()`.

   *Viết lại `blank_face()`:* cách cũ đi tìm từng LỖ trong mặt nạ da rồi tô đè màu da
   trung bình — phụ thuộc hoàn toàn vào `skin_mask` vốn rất thất thường trên art 3D, kết
   quả sót hẳn một bên mắt, miệng nhoè, lem thành mảng vuông. Cách mới khoanh vùng nét mặt
   (elip nội tiếp khung mặt, chặn bằng mặt nạ da đã lấp lỗ + giãn 25px) rồi thay bằng chính
   khuôn mặt đó đã lọc trung vị bán kính lớn: xoá chi tiết nhỏ nhưng giữ khối sáng tối.
   **Vùng xoá là SIÊU-ELIP** (`|dx/a|^4 + |dy/b|^4 <= 1`), không phải elip thường. Elip
   thóp rất nhanh về hai đầu, mà khung mặt thì kéo dài xuống tận cổ nên MẮT rơi vào gần
   đỉnh elip — đúng chỗ hẹp nhất: đo ra ở tầm mắt elip chỉ phủ `x=425..655` trong khi mắt
   trái nằm ở `x=400..490`, lọt hẳn ra ngoài. Đó mới là lý do sót mắt (hai lần đoán trước
   — mặt nạ da thủng, rồi mặt nghiêng nên không có da phía ngoài lông mày — đều SAI, tìm
   ra bằng cách dump mặt nạ trung gian ra xem). Siêu-elip mũ 4 gần như chữ nhật bo góc,
   ở cùng độ cao đó phủ `x=374..706`, trùm hết bề ngang mặt.
   **Loại phụ kiện theo BỀ NGANG VỆT:** trên mỗi hàng, vệt không-phải-da nào rộng hơn 70%
   bề ngang mặt thì là phụ kiện vắt ngang (băng đô Naruto/Sasuke) → giữ lại; mắt và lông
   mày hẹp hơn nhiều nên vẫn bị xoá. Mặt nạ da chỉ còn dùng cho việc này, không dùng để
   quyết định vùng phủ nữa.

   *Chạy lại `make-mock-ar.py`* để 3 ảnh mô phỏng vùng camera AR khớp bộ art hiện tại —
   các frame `30x`, `41x`, `51b`, `53`, `54`, `60`, `61`, `62` đều dùng chúng.

10. **Vùng xoá nét mặt: chốt bằng bảng khai báo tay, bỏ luật tự nhận diện.**
    Đã thử **bốn** luật tự nhận diện phụ kiện vắt ngang trán để vừa xoá sạch mắt vừa giữ
    băng đô: (a) bề ngang từng vệt không-phải-da, (b) tỉ lệ không-phải-da theo hàng,
    (c) như (b) nhưng chỉ đếm trong bề ngang khuôn mặt, (d) so sắc độ sau khi chuẩn hoá
    độ sáng. Luật nào cũng kẹt giữa hai cực — chặt tay thì sót mắt Ronaldo, lỏng tay thì
    nuốt băng đô Naruto — vì tất cả đều dựa vào `skin_mask`, mà mặt nạ da trên art 3D
    render quá thất thường (của Ronaldo khuyết hẳn một mảng ở tầm mắt).
    Chốt lại: **bỏ hẳn luật tự động**, vùng xoá = siêu-elip ∩ mặt nạ nhân vật, và khai báo
    tay `ZONE_TOP = {19: 0.44, 22: 0.44}` — chỉ 2 nhân vật có băng đô cần mép trên thấp
    hơn mặc định `0.10`. Chắc chắn đúng, và chỉnh lại chỉ mất một giây.
    Thêm nữa, trường da mượt nay dựng bằng **tích chập chuẩn hoá** (làm mờ ảnh×mặt-nạ-da
    rồi chia cho mặt-nạ-da đã làm mờ) thay cho lọc trung vị: chỉ điểm DA đóng góp nên sát
    chân tóc không còn bị trám ra vệt tối — đó là chỗ sót cuối cùng ở đuôi lông mày.

11. **Đổi art Naruto (id 19) và Sasuke (id 22)** sang `uzumaki.jpeg` / `uchiha.jpeg`
    (thêm id 19 vào `USE_3D`). Hai ảnh này nền lửa cam và khói tím, rậm rạp và nhiều
    tương phản.
    ⚠ **Cố ý KHÔNG đưa vào `SYNTH_BG`** — giữ nguyên nền gốc theo yêu cầu, và cũng vì
    `subject_alpha()` giả định nền MƯỢT (khớp một mặt cong trơn rồi lấy sai lệch), gặp nền
    rậm là hỏng hoàn toàn.
    ⚠ Hệ quả: `reference/21-nhanvat-overlay/19.png` và `22.png` **không dùng được** —
    matting phủ 91.5% và 64.6% thay vì bám sát nhân vật. Hai file này là tài liệu tham
    chiếu, **không nhúng vào plugin**, và `make-mock-ar.py` chỉ dùng overlay id 4, nên bản
    thiết kế Figma không bị ảnh hưởng. Muốn overlay AR đúng cho hai nhân vật này thì cần
    ảnh nguồn có nền tách bạch.

12. **Hệ thiết kế v3 — `figma/v3`.** Bản THIẾT KẾ SẢN PHẨM, tách khỏi v1.
    Palette Purple (thương hiệu) / Orange (hành động) / Warm White (màn đọc chữ) /
    Dark (màn nội dung) / Mint (thành công). Đặc tả đầy đủ — vai trò màu, lý do từng
    quyết định, bảng tương phản WCAG, ánh xạ sang XML cho dev — nằm ở
    `docs/superpowers/specs/2026-09-20-funny-face-ui-v3-design.md`.

    Điểm chính: thẻ nhân vật bỏ nền trắng + viền nét đứt, ảnh tràn hết thẻ và tên đè lên
    dải chuyển (ảnh to hơn 33% trong cùng diện tích) · màn nội dung sang nền tím than để
    ảnh nổi và để khối quảng cáo phân biệt được với ô nội dung · Warm White chuyển sang
    dùng cho Settings/Privacy/Term · mọi CTA sang cam đặc chữ tối (7.1:1; trắng trên cam
    chỉ 2.9:1, trượt AA).

    `figma/v1` **giữ nguyên vĩnh viễn** làm bằng chứng đối chiếu với APK — mọi file trong
    `specs/` mô tả nó. `figma/v2` nay **thừa**, v3 thay thế hoàn toàn.

    ⚠ `make-v3.py` là bộ **khởi tạo một lần**, KHÔNG phải phép biến đổi lặp được như
    `make-v2.py`: đổi bố cục thì không có phép biến đổi nào suy ra được từ v1. Script từ
    chối ghi đè nếu `figma/v3` đã có, trừ khi truyền `--force` — chạy lại là xoá sạch mọi
    chỉnh tay trên v3.

13. **Hai lỗi của `kit/` phát hiện khi làm v3:**
    - `code.js` — `grad()` hardcode `a:1` cho cả hai điểm dừng nên **mọi gradient có alpha
      bị vẽ thành mảng đặc**. Không lộ ở v1 vì v1 chỉ dùng gradient đục. Đã sửa trong v3.
    - `render-preview.py` — cũng ép alpha = 255 khi vẽ gradient, nên ảnh preview khác hẳn
      kết quả thật trong Figma. **Đã sửa trong kit**, ảnh hưởng mọi app dùng bộ công cụ này.

14. **`script/audit-contrast.py` — soát tương phản chữ/nền toàn bộ frame theo WCAG 2.1.**
    Duyệt scene JSON theo đúng thứ tự vẽ, với mỗi node chữ tìm lớp nền đục gần nhất phủ
    dưới nó rồi tính tỉ lệ. Chữ/nền bán trong suốt được trộn trước khi tính; gradient lấy
    màu tại đúng độ cao của chữ.

    Bắt buộc chạy sau mỗi lần đổi token. Lý do: hệ dùng token chung nên đổi nghĩa MỘT token
    là ảnh hưởng mọi nơi tham chiếu — đã hỏng thật một lần, đổi `C.textHi` sang màu sáng
    rồi quên `onboard.js`, để lọt 21 node Language Picker thành chữ trắng trên ô trắng
    (1.10:1). Soát bằng mắt qua 41 frame không bắt được.

    v3 hiện tại: **303/303 node đạt AA**.

### Build v3

```sh
cd "App 6"
PYTHONUTF8=1 python "Funny Face/script/make-v3.py"        # chỉ chạy lần đầu
PYTHONUTF8=1 python tools/build-plugin.py --src "Funny Face/assets/v3" --plugin "Funny Face/figma/v3"
node tools/verify.js "Funny Face/figma/v3/plugin.js"
node "Funny Face/script/capture-scene.js" "Funny Face/figma/v3/plugin.js" > "Funny Face/build/scene-v3.json"
PYTHONUTF8=1 python "Funny Face/script/audit-contrast.py" "Funny Face/build/scene-v3.json"
```

### Chạy lại trên Windows
`python3` trong PATH của Windows là stub Microsoft Store — dùng `python`, và bật UTF-8 vì
script mở file không khai báo encoding (mặc định cp1252 sẽ lỗi):

```sh
cd "App 6"
PYTHONUTF8=1 python "Funny Face/script/make-v2.py"
PYTHONUTF8=1 python tools/build-plugin.py --src "Funny Face/assets/v1" --plugin "Funny Face/figma/v1"
PYTHONUTF8=1 python tools/build-plugin.py --src "Funny Face/assets/v2" --plugin "Funny Face/figma/v2"
node tools/verify.js "Funny Face/figma/v1/plugin.js"
```
