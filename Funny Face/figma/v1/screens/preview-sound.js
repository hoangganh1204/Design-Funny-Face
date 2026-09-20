// ============================================================================
//  Cụm: preview-sound — FragmentPreviewTemplate · FragmentPreviewWithMusic ·
//  FragmentSoundPicker · DialogFragmentSoundPicker
//  Nguồn số liệu: specs/preview-sound.md (đã fix round 1 — 4 cờ runtime thật còn lại)
// ============================================================================

// ---- dữ liệu hardcode: 4 bài nhạc, ĐÚNG thứ tự trong AppSetting.kt constructor ----
// (AppSetting.java:47 — arraylistOf(SoundEntity(...) x4)). duration KHÔNG hardcode,
// tính runtime bằng MediaMetadataRetriever → KHÔNG bịa số giây, để nhãn 'runtime'.
const SOUND_LIST = [
  { name: 'Greedy Sped Up', author: 'TateMcRae' },
  { name: 'Jingle Bells',   author: 'Orchestra'  },
  { name: 'Original Sound', author: 'Mariavsalo' },
  { name: 'Spring Snow',    author: '10cm'       },
];

// ---- helper dùng chung trong file này (không import, chỉ hàm JS nội bộ) ----

// khung back-button style BackImageButton2 (video preview): khung 48x48 margin12,
// padding4 → icon 40x40 tại (16,16), icon vector 36x36 fitCenter căn giữa → (18,18,36,36)
function backOnVideo(f) {
  const ic = icon('ic_back_2', 18, 18, 36, 36);
  if (ic) add(f, ic);
}
// back-button style BackImageButton1 (nền sáng, Sound Picker): khung48 padding8 margin12
// → icon 24x24 fitCenter căn giữa trong hộp32x32 → (24,24,24,24)
function backOnLight(f) {
  const ic = icon('ic_back_1', 24, 24, 24, 24);
  if (ic) add(f, ic);
}

// nút Button.Primary (bg_primary_rounded gradient #00fbff→#0080f6, radius=size_48=pill,
// chữ = @color/button_primary_text_color resolve enabled → #171716 — res/color/
// button_primary_text_color.xml + colors.xml:497)
function primaryButton(f, x, y, w, label) {
  const btn = frame('Button.Primary · ' + label, x, y, w, 48, {
    gradient: ['00fbff', '0080f6'], gradientDir: 'v', radius: 24,
  });
  add(f, btn);
  add(btn, text(label, 0, 0, {
    size: 16, weight: 700, color: C.textHi, w: w, h: 48,
    align: 'CENTER', valign: 'CENTER',
  }));
  return btn;
}

