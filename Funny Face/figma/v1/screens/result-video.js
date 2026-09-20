// ============================================================================
// figma/v1/screens/result-video.js — cụm result-video (Kết quả · Phát video · Thư viện video)
// Nguồn số liệu: specs/result-video.md (đã 2 fix round, review clean).
// Numbering: 60 Result, 61 PlayVideo, 62 VideoGallery, 90 TabGallery (dead code). Dialog D6x.
// Quy ước toạ độ: mọi icon/text nhét vào 1 frame nút (btnBack/btnShare/btnDelete, 48×48,
// padding thật = size_8 theo style Base.PrimaryButton.Square) đều dùng TOẠ ĐỘ LOCAL (8,8,32,32)
// vì frame nút đã được đặt đúng vị trí tuyệt đối trên `f`.
// ============================================================================

// ---------------------------------------------------------------------------
// 60 · FragmentResult — state skeleton-ad (t=0)
// spec mục A/B · fragment_result.xml · FragmentResult$initUi$1.AnonymousClass1 (delay 2000ms)
// ---------------------------------------------------------------------------
screen('60 · Result · Skeleton ad (t=0)',
  'ĐẾN TỪ: màn 54 (Preview With Music sau khi mux xong) — chung cho cả luồng Face Puzzle lẫn Funny Puzzle. Nút Save ở màn này là bước cuối, sau đó về 62 VideoGallery. | fragment_result.xml + FragmentResult.java initUi()/initListener() — spec mục A/B/D. ' +
  'Trạng thái ngay khi vào màn: collapseHolderNative còn VISIBLE (chưa qua delay 2000ms). ' +
  '⚠ collapseHolderNative đè lên vùng dưới btnSave (cả 2 view neo bottom_toBottomOf=parent, xem spec mục M.2). ' +
  'HIỂN THỊ: khung video là ảnh MÔ PHỎNG mock_ar_ronaldo (assets/v1/50-mock-ar, script/make-mock-ar.py — mặt tổng hợp + ' +
  'overlay nhân vật thật trong APK), KHÔNG phải ảnh chụp app thật — nội dung thật (pathVideoResult) là video người dùng ' +
  'tự quay, chỉ có lúc chạy (Glide.load lấy frame đầu). Khối trắng dưới cùng là collapseHolderNative, hiện tới t=2000ms rồi GONE.',
  (f) => {
    add(f, img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));

    // btnBack — style BackImageButton1 (margin 12, padding 8) trên Base.PrimaryButton.Square 48×48, src=ic_home
    const btnBack = frame('btnBack', 12, 12, 48, 48, {});
    add(f, btnBack);
    add(btnBack, icon('ic_home', 8, 8, 32, 32));

    // appCompatTextView — "Result" ScreenTitleCommon: 20sp/bold(lato_bold_700)/text_primary_color, center theo btnBack
    add(f, text('Result', 0, 12, { size: 20, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, h: 48, align: 'CENTER', valign: 'CENTER' }));

    // btnShare — Base.PrimaryButton.Square 48×48, marginEnd=size_8, top/bottom=btnBack
    const btnShare = frame('btnShare', SCREEN_W - 8 - 48, 12, 48, 48, {});
    add(f, btnShare);
    add(btnShare, icon('ic_share', 8, 8, 32, 32));

    // imvThumbVideo — video kết quả, RUNTIME PLACEHOLDER (không lấy ảnh template thay thế)
    // top=btnBack.bottom+16=76, bottom=btnSave.top-16=710 → h=634 (ratio 1080:1920 gần khớp full width)
    // Ảnh mô phỏng mock_ar_ronaldo (assets/v1/50-mock-ar), cùng nội dung với PlayVideo/VideoGallery
    // (cùng là video vừa quay xong). Giữ nguyên box 0,76,360,634 + radius R.card.
    add(f, rect('imvThumbVideo', 0, 76, SCREEN_W, 634, { image: 'mock_ar_ronaldo', scaleMode: 'FILL', radius: R.card }));
    // skeleton state (t=0) — phủ lớp tối để gợi "video chưa sẵn sàng hiện native ad", cùng quy ước
    // buffering-dim-overlay của preview-sound.js
    add(f, rect('dim overlay (mô phỏng skeleton t=0)', 0, 76, SCREEN_W, 634, { fill: '000000', opacity: 0.35 }));
    // play icon overlay, 64×64 giữa thumbnail, tint primary_color
    add(f, icon('ic_play_music', (SCREEN_W - 64) / 2, 76 + (634 - 64) / 2, 64, 64));

    // btnSave — LinearLayout, margin 16 mọi cạnh, h=58, bg bg_primary_rounded (solid primary_color), bottom=parent
    const saveY = SCREEN_H - 16 - 58; // = 726
    const btnSave = frame('btnSave', 16, saveY, SCREEN_W - 32, 58, { fill: C.primary, radius: 48 });
    add(f, btnSave);
    // icon ic_record + text "Save" — LinearLayout gravity=center, toạ độ LOCAL trong btnSave (328×58).
    // kích thước icon wrap_content, ước lượng 20×20 (không có dimen tường minh trong XML).
    add(btnSave, icon('ic_record', 130, 19, 20, 20));
    // màu chữ "Save": ColorStateList button_primary_text_color, state enabled (mặc định, không có code disable) → text_primary_color #171716
    add(btnSave, text('Save', 158, 0, { size: 16, weight: 700, font: 'main', color: C.textHi, w: 140, h: 58, align: 'LEFT', valign: 'CENTER' }));

    // nativeCollapsibleContainer + collapseHolderNative — CỜ spec M.2: cả 2 view neo bottom_toBottomOf=parent,
    // XML khai container SAU btnSave → đè lên phần dưới của Save button khi hiện (z-order thật, không phải lỗi dựng).
    const adY = SCREEN_H - 256; // ad_native_collapsed_height = size_256 = 256dp
    const skeleton = frame('collapseHolderNative (skeleton, bg_ad_native_media_white)', 0, adY, SCREEN_W, 256, { fill: C.white });
    add(f, skeleton);
    add(skeleton, rect('divider #ffe4e3e2', 0, 0, SCREEN_W, 1, { fill: 'ffe4e3e2' }));
  }, { adDup: true }); // SHOW_ADS=false → trùng '60 · Result' (đã bỏ dim/skeleton bên dưới), bỏ khỏi registry. Build/note giữ nguyên 100% cho bản đầy đủ (SHOW_ADS=true).

