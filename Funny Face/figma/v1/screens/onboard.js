// ============================================================================
//  Cụm "onboard" — FragmentSplash (10) → FragmentIntro (11a/b/c) / FragmentLanguagePicker (12)
//  Nguồn số liệu: specs/onboard.md (Plan 1 Phase 2). Mọi x/y/w/h suy từ constraint + dimens
//  thật (@dimen/size_16=16, size_8=8, size_12=12, size_20=20, size_150=150, size_30=30).
//  Nhánh MẶC ĐỊNH của app: Splash → thẳng Home (onboarding_enabled=false, language_enabled=false,
//  cả 2 đúng key RC đã fetch, default-khi-lỗi cũng false). FragmentIntro/FragmentLanguagePicker
//  trong file này là nhánh KHÔNG mặc định (chỉ vào qua Settings, hoặc nếu RC bật lại 2 flag).
//  img_intro_1/2/3: đã xác minh KHÔNG TỒN TẠI trong APK (id có trong R.java nhưng không có entry
//  trong public.xml, resolve-arsc.py trả NULL, không có file img_intro* trong unzip -l) →
//  remoteTile() có nhãn, KHÔNG thay ảnh khác. showLoading() của LanguagePicker là dead code
//  (không nơi nào gọi trong smali) → KHÔNG dựng overlay "Setting up".
// ============================================================================
(function () {

  const STR = {
    loading: 'Loading...',
    adsNote: 'This action contain ads',
    mixFaces: 'Mix Faces, Make Fun Happen!',
    takeChallenge: 'Take the challenge with your friends',
    recordLaugh: 'Record, Laugh, Go Viral!',
    start: 'Start',
    language: 'Language',
  };

  // LANGS (7 ngôn ngữ, đúng thứ tự AppSetting.java:44) nay khai báo ở code.js — dùng chung với D71.

  // ad tile chiều cao ước lượng cho native ad wrap_content (không có số thật trong spec vì
  // phụ thuộc SDK/ template lúc runtime) — chỉ dùng để layout hợp lý, ghi rõ là ước lượng.
  const AD_H = 100;

  // khung viền NÉT ĐỨT vẽ trực tiếp bằng SVG (figma.createNodeFromSvg) — helper frame() không
  // hỗ trợ dash, nên tự vẽ để "trông có chủ ý" chứ không phải viền mờ.
  function dashedFrame(parent, x, y, w, h, o) {
    o = o || {};
    const sw = o.strokeW || 2;
    const fillHex = o.fill || '242424';
    const strokeHex = o.stroke || 'f19336';
    const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + w + '" height="' + h + '">' +
      '<rect x="' + (sw / 2) + '" y="' + (sw / 2) + '" width="' + (w - sw) + '" height="' + (h - sw) + '" ' +
      'fill="#' + fillHex + '" stroke="#' + strokeHex + '" stroke-width="' + sw + '" stroke-dasharray="' + (o.dash || '10,8') + '"/></svg>';
    const n = figma.createNodeFromSvg(svg);
    n.name = o.name || 'dashed';
    n.x = x; n.y = y; n.resize(w, h);
    add(parent, n);
    return n;
  }

  // ---------------------------------------------------------------- 10 · FragmentSplash
  // layout/fragment_splash.xml (ConstraintLayout). Geometry: xem specs/onboard.md mục 1.A.
  function buildSplash(f, opt) {
    opt = opt || {};
    // nền: gradient dọc trắng → #08bdff, resolve từ drawable/$bg_splash__0.xml (linear gradient
    // offset0=#ffffffff offset1=#ff08bdff, trục (187.5,0)→(187.5,812))
    add(f, frame('bg_splash · gradient', 0, 0, SCREEN_W, SCREEN_H, { gradient: ['ffffff', '08bdff'], gradientDir: 'v' }));

    // Guideline lineCenterY @ 46% chiều cao = 368dp. ic_logo: wrap×wrap, centered trong khoảng
    // 0..368 (top+bottom constraint), centered ngang toàn màn. Ảnh export 334×181px (40-anh-app/ic_splash).
    const logoW = 334, logoH = 181;
    const logoX = (SCREEN_W - logoW) / 2;
    const logoY = (SCREEN_H * 0.46 - logoH) / 2;
    add(f, img('ic_splash', logoX, logoY, logoW, logoH, 'FIT'));

    // progress: top→ic_logo.bottom marginTop16, width 60% (216dp) centered, style CustomProgressBar
    // (maxHeight20 minHeight10 → wrap_content render ~ minHeight khi drawable không có intrinsic height)
    const progY = logoY + logoH + 16;
    const progW = SCREEN_W * 0.6, progX = (SCREEN_W - progW) / 2, progH = 10;
    const track = frame('progress · track', progX, progY, progW, progH, { fill: 'ffffff', stroke: '1a000000', strokeW: 1, radius: 8 });
    add(f, track);
    const pct = opt.progressPct !== undefined ? opt.progressPct : 0.5;
    add(f, rect('progress · fill', progX, progY, progW * pct, progH, { fill: '7a00e2', radius: 8 }));

    // tvLoading: top→progress.bottom marginTop16, style ScreenTitleCommon (20sp bold center textHi)
    const loadY = progY + progH + 16;
    add(f, textC(STR.loading, loadY, { size: 20, weight: 700, font: 'main', color: C.textHi }));
    const loadH = 26;

    // adContainer: top→tvLoading.bottom, bottom→tvNote.top, margin 16 hai bên — AD SLOT native_splash
    const noteH = 26;
    const noteY = SCREEN_H - 16 - noteH;
    const adY = loadY + loadH + 16;
    // adContainer chỉ vẽ khi SHOW_ADS=true (kể cả trạng thái "chưa load" — đó cũng là nội dung
    // thuộc khu vực quảng cáo, không phải UI cố định của app). Chi tiết vị trí/placement nằm ở
    // note của screen('10 ...').
    if (SHOW_ADS) {
      if (opt.showAd) {
        adSlot(f, 16, adY, SCREEN_W - 32, AD_H, 'native_splash (Style6)');
      } else {
        add(f, frame('adContainer · empty', 16, adY, SCREEN_W - 32, AD_H, { fill: '1a1a1a', stroke: '3a3a3a', strokeW: 1, radius: 8 }));
        add(f, text('adContainer (chưa load)', 16, adY + AD_H / 2 - 7, { size: 11, color: '6a6a6a', w: SCREEN_W - 32, align: 'CENTER' }));
      }
    }

    // tvNote: bottom=parent marginBottom16, style ScreenTitleCommon
    add(f, textC(STR.adsNote, noteY, { size: 20, weight: 700, font: 'main', color: C.textHi }));

    // config View 150×150 top-start=parent — hitbox debug Monet.setupDeveloperMode, không có nội dung UI
    add(f, frame('config · debug hitbox (invisible)', 0, 0, 150, 150, {}));
  }

  screen('10 · Splash · đang load', 'layout/fragment_splash.xml + ui/onboard/FragmentSplash.java:110-134 (initUi, progress loop 0-100 1500ms REVERSE vô hạn). ' +
    'NHÁNH MẶC ĐỊNH CỦA APP: goToInside() (FragmentSplash.java:42-49) → vì onboarding_enabled=false VÀ language_enabled=false (key thật đúng RC đã fetch, default-khi-lỗi cũng false) → Splash điều hướng THẲNG tới Home (isShowHomeNewUI()=true vì ui_home_show_case=1 → actionSplashToHome, KHÔNG phải HomeOldUI), bỏ qua cả FragmentIntro lẫn FragmentLanguagePicker. 2 màn đó (11/12 trong file này) là nhánh KHÔNG MẶC ĐỊNH — chỉ vào được qua Settings (action_fragmentSettingsToLanguagePicker) hoặc nếu RC bật lại onboarding_enabled/language_enabled. adContainer nằm giữa tvLoading và tvNote (margin 16dp hai bên/trên), nhận native_splash Style6 lúc chạy (FragmentSplash.loadAndShowNative smali dòng 502-609) — chỉ vẽ khi SHOW_ADS=true (kể cả trạng thái \"chưa load\"), tắt ads là ẩn hẳn ô này. \"This action contain ads\" (tvNote, @string/this_action_contain_ads) là CHUỖI THẬT của app, KHÔNG phải ô quảng cáo — luôn giữ, không tắt theo SHOW_ADS.',
    (f) => { buildSplash(f, { progressPct: 0.35, showAd: false }); });

  screen('10b · Splash · load xong', 'ui/onboard/FragmentSplash.loadAndShowNative (smali dòng 502-609): Monet.start → NativeManager.present("native_splash", Style6) vào adContainer, rồi FullscreenManager.present("inter_splash") (xem 10c), sau đó goToInside() tự điều hướng khi lifecycle≥STARTED. Khác "10 · đang load" ở progress=100% (10 =35%) — vẫn giữ khi SHOW_ADS=false vì progress bar khác nhau nên KHÔNG trùng lặp; ad tile tự ẩn qua adSlot()/SHOW_ADS.',
    (f) => { buildSplash(f, { progressPct: 1, showAd: true }); });

  dialog('10c · Splash · Interstitial ads (inter_splash)', 'FragmentSplash.loadAndShowNative smali dòng 623-627: FullscreenManager.present(activity,"inter_splash",false,...) — overlay full-screen của SDK ads, KHÔNG phải 1 view trong fragment_splash.xml, đè lên trên Splash trước khi goToInside(). Toàn bộ frame là nội dung quảng cáo (kể cả phần vẽ tay card/badge/close/media/CTA, không qua adSlot()) → bỏ hẳn khỏi registry khi SHOW_ADS=false.',
    (f) => {
      // nền: màn Splash bên dưới (đúng cái mà interstitial đè lên trong luồng thật)
      buildSplash(f, { progressPct: 1, showAd: true });
      // scrim: dim màn bên dưới trước khi ad SDK vẽ đè
      add(f, rect('scrim', 0, 0, SCREEN_W, SCREEN_H, { fill: '000000', opacity: 0.6 }));

      // khung interstitial tối giản — UI THẬT DO SDK (Applovin/AdMob…) TỰ VẼ LÚC RUNTIME,
      // KHÔNG có layout XML nào trong APK cho nó → mọi chi tiết dưới đây là bố cục điển hình
      // của 1 interstitial (đóng / badge Ad / media / CTA), không phải ảnh chụp quảng cáo thật.
      const cardW = SCREEN_W - 16, cardH = SCREEN_H - 16; // 8dp margin mỗi phía
      const card = frame('AD SLOT · inter_splash — UI của SDK quảng cáo (không có layout trong APK)', 8, 8, cardW, cardH, { fill: '1a1a1a', stroke: '3a3a3a', strokeW: 1, radius: R.card });
      add(f, card);

      // badge "Ad" — top-left (toạ độ local trong `card`)
      const badge = frame('badge · Ad', 16, 16, 30, 18, { fill: '2d2d2d', radius: 4 });
      add(card, badge);
      add(badge, text('Ad', 0, 2, { size: 10, weight: 700, font: 'main', color: 'c0c0c0', w: 30, align: 'CENTER' }));

      // nút đóng (X) — top-right, xuất hiện sau vài giây theo hành vi chuẩn của SDK ads
      const closeR = 28, closeX = cardW - 16 - closeR;
      add(card, ellipse('close · bg', closeX, 16, closeR, closeR, { fill: '000000', opacity: 0.45 }));
      vpath(card, closeX + 6, 16 + 6, 16, 16, '24 24', 'M6 6 L18 18 M18 6 L6 18', { stroke: 'ffffff', sw: 2, name: 'ic_close' });

      // nhãn bắt buộc: đây là UI của SDK, không phải nội dung app
      add(card, text('UI của SDK quảng cáo — không có layout trong APK', 16, 56, { size: 11, weight: 700, font: 'main', color: 'f19336', w: cardW - 32, align: 'CENTER' }));

      // vùng media (creative ad — nội dung do network ads trả về lúc runtime, không tĩnh)
      const mediaY = 88, ctaH = 48, ctaY = cardH - 16 - ctaH, mediaH = ctaY - 12 - mediaY;
      const media = frame('media (SDK ad creative — runtime)', 16, mediaY, cardW - 32, mediaH, { fill: '2a2a2a', radius: 8 });
      add(card, media);
      add(media, text('media (SDK ad creative)', 0, mediaH / 2 - 7, { size: 11, color: '6a6a6a', w: cardW - 32, align: 'CENTER' }));

      // CTA "Install" — pill button chuẩn interstitial
      add(card, rect('CTA · Install', 16, ctaY, cardW - 32, ctaH, { fill: C.primary, radius: R.pill }));
      add(card, text('Install', 16, ctaY, { size: 16, weight: 700, font: 'main', color: 'ffffff', w: cardW - 32, h: ctaH, align: 'CENTER', valign: 'CENTER' }));
    }, { adOnly: true });

  // ---------------------------------------------------------------- 11a/b/c · FragmentIntro
  // layout/fragment_intro.xml (ConstraintLayout) + item_intro.xml. Geometry: specs/onboard.md mục 2.A.
  const INTRO_PAGES = [
    { key: 'img_intro_1', id: '0x7f080248', desc: STR.mixFaces, ad: 'native_onboard' },
    { key: 'img_intro_2', id: '0x7f080249', desc: STR.takeChallenge, ad: 'native_onboard2' },
    { key: 'img_intro_3', id: '0x7f08024a', desc: STR.recordLaugh, ad: 'native_onboard3' },
  ];

  function buildIntroPage(f, pageIndex, opt) {
    opt = opt || {};
    const p = INTRO_PAGES[pageIndex];

    // tính layout TRƯỚC (không vẽ gì) để biết ô ảnh dừng ở đâu, tránh đè lên bottomView.
    const adY = SCREEN_H - AD_H;
    const controlH = 30;
    const descH = 24;
    const bottomViewBottom = adY - 16;
    const controlY = bottomViewBottom - controlH;
    const descY = controlY - descH;

    // windowBackground: fragment_intro.xml root KHÔNG set android:background (ConstraintLayout
    // trong suốt) → nền thật là theme windowBackground = @mipmap/window_bg. Vẽ full-bleed ĐẦU
    // TIÊN, dưới mọi thứ khác — y hệt quy ước screens/settings-dialogs.js.
    const bg = img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL');
    bg.name = 'windowBackground · window_bg';
    add(f, bg);

    // viewPager: top/start/end=parent, height wrap_content nhưng item_intro là FrameLayout fill×fill.
    // img_intro_1/2/3: KHÔNG TỒN TẠI trong APK (đã truy đến tận cùng — R.java có id nhưng
    // values/public.xml KHÔNG có entry, resolve-arsc trả NULL mọi config, không có file img_intro*
    // trong unzip -l). RULING: dựng placeholder CÓ CHỦ Ý, đọc được, không phải khung trống/mờ.
    // Ô ảnh CHỈ chiếm phần trên (0..descY) — bottomView/adContainer bên dưới không có background
    // riêng trong XML nên vẫn hiện windowBackground (đúng như app thật, giữ chuỗi marketing #171716
    // đọc được trên nền sáng thay vì đè lên placeholder tối).
    const introBox = dashedFrame(f, 0, 0, SCREEN_W, descY, { fill: '242424', stroke: 'f19336', strokeW: 3, dash: '12,8', name: p.key + ' — không có trong APK' });
    // badge nhỏ gọn góc trên-trái — chi tiết bằng chứng đầy đủ chuyển xuống note của screen()
    // (setPluginData('source')), đọc khi click layer trong Figma; canvas chỉ giữ 1 dòng ngắn.
    const badgeLabel = p.key + ' · không có trong APK';
    const badgeW = 8 + badgeLabel.length * 5.6 + 8;
    add(introBox, frame('badge · ' + badgeLabel, 16, 16, badgeW, 22, { fill: '000000', opacity: 0.55, stroke: 'f19336', strokeW: 1, radius: 4 }));
    add(introBox, text(badgeLabel, 24, 20, { size: 11, weight: 700, font: 'main', color: 'ffffff' }));

    // adContainer: bottom=parent, width fill, marginTop16 — AD SLOT theo trang (native_onboard/2/3)
    adSlot(f, 0, adY, SCREEN_W, AD_H, p.ad + ' (trang ' + (pageIndex + 1) + '/3, chỉ load 1 lần/trang — traveledPages early-return, FragmentIntro$loadAdIfNeed$1.smali:340-353)');

    // bottomView: bottom→adContainer.top marginBottom16. controlBar (dots+Start) VISIBLE vì
    // onboarding_buttons_enabled=true (RC, nhánh mặc định của flag này) — FragmentIntro.java:245-253.
    // Text màu C.textHi (#171716, kế thừa theme — item_intro.xml không set textColor riêng) —
    // ĐÚNG như spec, giữ nguyên; giờ đọc được vì nền dưới là windowBackground sáng, không phải introBox tối.
    add(f, textC(p.desc, descY, { size: 16, weight: 600, font: 'main', color: C.textHi }));

    // dotsIndicator: dotsSize=4dp, dotsWidthFactor=4.5 (dot đang chọn rộng 18dp), spacing 4dp,
    // dotsColor=gray(#c0c0c0), selectedDotColor=primary(#016cf7). 3 chấm cho 3 trang.
    let dotX = 16;
    const dotY = controlY + (controlH - 4) / 2;
    for (let i = 0; i < 3; i++) {
      const w = i === pageIndex ? 18 : 4;
      add(f, ellipse('dot ' + (i + 1), dotX, dotY, w, 4, { fill: i === pageIndex ? C.primary : C.gray }));
      dotX += w + 4;
    }

    // nextButton "Start": textColor selector button_text_color (disabled→gray, enabled→primary).
    // Ở trang này nút đã unlock (>500ms sau khi vào trang, lockContinueButton() FragmentIntro.java:107-114).
    add(f, text(STR.start, SCREEN_W - 20 - 74, controlY, {
      size: 16, weight: 700, font: 'main', w: 74, h: controlH,
      align: 'RIGHT', valign: 'CENTER', color: opt.buttonEnabled === false ? C.gray : C.primary,
    }));

    // animation_view (Lottie swipe_left.json, loop=true): mặc định invisible, CHỈ show ở trang 0
    // (onPageSelected position==0 → show+play sau 500ms, KHÔNG bị chặn bởi onboarding_buttons_enabled
    // — FragmentIntro$setupViewPager$1$onPageSelected$1.java). Vẽ khung tĩnh, ghi tên asset gốc.
    if (opt.showLottie) {
      const lw = 150, lh = 150, lx = (SCREEN_W - lw) / 2, ly = (SCREEN_H - lh) / 2;
      const g = frame('animation_view · Lottie swipe_left.json (loop)', lx, ly, lw, lh, { fill: '000000', opacity: 0.05, stroke: '3a3a3a', strokeW: 1, radius: 8 });
      add(f, g);
      add(g, text('Lottie: swipe_left.json\n(assets/swipe_left.json, loop=true)', 0, lh / 2 - 16, { size: 10, color: '6a6a6a', w: lw, align: 'CENTER' }));
    }
  }

  screen('11a · Intro · trang 1/3', 'layout/fragment_intro.xml + ui/onboard/FragmentIntro.java:117-203 (setupViewPager, onPageSelected position=0). Text @string/mix_faces_make_fun="Mix Faces, Make Fun Happen!". Ad native_onboard (AdKey.NATIVE_INTRO_1). Lottie swipe_left.json show sau 500ms (setupViewPager$1$onPageSelected$1). Nhánh KHÔNG mặc định của app (xem note màn 10). ' +
    'img_intro_1 KHÔNG CÓ TRONG APK: R.drawable.img_intro_1=0x7f080248 (R.java:157) · values/public.xml KHÔNG có entry (nhảy thẳng 0x…247→0x…24b) · resolve-arsc.py trả NULL mọi config · không có file img_intro* trong unzip -l · đã loại trừ split APK (không lib/, không split_*, có resources.arsc đầy đủ 1 file) → nghi do resource shrinking hoặc dấu vết reskin (AndroidManifest package com.filter.face.puzzle ≠ code namespace com.cem.face.puzzle). RULING: KHÔNG thay ảnh khác, chỉ dựng placeholder có nhãn. windowBackground=@mipmap/window_bg (fragment root transparent, không set android:background). LOẠI KHỎI BẢN TRÌNH BÀY theo yêu cầu design lead (ô ảnh trống vì img_intro_N không tồn tại trong APK). Code giữ nguyên — bỏ { excluded: true } là frame quay lại.',
    (f) => { buildIntroPage(f, 0, { buttonEnabled: true, showLottie: true }); }, { excluded: true });

  screen('11b · Intro · trang 2/3', 'layout/fragment_intro.xml + FragmentIntro.java dòng 169-187 (onPageSelected position=1). Text @string/take_the_challenge="Take the challenge with your friends". Ad native_onboard2 (AdKey.NATIVE_INTRO_2). Lottie chỉ show nếu onboarding_buttons_enabled=false (không mặc định) — mặc định flag=true nên KHÔNG show ở trang này. ' +
    'img_intro_2 KHÔNG CÓ TRONG APK: R.drawable.img_intro_2=0x7f080249 (R.java:158) · values/public.xml KHÔNG có entry (nhảy thẳng 0x…247→0x…24b) · resolve-arsc.py trả NULL mọi config · không có file img_intro* trong unzip -l · đã loại trừ split APK (không lib/, không split_*, có resources.arsc đầy đủ 1 file) → nghi do resource shrinking hoặc dấu vết reskin (AndroidManifest package com.filter.face.puzzle ≠ code namespace com.cem.face.puzzle). RULING: KHÔNG thay ảnh khác, chỉ dựng placeholder có nhãn. windowBackground=@mipmap/window_bg (fragment root transparent, không set android:background). LOẠI KHỎI BẢN TRÌNH BÀY theo yêu cầu design lead (ô ảnh trống vì img_intro_N không tồn tại trong APK). Code giữ nguyên — bỏ { excluded: true } là frame quay lại.',
    (f) => { buildIntroPage(f, 1, { buttonEnabled: true, showLottie: false }); }, { excluded: true });

  screen('11c · Intro · trang 3/3', 'layout/fragment_intro.xml + FragmentIntro.java dòng 169-192 (onPageSelected position=2): animationView.pauseAnimation()+gone(). Text @string/record_laugh="Record, Laugh, Go Viral!". Ad native_onboard3 (AdKey.NATIVE_INTRO_3). Bấm "Start" ở trang cuối → finish() → actionIntroToHome (FragmentIntro.java:57-60). ' +
    'img_intro_3 KHÔNG CÓ TRONG APK: R.drawable.img_intro_3=0x7f08024a (R.java:159) · values/public.xml KHÔNG có entry (nhảy thẳng 0x…247→0x…24b) · resolve-arsc.py trả NULL mọi config · không có file img_intro* trong unzip -l · đã loại trừ split APK (không lib/, không split_*, có resources.arsc đầy đủ 1 file) → nghi do resource shrinking hoặc dấu vết reskin (AndroidManifest package com.filter.face.puzzle ≠ code namespace com.cem.face.puzzle). RULING: KHÔNG thay ảnh khác, chỉ dựng placeholder có nhãn. windowBackground=@mipmap/window_bg (fragment root transparent, không set android:background). LOẠI KHỎI BẢN TRÌNH BÀY theo yêu cầu design lead (ô ảnh trống vì img_intro_N không tồn tại trong APK). Code giữ nguyên — bỏ { excluded: true } là frame quay lại.',
    (f) => { buildIntroPage(f, 2, { buttonEnabled: true, showLottie: false }); }, { excluded: true });

  // ---------------------------------------------------------------- 12 · FragmentLanguagePicker
  // layout/fragment_language_picker.xml + item_language.xml. Geometry: specs/onboard.md mục 3.A.
  function buildLanguagePicker(f, opt) {
    opt = opt || {};

    // windowBackground: fragment_language_picker.xml root KHÔNG set android:background
    // (ConstraintLayout trong suốt) → nền thật là theme windowBackground = @mipmap/window_bg.
    // Vẽ full-bleed ĐẦU TIÊN, dưới mọi thứ khác — quy ước như screens/settings-dialogs.js.
    const bg = img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL');
    bg.name = 'windowBackground · window_bg';
    add(f, bg);

    // btnBack: style BackImageButton1 (Base.PrimaryButton.Square 48×48, padding8, margin12,
    // src=ic_back_1). isFromSplash=true (entry point của cụm onboard) → setVisibility(INVISIBLE).
    if (opt.btnBackVisible) {
      const ic = icon('ic_back_1', 20, 20, 32, 32);
      if (ic) add(f, ic);
    }

    // appCompatTextView4 "Language": bottom/top→btnBack (y=12,h=48), style ScreenTitleCommon
    add(f, text(STR.language, 0, 12, { size: 20, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, h: 48, align: 'CENTER', valign: 'CENTER' }));

    // btnDone: style Base.PrimaryButton.Square 48×48, end=parent marginEnd12, src=ic_tick_selector
    // (disabled→ic_tick_disabled, enabled→ic_tick). initUi() set enabled(false) ban đầu (dòng 271).
    const doneIcon = icon(opt.hasSelection ? 'ic_tick' : 'ic_tick_disabled', 308, 20, 32, 32);
    if (doneIcon) add(f, doneIcon);

    // adContainer: bottom=parent marginTop16 — AD SLOT: native_language lúc mở màn, đổi sang
    // native_language2 ngay khi chọn ngôn ngữ lần đầu (willShowSecondAd true→false, chỉ 1 lần)
    const adY = SCREEN_H - AD_H;
    adSlot(f, 0, adY, SCREEN_W, AD_H, opt.hasSelection ? 'native_language2' : 'native_language');

    // rvLanguage: top→btnBack.bottom(=60), bottom→adContainer.top marginBottom8, LinearLayoutManager
    const listTop = 60;
    const itemW = SCREEN_W - 40, itemX = 20, itemH = 64, gapTop = 16; // SettingItemText: padding20 + marginTop16 + marginStart/End20
    let y = listTop;
    LANGS.forEach((lang, i) => {
      y += gapTop;
      const it = frame('item_language · ' + lang[0], itemX, y, itemW, itemH, { fill: 'ffffff', stroke: C.textHi, strokeW: 1, radius: 16 });
      add(f, it);
      const selected = opt.selectedIndex === i;
      const ic = icon(selected ? 'ic_check_box_selected' : 'ic_check_box_unselected', 20, itemH / 2 - 12, 24, 24);
      if (ic) add(it, ic);
      add(it, text(lang[0], 52, 0, { size: 20, weight: 700, font: 'main', color: C.textHi, w: itemW - 72, h: itemH, valign: 'CENTER' }));
      y += itemH;
    });
    grow(f, Math.max(SCREEN_H, y + 8));
  }

  screen('12 · Language Picker · chưa chọn', 'layout/fragment_language_picker.xml + ui/language/FragmentLanguagePicker.java:181-272 (initUi). isFromSplash=true → btnBack INVISIBLE (dòng 190). 7 ngôn ngữ hardcode đúng thứ tự AppSetting.kt (data/system/AppSetting.java:44): English/Hindi/Spanish/French/Portuguese/Vietnamese/Japanese. Không item nào selected (chỉ set currentLanguage cho adapter khi !isFromSplash, dòng 202-204). btnDone disabled (dòng 271). Ad native_language (loadAndShowFirstAd, AdKey.NATIVE_LANGUAGE). Nhánh KHÔNG mặc định của app (xem note màn 10). KHÔNG dựng overlay "Setting up": showLoading() là dead code, không nơi nào gọi (đã grep toàn bộ smali ui/language/). windowBackground=@mipmap/window_bg (fragment root transparent, không set android:background).',
    (f) => { buildLanguagePicker(f, { btnBackVisible: false, hasSelection: false, selectedIndex: -1 }); });

  screen('12b · Language Picker · đã chọn English', 'FragmentLanguagePicker.java:118-126 (initUi$lambda$0$0): tap 1 ngôn ngữ → btnDone.setEnabled(true), currentLanguage đổi selected (AdapterLanguage.onBindData dòng 85-99: chỉ icon drawableStart đổi ic_check_box_selected/_unselected, nền bg_item_setting là shape TĨNH không đổi theo state — đã xác minh, không phải selector), loadAndShowSecondAd() → ad chuyển native_language2 (willShowSecondAd true→false, chỉ 1 lần, FragmentLanguagePicker$loadAndShowSecondAd$1.java:54-65). windowBackground=@mipmap/window_bg (fragment root transparent, không set android:background).',
    (f) => { buildLanguagePicker(f, { btnBackVisible: false, hasSelection: true, selectedIndex: 0 }); });

  // Nhánh vào từ Settings (action_fragmentSettingsToLanguagePicker, main_nav.xml:43) —
  // isFromSplash=false. Đây là đường vào DUY NHẤT còn sống khi RC language_enabled=false,
  // và là màn người dùng thực tế gặp trên máy.
  screen('12c · Language Picker · vào từ Settings', 'layout/fragment_language_picker.xml + ui/language/FragmentLanguagePicker.java:181-272 (initUi), vào qua main_nav.xml:43 action_fragmentSettingsToLanguagePicker → isFromSplash=FALSE. Khác màn 12/12b ở 3 điểm, cả 3 đều đọc thẳng từ code: (1) btnBack VISIBLE — dòng 190 btnBack.setVisibility(isFromSplash ? 4 : 0); (2) ngôn ngữ hiện hành được chọn sẵn — dòng 202-204 if(!isFromSplash) adapter.setCurrentLanguage(sharedViewModel.currentLanguage), minh hoạ English = mặc định; (3) btnDone VẪN disabled (ic_tick_disabled) vì dòng 271 btnDone.setEnabled(false) gọi VÔ ĐIỀU KIỆN ở cuối initUi(), sau cả nhánh setCurrentLanguage — tick chỉ sáng khi người dùng tự tap 1 item. Đối chiếu ảnh chụp máy thật: khớp cả 3. windowBackground=@mipmap/window_bg (fragment root transparent).',
    (f) => { buildLanguagePicker(f, { btnBackVisible: true, hasSelection: false, selectedIndex: 0 }); });

})();