// ads_native_media_common.xml — geometry THẬT resolve từ res/layout (briefs/_fill-empty.md
// mục 1): NativeAdView fill x wrap > ConstraintLayout bg=bg_ad_native_media_common padding12dp
// { icon 48x48 · badge "AD" 8sp trắng bg=bg_text_view_ads padding 8/2/8/2 marginStart8 ·
//   primary 16sp lato_bold_700 marginStart8 · body 12sp lato_regular_400 marginTop4 ·
//   media_view fill x120dp marginTop8 · cta fill_parent text="Install" margin 4/8/4/4 }.
// Số đo wrap_content không cho sẵn (badge/primary/body/cta height) suy ra để KHỚP ĐÚNG tổng
// cao container = ad_native_collapsed_height = 256dp (12+52+8+120+8+40+4+12=256) — ghi rõ
// đây là số ƯỚC LƯỢNG, không phải resolve tĩnh. "AD"/"Install" là chuỗi THẬT trong layout.
// Nội dung quảng cáo cụ thể (icon/tiêu đề/mô tả) là runtime → placeholder trung tính,
// KHÔNG bịa tên thương hiệu.
function nativeAdCard(adFrame) {
  if (!SHOW_ADS) return; // công tắc bản gọn không quảng cáo (code.js SHOW_ADS) — adSlot() đã tự
  // trả null nên adFrame ở đây cũng null khi tắt; return sớm để khỏi add() vào null.
  // bg_ad_native_media_common — màu thật CHƯA resolve trong brief (không có hex) → thẻ nền
  // trung tính phủ lên khung adSlot() mặc định, chỉ để dựng ĐÚNG bố cục, không claim màu thật.
  add(adFrame, rect('bg_ad_native_media_common (màu chưa resolve — nền trung tính)', 0, 0, SCREEN_W, 256, { fill: C.grayF4, radius: 8 }));
  const pad = 12;
  add(adFrame, rect('icon (48x48 — nội dung ad runtime)', pad, pad, 48, 48, { fill: C.gray, radius: 8 }));
  const badgeX = pad + 48 + 8, badgeY = pad, badgeW = 26, badgeH = 14;
  add(adFrame, rect('ad badge (bg_text_view_ads)', badgeX, badgeY, badgeW, badgeH, { fill: C.textHi, radius: 3 }));
  add(adFrame, text('AD', badgeX, badgeY, { size: 8, color: C.white, w: badgeW, h: badgeH, align: 'CENTER', valign: 'CENTER' }));
  const primX = badgeX + badgeW + 8, primW = SCREEN_W - pad - primX;
  add(adFrame, text('Ad headline', primX, pad, {
    size: 16, weight: 700, font: 'main', color: C.textHi, w: primW, h: 20,
  })); // primary — ellipsize=end, marginStart=8dp từ badge
  add(adFrame, text('Ad description text', primX, pad + 20 + 4, {
    size: 12, font: 'main', color: C.textHi, w: primW, h: 28,
  })); // body — marginTop=4dp
  const mediaY = pad + 52 + 8, mediaW = SCREEN_W - pad * 2;
  add(adFrame, rect('media_view (native ad creative — runtime)', pad, mediaY, mediaW, 120, { fill: C.gray, radius: 6 }));
  const ctaY = mediaY + 120 + 8, ctaX = pad + 4, ctaW = SCREEN_W - ctaX - (pad + 4), ctaH = 40;
  add(adFrame, rect('cta (AppCompatButton, cao ước lượng)', ctaX, ctaY, ctaW, ctaH, { fill: C.primary, radius: 6 }));
  add(adFrame, text('Install', ctaX, ctaY, { size: 14, weight: 700, color: C.white, w: ctaW, h: ctaH, align: 'CENTER', valign: 'CENTER' }));
}

// nativeCollapsibleContainer (fill x 256dp, đáy màn) — placeholder trắng collapseHolderNative
// hiện 2000ms đầu (FragmentPreviewTemplate$initUi$1 / FragmentPreviewWithMusic$initUi$1,
// delay(2000L) rồi gone()). Container này được add SAU btnTryNow/btnNext trong XML → khi
// hiện, nó VẼ ĐÈ LÊN nút CTA cùng vị trí (cùng constraint bottom→top(bottomSpace)) → không
// vẽ nút CTA ở state này (bị che bởi z-order XML, không phải suy đoán).
function collapsibleAdBottom(f) {
  const adFrame = adSlot(f, 0, SCREEN_H - 256, SCREEN_W, 256, 'native_collapsible_preview');
  nativeAdCard(adFrame);
}

// khung video preview — CHƯA có asset video thật trong APK/CDN cho urlVideoTemplate/
// pathVideoPreview (đều là runtime: URL template hoặc file user vừa quay). Dùng ảnh MÔ PHỎNG
// mock_ar_ronaldo (assets/v1/50-mock-ar/ — nhân vật thật trong APK + nét mặt tổng hợp, theo
// briefs/_fill-empty.md mục 4), KHÔNG lấy thumbnail CDN (30-template-v2/31-template-v1) vì đó
// là nội dung của người khác. dim=true mô phỏng trạng thái đang buffer (chưa phát rõ).
// (2024 cleanup theo yêu cầu design lead — canvas SẠCH: bỏ nhãn "MÔ PHỎNG · …" từng in
// trên canvas. Thông tin KHÔNG mất — mỗi screen()/dialog() gọi hàm này đã nối đủ chi tiết
// vào note (tham số 2 của screen()/dialog(), đọc trong Figma qua pluginData['source']).
function videoPreviewBg(f, label, dim, mock) {
  add(f, rect('video bg', 0, 0, SCREEN_W, SCREEN_H, { fill: '1f1f1f' })); // fallback nếu thiếu asset
  // mock_ar_ronaldo giờ là khung dọc 540x1200 (đúng tỉ lệ 360x800, camera/video phủ TRỌN
  // khung — nhân vật chỉ ~55% bề ngang, không còn vuông) → FILL full-bleed khớp geometry thật
  // của exoPlayerView (fragment_preview_template.xml/fragment_preview_with_music.xml: 4 cạnh
  // constraint = parent, không có toolbar/khung cắt bớt), không méo vì đã đúng tỉ lệ khung hình.
  add(f, img(mock || 'mock_ar_ronaldo', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));
  if (dim) add(f, rect('buffering dim overlay (mô phỏng chưa phát rõ)', 0, 0, SCREEN_W, SCREEN_H, { fill: '000000', opacity: 0.55 }));
}

