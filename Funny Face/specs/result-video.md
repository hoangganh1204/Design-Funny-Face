# Cụm: result-video — Kết quả · Phát video · Thư viện video đã lưu

Nguồn đọc trọn: `FragmentResult.java` (+5 inner lambda class), `FragmentPlayVideo.java`,
`FragmentVideoGallery.java`, `FragmentTabGallery.java`, `AdapterMyVideo.java`,
`VideoGalleryViewModel.java`, `DatabaseRepositoryImpl.java` (+`getAllMyVideos$1`),
`PopupUtilsKt.java`, `FileUtilsKt.java`, `ContextExtKt.java` (rateMyApp/showAppReview),
`RecordingManagerImpl.java`, `SurfaceMediaRecorder.java`, `main_nav.xml`.
Layout raw XML đọc trực tiếp (resolve-layout.py không tính x/y cho ConstraintLayout nên
geometry dưới đây ghi bằng **quan hệ constraint + margin thật**, không bịa số px).

Canvas 360×800dp (sdp==dp).

---

## 0. Pipeline & điều hướng (bối cảnh bắt buộc phải biết trước khi dựng UI)

```
FragmentPreviewWithMusic --actionPreviewWithMusicToResult--> FragmentResult(pathVideoResult)
                                                                 │ imvThumbVideo tap
                                                                 ▼
                                                          FragmentPlayVideo(path, canDelete=false)

FragmentHome --actionHomeToVideoGallery--> FragmentVideoGallery
                                                 │ item tap
                                                 ▼
                                          FragmentPlayVideo(path, canDelete=true)

[FragmentTabGallery — KHÔNG có đường điều hướng thật tới, xem mục I]
```
(nav args: `main_nav.xml` dòng 30-40 — `fragmentResult{pathVideoResult:string}`,
`fragmentPlayVideo{pathVideo:string, canDelete:boolean}`, `fragmentVideoGallery` không có arg)

**Nguồn video kết quả**: `RecordingManagerImpl.java` — quay bằng `ViewRecorder`/`SurfaceMediaRecorder`
ghi trực tiếp canvas của `OverlayView` (camera + overlay mặt đã compose sẵn trong màn quay,
KHÔNG thuộc cụm này). Thông số ghi cứng trong `prepare()`:
- `setVideoSize(widthSupport, heightSupport)` — mặc định **1080×1920** (portrait), auto-dò theo
  `CameraCharacteristics` nếu tìm được size gần `screenHeight` hơn; fallback về 1080×1920 khi lỗi.
- `VIDEO_FRAME_RATE = 26` fps.
- `setVideoEncodingBitRate(5242880)` (~5 Mbps), `setOutputFormat(MPEG_4)`, `setVideoEncoder(H264)`,
  `setAudioEncoder(AAC)` chỉ khi có quyền `RECORD_AUDIO`.
- File output: `<cache>/.../<tên>.mp4` (xoá cả thư mục cha khi prepare lại hoặc khi rời Result).
- **KHÔNG có watermark/logo chèn ở tầng encode** trong 2 file này — nếu có watermark thì nó được
  vẽ trực tiếp lên `OverlayView` ở màn quay (ngoài cụm result-video, cần audit riêng nếu cần).
- Thời lượng video: do màn quay (đếm giờ) quyết định — `item_time_record.xml` (xem mục F) thuộc
  `ui/face_puzzle/AdapterTimeRecord`, KHÔNG thuộc 3 fragment của cụm này.

**Thư mục lưu / thư viện**: KHÔNG phải Room DB dù tên `DatabaseRepository`. Truy nguồn đầy đủ
file:dòng cho cả 2 chiều (đọc list + ghi file khi Save):

- Interface: `com/cem/domain/repository/DatabaseRepository.java:17` —
  `Flow<List<String>> getAllMyVideos(String rootFolderName)`.
- Impl gọi flow: `com/cem/data/repository/DatabaseRepositoryImpl.java:46-48` —
  `getAllMyVideos(rootFolderName) { return FlowKt.flow(new DatabaseRepositoryImpl$getAllMyVideos$1(this, rootFolderName, null)); }`.
