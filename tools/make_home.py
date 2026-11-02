"""The four app cards of alifo.app's homepage, in one format: app icon, name, one-line tagline, and a 16:10 visual
(the app's marketing screenshot when there is one, otherwise a panel with the icon on the app's own colours).

Icons come from each project's AppIcon set. KeyToons' icon is a full square: it is placed on the macOS icon grid
(824 px body, rounded corners) like the others. AfterShot's project is not on this Mac: its icon is a neutral one
(initial on the colours of its page), to be replaced by the real icon when available.

Writes assets/img/apps/* and the cards in index.html (between <h2>Apps</h2> and the footer) of the site's working tree.
Run from the tooling worktree (branch "tooling"), with its own environment (docs/SITE.md):
  .venv/bin/python tools/make_home.py
"""
import os, re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont



def site_dir():
    """The site's working tree (branch main): $ALIFO_SITE, else the alifo-site folder next to this tooling worktree."""
    env = os.environ.get("ALIFO_SITE")
    site = Path(env).expanduser() if env else Path(__file__).resolve().parents[2] / "alifo-site"
    if not (site / "CNAME").exists():
        raise SystemExit(f"not the site's working tree: {site} (set ALIFO_SITE)")
    return site


SITE = site_dir()
DEV = Path.home() / "Developer"                                # the apps' repositories (icons, screenshots)
EXTRACTO = DEV / "Extracto"
# KeyToons' marketing screenshot (real menu bar UI); without it, its card shows the icon panel.
KEYTOONS_SHOT = Path.home() / "Downloads" / "keytoons_shot_1_duck.png"
OUT = SITE / "assets" / "img" / "apps"
SF = "/System/Library/Fonts/SFNS.ttf"

APPS = [
    # slug, name, tagline, icon source, screenshot, panel colours (top, bottom) when there is no screenshot
    ("aftershot", "AfterShot", "A private diary for allergy shots, on iPhone.", None, None, ("#26301f", "#10150f")),
    ("alwah", "Alwah", "Learn the Quran by heart, on your Mac.",
     DEV / "Lemseed/App/Resources/Assets.xcassets/AppIcon.appiconset/icon_512x512@2x.png",
     DEV / "Lemseed/captures/appstore/mac-en/01-msid.png", None),
    ("extracto", "Extracto", "Text, tables and data from any PDF or image, on your Mac.",
     EXTRACTO / "Extracto/Resources/Assets.xcassets/AppIcon.appiconset/icon_512x512@2x.png",
     EXTRACTO / "captures/appstore/mac-en/1-tables.png", None),
    ("grandio", "Grandio", "Print any photo big and sharp, with an Etsy print pack, on your Mac.",
     DEV / "Restora/Restora/Resources/Assets.xcassets/AppIcon.appiconset/icon_512x512@2x.png",
     DEV / "Restora/captures/appstore/mac-en/1-print.png", None),
    ("keytoons", "KeyToons", "Fun keyboard sounds for your Mac.",
     DEV / "KeyToons/Resources/Assets.xcassets/AppIcon.appiconset/icon_512x512@2x.png",
     KEYTOONS_SHOT if KEYTOONS_SHOT.exists() else None, ("#2c3a5c", "#12161d")),
]
SHOT_ALT = {
    "alwah": "Alwah on a Mac: today's memorization session, with recent, new and old words to recite.",
    "extracto": "Extracto on a Mac: a table read from a PDF and the Excel file it wrote.",
    "grandio": "Grandio's Print Studio on a Mac: a 1940 poster framed for an 18 × 24 in print at 300 dpi, quality Good, with a before/after loupe at 100 %.",
    "keytoons": "KeyToons' menu on a Mac, with the Duck theme selected: every key goes quack.",
}


def on_grid(icon):
    """A full-square icon on the macOS icon grid: 824 px body with rounded corners, centred on 1024."""
    body = icon.resize((824, 824), Image.LANCZOS)
    mask = Image.new("L", (824, 824), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 823, 823], radius=185, fill=255)
    out = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    out.paste(body, (100, 100), mask)
    return out


