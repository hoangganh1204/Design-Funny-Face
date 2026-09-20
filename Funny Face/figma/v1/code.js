// ============================================================================
//  Funny Face — APK → Figma reconstruction (v1)   [TEMPLATE — fill C, FONTS, screens]
//  Canvas 360×800 dp. No status bar. Requires assets.js + icons.js concatenated ABOVE
//  (build-plugin.py produces plugin.js = assets.js + icons.js + this file).
//  Every layer must trace to one XML view or one code instruction — else delete it.
// ============================================================================
const C = {                                   // đo từ res/values/colors.xml (đã resolve)
  primary:  '016cf7',   // primary_color — brand xanh dương
  white:    'ffffff',   // white / secondary_color
  black:    '000000',
  textHi:   '171716',   // text_primary_color — màu chữ mặc định của theme
  textSub:  '999894',   // text_secondary_color
  textHint: 'bab8b6',   // text_hint_color
  text2:    'a3a3a3',   // color_second_text
  gray:     'c0c0c0', grayDark: '6d6969', gray9d: '9d9d9d',
  grayF4:   'f4f4f4', grayF5EEE9: 'f5eee9', e6e6e5: 'e6e6e5',
  dark141414: '141414', dark2D: '2d2d2d',
  scrim20:  '33000000', scrim30: '4d000000', scrimA6: 'a61f1e26',
  red:      'ff4342',   // color_FF4342
  orange:   'f19336',   // color_bottom_green (tên sai, giá trị là cam)
  transparent: '00ffffff',
};
const R = { card: 12, tile: 16, pill: 30, sm: 8, dialog: 16, r12: 12, r69: 69 };
// Theme: Base.Theme.FacePuzzle parent Theme.AppCompat.Light.NoActionBar → nền SÁNG.
// windowBackground = @mipmap/window_bg (đã export assets/v1/40-anh-app/window_bg.png)
// android:fontFamily mặc định = @font/lato_regular_400 ; android:textSize = 14sp
const FONTS = {                               // res/font/*.ttf → family Figma (đều là Google Fonts)
  main:       { family: 'Lato',       w: { 100:'Thin', 300:'Light', 400:'Regular', 600:'SemiBold', 700:'Bold', 900:'Black' } },
  inter:      { family: 'Inter',      w: { 400:'Regular', 700:'Bold' } },
  montserrat: { family: 'Montserrat', w: { 400:'Regular', 600:'SemiBold' } },
  nunito:     { family: 'Nunito',     w: { 700:'Bold', 900:'Black' } },
  onest:      { family: 'Onest',      w: { 700:'Bold' } },
  poppins:    { family: 'Poppins',    w: { 400:'Regular', 500:'Medium' } },
  roboto:     { family: 'Roboto',     w: { 500:'Medium' } },
};
const DEFAULT_FONT = 'main';
const SCREEN_W = 360, SCREEN_H = 800;
const LOADED = {};

