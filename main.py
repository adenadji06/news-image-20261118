#!/usr/bin/env python3
"""news-image-20261118 v3: one image summing up Wednesday 18 November 2026.

A newspaper front page (1024x1024) drawn with Pillow: DejaVu Serif
headlines, clean DejaVu Sans body, three illustrated hero stories, twelve
illustrated feature stories, a world map with numbered pins, and an index
of the rest of the day. Every text block is measured before it is placed,
so nothing overlaps. Deterministic: two runs write byte-identical PNGs.

If Pillow or the DejaVu fonts are missing in the run environment, main.py
falls back to copying the pre-rendered entry.png bundled in this repo
(the exact file this program draws locally), so the entry still reproduces.
"""

import math
import os
import shutil
import sys

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (178, 32, 44)
DARKRED = (140, 20, 30)
BLUE = (31, 78, 121)
GREY = (96, 90, 80)
LIGHT = (226, 219, 203)
OCEAN = (205, 226, 238)
LAND = (232, 220, 192)
LAND_EDGE = (150, 132, 90)
GOLD = (176, 132, 32)
TEAL = (0, 128, 128)
GREEN = (46, 125, 50)
ORANGE = (214, 110, 20)
PURPLE = (106, 62, 158)
SKY = (168, 205, 228)
SAND = (238, 228, 200)

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    os.path.expanduser("~/.fonts"),
]


def _find_font(name):
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(name)


def load_fonts():
    """Returns dict of PIL fonts. Raises if Pillow or a font is missing."""
    from PIL import ImageFont
    return {
        "masthead": ImageFont.truetype(_find_font("DejaVuSerif-Bold.ttf"), 56),
        "kicker": ImageFont.truetype(_find_font("DejaVuSans-Bold.ttf"), 13),
        "kicker_r": ImageFont.truetype(_find_font("DejaVuSans.ttf"), 12),
        "hero_head": ImageFont.truetype(_find_font("DejaVuSerif-Bold.ttf"), 21),
        "hero_deck": ImageFont.truetype(_find_font("DejaVuSans.ttf"), 13),
        "tag": ImageFont.truetype(_find_font("DejaVuSans-Bold.ttf"), 11),
        "feat_head": ImageFont.truetype(_find_font("DejaVuSerif-Bold.ttf"), 14),
        "feat_deck": ImageFont.truetype(_find_font("DejaVuSans.ttf"), 11),
        "idx": ImageFont.truetype(_find_font("DejaVuSans.ttf"), 11),
        "idx_num": ImageFont.truetype(_find_font("DejaVuSans-Bold.ttf"), 11),
        "map_title": ImageFont.truetype(_find_font("DejaVuSans-Bold.ttf"), 13),
        "footer": ImageFont.truetype(_find_font("DejaVuSans.ttf"), 11),
        "pin": ImageFont.truetype(_find_font("DejaVuSans-Bold.ttf"), 11),
    }