// ---------------------------------------------------------------------------
// 60b · FragmentResult — state ad hiện (t>=2s)
// ---------------------------------------------------------------------------
screen('60 · Result',
  'fragment_result.xml + FragmentResult$initUi$1.AnonymousClass1 (ViewExtKt.gone(collapseHolderNative) sau delay 2000ms) ' +
  '+ loadAndShowAds()/loadAndShowNativeCollapsibleSafe (AdKey.NATIVE_CLS_RESULT) — spec mục A/B/K. ' +
  'Chiều cao slot ad thật (native template) không cố định trong XML (wrap_content) — dùng lại 256dp (ad_native_collapsed_height) làm ước lượng slot, ghi rõ là giả định. ' +
  '⚠ nativeCollapsibleContainer đè lên vùng dưới btnSave nếu ad hiện đủ cao (cả 2 view neo bottom_toBottomOf=parent, xem spec mục M.2). Nếu load fail → container ẩn hẳn (GONE), Save lộ hết. ' +
  'HIỂN THỊ: khung video là ảnh MÔ PHỎNG mock_ar_ronaldo (assets/v1/50-mock-ar, script/make-mock-ar.py — mặt tổng hợp + ' +
  'overlay nhân vật thật trong APK), KHÔNG phải ảnh chụp app thật — nội dung thật (pathVideoResult) là video người dùng ' +
  'tự quay, chỉ có lúc chạy (Glide.load lấy frame đầu).',
  (f) => {
    add(f, img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));

    const btnBack = frame('btnBack', 12, 12, 48, 48, {});
    add(f, btnBack);
    add(btnBack, icon('ic_home', 8, 8, 32, 32));

    add(f, text('Result', 0, 12, { size: 20, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, h: 48, align: 'CENTER', valign: 'CENTER' }));

    const btnShare = frame('btnShare', SCREEN_W - 8 - 48, 12, 48, 48, {});
    add(f, btnShare);
    add(btnShare, icon('ic_share', 8, 8, 32, 32));

    // imvThumbVideo — ảnh mô phỏng mock_ar_ronaldo, cùng nội dung với PlayVideo/VideoGallery (cùng
    // video vừa quay xong). Không phủ dim (ad đã hiện xong ở t≥2s, video được xem là sẵn sàng).
    add(f, rect('imvThumbVideo', 0, 76, SCREEN_W, 634, { image: 'mock_ar_ronaldo', scaleMode: 'FILL', radius: R.card }));
    add(f, icon('ic_play_music', (SCREEN_W - 64) / 2, 76 + (634 - 64) / 2, 64, 64));

    const saveY = SCREEN_H - 16 - 58;
    const btnSave = frame('btnSave', 16, saveY, SCREEN_W - 32, 58, { fill: C.primary, radius: 48 });
    add(f, btnSave);
    add(btnSave, icon('ic_record', 130, 19, 20, 20));
    add(btnSave, text('Save', 158, 0, { size: 16, weight: 700, font: 'main', color: C.textHi, w: 140, h: 58, align: 'LEFT', valign: 'CENTER' }));

    // collapseHolderNative đã GONE — nativeCollapsibleContainer hiện native ad thật (AD SLOT).
    // Bọc if(SHOW_ADS) vì phần vẽ tay (red warning) KHÔNG qua adSlot() nên không tự tắt —
    // adSlot() trả null khi SHOW_ADS=false, add(null,...) sẽ lỗi nếu không bọc.
    if (SHOW_ADS) {
      const adY = SCREEN_H - 256;
      adSlot(f, 0, adY, SCREEN_W, 256, 'native_collapsible_result · NativeCollapsibleTemplate style7 (NativeManager.presentCollapsible)');
    }
  });

