# Cụm: face-puzzle — Màn chơi ghép mặt (camera AR filter) + Chọn level

Nguồn: SRC = `decompiled/sources/sources/com/cem/face/puzzle` (lưu ý: KHÔNG phải
`decompiled/sources/com/cem/face/puzzle` — package thật nằm dưới `sources/sources/`).
RES = `decompiled/resources/res`.

## 0. Phát hiện quan trọng — đính chính giả định trong brief

**"Face Puzzle" KHÔNG phải màn kéo-thả mảnh ghép jigsaw.** Đọc trọn
`ui/face_puzzle/FragmentFacePuzzle.java` + `face_mark/OverlayView.java` +
`recording/RecordingManagerImpl.java` cho thấy đây là **màn quay video bằng camera
trước, có bộ lọc AR "ghép mặt"**: `OverlayView` dùng MediaPipe `FaceLandmarker` để
dò 468 điểm mốc trên khuôn mặt live, sau đó **cắt 6 vùng mặt (2 mắt, 2 lông mày,
mũi, miệng — enum `ComponentName`) ra khỏi khung hình và cho chúng bay lượn/xoay/co
giãn ngẫu nhiên quanh mặt** (3 chế độ `OverlayView.Mode`: `FacePuzzle` — mảnh mặt
rời rạc bay quanh, `FacePop` — phồng/co, `FaceWhirl` — xoáy). "Puzzle" ở đây là
tên hiệu ứng thị giác, không có tương tác kéo-thả nào. Người dùng chỉ bấm nút quay
video (RecordingProgress) — camera + hiệu ứng chạy tự động trong lúc quay.

`fragment_level_picker.xml` không chọn "độ khó puzzle logic" mà chọn **tốc độ hiệu
ứng** (`OverlayView.PlayLevel`: Easy/Intermediate/Difficulty → biên độ dịch chuyển
+ tốc độ xoay + tốc độ co giãn của các mảnh mặt).

`item_face_puzzle_template.xml` + `item_face_puzzle_ad.xml` **không nằm trong
`fragment_face_puzzle.xml`/`fragment_level_picker.xml`**. Chúng là item của
`AdapterFacePuzzleTemplate` (package `ui/home`, KHÔNG phải `ui/face_puzzle`),
được RecyclerView lưới 2 cột trên **màn Home** (`FragmentHome` / `FragmentTabHome`
/ `FragmentHomeOldUI`) render — đây là danh sách **video mẫu (template preview)**
dẫn người dùng vào luồng face-puzzle. Bấm 1 item → `actionHomeToPreviewTemplate(url)`
→ màn preview video (`FragmentPreviewTemplate`, KHÔNG thuộc cụm này) → nút "Try
now" ở đó mới điều hướng vào `level_picker`/`face_puzzle` của cụm này. Tài liệu
này vẫn đặc tả đầy đủ hình học + logic của 2 layout item này theo yêu cầu brief,
và ghi rõ chúng render ở màn Home.

## 1. Sơ đồ luồng & điều hướng vào cụm

Entry point chính: `FragmentPreviewTemplate.levelPicker()`
(`ui/preview/FragmentPreviewTemplate.java:75-86`):
```
if (FirebaseRemoteManager.getBoolean(ConfigKey.LEVEL_PICKER_SKIPPED)) {
    actionPreviewToFacePuzzle(level = 2)          // bỏ qua level picker, mặc định Intermediate
} else {
    actionToLevelPicker(funnyPuzzleTemplate = null) // vào level picker
}
```
`ConfigKey.LEVEL_PICKER_SKIPPED = "level_picker_skipped"` — **khớp CHÍNH XÁC** tên
key trong RC đã fetch. Đọc bằng `FirebaseRemoteManager.getBoolean()` →
`RemoteConfigKt.getRemoteConfig(Firebase).getBoolean(value)`, bọc try/catch, nếu
lỗi/không có → trả `false`. Không có `remote_config_defaults.xml` trong app (không
tìm thấy file default RC nào) → default SDK khi chưa fetch cũng là `false`.
⇒ **Nhánh mặc định = level_picker_skipped = false = LEVEL PICKER CÓ HIỂN THỊ**
(khớp với `/tmp/rc.json` đã fetch thật: `level_picker_skipped=false`).

`FragmentLevelPicker` cũng được nhiều màn khác điều hướng tới qua
`MainNavDirections.actionToLevelPicker(funnyPuzzleTemplate: FunnyPuzzleUI?)`
(splash, intro, home, preview-with-music, result, video-gallery, language-picker…)
— khi `funnyPuzzleTemplate != null` thì bấm level trong picker sẽ đi sang
`FunnyPuzzle` (cụm khác), khi `null` (trường hợp từ face-puzzle) thì đi sang
`FragmentFacePuzzle` của cụm này. `fragment_level_picker.xml` dùng chung 1 layout
cho cả 2 luồng — file này đặc tả layout đó, ghi rõ nhánh `funnyPuzzleTemplate=null`
là nhánh của cụm face-puzzle.

`FragmentLevelPicker.supportNavigate(level)`
(`ui/level/FragmentLevelPicker.java:96-106`):
```
if (args.funnyPuzzleTemplate == null) actionLevelPickerToFacePuzzle(level)
else actionLevelPickerToFunnyPuzzle(funnyPuzzleTemplate, level)
```
level: Easy→1, Intermediate→2, Difficulty→3 (khớp `OverlayView.setPlaySpeed`:
`level==1→Easy, level==2→Intermediate, else→Difficulty`,
`face_mark/OverlayView.java:1474-1475`).

