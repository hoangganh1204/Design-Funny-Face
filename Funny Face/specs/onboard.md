# Cụm "onboard" — FragmentSplash → FragmentIntro / FragmentLanguagePicker

Nav graph: `res/navigation/main_nav.xml`, `app:startDestination="@id/fragmentSplash"` (dòng 2).
3 destination trong cụm:
- `@id/fragmentSplash` → `com.cem.face.puzzle.ui.onboard.FragmentSplash` (dòng 52-56)
- `@id/fragmentLanguagePicker` → `com.cem.face.puzzle.ui.language.FragmentLanguagePicker` (dòng 58-62, có argument `isFromSplash: boolean`)
- `@id/fragmentIntro` → `com.cem.face.puzzle.ui.onboard.FragmentIntro` (dòng 77-78)

Canvas 360×800dp, không vẽ status bar.

---

## 0. XÁC MINH REMOTE CONFIG (mục đặc biệt #1)

File: `utils/FeatureFlag.java` (implements `utils/IFeatureFlag.java`), inject vào cả 3 fragment qua `@Inject public IFeatureFlag featureFlag`.

| Flag interface | Key Firebase RC đọc thật (`FeatureFlag.kt` decompiled) | RC đã fetch (`/tmp/rc.json`) |
|---|---|---|
| `languageEnabled()` | `FirebaseRemoteManager.getBoolean("language_enabled")` | `false` |
| `onboardingEnabled()` | `FirebaseRemoteManager.getBoolean("onboarding_enabled")` | `false` |
| `onboardingButtonsEnabled()` | `FirebaseRemoteManager.getBoolean("onboarding_buttons_enabled")` | `true` |

Key trùng khớp 100% với tên RC đã fetch → 3 flag này đọc đúng key đã cho.

**Default khi CHƯA fetch được RC**: `FirebaseRemoteManager.getBoolean()` (`admodule/analytics/config/firebase/FirebaseRemoteManager.java:25-45`) bọc try/catch quanh `RemoteConfig.getBoolean(key)`; nếu lỗi/chưa có giá trị, `bool == null` → hàm trả về `false` cứng (dòng 43-44). Không set default XML nào khác được thấy trong repo. Vậy default-trước-khi-fetch của `language_enabled` và `onboarding_enabled` **cũng là `false`** — khớp với giá trị RC đã fetch → nhánh mặc định ổn định dù server chưa trả lời.

**Luồng rẽ nhánh thật** — `FragmentSplash.goToInside()` (`ui/onboard/FragmentSplash.java:42-49`):
```
actionSplashToIntro =
  (isLanguagePickerPassed() || !languageEnabled())
    ? (isFirstInstall() && onboardingEnabled())
        ? actionSplashToIntro()
        : (isShowHomeNewUI() ? actionSplashToHome() : actionSplashToHomeOldUI())
    : actionSplashToLanguagePicker(isFromSplash = true)
```
Với `language_enabled=false` → điều kiện `!languageEnabled()` = true → **luôn bỏ qua nhánh language picker từ Splash**, bất kể `isLanguagePickerPassed()`.
Với `onboarding_enabled=false` → điều kiện trong `(isFirstInstall() && onboardingEnabled())` luôn false → **luôn bỏ qua Intro**.
⇒ **Nhánh mặc định thật của cả cụm: Splash → Home thẳng** (bỏ qua cả Language Picker lẫn Intro). `isShowHomeNewUI()` (`CemViewModel.isShowHomeNewUI()` = `uiHomeShowCase()==1`, đọc key `ui_home_show_case` default 0 khi lỗi) — RC fetch `ui_home_show_case=1` ⇒ `actionSplashToHome()` (Home UI mới), không phải `actionSplashToHomeOldUI()`.

⚠️ **FragmentIntro và FragmentLanguagePicker VẪN PHẢI dựng** theo yêu cầu — chúng là destination thật trong nav graph và có thể vào bằng tay (Settings → `action_fragmentSettingsToLanguagePicker`, hoặc khi RC bật lại 2 flag). Ghi rõ trong spec: **đây là nhánh KHÔNG mặc định**.

`onboarding_buttons_enabled=true` (RC) ảnh hưởng **FragmentIntro**: xem mục 2.B.

---

## 1. FragmentSplash

Source: `ui/onboard/FragmentSplash.java` (không tự inflate binding raw, dùng `FragmentSplashBinding`).
Layout: `layout/fragment_splash.xml` (resolve qua tool, xem raw constraints để có geometry vì tool không in `app:layout_constraint*`).

### A. Geometry
Root: `ConstraintLayout`, `fill_parent × fill_parent`, `android:background="@drawable/bg_splash"` (vector 375×812dp, path fill `@drawable/$bg_splash__0`). Đã mở `$bg_splash__0.xml` (aapt-inline gradient tách riêng bởi apktool): **linear gradient dọc**, `angle=0`, trục từ `(187.5,0)` đến `(187.5,812)` (đúng tâm-trên → tâm-dưới, phủ toàn bộ chiều cao 812dp) — `offset 0.0 = #ffffffff` (trắng, đỉnh) → `offset 1.0 = #ff08bdff` (xanh cyan, đáy). Nền Splash = gradient trắng→xanh dương cyan từ trên xuống dưới, không phải solid color, không phải ảnh raster.

