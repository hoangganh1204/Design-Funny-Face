// ============================================================================
//  Cụm: funny-puzzle — FragmentListFunnyPuzzle (40) + FragmentFunnyPuzzle (41a..41h)
//  Nguồn số liệu: specs/funny-puzzle.md (đã review pass — "không ô ad trong list" xác nhận đúng)
//  XML: fragment_list_funny_puzzle.xml, item_funny_puzzle.xml, item_funny_puzzle_ad.xml,
//       fragment_funny_puzzle.xml, item_time_record.xml
//  Code: FragmentListFunnyPuzzle.java, AdapterFunnyPuzzleTemplate.java, FunnyPuzzleItem.java,
//        FragmentFunnyPuzzle.java, RecordingProgress.java, OverlayView.java, AdapterTimeRecord.java
// ============================================================================

// --- D. Data hardcode — nguồn: assets/face_funny/data_funny.json (16/20 entry gốc) + 2 đề xuất.
//     id 16 Messi / 17 Ronaldo / 18 Neymar Jr / 9 Bruno Mars đã BỎ khỏi bản thiết kế theo yêu cầu.
//     ⚠ THỨ TỰ HIỂN THỊ DƯỚI ĐÂY LÀ THỨ TỰ THIẾT KẾ do design lead chỉ định — KHÔNG còn
//     trùng thứ tự trong data_funny.json. Trường id vẫn giữ nguyên id gốc của APK để truy
//     ngược được. Muốn app khớp bản thiết kế, dev phải sắp lại data_funny.json theo dãy id:
//     2, 4, 3, 1, 6, 7, 5, 21, 8, 10, 15, 12, 13, 14, 11, 20, 19, 22
// name = hiển thị (tvName) ; image = khoá ảnh origin (Glide originImagePath dùng field "image")
const FNP_LIST_DATA_V1 = [
  { id: 2,  name: 'Leonel Messi',      image: 'Leonel_Messi'       },
  { id: 4,  name: 'Cristiano Ronaldo', image: 'Cristiano_Ronaldo'  },
  { id: 3,  name: 'Erling Haaland',    image: 'Erling_Haaland'     },
  { id: 1,  name: 'Kylian Mbappe',     image: 'Kylian_Mbappe'      },
  // id=6: ẢNH đã thay bằng Lamine Yamal theo yêu cầu, nên NHÃN phải đổi theo, nếu không
  // bảng thiết kế sẽ hiện ảnh Yamal dưới chữ 'Messi' và trông như lỗi. Lưu ý: file dữ
  // liệu của app (assets/face_funny/data_funny.json) VẪN ghi 'Messi' — muốn khớp thật
  // thì phía dev phải sửa entry id=6 trong file đó.
  { id: 6,  name: 'Lamine Yamal',      image: 'messi'              },
  { id: 7,  name: 'Vinicius Junior',   image: 'Vinicius_Junior'    },
  { id: 5,  name: 'Jude Bellingham',   image: 'Jude_Bellingham'    },
  { id: 21, name: 'Pedri',             image: 'Pedri'              },   // THÊM MỚI, không có trong data_funny.json
  { id: 8,  name: 'Neymar Junior',     image: 'Neymar_Junior'      },
  { id: 10, name: 'Donald Trump',      image: 'Donald_Trump'       },
  { id: 15, name: 'Mr.Bean',           image: 'Mr_Bean'            },
  { id: 12, name: 'Timothe Chalamet',  image: 'Timothe_Chalamet'   },
  { id: 13, name: 'Taylor Swift',      image: 'Taylor_Swift'       },
  { id: 14, name: 'Leonardo Dicaprio', image: 'Leonardo_Dicaprio'  },
  { id: 11, name: 'Jennie',            image: 'Jennie'             },
  { id: 20, name: 'Rose',              image: 'Rose'               },
  { id: 19, name: 'Naruto',            image: 'Naruto'             },
  { id: 22, name: 'Sasuke',            image: 'Sasuke'             },   // THÊM MỚI, không có trong data_funny.json
];

