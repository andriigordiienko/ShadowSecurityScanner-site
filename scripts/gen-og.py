#!/usr/bin/env python3
"""Generate the website social-share card (assets/og-image.png).

A 1200x630 Open Graph / Twitter card on-brand with the app (SOC-dark +
cyan accent). Run from the repo root:

    python3 scripts/gen-og.py        # needs Pillow:  pip install Pillow

Edit the copy/colours below and re-run; commit the regenerated PNG.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "og-image.png")

# macOS system fonts; swap for any TTF if you're elsewhere.
ARB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
AR = "/System/Library/Fonts/Supplemental/Arial.ttf"

W, H = 1200, 630


def main():
    img = Image.new("RGBA", (W, H), "#0a0e16")
    d = ImageDraw.Draw(img)
    top, bot = (10, 14, 22), (13, 19, 32)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(
            int(top[0] + (bot[0] - top[0]) * t),
            int(top[1] + (bot[1] - top[1]) * t),
            int(top[2] + (bot[2] - top[2]) * t), 255))

    # cyan glow, top-right
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = 980, 110
    for rad in range(440, 0, -6):
        a = int(40 * (1 - rad / 440))
        gd.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(56, 189, 248, a))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)

    def F(p, s):
        return ImageFont.truetype(p, s)

    # shield mark
    sx, sy, sw, sh = 90, 160, 150, 180
    d.polygon([(sx, sy + 20), (sx + sw // 2, sy), (sx + sw, sy + 20),
               (sx + sw, sy + sh * 0.55), (sx + sw // 2, sy + sh),
               (sx, sy + sh * 0.55)], fill=(12, 135, 201, 255))
    ins = 16
    d.polygon([(sx + ins, sy + 20 + ins * 0.7), (sx + sw // 2, sy + ins),
               (sx + sw - ins, sy + 20 + ins * 0.7),
               (sx + sw - ins, sy + sh * 0.55 - ins * 0.4),
               (sx + sw // 2, sy + sh - ins),
               (sx + ins, sy + sh * 0.55 - ins * 0.4)], fill=(56, 189, 248, 255))
    d.line([(sx + sw * 0.32, sy + sh * 0.45), (sx + sw * 0.46, sy + sh * 0.60),
            (sx + sw * 0.72, sy + sh * 0.28)], fill=(10, 14, 22, 255),
           width=14, joint="curve")

    tx = 280
    maxw = W - tx - 70
    ts = 84
    while d.textlength("ShadowSecurityScanner", font=F(ARB, ts)) > maxw and ts > 48:
        ts -= 2
    f_title = F(ARB, ts)
    f_sub, f_tag = F(AR, 36), F(ARB, 30)
    f_small, f_chip = F(AR, 25), F(ARB, 24)

    d.text((tx, 158), "ShadowSecurityScanner", font=f_title, fill="#f4f7fb")
    d.text((tx, 158 + ts + 18), "Modern network vulnerability scanner",
           font=f_sub, fill="#9fb0c3")
    d.text((tx, 330), "Fix what's actually exploited.", font=f_tag, fill="#38bdf8")

    chips = [("CRITICAL", "#f04747"), ("HIGH", "#ff8c42"), ("EPSS", "#38bdf8"),
             ("KEV", "#f04747"), ("SARIF", "#7c8aa0")]
    x, y = tx, 405
    for label, col in chips:
        w = d.textlength(label, font=f_chip)
        pad = 18
        d.rounded_rectangle([x, y, x + w + pad * 2, y + 46], radius=10,
                            outline=col, width=2)
        d.text((x + pad, y + 9), label, font=f_chip, fill=col)
        x += w + pad * 2 + 16

    d.line([(tx, 498), (W - 90, 498)], fill=(60, 75, 95, 120), width=1)
    d.text((tx, 518),
           "Open-source · self-hosted · no cloud   ·   Windows · macOS · Linux",
           font=f_small, fill="#7c8aa0")

    img.convert("RGB").save(OUT, "PNG")
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
