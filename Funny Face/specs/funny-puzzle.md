# Cụm: funny-puzzle (list nhân vật + màn ghép mặt vui)

Nguồn: `com.cem.face.puzzle.ui.face_funny.*` — 2 màn:
- **A. FragmentListFunnyPuzzle** — `fragment_list_funny_puzzle.xml` — danh sách 20 nhân vật (grid 2 cột)
- **B. FragmentFunnyPuzzle** — `fragment_funny_puzzle.xml` — màn camera AR ghép mặt (KHÔNG phải màn chọn ảnh tĩnh — xem mục "Sửa hiểu lầm quan trọng" bên dưới)

Điều hướng thật (từ code, không suy diễn):
`FragmentListFunnyPuzzle` → click item → `FragmentListFunnyPuzzleDirections.actionToLevelPicker(funnyPuzzleUI)` → **màn Level Picker** (NGOÀI CỤM NÀY, không có source trong `ui/face_funny`) → chọn `level:Int` → `FragmentFunnyPuzzle(funnyPuzzleTemplate, level)`.
`FragmentFunnyPuzzle` sau khi ghi hình xong → `actionFunnyPuzzleToPreviewWithMusic(fileSave, soundUI)` (màn Preview, ngoài cụm).

---

## SỬA HIỂU LẦM QUAN TRỌNG so với đề bài

1. **`item_funny_puzzle_ad.xml` KHÔNG BAO GIỜ được chèn vào RecyclerView của FragmentListFunnyPuzzle.**
   `AdapterFunnyPuzzleTemplate` hỗ trợ `VIEW_TYPE_AD` (dùng ở nơi khác), nhưng bộ collector
   thật sự nạp dữ liệu cho màn này —
   `FragmentListFunnyPuzzle$initUi$1$2.invokeSuspend` (file `FragmentListFunnyPuzzle$initUi$1$2.java:60-68`) —
   chỉ map `List<FunnyPuzzleUI>` → `List<FunnyPuzzleItem.ContentItem>` rồi gọi `adapter.updateAll(...)`.
   KHÔNG có dòng nào add `FunnyPuzzleItem.AdItem`.
   Việc chèn `AdItem.INSTANCE` tại vị trí index 2 (`arrayList.add(2, FunnyPuzzleItem.AdItem.INSTANCE)`)
   chỉ xảy ra trong `AdapterTemplateCategory.createFunnyPuzzleItems()`
   (`ui/home/AdapterTemplateCategory.java:277-287`) — đây là adapter của **Home screen** (category
   carousel funny-puzzle rút gọn trên trang chủ), một cluster khác, ngoài phạm vi "funny-puzzle".
   → **Số ô render trong FragmentListFunnyPuzzle = ĐÚNG 20, không có ô AD nào.**
   `item_funny_puzzle_ad.xml` vẫn phải được dựng trong Figma (vì `AdapterFunnyPuzzleTemplate`
   dùng chung cho cả 2 màn) nhưng gắn cờ "chỉ xuất hiện ở Home carousel, KHÔNG xuất hiện ở
   FragmentListFunnyPuzzle".

2. **FragmentFunnyPuzzle KHÔNG phải màn "chọn ảnh từ camera/gallery rồi ghép tĩnh".**
   Đây là màn **quay video AR thời gian thực**: `OverlayView` (custom view, MediaPipe
   FaceLandmarker) mở camera trước/sau, track landmark mặt người dùng theo thời gian thực, và
   vẽ đè `overlayImagePath` (ảnh "funny" — mặt biến dạng/phụ kiện hài) lên đúng vị trí mặt đã
   track, rồi `RecordingManager` ghi lại thành video (`fileSave = cacheDir/Tmp/<timestamp>.mp4`).
   KHÔNG có bước "chọn ảnh tĩnh từ thư viện" — chỉ có luồng xin quyền CAMERA (+RECORD_AUDIO,
   +WRITE_EXTERNAL_STORAGE nếu API≤28) rồi mở camera trực tiếp.
   `imvFunnyOrigin` (ảnh nhỏ 85×85dp góc phải trên) hiển thị **`originImagePath`** của nhân vật
   mẫu (ảnh gốc ngôi sao) làm ảnh tham chiếu để người dùng "nhại theo", KHÔNG PHẢI ảnh người dùng.