// ---------------------------------------------------------------------------
// D60 · Result · AD inter_save (interstitial, transient khi bấm Save)
// D61 · Result · AD native_fullscreen_save (native full-screen, transient khi back/đóng)
// spec mục D.1/D.3/K — cả 2 ad này KHÔNG nằm trong fragment_result.xml, là overlay SDK toàn màn
// chèn vào flow trước khi thực hiện hành động, nên dựng riêng ở trang Dialogs & States.
// ---------------------------------------------------------------------------
dialog('D60 · Result · AD inter_save (tap Save)',
  'FragmentResult$initListener$1$4$1 → FullscreenManager.present(activity, AdKey.INTER_SAVE, false, ...) — spec mục D.3/K. ' +
  'Creative ad do SDK render toàn màn, app không có UI riêng để dựng ngoài điểm trigger. ' +
  'HIỂN THỊ: nền phía sau card interstitial là ảnh MÔ PHỎNG mock_ar_ronaldo (assets/v1/50-mock-ar) minh hoạ màn Result ' +
  'vừa quay xong phía sau (video vừa quay — runtime, không có trong APK).',
  (f) => {
    // Interstitial của mediation SDK — KHÔNG có layout trong APK (không phải native_fake_full_inter.xml,
    // đó là format "native full-screen" riêng dùng cho D61 — AdKey.INTER_SAVE có tiền tố INTER_ giống
    // INTER_SPLASH/INTER_RECORD, tức interstitial thật do SDK vẽ 100% lúc runtime).
    // Dựng theo ĐÚNG khung mà cụm funny-puzzle đã dùng cho 41g (cùng hoàn cảnh AdKey INTER_*) để 4 frame
    // interstitial toàn màn của file cùng một hệ: nền = khung hình màn Result phía sau (mock_ar_ronaldo)
    // + scrim + card interstitial tối giản (nút đóng, badge "Ad", vùng media, CTA "Install").
    add(f, img('mock_ar_ronaldo', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));

    // scrim — ad sắp phủ kín lên trên toàn màn
    add(f, rect('scrim', 0, 0, SCREEN_W, SCREEN_H, { fill: '000000', opacity: 0.55 }));

    // khung interstitial của SDK mediation — KHÔNG có layout trong APK, chỉ là minh hoạ chrome
    // phổ biến (nút đóng, badge "Ad", vùng media, nút CTA)
    const card = frame('SDK Interstitial (inter_save) — UI của SDK, không có layout trong APK', 0, 0, SCREEN_W, SCREEN_H, {
      fill: '141414',
    });
    add(f, card);
    const closeBtn = ellipse('close (SDK chrome)', SCREEN_W - 44, 20, 24, 24, { stroke: 'ffffff', strokeW: 1.5 });
    add(card, closeBtn);
    vpath(card, SCREEN_W - 44 + 6, 20 + 6, 12, 12, '24 24', 'M4 4 L20 20 M20 4 L4 20', { stroke: 'ffffff', sw: 2, name: 'x (SDK chrome)' });
    add(card, text('Ad', 16, 18, { size: 11, font: 'main', color: 'ffffffb3', w: 40, h: 20 }));
    remoteTile(card, 16, 56, SCREEN_W - 32, 656, 'ad media — runtime (SDK mediation)', 12);
    add(card, rect('cta (SDK chrome)', 16, SCREEN_H - 76, SCREEN_W - 32, 48, { fill: '2f6bff', radius: 24 }));
    add(card, text('Install', 16, SCREEN_H - 76, {
      size: 15, weight: 700, font: 'main', color: C.white, w: SCREEN_W - 32, h: 48, align: 'CENTER', valign: 'CENTER',
    }));
    add(card, text('UI của SDK quảng cáo — không có layout trong APK', 16, SCREEN_H - 22, {
      size: 9, font: 'main', color: 'ffffff80', w: SCREEN_W - 32, align: 'CENTER',
    }));
  }, { adOnly: true });