// ============================== 40 · FragmentListFunnyPuzzle ================
screen(
  '40 · List Funny Puzzle',
  'res/layout/fragment_list_funny_puzzle.xml + item_funny_puzzle.xml — GridLayoutManager spanCount=2 set thẳng trong XML (app:spanCount="2"). ' +
  '20/20 ô ContentItem, KHÔNG có ô ad: FragmentListFunnyPuzzle$initUi$1$2.java:60-68 chỉ map List<FunnyPuzzleUI>→List<FunnyPuzzleItem.ContentItem> rồi adapter.updateAll(...) — ' +
  'logic add(2,FunnyPuzzleItem.AdItem.INSTANCE) chỉ tồn tại ở ui/home/AdapterTemplateCategory.java:277-287 (Home carousel, cụm khác). Data: assets/face_funny/data_funny.json (20 entry).',
  (f) => {
    // rvFunnyPuzzleTemplates — grid 2 cột, item card 150x150 (padding1 + image148x148 1:1 +
    // nameplate overlay đáy, bo góc 16dp theo bg_funny_puzzle, viền 1dp primary — dashed trong
    // XML (stroke dash không hỗ trợ trong helper frame(), vẽ solid gần đúng nhất)
    const GRID_TOP = 80;      // btnBack.bottom(60) + RV padding10 + item margin10
    const COL_X = [20, 190];  // slot170 + margin10 mỗi bên
    const ROW_STEP = 170;     // card150 + gap20 (margin10+margin10 giữa 2 hàng)
    const CARD = 150;
    // chiều cao nội dung THẬT (10 hàng, 20 nhân vật) — tính TRƯỚC để nền + grow() khớp nhau,
    // tránh nền 800dp cứng trong khi frame nới cao hơn theo grow() (tràn viền, lộ nền tối canvas)
    const contentH = GRID_TOP + Math.ceil(FNP_LIST_DATA_V1.length / 2) * ROW_STEP - (ROW_STEP - CARD) + 20;

    add(f, rect('bg', 0, 0, SCREEN_W, contentH, { fill: C.white }));

    // header — btnBack style BackImageButton1 (48x48, padding8, ic_back_1) + title ScreenTitleCommon
    const back = frame('btnBack', 12, 12, 48, 48, {});
    add(f, back);
    // toạ độ LOCAL trong `back` (không phải tuyệt đối) — padding8 trên hộp 48x48 → 48-8*2=32
    const backIc = icon('ic_back_1', 8, 8, 32, 32);
    if (backIc) add(back, backIc);
    add(f, text('Funny Puzzle', 0, 12, {
      size: 20, weight: 700, font: 'main', color: C.textHi,
      w: SCREEN_W, h: 48, align: 'CENTER', valign: 'CENTER',
    }));

    FNP_LIST_DATA_V1.forEach((item, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const x = COL_X[col], y = GRID_TOP + row * ROW_STEP;
      const card = frame('Card · ' + item.name + ' (#' + item.id + ')', x, y, CARD, CARD, {
        fill: C.white, radius: R.tile, stroke: C.primary, strokeW: 1, clip: true,
      });
      add(f, card);
      photo(card, 1, 1, CARD - 2, CARD - 2, item.image, 'FILL', R.tile - 1);
      const plate = rect('NamePlate', 1, CARD - 1 - 37, CARD - 2, 37, { fill: C.white });
      add(card, plate);
      add(card, text(item.name, 1, CARD - 1 - 37, {
        size: 14, weight: 700, font: 'main', color: C.textHi,
        w: CARD - 2, h: 37, align: 'CENTER', valign: 'CENTER',
      }));
    });

    grow(f, contentH);
  }
);