| id | vai trò | vị trí (constraint) | w×h | style/thuộc tính khác |
|---|---|---|---|---|
| `lineCenterY` | Guideline horizontal | `layout_constraintGuide_percent=0.46` (46% chiều cao) | 0×0 | ẩn, chỉ để neo |
| `ic_logo` | AppCompatImageView logo app | top=parent, start=parent, end=parent, bottom→`lineCenterY` | wrap×wrap | `srcCompat=@drawable/ic_splash` (PNG), `adjustViewBounds=true` |
| `progress` | ProgressBar (ngang) | top→`ic_logo`.bottom, start/end=parent, bottom→`tvLoading`.top, marginTop=16dp | width 60% parent (`layout_constraintWidth_percent=0.6`) × wrap | `style=@style/CustomProgressBar` (xem dưới), `max=100`, `progress=0` khởi tạo XML |
| `tvLoading` | AppCompatTextView "Loading..." | top→`progress`.bottom, start/end=parent, marginTop=`@dimen/size_16`=16dp | wrap×wrap | text=`@string/loading`="Loading...", `style=@style/ScreenTitleCommon`: size 20sp, `text_primary_color` `#ff171716`, gravity center, `singleLine=true`, font `@font/lato_bold_700` |
| `adContainer` | FrameLayout — **AD SLOT** | top→`tvLoading`.bottom, bottom→`tvNote`.top, start/end=parent, margin 16dp (trái/phải/trên qua `layout_marginHorizontal` + riêng trái/phải/trên = `size_16`) | width=match(0dp)×wrap | rỗng trong XML, code inflate native ad runtime |
| `tvNote` | AppCompatTextView "This action contain ads" | bottom=parent, start/end=parent, marginBottom=`size_16`=16dp | wrap×wrap | text=`@string/this_action_contain_ads`, style `ScreenTitleCommon` (20sp, bold, center, `#ff171716`) |
| `config` | `View` ẩn (Monet dev-mode trigger, tap ẩn để mở developer ads panel) | top=parent, start=parent | 150×150dp | không background, không hiển thị nội dung, chỉ hitbox |

`CustomProgressBar` style (`values/styles.xml:2995-3000`): `maxHeight=20dp`, `minHeight=10dp`, `progressDrawable=@drawable/custom_progress_with_image` = layer-list: nền bo góc 8dp fill trắng `#ffffffff` viền 1dp `#1a000000`, phần progress là clip-shape bo góc 8dp màu tím `#ff7a00e2`.

### B. Visibility
| view | XML mặc định | setter runtime | điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| tất cả view tĩnh (logo, progress, tvLoading, tvNote, config) | VISIBLE | không có setter ẩn/hiện nào trong `initUi()` | — | luôn VISIBLE trong suốt vòng đời Splash |
| `adContainer` | rỗng nhưng VISIBLE (FrameLayout) | `NativeManager.present(...)` inflate native ad "native_splash" (Style6 template) vào bên trong nếu load được; nếu lỗi/timeout thì vẫn rỗng | native ad load thành công hay không (network, fill-rate) | **STATE A** (ad có) / **STATE B** (ad trống, container 0dp cao do `wrap_content` + không con) |
| Interstitial "inter_splash" | không phải view trong layout — full-screen overlay của SDK ads (`FullscreenManager.present`) | hiện full-màn hình đè lên Splash một khoảng thời gian trước khi `goToInside()` | luôn cố gắng present nếu load kịp trong khi progress đang chạy | **placeholder có nhãn**: "Interstitial full-screen ad (inter_splash)" |

### C. List
Không có RecyclerView/ViewPager trong Splash.

### D. Data hardcode
- `tvLoading` = "Loading..." (`@string/loading`)
- `tvNote` = "This action contain ads" (`@string/this_action_contain_ads`)
- `progress.max = 100`, animate 0→100 lặp vô hạn: `ObjectAnimator.ofInt(progress,"progress",0,100)`, `duration=1500L`, `repeatCount=-1 (INFINITE)`, `repeatMode=REVERSE (1)`, `LinearInterpolator` (`initUi()` dòng 126-132) — progress bar CHẠY VÔ HẠN LẶP LẠI, không phản ánh % tải thật, chỉ là animation trang trí trong lúc chờ SDK ads + điều hướng.

### E. Nguồn từng view
- `ic_logo` → local drawable `@drawable/ic_splash` (PNG bundled trong app).
- `adContainer` → **AD SLOT**, placement `native_splash` (const `AdKey.NATIVE_SPLASH`), template `NativeFixedTemplate.Style6` (`AdsUtils.getNativeStyle6Template`), load qua `NativeManager.present(...)` (`FragmentSplash.loadAndShowNative`, smali dòng 502-609).
- Interstitial → **AD SLOT**, placement `inter_splash` (const `AdKey.INTER_SPLASH`), `FullscreenManager.present(activity, "inter_splash", false, ...)` (smali dòng 623-627).
- `config` view → không phải content người dùng thấy, là hook debug (`Monet.setupDeveloperMode`).

### F. Nhánh remote-config / luồng
`initUi()` (`FragmentSplash.java:110-134`):
1. `Monet.setupDeveloperMode(config, context)` — bind `config` view làm cổng vào panel debug ads (long-press ẩn).
2. `Monet.blockDefaultOpenAds()`.
3. Log event `splash_view` (`EventTrackingConst.SPLASH_VIEW`).
4. `ContextExtKt.setLocale(context, sharedViewModel.currentLanguage.code)` — áp locale đã lưu (mặc định "en" nếu chưa từng chọn — xem mục 3.D).
5. Setup progress animation (mục D).
6. `loadAndShowInterAd()` → gọi `loadAndShowNative()`:
   - `Monet.start(activity, "monet_super", "open_ads", banPickScenario)` khởi động SDK ads với `BanPickScenario` từ `makeBanPickScenario()` (map các placement Home/Language/Intro cần "cấm" hiện song song tuỳ trạng thái first-install/feature-flag — chi tiết dùng nội bộ SDK ads, không hiển thị UI).
   - present native `native_splash` vào `adContainer`.
   - present interstitial `inter_splash`.
   - Cuối cùng, nếu fragment còn `isAdded()` và lifecycle ≥ STARTED → gọi `goToInside()` (mục 0) → điều hướng.