dialog('D61 · Result · AD native_fullscreen_save (back/đóng)',
  'FragmentResult$handleCloseScreen$1 → LifeCycleExtKt.loadShowFullscreenSafe(this, AdKey.NATIVE_FULL_SAVE, ...) — spec mục D.1/K. ' +
  'Hiện trước khi xoá thư mục tạm pathVideoResult và popBackStack().',
  (f) => {
    // native_fake_full_inter.xml (Google Native Templates/GNT) — geometry THẬT đọc từ res/layout, không phải mô tả gián tiếp:
    // media_view 0x0 fill parent · info-block ConstraintLayout bg=bg_r8_f4f4f4_ads NHƯNG backgroundTint=#33000000
    //   (→ nền thật là đen 20% opacity, không phải xám f4f4f4) margin L5 T50 R5, padding T/B 15dp
    //   ad_notification_view "AD" 10sp trắng bg=bg_text_view_ads(gnt_red #ffff0000, radius10) marginStart10, cùng hàng với primary
    //   primary 16sp bold trắng maxLines1 width~70%(≈245dp) start_toEndOf badge, marginStart10
    //   body 14sp gnt_white maxLines2 marginTop5 full width (margin L10R10)
    // cta AppCompatButton h=45dp bg=bg_white_r16_ads NHƯNG backgroundTint=gnt_blue(#ff4285f4 → nền thật là XANH, không phải trắng)
    //   width_percent 0.95(≈340dp từ margin L10R10) — bottom_toBottomOf=parent marginBottom=20 (marginTop=20 khai nhưng KHÔNG có top-constraint nên vô tác dụng)
    remoteTile(f, 0, 0, SCREEN_W, SCREEN_H, 'media_view · ad creative (runtime, Google NativeAdView MediaView)', 0);

    const infoX = 5, infoY = 50, infoW = SCREEN_W - 10;
    const info = frame('info-block (bg_r8_f4f4f4_ads + backgroundTint=#33000000 → đen 20%)', infoX, infoY, infoW, 99, { fill: '000000', opacity: 0.2, radius: 8 });
    add(f, info);
    // toạ độ dưới đây LOCAL trong info-block
    add(info, rect('ad_notification_view bg (bg_text_view_ads=gnt_red #ffff0000, r10)', 10, 15, 34, 16, { fill: 'ff0000', radius: 10 }));
    add(info, text('AD', 10, 15, { size: 10, font: 'main', color: C.white, w: 34, h: 16, align: 'CENTER', valign: 'CENTER' }));
    add(info, text('Ad headline', 54, 15, { size: 16, weight: 700, font: 'main', color: C.white, w: 245, align: 'LEFT' }));
    add(info, text('Ad description text — nội dung quảng cáo runtime, không bịa thương hiệu', 10, 48, { size: 14, font: 'main', color: 'ffffff', w: infoW - 20, align: 'LEFT' }));

    // cta — LOCAL trong f (constraint tới `background` toàn màn, không phải info-block)
    const ctaY = SCREEN_H - 20 - 45;
    add(f, rect('cta bg (bg_white_r16_ads + backgroundTint=gnt_blue #ff4285f4)', 10, ctaY, SCREEN_W - 20, 45, { fill: '4285f4', radius: 16 }));
    add(f, text('Install', 10, ctaY, { size: 20, font: 'main', color: C.white, w: SCREEN_W - 20, h: 45, align: 'CENTER', valign: 'CENTER' }));
  }, { adOnly: true });

