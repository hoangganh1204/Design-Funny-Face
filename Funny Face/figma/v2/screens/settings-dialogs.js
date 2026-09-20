// ============================================================================
// Cụm: settings-dialogs — nguồn: specs/settings-dialogs.md
// Screens: FragmentSettings, CompanyInfoFragment (2 biến thể)
// Dialogs: loading overlay (layout_loading.xml), loading card (layout_loading_with_text.xml),
//          native full-screen ad (dialog_native_full_screen.xml),
//          native "fake app-open" ad (activity_native_show_open_fake.xml)
// KHÔNG dựng: custom_dialog.xml/loading_alert.xml (Pangle/MBridge SDK, không phải app),
//             popup_exit_confirm (dựng bởi cụm result-video / preview-sound),
//             dot_layout/fragment_intro (dựng bởi cụm onboard).
// ============================================================================

// ---- Nội dung THẬT của privacy_policy.html / term_of_use.html — trích từ
// build/policy-text.json (CompanyInfoFragment.java:119,122 loadUrl 2 file này).
// Lấy 16 đoạn đầu mỗi file (nằm trong khoảng 12-18 đoạn theo brief _fill-empty.md#2).
// Đoạn 0/1 của privacy_policy.html đều là "Privacy Policy" (tiêu đề lặp 2 lần — có thật
// trong file, giữ nguyên). Đoạn 0 của term_of_use.html CŨNG là "Privacy Policy" — đây là
// lỗi có thật của chính app (nhầm tiêu đề), đoạn 1 mới là "Terms of Use" thật — giữ nguyên,
// không sửa, ghi chú trong note của screen 72.
const PRIVACY_PARAS = [
  'Privacy Policy',
  'Privacy Policy',
  'This SERVICE is provided by CEM Software. at no cost and is intended for use as is.',
  'This page is used to inform visitors regarding our policies with the collection, use, and',
  'disclosure of Personal Information if anyone decided to use our Service.',
  'If you choose to use our Service, then you agree to the collection and use of information in',
  'relation to this policy. The Personal Information that we collect is used for providing and',
  'improving the Service. We will not use or share your information with anyone except as',
  'described in this Privacy Policy.',
  'The terms used in this Privacy Policy have the same meanings as in our Terms and Conditions,',
  'which is accessible at Contacts Backup unless otherwise defined in this Privacy Policy.',
  'Information Collection and Use',
  'For a better experience, while using our',
  'Service, we may require you to provide us with',
  'certain personally identifiable information. The information that we request will be',
  'retained by us and used as described in this privacy policy.',
];
const TERM_PARAS = [
  'Privacy Policy',
  'Terms of Use',
  'If you continue to use this application , you are agreeing to comply with and be bound by',
  'the following terms and conditions of use, which together with our privacy policy govern',
  'app relationship with you in relation to this application. If you disagree with any part',
  'of these terms and conditions, please do not use our application.',
  'This is a security service and we do not guarantee to give you %100 security. It was',
  'designed to protect your conversations and having them backed up on encrypted cloud',
  'platform. You accept that we do not guarantee to give you exact results by downloading',
  'and upgrading your membership. Keep in mind that this app does not add a passcode to the',
  'original applications, only the imported conversations of your choice.',
  'Links To Other Web Sites',
  'We have no control over, and assumes no responsibility for, the content, privacy',
  'policies, or practices of any third party web sites or services. You further acknowledge',
  'and agree that CEM Software. shall not be responsible or liable, directly or indirectly,',
  'for any damage or loss caused or alleged to be caused by or in connection with use of or',
];

