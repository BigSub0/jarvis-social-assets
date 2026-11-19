#!/usr/bin/env python3
"""Build the daily free-card email from cards/latest.json.

Usage:
  python3 templates/v3/build_email.py <unsubscribe_url> [--welcome] [--out DIR]

Writes DIR/email.html, DIR/email.txt and DIR/email.json (subject + the local image files to attach
inline, in order: att0, att1). Gmail strips remote images, so the card images are attached inline
and referenced as cid:att0 / cid:att1.
"""
import json, sys, argparse, pathlib, html, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = "https://raw.githubusercontent.com/BigSub0/jarvis-social-assets/main/"
ADDRESS = "5907 Southland Drive, Stone Mountain, GA 30087"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("unsubscribe_url")
    ap.add_argument("--welcome", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "cards" / "_email"))
    a = ap.parse_args()
    m = json.loads((ROOT / "cards" / "latest.json").read_text())
    date = m["date"]
    cards = sorted(m["cards"], key=lambda c: 0 if c["slot"] == "am" else 1)  # morning card first
    files = []
    for c in cards:
        rel = c["image"].replace(RAW, "")
        p = (ROOT / rel).resolve()
        if not p.exists():
            sys.exit(f"missing image {p}")
        files.append(str(p))
    utm = lambda content: "https://jarvissportsai.com/?" + urllib.parse.urlencode(
        {"utm_source": "email", "utm_medium": "daily", "utm_campaign": date, "utm_content": content})
    games = " and ".join(c["game"] for c in cards)
    subject = ("Welcome! " if a.welcome else "") + f"Today's free JARVIS cards: {cards[0]['game']}" + (f" + {cards[1]['game']}" if len(cards) > 1 else "")
    esc = html.escape
    intro = ("Thanks for joining. Every morning you'll get the day's free JARVIS cards: real game-log research on the games worth watching. "
             if a.welcome else "")
    rows = ""
    for i, c in enumerate(cards):
        rows += f"""
<tr><td style="padding:18px 0 6px;font:700 13px Arial,sans-serif;letter-spacing:2px;color:#7adeff">{esc(c['league'])} · {esc(c['game'].upper())}</td></tr>
<tr><td><img src="cid:att{i}" width="520" style="width:100%;max-width:520px;border-radius:12px;display:block" alt="{esc(c['game'])} JARVIS card"></td></tr>
<tr><td style="padding:10px 0 4px;font:16px/1.4 Arial,sans-serif;color:#ebeff5"><b style="color:#b8eb6b">📊 JARVIS Safe Sheet:</b> {esc(c['nugget'])}</td></tr>"""
    body = f"""<!doctype html><html><body style="margin:0;background:#0b0e14">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0b0e14"><tr><td align="center" style="padding:24px 16px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px">
<tr><td style="font:900 24px Arial,sans-serif;color:#ebeff5">JARVIS <span style="color:#b8eb6b">SPORTS AI</span></td></tr>
<tr><td style="padding:14px 0 0;font:16px/1.5 Arial,sans-serif;color:#ebeff5">{esc(intro)}Here's today's free research for {esc(games)}.</td></tr>
{rows}
<tr><td style="padding:22px 0 8px" align="center"><a href="{utm('breakdown')}" style="display:inline-block;background:#7adeff;color:#0b0e14;font:700 17px Arial,sans-serif;text-decoration:none;padding:14px 26px;border-radius:40px">See today's free breakdown</a></td></tr>
<tr><td style="padding:6px 0 18px" align="center"><a href="{utm('trial')}" style="display:inline-block;background:#b8eb6b;color:#0b0e14;font:700 17px Arial,sans-serif;text-decoration:none;padding:14px 26px;border-radius:40px">Start your free month</a></td></tr>
<tr><td style="font:12px/1.5 Arial,sans-serif;color:#8a94a6;border-top:1px solid #2b3645;padding-top:14px">
Research only: historical stats and estimates, not predictions or guarantees.<br>
jarvissportsai.com · {ADDRESS}<br>
<a href="{esc(a.unsubscribe_url)}" style="color:#8a94a6">Unsubscribe</a></td></tr>
</table></td></tr></table></body></html>"""
    text = (f"JARVIS SPORTS AI\n\n{intro}Today's free research for {games}.\n\n"
            + "\n".join(f"{c['league']} · {c['game']}\n📊 JARVIS Safe Sheet: {c['nugget']}\n" for c in cards)
            + f"\nSee today's free breakdown: {utm('breakdown')}\nStart your free month: {utm('trial')}\n\n"
            f"Research only: historical stats and estimates, not predictions or guarantees.\njarvissportsai.com · {ADDRESS}\nUnsubscribe: {a.unsubscribe_url}\n")
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "email.html").write_text(body); (out / "email.txt").write_text(text)
    (out / "email.json").write_text(json.dumps({"subject": subject, "inline_images": files}, indent=1))
    print(json.dumps({"subject": subject, "inline_images": files}))


if __name__ == "__main__":
    main()
