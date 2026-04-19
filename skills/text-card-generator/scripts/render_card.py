#!/usr/bin/env python3
"""
Render card-style PNG images from JSON data.
Usage:
  python render_card.py --data '{"card_type":"list",...}' --output out.png
  python render_card.py --data-file data.json --output out.png
  python render_card.py --font-dir /path/to/fonts --data-file data.json --output out.png
"""

import argparse
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ── Defaults ──
FONT_DIR = os.environ.get("CARD_FONT_DIR", "/tmp/card-gen-fonts")
W = 1080

# ── Colors ──
BG = "#FAFAFA"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#EEEEEE"
TITLE_CLR = "#1A1A1A"
DESC_CLR = "#888888"
DIVIDER = "#F0F0F0"
ACCENTS = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFB347", "#DDA0DD"]


def font(size, bold=False):
    name = "NotoSansCJKsc-Bold.otf" if bold else "NotoSansCJKsc-Regular.otf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap_lines(draw, text, ft, max_w):
    lines, cur = [], ""
    for ch in text:
        if draw.textbbox((0, 0), cur + ch, font=ft)[2] > max_w:
            if cur:
                lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def line_h(ft, spacing=8):
    return ft.getbbox("测")[3] + spacing


def draw_text_wrapped(draw, x, y, text, ft, fill, max_w, spacing=8):
    lns = wrap_lines(draw, text, ft, max_w)
    lh = line_h(ft, spacing)
    for ln in lns:
        draw.text((x, y), ln, font=ft, fill=fill)
        y += lh
    return y


def draw_circle(draw, cx, cy, r, fill_color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill_color)