- Thân flow (nơi thực sự quét đĩa) —
  `com/cem/data/repository/DatabaseRepositoryImpl$getAllMyVideos$1.java`:
  dòng 108 `Environment.DIRECTORY_DOWNLOADS`, dòng 111 ghép `rootFolderName` thành
  `new File(downloadsDir, rootFolderName)`, dòng 113 `File[] listFiles = dir.listFiles()`,
  dòng 132-133 lọc `kotlin.io.FilesKt.getExtension(f) == "mp4"` (bỏ thư mục con) rồi add
  `absolutePath` vào `listAllMyVideos` (biến cache in-memory, khai ở
  `DatabaseRepositoryImpl.java:19`). **Không có `MediaStore.query`, không có Room DAO/Entity nào
  trong file này** — xác nhận đây là scan filesystem thuần qua `java.io.File.listFiles()`.
  Sort giảm dần qua `DatabaseRepositoryImpl$getAllMyVideos$1$invokeSuspend$$inlined$sortByDescending$1`
  (dòng 117-120 gọi `ArraysKt.sortWith`) — nội dung comparator không đọc được do JADX decompile lỗi
  phần thân (xem cờ M.5), chỉ chắc chắn là **giảm dần**.
- `rootFolderName` truyền vào từ `ui/video_gallery/VideoGalleryViewModel.java:26-27` —
  `context.getString(R.string.folder_name_my_library)` → `values/strings.xml:242` =
  **"CemFacePuzzle"**.
- Chiều ghi (khi bấm Save ở Result, mục D.3): `utils/FileUtilsKt.java` —
  `createFileDownload()` dòng 66-70: `context.getString(R.string.folder_name_my_library)`
  (cùng string `values/strings.xml:242` = "CemFacePuzzle") ghép với
  `Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)` →
  `createFileInDirectory()` dòng 77-95 tạo file `.mp4` trong thư mục đó. Vậy đường ghi và đường đọc
  **dùng chung 1 thư mục vật lý** `Downloads/CemFacePuzzle/`, chỉ khác cơ chế (ghi = tạo file trực
  tiếp; đọc = quét lại thư mục đó mỗi lần `getAllMyVideos` được collect lần đầu).

→ **Không có trạng thái "loading" xoay/skeleton** trong code — `Flow` emit ngay list rỗng hoặc có
sẵn trong cùng 1 lần collect, nên UI luôn nhảy thẳng rỗng↔có-N mà không có spinner riêng.
→ **Không có trạng thái lỗi** được xử lý (không try/catch hiển thị lỗi ra UI) — mọi exception khi
liệt kê file coi như rỗng.

**Rating / In-App Review** — đã kiểm code: `showAppReview()` (ContextExtKt, dùng
`com.google.android.play.core.review.ReviewManager` — In-App Review API thật của Google) và
`rateMyApp()` (mở Play Store) **chỉ được gọi từ `FragmentHome`/`FragmentHomeOldUI`**
(`grep showAppReview(` → 2 chỗ, cả hai ở `ui/home/`). **Không có lời gọi rating nào trong
FragmentResult / FragmentPlayVideo / FragmentVideoGallery / FragmentTabGallery.** Vậy cụm
result-video KHÔNG có popup rating 5-sao / feedback-in-app nào cả — đây là điểm khác với cảnh báo
"Plan 1" trong brief, đã verify bằng code, không bịa dialog rating cho cụm này.

---

## A. FragmentResult — `fragment_result.xml`

Root: `ConstraintLayout` fill_parent × fill_parent, nền theo theme (không set riêng).

