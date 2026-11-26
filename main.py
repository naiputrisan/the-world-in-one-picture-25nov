#!/usr/bin/env python3
"""The World in One Page - Wednesday 25 November 2026.

Draws a maximal-density broadsheet poster of the day's world news with the
Python standard library only, and writes it to /output/entry.png.

Layout (1024x1024): masthead, stat strip, hero panel, 12 numbered panels in
a 3x4 grid, an ALSO band of 18 more stories, a pin map and a DATE CHECK box
for the big stories that failed the Wednesday date rule, plus a sources
footer. Every event on the poster happened, or was first reported, on
Wednesday 25 November 2026 (local date); every figure is a Wednesday close
or final result.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# --- palette ---------------------------------------------------------------
PAPER = (250, 248, 240)
INK = (22, 22, 22)
GREY = (110, 108, 100)
RED = (176, 32, 32)
DARKRED = (120, 20, 20)
BLUE = (28, 68, 120)
OCEAN = (196, 216, 228)
LAND = (232, 222, 190)
LANDBORDER = (170, 158, 120)
PANELBG = (255, 255, 255)
PANELLINE = (180, 175, 160)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (250, 220, 120)

# --- 5x7 bitmap font -------------------------------------------------------
# Each glyph is 7 rows of 5 bits, '#' = pixel on, '.' = off.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
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
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01111", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01000", "10000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "–": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "—": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "°": ("01100", "10010", "01100", "00000", "00000", "00000", "00000"),
    "·": ("00000", "00000", "00000", "00000", "01100", "01100", "00000"),
    "•": ("00000", "01110", "11111", "11111", "11111", "01110", "00000"),
    "→": ("00000", "00100", "00010", "11111", "00010", "00100", "00000"),
    "↓": ("00100", "00100", "00100", "00100", "00100", "01110", "00100"),
    "↑": ("00100", "01110", "00100", "00100", "00100", "00100", "00100"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    "`": ("00100", "01000", "00000", "00000", "00000", "00000", "00000"),
    "^": ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "\\": ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
    "×": ("00000", "10001", "01010", "00100", "01010", "10001", "00000"),
}

CHAR_W = 6  # advance per character, in font units (5 px glyph + 1 px gap)


def text_width(s, scale):
    return len(s) * CHAR_W * scale


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, color, t=1):
        self.rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def poly(self, pts, color):
        for a, b in zip(pts, pts[1:] + pts[:1]):
            self.line(a[0], a[1], b[0], b[1], color)

    def fill_poly(self, pts, color):
        # Even-odd scanline fill.
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.hline(int(round(xs[j])), y, max(1, int(round(xs[j + 1])) - int(round(xs[j]))), color)

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def glyph(self, x, y, ch, scale, color):
        rows = FONT.get(ch)
        if rows is None:
            rows = FONT["?"]
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "1":
                    self.rect(x + c * scale, y + r * scale, scale, scale, color)

    def text(self, x, y, s, scale, color, align="left"):
        if align == "center":
            x -= text_width(s, scale) // 2
        elif align == "right":
            x -= text_width(s, scale)
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, color)
            cx += CHAR_W * scale
        return cx

    def wrap(self, s, max_px, scale):
        """Greedy word wrap; returns list of lines fitting max_px."""
        max_chars = max(1, max_px // (CHAR_W * scale))
        words = s.split(" ")
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                # long word: hard-split it
                while len(word) > max_chars:
                    lines.append(word[:max_chars])
                    word = word[max_chars:]
                cur = word
        if cur:
            lines.append(cur)
        return lines


def png_bytes(canvas):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        i = y * canvas.w * 3
        raw += canvas.px[i:i + canvas.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))

# --- content: Wednesday 25 November 2026 ------------------------------------
# Every panel is a Wednesday-local-date event; every figure is a Wednesday
# close or final result. Sources are the wires that reported each story.

PANELS = [
    # (number, region, headline, body, source) -- panel 1 is the hero.
    (1, "ASIA", "ASIA'S CHIP ROUT",
     "The AI rally reverses in one session. Samsung -9.9%, SK Hynix about "
     "-10%, SoftBank -14.8%, Advantest -12.7%. The US tech pullback and fresh "
     "tariff threats end the rebound a day after Nvidia's surge.",
     "Reuters"),
    (2, "ASIA", "FIRST PAKISTANI IN ORBIT",
     "Shenzhou-24 lifts off from Jiuquan at 08:18 Beijing time. Crew: Tang "
     "Hongbo, Wu Yi and Muhammad Zeeshan Ali, 40 - the first Pakistani in "
     "orbit and the first foreign astronaut aboard Tiangong. A 5-10 day stay, "
     "90+ experiments.",
     "Xinhua / Reuters"),
    (3, "MIDDLE EAST", "JEDDAH IN THE CROSSHAIRS",
     "The Houthis threaten Jeddah and all Saudi Red Sea ports. The Saudi-led "
     "coalition answers with strikes on Hodeidah port, Saada and Amran after "
     "an evacuation warning. Spokesman Saree claims 72 strikes in 24 hours.",
     "Reuters"),
    (4, "OCEANIA", "AUSTRALIA'S INFLATION JUMPS TO 4.9%",
     "October CPI +4.9% y/y, a three-year high, from 4.3% in September; "
     "forecast was 4.8%. Trimmed mean 3.8%. Fuel +32.5% y/y, electricity "
     "+25.2% as rebates end. The jobless rate is 4.9% too.",
     "ABS via Reuters"),
    (5, "NORTH AMERICA", "FIVE TONS OF TROUBLE",
     "The Army detonates the nation's whole stockpile of unstable lead azide "
     "- about 9,500 lb in 68 drums - at the Iowa Army Ammunition Plant, "
     "Middletown, at ~9 a.m. CST. Two blasts, no kickout, zero airborne lead "
     "detected.",
     "US Army / AP"),
    (6, "EUROPE", "CHAMPIONS LEAGUE MD5",
     "Barcelona win 4-1 at Sabah; Liverpool 3-0 at Club Brugge; PSG 2-2 "
     "Roma - the perfect record ends; Lille 2-1 Bayern; Sporting 2-2 Man "
     "Utd; Inter 2-0 Stuttgart; Villarreal 1-0 at Slavia; Fenerbahce 1-0 at "
     "Shakhtar; Atletico 2-0 Viking.",
     "UEFA"),
    (7, "AFRICA", "DAY 3 IN CENTURION",
     "South Africa win the 2nd Test by an innings and 219 runs. Bangladesh "
     "91 & 184; South Africa 494/7 declared. Mulder takes 7-31 in the second "
     "innings. Ackerman's 150 and Mulder's 100 set it up on Day 2.",
     "ESPNCricinfo"),
    (8, "NORTH AMERICA", "AMERICA'S INFLATION TEST",
     "October PCE +3.8% y/y, core +3.3% - a three-year high - both +0.3% "
     "m/m. The last major inflation read before the Fed's Dec 9 decision. "
     "Personal income +0.7%, spending +0.3%.",
     "BEA"),
    (9, "NORTH AMERICA", "THE GREAT GETAWAY",
     "The Thanksgiving outbound crush: 49,831 flights on Wednesday, in the "
     "busiest travel week in 16 years - 417,000 flights Nov 23-Dec 1. AAA "
     "expects 81.5m Americans travelling; TSA to screen 17.6m.",
     "FAA / AAA"),
    (10, "MIDDLE EAST", "OIL CLIMBS AS HORMUZ BURNS",
     "WTI settles $84.08, +2.47%, Brent near $94.61, after the Houthis claim "
     "a hit on a Saudi refinery and a container ship is targeted near the "
     "Strait of Hormuz. Libya's Sharara pipeline restarts; OPEC+ meets Nov 29.",
     "Reuters"),
    (11, "AFRICA", "EKURHULENI VOTE DELAYED",
     "Councillors are sworn in at Germiston, then the mayor vote is deferred "
     "to Friday - the 14-day deadline - as coalition talks stall. The "
     "ANC-ActionSA deal is still unsigned; no mayor is elected.",
     "Business Day"),
    (12, "NORTH AMERICA", "TARIFF DECISION DAY",
     "USTR announces Section 301 findings for 14 economies - China, the EU, "
     "India, Japan, Korea and nine more. Proposed duties 15-25%, capped by "
     "partner: EU/Japan/Korea 15%, China 20%, India 17% with a deal. Mexico "
     "and Norway excluded.",
     "Reuters"),
    (13, "NORTH AMERICA", "WALL STREET'S WEDNESDAY",
     "Dow 50,182.95, +0.33%, erasing a 1,100-point intraday plunge - the "
     "biggest reversal since Jan 2022. S&P 7,182.78, -0.25%; Nasdaq "
     "23,585.80, -0.62%; Nvidia -3.91% to $149.30. VIX 28.29.",
     "Reuters"),
]

HERO_SUB = ("KOSPI 4,697.51 -6.16%  ·  TAIEX 38,195.43 -4.80%  ·  "
            "NIKKEI 57,011.62 -2.78%")

ALSO = [
    "Q3 GDP revised up to 4.3% — BEA",
    "Jobless claims fall to 189,000 — DOL",
    "Fed Beige Book out at 2 p.m. ET — Fed",
    "New home sales, October, 10 a.m. ET — Census",
    "Durable goods orders due 8:30 a.m. — Census",
    "Ali's orbit tests: microalgae, quinoa — Xinhua",
    "UK sanctions the Houthis, 4 leaders — Reuters",
    "Sea-Tac expects ~164,000 travellers — The Traveler",
    "TSA to screen 17.6m, Nov 24-30 — TSA",
    "Ship targeted near Hormuz; IRGC claims — Reuters",
    "Brazil 'outraged' at new US tariffs — Reuters",
    "Gauteng: Tshwane Thu, Joburg Fri — africanbulletin24",
    "PSG perfect no more; Real Madrid only 100% — UEFA",
    "Core PCE +3.3%, 0.1pp hot — InvestingLive",
    "Chalmers vows 'substantial savings' — AFR",
    "Iowa: FEMA lodging thru Fri — US Army",
    "Iowa blast postponed three times — AP",
    "Shenzhou emblem carries a jasmine — Xinhua",
]

DATE_CHECK = [
    ("CIA/ODNI unclassified network breached", "TUE 24 NOV", "NYT"),
    ("Houthi strike on Riyadh PIF Tower, 11 hurt", "TUE 24 NOV", "Reuters"),
    ("WHO Ebola team evacuated from Akwe hospital", "TUE 24 NOV", "WHO"),
    ("Huawei convicted, 10 of 12 counts", "TUE 24 NOV", "Reuters"),
    ("Dell record Q3: revenue $54.9bn, +103%", "TUE 24 NOV", "Dell"),
    ("Dow's first close above 50,000: 50,018.70", "TUE 24 NOV", "Reuters"),
    ("Germany gets first access to Ukraine's DELTA", "TUE 24 NOV", "Reuters"),
    ("Japan factory PMI 53.7", "TUE 24 NOV", "Reuters"),
    ("Cartagena hostage standoff, ~30 held", "TUE 24 NOV", "Reuters"),
    ("COP31 ends with no deal", "SUN 22 NOV", "Reuters"),
]

SOURCES = ["Reuters", "Xinhua", "AP", "ABS", "US Army", "UEFA", "ESPNCricinfo",
           "BEA", "FAA", "AAA", "Business Day", "africanbulletin24",
           "InvestingLive", "The Traveler", "TSA", "DOL", "US Census",
           "Federal Reserve", "AFR"]

# (pin label, lon, lat, dx, dy) -- dx/dy nudge the number badge in pixels.
PINS = [
    ("1", 127.0, 37.5, 8, 8),       # Seoul
    ("2", 98.5, 39.8, 6, -12),     # Jiuquan
    ("3", 39.2, 21.5, 8, 12),      # Jeddah
    ("4", 149.1, -35.3, -32, 0),   # Canberra
    ("5", -91.3, 40.8, -30, -14),  # Middletown, Iowa
    ("6", 2.35, 48.9, -8, -12),    # Paris
    ("7", 28.2, -25.9, -34, 0),    # Centurion
    ("8/12", -77.0, 38.9, -8, 10), # Washington (panels 8 and 12)
    ("9", -87.6, 41.9, -10, -16),  # Chicago
    ("10", 56.3, 26.6, 8, -12),    # Strait of Hormuz
    ("11", 28.2, -26.2, 0, 12),    # Germiston
    ("13", -74.0, 40.7, 10, -8),   # New York
    ("14", -47.9, -15.8, 14, 12),  # Brasilia (ALSO: Brazil reacts)
]

# Simplified continent outlines (lon, lat), equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-75, 73), (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 29), (-97, 26), (-105, 22), (-110, 23),
     (-115, 28), (-120, 34), (-125, 40), (-125, 49), (-135, 58),
     (-150, 60), (-165, 60)],
    # South America
    [(-80, 10), (-75, 11), (-70, 12), (-62, 10), (-55, 6), (-50, 0),
     (-45, -3), (-38, -5), (-35, -9), (-40, -15), (-42, -23), (-48, -28),
     (-53, -33), (-58, -38), (-65, -41), (-68, -50), (-70, -54),
     (-73, -50), (-73, -40), (-72, -30), (-70, -20), (-75, -15),
     (-80, -5), (-81, 0), (-80, 5)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (0, 50), (3, 52), (7, 54),
     (8, 57), (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
     (32, 70), (40, 68), (44, 68), (40, 64), (35, 60), (30, 55), (28, 50),
     (24, 45), (23, 40), (19, 42), (15, 44), (12, 44), (8, 44), (3, 43),
     (-1, 37)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 20), (-17, 15), (-15, 11),
     (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (12, 0),
     (13, -5), (12, -12), (13, -18), (16, -22), (18, -28), (20, -35),
     (26, -34), (32, -29), (35, -24), (38, -18), (40, -12), (40, -5),
     (42, 0), (46, 5), (51, 10), (48, 11), (43, 12), (40, 15), (38, 18),
     (35, 22), (33, 27), (30, 31), (25, 32), (20, 32), (15, 32), (10, 34)],
    # Asia
    [(35, 42), (40, 40), (45, 38), (50, 37), (55, 40), (60, 42), (65, 45),
     (70, 50), (75, 55), (80, 60), (85, 65), (90, 68), (95, 70), (100, 72),
     (110, 73), (120, 72), (130, 72), (140, 72), (150, 70), (160, 69),
     (170, 66), (178, 65), (178, 62), (170, 60), (162, 58), (158, 52),
     (155, 50), (150, 45), (145, 42), (140, 40), (135, 35), (130, 33),
     (127, 35), (122, 38), (120, 32), (118, 25), (112, 22), (108, 18),
     (105, 10), (103, 2), (100, 8), (98, 12), (95, 16), (92, 20), (88, 22),
     (85, 19), (80, 13), (77, 8), (75, 15), (72, 20), (68, 24), (65, 25),
     (60, 25), (57, 26), (52, 27), (50, 29), (48, 30), (44, 29), (40, 32),
     (36, 36), (33, 38), (30, 40), (28, 42)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20)],
]

# --- layout ------------------------------------------------------------------
MARGIN = 12
GUTTER = 8
STAT_LINES = [
    "KOSPI -6.16%  ·  NIKKEI -2.78%  ·  TAIEX -4.80%  ·  DOW +0.33%  ·  "
    "NASDAQ -0.62%  ·  PCE +3.8%  ·  CORE +3.3%",
    "BRENT ~$94.61  ·  WTI $84.08  ·  AUS CPI 4.9%  ·  81.5M TRAVELLERS  ·  "
    "9,500 LB LEAD AZIDE  ·  49,831 FLIGHTS",
]


def draw_masthead(cv, y):
    cv.text(W // 2, y, "THE WORLD IN ONE PAGE", 4, INK, align="center")
    y += 34
    cv.text(W // 2, y, "WEDNESDAY 25 NOVEMBER 2026", 2, RED, align="center")
    y += 20
    count = ("31 STORIES  ·  7 REGIONS  ·  %d NAMED SOURCES  ·  EVERY EVENT "
             "DATED WEDNESDAY 25 NOVEMBER 2026" % len(SOURCES))
    cv.text(W // 2, y, count, 1, GREY, align="center")
    y += 14
    cv.hline(MARGIN, y, W - 2 * MARGIN, INK, 3)
    cv.hline(MARGIN, y + 5, W - 2 * MARGIN, INK, 1)
    return y + 9


def draw_stat_strip(cv, y):
    h = 28
    cv.rect(0, y, W, h, BLACK)
    cv.text(W // 2, y + 5, STAT_LINES[0], 1, WHITE, align="center")
    cv.text(W // 2, y + 16, STAT_LINES[1], 1, YELLOW, align="center")
    return y + h


def draw_hero(cv, y):
    num, region, headline, body, source = PANELS[0]
    h = 108
    x0, x1 = MARGIN, W - MARGIN
    cv.rect(x0, y, x1 - x0, h, PANELBG)
    cv.rect(x0, y, 10, h, RED)
    # border
    cv.hline(x0, y, x1 - x0, PANELLINE)
    cv.hline(x0, y + h - 1, x1 - x0, PANELLINE)
    cv.vline(x0, y, h, PANELLINE)
    cv.vline(x1 - 1, y, h, PANELLINE)
    tx = x0 + 20
    cv.rect(tx, y + 8, 30, 18, RED)
    cv.text(tx + 15, y + 10, "1", 2, WHITE, align="center")
    cv.text(tx + 38, y + 12, region + "  ·  HERO", 1, RED)
    cv.text(tx, y + 30, headline, 3, INK)
    cv.text(tx, y + 56, HERO_SUB, 2, INK)
    lines = cv.wrap(body, x1 - tx - 12, 1)
    ly = y + 76
    for ln in lines[:2]:
        cv.text(tx, ly, ln, 1, INK)
        ly += 9
    cv.text(x1 - 12, y + h - 13, "SOURCE: " + source.upper(), 1, GREY,
            align="right")
    return y + h


def draw_panel(cv, x, y, w, h, panel):
    num, region, headline, body, source = panel
    cv.rect(x, y, w, h, PANELBG)
    cv.hline(x, y, w, PANELLINE)
    cv.hline(x, y + h - 1, w, PANELLINE)
    cv.vline(x, y, h, PANELLINE)
    cv.vline(x + w - 1, y, h, PANELLINE)
    tx = x + 8
    inner = w - 16
    cv.rect(tx, y + 7, 30, 18, RED)
    cv.text(tx + 15, y + 9, str(num), 2, WHITE, align="center")
    cv.text(tx + 38, y + 11, region, 1, RED)
    head_lines = cv.wrap(headline, inner, 2)
    hy = y + 30
    for ln in head_lines[:2]:
        cv.text(tx, hy, ln, 2, INK)
        hy += 15
    body_lines = cv.wrap(body, inner, 1)
    by = hy + 3
    max_lines = max(0, (y + h - 14 - by) // 9)
    for ln in body_lines[:max_lines]:
        cv.text(tx, by, ln, 1, INK)
        by += 9
    cv.text(x + w - 8, y + h - 12, "SOURCE: " + source.upper(), 1, GREY,
            align="right")


def draw_panels(cv, y):
    cols, rows = 3, 4
    pw = (W - 2 * MARGIN - (cols - 1) * GUTTER) // cols
    ph = 118
    rest = PANELS[1:]
    for i, panel in enumerate(rest):
        cx = MARGIN + (i % cols) * (pw + GUTTER)
        cy = y + (i // cols) * (ph + GUTTER)
        draw_panel(cv, cx, cy, pw, ph, panel)
    return y + rows * ph + (rows - 1) * GUTTER


def draw_also(cv, y):
    h = 116
    x0, x1 = MARGIN, W - MARGIN
    cv.hline(x0, y, x1 - x0, INK, 2)
    cv.text(x0, y + 5, "ALSO ON WEDNESDAY — 18 MORE STORIES", 2, INK)
    cv.text(x1, y + 5, "ALL DATED 25 NOV 2026", 1, GREY, align="right")
    cols = 3
    cw = (x1 - x0 - (cols - 1) * GUTTER) // cols
    for i, item in enumerate(ALSO):
        cx = x0 + (i % cols) * (cw + GUTTER)
        cy = y + 24 + (i // cols) * 15
        cv.text(cx, cy, "• " + item, 1, INK)
    return y + h


def draw_map(cv, x, y, w, h):
    cv.rect(x, y, w, h, OCEAN)
    cv.hline(x, y, w, PANELLINE)
    cv.hline(x, y + h - 1, w, PANELLINE)
    cv.vline(x, y, h, PANELLINE)
    cv.vline(x + w - 1, y, h, PANELLINE)
    cv.text(x + 8, y + 6, "WHERE IT HAPPENED — 14 PINS", 1, INK)
    mx, my, mw, mh = x + 6, y + 20, w - 12, h - 44

    def proj(lon, lat):
        return (mx + int((lon + 180.0) / 360.0 * mw),
                my + int((90.0 - lat) / 180.0 * mh))

    for cont in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in cont]
        cv.fill_poly(pts, LAND)
        cv.poly(pts, LANDBORDER)
    labels = [("N. AMERICA", -150, 55), ("S. AMERICA", -68, -28),
              ("EUROPE", 32, 50), ("AFRICA", 20, 8), ("ASIA", 120, 62),
              ("OCEANIA", 128, -48)]
    for name, lon, lat in labels:
        px, py = proj(lon, lat)
        cv.text(px, py, name, 1, (90, 80, 60), align="center")
    for label, lon, lat, dx, dy in PINS:
        px, py = proj(lon, lat)
        cv.disc(px, py, 4, RED)
        cv.disc(px, py, 2, WHITE)
        bw = 10 + 6 * len(label)
        bx, by = px + dx + 6, py + dy - 5
        cv.rect(bx, by, bw, 11, RED)
        cv.text(bx + 2, by + 2, label, 1, WHITE)
    cv.text(x + 8, y + h - 18,
            "2 LAUNCHED INTO SPACE  ·  14 BRASILIA: BRAZIL REACTS TO TARIFFS",
            1, INK)


def draw_date_check(cv, x, y, w, h):
    cv.rect(x, y, w, h, PANELBG)
    cv.hline(x, y, w, PANELLINE)
    cv.hline(x, y + h - 1, w, PANELLINE)
    cv.vline(x, y, h, PANELLINE)
    cv.vline(x + w - 1, y, h, PANELLINE)
    cv.rect(x, y, w, 20, DARKRED)
    cv.text(x + 8, y + 5, "DATE CHECK — THE BIG STORIES THAT WERE NOT WEDNESDAY",
            1, WHITE)
    cv.text(x + 8, y + 26,
            "These happened earlier. They are not today's news.", 1, GREY)
    cy = y + 40
    for title, date, src in DATE_CHECK:
        line = "×  %s  —  %s (%s)" % (title, date, src)
        cv.text(x + 8, cy, line, 1, INK)
        cy += 10
    return y + h


def draw_footer(cv, y):
    half = (len(SOURCES) + 1) // 2
    cv.text(W // 2, y,
            "SOURCES: " + " · ".join(s.upper() for s in SOURCES[:half]),
            1, GREY, align="center")
    cv.text(W // 2, y + 10,
            " · ".join(s.upper() for s in SOURCES[half:]),
            1, GREY, align="center")
    cv.text(W // 2, y + 20,
            "ALL EVENTS DATED WEDNESDAY 25 NOVEMBER 2026 (LOCAL DATE)  ·  "
            "THE WORLD IN ONE PAGE", 1, INK, align="center")
    return y + 30


def build():
    cv = Canvas(W, H, PAPER)
    cv.rect(0, 0, W, 6, RED)
    y = 10
    y = draw_masthead(cv, y)
    y = draw_stat_strip(cv, y) + 3
    y = draw_hero(cv, y) + 3
    y = draw_panels(cv, y) + 3
    y = draw_also(cv, y) + 3
    bottom_h = 140
    map_w = 400
    draw_map(cv, MARGIN, y, map_w, bottom_h)
    dc_x = MARGIN + map_w + GUTTER
    draw_date_check(cv, dc_x, y, W - MARGIN - dc_x, bottom_h)
    y += bottom_h + 4
    y = draw_footer(cv, y)
    assert y <= H, "layout overflow: %d > %d" % (y, H)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