---

## 2. Màn `fragment_face_puzzle.xml` — quay video hiệu ứng ghép mặt

Fragment: `ui/face_puzzle/FragmentFacePuzzle.java` (extends `AdBaseFragment`).
ViewModel: `FacePuzzleViewModel.java`. Canvas 360×800dp, không vẽ status bar
(brief), nhưng code có gọi `updateMarginForView(btnBack, bottomSpace)`
(`BaseFragment.java:283`) để cộng inset status-bar/nav-bar runtime qua
`WindowInsetsCompat` — dựng UI ở margin tĩnh khai báo trong XML, bỏ qua inset.

### A. Geometry (từ `resolve-layout.py` + raw XML, `layout/fragment_face_puzzle.xml`)

Root: `ConstraintLayout` fill_parent × fill_parent (360×800dp).

| View | id | Kích thước / vị trí (constraint) | Nền / style | Text |
|---|---|---|---|---|
| `OverlayView` (custom, xem mục "Custom view") | `overlay` | 0dp×0dp thực chất = full màn (start/end/top/bottom = parent, `layout_constraintHeight_percent=1.0`) | vẽ tay (camera preview + hiệu ứng) | — |
| `ImageView` | `imvNotify` | width=85% overlay (`layout_constraintWidth_percent=0.85`), height=wrap, căn giữa trong `overlay` | `adjustViewBounds=true`, ảnh nạp bằng Glide `R.drawable.img_notify_puzzle` (asset bundled, webp local) | — |
| `ImageButton` | `btnBack` | style `BackImageButton2` → 48×48dp, `layout_margin=12dp`, `padding=4dp`, elevation=`@dimen/size_10`=10dp; góc trên-trái (start/top = parent) | ripple `?selectableItemBackgroundBorderless`, icon `@drawable/ic_back_2` | — |
| `ConstraintLayout` (pill âm nhạc) | `btnAddMusic` | wrap×32dp, `maxWidth=180dp`, `paddingHorizontal=4dp`; top/bottom neo vào `btnBack` (cùng hàng), start=end=parent (căn giữa full-width) | `bg_black_40_rounded` = shape bo tròn radius=20dp, solid `#66171716` | — |
| ⤷ `AppCompatImageView` | `imgMusic` | wrap×wrap, `padding=4dp`, `marginStart=4dp` | src `@drawable/ic_music` | — |
| ⤷ `AppCompatTextView` | `tvNameSong` | wrap×wrap, `maxWidth=96dp`, `marginEnd=8dp`, `ellipsize=marquee`, `singleLine=true` | — | mặc định `"Add song"` (`@string/add_sound`), màu trắng `#ffffffff` |
| ⤷ `AppCompatImageView` (divider) | `vVertical` | 1dp×0dp (match height cha), margin V=4dp | nền trắng, **`visibility=gone` mặc định** | — |
| ⤷ `AppCompatImageView` | `btnRemoveSound` | wrap×wrap, `padding=4dp`, `marginEnd=4dp`, **`visibility=gone` mặc định** | src `@drawable/ic_close` | — |
| `RecordingProgress` (custom, xem mục "Custom view") | `btnRecording` | 80×80dp, `marginBottom=24dp`, căn giữa ngang, bottom neo `bottomSpace` top | vẽ tay (vòng tiến trình + icon play/pause) | — |
| `SnappyRecycleView` (custom RecyclerView) | `rcvTimeRecord` | wrap×wrap, orientation=horizontal, `LinearLayoutManager`; bottom neo top của `btnRecording`, start/end = `btnRecording` (căn giữa ngang) | — | list 3 item (mục List) |
| `AppCompatTextView` | `tvWaitingRecordCountdown` | wrap×wrap, `marginBottom=16dp`, cùng vị trí neo như `rcvTimeRecord` (bottom→top btnRecording, start/end=btnRecording); **`visibility=gone` mặc định** | — | số giây đếm ngược, size=36sp, màu `#ff02bbfa` (`@color/progress_color`), font `lato_black_900` |
| `AppCompatImageView` | `btnFlipCamera` | style `Base.PrimaryButton.Square` (48×48dp) + `padding=4dp`, `marginEnd=8dp`; top/bottom neo `btnBack` (cùng hàng), end=parent → góc trên-phải | src `@drawable/ic_rotation_camera` | — |
| `Space` | `bottomSpace` | fill_parent × 0dp, bottom=parent (đệm cho inset đáy runtime) | vô hình | — |
| `FrameLayout` (AD SLOT) | `nativeCollapsibleContainer` | width=0dp (full qua start/end=parent), height=wrap; bottom neo top `bottomSpace` | — | — |
| ⤷ `View` | `collapseHolderNative` | fill_parent × `@dimen/ad_native_collapsed_height`=256dp | nền `bg_ad_native_media_white` (layer-list: nền trắng + viền 1dp `#ffe4e3e2` phía trên) | — |
| `Group` | `groupFunctions` | tham chiếu `btnAddMusic, btnFlipCamera, rcvTimeRecord, imvNotify` — dùng để ẩn/hiện đồng loạt khi bắt đầu quay | | |

### B. Visibility (từ code)

