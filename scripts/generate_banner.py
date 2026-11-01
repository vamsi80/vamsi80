"""
generate_banner.py  —  self-hosted "profile.sh --live" terminal banner.

Produces assets/banner-dark.svg and assets/banner-light.svg:
  * left panel  VISUAL.MAP  : stipple point-cloud portrait of the GitHub avatar
  * right panel SYSTEM.INFO : monospace spec table with dotted leaders

Edit SYSTEM_INFO / FOOTER below and re-run:  python scripts/generate_banner.py
Source photo: scripts auto-downloads https://github.com/<USER>.png (cached as
_avatar_src.png).  Bump VERSION and the ?v=N in README to cache-bust on GitHub.
"""
import os
import urllib.request
import numpy as np
from PIL import Image

USER = "vamsi80"
VERSION = 1
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
SRC = os.path.join(ROOT, "_avatar_src.png")

# ------------------------------------------------------------------ content ---
TAGLINE_PILL = "@vamsi80"
SYSTEM_INFO = [
    ("Subject",        "Vamsi"),
    ("Role",           "Full-Stack Web Developer"),
    ("Origin",         "Bengaluru, India"),
    ("Status",         "Building + Shipping"),
    ("Focus",          "Enterprise ERP · Web Apps"),
    ("ToolChain",      "VS Code · Git · Vercel"),
    ("Core.Lang",      "TypeScript · JavaScript · SQL"),
    ("Core.Frontend",  "React · Next.js · Tailwind · GSAP"),
    ("Core.Backend",   "Node · Express"),
    ("Core.Database",  "PostgreSQL"),
    ("Core.Infra",     "Vercel · Docker"),
    ("Grid.Portfolio", "portfolio-eta-tan-14.vercel.app"),
    ("Grid.LinkedIn",  "/in/vamsi-krishna-mannem"),
    ("Grid.GitHub",    "vamsi80"),
]
FOOTER_LEFT = "ALL SYSTEMS NOMINAL"
FOOTER_RIGHT = "UTC+5:30 · BLR NODE"
TITLE = "profile.sh --live"

# ------------------------------------------------------------------- layout ---
W, H = 1160, 460
PBOX = 300  # portrait sampling grid (square)
N_POINTS = 12000
CROP = (100, 95, 330, 325)

# monospace glyph advance as a fraction of font-size (Consolas/DejaVu ~0.60)
ADV = 0.60


def ensure_avatar():
    if os.path.exists(SRC):
        return
    url = f"https://github.com/{USER}.png"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=30).read()
    with open(SRC, "wb") as f:
        f.write(data)


def build_points():
    im = Image.open(SRC).convert("RGB").crop(CROP).resize((PBOX, PBOX), Image.LANCZOS)
    arr = np.asarray(im).astype(np.float32)
    gray = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]) / 255.0

    yy, xx = np.mgrid[0:PBOX, 0:PBOX].astype(np.float32)
    cx, cy = PBOX * 0.50, PBOX * 0.46
    rx, ry = PBOX * 0.44, PBOX * 0.55
    d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    mask = np.clip(1.02 - d, 0, 1)

    weight = (gray ** 1.35) * mask
    weight[gray < 0.20] *= 0.08

    rng = np.random.default_rng(7)
    flat = weight.flatten()
    probs = flat / flat.sum()
    idx = rng.choice(flat.size, size=N_POINTS, replace=True, p=probs)
    ys = idx // PBOX
    xs = idx % PBOX
    shades = gray[ys, xs]
    xs = xs + rng.random(N_POINTS)
    ys = ys + rng.random(N_POINTS)
    return list(zip(xs.tolist(), ys.tolist(), shades.tolist()))


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def hx(rgb):
    return "#%02x%02x%02x" % rgb