### STATE (Splash)
1. **Loading mặc định** (duy nhất theo UI-state, vì mọi view tĩnh luôn hiển thị) — progress bar đang chạy loop, native ad có thể có/không có (2 biến thể nhỏ của `adContainer`), sau đó tự động chuyển màn (không cần thao tác người dùng). Không có ô nhập liệu, không có lỗi hiển thị riêng trên UI này.
2. GDPR/UMP consent: **KHÔNG** có trong layout hay code của `FragmentSplash` — không tìm thấy lời gọi consent form trong fragment này (được xử lý ở tầng khác ngoài cụm "onboard", ví dụ Activity/`Monet.start`). Flag: nếu cần dựng consent dialog thì đó là UI hệ thống của SDK ads, không thuộc layout `fragment_splash.xml` — **placeholder có nhãn "UMP/GDPR consent (SDK, ngoài layout)"**.

---

## 2. FragmentIntro (ViewPager, 3 trang)

Source: `ui/onboard/FragmentIntro.java`; adapter ảnh `defpackage/IntroAdapter.java` (item `layout/item_intro.xml`); item text lấy từ code, không từ adapter riêng.
Layout: `layout/fragment_intro.xml`.

### A. Geometry
Root `ConstraintLayout` fill×fill.

| id | vai trò | vị trí | w×h | ghi chú |
|---|---|---|---|---|
| `viewPager` | `ViewPager2` (androidx.viewpager2) | top=parent, start/end=parent | width match(0dp) × wrap_content | chứa 3 trang ảnh full-bleed |
| `bottomView` | LinearLayout (vertical) — vùng chữ + control bar | bottom→`adContainer`.top, start/end=parent, marginBottom=16dp | width match(0dp) × wrap | chứa `descriptionText` + `controlBar` |
| `descriptionText` | TextView mô tả trang hiện tại | (trong bottomView) | fill_parent × wrap | textSize 16sp, gravity center, font `@font/lato_semibold_600`, không màu cố định trong XML (kế thừa mặc định TextView đen) |
| `controlBar` | LinearLayout (horizontal) — thanh dots + nút | (trong bottomView) | fill_parent × 30dp | `visibility="gone"` mặc định trong XML, gravity center\|bottom |
| — Space | spacer trái | trong controlBar | 16dp × wrap | |
| `dotsIndicator` | `DotsIndicator` (tbuonomo lib) — chỉ báo trang | trong controlBar | wrap × wrap | `paddingBottom=6dp`, `dotsColor=@color/gray(#ffc0c0c0)`, `dotsCornerRadius=2dp`, `dotsSize=4dp`, `dotsSpacing=4dp`, `dotsWidthFactor=4.5`, `selectedDotColor=@color/primary_color(#ff016cf7)`, `progressMode=false` |
| — Space | spacer giãn | trong controlBar | 0dp × wrap, `layout_weight=1` | đẩy nút Start sang phải |
| `nextButton` | Button "Start"/next | trong controlBar | wrap × wrap | text=`@string/start`="Start", textSize 16sp, `textColor=@color/button_text_color` (selector: disabled→`gray #ffc0c0c0`, enabled→`primary_color #ff016cf7`), `background=transparent`, padding ngang 20dp, `textAllCaps=false`, font `@font/lato_bold_700` |
| `adContainer` | FrameLayout — **AD SLOT** | bottom=parent, start/end=parent, marginTop=16dp | fill_parent × wrap | native ad, 1 slot dùng lại cho cả 3 trang (key đổi theo trang, xem F) |
| `animation_view` | `LottieAnimationView` — hint vuốt tay | top/bottom/start/end=parent (full overlay) | wrap × 150dp | `visibility="invisible"` mặc định; `app:lottie_fileName="swipe_left.json"`, `lottie_loop=true` — **animation**: asset gốc `assets/swipe_left.json` |

Item `item_intro.xml` (mỗi trang ViewPager): `FrameLayout` fill×fill chứa 1 `ImageView` id `imageView`, fill×fill, `scaleType=centerCrop` — ảnh minh hoạ full-bleed.

### B. Visibility
| view | XML mặc định | setter runtime | điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| `controlBar` (dots + nút Start) | GONE | `ViewExtKt.visible(controlBar)` / `gone(controlBar)` trong `initUi()` (`FragmentIntro.java:245-253`) | `featureFlag.onboardingButtonsEnabled()` | RC = `true` (default) ⇒ **VISIBLE** (nhánh mặc định: có dots + nút Start). Nếu flag `false` (không mặc định) ⇒ GONE, điều hướng chỉ bằng vuốt tay + Lottie hint. |
| `animation_view` (Lottie vuốt tay) | INVISIBLE | `visible()+playAnimation()` tại trang 0 (delay 500ms, `setupViewPager$1$onPageSelected$1`) và trang 1 lần đầu (`onPageSelected$2`, chỉ nếu `!hasShownOnboardStory`); `pauseAnimation()+gone()` khi vào trang 2 | chỉ chạy nhánh này khi `!onboardingButtonsEnabled()` (trang 1) — trang 0 luôn chạy show bất kể flag (đoạn code trang 0 không check flag) | Với flag mặc định `true`: Lottie **vẫn được show ở trang 0** sau 500ms (không bị chặn bởi flag), nhưng ở trang 1 sẽ **không** tự show lại (điều kiện chặn bởi flag) — trang 2 luôn ẩn Lottie. |
| `nextButton` | enabled tuỳ trạng thái | `lockContinueButton()`: set `enabled=false`, sau 500ms set `enabled=true` (delay tránh double-click) | gọi mỗi khi `onboardingButtonsEnabled()=true` và mỗi lần `onPageSelected` trang 0 hoặc trang 1 | Nút bị khoá 500ms mỗi lần đổi trang 0/1 rồi tự mở lại |
| `descriptionText` | text rỗng trong XML | set text theo `position` mỗi lần `onPageSelected` | trang 0/1/2 | xem mục D |