// ============================== 41a..41h · FragmentFunnyPuzzle ==============
// Shared chrome — fragment_funny_puzzle.xml. Nhân vật mẫu dùng để dựng imvFunnyOrigin/imvNotify:
// Cristiano_Ronaldo (id 4) — chỉ là ví dụ đại diện, mọi state đều dùng chung 1 nhân vật cho nhất quán.
function fnp_drawChrome(f, o) {
  o = o || {};
  // overlay (OverlayView) — camera preview + AR face-tracking renderer thời gian thực (MediaPipe
  // FaceLandmarker), fill kín màn — 100% runtime, không có asset tĩnh trong APK
  // Camera truc tiep + lop AR: KHONG co asset tinh trong APK. O nay la anh MÔ PHỎNG sinh boi
  // script/make-mock-ar.py - overlay nhan vat THAT trong APK + khuon mat TONG HOP, ghep dung
  // thu tu ve cua OverlayView.java:700-712: drawBitmap(camera) -> drawFunnyOverlay(nhan vat,
  // MAT TRONG, ve nguyen xi) -> drawFunnyComponent (cat 1 bo phan tu anh nhan vat GOC bang
  // BitmapShader roi tinh tien xuong theo frameCount = animation runtime, khong dung tinh).
  // => mat nhan vat LUON TRONG. Ban mock cu dan nham bo net mat tong hop vao lo -> da bo.
  // Mock v2 (540x1200, tỉ lệ 360x800): camera phủ trọn màn (selfie người dùng), nhân vật chỉ
  // chiếm ~55% bề ngang đè lên vùng mặt — khớp ảnh chụp app thật user gửi. Full-bleed, không
  // còn 'camera bg' lấp chỗ vì ảnh mock đã phủ kín; đặt NGAY SAU nền, TRƯỚC mọi chrome.
  // Chua duoc cap quyen -> cameraManager.startFunnyCamera(...) CHUA CHAY (no nam trong nhanh
  // if(z) cua launcherOpenCameraDevice$lambda$0, FragmentFunnyPuzzle.java:306-341), nen OverlayView
  // khong nhan ca khung camera lan bitmap nhan vat -> khung preview TRONG. Ve nen den, khong ve
  // mock AR. Cung quy uoc voi 30f ben cum face-puzzle ('camera-not-started').
  if (o.noCamera) {
    add(f, rect('camera-not-started · chưa cấp quyền → startFunnyCamera() chưa chạy', 0, 0, SCREEN_W, SCREEN_H, { fill: C.black }));
  } else {
    add(f, img('mock_ar_ronaldo', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));
  }
  // Nhãn giải thích "MÔ PHỎNG · camera live + AR overlay..." đã GỠ khỏi canvas theo yêu cầu —
  // nội dung chuyển vào note của từng screen() gọi hàm này (41a/b/c/d/e/f/h), xem tham số note.

  // imvFunnyOrigin — 85x85, ảnh gốc nhân vật mẫu (originImagePath), luôn hiển thị (KHÔNG thuộc groupFunctions)
  // Glide...into(imvFunnyOrigin) CUNG nam trong nhanh if(z) (FragmentFunnyPuzzle.java:307) ->
  // chua cap quyen thi ImageView nay rong, khong co src, khong ve gi.
  if (!o.noCamera) photo(f, 275, 76, 85, 85, 'Cristiano_Ronaldo', 'FILL', 0);

  if (o.groupVisible) {
    // imvNotify — img_notify_puzzle, width85% màn (306), tỉ lệ thật ảnh gốc 1025:84
    add(f, img('img_notify_puzzle', 27, 193, 306, 25, 'FIT'));

    // btnBack — style BackImageButton2 (48x48, padding4, ic_back_2, elevation10)
    const back = frame('btnBack', 12, 12, 48, 48, {});
    add(f, back);
    // toạ độ LOCAL trong `back` — padding4 trên hộp 48x48 → 48-4*2=40
    const backIc = icon('ic_back_2', 4, 4, 40, 40);
    if (backIc) add(back, backIc);

    // btnAddMusic — pill 40dp radius (bg_black_40_rounded #66171716), maxWidth180
    const pillW = o.musicChosen ? 160 : 130;
    const pill = frame('btnAddMusic', (SCREEN_W - pillW) / 2, 20, pillW, 32, {
      fill: '66171716', radius: 40,
    });
    add(f, pill);
    const musicIc = icon('ic_music', 8, 8, 16, 16);
    if (musicIc) add(pill, musicIc);
    add(pill, text(o.songLabel || 'Add song', 28, 0, {
      size: 13, font: 'main', color: C.white, w: pillW - 36, h: 32, valign: 'CENTER', align: 'LEFT',
    }));
    // vVertical + btnRemoveSound: XML mặc định visibility="gone" cả 2. Chưa xác định được chính
    // xác điều kiện code set visible khi đã chọn nhạc (xem specs/funny-puzzle.md mục "Cờ #1") →
    // giữ nguyên nhánh mặc định GONE, KHÔNG dựng thành state riêng (theo chỉ đạo coordinator).

    // btnFlipCamera — Base.PrimaryButton.Square 48x48, padding4, ic_rotation_camera
    const flip = frame('btnFlipCamera', 304, 12, 48, 48, {});
    add(f, flip);
    // toạ độ LOCAL trong `flip` — padding4 trên hộp 48x48 → 48-4*2=40 (trước đó dùng toạ độ
    // tuyệt đối 308,16 rồi add vào sub-frame flip(x=304) → double-offset, icon lệch ra ngoài màn)
    const flipIc = icon('ic_rotation_camera', 4, 4, 40, 40);
    if (flipIc) add(flip, flipIc);

    // rcvTimeRecord — SnappyRecycleView horizontal, 3 item hardcode 15s/30s/1m (AppSetting.java:46)
    const TIMES = ['15s', '30s', '1m'];
    const itemW = 56, listX = 96, listY = 652;
    TIMES.forEach((t, i) => {
      const ix = listX + i * itemW;
      const selected = o.timeSelectedIndex === i;
      add(f, text(t, ix, listY + 4, {
        size: 14, font: 'main', color: selected ? C.white : 'ffffff99',
        w: itemW, align: 'CENTER',
      }));
      const dot = ellipse('imgDot', ix + itemW / 2 - 3, listY + 4 + 21, 6, 6, { fill: C.white });
      dot.visible = !!selected;
      add(f, dot);
    });
  }

  // tvWaitingRecordCountdown — gone mặc định, visible khi đang đếm ngược (runtime text, ví dụ "3")
  if (o.countdownText) {
    add(f, text(o.countdownText, 150, 637, {
      size: 36, weight: 900, font: 'main', color: '02bbfa',
      w: 60, h: 43, align: 'CENTER', valign: 'CENTER',
    }));
  }

  // btnRecording — RecordingProgress custom view onDraw: drawIcon (bitmap play/pause fill toàn bộ
  // 80x80) + drawArc(strokeWidth12, color #ff02bbfa, start-90°, sweep=360×progress)
  const rec = frame('btnRecording', 140, 696, 80, 80, {});
  add(f, rec);
  const recIc = icon(o.recordIcon || 'ic_play_filter', 0, 0, 80, 80);
  if (recIc) add(rec, recIc);
  // track (interpretive — code không vẽ track nền, chỉ vẽ đúng phần progress; thêm ellipse mờ
  // theo yêu cầu coordinator để dễ đọc trong Figma, KHÔNG phải số liệu từ code)
  add(rec, ellipse('progress track (interpretive)', 6, 6, 68, 68, { stroke: '02bbfa', strokeW: 12, strokeOpacity: 0.25 }));
  if (o.progressArcD) {
    vpath(rec, 0, 0, 80, 80, '80 80', o.progressArcD, { stroke: '02bbfa', sw: 12, name: 'progress arc' });
  }

  // nativeCollapsibleContainer — AD SLOT native_collapsible_detail. collapseHolderNative(256dp)
  // chỉ là placeholder-chờ-tải, bị gone() sau 2000ms (FragmentFunnyPuzzle$initUi$1$1.smali:~150).
  // Sau đó container co theo kích thước native ad thật (runtime, không xác định tĩnh được) —
  // dựng compact 72dp thay vì 256dp của placeholder chờ tải. Chỉ vẽ 1 lần đại diện ở state 41c
  // để tránh lặp lại hình ảnh chồng lấn 8 lần.
  if (o.showCollapsibleAd) {
    adSlot(f, 0, SCREEN_H - 72, SCREEN_W, 72, 'native_collapsible_detail');
  }
}

