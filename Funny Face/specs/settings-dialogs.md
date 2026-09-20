# Cụm: settings-dialogs — Settings, Company Info, dialog/loading dùng chung

Nguồn: SRC = `decompiled/sources/sources/com/cem/face/puzzle` (chú ý: path thật có thêm 1 tầng
`sources/sources/...`, KHÔNG phải `sources/com/...` như trong `_shared-context.md`).
RES = `decompiled/resources/res`.

---

## 0. Tổng quan phát hiện quan trọng (đọc trước khi dựng Figma)

1. **KHÔNG có PRO/IAP UI nào cả.** Qonversion SDK có trong APK
   (`com/qonversion/android/sdk/*`) và `com.cem.admodule.manager.billing.PurchaseManager`
   tồn tại, nhưng **package app `com.cem.face.puzzle` không hề gọi tới Qonversion, không có
   `Paywall`, `isPro`, `Premium`, không có string "remove ads"/"premium"/"upgrade" nào trong
   `strings.xml`, không có icon crown/diamond/vip nào trong `res/drawable`.**
   `FragmentSettings` chỉ có 2 action điều hướng trong `main_nav.xml`
   (`actionSettingsToInfoFragment`, `action_fragmentSettingsToLanguagePicker`) — không có
   action nào tới màn subscription/paywall. → **Không dựng frame PRO/Remove Ads cho Settings.**
   Đây là kết luận đã verify, không phải suy đoán.
2. **`custom_dialog.xml` KHÔNG PHẢI dialog dùng chung của app.** Grep toàn bộ source cho thấy
   nó chỉ được dùng bởi `com/bytedance/sdk/openadsdk/core/widget/oa.java` và
   `.../utils/dj.java` — tức là layout nội bộ của **Pangle (ByteDance) ad SDK**, không do app
   `com.cem.face.puzzle` sở hữu và không hiển thị nội dung nào của app. Dialog dùng chung
   THẬT của app là `popup_exit_confirm.xml` (xem mục 3).
3. **`loading_alert.xml`** dùng id `mbridge_progressBar1`/`mbridge_textView` → là layout loading
   nội bộ của **MBridge ad SDK**, không được app gọi trực tiếp (không có kết quả grep nào
   trong source app). Không dựng như màn app.
4. Dialog "xác nhận" thật của app dùng chung 1 layout (`popup_exit_confirm.xml`) cho 2 tình
   huống khác nội dung: thoát màn preview (chưa lưu video) và xoá video đã quay — xem mục 3.
5. Không tìm thấy dialog "mất mạng" nào được dựng thật: `BaseActivity` có khai báo field
   `dialogNetWork: Dialog?` nhưng field này **không hề được gán/hiển thị ở đâu trong toàn bộ
   BaseActivity.java** (dead field, không có logic no-network dialog nào chạy). Ghi cờ, không
   dựng frame giả cho trường hợp này.
6. Toast thật (không phải Dialog/Snackbar) dùng ở `ContextExtKt.toastMessageShortTime/LongTime`
   (`Toast.makeText`) — ví dụ lỗi share text, lỗi không có app email, thiết bị không hỗ trợ
   Play Store. Các thông báo lỗi generic này là Toast OS chuẩn, KHÔNG phải custom dialog.
7. In-app review dùng Google Play Core `ReviewManager` (`ContextExtKt.showAppReview`) — gọi
   **vô điều kiện mỗi lần `FragmentHome.initUi()` chạy** (không gọi từ Settings). UI thật do
   Google Play render → **placeholder có nhãn**, không dựng chi tiết.

---

## 1. FragmentSettings — `fragment_settings.xml`

File: `res/layout/fragment_settings.xml` · Java: `ui/settings/FragmentSettings.java`

### A. Geometry (ConstraintLayout, 360×800dp canvas, fill_parent)

