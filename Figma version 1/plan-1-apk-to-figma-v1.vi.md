# Plan 1 — APK folder → Figma v1 (ưu tiên CODE, không sót)

> Quy trình tự chứa để dựng lại BẤT KỲ app Android thành plugin Figma từ file APK.
> Bản tiếng Anh: `plan-1-apk-to-figma-v1.en.md`.
>
> **Lập trường cốt lõi: CODE decompile là nguồn chân lý DUY NHẤT. Đọc cạn kiệt — tuyệt đối
> không sai, không sót. Screenshot chỉ là đối chiếu phụ, KHÔNG phải phương pháp chính.**

## Mục tiêu
Từ thư mục chứa 1 file `.apk`, tạo **plugin Figma** dựng lại app 1:1 (đúng dp, đúng chữ, đúng asset,
đủ mọi màn, mọi state) — độ chính xác **suy ra và kiểm từ chính CODE**, không phải nhìn mắt.

## Chỉ thị tối cao (theo thứ tự ưu tiên)
1. **Code là chân lý.** Mọi số/màu/chữ/asset/hành vi phải truy về file+dòng đã decompile hoặc resource
   đã resolve. Đọc **trọn** file liên quan — không lướt, không suy từ cái tên. Chưa rõ thì **resolve**
   (Phụ lục C), không đoán.
2. **Không sót gì.** Mọi nav destination, dialog, runtime state, item list đều suy từ code và có mặt.
   Độ phủ được **kiểm bằng máy đối chiếu với code** (Phase 6).
3. **Obfuscate/strip ⇒ resolve, không xấp xỉ.** Field code → giá trị R → `public.xml`/`resources.arsc`
   → tên thật. Không thay giá trị chưa resolve bằng phỏng đoán; đánh dấu rồi resolve.
4. **Screenshot là "thêm", không phải "cơ chế".** Độ đúng đến từ đọc code trọn vẹn + layout đã resolve
   + audit độ phủ. Bản render tự-xem (từ chính build của ta) là cái liếc kiểm; screenshot khách (nếu có)
   là đối chiếu thêm — plan phải đúng **kể cả khi KHÔNG có** screenshot.

Canvas chuẩn: **360×800 dp** (`sdp`==dp, `ssp`==sp ở bucket gốc). Không có status bar (UI hệ thống).

## Kit & yêu cầu cài đặt
Dùng `kit/` đặt cạnh plan — có sẵn tools + template đã kiểm chứng, generic, khỏi dựng lại mỗi app (xem
`kit/README.md`). Cài 1 lần: **apktool, jadx, node, python3+Pillow, Figma desktop**. Tools dùng chung →
`tools/` gốc repo: `build-plugin.py · verify.js + figma-mock.js · vd2svg.py · resolve-layout.py ·
resolve-arsc.py · fetch-remote-config.py`. Template mỗi app → `<App>/{figma/v1,script}/`: `code.js`
(khung — helper + registry `screen()/dialog()`; viết 1 builder mỗi màn/state), `manifest.json ·
build.sh · export-assets.py · download-remote.py · capture-scene.js · render-preview.py · make-v2.py`.

---

## Phase 0 — Chuẩn bị & giải nén
```
apktool d app.apk -o out        # res/ (layout, drawable, values) + AndroidManifest + *.properties
jadx -d out app.apk             # sources/ (java/kotlin) để đọc runtime; jadx cũng decode resources
grep -oE 'package=|versionName=|versionCode=' AndroidManifest.xml
```
- Đưa apk → `<App>/apk/`, giải nén → `<App>/decompiled/{resources,sources}`.
- **Split APK / bundle trước tiên.** Nếu nhận `.apks`/`.xapk`/`.apkm` hoặc base + `config.*`/`split_*`,
  **gộp trước khi decode** (`bundletool build-apks --mode=universal`, hoặc giải nén bundle rồi merge
  split) — không thì thiếu bucket density, thiếu vài drawable/lib, và resource id resolve ra NULL. Dấu
  hiệu sau này: `resolve-arsc.py` báo id NULL "likely split APK".