| View | XML mặc định | Setter runtime | Điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| `tvWaitingRecordCountdown` | gone | `visible()` trong `onStartWaitingRecord`; `gone()` trong `onFinishWaitingRecord` | mỗi lần bấm quay (`RecordingManager.start`) | thoáng qua — xem STATE bên dưới, vì `timeWaiting` luôn = 0 |
| `groupFunctions` (btnAddMusic/btnFlipCamera/rcvTimeRecord/imvNotify) | visible (không đặt gone trong XML) | `ViewExtKt.gone(groupFunctions)` trong `onStartWaitingRecord` — **không có setter nào set lại visible** trong suốt vòng đời fragment (kể cả `onStopRecording`) | ngay khi bấm nút quay | ẨN VĨNH VIỄN sau khi bắt đầu quay lần đầu, cho tới khi rời màn |
| `btnBack` | visible | `setVisibility(INVISIBLE=4)` trong `onStartWaitingRecord`; `setVisibility(VISIBLE=0)` trong `onStopRecording$1` (sau khi quay xong) | như trên | ẨN (giữ chỗ) trong lúc quay, hiện lại khi dừng |
| `btnRemoveSound` | gone | `visibility = soundUI != null ? VISIBLE : GONE` (`observeCurrentSound$2`) | có nhạc nền đang chọn hay không (`FacePuzzleViewModel.currentSound`, mặc định `null`) | GONE mặc định (chưa chọn nhạc) |
| `vVertical` | gone | `visibility = (btnRemoveSound.visibility==VISIBLE) ? VISIBLE : GONE` | theo `btnRemoveSound` | GONE mặc định |
| `nativeCollapsibleContainer` | (không set trong XML, mặc định visible khi có view) | tải ad qua `loadAndShowNativeCollapsibleSafe(AdKey.NATIVE_DETAIL_COLLAP, …)`; sau khi hiển thị, có coroutine `delay(2000ms)` rồi `ViewExtKt.gone(collapseHolderNative)` (`FragmentFacePuzzle$initUi$2`) | luôn chạy khi vào màn | AD SLOT tự thu gọn/ẩn sau 2 giây kể cả nếu ad tải chậm — **placement `native_collapsible_detail`** |

### C. Custom view vẽ tay (onDraw)

**`RecordingProgress`** (`ui/custom_view/RecordingProgress.java`, view gốc `btnRecording`):
- `onDraw`: vẽ icon tròn giữa (bitmap từ `R.drawable.ic_play_filter` lúc chưa quay,
  đổi sang `R.drawable.ic_pause_filter` khi bắt đầu quay/resume) qua `drawIcon()`,
  sau đó vẽ **1 cung tròn tiến trình** (`canvas.drawArc`, `strokeWidth=12px`,
  `Cap.ROUND`, màu `R.color.progress_color`=`#ff02bbfa`) chạy từ -90° (đỉnh) quét
  `360° × progress` — `progress` do `ValueAnimator` 0→1 chạy trong
  `durationSeconds*1000` ms (đặt bằng thời lượng chọn ở `rcvTimeRecord`, mặc định
  item đầu = 15s). Khi animator kết thúc → `AnimationListener.onFinish()` →
  `RecordingManager.stop()` (tự dừng quay khi hết thời lượng).
- API: `startCountdown()`, `pauseRecord()`/`resumeRecord()` (đổi icon + pause/resume
  animator), `resetRecording()`.

**`OverlayView`** (`face_mark/OverlayView.java`, view gốc `overlay`, KHÔNG kế thừa
android/androidx custom view — code app):
- Đây vừa là bề mặt hiển thị camera preview, vừa là canvas vẽ hiệu ứng. Dùng
  MediaPipe `FaceLandmarker` (`results: FaceLandmarkerResult`) để lấy landmark mặt.
- Định nghĩa 6 `ComponentName` (Mouth, LeftEyebrow, RightEyebrow, RightEye, LeftEye,
  Nose), mỗi cái có 1 danh sách index landmark cố định (hardcode trong `static {}`,
  ví dụ `listPosMouth` = 19 điểm, `listPosNose` = 14 điểm…) dùng để cắt path
  (`Path`) vùng đó ra khỏi bitmap khuôn mặt.
- `Mode` (sealed): `FacePuzzle` (mặc định), `FacePop`, `FaceWhirl`, `FaceFunny`
  (dùng ở cụm funny-puzzle khác). `SharedViewModel.overlayViewMode` mặc định =
  `FacePuzzle.INSTANCE`; màn Home set mode này trước khi điều hướng vào theo
  `categoryId` của template: `2→FacePop`, `3→FaceWhirl`, còn lại→`FacePuzzle`.
- `PlayLevel` (dùng `args.level` từ `FragmentFacePuzzleArgs`, set qua
  `setPlaySpeed(level)`):
  | level | PlayLevel | speed (px, dpToPx) | rotationSpeed | scaleSpeed |
  |---|---|---|---|---|
  | 1 | Easy | 4dp | 10.0 | 0.05 |
  | 2 | Intermediate | 10dp | 15.0 | 0.075 |
  | khác (3) | Difficulty | 16dp | 20.0 | 0.1 |
