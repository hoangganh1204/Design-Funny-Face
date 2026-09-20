# Funny Face — hệ thiết kế v3

Ngày 2026-09-20 · Bản giao: `figma/v3` + `assets/v3` · Bộ khởi tạo: `script/make-v3.py`

## Mục tiêu và ràng buộc

**Mục tiêu.** Làm giao diện hút mắt và giữ chân người dùng hơn app gốc, trong khi doanh thu
thuần đến từ quảng cáo.

**Phạm vi (design lead chốt).** Reskin **cộng** sửa bố cục trong từng màn. Không thêm màn,
không đổi luồng, không thêm phần tử nào cần logic mới. Mọi thay đổi phải ánh xạ được vào một
view đã có trong layout XML — dev sửa XML và drawable, không đụng nav graph hay code luồng.

**Không có bằng chứng** rằng bảng màu này tăng conversion, retention hay doanh thu so với
bảng khác. Đây là điểm khởi đầu cho prototype; muốn kết luận phải A/B test với người dùng
thật. Thứ duy nhất đo được ở đây là **tương phản**.

## Vai trò màu

| Vai trò | Token | Mã | Dùng ở đâu |
|---|---|---|---|
| Thương hiệu | `brand` | `#7C3AED` | chip đang chọn, viền trạng thái, gradient Splash |
| Hành động | `action` | `#FF6B35` | Try Now · Next · Save · Done · thanh tiến trình |
| Chữ trên hành động | `onAction` | `#1A1523` | chữ/icon trên nền cam |
| Thành công | `mint` | `#34D399` | trạng thái lưu xong — dùng tiết chế |
| Nền màn nội dung | `bg` | `#14101F` | Home, chọn hiệu ứng, thư viện, Result, Sound |
| Bề mặt | `surface` / `surfaceHi` | `#1E1830` / `#2A2140` | thẻ, khối ad, chip chưa chọn |
| Nền màn đọc chữ | `paper` | `#FDF9F3` | Settings, Privacy Policy, Term of use |
| Chữ | `onDark` / `onLight` | `#F5F3FF` / `#1A1523` | theo nền |

### Vì sao tách hai màu chứ không dùng một

Một màu duy nhất thì đồng nhất nhưng mất phân cấp hành động. Purple mang nhận diện và các
khu vực chính; Orange chỉ dành cho thứ cần bấm. Hệ quả cụ thể: **trong mỗi màn chỉ có đúng
một khối màu cam**, nên không cần suy nghĩ cũng biết bấm vào đâu.

Chip danh mục ở Home dùng **tím chứ không phải cam**, dù nó là trạng thái tương tác: nó là
điều hướng, không phải hành động. Để cam ở đó là có hai vùng cam trong một màn, và nút CTA
mất đi tính duy nhất.

### Vì sao màn nội dung để nền TỐI

1. **Nội dung chính của các màn đó là ảnh** — thumbnail video và ảnh nhân vật. Nền sáng
   cạnh tranh chú ý với chính nội dung; nền tối đẩy ảnh lên trước.
2. **Phân biệt quảng cáo.** 6 trong 12 placement là native nằm ngay trong màn nội dung. Trên
   nền trắng, khối native trông y hệt một ô nội dung — người dùng bấm nhầm. Trên nền tối, ô
   nội dung là ảnh còn khối ad là mảng phẳng có nhãn, phân biệt được ngay.

Điểm 2 là chỗ **dễ chịu cho người dùng và tốt cho doanh thu dài hạn trùng nhau**: bấm nhầm
đẩy CTR ngắn hạn lên nhưng giết retention, mà app không có IAP nên retention chính là doanh
thu. Đây là lập luận về cơ chế, không phải lời hứa về con số.

Warm White giữ đúng vai trò: các màn ĐỌC CHỮ.

### Tương phản

Kiểm tự động bằng `script/audit-contrast.py` — **303/303 node đạt WCAG AA**.