// ProgressBar hệ thống (spinner tròn) — vẽ như vòng tròn viền, không có src cụ thể
function spinner(f, cx, cy) {
  add(f, ellipse('ProgressBar (loading)', cx - 16, cy - 16, 32, 32, { stroke: C.white, strokeW: 3 }));
}

// 1 dòng item_sound_layout.xml — root wrap_content, padding dọc 2dp, margin dọc 8dp
// → itemH ước lượng 44dp (checkbox24 + tvNameSong + tvActor/tvTime chồng dọc)
function soundItem(f, y, entry, selected) {
  const itemH = 44;
  add(f, icon(selected ? 'ic_check_box_selected' : 'ic_check_box_unselected', 16, y + (itemH - 24) / 2, 24, 24));
  add(f, text(entry.name, 56, y, {
    size: 14, weight: 700, font: 'main', color: C.textHi, w: 220, h: 17,
  }));
  // w thu hẹp còn 56 (thay vì 90) để hộp KHÔNG tràn qua dot/tvTime — dot ở x=118, author bắt
  // đầu x=56 → khoảng trống thật = 62dp, chừa padding 6dp trước dot (118-56-56=6). 90 cũ khiến
  // hộp author (56..146) đè lên hộp tvTime (126..186) 20x15dp ở mọi item — chữ vẫn đọc được vì
  // tên ngắn nhưng 2 layer chồng nhau trong Figma.
  add(f, text(entry.author, 56, y + 21, {
    size: 12, color: C.textHi, w: 56, h: 15,
  }));
  // dot_black_size_2 — chấm tròn đen 4x4dp phân cách tác giả/thời lượng
  add(f, ellipse('dot_black_size_2', 56 + 62, y + 21 + 6, 4, 4, { fill: C.textHi }));
  add(f, text('--:--', 56 + 70, y + 21, {
    size: 12, color: C.textSub, w: 60, h: 15,
  })); // tvTime — duration tính bằng MediaMetadataRetriever lúc chạy, KHÔNG hardcode số giây.
  // '--:--' = quy ước thời lượng chưa biết (không phải thuật ngữ kỹ thuật) — lý do đầy đủ
  // nằm trong note của screen()/dialog() gọi buildSoundPickerContent (52/52b/D53).
  const playIc = selected ? 'ic_pause_music' : 'ic_play_music';
  add(f, icon(playIc, SCREEN_W - 32 - 16, y + (itemH - 24) / 2, 24, 24));
}

// toàn bộ nội dung fragment_sound_picker.xml (dùng chung cho FragmentSoundPicker VÀ
// DialogFragmentSoundPicker — 2 class cùng binding FragmentSoundPickerBinding).
// selectedIndex = -1 → chưa chọn gì (positionSelected mặc định -1 trong AdapterSounds).
function buildSoundPickerContent(f, selectedIndex) {
  add(f, img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));
  backOnLight(f);
  add(f, text('Sound', 0, 12, {
    size: 20, weight: 700, color: C.textHi, w: SCREEN_W, h: 48,
    align: 'CENTER', valign: 'CENTER',
  })); // style ScreenTitleCommon
  // rcvMusic: margin ngang 16dp, top=dưới btnBack(60), bottom=trên btnDone (adNativeView
  // KHÔNG vẽ — xem ghi chú cuối file — nên trong thực tế FrameLayout rỗng co về 0dp,
  // rcvMusic kéo gần sát btnDone)
  const listX = 16, listTop = 60;
  SOUND_LIST.forEach((entry, i) => {
    soundItem(f, listTop + i * 60, entry, i === selectedIndex);
  });
  primaryButton(f, 24, SCREEN_H - 24 - 48, SCREEN_W - 48, 'Done');
}