screen(
  '41a · Funny Puzzle · xin quyền camera',
  'FragmentFunnyPuzzle.java:428-430 requireCameraPermission() → launcherOpenCameraDevice.launch([CAMERA, RECORD_AUDIO, (WRITE_EXTERNAL_STORAGE nếu API≤28)]) gọi ngay trong initUi$1$1 sau khi nạp overlayImagePath vào OverlayView. Android xin runtime-permission TỪNG QUYỀN MỘT (không gộp) → hệ thống tách mảng trên thành nhiều dialog liên tiếp; đây là dialog đầu tiên (CAMERA). AndroidManifest khai báo CAMERA/RECORD_AUDIO (+READ_MEDIA_VIDEO, POST_NOTIFICATIONS…); "android.permission.CAMERA" xuất hiện 3 chỗ trong code xin runtime. ' +
  'Dựng theo mẫu chuẩn Material You permission dialog (Android 12+) — đây là UI HỆ ĐIỀU HÀNH có thật (không phải app tự vẽ, không có layout XML trong APK), nên KHÔNG cần gắn cờ "placeholder" — chỉ ghi rõ là UI hệ thống. Icon camera là hình minh hoạ đơn giản hoá (không trích từ icon hệ thống thật, chỉ gợi ý loại quyền). ' +
  '| HIỂN THỊ: khung preview ĐỂ ĐEN, KHÔNG vẽ mock AR. Lý do đọc thẳng từ code: cameraManager.startFunnyCamera(viewLifecycleOwner, overlay, resource) và Glide…into(imvFunnyOrigin) ĐỀU nằm trong nhánh if(z) "đã cấp quyền" của launcherOpenCameraDevice$lambda$0 (FragmentFunnyPuzzle.java:306-341). Chưa cấp quyền ⇒ OverlayView không nhận khung camera lẫn bitmap nhân vật, và ImageView góc phải cũng không có src ⇒ cả hai đều trống. Bản dựng trước vẽ mock AR ở 2 state này là SAI — không thể có hình camera khi chưa có quyền. Cùng quy ước với 30f bên cụm Face Puzzle. Dialog xin quyền là UI hệ điều hành Android 12+ (Material You permission dialog), không phải màn do app thiết kế và không có layout trong APK.',
  (f) => {
    fnp_drawChrome(f, { groupVisible: true, recordIcon: 'ic_play_filter', noCamera: true });

    const DW = 312, DH = 320, DX = (SCREEN_W - DW) / 2, DY = 240;
    const card = frame('OS permission dialog · CAMERA (Android 12+)', DX, DY, DW, DH, {
      fill: C.white, radius: 28, shadow: 0.18,
    });
    add(f, card);

    // icon camera — minh hoạ đơn giản hoá (thân máy ảnh vpath + vòng ống kính), màu #5f6368
    const icoX = DW / 2 - 12, icoY = 24;
    vpath(card, icoX, icoY, 24, 24, '24 24', 'M2,6 H22 V20 H2 Z M8,4 H16 V6 H8 Z', { fill: '5f6368', name: 'camera icon (minh hoạ)' });
    add(card, ellipse('camera lens', icoX + 8, icoY + 9, 8, 8, { fill: C.white }));
    add(card, ellipse('camera lens ring', icoX + 8, icoY + 9, 8, 8, { stroke: '5f6368', strokeW: 1.4 }));

    // tiêu đề — chuỗi CHUẨN của HỆ ĐIỀU HÀNH (tiếng Anh), không phải string.xml của app
    add(card, text('Allow Funny Face to take pictures and record video?', 24, 64, {
      size: 20, font: 'main', color: '1f1f1f', w: DW - 48, h: 56, align: 'CENTER', valign: 'TOP', lineHeight: 28,
    }));

    // 3 nút chữ dọc, đúng thứ tự chuẩn Android: While using the app / Only this time / Don't allow
    const BTN = ['While using the app', 'Only this time', "Don't allow"];
    const btnTop = 144, btnH = 52;
    BTN.forEach((label, i) => {
      add(card, text(label, 24, btnTop + i * btnH, {
        size: 14, weight: 500, font: 'main', color: '0b57d0', w: DW - 48, h: btnH, align: 'CENTER', valign: 'CENTER',
      }));
    });

    // Nhãn "UI hệ điều hành..." đã GỠ khỏi canvas theo yêu cầu — nội dung đã nối vào note ở trên.
  }
);

