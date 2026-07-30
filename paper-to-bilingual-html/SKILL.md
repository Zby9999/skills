---
name: paper-to-bilingual-html
description: 将学术论文完整翻译为逐段中英对照的双语 HTML(无删减、不概括;参考文献保持英文原状),并从 PDF 中裁出高清插图/表格截图,逐张目检确认无遮挡、无截断后插入原文对应位置。触发词包括"双语 HTML""中英对照网页""论文转 HTML""bilingual html""完整翻译论文成网页""论文截图插入"等。Use when asked to turn a full academic paper (usually PDF) into a complete paragraph-by-paragraph English-Chinese side-by-side HTML file, with figures/tables cropped from the PDF at their original positions and the reference list kept in the original language.
---

# Paper to Bilingual HTML

## Overview

将学术论文整理成**无删减**的中英对照 HTML:左栏英文原文、右栏中文译文,严格保留原文结构、段落顺序和全部可读内容;插图与表格以 PDF 高清截图插入原文对应位置;参考文献整块保持英文原状。

## Workflow

1. 运行依赖预检。
   - 首次在一台机器上运行,或 Python、`fitz`、裁图脚本出现错误时,按 [references/dependencies.md](references/dependencies.md) 检查并获取依赖。
   - 后续所有脚本命令都使用通过预检的同一个 Python 解释器。
   - **完成条件**:该解释器为 Python 3.10+,可导入 `fitz`,且 `scripts/extract_figures.py --help` 成功退出;同时确认具备逐张查看 PNG 的能力。
2. 读取最忠实的源文本。
   - 优先使用用户提供的原始 PDF、DOCX、Markdown 或纯文本。
   - 处理 PDF、扫描件或 OCR 文本时,先恢复阅读顺序(双栏论文警惕跨栏串读),再开始翻译。
   - 遇到模糊、断裂、重叠、错列或明显 OCR 问题时,不要擅自补写,标注 `[原文疑似识别错误]`。
3. 先识别结构,再开始正文输出。
   - 识别标题、作者信息、摘要、章节标题、图表标题、脚注、参考文献、附录等。
   - 在正式内容前,先简短列出识别到的论文结构。
4. 提取插图与表格截图。
   - 使用通过预检的 Python 解释器运行 `scripts/extract_figures.py PAPER.pdf -o <输出目录>/assets`,自动按 caption 定位并裁剪 Figure/Table 区域,生成 PNG 与 `manifest.json`。
   - **逐张目检**:用读图工具查看每一张 PNG,确认无截断、无相邻栏内容、无页眉页脚、不含 caption 文字(caption 在 HTML 中以双语文字呈现)。检查清单与手动重裁方法见 [references/figure-extraction.md](references/figure-extraction.md)。
   - 任何一张不合格:用 `--set N --kind figure|table --page P --rect x0,y0,x1,y1` 手动重裁,**重新目检**,直到合格为止。未通过目检的图不得写入 HTML。
5. 严格按原顺序逐段翻译。
   - 保持原始章节、编号、标题层级与段落顺序;不删减、不概括、不跳段、不重组。
   - 遵循 [references/translation-rules.md](references/translation-rules.md) 的保真规则。
   - **参考文献整块保持英文原状**:完整列出、不逐条翻译、不把 "et al." 改成"等"、不中文化任何部分。
   - 内容过长时,从中断处继续,不要切换成总结模式。
   - **完成条件**:除参考文献与无需翻译的代码/公式外,每个可翻译单元都通过 `translation-rules.md` 的 Model-authored Translation Quality Gate;未通过不得写入最终 HTML。
6. 按 [references/output-format.md](references/output-format.md) 写入 HTML。
   - 每个可读单元一行双语对照;插图插入其在原文中的位置(原 caption 处),caption 用双语文字行呈现。
   - 表格优先转写为 HTML 表格;结构无法可靠还原时,用表格截图代替,并保留全部可读文字。
   - 将本技能 `assets/` 中的 `Geist-VariableFont_wght.ttf` 与 `IBMPlexSerif-Italic.ttf` 复制到交付物的 `assets/` 目录,确保 HTML 离线打开时字体仍然正确。
   - 论文存在至少两个真实顶层章节时,按 [references/section-guide.md](references/section-guide.md) 添加仅在超宽视口显示的章节引导器;引导器代码、交互与验证要求以该独立 reference 为准。
7. 保持术语和技术细节稳定。
   - 保留公式、符号、变量名、单位、图表编号、引文编号和参考文献编号原样。
   - 首次出现的重要术语可写成"中文(English)",后续保持统一。
8. 未经用户明确要求,不要额外添加摘要、评论、难点解析、学习建议、背景扩展或结尾总结。

## Output Contract

- 最终交付物是一个 `.html` 文件 + 同目录 `assets/` 资源文件夹,默认写到论文所在目录。
- 文件名:`<论文标题>-bilingual.html`(文件系统不安全字符先清洗),图片为 `assets/figureN.png`、`assets/tableN.png`。
- `assets/` 同时包含从本技能复制的 `Geist-VariableFont_wght.ttf` 与 `IBMPlexSerif-Italic.ttf`。
- 全文所有可读单元都必须出现;参考文献完整列出但保持英文原状。
- 严格遵循 [references/output-format.md](references/output-format.md) 的 HTML 结构与样式模板。
- 超宽章节引导器严格遵循 [references/section-guide.md](references/section-guide.md),不要把其代码合并回基础输出模板。
- 处理 PDF、扫描件、双栏排版或 OCR 文本时,遵循 [references/source-handling.md](references/source-handling.md)。

## Decision Rules

- 忠实度优先于润色度。
- 对齐优先于重写。
- 明示不确定性优先于猜测性补写。
- 保留全部可读内容优先于输出简洁。
- 插图必须逐张目检合格后才能插入;宁可手动重裁,也不交付截断或串栏的图。