// ============================== SCREENS (page Screens) =====================

// ---- 25 · FragmentPreviewTemplate — 2 state ----
// Danh so 25 (KHONG phai 50) de dung vi tri trong luong: Home(20) -> tap template Face Puzzle
// -> man Try Now nay -> man quay Face Puzzle(30). Truoc day danh 50 nen tren canvas no roi
// xuong tan sau cum Funny Puzzle, doc nguoc hoan toan voi thu tu nguoi dung thuc su di qua.
// 51x (Preview With Music) VAN o 50s vi no dien ra SAU khi quay xong.
screen('25 · Preview Template (Face Puzzle) · Loading (buffer)',
  'LUỒNG: đây là màn "Try Now" của nhánh FACE PUZZLE, không phải Funny Puzzle. Vào: FragmentHome$observeHomeData$pagerAdapter$1$onFacePuzzleTemplateClick$1.java:67 → actionHomeToPreviewTemplate(item.url) (tab Funny Puzzle đi đường KHÁC: onFunnyPuzzleTemplateClick → actionHomeToFunnyPuzzle/actionToLevelPicker → màn 28/41x). Ra: FragmentPreviewTemplate.levelPicker() dòng 80-84 — RC ConfigKey.LEVEL_PICKER_SKIPPED ? actionPreviewToFacePuzzle(2) : actionToLevelPicker(). Cờ mặc định FALSE ⇒ luồng THẬT là Try Now → Level Picker (màn 28) → màn quay (30/30a). Vì vậy 28 đánh số TRƯỚC 30, không phải 31 như bản trước. | fragment_preview_template.xml + FragmentPreviewTemplate.java:158-198,initUi$1 (delay 2000ms) — video=urlVideoTemplate runtime placeholder | HIỂN THỊ: khung preview là ảnh MÔ PHỎNG hiệu ứng FACE PUZZLE (assets/v1/50-mock-ar/mock_ar_facepuzzle — mặt tổng hợp cắt 6 vùng rồi dịch/xoay theo drawFacePuzzleComponent, script/make-mock-ar.py). TRƯỚC ĐÂY dùng nhầm mock_ar_ronaldo (nhân vật của nhánh Funny Puzzle) — sai luồng, đã sửa. KHÔNG phải ảnh chụp app thật: nội dung thật là video mẫu tải từ urlVideoTemplate (nav arg), chỉ có lúc chạy; cũng KHÔNG dùng thumbnail CDN vì đó là nội dung của người khác. | AD SLOT native_collapsible_preview: placeholder trắng collapseHolderNative hiện 2000ms đầu rồi ẩn/nhường chỗ ad thật; container add SAU nút CTA trong XML nên khi hiện sẽ che nút — nội dung ad (headline/mô tả/icon) là placeholder trung tính, không phải quảng cáo thật.',
  (f) => {
    videoPreviewBg(f, 'video mẫu — urlVideoTemplate (runtime, đang buffer)', true, 'mock_ar_facepuzzle');
    spinner(f, SCREEN_W / 2, SCREEN_H / 2); // Player.Listener STATE_BUFFERING → progress visible
    backOnVideo(f);
    // btnTryNow KHÔNG có toggle visibility runtime (luôn VISIBLE theo XML) — trước đây bị bỏ
    // vẽ ở state này vì ad che; giờ vẽ luôn, để collapsibleAdBottom (nếu SHOW_ADS=true) đè lên
    // sau cùng đúng z-order XML thật. Khi SHOW_ADS=false, ad là no-op → nút hiện bình thường,
    // đây là điểm còn khác 50b (dim overlay + spinner buffer) nên GIỮ CẢ HAI khi tắt ad.
    primaryButton(f, 16, SCREEN_H - 16 - 48, SCREEN_W - 32, 'Try Now');
    collapsibleAdBottom(f); // che nút Try Now cùng vị trí khi SHOW_ADS=true (xem note collapsibleAdBottom)
  });