screen(
  '41b · Funny Puzzle · từ chối quyền camera',
  'FragmentFunnyPuzzle.java:298-348 launcherOpenCameraDevice$lambda$0 — quyền CAMERA bị từ chối → ContextExtKt.toastMessageLongTime(context, R.string.you_need_permission_to_use_this_feature)="You need permission to use this feature" (values/strings.xml:724) rồi popBackStack() ngay — OS toast placeholder có nhãn. ' +
  '| HIỂN THỊ: khung preview ĐỂ ĐEN, KHÔNG vẽ mock AR. Lý do đọc thẳng từ code: cameraManager.startFunnyCamera(viewLifecycleOwner, overlay, resource) và Glide…into(imvFunnyOrigin) ĐỀU nằm trong nhánh if(z) "đã cấp quyền" của launcherOpenCameraDevice$lambda$0 (FragmentFunnyPuzzle.java:306-341). Chưa cấp quyền ⇒ OverlayView không nhận khung camera lẫn bitmap nhân vật, và ImageView góc phải cũng không có src ⇒ cả hai đều trống. Bản dựng trước vẽ mock AR ở 2 state này là SAI — không thể có hình camera khi chưa có quyền. Cùng quy ước với 30f bên cụm Face Puzzle. ',
  (f) => {
    fnp_drawChrome(f, { groupVisible: true, recordIcon: 'ic_play_filter', noCamera: true });
    const toast = frame('OS toast', 30, 700, SCREEN_W - 60, 44, {
      fill: '2d2d2d', radius: 8, opacity: 0.92,
    });
    add(f, toast);
    add(toast, text('You need permission to use this feature', 12, 0, {
      size: 12, font: 'main', color: C.white, w: SCREEN_W - 84, h: 44, valign: 'CENTER', align: 'CENTER',
    }));
  }
);

