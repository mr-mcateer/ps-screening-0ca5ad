#!/usr/bin/env python3
"""Versions page generator (GOVERNING for versions/index.html; never hand-edit the HTML).

versions.json is the record of every cut; this writes index.html from it. Standard library only, so it runs the
same on the Macs and the PC. Add a cut with --add, or edit versions.json, then run with no arguments.

  python3 build_versions.py
  python3 build_versions.py --add beach '{"title": "Draft v0.4", "video": "beach-v0.4.mp4", ...}'

Public page: no brand names, no legal or licence notes, no internal asks, no em dashes. check() refuses them.
"""
import html, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "versions.json"
BANNED = [r"—", r"red stripe", r"counsel", r"trade dress", r"licen[cs]", r"temp music", r"\bASKS?\b",
          r"DO_NOT_SHIP", r"unlicensed"]

CSS = (HERE / "style.css").read_text() if (HERE / "style.css").exists() else ""


def check(text):
    bad = [b for b in BANNED if re.search(b, text, re.I)]
    if bad:
        sys.exit(f"build_versions: refused, public text matches {bad}")


def e(s):
    return html.escape(str(s), quote=True)


def cut(it):
    ch = "".join(f"<li>{e(c)}</li>" for c in it.get("changes", []))
    ch = f'<ul class="chg">{ch}</ul>' if ch else ""
    meta = " · ".join(x for x in [it.get("meta", ""), it.get("date", "")] if x)
    return (f'<figure><video controls playsinline preload="metadata" poster="{e(it["poster"])}" src="{e(it["video"])}">'
            f'</video><figcaption><b>{e(it["title"])}</b><span>{e(meta)}</span>'
            f'<span class="where">Rendered on {e(it["rendered"])}</span>'
            f'<p><strong>TL;DR</strong> {e(it.get("tldr", ""))}</p>{ch}</figcaption></figure>')


def sting(it):
    cls = f' class="{e(it["cls"])}"' if it.get("cls") else ""
    return (f'<figure{cls}><video src="{e(it["video"])}" poster="{e(it["poster"])}" autoplay muted loop playsinline '
            f'aria-label="{e(it["title"])} logo end screen"></video><figcaption><b>{e(it["title"])}</b></figcaption></figure>')


def sheet(it):
    return (f'<figure><a href="{e(it["img"])}"><img src="{e(it["img"])}" alt="{e(it["alt"])}" width="{it["w"]}" '
            f'height="{it["h"]}" loading="lazy"></a><figcaption><b>{e(it["title"])}</b><span>{e(it["sub"])}</span>'
            f'</figcaption></figure>')


def build(d):
    out = []
    for s in d["sections"]:
        kind = s["kind"]
        body = "".join({"cuts": cut, "stings": sting, "sheets": sheet}[kind](it) for it in s["items"])
        grid = {"cuts": "cuts", "stings": "stings", "sheets": "sheets"}[kind]
        label = f'<span class="label">{e(s["label"])}</span>' if s.get("label") else ""
        note = f'<p class="note">{e(s["note"])}</p>' if s.get("note") else ""
        out.append(f'<section aria-labelledby="{e(s["id"])}-h"><div class="head"><h2 id="{e(s["id"])}-h">'
                   f'{e(s["title"])}</h2>{label}</div>{note}<div class="{grid}">{body}</div></section>')
    nav = "".join(f'<a href="#{e(s["id"])}-h">{e(s["title"].split(" · ")[0])}</a>' for s in d["sections"][:3])
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<title>PoleStrike Cuts</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Barlow:wght@400;500;600&family=Barlow+Semi+Condensed:wght@500;600&display=swap">
<style>
{CSS}
  figcaption .where {{ color: var(--cyan); }}
  figcaption strong {{ font: 600 12px/1 var(--label); letter-spacing: .1em; color: var(--text); margin-right: 4px; }}
  .chg {{ margin: 4px 0 0; padding-left: 18px; color: var(--muted); font-size: 14px; display: grid; gap: 2px; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <img src="../room/logo.png" alt="PoleStrike logo: the rainbow bottle emblem over the PoleStrike wordmark" width="900" height="615">
    <h1>Every cut so far</h1>
    <p>Every PoleStrike film version in one place, newest first, with what changed and where each one was rendered. As of {e(d["asof"])}.</p>
    <nav aria-label="Sections">{nav}<a href="../room/">Screening room</a></nav>
  </header>
  {"".join(out)}
  <footer>PoleStrike · patent pending · shared privately for review</footer>
</div>
</body>
</html>
"""
    check(page)
    return page


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    if len(sys.argv) >= 4 and sys.argv[1] == "--add":
        sec = next(s for s in d["sections"] if s["id"] == sys.argv[2])
        item = json.loads(sys.argv[3])
        check(json.dumps(item))
        sec["items"] = [i for i in sec["items"] if i.get("title") != item["title"]]
        sec["items"].insert(0, item)
        if item.get("date"):
            d["asof"] = item["date"]
        DATA.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (HERE / "index.html").write_text(build(d), encoding="utf-8")
    print(f"build_versions: index.html written, {sum(len(s['items']) for s in d['sections'])} items")


if __name__ == "__main__":
    main()
