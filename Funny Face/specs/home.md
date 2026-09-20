# Cụm HOME — spec dựng Figma 1:1

Nguồn: `SRC = decompiled/sources/sources/com/cem/face/puzzle` (lưu ý: có 2 lớp `sources/sources`
lồng nhau trong repo giải nén — path thật là
`decompiled/sources/sources/com/cem/face/puzzle`, KHÔNG phải `decompiled/sources/com/...`).
`RES = decompiled/resources/res`. Canvas 360×800dp, sdp==dp/ssp==sp, không vẽ status bar.

---

## 0. Khung MainActivity

`RES/layout/activity_main.xml`:
```
FragmentContainerView [id=mainNavHost, w=fill, h=fill, navGraph=@navigation/main_nav, defaultNavHost=true]
```
Toàn màn hình chỉ là 1 NavHostFragment. `MainActivity.java` (`ui/MainActivity.java`) KHÔNG
override `startDestination`, KHÔNG gọi `navController.navigate()`/`setGraph()` nào ở
`initView()` — chỉ đăng ký `onBackPressedListener()`: nếu destination hiện tại là
`fragmentHome` / `fragmentHomeOldUI` / `fragmentSplash` thì back = `finish()` app; các màn khác
thì `navigateUp()`. → 3 destination này được coi là "root" của back-stack.

---

## 1. Bản đồ điều hướng — `res/navigation/main_nav.xml` (18 destination, startDestination = `fragmentSplash`)

| # | id | Fragment/Dialog | Action ra | Đích | Argument của destination |
|---|----|------------------|-----------|------|---------------------------|
| 1 | fragmentSplash (START) | ui.onboard.FragmentSplash | actionSplashToHome<br>actionSplashToHomeOldUI<br>actionSplashToLanguagePicker<br>actionSplashToIntro | fragmentHome<br>fragmentHomeOldUI<br>fragmentLanguagePicker<br>fragmentIntro | — |
| 2 | fragmentHome | ui.home.FragmentHome | actionHomeToVideoGallery<br>actionHomeToSettings<br>actionHomeToPreviewTemplate<br>actionHomeToFunnyPuzzle | fragmentVideoGallery<br>fragmentSettings<br>fragmentPreviewTemplate<br>fragmentFunnyPuzzle | — |
| 3 | fragmentHomeOldUI | ui.home.FragmentHomeOldUI | actionHomeToVideoGallery<br>actionHomeToSettings<br>actionHomeToListFunnyPuzzle<br>actionHomeToPreviewTemplate | fragmentVideoGallery<br>fragmentSettings<br>fragmentListFunnyPuzzle<br>fragmentPreviewTemplate | — |
| 4 | fragmentIntro | ui.onboard.FragmentIntro | actionIntroToHome | **fragmentHome** (luôn về UI mới, không có nhánh sang HomeOldUI) | — |
| 5 | fragmentLanguagePicker | ui.language.FragmentLanguagePicker | actionLanguagePickerToHome<br>actionLanguagePickerToHomeOldUI<br>actionLanguagePickerToIntro | fragmentHome<br>fragmentHomeOldUI<br>fragmentIntro | `isFromSplash: boolean` |
| 6 | fragmentLevelPicker | ui.level.FragmentLevelPicker | actionLevelPickerToFacePuzzle<br>actionLevelPickerToFunnyPuzzle | fragmentFacePuzzle<br>fragmentFunnyPuzzle | `funnyPuzzleTemplate: FunnyPuzzleUI?` (nullable) |
| 7 | fragmentFacePuzzle | ui.face_puzzle.FragmentFacePuzzle | actionToPreviewWithMusic<br>actionPlayFilterToSoundPicker | fragmentPreviewWithMusic<br>dialogFragmentSoundPicker | `level: integer` |
| 8 | fragmentFunnyPuzzle | ui.face_funny.FragmentFunnyPuzzle | actionFunnyPuzzleToSoundPicker<br>actionFunnyPuzzleToPreviewWithMusic | dialogFragmentSoundPicker<br>fragmentPreviewWithMusic | `funnyPuzzleTemplate: FunnyPuzzleUI`, `level: integer` |
| 9 | fragmentPreviewWithMusic | ui.preview.FragmentPreviewWithMusic | actionPreviewWithMusicToSoundPicker<br>actionPreviewWithMusicToResult | fragmentSoundPicker<br>fragmentResult (popUpTo=fragmentHome) | `pathVideoPreview: string`, `soundPreview: SoundUI?` |
| 10 | fragmentSoundPicker | ui.sound_picker.FragmentSoundPicker | — | — | — |
| 11 | dialogFragmentSoundPicker (dialog) | ui.sound_picker.DialogFragmentSoundPicker | — | — | — |
| 12 | fragmentResult | ui.result.FragmentResult | actionResultToPlayVideo | fragmentPlayVideo | `pathVideoResult: string` |
| 13 | fragmentPlayVideo | ui.play_video.FragmentPlayVideo | — | — | `pathVideo: string`, `canDelete: boolean` |
| 14 | fragmentVideoGallery | ui.video_gallery.FragmentVideoGallery | actionGalleryToPlayVideo | fragmentPlayVideo | — |
| 15 | fragmentSettings | ui.settings.FragmentSettings | actionSettingsToInfoFragment<br>action_fragmentSettingsToLanguagePicker | companyInfoFragment<br>fragmentLanguagePicker | — |
| 16 | companyInfoFragment | ui.settings.CompanyInfoFragment | — | — | `infoType: CompanyInfoFragment.Type` |
| 17 | fragmentPreviewTemplate | ui.preview.FragmentPreviewTemplate | actionPreviewToFacePuzzle | fragmentFacePuzzle | `urlVideoTemplate: string` |
| 18 | fragmentListFunnyPuzzle | ui.face_funny.FragmentListFunnyPuzzle | — | — | — (chỉ dùng bởi HomeOldUI) |

Ngoài root `actionToLevelPicker`/`actionToPlayVideo` khai báo global ở đầu file (không gắn
fragment cụ thể) — dùng bởi các Directions companion `actionToLevelPicker$default`.

**Toàn bộ 18 destination đã liệt kê đủ.** Không có action nào bị MainActivity ghi đè.

---

## 2. NHÁNH 2 UI HOME — cờ thật, default, kết quả

File: `ui/CemViewModel.java`, `ad_support/AdKey.java`.

```kotlin
// AdKey.java
HOME_SHOW_CASE_FB    = "home_show_case"        // dòng 13
UI_HOME_SHOW_CASE_FB = "ui_home_show_case"      // dòng 36

// CemViewModel.java
private fun uiHomeShowCase(): Int =
    FirebaseRemoteManager.getInt(AdKey.UI_HOME_SHOW_CASE_FB) ?: 0      // default KHI CHƯA FETCH = 0
fun homeShowCase(): Int =
    FirebaseRemoteManager.getInt(AdKey.HOME_SHOW_CASE_FB) ?: 1         // default KHI CHƯA FETCH = 1
fun isShowHomeNewUI(): Boolean = uiHomeShowCase() == 1
```