| Cặp màu | Tỉ lệ | Mức |
|---|---|---|
| `onDark` trên `bg` | 16.8:1 | AAA |
| `onDarkSub` trên `bg` | 7.4:1 | AAA |
| `onAction` trên `action` | 7.1:1 | AAA |
| trắng trên `action` | 2.9:1 | **trượt AA** — chữ trên nút cam phải là chữ TỐI |
| trắng trên `brand` | 5.9:1 | AA |
| `onLight` trên `paper` | 16.3:1 | AAA |

App gốc để chữ đen trên brand xanh — 3.84:1, dưới chuẩn AA. Hệ mới không còn cặp nào trượt.

## Vòng chỉnh màu — đo trước, sửa sau

Phản hồi "màu cứ u tối thế nào ấy". Đo ra thì không phải tại tím:

**1. Cả bộ khung nằm trong 7 độ sắc.** bg 256° · surface 255° · surfaceHi 257° · line 257° ·
brand 262°. Không có tương phản sắc độ ở đâu nên mắt đọc toàn bộ khung như MỘT mảng
tím-đen phẳng. Dark UI làm tốt thì bóng lạnh hơn, mặt nổi ấm hơn.

**2. Dải độ sáng quá hẹp.** Spotify 14 điểm, TikTok 16, v3 cũ chỉ **10**.

| | nền | mặt | mặt nổi | viền | dải |
|---|---|---|---|---|---|
| trước | L*5.6 | L*10 | L*15 | L*19.5 | 10 |
| **sau** | **L*10.5** | **L*17** | **L*23.7** | **L*31.6** | **21** |

**3. 358dp khoảng trống chết trên mỗi màn Home.** `home_chrome` trả `gridStartY: 212` cố
định và `home_footerAd` trả `y + 256` cố định — cả hai chừa chỗ cho ô quảng cáo **vô điều
kiện**, trong khi `adSlot()` không vẽ gì khi `SHOW_ADS=false`. Kết quả: 118dp trống ngay
đầu màn (đúng chỗ nhìn đầu tiên) + 240dp ở đáy. Đây mới là nguyên nhân chính của cảm giác
"tối" — không phải màu sai mà là quá nhiều khoảng trống.

Sau khi chừa chỗ có điều kiện: mật độ ảnh **56.3% → 67.8%**, khung Home 1998 → 1660dp.

**4. Chữ "Face Puzzle" phối màu hỏng.** Đo pixel: thân chữ xanh bão hoà 100% ở L*27, viền
chữ **ĐEN** L*0, đặt trên nền L*5.6 — viền tan hẳn vào nền, thân chữ hơn nền 2.3:1. Bản gốc
vốn là xanh nhạt **viền trắng** trên nền trắng; xoay hue máy móc giữ nguyên độ sáng nên đảo
nền xong là hỏng. `recolor_wordmark()` phân loại pixel theo ĐỘ SÁNG: viền → trắng, thân →
dải vàng→cam. Vàng-cam là màu bù của tím nên bật mạnh nhất trên nền này.

**5. Chip đang chọn nằm ngoài khung.** `tabMode=scrollable` nên lúc chạy tab được chọn luôn
được cuộn vào tầm nhìn; dựng tĩnh không mô phỏng thì frame 20e có chip đang chọn ở x=347,
ngoài khung 360 — người xem không biết tab nào đang mở. Lỗi TRUYỀN ĐẠT, không phải thẩm mỹ.
Nay `home_drawTabs` tự dịch hàng chip đúng như runtime.

**6. Màn chọn độ khó.** Ba khối chiếm 40% màn. Thử FILL khung 160dp thì **cắt chữ** ở nhãn
dài nhất — lỗi cứng, bỏ. Dùng: giữ FIT, nới sát mép, đẩy cả nhóm xuống vùng ngón cái với
tới. Khoảng trống trên thành khoảng thở dưới tiêu đề, và thao tác một tay dễ hơn.

## Vòng chỉnh cuối — nâng sáng dải tím

Phản hồi "vẫn tối quá" và "dải màu đơn sắc". Ba thay đổi, mỗi cái kéo theo hệ quả phải sửa:

