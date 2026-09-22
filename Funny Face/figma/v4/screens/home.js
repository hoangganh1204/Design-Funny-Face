// ============================================================================
// Cụm HOME — figma/v1/screens/home.js
// Nguồn số liệu: specs/home.md (đã fix round 1+2, hết cờ dữ liệu template).
// FragmentHome (UI MỚI, nhánh mặc định — ui_home_show_case=1) = 5 tab, mỗi tab 1 screen (20a-20e).
// FragmentHomeOldUI (fallback RC=0/chưa fetch RC) = 21, grid liên tục 28 ô.
// FragmentTabHome = 91, DEAD CODE (unreachable — không có trong main_nav.xml, không
//   FragmentStateAdapter/ViewPager2 nào add nó, chỉ Hilt generated DI tham chiếu).
// FragmentTabGallery KHÔNG dựng ở đây (cụm result-video dựng ở 90 theo phân công).
// Mọi top-level identifier có tiền tố home_ để tránh đụng tên khi build-plugin ghép nhiều
// file screens/*.js lại với nhau.
// ============================================================================

// ---- Data: 18 Funny Puzzle — nguồn: assets/face_funny/data_funny.json (16/20) + 2 đề xuất.
//     id 16 Messi / 17 Ronaldo / 18 Neymar Jr / 9 Bruno Mars đã BỎ khỏi bản thiết kế theo yêu cầu.
//     ⚠ THỨ TỰ HIỂN THỊ DƯỚI ĐÂY LÀ THỨ TỰ THIẾT KẾ do design lead chỉ định — KHÔNG còn
//     trùng thứ tự trong data_funny.json. Trường id vẫn giữ nguyên id gốc của APK để truy
//     ngược được. Muốn app khớp bản thiết kế, dev phải sắp lại data_funny.json theo dãy id:
//     2, 4, 3, 1, 6, 7, 5, 21, 8, 10, 15, 12, 13, 14, 11, 20, 19, 22
const home_FUNNY = [
  { image: 'Leonel_Messi',       name: 'Leonel Messi' },     // id=2
  { image: 'Cristiano_Ronaldo',  name: 'Cristiano Ronaldo' }, // id=4
  { image: 'Erling_Haaland',     name: 'Erling Haaland' },   // id=3
  { image: 'Kylian_Mbappe',      name: 'Kylian Mbappe' },    // id=1
  // id=6: ẢNH đã thay bằng Lamine Yamal theo yêu cầu, nên NHÃN phải đổi theo, nếu không
  // bảng thiết kế sẽ hiện ảnh Yamal dưới chữ 'Messi' và trông như lỗi. Lưu ý: file dữ
  // liệu của app (assets/face_funny/data_funny.json) VẪN ghi 'Messi' — muốn khớp thật
  // thì phía dev phải sửa entry id=6 trong file đó.
  { image: 'messi',              name: 'Lamine Yamal' },     // id=6
  { image: 'Vinicius_Junior',    name: 'Vinicius Junior' },  // id=7
  { image: 'Jude_Bellingham',    name: 'Jude Bellingham' },  // id=5
  { image: 'Pedri',              name: 'Pedri' },            // id=21   // THÊM MỚI, không có trong data_funny.json
  { image: 'Neymar_Junior',      name: 'Neymar Junior' },    // id=8
  { image: 'Donald_Trump',       name: 'Donald Trump' },     // id=10
  { image: 'Mr_Bean',            name: 'Mr.Bean' },          // id=15
  { image: 'Timothe_Chalamet',   name: 'Timothe Chalamet' }, // id=12
  { image: 'Taylor_Swift',       name: 'Taylor Swift' },     // id=13
  { image: 'Leonardo_Dicaprio',  name: 'Leonardo Dicaprio' }, // id=14
  { image: 'Jennie',             name: 'Jennie' },           // id=11
  { image: 'Rose',               name: 'Rose' },             // id=20
  { image: 'Naruto',             name: 'Naruto' },           // id=19
  { image: 'Sasuke',             name: 'Sasuke' },           // id=22   // THÊM MỚI, không có trong data_funny.json
];