screen('25b · Preview Template (Face Puzzle) · Ready — nút Try Now',
  'LUỒNG: đây là màn "Try Now" của nhánh FACE PUZZLE, không phải Funny Puzzle. Vào: FragmentHome$observeHomeData$pagerAdapter$1$onFacePuzzleTemplateClick$1.java:67 → actionHomeToPreviewTemplate(item.url) (tab Funny Puzzle đi đường KHÁC: onFunnyPuzzleTemplateClick → actionHomeToFunnyPuzzle/actionToLevelPicker → màn 28/41x). Ra: FragmentPreviewTemplate.levelPicker() dòng 80-84 — RC ConfigKey.LEVEL_PICKER_SKIPPED ? actionPreviewToFacePuzzle(2) : actionToLevelPicker(). Cờ mặc định FALSE ⇒ luồng THẬT là Try Now → Level Picker (màn 28) → màn quay (30/30a). Vì vậy 28 đánh số TRƯỚC 30, không phải 31 như bản trước. | fragment_preview_template.xml + FragmentPreviewTemplate.java:179-198 (STATE_READY→progress gone, setPlayWhenReady) — sau 2000ms collapseHolderNative đã gone() | HIỂN THỊ: khung preview là ảnh MÔ PHỎNG hiệu ứng FACE PUZZLE (assets/v1/50-mock-ar/mock_ar_facepuzzle — mặt tổng hợp cắt 6 vùng rồi dịch/xoay theo drawFacePuzzleComponent, script/make-mock-ar.py). TRƯỚC ĐÂY dùng nhầm mock_ar_ronaldo (nhân vật của nhánh Funny Puzzle) — sai luồng, đã sửa. KHÔNG phải ảnh chụp app thật: nội dung thật là video mẫu tải từ urlVideoTemplate (nav arg), chỉ có lúc chạy; cũng KHÔNG dùng thumbnail CDN vì đó là nội dung của người khác.',
  (f) => {
    videoPreviewBg(f, 'video mẫu — urlVideoTemplate (runtime, đang phát loop)', false, 'mock_ar_facepuzzle');
    backOnVideo(f);
    primaryButton(f, 16, SCREEN_H - 16 - 48, SCREEN_W - 32, 'Try Now');
  });

// ---- 51 · FragmentPreviewWithMusic — 4 state (gồm loading mux) ----
// 51 chỉ khác 51b ở chỗ CÓ ad che nút Next (xem note collapsibleAdBottom) — khi SHOW_ADS=false
// ad không vẽ, 51 trở thành hệt 51b (video+back+pill chưa chọn nhạc, không nút) NHƯNG 51b đã
// vẽ sẵn nút Next → trùng lặp thật sự. Giữ 51b (có nút CTA), gắn adDup cho 51.
screen('51 · Preview With Music · Vừa vào (ad placeholder, chưa chọn nhạc)',
  'fragment_preview_with_music.xml + FragmentPreviewWithMusic.java:396-432,initUi$1 (delay 2000ms) — video=pathVideoPreview runtime, sound=null (SharedViewModel.randomSound đang chọn hoặc soundPreview null) | HIỂN THỊ: khung preview là ảnh MÔ PHỎNG (assets/v1/50-mock-ar/mock_ar_ronaldo — nhân vật thật trong APK + nét mặt tổng hợp, script/make-mock-ar.py), KHÔNG phải ảnh chụp app thật — nội dung thật là video kết quả từ pathVideoPreview (do user vừa quay), chỉ có lúc chạy. | AD SLOT native_collapsible_preview: placeholder trắng collapseHolderNative hiện 2000ms đầu rồi ẩn/nhường chỗ ad thật; container add SAU nút CTA trong XML nên khi hiện sẽ che nút — nội dung ad (headline/mô tả/icon) là placeholder trung tính, không phải quảng cáo thật.',
  (f) => {
    videoPreviewBg(f, 'video kết quả — pathVideoPreview (runtime, do user tạo)', false);
    backOnVideo(f);
    musicPill(f, false);
    collapsibleAdBottom(f); // che nút Next cùng vị trí
  },
  { adDup: true });