- **Đánh giá tuổi APK** (timestamp zip bị chuẩn hoá `1981`, vô dụng). Proxy: đọc
  `play-services-ads.properties` / `.properties` khác (version SDK ≈ mốc build); quét `res/drawable`
  tìm tên theo mùa. Nói với khách "build khoảng T, app trên máy có thể khác" — là dữ kiện, không phải
  cái cớ để xấp xỉ.

## Phase 1 — Dựng bản đồ màn CHÍNH XÁC từ code
- **Manifest = danh sách Activity.** App hay single-activity + Navigation → đọc `res/navigation/*.xml`
  (startDestination + mọi destination = 1 Fragment). ⚠ `startDestination` trong XML có thể bị code
  trong launcher Activity ghi đè — kiểm lại. Nav graph là **tập chuẩn** mọi màn phải đối chiếu đủ.
  Ghi cả Activity thứ 2 (overlay, activity hiệu ứng trong suốt).
- **Token thiết kế** từ `res/values/`: `colors.xml`, `styles.xml` (typography), `dimens.xml`.
  - ⚠ Đừng tin `colorPrimary` — màu brand thật của app template thường **hardcode trong layout**; đo
    tần suất: `grep -ohE '#[0-9a-fA-F]{6,8}' res/layout/{fragment,item,activity}_*.xml | sort | uniq -c | sort -rn`, rồi xác nhận nơi code set.
  - ⚠ **Dark theme thường GIẢ:** `values-night/colors.xml` rỗng + parent `DayNight` ≠ dark mode thật.
- **Font:** liệt kê `res/font/*.ttf` → map sang family Figma có sẵn (Google Fonts). Ghi view nào dùng
  font nào (heading, đồng hồ số, stencil…).
- **Resolve, đừng đọc raw.** Mọi layout chạy `tools/resolve-layout.py <res> <layout.xml>` để
  `@dimen/@color/@string/@drawable` thành giá trị thật. Còn sót raw `@…`/`0x…` = lỗ hổng phải lấp
  (Phase 6 / Phụ lục C), không phải giá trị để bịa.

## Phase 2 — Đọc runtime CẠN KIỆT (trái tim của plan)
Layout XML nói màn *có thể* chứa gì; **code quyết định cái người dùng THẬT SỰ thấy**. Với **mỗi**
fragment/activity trong nav graph, mở và đọc **trọn**: Fragment/Activity, chỗ dùng ViewBinding,
Adapter/Controller/ViewHolder, ViewModel/repository, và mọi custom `View` nó inflate. Chia song song
mỗi cụm 1 agent — nhưng mỗi agent phải ra spec **đầy đủ**, không phác thảo. Mỗi màn trả lời đủ 6 mục:

**A. Geometry** (từ layout đã resolve): mỗi phần tử `vai trò · x/y dp · w/h dp · nền #hex · bo góc`;
text = `chuỗi resolve thật · size sp · font · màu · canh`. Không bỏ sót phần tử.

**B. Visibility** (từ code): bảng `view | XML mặc định | setter runtime | điều kiện | KẾT QUẢ`. Biết
mỗi helper (`show()/gone()/inv()`, và loại *khác* `show(v,bool)`/`visible(v,bool)` có thể VISIBLE
**hoặc** GONE), nhánh mặc định, và mọi `if(state)/when(...)`. Bẫy: view khai báo `visible` có thể luôn
GONE; view `invisible` lại là trạng thái bình thường.

**C. List** (chính xác, từ code): mỗi list ghép thế nào — `enum.values()`, `listOf` hardcode, Epoxy
`buildModels`, Room DB, hay JSON remote → **đúng số lượng + tên + thứ tự**, *kể cả item code chèn*
(ô ad, ô "Add", promo cuối). `spanCount`/layoutManager có thể set trong code, khác XML. Số trong design
phải bằng số trong code (lệch 1 = sót item chèn).