- Vẽ: mỗi component được cắt bằng `componentPaint` (`PorterDuff.SRC_IN`,
  `CornerPathEffect` bo góc 24dp, `BlurMaskFilter` blur 16), rồi vẽ chồng lên
  camera preview tại vị trí lệch động theo thời gian (biên độ theo `PlayLevel`),
  tạo cảm giác "mảnh mặt" trôi nổi quanh khuôn mặt gốc, có xoay + co giãn liên tục
  bằng `Matrix`. `overlayBlur` (mặc định 44) làm mờ nền quanh mặt. Không đọc sâu
  toàn bộ 1496 dòng (thuật toán chi tiết không cần cho Figma), nhưng đủ dữ liệu để
  dựng frame preview: 1 khung camera full-bleed + 4–6 mảnh khuôn mặt nhỏ (hình bo
  góc, có bóng đổ nhẹ do blur) rải rác quanh vị trí khuôn mặt gốc.
- ⚠ CỜ: nội dung camera live + landmark mặt là **runtime placeholder** (ảnh selfie
  người dùng) — không có asset tĩnh để export; dựng preview bằng ảnh mẫu gương mặt
  có nhãn "camera live preview".

### D. Data hardcode

`rcvTimeRecord` — `AdapterTimeRecord` (`ui/face_puzzle/AdapterTimeRecord.java`),
data từ `FacePuzzleViewModel.listTimeRecord` = `AppSettingRepository.getLisTimeRecord()`
→ `AppSetting.listTimeRecord` (`data/system/AppSetting.java:46`), **hardcode trong
code, đúng thứ tự**:
1. `"15s"` (15)
2. `"30s"` (30)
3. `"1m"` (60)

Item mặc định chọn = index 0 (`"15s"`) — `AdapterTimeRecord.updateListData` tự
set `positionSelected=0` và gọi callback đặt `RecordingProgress.durationSeconds=15`
ngay khi list được nạp.

Layout item (`item_time_record.xml`, không thuộc danh sách brief nhưng là
RecyclerView ẩn cần rà theo mục "Hay bị sót"): `LinearLayout` dọc, `gravity=center`,
`margin=4dp` — `tvTime` (text=`timeString`, size 14sp, màu mặc định `white_60`
`#99ffffff`, đổi `white` khi được chọn, padding H=12dp V=4dp) + `imgDot` (chấm
tròn 6×6dp `@drawable/dot_white`, `marginTop=4dp`, **`visibility=invisible` trừ
item đang chọn**).

Ảnh nền chọn level → xem mục Level Picker bên dưới (không thuộc màn này).

### E. Nguồn từng view

| View | Nguồn |
|---|---|
| `img_notify_puzzle` | asset bundled `res/drawable/img_notify_puzzle.webp` (local) |
| `ic_back_2`, `ic_music`, `ic_close`, `ic_rotation_camera`, `ic_play_filter`, `ic_pause_filter`, `dot_white` | vector/drawable local trong `res/drawable/` |
| Camera preview + landmark mặt | **runtime placeholder** (camera trước thiết bị, xử lý on-device qua MediaPipe) |
| Nhạc nền (`tvNameSong`, phát bằng `MediaPlayer`) | `SoundUI` chọn từ màn Sound Picker (cụm khác) — nguồn file nhạc là `raw/*` local, không remote |
| `nativeCollapsibleContainer` | AD SLOT — placement `native_collapsible_detail` (`AdKey.NATIVE_DETAIL_COLLAP`) |
| Video quay xong | ghi vào `context.cacheDir + "/Tmp/" + timestamp + ".mp4"` (file tạm cục bộ), không phải asset |

### F. Nhánh remote-config / A-B

Không có nhánh RC nào rẽ trực tiếp trong `fragment_face_puzzle.xml`/
`FragmentFacePuzzle`. Nhánh RC duy nhất ảnh hưởng tới việc CÓ VÀO được màn này
theo `level` cụ thể nào nằm ở màn trước đó (`FragmentPreviewTemplate` /
`FragmentLevelPicker`, xem mục 1).

### STATE — mỗi state 1 frame

1. **Idle / chuẩn bị quay** (mặc định khi vào màn, sau khi cấp quyền camera):
   camera preview full-bleed, `imvNotify` hiện (badge hướng dẫn), `btnAddMusic`
   hiện dạng pill "Add song", `btnFlipCamera` hiện góc phải, `rcvTimeRecord`
   hiện 3 lựa chọn thời lượng (15s được chọn), `btnRecording` icon play + vòng
   tiến trình = 0%, `btnBack` hiện góc trái, `tvWaitingRecordCountdown` ẩn,
   `nativeCollapsibleContainer` có thể hiện banner ad rồi tự ẩn sau 2s.
2. **Đang quay** (ngay khi bấm `btnRecording`, vì `timeWaiting` luôn truyền 0 nên
   state "waiting" gần như tức thời — không cần dựng frame riêng, có thể note
   annotation): `groupFunctions` ẩn hết (không quay lại được), `btnBack` ẩn (giữ
   chỗ), `btnRecording` đổi icon pause + vòng tiến trình chạy tăng dần theo thời
   lượng đã chọn, hiệu ứng ghép mặt (mảnh mặt bay quanh) chạy động trên camera.
3. **Tạm dừng quay** (bấm lại `btnRecording` giữa chừng): icon đổi lại play, vòng
   tiến trình đứng yên tại vị trí dừng, nhạc nền (nếu có) pause.
4. **Đã chọn nhạc nền**: `btnAddMusic` pill hiện tên bài hát thay vì "Add song",
   `vVertical` + `btnRemoveSound` (icon X) hiện thêm ở cuối pill.
5. **Quay xong** (vòng tiến trình đạt 100% tự động HOẶC bấm dừng thủ công):
   `btnBack` hiện lại, phát interstitial ad (`inter_record`), rồi điều hướng sang
   `FragmentPreviewWithMusic` (cụm khác) mang theo file video + `SoundUI` hiện tại
   — không có frame "kết thúc" ở lại trong chính màn này.