screen('51b · Preview With Music · Chưa chọn nhạc',
  'ĐIỂM HỢP LƯU: màn này nhận video từ CẢ HAI luồng quay — FragmentFacePuzzle$onStopRecording$1.java:78 actionToPreviewWithMusic(fileSave, sound) và FragmentFunnyPuzzle$onStopRecording$1.java actionFunnyPuzzleToPreviewWithMusic. Dựng MỘT lần, không nhân đôi theo luồng (đúng như app). Vì vậy trên canvas hàng Face Puzzle (30x) và hàng Funny Puzzle (41x) đều kết thúc ở "đang quay" rồi cùng chảy xuống hàng 51b→54. | fragment_preview_with_music.xml + FragmentPreviewWithMusic.java:398-432,initUi$5 — soundUI=null → tvNameSong="Add song" (@string/add_sound), vVertical/btnRemoveSound gone | HIỂN THỊ: khung preview là ảnh MÔ PHỎNG (assets/v1/50-mock-ar/mock_ar_ronaldo — nhân vật thật trong APK + nét mặt tổng hợp, script/make-mock-ar.py), KHÔNG phải ảnh chụp app thật — nội dung thật là video kết quả từ pathVideoPreview (do user vừa quay), chỉ có lúc chạy.',
  (f) => {
    videoPreviewBg(f, 'video kết quả — pathVideoPreview (runtime, do user tạo)', false);
    backOnVideo(f);
    musicPill(f, false);
    primaryButton(f, 16, SCREEN_H - 16 - 48, SCREEN_W - 32, 'Next');
  });

screen('53 · Preview With Music · Đã chọn nhạc',
  'SỐ THỨ TỰ: đánh 53 (không phải 51c) vì luồng QUAY LẠI — FragmentPreviewWithMusic.java:240 btnAddMusic → actionPreviewWithMusicToSoundPicker → fragmentSoundPicker (main_nav.xml:25, MÀN RIÊNG, khác dialogFragmentSoundPicker=D53 mà màn quay dùng). Trình tự thật: 51b (chưa nhạc) → 52/52b (Sound Picker) → màn này → 54 (render). Gộp 51b/51c/51d liền nhau như bản trước khiến Sound Picker bị đẩy xuống sau, đọc sai luồng. | fragment_preview_with_music.xml + FragmentPreviewWithMusic.java:428-432,initUi$5 — soundUI!=null → btnRemoveSound/vVertical visible, tvNameSong=soundUI.nameSound | HIỂN THỊ: khung preview là ảnh MÔ PHỎNG (assets/v1/50-mock-ar/mock_ar_ronaldo — nhân vật thật trong APK + nét mặt tổng hợp, script/make-mock-ar.py), KHÔNG phải ảnh chụp app thật — nội dung thật là video kết quả từ pathVideoPreview (do user vừa quay), chỉ có lúc chạy.',
  (f) => {
    videoPreviewBg(f, 'video kết quả — pathVideoPreview (runtime, do user tạo)', false);
    backOnVideo(f);
    musicPill(f, true, SOUND_LIST[0].name);
    primaryButton(f, 16, SCREEN_H - 16 - 48, SCREEN_W - 32, 'Next');
  });

screen('54 · Preview With Music · Đang render (loading mux)',
  'SỐ THỨ TỰ: đánh 54 (không phải 51d) — xem lý do ở màn 53. | fragment_preview_with_music.xml <include layout_loading.xml> + FragmentPreviewWithMusic.java:388-393,388(btnNext.setEnabled(false))+genFile()/addMusicToVideo-BWLJW6A (MediaMuxer) — CỜ: thời điểm show/gone viewLoading không decompile được tường minh (initListener$1$5$1 JADX dump lỗi), dựng theo luồng suy luận | HIỂN THỊ: khung preview là ảnh MÔ PHỎNG (assets/v1/50-mock-ar/mock_ar_ronaldo — nhân vật thật trong APK + nét mặt tổng hợp, script/make-mock-ar.py), KHÔNG phải ảnh chụp app thật — nội dung thật là video kết quả từ pathVideoPreview (do user vừa quay), chỉ có lúc chạy.',
  (f) => {
    videoPreviewBg(f, 'video kết quả — pathVideoPreview (runtime, do user tạo)', false);
    backOnVideo(f);
    musicPill(f, true, SOUND_LIST[0].name);
    primaryButton(f, 16, SCREEN_H - 16 - 48, SCREEN_W - 32, 'Next');
    // layout_loading.xml: FrameLayout #40000000 fill + ProgressBar giữa màn — vẽ SAU cùng (đè lên)
    add(f, frame('viewLoading (#40000000)', 0, 0, SCREEN_W, SCREEN_H, { fill: '40000000' }));
    spinner(f, SCREEN_W / 2, SCREEN_H / 2);
  });