// ---- Data: v2 endpoint (FacePuzzle/ios_data_facepuzzle_v2.json) — 3 category x 6, snapshot CDN ----
// nhãn "Nk uses" = MapperKt.round(likes/1000f,1)+"k uses" — đã tính sẵn & verify (specs/home.md mục 3.C)
const home_V2_CATS = [
  { name: 'Face Puzzle', folder: 'Face_Puzzle', id: 1,
    items: [
      { n: 1, uses: '273.3k uses' }, { n: 2, uses: '716.8k uses' }, { n: 3, uses: '22.5k uses' },
      { n: 4, uses: '18.8k uses' },  { n: 5, uses: '49.4k uses' },  { n: 6, uses: '164.4k uses' },
    ] },
  { name: 'Face Pop', folder: 'Face_Pop', id: 2,
    items: [
      { n: 1, uses: '249.1k uses' }, { n: 2, uses: '164.4k uses' }, { n: 3, uses: '39.9k uses' },
      { n: 4, uses: '5.2k uses' },   { n: 5, uses: '1.3k uses' },   { n: 6, uses: '1.0k uses' },
    ] },
  { name: 'Whirl Face', folder: 'Whirl_Face', id: 3,
    items: [
      { n: 1, uses: '273.3k uses' }, { n: 2, uses: '49.4k uses' },  { n: 3, uses: '23.9k uses' },
      { n: 4, uses: '18.8k uses' },  { n: 5, uses: '4.8k uses' },   { n: 6, uses: '1.0k uses' },
    ] },
];

// ---- Data: v1 endpoint (FacePuzzle/ios_data_facepuzzle.json) — 1 category "Face Puzzle" x 8 ----
const home_V1_ITEMS = [
  { n: 1, uses: '273.3k uses' }, { n: 2, uses: '716.8k uses' }, { n: 3, uses: '22.5k uses' },
  { n: 4, uses: '18.8k uses' },  { n: 5, uses: '49.4k uses' },  { n: 6, uses: '164.4k uses' },
  { n: 7, uses: '28.2k uses' },  { n: 8, uses: '39.9k uses' },
];

// ---- Geometry chung của lưới 2 cột (item_face_puzzle_template.xml / item_funny_puzzle.xml) ----
const home_HOT = { Leonel_Messi: 1, Cristiano_Ronaldo: 1, Neymar_Junior: 1, Leonardo_Dicaprio: 1, Naruto: 1, Sasuke: 1 };

function home_hotBadge(card, x, y) {
  const w = 52, h = 26;
  const b = frame('badge · HOT', x, y, w, h, {
    gradient: ['ff8a3d', 'ff4f81'], gradientDir: 'h', radius: h / 2,
    stroke: 'ffffff', strokeW: 2.5, shadow: 0.55,
  });
  add(card, b);
  add(b, text('HOT', 0, 0, { size: 12, weight: 900, font: 'main',
    color: '181522', w: w, h: h, align: 'CENTER', valign: 'CENTER' }));
}

const home_GRID_PAD = 10;                               // rvFacePuzzleTemplate paddingLeft/Right
const home_COL_W = (SCREEN_W - home_GRID_PAD * 2) / 2;  // 170
const home_CONTENT_W = home_COL_W - home_GRID_PAD * 2;  // 150 — vừa = face padding(10x2) vừa = funny margin(10x2)
const home_FACE_RATIO = 224 / 158;                       // app:layout_constraintDimensionRatio="158:224"
const home_FACE_H = home_CONTENT_W * home_FACE_RATIO;    // ~212.66dp
const home_FUNNY_CARD = home_CONTENT_W;                  // card vuông ~150dp (funny margin=10, padding=1, ratio 1:1)