**D. Data hardcode** — chép nguyên văn, đúng thứ tự: `grep -rn "arrayListOf\|listOf(\|enum class\|values()"`.
Lỗi tệ nhất: bịa N item trong khi code có M.

**E. Nguồn từng view:** local drawable / URL remote / switch theo mùa. Map model→field
(`@SerializedName`) để biết chính xác field nào nuôi ảnh/chữ nào. View có `src` có thể bị image loader
ghi đè; nhiều view không có `src` (set lúc chạy).

**F. Nhánh mùa / A-B / remote-config:** dựng **nhánh mặc định trước** (đa số user thấy). `grep -rn
"RemoteConfig\|getLong(\|getBoolean(\|Variant\|ShowUIEvent"`; đọc `res/xml/remote_config_defaults.xml`.
Key không có trong defaults → trả `0/false/""`. Mỗi mùa/variant có thể có geometry riêng cho cùng 1 view.

**State — gen đủ.** Một Activity/layout thường có nhiều state runtime; mỗi state là **1 frame riêng**.
Trục hay gặp: kết nối (tắt/đang kết nối/đã kết nối/mất); quyền (đã/chưa cấp); dữ liệu (rỗng/loading/có/
lỗi); gói (free-có-ads / đã mua PRO); lần đầu vs quay lại (onboarding/consent chỉ 1 lần, EU-only); cờ
tính năng (icon đổi theo cờ). Ưu tiên `buildX(f, state)` và đăng ký 1 `screen()` mỗi state để không sót.

**Hay bị sót — rà từng cái:**
- `res/menu/*.xml` inflate qua `getMenuInflater()` → nút toolbar (Settings/Share/PRO) **không có trong
  layout XML**.
- Custom view tên `*View`/`*Layout` **không** thuộc `android/androidx` vẽ phần nhìn thấy trong
  `onDraw()` (chấm step, progress, indicator) — vô hình trong cây layout. Mở class đọc `onDraw`.
- RecyclerView ẩn trong 1 layout (bảng chọn màu, list thiết bị, list ngôn ngữ, FAQ).
- Ripple/selector bọc ảnh thật (`<ripple>`→`<item drawable="@mipmap/…">`).
- Nền nung sẵn hoạ tiết (dấu "?" mờ, brush) — dùng ảnh thật, đừng vẽ tay.

**Cờ (ghi chú, không giả):** NativeAdView/banner = **AD SLOT**; Lottie/PAG/video = **animation** (Figma
tĩnh, ghi tên asset gốc); ảnh remote/API = **runtime**; UI OS/SDK (UMP/GDPR, In-App Review, cast/share
sheet, permission) = **placeholder có nhãn**.

## Phase 3 — Nội dung thật khi server điều khiển (vẫn suy từ code)
Nếu app kéo content/list từ server/CDN, riêng APK không khớp app thật — nhưng chính key của app lấy được
data thật một cách xác định (suy-từ-code, không nhìn mắt):
- Repo CDN private (raw host → 404 khi chưa auth) → token nằm trong **Firebase Remote Config**. Gọi y
  như app, dùng `google_api_key`+`google_app_id` trong `res/values/strings.xml`:
  ```
  POST https://firebaseremoteconfig.googleapis.com/v1/projects/<PROJECT_NUMBER>/namespaces/firebase:fetch?key=<google_api_key>
  {"appId":"<google_app_id>","appInstanceId":"<bất kỳ>"}
  ```
  → mọi tham số remote: token asset + mọi list remote (JSON). Tải ảnh bằng token → PNG.
- Xác nhận code đọc **field** nào (`image_url` vs `preview_url`, `thumbnail` vs biến thể mới hơn) — truy
  trong model/repository, không chọn "file nào trông mới nhất".
- **Bảo mật:** KHÔNG commit token (để `/tmp`); PAT hết hạn → fetch lại RC.