// ---------------------------------------------------------------------------
// 70 · Settings — res/layout/fragment_settings.xml · ui/settings/FragmentSettings.java
// ---------------------------------------------------------------------------
screen('70 · Settings', 'res/layout/fragment_settings.xml + ui/settings/FragmentSettings.java — 1 state duy nhất, không PRO/EU branching (verify: initListener() chỉ gắn 5 click listener, không có initUi()/show()/gone() nào)', (f) => {
  // windowBackground = @mipmap/window_bg (theme, fragment root không tự set background)
  const bg = img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL');
  bg.name = 'windowBackground · window_bg';
  add(f, bg);

  // btnBack — style BackImageButton1: padding 8dp, layout_margin 12dp, src ic_back_1, 24x24 icon
  const backIc = icon('ic_back_1', 20, 20, 24, 24);
  if (backIc) add(f, backIc);

  // appCompatTextView3 — style ScreenTitleCommon, constraint top/bottom = btnBack (12..52)
  add(f, text('Settings', 0, 12, { size: 20, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, h: 40, align: 'CENTER', valign: 'CENTER' }));

  // 4 hàng setting — style SettingItemText: bg_item_setting (trắng, bo 16, viền 1dp — XML là viền
  // NÉT ĐỨT dashWidth8/dashGap6, helper frame() không hỗ trợ dash nên vẽ viền liền màu đúng, gần đúng nhất có thể),
  // padding 20, marginTop 16 (trừ hàng đầu marginTop từ btnBack.bottom=52), marginStart/End 20,
  // drawablePadding 8, fontFamily lato_bold_700 cho CẢ 4 hàng. Chỉ btnLanguage override textSize=20sp,
  // 3 hàng còn lại dùng size mặc định theme = 14sp (không có android:textSize riêng trong XML).
  const rows = [
    { icon: 'ic_setting_language', label: 'Language', size: 20 },
    { icon: 'ic_setting_policy', label: 'Privacy Policy', size: 14 },
    { icon: 'ic_setting_term', label: 'Term of use', size: 14 },
    { icon: 'ic_setting_share', label: 'Share', size: 14 },
  ];
  let top = 68; // 52 (btnBack.bottom) + 16 (marginTop hàng đầu)
  const ROW_H = 64; // padding20*2 + icon/text 24 (wrap_content, icon 24dp dominant)
  rows.forEach((r) => {
    const row = frame('Row · ' + r.label, 20, top, 320, ROW_H, { fill: C.white, radius: R.tile, stroke: C.textHi, strokeW: 1, clip: true });
    add(f, row);
    const ic = icon(r.icon, 20, (ROW_H - 24) / 2, 24, 24);
    if (ic) add(row, ic);
    add(row, text(r.label, 52, 0, { size: r.size, weight: 700, font: 'main', color: C.textHi, w: 320 - 52 - 20, h: ROW_H, valign: 'CENTER', align: 'LEFT' }));
    top += ROW_H + 16;
  });
});

// ---------------------------------------------------------------------------
// 71 · CompanyInfo · Privacy Policy — res/layout/fragment_company_info.xml
// ui/settings/CompanyInfoFragment.java — Type.PRIVACY_POLICY
// ---------------------------------------------------------------------------
screen('71 · CompanyInfo · Privacy Policy', 'res/layout/fragment_company_info.xml + CompanyInfoFragment.initUi() — Type.PRIVACY_POLICY → loadUrl file:///android_asset/privacy_policy.html. Nội dung 16 đoạn đầu trích THẬT từ build/policy-text.json (đoạn 0+1 đều "Privacy Policy" — có thật trong file, không phải lỗi dựng hình).', (f) => {
  add(f, img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));
  buildCompanyInfoToolbarAndBody(f, 'Privacy Policy', 'privacy_policy.html', PRIVACY_PARAS);
});

// ---------------------------------------------------------------------------
// 72 · CompanyInfo · Term of use — res/layout/fragment_company_info.xml
// ui/settings/CompanyInfoFragment.java — Type.TERM_OF_USE
// ---------------------------------------------------------------------------
screen('72 · CompanyInfo · Term of use', 'res/layout/fragment_company_info.xml + CompanyInfoFragment.initUi() — Type.TERM_OF_USE → loadUrl file:///android_asset/term_of_use.html. Nội dung 16 đoạn đầu trích THẬT từ build/policy-text.json — ĐOẠN ĐẦU TIÊN "Privacy Policy" là LỖI CÓ THẬT của term_of_use.html (tiêu đề sai), đoạn 2 "Terms of Use" mới đúng — giữ nguyên như app thật, không sửa.', (f) => {
  add(f, img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));
  buildCompanyInfoToolbarAndBody(f, 'Term of use', 'term_of_use.html', TERM_PARAS);
});