| # | View | id | Vai trò | Constraint / vị trí | Size | Style/nền | Margin |
|---|------|----|---------|---------------------|------|-----------|--------|
| 1 | AppCompatImageView | `btnBack` | Nút back | top/start parent | 48×48dp (`Base.PrimaryButton.Square`) | `ic_home` (icon "home", KHÔNG phải mũi tên back!), ripple borderless | padding 8dp + margin 12dp (`BackImageButton1`) |
| 2 | AppCompatTextView | `appCompatTextView` | Tiêu đề màn | center ngang parent, top/bottom = btnBack | wrap | text **"Result"** (`@string/result`) · 20sp · `#ff171716` (`text_primary_color`) · center · `ScreenTitleCommon` | — |
| 3 | AppCompatImageView | `btnShare` | Nút share | end parent, top/bottom = btnBack | 48×48dp | `ic_share`, `Base.PrimaryButton.Square` | marginEnd 8dp |
| 4 | AppCompatImageView | `imvThumbVideo` | **Thumbnail video kết quả — RUNTIME PLACEHOLDER** | full width (0dp), top = btnBack, bottom = btnSave | height=0dp, ratio khoá **1080:1920** (dọc) | `scaleType=fitXY`, bo góc runtime = `R.dimen.size_12` (set code `ViewExtKt.setRadiusPx`, KHÔNG có trong XML) | marginTop/Bottom 16dp |
| 5 | AppCompatImageView | (no id) | Icon play overlay giữa thumbnail | center trong imvThumbVideo (4 cạnh) | 64×64dp | `ic_play_music`, tint `#ff016cf7` (`primary_color`) | — |
| 6 | LinearLayout | `btnSave` | Nút Save | bottom parent, end parent (không start — width=fill_parent) | height 58dp, width fill_parent | `bg_primary_rounded`, gravity center horizontal | margin 16dp mọi cạnh |
| 6a | ⌙ AppCompatImageView | (no id) | icon trong Save | wrap | `ic_record` | marginStart mặc định (0) |
| 6b | ⌙ AppCompatTextView | (no id) | label Save | wrap | text **"Save"** (`@string/save`) · 16sp · `fontFamily=@font/lato_bold_700` · color `@color/button_primary_text_color` — **ColorStateList** `res/color/button_primary_text_color.xml`: `state_enabled=false → @color/text_secondary_color = #ff999894`, else `→ @color/text_primary_color = #ff171716` (`values/colors.xml:497-498`). `btnSave` không tự disable nên state thực tế luôn **enabled → #171716**; state disabled (#999894) chỉ áp dụng lý thuyết nếu nút này từng bị `setEnabled(false)` (không xảy ra trong code đọc được cho label Save) | marginStart 8dp |
| 7 | FrameLayout | `nativeCollapsibleContainer` | **AD SLOT** — container native ad collapsible | full width (0dp), bottom/start/end parent, **không có top constraint** → height=wrap_content, chồng lên vùng dưới cùng | — | — | — |
| 7a | ⌙ View | `collapseHolderNative` | placeholder/skeleton nền trong lúc chờ ad | fill_parent × `@dimen/ad_native_collapsed_height` = 256dp | `bg_ad_native_media_white` | — |

**Ghi chú vị trí 6 vs 7**: cả `btnSave` và `nativeCollapsibleContainer` đều neo `bottom_toBottomOf
parent`; `btnSave` khai trước trong XML nên `nativeCollapsibleContainer` (ad) vẽ **đè lên trên** về
z-order khi ad load xong (thực tế ad native collapsible này thường trồi lên phía trên nút Save khi
xuất hiện — cần verify trực quan trong app thật vì ConstraintLayout không tự tránh chồng lấn; ghi
CỜ vị trí ad runtime).

### B. Visibility (từ code)

| View | XML mặc định | Runtime setter | Điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| `collapseHolderNative` | visible (không set) | `ViewExtKt.gone(view)` trong `FragmentResult$initUi$1.AnonymousClass1`, chạy trong `repeatOnLifecycle(STARTED)` sau `delay(2000L)` | Luôn chạy 2s sau khi vào màn, lặp lại mỗi lần STARTED | **GONE sau 2 giây** kể cả ad đã load hay chưa — dựng 2 frame: t=0 (skeleton hiện) và t≥2s (skeleton ẩn, ad thật hoặc trống nếu ad fail) |
| `nativeCollapsibleContainer` nội dung | rỗng | `NativeManager.presentCollapsible(...)` trong `loadAndShowNativeCollapsibleSafe` (gọi từ `loadAndShowAds()`, chạy song song `initUi()`) | Cần fragment `isAdded`, activity chưa finish/destroy, view `isAttachedToWindow`, lifecycle ≥ STARTED | Có thể **có native ad** hoặc **trống hẳn** (ẩn `viewGroup.setVisibility(GONE)` nếu load fail — trong callback `onFailFullScreen`-style function0) |
| `btnSave` | enabled | `fragmentResultBinding.btnSave.setEnabled(false)` trong `initListener$1$4$1` SAU khi hiện xong interstitial `INTER_SAVE` | Khi user bấm Save | Nút Save **disable** trong lúc xin quyền lưu / copy file (chống double-tap) |
| `btnDelete` (PlayVideo, không phải Result) | N/A ở đây | — | — | — |