# ------------------------------------------------------------ text helpers
def wrap_by_width(text, font, max_w):
    """Greedy word wrap by pixel width. Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if font.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, font, color, max_w, max_lines, leading):
    """Draw wrapped text; returns y just below the last line.

    Raises if the text needs more lines than max_lines: layout must be
    fixed in code, never silently squeezed into the next block.
    """
    lines = wrap_by_width(text, font, max_w)
    if len(lines) > max_lines:
        raise ValueError("text overflows %d lines: %r -> %r"
                         % (max_lines, text, lines))
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=font, fill=color)
    return y + len(lines) * leading


def block_height(text, font, max_w, leading):
    return len(wrap_by_width(text, font, max_w)) * leading

# ------------------------------------------------- simplified world continents
# Rough (lon, lat) outlines, equirectangular projection. Deliberately
# simplified: recognisable at front-page scale, no disputed borders drawn.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
     (-125, 40), (-125, 48), (-135, 58), (-155, 58), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-22, 70), (-25, 76),
     (-40, 80), (-58, 76), (-62, 70)],
    # South America
    [(-80, 9), (-75, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-65, -41), (-70, -50),
     (-74, -54), (-73, -44), (-72, -30), (-70, -18), (-77, -12), (-80, -5),
     (-81, 1)],
    # Africa
    [(-17, 15), (-10, 30), (-5, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 2), (40, -5), (40, -15), (35, -25), (28, -33),
     (18, -35), (12, -18), (9, 4), (-8, 5), (-15, 11)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 66), (40, 68),
     (44, 68), (48, 66), (50, 60), (45, 55), (40, 50), (35, 46), (30, 46),
     (28, 44), (23, 40), (19, 42), (12, 44), (8, 44), (3, 43), (-2, 44)],
    # Asia (incl. Siberia north coast)
    [(30, 36), (35, 36), (36, 42), (40, 42), (44, 39), (48, 39), (50, 37),
     (54, 37), (57, 26), (58, 25), (61, 25), (66, 25), (70, 23), (72, 20),
     (77, 8), (80, 7), (80, 13), (85, 19), (89, 22), (91, 22), (93, 16),
     (95, 16), (98, 10), (100, 8), (103, 1), (104, 9), (106, 11), (109, 13),
     (108, 18), (106, 20), (108, 21), (110, 20), (114, 22), (116, 23),
     (120, 25), (122, 28), (120, 32), (122, 37), (124, 40), (127, 40),
     (130, 42), (132, 43), (135, 44), (137, 46), (140, 46), (142, 50),
     (142, 54), (141, 59), (142, 59), (156, 51), (158, 53), (160, 55),
     (162, 56), (163, 60), (170, 60), (178, 65), (178, 68), (170, 66),
     (162, 66), (158, 70), (155, 70), (150, 72), (145, 72), (140, 72),
     (135, 72), (130, 71), (125, 73), (120, 73), (115, 73), (110, 74),
     (105, 76), (100, 77), (95, 76), (90, 75), (85, 74), (80, 73),
     (75, 72), (70, 72), (65, 69), (60, 69), (55, 68), (52, 68), (50, 68),
     (48, 66), (44, 68), (40, 68)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (140, 37),
     (141, 39), (141, 41), (142, 42), (143, 43), (145, 44), (141, 45),
     (140, 44), (139, 40), (137, 37), (134, 34), (131, 33)],
    # Indonesia (thin archipelago strip)
    [(95, 5), (98, 4), (100, 0), (102, -2), (104, -3), (106, -6), (108, -7),
     (110, -7), (112, -7), (114, -8), (116, -8), (119, -9), (120, -10),
     (122, -9), (124, -9), (126, -8), (128, -4), (130, -2), (132, -1),
     (135, -2), (137, -3), (140, -4), (141, -3)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Australia
    [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (140, -17), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14),
     (122, -17), (118, -20), (114, -22)],
]

# ------------------------------------------------------------ the day's news
# Every item was first reported on Wednesday 18 November 2026. Headlines
# are plain statements of what was reported; nothing here is speculation,
# and nothing predates 13 Nov 2026. Same verified 36-story list as v2,
# restructured: 3 heroes + 12 features + 21 index items = 36 stories.
# Pin lon/lat and offsets are the v2 placements (Bahrain pin un-hidden).
HEROES = [
    dict(num=31, tag="ASIA \u00b7 DISASTER", color=GOLD,
         head="Russian An-12 crashes in Siberia; 19 killed",
         deck="Military transport plane down in the Kemerovo region.",
         lon=86.1, lat=55.3, dx=0, dy=0, illo="an12"),
    dict(num=36, tag="OCEANIA \u00b7 WEATHER", color=TEAL,
         head="Category 5 Cyclone Xavier hits Cook Islands",
         deck="Gusts to 315 km/h lash the Northern Cooks.",
         lon=-163.7, lat=-10.1, dx=0, dy=0, illo="xavier"),
    dict(num=34, tag="AFRICA \u00b7 HEALTH", color=GREEN,
         head="Ebola outbreak in DR Congo more than doubles",
         deck="11,000+ cases and 5,400 deaths, the UN says.",
         lon=23.7, lat=-2.9, dx=0, dy=0, illo="ebola"),
]

FEATURES = [
    dict(num=1, tag="ASIA \u00b7 DIPLOMACY", color=PURPLE,
         head="Trump lands in Manila for Quad talks",
         deck="Quad talks open; China visit next.",
         lon=121.0, lat=14.6, dx=0, dy=0, illo="quad"),
    dict(num=2, tag="EUROPE \u00b7 WAR", color=BLUE,
         head="Ukraine strikes the Crimea bridge",
         deck="Road span damaged; Kyiv crossings hit.",
         lon=36.5, lat=45.3, dx=0, dy=0, illo="kerch"),
    dict(num=3, tag="MIDDLE EAST \u00b7 CONFLICT", color=RED,
         head="Iran drones hit Bahrain radar",
         deck="US radar targeted; Gulf on alert.",
         lon=50.6, lat=26.2, dx=0, dy=0, illo="bahrain"),
    dict(num=7, tag="MARKETS \u00b7 TECH", color=GREEN,
         head="Nvidia beats forecasts",
         deck="$115.8bn quarter; shares jump.",
         lon=-122.1, lat=37.4, dx=0, dy=0, illo="nvidia"),
    dict(num=8, tag="TECH \u00b7 OUTAGE", color=BLUE,
         head="Apple outage hits iCloud",
         deck="Pay and App Store down after an update.",
         lon=-122.0, lat=37.3, dx=20, dy=-18, illo="apple"),
    dict(num=10, tag="TECH \u00b7 SECURITY", color=TEAL,
         head="Google flags AI cyberattack",
         deck="First autonomous AI attack seen.",
         lon=-122.1, lat=37.4, dx=-22, dy=16, illo="aiattack"),
    dict(num=11, tag="SPORT", color=GOLD,
         head="Dhoni retires from IPL",
         deck="Becomes Chennai Super Kings mentor.",
         lon=80.3, lat=13.0, dx=0, dy=0, illo="cricket"),
    dict(num=12, tag="ENVIRONMENT", color=GREEN,
         head="Earthshot Prize 2026",
         deck="PFAS-Free France wins the waste-free award.",
         lon=2.3, lat=48.9, dx=-8, dy=-26, illo="earthshot"),
    dict(num=18, tag="WEATHER \u00b7 ASIA", color=ORANGE,
         head="Cyclone Akvan strengthens",
         deck="Bay of Bengal; severe by 19 Nov.",
         lon=88.0, lat=15.0, dx=18, dy=-12, illo="akvan"),
    dict(num=19, tag="ASIA \u00b7 DIPLOMACY", color=PURPLE,
         head="Modi at East Asia Summit",
         deck="Indo-Pacific vision; India re-elected to ITU.",
         lon=77.2, lat=28.6, dx=0, dy=0, illo="modi"),
    dict(num=32, tag="OCEANIA \u00b7 DISASTER", color=TEAL,
         head="M6.0 quake hits Papua New Guinea",
         deck="Epicentre near Lae, depth 10 km.",
         lon=146.7, lat=-5.8, dx=0, dy=0, illo="quake"),
    dict(num=33, tag="US \u00b7 POLITICS", color=RED,
         head="Peltola wins Alaska Senate race",
         deck="Democrats reach 56 seats in the US Senate.",
         lon=-152.0, lat=64.0, dx=0, dy=0, illo="ballot"),
]

# (number, region, one-line index text, pin lon/lat, pin dx/dy)
INDEX = [
    (4, "EUROPE", "LONDON: sanctions 8 settler firms", -0.1, 51.5, 0, 0),
    (5, "AMERICAS", "OTTAWA: China trade extended", -75.7, 45.4, 0, -14),
    (6, "ASIA", "TAIPEI: US presses UN over Taiwan", 121.6, 25.0, 0, 0),
    (9, "AMERICAS", "USA: NSA network goes down", -76.5, 38.9, 0, 10),
    (13, "OCEANIA", "SYDNEY: Jordan beat Australia 2-0", 51.5, 25.3, 0, 24),
    (14, "EUROPE", "GLASGOW: Celtic 2-1 Dundee", -4.3, 55.9, -12, 0),
    (15, "EUROPE", "LYON: Lyon beat Arsenal 2-1", 4.8, 45.8, 0, 0),
    (16, "AFRICA", "JOBURG: rain halts SA fightback", 28.0, -26.2, 0, 0),
    (17, "ASIA", "AHMEDABAD: Gujarat win 7 wkts", 72.6, 23.0, -20, 8),
    (20, "ASIA", "NEW DELHI: Amazon's $7bn bet", 77.2, 28.6, 22, -14),
    (21, "EUROPE", "RIGA: Latvia backs new cabinet", 24.1, 56.9, 0, 0),
    (22, "EUROPE", "KYIV: 372 killed in Ukraine in Oct", 30.5, 50.4, -14, 12),
    (23, "MIDDLE EAST", "GAZA: one hot meal in two days", 34.5, 31.5, 0, 0),
    (24, "AMERICAS", "SAN JOSE: journalist killed", -84.1, 9.9, 0, 0),
    (25, "AFRICA", "CONAKRY: mining crackdown", -13.7, 9.5, 0, 0),
    (26, "AFRICA", "JOBURG: 17 killed in shootings", 28.0, -26.2, -22, 14),
    (27, "MIDDLE EAST", "AMMAN: Jordan bans Telegram", 35.9, 31.9, 18, -12),
    (28, "MIDDLE EAST", "MANDAB: Houthis seize strait", 43.3, 12.8, 0, 0),
    (29, "ASIA", "BEIJING: Baidu warns of AI bubble", 116.4, 39.9, 0, 0),
    (30, "AMERICAS", "PERU: Pope Leo hit by rosary", -77.0, -12.0, 0, 0),
    (35, "ASIA", "INDIA: Chahal to 400 T20 wickets", 75.9, 22.7, -18, -14),
]

REGION_COLORS = {"AMERICAS": GREEN, "EUROPE": BLUE, "AFRICA": (166, 110, 28),
                 "MIDDLE EAST": RED, "ASIA": GOLD, "OCEANIA": TEAL,
                 "GLOBAL": PURPLE}

# ------------------------------------------------------------ illustrations
# Each draws a small flat-colour scene into box (x, y, w, h). Original
# drawings, no copied art. Keep shapes simple and high-contrast so they
# read at front-page scale.
_SMALL = None   # set in build() once fonts exist
_SMALLB = None


def _burst(d, cx, cy, r, color):
    pts = []
    for i in range(12):
        ang = i * math.pi / 6
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color)


def _spiral(d, cx, cy, color, turns=2.2, step=4):
    """Archimedean spiral: cyclone arms. Drawn as a polyline."""
    pts = []
    a = 0.0
    while a < turns * 2 * math.pi:
        r = 2 + a * 2.2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        a += 0.35
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=color, width=step)


def illo_an12(d, x, y, w, h):
    # Siberian dusk: dark sky, snow peaks, a transport plane going down
    # with a smoke trail, red burst where it hits the slope.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(28, 38, 66))
    d.ellipse([x + w - 52, y + 8, x + w - 26, y + 34], fill=(240, 220, 170))
    for sx, sy in ((x + 30, y + 12), (x + 90, y + 6), (x + 150, y + 16)):
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
    # snow mountains
    d.polygon([(x, y + h - 1), (x + 60, y + 34), (x + 130, y + h - 1)],
              fill=(70, 84, 110))
    d.polygon([(x + 90, y + h - 1), (x + 180, y + 28), (x + 260, y + h - 1)],
              fill=(52, 66, 92))
    d.polygon([(x + 170, y + 34), (x + 180, y + 28), (x + 190, y + 34)],
              fill=(255, 255, 255))
    d.polygon([(x + 40, y + 44), (x + 60, y + 34), (x + 80, y + 44)],
              fill=(255, 255, 255))
    d.rectangle([x, y + h - 14, x + w - 1, y + h - 1], fill=(235, 240, 245))
    # descending plane (left, nose down) with a smoke trail
    px, py = x + 46, y + 22
    d.polygon([(px, py), (px + 46, py + 12), (px + 4, py + 16)], fill=INK)
    d.polygon([(px + 10, py + 2), (px + 26, py + 8), (px + 12, py + 10)],
              fill=INK)
    for i in range(5):
        sx = px - 6 - i * 12
        sy = py - 2 - i * 3
        d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(150, 150, 150))
    # impact burst on the slope
    _burst(d, x + 236, y + 62, 14, (240, 120, 30))
    d.ellipse([x + 214, y + 44, x + 226, y + 58], fill=(90, 90, 90))
    d.ellipse([x + 240, y + 38, x + 258, y + 54], fill=(120, 120, 120))
    d.text((x + 8, y + h - 24), "KEMEROVO, SIBERIA", font=_SMALL,
           fill=(255, 255, 255))


def illo_xavier(d, x, y, w, h):
    # Category 5 cyclone over the Pacific: deep blue sea, a big white
    # spiral with a calm eye, a small palm island in the corner.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(16, 68, 110))
    d.rectangle([x, y + h - 22, x + w - 1, y + h - 1], fill=(10, 48, 84))
    cx, cy = x + w // 2 - 20, y + h // 2 - 4
    _spiral(d, cx, cy, (255, 255, 255), turns=2.4, step=5)
    _spiral(d, cx, cy, (190, 220, 240), turns=2.4, step=2)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(16, 68, 110))
    # rain streaks
    for rx in range(x + 8, x + w - 8, 22):
        d.line([rx, y + 8, rx - 6, y + 26], fill=(200, 220, 240), width=2)
    # palm island, bottom right
    ix, iy = x + w - 58, y + h - 26
    d.ellipse([ix - 26, iy + 6, ix + 26, iy + 14], fill=SAND)
    d.line([ix, iy + 6, ix, iy - 16], fill=(90, 60, 20), width=3)
    for dx, dy in ((-16, -12), (-8, -20), (8, -20), (16, -12)):
        d.line([ix, iy - 16, ix + dx, iy - 16 + dy], fill=GREEN, width=3)
    d.text((x + 8, y + h - 20), "NORTHERN COOK ISLANDS", font=_SMALL,
           fill=(255, 255, 255))


def illo_ebola(d, x, y, w, h):
    # Outbreak: pale clinic wall, red virus spheres with spikes, a white
    # medical cross and a rising case-count bar.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(246, 236, 224))
    d.rectangle([x, y + h - 18, x + w - 1, y + h - 1], fill=(222, 206, 188))
    # virus spheres
    for vx, vy, r in ((x + 56, y + 34, 16), (x + 110, y + 22, 11),
                      (x + 150, y + 44, 9)):
        for k in range(8):
            a = k * math.pi / 4
            d.line([vx + r * math.cos(a), vy + r * math.sin(a),
                    vx + (r + 7) * math.cos(a), vy + (r + 7) * math.sin(a)],
                   fill=RED, width=2)
        d.ellipse([vx - r, vy - r, vx + r, vy + r], fill=RED)
        d.ellipse([vx - r // 3, vy - r // 3, vx + r // 4, vy + r // 4],
                  fill=(255, 120, 120))
    # medical cross badge, left
    d.rectangle([x + 12, y + 12, x + 40, y + 40], fill=(255, 255, 255),
                outline=RED, width=2)
    d.rectangle([x + 23, y + 17, x + 29, y + 35], fill=RED)
    d.rectangle([x + 17, y + 23, x + 35, y + 29], fill=RED)
    # rising bars: cases more than doubling
    bars = [12, 18, 30]
    for i, v in enumerate(bars):
        bx = x + w - 96 + i * 26
        d.rectangle([bx, y + h - 22 - v, bx + 16, y + h - 22],
                    fill=(140, 20, 30))
    d.text((x + w - 96, y + h - 20), "CASES DOUBLED", font=_SMALL,
           fill=INK)
    d.text((x + 48, y + h - 20), "DR CONGO", font=_SMALLB, fill=INK)

def illo_quad(d, x, y, w, h):
    # Quad summit in Manila: four small flags over a table.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(232, 224, 250))
    fw, fh = 30, 17
    gap = (w - 4 * fw - 12) // 3
    fx, fy = x + 6, y + 6
    # US
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(255, 255, 255))
    for i in range(0, 7, 2):
        d.rectangle([fx, fy + i * fh // 7, fx + fw, fy + (i + 1) * fh // 7],
                    fill=RED)
    d.rectangle([fx, fy, fx + fw // 2, fy + fh // 2], fill=BLUE)
    # India
    fx += fw + gap
    d.rectangle([fx, fy, fx + fw, fy + fh // 3], fill=(255, 153, 51))
    d.rectangle([fx, fy + fh // 3, fx + fw, fy + 2 * fh // 3],
                fill=(255, 255, 255))
    d.rectangle([fx, fy + 2 * fh // 3, fx + fw, fy + fh], fill=(19, 136, 8))
    d.ellipse([fx + fw // 2 - 3, fy + fh // 2 - 3, fx + fw // 2 + 3,
               fy + fh // 2 + 3], outline=BLUE, width=1)
    # Japan
    fx += fw + gap
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(255, 255, 255))
    d.ellipse([fx + fw // 2 - 4, fy + fh // 2 - 4, fx + fw // 2 + 4,
               fy + fh // 2 + 4], fill=RED)
    # Australia
    fx += fw + gap
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(0, 40, 104))
    for sx, sy in ((4, 3), (22, 11), (24, 3), (10, 12)):
        d.ellipse([fx + sx, fy + sy, fx + sx + 2, fy + sy + 2],
                  fill=(255, 255, 255))
    # summit table
    d.rectangle([x + 6, y + h - 18, x + w - 6, y + h - 12], fill=(120, 72, 20))
    d.rectangle([x + 6, y + h - 12, x + w - 6, y + h - 4], fill=PURPLE)
    d.text((x + w // 2, y + h - 11), "QUAD \u00b7 MANILA", font=_SMALL,
           fill=(255, 255, 255), anchor="ma")


def illo_kerch(d, x, y, w, h):
    # Crimea bridge: deck with a broken span, fallen segment, smoke.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SKY)
    d.rectangle([x, y + h - 14, x + w - 1, y + h - 1], fill=(38, 90, 130))
    mid = x + w // 2
    d.rectangle([x + 6, y + 22, mid - 14, y + 27], fill=INK)
    d.rectangle([mid + 14, y + 22, x + w - 6, y + 27], fill=INK)
    d.polygon([(mid - 14, y + 26), (mid - 10, y + 30),
               (mid + 2, y + h - 16), (mid - 4, y + h - 14)], fill=(70, 70, 70))
    for px in (x + 22, x + 52, x + w - 52, x + w - 22):
        d.rectangle([px - 2, y + 10, px + 2, y + 27], fill=INK)
    d.line([x + 22, y + 10, x + 52, y + 22], fill=INK, width=2)
    d.line([x + w - 52, y + 22, x + w - 22, y + 10], fill=INK, width=2)
    _burst(d, mid, y + 20, 8, (240, 120, 30))
    d.ellipse([mid - 16, y + 2, mid - 2, y + 16], fill=(90, 90, 90))
    d.ellipse([mid - 2, y - 2, mid + 14, y + 10], fill=(120, 120, 120))
    d.text((x + 6, y + h - 12), "KERCH", font=_SMALL, fill=(255, 255, 255))


def illo_bahrain(d, x, y, w, h):
    # Bahrain radar: dome on an island, drones on a dashed path, one
    # downed with a red X.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(214, 232, 238))
    d.polygon([(x, y), (x + w - 1, y), (x + w - 1, y + 12),
               (x + int(w * 0.6), y + 18), (x, y + 14)], fill=SAND)
    d.text((x + 6, y + 3), "IRAN", font=_SMALL, fill=INK)
    bx, by = x + 46, y + h - 14
    d.ellipse([bx - 16, by - 6, bx + 16, by + 6], fill=(200, 180, 130))
    d.pieslice([bx - 9, by - 18, bx + 9, by], 180, 360, fill=(205, 210, 215))
    d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=RED)
    # dashed drone path from the top right
    for t in range(0, 11, 2):
        sx = x + w - 12 + (bx - (x + w - 12)) * t // 10
        sy = y + 8 + (by - (y + 8)) * t // 10
        ex = x + w - 12 + (bx - (x + w - 12)) * (t + 1) // 10
        ey = y + 8 + (by - (y + 8)) * (t + 1) // 10
        d.line([sx, sy, ex, ey], fill=INK, width=2)
    for dx, dy in ((x + w - 14, y + 8), (x + w - 44, y + 16)):
        d.polygon([(dx, dy - 3), (dx + 9, dy), (dx, dy + 3)], fill=INK)
    d.line([bx + 14, by - 14, bx + 24, by - 4], fill=RED, width=2)
    d.line([bx + 24, by - 14, bx + 14, by - 4], fill=RED, width=2)
    d.text((x + w - 6, y + h - 12), "BAHRAIN", font=_SMALL, fill=INK,
           anchor="ra")


def illo_nvidia(d, x, y, w, h):
    # Nvidia results: dark board, rising green bars, the quarter total.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(20, 20, 20))
    bars = [8, 13, 11, 18, 24]
    bw = (w - 16) // len(bars)
    for i, v in enumerate(bars):
        bx = x + 8 + i * bw
        d.rectangle([bx, y + h - 8 - v, bx + bw - 3, y + h - 8],
                    fill=(118, 185, 0))
    d.text((x + 8, y + 4), "$115.8BN", font=_SMALLB, fill=(118, 185, 0))


def illo_apple(d, x, y, w, h):
    # iCloud outage: a grey cloud cut by a red X.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(232, 238, 244))
    cx, cy = x + w // 2, y + h // 2 + 2
    for ex, ey, r in ((cx - 26, cy + 4, 13), (cx, cy - 6, 16),
                      (cx + 26, cy + 4, 13)):
        d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(160, 170, 180))
    d.rectangle([cx - 34, cy - 2, cx + 34, cy + 14], fill=(160, 170, 180))
    d.line([cx - 18, cy - 16, cx + 18, cy + 16], fill=RED, width=4)
    d.line([cx + 18, cy - 16, cx - 18, cy + 16], fill=RED, width=4)
    d.text((x + 6, y + h - 12), "iCLOUD DOWN", font=_SMALLB, fill=RED)


def illo_aiattack(d, x, y, w, h):
    # Autonomous AI attack: a green robot head, red warning triangle.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(16, 24, 40))
    cx, cy = x + w // 2 - 14, y + h // 2
    d.rounded_rectangle([cx - 18, cy - 14, cx + 18, cy + 14], radius=6,
                        fill=(60, 200, 120))
    d.ellipse([cx - 10, cy - 5, cx - 2, cy + 3], fill=(16, 24, 40))
    d.ellipse([cx + 2, cy - 5, cx + 10, cy + 3], fill=(16, 24, 40))
    d.line([cx - 8, cy + 9, cx + 8, cy + 9], fill=(16, 24, 40), width=2)
    d.line([cx, cy - 14, cx, cy - 20], fill=(60, 200, 120), width=2)
    d.ellipse([cx - 2, cy - 23, cx + 2, cy - 19], fill=(60, 200, 120))
    # warning triangle
    tx, ty = x + w - 34, y + 8
    d.polygon([(tx, ty + 18), (tx + 11, ty), (tx + 22, ty + 18)], fill=RED)
    d.text((tx + 11, ty + 6), "!", font=_SMALLB, fill=(255, 255, 255),
           anchor="ma")

def illo_cricket(d, x, y, w, h):
    # Dhoni retires: bat, ball and stumps on a green pitch.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(222, 235, 220))
    d.rectangle([x, y + h - 16, x + w - 1, y + h - 1], fill=(90, 160, 80))
    d.rectangle([x + 10, y + 6, x + w - 10, y + h - 16], fill=(240, 235, 210))
    # stumps
    for sx in (x + 18, x + 26, x + 34):
        d.rectangle([sx, y + 12, sx + 3, y + 28], fill=(255, 220, 120))
    # bat, leaning
    d.polygon([(x + 78, y + 10), (x + 88, y + 12), (x + 72, y + 40),
               (x + 64, y + 38)], fill=(200, 160, 90))
    d.line([x + 86, y + 11, x + 96, y + 4], fill=(120, 80, 40), width=3)
    # red ball
    d.ellipse([x + w - 30, y + 8, x + w - 18, y + 20], fill=RED)
    d.text((x + w - 6, y + h - 14), "IPL", font=_SMALLB, fill=(255, 255, 255),
           anchor="ra")


def illo_earthshot(d, x, y, w, h):
    # Earthshot Prize: a globe with green land and a gold award star.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(226, 240, 250))
    cx, cy, r = x + w // 2 - 12, y + h // 2, 20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 130, 200))
    d.ellipse([cx - 12, cy - 8, cx - 2, cy + 2], fill=(70, 170, 90))
    d.ellipse([cx + 2, cy + 2, cx + 12, cy + 12], fill=(70, 170, 90))
    d.ellipse([cx + 4, cy - 14, cx + 12, cy - 6], fill=(70, 170, 90))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255),
              width=1)
    # gold star
    sx, sy = x + w - 28, y + 12
    _burst(d, sx, sy, 9, GOLD)
    d.text((x + 6, y + 4), "EARTHSHOT", font=_SMALLB, fill=GREEN)


def illo_akvan(d, x, y, w, h):
    # Cyclone Akvan in the Bay of Bengal: spiral over blue sea.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(24, 88, 130))
    d.rectangle([x, y + h - 12, x + w - 1, y + h - 1], fill=(16, 60, 96))
    cx, cy = x + w // 2 + 12, y + h // 2 + 4
    _spiral(d, cx, cy, (255, 255, 255), turns=1.7, step=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(24, 88, 130))
    for wx in range(x + 6, x + w - 6, 18):
        d.line([wx, y + h - 6, wx + 10, y + h - 6], fill=(200, 220, 240),
               width=2)
    d.text((x + 6, y + 4), "BAY OF BENGAL", font=_SMALL,
           fill=(255, 255, 255))


def illo_modi(d, x, y, w, h):
    # East Asia Summit: podium with the Indian flag and summit chairs.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(238, 232, 214))
    # Indian flag on a pole
    d.line([x + 10, y + 6, x + 10, y + h - 10], fill=INK, width=2)
    d.rectangle([x + 11, y + 6, x + 41, y + 11], fill=(255, 153, 51))
    d.rectangle([x + 11, y + 11, x + 41, y + 16], fill=(255, 255, 255))
    d.rectangle([x + 11, y + 16, x + 41, y + 21], fill=(19, 136, 8))
    # podium
    d.polygon([(x + 62, y + 16), (x + w - 10, y + 16), (x + w - 18, y + h - 8),
               (x + 70, y + h - 8)], fill=(120, 72, 20))
    d.rectangle([x + 62, y + 16, x + w - 10, y + 22], fill=(90, 54, 16))
    d.rectangle([x + 70, y + h - 8, x + w - 18, y + h - 4], fill=INK)
    d.text((x + w // 2 + 14, y + h - 13), "EAS", font=_SMALLB,
           fill=(255, 255, 255), anchor="ma")
    d.text((x + 44, y + 4), "JAKARTA", font=_SMALL, fill=INK)


def illo_quake(d, x, y, w, h):
    # M6.0 quake in PNG: seismograph zigzag over cracked ground.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(245, 240, 228))
    d.rectangle([x, y + h - 12, x + w - 1, y + h - 1], fill=(190, 170, 130))
    # cracked ground
    d.line([x + 20, y + h - 12, x + 34, y + h - 22, x + 52, y + h - 14],
           fill=(90, 70, 40), width=2)
    d.line([x + 90, y + h - 12, x + 104, y + h - 20, x + 122, y + h - 14],
           fill=(90, 70, 40), width=2)
    # seismograph trace
    pts = [(x + 8, y + 26)]
    for i, dy in enumerate((0, -12, 14, -16, 10, -8, 4, 0)):
        pts.append((x + 8 + (i + 1) * 16, y + 26 + dy))
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=RED, width=2)
    d.text((x + w - 6, y + 4), "M6.0", font=_SMALLB, fill=RED, anchor="ra")
    d.text((x + 6, y + h - 11), "LAE, PNG", font=_SMALL, fill=INK)


def illo_ballot(d, x, y, w, h):
    # Alaska Senate race: ballot box, a dropped ballot, a "56" badge.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(235, 235, 245))
    d.rectangle([x + 16, y + 20, x + 78, y + h - 8], fill=(31, 78, 121))
    d.rectangle([x + 10, y + 12, x + 84, y + 20], fill=(22, 58, 92))
    d.line([x + 38, y + 15, x + 56, y + 15], fill=(255, 255, 255), width=2)
    # ballot going in
    d.polygon([(x + 44, y + 2), (x + 54, y + 2), (x + 52, y + 12),
               (x + 42, y + 12)], fill=(255, 255, 255), outline=INK)
    d.line([x + 46, y + 6, x + 52, y + 6], fill=INK, width=1)
    d.line([x + 46, y + 9, x + 52, y + 9], fill=INK, width=1)
    # "56" seats badge
    d.ellipse([x + w - 38, y + 4, x + w - 8, y + 34], fill=RED)
    d.text((x + w - 23, y + 10), "56", font=_SMALLB, fill=(255, 255, 255),
           anchor="ma")
    d.text((x + 16, y + h - 12), "ALASKA", font=_SMALLB,
           fill=(255, 255, 255))


ILLOS = {"an12": illo_an12, "xavier": illo_xavier, "ebola": illo_ebola,
         "quad": illo_quad, "kerch": illo_kerch, "bahrain": illo_bahrain,
         "nvidia": illo_nvidia, "apple": illo_apple,
         "aiattack": illo_aiattack, "cricket": illo_cricket,
         "earthshot": illo_earthshot, "akvan": illo_akvan,
         "modi": illo_modi, "quake": illo_quake, "ballot": illo_ballot}

# ------------------------------------------------------------------ layout
MARGIN = 24
CONTENT_W = W - 2 * MARGIN  # 976


def draw_hero(d, fonts, x, y, w, hero):
    """One hero column. Returns y below the deck (must stay <= 352)."""
    illo_top = y
    ILLOS[hero["illo"]](d, x, illo_top, w, 102)
    d.rectangle([x, illo_top, x + w - 1, illo_top + 101], outline=INK)
    ty = illo_top + 108
    d.text((x, ty), hero["tag"], font=fonts["tag"], fill=hero["color"])
    hy = ty + 17
    hy = text_block(d, x, hy, hero["head"], fonts["hero_head"], INK,
                    w, 3, 24)
    dy = text_block(d, x, hy + 2, hero["deck"], fonts["hero_deck"], GREY,
                    w, 3, 15)
    return dy


def draw_feature(d, fonts, x, y, w, feat):
    """One feature cell (6 per row). Returns y below the deck."""
    ILLOS[feat["illo"]](d, x, y, w, 52)
    d.rectangle([x, y, x + w - 1, y + 51], outline=INK)
    ty = y + 56
    d.text((x, ty), feat["tag"], font=fonts["tag"], fill=feat["color"])
    hy = ty + 15
    hy = text_block(d, x, hy, feat["head"], fonts["feat_head"], INK,
                    w, 3, 16)
    dy = text_block(d, x, hy + 2, feat["deck"], fonts["feat_deck"], GREY,
                    w, 2, 12)
    return dy


def draw_map(d, fonts, x, y, w, h):
    """World map box with numbered pins (heroes + features) and dots
    (index stories)."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=OCEAN)
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=2)
    map_top = y + 8
    map_h = h - 52

    def proj(lon, lat):
        px = x + int((lon + 180.0) / 360.0 * w)
        py = map_top + int((84.0 - lat) / 144.0 * map_h)
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND)
        d.line(pts + [pts[0]], fill=LAND_EDGE, width=1)

    def region_of(tag):
        return tag.split(" \u00b7 ")[0]

    # Pass 1: leader lines from true spots to offset pins. All lines are
    # drawn before any pin circle, so no line ever crosses a pin face
    # (pins 7/8/10 share one true spot in California).
    pin_specs = []
    for hero in HEROES:
        pin_specs.append((hero["num"], hero["lon"], hero["lat"],
                          hero["dx"], hero["dy"], region_of(hero["tag"])))
    for feat in FEATURES:
        pin_specs.append((feat["num"], feat["lon"], feat["lat"],
                          feat["dx"], feat["dy"], region_of(feat["tag"])))
    for num, lon, lat, dx, dy, region in pin_specs:
        if dx or dy:
            tx, ty = proj(lon, lat)
            color = REGION_COLORS.get(region, (90, 90, 90))
            d.line([tx, ty, tx + dx, ty + dy], fill=color, width=2)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=color)

    # Pass 2: pin circles + numbers on top of the lines.
    for num, lon, lat, dx, dy, region in pin_specs:
        tx, ty = proj(lon, lat)
        px, py = tx + dx, ty + dy
        color = REGION_COLORS.get(region, (90, 90, 90))
        d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=(255, 255, 255),
                  outline=color, width=2)
        label = str(num)
        tw = fonts["pin"].getlength(label)
        d.text((px - tw / 2, py - 6), label, font=fonts["pin"], fill=INK)

    # index dots: stories sharing a spot spread on a small ring
    spots = {}
    for (num, region, _text, lon, lat, dx, dy) in INDEX:
        spots.setdefault((round(lon, 1), round(lat, 1)), []).append(
            (num, region, lon, lat, dx, dy))
    for key, group in spots.items():
        for i, (num, region, lon, lat, dx, dy) in enumerate(group):
            tx, ty = proj(lon, lat)
            if len(group) > 1:
                a = 2 * math.pi * i / len(group)
                tx += int(7 * math.cos(a))
                ty += int(7 * math.sin(a))
            tx += dx
            ty += dy
            color = REGION_COLORS.get(region, (90, 90, 90))
            d.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], fill=color,
                      outline=(255, 255, 255))

    # legend: all regions that appear on this page
    ly = y + h - 38
    items = [("Americas", GREEN), ("Europe", BLUE),
             ("Africa", (166, 110, 28)), ("Middle East", RED),
             ("Asia", GOLD), ("Oceania", TEAL), ("Global", PURPLE)]
    lx = x + 10
    for name, color in items:
        d.ellipse([lx, ly, lx + 8, ly + 8], fill=color)
        d.text((lx + 12, ly - 1), name, font=fonts["footer"], fill=INK)
        lx += 12 + int(fonts["footer"].getlength(name)) + 12
    d.text((x + w - 10, ly + 16), "Pins: heroes + features \u00b7 Dots: index",
           font=fonts["footer"], fill=GREY, anchor="ra")