function buildCompanyInfoToolbarAndBody(f, title, htmlFile, paragraphs) {
  // toolbarLayout — FrameLayout background window_bg_color #fffdfb, height wrap = 64 (btnBack 40 + margin12 top+bottom)
  const toolbar_ = frame('toolbarLayout', 0, 0, SCREEN_W, 64, { fill: 'fdfdfd' });
  add(f, toolbar_);
  const backIc = icon('ic_back_1', 20, 20, 24, 24);
  if (backIc) add(toolbar_, backIc);
  add(toolbar_, text(title, 0, 12, { size: 20, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, h: 40, align: 'CENTER', valign: 'CENTER' }));

  // wvPrivacyPolicy — WebView, width fill, height match-constraint xuống đáy màn (0dp → 800-64=736)
  const web = frame('wvPrivacyPolicy · WebView', 0, 64, SCREEN_W, SCREEN_H - 64, { fill: C.white, clip: true });
  add(f, web);
  // Chú thích rút còn 1 dòng (fix đè chữ: bản 3 dòng cũ lấn xuống đoạn văn bản đầu tiên y=48).
  // Chi tiết "văn bản thật, không phải placeholder" đã có trong note của screen() — không lặp lại trên canvas.
  add(web, text('file:///android_asset/' + htmlFile + ' · 16 đoạn đầu', 16, 16, { size: 10, font: 'main', color: C.textSub, w: SCREEN_W - 32 }));

  // Nội dung HTML thật — 12sp Lato Regular #171716, cách đoạn 8dp, tiêu đề ngắn (<40 ký tự,
  // không kết thúc bằng dấu chấm) in đậm. FIX chồng chữ: KHÔNG đọc node.height sau text() (mock
  // capture-scene trả t.height=0→resize về 1, chỉ đúng trong Figma thật) — thay vào đó tự tính
  // số dòng từ độ dài chuỗi rồi TRUYỀN o.h tường minh (autoResize='NONE'), giống hệt Figma thật.
  const CW = 5.6; // bề rộng ký tự trung bình, Lato 12sp
  const LH = 16;  // line-height 12sp
  const PARA_W = SCREEN_W - 32; // 328, padding 16 trái/phải
  let cursor = 48;
  paragraphs.forEach((p) => {
    const isHeading = p.length < 40 && !p.trim().endsWith('.');
    const lines = Math.max(1, Math.ceil((p.length * CW) / PARA_W));
    const h = lines * LH;
    add(web, text(p, 16, cursor, {
      size: 12, weight: isHeading ? 700 : 400, font: 'main', color: C.textHi,
      w: PARA_W, h: h, lineHeight: LH,
    }));
    cursor += h + 8; // cách đoạn 8dp
  });
  // cursor cuối < 736 (chiều cao web frame) ở cả 2 màn → không cần grow(), nội dung vừa khung WebView.
}

// ---------------------------------------------------------------------------
// D70 · Loading overlay (full-screen dim) — res/layout/layout_loading.xml
// include trong fragment_preview_with_music.xml (id=viewLoading, visibility mặc định GONE)
// ---------------------------------------------------------------------------
dialog('D70 · Loading overlay · full-screen dim', 'res/layout/layout_loading.xml, include id=viewLoading trong fragment_preview_with_music.xml — bật khi FragmentPreviewWithMusic.genFile() đang export video. Nền vẽ lại chrome tối giản của chính fragment_preview_with_music.xml (res/layout/fragment_preview_with_music.xml: exoPlayerView fill, btnBack style BackImageButton2, btnAddMusic pill, btnNext style Button.Primary) — đây LUÔN là màn bên dưới overlay, không phải ô đen trơn. exoPlayerView = video kết quả · pathVideoPreview (runtime, do user tạo).', (f) => {
  // --- chrome tối giản của fragment_preview_with_music.xml (màn nền, LUÔN có mặt dưới overlay) ---
  // exoPlayerView (runtime, do user tạo) — chi tiết nguồn đã chuyển vào note của dialog() này
  remoteTile(f, 0, 0, SCREEN_W, SCREEN_H, '', 0);
  // btnBack — style BackImageButton2: padding4 margin12 → box48x48 tại (12,12), icon ic_back_2 36x36 fitCenter
  const backIc70 = icon('ic_back_2', 18, 18, 36, 36);
  if (backIc70) add(f, backIc70);
  // btnAddMusic — bg_black_40_rounded pill, bottom/top = btnBack (12..60), center ngang
  const pill70 = frame('btnAddMusic', (SCREEN_W - 120) / 2, 20, 120, 32, { fill: '66171716', radius: 40 });
  add(f, pill70);
  const musicIc70 = icon('ic_music', 8, 7, 18, 18);
  if (musicIc70) add(pill70, musicIc70);
  add(pill70, text('Song name', 30, 0, { size: 14, color: C.white, w: 120 - 30 - 8, h: 32, valign: 'CENTER' }));
  // btnNext — style Button.Primary, margin16, height48, bg gradient #00fbff→#0080f6, DISABLED (btnNext.setEnabled(false) khi genFile() đang chạy)
  const cta70 = frame('btnNext (disabled, genFile() đang chạy)', 16, SCREEN_H - 16 - 48, SCREEN_W - 32, 48, { gradient: ['2715d1', '7a14c9'], gradientDir: 'v', radius: 24, opacity: 0.5 });
  add(f, cta70);
  add(cta70, text('Next', 0, 0, { size: 16, weight: 700, color: C.textHi, w: SCREEN_W - 32, h: 48, align: 'CENTER', valign: 'CENTER' }));

  // --- overlay layout_loading.xml (đè lên trên) ---
  add(f, rect('background #40000000', 0, 0, SCREEN_W, SCREEN_H, { fill: '000000', opacity: 0x40 / 255 }));
  add(f, ellipse('ProgressBar (spinner OS mặc định)', (SCREEN_W - 40) / 2, (SCREEN_H - 40) / 2, 40, 40, { stroke: C.white, strokeW: 4 }));
});