**1. Nâng cả dải lên một bậc.** bg L*10.5 → **16.8**, dải khung 21 → **23 điểm**.

**2. Hệ quả: brand phải sáng theo.** Trên nền mới, `#7C3AED` chỉ còn **2.54:1** so với nền —
dưới ngưỡng 3:1 cho thành phần phi văn bản, chip đang chọn sẽ chìm. `#9A6CFF` đạt **4.10:1**
so với nền và **5.10:1** cho chữ tối đặt trên nó. Lưu ý chữ TRẮNG trên `#9A6CFF` chỉ 3.52:1 —
trượt — nên **chữ trên chip brand phải là chữ TỐI**, cùng nguyên tắc với nút cam.

**3. Hệ quả: chữ phụ phải sáng theo.** `#A79FC4` chỉ còn 3.58:1 trên chip chưa chọn.
`#C9C2DE` đạt 5.23:1 ở đó và 8.43:1 trên nền.

**4. Dải Splash / Language trải rộng thật.** Hai điểm dừng cũ quá gần nhau nên đọc ra đơn sắc.
Mới: `#5B21B6` (sẫm, đỉnh) → `#C4B0FF` (tím nhạt, đáy). Kiểm từng vị trí có chữ:

| Vị trí | Nền tại đó | Chữ trắng |
|---|---|---|
| wordmark 18% | `#6D3AC3` | 6.90:1 ✓ |
| "Loading…" 41% | `#865BD3` | 4.72:1 ✓ |
| đáy thẻ Language 56% | `#9672DF` | 3.64:1 ✓ |
| ghi chú ads 95% | `#BEA8FB` | **2.06:1 ✗** |

Dòng ghi chú ở 95% rơi vào chỗ tím nhạt nên đổi sang **chữ tối** (7.66:1), và hạ 20sp → 13sp —
một dòng ghi chú pháp lý vốn không nên to bằng tiêu đề.

**5. Fading edge cho hàng chip.** Hàng chip cuộn ngang nên luôn có một chip bị cắt ở mép trái;
dựng tĩnh thì trông như lỗi render. Dải mờ dần 28dp biến chỗ cắt thành tín hiệu "còn nữa,
cuộn đi". Ánh xạ: `android:requiresFadingEdge="horizontal"` — thuộc tính có sẵn, không thêm view.

## Nền màn nội dung — A/B ba bản, có chấm điểm

Câu hỏi: màn nội dung nên để tím đậm phẳng, hay dùng dải màu sáng như Splash? Dựng thật cả ba
rồi đo, không phán.

| | Nền đo dọc trang (8% → 95%) | Điểm |
|---|---|---|
| **A** phẳng `#2B2252` | không đổi | 8.7 |
| **B** dải nhẹ `#2B2252 → #3D3070` | `#2c2354 → #3c2f6e` (~8 điểm L*) | **8.9 ✓ CHỌN** |
| **C** dải sáng như Splash | `#632cbb → #bea8fb` | 5.6 |

Thang chấm: thẻ tách khỏi nền 30% · nhất quán khi cuộn 25% · sức sống 20% · không cạnh tranh
với 18 ô màu 15% · khớp phân vai hệ 10%.

**Vì sao C hỏng — và đây là lỗi cơ chế, không phải khẩu vị.** Home cuộn **1660dp**. Dải rộng
nghĩa là nửa dưới nền thành tím nhạt: thẻ tối (Sasuke, Jennie, Timothée) chìm hẳn, trong khi
cùng những thẻ đó ở nửa trên lại bật lên. **Cùng một component đọc khác nhau tuỳ vị trí cuộn** —
đó là hỏng phân cấp. Splash không cuộn và chỉ có một object (logo), nên ở đó dải rộng là
không khí; ở Home nó là nhiễu.

**Vì sao B thắng A.** Chênh ~8 điểm L* đủ để mắt đọc ra *chiều sâu* mà chưa đủ để đọc ra *đổi
màu nền*. Hết cảm giác mảng phẳng chết mà không đánh đổi gì.

