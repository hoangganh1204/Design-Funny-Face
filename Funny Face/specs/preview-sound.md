# Cụm: preview-sound

Nguồn: `$SRC/ui/preview/{FragmentPreviewTemplate,FragmentPreviewWithMusic,PreviewWithMusicViewModel}.java`,
`$SRC/ui/sound_picker/{FragmentSoundPicker,DialogFragmentSoundPicker,AdapterSounds,SoundConst}.java`,
layouts `fragment_preview_template.xml`, `fragment_preview_with_music.xml`, `fragment_sound_picker.xml`,
`item_sound_layout.xml`, `layout_loading.xml`, `popup_exit_confirm.xml`.
`$SRC` thật = `decompiled/sources/sources/com/cem/face/puzzle` (có 1 lớp `sources/sources` thừa trong cây).

Nav graph (`res/navigation/main_nav.xml`):
```
fragmentHome --actionHomeToPreviewTemplate--> fragmentPreviewTemplate (arg urlVideoTemplate:string)
fragmentPreviewTemplate --actionPreviewToFacePuzzle--> fragmentFacePuzzle (arg level:int)
fragmentFacePuzzle --actionToPreviewWithMusic--> fragmentPreviewWithMusic (args pathVideoPreview:string, soundPreview:SoundUI?)
fragmentFacePuzzle --actionPlayFilterToSoundPicker--> dialogFragmentSoundPicker   (KHÁC cụm gọi)
fragmentFunnyPuzzle --actionFunnyPuzzleToSoundPicker--> dialogFragmentSoundPicker (KHÁC cụm gọi)
fragmentFunnyPuzzle --actionFunnyPuzzleToPreviewWithMusic--> fragmentPreviewWithMusic
fragmentPreviewWithMusic --actionPreviewWithMusicToSoundPicker--> fragmentSoundPicker (full-screen, KHÔNG dialog)
fragmentPreviewWithMusic --actionPreviewWithMusicToResult--> fragmentResult (popUpTo fragmentHome)
```
→ Trong cụm này, "Add Music/Change Sound" trên FragmentPreviewWithMusic mở **FragmentSoundPicker** (full-screen
nav destination), KHÔNG phải dialog. **DialogFragmentSoundPicker** chỉ được 2 màn NGOÀI cụm gọi
(FragmentFacePuzzle, FragmentFunnyPuzzle — thuộc cụm khác) nhưng dùng đúng cùng layout/adapter nên vẫn dựng ở
đây theo yêu cầu brief.

---

## 1. FragmentPreviewTemplate — xem trước template (trước khi chụp/quay)
Layout: `fragment_preview_template.xml`. ConstraintLayout full-screen, không status-bar giả lập.
Class: `com.cem.face.puzzle.ui.preview.FragmentPreviewTemplate extends AdBaseFragment<FragmentPreviewTemplateBinding>`.
Nav arg: `urlVideoTemplate: String` (URL/đường dẫn video mẫu — **runtime placeholder**, không phải asset tĩnh).

### A. Geometry (từ XML thật, ConstraintLayout — ghi theo constraint vì không có x/y tuyệt đối)
| id | vai trò | w×h | constraint | khác |
|---|---|---|---|---|
| root | ConstraintLayout | fill×fill | — | nền: video full-bleed |
| `exoPlayerView` | `androidx.media3.ui.PlayerView` | 0dp×0dp (match qua constraint 4 cạnh = full-bleed) | top/bottom/start/end = parent | `resize_mode=fill`, `use_controller=false` → **animation: video player**, video = **runtime placeholder** (từ `urlVideoTemplate`) |
| `progress` | `ProgressBar` (spinner tròn hệ thống) | wrap×wrap, gravity=center | căn giữa `exoPlayerView` (4 cạnh) | mặc định GONE trong code, chỉ hiện khi player đang buffer |
| `btnBack` | `ImageButton` style `BackImageButton2` | 36×36dp (icon) trong khung 48×48dp (`Base.PrimaryButton.Square`: padding 8dp→ghi đè `padding=4dp` ở BackImageButton2), margin 12dp | start/top = parent | icon `@drawable/ic_back_2`: vòng tròn đen 40% alpha + mũi tên trắng — thiết kế để nổi trên video nền bất kỳ màu gì |
| `bottomSpace` | `Space` | fill×0dp | bottom=parent | height=0 tĩnh; code cộng `insets.bottom` runtime (an toàn cử chỉ) |
| `btnTryNow` | `AppCompatTextView` style `Button.Primary` | fill×48dp, margin 16dp mọi cạnh | bottom→top của `bottomSpace`, start/end=parent | text="Try Now" (`@string/try_now`), 16sp, màu chữ `@color/button_primary_text_color` = selector `res/color/button_primary_text_color.xml`: enabled → `@color/text_primary_color` = **#171716**, disabled (`state_enabled=false`) → `@color/text_secondary_color` = **#999894**; nền `bg_primary_rounded` selector: enabled=gradient xanh `#00fbff→#0080f6` bo góc 48dp full-pill, disabled=`#6600fbff` |
| `nativeCollapsibleContainer` | `FrameLayout` | 0dp×wrap | bottom→top của `bottomSpace`, start/end=parent | **AD SLOT** container — trùng vị trí `btnTryNow` (ẩn hiện luân phiên bằng cùng constraint) |
| `collapseHolderNative` (con của trên) | `View` placeholder nền trắng | fill×256dp (`ad_native_collapsed_height`=`size_256`) | — | nền `bg_ad_native_media_white` (trắng + viền trên 1dp `#e4e3e2`) — placeholder TRƯỚC khi ad thật load |