// ---------------------------------------------------------------------------
// D71 · Loading card "Setting up" — res/layout/layout_loading_with_text.xml
// include trong fragment_language_picker.xml (id=viewLoading, visibility mặc định GONE)
// ---------------------------------------------------------------------------
dialog('D71 · Loading card · Setting up', 'res/layout/layout_loading_with_text.xml, include id=viewLoading trong fragment_language_picker.xml — bg root = @color/transparent (KHÔNG có scrim đen, khác D70), card bg_loading_rounded #ffd3d3d3 bo 12dp, text @string/setting_up_language. ⚠ CỜ đã verify độc lập (grep ui/language/FragmentLanguagePicker.java): showLoading() định nghĩa ở dòng 147 nhưng KHÔNG được gọi ở bất kỳ initUi()/click-listener nào đọc được — trùng phát hiện của cụm onboard (screens/onboard.js dòng note màn 12). Đây là STATE LÝ THUYẾT dựng đúng theo layout XML tồn tại thật, KHÔNG phải luồng đang chạy được trong build hiện tại. Nền vẽ chrome fragment_language_picker.xml ĐỦ 7 ngôn ngữ (dùng chung hằng LANGS ở code.js với màn 12/12b/12c, không khai báo lại) (entry point THẬT duy nhất còn lại = qua Settings → action_fragmentSettingsToLanguagePicker(false) → isFromSplash=false → btnBack VISIBLE theo FragmentLanguagePicker.java:181-189).', (f) => {
  // --- chrome tối giản của fragment_language_picker.xml (màn nền) ---
  add(f, img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));
  const backIc71 = icon('ic_back_1', 20, 20, 24, 24); // vào từ Settings → isFromSplash=false → VISIBLE
  if (backIc71) add(f, backIc71);
  add(f, text('Language', 0, 12, { size: 20, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, h: 40, align: 'CENTER', valign: 'CENTER' }));
  const doneIc71 = icon('ic_tick_disabled', 308, 20, 32, 32);
  if (doneIc71) add(f, doneIc71);
  // rvLanguage — dựng ĐỦ 7 ngôn ngữ từ LANGS (code.js), y hệt màn 12/12b/12c.
  // Trước đây chỉ vẽ 2 dòng ['English','Hindi'] cho gọn → nhìn vào tưởng app chỉ có 2 ngôn ngữ.
  LANGS.forEach((lang, i) => {
    const y = 60 + 16 + i * 80;
    const row71 = frame('item_language · ' + lang[0], 20, y, 320, 64, { fill: C.white, stroke: C.textHi, strokeW: 1, radius: 16 });
    add(f, row71);
    const chk71 = icon('ic_check_box_unselected', 20, 20, 24, 24);
    if (chk71) add(row71, chk71);
    add(row71, text(lang[0], 52, 0, { size: 20, weight: 700, font: 'main', color: C.textHi, w: 320 - 72, h: 64, valign: 'CENTER' }));
  });

  // --- overlay layout_loading_with_text.xml (đè lên trên, nền trong suốt — KHÔNG scrim) ---
  const w = 110, h = 94;
  const card = frame('LinearLayout · bg_loading_rounded', (SCREEN_W - w) / 2, (SCREEN_H - h) / 2, w, h, { fill: 'd4d1d5', radius: 12 });
  add(f, card);
  add(card, ellipse('ProgressBar', (w - 40) / 2, 16, 40, 40, { stroke: C.primary, strokeW: 4 }));
  add(card, text('Setting up', 0, 60, { size: 14, font: 'main', color: C.textHi, w: w, align: 'CENTER' }));
});