- `homeShowCase()` **KHÔNG được gọi ở bất kỳ đâu khác trong toàn bộ source** (đã `grep -rn
  "\.homeShowCase()"` toàn repo → 0 kết quả ngoài định nghĩa). → **dead/unused code**, key
  `home_show_case` fetch được (=0) nhưng không rẽ nhánh gì cả. Không dựng theo giá trị này.
- `isShowHomeNewUI()` **là cờ thật quyết định UI Home**, dùng ở 2 nơi:
  - `FragmentSplash.goToInside()` (`ui/onboard/FragmentSplash.java:43`)
  - `FragmentLanguagePicker` sau khi chọn ngôn ngữ từ splash (`ui/language/FragmentLanguagePicker.java:92`)

Điều kiện đầy đủ tại Splash (`goToInside()`):
```
actionSplashToIntro =
  (isLanguagePickerPassed() || !languageEnabled())
    ? (isFirstInstall() && onboardingEnabled())
        ? actionSplashToIntro()
        : isShowHomeNewUI() ? actionSplashToHome() : actionSplashToHomeOldUI()
    : actionSplashToLanguagePicker(true)
```
`languageEnabled()`/`onboardingEnabled()` đọc RC key **`language_enabled`** /
**`onboarding_enabled`** qua `FeatureFlag.java` (`getBoolean`, default false nếu SDK RC trả
false khi thiếu key).

**Áp giá trị RC đã fetch thật** (`onboarding_enabled=false`, `language_enabled=false`,
`ui_home_show_case=1`):
- `!languageEnabled()` = true → luôn bỏ qua LanguagePicker.
- `isFirstInstall() && onboardingEnabled()` = false (vì `onboardingEnabled()`=false) → luôn bỏ
  qua Intro/Onboarding, **cả lần đầu mở lẫn quay lại**.
- `isShowHomeNewUI()` = (`ui_home_show_case`==1) = **true**.

→ **NHÁNH MẶC ĐỊNH DUY NHẤT khi chạy thật với RC hiện tại: Splash → `FragmentHome` (UI MỚI)**,
bất kể first-install hay không. `FragmentHomeOldUI` chỉ xuất hiện nếu BE đổi
`ui_home_show_case` về 0 (hoặc app chưa fetch được RC lần đầu và dùng default cứng 0 — xem dưới).

- Case "chưa fetch được RC" (mất mạng lần mở đầu tiên): `uiHomeShowCase()` trả default cứng
  **0** → `isShowHomeNewUI()`=false → app fallback về `FragmentHomeOldUI`. **Đây là state cần
  dựng thêm**: "Home – lần đầu, chưa có Remote Config" → UI CŨ.
- `FragmentIntro` (khi onboarding bật) luôn thoát về `FragmentHome` (UI MỚI) bất kể cờ
  `ui_home_show_case`, KHÔNG có route sang HomeOldUI (`actionIntroToHome` chỉ trỏ tới
  `fragmentHome`).

→ **Dựng theo thứ tự ưu tiên: FragmentHome (UI mới) = màn chính/mặc định. FragmentHomeOldUI =
màn phụ (nhánh RC=0 hoặc chưa-fetch-RC).**

---

## 3. FragmentHome — UI MỚI (MẶC ĐỊNH)

File code: `ui/home/FragmentHome.java`. Layout: `RES/layout/fragment_home.xml`.
Binding: `FragmentHomeBinding`.

### A. Geometry (từ `resolve-layout.py` + XML constraint, canvas 360×800)

Root: `ConstraintLayout` full-screen (360×800).

| View | id | Vai trò | Constraint → x/y/w/h ước tính (dp) | Style/nền | Bo góc |
|---|---|---|---|---|---|
| AppCompatImageView | `btnSettings` | nút Cài đặt | End+Top parent, marginEnd=12,marginTop=12 → **x=300,y=12,w=48,h=48** | `@style/Base.PrimaryButton.Square` (bg=`?selectableItemBackgroundBorderless`, padding=8) · `src=@drawable/ic_setting` | ripple tròn (borderless) |
| AppCompatImageView | `btnGalley` | nút mở Video Gallery (My library) | Start parent marginStart=12, Top/Bottom = btnSettings → **x=12,y=12,w=48,h=48** | như trên · `src=@drawable/ic_gallery_btn` | ripple tròn |
| AppCompatImageView | `imvAppName` | logo app | căn giữa ngang (Start=End=parent), Top/Bottom=btnSettings (canh giữa dọc theo hàng 48dp) → **y≈24,h=24**, w=wrap (theo ảnh gốc) | `src=@mipmap/img_app_name` (webp, có 3 mật độ hdpi/xhdpi/xxhdpi) | — |
| TabLayout | `templateTabLayout` | **tab danh mục template** | fill width trừ margin 14 trái/phải, marginTop=12 từ đáy btnSettings (đáy=60) → **x=14,y=72,w=332,h=32** | style `@style/TemplateTabLayout` (xem mục C) | pill bo góc `size_8`=8dp mỗi tab |
| FrameLayout | `homeNativeContainer` | **AD SLOT** (native ad cố định trong Home) | width=0 (match giữa 2 margin 14), marginTop=8 từ đáy tab (104) → **x=14,y=112,w=332,h=wrap** | trống — nạp view ad runtime | — |
| ViewPager2 | `templateViewPager` | **carousel nội dung theo tab** (pager 2 chiều, mỗi trang = grid template) | Top = đáy `homeNativeContainer`, Bottom = đỉnh `nativeCollapsibleContainer`, fill width → **x=0,y≈112 (khi ad container GONE mặc định),w=360,h=fill phần còn lại** | — | — |
| FrameLayout | `nativeCollapsibleContainer` | **AD SLOT** (native ad "collapsible" đáy màn) | Bottom/Start/End=parent, width=0 (match) → **x=0,y=800-h,w=360,h=wrap (0 nếu con GONE)** | — | — |
| View (con) | `collapseHolderNative` | placeholder nền cho ad collapsible khi đang tải | fill width trong container, h=`@dimen/ad_native_collapsed_height`=**256dp** | `background=@drawable/bg_ad_native_media_white` | theo drawable |

Padding/margin đã ghi trong bảng (marginEnd/marginTop/marginStart=12 cho 2 nút icon; tab
margin ngang 14 + marginTop 12; native container margin ngang 14 + marginTop 8).

### B. Visibility (từ code)