| # | View (id) | Loại | Vị trí (constraint) | Kích thước | Nền/style | Text |
|---|---|---|---|---|---|---|
| 1 | `btnBack` | AppCompatImageView | start=parent, top=parent | style `BackImageButton1` → padding 8dp, margin 12dp, `android:background=?selectableItemBackgroundBorderless` (ripple borderless, không nền) | src=`@drawable/ic_back_1` | — |
| 2 | `appCompatTextView3` | AppCompatTextView | top/bottom = btnBack, center ngang trong parent | style `ScreenTitleCommon`: wrap_content, `android:gravity=center`, singleLine | text=**"Settings"** (`@string/settings`) · 20sp · `@font/lato_bold_700` · màu `#ff171716` (`text_primary_color`) | |
| 3 | `btnLanguage` | AppCompatTextView (row) | top = btnBack.bottom | width=fill_parent, height=wrap_content | style `SettingItemText`: `background=@drawable/bg_item_setting` (bo góc 16dp, viền 1dp dash màu `#ff171716`, nền trắng), padding 20dp, marginTop 16dp, marginStart/End 20dp, drawablePadding 8dp | text=**"Language"** (`@string/language`) · 20sp (override `text_size_20`) · `lato_bold_700` · `drawableStart=@drawable/ic_setting_language` |
| 4 | `btnPrivacyPolicy` | AppCompatTextView (row) | top = btnLanguage.bottom | như trên (style `SettingItemText`, không override textSize → mặc định style không set size riêng, kế thừa theme) | text=**"Privacy Policy"** (`@string/privacy_policy`) · `lato_bold_700` · `drawableStart=@drawable/ic_setting_policy` |
| 5 | `btnTerm` | AppCompatTextView (row) | top = btnPrivacyPolicy.bottom | như trên | text=**"Term of use"** (`@string/term_of_use`) · `drawableStart=@drawable/ic_setting_term` |
| 6 | `btnShare` | AppCompatTextView (row) | top = btnTerm.bottom | như trên | text=**"Share"** (`@string/share`) · `drawableStart=@drawable/ic_setting_share` |

Ghi chú: layout KHÔNG dùng RecyclerView — 4 hàng setting là AppCompatTextView tĩnh viết thẳng
trong XML (không phải list động, không có adapter). Icon là vector drawable
(`ic_setting_language.xml`, `ic_setting_policy.xml`, `ic_setting_term.xml`, `ic_setting_share.xml`)
đặt qua `drawableStart` (không phải ImageView riêng).

### B. Visibility

| View | XML mặc định | setter runtime | điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| btnBack, appCompatTextView3, btnLanguage, btnPrivacyPolicy, btnTerm, btnShare | VISIBLE (không set `android:visibility`) | KHÔNG có — `FragmentSettings.java` chỉ override `initListener()` (gắn 5 click listener) và `provideScreenName()`. Không có `initUi()` override, không gọi `show()/gone()` cho bất kỳ view nào | Không có điều kiện PRO/EU/remote-config nào trong code | Luôn VISIBLE, 1 biến thể UI duy nhất — **không có frame ẩn/hiện theo gói hay theo vùng** |

### C/D. List & data hardcode
Không có list động. 4 hàng cố định, đúng thứ tự trên. Chuỗi resolve thật đã ghi ở bảng A.

### E. Nguồn view
Toàn bộ local drawable/string, không có ảnh runtime/remote/AD SLOT nào trên màn Settings.

### F. Hành vi click (từ `initListener()`)
- `btnBack` → `popBackStack()`.
- `btnLanguage` → điều hướng `actionFragmentSettingsToLanguagePicker(false)` (tham số `false`
  — không phải luồng onboarding).
- `btnPrivacyPolicy` → `actionSettingsToInfoFragment(CompanyInfoFragment.Type.PRIVACY_POLICY)`.
- `btnTerm` → `actionSettingsToInfoFragment(CompanyInfoFragment.Type.TERM_OF_USE)`.
- `btnShare` → `ContextExtKt.shareMyApp(context, BuildConfig.APPLICATION_ID, appName)` — mở
  Android share sheet chuẩn (`Intent.ACTION_SEND` + `Intent.createChooser`) với text
  `"https://play.google.com/store/apps/details?id=" + applicationId`. → **placeholder có nhãn**
  (share sheet OS).

### STATE
Chỉ 1 state — không có empty/loading/error, không có biến thể theo gói (free/PRO — vì không
có gói), không có biến thể theo vùng (EU/non-EU — vì không có "Privacy settings" GDPR row).

---