function home_colX(col) { return home_GRID_PAD + col * home_COL_W + home_GRID_PAD; } // 20 / 190

// badge "Nk uses" — top-right trong ảnh, bg=@drawable/bg_primary_rounded_enabled nhưng
// backgroundTint="#66171716" ghi đè màu gradient xanh → pill đen mờ 40%, chữ trắng.
function home_badgeTopRight(f, boxX, boxY, boxW, label) {
  const margin = 8, padX = 12, padY = 4;
  const t = text(label, 0, 0, { size: 14, weight: 700, font: 'main', color: C.white });
  const w = t.width + padX * 2, h = t.height + padY * 2;
  const bx = boxX + boxW - margin - w, by = boxY + margin;
  add(f, rect('uses · ' + label, bx, by, w, h, { fill: 'b814101f', radius: h / 2 }));
  t.x = bx + padX; t.y = by + padY;
  add(f, t);
}

// item_face_puzzle_template.xml — ImageView imvThumbVideo (ratio 158:224, radius runtime 16dp) + badge
function home_drawFaceContent(f, x, y, key, uses) {
  const w = home_CONTENT_W, h = home_FACE_H;
  photo(f, x, y, w, h, key, 'FILL', 16);
  home_badgeTopRight(f, x, y, w, uses);
  return h;
}

// item_funny_puzzle.xml — card trắng bo 16, viền 1dp primary (dashed trong XML, vẽ solid trong Figma),
// ảnh vuông 1:1 inset 1dp, tên đè ở đáy trên nền trắng bo góc dưới (clip theo card).
function home_drawFunnyContent(f, x, y, key, name) {
  const cardW = home_FUNNY_CARD, cardH = home_FUNNY_CARD;
  const card = frame('funny · ' + name, x, y, cardW, cardH, {
    fill: C.surface, radius: R.tile, clip: true,
  });
  add(f, card);
  photo(card, 0, 0, cardW, cardH, key, 'FILL', 0);
  // Dải chuyển từ trong suốt xuống gần đặc, cao 40% thẻ: đủ để chữ trắng luôn đọc
  // được dù ảnh dưới nó sáng hay tối, mà vẫn thấy được phần thân ảnh phía sau.
  if (home_HOT[key]) home_hotBadge(card, 8, 8);
  add(card, rect('scrim tên', 0, cardH * 0.6, cardW, cardH * 0.4,
    { gradient: ['0014101f', 'ee14101f'], gradientDir: 'v' }));
  add(card, text(name, 0, cardH - 30, {
    size: 14, weight: 700, font: 'main', color: C.white, align: 'CENTER',
    w: cardW, h: 20, valign: 'CENTER',
  }));
  return cardH;
}

// Vẽ 1 lưới 2 cột liên tục từ danh sách cell phẳng đã đúng thứ tự (mỗi cell {type:'face'|'funny',...}).
// Trả về y sau cùng (đáy lưới) để đặt AD SLOT / grow() tiếp theo.
function home_drawGrid(f, startY, cells) {
  let y = startY;
  for (let i = 0; i < cells.length; i += 2) {
    const row = cells.slice(i, i + 2);
    let maxH = 0;
    row.forEach((c, col) => {
      const x = home_colX(col), cy = y + home_GRID_PAD;
      const h = c.type === 'face'
        ? home_drawFaceContent(f, x, cy, c.key, c.uses)
        : home_drawFunnyContent(f, x, cy, c.key, c.name);
      if (h > maxH) maxH = h;
    });
    y += home_GRID_PAD * 2 + maxH;
  }
  return y;
}

function home_chunk(arr, n) { const r = []; for (let i = 0; i < arr.length; i += n) r.push(arr.slice(i, i + n)); return r; }

