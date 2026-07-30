# Output Format(HTML)

最终交付物:`<论文标题>-bilingual.html` + 同目录 `assets/` 资源文件夹。将技能自带的 `Geist-VariableFont_wght.ttf` 与 `IBMPlexSerif-Italic.ttf` 复制到该目录。HTML 为左右对照布局:左栏英文原文,右栏中文译文;插图通栏插入原文位置;参考文献通栏单栏保持英文原状。

## 文件骨架

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>论文标题 - Bilingual (EN/ZH)</title>
<style>
@font-face {
  font-family: "Geist";
  src: url("assets/Geist-VariableFont_wght.ttf") format("truetype");
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
}
@font-face {
  font-family: "IBM Plex Serif";
  src: url("assets/IBMPlexSerif-Italic.ttf") format("truetype");
  font-style: italic;
  font-weight: 400;
  font-display: swap;
}
:root {
  --en-color: #1a1a2e;
  --zh-color: #2d3436;
  --border: #e0e0e0;
  --divider: rgba(0, 0, 0, 0.16);
  --bg-en: #fafbfc;
  --bg-zh: #f8f9fa;
  --max-width: 1000px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: "Geist", system-ui, -apple-system, sans-serif;
  font-size: 16px;
  line-height: 1.75;
  color: var(--en-color);
  background: #fff;
}
.page-wrap { max-width: var(--max-width); margin: 0 auto; padding: 5rem 1.5rem 4rem; }
.paper { position: relative; }
.paper::before {
  content: ""; position: absolute; inset: 0 auto 0 50%; width: 1px;
  background: var(--divider); transform: translateX(-0.5px); pointer-events: none;
}
.bilingual-row {
  position: relative; z-index: 1; display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  column-gap: 32px; margin-bottom: 32px; align-items: start;
}
.col { padding: 12px 16px; border: 0; border-radius: 16px; min-width: 0; }
.col.en { background: var(--bg-en); font-family: "Geist", system-ui, -apple-system, sans-serif; }
.col.en p, .col.en li { letter-spacing: -0.02em; }
.col.zh {
  background: var(--bg-zh);
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  color: var(--zh-color);
}
.paper-header { margin-bottom: 2rem; }
.title-row .col, .meta-row .col, .heading-row .col, .caption-row .col { background: transparent; border: none; }
.title-row .col { padding: 0.5rem 0; border-radius: 0; }
.title-row h1 { font-size: 20px; line-height: 1.674; font-weight: 400; }
.title-row .en h1 { font-family: "IBM Plex Serif", Georgia, serif; font-style: italic; }
.meta-row .col { padding: 0.25rem 0; font-size: 0.9rem; }
.meta { color: #555; }
.heading-row { scroll-margin-top: 32px; margin-top: 32px; margin-bottom: 4px; }
.heading-row .col { padding: 0.25rem 24px; border-radius: 0; }
.heading-row h2, .heading-row h3, .heading-row h4 {
  border: 0; padding: 0; font-weight: 400; line-height: 1.674; color: inherit;
}
.heading-row h2 { font-size: 18px; }
.heading-row h3 { font-size: 16px; }
.heading-row h4 { font-size: 14px; }
.heading-row .en h2, .heading-row .en h3, .heading-row .en h4 {
  font-family: "IBM Plex Serif", Georgia, serif; font-style: italic;
}
p { text-align: justify; hyphens: auto; }
ol, ul { padding-left: 1.5rem; }
li { margin-bottom: 0.6rem; text-align: justify; }
.paper-figure { position: relative; z-index: 1; margin: 32px 0; width: 100%; clear: both; }
.figure-image-wrap {
  width: 100%; max-width: 900px; margin: 0 auto; overflow: visible;
  background: #fff; border: 1px solid var(--border); border-radius: 6px;
  padding: 0.5rem; text-align: center;
}
.figure-image-wrap img { display: block; max-width: 100%; width: auto; height: auto; margin: 0 auto; object-fit: contain; }
.caption-row { margin-top: 0.75rem; margin-bottom: 0; }
.caption-row .col { padding: 0.25rem 0; border-radius: 0; }
figcaption, .caption-row p { font-size: 0.9rem; color: #555; font-style: italic; text-align: center; }
.paper-table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }
.paper-table th, .paper-table td { border-top: 1px solid #999; padding: 0.3rem 0.5rem; text-align: left; vertical-align: top; }
.paper-table thead th { border-top: 1.5px solid #333; border-bottom: 1px solid #666; }
.paper-table tbody tr:last-child td { border-bottom: 1.5px solid #333; }
.ref-block {
  position: relative; z-index: 1; margin: 0.5rem 0 1rem; background: #fff;
  font-family: "Georgia", "Times New Roman", "Songti SC", "SimSun", serif;
}
.ref-block p.ref { font-size: 0.82rem; line-height: 1.5; text-align: left; margin-bottom: 0.35rem; }
.ref-num { font-weight: 600; }
.footer-note {
  margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border);
  font-size: 0.8rem; color: #888; text-align: center; font-family: system-ui, sans-serif;
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
}
@media (max-width: 860px) {
  .page-wrap { padding: 2rem 1rem 4rem; }
  .paper::before { display: none; }
  .bilingual-row { grid-template-columns: 1fr; row-gap: 16px; }
}
@media print {
  .paper::before { display: none; }
  .bilingual-row { break-inside: avoid; page-break-inside: avoid; }
  .paper-figure { break-inside: avoid; page-break-inside: avoid; }
  .figure-image-wrap img { max-width: 100%; }
}
</style>
</head>
<body>
<div class="page-wrap">
  <article class="paper">
    <!-- 内容行 -->
  </article>
  <p class="footer-note">Bilingual translation generated from the original PDF. Source: <会议/出处>. Images preserved at full resolution.</p>
</div>
</body>
</html>
```

## 行类型(按原文顺序拼装)

1. **标题行**(仅一次):
```html
<header class="paper-header">
  <div class="bilingual-row title-row">
    <div class="col en"><h1>英文标题</h1></div>
    <div class="col zh"><h1>中文标题</h1></div>
  </div>
</header>
```
2. **作者/机构/出处行**(meta-row,可多个):`<div class="bilingual-row meta-row"><div class="col en"><p class="meta">…</p></div><div class="col zh"><p class="meta">…</p></div></div>`
3. **章节标题行**(heading-row,h2/h3/h4 对应原文层级,不自行改层级):
```html
<div class="bilingual-row heading-row">
  <div class="col en"><h2>1 INTRODUCTION</h2></div>
  <div class="col zh"><h2>1 引言</h2></div>
</div>
```
4. **普通段落行**(默认):`<div class="bilingual-row"><div class="col en"><p>…</p></div><div class="col zh"><p>…</p></div></div>`
   - 一个原文段落一行,不合并、不拆分;列表项用 `<ol>/<ul><li>` 放在各自 col 内。
5. **插图块**(通栏,图片在前、双语 caption 在后):
```html
<figure class="paper-figure">
  <div class="figure-image-wrap">
    <img src="assets/figure1.png" alt="Figure 1: 原文 caption 起始部分" loading="lazy" />
  </div>
  <div class="bilingual-row caption-row">
    <div class="col en"><p><strong>Figure 1:</strong> 英文 caption 全文。</p></div>
    <div class="col zh"><p><strong>图 1:</strong> 中文 caption 译文。</p></div>
  </div>
</figure>
```
6. **表格**:优先双语 HTML 表格(表头、单元格逐格对照,英文在上中文在下或左右两表均可,保持全量内容):
```html
<div class="bilingual-row">
  <div class="col en"><table class="paper-table">…</table></div>
  <div class="col zh"><table class="paper-table">…</table></div>
</div>
```
   结构无法可靠还原时,改用插图块形式插入 `assets/tableN.png`,caption 双语,并在行内说明"表格结构部分丢失,以下保留全部可读文字内容"。
7. **参考文献块**(通栏单栏,英文原状,不翻译):
```html
<div class="bilingual-row heading-row">
  <div class="col en"><h2>REFERENCES</h2></div>
  <div class="col zh"><h2>参考文献</h2></div>
</div>
<div class="ref-block">
  <p class="ref"><span class="ref-num">[1]</span> 原文条目,保持英文原样。</p>
  <p class="ref"><span class="ref-num">[2]</span> …</p>
</div>
```
8. **脚注**:保持在其原始逻辑位置(页脚内容可移到对应段落之后),按普通双语行处理,保留编号。

## 组装规则

1. 插图插入其在原文中的位置(原 caption 处);若原文为"先文后图"且图在后续页面,保持图在其 caption 所在位置,不挪动。
2. 图表编号、引文编号 `[12]`、公式编号在译文中保持原样。
3. 单次写不完时,在一个完整的行边界处停下;下次从准确中断位置继续追加,不回顾总结。
4. HTML 特殊字符转义(`&` `<` `>`);英文撇号可用 `&#x27;`。
5. 文件末尾保留 footer-note,注明来源会议/出处。