function rgb(h){h=h.replace('#','');if(h.length===3)h=h.split('').map(c=>c+c).join('');if(h.length===8)h=h.slice(2);return{r:parseInt(h.slice(0,2),16)/255,g:parseInt(h.slice(2,4),16)/255,b:parseInt(h.slice(4,6),16)/255};}
function alphaOf(h){h=h.replace('#','');return h.length===8?parseInt(h.slice(0,2),16)/255:undefined;}
function solid(h,o){const a=o!==undefined?o:alphaOf(h);const p={type:'SOLID',color:rgb(h)};if(a!==undefined)p.opacity=a;return p;}
function grad(a,b,dir){const t=dir==='h'?[[1,0,0],[0,1,0]]:[[0,1,0],[-1,0,1]];return[{type:'GRADIENT_LINEAR',gradientTransform:t,gradientStops:[{position:0,color:Object.assign(rgb(a),{a:1})},{position:1,color:Object.assign(rgb(b),{a:1})}]}];}
const imgCache={};
function imageFill(name,scaleMode){if(typeof ASSETS==='undefined'||!ASSETS[name])return null;if(!imgCache[name]){const b=figma.base64Decode?figma.base64Decode(ASSETS[name]):Uint8Array.from(atob(ASSETS[name]),c=>c.charCodeAt(0));imgCache[name]=figma.createImage(b).hash;}return{type:'IMAGE',scaleMode:scaleMode||'FILL',imageHash:imgCache[name]};}
function pickFont(fk,weight){const def=FONTS[fk]||FONTS[DEFAULT_FONT];const fam=def.family,want=def.w[weight||400]||def.w[400]||'Regular';if(LOADED[fam]){if(LOADED[fam][want])return{family:fam,style:want};if(LOADED[fam].Regular)return{family:fam,style:'Regular'};const any=Object.keys(LOADED[fam])[0];if(any)return{family:fam,style:any};}const d=FONTS[DEFAULT_FONT].family;if(LOADED[d]&&LOADED[d].Regular)return{family:d,style:'Regular'};return{family:'Roboto',style:'Regular'};}
function frame(name,x,y,w,h,o){o=o||{};const f=figma.createFrame();f.name=name;f.x=x;f.y=y;f.resize(Math.max(w,0.01),Math.max(h,0.01));f.fills=o.fill?[solid(o.fill,o.opacity)]:[];if(o.gradient)f.fills=grad(o.gradient[0],o.gradient[1],o.gradientDir);if(o.image){const p=imageFill(o.image,o.scaleMode);if(p)f.fills=[p];}if(o.radius!==undefined)f.cornerRadius=o.radius;if(o.radiusTop!==undefined){f.topLeftRadius=o.radiusTop;f.topRightRadius=o.radiusTop;}if(o.stroke){f.strokes=[solid(o.stroke,o.strokeOpacity)];f.strokeWeight=o.strokeW||1;}if(o.shadow)f.effects=[{type:'DROP_SHADOW',color:{r:0,g:0,b:0,a:o.shadow===true?0.4:o.shadow},offset:{x:0,y:6},radius:16,spread:0,visible:true,blendMode:'NORMAL'}];if(o.clip!==undefined)f.clipsContent=o.clip;return f;}
function rect(name,x,y,w,h,o){o=o||{};const r=figma.createRectangle();r.name=name;r.x=x;r.y=y;r.resize(Math.max(w,0.01),Math.max(h,0.01));r.fills=o.fill?[solid(o.fill,o.opacity)]:[];if(o.gradient)r.fills=grad(o.gradient[0],o.gradient[1],o.gradientDir);if(o.image){const p=imageFill(o.image,o.scaleMode);if(p)r.fills=[p];}if(o.radius!==undefined)r.cornerRadius=o.radius;if(o.stroke){r.strokes=[solid(o.stroke,o.strokeOpacity)];r.strokeWeight=o.strokeW||1;}if(o.rotate)r.rotation=o.rotate;return r;}
function ellipse(name,x,y,w,h,o){o=o||{};const e=figma.createEllipse();e.name=name;e.x=x;e.y=y;e.resize(w,h);e.fills=o.fill?[solid(o.fill,o.opacity)]:[];if(o.image){const p=imageFill(o.image,o.scaleMode);if(p)e.fills=[p];}if(o.gradient)e.fills=grad(o.gradient[0],o.gradient[1],o.gradientDir);if(o.stroke){e.strokes=[solid(o.stroke,o.strokeOpacity)];e.strokeWeight=o.strokeW||1;}return e;}
function text(chars,x,y,o){o=o||{};const t=figma.createText();t.fontName=pickFont(o.font,o.weight);t.characters=chars;t.fontSize=o.size||14;t.fills=o.gradient?grad(o.gradient[0],o.gradient[1],o.gradientDir||'v'):[solid(o.color||C.textHi,o.opacity)];t.x=x;t.y=y;if(o.w){t.textAutoResize=o.h?'NONE':'HEIGHT';t.resize(o.w,o.h||Math.max(t.height,1));}else t.textAutoResize='WIDTH_AND_HEIGHT';if(o.align)t.textAlignHorizontal=o.align;if(o.valign)t.textAlignVertical=o.valign;if(o.lineHeight)t.lineHeight={value:o.lineHeight,unit:'PIXELS'};if(o.rotate)t.rotation=o.rotate;t.name=chars.length>26?chars.slice(0,26)+'…':chars;return t;}
function textC(chars,y,o){o=Object.assign({w:SCREEN_W,align:'CENTER'},o||{});return text(chars,0,y,o);}
function img(name,x,y,w,h,mode){return rect(name,x,y,w,h,{image:name,scaleMode:mode||'FIT'});}
function svgNode(name,x,y,w,h){if(typeof ICONS==='undefined'||!ICONS[name])return null;const n=figma.createNodeFromSvg(ICONS[name]);n.name=name;n.x=x;n.y=y;n.resize(w,h);return n;}
function icon(name,x,y,w,h){const s=svgNode(name,x,y,w,h);if(s)return s;if(typeof ASSETS!=='undefined'&&ASSETS[name])return img(name,x,y,w,h,'FIT');return null;}
function add(parent){for(let i=1;i<arguments.length;i++)if(arguments[i])parent.appendChild(arguments[i]);return parent;}
function grow(f,h){if(h>f.height)f.resize(SCREEN_W,h);}
function vpath(parent,x,y,w,h,vb,d,o){o=o||{};const svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+vb+'"><path d="'+d+'" fill="'+(o.fill?'#'+o.fill:'none')+'"'+(o.stroke?' stroke="#'+o.stroke+'" stroke-width="'+(o.sw||2)+'" stroke-linecap="round" stroke-linejoin="round"':'')+'/></svg>';const n=figma.createNodeFromSvg(svg);n.name=o.name||'icon';n.x=x;n.y=y;n.resize(w,h);add(parent,n);return n;}
function backChevron(p,x,y,s,c){return vpath(p,x,y,s,s,'24 24','M15 5 L8 12 L15 19',{stroke:c||C.white,sw:2.4,name:'ic_back'});}
// image placeholder for remote/runtime content that isn't in the APK (label it honestly)
function remoteTile(parent,x,y,w,h,label,r){const g=frame('remote · '+(label||''),x,y,w,h,{fill:'242424',stroke:'3a3a3a',strokeW:1,radius:r!==undefined?r:8,clip:true});add(parent,g);add(g,text(label||'remote',0,h/2-8,{size:10,font:'main',color:'6a6a6a',w:w,align:'CENTER'}));return g;}
// real photo (downloaded asset) or fallback placeholder
function photo(parent,x,y,w,h,key,mode,r){if(typeof ASSETS!=='undefined'&&ASSETS[key]){const n=rect(key,x,y,w,h,{image:key,scaleMode:mode||'FILL',radius:r});add(parent,n);return n;}return remoteTile(parent,x,y,w,h,key,r);}
// toolbar: back + centered title + optional right text/gear. Match the app's real toolbar geometry.
function toolbar(parent,title,o){o=o||{};const h=o.h||56;const g=frame('Toolbar · '+(title||''),0,0,SCREEN_W,h,o.transparent?{}:{fill:o.fill||C.toolbar});if(o.back!==false){const ic=icon('ic_back',20,(h-24)/2,24,24);if(ic)add(g,ic);else backChevron(g,20,(h-22)/2,22,C.white);}if(title)add(g,text(title,52,0,{size:o.size||18,font:o.font||'main',weight:700,color:C.textHi,w:SCREEN_W-104,h:h,valign:'CENTER',align:'CENTER'}));if(o.rightText)add(g,text(o.rightText,SCREEN_W-80,0,{size:o.rightSize||15,font:'main',weight:700,color:o.rightColor||C.accent,w:60,h:h,valign:'CENTER',align:'RIGHT'}));if(!o.transparent&&o.divider!==false)add(g,rect('divider',0,h-1,SCREEN_W,1,{fill:C.toolbarDiv}));add(parent,g);return g;}
// AD SLOT placeholder (native/banner filled at runtime — not in the APK)
function adSlot(parent,x,y,w,h,label){if(!SHOW_ADS)return null;const g=frame('AD SLOT · '+(label||'Native'),x,y,w,h,{fill:'1a1a1a',stroke:'3a3a3a',strokeW:1,radius:8});add(g,text('AD · '+(label||''),0,h/2-8,{size:12,font:'main',color:'6a6a6a',w:w,align:'CENTER'}));add(parent,g);return g;}
// scrim + centered dialog card; use one artboard per dialog
function dcard(f,w,h,o){o=o||{};add(f,rect('scrim',0,0,SCREEN_W,SCREEN_H,{fill:'000000',opacity:o.scrim!==undefined?o.scrim:0.6}));const y=o.y!==undefined?o.y:(SCREEN_H-h)/2;const d=frame(o.name||'dialog',(SCREEN_W-w)/2,y,w,h,{fill:o.fill||C.card,radius:o.radius!==undefined?o.radius:R.dialog,shadow:true,clip:true});add(f,d);return d;}
function sheet(f,h,o){o=o||{};add(f,rect('scrim',0,0,SCREEN_W,SCREEN_H,{fill:'000000',opacity:o.scrim!==undefined?o.scrim:0.6}));const d=frame(o.name||'sheet',0,SCREEN_H-h,SCREEN_W,h,{fill:o.fill||C.card,radiusTop:o.radius!==undefined?o.radius:20,clip:true});add(f,d);return d;}