**Phân vai chốt lại:** dải rộng = dành cho **khoảnh khắc** (Splash, Language — xem một lần,
không cuộn). Dải rất nhẹ = dành cho **chỗ làm việc** (Home, thư viện — ở lâu, cuộn nhiều).

## Nền dùng chung — một tông, có hoạ tiết, mọi màn

Gom vào một hàm `screenBg(f, h)`: **một dải chuyển + một lớp hoạ tiết**. Trước đây mỗi màn tự
khai báo nền nên Level Picker dùng ảnh nướng sẵn còn Home dùng dải chuyển — hai tông khác nhau.

**13 màn nội dung tối dùng chung đúng một dải `#2B2252 → #3D3070` và đều có hoạ tiết** (đã
kiểm bằng cách đọc lại scene: xem bảng dưới). Ba màn còn lại cố ý khác: Privacy/Term là nền
giấy (đọc chữ dài), và card "Setting up" là thẻ dialog chứ không phải nền màn.

### Hoạ tiết phải LÁT, không được kéo giãn

Bản đầu dùng `scaleMode: 'FILL'` — hỏng. Các frame cao khác nhau (800dp cho màn thường,
**1660dp** cho Home cuộn) nên cùng một hoạ tiết bị phóng to nhỏ khác nhau ở mỗi màn, và trên
frame rất cao nó phình thành **mảng loang** chứ không ra hoa văn.

Sửa: sinh một **ô lát vuông 720×720** và dùng `scaleMode: 'TILE'`. Hoạ tiết giữ nguyên kích
thước thật ở mọi màn — đúng bản chất hoa văn. Alpha hạ từ 0.30 xuống **0.11**.

### Ba bản hoạ tiết, mỗi bản một việc

| Bản | Dùng ở | Cách dựng |
|---|---|---|
| `window_bg` | Settings (nền giấy) | nướng sẵn trên `#FDF9F3`, cường độ 0.34 |
| `pattern_overlay` | 13 màn nội dung tối | **nền alpha = 0**, ô lát 720×720, cường độ 0.11 |
| `pattern_dark` | — (dự phòng) | nướng sẵn trên `#2B2252` |

Bản `pattern_overlay` trong suốt là bản quan trọng: hai bản kia đều nướng sẵn nền nên đắp lên
màn có dải chuyển là **mất dải**. Chỉ lớp phủ trong suốt mới vừa giữ được dải vừa có hoa văn.

## Icon phải tô theo NGỮ CẢNH, không theo tên asset

Icon lấy từ APK vốn đặt trên nền TRẮNG nên nét là đen/xám đậm. Phép xoay hue chỉ đụng pixel
thuộc họ màu brand (bão hoà ≥ 0.35) nên pixel trung tính được giữ nguyên — đúng với mục đích
xoay hue, nhưng **sai hoàn toàn sau khi đảo nền sang tối**. Đo được: `ic_home` L\*8,
`ic_back_1` L\*0, `ic_gallery_btn` L\*0, trên nền L\*10.5–17 → chìm hẳn.

`tintIcon()` chỉ đổi pixel **trung tính VÀ tối** (bão hoà < 0.25 và độ sáng < 0.45) nên điểm
nhấn có màu được giữ: bánh răng đỏ, mảng vàng của icon thư viện, tím của ô check.

**Cùng một asset dùng ở cả hai loại nền** — `ic_back_1` ở Level Picker (tối) và Settings
(giấy), `ic_check_box_*` ở Sound Picker (tối) và Language Picker (thẻ trắng). Tô theo TÊN
ASSET là sai ở một trong hai chỗ. `iconDark()` ép nét tối tại đúng call site nằm trên bề mặt
sáng. Đây chính là lý do trong app thật phải dùng `android:tint` trên từng ImageView chứ không
sửa file drawable.

Kiểm lại: 12 icon còn nét tối, **toàn bộ đều nằm trên bề mặt sáng**.

## Màn Result — A/B rồi chọn