// Trang "All" (tab 1 của FragmentHome UI mới) — replica CHÍNH XÁC SharedViewModel.mixToListHomepageUI
// (dòng 91-118): lặp cụm 2-item của [FacePuzzle, FacePop, WhirlFace, Funny] cho tới khi nguồn dài
// nhất (Funny, 20 item) cạn; 3 category face chỉ đủ cho 3 vòng đầu (6 item/2=3), 7 vòng còn lại chỉ
// còn Funny. → 18 face-item + 20 funny-item = 38 item, đã verify khớp specs/home.md mục 3.C.
function home_mixAllTabFlat() {
  const cats = home_V2_CATS.map(c => c.items.map(it => ({ type: 'face', key: c.folder + '_Video' + it.n, uses: it.uses })));
  const funny = home_FUNNY.map(f => ({ type: 'funny', key: f.image, name: f.name }));
  const out = [];
  const maxLen = Math.max(cats[0].length, cats[1].length, cats[2].length, funny.length);
  for (let i = 0; i < maxLen; i += 2) {
    for (let c = 0; c < 3; c++) out.push(...cats[c].slice(i, i + 2));
    out.push(...funny.slice(i, i + 2));
  }
  return out;
}

// Grid của 1 tab category riêng (Face Puzzle / Face Pop / Whirl Face) — 6 item, không xen ad
// (showAdsInList=false, FragmentHome.java:292/317 — đã verify độc lập bởi coordinator).
function home_categoryTabFlat(cat) {
  return cat.items.map(it => ({ type: 'face', key: cat.folder + '_Video' + it.n, uses: it.uses }));
}

// Tab "Funny Puzzle" — 20 item, không xen ad.
function home_funnyTabFlat() {
  return home_FUNNY.map(f => ({ type: 'funny', key: f.image, name: f.name }));
}

// FragmentHomeOldUI — replica CHÍNH XÁC SharedViewModel$dataHomepage$1 (dòng 56-73): chunked(2) cho
// 8 item v1, chunked(4) cho 20 funny, loop theo số chunk funny (5), face optional (chỉ 4 vòng đầu).
// → 8 face-item + 20 funny-item = 28 item, đã verify khớp specs/home.md mục 4.C.
function home_oldUIFlat() {
  const face = home_V1_ITEMS.map(it => ({ type: 'face', key: 'v1_Video' + it.n, uses: it.uses }));
  const funny = home_FUNNY.map(f => ({ type: 'funny', key: f.image, name: f.name }));
  const chunkedFace = home_chunk(face, 2);   // 4 nhóm
  const chunkedFunny = home_chunk(funny, 4); // 5 nhóm
  const out = [];
  for (let i = 0; i < chunkedFunny.length; i++) {
    if (chunkedFace[i]) out.push(...chunkedFace[i]);
    out.push(...chunkedFunny[i]);
  }
  return out;
}

// ---- Chrome chung của FragmentHome UI mới (fragment_home.xml) ----
const home_TABS = ['All', 'Face Puzzle', 'Face Pop', 'Whirl Face', 'Funny Puzzle'];

// Ước lượng bề rộng chữ (Lato Bold) KHÔNG dựa vào t.width đo runtime sau khi tạo text node —
// giá trị đó không đáng tin cậy giữa các renderer khác nhau (self-check round 2/5: mọi chip ra
// đúng 40dp bất kể nhãn dài ngắn vì t.width bị đọc sai/quá sớm). Dùng công thức cố định theo
// fontSize, rồi ép o.w khi tạo text() để cả bề rộng lẫn canh giữa đều nhất quán mọi renderer.
function home_measureTextWidth(label, fontSize) {
  const CHAR_W = fontSize * 0.58, SPACE_W = fontSize * 0.30;
  let w = 0;
  for (const ch of label) w += ch === ' ' ? SPACE_W : CHAR_W;
  return w;
}