### C. Data / hardcode

- Text hardcode: "Result" (`@string/result`), "Save" (`@string/save`).
- Không có list nào trong FragmentResult.

### D. Interaction chi tiết

1. **btnBack** & hệ thống back (OnBackPressedCallback) → `handleCloseScreen()`:
   `loadShowFullscreenSafe(AdKey.NATIVE_FULL_SAVE, ...)` **[AD SLOT — full-screen native,
   placement "native_fullscreen_save"]** → trong callback: xoá đệ quy thư mục cha của
   `pathVideoResult` (video kết quả **bị xoá nếu người dùng KHÔNG bấm Save trước khi back**) →
   `popBackStack()`.
2. **btnShare** → `FileUtilsKt.shareVideoFile()` — **placeholder có nhãn: Android Share Sheet
   (`Intent.ACTION_SEND`, type "video/mp4", FileProvider `com.filter.face.puzzle.fileProvider`,
   chooser title "Share file via")**.
3. **btnSave** → coroutine: hiện interstitial **[AD SLOT — inter, placement "inter_save"]** qua
   `FullscreenManager.present(..., AdKey.INTER_SAVE, ...)` → disable btnSave → xin quyền
   `WRITE_EXTERNAL_STORAGE`/scoped storage (`launcherRequireStorage`, **placeholder có nhãn: hệ
   thống permission dialog**) → nếu cấp quyền: copy file từ cache sang
   `Downloads/CemFacePuzzle/<timestamp>.mp4` (`createFileInDirectory`+`copyFile`), scan MediaStore,
   toast **"Save success"**, gọi `sharedViewModel.saveMyVideo(path)` (thêm vào cache in-memory của
   thư viện), rồi luôn `popBackStack()` (kể cả lỗi, trong `finally`).
4. **imvThumbVideo tap** → `actionResultToPlayVideo(pathVideoResult, canDelete=false)` — mở
   PlayVideo xem trước, **không cho xoá** vì video chưa được Save chính thức.
5. Không có nút "Home"/"Again" riêng biệt trong layout — `btnBack` đóng vai trò cả hai (icon dùng
   `ic_home`, hành vi là "đóng & xoá file tạm rồi back").

---

## E. FragmentPlayVideo — `fragment_play_video.xml`

Root: `ConstraintLayout` fill_parent × fill_parent, nền đen ngầm định (ExoPlayer full-bleed).

| # | View | id | Vai trò | Constraint | Size | Nền/màu | Margin |
|---|------|----|---------|-----------|------|---------|--------|
| 1 | `androidx.media3.ui.PlayerView` | `exoPlayerView` | **Player video — RUNTIME PLACEHOLDER** (ExoPlayer, `resize_mode=fill`, `use_controller=true` → có control bar mặc định của ExoPlayer) | phủ toàn màn (0dp mọi cạnh = parent) | fill | đen | — |
| 2 | AppCompatImageView | `btnBack` | back | top/start parent (`updateMarginForView` set thêm margin runtime theo status bar/notch) | 48×48dp | `ic_back_1`, tint `@color/white` | margin runtime |
| 3 | TextView | `textView` | tiêu đề | center ngang, top/bottom=btnBack | wrap | text **"Preview"** (`@string/preview`) · trắng · `ScreenTitleCommon` | — |
| 4 | AppCompatImageView | `btnShare` | share | end_toStartOf btnDelete, top/bottom=btnBack | 48×48dp | `ic_share`, tint trắng | — |
| 5 | AppCompatImageView | `btnDelete` | xoá video | end_toStartOf endSpace, top/bottom=btnBack | 48×48dp | `ic_delete` | — |
| 6 | Space | `endSpace` | đệm lề phải | top/end parent | width=8dp | — | — |