## Phase 4 — Xuất asset (tên = khoá, chính xác)
- **Bitmap** (`.webp/.png/.jpg/.gif`): bucket phân giải cao nhất; **đổi WEBP/GIF → PNG** (Figma không
  đọc WEBP; GIF → 1 frame đại diện). Tên file (bỏ đuôi) = khoá code tra ảnh.
- **VectorDrawable** (`drawable/*.xml`) → **SVG** (`tools/vd2svg.py`, xử lý pathData/gradient/alpha
  `#AARRGGBB`/evenOdd/group transform). Chỉ lấy PNG là mất sạch icon nav/settings — luôn convert vector.
  Render kiểm 1 icon sau khi convert.
- **Ảnh nung sẵn** (art dialog, ô danh mục, icon launcher): dùng **bytes gốc**, không vẽ lại.
- **Lề trong suốt không đều**: ảnh nguồn lề khác nhau → cùng khung mà chủ thể to/nhỏ lệch → chuẩn hoá
  (crop về bbox chủ thể rồi căn giữa cho chủ thể lấp cùng tỉ lệ cạnh ô).
- **Icon launcher là adaptive**: canvas 108dp, **safe zone 72dp (66%)**, mỗi máy mask khác (tròn/
  squircle/vuông). Xuất legacy 48→192px + round + adaptive foreground + màu nền + 512 cho store; chủ thể
  nằm trong safe zone.
- Asset resolve ra **id bị strip/split-APK** → resolve qua `resources.arsc`; nếu thật sự nằm trong split
  APK không có → **ghi nhận sự thật đó** (không âm thầm thay thế).

## Phase 5 — Dựng plugin (mỗi lớp truy về code)
Tách **asset** khỏi **code build** để thay ảnh không đụng logic. Tái dùng khung khai báo mỏng:
`frame/rect/ellipse/text/img/svgNode/photo` + registry `screen()/dialog()` + font loader + xếp trang.
Mỗi layer Figma phải truy về 1 view XML hoặc 1 lệnh code — không truy được ⇒ xoá (đừng thêm caption
trùng tên frame; cần ghi chú thì `setPluginData`).
```
python3 tools/build-plugin.py --src "<App>/assets/v1" --plugin "<App>/figma/v1"
# quét assets → base64 → assets.js/icons.js → ghép code.js → plugin.js → chạy verify
```
- **Font:** nạp mọi family đã map; thiếu style → lùi Regular + **log** (Figma **không tự fallback** —
  chữ non-Latin trong font Latin sẽ **trắng bóc**; chọn Noto Sans <hệ chữ> theo nội dung từng label:
  Ả Rập/Thái/Nhật/Hàn/Cyrillic…).
- **Dựng trước, xếp sau:** vài frame tự cao hơn base (grid đầy, list dài) → đo chiều cao **thật** sau
  khi dựng rồi mới xếp hàng và `f.resize(W, max(H, y+pad))` để không cắt/đè.
- **Nén ảnh nhúng** (~2× kích thước hiển thị): đục → JPEG q≈80; có alpha → PNG quantize. Nhẹ mà không
  lộ mắt.
- **Icon vector trong Figma** (`createNodeFromSvg`): chữ trong badge phải là **path** (đừng dùng SVG
  `<text>`); clip facet vào shape; chừa padding viewBox kẻo icon chạm mép container.

## Phase 6 — Audit độ phủ (suy từ CODE, KHÔNG cần screenshot)
Ép "không sót" bằng máy, đối chiếu với code:
1. **Phủ destination:** diff destination `nav_graph` (+ activity phụ) vs registry `screen()` →
   **không thiếu cái nào**. Mỗi fragment/activity có ≥1 frame (nhiều hơn nếu đa state).
2. **Phủ resolve:** chạy lại `resolve-layout` trên mọi layout đã dựng → khẳng định **không còn raw
   `@…`/`0x…`** trong thứ đã vẽ. Mỗi lỗ hổng resolve qua `public.xml`/`.arsc` hoặc gắn cờ rõ.
