#!/usr/bin/env node
/**
 * verify.js — chạy plugin Figma trong Node và kiểm tra những thứ mắt thường bỏ sót.
 *
 *   node tools/verify.js figma-plugin/plugin.js
 *
 * Kiểm tra:
 *   1. Chạy không lỗi runtime
 *   2. Asset audit   — mọi ảnh/icon code gọi đều tồn tại trong bundle
 *   3. Unused audit  — asset nhúng nhưng không dùng (làm phình bundle)
 *   4. Overlap test  — không frame nào đè lên frame khác
 *   5. Empty text    — không text node nào rỗng (dấu hiệu thiếu font/dữ liệu)
 *
 * Thoát mã 1 nếu có lỗi, để cắm được vào CI.
 */
const path = require('path');
const fs = require('fs');

const target = process.argv[2] || 'figma-plugin/plugin.js';
require(path.resolve(__dirname, 'figma-mock.js'));

const missingImg = [], usedImg = new Set();
const missingIcon = [], emptyText = [];

global.__auditImg = (n, ok) => (ok ? usedImg.add(n) : missingImg.push(n));
global.__auditIcon = (n, ok) => { if (!ok) missingIcon.push(String(n)); };

let src = fs.readFileSync(path.resolve(target), 'utf8');
// Khớp bằng REGEX, không phụ thuộc cách đặt dấu cách — code.js của kit viết dạng nén
// (`function imageFill(name,scaleMode){`) nên phép thay theo chuỗi có dấu cách luôn trượt,
// khiến audit asset/unused im lặng không chạy. (bug kit, phát hiện khi dựng Funny Face)
function inject(src, re, add, label) {
  const m = src.match(re);
  if (!m) { console.error(`verify.js: KHÔNG hook được ${label} — audit này sẽ không chạy`); return src; }
  return src.replace(re, (hit) => hit + add);
}
src = inject(src, /function\s+imageFill\s*\([^)]*\)\s*\{/,
  ' __auditImg(name, typeof ASSETS !== "undefined" && !!ASSETS[name]);', 'imageFill');
src = inject(src, /function\s+svgNode\s*\([^)]*\)\s*\{/,
  ' __auditIcon(name, typeof ICONS !== "undefined" && !!ICONS[name]);', 'svgNode');
// __A phải gán SAU khai báo const ASSETS (nếu đặt đầu file sẽ dính temporal dead zone),
// nên chèn ngay TRƯỚC định nghĩa main() — chỗ này chắc chắn đã qua mọi khai báo.
{
  const re = /async\s+function\s+main\s*\(\s*\)\s*\{/;
  if (re.test(src)) {
    src = src.replace(re, (hit) =>
      'global.__A = typeof ASSETS !== "undefined" ? ASSETS : {};\n' + hit);
  } else {
    console.error('verify.js: KHÔNG hook được main — audit unused-asset sẽ không chạy');
  }
}

eval(src);

setTimeout(() => {
  const r = global.__report();
  const fail = [];

  // --- 2. asset audit
  const missImg = [...new Set(missingImg)];
  const missIcon = [...new Set(missingIcon)].filter((n) => n !== 'undefined');
  if (missImg.length) fail.push('Thiếu ảnh: ' + missImg.join(', '));
  if (missIcon.length) fail.push('Thiếu icon: ' + missIcon.join(', '));

  // --- 3. unused audit (cảnh báo, không fail)
  const unused = Object.keys(global.__A).filter((k) => !usedImg.has(k));

  // --- 4. overlap
  const pages = r.pages || [];
  let overlaps = 0;
  pages.forEach((p) => {
    const fr = p.children.filter((n) => n.type === 'FRAME');
    for (let a = 0; a < fr.length; a++) {
      for (let b = a + 1; b < fr.length; b++) {
        const A = fr[a], B = fr[b];
        if (A.x < B.x + B.width && B.x < A.x + A.width &&
            A.y < B.y + B.height && B.y < A.y + A.height) {
          if (overlaps < 5) fail.push(`Frame đè nhau: "${A.name}" × "${B.name}"`);
          overlaps++;
        }
      }
    }
  });

  // --- 5. empty text
  const walk = (n) => {
    if (n.type === 'TEXT' && !String(n.characters || '').trim()) emptyText.push(n.name || '(vô danh)');
    (n.children || []).forEach(walk);
  };
  pages.forEach(walk);
  if (emptyText.length) fail.push('Text rỗng: ' + emptyText.slice(0, 5).join(', '));

  console.log('─'.repeat(58));
  console.log(`nodes ${r.nodeCount} · images ${r.imageCount} · svg ${r.svgCount} · text ${r.textCount}`);
  pages.forEach((p) => console.log(`  page "${p.name}" → ${p.children.length} phần tử`));
  if (unused.length) console.log(`⚠ ${unused.length} asset nhúng nhưng không dùng: ${unused.slice(0, 10).join(', ')}${unused.length > 10 ? '…' : ''}`);
  console.log('─'.repeat(58));

  if (fail.length) {
    fail.forEach((m) => console.error('✗ ' + m));
    process.exit(1);
  }
  console.log('✓ asset đầy đủ · không frame nào đè nhau · không text rỗng');
  console.log('\n⚠ NHẮC: đây chỉ là kiểm tra cấu trúc.');
  console.log('  Vẫn PHẢI render ra và so bằng mắt với ảnh chụp app thật.');
}, 3500);