### F. Visibility

| View | XML mặc định | Runtime | Điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| `btnDelete` | (không set trong XML, mặc định visible) | `btnDelete.setVisibility(args.canDelete ? VISIBLE : GONE)` trong `initUi()` | `canDelete` = nav-arg | **Từ Result → preview**: canDelete=false → **btnDelete GONE**. **Từ Gallery/TabGallery → xem lại video đã lưu**: canDelete=true → **btnDelete VISIBLE**. → 2 STATE bắt buộc dựng riêng. |

### G. Interaction

1. **btnBack** → disable chính nó, `popBackStack()`.
2. **btnShare** → share sheet, cùng cơ chế Result.
3. **btnDelete** → `PopupUtilsKt.showPopupConfirmDelete()` **[dialog xác nhận xoá — dựng riêng 1
   frame, xem layout ở mục H]** → nếu confirm: xoá file vật lý; nếu Android < 30 hoặc `delete()`
   thành công → xoá luôn thumbnail cache (`filesDir/Thumb/Custom/<tên>.png`) +
   `sharedViewModel.deleteMyVideo(path)` + back. Nếu Android ≥ 30 và xoá file trực tiếp thất bại
   (do scoped storage) → gọi `MediaStore.createDeleteRequest` → **placeholder có nhãn: hệ thống
   xác nhận xoá MediaStore (IntentSender)** → callback resultCode OK mới thực sự xoá record + back.
4. ExoPlayer: `setPlayWhenReady(true)` khi vào màn, `false` ở `onPause`, `release()` ở
   `onDestroyView`. Dùng UI control mặc định của `androidx.media3.ui.PlayerView`
   (`use_controller="true"`) — KHÔNG phải custom seekbar tự vẽ (không có `onDraw()` custom nào cho
   player trong cụm này).

---

## H. FragmentVideoGallery — `fragment_video_gallery.xml` (màn full-screen, từ Home → "My library")