3. **Phủ số lượng:** mỗi màn list, `số suy-từ-code == số đã render`. Lệch 1 = sót item chèn; sửa.
4. **Phủ state:** mỗi fragment, liệt kê nhánh `setVisibility/when(state)` → mỗi nhánh map 1 frame.
   Nhánh chưa map = màn còn thiếu.
5. **Audit asset** (`tools/verify.js` + `figma-mock.js`): mọi asset code gọi đều tồn tại; mọi asset
   nhúng đều dùng hoặc log; không frame đè; không text rỗng. Kiểm bằng cách **chạy thật** plugin trong
   Figma-API giả (`sh <App>/script/build.sh`) — quét chuỗi tĩnh báo nhầm với asset tên ghép động.
6. **Lượt tự soi có cấu trúc:** đọc lại từng cụm chỉ hỏi "mình sót gì?" — một menu, một `onDraw`, một
   RecyclerView ẩn, một state chưa dựng, một field chưa kiểm. Phát hiện → sửa.
7. **Visual sanity (tuỳ chọn)** — render *chính build của ta* bằng font APK gốc (render từ scene suy-từ-
   code, KHÔNG phải ảnh chụp điện thoại):
   ```
   node <App>/script/capture-scene.js <App>/figma/v1/plugin.js > scene.json
   python3 <App>/script/render-preview.py     # → contact sheet mỗi page, font TTF gốc + asset thật
   ```
   Screenshot khách (nếu có) là đối chiếu thêm — nhưng audit ở trên mới đảm bảo đúng. Plugin dev Figma
   chỉ chạy **desktop**; chạy 1 lần → tự sync figma.com.

---

## Phụ lục A — Thông tin đúng nằm ở đâu (đừng đoán mấy cái này)
| Câu hỏi | Nguồn chuẩn (KHÔNG phải layout XML) |
|---|---|
| Màn này hiện bao nhiêu item? | Controller/Adapter/enum trong `sources/` |
| Có mấy ngôn ngữ/danh mục? | List hardcode trong file source tương ứng |
| View này có hiện không? | `setVisibility` trong Fragment binding + nhánh mặc định |
| Màu nền/nút? | `colors.xml` + shape `drawable/*.xml`, ưu tiên override trong code |
| Ảnh này từ đâu? | API/remote runtime nếu có; không thì `res/drawable` |
| Màn này có mấy biến thể? | remote-config key + enum biến thể |
| Icon launcher kích thước? | `mipmap-*/` (48→192px) + `mipmap-anydpi/ic_launcher.xml` (adaptive 108dp) |
| Thông báo kiểu gì? | Đọc code: `Toast` ≠ `Dialog` ≠ `Snackbar` |
| List item dùng layout nào? | `getDefaultLayout()` / adapter `onCreateViewHolder` |

## Phụ lục B — Cạm bẫy thường gặp (mỗi cái đều đã cắn 1 bản dựng thật)
1. **Layout ad-SDK lẫn vào** — `res/layout` có cả layout SDK (AppLovin/Mbridge/Google…). Chỉ giữ layout
   thuộc package app.
2. **Nhầm loại thông báo** — đừng mặc định "thông báo = dialog". No-internet hay là **Toast**. Đọc code.
3. **Màn giả / dark pattern** — dựng đúng nhưng ghi chú: "choose favorite" không cá nhân hoá gì; đồng hồ
   "sale" IAP reset mỗi lần mở; rating luôn trỏ 5 sao, <5 sao giữ feedback trong app, =5 sao đẩy ra store.