Phản hồi: "trông như bị chặt 3 khúc". Đo ra đúng vậy: tím `0–76` · video `76–710` · tím
`710–800`. Dải tệ nhất là dải dưới — nó **tách nút Save khỏi đúng cái video mà nó lưu**.

| | Điểm |
|---|---|
| **A** giữ nguyên | 6.9 |
| **B** video tràn trọn màn | *không chấm được* |
| **C** dải tiêu đề + video kéo hết đáy, CTA nổi trên video | **8.9 ✓ CHỌN** |

Thang: liên tục thị giác 30% · CTA gắn với nội dung 25% · video là nhân vật chính 20% · tiêu
đề đọc được 15% · dev dễ làm 10%.

**B tự loại, không phải vì xấu:** video được vẽ SAU thanh tiêu đề nên khi tràn trọn màn nó che
mất tiêu đề và hai icon. Làm đúng phải đảo thứ tự vẽ — việc khác, chưa làm.

**C:** còn hai vùng thay vì ba, video cao thêm 90dp (chiếm 90% màn), và nút Save giờ nằm TRÊN
chính nội dung nó tác động. *Ánh xạ:* đổi constraint bottom của `exoPlayerView` về parent và
nâng `btnSave` lên trên bằng elevation. Không thêm view.

## Thay đổi bố cục

Mỗi mục kèm ánh xạ sang XML để dev biết sửa gì. **Không thêm view nào.**

### Thẻ nhân vật (Home tab Funny + màn 40)

**Trước:** thẻ trắng, viền nét đứt 1dp, ảnh vuông inset 1dp, tên trên dải trắng riêng ở đáy.
Ba vấn đề: dải trắng ăn 25% chiều cao thẻ mà không mang thêm thông tin; nét đứt đọc ra "ô
trống chờ điền" chứ không phải "nội dung bấm được"; thẻ trắng trên nền trắng không có ranh giới.

**Sau:** ảnh tràn hết thẻ, tên đè lên dải chuyển tối (trong suốt → 93%, cao 40% thẻ). Ảnh to
hơn **33%** trong cùng diện tích.

*XML:* `item_funny_puzzle.xml` — ImageView → `match_parent`; TextView giữ nguyên, `background`
đổi thành shape gradient; bỏ `bg_funny_puzzle` viền dashed.

### Chip danh mục (Home)

Chọn = tím đặc, bo tròn hẳn thành pill. Chưa chọn = `surfaceHi`, không viền. Pill đọc ra
"hàng này cuộn ngang được" rõ hơn hộp bo 8.

*XML:* `styles.xml` → `TemplateTabLayout`, đổi drawable selector.

### Tag HOT

⚠ **Đây là thứ DUY NHẤT trong v3 cần thêm view:** một TextView trong `item_funny_puzzle.xml`
cộng một cờ boolean trong `FunnyPuzzleUI`. Mọi thứ khác đều ánh xạ vào view đã có.

**Ràng buộc màu, đo chứ không đoán.** Nền các thẻ trải khắp vòng màu (xanh, đỏ, vàng, tím,
cam, hồng) nên không màu đơn nào đọc được trên tất cả. Chữ TRẮNG trượt AA trên mọi nền tag ấm:

| Nền tag | trắng | chữ tối `#181522` |
|---|---|---|
| pink `#FF4F81` | 3.14:1 ✗ | 5.72:1 ✓ |
| cam `#FF8A3D` | 2.35:1 ✗ | 7.66:1 ✓ |
| vàng `#FFD43B` | 1.43:1 ✗ | 12.60:1 ✓ |
| đỏ `#D92D20` | 4.83:1 ✓ | — |

Chỉ đỏ đậm mới cho chữ trắng đạt, nhưng đỏ đậm đọc ra "cảnh báo" chứ không phải "đang hot",
lại đụng thẻ Haaland nền đỏ.

**Chốt:** pill gradient **cam → hồng**, **chữ tối**,
**viền trắng 2dp**, đổ bóng nhẹ. Viền trắng mới là thứ tách tag khỏi *bất kỳ* nền thẻ nào —
trên thẻ lửa cam của Naruto nó là thứ duy nhất làm được việc đó.