DARK = dict(
    name="dark",
    bg="#0d1117", win="#0d1117", border="#30363d", titlebar="#161b22",
    muted="#6e7681", label="#8b949e", value="#c9d1d9", leader="#30363d",
    accent="#2f81f7", pill_bg="#1f6feb", pill_tx="#ffffff",
    pt_lo=(47, 129, 247), pt_hi=(240, 245, 255),
    green="#3fb950", red="#ff5f56", yellow="#ffbd2e", grn="#27c93f",
)
LIGHT = dict(
    name="light",
    bg="#ffffff", win="#ffffff", border="#d0d7de", titlebar="#f6f8fa",
    muted="#6e7681", label="#57606a", value="#1f2328", leader="#d8dee4",
    accent="#0969da", pill_bg="#0969da", pill_tx="#ffffff",
    pt_lo=(10, 48, 105), pt_hi=(9, 105, 218),
    green="#1a7f37", red="#ff5f56", yellow="#ffbd2e", grn="#27c93f",
)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(theme, points):
    t = theme
    o = []
    o.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="\'JetBrains Mono\',\'Cascadia Code\',Consolas,\'DejaVu Sans Mono\',monospace">'
    )
    o.append(f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>')

    # window frame
    o.append(f'<rect x="8" y="8" width="{W-16}" height="{H-16}" rx="14" '
             f'fill="{t["win"]}" stroke="{t["border"]}" stroke-width="1.5"/>')
    # title bar
    o.append(f'<path d="M8 22 Q8 8 22 8 H{W-22} Q{W-8} 8 {W-8} 22 V56 H8 Z" fill="{t["titlebar"]}"/>')
    o.append(f'<line x1="8" y1="56" x2="{W-8}" y2="56" stroke="{t["border"]}" stroke-width="1.5"/>')
    o.append(f'<circle cx="30" cy="32" r="6.5" fill="{t["red"]}"/>')
    o.append(f'<circle cx="52" cy="32" r="6.5" fill="{t["yellow"]}"/>')
    o.append(f'<circle cx="74" cy="32" r="6.5" fill="{t["grn"]}"/>')
    o.append(f'<text x="{W/2}" y="37" text-anchor="middle" font-size="15" '
             f'fill="{t["muted"]}" letter-spacing="2">{esc(TITLE)}</text>')

    # ---- panels ----
    lp_x, lp_w = 28, 380
    rp_x, rp_w = 424, 708
    p_y, p_h = 72, 364
    for px, pw in ((lp_x, lp_w), (rp_x, rp_w)):
        o.append(f'<rect x="{px}" y="{p_y}" width="{pw}" height="{p_h}" rx="8" '
                 f'fill="none" stroke="{t["border"]}" stroke-width="1.5"/>')

    # ---- LEFT: VISUAL.MAP ----
    o.append(f'<text x="{lp_x+18}" y="100" font-size="13" font-weight="700" '
             f'fill="{t["accent"]}" letter-spacing="2">VISUAL.MAP</text>')
    o.append(f'<text x="{lp_x+lp_w-18}" y="100" text-anchor="end" font-size="11" '
             f'fill="{t["muted"]}" letter-spacing="1">300x300 / 1-BIT</text>')

    # portrait box + corner brackets
    bx, by, bs = lp_x + 40, 118, 300
    cl = 16
    bracket = (f'M{bx} {by+cl} V{by} H{bx+cl} '
               f'M{bx+bs-cl} {by} H{bx+bs} V{by+cl} '
               f'M{bx+bs} {by+bs-cl} V{by+bs} H{bx+bs-cl} '
               f'M{bx+cl} {by+bs} H{bx} V{by+bs-cl}')
    o.append(f'<path d="{bracket}" fill="none" stroke="{t["accent"]}" stroke-width="2"/>')

    # points
    o.append(f'<g transform="translate({bx},{by})">')
    for x, y, sh in points:
        col = hx(lerp(t["pt_lo"], t["pt_hi"], min(1.0, sh * 1.15)))
        r = 0.95 if sh > 0.5 else 0.72
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}"/>')
    o.append('</g>')

    o.append(f'<text x="{lp_x+18}" y="{by+bs+20}" font-size="10" '
             f'fill="{t["muted"]}" letter-spacing="1">PTS {N_POINTS} · FS/SERPENTINE</text>')

    # ---- RIGHT: SYSTEM.INFO ----
    o.append(f'<text x="{rp_x+18}" y="100" font-size="13" font-weight="700" '
             f'fill="{t["accent"]}" letter-spacing="2">SYSTEM.INFO</text>')
    # LIVE + pill on header right
    pill_r = rp_x + rp_w - 18
    pill_tw = len(TAGLINE_PILL) * 15 * ADV
    pill_w = pill_tw + 26
    pill_l = pill_r - pill_w
    o.append(f'<rect x="{pill_l:.1f}" y="84" width="{pill_w:.1f}" height="22" rx="11" fill="{t["pill_bg"]}"/>')
    o.append(f'<text x="{(pill_l+pill_r)/2:.1f}" y="100" text-anchor="middle" font-size="13" '
             f'fill="{t["pill_tx"]}">{esc(TAGLINE_PILL)}</text>')
    live_r = pill_l - 12
    o.append(f'<text x="{live_r:.1f}" y="100" text-anchor="end" font-size="12" '
             f'fill="{t["red"]}" letter-spacing="1">LIVE</text>')
    o.append(f'<circle cx="{live_r - 4*15*ADV - 10:.1f}" cy="95" r="4" fill="{t["red"]}"/>')
    o.append(f'<line x1="{rp_x+18}" y1="114" x2="{rp_x+rp_w-18}" y2="114" '
             f'stroke="{t["border"]}" stroke-width="1" stroke-dasharray="2 4"/>')

    # rows
    row_x = rp_x + 18
    val_r = rp_x + rp_w - 18
    y0, y1 = 140, 414
    n = len(SYSTEM_INFO)
    step = (y1 - y0) / (n - 1)
    fs = 15
    for i, (lab, val) in enumerate(SYSTEM_INFO):
        y = y0 + i * step
        lw = len(lab) * fs * ADV
        vw = len(val) * fs * ADV
        o.append(f'<text x="{row_x}" y="{y:.1f}" font-size="{fs}" fill="{t["label"]}">{esc(lab)}</text>')
        o.append(f'<text x="{val_r}" y="{y:.1f}" text-anchor="end" font-size="{fs}" fill="{t["value"]}">{esc(val)}</text>')
        dx1 = row_x + lw + 8
        dx2 = val_r - vw - 8
        if dx2 > dx1:
            o.append(f'<line x1="{dx1:.1f}" y1="{y-4:.1f}" x2="{dx2:.1f}" y2="{y-4:.1f}" '
                     f'stroke="{t["leader"]}" stroke-width="1.4" stroke-dasharray="1 5" stroke-linecap="round"/>')

    # footer
    fy = 428
    o.append(f'<circle cx="{row_x+4}" cy="{fy-4}" r="4" fill="{t["green"]}"/>')
    o.append(f'<text x="{row_x+16}" y="{fy}" font-size="10" fill="{t["green"]}" '
             f'letter-spacing="1">{esc(FOOTER_LEFT)}</text>')
    o.append(f'<text x="{val_r}" y="{fy}" text-anchor="end" font-size="10" '
             f'fill="{t["muted"]}" letter-spacing="1">{esc(FOOTER_RIGHT)}</text>')

    o.append('</svg>')
    return "\n".join(o)


def main():
    ensure_avatar()
    os.makedirs(ASSETS, exist_ok=True)
    pts = build_points()
    for theme in (DARK, LIGHT):
        out = os.path.join(ASSETS, f"banner-{theme['name']}.svg")
        with open(out, "w", encoding="utf-8") as f:
            f.write(svg(theme, pts))
        kb = os.path.getsize(out) / 1024
        print(f"wrote {out}  ({kb:.0f} KB)")
    print(f"VERSION {VERSION} -> reference as assets/banner-<theme>.svg?v={VERSION}")


if __name__ == "__main__":
    main()