// ---------------------------------------------------------------------------
// 61 · FragmentPlayVideo — canDelete=true (mở từ Gallery/TabGallery)
// spec mục E/F/G · fragment_play_video.xml
// ---------------------------------------------------------------------------
screen('61 · PlayVideo · canDelete=true',
  'fragment_play_video.xml + FragmentPlayVideo.initUi() (btnDelete.setVisibility(args.canDelete?VISIBLE:GONE)) — spec mục E/F. ' +
  'Vào từ actionGalleryToPlayVideo / FragmentHomeDirections.actionToPlayVideo (canDelete=true). ' +
  'HIỂN THỊ: khung video là ảnh MÔ PHỎNG mock_ar_ronaldo (assets/v1/50-mock-ar), KHÔNG phải ảnh chụp app thật — nội dung ' +
  'thật (exoPlayerView) là video người dùng tự quay đang phát, chỉ có lúc chạy; ExoPlayer default controls không vẽ.',
  (f) => {
    // exoPlayerView — full-bleed. Cùng nội dung với 61b/Result/VideoGallery (cùng 1 video vừa quay
    // xong đang được xem/phát lại) → dùng mock_ar_ronaldo, giữ nguyên bounding box 0,0,360,800.
    add(f, rect('exoPlayerView bg', 0, 0, SCREEN_W, SCREEN_H, { fill: '000000' }));
    add(f, img('mock_ar_ronaldo', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));

    const btnBack = frame('btnBack', 12, 12, 48, 48, {});
    add(f, btnBack);
    add(btnBack, icon('ic_back_1', 8, 8, 32, 32)); // tint=white theo XML, icon() không hỗ trợ tint runtime

    add(f, text('Preview', 0, 12, { size: 20, weight: 700, font: 'main', color: C.white, w: SCREEN_W, h: 48, align: 'CENTER', valign: 'CENTER' }));

    // endSpace 8dp ở end parent (không vẽ, chỉ là spacer) → btnDelete end_toStartOf endSpace
    const btnDeleteX = SCREEN_W - 8 - 48; // = 304
    const btnDelete = frame('btnDelete', btnDeleteX, 12, 48, 48, {});
    add(f, btnDelete);
    add(btnDelete, icon('ic_delete', 8, 8, 32, 32));

    // btnShare end_toStartOf btnDelete
    const btnShareX = btnDeleteX - 48; // = 256
    const btnShare = frame('btnShare', btnShareX, 12, 48, 48, {});
    add(f, btnShare);
    add(btnShare, icon('ic_share', 8, 8, 32, 32)); // tint=white theo XML
  });

// ---------------------------------------------------------------------------
// 61b · FragmentPlayVideo — canDelete=false (mở từ Result, xem trước khi Save)
// ---------------------------------------------------------------------------
screen('61b · PlayVideo · canDelete=false',
  'fragment_play_video.xml + FragmentPlayVideo.initUi() — spec mục E/F. ' +
  'Vào từ FragmentResult.actionResultToPlayVideo(pathVideoResult, false). btnDelete GONE → btnShare chiếm chỗ (end_toStartOf btnDelete co về vị trí btnDelete cũ). ' +
  'HIỂN THỊ: khung video là ảnh MÔ PHỎNG mock_ar_ronaldo (assets/v1/50-mock-ar), KHÔNG phải ảnh chụp app thật — nội dung ' +
  'thật (exoPlayerView) là video người dùng tự quay đang phát, chỉ có lúc chạy; ExoPlayer default controls không vẽ.',
  (f) => {
    // exoPlayerView — full-bleed. Ảnh mô phỏng mock_ar_ronaldo (assets/v1/50-mock-ar) thay cho ô đen trơn,
    // gắn nhãn theo đúng quy ước face-puzzle.js/funny-puzzle.js. Bounding box giữ nguyên 0,0,360,800.
    add(f, rect('exoPlayerView bg', 0, 0, SCREEN_W, SCREEN_H, { fill: '000000' }));
    add(f, img('mock_ar_ronaldo', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));

    const btnBack = frame('btnBack', 12, 12, 48, 48, {});
    add(f, btnBack);
    add(btnBack, icon('ic_back_1', 8, 8, 32, 32));

    add(f, text('Preview', 0, 12, { size: 20, weight: 700, font: 'main', color: C.white, w: SCREEN_W, h: 48, align: 'CENTER', valign: 'CENTER' }));

    // btnDelete GONE (canDelete=false) — không vẽ. btnShare dịch sang vị trí btnDelete cũ (end_toStartOf endSpace collapse về đó)
    const btnShareX = SCREEN_W - 8 - 48; // = 304, thay vì 256 như state canDelete=true
    const btnShare = frame('btnShare', btnShareX, 12, 48, 48, {});
    add(f, btnShare);
    add(btnShare, icon('ic_share', 8, 8, 32, 32));
  });