---

## A. FragmentListFunnyPuzzle — `fragment_list_funny_puzzle.xml`

### A.1 Geometry (resolve-layout + raw XML, res/values)

Canvas 360×800dp. Root: `ConstraintLayout` fill_parent.

| Vai trò | View | Thuộc tính |
|---|---|---|
| Nút back | `AppCompatImageView id=btnBack` | style `BackImageButton1` → kế thừa `Base.PrimaryButton.Square` (48×48dp, background `?selectableItemBackgroundBorderless`, scaleType fitCenter, adjustViewBounds) + override: `padding=8dp(size_8)`, `layout_margin=12dp(size_12)`, `src=@drawable/ic_back_1`. Constraint: start=parent, top=parent. |
| Tiêu đề | `AppCompatTextView` | style `ScreenTitleCommon`: text=`@string/funny_puzzle`="**Funny Puzzle**", `textSize=20sp(text_size_20)`, `textColor=#ff171716(text_primary_color)`, `gravity=center`, `singleLine=true`, `fontFamily=@font/lato_bold_700`, wrap×wrap. Constraint: căn giữa theo `btnBack` (top/bottom = btnBack, start/end = parent) → text nằm ngang hàng nút back, canh giữa màn ngang. |
| List | `RecyclerView id=rvFunnyPuzzleTemplates` | `padding=10dp(size_10)`, width=fill_parent, height=0dp (match constraint top=btnBack.bottom, bottom=parent) → chiếm hết phần còn lại phía dưới header. `app:layoutManager="androidx.recyclerview.widget.GridLayoutManager"` VÀ `app:spanCount="2"` — **set thẳng trong XML** (không set lại trong code — `AdapterFunnyPuzzleTemplate.getSpanSizeLookup()` chỉ dùng để set spanSize=1 cho content item, không đổi spanCount). |

### A.2 Visibility

| View | XML mặc định | Runtime | Điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| btnBack | visible | `setEnabled(false)` khi click (chặn double-tap) rồi `popBackStack()` | luôn | VISIBLE luôn, chỉ disable tạm |
| Toàn bộ list | ẩn cho tới khi Flow `getListFunnyPuzzleTemplates()` (StateFlow từ DB) emit | — | mặc định khởi tạo `emptyList()` (`SharingStarted.WhileSubscribed(5000)` + `CollectionsKt.emptyList()` initial) → sau đó DatabaseRepositoryImpl.getFunnyTemplates() đọc JSON asset và emit 20 item gần như ngay (không phải network) | STATE "rỗng" chỉ thoáng qua lúc mở màn, thực tế luôn có data (bundled asset, không cần mạng) |

### A.3 List — item_funny_puzzle.xml (ContentItem, ×20, KHÔNG có ad)

Grid 2 cột (`GridLayoutManager spanCount=2`), `spanSize`: content=1, ad=2 (nhưng ad không bao giờ xuất hiện ở màn này — xem mục "SỬA HIỂU LẦM").