// btnAddMusic pill — ConstraintLayout con, bg_black_40_rounded, wrap x32dp maxWidth180dp,
// căn giữa ngang, cùng hàng với btnBack (y=20,h=32)
function musicPill(f, hasSound, songName) {
  const w = hasSound ? 170 : 120;
  const x = (SCREEN_W - w) / 2, y = 20, h = 32;
  const pill = frame('btnAddMusic', x, y, w, h, { fill: '66171716', radius: 40 });
  add(f, pill);
  const ic = icon('ic_music', 8, (h - 18) / 2, 18, 18);
  if (ic) add(pill, ic);
  if (hasSound) {
    add(pill, text(songName, 30, 0, {
      size: 14, color: C.white, w: w - 30 - 8 - 1 - 8 - 16 - 4, h: h,
      valign: 'CENTER',
    }));
    add(pill, rect('vVertical', w - 8 - 16 - 4 - 1, 4, 1, h - 8, { fill: C.white })); // toạ độ tương đối trong pill (marginVertical 4dp)
    const closeIc = icon('ic_close', w - 8 - 16, (h - 16) / 2, 16, 16);
    if (closeIc) add(pill, closeIc);
  } else {
    add(pill, text('Add song', 30, 0, {
      size: 14, color: C.white, w: w - 30 - 8, h: h, valign: 'CENTER',
    })); // fallback @string/add_sound khi soundUI == null
  }
}

// ---- 52 · FragmentSoundPicker (full-screen, nav destination) — 2 state ----
screen('52 · Sound Picker · Mặc định (chưa chọn)',
  'fragment_sound_picker.xml + FragmentSoundPicker.java + AdapterSounds.java:30 (positionSelected=-1 mặc định) — 4 bài từ AppSetting.java:47 | THỜI LƯỢNG (tvTime): hiện “--:--” — MapperKt.toSoundUI() tính duration bằng MediaMetadataRetriever lúc chạy (đọc từ file .aac thật), không hardcode số giây tĩnh được nên không thể in số thật ở đây; “--:--” là quy ước placeholder cho giá trị chưa biết.',
  (f) => { buildSoundPickerContent(f, -1); });

screen('52b · Sound Picker · Đã chọn 1 bài',
  'fragment_sound_picker.xml + AdapterSounds.java:34-44,60-77 (onBindData: checkbox.setSelected + ic_check_box_selected/ic_pause_music khi position==positionSelected) | THỜI LƯỢNG (tvTime): hiện “--:--” — MapperKt.toSoundUI() tính duration bằng MediaMetadataRetriever lúc chạy (đọc từ file .aac thật), không hardcode số giây tĩnh được nên không thể in số thật ở đây; “--:--” là quy ước placeholder cho giá trị chưa biết.',
  (f) => { buildSoundPickerContent(f, 0); });

// ============================== DIALOGS (page Dialogs & States) ============

