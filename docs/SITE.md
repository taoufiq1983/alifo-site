# alifo.app: generated pages

The site is the GitHub Pages repository `taoufiq1983/alifo-site`, published from the `main` branch. Two scripts
generate parts of it. They read images from the apps' repositories in `~/Developer`. The other apps' pages are written
by hand.

## Where the tools live: the `tooling` branch (not published)

`main` has a `.nojekyll` file, so Jekyll is off and GitHub Pages serves every file of `main` as is. There, an
`exclude:` list in `_config.yml` would have no effect, and a `_tooling/` folder would be published too. The tools are
therefore kept out of `main`, in an orphan branch, `tooling`: `tools/`, `docs/`, `requirements.txt`, `README.md`.
GitHub Pages never serves that branch.

Why not turn Jekyll back on, with `_config.yml` and `exclude: [tools, docs, requirements.txt, README.md]`? Jekyll would
then build every page of the site, including GitHub's default plugins. That build cannot be checked on this Mac
(Jekyll is not installed). The branch keeps the published files byte-identical, with nothing to verify.

Set up once, next to the site's working tree:

```sh
cd ~/Downloads/alifo-site
git worktree add ../alifo-site-tooling tooling        # the branch, checked out in ../alifo-site-tooling
cd ../alifo-site-tooling
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt     # Pillow only; .venv/ is ignored by git
```

Run from `~/Downloads/alifo-site-tooling`:

```sh
.venv/bin/python tools/make_site.py      # Extracto's pages
.venv/bin/python tools/make_home.py      # the homepage's app cards
```

The scripts write into the site's working tree. That is `$ALIFO_SITE` if set, otherwise the `alifo-site` folder next
to this worktree; they stop if that folder has no `CNAME`. Then commit in the site's working tree (`main`), and the
scripts in this one (`tooling`). Push both: `git push origin main tooling`.

Both scripts are idempotent. On 2026-11-01, with this environment, they regenerated `main` with 0 changes.

### After a push: the tools must not be online

```sh
for u in tools/make_site.py tools/make_home.py docs/SITE.md requirements.txt README.md; do
  printf "%s %s\n" "$(curl -s -o /dev/null -w '%{http_code}' https://alifo.app/$u)" "$u"
done                                   # expected: 404 for each
```

No personal path in the published files: `cd ~/Downloads/alifo-site && grep -rl "/Users/" --exclude-dir=.git . | wc -l`
(expected 0; on 2026-11-01: 0, text and binary files).

| Page | Source |
|---|---|
| `/extracto/`, `/extracto/fr/`, `/extracto/es/` | `tools/make_site.py` (texts in its `T` dictionary) |
| `/extracto/support/`, `/extracto/privacy/` | content written by hand; header, footer and styles rewritten by `make_site.py` |
| `/extracto/img/shots/<lang>/` | Extracto's App Store screenshots (`~/Developer/Extracto/captures/appstore`), WebP + PNG at 640 / 1280 / 1920 px |
| `/extracto/img/og-<lang>.png` | 1200 × 630 share image from "Tables straight to Excel" |
| `/sitemap.xml`, `/robots.txt` | `make_site.py` |
| homepage app cards | `tools/make_home.py`: rewrites the cards between `<h2>Apps</h2>` and the footer of `index.html`, and `assets/img/apps/` |

Regenerate Extracto's pages after new screenshots with `tools/make_site.py`.

### Homepage cards (`tools/make_home.py`)

Each card has the app's icon, its name, a one-line tagline and a 16:10 visual. Styles: `.app-card-*` in
`assets/style.css`. Sources:

| App | Icon | Visual |
|---|---|---|
| AfterShot | neutral placeholder: the initial on its page's colours (no project on this Mac) | icon panel |
| Alwah | `~/Developer/Lemseed/App/Resources/Assets.xcassets/AppIcon.appiconset` | `~/Developer/Lemseed/captures/appstore/mac-en/01-msid.png` |
| Extracto | `~/Developer/Extracto/Extracto/Resources/Assets.xcassets/AppIcon.appiconset` | `~/Developer/Extracto/captures/appstore/mac-en/1-tables.png` |
| KeyToons | `~/Developer/KeyToons/Resources/Assets.xcassets/AppIcon.appiconset`, placed on the macOS icon grid (the source is a full square) | `~/Downloads/keytoons_shot_1_duck.png` (icon panel if absent) |

