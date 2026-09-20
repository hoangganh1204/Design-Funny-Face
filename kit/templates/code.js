// ============================================================================
//  <App> — APK → Figma reconstruction (v1)   [TEMPLATE — fill C, FONTS, screens]
//  Canvas 360×800 dp. No status bar. Requires assets.js + icons.js concatenated ABOVE
//  (build-plugin.py produces plugin.js = assets.js + icons.js + this file).
//  Every layer must trace to one XML view or one code instruction — else delete it.
// ============================================================================
const C = {                                   // ← fill from resolved layouts (measure real hexes)
  bg: '121212', black: '000000', white: 'ffffff',
  toolbar: '1c1b1f', card: '1e1e1e',
  toolbarDiv: '4dffffff', settingDiv: '1affffff',
  textHi: 'ffffff', sub: 'b3b3b3', sub2: '808080',
  accent: 'ffcd6a', accentB: 'ffdb76',        // brand color(s) — measure, don't trust colorPrimary
  green: '1d873b', red: 'd93025',
};
const R = { card: 12, tile: 16, pill: 30, sm: 8, dialog: 16 };
// Map each @font/*.ttf → a Figma-available family (Google Fonts). Figma has NO auto-fallback.
const FONTS = {
  main:    { family: 'Roboto',  w: { 400: 'Regular', 500: 'Medium', 700: 'Bold' } },
  // add: heading/stencil/digital/CJK families as the app uses them
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
function adSlot(parent,x,y,w,h,label){const g=frame('AD SLOT · '+(label||'Native'),x,y,w,h,{fill:'1a1a1a',stroke:'3a3a3a',strokeW:1,radius:8});add(g,text('AD · '+(label||''),0,h/2-8,{size:12,font:'main',color:'6a6a6a',w:w,align:'CENTER'}));add(parent,g);return g;}
// scrim + centered dialog card; use one artboard per dialog
function dcard(f,w,h,o){o=o||{};add(f,rect('scrim',0,0,SCREEN_W,SCREEN_H,{fill:'000000',opacity:o.scrim!==undefined?o.scrim:0.6}));const y=o.y!==undefined?o.y:(SCREEN_H-h)/2;const d=frame(o.name||'dialog',(SCREEN_W-w)/2,y,w,h,{fill:o.fill||C.card,radius:o.radius!==undefined?o.radius:R.dialog,shadow:true,clip:true});add(f,d);return d;}
function sheet(f,h,o){o=o||{};add(f,rect('scrim',0,0,SCREEN_W,SCREEN_H,{fill:'000000',opacity:o.scrim!==undefined?o.scrim:0.6}));const d=frame(o.name||'sheet',0,SCREEN_H-h,SCREEN_W,h,{fill:o.fill||C.card,radiusTop:o.radius!==undefined?o.radius:20,clip:true});add(f,d);return d;}

const SCREENS=[],DIALOGS=[];
function screen(name,note,build){SCREENS.push({name,note,build});}
function dialog(name,note,build){DIALOGS.push({name,note,build});}

// ============================== SCREENS =====================================
// One builder per screen (and per runtime STATE). Every value from the resolved layout/code.
// Example — delete and replace with the real screens:
screen('00 · Example', 'Fragment X · note the real source (file:line)', (f) => {
  add(f, rect('bg', 0, 0, SCREEN_W, SCREEN_H, { fill: C.bg }));
  toolbar(f, 'Title');
  // add(f, text(...)), add(f, img(...)), photo(f, ...), adSlot(f, ...) — trace each to code.
  // for tall content: grow(f, y + pad);
});

// ============================== Main ========================================
async function buildPage(title,list){const page=figma.createPage();page.name=title;const GAP_X=60,GAP_Y=120,PER_ROW=6;const built=list.map(s=>{const f=frame(s.name,0,0,SCREEN_W,SCREEN_H,{fill:C.bg,clip:true});try{s.build(f);}catch(e){add(f,text('BUILD ERR: '+s.name+' — '+e.message,8,8,{size:11,color:'ff5555',w:SCREEN_W-16}));}f.setPluginData('source',s.note||'');page.appendChild(f);return f;});let y=0;for(let i=0;i<built.length;i+=PER_ROW){const row=built.slice(i,i+PER_ROW);let tall=0;row.forEach((f,j)=>{f.x=j*(SCREEN_W+GAP_X);f.y=y;if(f.height>tall)tall=f.height;});y+=tall+GAP_Y;}return page;}
async function main(){if(figma.loadAllPagesAsync)await figma.loadAllPagesAsync();const fams={};Object.keys(FONTS).forEach(k=>{fams[FONTS[k].family]=FONTS[k].w;});for(const fam of Object.keys(fams)){LOADED[fam]={};for(const st of new Set(Object.values(fams[fam]))){try{await figma.loadFontAsync({family:fam,style:st});LOADED[fam][st]=true;}catch(e){}}}try{await figma.loadFontAsync({family:'Roboto',style:'Regular'});LOADED['Roboto']={Regular:true};}catch(e){}const p1=await buildPage('📱 <App> · Screens',SCREENS);await buildPage('💬 <App> · Dialogs & States',DIALOGS);await figma.setCurrentPageAsync(p1);figma.viewport.scrollAndZoomIntoView(p1.children);figma.closePlugin('<App>: '+SCREENS.length+' screens + '+DIALOGS.length+' dialogs/states.');}
main();
