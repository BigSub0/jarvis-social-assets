# JARVIS cards v3: 8 rotating looks

Looks (rotation order): stadium · hud (JARVIS Scan) · magazine · mixtape · broadcast · neon · bold · retro.
Brand kit (colors, logo, fonts from jarvissportsai.com): `brand.json`, `assets/brand/`, `assets/fonts/` (no npm needed).

Daily use:
1. Write `cards/YYYY-MM-DD/<slug>.json` (copy `cards/2026-11-19/nba-nyk-min.json`).
2. `python3 templates/v3/build_card.py cards/YYYY-MM-DD/<slug>.json --slot am` (or `--slot pm`).
   Writes .html/.png/.jpg and prints the look used. The look is picked from the date and slot, so the AM and PM cards always differ and all 8 cycle every 4 days.
   Fix any WARNING (shorten text) and re-run. `--theme NAME` forces a look.
3. `templates/make_short.sh <jpg> <mp4>` for YouTube Shorts.