To change an icon or a visual, edit `APPS` in the script and run it again.

Principles: no script (only a JSON-LD data block), no tracker, no external font (system font), CSS in each page,
light and dark (`prefers-color-scheme`), images lazy-loaded except the first one.

## The Mac App Store link (to do at launch)

Until the app is live, `APP_STORE_URL = None` in `tools/make_site.py`: the pages say "Coming soon on the Mac App Store"
(plain text). Apple's badge is not shown, because it must link to the app's App Store page.

At launch:
1. Set `APP_STORE_URL` to the product page, e.g. `"https://apps.apple.com/app/id0000000000"` (App Store Connect ›
   App Information › Apple ID).
2. Run `tools/make_site.py`.

The official badge then replaces the text in the hero and in the final call. It is black on light pages and white on
dark ones, in the page's language. The badges are in `extracto/img/badges/`. They were downloaded unmodified on
2026-11-01 from Apple's marketing tools, `https://toolbox.marketingtools.apple.com/api/v2/badges/download-on-the-mac-app-store/<black|white>/<en-us|fr-fr|es-es>`
(the older host, tools.applemarketingtools.com, no longer resolves). They are SVG, 156 × 40, shown at 54 px high
(48 px on phones).

## Figures on the page

- **17 languages:** `docs/LANGUAGES.md` in the Extracto repository, section 3.
- **6 MB:** installed size of the universal Release build (arm64 + x86_64), measured on 2026-11-01 with
  `du -sk` = 6068 KB. It is 1.96 MB zipped. The App Store's download size will be shown in App Store Connect after
  upload: update the figure if it differs. The "2.4 MB" of older notes was an earlier archive.
- **The price of Pro** is never written on the site ("One-time purchase on the Mac App Store").

## Checks (2026-11-01)

The check tools stay in the Extracto repository (check_site.py needs only Python's standard library).

1. Serve the site from its working tree (`~/Downloads/alifo-site`): `python3 -m http.server 8000`.
2. Links and hreflang: `python3 ~/Developer/Extracto/Tools/check_site.py http://127.0.0.1:8000 - / /extracto/ /extracto/fr/ /extracto/es/ /extracto/support/ /extracto/privacy/ /aftershot/ /alwah/ /keytoons/`.
   Result: 136 URLs checked on 9 pages, 0 failures. hreflang is reciprocal and there is no script other than JSON-LD.
3. Renders: in `~/Developer/Extracto`, `swiftc -O Tools/site_shots.swift -o Tools/ocr-bench/out/site_shots`, then
   `site_shots <url> <width> <height> <light|dark> <viewport|full> <out.png>` (WebKit, no cache).

Requests and weight are counted from the server log while WebKit renders. "First display" is the viewport only;
"whole page" is scrolled to the end. Retina, light mode.

| Page | Desktop 1440: first display | Desktop: whole page | Phone 390: first display | Phone: whole page |
|---|---|---|---|---|
| /extracto/ | 4 requests, 151 KB | 9, 625 KB | 5, 183 KB | 9, 413 KB |
| /extracto/fr/ | 4, 175 KB | 9, 671 KB | 5, 206 KB | 9, 445 KB |
| /extracto/es/ | 4, 168 KB | 9, 652 KB | 5, 195 KB | 9, 431 KB |
| /extracto/support/ | 2, 18 KB | 2, 18 KB | 2, 18 KB | 2, 18 KB |
| /extracto/privacy/ | 2, 17 KB | 2, 17 KB | 2, 17 KB | 2, 17 KB |
| / (homepage) | 4, 49 KB | 4, 49 KB | 4, 49 KB | 4, 49 KB |

Page captures for review: `~/Developer/Extracto/captures/site/` (not in git, 41 MB). They cover `extracto-<en|fr|es>-<desktop|mobile>-<light|dark>.png`,
the homepage, Support and Privacy.