screen(
  '41c · Funny Puzzle · live camera (đã cấp quyền)',
  'DÒNG CHỮ "Tap screen or blink to stop" KHÔNG phải text node: nó là ẢNH THẬT trong APK — @drawable/img_notify_puzzle (1025×84, chữ trắng nền trong suốt), vẽ qua imvNotify trong fragment_funny_puzzle.xml, chỉ hiện khi groupFunctions visible. Vì vậy grep strings.xml/resources.arsc/classes*.dex đều không thấy — đã kiểm chứng. Đối chiếu ảnh chụp máy thật của người dùng: khớp cả vị trí lẫn kiểu chữ. | | FragmentFunnyPuzzle.java:298-340 — quyền đã cấp → Glide load originImagePath vào imvFunnyOrigin (into thật), cameraManager.startFunnyCamera(...), recordingManager.prepare(...). groupFunctions visible mặc định (chưa vào countdown). AD SLOT native_collapsible_detail dựng đại diện ở state này (xem note trong fnp_drawChrome). ' +
  '| HIỂN THỊ: khung camera là ảnh MÔ PHỎNG (script/make-mock-ar.py, overlay nhân vật THẬT trong APK + khuôn mặt tổng hợp, ghép theo đúng thứ tự vẽ OverlayView.java:700-712 — camera, rồi overlay nhân vật vẽ NGUYÊN XI với MẶT TRỐNG; app KHÔNG vẽ nét mặt người dùng vào lỗ, thứ động duy nhất là 1 bộ phận rơi xuống do drawFunnyComponent, là animation runtime nên không dựng tĩnh) — KHÔNG phải ảnh chụp app thật; camera live + AR overlay 100% runtime (OverlayView · MediaPipe FaceLandmarker), không có asset tĩnh trong APK.',
  (f) => {
    fnp_drawChrome(f, {
      groupVisible: true, recordIcon: 'ic_play_filter', timeSelectedIndex: -1, showCollapsibleAd: true,
    });
  }
);

screen(
  '41d · Funny Puzzle · đếm ngược trước khi quay',
  'LOẠI: state này KHÔNG BAO GIỜ HIỂN THỊ trong UI thật — phát hiện khi rà lại theo yêu cầu coordinator sau vụ 41f (pause). FragmentFunnyPuzzle$initListener$lambda$0$1 (FragmentFunnyPuzzle.java:250-254, smali dòng 693) gọi recordingManager.start(0L, overlay) với timeWaiting HARDCODE 0L (const-wide/16 v0,0x0 — không phải biến, không có UI nào cho chọn giá trị khác). RecordingManagerImpl.startWaitingRecordCountdown() (RecordingManagerImpl.java:198-215): gọi listener.onStartWaitingRecord() rồi NGAY LẬP TỨC kiểm tra "if (timeWaiting <= 0) { startRecordingInternal(view); return }" — startRecordingInternal() gọi onFinishWaitingRecord() rồi onStartRecording() NGAY TRONG CÙNG LỜI GỌI HÀM (đồng bộ, không CountDownTimer nào được tạo vì nhánh timeWaiting<=0 return trước dòng "countDownTimer.start()"). Tức tvWaitingRecordCountdown được set visible() rồi gone() lại trong cùng một khung xử lý, trước khi Android có cơ hội vẽ frame nào — người dùng KHÔNG BAO GIỜ thấy số đếm ngược. Trạng thái "waiting" trong RecordingManager là API dùng chung (có thể có countdown thật ở màn khác dùng timeWaiting>0, vd FacePuzzle với listTimeCountDown=["0s","3s","10s"]), nhưng ở FragmentFunnyPuzzle luôn gọi với 0L nên nhánh này chết. ' +
  'BÀI HỌC: thấy callback onStartWaitingRecord()/onWaitingRecord() tồn tại trong code KHÔNG có nghĩa là có state đếm ngược hiển thị được — phải truy NGƯỢC lên nơi gọi start(timeWaiting,...) xem giá trị timeWaiting THẬT SỰ là gì (hardcode 0, biến runtime, hay UI cho chọn). Đọc trọn, không suy từ tên callback.',
  (f) => {
    fnp_drawChrome(f, { groupVisible: false, countdownText: '3', recordIcon: 'ic_play_filter' });
  },
  { excluded: true }
);