6. **Chưa cấp quyền camera/mic**: màn gọi `requireCameraPermission()` ngay khi vào
   (`initUi$1`); nếu người dùng từ chối quyền CAMERA → toast
   "you_need_permission_to_use_this_feature" + `popBackStack()` (thoát khỏi màn
   ngay, không có UI riêng) — đây là **UI hệ điều hành (placeholder có nhãn)**,
   không dựng trong Figma.

---

## 3. Màn `fragment_level_picker.xml` — Chọn level

Fragment: `ui/level/FragmentLevelPicker.java`. Không có ViewModel riêng (chỉ dùng
`NavArgsLazy` + `CemViewModel`/`SharedViewModel` kế thừa từ `BaseFragment`).

### A. Geometry (`layout/fragment_level_picker.xml`)

Root: `ConstraintLayout` fill×fill (360×800dp).

| View | id | Kích thước / vị trí | Nền / style | Text |
|---|---|---|---|---|
| `AppCompatImageView` | `btnBack` | style `BackImageButton1` → 48×48dp, `padding=8dp`, `layout_margin=12dp`; góc trên-trái | icon `@drawable/ic_back_1` (khác icon back của màn face_puzzle: `ic_back_1` vs `ic_back_2`) | — |
| `AppCompatTextView` | `appCompatTextView` | style `ScreenTitleCommon`: wrap×wrap, `gravity=center`, `singleLine`, font `lato_bold_700`; top/bottom neo `btnBack`, start/end=parent (căn giữa ngang, cùng hàng `btnBack`) | — | `"Select level"` (`@string/select_level`), size 20sp, màu `#ff171716` (`text_primary_color`) |
| `ScrollView` | (không id) | fill × 0dp, `marginTop=8dp` `marginBottom=8dp`; top neo `btnBack`, bottom neo `nativeCollapsibleContainer` | — | — |
| ⤷ `LinearLayout` dọc | (không id) | fill×wrap, `paddingHorizontal=20dp` | — | — |
| ⤷⤷ `AppCompatImageView` | `btnLevelEasy` | fill_parent × wrap, `marginTop=16dp`, `adjustViewBounds=true`, bo góc runtime 16dp (`ViewExtKt.setRadiusPx`, `R.dimen.size_16`) | ảnh `R.mipmap.bg_level_easy` qua Glide | — |
| ⤷⤷ `AppCompatImageView` | `btnLevelIntermediate` | như trên | `R.mipmap.bg_level_intermediate` | — |
| ⤷⤷ `AppCompatImageView` | `btnLevelDifficulty` | như trên | `R.mipmap.bg_level_difficulty` | — |
| ⤷⤷ `FrameLayout` (AD SLOT) | `adNativeView` | fill × wrap, `marginTop=16dp` | native ad view | — |
| `FrameLayout` (AD SLOT) | `nativeCollapsibleContainer` | width=0dp (full), wrap height; **`visibility=gone` mặc định trong XML** | | |
| ⤷ `View` | `collapseHolderNative` | fill × 256dp (`ad_native_collapsed_height`) | `bg_ad_native_media_white` | — |

### B. Visibility

| View | XML mặc định | Setter runtime | KẾT QUẢ |
|---|---|---|---|
| `nativeCollapsibleContainer` | gone | không thấy code nào set visible trong `FragmentLevelPicker.java` đã đọc (chỉ có `adNativeView` trong ScrollView được nạp ad qua `loadAndShowAds()`/`AdKey.NATIVE_LEVEL`) | **GONE cố định** trên màn này — container này là dead code còn sót trong layout, không hoạt động |
| `btnBack` | visible, `enabled=true` | `setEnabled(false)` khi bấm (chặn double-tap) rồi `popBackStack()` | — |
| `btnLevelEasy/Intermediate/Difficulty` | visible, `enabled=true` | `setEnabled(false)` ngay khi bấm (trong lúc chờ tải ad `native_fullscreen_level`), enable lại nếu lỗi | — |

### C. Custom view onDraw

Không có custom view vẽ tay trong màn này — 3 ảnh level là bitmap tĩnh (mipmap),
chỉ bo góc runtime bằng `ViewExtKt.setRadiusPx` (clip, không phải vẽ tay).

### D. Data hardcode — 3 level, đúng thứ tự trên xuống dưới

| # | id view | Tên (không có text hiển thị, chỉ ảnh) | Ảnh (mipmap) | level truyền đi | Khoá? |
|---|---|---|---|---|---|
| 1 | `btnLevelEasy` | Easy | `mipmap/bg_level_easy` (có ở hdpi/xhdpi/xxhdpi) | 1 | Không |
| 2 | `btnLevelIntermediate` | Intermediate | `mipmap/bg_level_intermediate` | 2 | Không |
| 3 | `btnLevelDifficulty` | Difficulty | `mipmap/bg_level_difficulty` | 3 | Không |

**Không có level nào bị khoá** (không tìm thấy cờ `isPro`/`isLocked` nào áp cho 3
nút này trong `FragmentLevelPicker.java`) — cả 3 đều bấm được ngay, chỉ chờ tải 1
quảng cáo fullscreen (`native_fullscreen_level`, preload=true) trước khi điều
hướng (không chặn nếu ad lỗi/timeout — logic `setOnClickLoadShowAd` bọc try/catch).