| View | XML mặc định | Setter runtime | Điều kiện | KẾT QUẢ hiển thị mặc định |
|---|---|---|---|---|
| `homeNativeContainer` | `android:visibility="gone"` | `loadHomeFixedNative()` set `VISIBLE` trước khi gọi `loadAndShowNativeSafe`; nếu load thất bại → `removeAllViews()` + set lại `GONE` (`FragmentHome.java` loadHomeFixedNative, dòng ~234-280) | Kết quả load native ad "native_home" (async, `startHomeFixedNativeReload()` gọi lặp lại) | **GONE** cho tới khi ad load xong → khi đó VISIBLE, chèn native ad view. Không đoán được tại design-time nếu không có ad thật → coi state mặc định = ẩn |
| `nativeCollapsibleContainer` | không set (mặc định VISIBLE — là `FrameLayout`) | container luôn hiển thị (chứa `collapseHolderNative`); `loadAds()` set `collapseHolderNative`... thực chất set **chính container** `VISIBLE`→ khi fail thì `removeAllViews()` rồi set **GONE** | load "native_collapsible_home" | Ban đầu container hiện nhưng rỗng (h=wrap→0 vì con gone) cho tới khi có ad |
| `collapseHolderNative` (con, placeholder xám) | không set trong XML (mặc định VISIBLE) | `initUi()`: `ViewExtKt.gone(collapseHolderNative)` — GONE ngay khi vào màn | luôn luôn | **GONE mặc định** (đây là placeholder chờ SDK debug, không phải nội dung thật) |
| `templateViewPager` | VISIBLE | `setAdapter(null)` ở `onDestroyView` | — | VISIBLE |
| `templateTabLayout` | VISIBLE, số tab phụ thuộc data | `TabLayoutMediator` attach trong `observeHomeData$1` khi có dữ liệu | dữ liệu `dataHomepageV2` rỗng cho tới khi network trả về | **0 tab hiển thị lúc mới mở** (list rỗng) → tab xuất hiện khi remote trả dữ liệu |

Không có view nào dùng helper `show(v, bool)` phức tạp trong màn này (chỉ `gone()` đơn giản,
`ViewExtKt.java` dòng 88).

### C. List — cơ chế TAB THẬT (TabLayout + ViewPager2, KHÔNG phải BottomNavigationView)

`templateTabLayout` + `templateViewPager` được nối bằng `TabLayoutMediator`
(`FragmentHome$observeHomeData$1.java`, tạo trong `invokeSuspend`, `attach()` ngay). Adapter
của ViewPager2 là `AdapterTemplateCategory` (`RecyclerView.Adapter` thường, KHÔNG phải
`FragmentStateAdapter` — mỗi "trang" là 1 `RecyclerView` lồng bên trong `item_pager_tepmlate_category.xml`).

**Nguồn danh sách tab**: `SharedViewModel.getDataHomepageV2()` = zip của
`listFacePuzzleTemplateUIV2` (List<CategoryUI>, từ `DataRemoteRepositoryImpl.getFacePuzzleTemplatesV2()`
→ REMOTE, gọi **`RemoteFacePuzzleService.getDataForHomeV2()`** = `GET FacePuzzle/ios_data_facepuzzle_v2.json`
trên `BASE_URL = https://wallpaperhd.nyc3.cdn.digitaloceanspaces.com/`
(`com/cem/data/remote/RemoteFacePuzzleService.java:17`, `com/cem/data/BuildConfig.java:6`);
nếu offline/lỗi → fallback `listTemplateCategory` nội bộ = `ArrayList` rỗng) và
`listFunnyPuzzleTemplates` (local, 20 item từ `assets/face_funny/data_funny.json`).

Thứ tự tab dựng trong `SharedViewModel$dataHomepageV2$1.invokeSuspend` (dòng 60-69):
```
1. "All"           — HomepageUIV2(name="All", allPuzzle = mixToListHomepageUI(...))
2..N+1. <category.getName()> — mỗi CategoryUI remote → 1 tab riêng, content = category.videos
N+2. "Funny Puzzle" — content = 20 FunnyPuzzleUI local
```
**RESOLVED (fetch thật CDN, snapshot lúc audit — server có thể đổi bất cứ lúc nào, không có
cơ chế version-pin trong app):** `ios_data_facepuzzle_v2.json` trả **đúng 3 category, cố định
theo code** (`SharedViewModel.mixToListHomepageUI` đọc cứng `listFace[0..2]` — snapshot xác
nhận đúng 3, không có category thứ 4 nào bị bỏ sót). → **`N=3`, tab thật của FragmentHome
luôn là 5 tab, đúng thứ tự:**

| # tab | Tên tab (`CategoryUI.name`/hardcode) | id category | folder | Số ô hiển thị | spanCount |
|---|---|---|---|---|---|
| 1 | **All** (hardcode code, không phải remote) | — | — | 18 face (mix 3×6, xem dưới) + xen 20 funny theo cụm 2 | 2 |
| 2 | **Face Puzzle** | 1 | `Face_Puzzle` | 6 (Video1..6) | 2 |
| 3 | **Face Pop** | 2 | `Face_Pop` | 6 (Video1..6) | 2 |
| 4 | **Whirl Face** | 3 | `Whirl_Face` | 6 (Video1..6) | 2 |
| 5 | **Funny Puzzle** (hardcode code) | — | — | 20 (data_funny.json) | 2 |

`categoryId` dùng lại trong `OverlayView.Mode` khi click item (mục 5): `1`→FacePuzzle mode
(default/else), `2`→FacePop, `3`→FaceWhirl — khớp đúng 3 category trên, xác nhận thứ tự
id 1/2/3 không đổi.

**Nhãn "N uses" từng ô** — công thức `MapperKt.round(likes/1000f, 1) + "k uses"`
(`com/cem/data/mappers/MapperKt.java:85`, làm tròn 1 chữ số thập phân):

| Category | Video1 | Video2 | Video3 | Video4 | Video5 | Video6 |
|---|---|---|---|---|---|---|
| Face Puzzle (id1) | 273.3k uses | 716.8k uses | 22.5k uses | 18.8k uses | 49.4k uses | 164.4k uses |
| Face Pop (id2) | 249.1k uses | 164.4k uses | 39.9k uses | 5.2k uses | 1.3k uses | 1.0k uses |
| Whirl Face (id3) | 273.3k uses | 49.4k uses | 23.9k uses | 18.8k uses | 4.8k uses | 1.0k uses |

(likes gốc: FP 273300/716845/22536/18833/49400/164400 · Pop 249100/164400/39900/5166/1255/985 ·
Whirl 273300/49400/23937/18800/4848/985 — nguồn fetch CDN trực tiếp, snapshot tại thời điểm
audit, KHÔNG hardcode trong APK, server đổi được).