// ---------------------------------------------------------------------------
// D62 · Popup xác nhận xoá video — popup_exit_confirm.xml biến thể "Delete video?"
// (biến thể "Go back?" thuộc cụm preview-sound — KHÔNG dựng lại ở đây)
// Trigger: FragmentPlayVideo.initListener() → PopupUtilsKt.showPopupConfirmDelete()
// ---------------------------------------------------------------------------
dialog('D62 · PlayVideo · Popup xoá video (Delete video?)',
  'popup_exit_confirm.xml (biến thể delete) + PopupUtilsKt.showPopupConfirmDelete() — spec mục G.3/J. ' +
  'Width = screenWidth*0.85 = 306dp, height wrap_content (ước lượng 164dp từ padding/margin thật, không có số tường minh cho text 2 dòng). ' +
  'Radius thật của bg_solid_rounded_12 = size_12 = 12dp (không dùng R.dialog=16 mặc định). ' +
  'HIỂN THỊ: khung video nền là ảnh MÔ PHỎNG mock_ar_ronaldo (assets/v1/50-mock-ar), KHÔNG phải ảnh chụp app thật — nội ' +
  'dung thật (exoPlayerView) là video người dùng tự quay, chỉ có lúc chạy; ExoPlayer default controls không vẽ.',
  (f) => {
    // Chrome màn nền FragmentPlayVideo (canDelete=true) — dialog này bật ra từ nút xoá ở màn đó.
    // Tái dùng đúng số liệu đã dựng ở frame 61 (screen '61 · PlayVideo · canDelete=true').
    add(f, rect('exoPlayerView bg', 0, 0, SCREEN_W, SCREEN_H, { fill: '000000' }));
    add(f, img('mock_ar_ronaldo', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));
    const bgBtnBack = frame('btnBack', 12, 12, 48, 48, {});
    add(f, bgBtnBack);
    add(bgBtnBack, icon('ic_back_1', 8, 8, 32, 32));
    add(f, text('Preview', 0, 12, { size: 20, weight: 700, font: 'main', color: C.white, w: SCREEN_W, h: 48, align: 'CENTER', valign: 'CENTER' }));
    const bgBtnDeleteX = SCREEN_W - 8 - 48; // = 304
    const bgBtnDelete = frame('btnDelete', bgBtnDeleteX, 12, 48, 48, {});
    add(f, bgBtnDelete);
    add(bgBtnDelete, icon('ic_delete', 8, 8, 32, 32));
    const bgBtnShareX = bgBtnDeleteX - 48; // = 256
    const bgBtnShare = frame('btnShare', bgBtnShareX, 12, 48, 48, {});
    add(f, bgBtnShare);
    add(bgBtnShare, icon('ic_share', 8, 8, 32, 32));

    const card = dcard(f, 306, 164, { fill: C.white, radius: 12, name: 'popup_exit_confirm · Delete video', scrim: 0.6 });
    // toạ độ dưới đây LOCAL trong card (306×164). padding 16 quanh card (android:padding=size_16).
    // tvHeader "Delete video" — ScreenTitleCommon
    add(card, text('Delete video', 0, 16, { size: 20, weight: 700, font: 'main', color: C.textHi, w: 306, align: 'CENTER' }));
    // tvContent — marginTop 8 từ header, marginHorizontal 8 (thêm, trong padding 16 đã có) → x=24,w=258
    add(card, text('Are you sure you want to delete this video?', 24, 48, { size: 14, font: 'main', color: C.textHi, w: 258, align: 'CENTER' }));
    // hàng nút — marginTop 16 từ tvContent, height ước lượng 44 (paddingVertical 12 + 1 dòng 14sp bold)
    const btnY = 104, btnH = 44, gap = 16;
    const btnW = (306 - 32 - gap) / 2; // = 129, trong vùng padding 16 mỗi bên
    // btnCancel — bg color_E6E6E5, radius 69 (bg_white_corner_69), text "Cancel" (không có color override → mặc định textHi)
    add(card, rect('btnCancel bg', 16, btnY, btnW, btnH, { fill: C.e6e6e5, radius: R.r69 }));
    add(card, text('Cancel', 16, btnY, { size: 14, weight: 700, font: 'main', color: C.textHi, w: btnW, h: btnH, align: 'CENTER', valign: 'CENTER' }));
    // btnDelete — bg color_FF4342(=C.red), text trắng "Delete"
    const btnDeleteX = 16 + btnW + gap;
    add(card, rect('btnDelete bg', btnDeleteX, btnY, btnW, btnH, { fill: C.red, radius: R.r69 }));
    add(card, text('Delete', btnDeleteX, btnY, { size: 14, weight: 700, font: 'main', color: C.white, w: btnW, h: btnH, align: 'CENTER', valign: 'CENTER' }));
  });

