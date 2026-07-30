#!/usr/bin/env python3
"""Crop figure/table images from a PDF around their captions.

Detects "Figure N" / "Table N" caption lines with PyMuPDF, crops the adjacent
content region at high resolution, and writes a manifest for verification.

Strategy:
- Figures: union of vector/raster graphics adjacent to the caption (usually
  above it in ACM layouts), trimmed so no body text is included.
- Tables: downward sweep from the caption (table bodies are mostly text, so
  graphics alone are not enough), cut at the table's closing rule when one is
  found, otherwise at the first large vertical gap.

Typical workflow:
  1. python3 extract_figures.py PAPER.pdf -o assets            # extract all
  2. View every PNG; if a crop is wrong, re-crop it manually:
     python3 extract_figures.py PAPER.pdf -o assets --set 3 --kind table \
         --page 4 --rect 50,90,560,300
  3. To pick manual coordinates, render a full page first:
     python3 extract_figures.py PAPER.pdf -o assets --render-page 4
     (pixels in the render / --page-zoom = PDF points for --rect)

Coordinates are PDF points, origin at the page's top-left, y growing downward.
Pages are 1-based everywhere.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

CAPTION_RE = re.compile(r"^\s*(Figure|Fig\.?|TABLE|Table)\s*(\d+)\s*[:.]?\s*(.*)$")
SECTION_RE = re.compile(r"^\s*\d+(\.\d+)*\s+\S")

# Vertical tolerance when deciding whether an item touches the caption band.
EDGE_TOL = 2.0
# Padding added around the union of graphic bounding boxes.
PAD = 3.0
# Caption lines wider than this fraction of the page width are treated as
# belonging to full-width (spanning) floats.
FULL_WIDTH_RATIO = 0.60
# Vertical gap (points) that ends a table sweep.
TABLE_GAP = 14.0
# When a table sweep stalls, keep going if another horizontal rule starts
# within this distance — wrapped cells can produce large internal gaps.
RULE_BRIDGE = 45.0
# Margin left below a caption so glyph descenders never bleed into the crop.
CAPTION_MARGIN = 2.5
# A horizontal rule marking a table edge: wider than this share of the column
# and thinner than RULE_MAX_HEIGHT points.
RULE_MIN_WIDTH_RATIO = 0.5
RULE_MAX_HEIGHT = 3.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", type=Path, help="Source PDF path.")
    parser.add_argument("-o", "--outdir", type=Path, required=True, help="Directory for PNG outputs and manifest.json.")
    parser.add_argument("--zoom", type=float, default=3.0, help="Render scale for crops (default 3.0 ≈ 216 DPI).")
    parser.add_argument("--only", type=str, default="", help="Comma-separated caption numbers to extract, e.g. 1,4.")
    parser.add_argument("--list", action="store_true", help="List detected captions without rendering crops.")
    parser.add_argument("--set", dest="set_id", type=str, default="", help="Re-crop one caption number with a manual rect.")
    parser.add_argument("--kind", type=str, default="figure", choices=["figure", "table"], help="Kind used with --set.")
    parser.add_argument("--page", type=int, default=0, help="1-based page number used with --set.")
    parser.add_argument("--rect", type=str, default="", help="Manual clip 'x0,y0,x1,y1' in PDF points, used with --set.")
    parser.add_argument("--render-page", type=int, default=0, help="Render one full page to <outdir>/page-N.png for coordinate picking.")
    parser.add_argument("--page-zoom", type=float, default=1.5, help="Scale used by --render-page (default 1.5).")
    return parser.parse_args()


def caption_kind(label: str) -> str:
    return "table" if label.lower().startswith("table") else "figure"


def find_captions(doc: fitz.Document) -> list[dict]:
    """Locate caption lines across the document (1-based page numbers)."""
    captions: list[dict] = []
    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        page_width = page.rect.width
        data = page.get_text("dict")
        for block in data.get("blocks", []):
            if block.get("type") != 0:
                continue
            lines = block.get("lines", [])
            for line_index, line in enumerate(lines):
                text = "".join(span.get("text", "") for span in line.get("spans", [])).strip()
                match = CAPTION_RE.match(text)
                if not match:
                    continue
                # Captions often wrap; absorb the remaining lines of the same
                # block so the crop starts below the whole caption, and stop
                # early if another caption or a section heading begins.
                x0, y0, x1, y1 = line["bbox"]
                parts = [text]
                for follow in lines[line_index + 1:]:
                    follow_text = "".join(span.get("text", "") for span in follow.get("spans", [])).strip()
                    if CAPTION_RE.match(follow_text) or SECTION_RE.match(follow_text):
                        break
                    fx0, fy0, fx1, fy1 = follow["bbox"]
                    if fy0 - y1 > TABLE_GAP:
                        break
                    x0, y0, x1, y1 = min(x0, fx0), min(y0, fy0), max(x1, fx1), max(y1, fy1)
                    parts.append(follow_text)
                full_text = " ".join(parts)
                width = x1 - x0
                span = "full" if width > FULL_WIDTH_RATIO * page_width else (
                    "left" if (x0 + x1) / 2 < page_width / 2 else "right"
                )
                captions.append({
                    "kind": caption_kind(match.group(1)),
                    "num": int(match.group(2)),
                    "page": page_index + 1,
                    "bbox": [x0, y0, x1, y1],
                    "span": span,
                    "text": full_text[:120],
                })
                break  # one caption per block
    return captions


def column_xrange(page: fitz.Page, span: str) -> tuple[float, float]:
    """X-range a float may occupy; keeps neighbor-column content out of the crop."""
    width = page.rect.width
    if span == "full":
        return 0.0, width
    mid = width / 2
    return (0.0, mid) if span == "left" else (mid, width)


def graphic_bboxes(page: fitz.Page) -> list[fitz.Rect]:
    """Bounding boxes of vector drawings and raster images on the page."""
    boxes: list[fitz.Rect] = []
    for drawing in page.get_drawings():
        rect = drawing.get("rect")
        if rect and not rect.is_empty and rect.width > 2 and rect.height > 2:
            boxes.append(fitz.Rect(rect))
    for info in page.get_image_info():
        bbox = info.get("bbox")
        if bbox:
            rect = fitz.Rect(bbox)
            if not rect.is_empty and rect.width > 2 and rect.height > 2:
                boxes.append(rect)
    return boxes


def text_blocks(page: fitz.Page) -> list[tuple[fitz.Rect, str]]:
    blocks: list[tuple[fitz.Rect, str]] = []
    for block in page.get_text("blocks"):
        if len(block) >= 7 and block[6] == 0:  # text block
            blocks.append((fitz.Rect(block[:4]), str(block[4])))
    return blocks


def looks_like_heading(text: str) -> bool:
    """Short blocks starting with a section number are headings, not table rows.

    Long blocks are never headings — a multi-row table body can also begin
    with a digit (e.g. PID columns), so length is the deciding factor.
    """
    lines = [line for line in text.strip().splitlines() if line.strip()]
    return bool(lines) and len(lines) <= 3 and bool(SECTION_RE.match(lines[0]))


def horizontal_rules(page: fitz.Page, x_min: float, x_max: float, col_width: float) -> list[fitz.Rect]:
    """Long hairline rules (table edges). Their rects can have zero height, so
    they must be collected straight from drawings, not via graphic_bboxes."""
    rules: list[fitz.Rect] = []
    for drawing in page.get_drawings():
        rect = drawing.get("rect")
        if not rect:
            continue
        rect = fitz.Rect(rect)
        if rect.width <= RULE_MIN_WIDTH_RATIO * col_width or rect.height > RULE_MAX_HEIGHT:
            continue
        center_x = (rect.x0 + rect.x1) / 2
        if x_min - EDGE_TOL <= center_x <= x_max + EDGE_TOL:
            rules.append(rect)
    return rules


def table_region_below(page: fitz.Page, cap: fitz.Rect, x_min: float, x_max: float) -> fitz.Rect | None:
    """Sweep downward from the caption; table bodies are text, so include text blocks.

    The region ends at the closing horizontal rule when rules are present,
    otherwise at the first vertical gap larger than TABLE_GAP.
    """
    col_width = x_max - x_min

    def in_column(rect: fitz.Rect) -> bool:
        center_x = (rect.x0 + rect.x1) / 2
        return x_min - EDGE_TOL <= center_x <= x_max + EDGE_TOL

    rules = [r for r in horizontal_rules(page, x_min, x_max, col_width) if r.y0 >= cap.y1 - EDGE_TOL]

    items: list[tuple[fitz.Rect, bool]] = []  # (rect, is_heading)
    for rect in graphic_bboxes(page):
        if in_column(rect) and rect.y0 >= cap.y1 - EDGE_TOL:
            items.append((rect, False))
    for rect, text in text_blocks(page):
        if not in_column(rect) or rect.y0 < cap.y1 - EDGE_TOL:
            continue
        items.append((rect, looks_like_heading(text)))

    if not items:
        return None
    items.sort(key=lambda item: (item[0].y0, item[0].x0))

    collected: list[fitz.Rect] = []
    bottom = cap.y1
    for rect, is_heading in items:
        if is_heading and collected:
            break
        if is_heading:
            continue
        if collected and rect.y0 - bottom > TABLE_GAP:
            break
        collected.append(rect)
        bottom = max(bottom, rect.y1)
    if not collected:
        return None

    # Tables with wrapped cells can have internal gaps larger than TABLE_GAP.
    # Bridge such gaps as long as another horizontal rule follows soon after;
    # a rule means the table continues, body text never starts with one.
    while True:
        ahead = [r for r in rules if r.y1 > bottom + EDGE_TOL and r.y0 - bottom <= RULE_BRIDGE]
        if not ahead:
            break
        nxt = min(ahead, key=lambda r: r.y0)
        bottom = nxt.y1
        for rect, _ in items:
            if rect.y0 <= bottom + EDGE_TOL and all(rect is not c for c in collected):
                collected.append(rect)

    closing_rules = [r for r in rules if r.y1 <= bottom + EDGE_TOL]
    if closing_rules:
        cut = max(r.y1 for r in closing_rules)
        collected = [r for r in collected if r.y0 <= cut + EDGE_TOL]
        bottom = cut

    region = collected[0]
    for rect in collected[1:]:
        region |= rect
    region.y0 = cap.y1 + CAPTION_MARGIN
    region.y1 = bottom
    # Widen to the full rule span so edge rules are not clipped.
    for rule in rules:
        if rule.y0 >= region.y0 - EDGE_TOL and rule.y1 <= bottom + EDGE_TOL:
            region |= rule
            region.y0 = cap.y1 + CAPTION_MARGIN
            region.y1 = bottom
    return region


def figure_region(page: fitz.Page, cap: fitz.Rect, x_min: float, x_max: float) -> fitz.Rect | None:
    """Union of graphics adjacent to the caption (above first, then below)."""

    def in_column(rect: fitz.Rect) -> bool:
        center_x = (rect.x0 + rect.x1) / 2
        return x_min - EDGE_TOL <= center_x <= x_max + EDGE_TOL

    graphics = [g for g in graphic_bboxes(page) if in_column(g)]
    above = [g for g in graphics if g.y1 <= cap.y0 + EDGE_TOL]
    below = [g for g in graphics if g.y0 >= cap.y1 - EDGE_TOL]
    candidates = above or below
    if not candidates:
        return None

    region = candidates[0]
    for g in candidates[1:]:
        region |= g
    region = fitz.Rect(region.x0 - PAD, region.y0 - PAD, region.x1 + PAD, region.y1 + PAD)

    blocks = [b for b, _ in text_blocks(page) if in_column(b)]
    if candidates is above:
        # Do not swallow body text sitting above the figure.
        tops = [b.y1 for b in blocks if b.y1 <= region.y0 + EDGE_TOL]
        if tops:
            region.y0 = max(region.y0, max(tops))
        region.y1 = min(region.y1, cap.y0 - 1)
    else:
        bottoms = [b.y0 for b in blocks if b.y0 >= region.y1 - EDGE_TOL]
        if bottoms:
            region.y1 = min(region.y1, min(bottoms))
    return region


def whitespace_region(page: fitz.Page, cap: fitz.Rect, x_min: float, x_max: float) -> fitz.Rect | None:
    """Fallback: the text-free gap around the caption (for text-rendered diagrams)."""

    def in_column(rect: fitz.Rect) -> bool:
        center_x = (rect.x0 + rect.x1) / 2
        return x_min - EDGE_TOL <= center_x <= x_max + EDGE_TOL

    blocks = [b for b, _ in text_blocks(page) if in_column(b)]
    upper = [b for b in blocks if b.y1 <= cap.y0 + EDGE_TOL]
    lower = [b for b in blocks if b.y0 >= cap.y1 - EDGE_TOL]
    top = max((b.y1 for b in upper), default=0.0)
    bottom = min((b.y0 for b in lower), default=page.rect.height)
    region = fitz.Rect(x_min, top, x_max, bottom)
    return None if region.is_empty else region


def guess_region(page: fitz.Page, caption: dict) -> fitz.Rect | None:
    cap = fitz.Rect(caption["bbox"])
    x_min, x_max = column_xrange(page, caption["span"])

    region = None
    if caption["kind"] == "table":
        region = table_region_below(page, cap, x_min, x_max)
    if region is None:
        region = figure_region(page, cap, x_min, x_max)
    if region is None:
        region = whitespace_region(page, cap, x_min, x_max)
    if region is None:
        return None

    region &= fitz.Rect(x_min, 0, x_max, page.rect.height)
    region &= page.rect
    if region.is_empty or region.width < 20 or region.height < 20:
        return None
    return region


def render_clip(page: fitz.Page, rect: fitz.Rect, zoom: float, out_path: Path) -> None:
    matrix = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pixmap.save(out_path)


def output_name(kind: str, num: int) -> str:
    return f"{kind}{num}.png"


def main() -> int:
    args = parse_args()
    pdf_path = args.pdf.expanduser().resolve()
    if not pdf_path.exists():
        print(f"error: PDF not found: {pdf_path}", file=sys.stderr)
        return 1
    outdir = args.outdir.expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)

    if args.render_page:
        page = doc.load_page(args.render_page - 1)
        out = outdir / f"page-{args.render_page}.png"
        render_clip(page, page.rect, args.page_zoom, out)
        print(out)
        return 0

    if args.set_id:
        if not args.page or not args.rect:
            print("error: --set requires --page and --rect", file=sys.stderr)
            return 1
        rect = fitz.Rect([float(v) for v in args.rect.split(",")])
        page = doc.load_page(args.page - 1)
        out = outdir / output_name(args.kind, int(args.set_id))
        render_clip(page, rect, args.zoom, out)
        print(out)
        return 0

    captions = find_captions(doc)
    if args.only:
        wanted = {int(v) for v in args.only.split(",")}
        captions = [c for c in captions if c["num"] in wanted]

    if args.list:
        for c in captions:
            bbox = ", ".join(f"{v:.0f}" for v in c["bbox"])
            print(f"{c['kind']}{c['num']}  page {c['page']}  span {c['span']}  caption bbox [{bbox}]  {c['text'][:60]}")
        return 0

    manifest: list[dict] = []
    for caption in captions:
        page = doc.load_page(caption["page"] - 1)
        region = guess_region(page, caption)
        entry = {
            "kind": caption["kind"],
            "num": caption["num"],
            "page": caption["page"],
            "span": caption["span"],
            "caption": caption["text"],
            "file": output_name(caption["kind"], caption["num"]),
            "rect": None,
            "status": "ok",
        }
        if region is None:
            entry["status"] = "no-region-found (re-crop manually with --set)"
        else:
            entry["rect"] = [round(region.x0, 1), round(region.y0, 1), round(region.x1, 1), round(region.y1, 1)]
            render_clip(page, region, args.zoom, outdir / entry["file"])
        manifest.append(entry)

    manifest_path = outdir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    for entry in manifest:
        rect = entry["rect"] if entry["rect"] else "-"
        print(f"{entry['file']}  page {entry['page']}  rect {rect}  {entry['status']}")
    print(f"manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