Ảnh mipmap chỉ có 3 mật độ (hdpi/xhdpi/xxhdpi), KHÔNG có mdpi/xxxhdpi — dùng bản
xhdpi hoặc xxhdpi làm nguồn export cho Figma.

### E. Nguồn từng view

Tất cả local: mipmap bundled trong APK. `adNativeView`/`collapseHolderNative` là
AD SLOT (placement `native_fullscreen_level` cho hành động bấm level,
`native_level` cho banner tĩnh trong ScrollView).

### F. Nhánh remote-config / A-B

Bản thân layout này không rẽ nhánh RC. Nhánh RC (`level_picker_skipped`) chỉ quyết
định MÀN NÀY CÓ ĐƯỢC ĐIỀU HƯỚNG TỚI hay không (xem mục 1) — dựng frame này vẫn
đúng vì nhánh mặc định = hiển thị.

### STATE

1. **Mặc định (duy nhất 1 state tĩnh)**: 3 ảnh level xếp dọc, đầy đủ, không có
   ổ khóa, banner ad tĩnh dưới cùng trong ScrollView (có thể có hoặc không tuỳ
   tải ad thành công). Không có state rỗng/loading/lỗi vì dữ liệu 3 level là
   hardcode, không phụ thuộc network.
2. **Đang chờ ad fullscreen sau khi bấm 1 level**: nút vừa bấm `enabled=false`
   trong thời gian ngắn (không có chỉ báo loading riêng trong XML) rồi điều
   hướng sang `fragment_face_puzzle` (nếu `funnyPuzzleTemplate==null`) mang theo
   `level` tương ứng.

---

## 4. Item list `item_face_puzzle_template.xml` + `item_face_puzzle_ad.xml`
(render trên màn Home, ĐÍNH KÈM theo yêu cầu brief — không phải RecyclerView của
`fragment_face_puzzle.xml`/`fragment_level_picker.xml`)

Adapter: `ui/home/AdapterFacePuzzleTemplate.java` (package `ui.home`). Item model:
`ui/home/FacePuzzleItem.java` (sealed: `ContentItem(content: FacePuzzleTemplateUI)`
| `AdItem`).

### A. Geometry

**`item_face_puzzle_template.xml`** — `ConstraintLayout`, `padding=10dp`,
fill_parent × wrap_content:
- `ImageView imvThumbVideo`: fill × 0dp, tỉ lệ khoá `158:224` (~0.706 — dọc,
  gần 9:16), `scaleType=centerCrop`, bo góc runtime 16dp
  (`ViewExtKt.setRadiusPx`, `R.dimen.size_16`, set trong `onAttachedToRecyclerView`).
  Ảnh nạp bằng Glide từ `content.thumbUrl` (REMOTE).
- `TextView tvUserCount`: wrap×wrap, `margin=8dp`, góc trên-phải
  (`constraintEnd_toEndOf=parent`, `constraintTop_toTopOf=parent`),
  `paddingHorizontal=12dp` `paddingVertical=4dp`, nền `bg_primary_rounded_enabled`
  nhưng bị `backgroundTint="#66171716"` đè màu → **pill đen mờ 40%**, bo góc
  `size_48`=48dp (viên thuốc hoàn chỉnh vì cao < 48dp), text màu trắng, nội dung
  = `content.useViewCounter` (chuỗi REMOTE, vd lượt xem dạng "12.3K").

**`item_face_puzzle_ad.xml`** — `ConstraintLayout` fill×wrap chỉ chứa 1
`FrameLayout adNativeView` fill×wrap `margin=8dp` (AD SLOT, span 2 cột trong
grid — xem mục C).

### B. Visibility

Không có view ẩn/hiện có điều kiện trong 2 layout item — toàn bộ view luôn hiện
khi item được bind (trừ `isAdLoaded` cờ nội bộ chặn bind ad 2 lần,
`AdapterFacePuzzleTemplate.java:135-138`).

### C. List — cách ghép đúng số lượng/thứ tự

`GridLayoutManager(context, spanCount=2)` (`AdapterTemplateCategory.java:309`).
`AdapterFacePuzzleTemplate.getSpanSizeLookup()`: item content (`viewType=0`) span
1 cột, item ad (`viewType=1`) span **2 cột** (full width).

**SỬA (round 1, đã phân xử bởi coordinator — finding trước SAI):** ban đầu spec
ghi "`FragmentHome`/`FragmentTabHome` mặc định `showAdsInList=true` → luôn chèn
ad" — SAI. Đọc lại đúng call-site: `FragmentHome.java:292` kết thúc lời gọi
constructor bằng `}, false);` — đối số thứ 3 (`showAdsInList`) truyền **TƯỜNG
MINH = `false`**, không dùng constructor rút gọn/default. `FragmentTabHome.java`
gọi tương tự nhưng **`FragmentTabHome` không xuất hiện trong `main_nav.xml`**
(0 destination/action nào tham chiếu nó — chỉ có `FragmentHome` id=`fragmentHome`
và `FragmentHomeOldUI` id=`fragmentHomeOldUI`, cả 2 đều trong nav graph thật) ⇒
`FragmentTabHome` là **dead code**, không tính.

⇒ Cả 2 destination Home thật sự tồn tại trong nav graph đều KHÔNG chèn ad vào
lưới Face Puzzle:
1. **`FragmentHomeOldUI`** (`observeHomeData$addFacePuzzleTemplate`,
   dòng 211-234): map THẲNG mỗi phần tử data → `FacePuzzleItem.ContentItem`,
   không gọi `createFacePuzzleItems` → không có đường chèn `AdItem`.