### C. List — ViewPager2 3 trang
`setupViewPager()` (`FragmentIntro.java:117-118`): `IntroAdapter(listOf(R.drawable.img_intro_1, R.drawable.img_intro_2, R.drawable.img_intro_3))` — **ĐÚNG 3 trang, cố định, hardcode trong code** (không phải từ remote/DB):

| # (index) | ảnh (`item_intro.imageView`) | `descriptionText` (theo `onPageSelected`, `FragmentIntro.java:161`) | ad placement trang này |
|---|---|---|---|
| 0 | `@drawable/img_intro_1` | `@string/mix_faces_make_fun` = **"Mix Faces, Make Fun Happen!"** | `native_onboard` (`AdKey.NATIVE_INTRO_1`) |
| 1 | `@drawable/img_intro_2` | `@string/take_the_challenge` = **"Take the challenge with your friends"** | `native_onboard2` (`AdKey.NATIVE_INTRO_2`) |
| 2 | `@drawable/img_intro_3` | `@string/record_laugh` = **"Record, Laugh, Go Viral!"** | `native_onboard3` (`AdKey.NATIVE_INTRO_3`) |

**RULING (đã truy đến tận cùng, KHÔNG còn là "thiếu trong dump")**: `img_intro_1/2/3` **THỰC SỰ KHÔNG TỒN TẠI trong APK**, đây là sự thật của bản build, không phải giới hạn của công cụ giải nén. Bằng chứng:
- `R.java:157-159` / `R$drawable.smali:133-137`: id khai báo đủ 3 hằng `img_intro_1=0x7f080248`, `img_intro_2=0x7f080249`, `img_intro_3=0x7f08024a`, và `FragmentIntro.java:118` dùng đúng 3 id này trong `IntroAdapter`.
- `values/public.xml` **không có entry** cho 3 id trên — bảng nhảy thẳng từ `0x7f080247` (`img_banner_funny_puzzle`) sang `0x7f08024b` (`img_notify_puzzle`).
- `resolve-arsc.py apk/app.apk 0x7f080248` → NULL ở mọi config (không có bất kỳ biến thể density/locale nào trỏ tới entry này).
- `unzip -l app.apk` → không có file nào tên `img_intro*` trong bất kỳ bucket `res/` nào.
- Đã loại trừ khả năng split APK (không có `lib/`, không có `split_*.apk`, có `resources.arsc` đầy đủ 1 file) → không phải do thiếu 1 split chứa ảnh.

⇒ Nguyên nhân nhiều khả năng: resource shrinking lúc build, hoặc dấu vết còn sót của quá trình reskin app (`AndroidManifest` khai báo package `com.filter.face.puzzle` nhưng code namespace là `com.cem.face.puzzle` — bản build gốc có thể đã tham chiếu ảnh khác cho 3 slot này rồi bị strip khi đóng gói bản reskin).

**Quyết định dựng Figma**: vẫn dựng đủ 3 frame Intro (geometry/role ImageView full-bleed `centerCrop` đã xác định chắc chắn), nhưng ô ảnh phải là **PLACEHOLDER CÓ NHÃN** ghi rõ `"img_intro_1 — không có trong APK"` / `"img_intro_2 — không có trong APK"` / `"img_intro_3 — không có trong APK"`. TUYỆT ĐỐI không thay bằng ảnh tự chọn, ảnh nhân vật gần giống, hay bất kỳ suy đoán nội dung nào — đây là giới hạn thật của APK nguồn, phải ghi nhận nguyên trạng, không âm thầm thay thế.

Mapping trang→ad key xác nhận từ smali `FragmentIntro$loadAdIfNeed$1.smali:375-397` (switch theo `$page`: 0→"native_onboard", 1→"native_onboard2", 2→"native_onboard3"), gọi trong `loadAdIfNeed(page)` mỗi lần `onPageSelected` (mục F) và trong `onResume()`. Cơ chế `traveledPages: Set<Int>` **đã xác nhận rõ trong smali** (dòng 340-353): đầu hàm `invokeSuspend` check `traveledPages.contains(page)` — **nếu đã có trong set → return sớm, KHÔNG load/hiện lại ad**; chỉ khi chưa có mới add page vào set (dòng 354-362, sau đoạn check) rồi tiến hành load native ad. Kết luận dứt khoát: **mỗi trang chỉ load ad đúng 1 lần trong vòng đời Fragment** (lần đầu `onPageSelected` hoặc `onResume` chạm trang đó); quay lại trang đã xem trước đó sẽ KHÔNG load/hiện lại ad (ô `adContainer` giữ nguyên trạng thái cũ, kể cả rỗng nếu lần đầu load lỗi).

