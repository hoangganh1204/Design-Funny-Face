# SDD ledger — plan: Design/App 6/Figma version 1/plan-1-apk-to-figma-v1.vi.md
App: Funny Face Mashup Challenge (com.filter.face.puzzle / code com.cem.face.puzzle)
APK: Funny Face/apk/app.apk (115MB, universal, không split, KHÔNG obfuscate)

## Pre-flight rulings
Ruling: Không git init — skill giả định repo git (worktree/commit/diff review package),
  project này là pipeline APK→Figma không phải codebase. Thay bằng artifact file:
  brief=briefs/<cụm>.md, report=reports/<cụm>.md, spec=specs/<cụm>.md, ledger=specs/progress.md.
  Cost nếu sai: không có git history để rollback; bù bằng spec file bất biến + audit Phase 6.
Ruling: Dispatch 7 agent Phase 2 SONG SONG, trái với "never parallel implementers" của skill.
  Lý do: skill cấm song song vì implementer sửa chung codebase; ở đây mỗi agent CHỈ ĐỌC
  decompiled/ và ghi 1 file spec riêng — không giao nhau. Plan 1 Phụ lục F mandate song song.
  Spec (Plan 1) là binding authority. Cost nếu sai: không có.
Ruling: Chạy Phase 3 (Firebase RC) TRƯỚC Phase 2. Lý do: spec mỗi màn phải ghi đúng count
  và nguồn ảnh; list remote quyết định count. Chạy sau sẽ phải viết lại spec.
  Cost nếu sai: không có, chỉ đổi thứ tự.
Ruling: Dựng CẢ FragmentHome và FragmentHomeOldUI (user: "cứ làm hết"), nhưng ghi rõ
  nhánh nào mặc định sau khi đọc code. Cost nếu sai: thừa vài frame, không thiếu.

## Pre-flight conflict scan (Plan 1 phases)
| Cặp | Sản xuất → tiêu thụ | Kết quả |
|---|---|---|
| P0→P1 | decompiled/{resources,sources} → nav graph + token | ✅ đủ: main_nav.xml 18 dest, 336 file app |
| P1→P2 | nav graph = tập chuẩn → 1 spec mỗi dest | ✅ 18 dest map hết vào 7 cụm, không sót |
| P3→P2 | RC remote lists → count/nguồn ảnh trong spec | ⚠ thứ tự đảo — đã ruling ở trên |
| P2→P4 | tên drawable trong spec → export-assets BITMAPS/VECTORS | ✅ spec bắt buộc liệt kê tên drawable |
| P2→P5 | spec → 1 screen() mỗi màn/state | ✅ |
| P4→P5 | assets/v1 khoá=tên file → imageFill(name) | ✅ build-plugin.py đối chiếu 2 chiều |
| P5→P6 | registry screen() → diff với nav graph | ✅ |
| P6 tự mâu thuẫn? | audit "không còn raw @…" vs ảnh remote | ⚠ ảnh remote không có trong res → dùng photo()/remoteTile() có nhãn, KHÔNG tính là raw chưa resolve |

## Tasks
Phase 0: complete — apktool 2.12.0 + jadx 1.5.1 cài tại ~/bin. 336 file app, 0 lỗi decompile
  trong com/cem/face/puzzle (123/29631 lỗi toàn ở SDK ads). KHÔNG obfuscate → bỏ Phụ lục C.