// ---------------------------------------------------------------------------
// D72 · Native full-screen ad — res/layout/dialog_native_full_screen.xml
// class ll0.I (com.cem.admodule) — DialogFragment, NativeFullscreenConfig/NativeFullscreenTemplate
// ---------------------------------------------------------------------------
dialog('D72 · AD SLOT · Native full-screen', 'res/layout/dialog_native_full_screen.xml (container_view, fill_parent, bg trắng) LỒNG res/layout/native_fake_full_inter.xml bên trong (NativeAdView thật được nạp vào container_view bởi ll0.I / NativeFullscreenTemplate). Geometry đọc trực tiếp từ native_fake_full_inter.xml: media_view fill 0x0, info-block bg_r8_f4f4f4_ads + backgroundTint #33000000 (ĐÃ verify: tint ghi đè màu solid f4f4f4 → nền THẬT là đen 20% trong suốt, không phải xám) margin L5T50R5 padding V15, badge "AD" (@string/ad) bg_text_view_ads=gnt_red #ffff0000 10sp trắng, primary 16sp bold trắng maxLines1 width70%, body 14sp trắng(gnt_white) maxLines2, cta 45dp bg_white_r16_ads+backgroundTint gnt_blue #4285f4 (→ THẬT là nút xanh, không trắng) text "Install" (@string/install) 20sp trắng width95%. Nội dung quảng cáo cụ thể (icon/tiêu đề/mô tả) là runtime → placeholder trung tính, không bịa thương hiệu. Placement không resolve tĩnh được (remote ad config monet/monet_v2/monet_super/and_ads_test) — CỜ.', (f) => {
  // media_view — 0x0 giãn hết toàn màn (app:layout_constraint...=parent cả 4 cạnh)
  adSlot(f, 0, 0, SCREEN_W, SCREEN_H, 'media_view (Ad media — ảnh/video quảng cáo, runtime)');

  // info-block — ConstraintLayout bg_r8_f4f4f4_ads + backgroundTint #33000000 (đen 20%), radius8,
  // paddingVertical15, margin L5 T50 R5 → x=5,y=50,w=350
  const infoX = 5, infoY = 50, infoW = SCREEN_W - 10;
  const info = frame('info-block · bg_r8_f4f4f4_ads (tint #33000000)', infoX, infoY, infoW, 104, { fill: '33000000', radius: 8 });
  add(f, info);
  // ad_notification_view "AD" — 10sp trắng, bg gnt_red, padding10/2/10/2, marginStart10, paddingTop15(của info)
  const badge = frame('ad_notification_view · bg_text_view_ads (gnt_red)', 10, 15, 34, 18, { fill: 'ff0000', radius: 10 });
  add(info, badge);
  add(badge, text('AD', 0, 0, { size: 10, weight: 500, font: 'roboto', color: C.white, w: 34, h: 18, align: 'CENTER', valign: 'CENTER' }));
  // primary — 16sp bold trắng, maxLines1, width 70% info-block, marginStart(badge.end+10)
  add(info, text('Ad headline', 54, 15, { size: 16, weight: 700, font: 'main', color: C.white, w: infoW * 0.7 - 10, h: 20 }));
  // body — 14sp trắng(gnt_white), maxLines2, margin L10 T5 R10 dưới primary
  add(info, text('Ad description text', 10, 40, { size: 14, font: 'main', color: C.white, w: infoW - 20, h: 34 }));

  // cta — AppCompatButton 45dp, bg_white_r16_ads + backgroundTint gnt_blue, width95%, margin L10T20R10B20, bottom=parent
  const ctaW = SCREEN_W * 0.95;
  const cta = frame('cta · bg_white_r16_ads (tint gnt_blue)', (SCREEN_W - ctaW) / 2, SCREEN_H - 20 - 45, ctaW, 45, { fill: 'ae37e0', radius: 16 });
  add(f, cta);
  add(cta, text('Install', 0, 0, { size: 20, weight: 500, font: 'roboto', color: C.white, w: ctaW, h: 45, align: 'CENTER', valign: 'CENTER' }));
}, { adOnly: true }); // toàn màn là 1 native ad (media_view+info-block+cta) — SHOW_ADS=false thì frame rỗng