screen(
  '41e · Funny Puzzle · đang quay',
  'ĐI TIẾP: dừng quay → actionFunnyPuzzleToPreviewWithMusic → màn 51b (nút Next) → 54 → 60 Result (nút Save). Hai màn đó dùng chung với luồng Face Puzzle nên nằm ở hàng dưới, không lặp lại ở hàng này. | Vào thẳng state này khi bấm btnRecording — KHÔNG qua 41d (đếm ngược) như hình dung ban đầu: recordingManager.start(0L,...) khiến onStartWaitingRecord()/onFinishWaitingRecord() chạy đồng bộ tức thời (xem note đã LOẠI ở 41d), nên onStartRecording() coi như chạy ngay sau cú bấm. RecordingManager.Listener.onStartRecording() (FragmentFunnyPuzzle.java:598-608) → btnRecording.setEnabled(true), RecordingProgress.startAnimation() đổi icon ic_pause_filter + chạy ValueAnimator progress 0→1 trong durationSeconds×1000ms (mặc định 60s="1m", AppSetting.java:46), mediaMusic.start() nếu có nhạc. groupFunctions vẫn GONE (không có lệnh restore). ' +
  '| HIỂN THỊ: khung camera là ảnh MÔ PHỎNG (script/make-mock-ar.py, overlay nhân vật THẬT trong APK + khuôn mặt tổng hợp, ghép theo đúng thứ tự vẽ OverlayView.java:700-712 — camera, rồi overlay nhân vật vẽ NGUYÊN XI với MẶT TRỐNG; app KHÔNG vẽ nét mặt người dùng vào lỗ, thứ động duy nhất là 1 bộ phận rơi xuống do drawFunnyComponent, là animation runtime nên không dựng tĩnh) — KHÔNG phải ảnh chụp app thật; camera live + AR overlay 100% runtime (OverlayView · MediaPipe FaceLandmarker), không có asset tĩnh trong APK.',
  (f) => {
    fnp_drawChrome(f, {
      groupVisible: false, recordIcon: 'ic_pause_filter', timeSelectedIndex: 2,
      progressArcD: 'M40,6 A34,34 0 0,1 59.98,67.51', // progress ≈0.4 (144°), minh hoạ giữa chừng
    });
  }
);

screen(
  '41f · Funny Puzzle · tạm dừng quay',
  'LOẠI: state này KHÔNG TỒN TẠI trong UI. pause() chỉ được gọi từ Fragment.onPause() (lifecycle, khi app xuống nền) tại FragmentFunnyPuzzle.java:547-551, không có nút nào kích hoạt. Nút dừng gọi stop() -> sang thẳng Result. Phát hiện khi user chơi app thật. ' +
  'RecordingManager.Listener.onPauseRecording() (FragmentFunnyPuzzle.java:386-394) → RecordingProgress.pauseRecord(): initIconBitmap(ic_play_filter) [đổi icon về play dù đang ở giữa tiến trình], animator.pause() [giữ nguyên % hiện tại], mediaMusic.pause(). groupFunctions vẫn GONE — nội dung này ĐÚNG về mặt code nhưng KHÔNG BAO GIỜ được người dùng nhìn thấy vì app đã ở nền (màn hình khác đang hiển thị) khi pause() chạy. ' +
  'BÀI HỌC (ghi lại để người sau không lặp lại): thấy pauseRecord()/onPauseRecording() trong code KHÔNG có nghĩa là có nút tạm dừng — phải truy NGƯỢC xem AI GỌI nó (lifecycle callback hay UI click listener). Plan 1 đã cảnh báo "đọc trọn, không suy từ tên" và ta vẫn dính lỗi này ở lượt build trước; chỉ được sửa sau khi user chơi app thật và báo lại.',
  (f) => {
    fnp_drawChrome(f, {
      groupVisible: false, recordIcon: 'ic_play_filter', timeSelectedIndex: 2,
      progressArcD: 'M40,6 A34,34 0 0,1 59.98,67.51', // giữ nguyên % lúc pause, minh hoạ cùng mốc 0.4
    });
  },
  { excluded: true }
);