### B. Visibility (từ code)
| view | XML mặc định | runtime | điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| `progress` | không khai báo (mặc định VISIBLE) | `visible()`/`gone()` qua `Player.Listener.onPlaybackStateChanged` | `STATE_BUFFERING(2)`→visible; `STATE_READY(3)`→gone + `setPlayWhenReady(true)` | ẩn ngay khi video sẵn sàng để play |
| `collapseHolderNative` | VISIBLE | `gone()` sau delay 2000ms (`repeatOnLifecycle(STARTED)`, `delay(2000L)`) | luôn, không điều kiện remote | placeholder trắng biến mất sau 2s dù ad có load hay không (native ad thật vẽ đè lên `nativeCollapsibleContainer` bằng `NativeManager.presentCollapsible(...)`, key=`AdKey.NATIVE_PREVIEW_COLLAP`="native_collapsible_preview") |
| `btnTryNow` | enabled | `setEnabled(false)` khi bấm → log event → `setEnabled(true)` ngay (chặn double-tap trong 1 frame, không debounce thật) | — | — |

### C. List
Không có list trong màn này.

### D. Hardcode
- Text: "Try Now" (`@string/try_now`).
- Event log: `EventTrackingConst.PREVIEW_RECORD_VIEW` (onCreate), `PREVIEW_RECORD_CLICK_TRY` (khi bấm Try Now).

### E. Nguồn từng view
- Video (`exoPlayerView`) ← `urlVideoTemplate` (nav arg) = **runtime placeholder** (URL video mẫu, không tĩnh trong repo này — nguồn ở màn Home gọi action, ngoài cụm).
- `collapseHolderNative`/native ad ← AdMob/nextgen native qua `NativeManager`, placement key **`native_collapsible_preview`** = **AD SLOT**.

### F. Nhánh remote/logic
- Bấm "Try Now" → `levelPicker()`:
  - Đọc `FirebaseRemoteManager.getBoolean(ConfigKey.LEVEL_PICKER_SKIPPED)`.
  - Theo `_shared-context.md`: `level_picker_skipped = false` (giá trị fetch thật) → **nhánh mặc định = ĐI QUA LevelPicker** (`actionToLevelPicker`), KHÔNG nhảy thẳng `actionPreviewToFacePuzzle(level=2)`.
  - Nhánh `true` (nếu bật) sẽ nhảy thẳng `FragmentFacePuzzle(level=2)`, bỏ qua LevelPicker — ghi chú nhưng KHÔNG dựng vì không phải mặc định.