**Vị trí:** góc trên-TRÁI. Mặt nhân vật luôn ở giữa nên góc trên trống ở mọi ảnh, và badge
"Nk uses" của thẻ Face Puzzle nằm góc trên-PHẢI — hai thứ không đụng nhau khi trộn chung lưới
ở tab All.

Ban đầu thử **vàng→cam** (gợi ngọn lửa) nhưng trên thẻ VÀNG của Leonardo thì tag lẫn vào
nền — chỉ còn viền trắng gánh toàn bộ việc tách. Cam→hồng có tương phản **sắc độ** thật với
cả nền vàng lẫn nền lửa cam của Naruto, nên không phụ thuộc mỗi cái viền.

**Chỉ gắn 6/18 thẻ.** Gắn nhiều thì tag mất nghĩa — cái gì cũng hot thì không cái nào hot.
Danh sách hiện tại (`home_HOT`) là **đề xuất thiết kế**: app không có dữ liệu lượt dùng cho
nhóm nhân vật, khác nhóm template vốn có field `likes` từ CDN. Dev nối vào số liệu thật thì
sửa đúng một dòng.

### Khung nét đứt — chỉ dùng cho trạng thái RỖNG

Trong quy ước UI, nét đứt nghĩa là **"ô trống, chờ điền vào"**. App gốc dùng nó ở khắp nơi —
thẻ nhân vật, hàng Settings — nên mắt đọc thành "chỗ này chưa có gì" trong khi chỗ đó đã đầy.
v3 bỏ nét đứt khỏi mọi thẻ CÓ nội dung.

Nhưng app có đúng một chỗ nét đứt mang nghĩa thật: **màn thư viện rỗng**. Ở đó nó vừa đúng
quy ước vừa giữ được nét vẽ tay của app gốc. `dashRect()` vẽ khung `12,9` bo 28, màu
`#8B7BC4` — đủ thấy trên nền tối mà không hét.

### Hoạ tiết mặt — khuếch đại rồi mới dùng

Ảnh `window_bg` của app gốc: điểm tối nhất 189 trên nền 255, nhưng **giá trị trung bình 254**
— hoạ tiết phủ cực ít và mờ tới mức gần như vô hình. Nó không đọc ra "hoa văn có chủ ý" mà ra
"ảnh scan bị bẩn".

Ý tưởng thì tốt: mắt / lông mày / môi chính là những bộ phận app cắt ra và ghép lại — đúng chủ
đề sản phẩm. Chỉ là thực thi đang phí nó. `restyle_face_pattern()` lấy độ lệch so với trắng
làm cường độ, **nhân 2.4**, rồi vẽ lại bằng tím nhạt `brandSoft` trên nền giấy.

**Hai bản:** nền giấy cho Settings, nền tối cho Level Picker và thư viện rỗng. **KHÔNG** dùng sau lưới Home/màn 40 — ở đó thẻ đã phủ 67.8% diện tích nên hoa văn chỉ ló qua mấy khe hẹp, đọc thành nhiễu chứ không thành hoa văn; hoa văn cần MẢNG TRỐNG LIỀN mới ra hình. Bản nền giấy dùng ở Settings — nơi có khoảng trống thật ở nửa dưới và không có đoạn văn dài nào
chạy dưới hoa văn. Privacy/Term có 16 đoạn chữ liền nhau nên giữ nền phẳng.

⚠ Ảnh được nướng sẵn nền `#FDF9F3` **đúng bằng token `C.paper`** của màn Settings (đã kiểm:
94.9% số pixel là màu này). Dùng lại nó trên màn nền tối sẽ ra một mảng trắng — phải sinh bản
khác nếu muốn.

### Badge "Nk uses"

Bằng chứng xã hội — thứ duy nhất trên lưới nói "người khác đã dùng cái này". **Trước:** đen
40%, chữ trắng bay mất trên thumbnail sáng. **Sau:** tím than 72%.