// ---- D53 · DialogFragmentSoundPicker — full-screen DialogFragment, KHÔNG scrim ----
// getTheme()=R.style.FullScreenDialog (styles.xml:3185-3193): windowIsFloating=false,
// backgroundDimEnabled=false → KHÔNG dcard()/scrim, dựng y hệt FragmentSoundPicker (cùng
// binding FragmentSoundPickerBinding, cùng AdapterSounds). Gọi từ FragmentFacePuzzle/
// FragmentFunnyPuzzle (2 màn NGOÀI cụm preview-sound) qua main_nav.xml dialogFragmentSoundPicker.
dialog('D53 · Dialog Sound Picker (full-screen, không scrim)',
  'main_nav.xml:20,68 dialogFragmentSoundPicker + BaseDialogFragment.java:100-103 getTheme=FullScreenDialog(backgroundDimEnabled=false) + DialogFragmentSoundPicker.java — cùng layout/adapter với FragmentSoundPicker | THỜI LƯỢNG (tvTime): hiện “--:--” — MapperKt.toSoundUI() tính duration bằng MediaMetadataRetriever lúc chạy (đọc từ file .aac thật), không hardcode số giây tĩnh được nên không thể in số thật ở đây; “--:--” là quy ước placeholder cho giá trị chưa biết.',
  (f) => { buildSoundPickerContent(f, -1); });

// ---- D51 · popup_exit_confirm "Go back?" (FragmentPreviewWithMusic only) ----
// AlertDialog (KHÔNG bottom-sheet), width=85% màn hình, dim mặc định AlertDialog (KHÔNG
// override) → dùng dcard(). Layout popup_exit_confirm.xml text mặc định (KHÔNG override text
// như showPopupConfirmDelete của cụm result-video — biến thể "Delete video?" thuộc cụm đó,
// KHÔNG dựng lại ở đây).
dialog('D51 · Preview With Music · Xác nhận thoát (Go back?)',
  'popup_exit_confirm.xml + PopupUtilsKt.java:98-140 (showPopupExit, width=85%*screenWidth) + FragmentPreviewWithMusic.java:214-231 (handleCloseScreen, gọi khi btnBack/OnBackPressedCallback) | HIỂN THỊ: khung preview là ảnh MÔ PHỎNG (assets/v1/50-mock-ar/mock_ar_ronaldo — nhân vật thật trong APK + nét mặt tổng hợp, script/make-mock-ar.py), KHÔNG phải ảnh chụp app thật — nội dung thật là video kết quả từ pathVideoPreview (do user vừa quay), chỉ có lúc chạy.',
  (f) => {
    // Chrome màn nền phía sau — dialog này luôn nổi TRÊN chính FragmentPreviewWithMusic
    // (handleCloseScreen gọi từ btnBack/OnBackPressedCallback của màn đó), tái dùng đúng số
    // liệu đã dựng ở 51b/53 (videoPreviewBg/backOnVideo/musicPill/primaryButton) thay vì
    // để nền đen trơn. Chọn cấu hình "đã chọn nhạc" (màn 53) — trạng thái điển hình trước khi bấm back.
    videoPreviewBg(f, 'video kết quả — pathVideoPreview (runtime, do user tạo)', false);
    backOnVideo(f);
    musicPill(f, true, SOUND_LIST[0].name);
    primaryButton(f, 16, SCREEN_H - 16 - 48, SCREEN_W - 32, 'Next');

    const w = 306, h = 158, x = (SCREEN_W - w) / 2, y = (SCREEN_H - h) / 2;
    const card = dcard(f, w, h, { y, radius: 12, fill: C.white, name: 'popup_exit_confirm' });
    add(card, text('Go back ?', 0, 16, {
      size: 20, weight: 700, color: C.textHi, w: w, align: 'CENTER',
    })); // tvHeader — @string/go_back, style ScreenTitleCommon
    add(card, text('Your video will not be save if you go back', 16, 48, {
      size: 14, color: C.textHi, w: w - 32, align: 'CENTER',
    })); // tvContent — @string/your_video_will_not_be_save_if_you_go_back
    const btnW = (w - 32 - 16) / 2;
    add(card, frame('btnCancel', 16, 98, btnW, 44, { fill: 'e6e6e5', radius: 69 }));
    add(card, text('No', 16, 98, { size: 14, weight: 700, color: C.textHi, w: btnW, h: 44, align: 'CENTER', valign: 'CENTER' }));
    add(card, frame('btnDelete', 16 + btnW + 16, 98, btnW, 44, { fill: 'ff4342', radius: 69 }));
    add(card, text('Yes', 16 + btnW + 16, 98, { size: 14, weight: 700, color: C.white, w: btnW, h: 44, align: 'CENTER', valign: 'CENTER' }));
  });