2. **`FragmentHome`** (`AdapterTemplateCategory.createFacePuzzleAdapter` →
   `createFacePuzzleItems(rawData, showAds)`, `AdapterTemplateCategory.java:236-246`):
   ```
   items = rawData.map { ContentItem(it) }
   if (showAds && items.size >= 2) items.add(index=2, AdItem)
   ```
   nhưng `showAds = showAdsInList = false` (truyền từ `FragmentHome.java:292`)
   ⇒ điều kiện `showAds && …` luôn `false` ⇒ **KHÔNG BAO GIỜ chèn `AdItem`** ở
   luồng mặc định.

**KẾT LUẬN: `item_face_puzzle_ad.xml` KHÔNG XUẤT HIỆN trong bản dựng mặc định**
của lưới Face Puzzle trên Home (dù ở bất kỳ destination Home nào trong nav graph
thật). Code chèn ad (`createFacePuzzleItems`, index cố định = 2, span 2 cột) vẫn
tồn tại và đúng về mặt logic nếu `showAdsInList=true` được truyền vào (chỉ
`FragmentTabHome` dead-code làm vậy) — giữ lại mô tả layout + logic index=2 trong
tài liệu này để tham khảo, nhưng gắn nhãn **"unused in default flow"**: KHÔNG dựng
frame có ô ad cho lưới Face Puzzle của Home trong Figma trừ khi có yêu cầu dựng
riêng nhánh dead-code.

Layout ô ad (nếu được bật): `AdKey` không có hằng số riêng cho vị trí này trong
code đã đọc — `showAds: Function1<FrameLayout, Unit>` được `AdapterTemplateCategory`
truyền xuống, gọi `listener.showAds(frameLayout)` (không lộ placement key cụ thể
trong phạm vi file đã đọc).

### D. Data hardcode

Không có data hardcode — toàn bộ template + `useViewCounter` đến từ REMOTE JSON
(mục E). Chỉ có `AdapterFacePuzzleTemplate` insert **đúng 1** `AdItem` tại index
cố định = 2 (không phải data).

### E. Nguồn — remote CDN, KHÔNG phải `assets/face_funny/*`

`FacePuzzleTemplateUI(id, categoryId, folderName, useViewCounter, url, thumbUrl)`
— lấy qua `SharedViewModel.listFacePuzzleTemplateUI` /
`listFacePuzzleTemplateUIV2` → `DataRemoteRepositoryImpl.getFacePuzzleTemplates()`
/ `getFacePuzzleTemplatesV2()` → `RemoteFacePuzzleService` (Retrofit):

```
@GET("FacePuzzle/ios_data_facepuzzle.json")     // v1, flat list CategoryEntity
@GET("FacePuzzle/ios_data_facepuzzle_v2.json")  // v2, group theo CategoryEntityV2
```
Base URL (`com/cem/data/BuildConfig.java`):
`https://wallpaperhd.nyc3.cdn.digitaloceanspaces.com/`

⇒ URL đầy đủ:
`https://wallpaperhd.nyc3.cdn.digitaloceanspaces.com/FacePuzzle/ios_data_facepuzzle.json`
và bản `_v2.json`. **KHÔNG PHẢI Room DB, KHÔNG PHẢI asset bundled trong APK** —
đây là JSON tải runtime từ CDN DigitalOcean Spaces (không phải Firebase RC, không
phải Firestore). `thumbUrl` trong mỗi entry cũng là URL remote (ảnh thumbnail tải
qua Glide).

**Endpoint nào được dùng ở đâu — đã verify qua code, không đoán:**
`FragmentHome.java:318` gọi `getSharedViewModel().getDataHomepageV2()` (dùng
**v2**, `ios_data_facepuzzle_v2.json`) — đây là destination Home mặc định trong
nav graph thật. `FragmentHomeOldUI.java:205` gọi
`getSharedViewModel().getDataHomepage()` (dùng **v1**, `ios_data_facepuzzle.json`)
— destination Home thay thế (`fragmentHomeOldUI`), cũng có trong nav graph, chọn
qua `actionSplashToHomeOldUI`. Cả 2 destination đều thật; không xác định được
tĩnh trong phạm vi agent này Home nào đang active theo `ui_home_show_case` (thuộc
cụm "home", không đọc ở đây) — dựng cả 2 tập dữ liệu là an toàn.

**SỬA (round 1) — cờ "không đếm được số lượng" nay ĐÃ RESOLVE bằng fetch endpoint
thật** (coordinator đã tải, snapshot tại thời điểm fetch — server có thể đổi sau):

*v2 (`ios_data_facepuzzle_v2.json`, dùng bởi `FragmentHome`)* — 3 category × 6
video = **18 template**:

| categoryId | Tên category | folder | video id | ví dụ likes |
|---|---|---|---|---|
| 1 | Face Puzzle | `Face_Puzzle` | Video1..Video6 | Video1=273300, Video2=716845 |
| 2 | Face Pop | `Face_Pop` | Video1..Video6 | — |
| 3 | Whirl Face | `Whirl_Face` | Video1..Video6 | — |

*v1 (`ios_data_facepuzzle.json`, dùng bởi `FragmentHomeOldUI`)* — 1 category
"Face Puzzle" × **8 video** (Video1..Video8), có field `thumbnail` riêng (khác
cơ chế suy ra URL của v2).