Phase 1: complete — main_nav.xml 18 destination, startDestination=fragmentSplash.
  16 font đều Google Fonts (Inter/Lato/Montserrat/Nunito/Onest/Poppins/Roboto) → Figma có đủ.
  Gần như không có màu hardcode trong layout (1 chỗ #66171716) → mọi thứ qua @color/.
Phase 3: complete — RC fetch THẬT từ project and-facepuzzle, 10 param, lưu /tmp/rc.json.
  Phát hiện: content KHÔNG remote mà BUNDLED trong APK (assets/face_funny/: data_funny.json
  20 entry + origin/*.png 20 + overlay/*.png 20). → KHÔNG cần download-remote.py.
  Cờ UI: onboarding_enabled=false, language_enabled=false, level_picker_skipped=false,
  home_show_case=0, ui_home_show_case=1, onboarding_buttons_enabled=true.
Phase 2: dispatched 7 agent song song (onboard, home, face-puzzle, funny-puzzle,
  preview-sound, result-video, settings-dialogs) — model sonnet, output specs/<cụm>.md.
Ruling: Hoãn tinh chỉnh MAXDIM trong tools/build-plugin.py đến khi có spec. Lý do: trần
  kích thước = 2× kích thước hiển thị thật, mà kích thước đó nằm trong spec Phase 2.
  Tạm dùng DEFAULT_MAXDIM=720. Tên nhóm của app cũ (01-nen-va-khung...) vô hại vì nhóm của
  app này đặt tên khác → rơi về default. NORM_GROUPS cũng không trúng. Cost nếu sai: ảnh
  nhúng to hơn cần thiết → plugin.js phình; sửa được bằng 1 lần build lại.
Kit patched: #1 render-preview.py SCRATCH -> <App>/build/ ; #2 build.sh đường dẫn thật.
Phase 4 (prep): 40 PNG nhân vật đã trích -> assets/v1/{20-nhanvat-origin,21-nhanvat-overlay}.
  Đối chiếu data_funny.json <-> file: 20 tham chiếu / 20 file, 0 thiếu, 0 thừa. ✅ count audit
Inventory res: KHÔNG có density bucket (mọi bitmap nằm ở drawable/ 611 file + nodpi/ 7).
  234 vector .xml thuộc app -> công việc chính của Phase 4 là vd2svg, không phải bitmap.
  mipmap: ic_launcher adaptive (anydpi xml + foreground.webp).
ĐỐI CHỨNG cho review spec preview-sound: res/raw/ có ĐÚNG 5 file .aac
  (audio, greedy_sped, jingle_bells, original_sound, spring_snow). Nếu spec báo số nhạc
  khác 5 thì phải giải thích (bài nào không dùng / có nguồn khác).
Phase 4 (prep, tiếp): drawable/ của app = 190 file (đã lọc SDK + bỏ $inline của apktool).
  Trong đó 74 là <vector> thật -> SVG qua vd2svg (test 20/20 OK, converter chạy được với app này).
  116 còn lại là <shape>/<selector>/<layer-list> -> dựng bằng rect/fill trong code.js, không phải SVG.
  Icon riêng của app có tiền tố `cem_ic_*`.

## Phase 2 — kết quả từng cụm
BUG trong brief của tôi: SRC ghi thiếu 1 cấp (jadx lồng sources/sources/). Đã sửa
  briefs/_shared-context.md. Các agent tự tìm ra đường đúng nên không ảnh hưởng spec.
Ruling: FragmentTabGallery (nằm ở package ui/home nhưng dùng chung adapter/VM với
  FragmentVideoGallery) thuộc spec result-video, KHÔNG thuộc home. Home chỉ tả khung tab.
  Lý do: tránh 2 spec mô tả chồng nhau lệch nhau. Cost nếu sai: home spec thiếu 1 tab -> bắt
  được ở audit Phase 6 mục 1.

Task result-video: DONE_WITH_CONCERNS -> task review (controller, grep đối chiếu source):
  ✅ Downloads/CemFacePuzzle ĐÚNG (truy được: FileUtilsKt.createFileDownload ->
     R.string.folder_name_my_library -> values/strings.xml:242 = "CemFacePuzzle") — agent
     resolve thật, không đoán.
  ✅ FragmentTabGallery có thật (4 file trong ui/home).
  ✅ item_time_record thuộc ui/face_puzzle/AdapterTimeRecord — agent gắn cờ ngoài-cụm đúng.
  ❌ FINDING (Important): @color/button_primary_text_color KHÔNG phải "không tìm thấy" —
     nó là ColorStateList ở res/color/button_primary_text_color.xml. Phase 6 mục 2 đòi
     không còn raw @… -> phải resolve, vào fix loop.
  ⚠  Claim "quét filesystem, KHÔNG phải MediaStore": grep của tôi trên ui/video_gallery/
     không thấy listFiles/MediaStore/.mp4 -> spec phải chỉ ĐÚNG file:dòng sinh ra list.
Task settings-dialogs: DONE -> review: ✅ fragment_settings.xml đúng 4 hàng
  (btnLanguage/btnPrivacyPolicy/btnTerm/btnShare), KHÔNG có hàng PRO/Remove-Ads -> khớp
  claim "không có IAP UI". ✅ face_mark/ có thật (FaceLandmarkerHelper, FaceOverlay,
  EyeClosureDetector, CameraManagerImpl) -> xác nhận AR camera thật.
Task onboard: DONE — RC key verify khớp, default=false, nhánh mặc định = Splash -> Home thẳng.
Task funny-puzzle: DONE — 20 item, KHÔNG có ô ad chèn (sửa giả định trong brief của tôi).

## Phase 2 — phân xử xung đột giữa các spec
Ruling (LOAD-BEARING): XUNG ĐỘT về ô ad trong lưới Home. spec face-puzzle nói
  "showAdsInList=true hardcode, FragmentHome có chèn ad tại index 2"; spec home nói
  "FragmentHome truyền false -> KHÔNG chèn". → VERIFY: FragmentHome.java:292 khởi tạo
  AdapterTemplateCategory(..., false) (lời gọi kết thúc bằng `}, false);`). spec home ĐÚNG.
  QUYẾT ĐỊNH: lưới Home KHÔNG có ô ad chèn; item_face_puzzle_ad.xml và item_funny_puzzle_ad.xml
  KHÔNG dựng trong luồng mặc định (chỉ ghi chú là code path tồn tại nhưng tắt).
  Cost nếu sai: đếm item lưới Home lệch -> bắt được ở audit Phase 6 mục 3.
Ruling: XUNG ĐỘT về FragmentTabGallery/FragmentTabHome. spec result-video coi TabGallery là
  màn thật; spec home nói DEAD CODE. → VERIFY: 0 hit trong main_nav.xml; chỉ được tham chiếu
  bởi Hilt generated DI (CemApplication_HiltComponents, Dagger...SingletonC) = auto-gen cho
  mọi @AndroidEntryPoint, KHÔNG phải lời gọi thật. spec home ĐÚNG.
  QUYẾT ĐỊNH: dựng 2 frame nhưng gắn nhãn "unreachable / dead code", LOẠI khỏi audit phủ
  destination Phase 6 mục 1. Đảo ruling trước đó về chủ sở hữu TabGallery.
  Cost nếu sai: 2 frame thừa có nhãn rõ, không gây sai lệch.

## Phase 3 vòng 2 — content remote ĐÃ RESOLVE (lấp cờ lớn nhất của spec home + face-puzzle)
CDN: https://wallpaperhd.nyc3.cdn.digitaloceanspaces.com/  (data/BuildConfig.java BASE_URL)
Endpoint: FacePuzzle/ios_data_facepuzzle.json (v1) và FacePuzzle/ios_data_facepuzzle_v2.json (v2)
v2 = 3 category x 6 video = 18 template: Face Puzzle(Face_Puzzle) / Face Pop(Face_Pop) /
  Whirl Face(Whirl_Face), mỗi cái Video1..Video6 + likes. Khớp OverlayView.Mode trong code.
v1 = 1 category (Face Puzzle) x 8 video (Video1..Video8) + field thumbnail.
URL thumb: FacePuzzle/<folder>/Thumb/<id>.png, NHƯNG MapperKt.java:86 đặt folder="" khi
  folder=="Face_Puzzle" -> FacePuzzle/Thumb/<id>.png (đó là lý do 6 file đầu trả 403).
Đã tải: 12 thumb (Face_Pop + Whirl_Face) + 8 thumb v1, rồi copy 6 v1 -> Face_Puzzle.
  => assets/v1/30-template-v2 = 18 file, 31-template-v1 = 8 file. Ảnh THẬT 576x1024.
"likes" -> nhãn "<round(likes/1000,1)>k uses" (MapperKt) — vd 273300 -> "273.3k uses".
Task result-video: fix round 1/5 (2 addressed, 0 open) -> fix round 2/5 (1 addressed, 0 open).
  complete (specs/result-video.md, review clean). Agent tự verify lại ruling trước khi sửa.

## Phase 4 — phát hiện & ruling
GOTCHA KIT (mới, chưa có trong Plan 1): app này để ẢNH NỘI DUNG trong res/mipmap-*, không phải
  res/drawable-*. export-assets.py của kit chỉ quét BUCKETS drawable-* -> sẽ MISS hết
  bg_level_easy/intermediate/difficulty, img_app_name, window_bg. Phải thêm mipmap-* vào BUCKETS.
  (mipmap-xxhdpi là bucket cao nhất cho ảnh nội dung; xxxhdpi chỉ có icon launcher.)
Ruling (LOAD-BEARING): img_intro_1/2/3 KHÔNG TỒN TẠI trong APK. Bằng chứng dứt khoát:
  - R.java:157-159 có hằng số img_intro_1/2/3 = 0x7f080248/249/24a
  - FragmentIntro.java:118 setupViewPager() dùng đúng 3 hằng số đó
  - values/public.xml KHÔNG có entry nào cho 3 id này (dãy nhảy 0x…247 -> 0x…24b)
  - resolve-arsc.py: NULL in every config cho cả 3 id
  - unzip -l apk: không có file nào tên img_intro* ở bất kỳ bucket nào
  - KHÔNG phải split APK (đã loại trừ ở Phase 0: không lib/, không split_*, có resources.arsc)
  Nguyên nhân nhiều khả năng: resource shrinking hoặc dấu vết quá trình reskin (package khai báo
  com.filter.face.puzzle != package code com.cem.face.puzzle).
  QUYẾT ĐỊNH: dựng 3 frame Intro với ô ảnh là PLACEHOLDER CÓ NHÃN ("img_intro_N — không có
  trong APK"), tuyệt đối KHÔNG thay bằng ảnh tự chọn. Theo Plan 1 Phase 4: "ghi nhận sự thật đó,
  không âm thầm thay thế". Ghi vào README bàn giao.
  Cost nếu sai: 3 ô ảnh trống có nhãn thay vì ảnh thật; nếu sau này có bản APK khác đủ asset thì
  thả file vào assets/v1 đúng tên là build lại được ngay (khoá = tên file).
Task face-puzzle: fix round 1/5 (2 addressed, 0 open). complete.
  Chốt được: FragmentHome -> getDataHomepageV2() (v2, 18 template);
             FragmentHomeOldUI -> getDataHomepage() (v1, 8 template). CẢ HAI endpoint đều dùng.
Task preview-sound: fix round 1/5 (1 addressed, 0 open, +2 cờ agent tự resolve thêm). complete.
  Còn đúng 4 cờ THẬT (runtime, không phải resource ref) — đúng tinh thần plan.
Task home: fix round 1/5 (1 addressed + agent TỰ phát hiện và sửa 1 lỗi của chính nó về
  mixToListHomepageUI). Chốt: FragmentHome = 5 tab (All 38 / FacePuzzle 6 / FacePop 6 /
  WhirlFace 6 / FunnyPuzzle 20); FragmentHomeOldUI = grid liên tục 28 ô (8 v1 + 20 funny),
  logic chunked(2)/chunked(4). complete.
Task onboard: fix round 1/5 (1 addressed + agent tự resolve thêm 4 cờ bằng smali:
  bg_splash gradient #ffffff->#08bdff dọc; showLoading() là DEAD CODE; traveledPages
  early-return; bg_item_setting là shape tĩnh không phải selector). complete.
  Verify của tôi: fragment_splash.xml chỉ dùng bg_splash+ic_splash; img_app_name thuộc
  layout home; window_bg chỉ là windowBackground cấp theme -> claim của agent đúng.

## Phase 5 — kiến trúc build
Ruling: vá tools/build-plugin.py để ghép thêm figma/v1/screens/*.js (sorted) và main.js,
  sau code.js. Lý do: 7 agent viết song song không thể cùng sửa 1 code.js. Thay đổi là
  ADDITIVE (không có screens/ thì hành xử y như cũ) nên kit vẫn dùng được cho app khác.
  Cost nếu sai: không, đã test node --check.
Ruling: TÁI DÙNG 7 agent cụm làm builder Phase 5 thay vì spawn agent mới. Lý do: họ đã giữ
  số liệu spec trong context, agent mới phải đọc lại spec (tốn hơn, dễ sai hơn). Cũng giữ
  tổng số agent ở 7 thay vì 14, trong hạn mức workflow size.
  Cost nếu sai: context các agent đã nặng (200-320k); nếu chất lượng builder giảm thì phải
  dispatch agent mới đọc spec từ file.
code.js: điền token THẬT — primary #016cf7, theme LIGHT (Theme.AppCompat.Light.NoActionBar),
  text mặc định 14sp/#171716/Lato. 7 họ font map sang Google Fonts (Lato/Inter/Montserrat/
  Nunito/Onest/Poppins/Roboto) — Figma có đủ, không lo lỗi chữ trắng.
Đánh số frame để không trùng: 10-12 onboard · 20-21 home · 30-31 face-puzzle ·
  40-41 funny-puzzle · 50-53 preview-sound · 60-62 result-video · 70-72 settings ·
  90-91 dead code. Dialog dùng tiền tố D.
Phase 5 settings-dialogs: DONE — 3 screen + 4 dialog, node --check sạch, khoá ảnh đều tồn tại,
  token C.* hợp lệ. Agent phát hiện thêm dark-pattern: imgViewClose (mũi tên) KHÔNG có onClick,
  chỉ imgDismissNative vô hình mới đóng được -> đã dựng kèm chú thích.

## Gotcha KIT #5 (nặng, phát hiện bởi agent face-puzzle, tôi verify rộng hơn)
tools/verify.js hook vào plugin bằng phép thay CHUỖI CHÍNH XÁC có dấu cách:
  'function imageFill(name, scaleMode) {'  và  'async function main() {'
NHƯNG templates/code.js của chính kit viết dạng NÉN: 'function imageFill(name,scaleMode){'.
=> cả 3 phép thay đều TRƯỢT, im lặng. Hậu quả: audit asset + audit unused của Phase 6 mục 5
   KHÔNG BAO GIỜ CHẠY, mà verify vẫn báo xanh. Đây là lỗi kit có sẵn, ảnh hưởng MỌI app dùng kit.
Đã sửa: thay bằng regex \s*-tolerant + in cảnh báo rõ ràng nếu không hook được (thay vì im lặng).
Sửa cùng lỗi ở script/capture-scene.js (cũng dùng chuỗi có dấu cách).
Cost nếu sai: đã node --check cả 2; sẽ chạy thật ở bước build.
Phase 5 face-puzzle: DONE — 8 screen, 0 overlap, 0 asset thiếu (agent tự build thử full plugin).
  Agent tự bắt bug của chính mình: img() không tự add() vào parent -> đã sửa 9 chỗ.
Phase 5 onboard: DONE — 7 screen + 1 dialog. Thành thật 2 chỗ: viền nét đứt vẽ thành nét liền
  (helper không hỗ trợ dash), AD_H=100 là ước lượng wrap_content -> đều ghi chú trong code.
Phase 5 preview-sound: DONE — 8 screen + 2 dialog. Agent tự viết smoke-test chạy cả 10 builder
  với ASSETS/ICONS rỗng (ép nhánh fallback) -> 0 lỗi. Phát hiện z-order: ad collapsible add SAU
  nút CTA nên khi hiện sẽ CHE nút -> state đó không vẽ nút.

## Phase 6 — KẾT QUẢ CUỐI (sau fix tab)
1 phủ destination ✅ 18/18 · 2 phủ resolve ✅ 0 raw · 3 phủ số lượng ✅ 10/10 ·
4 phủ state ✅ 23 màn/15 đa state · 5 asset ✅ (1 thừa hợp lệ ic_launcher_foreground) ·
6 overlap+text rỗng ✅ · 7 render self-check ✅ 59 frame font TTF gốc.
Build: 59 frame (49 screen + 10 dialog), 1256 node, plugin 3.9 MB, 83 asset nhúng.

Ruling: audit 3 bản ĐẦU báo lệch +4 ở mọi frame có nhân vật -> điều tra ra BỘ ĐẾM CỦA TÔI SAI,
  không phải bản dựng: mỗi thẻ = 1 node ảnh + 1 node text, mà 4 nhân vật (Jennie/Ronaldo/
  Naruto/Rose) có tên hiển thị TRÙNG tên file ảnh nên bị đếm 2 lần. Sửa: chỉ đếm node có
  IMAGE fill -> 10/10. Bài học: không sửa builder theo con số audit đầu tiên chưa kiểm.
Ruling: KHÔNG viết trình rasterize SVG cho render-preview. Lý do: môi trường không có pip/
  cairosvg/rsvg/inkscape; viết parser path đầy đủ (M/L/C/Q/A) là việc lớn cho một công cụ QA
  PHỤ, trong khi audit 1-6 mới là thứ bảo đảm đúng. Thay bằng silhouette đúng màu fill thật.
  Cost nếu sai: ảnh self-check không thấy hình icon thật; icon vẫn đúng trong Figma (26 SVG
  đều có trong bundle). Đã ghi thẳng giới hạn này vào README.
Fix tab (từ render self-check): home_drawTabs dùng tabMinWidth=40dp làm chiều rộng CỐ ĐỊNH,
  thật ra styles.xml TemplateTabLayout ghi tabMinWidth là TỐI THIỂU + tabMode=scrollable +
  padding 8dp. Agent sửa: w = max(40, đo_chữ + 16). Chip mới: All=40 · Face Puzzle=89.2 ·
  Face Pop=68.3 · Whirl Face=82.2 · Funny Puzzle=96.2 (tràn 360dp -> bị cắt, ĐÚNG vì scrollable).
  Đây là lỗi mà 6 audit tự động KHÔNG bắt được (chúng kiểm cấu trúc/số lượng, không kiểm
  hình học chữ) -> minh chứng Phase 6 mục 7 là cần thiết.
README.md: viết xong, ghi rõ 5 nhóm giới hạn + 6 lỗi kit đã vá.
PLAN 1: HOÀN TẤT.

## PLAN 2 — reskin v2
Luật 1 (màu): SAMPLE trước rồi mới chọn góc, đúng yêu cầu plan.
  Họ brand v1 đo được: hue 181-214 deg, S 98-100%, L 48-52% (cyan -> xanh dương), rất chặt.
  Thử 9 góc, tính tương phản WCAG chữ đen #171716 trên primary:
    v1 (0 deg)  #016cf7 -> 3.84 (DƯỚI chuẩn AA 4.5 — chính app gốc đã vậy)
    +90 deg     #f701e7 -> 5.22 ✅ VƯỢT AA, magenta, cách đỏ chức năng 55 deg
    +150 deg    #f71101 -> đụng đỏ chức năng, LOẠI
    +240 deg    #6cf701 -> 12.76 nhưng xanh neon chói, dễ nhầm màu "thành công", LOẠI
  CHỌN +90 deg: vừa đổi nhận diện rõ, vừa CẢI THIỆN độ đọc chữ đen trên CTA.
Ruling: dùng QUY TẮC THEO HUE thay vì liệt kê tay từng hex. Màu nằm trong dải 165-230 deg
  và S>=0.35 -> xoay; ngoài dải hoặc S thấp -> giữ. Lý do: screens/*.js có 25 hex viết thẳng
  ngoài bảng C, liệt kê tay chắc chắn sót. Cost nếu sai: màu brand lạ ngoài dải bị bỏ sót —
  đã kiểm bằng cách render đối chiếu v1/v2.
Luật 2 (nền): app theme LIGHT -> dịch trong dải sáng, KHÔNG đảo tối.
  7 bề mặt gần-trắng retint nhẹ về hue mới (f4f4f4->f6f2f6, e6e6e5->e8e3e8...).
  KHÔNG đụng #ffffff, #000000, scrim, màu chữ — đúng cảnh báo của plan.
Luật 3 (bo góc): +1 bậc — card 12->16, tile 16->20, sm 8->10, dialog 16->20, r12 12->16.
  GIỮ NGUYÊN pill 30 và r69: silhouette đặc trưng, plan cấm đổi.
Luật 4 (asset): 46 ảnh nội dung (20 nhân vật + 26 thumbnail) KHÔNG ĐỤNG, verify khớp BYTE.
  11 PNG + 26 SVG art brand xoay hue theo cùng quy tắc pixel-level (giữ pixel trung tính và
  pixel ngoài họ brand -> hoạ tiết xám không bị ám màu, cam/đỏ trong art không lệch).
Luật 6: make-v2.py sinh TOÀN BỘ v2 (9 file js + manifest + assets). KHÔNG fork tay file nào.
  Sửa v1 -> chạy lại -> v2 luôn khớp.

## AUDIT PLAN 2 — tiêu chí "coi là XONG"
1. Số frame        v1=59  v2=59   ✅
2. Số node         v1=1256 v2=1256 ✅ layout Y HỆT
3. Toạ độ/kích thước 59/59 frame giữ NGUYÊN ✅ (Back/Next không đổi chỗ)
4. Thứ tự layer    ✅ không đảo frame nào
5. Ảnh nội dung    ✅ khớp BYTE với v1 (3 nhóm, 46 file)
6. Art brand       ✅ 6/11 PNG + 6/26 SVG đổi màu (số còn lại vốn trung tính, đúng)
7. Token           primary #016cf7 -> #f701e7 · 3 bề mặt retint
Ruling: GIỮ NGUYÊN màu 3 thẻ Level (Easy xanh lá / Intermediate vàng / Difficulty hồng).
  Lý do: đó là THANG ĐỘ KHÓ mang ý nghĩa chức năng, Luật 1 nói rõ "giữ màu chức năng —
  chúng mang ý nghĩa, không phải brand". Xoay sẽ phá thang màu dễ->khó.
  Cost nếu sai: màn Level Picker trông giống v1, reskin kém triệt để ở đúng 1 màn.
  -> Đã nêu cho user quyết định.
PLAN 2: HOÀN TẤT.

## PLAN 2 — VÒNG 2: chỉnh lại màu (user: "màu chưa đẹp và chưa hợp lý")
Chẩn đoán: vấn đề KHÔNG ở góc xoay mà ở ĐỘ BÃO HOÀ. Xoay cơ học giữ S=99% — mức đó hợp
  với xanh dương nhưng sang magenta thành neon chói, mà app nền TRẮNG + đầy ẢNH NGƯỜI THẬT
  nên màu chói đánh nhau với tông da.
Ruling: áp biến đổi ĐỒNG NHẤT trên CẢ BA kênh thay vì chỉ hue. Vẫn giữ tính nhất quán của
  họ màu (đúng tinh thần Luật 1) nhưng chỉnh được thẩm mỹ:
    +65 do  -> primary H214 -> H279 (tím violet: màu giải trí/sáng tạo, bổ trợ tông da ấm;
               cách đỏ chức năng 81 do, cách xanh v1 65 do)
    S x0.82 -> 99% -> 81% (hết neon, vẫn rực)
    L x0.90 -> 49% -> 44% (đậm lại để chữ TRẮNG đạt chuẩn)
  primary #016cf7 -> #8b15ca. Cost nếu sai: khác plan ở chỗ plan chỉ nói "xoay hue"; nhưng
  plan cũng bắt "kiểm lại độ đọc sau khi đổi màu" nên tinh chỉnh là bắt buộc, không phải thêm.
Ruling: ĐỔI MÀU CHỮ trên nền brand sang trắng. v1 dùng #171716 trên xanh = 3.84 (DƯỚI AA).
  v2 primary đậm hơn nên chữ đen sẽ càng tệ -> chuyển trắng = 6.87 (AA chữ thường, AAA chữ lớn).
  Thay CÓ CHỦ ĐÍCH đúng 3 chỗ (btnSave x2, Button.Primary, dòng adsNote của Splash) —
  C.textHi còn 39 chỗ khác là chữ trên nền trắng, KHÔNG đụng.
  Cost nếu sai: nếu app gốc cố ý dùng chữ đen thì v2 lệch ở 3 nút; nhưng v1 vẫn giữ nguyên
  bản gốc nên đối chiếu được.
BẮT ĐƯỢC 1 LỖI TỰ GÂY RA: dòng "This action contain ads" nằm ở ĐÁY gradient Splash. Sau khi
  làm gradient đậm hơn, tương phản tụt 8.56 -> 2.34 (FAIL nặng). Đo tại ĐÚNG toạ độ y=758 mới
  thấy — đo ở màu token thì không lộ. Đã sửa sang chữ trắng -> 7.67. Dòng "Loading..." ở trên
  vẫn 8.18 nên GIỮ đen (không sửa mù cả màn).
QUÉT TOÀN BỘ 382 node text, đối chiếu v1 vs v2:
  0 node tụt tương phản thật · 15 node TĂNG · các cảnh báo còn lại là artifact của bộ quét
  (không suy được nền cho chữ đặt tuyệt đối dạng sibling — giống hệt nhau ở cả v1 và v2).
Audit Plan 2 chạy lại: 59 frame · 1256 node (= v1) · toạ độ/kích thước/thứ tự layer giữ nguyên ·
  46 ảnh nội dung khớp BYTE.

## MÔ PHỎNG vùng camera AR (user yêu cầu lấp 2 màn quay)
Ruling: sinh ảnh MÔ PHỎNG thay vì để ô trống, NHƯNG gắn nhãn "MÔ PHỎNG" ngay trên canvas.
  Không dùng ảnh người thật nào: khuôn mặt là hình khối tổng hợp do script vẽ.
  Không dùng thumbnail template thay thế (Plan 1 cấm "âm thầm thay thế").
  Cost nếu sai: người xem nhầm là ảnh chụp app thật -> đã chặn bằng nhãn trên canvas +
  ghi trong README + tên script make-mock-ar.py.
SAI RỒI SỬA (2 vòng, đáng ghi lại):
  Vòng 1: tôi GIẢ ĐỊNH overlay có lỗ khoét trong suốt ở vùng mặt, mặt người dùng lộ qua lỗ.
    -> dò alpha: lỗ nội bộ lớn nhất chỉ 26 pixel (răng cưa). GIẢ ĐỊNH SAI.
  Vòng 2: đọc OverlayView.java:1311-1317 mới ra thứ tự thật:
      drawFunnyOverlay(canvas, funnyModeInfo);        // overlay nhân vật (mặt TRỐNG) vẽ TRƯỚC
      drawFunnyComponent(canvas, list2, funnyModeInfo);  // nét mặt người dùng vẽ LÊN TRÊN
    Tức là NGƯỢC hẳn: không khoét lỗ mà dán nét mặt lên mặt trống của nhân vật.
  Bài học: dò asset để đoán cơ chế là sai hướng — phải đọc thứ tự vẽ trong code trước.
FacePuzzle mode khác hẳn FaceFunny: drawFacePuzzleComponent cắt mặt thành 6 vùng rồi
  dịch/xoay, KHÔNG có art nhân vật -> mock riêng, không dùng chung.
Kết quả: 3 ảnh mock (mock_camera_face, mock_ar_facepuzzle, mock_ar_funny_1) lắp vào
  helper cameraBg() của face-puzzle và fnp_drawChrome() của funny-puzzle — sửa đúng 2 hàm,
  áp cho cả 14 frame (30a-30f, 41a-41h). node 1256 -> 1268 ở CẢ v1 và v2 (vẫn khớp nhau).

## LẤP FRAME TRỐNG (user: "còn nhiều ảnh trống, trình lên lead")
Đo trước khi làm: quét scene.json đếm node/frame. Trung vị 11. 22 frame dưới mức đó,
  tệ nhất 3 node (D60, D61, D70, D72, 41g) = 1 ô đen + 1 dòng chữ.
Bốn nhóm, bốn cách lấp khác nhau (KHÔNG lấp mù):
  1. Privacy/Terms -> VĂN BẢN THẬT trong APK. CompanyInfoFragment.java:119,122 nạp
     assets/privacy_policy.html (89 đoạn) + term_of_use.html (57 đoạn). Trích ra
     build/policy-text.json. Đây là nội dung thật -> KHÔNG cần nhãn mô phỏng.
  2. Native ad -> GEOMETRY THẬT từ ads_native_media_common.xml + native_fake_full_inter.xml.
     Chuỗi "AD" và "Install" là text thật trong layout. Nội dung quảng cáo cụ thể là runtime
     -> placeholder trung tính, CẤM bịa tên thương hiệu.
  3. Overlay loading -> vẽ CHỒNG lên chrome màn nền thật (đúng cách chúng xuất hiện trong app),
     thay vì hình chữ nhật trơn.
  4. Khung video/preview -> dùng 3 ảnh mô phỏng AR đã sinh, kèm nhãn MÔ PHỎNG.
Ruling: frame nào VỐN DĨ trống trong app thật thì GIỮ TRỐNG (30b/30c app ẩn chrome khi quay,
  62 empty state, 90 dead code, D60 interstitial của SDK). Đầy đặn không quan trọng bằng đúng.
  Cost nếu sai: lead hỏi "sao trống" -> note trên frame trả lời được.

## BA LẦN AGENT BÁC LẠI COORDINATOR — cả ba đều đúng
1. funny-puzzle: tôi đưa 2 layout native ad để tham khảo; nó kiểm AdKey.INTER_RECORD tiền tố
   INTER_ -> interstitial do SDK vẽ, không phải native. Verify: layout interstitial duy nhất
   trong APK là của Bigo SDK. Nó TỪ CHỐI gán bừa và dựng khung tối giản có nhãn.
2. result-video: đọc raw XML, phát hiện brief của tôi SAI MÀU:
   backgroundTint="#33000000" (nền đen 20%, không phải xám f4f4f4) và
   backgroundTint=@color/gnt_blue #4285f4 (nút xanh, không phải trắng).
3. settings-dialogs: cũng tự đọc raw XML nên đã bắt đúng từ trước, đính chính của tôi trùng khớp.

## GOTCHA KIT #7 — resolve-layout.py nuốt mất backgroundTint
KEEP list thiếu backgroundTint -> output chỉ có `background=`, mất trọn lớp tint đè lên.
Tôi dán output đó vào brief nên truyền lỗi xuống agent. Đã vá: thêm backgroundTint,
foregroundTint, drawableTint, iconTint, elevation, alpha, strokeColor, strokeWidth, rotation.
(elevation cũng từng bị bỏ sót -> agent result-video phải tự đọc raw XML mới thấy shadow 10dp.)
Bài học: THIẾU THUỘC TÍNH TRONG KEEP = IM LẶNG MẤT THÔNG TIN, không có cảnh báo nào.

## GOTCHA KIT #8 — font APK bị subset, thiếu glyph tiếng Việt
lato_regular_400.ttf trong APK KHÔNG có đ ạ ầ ă ả Ậ ừ (test bằng cách so chữ ký ảnh render
với .notdef; test PIL getbbox() ban đầu SAI vì .notdef vẫn có bbox).
Không ảnh hưởng file Figma (Figma dùng Lato của Google Fonts, đủ tiếng Việt) nhưng ảnh
preview vẽ bằng chính TTF của APK nên chữ Việt ra ô vuông.
Đã vá render-preview.py: dò glyph thiếu rồi tự lùi sang DejaVu Sans cho ký tự đó.

## LỖI TỰ GÂY RA RỒI TỰ BẮT (vòng này)
71/72 chồng chữ: agent dùng y-cursor += node.height, nhưng helper text() trong code.js đặt
  textAutoResize='HEIGHT' rồi đọc t.height — trong mock capture-scene t.height=0 nên rơi về 1,
  con trỏ chỉ nhích 9px. Trong Figma thật CÓ THỂ đúng, nhưng không kiểm được -> bắt sửa thành
  tính số dòng tường minh (CW=5.6, LH=16) rồi truyền o.h, để render GIỐNG NHAU ở cả hai nơi.
  Bài học: không giao cho lead thứ chỉ "có thể đúng".
Kết quả: node 1268 -> 1380 ở CẢ v1 và v2, vẫn khớp nhau tuyệt đối, 0 lệch toạ độ.
Audit Phase 6: destination ✅ · resolve ✅ 0 raw · count ✅ 10/10 · state ✅ · truy vết ✅ 0 thiếu note.
Fix cuối: hộp tên nghệ sĩ w=90 -> 56 trong soundItem() (dùng chung 3 frame 52/52b/D53).
  => chồng chữ THẬT toàn file = 0.
Ruling: bộ đếm chồng chữ đầu tiên báo 51 -> SAI, vì chỉ so khoảng y không xét x nên hai text
  NẰM CẠNH NHAU cũng bị tính. Đo lại có xét giao cả hai trục: 12, cùng 1 nguyên nhân.
  Đây là lần thứ 2 bộ đếm của tôi báo động giả (lần 1: audit count lệch +4 vì đếm cả node
  text trùng tên file ảnh). Bài học: luôn kiểm mẫu cụ thể trước khi tin con số tổng.
TRẠNG THÁI CUỐI: 59 frame · 1378 node · v1==v2 tuyệt đối (0 lệch toạ độ) · 0 chồng chữ ·
  mỏng nhất 7 node (trước 3) · trung vị 14 (trước 11) · audit Phase 6 đủ 7/7.
README cập nhật: mục v1/v2, mục ảnh mô phỏng AR, gotcha #7 #8, sửa mục WebView đã lỗi thời.
Fix (user phát hiện): thumbnail imvFunnyOrigin là Cristiano_Ronaldo nhưng lớp AR mô phỏng
  lại sinh từ overlay 1.png = Kylian Mbappe -> MÂU THUẪN trong cùng frame.
  Nguyên nhân: make-mock-ar.py lấy sorted(listdir)[:1] = file đầu thư mục, không liên quan
  gì tới nhân vật mà builder chọn. Tên khoá "mock_ar_funny_1" còn gợi ý sai là "overlay 1".
  Sửa: script đọc data_funny.json, tra id theo TÊN nhân vật (MOCK_CHARACTER='Cristiano_Ronaldo',
  id=4 -> overlay 4.png), đổi khoá thành mock_ar_ronaldo cho hết bẫy. Sửa ở 3 file dùng nó.
  Bài học: tự động chọn "file đầu tiên" là nguồn của mâu thuẫn im lặng — phải neo vào dữ liệu
  thật (data_funny.json) thay vì thứ tự thư mục.

## VÒNG SOI THỨ 3 CỦA USER — lỗi BẤT NHẤT giữa các frame anh em
User chỉ ra chỗ trống. Phân loại: có cái lấp được, có cái KHÔNG, và có cái là lỗi bất nhất.
Ruling: 61 có mock nhưng 61b không (cùng màn, 2 state) · 60/60b Result trống ô video trong khi
  62b đã dùng mock -> lấp mock_ar_ronaldo cho 60/60b/61 cho khớp. Cost nếu sai: không.
Ruling: 4 frame quảng cáo toàn màn đang dựng 4 kiểu -> đưa về cùng hệ. NHƯNG agent face-puzzle
  BÁC LẠI và ĐÚNG: 31b có key NATIVE_FS_LEVEL tiền tố NATIVE_ nên CÓ layout thật
  (native_fake_full_inter.xml), phải dựng theo geometry thật; 41g tiền tố INTER_ là SDK vẽ,
  không có layout. Hai cái VỐN KHÁC BẢN CHẤT -> làm giống nhau mới là sai.
  Agent còn bỏ nút đóng vì layout thật có 0 nút đóng (tôi verify: đúng).
  => Bài học: "nhất quán hình thức" không được đè lên "code là chân lý".
Ruling: 11a-c Intro giữ placeholder (img_intro không tồn tại) nhưng dựng cho TRÔNG CÓ CHỦ Ý —
  viền nét đứt + chữ đọc được + in thẳng bằng chứng (id 0x7f08024{8,9,a}, public.xml không có
  entry, resources.arsc NULL) lên canvas. Lead nhìn là hiểu ngay đây là giới hạn APK.

## HAI LỖI CỦA CHÍNH CÔNG CỤ, lộ ra trong vòng này
1. audit-phase6 mục 2 báo ĐỎ ở onboard.js:147-149 vì regex bắt '0x7f…'. Nhưng đó là chuỗi
   BẰNG CHỨNG in lên canvas, không phải ref chưa resolve. Siết regex: chỉ báo khi 0x7f… được
   dùng làm GIÁ TRỊ VẼ (fill/color/stroke/image/src hoặc img()/icon()/photo()/svgNode()).
2. render-preview.py: col() trả đúng alpha NHƯNG ImageDraw.rectangle() GHI ĐÈ pixel, KHÔNG
   alpha-blend -> lớp dim 35% ở màn Result XOÁ SẠCH ảnh bên dưới, ô video thành đen đặc.
   Tôi suýt kết luận agent dựng thiếu, trong khi bản dựng ĐÚNG (có ảnh + opacity 0.35).
   Sửa: fill có alpha<255 vẽ ra lớp riêng rồi alpha_composite.
   HỆ QUẢ NGOÀI Ý MUỐN: scrim dialog trước đây hiện XÁM là do chính bug này; blend đúng thì
   D51/D62 thành đen trơn -> lộ ra chúng thiếu chrome màn nền. Đã sửa nốt.
   => Sửa một bug làm lộ bug khác — lý do phải render lại và soi sau MỖI lần vá công cụ.

## TRẠNG THÁI CUỐI
59 frame · 1431 node · v1 == v2 tuyệt đối (0 lệch toạ độ) · 0 chồng chữ
node/frame: mỏng nhất 7 · trung vị 18 (ban đầu 11) · dày nhất 155
10/10 dialog có chrome nền đúng (trừ D61/D72 là quảng cáo phủ toàn màn — không nền là ĐÚNG)
Audit Phase 6: 7/7 đạt.

## KIỂM KỸ TRƯỚC KHI NỘP (user yêu cầu)
Đối chiếu 3 tầng độc lập:
1. NAV GRAPH: 17/18 destination có frame. Thiếu duy nhất FragmentIntro — CỐ Ý loại theo
   yêu cầu design lead, đã gắn { excluded: true } + note. Audit ĐỂ BÁO ĐỎ, không sửa cho xanh.
2. LAYOUT MÀN của app: 16/20 có mặt. 4 cái thiếu đều có lý do:
   activity_main (khung chứa NavHost, không phải màn) · fragment_intro (loại theo yêu cầu) ·
   fragment_tab_home + fragment_tab_gallery (DEAD CODE, 0 hit nav graph).
3. LAYOUT item/dialog: tất cả đều được dựng BÊN TRONG danh sách/dialog tương ứng
   (item_funny_puzzle -> 20 ô ở frame 40, item_language -> 7 hàng ở 12, item_sound_layout ->
   4 hàng ở 52, item_my_video -> thumbnail ở 62b, item_time_record -> hàng 15s/30s/1m,
   popup_exit_confirm -> D51+D62, layout_loading + layout_loading_with_text -> D70+D71).
   item_pager_tepmlate_category chỉ là RecyclerView padding 10dp — khung chứa lưới mỗi tab
   Home, nội dung đã thể hiện ở 20a-20e.
   item_face_puzzle_ad / item_funny_puzzle_ad: không bao giờ chèn (showAdsInList=false) -> đúng khi vắng.

PHÁT HIỆN MỚI khi kiểm kỹ: popup_language_confirm.xml là DEAD CODE THỨ BA.
  Layout có thật ("Attention" / "Do you confirm this language ?" / Allow / Deny + adContainer)
  nhưng CHỈ xuất hiện trong R$layout.smali, không nơi nào inflate, không ai dùng
  PopupLanguageConfirmBinding. Trước đó ta chỉ biết 2 dead code (tab_home, tab_gallery).

LỖI BỘ KIỂM CỦA TÔI (lần thứ 3 trong dự án): tôi tra note qua scene.json và kết luận
  "12 layout không được nhắc" -> SAI. capture-scene.js có setPluginData(){} là hàm RỖNG nên
  scene.json KHÔNG mang note nào (0/41 frame có note). Phải tra trong MÃ NGUỒN.
  Hệ quả: audit 5 "truy vết" trước đây đo trên mã nguồn là ĐÚNG, nhưng mọi phép tra note
  qua scene.json đều vô nghĩa. Note vẫn tới Figma thật (setPluginData hoạt động ở đó).
KẾT LUẬN: KHÔNG THIẾU MÀN NÀO. 41 frame, mọi thứ vắng mặt đều có lý do ghi rõ.