Item (`item_funny_puzzle.xml`):
- Root `ConstraintLayout`: `background=@drawable/bg_funny_puzzle` (shape: solid `#ffffffff` (white), `corners radius=16dp(size_16)`, `stroke width=1dp(size_1) color=#ff016cf7(primary_color) dashWidth=4dp dashGap=4dp` — viền nét đứt xanh dương), `padding=1dp(size_1)`, `layout_margin=10dp(size_10)`, width=fill_parent, height=wrap_content.
  - `ImageView id=imvFunnyPuzzle`: width=fill_parent, height=0dp, `adjustViewBounds=true`, `layout_constraintDimensionRatio="1:1"` (vuông), bo góc runtime `ViewExtKt.setRadiusPx(16dp = R.dimen.size_16)` (set bằng code, không phải XML — outline/clip). Ảnh: `Glide.load(content.getOriginImagePath())` — dùng field **`originImagePath`**, KHÔNG phải overlay. Click → callback `onItemClick`.
  - `TextView id=tvName`: `background=@drawable/bg_funny_puzzle_text_name` (shape: `bottomLeftRadius=bottomRightRadius=16dp`, solid white — chỉ bo 2 góc dưới, khớp với ảnh vuông phía trên để tạo card bo toàn phần), `padding=10dp`, `gravity=center`, `singleLine=true`, `fontFamily=@font/lato_bold_700`, width=fill_parent, height=wrap_content, constraint bottom=parent. Text = `content.getName()`.

### A.4 Data hardcode — `assets/face_funny/data_funny.json` (20 entry, ĐỌC THẬT từ APK, đúng thứ tự)

```json
[
 {"id":1,"name":"Kylian Mbappe","image":"Kylian_Mbappe"},
 {"id":2,"name":"Leonel Messi","image":"Leonel_Messi"},
 {"id":3,"name":"Erling Haaland","image":"Erling_Haaland"},
 {"id":4,"name":"Cristiano Ronaldo","image":"Cristiano_Ronaldo"},
 {"id":5,"name":"Jude Bellingham","image":"Jude_Bellingham"},
 {"id":6,"name":"Messi","image":"messi"},
 {"id":7,"name":"Vinicius Junior","image":"Vinicius_Junior"},
 {"id":8,"name":"Neymar Junior","image":"Neymar_Junior"},
 {"id":9,"name":"Bruno Mars","image":"Bruno_Mars"},
 {"id":10,"name":"Donald Trump","image":"Donald_Trump"},
 {"id":11,"name":"Jennie","image":"Jennie"},
 {"id":12,"name":"Timothe Chalamet","image":"Timothe_Chalamet"},
 {"id":13,"name":"Taylor Swift","image":"Taylor_Swift"},
 {"id":14,"name":"Leonardo Dicaprio","image":"Leonardo_Dicaprio"},
 {"id":15,"name":"Mr.Bean","image":"Mr_Bean"},
 {"id":16,"name":"Messi","image":"Messi_2"},
 {"id":17,"name":"Ronaldo","image":"Ronaldo"},
 {"id":18,"name":"Neymar Jr","image":"Neymar_Jr"},
 {"id":19,"name":"Naruto","image":"Naruto"},
 {"id":20,"name":"Rose","image":"Rose"}
]
```
Chú ý: `"Messi"` xuất hiện 3 lần (id 2 "Leonel Messi", id 6 "Messi"/messi.png, id 16 "Messi"/Messi_2.png) — 3 card khác nhau, ảnh khác nhau, KHÔNG được gộp.

### A.5 Nguồn ảnh — mapping field JSON → asset path (từ `MapperKt.toFunnyPuzzleUI`, file `com/cem/data/mappers/MapperKt.java:94-97`)

```
originImagePath  = "file:///android_asset/face_funny/origin/"  + entity.image + ".png"   ← dùng field "image"
overlayImagePath = "file:///android_asset/face_funny/overlay/" + entity.id    + ".png"   ← dùng field "id" (SỐ, không phải "image")
```
- `origin/` = 20 file đặt tên theo `image` (vd `origin/Kylian_Mbappe.png`, `origin/messi.png`, `origin/Messi_2.png`) — asset bundled, đã verify tồn tại đủ 20 file trong APK.
- `overlay/` = 20 file đặt tên **theo số thứ tự `1.png`…`20.png`** (khớp `id`, không khớp tên) — asset bundled, đã verify tồn tại đủ 20 file.
- **item_funny_puzzle.xml (list) dùng `originImagePath`** (ảnh gốc ngôi sao, vuông, card danh sách).
- **imvFunnyOrigin trên FragmentFunnyPuzzle cũng dùng `originImagePath`** (ảnh tham chiếu nhỏ).
- **`overlayImagePath` chỉ dùng làm bitmap AR ghép mặt** (`OverlayView.setOverlayFunnyBitmap(bitmap)`), KHÔNG hiển thị trực tiếp trong list hay làm thumbnail.