def neutral_icon(top, bottom, letter):
    """Placeholder: the initial on a vertical gradient, on the macOS icon grid."""
    g = Image.new("RGB", (1, 824))
    t, b = (int(top[i:i + 2], 16) for i in (1, 3, 5)), (int(bottom[i:i + 2], 16) for i in (1, 3, 5))
    t, b = list(t), list(b)
    for y in range(824):
        g.putpixel((0, y), tuple(round(t[i] + (b[i] - t[i]) * y / 823) for i in range(3)))
    body = g.resize((824, 824)).convert("RGBA")
    f = ImageFont.truetype(SF, 470)
    f.set_variation_by_axes([100, 96, 400, 700])
    ImageDraw.Draw(body).text((412, 430), letter, font=f, fill=(226, 164, 60), anchor="mm")
    return on_grid(body.resize((1024, 1024)))


def save(img, stem, sizes):
    for w in sizes:
        im = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
        im.save(OUT / f"{stem}-{w}.png", optimize=True)
        im.save(OUT / f"{stem}-{w}.webp", "WEBP", quality=85 if img.width == img.height else 80, method=6)


def card(slug, name, tagline, has_shot, colours):
    icon = (f'<picture><source type="image/webp" srcset="/assets/img/apps/{slug}-icon-64.webp 1x, '
            f'/assets/img/apps/{slug}-icon-128.webp 2x"><img class="app-card-icon" src="/assets/img/apps/{slug}-icon-64.png" '
            f'srcset="/assets/img/apps/{slug}-icon-128.png 2x" width="52" height="52" alt=""></picture>')
    if has_shot:
        stem = f"/assets/img/apps/{slug}-shot"
        visual = (f'<picture><source type="image/webp" srcset="{stem}-640.webp 640w, {stem}-1280.webp 1280w" '
                  f'sizes="(min-width: 708px) 610px, 88vw"><img src="{stem}-640.png" srcset="{stem}-640.png 640w, '
                  f'{stem}-1280.png 1280w" sizes="(min-width: 708px) 610px, 88vw" width="640" height="400" '
                  f'loading="lazy" decoding="async" alt="{SHOT_ALT[slug]}"></picture>')
        visual = f'<div class="app-card-visual">{visual}</div>'
    else:
        visual = (f'<div class="app-card-visual app-card-panel" style="background: linear-gradient(160deg, {colours[0]}, {colours[1]})">'
                  f'<img src="/assets/img/apps/{slug}-icon-256.png" width="128" height="128" loading="lazy" decoding="async" alt=""></div>')
    return (f'  <a class="app-card" href="/{slug}/">\n    <div class="app-card-head">{icon}\n'
            f'      <div><div class="name">{name}</div><div class="tag">{tagline}</div></div>\n    </div>\n'
            f'    {visual}\n  </a>\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = []
    for slug, name, tagline, icon_src, shot, colours in APPS:
        if icon_src is None:
            icon = neutral_icon(*colours, name[0])
        else:
            icon = Image.open(icon_src).convert("RGBA")
            if icon.getchannel("A").getbbox() == (0, 0, 1024, 1024):      # full square: put it on the grid
                icon = on_grid(icon)
        save(icon, f"{slug}-icon", [64, 128, 256])
        if shot:
            save(Image.open(shot).convert("RGB"), f"{slug}-shot", [640, 1280])
        cards.append(card(slug, name, tagline, shot is not None, colours))
        print(slug, "icon" + (" + screenshot" if shot else " + panel"))
    index = SITE / "index.html"
    src = index.read_text(encoding="utf-8")
    src = re.sub(r"(<h2>Apps</h2>\n\n).*?(\n  <footer)", lambda m: m.group(1) + "\n".join(cards) + m.group(2), src, flags=re.S)
    index.write_text(src, encoding="utf-8")


if __name__ == "__main__":
    main()