// ─── Công tắc quảng cáo ──────────────────────────────────────────────────────
// false = bản GỌN để trình bày: bỏ mọi ô quảng cáo và mọi frame chỉ-để-hiện-ad.
// true  = bản TRUNG THỰC 1:1 với app (ad là phần có thật của UI, Plan 1 yêu cầu dựng).
// Đổi 1 dòng này rồi build lại là chuyển qua lại, KHÔNG mất frame nào.
const SHOW_ADS = false;

// 7 ngon ngu hardcode, DUNG THU TU (data/system/AppSetting.java:44).
// De o code.js chu khong trong screens/onboard.js vi CA hai noi dung: man 12/12b/12c
// (cum onboard) va D71 (cum settings-dialogs). Truoc day D71 tu khai bao lai 2 dong
// ['English','Hindi'] cho "minh hoa" -> nhin vao tuong app chi co 2 ngon ngu.
const LANGS = [
  ['English', 'en'], ['Hindi', 'hi'], ['Spanish', 'es'], ['French', 'fr'],
  ['Portuguese', 'pt'], ['Vietnamese', 'vi'], ['Japanese', 'ja'],
];

const SCREENS=[],DIALOGS=[];
// opts.adOnly = frame này KHÔNG còn gì khi tắt ad (toàn bộ nội dung là quảng cáo)
//               -> bỏ hẳn khỏi registry khi SHOW_ADS=false.
// opts.adDup  = frame này chỉ khác một frame khác ở chỗ CÓ ad -> trùng lặp khi tắt ad.
// opts.excluded = design lead YÊU CẦU BỎ khỏi bản trình bày. Code vẫn giữ nguyên,
//                 bỏ cờ là frame quay lại. Ghi lý do vào note để không ai tưởng là sót.
function screen(name,note,build,opts){opts=opts||{};if(opts.excluded)return;if(!SHOW_ADS&&(opts.adOnly||opts.adDup))return;SCREENS.push({name,note,build});}
function dialog(name,note,build,opts){opts=opts||{};if(opts.excluded)return;if(!SHOW_ADS&&(opts.adOnly||opts.adDup))return;DIALOGS.push({name,note,build});}

