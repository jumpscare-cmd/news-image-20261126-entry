#!/usr/bin/env python3
"""The World Today -- newspaper front page for Thursday, 26 November 2026.

Stdlib only. Draws entry.png (1024x1024) with a hand-built 5x7 bitmap
font. Fully deterministic: no network, no randomness, no timestamps.
Run: python3 main.py  (writes entry.png next to main.py)
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (163, 18, 18)
GREY = (90, 86, 76)

# 5x7 bitmap font: 7 rows of 5 bits, "#" = on, "." = off.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "00100", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap(text, scale, max_w):
    """Greedy word wrap; returns list of lines."""
    per = max(1, max_w // (6 * scale))
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        cand = w if not cur else cur + " " + w
        if len(cand) <= per:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    # Avoid stranding a lone word on the last line: pull the previous
    # line's final word down when the pair still fits the line width.
    # (Greedy wrapping left e.g. "KIM VOWS MORE NUCLEAR / ARMS" and
    # "LEBANON PLANS SECOND / AIRPORT" with a one-word second line.)
    if len(lines) >= 2 and " " not in lines[-1]:
        prev = lines[-2].rsplit(" ", 1)
        if len(prev) == 2:
            moved = prev[1] + " " + lines[-1]
            if len(moved) <= per:
                lines[-2] = prev[0]
                lines[-1] = moved
    return lines


class Canvas:
    def __init__(self):
        self.px = bytearray(PAPER * W * H)

    def set(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def circle(self, cx, cy, r, color, thick=2):
        for deg in range(0, 360):
            a = math.radians(deg)
            for t in range(thick):
                self.set(int(cx + (r - t) * math.cos(a)),
                         int(cy + (r - t) * math.sin(a)), color)

    def ellipse_arc(self, cx, cy, rx, ry, color):
        for deg in range(0, 360):
            a = math.radians(deg)
            self.set(int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a)), color)

    def line(self, x0, y0, x1, y1, color):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.set(int(x0 + (x1 - x0) * i / n), int(y0 + (y1 - y0) * i / n), color)

    def draw_text(self, x, y, text, scale, color):
        text = text.upper()
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_centered(self, y, text, scale, color, cx=W // 2):
        self.draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)

    def png_bytes(self):
        raw = bytearray()
        stride = W * 3
        for y in range(H):
            raw.append(0)
            raw.extend(self.px[y * stride:(y + 1) * stride])

        def chunk(ctype, data):
            out = struct.pack(">I", len(data)) + ctype + data
            out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))


LEAD_HEAD = "U.S. PROPOSES NEW TARIFFS ON 14 PARTNERS"
LEAD_SUM = ("Washington cites excess factory capacity. China, the EU, Japan "
            "and India face new levies as markets fall and AI shares slide.")

# (section, headline, summary) -- 28 items, summaries <= 50 chars.
ITEMS = [
    ("TRADE & ECONOMY", "SEOUL VOWS TARIFF TALKS",
     "South Korea to defend its factories in US talks."),
    ("TRADE & ECONOMY", "TOKYO PROTESTS 15% LEVY",
     "Japan rejects excess-capacity claim behind levy."),
    ("TRADE & ECONOMY", "ASIA LINKS PAYMENT SYSTEMS",
     "China, Japan, Korea and ASEAN plan shared rules."),
    ("TRADE & ECONOMY", "OIL NEARS $95 ON SUPPLY FEARS",
     "Houthi strikes and Hormuz mines lift crude prices."),
    ("TRADE & ECONOMY", "NVIDIA HALTS SE ASIA SHIPMENTS",
     "Deliveries to four nations stopped, FT reports."),
    ("TECHNOLOGY", "CHIP CURBS SLOW CHINA AI",
     "US rules delay flagship models at Z.AI, Moonshot."),
    ("TECHNOLOGY", "FCC CLEARS 1M SPACE SATELLITES",
     "SpaceX can orbit data centres, starting by 2033."),
    ("TECHNOLOGY", "JAXA SHOWS MOON ROVER MODEL",
     "Joint Japan-India craft to hunt for lunar water."),
    ("TECHNOLOGY", "UBER NAMES INDIA CHIEF",
     "Rakesh Ranjan to lead India and South Asia in Jan."),
    ("TECHNOLOGY", "HUANG BACK AT NVIDIA",
     "Jensen Huang returns amid US scrutiny over chips."),
    ("ASIA & PACIFIC", "KIM VOWS MORE NUCLEAR ARMS",
     "Kim orders wider tactical nuclear deployment."),
    ("ASIA & PACIFIC", "MYANMAR REJECTS COURT RULING",
     "Junta leader defies parts of world court order."),
    ("ASIA & PACIFIC", "JAPAN CENSURE MOTION FILED",
     "Opposition targets minister in fundraising scandal."),
    ("ASIA & PACIFIC", "TEPCO DELAYS REACTOR RESTART",
     "Niigata unit pushed back by more than a year."),
    ("ASIA & PACIFIC", "HONG KONG MOURNS FIRE DEAD",
     "City remembers 168 killed in housing complex blaze."),
    ("MIDDLE EAST & CONFLICT", "US TELLS CITIZENS: LEAVE IRAN",
     "Washington warns hostilities could escalate fast."),
    ("MIDDLE EAST & CONFLICT", "ISRAELI STRIKE KILLS HAMAS CHIEF",
     "Security head hit in northern Gaza, reports say."),
    ("MIDDLE EAST & CONFLICT", "HOUTHIS HIT SAUDI REFINERY",
     "Ras Tanura attacked as Gulf tensions widen."),
    ("MIDDLE EAST & CONFLICT", "TRUMP AND NATO WARN MOSCOW",
     "Russia urged not to widen its war in Ukraine."),
    ("MIDDLE EAST & CONFLICT", "LEBANON PLANS SECOND AIRPORT",
     "Northern gateway signals Hezbollah's waning sway."),
    ("AFRICA & HEALTH", "CAIRO TANKER FIRE KILLS 31",
     "Fuel truck blaze on ring road injures about 21."),
    ("AFRICA & HEALTH", "CONGO EBOLA TOPS 12,000 CASES",
     "Outbreak deaths reach 5,904, government data show."),
    ("AFRICA & HEALTH", "KENYA COURT FAULTS EBOLA SITE",
     "US-backed quarantine build breached constitution."),
    ("AFRICA & HEALTH", "TURKEY MARCHES AGAINST ABUSE",
     "Thousands protest violence against women."),
    ("EUROPE & AMERICAS", "MACY PARADE MOVED TO SATURDAY",
     "Storm postpones 100th parade for first time."),
    ("EUROPE & AMERICAS", "BIRTHRIGHT ORDER BLOCKED AGAIN",
     "Second US judge halts Trump citizenship curbs."),
    ("EUROPE & AMERICAS", "SINNER OUT OF AUSTRALIAN OPEN",
     "Two-time champion to miss event after knee surgery."),
    ("EUROPE & AMERICAS", "GUARDIOLA EYES NATIONAL JOB",
     "Guardiola says his next job is a national team."),
]

COLUMNS = [
    ["TRADE & ECONOMY", "TECHNOLOGY"],
    ["ASIA & PACIFIC", "MIDDLE EAST & CONFLICT"],
    ["AFRICA & HEALTH", "EUROPE & AMERICAS"],
]


def draw_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, INK, 3)
    cv.ellipse_arc(cx, cy, r, r // 3, INK)
    cv.ellipse_arc(cx, cy, r // 3, r, INK)
    cv.hline(cx - r, cy, 2 * r, INK)
    cv.line(cx, cy - r, cx, cy + r, INK)
    # simple continents as filled blocks
    cv.rect(cx - 38, cy - 30, 26, 14, INK)
    cv.rect(cx - 6, cy - 38, 20, 12, INK)
    cv.rect(cx + 8, cy + 6, 30, 16, INK)
    cv.rect(cx - 30, cy + 18, 18, 10, INK)
    cv.rect(cx + 22, cy - 26, 12, 10, INK)


def build():
    cv = Canvas()
    mx = 28
    # --- masthead ---
    cv.text_centered(20, "THE WORLD TODAY", 5, INK)
    cv.hline(mx, 66, W - 2 * mx, INK, 3)
    cv.hline(mx, 71, W - 2 * mx, INK, 1)
    cv.text_centered(82, "THURSDAY, 26 NOVEMBER 2026", 3, RED)
    cv.text_centered(112, "29 STORIES FROM EVERY REGION - THE DAY IN FULL", 1, GREY)
    cv.hline(mx, 132, W - 2 * mx, INK, 2)

    # --- lead story ---
    cv.draw_text(mx, 150, "LEAD STORY - TRADE WAR", 1, RED)
    y = 170
    for line in wrap(LEAD_HEAD, 3, 600):
        cv.draw_text(mx, y, line, 3, INK)
        y += 26
    y += 4
    for line in wrap(LEAD_SUM, 1, 600):
        cv.draw_text(mx, y, line, 1, INK)
        y += 11
    draw_globe(cv, 872, 218, 62)
    cv.draw_text(812, 292, "THE WORLD, TODAY", 1, GREY)
    cv.hline(mx, 312, W - 2 * mx, INK, 2)

    # --- columns ---
    col_w = 304
    col_x = [mx, mx + col_w + 24, mx + 2 * (col_w + 24)]
    top = 330
    for ci, sections in enumerate(COLUMNS):
        x = col_x[ci]
        y = top
        for sec in sections:
            cv.rect(x, y + 2, 10, 10, RED)
            cv.draw_text(x + 16, y, sec, 1, INK)
            cv.hline(x, y + 14, col_w, INK, 1)
            y += 24
            for (s, head, summ) in ITEMS:
                if s != sec:
                    continue
                for line in wrap(head, 2, col_w):
                    cv.draw_text(x, y, line, 2, INK)
                    y += 17
                for line in wrap(summ, 1, col_w):
                    cv.draw_text(x, y, line, 1, GREY)
                    y += 10
                y += 9
            y += 6

    # --- footer ---
    cv.hline(mx, 968, W - 2 * mx, INK, 2)
    cv.text_centered(980, "THE WORLD TODAY - THURSDAY, 26 NOVEMBER 2026", 1, INK)
    cv.text_centered(994, "SOURCES: REUTERS, AP, KYODO, JAPAN TIMES, ECONOMIC TIMES", 1, GREY)
    return cv.png_bytes()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "entry.png"), "wb") as f:
        f.write(build())


if __name__ == "__main__":
    main()