// TabLayout templateTabLayout (style TemplateTabLayout, styles.xml:3727-3745):
// tabMinWidth=40dp (TỐI THIỂU, không phải cố định) · tabPaddingStart/End=8dp mỗi bên ·
// tabMode=scrollable (hàng tab được phép dài hơn 360dp, phần thừa cuộn ngang/bị cắt ở mép phải,
// KHÔNG co nhãn lại) · margin runtime 6dp mỗi bên mỗi tab (FragmentHome$observeHomeData$1:80-93).
function home_drawTabs(f, activeIdx, startX, y) {
  const fontSize = 12, padX = 8;
  const tabW = home_TABS.map(l => Math.max(home_measureTextWidth(l, fontSize) + padX * 2, 40));
  let naturalX = startX;
  for (let i = 0; i < activeIdx; i++) naturalX += tabW[i] + 12;
  const overflow = naturalX + tabW[activeIdx] - (SCREEN_W - 20);
  let tx = startX - Math.max(0, overflow);
  add(f, rect('fadingEdge trái', 0, y, 28, 32, 
    { gradient: [C.bg, '00' + C.bg], gradientDir: 'h' }));
  home_TABS.forEach((label, idx) => {
    const active = idx === activeIdx;
    const w = tabW[idx], h = 32;
    add(f, rect('tab · ' + label, tx, y, w, h, active
      ? { fill: C.chipSel, radius: h / 2 }
      : { fill: C.surfaceHi, radius: h / 2 }));
    const t = text(label, tx, y, {
      size: fontSize, weight: 700, font: 'main', color: active ? C.onChipSel : C.onDarkSub,
      w, h, align: 'CENTER', valign: 'CENTER',
    });
    add(f, t);
    tx += w + 12; // tabPaddingStart/End=8dp đã tính trong w + margin runtime 6dp mỗi bên = 12dp giữa 2 tab
  });
}

// header: btnSettings(x300,y12,48x48) · btnGalley(x12,y12,48x48) · imvAppName(logo, canh giữa hàng 48dp)
// · templateTabLayout(y72,32) · homeNativeContainer AD SLOT(native_home) · trả về {bg, gridStartY}.
// `bg` được resize lại đúng chiều cao thật ở cuối builder (xem home_buildTabScreen) — KHÔNG dùng
// hằng số ước lượng nữa (fix: 20a/91 nền thấp hơn nội dung thật khi số ô nhiều hơn dự tính).
function home_chrome(f, activeTabIdx) {
  const _sb = screenBg(f, SCREEN_H), bg = _sb.bg, pat = _sb.pat;
  add(f, rect('btnSettings', 300, 12, 48, 48, {}));
  const ic1 = icon('ic_setting', 308, 20, 32, 32); if (ic1) add(f, ic1);
  add(f, rect('btnGalley', 12, 12, 48, 48, {}));
  const ic2 = icon('ic_gallery_btn', 20, 20, 32, 32); if (ic2) add(f, ic2);
  // imvAppName: @mipmap/img_app_name (558x84 → ratio 6.6429), h=24dp cố định, canh giữa dọc hàng btnSettings
  const appNameW = 24 * (558 / 84);
  add(f, img('img_app_name', (SCREEN_W - appNameW) / 2, 24, appNameW, 24, 'FIT'));
  home_drawTabs(f, activeTabIdx, 20, 72);
  adSlot(f, 14, 112, 332, 100, 'native_home');
  return { bg, pat, gridStartY: SHOW_ADS ? 212 : 114 };
}

function home_footerAd(f, y) {
  adSlot(f, 0, y, SCREEN_W, 256, 'native_collapsible_home');
  return y + (SHOW_ADS ? 256 : 16);
}

function home_buildTabScreen(f, tabIdx, cells) {
  const { bg, pat, gridStartY } = home_chrome(f, tabIdx);
  const gridEndY = home_drawGrid(f, gridStartY, cells);
  const bottom = home_footerAd(f, gridEndY);
  bg.resize(SCREEN_W, bottom); pat.resize(SCREEN_W, bottom); // nền = đúng chiều cao nội dung thật, không phải hằng số ước lượng
  grow(f, bottom);
}

