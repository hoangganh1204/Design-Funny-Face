// ============================================================================
//  Cụm: face-puzzle — FragmentFacePuzzle (quay video AR filter) + FragmentLevelPicker
//  Nguồn số liệu: specs/face-puzzle.md (đã fix round 1: showAdsInList=false, v1/v2 endpoint)
//  Mọi layer truy được về 1 view trong fragment_face_puzzle.xml / fragment_level_picker.xml
//  hoặc 1 hành vi code trích trong spec. KHÔNG dựng item_face_puzzle_template/_ad (cụm home).
// ============================================================================
(function () {
  // ---- số đo dẫn xuất từ tỉ lệ ảnh THẬT đã export (không bịa, xem spec mục A/D) ----
  var LV_W = 320, LV_H = (320 * 360) / 1008;              // bg_level_* thật = 1008x360px
  var NOTIFY_W = 306, NOTIFY_H = (306 * 84) / 1025;        // img_notify_puzzle thật = 1025x84px

  // ---- RecordingProgress (custom onDraw, ui/custom_view/RecordingProgress.java) ----
  // btnRecording = 80x80dp; Paint strokeWidth=12px → progressRectF inset 6dp mỗi cạnh
  // → tâm (40,40) bán kính 34dp trong hệ toạ độ cục bộ của nút.
  function recordingButton(f, x, y, opt) {
    opt = opt || {};
    var g = frame('btnRecording', x, y, 80, 80, {});
    add(f, g);
    if (opt.arcSweepDeg) {
      // vẽ tay cung tiến trình: canvas.drawArc(rect, startAngle=-90, sweep=360*progress)
      var start = -90, endDeg = start + opt.arcSweepDeg;
      var toRad = function (d) { return (d * Math.PI) / 180; };
      var sx = 40 + 34 * Math.cos(toRad(start)), sy = 40 + 34 * Math.sin(toRad(start));
      var ex = 40 + 34 * Math.cos(toRad(endDeg)), ey = 40 + 34 * Math.sin(toRad(endDeg));
      var large = opt.arcSweepDeg > 180 ? 1 : 0;
      var d = opt.arcSweepDeg >= 359.9
        ? 'M' + sx + ',' + sy + ' A34,34 0 1 1 ' + (sx - 0.01) + ',' + (sy + 0.01)
        : 'M' + sx.toFixed(2) + ',' + sy.toFixed(2) + ' A34,34 0 ' + large + ' 1 ' + ex.toFixed(2) + ',' + ey.toFixed(2);
      vpath(g, 0, 0, 80, 80, '80 80', d, { stroke: '5416cd', sw: 12, name: 'progress-arc' });
    }
    // drawIcon(): min=80, f=40, iconRectF=(0,0,80,80) → bitmap kéo phủ TRỌN 80x80 (không inset)
    var ic = icon(opt.icon || 'ic_play_filter', 0, 0, 80, 80);
    if (ic) add(g, ic);
    return g;
  }

  // ---- hàng trên cùng: btnBack + (btnAddMusic) + btnFlipCamera ----
  function backButton(f, iconKey) {
    var b = icon(iconKey, 16, 16, 40, 40); // BackImageButton2: box 48x48 @(12,12), padding4
    if (b) add(f, b);
  }
  function flipCameraButton(f) {
    var b = icon('ic_rotation_camera', 308, 16, 40, 40); // box 48x48 end margin8, padding4
    if (b) add(f, b);
  }
  function musicPill(f, hasSong) {
    var w = hasSong ? 168 : 140; // wrap_content thật, ước lượng theo nội dung (≤ maxWidth 180dp)
    var x = (SCREEN_W - w) / 2, y = 20; // căn giữa hàng btnBack (y=12..60, pill cao 32)
    var g = frame('btnAddMusic', x, y, w, 32, { fill: '66171716', radius: 20 });
    add(f, g);
    var ic = icon('ic_music', 8, 8, 16, 16);
    if (ic) add(g, ic);
    add(g, text(hasSong ? 'Lofi Chill Beat' : 'Add song', 28, 0, {
      size: 14, font: 'main', color: C.white, w: hasSong ? 90 : 96, h: 32, valign: 'CENTER',
    }));
    if (hasSong) {
      add(g, rect('vVertical', w - 28, 4, 1, 24, { fill: C.white }));
      var close = icon('ic_close', w - 24, 8, 16, 16);
      if (close) add(g, close);
    }
    return g;
  }

  // ---- hàng chọn thời lượng quay (rcvTimeRecord, hardcode 15s/30s/1m, item0 chọn) ----
  function timeRecordRow(f, y) {
    var items = [{ t: '15s', sel: true }, { t: '30s', sel: false }, { t: '1m', sel: false }];
    var cx = SCREEN_W / 2, gap = 48, w0 = cx - gap;
    items.forEach(function (it, i) {
      var x = w0 + i * gap - 16;
      add(f, text(it.t, x, y, {
        size: 14, font: 'main', color: it.sel ? C.white : '99ffffff', w: 32, align: 'CENTER',
      }));
      if (it.sel) add(f, ellipse('imgDot', x + 13, y + 22, 6, 6, { fill: C.white }));
    });
  }

  // ---- màn nền chung: camera live (runtime) full-bleed ----
  // Camera trực tiếp + lớp AR: KHÔNG có asset tĩnh trong APK. Nền dùng ảnh MÔ PHỎNG sinh bởi
  // script/make-mock-ar.py (mặt tổng hợp, không phải ảnh chụp app/người thật), áp dụng cơ chế
  // đọc từ OverlayView.drawFacePuzzleComponent (cắt mặt 6 vùng). Chi tiết này nằm trong note
  // của từng screen() gọi hàm này (canvas giữ sạch, không in caption kỹ thuật lên hình).
  function cameraBg(f, mock) {
    // mock mới (make-mock-ar.py) đã đúng khung dọc 540x1200 = tỉ lệ 360x800 → FILL full-bleed
    // không méo, camera phủ trọn màn như ảnh app thật (không còn ô vuông giữa màn).
    add(f, img(mock || 'mock_ar_facepuzzle', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));
  }

  // ============================== 30a·30f — FragmentFacePuzzle =====================

  screen('30a · Face Puzzle · Idle (sẵn sàng quay)',
    'ĐƯỜNG BẤM UI: state hiện ra ngay khi vào màn (điều hướng từ Level Picker qua actionLevelPickerToFacePuzzle) — không phải lifecycle-only.' +
    ' | layout/fragment_face_puzzle.xml + FragmentFacePuzzle.initUi$1 (state mặc định, groupFunctions visible)' +
    ' | HIỂN THỊ: nền camera là ảnh MÔ PHỎNG (script/make-mock-ar.py, khoá mock_camera_face — mặt tổng hợp, ' +
    'không phải ảnh chụp app/camera thật), minh hoạ camera live-runtime chạy MediaPipe FaceLandmarker + hiệu ứng ghép mặt.',
    function (f) {
      cameraBg(f, 'mock_camera_face');
      var notifyX = (SCREEN_W - NOTIFY_W) / 2;
      add(f, img('img_notify_puzzle', notifyX, 200, NOTIFY_W, NOTIFY_H, 'FIT'));
      backButton(f, 'ic_back_2');
      musicPill(f, false);
      flipCameraButton(f);
      timeRecordRow(f, 662);
      recordingButton(f, 140, 696, {}); // progress=0 → không vẽ cung, chỉ icon play
      adSlot(f, 0, 544, SCREEN_W, 256, 'native_collapsible_detail (tự ẩn sau 2s)');
    });

  screen('30b · Face Puzzle · Đang quay',
    'ĐI TIẾP: dừng quay → actionToPreviewWithMusic → màn 51b (nút Next) → 54 → 60 Result (nút Save). Hai màn đó dùng chung với luồng Funny Puzzle nên nằm ở hàng dưới, không lặp lại ở hàng này. | ĐƯỜNG BẤM UI: tap btnRecording lúc đang idle → FragmentFacePuzzle.java:512 initListener$lambda$0$1 gọi thẳng RecordingManager.start(0,overlay).' +
    ' | RecordingManagerImpl.startRecordingInternal + FragmentFacePuzzle.onStartWaitingRecord (groupFunctions=gone, btnBack=INVISIBLE)' +
    ' | HIỂN THỊ: nền camera là ảnh MÔ PHỎNG (script/make-mock-ar.py, khoá mock_ar_facepuzzle — cơ chế đọc từ ' +
    'OverlayView.drawFacePuzzleComponent cắt mặt 6 vùng), minh hoạ camera live-runtime đang ghi hình, hiệu ứng ghép mặt chạy động.',
    function (f) {
      cameraBg(f);
      // btnBack ẩn (INVISIBLE, giữ chỗ) — không vẽ icon; groupFunctions (imvNotify/btnAddMusic/
      // btnFlipCamera/rcvTimeRecord) ẩn toàn bộ trong lúc quay.
      recordingButton(f, 140, 696, { icon: 'ic_pause_filter', arcSweepDeg: 144 }); // minh hoạ ~40% thời lượng
    });

  screen('30c · Face Puzzle · Tạm dừng',
    'LOẠI: state KHÔNG TỒN TẠI trong UI. pause() chỉ gọi từ Fragment.onPause() (lifecycle, app xuống nền) tại ' +
    'FragmentFacePuzzle.java:578-582, không nút nào kích hoạt. Nút dừng gọi stop() -> sang thẳng Result. Phát hiện ' +
    'khi user chơi app thật.' +
    ' | (nguồn code cũ, để tham khảo): RecordingManagerImpl.pause() + RecordingProgress.pauseRecord() (icon→play, cung đứng yên) — ' +
    'nhưng ngay cả khi pause() thật sự chạy (app bị đẩy xuống nền), người dùng KHÔNG NHÌN THẤY vì app không ở foreground.',
    function (f) {
      cameraBg(f);
      recordingButton(f, 140, 696, { icon: 'ic_play_filter', arcSweepDeg: 144 }); // cung giữ nguyên vị trí dừng
    }, { excluded: true });

  screen('30d · Face Puzzle · Đã chọn nhạc nền',
    'ĐƯỜNG BẤM UI: tap btnAddMusic → điều hướng Sound Picker (actionPlayFilterToSoundPicker) → chọn bài → quay lại, fragment result listener set currentSound.' +
    ' | FragmentFacePuzzle$observeCurrentSound$2 (btnRemoveSound/vVertical VISIBLE khi currentSound != null)' +
    ' | HIỂN THỊ: nền camera là ảnh MÔ PHỎNG (script/make-mock-ar.py, khoá mock_ar_facepuzzle), minh hoạ camera live-runtime.',
    function (f) {
      cameraBg(f);
      var notifyX = (SCREEN_W - NOTIFY_W) / 2;
      add(f, img('img_notify_puzzle', notifyX, 200, NOTIFY_W, NOTIFY_H, 'FIT'));
      backButton(f, 'ic_back_2');
      musicPill(f, true);
      flipCameraButton(f);
      timeRecordRow(f, 662);
      recordingButton(f, 140, 696, { icon: 'ic_play_filter' });
      adSlot(f, 0, 544, SCREEN_W, 256, 'native_collapsible_detail (tự ẩn sau 2s)');
    });

  screen('30e · Face Puzzle · Quay xong (interstitial trước khi sang Preview)',
    'ĐƯỜNG BẤM UI: tap btnRecording lần nữa khi đang quay (initListener$lambda$0$1, nhánh isRecording=true gọi .stop() trực tiếp) ' +
    'HOẶC để đồng hồ tự chạy hết (RecordingProgress.onFinish() tự gọi .stop() — FragmentFacePuzzle.java:561-563).' +
    ' | FragmentFacePuzzle$onStopRecording$1 — btnBack VISIBLE lại, loadShowFullscreenSafe(AdKey.INTER_RECORD) rồi navigate' +
    ' | HIỂN THỊ: nền camera là ảnh MÔ PHỎNG (script/make-mock-ar.py, khoá mock_ar_facepuzzle), minh hoạ khung hình video vừa ghi xong.',
    function (f) {
      cameraBg(f);
      backButton(f, 'ic_back_2'); // duy nhất được phục hồi, groupFunctions vẫn ẩn vĩnh viễn
      recordingButton(f, 140, 696, { icon: 'ic_pause_filter', arcSweepDeg: 359.99 }); // vòng đầy = quay xong
      adSlot(f, 0, 0, SCREEN_W, SCREEN_H, 'inter_record (interstitial, che toàn màn hình)');
    }, { adOnly: true }); // toàn màn bị ad interstitial che kín — tắt ad thì không còn gì để xem

  screen('30 · Face Puzzle · Chưa cấp quyền Camera/Micro',
    'SỐ THỨ TỰ: đánh 30 (trước 30a) vì đây là state ĐẦU TIÊN của màn quay — initUi$1 luôn gọi requireCameraPermission() ngay khi vào, chưa cấp quyền thì dialog OS hiện trước cả khi thấy camera. Bản trước đánh 30f nên nằm CUỐI cụm, đọc ngược luồng. Cụm Funny Puzzle vốn đã đúng (41a xin quyền → 41c live). | ĐƯỜNG BẤM UI: tự hiện khi vào màn lần đầu/chưa từng cấp quyền — initUi$1 luôn gọi requireCameraPermission()→launcher.launch(), ' +
    'nhưng OS chỉ THẬT SỰ vẽ dialog khi quyền CHƯA cấp (rất phổ biến ở lần mở đầu tiên); nếu đã cấp trước đó, launcher trả về ngay, không có dialog — bỏ qua state này.' +
    ' | FragmentFacePuzzle.requireCameraPermission() → OS permission dialog (chưa phản hồi); nếu từ chối → toast + popBackStack' +
    ' | HIỂN THỊ: dialog xin quyền là UI HỆ ĐIỀU HÀNH thật (Android 12+ Material You permission dialog), không phải màn ' +
    'do app tự thiết kế — dữ liệu thật: AndroidManifest <uses-permission CAMERA/RECORD_AUDIO>, FragmentFacePuzzle.CAMERA_PERMISSIONS=' +
    '"android.permission.CAMERA"+"android.permission.RECORD_AUDIO", app_name="Funny Face\\nMashup Challenge" (dialog này = quyền CAMERA, ' +
    'Android hỏi từng quyền một, chuỗi tiêu đề/nút là tiếng Anh vì là chuỗi hệ thống).',
    function (f) {
      // camera chưa khởi động được vì chưa có quyền — nền đen, không phải remoteTile "live"
      add(f, rect('camera-not-started', 0, 0, SCREEN_W, SCREEN_H, { fill: C.black }));
      var notifyX = (SCREEN_W - NOTIFY_W) / 2;
      add(f, img('img_notify_puzzle', notifyX, 200, NOTIFY_W, NOTIFY_H, 'FIT'));
      backButton(f, 'ic_back_2');
      musicPill(f, false);
      flipCameraButton(f);
      timeRecordRow(f, 662);
      recordingButton(f, 140, 696, {});
      // OS runtime-permission dialog thật (Android 12+ Material You), KHÔNG thuộc layout APK — xem note.
      var CARD_W = 312, CARD_H = 344;
      var cardX = (SCREEN_W - CARD_W) / 2, cardY = (SCREEN_H - CARD_H) / 2;
      add(f, rect('scrim', 0, 0, SCREEN_W, SCREEN_H, { fill: '000000', opacity: 0.4 }));
      var d = frame('OS permission dialog (Android 12+, CAMERA)', cardX, cardY, CARD_W, CARD_H, {
        fill: 'ffffff', radius: 28, shadow: 0.25,
      });
      add(f, d);
      // icon 24x24 căn giữa trên cùng — glyph camera Material chuẩn, #5f6368
      vpath(d, (CARD_W - 24) / 2, 24, 24, 24, '24 24',
        'M9 2 7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.657 0-3 1.343-3 3s1.343 3 3 3 3-1.343 3-3-1.343-3-3-3z',
        { fill: '5f6368', name: 'ic_camera (Material, OS chrome)' });
      // tiêu đề 20sp #1f1f1f, lineHeight 28, cách icon 16dp — chuỗi HỆ THỐNG (tiếng Anh), có "Funny Face"
      add(d, text('Allow Funny Face to take pictures and record video?', 24, 64, {
        size: 20, weight: 600, font: 'main', color: '1f1f1f', w: CARD_W - 48, h: 84,
        align: 'CENTER', lineHeight: 28,
      }));
      // 3 nút chữ xếp dọc, không nền, 14sp weight 600 (gần nhất với medium 500 trong bộ Lato có sẵn), #0b57d0
      var btnLabels = ['While using the app', 'Only this time', "Don't allow"];
      var btnY = 164, btnH = 52, btnGap = 4;
      btnLabels.forEach(function (label) {
        add(d, text(label, 16, btnY, {
          size: 14, weight: 600, font: 'main', color: '7f1aab', w: CARD_W - 32, h: btnH,
          align: 'CENTER', valign: 'CENTER',
        }));
        btnY += btnH + btnGap;
      });
    });

  // ============================== 31 / 31b — FragmentLevelPicker ====================

  screen('28 · Level Picker · Mặc định (level_picker_skipped=false → CÓ hiển thị)',
    'layout/fragment_level_picker.xml + FragmentPreviewTemplate.levelPicker() nhánh mặc định (RC level_picker_skipped=false)',
    function (f) {
      add(f, rect('bg', 0, 0, SCREEN_W, SCREEN_H, { fill: C.white }));
      var b = icon('ic_back_1', 20, 20, 32, 32); // BackImageButton1: box48 padding8
      if (b) add(f, b);
      add(f, text('Select level', 0, 12, {
        size: 20, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, h: 48,
        align: 'CENTER', valign: 'CENTER',
      }));
      var y = 84;
      add(f, img('bg_level_easy', 20, y, LV_W, LV_H, 'FIT')); y += LV_H + 16;
      add(f, img('bg_level_intermediate', 20, y, LV_W, LV_H, 'FIT')); y += LV_H + 16;
      add(f, img('bg_level_difficulty', 20, y, LV_W, LV_H, 'FIT')); y += LV_H + 16;
      adSlot(f, 20, y, LV_W, 100, 'native_level');
    });

  // AdKey.NATIVE_FS_LEVEL = "native_fullscreen_level" — tiền tố NATIVE_ (không phải INTER_) →
  // đây LÀ quảng cáo NATIVE app tự vẽ, KHÔNG phải interstitial SDK vẽ toàn quyền. Đã verify
  // qua code trước (không tin thẳng brief): FragmentLevelPicker dùng AdKey.NATIVE_FS_LEVEL —
  // cùng họ NATIVE_*/NATIVE_FS_* dùng layout thật res/layout/native_fake_full_inter.xml
  // (NativeAdView fill×fill) — đã đọc RAW XML trực tiếp (không qua resolve-layout.py) nên bắt
  // đủ 2 backgroundTint mà tool cũ bỏ sót: panel info background=bg_r8_f4f4f4_ads NHƯNG
  // backgroundTint=#33000000 → nền THẬT đen 20%; nút cta background=bg_white_r16_ads NHƯNG
  // backgroundTint=@color/gnt_blue=#ff4285f4 → nền THẬT xanh, không phải trắng. Badge "AD" nền
  // @color/gnt_red=#ffff0000 (bg_text_view_ads, radius10). KHÔNG có nút đóng/X trong layout thật
  // (khác khung SDK-chrome minh hoạ ở 41g/inter_record — đó là INTER_RECORD, thật sự không có
  // layout XML nên phải minh hoạ; ở đây có layout thật nên dựng đúng layout, không thêm chi tiết
  // không có trong XML).
  function nativeFakeFullInter(f, placementLabel) {
    var g = frame('NativeAdView (' + placementLabel + ') — layout/native_fake_full_inter.xml', 0, 0, SCREEN_W, SCREEN_H, {});
    add(f, g);
    // media_view: layout_width/height=0dp + constraint 4 cạnh parent → match_constraint = phủ hết
    // (nội dung là ad media nạp runtime bởi SDK mediation — xem note của 31b, canvas giữ sạch)
    add(g, rect('media_view', 0, 0, SCREEN_W, SCREEN_H, { fill: '242424', stroke: '3a3a3a', strokeW: 1 }));
    // panel info: fill_parent x wrap, margin L5 T50 R5, padding V15, bg=bg_r8_f4f4f4_ads + backgroundTint=#33000000
    var panelX = 5, panelY = 50, panelW = SCREEN_W - 10, panelH = 100;
    var panel = frame('background (info panel)', panelX, panelY, panelW, panelH, { fill: '33000000', radius: 8 });
    add(g, panel);
    // ad_notification_view: badge "AD" — bg_text_view_ads = solid gnt_red, radius=10dp, text 10sp trắng
    var badge = frame('ad_notification_view', 10, 15, 32, 20, { fill: 'ff0000', radius: 10 });
    add(panel, badge);
    add(badge, text('AD', 0, 0, { size: 10, weight: 700, font: 'main', color: C.white, w: 32, h: 20, align: 'CENTER', valign: 'CENTER' }));
    // primary: 16sp bold trắng, marginStart10 từ badge, căn giữa dọc theo badge (top/bottom constraint)
    add(panel, text('Ad headline', 52, 15, {
      size: 16, weight: 700, font: 'main', color: C.white, w: 245, h: 20, valign: 'CENTER',
    }));
    // body: 14sp trắng (gnt_white), 2 dòng, marginTop5 dưới primary, marginStart/End 10
    add(panel, text('Ad description text', 10, 40, {
      size: 14, font: 'main', color: C.white, w: panelW - 20, h: 36, lineHeight: 18,
    }));
    // cta: bg_white_r16_ads (radius16) NHƯNG backgroundTint=gnt_blue → nền xanh #4285f4, chữ trắng 20sp
    var ctaW = SCREEN_W * 0.95, ctaX = (SCREEN_W - ctaW) / 2, ctaY = SCREEN_H - 20 - 45;
    add(g, rect('cta', ctaX, ctaY, ctaW, 45, { fill: 'ae37e0', radius: 16 }));
    add(g, text('Install', ctaX, ctaY, {
      size: 20, weight: 700, font: 'main', color: C.white, w: ctaW, h: 45, align: 'CENTER', valign: 'CENTER',
    }));
    return g;
  }

  screen('31b · Level Picker · Chờ ad fullscreen sau khi bấm 1 level',
    'FragmentLevelPicker.initListener — setOnClickLoadShowAd(AdKey.NATIVE_FS_LEVEL="native_fullscreen_level", preload=true) trước khi supportNavigate(); ' +
    'NATIVE_ prefix (không phải INTER_) → dựng đúng geometry layout/native_fake_full_inter.xml (đã đọc raw XML, có backgroundTint panel #33000000 + cta #4285f4)' +
    ' | HIỂN THỊ: vùng media_view (nền tối phủ trọn khung) là ô giữ chỗ cho ảnh/video quảng cáo nạp runtime bởi ' +
    'SDK mediation, không có ảnh tĩnh trong APK; "Ad headline"/"Ad description text" là nội dung quảng cáo placeholder ' +
    'trung tính, không bịa tên thương hiệu quảng cáo nào; khung xung quanh (badge AD, panel, nút Install) đúng ' +
    'layout thật res/layout/native_fake_full_inter.xml.',
    function (f) {
      add(f, rect('bg', 0, 0, SCREEN_W, SCREEN_H, { fill: C.white }));
      var b = icon('ic_back_1', 20, 20, 32, 32);
      if (b) add(f, b);
      add(f, text('Select level', 0, 12, {
        size: 20, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, h: 48,
        align: 'CENTER', valign: 'CENTER',
      }));
      var y = 84;
      add(f, img('bg_level_easy', 20, y, LV_W, LV_H, 'FIT')); // nút vừa bấm — enabled=false (mờ đi)
      add(f, rect('disabled-overlay', 20, y, LV_W, LV_H, { fill: C.white, opacity: 0.5 }));
      y += LV_H + 16;
      add(f, img('bg_level_intermediate', 20, y, LV_W, LV_H, 'FIT')); y += LV_H + 16;
      add(f, img('bg_level_difficulty', 20, y, LV_W, LV_H, 'FIT')); y += LV_H + 16;
      adSlot(f, 20, y, LV_W, 100, 'native_level');
      nativeFakeFullInter(f, 'native_fullscreen_level');
    }, { adDup: true }); // bỏ ad thì trùng '28 · Level Picker · Mặc định' (chỉ khác disabled-overlay mờ trên nút Easy)
})();