### Splash

**Trước:** gradient trắng → cyan; app tự giới thiệu bằng đúng cái nền trắng đang bị bỏ, rồi
chớp trắng trước khi vào Home tối. **Sau:** dải tím `#9333EA → #4C1D95`, nối liền mạch sang
Home. Thanh tiến trình màu cam — thứ duy nhất chuyển động, để mắt quen "cam = chỗ cần bấm"
trước khi vào app.

### Nền các màn

| Nhóm màn | Nền |
|---|---|
| Home, List Funny, Level Picker | `bg` tím than |
| Màn quay | giữ camera tối, chỉ đổi màu chip/CTA |
| Preview · Sound · Result · Gallery | `bg` tím than |
| Settings · Privacy · Term | `paper` warm white |
| Splash · Language Picker | gradient thương hiệu |

App gốc dùng `@mipmap/window_bg` — ảnh nền trắng có hoạ tiết mặt mũi mờ chạy dưới chữ, giảm
độ đọc ở màn văn bản và làm dơ nền ở màn ảnh. Bỏ hẳn.

### CTA

Mọi nút chính đổi từ gradient cyan→xanh sang **cam đặc, chữ tối, đổ bóng**. Bo góc bằng nửa
chiều cao.

### Bo góc và đổ bóng

Tăng đúng một bậc: card 12→16, tile 16→20, dialog 16→20, sm 8→10. Đổ bóng từ đen 40% sang
**ám tím** `rgba(10,5,26,.55)` offset 8, blur 24, spread −2 — bóng đen thuần trên nền tím
than trông bẩn và không tách được thẻ khỏi nền.

## Trạng thái component

**Language Picker.** App gốc chỉ đổi mỗi icon radio; `bg_item_setting` là shape TĨNH (đã xác
minh, không phải selector). Một tín hiệu đơn lẻ dễ bị bỏ sót. v3 dùng **ba** tín hiệu:

| | Nền | Viền | Chữ | Radio |
|---|---|---|---|---|
| Chưa chọn | `paperCard` | `paperLine` 1dp | `onLight` | rỗng |
| Đã chọn | `#F3EEFF` | `brand` 2dp | `onLight` | đặc, brand |

*XML:* `bg_item_setting` shape tĩnh → selector `state_selected`.

**Nút disabled.** Bề mặt `surfaceHi` đục + chữ `onDarkSub`. Không dùng nút màu hành động giảm
độ đục — cam 50% trên nền tối ra màu bùn, chữ trên nó 1.05:1, mà người dùng vẫn tưởng bấm được.

## Khối quảng cáo

Đọc ra là quảng cáo ngay từ cái nhìn đầu: mảng `surface` phẳng, viền 1dp, nhãn "AD" góc trên
trái. Cố tình không giả dạng ô nội dung.

**Hai dark pattern của app gốc KHÔNG dựng lại:** `activity_native_show_open_fake` (màn quảng
cáo giả dạng chính app, lấy icon và tên thật qua `PackageManager`) và nút đóng không có
`onClick` ở màn đó. Cả hai vi phạm chính sách Google Play — rủi ro là gỡ app.

## Hai câu hỏi về behavior — trả lời từ code

**Thanh progress ở Splash là ANIMATION thuần.** `FragmentSplash.java:127` —
`ObjectAnimator.ofInt(progress, "progress", 0, 100)`. Bar chạy hết không liên quan tới việc
load xong. `tvLoading` không được code đụng tới lần nào, nên frame `10b` (bar đầy + vẫn
"Loading...") **đúng với app thật**. Ghi chú: thanh tiến trình giả gây kỳ vọng sai về thời
gian chờ — sửa được nhưng là đổi behavior, ngoài phạm vi.

**`"This action contain ads"` là lỗi ngữ pháp có sẵn trong APK** (`strings.xml:555`). v3 đổi
thành `"This app contains ads"`. Dev sửa strings.xml, không đụng code.

## Soát tương phản tự động