## 2. CompanyInfoFragment — `fragment_company_info.xml`

File: `res/layout/fragment_company_info.xml` · Java: `ui/settings/CompanyInfoFragment.java`
Đây là **1 layout dùng chung cho 2 nội dung** (enum `CompanyInfoFragment.Type`), phân biệt qua
nav-arg `infoType` truyền từ `FragmentSettingsDirections.actionSettingsToInfoFragment(type)`.

### A. Geometry

| View (id) | Loại | Vị trí | Kích thước | Nền/style | Text |
|---|---|---|---|---|---|
| `toolbarLayout` | FrameLayout | top=parent | width=fill_parent, height=wrap_content | `background=@color/window_bg_color` (`#fffffdfb`) | — |
| `tvTitle` | TextView (trong toolbarLayout) | top/bottom=btnBack, center ngang | wrap_content | style `ScreenTitleCommon` → 20sp, `lato_bold_700`, màu `#ff171716`, gravity center | text set runtime (xem dưới) |
| `btnBack` (trong toolbarLayout) | ImageView | style `BackImageButton1` | padding 8, margin 12 | src `ic_back_1`, borderless ripple | — |
| `wvPrivacyPolicy` | WebView | top=toolbarLayout.bottom, full width, height=0dp (match constraint xuống đáy) | fill_parent width, match-constraint height | — | nội dung HTML load runtime |

### B. Visibility / nội dung theo Type (từ `initUi()`)
| Type | tvTitle | WebView load URL |
|---|---|---|
| `PRIVACY_POLICY` | **"Privacy Policy"** (`@string/privacy_policy`) | `file:///android_asset/privacy_policy.html` |
| `TERM_OF_USE` | **"Term of use"** (`@string/term_of_use`) | `file:///android_asset/term_of_use.html` |

→ **2 frame riêng**: "Company Info – Privacy Policy" và "Company Info – Term of use". Cả 2 file
HTML có trong `resources/assets/privacy_policy.html` và `.../term_of_use.html` (nội dung tĩnh
bundle sẵn, không tải remote). `WebView.getSettings().setJavaScriptEnabled(true)` được bật.

### F. Hành vi
`btnBack.setOnClickListener`: disable nút rồi `popBackStack()` (tránh double-tap). Không có
điều kiện remote-config nào ảnh hưởng màn này.

### STATE
2 state = 2 loại nội dung ở trên. Không có loading/error riêng cho WebView (không bắt
`onPageFinished`/`onReceivedError` trong code đã đọc).

---

## 3. Dialog dùng chung thật của app — `popup_exit_confirm.xml`

File: `res/layout/popup_exit_confirm.xml` · Logic: `utils/PopupUtilsKt.java`
(hàm `showPopupExit()` và `showPopupConfirmDelete()`), dựng bằng `AlertDialog.Builder` +
`PopupExitConfirmBinding` (KHÔNG phải `DialogFragment`).

### A. Geometry (ConstraintLayout, width = 85% screenWidth do code set — xem dưới, height=wrap)

| id | Loại | Vị trí | Kích thước | Nền/style | Text |
|---|---|---|---|---|---|
| root | ConstraintLayout | — | width=fill_parent (bên trong dialog window đã set 85% screenWidth), padding 16dp | `background=@drawable/bg_solid_rounded_12` (nền trắng `#ffffffff`, bo góc 12dp) | — |
| `tvHeader` | AppCompatTextView | top=parent, center ngang | wrap_content | style `ScreenTitleCommon` — 20sp, `lato_bold_700`, `#ff171716`, center | xem bảng biến thể |
| `tvContent` | AppCompatTextView | top=tvHeader.bottom | fill_parent width, marginHorizontal 8dp, marginTop 8dp | gravity center | xem bảng biến thể |
| `btnCancel` | AppCompatTextView (nút trái) | top=tvContent.bottom, marginTop 16dp, start=parent, end=vCenter | width=0dp (match constraint 50%), paddingVertical 12dp | `background=@drawable/bg_white_corner_69` (bo góc 69dp = pill) tint `@color/color_E6E6E5` (`#ffe6e6e5`, xám nhạt) | 14sp, `lato_bold_700`, `includeFontPadding=false`, center — xem bảng |
| `vCenter` | Space | giữa 2 nút | 16dp × 1dp | — | — |
| `btnDelete` | AppCompatTextView (nút phải) | top/bottom = btnCancel, start=vCenter, end=parent | width=0dp (match), height=0dp (= btnCancel) | bg pill tint `@color/color_FF4342` (`#ffff4342`, đỏ) | textColor trắng, 14sp, center — xem bảng |
| `overlayView` | View trong suốt phủ toàn dialog | full constraint 4 cạnh | — | dùng để khoá double-tap khi đang xử lý click (gone mặc định, hiện tạm khi user bấm nút rồi ẩn lại) | — |