Nhãn `useViewCounter` = `round(likes/1000.0f, 1) + "k uses"` (`MapperKt.java`
dòng 77 cho v1, dòng 85 cho v2) — vd `likes=273300` → `"273.3k uses"`.

URL thumbnail v2 (`MapperKt.java:80-90`):
`https://wallpaperhd.nyc3.cdn.digitaloceanspaces.com/FacePuzzle/<folderPrefix>Thumb/<id>.png`,
với `folderPrefix = ""` khi `folder=="Face_Puzzle"`, ngược lại
`folderPrefix = "<folder>/"` — vd category "Face Pop" → `.../FacePuzzle/Face_Pop/Thumb/Video1.png`,
riêng category "Face Puzzle" → `.../FacePuzzle/Thumb/Video1.png` (không có
`Face_Puzzle/` ở giữa). URL v1 dùng thẳng field `thumbnail` từ JSON
(`.../FacePuzzle/Thumb/<thumbnail>`).

Đủ 18 thumbnail thật (v2) đã được tải về
`assets/v1/30-template-v2/<folder>_<id>.png` (576×1024) để dùng làm ảnh thật khi
dựng Figma — không cần placeholder cho nhánh v2 nữa. Nhánh v1 (8 video) chưa có
ảnh tải sẵn trong repo này — nếu cần dựng đủ, gắn cờ fetch bổ sung.

`categoryId` field quyết định `OverlayView.Mode` khi vào màn quay (mục 2 phần
Custom view): `2→FacePop`, `3→FaceWhirl`, còn lại (mặc định, kể cả 1)→`FacePuzzle`
— khớp đúng 3 category `Face Puzzle`/`Face Pop`/`Whirl Face` ở trên.

### F. Nhánh remote-config / A-B

`showAdsInList` không đọc field RC nào — là hardcode truyền trực tiếp tại
call-site. `FragmentHome.java:292` truyền tường minh `false`; `FragmentHomeOldUI`
không dùng cờ này (đường code khác, không có bước chèn ad). ⇒ **cả 2 destination
Home thật trong nav graph đều KHÔNG chèn ad** vào lưới Face Puzzle ở luồng mặc
định (xem mục C).

### STATE

1. **Có dữ liệu (18 template, 3 category)** — nhánh `FragmentHome`/v2: grid 2
   cột liên tục 18 item, KHÔNG có ô ad (`showAdsInList=false`).
2. **Có dữ liệu (8 template, 1 category)** — nhánh `FragmentHomeOldUI`/v1: grid
   2 cột liên tục 8 item, KHÔNG có ô ad.
3. **Rỗng / đang tải**: không có empty-state UI riêng trong 2 layout item này —
   RecyclerView đơn giản không có item nào; empty-state (nếu có) thuộc phạm vi
   layout `fragment_home*.xml` (cụm home, không đọc ở đây).
4. **(Dead-code, không dựng)**: nếu `showAdsInList=true` (chỉ xảy ra ở
   `FragmentTabHome`, không có trong nav graph) → ô ad chèn tại index=2, span 2
   cột. Giữ lại để tham khảo, không tạo frame Figma riêng.

---

## 5. Bảng cờ tổng hợp (không bịa số/asset)

| Cờ | Ý nghĩa | Vị trí |
|---|---|---|
| RUNTIME PLACEHOLDER | camera preview + landmark mặt live trong `OverlayView` | `fragment_face_puzzle.xml` |
| RUNTIME/REMOTE (đã resolve số lượng — round 1) | 18 thumbnail template v2 (3 category × 6, ảnh thật đã tải về `assets/v1/30-template-v2/`) + 8 template v1 (chưa có ảnh tải sẵn) | `item_face_puzzle_template.xml` |
| AD SLOT `native_collapsible_detail` | banner native tự thu gọn sau 2s | `fragment_face_puzzle.xml` → `nativeCollapsibleContainer` |
| AD SLOT `inter_record` | interstitial khi quay xong, trước khi sang preview | code (`FragmentFacePuzzle$onStopRecording$1`) |
| AD SLOT `native_fullscreen_level` | fullscreen ad khi bấm chọn 1 level | `fragment_level_picker.xml` (không có view riêng — full-screen overlay do SDK ads vẽ) |
| AD SLOT `native_level` | banner native tĩnh cuối ScrollView | `fragment_level_picker.xml` → `adNativeView` |
| UNUSED IN DEFAULT FLOW (round 1 — đã sửa, trước ghi sai "mặc định chèn ad") | `item_face_puzzle_ad.xml` — `showAdsInList=false` ở cả 2 destination Home thật (`FragmentHome` truyền `false` tường minh; `FragmentHomeOldUI` không có đường chèn); chỉ bật ở `FragmentTabHome` dead-code (0 hit `main_nav.xml`) | `item_face_puzzle_ad.xml` |
| ĐÃ VERIFY KHỚP RC | `level_picker_skipped` (key + default `false` + hành vi rẽ nhánh) | `ConfigKey.LEVEL_PICKER_SKIPPED`, `FragmentPreviewTemplate.levelPicker()` |

Font dùng trong cụm: `lato_black_900` (đếm ngược), `lato_bold_700` (tiêu đề
"Select level") — cả 2 đều có sẵn trong `res/font/`, là Google Fonts (Lato) theo
ghi nhận Phase 1 của ledger.