def draw_circle_text(draw, cx, cy, r, bg_color, text, ft):
    draw_circle(draw, cx, cy, r, bg_color)
    bb = draw.textbbox((0, 0), text, font=ft)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((cx - tw // 2, cy - th // 2 - 2), text, font=ft, fill="#FFFFFF")


def shadow_rect(draw, box, radius, fill, so=3, sc="#E8E8E8"):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle([x1 + so, y1 + so, x2 + so, y2 + so], radius=radius, fill=sc)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=CARD_BORDER, width=1)


# ════════════════════════════════════════
# Card renderers
# ════════════════════════════════════════

def render_list(data):
    items = data["items"]
    title = data.get("title", "")
    PAD = 50
    title_ft = font(40, True)
    item_title_ft = font(30, True)
    item_desc_ft = font(22)
    icon_ft = font(22, True)

    tmp = Image.new("RGB", (W, 100))
    td = ImageDraw.Draw(tmp)

    content_w = W - PAD * 2 - 80 - 60  # card padding + icon area
    item_h_list = []
    for it in items:
        t_lines = wrap_lines(td, it["title"], item_title_ft, content_w)
        d_lines = wrap_lines(td, it.get("desc", ""), item_desc_ft, content_w)
        h = 8 + len(t_lines) * line_h(item_title_ft) + 4 + len(d_lines) * line_h(item_desc_ft) + 20
        item_h_list.append(max(h, 80))

    card_inner = sum(item_h_list) + (len(items) - 1) * 12 + 40
    H = 80 + card_inner + 40

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    if title:
        draw.text((PAD, 25), title, font=title_ft, fill=TITLE_CLR)

    cy1, cy2 = 80, H - 20
    cx1, cx2 = PAD - 10, W - PAD + 10
    shadow_rect(draw, [cx1, cy1, cx2, cy2], 20, CARD_BG)

    y = cy1 + 20
    for i, it in enumerate(items):
        clr = it.get("icon_color", ACCENTS[i % len(ACCENTS)])
        ix = cx1 + 35
        draw_circle_text(draw, ix + 22, y + 30, 22, clr, it.get("icon_text", str(i + 1)), icon_ft)

        tx = ix + 60
        tw = cx2 - 30 - tx
        ny = draw_text_wrapped(draw, tx, y + 8, it["title"], item_title_ft, TITLE_CLR, tw)
        if it.get("desc"):
            ny = draw_text_wrapped(draw, tx, ny + 4, it["desc"], item_desc_ft, DESC_CLR, tw)

        y = ny + 20
        if i < len(items) - 1:
            draw.line([(tx, y), (cx2 - 30, y)], fill=DIVIDER, width=1)
            y += 12

    return img


def render_comparison(data):
    left_items = data["left_items"]
    right_items = data["right_items"]
    lt = data.get("left_title", "")
    rt = data.get("right_title", "")

    title_ft = font(36, True)
    item_ft = font(24)
    icon_ft = font(20, True)

    max_items = max(len(left_items), len(right_items))
    item_h = 58
    ch = max_items * item_h + 56
    H = 90 + ch + 30

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    half = W // 2 - 45
    cy = 90

    # Left
    draw.text((55, 30), lt, font=title_ft, fill="#CC4444")
    shadow_rect(draw, [30, cy, 30 + half, cy + ch], 16, "#FFF8F8")
    draw.rounded_rectangle([30, cy, 36, cy + ch], radius=3, fill="#FF6B6B")

    y = cy + 28
    for it in left_items:
        draw_circle_text(draw, 70, y + 12, 11, "#FF6B6B", "×", icon_ft)
        draw.text((92, y), it, font=item_ft, fill="#884444")
        y += item_h

    # Right
    rx = W // 2 + 15
    draw.text((rx + 25, 30), rt, font=title_ft, fill="#2E8B57")
    shadow_rect(draw, [rx, cy, rx + half, cy + ch], 16, "#F5FFF5")
    draw.rounded_rectangle([rx, cy, rx + 6, cy + ch], radius=3, fill="#4ECDC4")

    y = cy + 28
    for it in right_items:
        draw_circle_text(draw, rx + 40, y + 12, 11, "#4ECDC4", "✓", icon_ft)
        draw.text((rx + 62, y), it, font=item_ft, fill="#2E6B3E")
        y += item_h

    return img


def render_terminal(data):
    lines = data["lines"]
    title = data.get("title", "Terminal")

    title_ft = font(32, True)
    code_ft = font(22)
    comment_ft = font(20)

    H = 80 + 45 + len(lines) * 32 + 40
    img = Image.new("RGB", (W, H), "#1E1E2E")
    draw = ImageDraw.Draw(img)

    draw.text((40, 25), title, font=title_ft, fill="#CDD6F4")

    ty, tx = 80, 40
    tw, th = W - 80, H - ty - 30
    draw.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=12, fill="#11111B", outline="#45475A", width=1)

    for i, c in enumerate(["#F38BA8", "#FAB387", "#A6E3A1"]):
        draw.ellipse([tx + 18 + i * 24, ty + 14, tx + 30 + i * 24, ty + 26], fill=c)

    y = ty + 45
    for ln in lines:
        txt = ln.get("text", "")
        clr = ln.get("color", "")
        if txt and clr:
            use_ft = code_ft if txt.startswith("$") or not txt.startswith("#") else comment_ft
            draw.text((tx + 25, y), txt, font=use_ft, fill=clr)
        y += 32

    return img


def render_fit(data):
    title = data.get("title", "")
    fit_title = data.get("fit_title", "适合使用")
    nofit_title = data.get("nofit_title", "可以不用")
    fit_items = data["fit_items"]
    nofit_items = data["nofit_items"]

    title_ft = font(36, True)
    section_ft = font(28, True)
    item_ft = font(24)
    icon_ft = font(18, True)

    item_h = 50
    H = 80 + 50 + len(fit_items) * item_h + 40 + 50 + len(nofit_items) * item_h + 50
    PAD = 50

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((PAD, 25), title, font=title_ft, fill=TITLE_CLR)

    y = 85
    draw.text((PAD + 10, y), fit_title, font=section_ft, fill="#2E8B57")
    y += 48
    for it in fit_items:
        draw_circle_text(draw, PAD + 30, y + 14, 13, "#4ECDC4", "✓", icon_ft)
        draw.text((PAD + 55, y), it, font=item_ft, fill="#333333")
        y += item_h

    y += 20
    draw.line([(PAD, y), (W - PAD, y)], fill="#E8E8E8", width=1)
    y += 20

    draw.text((PAD + 10, y), nofit_title, font=section_ft, fill="#999999")
    y += 48
    for it in nofit_items:
        draw_circle_text(draw, PAD + 30, y + 14, 13, "#CCCCCC", "—", icon_ft)
        draw.text((PAD + 55, y), it, font=item_ft, fill="#888888")
        y += item_h

    return img