4. **Chữ non-Latin trắng bóc** — Figma không tự fallback font (Phase 5 fonts).
5. **Vẽ nav bar/tab mà app đang ẩn** — đọc `setVisibility` + variant đang chạy.
6. **Thiếu phần tử list** — lệch số → tìm item code chèn.
7. **Sai field ảnh API** — tải hết biến thể, xác nhận field code đọc.
8. **Sai nhánh mùa** — mỗi mùa có thể dời view (margin khác cho cùng XML).
9. **Frame đè nhau** — dựng-trước-xếp-sau + test overlap.
10. **Vẽ thừa card/label** — mỗi layer phải truy về XML/code; đừng bọc thêm ảnh vốn đã là 1 tile nung sẵn.
11. **Caption trùng tên frame** — dùng `setPluginData`, đừng thêm text lên canvas.
12. **Sai item layout** — kiểm `getDefaultLayout()` của binding model.
13. **Tin APK là mới** — đánh giá tuổi ở Phase 0.
14. **Tin `colorPrimary`** — đo tần suất màu thật trong layout.
15. **Sót menu resource** — đọc `res/menu/*.xml`.
16. **Sót `onDraw` custom view** — chấm/thanh vẽ trong code.
17. **Chỉ dựng state happy-path** — gen đủ mọi state.
18. **Giả UI hệ thống/SDK thành màn app** — UMP/GDPR, In-App Review, cast picker, share sheet,
    permission là OS/SDK; làm placeholder có nhãn, đừng bịa màn app.
19. **Render Lottie/PAG như art tĩnh** — SVG-từ-Lottie hay vỡ; dùng asset brand tĩnh hoặc SVG khớp tay +
    ghi chú "gốc là animation".
20. **Nội dung cao bị cắt** — vòng lặp (list thiết bị, FAQ, N ngôn ngữ) vượt base height → resize frame
    sau khi dựng.

## Phụ lục C — APK bị obfuscate / strip
- **Activity trong Manifest thường còn nguyên** dù obfuscate → bắt đầu bản đồ màn từ đây, không phải từ
  105 layout vô danh.
- **Giải mã resource id: code field → id → file.** `setContentView(A0.f3307a)` → tìm `f3307a =
  2131492892` trong R-holder → `0x7f0c001c` → `res/values/public.xml` `<public type="layout" …
  id="0x7f0c001c"/>` → layout thật. Chính xác, không đoán.
- **Bị strip khỏi `public.xml`?** Resolve id thẳng từ `resources.arsc`:
  `python3 tools/resolve-arsc.py app.apk 0x7f08016f` → đường dẫn file thật, hoặc "NULL → likely split
  APK" (gộp split ở Phase 0 rồi thử lại). Thêm `--type drawable --dump` liệt kê mọi id→path. Không thay
  giá trị chưa resolve bằng phỏng đoán.
- Viết/giữ `resolve-layout` in cây phần tử với `@string/@color/@dimen/@drawable` đã thay bằng giá trị
  thật — đọc layout obfuscate mà không có nó là đọc mù.

## Phụ lục D — Checklist mỗi màn
```
[ ] Đọc Fragment + adapter/controller (không chỉ XML)
[ ] Bảng visibility: view | XML | runtime | điều kiện | mặc định
[ ] Variant A/B + nhánh mặc định; remote-config key + giá trị khi chưa fetch
[ ] Thứ tự list chính xác kể cả item code chèn
[ ] Data hardcode chép nguyên văn
[ ] Nguồn từng ảnh: local / API / theo mùa
[ ] Ghi đè text & màu runtime
[ ] Bảng theme theo mùa (kể cả geometry riêng)
[ ] Liệt kê mọi runtime state, mỗi state 1 frame
[ ] Đã rà menu resource + onDraw custom view
[ ] Build → asset audit + overlap test
[ ] Các audit độ phủ (destination/resolve/count/state) đều đạt
```

## Phụ lục E — Thành thật về giới hạn (nói trước)
Không lấy tĩnh được từ APK, phải gắn nhãn: nội dung từ server/API (đổi bất cứ lúc nào), nhánh A/B khác
(chỉ dựng mặc định), state theo remote-config, phiên bản app trên máy khách, animation (Lottie/PAG/video
— Figma tĩnh), UI OS/SDK. Nói trước, đừng để khách phát hiện.