Dialog window: `setCancelable(false)` (không tap-outside-to-dismiss, không back-press-to-dismiss
mặc định vì builder base không set), background window = transparent, width = `screenWidth*0.85`,
height = WRAP_CONTENT (`-2`).

### Bảng 2 biến thể nội dung (mỗi biến thể = 1 frame riêng)

| Biến thể | Gọi từ | tvHeader | tvContent | btnCancel (trái, xám) | btnDelete (phải, đỏ) |
|---|---|---|---|---|---|
| **"Go back?"** (thoát preview) | `showPopupExit()` — gọi từ `FragmentPreviewWithMusic.handleCloseScreen()` khi user back/đóng màn Preview With Music (video ghép nhạc chưa lưu) | **"Go back ?"** (`@string/go_back`) — dùng luôn giá trị mặc định trong XML (không set lại text ở code) | **"Your video will not be save if you go back"** (`@string/your_video_will_not_be_save_if_you_go_back`) | **"No"** (mặc định XML, không set lại) | **"Yes"** (mặc định XML) |
| **"Delete video"** (xoá video đã quay) | `showPopupConfirmDelete()` — gọi từ `FragmentPlayVideo` khi bấm nút xoá | **"Delete video"** (`@string/delete_video`, set lại runtime đè text mặc định) | **"Are you sure you want to delete this video?"** (`@string/are_you_sure_you_want_to_delete_this_video`, set lại runtime) | **"Cancel"** (`@string/cancel`, set lại runtime) | **"Delete"** (`@string/delete`, set lại runtime) |

Hành vi nút (giống nhau cho cả 2 biến thể): `btnCancel` → ẩn overlay, `changeCurAlertDialog(null)`,
đóng dialog không làm gì thêm. `btnDelete`/"Yes" → gọi callback `onDeleteClick()`/`onDeleteClick()`
tương ứng (xoá video thật hoặc thực hiện thoát màn) rồi đóng dialog. `overlayView` click cũng chỉ
hiện lại chính nó (no-op an toàn tránh double click xuyên dialog).

### STATE
2 frame nội dung như trên. Không có state loading/error cho dialog này (thao tác xoá/thoát xử
lý đồng bộ ngay trong callback, không có API call chờ).

---

## 4. Loading overlay #1 — `layout_loading.xml`

File: `res/layout/layout_loading.xml`. Dùng qua `<include>` trong
`fragment_preview_with_music.xml` với `id=viewLoading`, `visibility=gone` mặc định,
`layout_width/height=fill_parent`.

### A. Geometry
FrameLayout full màn, `background=#40000000` (đen 25% alpha, phủ mờ toàn màn) chứa 1
`ProgressBar` (spinner OS mặc định) `layout_gravity=center`, không text.

### B. Visibility
Mặc định GONE trong XML (`android:visibility="gone"`). Toggle VISIBLE/GONE runtime trong
`FragmentPreviewWithMusic` khi đang xử lý `genFile()` (ghép video + nhạc, xuất file — coroutine,
decompile không đầy đủ chi tiết dòng bật/tắt do bị rút gọn bởi jadx nhưng binding `viewLoading`
tồn tại đúng mục đích "đang xử lý export"). → **STATE: loading khi export video** (overlay đen mờ
+ spinner, chặn tương tác nhờ `focusable=true clickable=true`).

---

## 5. Loading overlay #2 — `layout_loading_with_text.xml`

File: `res/layout/layout_loading_with_text.xml`. Dùng qua `<include id=viewLoading
visibility=gone>` trong `fragment_language_picker.xml` (màn Language Picker, ngoài cụm
settings-dialogs nhưng layout thuộc cụm này).

