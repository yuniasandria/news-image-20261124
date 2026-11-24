#!/usr/bin/env python3
"""Sum up Tuesday 24 November 2026's world news in one 1024x1024 image.

Pure stdlib (zlib + struct + the generated bitmap font data in fontdata.py).
Deterministic: same bytes on every run. Writes /output/entry.png by default.
"""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontdata import FONTS  # noqa: E402

W = H = 1024

NAVY = (14, 42, 71)
GOLD = (201, 162, 39)
PALE_GOLD = (242, 217, 140)
CREAM = (255, 246, 219)
PAGE = (245, 241, 230)
INK = (20, 28, 38)
GREEN = (11, 122, 62)
WHITE = (255, 255, 255)
BORDER = (216, 210, 192)
GREY = (90, 90, 90)
TEAL = (13, 110, 110)
BLUE = (30, 80, 160)
ORANGE = (176, 84, 0)
PURPLE = (96, 60, 140)
DARKGREEN = (11, 110, 60)
CRIMSON = (150, 30, 40)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            o = (yy * self.w + x0) * 3
            self.px[o:o + len(row)] = row

    def text_width(self, font, text, scale=1):
        f = FONTS[font]
        return sum(f["glyphs"].get(ord(c), f["glyphs"][32])[0] for c in text) * scale

    def draw_text(self, font, x, y, text, color, scale=1):
        """Draw text with its top at y (ascender top). Returns end x."""
        f = FONTS[font]
        glyphs = f["glyphs"]
        cx = x
        for ch in text:
            g = glyphs.get(ord(ch), glyphs[32])
            adv, gw, gh, yoff, rows_hex = g
            if gw and gh:
                rows = bytes.fromhex(rows_hex)
                bpr = (gw + 7) // 8
                for gy in range(gh):
                    row = rows[gy * bpr:(gy + 1) * bpr]
                    for gx in range(gw):
                        if row[gx // 8] & (0x80 >> (gx % 8)):
                            self.fill_rect(cx + gx * scale, y + (yoff + gy) * scale,
                                           scale, scale, color)
            cx += adv * scale
        return cx

    def draw_centered(self, font, cx, y, text, color, scale=1):
        w = self.text_width(font, text, scale)
        return self.draw_text(font, cx - w // 2, y, text, color, scale)

    def fill_polygon(self, points, color):
        """Scanline fill for a simple polygon (list of (x, y))."""
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    t = (y - y1) / (y2 - y1)
                    xs.append(x1 + t * (x2 - x1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, color)


def png_bytes(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: None
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0))
    out += chunk(b"IDAT", comp)
    out += chunk(b"IEND", b"")
    return bytes(out)


CARDS = [
    ("CLIMATE", TEAL, ["COP31 ENDS", "WITH NO DEAL"], "92,000",
     ["No pact in Antalya;", "first failed COP"]),
    ("WAR AT SEA", BLUE, ["UKRAINE SINKS", "RUSSIAN SHIP"], "1 SHIP",
     ["Ukraine drones sink", "the corvette Merkury"]),
    ("INDONESIA", ORANGE, ["FACTORY FIRE", "IN INDONESIA"], "24",
     ["dead, ~30 missing", "in Banten, Indonesia"]),
    ("USA", PURPLE, ["DEMOCRATS", "WIN THE HOUSE"], "258",
     ["House seats - largest", "majority since 1992"]),
    ("CHESS", DARKGREEN, ["WORLD CHESS", "MATCH BEGINS"], "$2.5M",
     ["Game 1 in Geneva;", "14 games, both 20"]),
    ("IOWA", CRIMSON, ["TRUMP HALTS", "IOWA BLAST"], "9,773",
     ["lb of lead azide;", "paused by Trump"]),
]


def draw():
    c = Canvas(W, H, PAGE)
    # --- Banner ---
    c.fill_rect(0, 0, W, 108, NAVY)
    c.draw_centered("BOLD24", W // 2, 14, "THE WORLD IN ONE PICTURE", GOLD)
    c.draw_centered("BOLD56", W // 2, 44, "TUESDAY 24 NOVEMBER 2026", WHITE)
    # --- Gold strip ---
    c.fill_rect(0, 108, W, 40, PALE_GOLD)
    c.draw_centered("BOLD24", W // 2, 118, "SEVEN STORIES THAT DEFINED THE DAY", NAVY)
    # --- Lead story (pale, clean) ---
    c.fill_rect(0, 148, W, 320, CREAM)
    c.draw_text("BOLD24", 32, 166, "MARKETS - LEAD STORY", GREEN)
    c.draw_text("BOLD56", 32, 200, "NVIDIA BRINGS", INK)
    c.draw_text("BOLD56", 32, 264, "BACK ITS CEO", INK)
    c.draw_text("REG26", 32, 336, "The board unanimously reinstates", INK)
    c.draw_text("REG26", 32, 368, "Jensen Huang, 11 days after he quit.", INK)
    c.draw_text("REG26", 32, 400, "Nvidia's best day since 2003.", INK)
    # divider
    c.fill_rect(580, 168, 2, 280, BORDER)
    # right: big number + up arrow + rising bars
    c.draw_text("BOLD56", 612, 176, "+31.5%", GREEN)
    # green up arrow beside the number
    c.fill_polygon([(872, 176), (928, 176), (900, 148)], GREEN)
    c.fill_rect(888, 176, 24, 56, GREEN)
    bars = [26, 52, 82, 112, 142]
    bx = 612
    for bh in bars:
        c.fill_rect(bx, 400 - bh, 56, bh, GREEN)
        bx += 72
    c.draw_text("REG26", 612, 412, "Fri $125.53 to Mon $164.48", INK)
    c.draw_text("REG26", 612, 440, "+$952bn added in one day", INK)
    # --- Grid of text-led cards ---
    for i, (kicker, accent, head, num, ctx) in enumerate(CARDS):
        col, row = i % 3, i // 3
        x = 24 + col * (312 + 20)
        y = 484 + row * (240 + 16)
        c.fill_rect(x, y, 312, 240, WHITE)
        c.fill_rect(x, y, 312, 8, accent)
        # border
        c.fill_rect(x, y, 312, 2, BORDER)
        c.fill_rect(x, y + 238, 312, 2, BORDER)
        c.fill_rect(x, y, 2, 240, BORDER)
        c.fill_rect(x + 310, y, 2, 240, BORDER)
        c.draw_text("BOLD24", x + 16, y + 16, kicker, accent)
        c.draw_text("BOLD30", x + 16, y + 48, head[0], INK)
        c.draw_text("BOLD30", x + 16, y + 84, head[1], INK)
        c.draw_text("BOLD30", x + 16, y + 126, num, accent, scale=2)
        c.draw_text("REG26", x + 16, y + 178, ctx[0], INK)
        c.draw_text("REG26", x + 16, y + 208, ctx[1], INK)
    # --- Footer ---
    c.fill_rect(0, 980, W, 44, NAVY)
    c.draw_centered("REG26", W // 2, 997,
                    "Figures as reported 23-24 Nov 2026 - Reuters - AP - BBC - CNN - FIDE",
                    WHITE)
    return c


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    data = png_bytes(draw())
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "wb") as f:
        f.write(data)
    print("wrote", out, len(data), "bytes")


if __name__ == "__main__":
    main()
