#!/usr/bin/env python3
"""JARVIS card builder v3: 8 rotating looks, one data file.

Usage:
  python3 templates/v3/build_card.py cards/YYYY-MM-DD/<slug>.json [--theme NAME|auto] [--slot am|pm]

Writes cards/YYYY-MM-DD/<slug>.html, .png and .jpg next to the JSON.
--theme auto (default) picks the look from the rotation: date + slot, so the AM and
PM cards always differ and each day continues the cycle through all 8 looks.
Brand colors / logo live in templates/v3/brand.json (one place to change).
"""
import json, sys, argparse, datetime, pathlib, re
from jinja2 import Environment, FileSystemLoader

ROOT = pathlib.Path(__file__).resolve().parents[2]
V3 = ROOT / "templates" / "v3"
THEMES = ["stadium", "hud", "magazine", "mixtape", "broadcast", "neon", "bold", "retro"]
EPOCH = datetime.date(2026, 11, 19)
TIME_LABEL = {"football": "KICKOFF", "baseball": "FIRST PITCH", "basketball": "TIP-OFF", "hockey": "PUCK DROP"}

FONTS = {  # family: (file stem, [weights])
    "Anton": ("anton", [400]), "BC": ("barlow-condensed", [600, 800, 900]), "Teko": ("teko", [500, 600, 700]),
    "Saira": ("saira-condensed", [600, 800, 900]), "DMSerif": ("dm-serif-display", [400]),
    "Inter": ("inter", [500, 700, 800, 900]), "Orbitron": ("orbitron", [700, 900]), "Rajdhani": ("rajdhani", [600, 700]),
    "Marker": ("permanent-marker", [400]), "Bebas": ("bebas-neue", [400]), "Mono": ("jetbrains-mono", [500, 700, 800]),
    "Grotesk": ("space-grotesk", [500, 700]), "Bungee": ("bungee", [400]), "Oswald": ("oswald", [500, 700]),
    "Archivo": ("archivo-black", [400]),
    # brand fonts from jarvissportsai.com
    "Fraunces": ("fraunces", [600, 800, 900]), "FrauncesI": ("fraunces", [600, 800, 900], "italic"),
    "Plex": ("ibm-plex-sans", [500, 600, 700]), "PlexMono": ("ibm-plex-mono", [500, 600, 700]),
}


def theme_for(date_str, slot):
    d = datetime.date.fromisoformat(date_str)
    return THEMES[((d - EPOCH).days * 2 + (1 if slot == "pm" else 0)) % len(THEMES)]


def font_css(rel):
    out = []
    for fam, spec in FONTS.items():
        stem, ws = spec[0], spec[1]; style = spec[2] if len(spec) > 2 else "normal"
        for w in ws:
            out.append(f"@font-face{{font-family:{fam};font-weight:{w};src:url({rel}assets/fonts/{stem}-latin-{w}-{style}.woff2)}}")
    return "\n".join(out)


def ring_svg(hit, total, on, off, size=190, width=16, glow=True, gap=10):
    """Segmented progress ring (one segment per game, lit = hit)."""
    import math
    c = size / 2; r = c - width / 2 - 4; seg = 360 / total; gap = min(gap, seg * 0.4); parts = []
    for i in range(total):
        a0 = math.radians(i * seg + gap / 2 - 90); a1 = math.radians((i + 1) * seg - gap / 2 - 90)
        x0, y0, x1, y1 = c + r * math.cos(a0), c + r * math.sin(a0), c + r * math.cos(a1), c + r * math.sin(a1)
        col = on if i < hit else off
        parts.append(f'<path d="M{x0:.1f} {y0:.1f} A{r:.1f} {r:.1f} 0 0 1 {x1:.1f} {y1:.1f}" stroke="{col}" '
                     f'stroke-width="{width}" fill="none" stroke-linecap="round"{" filter=\"url(#rg)\"" if glow and i < hit else ""}/>')
    defs = '<defs><filter id="rg"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
    return f'<svg viewBox="0 0 {size} {size}" width="100%" height="100%">{defs}{"".join(parts)}</svg>'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("--theme", default="auto"); ap.add_argument("--slot", default="am")
    ap.add_argument("--out", default=None, help="output stem (default: same as data file)")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    dp = pathlib.Path(a.data).resolve()
    d = json.loads(dp.read_text())
    date = d.get("date") or dp.parent.name
    theme = theme_for(date, a.slot) if a.theme == "auto" else a.theme
    assert theme in THEMES, f"unknown theme {theme}; pick one of {THEMES}"
    brand = json.loads((V3 / "brand.json").read_text())
    stem = pathlib.Path(a.out).resolve() if a.out else dp.with_suffix("")
    rel = "../" * (len(stem.parent.relative_to(ROOT).parts))
    d.setdefault("time_label", TIME_LABEL.get(d["sport"], "START"))
    d["match"] = f'{d["away"]["name"]} ({d["away"]["rec"]}) AT {d["home"]["name"]} ({d["home"]["rec"]})'.upper().replace("-", "–")
    for p in ("p1", "p2"):
        d[p]["t"] = d[d[p]["team"]]
    n = d["nugget"]; n["frac"] = f'{n["hit"]}/{n["total"]}'
    if d.get("venuePhoto") and not d["venuePhoto"].startswith(("../", "http")):
        d["venuePhoto"] = rel + d["venuePhoto"]
    env = Environment(loader=FileSystemLoader(str(V3)), autoescape=False)
    env.globals.update(ring=ring_svg)
    html = env.get_template(f"themes/{theme}.html.j2").render(d=d, b=brand, fonts=font_css(rel), rel=rel, theme=theme)
    stem.with_suffix(".html").write_text(html)
    print("theme:", theme)
    if a.no_render:
        return
    render(stem.with_suffix(".html"), stem.with_suffix(".png"))
    from PIL import Image
    Image.open(stem.with_suffix(".png")).convert("RGB").save(stem.with_suffix(".jpg"), "JPEG", quality=92, optimize=True, progressive=True)
    print("wrote", stem.with_suffix(".jpg"))


def render(src, out):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(pathlib.Path(src).resolve().as_uri()); pg.wait_for_timeout(900)
        probs = pg.evaluate("""() => {
          const out=[]; const foot=document.querySelector('.foot');
          const c=document.querySelector('.content');
          if(foot&&c){const bot=Math.max(...[...c.children].filter(e=>getComputedStyle(e).display!=='none').map(e=>e.getBoundingClientRect().bottom));
            const ft=foot.getBoundingClientRect().top; if(bot>ft+2) out.push('content runs into footer by '+Math.round(bot-ft)+'px');}
          document.querySelectorAll('.chk').forEach(e=>{ if(e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2) out.push('text cut off: '+e.textContent.trim().slice(0,40)); });
          const r=document.body.getBoundingClientRect(); if(document.documentElement.scrollHeight>1922) out.push('page taller than 1920');
          return out; }""")
        for m in probs: print("WARNING:", m)
        pg.screenshot(path=str(out)); b.close()


if __name__ == "__main__":
    main()