Thumb/video URL (mapper V2, `MapperKt.toFacePuzzleTemplateUI(FacePuzzleTemplateEntityV2,...)`,
dòng 80-92): folder `Face_Puzzle` được thay bằng chuỗi rỗng trong URL (chỉ 2 category kia giữ
folder), pattern:
```
video: https://wallpaperhd.nyc3.cdn.digitaloceanspaces.com/FacePuzzle/[<folder>/]Video/<id>.mp4
thumb: https://wallpaperhd.nyc3.cdn.digitaloceanspaces.com/FacePuzzle/[<folder>/]Thumb/<id>.png
```
(`<folder>/` bị bỏ khi folder==`Face_Puzzle`; `<id>` = "Video1".."Video6").
Đã tải sẵn cả 18 thumbnail thật (576×1024) vào
`/home/ubuntu/workspace/Design/App 6/Funny Face/assets/v1/30-template-v2/<folder>_<id>.png`
(vd `Face_Puzzle_Video1.png`, `Face_Pop_Video3.png`, `Whirl_Face_Video6.png`) — dùng trực tiếp
làm ảnh thật khi dựng Figma thay vì placeholder.

Style tab (`@style/TemplateTabLayout`, `RES/values/styles.xml:3727`):
- `tabBackground=@drawable/tab_background` (selector: state_selected → solid `?colorPrimary`
  bo góc 8dp; mặc định → stroke 1dp đen + nền trắng, bo góc 8dp)
- `tabMode=scrollable`, `tabGravity=start`, `tabIndicator=@null` (không có gạch chân, chỉ đổi
  nền pill khi chọn)
- `tabMinWidth=40dp`, padding ngang mỗi tab 8dp (marginHorizontal 6dp gán runtime trong
  `observeHomeData$1`, dòng 80-93)