| # | View | id | Vai trò | Constraint | Size | Text/nền | Margin |
|---|---|----|---|---|---|---|---|
| 1 | AppCompatImageView | `btnBack` | back | top/start parent | 48×48dp | `BackImageButton1` | — |
| 2 | AppCompatTextView | `appCompatTextView2` | tiêu đề | center ngang, top/bottom=btnBack, elevation 10dp | wrap | **"My library"** (`@string/my_library`) | — |
| 3 | RecyclerView | `rvContent` | **Grid video đã lưu** — `GridLayoutManager` `spanCount=2` (khai trong XML `app:layoutManager`+`app:spanCount`, KHÔNG override trong code) | full width, top=btnBack, bottom=parent | height=0dp | — | — |
| 4 | AppCompatImageView | `imvEmpty` | ảnh empty-state | center ngang, bottom=`lineCenterY` (guideline 50%), ratio 1:1, width=50% màn | width%=0.5 | `ic_empty` | — |
| 5 | TextView | `tvEmptyNotify` | text empty-state | full width (trừ margin 20dp 2 bên), top=imvEmpty | wrap | **"No videos yet! Try a fun filter and \nstart recording!"** (`@string/video_gallery_empty_notify`, có xuống dòng cứng trong string gốc) · gravity center | marginHorizontal 20dp |
| 6 | Guideline | `lineCenterY` | mốc 50% chiều cao | horizontal, percent 0.5 | — | — | — |
| 7 | AppCompatTextView | `btnCreate` | CTA "Create Now" | bottom/start/end parent | `Button.Primary` style (fill width, bg `bg_primary_rounded`, textColor `@color/button_primary_text_color` — ColorStateList: enabled → `#ff171716` (`text_primary_color`), disabled → `#ff999894` (`text_secondary_color`), xem chi tiết ở mục A row 6b; `btnCreate` không bị disable trong code nên luôn ở state **enabled → #171716**) | margin 20dp | text **"Create Now"** (`@string/create_now`) |
| — | Group | `groupEmpty` | gom `imvEmpty`+`tvEmptyNotify` để show/hide 1 lần | — | — | — |

### Visibility

| View | XML mặc định | Runtime | Điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| `groupEmpty` (imvEmpty+tvEmptyNotify) | visible (Group không set) | `groupEmpty.setVisibility(isEmpty ? VISIBLE : GONE)` trong callback `AdapterMyVideo.Listener.onIsEmpty` | `listMyVideos.isEmpty()` sau mỗi `updateAll()` | STATE "rỗng": group VISIBLE, list ẩn (RecyclerView vẫn hiện nhưng 0 item nên trống). STATE "có N item": group GONE. |
| `btnCreate` | **`android:visibility="invisible"`** trong XML | **KHÔNG có setter nào trong `FragmentVideoGallery.java` đổi visibility của `btnCreate`** — chỉ gắn `setOnClickListener` (điều hướng `actionToLevelPicker`) | — | **KẾT QUẢ: luôn INVISIBLE trên thực tế theo code đọc được** — nút tồn tại, chiếm chỗ (không phải GONE) nhưng không hiện & không thể bấm bằng tay thật (invisible vẫn nhận click nếu code set clickable, nhưng user không thấy) → CỜ: có thể là bug/dead code của app gốc, hoặc bị 1 lớp runtime khác (theme/style) ghi đè — ghi rõ dead-state, KHÔNG dựng làm CTA chính, chỉ note trong spec. |

### List `rvContent` (mục C)

- Nguồn: `VideoGalleryViewModel.listMyVideos` = `StateFlow<List<String>>` init = `emptyList()`,
  nạp từ `DatabaseRepository.getAllMyVideos("CemFacePuzzle")` — filesystem scan qua
  `java.io.File.listFiles()`, trích dẫn đầy đủ file:dòng ở mục 0 ("Thư mục lưu / thư viện").
- Adapter: `AdapterMyVideo` (item = `item_my_video.xml`, 1 loại view duy nhất — **không có ô ad,
  không có ô "Add" chèn thêm** trong adapter này, khác với các list template khác trong app).
- Thumbnail mỗi item: `GlideUtilKt.loadThumbnailFromVideoWithCache` (Glide load frame đầu video,
  có cache theo lifecycleOwner) → **runtime placeholder**, bo góc `R.dimen.size_16` set code.
- Item click → `actionGalleryToPlayVideo(path, canDelete=true)`.
- **Không có long-press / multi-select / menu ngữ cảnh nào trong `AdapterMyVideo`** — chỉ 1
  `setOnClickListener` trên root. Xoá video chỉ thực hiện ở màn PlayVideo (mục G.3).
- **STATE bắt buộc dựng** (đúng yêu cầu "count không cố định"):
  1. **Rỗng** — `groupEmpty` visible, `rvContent` 0 item.
  2. **Có N item** — minh hoạ với **N=7** (số lẻ để thấy dòng cuối lệch trong grid 2 cột) —
     ghi rõ "minh hoạ runtime, số lượng thực tế do người dùng quyết định", thumbnail = runtime
     placeholder (khung xám/video-icon), không bịa ảnh thật.
  3. **Loading** — **KHÔNG có trong code** (Flow không emit trạng thái loading riêng, xem mục 0).
     → nếu Figma cần 1 frame "loading" để mô phỏng lúc quét file, đây là **suy diễn UI/UX thêm**,
     phải ghi rõ "không có trong code gốc, dựng tham khảo" chứ không claim là 1:1.
  4. **Lỗi** — **KHÔNG có trong code** (không try/catch hiển thị lỗi ra UI). Tương tự trên, nếu cần
     dựng phải ghi rõ là suy diễn, không phải hành vi thật.

---

## I. FragmentTabGallery — `fragment_tab_gallery.xml` — ⚠ DEAD CODE, KHÔNG PHẢI MÀN THẬT

**Ruling (round 2, đối chiếu chéo với spec cụm home — spec home đúng, đã verify độc lập tại đây):**
`FragmentTabGallery` **không có đường điều hướng nào tới nó trong app** — không phải màn/biến thể
tab thật đang chạy được, mà là code còn sót lại (dead code / unreachable). Bằng chứng:
- `grep -in "tabgallery" res/navigation/main_nav.xml` → **0 hit** (không phải nav destination).
- Toàn bộ source chỉ có 8 file tham chiếu `FragmentTabGallery`, và ngoài chính bản thân nó
  (`FragmentTabGallery.java`, `Hilt_FragmentTabGallery.java`, `FragmentTabGalleryBinding.java`,
  `FragmentTabGallery$setupMyListVideo$2.java`, `*_GeneratedInjector.java`) thì 2 file còn lại là
  `CemApplication_HiltComponents.java` và `DaggerCemApplication_HiltComponents_SingletonC.java`
  — đây là code Hilt **tự sinh cho MỌI fragment có `@AndroidEntryPoint`**, không phải lời gọi thật
  từ `FragmentHome`.
- `FragmentHome.java` **không** chứa reference nào tới `FragmentTabGallery` (không có trong danh
  sách file grep ra) → không ViewPager2/adapter/BottomNav nào add nó, `newInstance()` không ai gọi.

→ **Kết luận đã sửa**: KHÔNG tính là 1 trong các "màn thật" của cụm result-video khi audit độ phủ
destination ở Phase 6 mục 1 (so khớp với nav graph) — vì nó không có đường vào, đưa vào sẽ làm sai
phép diff. **Vẫn dựng 1 frame cho layout này trong Figma** (theo yêu cầu dựng hết layout đã đọc),
nhưng gắn nhãn rõ **"unreachable / dead code — không có đường điều hướng tới"** trên frame đó.

Cùng ViewModel/Adapter với FragmentVideoGallery. Nếu vẫn dựng, khác biệt layout so với H:

| Khác biệt | fragment_video_gallery.xml | fragment_tab_gallery.xml |
|---|---|---|
| `btnBack` | visible | **`android:visibility="invisible"`** (vì đang là 1 tab trong Home, không cần back riêng) |
| `rvContent` padding | không có | `paddingBottom=@dimen/main_menu_height_offset (100dp)` + `clipToPadding=false` — chừa chỗ cho bottom nav bar của Home |
| `tvEmptyNotify` | width=fill_parent, không bold, không set textSize riêng (kế thừa mặc định) | width=wrap_content, `textSize=@dimen/text_size_16`, `textStyle=bold` |
| `btnCreate` | có (nhưng invisible chết, xem trên) | **KHÔNG có view này trong layout** |
| Item click đích | `actionGalleryToPlayVideo` (nav graph riêng) | `FragmentHomeDirections.actionToPlayVideo` (action khai trong `fragmentHome`/global, nav_main.xml dòng 5) |

→ Cùng bộ state rỗng/có-N như mục H (dùng chung `groupEmpty`/`AdapterMyVideo`), KHÔNG có state
loading/lỗi ở đây (lý do như trên).

---

## J. Popup xác nhận xoá — `popup_exit_confirm.xml` (dùng chung 2 nơi: exit-confirm & delete-confirm)

Bị gọi từ `PopupUtilsKt.showPopupConfirmDelete()` (FragmentPlayVideo, mục G.3) — **AlertDialog**
custom, width = 85% chiều rộng màn hình (tính code: `screenWidth*0.85`), height wrap, nền
`bg_solid_rounded_12`, padding 16dp, không cancelable (chỉ đóng qua nút).

| View | id | Text khi dùng cho "xoá video" | Style |
|---|---|---|---|
| AppCompatTextView | `tvHeader` | **"Delete video"** (`@string/delete_video`) | `ScreenTitleCommon` |
| AppCompatTextView | `tvContent` | **"Are you sure you want to delete this video?"** (`@string/are_you_sure_you_want_to_delete_this_video`) | center, marginHorizontal 8dp |
| AppCompatTextView | `btnCancel` | **"Cancel"** (`@string/cancel`) | nền `#ffe6e6e5` (`color_E6E6E5`), bo `bg_white_corner_69`, font `lato_bold_700` |
| AppCompatTextView | `btnDelete` | **"Delete"** (`@string/delete`) | nền `#ffff4342` (`color_FF4342`), chữ trắng, bo `bg_white_corner_69` |
| Space | `vCenter` | đệm giữa 2 nút, 16dp | — |
| View | `overlayView` | overlay chặn double-tap trong lúc dialog đang xử lý (gone→visible khi bấm) | — |

Lưu ý: cùng layout này còn dùng cho `showPopupExit()` (popup "Go back?" ở màn quay — **ngoài cụm
result-video**, string khác: `go_back`/`your_video_will_not_be_save_if_you_go_back`/`no`/`yes`) —
chỉ ghi để không nhầm code path, KHÔNG dựng frame đó ở đây.

---

## K. Bảng AD SLOT của cụm

| Placement key | Loại | Màn | Trigger |
|---|---|---|---|
| `inter_save` | Interstitial | FragmentResult | Bấm nút Save, trước khi xin quyền lưu |
| `native_collapsible_result` | Native collapsible (co giãn) | FragmentResult | Tự load khi vào màn (`loadAndShowAds()` chạy song song `initUi()`), container `nativeCollapsibleContainer` |
| `native_fullscreen_save` | Native full-screen | FragmentResult | Khi back/đóng màn Result (`handleCloseScreen`) |

PlayVideo / VideoGallery / TabGallery: **không có AD SLOT nào trong layout hoặc code fragment đọc
được** (không native container, không gọi `FullscreenManager`/`NativeManager` nào trong 4 file
Java đã đọc trọn).

---

## L. Remote Config / A-B

Không có key Remote Config nào được đọc trong `FragmentResult`, `FragmentPlayVideo`,
`FragmentVideoGallery`, `FragmentTabGallery`, `AdapterMyVideo`, `VideoGalleryViewModel` (đã đọc
trọn cả 6 file, không có `getBoolean/getLong/getString` remote-config nào). → Không có nhánh
mặc định cần chọn cho cụm này; toàn bộ UI là tĩnh theo code, chỉ biến thiên theo dữ liệu
runtime (video path, canDelete, list rỗng/có-N).

---

## M. Tổng hợp CỜ (chưa resolve / cần verify thêm)

1. `btnCreate` ("Create Now") trong `fragment_video_gallery.xml` mặc định `invisible` và **không
   có đoạn code nào set lại visibility** trong `FragmentVideoGallery.java` — nút coi như chết theo
   code đọc được. Ghi trong spec là dead-state, không dùng làm CTA chính khi dựng Figma trừ khi có
   bằng chứng khác (ví dụ set từ 1 base class khác chưa đọc tới).
2. Vị trí chồng lấn giữa `btnSave` và `nativeCollapsibleContainer` (cả hai đều
   `bottom_toBottomOf="parent"`) — ConstraintLayout không tự sắp xếp tránh nhau, ghi CỜ cần xem
   ảnh chụp màn hình thật hoặc video demo để biết layout thật khi ad hiện.
3. Trạng thái "loading" và "lỗi" của Video Gallery — **không tồn tại trong code**, nếu Figma
   yêu cầu đủ 4 state theo brief thì 2 state này là suy diễn thêm ngoài spec (đã ghi rõ ở mục H).
4. Sort order chính xác của `getAllMyVideos` (`sortByDescending$1`) không đọc được nội dung
   comparator (JADX decompile lỗi phần thân, xem `DatabaseRepositoryImpl$getAllMyVideos$1.java`
   dòng 117-120), chỉ biết là **giảm dần** — khả năng cao theo `lastModified()` (video mới nhất lên
   đầu) nhưng chưa verify field cụ thể.
5. Cảnh báo "rating 5 sao" trong brief **không áp dụng cho cụm này** — đã verify `showAppReview`/
   `rateMyApp` chỉ gọi từ `FragmentHome`/`FragmentHomeOldUI`, ngoài phạm vi result-video.