// ============================== 20a-20e · FragmentHome (UI MỚI, MẶC ĐỊNH) ===================
// Nguồn chung: ui/home/FragmentHome.java + res/layout/fragment_home.xml +
// TabLayoutMediator trong FragmentHome$observeHomeData$1.java (tab list) +
// AdapterTemplateCategory.java (grid, spanCount=2, showAdsInList=false → không ô ad trong lưới).
// Nhánh mặc định vì CemViewModel.isShowHomeNewUI() = (ui_home_show_case==1) = true với RC đã fetch.

screen('20a · Home · All tab', 'ui/home/FragmentHome.java + fragment_home.xml + SharedViewModel.mixToListHomepageUI dòng 91-118 (specs/home.md mục 3.C) · 38 ô = 18 face (3 category v2 x 6) + 20 funny, snapshot CDN v2 · templateTabLayout tabMode=scrollable (hàng tab cuộn ngang, chip rộng theo nhãn, tabMinWidth=40dp)', (f) => {
  home_buildTabScreen(f, 0, home_mixAllTabFlat());
});

screen('20b · Home · Face Puzzle tab', 'ui/home/AdapterTemplateCategory.java · CategoryUI id=1 folder=Face_Puzzle · FacePuzzle/ios_data_facepuzzle_v2.json snapshot CDN, 6 template (specs/home.md mục 3.C) · templateTabLayout tabMode=scrollable (hàng tab cuộn ngang, chip rộng theo nhãn, tabMinWidth=40dp)', (f) => {
  home_buildTabScreen(f, 1, home_categoryTabFlat(home_V2_CATS[0]));
});

screen('20c · Home · Face Pop tab', 'ui/home/AdapterTemplateCategory.java · CategoryUI id=2 folder=Face_Pop · FacePuzzle/ios_data_facepuzzle_v2.json snapshot CDN, 6 template (specs/home.md mục 3.C) · templateTabLayout tabMode=scrollable (hàng tab cuộn ngang, chip rộng theo nhãn, tabMinWidth=40dp)', (f) => {
  home_buildTabScreen(f, 2, home_categoryTabFlat(home_V2_CATS[1]));
});

screen('20d · Home · Whirl Face tab', 'ui/home/AdapterTemplateCategory.java · CategoryUI id=3 folder=Whirl_Face · FacePuzzle/ios_data_facepuzzle_v2.json snapshot CDN, 6 template (specs/home.md mục 3.C) · templateTabLayout tabMode=scrollable (hàng tab cuộn ngang, chip rộng theo nhãn, tabMinWidth=40dp)', (f) => {
  home_buildTabScreen(f, 3, home_categoryTabFlat(home_V2_CATS[2]));
});

screen('20e · Home · Funny Puzzle tab', 'ui/home/AdapterTemplateCategory.java · SharedViewModel.listFunnyPuzzleTemplates (local, assets/face_funny/data_funny.json, 20 item) — hardcode NGUYÊN VĂN (specs/home.md mục 3.D) · templateTabLayout tabMode=scrollable (hàng tab cuộn ngang, chip rộng theo nhãn, tabMinWidth=40dp)', (f) => {
  home_buildTabScreen(f, 4, home_funnyTabFlat());
});

// ============================== 21 · FragmentHomeOldUI (FALLBACK — KHÔNG PHẢI MẶC ĐỊNH) ========
// Nhánh chỉ xuất hiện khi CemViewModel.isShowHomeNewUI()=false, tức ui_home_show_case RC ≠ 1
// HOẶC app chưa fetch được Remote Config lần đầu (default cứng uiHomeShowCase()=0 khi thiếu key).
// Nguồn: ui/home/FragmentHomeOldUI.java + res/layout/fragment_home_old_ui.xml +
// SharedViewModel$dataHomepage$1.java (specs/home.md mục 4.C).