## Phụ lục F — Prompt agent trích spec (Phase 2, mỗi cụm)
Giao mỗi cụm màn cho 1 agent với prompt kiểu này (điền `<>`), để mỗi agent trả về spec *đầy đủ*, không
phác thảo:
```
Bạn trích spec UI CHÍNH XÁC từ APK Android đã decompile để dựng lại màn 1:1 trong Figma.
CHÍNH XÁC LÀ TRÊN HẾT — không bịa số/màu/chữ/asset; mọi giá trị truy về file. Chỗ runtime/remote/
animation/DB không resolve tĩnh được thì GẮN CỜ, đừng đoán.
PATHS: RES=<...>/decompiled/resources/res  APP=<...>/sources/<pkg>
TOOL (geometry chính xác): python3 tools/resolve-layout.py "<RES>" "<RES>/layout/<file>.xml"
Canvas 360×800 dp (sdp==dp). Báo mọi kích thước theo dp.
CỤM = <tên>. Layout: <fragment_x.xml + item/dialog>. Fragment: <XFragment.java + adapter + viewmodel>.
Mỗi màn: cây phần tử — vai trò · x/y dp · w/h dp · nền #hex · bo góc; text = chuỗi resolve thật · size
sp · font(@font resolved) · màu · canh. Ghi padding/margin.
RUNTIME (đọc Fragment/adapter): visibility mặc định (setVisibility/gone/show), text/màu set bằng code,
list ghép thế nào + ĐÚNG count/tên/thứ tự (tìm nguồn: enum/hardcode/DB/JSON remote), mọi runtime STATE
(mỗi nhánh setVisibility/when 1 cái). Cờ: NativeAdView=AD SLOT, Lottie/PAG/video=animation, ảnh remote/
API=runtime, UI OS/SDK=placeholder. Liệt kê mọi tên drawable (đánh dấu .webp).
Ghi spec đầy đủ ra <scratch>/specs/<cụm>.md; trả về summary NGẮN (count, kích thước chính, cờ).
```
Vì kỳ vọng là zero-omission, chạy thêm lượt **completeness critic** trên các spec: đọc lần 2 chỉ hỏi
"extractor sót gì — menu, custom onDraw, RecyclerView ẩn, state chưa xử, field chưa kiểm?" Đưa phát hiện
vào trước khi dựng.

---

## OUTPUT — cấu trúc thư mục (mỗi app; `tools/` dùng chung ở gốc repo)
```
<Gốc repo>/
├─ tools/                        # DÙNG CHUNG mọi app
│   ├─ build-plugin.py           # assets → assets.js/icons.js → plugin.js → verify
│   ├─ verify.js + figma-mock.js # chạy plugin trong Figma-API giả (kiểm cấu trúc)
│   ├─ vd2svg.py                 # VectorDrawable XML → SVG
│   └─ resolve-layout.py         # @string/@color/@dimen/@drawable → giá trị thật
└─ <App>/
    ├─ apk/<app>.apk
    ├─ decompiled/{resources,sources}   # resources=res+manifest+.properties; sources=java/kotlin
    ├─ assets/v1/                        # đã xuất; TÊN FILE (bỏ đuôi) = khoá code
    │   ├─ 01-<nhóm>/*.png   10-icons/*.svg   ...
    ├─ figma/v1/
    │   ├─ manifest.json  code.js  assets.js*  icons.js*  plugin.js*   (*=sinh ra)
    ├─ script/
    │   ├─ export-assets.py  download-remote.py  capture-scene.js  render-preview.py  build.sh
    └─ README.md                         # màn + ghi chú runtime + cách chạy Figma
```

## Coi là XONG khi
- Audit destination/resolve/count/state đều đạt → chứng minh được không sót, không còn chỗ chưa resolve.
- Mỗi layer Figma truy về một nguồn code/XML; mỗi mục gắn cờ đều có nhãn, không bịa.
- README ghi chính xác phần nào runtime/remote/animation/SDK.
- Nếu sau này có screenshot khách, nó **không lộ ra điều gì mới** — code đã cho ta biết trước.