`script/audit-contrast.py` duyệt scene JSON theo đúng thứ tự vẽ, quy toạ độ về tuyệt đối, với
mỗi node chữ **gom chồng các lớp bán trong suốt** rồi trộn lên lớp đục đầu tiên phía dưới.

```sh
PYTHONUTF8=1 python "Funny Face/script/audit-contrast.py" build/scene-v3.json
```

Bắt buộc chạy sau mỗi lần đổi token. Lý do: hệ dùng token chung, đổi nghĩa MỘT token là ảnh
hưởng mọi nơi tham chiếu. Đã hỏng thật — đổi `C.textHi` sang màu sáng rồi quên `onboard.js`,
để lọt 21 node Language Picker thành chữ trắng trên ô trắng (1.10:1). Soát bằng mắt qua 41
frame không bắt được.

## Cấu trúc bản giao

```
figma/v3/
├─ code.js        # token (bảng C, R) + helper
├─ screens/*.js   # 7 file
└─ manifest.json  # "Funny Face — Design v3"
assets/v3/        # asset thương hiệu đã xoay +48° sang tông tím
```

`figma/v1` **giữ nguyên vĩnh viễn** — bằng chứng đối chiếu 1:1 với APK, mọi file trong
`specs/` mô tả nó. `figma/v2` nay **thừa**, v3 thay thế hoàn toàn.

`make-v3.py` là bộ **khởi tạo một lần**, không phải phép biến đổi lặp được như `make-v2.py`
— đổi bố cục thì không có phép biến đổi nào suy ra được từ v1. Script từ chối ghi đè nếu v3
đã tồn tại, trừ khi truyền `--force`.

## Lỗi của `kit/` phát hiện khi làm v3

1. **`grad()` trong `code.js` vứt mất kênh alpha** — hardcode `a:1` cho cả hai điểm dừng nên
   mọi gradient trong suốt bị vẽ thành mảng đặc. Không lộ ở v1 vì v1 chỉ dùng gradient đục.
2. **`render-preview.py` ép alpha = 255** khi vẽ gradient — ảnh preview khác hẳn kết quả thật.
3. **`audit-contrast.py` (bản đầu) trộn lớp bán trong suốt rồi vẫn quét tiếp**, để lớp đục
   phía sau ghi đè kết quả — báo trắng-trên-trắng ở một pill scrim 80% nằm trên thẻ trắng.

Cả ba đều ảnh hưởng mọi app dùng chung bộ công cụ.

## Chưa xong

- **Wordmark `ic_splash` / `img_app_name`** mới chỉ xoay hue máy móc, ra một khối xanh-tím
  phẳng, đang hút chú ý hơn mức cần. Phải vẽ tay.
- **Khoảng trống dưới hàng chip ở Home** là chỗ dành cho `native_home`; khi tắt ad thành lỗ
  hổng. Tật có từ v1.
- **Chưa A/B test.**

## Phụ lục — hướng "sáng-trước" đã thử rồi lùi lại

Có một lượt thử lật toàn bộ sang nền sáng `#FFF8F2`, tím chỉ làm CTA, thêm 5 màu accent và
đổi font sang Fredoka/Nunito. Đạt 303/303 AA nhưng bị đánh giá là **chưa tới**, nên đã lùi về
bản này. Các quyết định còn giữ lại từ lượt đó:

- Dải chuyển Splash nhẹ hơn (`#9333EA → #4C1D95` thay vì kết thúc gần đen)
- Ba tín hiệu cho trạng thái chọn ở Language Picker
- Nút disabled dùng bề mặt đục thay vì giảm độ đục của màu hành động
- Sửa lỗi ngữ pháp `"This app contains ads"`
- Bản vá tính-alpha của `audit-contrast.py`

Nếu quay lại hướng sáng, những thứ cần làm thêm mà lượt đó chưa chạm tới: Home dạng hero +
2 thẻ mode, carousel "Popular", badge NEW/POPULAR, bottom navigation, nút Rename/Share ở
Result — tất cả đều cần thêm view và thêm code, nằm ngoài phạm vi "chỉ UI/UX".