screen('21 · Home Old UI (fallback, RC=0 / chưa fetch RC — KHÔNG phải nhánh mặc định)', 'LOẠI theo yêu cầu design lead (cùng lý do đã bỏ 3 màn Intro): đây KHÔNG phải nhánh mặc định. FragmentSplash.java:43 — isShowHomeNewUI() ? actionSplashToHome() : actionSplashToHomeOldUI(), với CemViewModel.java:58 isShowHomeNewUI() = (uiHomeShowCase()==1) đọc RC key ui_home_show_case (lỗi fetch → 0). RC thật đã fetch của app trả ui_home_show_case=1 ⇒ người dùng thật LUÔN vào Home UI mới (20a…20e). Màn cũ này chỉ hiện khi máy không fetch được RC, hoặc nếu họ gạt cờ về sau. Lối vào thứ hai cùng điều kiện: FragmentLanguagePicker.java:95 actionLanguagePickerToHomeOldUI(). Bật lại: bỏ { excluded: true } ở cuối screen() này. | ui/home/FragmentHomeOldUI.java + fragment_home_old_ui.xml · endpoint v1 FacePuzzle/ios_data_facepuzzle.json (1 category "Face Puzzle" x 8) trộn chunked(2)/chunked(4) với 20 funny = 28 ô (specs/home.md mục 4.A/4.C)', (f) => {
  const _sb = screenBg(f, SCREEN_H), bg = _sb.bg, pat = _sb.pat;

  // imvAppName: marginTop=16, h=28dp cố định, canh giữa ngang
  const appNameW = 28 * (558 / 84);
  const appNameY = 16;
  add(f, img('img_app_name', (SCREEN_W - appNameW) / 2, appNameY, appNameW, 28, 'FIT'));
  // btnSettings: canh giữa dọc theo imvAppName (Top/Bottom = imvAppName, cả 2 đều fix height khác nhau → CL center)
  const btnY = appNameY + (28 - 48) / 2;
  add(f, rect('btnSettings', 300, btnY, 48, 48, {}));
  const icS = icon('ic_setting', 300 + 8, btnY + 8, 32, 32); if (icS) add(f, icS);

  // 2 banner quảng bá (local drawable, ratio thật 648x320=0.4938)
  const bannerY = appNameY + 28 + 16; // 60
  const bannerW = 154, bannerH = bannerW * (320 / 648);
  add(f, rect('imvBannerFacePuzzle', 20, bannerY, bannerW, bannerH, { image: 'img_banner_face_puzzle', scaleMode: 'FILL', radius: 16 }));
  add(f, rect('imvBannerFunnyPuzzle', 186, bannerY, bannerW, bannerH, { image: 'img_banner_funny_puzzle', scaleMode: 'FILL', radius: 16 }));

  // btnMyLibrary: viền nét đứt xanh (vẽ solid), bg #fff5f9ff, icon + text "My library"
  const libY = bannerY + bannerH + 16;
  const libT = text('My library', 0, 0, { size: 20, weight: 700, font: 'main', color: C.primary });
  const libPadV = 28, libH = libT.height + libPadV * 2;
  add(f, rect('btnMyLibrary', 20, libY, 320, libH, { fill: 'fff5f9ff', radius: 16, stroke: C.primary, strokeW: 2 }));
  const icL = icon('ic_layers', 20 + (320 - libT.width - 24 - 8) / 2, libY + (libH - 24) / 2, 24, 24); if (icL) add(f, icL);
  libT.x = 20 + (320 - libT.width) / 2 + 16; libT.y = libY + (libH - libT.height) / 2;
  add(f, libT);

  // rvFacePuzzleTemplate — grid 2 cột liên tục, 28 ô
  const gridStartY = libY + libH + 10;
  const gridEndY = home_drawGrid(f, gridStartY, home_oldUIFlat());
  const bottom = home_footerAd(f, gridEndY);
  bg.resize(SCREEN_W, bottom); pat.resize(SCREEN_W, bottom); // nền = đúng chiều cao nội dung thật, không phải hằng số ước lượng
  grow(f, bottom);
}, { excluded: true });