### STATE (mỗi state 1 frame)
1. **Loading video** — `progress` visible giữa màn hình, video chưa play, `collapseHolderNative` trắng (nếu <2s đầu).
2. **Ready / playing** — video full-bleed đang phát loop (`setRepeatMode(REPEAT_MODE_ALL)`), `progress` gone, `collapseHolderNative` gone (sau 2s) — ad thật (nếu load được) hiện trong `nativeCollapsibleContainer`, nếu ad fail thì `nativeCollapsibleContainer` trống (height wrap_content→0 vì không có nội dung).
3. **Native ad hiện** (biến thể của #2) — `nativeCollapsibleContainer` có nội dung ad thật đè lên vị trí `btnTryNow`? ⚠ Cần lưu ý: `nativeCollapsibleContainer` và `btnTryNow` CÙNG constraint (chồng nhau) → dựng 2 lớp: ad nằm trên/dưới nút hay 2 khu vực loại trừ nhau — code không ẩn `btnTryNow` khi ad hiện, nên thực tế 2 view chồng lên nhau tại cùng vị trí (khả năng do bottomSpace + margin khác biệt che khuất một phần) — GẮN CỜ, không đủ info tĩnh để khẳng định chồng đè hoàn toàn hay ad chỉ chiếm phần trên nút.

---

## 2. FragmentPreviewWithMusic — xem trước kết quả (video đã ghép) + chọn nhạc nền
Layout: `fragment_preview_with_music.xml`. Class `... extends AdBaseFragment<FragmentPreviewWithMusicBinding>`,
ViewModel riêng `PreviewWithMusicViewModel` (SavedStateHandle, key `KEY_CURRENT_SOUND`).
Nav args: `pathVideoPreview: String` (đường dẫn video đã render — **runtime placeholder**), `soundPreview: SoundUI?` (nullable).

### A. Geometry
| id | vai trò | w×h | constraint | khác |
|---|---|---|---|---|
| root | ConstraintLayout | fill×fill | — | |
| `exoPlayerView` | PlayerView | 0dp×0dp = full-bleed | 4 cạnh = parent | `resize_mode=fixed_height` (khác màn 1 dùng `fill`), `use_controller=false` → **animation: video player**, nguồn = `pathVideoPreview` = **runtime placeholder** |
| `btnBack` | ImageButton `BackImageButton2` | 48×48dp khung / icon 36dp, margin 12dp | start/top=parent | icon `ic_back_2` (vòng đen mờ + mũi tên trắng) |
| `btnAddMusic` (ConstraintLayout con) | thanh pill "chọn nhạc" | wrap×32dp, max-width 180dp, padding ngang 4dp | bottom/top = `btnBack` (căn giữa hàng ngang với nút back), start/end=parent (căn giữa màn hình theo chiều ngang) | nền `bg_black_40_rounded` = đen 40% alpha bo góc 40dp (pill) |
| — `imgMusic` (con) | AppCompatImageView | wrap×wrap, padding 4dp, margin-start 4dp | start/top/bottom=parent (của btnAddMusic) | icon `@drawable/ic_music` |
| — `tvNameSong` (con) | AppCompatTextView | wrap×wrap, max-width 96dp | start=sau `imgMusic`, end=trước `vVertical`, top/bottom=parent | text runtime (tên bài hoặc "Add song"), màu trắng, `singleLine` + marquee khi tràn, `includeFontPadding=false`, margin-end 8dp |
| — `vVertical` (con) | AppCompatImageView (dùng làm divider) | 1dp×0dp (match chiều cao cha) | end→trước `btnRemoveSound`, top/bottom=parent | nền trắng, margin dọc 4dp, **mặc định GONE trong XML** |
| — `btnRemoveSound` (con) | AppCompatImageView | wrap×wrap, padding 4dp | end/top/bottom=parent | icon `ic_close`, margin-end 4dp, **mặc định GONE trong XML** |
| `bottomSpace` | Space | fill×0dp | bottom=parent | + inset runtime |
| `btnNext` | AppCompatTextView `Button.Primary` | fill×48dp, margin 16dp | bottom→top `bottomSpace`, start/end=parent | text="Next" (`@string/next`), màu chữ selector `button_primary_text_color`: enabled **#171716** / disabled **#999894** (xem mục 1) |
| `nativeCollapsibleContainer`/`collapseHolderNative` | như màn 1 | 0dp×wrap / fill×256dp | bottom→top `bottomSpace`, start/end=parent | cùng cơ chế: placeholder trắng 2s rồi gone, ad thật key `native_collapsible_preview` |
| `viewLoading` (`<include layout="@layout/layout_loading">`) | overlay loading | fill×fill | — | mặc định `visibility=gone`; nội dung: nền `#40000000` + `ProgressBar` giữa màn (không phải Lottie/PAG) |

### B. Visibility
| view | XML mặc định | runtime | điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| `vVertical`, `btnRemoveSound` | GONE | `setVisibility(VISIBLE/GONE)` theo `soundUI != null` trong `initUi$5` (collect `getCurrentSound()`) | có bài hát đang chọn → VISIBLE cả 2; không có → GONE cả 2 | divider + nút xoá chỉ hiện khi đã chọn nhạc |
| `tvNameSong` | text để trống trong XML | set = `soundUI.nameSound` hoặc fallback `@string/add_sound` ("Add song") | theo `currentSound` flow | |
| `collapseHolderNative` | VISIBLE | `gone()` sau 2000ms delay, giống màn 1 | — | |
| `viewLoading` | GONE | ⚠ không tìm được lệnh set visible tường minh trong code đã decompile được (method `initListener$1$5$1` bị JADX dump lỗi, chỉ còn bytecode) — suy luận từ include + luồng: bấm `btnNext` → `setEnabled(false)` → coroutine gọi `genFile()`→`addMusicToVideo-BWLJW6A()` (mux audio+video bằng `MediaMuxer`/`MediaExtractor`, chạy trên `Dispatchers.IO`) → điều hướng `actionPreviewWithMusicToResult`. Rất có khả năng `viewLoading` được set visible lúc bắt đầu mux và gone lúc xong/lỗi, nhưng KHÔNG resolve tĩnh được — GẮN CỜ. |
| `btnNext` | enabled | `setEnabled(false)` ngay khi bấm (chặn double-tap trong lúc mux) | — | |

### C. List
Không có list; chỉ có nút mở `FragmentSoundPicker`.

### D. Hardcode
- Text: "Next" (`@string/next`), "Add song" (`@string/add_sound`).
- Event: `EventTrackingConst.PREVIEW_FINISH` (log khi vào màn).
- Dialog xác nhận thoát: xem mục "Exit confirm" bên dưới — DÙNG CHUNG layout `popup_exit_confirm.xml` với text mặc định trong XML (không override text) = tiêu đề **"Go back ?"**, nội dung **"Your video will not be save if you go back"**, nút **"No"/"Yes"**.

### E. Nguồn từng view
- Video ← `pathVideoPreview` (nav arg, file cục bộ đã render) = **runtime placeholder**.
- Sound hiện tại ← `PreviewWithMusicViewModel.currentSound` (StateFlow trong SavedStateHandle) — khởi tạo từ `soundPreview` nav-arg nếu có, nếu null thì `SharedViewModel.randomSound()` chọn NGẪU NHIÊN 1 bài trong 4 bài hardcode (xem mục 5).
- `collapseHolderNative`/native ad ← placement `native_collapsible_preview` = **AD SLOT**, giống màn 1.

### F. Luồng nút & dialog thoát
- `btnBack` VÀ hệ thống back (OnBackPressedCallback) → `handleCloseScreen()` → `PopupUtilsKt.showPopupExit(activity, onDeleteClick)`:
  - Dialog: `AlertDialog` (KHÔNG phải BottomSheet), nền cửa sổ trong suốt, width = 85% screen width, height=wrap. Layout `popup_exit_confirm.xml`: card bo góc 12dp (`bg_solid_rounded_12`), tiêu đề "Go back ?" (style `ScreenTitleCommon`, 20sp), nội dung "Your video will not be save if you go back" (căn giữa), 2 nút ngang 50/50: **"No"** (nền `#E6E6E5`, chữ đen) / **"Yes"** (nền `#FF4342`, chữ trắng) — 14sp bold, bo pill (`bg_white_corner_69`).
  - Có `overlayView` phủ toàn dialog, mặc định GONE, chỉ hiện tạm khi bấm "No" (chặn tương tác trong lúc dialog đang đóng) rồi ẩn lại.
  - Bấm "Yes"/`btnDelete` → xoá thư mục cha của `pathVideoPreview` (`FilesKt.deleteRecursively`) rồi `popBackStack()`.
  - Bấm "No"/`btnCancel` → đóng dialog, ở lại màn.
  - **Đây CHÍNH LÀ dialog "xác nhận thoát mất tiến trình" brief hỏi** — chỉ có ở `FragmentPreviewWithMusic`, KHÔNG có ở `FragmentPreviewTemplate` (màn đó back = `popBackStack()` thẳng, không cảnh báo vì chưa có gì để mất).
- `btnAddMusic`/`btnRemoveSound`:
  - `btnRemoveSound` click → `changeSound(null)` (bỏ nhạc, không mở picker).
  - Vùng còn lại của `btnAddMusic` (pill) click → `navigateToDirections(actionPreviewWithMusicToSoundPicker())` → mở `FragmentSoundPicker` (full-screen, có back-stack), nhận kết quả qua `FragmentResultListener(SoundConst.SOUND_RESULT)` → `changeSound(parcelable SoundUI)`.
- `btnNext` → mux audio+video (mô tả ở trên) → `actionPreviewWithMusicToResult(outputPath)` với `popUpTo(fragmentHome)` — tức Result thay thế cả back-stack Preview/SoundPicker.

### STATE
1. **Đang phát video, chưa chọn nhạc** — `vVertical`/`btnRemoveSound` gone, `tvNameSong`="Add song".
2. **Đang phát video, đã có nhạc (random hoặc user chọn)** — `vVertical`/`btnRemoveSound` visible, `tvNameSong`=tên bài, nhạc nền phát loop qua `MediaPlayer` riêng (song song với video, KHÔNG mute video — cả 2 `Player`/`MediaPlayer` chạy cùng lúc trừ khi video preview tự câm tiếng; không thấy code mute exoVideoPlayer).
3. **Dialog xác nhận thoát** — overlay AlertDialog card giữa màn hình (mô tả trên), nền màn phía sau vẫn nhìn thấy (dim mặc định AlertDialog, không set riêng).
4. **Đang render/mux (loading)** — `viewLoading` full-screen `#40000000` + spinner giữa, `btnNext` disabled. (⚠ thời điểm bật/tắt chưa resolve tĩnh 100%, xem mục B).
5. **Lỗi mux** — không tìm thấy UI lỗi tường minh (`addMusicToVideo` trả `Result<String>`, nhánh `Result.failure` không có xử lý UI rõ trong phần decompile được) — GẮN CỜ, không dựng frame lỗi riêng vì không có bằng chứng UI cụ thể (có thể chỉ Timber log + không điều hướng).
6. Không có state free-vs-PRO/watermark: **KHÔNG tìm thấy bất kỳ logic PRO/watermark/premium nào** trong `ui/preview`, `ui/sound_picker` hay `ui/result` (đã grep toàn bộ, không match `watermark|isPro|premium`). App không có gói trả phí ở cụm này → chỉ 1 state "free" (có ads), không có PRO.

---

## 3. FragmentSoundPicker — chọn nhạc (full-screen, nav destination)
Layout: `fragment_sound_picker.xml`. Class `... extends AdBaseFragment<FragmentSoundPickerBinding>`.
Dùng `SharedViewModel.getListSounds()` (activity-scope), KHÔNG có nav-arg riêng.

### A. Geometry
| id | vai trò | w×h | constraint | khác |
|---|---|---|---|---|
| root | ConstraintLayout | fill×fill | — | nền mặc định theme (sáng — vì dùng `BackImageButton1` cho back, icon tối, khác 2 màn preview trên nền video) |
| `btnBack` | ImageButton style `BackImageButton1` | khung 48×48dp, padding 8dp, margin 12dp | start/top=parent | icon `ic_back_1`: mũi tên đen 24dp, KHÔNG có vòng tròn nền (vì nền màn là màu sáng, không phải video) |
| tiêu đề (không id, `AppCompatTextView`) | style `ScreenTitleCommon` | wrap×wrap | căn giữa theo `btnBack` (top/bottom = btnBack, start/end=parent) | text="Sound" (`@string/sound`), 20sp bold, màu `@color/text_primary_color` (#171716) |
| `rcvMusic` | `RecyclerView` | fill(-16dp mỗi bên)×0dp | top→dưới `btnBack`, bottom→trên `adNativeView` | `LinearLayoutManager` (set qua `app:layoutManager` trong XML, dọc), margin ngang 16dp |
| `btnDone` | AppCompatTextView `Button.Primary` | 0dp(=match constraint)×48dp, margin 24dp mọi cạnh | bottom=parent, start/end=parent | text="Done" (`@string/done`), màu chữ selector `button_primary_text_color`: enabled **#171716** / disabled **#999894** (xem mục 1) |
| `adNativeView` | FrameLayout | fill×wrap, margin 8dp | bottom→trên `btnDone` | **AD SLOT khai báo trong layout nhưng KHÔNG có code nào trong `FragmentSoundPicker`/`DialogFragmentSoundPicker` gán ad vào view này** — đã đọc TRỌN cả 2 class, không có `adNativeView`/`AdKey` nào liên quan trong `ui/sound_picker` → view này là **placeholder chết** (FrameLayout rỗng, không có nội dung) trừ khi có cơ chế inject ẩn ở lớp `Hilt_FragmentSoundPicker`/`AdBaseFragment` mà tôi không thấy access tới `adNativeView` cụ thể. GẮN CỜ: dựng như 1 khối trống cao ~theo nội dung ad chuẩn (ước lượng banner-height) nhưng ghi rõ "không xác nhận được có load ad thật hay không". |

### B. Visibility
Không có visibility runtime đặc biệt ngoài `initSoundsAdapter()` gán data cho `rcvMusic` khi `SharedViewModel.listSounds` emit.

### C. List — `rcvMusic` (RecyclerView, `AdapterSounds extends BaseAdapter<ItemSoundLayoutBinding, SoundUI>`)
- Nguồn: `SharedViewModel.getListSounds()` ← nếu rỗng lần đầu, lấy từ `AppSettingRepository.getListSounds()` ← `AppSetting.listSound` (hardcode trong constructor `AppSetting`), sau đó lưu lại vào `SavedStateHandle` (cache trong phiên).
- **ĐÚNG 4 item, thứ tự cố định trong code** (KHÔNG phải 5 — xem mục Hardcode #5 giải thích chênh lệch với 5 file `.aac`):
  1. "Greedy Sped Up" — "TateMcRae" — `R.raw.greedy_sped`
  2. "Jingle Bells" — "Orchestra" — `R.raw.jingle_bells`
  3. "Original Sound" — "Mariavsalo" — `R.raw.original_sound`
  4. "Spring Snow" — "10cm" — `R.raw.spring_snow`
- KHÔNG có ô "Add"/"promo"/"ad" chèn vào list — list thuần túy 4 item, không paginate, không empty-state UI (nếu rỗng, RecyclerView chỉ trống — không có empty view khai báo).
- Mỗi item = `item_sound_layout.xml` (xem mục 5).
- `layoutManager` = `LinearLayoutManager` set qua XML attr `app:layoutManager`, KHÔNG set trong code (không override spanCount, không GridLayoutManager).

### D. Hardcode
- 4 sound entries ở trên (nameSound, nameAuthor, R.raw id).
- `duration` field của `SoundUI` KHÔNG hardcode — tính runtime bằng `MediaMetadataRetriever.extractMetadata(METADATA_KEY_DURATION)` trên chính file raw, format qua `DateUtils.formatElapsedTime()` (dạng `m:ss`).
- Text: "Sound" (title), "Done" (nút).
- Event: `EventTrackingConst.SOUND_CHOOSE_VIEW` khi vào màn.

### E. Nguồn
- 4 file nhạc **bundled trong APK**: `res/raw/greedy_sped.aac`, `jingle_bells.aac`, `original_sound.aac`, `spring_snow.aac` (KHÔNG remote).
- `res/raw/audio.aac` (file thứ 5) **TỒN TẠI nhưng KHÔNG được tham chiếu** bởi `R.raw.audio` ở bất kỳ đâu trong `com/cem/face/puzzle` (đã grep toàn bộ source) → tài nguyên mồ côi/không dùng, KHÔNG xuất hiện trong list picker. (Khớp đối chứng progress.md: "5 file .aac, nếu spec báo số khác 5 phải giải thích" → giải thích: 5 file tồn tại trên đĩa, nhưng danh sách hiển thị trong UI chỉ có 4, vì `audio.aac` không được đăng ký trong `AppSetting.listSound`.)

### F. Không có nhánh remote-config nào chi phối list nhạc (hoàn toàn local hardcode).

### STATE (áp dụng chung cho cả FragmentSoundPicker và DialogFragmentSoundPicker vì cùng layout/adapter)
1. **Danh sách mặc định, chưa chọn gì** — không item nào có checkbox/icon "selected" (`positionSelected = -1` ban đầu → so `position == -1` luôn false).
2. **Đã chọn 1 item (đang phát)** — item đó: checkbox = `ic_check_box_selected` (viền xanh `#016cf7` + chấm tròn xanh đặc giữa), icon play/pause = `ic_pause_music` (vì `btnPlayOrPause.setSelected(checkbox.isSelected())`); các item khác: checkbox = `ic_check_box_unselected` (viền xanh rỗng), icon = `ic_play_music`. **CHỈ 2 STATE/ITEM** (chọn / không chọn) — KHÔNG có state "đang phát nhưng chưa chọn" riêng biệt, vì bấm vào item = chọn NGAY LẬP TỨC + phát nhạc đồng thời (`onItemClick` gọi `setAndPlayMusic` VÀ đổi `positionSelected` trong cùng 1 lần bấm).
3. **`btnDone`** → đóng màn (pop/dismiss) kèm trả kết quả `SoundConst.SOUND_RESULT` = `SoundUI` đang chọn (`adapterSounds.getSoundSelected()`, có thể là `null` nếu chưa chọn gì).

---

## 4. DialogFragmentSoundPicker — biến thể Dialog (KHÔNG dùng trực tiếp trong cụm preview-sound, nhưng dựng theo yêu cầu brief)
Class `... extends BaseDialogFragment<FragmentSoundPickerBinding>` — **DÙNG CHUNG NGUYÊN VẸN layout `fragment_sound_picker.xml`** với `FragmentSoundPicker` (cùng binding class `FragmentSoundPickerBinding`, cùng `AdapterSounds`, cùng logic `initSoundsAdapter`/`setAndPlayMusic`/`pauseMusic`/`resumeMusic`). Khác biệt DUY NHẤT là:
- Được gọi từ nav graph dạng `<dialog>` (id `dialogFragmentSoundPicker`) bởi `FragmentFacePuzzle` (`actionPlayFilterToSoundPicker`) và `FragmentFunnyPuzzle` (`actionFunnyPuzzleToSoundPicker`) — 2 màn NGOÀI cụm preview-sound.
- `getTheme()` override = `R.style.FullScreenDialog`:
  ```
  windowNoTitle=true, windowIsFloating=false, backgroundDimEnabled=false,
  windowSoftInputMode=adjustResize, windowCloseOnTouchOutside=false,
  statusBarColor=transparent, windowLightStatusBar=true
  ```
  → **Đây là DialogFragment FULL-SCREEN (windowIsFloating=false), KHÔNG PHẢI bottom-sheet, và `backgroundDimEnabled=false` → KHÔNG CÓ SCRIM/dim phía sau** (vì dialog che kín toàn màn hình nên không cần dim). ⚠ Khác giả định trong brief ("dialog thì có scrim") — đã verify code, KHÔNG có scrim; visual identical với `FragmentSoundPicker` (chỉ khác cơ chế đóng: `dismissSafe()` thay vì `popBackStack()`, và ViewModel lấy qua `activityViewModels()` thay vì fragment injection thường).
  - `windowCloseOnTouchOutside=false` → không tự đóng khi chạm ngoài (nhưng vì full-screen nên "ngoài" không tồn tại).

### Frame dựng
Dựng 1 frame giống hệt geometry/state của mục 3 (FragmentSoundPicker), KHÔNG thêm lớp scrim/overlay phía sau (vì `backgroundDimEnabled=false` và full-screen).

---

## 5. item_sound_layout.xml — 1 dòng trong RecyclerView
ConstraintLayout, `layout_width=fill_parent`, `layout_height=wrap_content`, padding dọc 2dp, margin dọc 8dp.

| id | vai trò | w×h | constraint | text/style |
|---|---|---|---|---|
| `checkbox` | AppCompatImageView | 24×24dp | start/top/bottom=parent | src=`@drawable/ic_check_box` (selector, xem STATE mục 3.2) |
| `tvNameSong` | AppCompatTextView | wrap×wrap | start→sau `checkbox` (margin-start 16dp), top=parent | text=`soundUI.nameSong`; `fontFamily=@font/lato_bold_700` (override); `includeFontPadding=false`; không khai báo `textSize`/`textColor` riêng → kế thừa default theme `Base.Theme.FacePuzzle` (`styles.xml:271-272`): **textSize=14sp** (`@dimen/text_size_14`), **textColor=#171716** (`@color/text_primary_color`) |
| `tvActor` | AppCompatTextView | wrap×wrap | start=`tvNameSong`, top→dưới `tvNameSong` (margin-top 4dp) | text=`soundUI.nameAuthor`; 12sp (`text_size_12`, override); màu kế thừa theme = **#171716**; `fontFamily` kế thừa theme = `@font/lato_regular_400` (không override); `drawableEnd=@drawable/dot_black_size_2` (chấm tròn đen 4×4dp, `drawablePadding=4dp`) — chấm phân cách trước phần thời lượng |
| `tvTime` | AppCompatTextView | wrap×wrap | start→sau `tvActor` (margin-start 4dp), top/bottom=`tvActor` | text=`soundUI.duration` (vd "0:32"); 12sp (override); màu + font kế thừa theme = **#171716** / `lato_regular_400` |
| `btnPlayOrPause` | AppCompatImageView | 24×24dp | end/top/bottom=parent | src=`@drawable/ic_state_play_music` (selector, xem STATE mục 3.2) |

Toàn bộ item = 1 `View.OnClickListener` trên root → chọn + phát nhạc (mô tả ở mục 3, STATE #2).

---

## Đối chứng số liệu (theo yêu cầu progress.md)
- `res/raw/*.aac` = **5 file** trên đĩa (đã đếm bằng `find`). Danh sách hiển thị trong UI = **4 bài** (đã đọc nguyên văn constructor `AppSetting`). Chênh lệch = `audio.aac`, không được `AppSetting.listSound` tham chiếu ở bất kỳ đâu (đã grep `R.raw.audio` toàn bộ `com/cem/face/puzzle`, 0 kết quả) → orphan resource, KHÔNG dựng trong list Figma.

## Cờ / chỗ chưa resolve tĩnh 100%
Đã resolve xong (KHÔNG còn là cờ, đưa vào bảng geometry ở trên):
- `@color/button_primary_text_color` — selector thật tại `res/color/button_primary_text_color.xml`:
  enabled → `@color/text_primary_color` = **#171716**, disabled → `@color/text_secondary_color` = **#999894**
  (`values/colors.xml:497-498`). Áp dụng cho `btnTryNow`/`btnNext`/`btnDone`.
- `tvNameSong`/`tvActor`/`tvTime` trong `item_sound_layout.xml` không set `textColor`/`textSize` (hoặc chỉ
  set `textSize`) riêng → kế thừa default `Base.Theme.FacePuzzle` (`styles.xml:266-281`):
  `android:textSize=@dimen/text_size_14` (14sp), `android:textColor=@color/text_primary_color` (**#171716**),
  `android:fontFamily=@font/lato_regular_400` — trừ `tvNameSong` override `fontFamily=lato_bold_700` và
  `tvActor`/`tvTime` override `textSize=text_size_12` (12sp), còn màu/font khác đều theo theme.

Còn lại là cờ THẬT (runtime/behavior không decompile tĩnh được, không phải resource reference):
1. Thời điểm bật/tắt `viewLoading` (overlay loading khi mux audio+video ở `FragmentPreviewWithMusic`) — method `initListener$1$5$1.invokeSuspend` bị JADX báo lỗi decompile ("Method dump skipped"), chỉ suy luận được luồng chung (disable nút → mux → navigate), không thấy lệnh `visible()/gone()` tường minh trên `viewLoading` trong phần đọc được.
2. Trạng thái LỖI khi mux thất bại (`addMusicToVideo-BWLJW6A` trả `Result.failure`) — không tìm thấy UI xử lý lỗi tường minh trong các file đã decompile; có thể chỉ log Timber. Không dựng frame lỗi riêng vì thiếu bằng chứng cụ thể về UI.
3. `adNativeView` trong `fragment_sound_picker.xml` — khai báo trong layout nhưng KHÔNG có bất kỳ tham chiếu nào trong `FragmentSoundPicker.java`/`DialogFragmentSoundPicker.java` (đã đọc trọn cả 2 file). Đây là thiếu code wiring (không phải resource chưa resolve) — không xác nhận được liệu 1 lớp base khác có auto-bind ad vào view theo tên hay không — dựng như FrameLayout trống/placeholder, ghi rõ nghi vấn.
4. Overlap hình học giữa `nativeCollapsibleContainer` và `btnTryNow`/`btnNext` (cùng constraint 4 cạnh) ở cả 2 màn preview — không rõ khi ad hiện thì nút CTA có bị che/thay thế hay 2 lớp chồng nhau thật (xem mục 1.STATE#3).

(Tham khảo, KHÔNG phải cờ — đã trả lời đầy đủ ở mục "Nguồn từng view" mục 1/2: ads config `native_preview`
brief nhắc tới = đúng 1 placement `native_collapsible_preview` (`AdKey.NATIVE_PREVIEW_COLLAP`), không có
biến thể "native_preview" không-collapsible nào khác trong `monet_super.json`/`monet_v2.json`.)

## Tổng kết đếm (cho reviewer)
- Số màn/frame chính trong cụm: 4 (FragmentPreviewTemplate, FragmentPreviewWithMusic, FragmentSoundPicker, DialogFragmentSoundPicker).
- Số state cần dựng riêng (không tính trùng lặp giữa 2 biến thể sound picker): Preview Template = 2 state chính (+1 biến thể ad chồng, gắn cờ); Preview With Music = 4 state chính (+2 gắn cờ: loading timing, lỗi); Sound Picker (cả 2 biến thể, dùng chung geometry) = 2 state item (chọn/chưa chọn) × 1 layout danh sách = coi như 2 frame state (default + đã chọn).
- List chính: `rcvMusic` = ĐÚNG 4 item cố định, không có ad-item/promo-item chèn vào.
- AD SLOT xác nhận có ad thật: `nativeCollapsibleContainer` (`native_collapsible_preview`) ở CẢ 2 màn preview. `adNativeView` ở Sound Picker: khai báo trong layout nhưng KHÔNG có code load ad — nghi vấn, đã gắn cờ.
- KHÔNG có PRO/watermark trong toàn cụm (đã grep xác nhận).
- Dialog xác nhận thoát: CÓ, chỉ ở FragmentPreviewWithMusic (`popup_exit_confirm.xml` qua `PopupUtilsKt.showPopupExit`), KHÔNG có ở FragmentPreviewTemplate.