def render_flow(data):
    steps = data["steps"]
    connections = data.get("connections", [])
    title = data.get("title", "")
    done = data.get("done")
    bottom_note = data.get("bottom_note")

    title_ft = font(36, True)
    label_ft = font(24, True)
    small_ft = font(20)
    tiny_ft = font(18)

    bw, bh = 220, 100
    gap = 80
    total = len(steps) * bw + (len(steps) - 1) * gap
    sx = (W - total) // 2
    sy = 120
    H = 480

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((50, 25), title, font=title_ft, fill=TITLE_CLR)

    boxes = []
    for i, st in enumerate(steps):
        x = sx + i * (bw + gap)
        clr = st.get("color", ACCENTS[i % len(ACCENTS)])
        shape = st.get("shape", "box")
        lbl = st["label"]

        if shape == "diamond":
            cx, cy = x + bw // 2, sy + bh // 2
            pts = [(cx, sy), (cx + bw // 2, cy), (cx, sy + bh), (cx - bw // 2, cy)]
            draw.polygon(pts, fill=clr + "22", outline=clr, width=2)
            for j, line in enumerate(lbl.split("\\n")):
                bb = draw.textbbox((0, 0), line, font=small_ft)
                draw.text((cx - (bb[2] - bb[0]) // 2, cy - 16 + j * 28), line, font=small_ft, fill=TITLE_CLR)
        else:
            draw.rounded_rectangle([x, sy, x + bw, sy + bh], radius=14, fill=clr + "22", outline=clr, width=2)
            for j, line in enumerate(lbl.split("\\n")):
                bb = draw.textbbox((0, 0), line, font=small_ft)
                draw.text((x + (bw - bb[2] + bb[0]) // 2, sy + 22 + j * 28), line, font=small_ft, fill=TITLE_CLR)

        boxes.append((x, sy, bw, bh))

    # Connections
    for conn in connections:
        fi, ti = conn["from"], conn["to"]
        clr = conn.get("color", "#999999")
        lbl = conn.get("label", "")
        style = conn.get("style", "")

        if style == "loop_top":
            # Right side of "from" box, up and around to top of "to" box
            fx = boxes[fi][0] + boxes[fi][2] // 2 + boxes[fi][2] // 2 + 5
            fy = boxes[fi][1] + boxes[fi][3] // 2
            tx_mid = boxes[ti][0] + boxes[ti][2] // 2
            loop_top = sy - 40
            rx = W - 60

            if lbl:
                draw.text((fx + 8, fy - 12), lbl, font=tiny_ft, fill=clr)

            draw.line([(fx, fy), (rx, fy)], fill=clr, width=2)
            draw.line([(rx, fy), (rx, loop_top)], fill=clr, width=2)
            draw.line([(rx, loop_top), (tx_mid, loop_top)], fill=clr, width=2)
            draw.line([(tx_mid, loop_top), (tx_mid, sy - 5)], fill=clr, width=2)
            draw.polygon([(tx_mid - 5, sy - 12), (tx_mid + 5, sy - 12), (tx_mid, sy - 5)], fill=clr)
        else:
            # Straight arrow
            x1 = boxes[fi][0] + boxes[fi][2]
            x2 = boxes[ti][0]
            ay = sy + bh // 2
            draw.line([(x1 + 5, ay), (x2 - 5, ay)], fill=clr, width=2)
            draw.polygon([(x2 - 12, ay - 5), (x2 - 12, ay + 5), (x2 - 5, ay)], fill=clr)

    # Done box
    if done:
        si = done.get("after_step", len(steps) - 1)
        dcx = boxes[si][0] + bw // 2
        dy1 = sy + bh + 5
        dy2 = dy1 + 50
        arrow_lbl = done.get("label_on_arrow", "")
        draw.line([(dcx, dy1), (dcx, dy2)], fill="#4ECDC4", width=2)
        draw.polygon([(dcx - 5, dy2 - 7), (dcx + 5, dy2 - 7), (dcx, dy2)], fill="#4ECDC4")
        if arrow_lbl:
            draw.text((dcx + 10, dy1 + 10), arrow_lbl, font=tiny_ft, fill="#4ECDC4")

        done_w, done_h = 140, 50
        draw.rounded_rectangle([dcx - done_w // 2, dy2 + 5, dcx + done_w // 2, dy2 + 5 + done_h],
                               radius=10, fill="#4ECDC4" + "33", outline="#4ECDC4", width=2)
        bb = draw.textbbox((0, 0), done["label"], font=label_ft)
        draw.text((dcx - (bb[2] - bb[0]) // 2, dy2 + 18), done["label"], font=label_ft, fill="#2E8B57")

    # Bottom note
    if bottom_note:
        draw.rounded_rectangle([50, H - 65, W - 50, H - 20], radius=8, fill="#F5F5F5", outline="#E0E0E0", width=1)
        bb = draw.textbbox((0, 0), bottom_note, font=tiny_ft)
        draw.text(((W - bb[2] + bb[0]) // 2, H - 52), bottom_note, font=tiny_ft, fill="#666666")

    return img


def render_quote(data):
    text = data["text"]
    source = data.get("source", "")
    accent = data.get("accent_color", "#45B7D1")

    H = 280
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    shadow_rect(draw, [60, 40, W - 60, H - 40], 20, CARD_BG)

    # Accent bar
    draw.rounded_rectangle([60, 40, 68, H - 40], radius=4, fill=accent)

    quote_ft = font(32, True)
    source_ft = font(22)

    draw_text_wrapped(draw, 100, 75, text, quote_ft, TITLE_CLR, W - 200)

    if source:
        bb = draw.textbbox((0, 0), f"— {source}", font=source_ft)
        draw.text((W - 100 - bb[2] + bb[0], H - 90), f"— {source}", font=source_ft, fill=DESC_CLR)

    return img


def render_stats(data):
    metrics = data["metrics"]
    title = data.get("title", "")

    title_ft = font(36, True)
    val_ft = font(48, True)
    label_ft = font(22)

    H = 300
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    if title:
        draw.text((50, 25), title, font=title_ft, fill=TITLE_CLR)

    shadow_rect(draw, [40, 85, W - 40, H - 30], 20, CARD_BG)

    n = len(metrics)
    slot_w = (W - 120) // n

    for i, m in enumerate(metrics):
        cx = 60 + i * slot_w + slot_w // 2
        clr = m.get("color", ACCENTS[i % len(ACCENTS)])

        val = m["value"]
        bb = draw.textbbox((0, 0), val, font=val_ft)
        draw.text((cx - (bb[2] - bb[0]) // 2, 115), val, font=val_ft, fill=clr)

        lbl = m["label"]
        bb = draw.textbbox((0, 0), lbl, font=label_ft)
        draw.text((cx - (bb[2] - bb[0]) // 2, 195), lbl, font=label_ft, fill=DESC_CLR)

    return img


def render_architecture(data):
    title = data.get("title", "")
    layers = data.get("layers", [])
    center_box = data.get("center_box")
    bottom_note = data.get("bottom_note")

    title_ft = font(36, True)
    label_ft = font(24, True)
    small_ft = font(22)
    tiny_ft = font(18)
    mod_ft = font(20)

    H = 750
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((50, 25), title, font=title_ft, fill=TITLE_CLR)

    # Render layers top-to-bottom
    layer_y = 95
    layer_positions = []

    for li, layer in enumerate(layers):
        boxes = layer.get("boxes", [])
        lbl = layer.get("label", "")

        bw, bh = 200, 65
        gap_b = 28
        total_bw = len(boxes) * bw + (len(boxes) - 1) * gap_b
        bsx = (W - total_bw) // 2

        box_positions = []
        for bi, bx in enumerate(boxes):
            x = bsx + bi * (bw + gap_b)
            clr = bx.get("color", ACCENTS[bi % len(ACCENTS)])
            draw.rounded_rectangle([x, layer_y, x + bw, layer_y + bh], radius=12, fill=clr + "22", outline=clr, width=2)
            bb = draw.textbbox((0, 0), bx["label"], font=small_ft)
            draw.text((x + (bw - bb[2] + bb[0]) // 2, layer_y + 18), bx["label"], font=small_ft, fill=TITLE_CLR)
            box_positions.append((x, layer_y, bw, bh))

        layer_positions.append({"y": layer_y, "h": bh, "boxes": box_positions})
        layer_y += bh + 80  # space for arrows

        # Center box between layers
        if center_box and li == 0:
            # Arrows down
            ay1 = layer_positions[-1]["y"] + bh + 8
            ay2 = ay1 + 50
            for bp in box_positions:
                ax = bp[0] + bp[2] // 2
                draw.line([(ax, ay1), (ax, ay2)], fill="#BBBBBB", width=2)
                draw.polygon([(ax - 5, ay2 - 7), (ax + 5, ay2 - 7), (ax, ay2)], fill="#BBBBBB")

            # Center box
            cb_clr = center_box.get("color", "#FFB347")
            dh = 210
            dx1, dx2 = 80, W - 80
            dy = ay2 + 18
            draw.rounded_rectangle([dx1, dy, dx2, dy + dh], radius=20, fill=cb_clr + "15", outline=cb_clr, width=2)
            draw.text((dx1 + 25, dy + 14), center_box["label"], font=label_ft, fill=cb_clr.replace("#", ""))

            # Sub-modules
            subs = center_box.get("sub_modules", [])
            if subs:
                mw, mh = 160, 46
                mg = 10
                tm = len(subs) * mw + (len(subs) - 1) * mg
                msx = (W - tm) // 2
                my = dy + 65
                for si, mod in enumerate(subs):
                    mx = msx + si * (mw + mg)
                    draw.rounded_rectangle([mx, my, mx + mw, my + mh], radius=8, fill="#FFFFFF", outline=cb_clr + "66", width=1)
                    bb = draw.textbbox((0, 0), mod, font=mod_ft)
                    draw.text((mx + (mw - bb[2] + bb[0]) // 2, my + 12), mod, font=mod_ft, fill=TITLE_CLR)

            if center_box.get("note"):
                draw.text((dx1 + 25, dy + dh - 50), center_box["note"], font=tiny_ft, fill="#BBBBBB")

            # Arrows to next layer
            layer_y = dy + dh + 80
            next_ay1 = dy + dh + 8
            next_ay2 = next_ay1 + 50
            for bp in layer_positions[-1]["boxes"]:
                ax = bp[0] + bp[2] // 2
                draw.line([(ax, next_ay1), (ax, next_ay2)], fill="#BBBBBB", width=2)
                draw.polygon([(ax - 5, next_ay2 - 7), (ax + 5, next_ay2 - 7), (ax, next_ay2)], fill="#BBBBBB")

    if bottom_note:
        bb = draw.textbbox((0, 0), bottom_note, font=tiny_ft)
        draw.text(((W - bb[2] + bb[0]) // 2, H - 40), bottom_note, font=tiny_ft, fill="#AAAAAA")

    return img


# ════════════════════════════════════════
# Dispatcher
# ════════════════════════════════════════

RENDERERS = {
    "list": render_list,
    "comparison": render_comparison,
    "terminal": render_terminal,
    "fit": render_fit,
    "flow": render_flow,
    "quote": render_quote,
    "stats": render_stats,
    "architecture": render_architecture,
}


def main():
    parser = argparse.ArgumentParser(description="Render card PNG from JSON data.")
    parser.add_argument("--data", help="JSON string")
    parser.add_argument("--data-file", help="Path to JSON file")
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument("--font-dir", help="Font directory override")
    args = parser.parse_args()

    global FONT_DIR
    if args.font_dir:
        FONT_DIR = args.font_dir

    if args.data_file:
        with open(args.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif args.data:
        data = json.loads(args.data)
    else:
        print("Error: provide --data or --data-file", file=sys.stderr)
        sys.exit(1)

    card_type = data.get("card_type")
    if card_type not in RENDERERS:
        print(f"Error: unknown card_type '{card_type}'. Available: {list(RENDERERS.keys())}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    img = RENDERERS[card_type](data)
    img.save(args.output, quality=95)
    print(f"Saved {args.output} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
