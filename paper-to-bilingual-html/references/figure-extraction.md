# Figure / Table Extraction

目标:从 PDF 裁出**无遮挡、无截断**的高清插图与表格截图,插入 HTML 的原文对应位置。任何图必须经过逐张目检才能写入 HTML。

## 工具

`scripts/extract_figures.py`。依赖获取与解释器选择以 [dependencies.md](dependencies.md) 为唯一准则;下列命令中的 `python3` 均可替换为通过预检的解释器。

```bash
# 1. 列出检测到的所有 Figure/Table caption(不动刀,先摸底)
python3 scripts/extract_figures.py PAPER.pdf -o assets --list

# 2. 自动裁剪全部,生成 assets/figureN.png、tableN.png 与 manifest.json
python3 scripts/extract_figures.py PAPER.pdf -o assets

# 3. 只处理指定编号
python3 scripts/extract_figures.py PAPER.pdf -o assets --only 1,4

# 4. 手动重裁某一张(坐标单位是 PDF point,左上角原点,y 向下,页码从 1 开始)
python3 scripts/extract_figures.py PAPER.pdf -o assets \
    --set 3 --kind figure --page 4 --rect 50,100,560,420

# 5. 渲染整页用于挑坐标(像素 ÷ --page-zoom = PDF point)
python3 scripts/extract_figures.py PAPER.pdf -o assets --render-page 4
```

自动检测的策略:按 caption 定位;Figure 取相邻图形元素并集(ACM 风格图在 caption 上方);Table 从 caption 向下扫描(表体多为文字),遇到收尾横线或大间距截止。双栏论文按 caption 所在栏裁剪,跨栏浮动按通栏裁剪。截图**不含 caption 文字**(caption 在 HTML 中以双语文字呈现)。

## 目检清单(每张必查)

用读图工具逐张查看,确认:

1. **完整**:图形/表格内容全部在框内,四边无截断(尤其底部收尾横线、右侧列、图例)。
2. **不串栏**:没有混入相邻栏的正文碎片。
3. **无多余内容**:不含页眉、页脚、页码、正文段落。
4. **不含 caption**:图题/表题文字不在图内(多行 caption 容易残留第二行起的内容,发现即重裁)。
5. **清晰**:默认 zoom=3(约 216 DPI);小字看不清时 `--zoom 4` 重裁该张。

任何一项不合格 → 进入手动重裁流程,重裁后**重新目检**,直至全部合格。

## 手动重裁流程

1. `--render-page N` 渲染整页,用读图工具查看,目测目标区域的像素坐标。
2. 换算成 PDF point:point = 像素 ÷ `--page-zoom`(默认 1.5)。
3. `--set N --kind figure|table --page P --rect x0,y0,x1,y1` 重裁。
4. 重新目检该张。
5. `manifest.json` 中 `status` 非 `ok` 的条目必须手动处理,不得跳过。

## 已知边界(遇到一律走手动流程)

- 跨页浮动体(图/表横断两页):分别裁剪后在 HTML 中相邻放置,并注明续页。
- 无 caption 的图(正文内嵌小图):用 `--render-page` 挑坐标手动裁,文件名按上下文命名(如 `figure-inline-1.png`)。
- 扫描件/OCR 噪声导致的检测失败:全部走手动。
- 表格也可不走截图:能可靠转写为 HTML 表格时优先转写(见 output-format.md),截图作为兜底。

## 插入规则

- 插图放在其在原文中的位置(原 caption 处),caption 以双语文字行呈现;不因排版美观挪图。
- `img` 的 `src` 用相对路径 `assets/figureN.png`,`alt` 放原文 caption 起始文字。
- 若原文为"先文后图"且图在后续页面,保持图在其 caption 所在位置。