### A.6 Ad slot & tracking
- Không có AD trong list này (xem mục sửa hiểu lầm #1).
- Click item → `CemViewModel.logEvent("cate_funny_choose", {"cate_funny": name})` (`EventTrackingConst.CATE_FUNNY_CHOOSE`/`PARAM_CATE_FUNNY_KEY`) rồi điều hướng sang Level Picker.

### A.7 Remote-config
Không có nhánh remote-config nào chi phối màn này trong code đã đọc (list nạp thẳng từ asset JSON bundled, không qua Firebase Remote Config).

---

## B. FragmentFunnyPuzzle — `fragment_funny_puzzle.xml`

Args bắt buộc: `funnyPuzzleTemplate: FunnyPuzzleUI` (Parcelable), `level: Int` (chọn ở Level Picker, ngoài cụm) — `level` chỉ dùng để set `overlay.setPlaySpeed(level)` (tốc độ phát animation overlay), KHÔNG đổi ảnh/overlay khác nhau theo level.

### B.1 Geometry (raw XML `fragment_funny_puzzle.xml` + res/values)

Root `ConstraintLayout` fill_parent (360×800dp), nền = camera preview vẽ bởi `OverlayView` (không có `background` màu tĩnh trong layout).

| Vai trò | View | Thuộc tính |
|---|---|---|
| Camera + AR overlay | `com.cem.face.puzzle.face_mark.OverlayView id=overlay` | width/height=0dp, `layout_constraintHeight_percent=1.0`, phủ kín 4 cạnh parent → full-bleed camera preview. **Custom view onDraw/draw()**, xem mục B.4. |
| Banner nhắc | `ImageView id=imvNotify` | width=0dp (`constraintWidth_percent=0.85`), height=wrap, `layout_marginTop=32dp(size_32)`, `adjustViewBounds=true`, top=dưới `imvFunnyOrigin`, canh giữa theo `overlay`. Ảnh: `Glide.load(R.drawable.img_notify_puzzle)` — asset local cố định (không đổi theo nhân vật). |
| Ảnh tham chiếu nhân vật | `ImageView id=imvFunnyOrigin` | width=85dp(size_85) cố định, height=0dp + `dimensionRatio=1:1` (→ 85×85dp vuông), `layout_marginTop=16dp(size_16)`, `adjustViewBounds=true`, constraint end=parent, top=dưới `btnBack` (góc phải trên màn). Ảnh nạp 2 lần khác thời điểm (xem B.3). |
| Nút back | `ImageButton id=btnBack` | style `BackImageButton2` (kế `Base.PrimaryButton.Square`: 48×48dp) override `padding=4dp(size_4)`, `layout_margin=12dp`, `src=@drawable/ic_back_2`; thêm `android:elevation=10dp(size_10)`. start/top=parent. |
| Pill nhạc nền | `ConstraintLayout id=btnAddMusic` | `background=@drawable/bg_black_40_rounded` (solid `#66171716`, corner radius=40dp — pill đen mờ 40%), `paddingHorizontal=4dp`, width=wrap, height=32dp(size_32), `maxWidth=180dp(size_180)`, canh giữa ngang màn, top/bottom = btnBack. |
| — icon nhạc | `AppCompatImageView id=imgMusic` | `padding=4dp`, `src=@drawable/ic_music`, `layout_marginStart=4dp`. |
| — tên bài hát | `AppCompatTextView id=tvNameSong` | `textColor=#ffffffff(white)`, `ellipsize=marquee`, `singleLine=true`, `maxWidth=96dp(size_96)`, `includeFontPadding=false`, `marqueeRepeatLimit=marquee_forever`, `layout_marginEnd=8dp`. Text mặc định = `@string/add_sound` = **"Add song"**. |
| — divider dọc | `AppCompatImageView id=vVertical` | `background=white`, width=1dp height=0dp, `visibility=gone` mặc định. |
| — nút xoá nhạc | `AppCompatImageView id=btnRemoveSound` | `src=@drawable/ic_close`, `visibility=gone` mặc định — chỉ hiện khi đã chọn nhạc (xem B.2). |
| Nút quay | `com.cem.face.puzzle.ui.custom_view.RecordingProgress id=btnRecording` | 80×80dp(size_80), `layout_marginBottom=24dp(size_24)`, canh giữa ngang, bottom = trên `bottomSpace`. Custom view onDraw, xem B.4. |
| List chọn thời lượng quay | `com.cem.face.puzzle.ui.custom_view.SnappyRecycleView id=rcvTimeRecord` | orientation=horizontal, wrap×wrap, `app:layoutManager=LinearLayoutManager` (set trong XML), canh giữa theo `btnRecording`, bottom = trên `btnRecording`. |
| Đếm ngược chờ quay | `AppCompatTextView id=tvWaitingRecordCountdown` | `textSize=36sp(text_size_36)`, `textColor=#ff02bbfa(progress_color)`, `fontFamily=@font/lato_black_900`, `includeFontPadding=false`, `visibility=gone` mặc định, `layout_marginBottom=16dp`, canh giữa theo `btnRecording`, bottom = trên `btnRecording`. |
| Nút lật camera | `AppCompatImageView id=btnFlipCamera` | style `Base.PrimaryButton.Square` (48×48dp) + `padding=4dp`, `src=@drawable/ic_rotation_camera`, `layout_marginEnd=8dp`, top/bottom = btnBack, end = parent. |
| Space đáy | `Space id=bottomSpace` | width=fill_parent, height=0dp, bottom=parent — dùng làm mốc margin động (xem B.2, `updateMarginForView`). |
| Container AD collapsible | `FrameLayout id=nativeCollapsibleContainer` | width=0dp(size_0, match constraint start/end=parent), height=wrap, bottom = trên `bottomSpace`. |
| — placeholder chờ ad | `View id=collapseHolderNative` | `background=@drawable/bg_ad_native_media_white` (layer-list: nền trắng + viền dưới 1dp `#ffe4e3e2`), height=`@dimen/ad_native_collapsed_height`=256dp(size_256), width=fill_parent. |
| Group tiện ích | `Group id=groupFunctions` | ref: `btnBack, btnAddMusic, btnFlipCamera, rcvTimeRecord, imvNotify` — ẩn/hiện đồng loạt lúc đang đếm ngược (xem B.2). |

### B.2 Visibility (từ code, `FragmentFunnyPuzzle.java` + `initUi$1$1` smali)

| View/Group | XML mặc định | Runtime setter | Điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| `collapseHolderNative` | visible | `ViewExtKt.gone(view)` sau delay 2000ms trong `initUi` (trừ khi `isRecordFinished=true` thì bỏ qua toàn bộ khối init) | luôn (first init) | GONE sau 2s, rồi native collapsible ad tự load vào `nativeCollapsibleContainer` (đè lên chỗ đã gone) |
| `tvWaitingRecordCountdown` | gone | `visible()` khi `onStartWaitingRecord()`; `gone()` khi `onFinishWaitingRecord()` | trong lúc đếm ngược trước khi quay thật (RecordingManager) | GONE mặc định → VISIBLE khi đếm ngược → GONE lại |
| `groupFunctions` (btnBack, btnAddMusic, btnFlipCamera, rcvTimeRecord, imvNotify) | visible | `ViewExtKt.gone(group)` khi `onStartWaitingRecord()` | trong lúc đếm ngược | Ẩn toàn bộ thanh công cụ khi đang đếm ngược để tập trung vào khung hình |
| `btnRecording` | enabled | `setEnabled(false)` lúc đếm ngược (`onStartWaitingRecord`, `onWaitingRecord`) và lúc chờ camera permission; `setEnabled(true)` khi `onStartRecording()` | | disable trong lúc chờ, enable khi record thật bắt đầu |
| `vVertical`, `btnRemoveSound` | gone | không thấy code set visible trực tiếp trong 2 file đã đọc (`initListener`, `initUi`) — chỉ `btnRemoveSound.setOnClickListener{ changeSound(null) }` | cần xem `observeCurrentSound`/binding adapter tự động qua data-binding `visibility` (không verify được tĩnh — **CỜ: chưa resolve chỗ set visible khi có nhạc**, có thể qua XML data-binding `app:goneUnless` không thấy trong layout thô đã đọc) | GẮN CỜ — suy đoán: hiện khi `currentSound != null`, nhưng chưa tìm được dòng code set trực tiếp |

### B.3 Nguồn ảnh 2 lần nạp vào `imvFunnyOrigin` (2 luồng độc lập, dùng chung 1 ImageView)

1. **Lúc `initUi` (ngay khi vào màn, không cần quyền)**: `Glide.with(imvFunnyOrigin).asBitmap().load(args.funnyPuzzleTemplate.getOverlayImagePath())…override(funnyBitmapSize)` nhưng `.into(CustomTarget)` — target này **KHÔNG set ảnh vào ImageView**, mà gọi `binding.overlay.setOverlayFunnyBitmap(bitmap)` (file `FragmentFunnyPuzzle$initUi$1$1$1$2.smali`) → bitmap này dùng làm lớp phủ AR trên mặt, không hiển thị trực tiếp ở `imvFunnyOrigin`.
2. **Lúc quyền CAMERA được cấp** (`launcherOpenCameraDevice$lambda$0`, file `FragmentFunnyPuzzle.java:298-348`): `Glide.with(imvFunnyOrigin).asBitmap().load(args.funnyPuzzleTemplate.getOriginImagePath())…into(imvFunnyOrigin)` — lần này **mới thật sự hiển thị ảnh vào `imvFunnyOrigin`** (dùng `originImagePath`, ảnh gốc ngôi sao) làm thumbnail tham chiếu góc phải trên. Callback `onResourceReady` cũng trigger `cameraManager.startFunnyCamera(...)` và `recordingManager.prepare(...)`.
`funnyBitmapSize = Math.min(screenWidth, screenWidth) = screenWidth` (px), set 1 lần trong `initUi$1$1`.

### B.4 Custom view onDraw

- **`OverlayView`** (`com/cem/face/puzzle/face_mark/OverlayView.java`, 1495 dòng) — View chuyên biệt, override `draw(Canvas)` (không phải `onDraw` cổ điển). Dùng MediaPipe `FaceLandmarkerResult` để track landmark mặt qua camera preview, có 4 `Mode` (`FacePuzzle`, `FaceFunny`, `FacePop`, `FaceWhirl`) — màn này set cứng `Mode.FaceFunny`. Vẽ overlay bitmap (từ `setOverlayFunnyBitmap`) khớp theo vị trí/scale/xoay khuôn mặt detect được mỗi frame (`drawFunnyOverlay`, `calculateScaleInfo`, `calculateComponentCenterPoint`…), có xử lý eye-blink detect, crop corner path effect. **KHÔNG PHẢI custom crop tĩnh — đây là renderer AR thời gian thực**, không nên dựng tĩnh 1:1 trong Figma mà nên annotate là "AR camera renderer — runtime placeholder cho khung hình camera + overlay tracking".
- **`RecordingProgress`** (`ui/custom_view/RecordingProgress.java`) — nút quay video hình tròn, override `onDraw(Canvas)` thật (dòng 162-172):
  - `drawIcon(canvas)`: vẽ `iconBitmap` (mặc định `R.drawable.ic_play_filter`, đổi thành `R.drawable.ic_pause_filter` khi bắt đầu animation) căn giữa, kích thước = `min(width,height)` hình vuông giữa view.
  - Vòng tiến trình: `Paint` stroke, `strokeWidth=12px`, `Cap.ROUND`, `color=#ff02bbfa(progress_color)`, `canvas.drawArc(rectF, startAngle=-90°, sweepAngle=360°×progress, useCenter=false, paint)` — vòng tròn đếm ngược tiến trình quay, `durationSeconds` mặc định 60L (khớp lựa chọn "1m" mặc định trong list thời lượng).

### B.5 List `rcvTimeRecord` — thời lượng quay (item `item_time_record.xml`, dùng `AdapterTimeRecord`)

Data hardcode 100% (từ `AppSetting.java:46`, KHÔNG remote):
```
listTimeRecord = [ {"15s", 15L}, {"30s", 30L}, {"1m", 60L} ]
```
→ đúng 3 item, thứ tự cố định "15s" → "30s" → "1m". Item layout:
- `LinearLayout` vertical, gravity=center, `layout_margin=4dp`.
  - `TextView id=tvTime`: `textSize=14sp`, `textColor=#99ffffff` (mặc định, unselected), padding 12/4/12/4dp. Khi selected → `textColor=white(#ffffffff)`.
  - `ImageView id=imgDot` 6×6dp, `src=@drawable/dot_white`, `visibility=invisible` mặc định → hiện (`VISIBLE`) khi item đang chọn.
`positionSelected` khởi tạo = **-1** (không item nào có dot hiện lúc mới vào, dù `RecordingProgress.durationSeconds` mặc định 60L/"1m") — click item mới đổi `positionSelected` + gọi `btnRecording.setTimeDuration(time)`.

### B.6 Ad slot & event tracking
- `nativeCollapsibleContainer` → AD SLOT native collapsible, placement key **`"native_collapsible_detail"`** (`AdKey.NATIVE_DETAIL_COLLAP`), load qua `loadAndShowNativeCollapsibleSafe` sau delay 2s.
- Sau khi `onStopRecording()`: gọi `loadShowFullscreenSafe(AdKey.INTER_RECORD = "inter_record", …)` → AD SLOT interstitial fullscreen — chờ ad xong (hoặc timeout) rồi mới `navigateToDirections(actionFunnyPuzzleToPreviewWithMusic(fileSave, soundUI))`.
- Log event: `"record_view"` (vào màn), `"record_button_click_start"`/`"record_button_click_stop"` (bấm nút quay), `"recording_view"` (bắt đầu quay thật).

### B.7 State (mỗi state = 1 frame riêng theo brief)

1. **Xin quyền camera** — ngay khi vào màn (sau khi ảnh overlay + origin nạp xong lần 1), tự động gọi `launcherOpenCameraDevice.launch([CAMERA, RECORD_AUDIO, (WRITE_EXTERNAL_STORAGE nếu API≤28)])`. UI hệ thống (permission dialog) → **placeholder có nhãn "OS permission dialog"**.
2. **Quyền bị từ chối** — `ContextExtKt.toastMessageLongTime(context, R.string.you_need_permission_to_use_this_feature)` rồi `popBackStack()` ngay (thoát màn, không có UI riêng để retry). → **placeholder có nhãn "OS toast"** + hành vi "quay lại màn trước".
3. **Quyền đã cấp / camera live** — `imvFunnyOrigin` hiện ảnh gốc ngôi sao, `OverlayView` chạy camera preview + AR tracking (runtime placeholder — không có khung hình camera thật trong APK để dựng tĩnh), `groupFunctions` hiện đầy đủ, `btnRecording` icon `ic_play_filter`, vòng tiến trình 0%.
4. **Đang đếm ngược trước khi quay** (`onStartWaitingRecord`→`onWaitingRecord`→`onFinishWaitingRecord`) — `tvWaitingRecordCountdown` VISIBLE hiện số đếm ngược (text runtime, không hardcode), `groupFunctions` GONE, `btnRecording` disabled.
5. **Đang quay** (`onStartRecording`) — icon nút đổi `ic_pause_filter`, vòng tiến trình chạy theo `progress` (animator 0→1 trong `durationSeconds`×1000ms), nhạc nền phát nếu có chọn (`mediaMusic.start()`).
6. **Tạm dừng quay** (`onPauseRecording`) — icon quay lại `ic_play_filter`, animator pause, nhạc pause.
7. **Dừng quay xong** (`onStopRecording`) — `isRecordFinished=true`, giải phóng camera/media, load `inter_record` ad, điều hướng sang Preview (ngoài cụm) mang theo `fileSave` (video mp4, **runtime placeholder — sản phẩm do camera tạo ra, không có trong APK**) + `soundUI` đã chọn.
8. **Đã chọn nhạc nền** — `btnAddMusic` hiện tên bài hát thật (`tvNameSong.text = sound.name`, xem `observeCurrentSound`), có khả năng hiện `vVertical`+`btnRemoveSound` (xem CỜ ở B.2) để gỡ nhạc.

### B.8 Remote-config
Không có nhánh Firebase Remote Config chi phối logic hiển thị của 2 màn này trong các file đã đọc — chỉ có config ads chuẩn (`AdKey`, ngoài phạm vi UI/geometry của cụm này).

---

## Cờ / chưa resolve tĩnh được

1. `vVertical` / `btnRemoveSound` visibility khi đã chọn nhạc — chưa tìm thấy dòng code set `visible()` trực tiếp trong `initListener()`/`initUi()`/`observeCurrentSound()` (chỉ thấy `btnRemoveSound.setOnClickListener{ changeSound(null) }`). Cần đọc thêm `FragmentFunnyPuzzle$observeCurrentSound$2.java` sâu hơn nếu cần chính xác 100% (đã đọc lướt, không thấy set visibility rõ ràng ở đoạn đã trích — khả năng cao nằm trong đúng file đó nhưng việc gán `visible()/gone()` có thể lồng trong nhánh `if (soundUI != null)`).
2. `OverlayView.draw()` (1495 dòng, nhiều nhánh Mode/FaceComponent) — chỉ tóm tắt hành vi tổng quan (AR renderer thời gian thực), KHÔNG chép toàn bộ logic vẽ pixel-by-pixel vì không khả thi dựng tĩnh trong Figma; đã gắn nhãn "runtime placeholder".
3. Camera preview thật (hình ảnh mặt người dùng + overlay AR ghép lên) — 100% runtime, không có asset tĩnh nào trong APK để tham chiếu màu/khung hình chính xác; Figma cần dùng khung placeholder có nhãn rõ "Live camera + AR overlay (runtime)".
4. `Lottie swipe_left.json` — grep toàn bộ `com/cem/face/puzzle` không tìm thấy tham chiếu nào trong 2 file/adapter của cụm `face_funny`. Không dùng trong cụm này (có thể dùng ở Level Picker hoặc Onboarding, ngoài phạm vi).
5. `res/menu/*` — không có menu nào của app (`getMenuInflater()`) áp dụng cho 2 màn này; 3 file menu tìm thấy trong `res/menu` đều thuộc SDK AppLovin/MAX debugger, không liên quan.
6. Level Picker (màn trung gian giữa List và FunnyPuzzle) — ngoài cụm "funny-puzzle" theo phân công, chỉ ghi nhận `level:Int` ảnh hưởng `overlay.setPlaySpeed(level)`, không có source code trong `ui/face_funny` để mô tả UI của nó.
