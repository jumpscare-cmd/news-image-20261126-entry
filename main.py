#!/usr/bin/env python3
"""Draw the front page of THE WORLD TODAY for Thursday, 26 November 2026.

Standard library only. No network, no randomness, no timestamps: running
this program twice writes byte-identical PNG files.

The image is a 1024x1024 newspaper front page: masthead, date line, one
lead story with a drawn globe, a small markets bar chart, and seven more
stories in three columns, plus a sources footer.
"""

import os
import struct
import zlib

W, H = 1024, 1024
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (110, 110, 110)
BLUE = (30, 60, 120)
RED = (170, 30, 30)

# 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11110", "01000", "01000", "01001", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "10001", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ';': ("00000", "01100", "00000", "01100", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width pixels."""
    char_w = 6 * scale
    max_chars = max(1, max_width // char_w)
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if len(trial) <= max_chars:
                line = trial
            else:
                if line:
                    lines.append(line)
                # A single over-long word is split hard.
                while len(word) > max_chars:
                    lines.append(word[:max_chars])
                    word = word[max_chars:]
                line = word
        if line:
            lines.append(line)
    return lines


class Canvas:
    def __init__(self, w, h, bg=WHITE):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def circle(self, cx, cy, r, color, thick=2):
        # Midpoint circle outline.
        x, y, d = 0, r, 1 - r
        while x <= y:
            for dx, dy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                for t in range(thick):
                    self.set(cx + dx, cy + dy + t, color)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

    def ellipse(self, cx, cy, rx, ry, color, thick=1):
        # Parametric ellipse outline, 1-degree steps.
        import math
        for deg in range(360):
            a = math.radians(deg)
            x = int(round(cx + rx * math.cos(a)))
            y = int(round(cy + ry * math.sin(a)))
            for t in range(thick):
                self.set(x, y + t, color)

    def draw_glyph(self, x, y, ch, scale, color):
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT['?']
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    self.rect(x + col * scale, y + row * scale,
                              scale, scale, color)

    def text(self, x, y, s, scale, color, bold=False, align="left"):
        w = text_width(s, scale)
        if align == "center":
            x = x - w // 2
        elif align == "right":
            x = x - w
        for ch in s:
            self.draw_glyph(x, y, ch, scale, color)
            if bold:
                self.draw_glyph(x + max(1, scale // 3), y, ch, scale, color)
            x += 6 * scale
        return w

    def paragraph(self, x, y, s, max_width, scale, color, leading=None):
        if leading is None:
            leading = 7 * scale + 1
        lines = wrap_text(s, max_width, scale)
        for line in lines:
            self.text(x, y, line, scale, color)
            y += leading
        return y


def png_bytes(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        raw += canvas.px[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# The day's news: Thursday, 26 November 2026.
# Stories verified against Reuters, Associated Press, Al Jazeera, BBC,
# Daily Maverick, Qatar Tribune and other outlets reporting on 26 Nov 2026.
# Figures are given only where at least two outlets agreed; disputed
# figures are left out and claims are attributed ("claimed", "said").
# ---------------------------------------------------------------------------

LEAD_KICKER = "MIDDLE EAST"
LEAD_HEAD = ["OIL NEARS $95 AS", "HOUTHI ATTACKS WIDEN"]
LEAD_BODY = (
    "Yemen's Houthis widened their attacks on Saudi Arabia, striking Red "
    "Sea ports and claiming a hit on the Ras Tanura refinery, the kingdom's "
    "largest. Saudi Arabia said it shot down drones over the site. Brent "
    "crude held near $95 a barrel after a 3.5 percent jump."
)

# (kicker, headline, body) for the three columns.
COLUMNS = [
    [
        ("TRADE", "U.S. SETS NEW TARIFFS ON 14 PARTNERS",
         "Washington proposed new tariffs on 14 trading partners, including "
         "China, the EU and Japan, after a probe into excess factory "
         "capacity. China faces the highest rate, at 20 percent."),
        ("MARKETS", "STOCKS SLIDE AS AI FEARS SPREAD",
         "The Nasdaq fell almost 4 percent as a sell-off in AI stocks "
         "spread, with all three main U.S. indexes down."),
    ],
    [
        ("SOUTH AFRICA", "COURT ENDS BID TO IMPEACH RAMAPHOSA",
         "The Western Cape High Court set aside the 2022 panel report that "
         "had exposed President Cyril Ramaphosa to impeachment over the "
         "Phala Phala farm theft. Parliament's inquiry falls away."),
        ("BANGLADESH", "GARMENT WORKERS WIN 36% PAY RISE",
         "Bangladesh raised the minimum wage for garment workers by 36 "
         "percent after weeks of protests that shut hundreds of factories. "
         "Workers had sought 30,000 taka a month."),
    ],
    [
        ("EGYPT", "31 KILLED IN CAIRO TANKER FIRE",
         "A fuel tanker overturned and caught fire on Cairo's ring road, "
         "killing at least 31 people."),
        ("NORTH KOREA", "PYONGYANG EXPELS SWISS DIPLOMAT",
         "North Korea ordered Switzerland to close its new office in "
         "Pyongyang, in a row over sanctions."),
        ("SPACE", "FIRST FOREIGN ASTRONAUT FOR CHINA STATION",
         "Pakistan's Muhammad Zeeshan Ali is to be the first foreign "
         "astronaut on China's Tiangong station."),
    ],
]

# (label, value in percent) for the markets bar chart.
BARS = [("BRENT", 3.5), ("WTI", 2.0), ("NASDAQ", -4.0)]

FOOTER = "Sources: Reuters, Associated Press, Al Jazeera, Daily Maverick and others."


def draw_globe(c, cx, cy, r):
    c.circle(cx, cy, r, BLUE, thick=2)
    c.ellipse(cx, cy, r, r // 3, BLUE)          # equator
    c.ellipse(cx, cy, r // 3, r, BLUE)          # central meridian
    c.ellipse(cx, cy, (r * 2) // 3, r, BLUE)    # outer meridians
    c.ellipse(cx, cy, r, (r * 2) // 3, BLUE)    # tropics
    c.ellipse(cx, cy, r, r // 3, BLUE)
    c.hline(cx - r, cy, 2 * r, BLUE)


def draw_bars(c, x, y, width):
    """Compact horizontal bar chart: label, bar, value per row."""
    c.text(x, y, "MARKETS, IN PERCENT", 2, BLACK, bold=True)
    y += 18
    zero_x = x + 92
    for label, val in BARS:
        c.text(x, y, label, 2, BLACK, bold=True)
        length = int(abs(val) * 14)
        color = RED if val < 0 else BLUE
        c.rect(zero_x, y + 2, length, 10, color)
        sign = "+" if val >= 0 else ""
        c.text(zero_x + length + 8, y, "%s%.1f%%" % (sign, val), 2, color)
        y += 22
    return y


def draw_story(c, x, y, width, kicker, head, body):
    c.text(x, y, kicker, 2, RED, bold=True)
    y += 16
    y = c.paragraph(x, y, head, width, 3, BLACK, leading=21)
    y += 4
    y = c.paragraph(x, y, body, width, 2, BLACK, leading=14)
    return y


def draw():
    c = Canvas(W, H)
    # Page frame.
    c.rect(10, 10, W - 20, 2, BLACK)
    c.rect(10, H - 12, W - 20, 2, BLACK)
    c.rect(10, 10, 2, H - 20, BLACK)
    c.rect(W - 12, 10, 2, H - 20, BLACK)

    # Masthead.
    c.text(W // 2, 26, "THE WORLD TODAY", 6, BLACK, bold=True, align="center")
    c.hline(30, 82, W - 60, BLACK, thick=3)
    c.hline(30, 88, W - 60, BLACK, thick=1)

    # Date line, large and unmistakable.
    c.text(W // 2, 102, "THURSDAY, 26 NOVEMBER 2026", 4, BLACK, bold=True,
           align="center")
    c.hline(30, 142, W - 60, BLACK, thick=1)

    # Lead story, left; globe, right.
    c.text(30, 160, LEAD_KICKER, 2, RED, bold=True)
    y = 182
    for line in LEAD_HEAD:
        c.text(30, y, line, 4, BLACK, bold=True)
        y += 30
    y += 6
    c.paragraph(30, y, LEAD_BODY, 600, 2, BLACK, leading=16)

    draw_globe(c, 820, 258, 92)
    c.text(820, 366, "THE WORLD, 26 NOVEMBER", 2, BLUE, bold=True,
           align="center")

    c.hline(30, 448, W - 60, BLACK, thick=2)

    # Three columns of stories.
    col_x = [30, 360, 690]
    col_w = 300
    for ci, stories in enumerate(COLUMNS):
        y = 468
        for kicker, head, body in stories:
            y = draw_story(c, col_x[ci], y, col_w, kicker, head, body)
            y += 18
        if ci == 0:
            draw_bars(c, col_x[ci], y + 2, col_w)
        if ci < 2:
            c.vline(col_x[ci] + col_w + 15, 468, 470, GREY, thick=1)

    # Footer.
    c.hline(30, 956, W - 60, BLACK, thick=1)
    c.text(W // 2, 966, FOOTER, 2, BLACK, align="center")
    c.text(W // 2, 986, "THE WORLD TODAY - 26 NOVEMBER 2026", 2, BLACK,
           bold=True, align="center")
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes(draw()))
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