// ---------------------------------------------------------------------------
// 62 · FragmentVideoGallery — state RỖNG (empty)
// spec mục H · fragment_video_gallery.xml
// ---------------------------------------------------------------------------
screen('62 · VideoGallery · Rỗng (empty)',
  'fragment_video_gallery.xml + AdapterMyVideo.Listener.onIsEmpty(true) → groupEmpty VISIBLE — spec mục H. ' +
  'btnCreate ("Create Now") mặc định android:visibility="invisible" và KHÔNG có code nào set lại trong FragmentVideoGallery.java (cờ M.1, dead-state) ' +
  '→ dựng theo KẾT QUẢ THẬT: không vẽ nút này.',
  (f) => {
    add(f, img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));

    const btnBack = frame('btnBack', 12, 12, 48, 48, {});
    add(f, btnBack);
    add(btnBack, icon('ic_back_1', 8, 8, 32, 32));

    // appCompatTextView2 có android:elevation=10dp trong XML — thêm drop-shadow nhẹ cho đúng chrome thật
    const title = text('My library', 0, 12, { size: 20, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, h: 48, align: 'CENTER', valign: 'CENTER' });
    title.effects = [{ type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: 0.25 }, offset: { x: 0, y: 3 }, radius: 6, spread: 0, visible: true, blendMode: 'NORMAL' }];
    add(f, title);

    // groupEmpty: imvEmpty (ratio1:1, width%=0.5 → 180×180) + tvEmptyNotify, mốc lineCenterY = 50% màn = y400
    add(f, icon('ic_empty', (SCREEN_W - 180) / 2, 220, 180, 180));
    add(f, text('No videos yet! Try a fun filter and \n start recording!', 20, 400, { size: 14, font: 'main', color: C.textHi, w: 320, align: 'CENTER' }));

    // rvContent trống (0 item) — không vẽ gì thêm dưới groupEmpty (rỗng đúng bản chất state này, không nhét item)
    // btnCreate: KHÔNG vẽ — xem note ở trên (cờ M.1, dead-state theo code)
  });

// ---------------------------------------------------------------------------
// 62b · FragmentVideoGallery — state CÓ N item (N=7, minh hoạ runtime)
// ---------------------------------------------------------------------------
screen('62b · VideoGallery · Có N item (N=7, minh hoạ runtime)',
  'fragment_video_gallery.xml + AdapterMyVideo (item_my_video.xml, GridLayoutManager spanCount=2) — spec mục H. ' +
  'N=7 CHỈ LÀ MINH HOẠ (số lượng thật do người dùng quyết định, nguồn = quét Downloads/CemFacePuzzle/*.mp4). ' +
  'item 164×253.3dp (cột 180dp trừ margin 8dp mỗi bên, ratio ảnh 158:244), bo góc 16dp (R.tile, code setRadiusPx size_16). ' +
  'Không có state loading/lỗi trong code (Flow không emit riêng) — không dựng thêm 2 state đó ở đây (xem spec mục H/M.3). ' +
  'HIỂN THỊ: cả 7 thumbnail là ảnh MÔ PHỎNG mock_ar_ronaldo (assets/v1/50-mock-ar), KHÔNG dùng thumbnail CDN template — ' +
  'nội dung thật (item_my_video.xml imvThumbVideo, Glide loadThumbnailFromVideoWithCache) là video người dùng tự quay, ' +
  'chỉ có lúc chạy. Số lượng 7 chỉ là minh hoạ, số thật phụ thuộc thư mục Downloads/CemFacePuzzle.',
  (f) => {
    // groupEmpty GONE — grid 2 cột, item width=164, height=164*244/158≈253.3, row pitch=269.3 (8+253.3+8)
    const itemW = 164, itemH = (164 * 244) / 158, rowPitch = itemH + 16;
    const colX = [8, 180 + 8];
    const gridTop = 60 + 8; // rvContent.top(60) + margin trên của item(8)
    const N = 7;
    // Tính chiều cao nội dung TRƯỚC (dòng cuối lệch trái, 4 hàng cho N=7) rồi mới vẽ nền window_bg
    // đúng chiều cao đó — window_bg vẽ cứng SCREEN_H=800 trước đây làm 369dp cuối lưới lộ nền canvas.
    const rows = Math.ceil(N / 2);
    const maxY = gridTop + (rows - 1) * rowPitch + itemH;
    const contentH = maxY + 40; // + khoảng chừa cho caption bên dưới (giữ nguyên hệ số cũ)

    // window_bg là ảnh hoạ tiết — FILL (không FIT) để lặp/phủ đẹp khi kéo cao hơn 800dp
    add(f, img('window_bg', 0, 0, SCREEN_W, contentH, 'FILL'));

    const btnBack = frame('btnBack', 12, 12, 48, 48, {});
    add(f, btnBack);
    add(btnBack, icon('ic_back_1', 8, 8, 32, 32));

    add(f, text('My library', 0, 12, { size: 20, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, h: 48, align: 'CENTER', valign: 'CENTER' }));

    for (let i = 0; i < N; i++) {
      const row = Math.floor(i / 2), col = i % 2;
      const x = colX[col], y = gridTop + row * rowPitch;
      // thumbnail — ảnh mô phỏng mock_ar_ronaldo (assets/v1/50-mock-ar), KHÔNG dùng thumbnail CDN template.
      // Box/bo góc giữ nguyên như cũ (itemW×itemH, radius R.tile). Nhãn "MÔ PHỎNG" đã chuyển vào note.
      add(f, rect('video ' + (i + 1) + ' thumb', x, y, itemW, itemH, { image: 'mock_ar_ronaldo', scaleMode: 'FILL', radius: R.tile }));
    }
    grow(f, contentH); // list dài hơn 800dp → nới khung (rule 5), khớp đúng chiều cao nền window_bg
  });