// ============================== 91 · FragmentTabHome — DEAD CODE (unreachable) =================
// ui/home/FragmentTabHome.java + res/layout/fragment_tab_home.xml. Verify: 0 hit trong
// res/navigation/main_nav.xml, không FragmentStateAdapter/ViewPager2/BottomNavigationView nào add
// nó, newInstance() companion không ai gọi ngoài chính nó — chỉ Hilt generated DI tham chiếu.
// (Coordinator đã verify độc lập, đúng — bác spec cụm khác coi nó là màn thật.)
// Vẽ đại diện phần chrome + 1 vòng dữ liệu đầu (8 ô) để chứng minh nó dùng lại đúng
// AdapterTemplateCategory/dataHomepageV2 — KHÔNG dựng đủ 38 ô vì màn này không bao giờ chạy được.
// FragmentTabGallery (cùng họ dead code) do cụm result-video dựng ở màn 90 — không dựng trùng ở đây.

screen('91 · FragmentTabHome — DEAD CODE (unreachable)', 'ui/home/FragmentTabHome.java + fragment_tab_home.xml — KHÔNG có trong main_nav.xml (18 destination), KHÔNG ViewPager2/FragmentStateAdapter nào add; newInstance() không ai gọi (specs/home.md mục 6.1) · templateTabLayout tabMode=scrollable (hàng tab cuộn ngang, chip rộng theo nhãn, tabMinWidth=40dp) · LOẠI KHỎI BẢN TRÌNH BÀY theo yêu cầu design lead. Vẫn là dead code có thật (0 hit trong main_nav.xml, chỉ Hilt generated DI tham chiếu — chính bạn đã chứng minh và bác lại spec cụm result-video) — bỏ { excluded: true } là frame quay lại.', (f) => {
  const _sb = screenBg(f, SCREEN_H), bg = _sb.bg, pat = _sb.pat;

  // imvAppName marginTop16 h28, btnSettings canh theo imvAppName — giống fragment_home_old_ui.xml
  const appNameW = 28 * (558 / 84);
  add(f, img('img_app_name', (SCREEN_W - appNameW) / 2, 16, appNameW, 28, 'FIT'));
  const btnY = 16 + (28 - 48) / 2;
  add(f, rect('btnSettings', 300, btnY, 48, 48, {}));
  const icS = icon('ic_setting', 300 + 8, btnY + 8, 32, 32); if (icS) add(f, icS);

  // templateTabLayout: Top=đáy btnSettings (btnY+48), KHÔNG marginTop (khác fragment_home.xml có 12dp)
  const tabY = btnY + 48;
  home_drawTabs(f, 0, 20, tabY);
  // KHÔNG có homeNativeContainer/nativeCollapsibleContainer trong layout này (khác FragmentHome thật)

  const gridStartY = tabY + 32;
  const cells = home_mixAllTabFlat().slice(0, 8); // 1 vòng đầu: FacePuzzle x2, FacePop x2, WhirlFace x2, Funny x2
  const gridEndY = home_drawGrid(f, gridStartY, cells);

  add(f, rect('dead-code-banner', 0, gridEndY + 20, SCREEN_W, 40, { fill: 'ffe8e8' }));
  add(f, text('DEAD CODE — unreachable: không route nào tới màn này trong app đang chạy', 12, gridEndY + 32, {
    size: 11, weight: 700, font: 'main', color: 'cc0000', w: SCREEN_W - 24,
  }));

  const bottom = gridEndY + 70;
  bg.resize(SCREEN_W, bottom); pat.resize(SCREEN_W, bottom); // nền = đúng chiều cao nội dung thật, không phải hằng số ước lượng
  grow(f, bottom);
}, { excluded: true });