// ---------------------------------------------------------------------------
// D73 · Native "fake app-open" ad — res/layout/activity_native_show_open_fake.xml
// class Il0.ll (com.cem.admodule) — DialogFragment theme NotHideDialog, NativeOpenConfig/NativeOpenTemplate
// ⚠ DARK PATTERN đã verify trong code: imgLogoApp/txtNameApp lấy TỪ PackageManager của CHÍNH APP
// Funny Face (context.getPackageName()), KHÔNG phải app quảng cáo — giả làm banner "tiếp tục vào app".
// ---------------------------------------------------------------------------
dialog('D73 · AD SLOT · Native fake app-open banner', 'res/layout/activity_native_show_open_fake.xml — class Il0.ll (com.cem.admodule.nextgen). Il0.ll.O(): imgLogoApp=getApplicationIcon(getPackageName()), txtNameApp=getApplicationLabel(getPackageName()) → icon/tên hiển thị = icon/tên THẬT của app Funny Face, không phải app được quảng cáo. container_view (native ad thật) chiếm hầu hết màn, containerName là banner giả phủ lên trên. imgViewClose (mũi tên, baseline_arrow_forward_ios_24) KHÔNG được gắn click listener trong Il0.ll.Il() — chỉ imgDismissNative (không icon hiển thị) mới thật sự gọi dismiss(). DARK PATTERN: vùng bấm "trông giống nút tiếp tục" (mũi tên) rơi xuống native ad bên dưới; nút đóng thật vô hình.', (f) => {
  // root — background #80000000
  add(f, rect('root #80000000', 0, 0, SCREEN_W, SCREEN_H, { fill: '000000', opacity: 0x80 / 255 }));

  // container_view — top=containerName.bottom(40)+marginTop8=48, xuống đáy màn. AD SLOT thật.
  adSlot(f, 0, 48, SCREEN_W, SCREEN_H - 48, 'Native Open (AdMob) — nội dung ad thật phủ dưới banner giả "tên app"');

  // containerName — bg_name_open_native (trắng, bo góc TRÁI 32dp, phải 0), width 80% (288), end=parent end (flush phải)
  const containerName = frame('containerName · bg_name_open_native', SCREEN_W - 288, 0, 288, 40, { fill: C.white });
  containerName.topLeftRadius = 32; containerName.bottomLeftRadius = 32;
  containerName.topRightRadius = 0; containerName.bottomRightRadius = 0;
  add(f, containerName);

  // imgLogoApp — icon THẬT của app (PackageManager.getApplicationIcon), khoá ảnh ic_launcher
  add(containerName, img('ic_launcher', 5, 7, 25, 25, 'FIT'));

  // txtNameApp — tên THẬT của app (PackageManager.getApplicationLabel), maxLines=1 maxLength=14
  add(containerName, text('Funny Face Ma…', 30, 0, { size: 16, font: 'main', color: C.black, w: 100, h: 40, valign: 'CENTER', align: 'LEFT' }));

  // txtContinueToApp — text tĩnh "Continue to app", fontFamily sans-serif-medium (map Roboto Medium)
  add(containerName, text('Continue to app', 132, 0, { size: 13, weight: 500, font: 'roboto', color: C.grayDark, w: 90, h: 40, valign: 'CENTER', align: 'CENTER' }));

  // container (cụm 2 icon bên phải) — cùng bg_name_open_native, bo TRÁI 32, phải 0
  const iconCluster = frame('container · bg_name_open_native', 228, 0, 60, 40, { fill: C.white });
  iconCluster.topLeftRadius = 32; iconCluster.bottomLeftRadius = 32;
  iconCluster.topRightRadius = 0; iconCluster.bottomRightRadius = 0;
  add(containerName, iconCluster);

  // imgViewClose — src baseline_arrow_forward_ios_24, padding10 (glyph 20x20). KHÔNG có click listener trong app code.
  vpath(iconCluster, 25, 10, 20, 20, '24 24', 'M9,5 L16,12 L9,19', { stroke: C.black, sw: 2, name: 'imgViewClose · ic_forward (không gắn onClick trong code app)' });

  // imgDismissNative — 40x40, KHÔNG có src (vô hình trong app thật) — nút đóng thật, viền đỏ chỉ để chú thích trong Figma
  add(iconCluster, rect('imgDismissNative · tap-target đóng thật (vô hình trong app, không có icon hiển thị)', 15, 0, 40, 40, { stroke: 'ff0000', strokeW: 1, radius: 20 }));
}, { adOnly: true }); // toàn màn là banner quảng cáo giả dạng app phủ lên native ad — SHOW_ADS=false thì frame rỗng. Note/code giữ nguyên, bật lại SHOW_ADS=true là hiện đủ (kể cả phần dark-pattern).