// ============================== SCREENS =====================================
// One builder per screen (and per runtime STATE). Every value from the resolved layout/code.
// Builder mỗi màn nằm ở figma/v1/screens/*.js (build-plugin ghép vào đây).

const BUILT_BY = 'funny-face-apk-to-figma';
// Chạy lại plugin nhiều lần phải RA CÙNG KẾT QUẢ, không chồng thêm bộ frame mới.
// Cách làm: đánh dấu mọi frame plugin tạo bằng pluginData BUILT_BY, và khi chạy thì
// XOÁ hết frame mang dấu đó trước (trên mọi trang), đồng thời TÁI DÙNG trang cùng tên
// thay vì tạo trang mới (gói Starter chỉ cho 3 trang/file).
async function clearPrevious(){
  const pages = figma.root.children;
  for (const pg of pages) {
    if (pg.loadAsync) { try { await pg.loadAsync(); } catch (e) {} }
    for (const n of pg.children.slice()) {
      try {
        const marked = n.getPluginData && n.getPluginData('builtBy') === BUILT_BY;
        // Frame do các bản plugin CŨ tạo ra KHÔNG có dấu builtBy -> phải nhận thêm bằng
        // TÊN. Quy ước đặt tên của plugin: "<mã> · <tên màn>" với mã dạng 10 / 10b / 41g /
        // D51 / 90. Mẫu này đủ hẹp để không đụng layer người dùng tự vẽ.
        const legacy = typeof n.name === 'string' && /^D?\d{1,3}[a-z]?\s·\s/.test(n.name);
        if (marked || legacy) n.remove();
      } catch (e) {}
    }
  }
}
// clearPrevious() chi go FRAME, nen trang do ban plugin DOI TRUOC tao ra (tieu de khac di
// mot chut -> findOrCreatePage khong nhan ra de gop) se nam lai duoi dang TRANG RONG. Chay
// nhieu lan thi panel Pages day nhung trang '📱'/'💬' trung nhau. Ham nay don chung, va CHI
// don trang that su rong -> khong bao gio dung vao trang nguoi dung tu tao co noi dung.
function removeStalePages(keep){
  const ours = /Funny Face|📱|💬/;
  for (const pg of figma.root.children.slice()) {
    try {
      if (keep.indexOf(pg) !== -1) continue;
      if (!ours.test(pg.name)) continue;
      if (pg.children && pg.children.length) continue;
      if (figma.root.children.length <= 1) break;   // Figma luon can it nhat 1 trang
      pg.remove();
    } catch (e) {}
  }
}
function findOrCreatePage(title){
  const found = figma.root.children.filter(p => p.name === title);
  if (found.length) {
    for (let k = 1; k < found.length; k++) { try { found[k].remove(); } catch (e) {} }
    return found[0];
  }
  const p = figma.createPage(); p.name = title; return p;
}
// Thu tu tren canvas: theo SO MAN, khong theo thu tu file nguon duoc noi.
// Truoc day SCREENS giu nguyen thu tu dang ky -> build-plugin.py noi screens/*.js theo alphabet
// (face-puzzle, funny-puzzle, home, onboard, ...) nen canvas ra 30 -> 40 -> 20 -> 10 -> 50:
// Splash nam giua thay vi dau. Sap lai cho doc duoc tu trai sang phai, tren xuong duoi.
function flowKey(name){
  const m = /^D?(\d+)([a-z]*)/.exec(String(name || ''));
  return m ? [parseInt(m[1], 10), m[2] || ''] : [9999, ''];
}
function flowOrder(list){
  return list.slice().sort((a, b) => {
    const x = flowKey(a.name), y = flowKey(b.name);
    return x[0] - y[0] || (x[1] < y[1] ? -1 : x[1] > y[1] ? 1 : 0);
  });
}
// Dan luoi: 6 frame/hang. Neu danh sach du dai thi moi NHOM LUONG (chuc: 10 onboarding,
// 20 home, 25 preview Try Now, 30 face puzzle, 40 funny, 50 preview+sound, 60 result,
// 70 settings) bat dau o
// hang moi -> nhin phat ra ngay ranh gioi tung luong.
function layoutGrid(built, y0){
  const GAP_X = 60, GAP_Y = 120, PER_ROW = 6;
  const group = built.length > 8;
  let y = y0 || 0, col = 0, tall = 0, dec = null;
  built.forEach((f) => {
    // Chia theo KHOI 5 chu khong phai khoi 10: 10-14 onboarding · 20-24 home ·
    // 25-29 preview Try Now · 30-34 face puzzle · 40-44 funny · 50-54 preview+sound ·
    // 60-64 result · 70-74 settings. Khoi 10 se gop 25 chung hang voi 20a..20e -> tran hang.
    const d = Math.floor(flowKey(f.name)[0] / 5);
    if (col >= PER_ROW || (group && dec !== null && d !== dec)) {
      y += tall + GAP_Y; col = 0; tall = 0;
    }
    dec = d;
    f.x = col * (SCREEN_W + GAP_X); f.y = y;
    if (f.height > tall) tall = f.height;
    col += 1;
  });
  return y + tall + GAP_Y;
}
async function buildPage(title,list){const page=findOrCreatePage(title);const built=flowOrder(list).map(s=>{const f=frame(s.name,0,0,SCREEN_W,SCREEN_H,{fill:C.bg,clip:true});try{s.build(f);}catch(e){add(f,text('BUILD ERR: '+s.name+' — '+e.message,8,8,{size:11,color:'ff5555',w:SCREEN_W-16}));}f.setPluginData('source',s.note||'');f.setPluginData('builtBy',BUILT_BY);page.appendChild(f);return f;});layoutGrid(built,0);return page;}