### D. Data hardcode
Xem bảng ở mục C. Ngoài ra:
- `nextButton` text = `@string/start` = "Start" (cố định cho mọi trang, không đổi theo trang cuối/giữa).
- Event analytics theo trang (`smali` dòng 525-537): `onboarding_1_view`, `onboarding_2_view`, `onboarding_3_view`.

### E. Nguồn từng view
- `img_intro_1/2/3` → local drawable bundled (không tìm thấy file nhị phân trong dump, xem cảnh báo mục C).
- `adContainer` (3 khoá theo trang) → **AD SLOT**: `native_onboard` / `native_onboard2` / `native_onboard3`, template `NativeFixedTemplate` qua `NativeManager.present` (giống cơ chế Splash/Language).
- `animation_view` → **animation**: Lottie `swipe_left.json` (`assets/swipe_left.json`, đã liệt kê trong shared-context).
- Nút "Start" khi ở trang 0 + bấm: trigger thêm 1 interstitial **AD SLOT** `native_fullscreen_onboard` (`AdKey.INTER_INTRO`) qua `LifeCycleExtKt.loadShowFullscreenSafe` (`FragmentIntro$initUi$2$1.java`) TRƯỚC KHI chuyển sang trang kế — luôn chạy bất kể `hasShownOnboardStory` (flag chỉ set `true`, không có nhánh gọi lại từ đây khi bấm nút — xảy ra ở mọi lần bấm Next tại trang 0).

### F. Nhánh remote-config
- `onboardingButtonsEnabled()` (RC `onboarding_buttons_enabled`, default `true`) quyết định:
  - `true` (mặc định): hiện `controlBar` (dots + Start), điều hướng chủ động qua nút bấm; nhánh check trong `onPageScrolled`/`onPageSelected` phụ thuộc `!onboardingButtonsEnabled()` bị bỏ qua (không auto-finish khi vuốt tới cuối, không auto-show Lottie ở trang 1).
  - `false` (không mặc định): ẩn `controlBar`, cho phép vuốt tự do; tại trang cuối vuốt xong 1 lần thì tự "finish()" sang Home (logic đếm `counter`/`alreadyFinished` trong `onPageScrolled`, `FragmentIntro.java:132-149`); Lottie tay vuốt hiện ở trang 0 (500ms) và trang 1 (nếu chưa từng hiện) để hướng dẫn.
- Điều hướng cuối (`finish()`, `FragmentIntro.java:57-60`): `setIntroNoPassed(false)` rồi `actionIntroToHome()` — luôn về Home (không phân nhánh Home mới/cũ tại đây, khác với Splash/LanguagePicker).

### STATE (Intro)
1. **Trang 0** — flag buttons=true (mặc định): ảnh img_intro_1, text "Mix Faces, Make Fun Happen!", controlBar visible, nextButton khoá 500ms rồi mở, Lottie hiện overlay sau 500ms (dù buttons bật), ad `native_onboard` load vào adContainer.
2. **Trang 1**: ảnh img_intro_2, text "Take the challenge with your friends", nextButton khoá/mở lại, ad `native_onboard2`.
3. **Trang 2 (cuối)**: ảnh img_intro_3, text "Record, Laugh, Go Viral!", Lottie ẩn, nút đổi vai trò → bấm sẽ `finish()` sang Home, ad `native_onboard3`.
4. **Biến thể ad rỗng** cho mỗi trang nếu native ad không load kịp (adContainer trống).
5. **Nhánh flag=false** (không mặc định, để tham khảo khi RC bật): controlBar ẩn, điều hướng bằng vuốt + swipe-hint Lottie, tại trang cuối tự "finish()" sau khi dừng vuốt.

---

## 3. FragmentLanguagePicker

Source: `ui/language/FragmentLanguagePicker.java`; adapter `ui/language/AdapterLanguage.java` (extends `BaseAdapter<ItemLanguageBinding, LanguageUI>`); model `com.cem.domain.model.LanguageUI` (name, code).
Layout: `layout/fragment_language_picker.xml`, item `layout/item_language.xml`, include `layout/layout_loading_with_text.xml`.
Argument nav: `isFromSplash: Boolean` (bắt buộc, không default) — điều khiển nút Back, hành vi finish/back, và nguồn ngôn ngữ khởi động đã chọn sẵn.

### A. Geometry
Root `ConstraintLayout` fill×fill.

| id | vai trò | vị trí | w×h | style/text |
|---|---|---|---|---|
| `btnBack` | AppCompatImageView back | start=parent, top=parent | `@style/Base.PrimaryButton.Square` → 48×48dp | `style=@style/BackImageButton1` (parent `Base.PrimaryButton.Square`): padding 8dp, margin 12dp, `src=@drawable/ic_back_1`, background `?selectableItemBackgroundBorderless` |
| `appCompatTextView4` | AppCompatTextView tiêu đề "Language" | bottom/top→`btnBack`, start/end=parent (canh giữa ngang màn hình, cùng hàng btnBack) | wrap×wrap | text=`@string/language`="Language", style `ScreenTitleCommon` (20sp, bold, center, `#ff171716`) |
| `btnDone` | AppCompatImageView nút xác nhận (dấu tick) | bottom/top→`btnBack`, end=parent, marginEnd=12dp | style `Base.PrimaryButton.Square` 48×48dp | `src=@drawable/ic_tick_selector` (selector: disabled→`ic_tick_disabled`, enabled→`ic_tick`) |
| `rvLanguage` | RecyclerView danh sách ngôn ngữ | top→`btnBack`.bottom, bottom→`adContainer`.top, marginBottom=8dp | fill_parent × match(0dp) | `layoutManager=LinearLayoutManager` (khai báo thẳng trong XML `app:layoutManager`) |
| `adContainer` | FrameLayout — **AD SLOT** | bottom=parent, start/end=parent, marginTop=16dp | fill_parent × wrap | native ad, dùng lại chung 1 container cho cả 2 lượt ad (xem F) |
| `viewLoading` (`<include>`) | overlay loading toàn màn hình | fill×fill, đè lên trên cùng | `visibility="gone"` mặc định | include `layout/layout_loading_with_text.xml` |