- text: `TemplateTabTextAppearance` — size `text_size_12`=12sp, bold, không viết hoa;
  `tabTextColor=@color/black` (#ff000000), `tabSelectedTextColor=@color/white` (#ffffffff)

**Trang "All" (tab 1)** — nội dung KHÔNG phải 1 RecyclerView đơn giản mà là `ConcatAdapter` xen
kẽ 4 nguồn theo từng cụm 2 item (`SharedViewModel.mixToListHomepageUI`, dòng 91-118):
```
lặp: [2 item Face Puzzle] → [2 item Face Pop] → [2 item Whirl Face] → [2 item Funny Puzzle]
```
(code đọc cứng `listFace[0]`, `listFace[1]`, `listFace[2]` = 3 category V2 đã xác nhận
**RESOLVED** ở trên (Face Puzzle/Face Pop/Whirl Face, đúng 3, không thiếu) → hết vòng lặp khi
nguồn dài nhất cạn (`max(6,6,6,20)=20` phần tử Funny Puzzle → 10 vòng lặp; các category face
hết dữ liệu ở vòng 3 thì `subList` rỗng, vẫn add `HomepageUI(true, emptyList)` — chunk rỗng
không render item nào nhưng KHÔNG dừng vòng lặp). Thứ tự cuối cùng trang "All": 3 vòng đầu có
đủ 4 khối (2 face×3 + 2 funny) = 24 item hiển thị (18 face + 6 funny), 7 vòng còn lại chỉ còn
khối Funny Puzzle (14 item funny) do 3 category face đã cạn → **tổng trang "All" = 18 face-item
+ 20 funny-item = 38 item**, chia làm nhiều nhóm 2-cột xen kẽ theo đúng trật tự trên.)

**Trang từng category riêng / trang "Funny Puzzle"**: `GridLayoutManager` 2 cột
(`item_pager_tepmlate_category.xml` → `spanCount=2` set trong XML, layout code
`AdapterTemplateCategory.onBindData` tạo `GridLayoutManager(context, 2)` — **spanCount lấy từ
CODE (hardcode 2), không phải từ XML** dù XML cũng ghi `app:spanCount="2"` — trùng nhau).

**Ô quảng cáo chèn trong lưới**: mỗi `AdapterFacePuzzleTemplate`/`AdapterFunnyPuzzleTemplate`
con (được tạo cho từng vị trí/category) tự chèn **1 ô AdItem tại index 2** nếu
`showAdsInList && list.size>=2` (`createFacePuzzleItems`/`createFunnyPuzzleItems`,
`AdapterTemplateCategory.java` dòng 235-245, 277-287). `showAdsInList` mặc định **true**
(param `showAdsInList: Boolean = true` trong constructor `AdapterTemplateCategory`,
`FragmentHome.observeHomeData()` gọi `AdapterTemplateCategory(activity, listener, false)` —
**để ý: FragmentHome truyền `false`** → **KHÔNG chèn ad trong lưới của UI mới**, chỉ
`FragmentTabHome` (dead code) truyền default `true`. Ô `item_face_puzzle_ad.xml` /
`item_funny_puzzle_ad.xml` do đó **không xuất hiện trong FragmentHome (UI mới)**.

**Item nội dung** (`item_face_puzzle_template.xml`, span=1/2 cột):
```
ConstraintLayout [padding=10dp, w=fill, h=wrap]
  ImageView imvThumbVideo [w=fill,h=0(match theo tỉ lệ ô), scaleType=centerCrop] — bo góc runtime 16dp (ViewExtKt.setRadiusPx)
     nguồn ảnh: Glide.load(item.thumbUrl) — REMOTE URL
  TextView tvUserCount [góc dưới-trái theo margin 8dp, bg=@drawable/bg_primary_rounded_enabled (gradient xanh, bo 48dp), padding 12/4, textColor=white]
     text: item.useViewCounter — REMOTE STRING (vd lượt dùng)
```
Item Funny Puzzle (`item_funny_puzzle.xml`):
```
ConstraintLayout [bg=@drawable/bg_funny_puzzle, padding=1dp, margin=10dp]
  ImageView imvFunnyPuzzle [w=fill,h=0] — Glide.load(item.originImagePath) → LOCAL asset (assets/face_funny/origin/<name>.png, 1 trong 20 file)
  TextView tvName [bg=@drawable/bg_funny_puzzle_text_name, padding 10dp, font=@font/lato_bold_700, gravity=center] — text = item.name (HARDCODE, xem mục D)
```

### D. Data hardcode

20 nhân vật Funny Puzzle — `assets/face_funny/data_funny.json` (NGUYÊN VĂN, đúng thứ tự):

| id | name | image |
|----|------|-------|
| 1 | Kylian Mbappe | Kylian_Mbappe |
| 2 | Leonel Messi | Leonel_Messi |
| 3 | Erling Haaland | Erling_Haaland |
| 4 | Cristiano Ronaldo | Cristiano_Ronaldo |
| 5 | Jude Bellingham | Jude_Bellingham |
| 6 | Messi | messi |
| 7 | Vinicius Junior | Vinicius_Junior |
| 8 | Neymar Junior | Neymar_Junior |
| 9 | Bruno Mars | Bruno_Mars |
| 10 | Donald Trump | Donald_Trump |
| 11 | Jennie | Jennie |
| 12 | Timothe Chalamet | Timothe_Chalamet |
| 13 | Taylor Swift | Taylor_Swift |
| 14 | Leonardo Dicaprio | Leonardo_Dicaprio |
| 15 | Mr.Bean | Mr_Bean |
| 16 | Messi | Messi_2 |
| 17 | Ronaldo | Ronaldo |
| 18 | Neymar Jr | Neymar_Jr |
| 19 | Naruto | Naruto |
| 20 | Rose | Rose |

Ảnh hiển thị trong grid = `origin/<image>.png` (20 file), overlay dùng ở màn chỉnh sửa (ngoài
cụm Home) = `overlay/<image>.png`.

Không có category/template face-puzzle nào hardcode trong APK — 100% remote (xem mục C), nhưng
đã fetch được snapshot thật (3 category/18 template v2, tên/likes/URL liệt kê đầy đủ ở mục C) —
KHÔNG phải giá trị cố định trong code, server đổi được bất cứ lúc nào.

### E. Nguồn từng view

| View | Nguồn |
|---|---|
| `imvAppName` | local mipmap `@mipmap/img_app_name` |
| `btnSettings` icon | local drawable `@drawable/ic_setting` |
| `btnGalley` icon | local drawable `@drawable/ic_gallery_btn` |
| Tên tab "All" | hardcode string trong code (`"All"`) |
| Tên tab category giữa | **REMOTE** (`CategoryUI.name`) — snapshot đã fetch: "Face Puzzle"/"Face Pop"/"Whirl Face", xem bảng mục C |
| Tên tab "Funny Puzzle" | hardcode string trong code (`"Funny Puzzle"`) |
| Thumbnail Face Puzzle | **REMOTE URL** (`FacePuzzleTemplateUI.thumbUrl`, Glide) — 18 ảnh thật đã tải sẵn, xem mục C |
| Số lượt dùng (`tvUserCount`) | **REMOTE** (`FacePuzzleTemplateUI.useViewCounter`) — công thức + bảng giá trị snapshot ở mục C |
| Ảnh Funny Puzzle | **local asset** `assets/face_funny/origin/<image>.png` |
| Tên Funny Puzzle (`tvName`) | **local JSON hardcode** (`data_funny.json`) |
| `homeNativeContainer`, `nativeCollapsibleContainer` | **AD SLOT** — native ad, placement `native_home` / `native_collapsible_home` (Monet SDK) |
| Ô ad trong grid (`item_face_puzzle_ad`/`item_funny_puzzle_ad`) | **AD SLOT** — nhưng **không kích hoạt trong FragmentHome UI mới** (xem mục C) |
| In-app review khi vào màn (`ContextExtKt.showAppReview`) | **UI OS/SDK** — Google In-App Review, không có layout riêng, không vẽ trong Figma trừ khi cần placeholder hệ thống |

### F. Nhánh remote-config — đã trình bày đầy đủ ở mục 2 (áp dụng cho toàn cụm, không riêng màn này).

### STATE — các trạng thái runtime cần dựng thành frame riêng

1. **Home (mặc định) — dữ liệu đã tải xong**: đủ **5 tab** ("All"/"Face Puzzle"/"Face Pop"/
   "Whirl Face"/"Funny Puzzle"), trang "All" có 38 item (18 face + 20 funny xen kẽ), ad slot ẩn
   (chưa mock ad thật).
2. **Home — đang tải remote (lần đầu mở / mất mạng)**: `dataHomepageV2` rỗng →
   `templateTabLayout` **0 tab**, `templateViewPager` không có trang nào (trắng). Đây là state
   thực tế xảy ra "lần đầu mở app" trước khi network trả dữ liệu.
3. **Home — có ad native "native_home" đã load**: `homeNativeContainer` VISIBLE, chèn khối ad
   dưới hàng tab (AD SLOT).
4. **Home — có ad native collapsible ở đáy màn** (`nativeCollapsibleContainer` VISIBLE, cao tới
   256dp) — đè lên phần dưới `templateViewPager`.
5. Không có khái niệm free/PRO riêng cho màn Home (không thấy badge PRO/khoá trong layout hay
   code màn này); trạng thái quyền không áp dụng cho Home (chỉ xuất hiện ở
   VideoGallery/PlayVideo do cần quyền lưu trữ).

---

## 4. FragmentHomeOldUI — UI CŨ (fallback khi `ui_home_show_case`≠1 hoặc chưa fetch RC)

File code: `ui/home/FragmentHomeOldUI.java`. Layout: `RES/layout/fragment_home_old_ui.xml`.

### A. Geometry

| View | id | Vai trò | Constraint → ước tính x/y/w/h (dp) | Nền/style | Bo góc |
|---|---|---|---|---|---|
| AppCompatImageView | `imvAppName` | logo | Top/Start/End=parent, marginTop=16 → **x=center,y=16,h=28** | `@mipmap/img_app_name` | — |
| AppCompatImageView | `btnSettings` | nút cài đặt | End=parent marginEnd=12, Top/Bottom=imvAppName → **x=300,y=16(canh giữa theo imvAppName 28dp→y≈14),w=48,h=48** | `Base.PrimaryButton.Square`, `src=@drawable/ic_setting` | ripple tròn |
| AppCompatImageView | `imvBannerFacePuzzle` | banner quảng bá Face Puzzle (bấm để vào Level Picker) | Start=parent marginStart=20, End=spaceBanner, Top=đáy imvAppName+16 → **x=20,y≈60,w=(360-20-12-20)/2=154,h=wrap(theo ảnh)** | local `@drawable/img_banner_face_puzzle` (webp) | bo góc runtime 16dp (`ViewExtKt.setRadiusPx`, `size_16`) |
| Space | `spaceBanner` | khoảng cách giữa 2 banner | 12×12dp, giữa 2 banner | — | — |
| AppCompatImageView | `imvBannerFunnyPuzzle` | banner quảng bá Funny Puzzle (bấm để vào list Funny Puzzle) | End=parent marginEnd=20, Start=spaceBanner, Top=đáy imvAppName+16 → **x=186,y≈60,w=154,h=wrap** | local `@drawable/img_banner_funny_puzzle` | bo góc runtime 16dp |
| FrameLayout | `btnMyLibrary` | nút "My library" (vào Video Gallery) | Start=imvBannerFacePuzzle, End=imvBannerFunnyPuzzle, Top=đáy banner+16, paddingVertical=28 → **x=20,y≈banner_bottom+16,w=320** | `@drawable/bg_button_my_library` (viền nét đứt xanh `primary_color`, bo 16dp, nền `#fff5f9ff`) | 16dp |
| — TextView (con btnMyLibrary) | — | nhãn nút | căn giữa trong FrameLayout | text=`@string/my_library`="My library", size=`text_size_20`=20sp, color=`primary_color`(#ff016cf7), font=`lato_bold_700`, icon trái `@drawable/ic_layers` (drawableStart, padding 8dp) | — |
| RecyclerView | `rvFacePuzzleTemplate` | **lưới template chính** | fill width, padding ngang 10dp, marginTop=10 từ đáy btnMyLibrary, Bottom=đỉnh nativeCollapsibleContainer | `GridLayoutManager` **spanCount=2 (khai trong XML `app:spanCount="2"` — KHÔNG override trong code, khác với UI mới)** | — |
| FrameLayout | `nativeCollapsibleContainer` | **AD SLOT** collapsible đáy màn | như FragmentHome | — | — |
| View | `collapseHolderNative` | placeholder ad | h=256dp | `@drawable/bg_ad_native_media_white` | — |

### B. Visibility

| View | XML mặc định | Setter runtime | Điều kiện | KẾT QUẢ |
|---|---|---|---|---|
| `collapseHolderNative` | VISIBLE (không khai trong XML) | `initUi()`: `ViewExtKt.gone(...)` | luôn | **GONE mặc định** |
| `nativeCollapsibleContainer` | VISIBLE | `loadHomeCollapsible()` (giống FragmentHome) set VISIBLE khi có ad / `removeAllViews()`+GONE khi fail | load "native_collapsible_home" | rỗng (h→0) cho tới khi có ad |
| `rvFacePuzzleTemplate` | VISIBLE | `setAdapter(null)` ở onDestroyView | — | VISIBLE, rỗng cho tới khi 2 flow `listFacePuzzleTemplateUI` (remote **v1**, `getDataForHome()`, 8 item) + `listFunnyPuzzleTemplates` (local, 20 item) đều có dữ liệu (`dataHomepage` chỉ emit khi CẢ HAI non-empty — Funny local sẵn 20 item ngay, chỉ chờ remote v1) |

### C. List

⚠️ **SỬA LỖI so với bản trước**: bản trước ghi nhầm FragmentHomeOldUI dùng chung
`mixToListHomepageUI` với trang "All" của UI mới — SAI, đã tự phát hiện + sửa khi verify lại
theo yêu cầu round 1. `mixToListHomepageUI` (đọc cứng `listFace[0..2]`, cần ĐÚNG 3 category)
CHỈ được gọi trong `SharedViewModel$dataHomepageV2$1` (nguồn V2, dùng cho FragmentHome UI mới,
mục 3.C). FragmentHomeOldUI dùng `SharedViewModel.getDataHomepage()` → nguồn khác hẳn:
`listFacePuzzleTemplateUI` (flat `List<FacePuzzleTemplateUI>`, từ
`DataRemoteRepositoryImpl.getFacePuzzleTemplates()` → **`RemoteFacePuzzleService.getDataForHome()`
= `GET FacePuzzle/ios_data_facepuzzle.json`** — endpoint **v1**, KHÔNG phải v2).

**RESOLVED (fetch thật):** `ios_data_facepuzzle.json` (v1) trả **1 category duy nhất "Face
Puzzle" × 8 template** (`Video1`..`Video8`). Vì v1 chỉ có 1 category, hàm map v1
(`DataRemoteRepositoryImpl$getFacePuzzleTemplates$1`) làm phẳng toàn bộ video của
`ApiRepoListData<CategoryEntity>` thành 1 `List<FacePuzzleTemplateUI>` 8 phần tử — khớp đúng
field kiểu `StateFlow<List<FacePuzzleTemplateUI>>` (không phải `List<CategoryUI>`).

Cách trộn thật (`SharedViewModel$dataHomepage$1.invokeSuspend`, dòng 56-73 — **KHÔNG phải
`mixToListHomepageUI`**):
```kotlin
chunkedFace  = listFace(8 item).chunked(2)   // 4 nhóm × 2 item
chunkedFunny = listFunny(20 item).chunked(4) // 5 nhóm × 4 item
for (i in 0..4 của chunkedFunny) {
    chunkedFace.getOrNull(i)?.let { add(HomepageUI(isFace=true, it)) }   // chỉ 4 vòng đầu có face
    add(HomepageUI(isFace=false, chunkedFunny[i]))                       // funny luôn add đủ 5 vòng
}
```
→ Thứ tự chunk hiển thị (adapter riêng cho mỗi chunk, add nối tiếp vào `ConcatAdapter`):
```
[2 Face Puzzle] → [4 Funny] → [2 Face Puzzle] → [4 Funny] → [2 Face Puzzle] → [4 Funny] → [2 Face Puzzle] → [4 Funny] → [4 Funny]
```
Tổng: **8 item Face Puzzle + 20 item Funny Puzzle = 28 item**, chia 9 chunk-adapter nối tiếp
(4 chunk face 2-item + 5 chunk funny 4-item), render trong 1 `GridLayoutManager` 2 cột duy nhất
(`rvFacePuzzleTemplate`).

Mỗi cụm trở thành **1 `AdapterFacePuzzleTemplate`/`AdapterFunnyPuzzleTemplate` con riêng** được
add vào `ConcatAdapter` (`isolateViewTypes=true`) — không gộp chung 1 adapter cho toàn bộ list;
`GridLayoutManager` set trong XML `spanCount=2`, mỗi item content span=1.

**Thumbnail v1**: đã tải sẵn 8 ảnh thật (576×1024) vào
`/home/ubuntu/workspace/Design/App 6/Funny Face/assets/v1/31-template-v1/v1_Video<1-8>.png`.

**RESOLVED (round 2)** — nhãn "Nk uses" 8 item v1 (cùng công thức `MapperKt.round(likes/1000f,
1)+"k uses"` đã dùng ở mục 3.C, đã verify lại phép làm tròn khớp 100%):

| Video1 | Video2 | Video3 | Video4 | Video5 | Video6 | Video7 | Video8 |
|---|---|---|---|---|---|---|---|
| 273.3k uses | 716.8k uses | 22.5k uses | 18.8k uses | 49.4k uses | 164.4k uses | 28.2k uses | 39.9k uses |

(likes gốc: 273300/716845/22536/18833/49400/164400/28153/39900 — snapshot CDN endpoint v1,
category "Face Puzzle", folder `Face_Puzzle`). Không còn cờ chưa resolve cho phần dữ liệu
template của cụm Home.

**Ô Ad trong list**: `addFacePuzzleTemplate`/`addFunnyPuzzleTemplate` gọi
`AdapterFacePuzzleTemplate(0, activity, ..., showAdsInList=true mặc định do dùng hàm nội bộ
`FacePuzzleItem.ContentItem` **không** qua `createFacePuzzleItems` có cờ ad — thực tế
`FragmentHomeOldUI.observeHomeData$addFacePuzzleTemplate` tự build `arrayList` chỉ gồm
`ContentItem`, KHÔNG chèn `AdItem`. → **Giống UI mới: KHÔNG có ô ad chèn trong lưới
FragmentHomeOldUI.** Ad chỉ xuất hiện ở `nativeCollapsibleContainer` (đáy màn).

Item content = `item_face_puzzle_template.xml` / `item_funny_puzzle.xml`, giống hệt mục 3.C.

### D. Data hardcode

Giống mục 3.D (20 Funny Puzzle từ `data_funny.json`). Banner ảnh 2 cái là **local drawable**
cố định: `img_banner_face_puzzle.webp`, `img_banner_funny_puzzle.webp` (không đổi theo data).

### E. Nguồn từng view

| View | Nguồn |
|---|---|
| `imvBannerFacePuzzle` / `imvBannerFunnyPuzzle` | local drawable (webp), Glide load lại mỗi lần (signature=timestamp, không cache) |
| `btnMyLibrary` icon | local `@drawable/ic_layers` |
| Grid template Face Puzzle (8 ô) | **REMOTE endpoint v1** (`getDataForHome()` = `FacePuzzle/ios_data_facepuzzle.json`, 1 category "Face Puzzle" × 8), thumbnail thật đã tải sẵn ở `assets/v1/31-template-v1/` |
| Grid template Funny Puzzle (20 ô) | local asset (`data_funny.json` + `assets/face_funny/origin/`), giống mục 3.E |
| `nativeCollapsibleContainer` | AD SLOT `native_collapsible_home` |

### STATE

1. **HomeOldUI mặc định** (đã có dữ liệu remote v1): 2 banner tĩnh + nút My library + grid 28
   item (8 Face Puzzle + 20 Funny Puzzle, thứ tự chunk 2/4 xen kẽ — xem mục C).
2. **HomeOldUI — đang tải remote**: grid rỗng phía dưới banner (banner vẫn hiện vì local).
3. **HomeOldUI — có ad collapsible** ở đáy màn (256dp), đè phần cuối RecyclerView.

### Điều hướng từ HomeOldUI (click)
- `imvBannerFacePuzzle` → `actionToLevelPicker(null)` (Face Puzzle mode)
- `imvBannerFunnyPuzzle` → `actionHomeToListFunnyPuzzle` → `FragmentListFunnyPuzzle`
- `btnMyLibrary` → `actionHomeToVideoGallery`
- `btnSettings` → `actionHomeToSettings`
- Click item template trong grid: face puzzle → `MAIN_FACE_PUZZLE_CLICK` event + tương tự
  FragmentHome (mở fullscreen ad rồi điều hướng — logic click cụ thể nằm trong adapter lambda,
  không lặp lại ở đây vì đã mô tả pattern ở mục 3).

---

## 5. Điều hướng click chi tiết trong FragmentHome (UI mới)

| Nguồn | Hành động | Đích |
|---|---|---|
| `btnSettings` | click | `actionHomeToSettings` → FragmentSettings |
| `btnGalley` | click | `actionHomeToVideoGallery` → FragmentVideoGallery |
| Item Face Puzzle trong grid | click ảnh → set `OverlayView.Mode` theo `categoryId` (2→FacePop, 3→FaceWhirl, khác→FacePuzzle mặc định) → hiện fullscreen ad **AD SLOT `native_fullscreen_home`** (`AdKey.NATIVE_FS_HOME`) → `actionHomeToPreviewTemplate(item.url)` | FragmentPreviewTemplate |
| Item Funny Puzzle trong grid | click → log event `CATE_FUNNY_CHOOSE` → set `OverlayView.Mode.FaceFunny` → hiện fullscreen ad `native_fullscreen_home` → nếu RC **`level_picker_skipped`** (đã fetch = **false**, default nếu đọc `getBoolean` cũng false) → `actionToLevelPicker(item)`; nếu true → `actionHomeToFunnyPuzzle(item, level=2)` | FragmentLevelPicker (nhánh mặc định vì RC=false) |
| Ô ad trong grid | — | không xuất hiện trong UI mới (đã nêu ở 3.C) |

---

## 6. "2 tab con" (`tab_home`/`tab_gallery`) — CẢNH BÁO: DEAD CODE, KHÔNG THỂ TỚI ĐƯỢC

Đã grep toàn bộ source: `FragmentTabHome` (`ui/home/FragmentTabHome.java`) và
`FragmentTabGallery` (`ui/video_gallery/FragmentTabGallery.java`) **không xuất hiện trong
`main_nav.xml`**, **không được add vào bất kỳ `FragmentStateAdapter`/`ViewPager2` nào**, và
`newInstance()` companion của cả 2 lớp **không được gọi ở đâu khác ngoài chính nó**. Đây là
tàn dư của một kiến trúc cũ (rất giống mô hình "BottomNavigationView 2 tab: Home + Gallery")
đã bị thay thế bằng kiến trúc Navigation Component hiện tại (Splash → FragmentHome/HomeOldUI,
Gallery là 1 destination riêng `fragmentVideoGallery`, không phải tab). **Không có cơ chế
BottomNav/TabLayout+ViewPager2 nào kết nối 2 fragment này với nhau trong app đang chạy.**

Layout của chúng vẫn được resolve đầy đủ theo yêu cầu (để tư liệu hoá), nhưng **KHÔNG dựng
navigation/interaction nối 2 frame này vào flow chính ở Phase 6** — chỉ dựng làm 2 frame tham
khảo "orphaned/legacy", đánh dấu rõ nhãn "DEAD CODE – unreachable" trên Figma.

### 6.1 `fragment_tab_home.xml` (`FragmentTabHome.java`)

```
ConstraintLayout [fill,fill]
  AppCompatImageView btnSettings   [Base.PrimaryButton.Square, End=parent marginEnd=12, canh theo imvAppName]
  AppCompatImageView imvAppName    [w=wrap,h=28dp, marginTop=16, Top/Start/End=parent, src=@mipmap/img_app_name]
  TabLayout templateTabLayout      [fill w trừ margin 14, h=32dp, Top=đáy btnSettings — KHÔNG có marginTop riêng (khác FragmentHome có marginTop=12)]
  ViewPager2 templateViewPager     [fill w, Top=đáy tab, Bottom=parent — KHÔNG có homeNativeContainer/nativeCollapsibleContainer]
```
Khác biệt với `fragment_home.xml`: KHÔNG có 2 AD SLOT (`homeNativeContainer`,
`nativeCollapsibleContainer`), KHÔNG có `btnGalley`. Code (`FragmentTabHome.java`) dùng
CHÍNH `AdapterTemplateCategory` với `showAdsInList=true` (default param, vì gọi
`AdapterTemplateCategory(requireActivity, listener, false, 4, null)` — thực ra cũng truyền
`false` giống FragmentHome, xem constructor dòng 96 `... false, 4, null)`) → không chèn ad ô
lưới. `btnSettings` click → `actionHomeToSettings` (dùng chung `FragmentHomeDirections` — phụ
thuộc `fragmentHome` đang là destination hiện tại trong graph thật, nên nếu fragment này được
add rời sẽ crash logic điều hướng — càng khẳng định đây là code chưa hoàn thiện/orphan).

### 6.2 `fragment_tab_gallery.xml` (`FragmentTabGallery.java`)

```
ConstraintLayout [fill,fill]
  AppCompatImageView btnBack       [style=BackImageButton1, visibility=INVISIBLE cố định trong XML]
  AppCompatTextView appCompatTextView2 [style=ScreenTitleCommon, text="My library", elevation=10dp, canh giữa theo btnBack]
  RecyclerView rvContent           [fill w, GridLayoutManager spanCount=2, paddingBottom=@dimen/main_menu_height_offset, Top=đáy btnBack, Bottom=parent]
  AppCompatImageView imvEmpty      [50% width, tỉ lệ 1:1, src=@drawable/ic_empty, Bottom=lineCenterY(guideline 50%)]
  TextView tvEmptyNotify           [size=16sp bold, text=@string/video_gallery_empty_notify = "No videos yet! Try a fun filter and \n start recording!", Top=đáy imvEmpty]
  Group groupEmpty                 [gom imvEmpty + tvEmptyNotify, ẩn/hiện theo AdapterMyVideo.Listener.onIsEmpty(isEmpty)]
```
`btnBack` **cố định INVISIBLE** trong XML (khác `FragmentVideoGallery` thật, dùng
`btnBack` thường để pop back stack) — càng cho thấy đây là bản dựng cho ngữ cảnh "tab" (không
cần back, vì đáng lẽ nó là 1 tab trong bottom-nav, không phải 1 destination có back-stack).
Content = `AdapterMyVideo` (danh sách video người dùng đã lưu — **runtime placeholder**,
không phải asset bundled).

**KHÔNG có nhãn/icon tab thật để trích** vì không có `TabLayoutMediator`/BottomNavigationView
nào cấu hình title+icon cho 2 fragment này ở bất kỳ đâu trong source — nếu Figma cần label,
dùng suy đoán hợp lý "Home" / "Gallery" (tên class) và ghi rõ đây là suy đoán, không phải chuỗi
resolve từ code.

---

## 7. Rà theo checklist "hay bị sót"

- `res/menu/*.xml`: chỉ có 3 file, đều thuộc SDK debug ads (`axon_events_activity_menu.xml`,
  `creative_debugger_displayed_ad_activity_menu.xml`, `mediation_debugger_activity_menu.xml`)
  — **không có menu nào áp dụng cho toolbar của Home**. Nút Settings/Gallery trong Home là
  `ImageView` thường trong layout, không phải menu item.
- Custom view `onDraw()`: không có custom View/Layout riêng của app (`*View`/`*Layout` ngoài
  androidx) trong 2 layout Home — chỉ dùng widget chuẩn (ConstraintLayout, TabLayout,
  ViewPager2, RecyclerView, ImageView, TextView, FrameLayout, Space).
- RecyclerView ẩn: không có RecyclerView ẩn phụ nào trong 2 layout Home (đã liệt kê hết: 1
  RecyclerView lồng trong mỗi trang ViewPager của UI mới qua `item_pager_tepmlate_category.xml`,
  1 RecyclerView trực tiếp `rvFacePuzzleTemplate` trong UI cũ).
- ripple/selector bọc ảnh thật: `btnSettings`/`btnGalley` dùng
  `?selectableItemBackgroundBorderless` (ripple tròn hệ thống, không phải `<ripple><item
  drawable=.../></ripple>` custom); `tab_background` là selector state_selected thường (đã mô
  tả ở mục 3.C), không bọc ảnh.
- include/merge/ViewStub: không có trong 4 layout đã đọc (`fragment_home`,
  `fragment_home_old_ui`, `fragment_tab_home`, `fragment_tab_gallery`).

---

## 8. Tổng hợp cờ / chỗ chưa resolve tĩnh được (KHÔNG bịa)

1. **[RESOLVED round 1]** Tên + số lượng category Face Puzzle — đã fetch thật từ CDN
   (`BASE_URL=https://wallpaperhd.nyc3.cdn.digitaloceanspaces.com/`):
   - **FragmentHome (UI mới, `getDataHomepageV2()`)** → endpoint **v2**
     `FacePuzzle/ios_data_facepuzzle_v2.json` → đúng 3 category **Face Puzzle/Face Pop/Whirl
     Face**, mỗi category 6 template → 5 tab thật `["All","Face Puzzle","Face Pop","Whirl
     Face","Funny Puzzle"]`, trang "All" = 18 face + 20 funny = 38 item. Chi tiết đầy đủ + bảng
     "Nk uses" từng ô ở mục 3.C.
   - **FragmentHomeOldUI (`getDataHomepage()`)** → endpoint **v1** khác hẳn
     `FacePuzzle/ios_data_facepuzzle.json` → chỉ 1 category "Face Puzzle" × 8 template, trộn với
     20 Funny Puzzle theo chunk(2)/chunk(4) xen kẽ = 28 item. Chi tiết ở mục 4.C.
   - Đây là **snapshot CDN tại thời điểm audit** (không phải hardcode trong APK) — nội dung
     server có thể đổi bất cứ lúc nào, không có cơ chế version-pin trong app. 18 thumbnail v2 +
     8 thumbnail v1 đã tải về `assets/v1/30-template-v2/` và `assets/v1/31-template-v1/` để
     dùng làm ảnh thật khi dựng Figma.
2. **[RESOLVED round 2]** `useViewCounter` ("Nk uses") của 8 item v1 (FragmentHomeOldUI) — số
   likes gốc đã fetch đủ, bảng "Nk uses" đầy đủ ở mục 4.C (Video1..8: 273.3k/716.8k/22.5k/
   18.8k/49.4k/164.4k/28.2k/39.9k). Cụm Home hết cờ dữ liệu template.
3. **`FragmentTabHome`/`FragmentTabGallery`** — dead code, không có nhãn/icon tab thật (không
   `TabLayoutMediator` nào gán title cho chúng) — xem mục 6.
4. **`home_show_case`** (RC fetch=0) — key có thật trong `AdKey` nhưng không được đọc ở đâu để
   rẽ nhánh UI/nội dung nào → bỏ qua, không dựng theo giá trị này.
5. Kích thước `imvAppName` chiều rộng = `wrap_content` (theo tỉ lệ ảnh gốc mipmap) — không có
   con số cứng, Figma nên dùng tỉ lệ ảnh thật export từ `img_app_name.webp`.
6. `?colorPrimary`/`?selectableItemBackgroundBorderless` là theme attribute hệ thống — không
   trace được giá trị hex tĩnh trong phạm vi cụm Home (không đọc `themes.xml` đầy đủ ở lần
   audit này); ripple dùng màu hệ thống mặc định, pill tab active dùng `?colorPrimary` — khuyến
   nghị dùng cùng `primary_color=#ff016cf7` đã xác nhận ở nơi khác trong app làm giá trị suy ra
   hợp lý (KHÔNG phải giá trị resolve trực tiếp từ `themes.xml`, ghi rõ khi dùng trong Figma).