screen(
  '41g · Funny Puzzle · dừng quay xong (inter_record ad)',
  'RecordingManager.Listener.onStopRecording() → FragmentFunnyPuzzle$onStopRecording$1.java:47-85: giải phóng camera/media, LifeCycleExtKt.loadShowFullscreenSafe(AdKey.INTER_RECORD="inter_record") rồi mới navigateToDirections(actionFunnyPuzzleToPreviewWithMusic(fileSave, soundUI)). Ad fullscreen che toàn bộ UI bên dưới trước khi điều hướng sang Preview (ngoài cụm) — fileSave (video mp4) là runtime placeholder, không có trong APK. ' +
  'Đã đối chiếu 2 khung native đã resolve trong briefs/_fill-empty.md (ads_native_media_common.xml, native_fake_full_inter.xml) nhưng KHÔNG dùng: cả 2 là layout app tự vẽ cho quảng cáo NATIVE (NativeAdView, dùng ở NATIVE_*/NATIVE_FS_* placement); "inter_record" là AdKey.INTER_RECORD — có tiền tố INTER_ (giống INTER_SPLASH/INTER_SAVE), tức interstitial THẬT, UI do SDK mediation vẽ 100% lúc runtime, không có layout XML nào trong res/layout của APK cho nó. Khung dưới đây là khung interstitial tối giản mang tính minh hoạ (nút đóng, badge "Ad", vùng media, nút CTA) theo quy ước phổ biến của SDK ads — KHÔNG lấy từ layout thật, không bịa tên thương hiệu quảng cáo nào. ' +
  '| HIỂN THỊ: nền là ảnh MÔ PHỎNG khung hình cuối video vừa quay (fileSave — runtime, không có trong APK, dùng mock_ar_ronaldo để gợi liên tục ngữ cảnh thay vì ô đen trơn không đọc ra được đây là 1 state). Khung interstitial phủ lên trên (nút đóng, badge "Ad", vùng media, CTA "Install") là UI của SDK quảng cáo — không có layout trong APK, chỉ minh hoạ chrome phổ biến của SDK mediation.',
  (f) => {
    // nền: khung hình cuối video vừa quay xong (fileSave.mp4 — runtime), dùng ảnh mô phỏng AR để
    // gợi liên tục ngữ cảnh (thay vì ô đen trơn không đọc ra được đây là 1 state).
    // Nhãn "MÔ PHỎNG · khung hình cuối..." đã GỠ khỏi canvas — nội dung đã nối vào note ở trên.
    add(f, img('mock_ar_ronaldo', 0, 0, SCREEN_W, SCREEN_H, 'FILL'));

    // scrim — ad sắp phủ kín lên trên toàn màn
    add(f, rect('scrim', 0, 0, SCREEN_W, SCREEN_H, { fill: '000000', opacity: 0.55 }));

    // khung interstitial của SDK mediation — KHÔNG có layout trong APK, chỉ là minh hoạ chrome
    // phổ biến (nút đóng, badge "Ad", vùng media, nút CTA)
    const card = frame('SDK Interstitial (inter_record) — UI của SDK, không có layout trong APK', 0, 0, SCREEN_W, SCREEN_H, {
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
    // Nhãn "UI của SDK quảng cáo..." đã GỠ khỏi canvas — nội dung đã nối vào note ở trên.
  },
  { adOnly: true } // state này = 100% lớp interstitial SDK che kín; nền "khung hình cuối video"
                    // chỉ là minh hoạ liên tục do agent thêm (app thật KHÔNG hiện lại frame đó —
                    // ad opaque che ngay lập tức), không phải UI riêng có thể đứng độc lập khi tắt ad.
                    // Tắt SHOW_ADS => bỏ khỏi registry, tránh 1 frame trống/gây hiểu lầm.
);

screen(
  '41h · Funny Puzzle · đã chọn nhạc nền',
  'FragmentFunnyPuzzle.java:350-362 observeCurrentSound() + FragmentFunnyPuzzle$observeCurrentSound$2.java — tvNameSong.text đổi theo SoundUI đã chọn ở Sound Picker (ngoài cụm), tên bài hát là dữ liệu runtime (không có trong data đã đọc của cụm này) nên dùng nhãn placeholder thay vì bịa tên bài hát thật. vVertical/btnRemoveSound: XML mặc định GONE, chưa xác định được dòng code set visible khi có nhạc (specs/funny-puzzle.md mục "Cờ #1") → giữ nguyên GONE theo chỉ đạo, không đoán.  | HIEN THI: nhan bai hat dung Greedy Sped Up (bai dau trong AppSetting.kt) lam minh hoa - ten that phu thuoc bai nguoi dung chon o Sound Picker.' +
  '| HIỂN THỊ: khung camera là ảnh MÔ PHỎNG (script/make-mock-ar.py, overlay nhân vật THẬT trong APK + khuôn mặt tổng hợp, ghép theo đúng thứ tự vẽ OverlayView.java:700-712 — camera, rồi overlay nhân vật vẽ NGUYÊN XI với MẶT TRỐNG; app KHÔNG vẽ nét mặt người dùng vào lỗ, thứ động duy nhất là 1 bộ phận rơi xuống do drawFunnyComponent, là animation runtime nên không dựng tĩnh) — KHÔNG phải ảnh chụp app thật; camera live + AR overlay 100% runtime (OverlayView · MediaPipe FaceLandmarker), không có asset tĩnh trong APK.',
  (f) => {
    fnp_drawChrome(f, {
      groupVisible: true, recordIcon: 'ic_play_filter', timeSelectedIndex: -1,
      musicChosen: true, songLabel: 'Greedy Sped Up',
    });
  }
);