`layout_loading_with_text.xml`: `FrameLayout` nền `@color/transparent`, `focusable/clickable=true` (chặn tương tác xuyên qua), chứa `LinearLayout` center, nền `@drawable/bg_loading_rounded` (bo góc 12dp, fill `#ffd3d3d3`), padding 16dp: 1 `ProgressBar` (spinner tròn mặc định) + `TextView` "Setting up" (`@string/setting_up_language`, marginTop 4dp).

Item `item_language.xml`: `AppCompatTextView` id `tvItemLanguage`, `fill_parent × wrap_content`, textSize 20sp, `drawableStart=@drawable/ic_check_box` (selector: `state_selected=true` → `ic_check_box_selected`, else → `ic_check_box_unselected`), style `@style/SettingItemText` (đã đọc TRỌN, `values/styles.xml:3567-3577`): `gravity=center_vertical`, `background=@drawable/bg_item_setting`, padding 20dp mọi phía, `layout_marginTop=16dp` + `layout_marginStart=20dp` + `layout_marginEnd=20dp` (khoảng cách giữa các item VÀ lề trái/phải so với `rvLanguage`), `drawablePadding=8dp`, font `@font/lato_bold_700`. `text` runtime = `languageUI.name`.

`bg_item_setting.xml` (đã mở TRỌN — `res/drawable/bg_item_setting.xml`): `<shape>` **tĩnh, KHÔNG phải `<selector>`** — viền nét đứt (`stroke width=1dp color=@color/text_primary_color(#ff171716) dashWidth=8dp dashGap=6dp`), bo góc `16dp`, nền fill `@color/white(#ffffffff)`. **RULING**: nền item KHÔNG đổi màu theo trạng thái `selected` (không có state-list nào cho background) — điểm khác biệt DUY NHẤT giữa item chọn/chưa chọn là icon `drawableStart` đổi (`ic_check_box_selected` ↔ `ic_check_box_unselected`); màu chữ/nền item giữ nguyên trắng + viền đen nét đứt trong mọi trạng thái.

### B. Visibility
| view | XML mặc định | setter runtime | điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| `btnBack` | `visibility` không set trong XML → mặc định VISIBLE | `btnBack.setVisibility(isFromSplash ? 4 : 0)` — dùng số nguyên trực tiếp, `4=INVISIBLE` | `args.isFromSplash()` | Từ Splash (`isFromSplash=true`) ⇒ **INVISIBLE** (chiếm chỗ nhưng không thấy — không phải GONE); Từ nơi khác (Settings, `isFromSplash=false`) ⇒ VISIBLE |
| `btnDone` | enabled mặc định true trong XML nhưng code set `setEnabled(false)` ngay trong `initUi()` cuối hàm (dòng 271) | `setEnabled(true)` khi người dùng chọn 1 ngôn ngữ trong list (`initUi$lambda$0$0`) | đã tap chọn ngôn ngữ hay chưa | Ban đầu **disabled** (icon `ic_tick_disabled`, không bấm được) → sau khi chọn ngôn ngữ bất kỳ **enabled** (icon `ic_tick`) |
| `viewLoading` include | GONE | `showLoading(timeout)` → `visible()`; `hideLoading()` → cancel job + `gone()` | **đã grep toàn bộ smali `FragmentLanguagePicker.smali` + mọi file trong package `ui/language/`: `showLoading(J)V` KHÔNG có lời gọi `invoke-direct`/`invoke-virtual` nào tới nó ở bất kỳ đâu ngoài định nghĩa của chính nó** | **RULING dứt khoát**: `showLoading()` là dead code trong bản build này — `viewLoading` overlay ("Setting up" + spinner) **KHÔNG BAO GIỜ được hiện** trong luồng UI hiện tại của `FragmentLanguagePicker`, mãi mãi GONE. Chỉ `hideLoading()` tồn tại nhưng vô nghĩa vì không có gì để ẩn. Dựng Figma: KHÔNG cần frame "loading overlay" cho màn này — nếu muốn ghi nhận vẫn để 1 state phụ ghi rõ "code path chết, không xuất hiện trong app thật". |
| `adContainer` | rỗng, VISIBLE | inflate native ad `native_language` lúc `initUi()`, đổi sang `native_language2` khi chọn ngôn ngữ lần đầu | xem F | 2 trạng thái nối tiếp nhau |

### C. List — RecyclerView `rvLanguage`
Nguồn dữ liệu: **hardcode trong code**, KHÔNG phải từ `values-<lang>/` (dù RES có >90 thư mục `values-<lang>` từ các SDK bên thứ 3, KHÔNG liên quan tới list này).

`AppSetting.kt` (`data/system/AppSetting.java:44`, field `listLanguage`):
```
listOf(
  LanguageEntity("English", "en"),
  LanguageEntity("Hindi", "hi"),
  LanguageEntity("Spanish", "es"),
  LanguageEntity("French", "fr"),
  LanguageEntity("Portuguese", "pt"),
  LanguageEntity("Vietnamese", "vi"),
  LanguageEntity("Japanese", "ja"),
)
```
→ **ĐÚNG 7 ngôn ngữ, thứ tự cố định**: English(en), Hindi(hi), Spanish(es), French(fr), Portuguese(pt), Vietnamese(vi), Japanese(ja). Không có ngôn ngữ nào bị ghim khác vị trí — thứ tự hiển thị = thứ tự khai báo, KHÔNG sort theo alphabet.