### A. Geometry
FrameLayout full màn `background=@color/transparent` (`#00ffffff`, trong suốt — khác hẳn overlay
#1 vốn đen mờ), chứa LinearLayout dọc, `gravity=center`, `background=@drawable/bg_loading_rounded`
(nền xám `#ffd3d3d3`, bo góc 12dp), padding 16dp, gồm:
- `ProgressBar` (spinner OS mặc định, không custom màu trong XML).
- `TextView` marginTop 4dp, text = **"Setting up"** (`@string/setting_up_language`).

### B. Visibility
Mặc định GONE. Hiện khi áp dụng đổi ngôn ngữ (chuyển `configLanguage`/`setLocale` + có thể
restart activity) — card bo góc + spinner + chữ "Setting up" nổi giữa màn, nền sau nó trong suốt
(không có lớp phủ đen như overlay #1).

**Khác biệt 2 loading:** #1 = full-screen dim overlay không chữ (dùng khi export video, chặn
toàn màn); #2 = card nhỏ giữa màn có chữ trạng thái, nền sau trong suốt (dùng khi đổi ngôn ngữ).
**Không có Lottie/animation trong cả 2** — chỉ `ProgressBar` (spinner OS chuẩn).

`loading_alert.xml` (mục 0.3) là của MBridge SDK, không liên quan 2 loading trên — không dựng.

---

## 6. `dot_layout.xml` — dot indicator

File: `res/layout/dot_layout.xml` — đây là layout **nội bộ mặc định của thư viện
`com.tbuonomo.viewpagerdotsindicator`** (`DotsIndicator`/`WormDotsIndicator`/`SpringDotsIndicator`
đều tự inflate layout này cho từng chấm — 1 `ImageView` 8×8dp `background=@drawable/dot_background`
trong `FrameLayout` wrap_content), KHÔNG phải file app tự vẽ tay.

**Nơi dùng trong app:** `res/layout/fragment_intro.xml` (màn Intro/Onboarding) — widget
`<com.tbuonomo.viewpagerdotsindicator.DotsIndicator id=dotsIndicator>` gắn với
`ViewPager2 id=viewPager`, cấu hình: `dotsColor=@color/gray` (`#ffc0c0c0`),
`selectedDotColor=@color/primary_color` (`#ff016cf7`), `dotsCornerRadius=2dp`, `dotsSize=4dp`,
`dotsSpacing=4dp`, `dotsWidthFactor=4.5`.

**Số chấm = 3**, khớp `IntroAdapter` trong `FragmentIntro.java` nhận
`listOf(R.drawable.img_intro_1, img_intro_2, img_intro_3)` (3 trang). Text mô tả theo trang
(`descriptionText`): trang 0 = **"Take the challenge with your friends"**, trang 1 =
**"Mix Faces, Make Fun Happen!"**, trang 2 = **"Record, Laugh, Go Viral!"**. Có
`Button nextButton` text **"Start"**, và 1 `LottieAnimationView` (`animation_view`, asset
`swipe_left.json`, loop) ẩn/hiện tuỳ trang (gợi ý vuốt).

⚠️ Remote Config mặc định `onboarding_enabled = false` → màn Intro này **KHÔNG hiển thị theo
mặc định** trong luồng app hiện tại (RC đã fetch thật, xem `_shared-context.md`). Ghi chú rõ đây
là frame phụ, không phải luồng chính. Chi tiết đầy đủ màn Intro/Onboarding thuộc cụm khác — ở
đây chỉ mô tả layout `dot_layout.xml` theo yêu cầu của cụm settings-dialogs.

---

## 7. AD SLOT dạng "fake app-open" — `dialog_native_full_screen.xml` +
   `activity_native_show_open_fake.xml`

Cả 2 layout này thuộc **`com.cem.admodule`** (module quảng cáo nội bộ, dùng chung nhiều app của
cùng nhà phát triển "cem"), được inflate bởi các class Java bị obfuscate tên gói ngắn
(`ll0/I.java`, `Il0/ll.java`) — nằm trong `com.cem.admodule.nextgen.*`.

### 7a. `dialog_native_full_screen.xml`
Dùng bởi class `ll0.I` (`DialogFragment`, theme mặc định, constructor
`super(R.layout.dialog_native_full_screen)`), field kiểu
`com.cem.admodule.manager.nativeads.NativeFullscreenConfig`/`NativeFullscreenTemplate` +
`NativeAd` (Google Mobile Ads). Layout chỉ có 1 `FrameLayout id=container_view` nền trắng full
màn — nội dung thật do `NativeManager` nạp `NativeAd` (Google AdMob) rồi bơm view quảng cáo
(icon/headline/media/CTA) vào `container_view` runtime.
→ **AD SLOT** — quảng cáo native full-screen thật (kiểu app-open/interstitial), placement lấy
từ `PlacementItem` (tên placement cụ thể không resolve được tĩnh vì đọc từ remote ad config,
KHÔNG BỊA — gắn cờ "tên placement: không resolve tĩnh được").

### 7b. `activity_native_show_open_fake.xml` — ⚠️ DARK PATTERN, ghi chú rõ bản chất
Dùng bởi class `Il0.ll` (`DialogFragment`, theme `NotHideDialog`), field kiểu
`com.cem.admodule.manager.nativeads.NativeOpenConfig`/`NativeOpenTemplate`.

**Đã verify trong code (`Il0.ll.O()`):** `txtNameApp` và `imgLogoApp` được set bằng
**`context.getPackageManager().getApplicationLabel/getApplicationIcon(context.getPackageName())`
— tức TÊN VÀ ICON CỦA CHÍNH APP FUNNY FACE**, không phải app được quảng cáo. Toàn bộ card
"đang mở lại app" này là **giao diện giả** phủ lên trên 1 quảng cáo native thật (nạp vào
`container_view`, kích thước 0×0dp co giãn theo nội dung ad) — người dùng tưởng đang thấy màn
hình "tiếp tục vào app" của Funny Face nhưng thực chất bên dưới/xung quanh là native ad, và
`imgViewClose` (icon mũi tên `baseline_arrow_forward_ios_24`) đóng vai trò như nút
"Continue"/CTA có thể trùng vùng bấm với quảng cáo.

**Geometry:**
| id | Vị trí | Kích thước | Nền | Nội dung |
|---|---|---|---|---|
| root (`main`) | full màn | fill_parent | `#80000000` (đen 50% — nền dim phía sau) | — |
| `container_view` | marginTop 8dp | 0×0dp (co theo NativeAd nạp vào) | — | **AD SLOT** (NativeAd thật, `NativeOpenTemplate`) |
| `containerName` | width 80% màn (`layout_constraintWidth_percent=0.8`) | height 40dp | `@drawable/bg_name_open_native` | card giả "tên app" |
| `imgLogoApp` | trong containerName, margin 5dp 2 bên | 25×0dp (match height card) | — | **icon = icon THẬT của app Funny Face** (lấy từ PackageManager, không phải asset ảnh cố định) |
| `txtNameApp` | cạnh icon | 0×0dp match | textSize 16sp, màu `#ff000000`, 1 dòng, ellipsize end | **= tên app "Funny Face..." (label thật của app)** |
| `txtContinueToApp` | cuối card | wrap_content × fill_parent | 13sp, màu `#ff6d6969`, `sans-serif-medium` | text tĩnh **"Continue to app"** |
| `container` (FrameLayout con) | trong containerName | wrap_content, padding start 15/end 5dp | `bg_name_open_native` | bọc 2 icon dưới |
| `imgViewClose` | trong container | 40×40dp, padding 10dp | `src=baseline_arrow_forward_ios_24` | icon mũi tên phải — trông như nút "tiếp tục", thật ra là **vùng chạm của native ad/CTA** |
| `imgDismissNative` | trong container | 40×40dp | — | nút đóng thật (`ll(ll, view) → dismiss()`) |

→ Dựng đúng layout 1:1 nhưng **BẮT BUỘC chú thích trong Figma**: "AD SLOT — Fake native app-open.
Icon/tên hiển thị = icon/tên thật của app Funny Face lấy runtime qua PackageManager (không phải
asset tĩnh), mục đích tạo cảm giác đây là màn hình của chính app trong khi vùng bấm chính là
quảng cáo native bên dưới." Đúng yêu cầu Phụ lục B mục 3.

---

## 8. res/menu — không có menu nào thuộc app

3 file duy nhất trong `res/menu/`: `axon_events_activity_menu.xml`,
`creative_debugger_displayed_ad_activity_menu.xml`, `mediation_debugger_activity_menu.xml` —
đều là menu debug của SDK mediation quảng cáo (AppLovin MAX Creative/Mediation Debugger), KHÔNG
liên quan Settings/CompanyInfo/dialog nào của app. Không có `getMenuInflater()` nào trong
`FragmentSettings`/`CompanyInfoFragment`.

---

## 9. Toast vs Dialog vs Snackbar — kết luận sau khi đọc code

- **Toast thật** (`android.widget.Toast`, qua `ContextExtKt.toastMessageShortTime/LongTime`):
  dùng cho lỗi vặt như share text lỗi, không có app email, thiết bị không mở được Play Store —
  KHÔNG liên quan Settings/CompanyInfo trực tiếp nhưng là cơ chế dùng chung toàn app.
- **Dialog thật dùng chung** duy nhất: `popup_exit_confirm.xml` (mục 3) — `AlertDialog` chuẩn
  Android, không phải `BottomSheetDialog`.
- **Không tìm thấy Snackbar** nào trong package app (`Snackbar.make` không xuất hiện ở
  `com/cem/face/puzzle/**`).
- `BaseDialogFragment` (mục app tự viết, theme `FullScreenDialog`) chỉ có 1 class con thật sự
  kế thừa trong toàn app: `DialogFragmentSoundPicker` (chọn nhạc nền) — đây là dialog full-screen
  riêng của tính năng ghép nhạc, KHÔNG phải dialog dùng chung cho nhiều màn, nên không thuộc
  phạm vi "dialog dùng chung" của cụm này (thuộc cụm màn ghép nhạc/preview nếu có).

---

## 10. Tóm tắt STATE toàn cụm

1. Settings — 1 state duy nhất (không PRO/EU/loading/error).
2. Company Info — 2 state: Privacy Policy / Term of Use.
3. Popup xác nhận dùng chung — 2 state nội dung: "Go back?" (thoát preview) / "Delete video?"
   (xoá video).
4. Loading overlay #1 (export video, full-screen dim + spinner) — 2 state: hidden/visible.
5. Loading overlay #2 (đổi ngôn ngữ, card "Setting up") — 2 state: hidden/visible.
6. Dot indicator (Intro, 3 trang) — 3 state vị trí trang, và 1 cờ "ẩn theo mặc định vì
   `onboarding_enabled=false`".
7. AD SLOT fake app-open (`activity_native_show_open_fake.xml`) — 1 state hiển thị (không có
   biến thể nội dung khác ngoài dữ liệu ad runtime).
8. AD SLOT native full-screen (`dialog_native_full_screen.xml`) — 1 state hiển thị.

Tổng: **~8 "màn/dialog" logic**, trong đó 2 là AD SLOT dark-pattern cần chú thích riêng, 2 là
loading (không Lottie), 1 dot indicator thuộc luồng bị tắt mặc định theo RC.

---

## 11. Cờ / chỗ chưa resolve tĩnh được

- Tên placement quảng cáo cụ thể cho `dialog_native_full_screen.xml` /
  `activity_native_show_open_fake.xml`: đọc từ `PlacementItem` truyền vào runtime (từ remote ad
  config `monet`/`monet_v2`/`monet_super`/`and_ads_test`), không resolve tĩnh được từ layout/Java
  đã đọc — **CỜ, không bịa tên placement**.
- Logic bật/tắt chính xác của `viewLoading` (`layout_loading.xml`) trong
  `FragmentPreviewWithMusic.genFile()`: coroutine bị jadx dump lỗi một phần
  ("Method dump skipped... To view this dump add '--comments-level debug'"), nên không trích
  được dòng `.visible()/.gone()` chính xác — nhưng mục đích sử dụng (overlay loading khi export)
  suy được chắc chắn từ tên id `viewLoading`, vị trí include, và ngữ cảnh gọi `genFile()`.
