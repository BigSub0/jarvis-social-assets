"""Render a JARVIS card HTML file to a 1080x1920 PNG.
Usage: python3 templates/render.py path/to/card.html out.png
Fonts: run `npm i @fontsource/anton @fontsource/barlow-condensed` in the repo root first.
"""
import sys, pathlib
from playwright.sync_api import sync_playwright
src = pathlib.Path(sys.argv[1]).resolve(); out = sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto(src.as_uri()); pg.wait_for_timeout(800)
    way = pg.evaluate('document.querySelector(".way").getBoundingClientRect().bottom')
    foot = pg.evaluate('document.querySelector(".foot").getBoundingClientRect().top')
    if way > foot: print(f"WARNING: content overflows footer ({way:.0f} > {foot:.0f}) - tighten text"); 
    pg.screenshot(path=out); b.close()
print("rendered", out)