Đường đi dữ liệu: `AppSetting.listLanguage` → `AppSettingRepositoryImpl.getListLanguages()` (map `LanguageEntity`→`LanguageUI` qua `MapperKt.toLanguageUI`) → `SharedViewModel.listLanguage` (field khởi tạo 1 lần trong constructor) → `AdapterLanguage.updateAll(sharedViewModel.getListLanguage())` (`FragmentLanguagePicker.initUi()` dòng 207).

Không có item chèn thêm bởi code (không có ô "Add", không có ô ad-item trong list — ad nằm ở `adContainer` riêng bên dưới, không phải 1 item trong RecyclerView).

**Item row** (`AdapterLanguage.onBindData`, `AdapterLanguage.java:85-99`): text = `language.name` (đúng 1 trong 7 tên ở trên, tiếng Anh, không dịch theo locale hiện tại), `tvItemLanguage.setSelected(...)` = true nếu là `currentLanguage` đang chọn — chỉ đổi icon `drawableStart` (`ic_check_box_selected`/`_unselected`), nền/viền/màu chữ item giữ nguyên (đã resolve dứt khoát ở mục A: `bg_item_setting.xml` là shape tĩnh, không phải selector).

**Vị trí cuộn ban đầu**: `initUi()` (dòng 209-231) — nếu `isFromSplash=true` dùng `sharedViewModel.currentSystemLanguage` (map theo `Resources.getSystem().configuration.locales[0].language`, có thể `null` nếu ngôn ngữ máy không nằm trong 7 ngôn ngữ trên); nếu `isFromSplash=false` dùng `currentLanguage` đã lưu (`SharedPreferences`, default "en"). Tìm index trong `listLanguage` theo `code`, nếu có → `layoutManager.scrollToPosition(index)`.

**Ngôn ngữ đang chọn sẵn** (`currentLanguage` truyền vào adapter): chỉ set khi `!isFromSplash` (dòng 202-204) — nghĩa là **vào từ Splash lần đầu, KHÔNG có item nào được đánh dấu selected sẵn** (`btnDone` disabled cho tới khi user tự chọn); vào từ Settings thì item = ngôn ngữ đang dùng được đánh dấu `selected=true` sẵn.

### D. Data hardcode
- Tiêu đề "Language" (`@string/language`).
- 7 ngôn ngữ — xem bảng mục C.
- Overlay loading: "Setting up" (`@string/setting_up_language`).

### E. Nguồn từng view
- `ic_back_1`, `ic_tick`/`ic_tick_disabled`, `ic_check_box_selected`/`_unselected`, `bg_item_setting`, `bg_loading_rounded` → local drawable/vector.
- `adContainer` → **AD SLOT** kép, tuần tự:
  1. Lúc mở màn: `native_language` (`AdKey.NATIVE_LANGUAGE`) — `loadAndShowFirstAd()`, gọi ngay đầu `initUi()`.
  2. Ngay khi user tap chọn 1 ngôn ngữ lần đầu (`willShowSecondAd` true→false, chỉ chạy 1 lần): thay bằng `native_language2` (`AdKey.NATIVE_LANGUAGE_2`) — `loadAndShowSecondAd()`. Các lần đổi chọn ngôn ngữ sau đó không load lại ad.
- Danh sách ngôn ngữ → hardcode trong `AppSetting.kt`, không phải remote/API.

### F. Nhánh remote-config
`finish()` (`FragmentLanguagePicker.java:77-97`), chạy khi bấm `btnDone`:
```
setCurrentLanguage(...) ; setLocale(...)
if (!isFromSplash) → popBackStack()          // vào từ Settings: quay lại, không set languagePickerPassed
else {
  setLanguagePickerPassed(true)
  if (onboardingEnabled())      → actionLanguagePickerToIntro()
  else if (isShowHomeNewUI())   → actionLanguagePickerToHome()
  else                          → actionLanguagePickerToHomeOldUI()
}
```
Với `onboarding_enabled=false` (RC mặc định) và `isShowHomeNewUI()=true` (`ui_home_show_case=1`) ⇒ nếu người dùng lỡ vào màn này (nhánh không mặc định, vì Splash mặc định bỏ qua màn này hoàn toàn — xem mục 0), bấm Done sẽ đưa thẳng tới Home UI mới, không qua Intro.

Nút Back cứng (system back, `OnBackPressedCallback`, dòng 240-263): nếu `isFromSplash` → `activity.finish()` (thoát app, KHÔNG cho back ra ngoài luồng onboarding); nếu không → `popBackStack()` bình thường.

### STATE (Language Picker)
1. **Vào từ Splash, lần đầu, chưa chọn gì** (không phải nhánh mặc định của app nhưng là entry point chính của màn): `btnBack` INVISIBLE, không item nào selected, `btnDone` disabled (`ic_tick_disabled`), `adContainer`=`native_language`, `viewLoading` gone, list cuộn tới vị trí ngôn ngữ hệ thống nếu khớp 1 trong 7 (nếu máy dùng ngôn ngữ khác 7 ngôn ngữ này, không cuộn — dừng ở đầu list "English").
2. **Đã chọn 1 ngôn ngữ**: item đó `selected=true` (icon check đổi), `btnDone` enabled (`ic_tick`), `adContainer` chuyển sang `native_language2`.
3. **Vào từ Settings** (`isFromSplash=false`, không thuộc cụm "onboard" nhưng cùng Fragment): `btnBack` VISIBLE, ngôn ngữ hiện tại đã `selected=true` sẵn, `btnDone` vẫn khởi tạo disabled cho tới khi user tap lại (chọn lại/khác) theo code `initUi()` dòng 271 luôn set `false` bất kể nhánh.
4. ~~viewLoading overlay~~ — ĐÃ LOẠI: `showLoading()` là dead code (xem mục B), overlay này không bao giờ xuất hiện trong app thật, KHÔNG dựng thành state riêng.
5. **Ad rỗng** biến thể cho cả 2 vị trí (`native_language`/`native_language2`) nếu load lỗi.