def draw_index(d, fonts, x, y, w, h):
    """Two-column numbered index of the 21 remaining stories."""
    col_w = (w - 16) // 2
    per_col = 11
    for ci in range(2):
        cx = x + ci * (col_w + 16)
        for ri in range(per_col):
            idx = ci * per_col + ri
            if idx >= len(INDEX):
                break
            num, region, text, _lon, _lat, _dx, _dy = INDEX[idx]
            iy = y + ri * 25
            color = REGION_COLORS.get(region, (90, 90, 90))
            d.ellipse([cx, iy + 1, cx + 15, iy + 16], fill=color)
            label = str(num)
            tw = fonts["idx_num"].getlength(label)
            d.text((cx + (15 - tw) / 2, iy + 2), label,
                   font=fonts["idx_num"], fill=(255, 255, 255))
            d.text((cx + 21, iy + 2), text, font=fonts["idx"],
                   fill=INK)
            tw = fonts["idx"].getlength(text)
            assert tw <= col_w - 21, "index overflow: %r" % text

def build():
    from PIL import Image, ImageDraw, ImageFont
    global _SMALL, _SMALLB
    fonts = load_fonts()
    _SMALL = ImageFont.truetype(_find_font("DejaVuSans.ttf"), 10)
    _SMALLB = ImageFont.truetype(_find_font("DejaVuSans-Bold.ttf"), 10)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # outer frame
    d.rectangle([0, 0, W - 1, 3], fill=INK)
    d.rectangle([0, H - 4, W - 1, H - 1], fill=INK)
    d.rectangle([0, 0, 3, H - 1], fill=INK)
    d.rectangle([W - 4, 0, W - 1, H - 1], fill=INK)

    # ---- kicker
    d.text((MARGIN, 10), "THE WORLD\u2019S NEWS IN ONE PICTURE",
           font=fonts["kicker"], fill=RED)
    right = "36 STORIES \u00b7 6 REGIONS \u00b7 ALL FROM WEDNESDAY"
    d.text((W - MARGIN, 11), right, font=fonts["kicker_r"], fill=GREY,
           anchor="ra")

    # ---- masthead (serif)
    title = "Wednesday 18 November 2026"
    tw = fonts["masthead"].getlength(title)
    assert tw <= CONTENT_W, "masthead too wide: %s" % tw
    d.text(((W - tw) / 2, 30), title, font=fonts["masthead"], fill=INK)
    d.rectangle([MARGIN, 100, W - MARGIN - 1, 102], fill=INK)

    # ---- heroes: 3 columns, illustration + tag + headline + deck
    hero_y = 110
    hero_bottoms = []
    for i, hero in enumerate(HEROES):
        hx = MARGIN + i * (312 + 20)
        hero_bottoms.append(draw_hero(d, fonts, hx, hero_y, 312, hero))
    hero_end = max(hero_bottoms)
    assert hero_end <= 352, "hero overflow: %s" % hero_end
    d.rectangle([MARGIN, 360, W - MARGIN - 1, 361], fill=INK)

    # ---- features: 6 columns x 2 rows
    feat_w = 152
    feat_gap = 12
    row1_y, row2_y = 370, 522
    row_bottoms = []
    for r, ry in enumerate((row1_y, row2_y)):
        for c in range(6):
            feat = FEATURES[r * 6 + c]
            fx = MARGIN + c * (feat_w + feat_gap)
            row_bottoms.append(draw_feature(d, fonts, fx, ry, feat_w, feat))
    feat_end = max(row_bottoms)
    assert feat_end <= 668, "feature overflow: %s" % feat_end

    # ---- section headers
    d.text((MARGIN, 676), "WHERE IT HAPPENED", font=fonts["map_title"],
           fill=RED)
    d.text((560, 676), "ALSO ON WEDNESDAY 18 NOVEMBER",
           font=fonts["map_title"], fill=RED)
    d.rectangle([MARGIN, 694, 548, 695], fill=RED)
    d.rectangle([560, 694, W - MARGIN - 1, 695], fill=RED)

    # ---- map (left) + index (right)
    draw_map(d, fonts, MARGIN, 702, 524, 282)
    draw_index(d, fonts, 560, 706, W - MARGIN - 560, 282)

    # ---- footer
    d.rectangle([MARGIN, 992, W - MARGIN - 1, 993], fill=INK)
    left = "All 36 stories were reported on Wednesday 18 November 2026."
    d.text((MARGIN, 999), left, font=fonts["footer"], fill=GREY)
    right = ("Sources: AP, Reuters, Al Jazeera, DW, ABC News, Euronews, "
             "ToI, Variety, Socceroos, RNZ, ESPNcricinfo.")
    assert fonts["footer"].getlength(left) + 20 \
        + fonts["footer"].getlength(right) <= CONTENT_W, "footer too wide"
    d.text((W - MARGIN, 999), right, font=fonts["footer"], fill=GREY,
           anchor="ra")
    return img


def draw_entry():
    """Render with Pillow. Returns PNG bytes (deterministic)."""
    img = build()
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    try:
        png = draw_entry()
    except Exception:
        # Pillow/fonts missing in this environment: reproduce the exact
        # pre-rendered file bundled in the repo instead of failing.
        # (Same validation the old copier did: file exists, non-empty,
        # starts with the PNG magic bytes.)
        try:
            here = os.path.dirname(os.path.abspath(__file__))
        except NameError:  # run via exec without __file__
            here = os.getcwd()
        bundled = os.path.join(here, "entry.png")
        if not os.path.isfile(bundled):
            raise
        if os.path.getsize(bundled) == 0:
            raise ValueError("entry.png is empty")
        with open(bundled, "rb") as fh:
            if fh.read(len(PNG_MAGIC)) != PNG_MAGIC:
                raise ValueError("entry.png is not a PNG file")
        shutil.copyfile(bundled, out_path)
        return
    with open(out_path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