// ---------------------------------------------------------------------------
// 90 · FragmentTabGallery — DEAD CODE, không có đường điều hướng tới (spec mục I)
// ---------------------------------------------------------------------------
screen('90 · TabGallery · DEAD CODE (unreachable)',
  'fragment_tab_gallery.xml + FragmentTabGallery.java — spec mục I. ' +
  'KHÔNG có nav destination trong main_nav.xml, KHÔNG có ViewPager/BottomNav nào add nó, newInstance() không ai gọi ' +
  '(chỉ Hilt auto-gen tham chiếu tới). Dựng 1 frame đại diện (biến thể empty-state, khác biệt rõ nhất so với 62: ' +
  'btnBack invisible, rvContent paddingBottom=100dp cho bottom-nav, tvEmptyNotify bold/wrap_content). ' +
  '⚠ DEAD CODE — không có đường điều hướng tới màn này (xem spec mục I). ' +
  'LOẠI KHỎI BẢN TRÌNH BÀY theo yêu cầu design lead. Vẫn là dead code có thật ' +
  '(0 hit trong main_nav.xml, chỉ Hilt generated DI tham chiếu) — bỏ { excluded: true } là frame quay lại.',
  (f) => {
    add(f, img('window_bg', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));

    // btnBack: android:visibility="invisible" trong XML → không vẽ icon, chỉ giữ chỗ (chiếm layout nhưng không hiện)
    // appCompatTextView2 có android:elevation=10dp trong XML (giống 62) — thêm drop-shadow nhẹ
    const title = text('My library', 0, 12, { size: 20, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, h: 48, align: 'CENTER', valign: 'CENTER' });
    title.effects = [{ type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: 0.25 }, offset: { x: 0, y: 3 }, radius: 6, spread: 0, visible: true, blendMode: 'NORMAL' }];
    add(f, title);

    // groupEmpty variant riêng của tab: tvEmptyNotify wrap_content, size16, bold (khác 62 dùng fill_parent/không bold)
    add(f, icon('ic_empty', (SCREEN_W - 180) / 2, 220, 180, 180));
    add(f, text('No videos yet! Try a fun filter and \n start recording!', 0, 400, { size: 16, weight: 700, font: 'main', color: C.textHi, w: SCREEN_W, align: 'CENTER' }));

    // rvContent paddingBottom=main_menu_height_offset=100dp — không có nội dung để vẽ trong state trống, ghi chú vùng chừa chỗ bottom-nav
    add(f, rect('rvContent paddingBottom=100dp (chừa chỗ bottom-nav Home)', 0, SCREEN_H - 100, SCREEN_W, 1, { fill: C.gray, opacity: 0.4 }));
  }, { excluded: true });