---

## Rà soát các mục "hay bị sót"
- `res/menu/*`: không có menu nào được `getMenuInflater()` trong 3 fragment này — cả 3 đều không có Toolbar/AppBar, dùng ImageView tự vẽ làm nút back/done.
- Custom View `onDraw`: không có custom View riêng của app trong cụm này (`DotsIndicator`, `LottieAnimationView`, `ViewPager2` đều là thư viện third-party, không phải `*View`/`*Layout` tự viết có `onDraw`).
- RecyclerView ẩn: `rvLanguage` (FragmentLanguagePicker) — đã liệt kê đầy đủ ở mục 3.C; `viewPager` (FragmentIntro) dùng `RecyclerView.Adapter` nội bộ của `ViewPager2`, đã liệt kê ở mục 2.C.
- ripple/selector bọc ảnh: `button_text_color.xml` (color selector cho `nextButton`), `ic_tick_selector.xml`, `ic_check_box.xml` (drawable selector) — đã giải mã đầy đủ ở mục A/B liên quan.
- include/merge/ViewStub: `fragment_language_picker.xml` có `<include layout="@layout/layout_loading_with_text" id="@id/viewLoading">` — đã mở và mô tả đầy đủ ở mục 3.A.

## Danh sách cờ/điểm KHÔNG resolve được — đây là GIỚI HẠN CỦA APK NGUỒN, không phải thiếu sót của bản dựng
Cập nhật fix round 1/5: 4/5 cờ ban đầu nay đã có kết luận dứt khoát (dựa trên bằng chứng, không suy đoán); chỉ còn 1 cờ thật sự mở.

1. **`img_intro_1/2/3` — 3 ảnh minh hoạ Intro KHÔNG TỒN TẠI trong APK** (đã truy đến tận cùng, xem chuỗi bằng chứng đầy đủ ở mục 2.C: id có trong `R.java`/`R$drawable.smali` nhưng KHÔNG có entry trong `public.xml`, `resolve-arsc.py` trả NULL mọi config, không có file `img_intro*` trong `unzip -l`, đã loại trừ split-APK). Nguyên nhân nhiều khả năng: resource shrinking hoặc dấu vết reskin (`AndroidManifest` package `com.filter.face.puzzle` ≠ code namespace `com.cem.face.puzzle`). **RULING**: dựng đủ 3 frame, ô ảnh = **PLACEHOLDER CÓ NHÃN** "img_intro_N — không có trong APK", tuyệt đối không thay ảnh tự chọn/gần giống.
2. ~~Màu nền `bg_splash`~~ — ĐÃ RESOLVE: mở `$bg_splash__0.xml` ra gradient tuyến tính dọc `#ffffffff` (đỉnh) → `#ff08bdff` (đáy), trục `(187.5,0)→(187.5,812)`.
3. ~~Thời điểm gọi `showLoading()`~~ — ĐÃ RESOLVE: grep toàn bộ smali `ui/language/` xác nhận `showLoading(J)V` không có lời gọi nào ngoài định nghĩa → dead code, overlay loading không bao giờ hiện.
4. ~~Logic `traveledPages`~~ — ĐÃ RESOLVE: smali `FragmentIntro$loadAdIfNeed$1.smali:340-353` xác nhận `if (traveledPages.contains(page)) return` (early-return) trước khi add+load ad → mỗi trang chỉ load native ad đúng 1 lần/vòng đời Fragment, không load lại khi quay lại trang đã xem.
5. ~~Nền item ngôn ngữ khi `selected=true`~~ — ĐÃ RESOLVE: `bg_item_setting.xml` là `<shape>` tĩnh (không phải selector), nền trắng + viền nét đứt cố định ở mọi trạng thái; khác biệt selected/chưa-chọn CHỈ ở icon `drawableStart`.
6. **UMP/GDPR consent — vẫn còn mở**: không nằm trong code 3 fragment cụm "onboard" (đã grep cả 3 file .java lẫn smali liên quan, không có lời gọi consent form nào). Nếu app có consent, nó chạy ở tầng khác (Activity hoặc bên trong `Monet.start`, nằm ngoài phạm vi cụm "onboard" được giao) — dựng như **placeholder có nhãn** riêng "UMP/GDPR consent (SDK, ngoài layout onboard)", không gộp vào Splash.

## Ghi chú bucket resource ảnh (theo rà soát chung của coordinator)
App để ảnh nội dung ở `res/mipmap-*` (ví dụ `img_app_name.webp`, `window_bg.webp` ở `mipmap-xxhdpi-v4`), không phải `res/drawable-*`. Cụm "onboard" **không dùng** `img_app_name` hay `window_bg` — logo Splash dùng `ic_logo`/`@drawable/ic_splash`, đã xác nhận đúng nằm ở `res/drawable/ic_splash.png` (không phải mipmap), không cần sửa đường dẫn trong spec này.
