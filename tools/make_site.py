"""Generate the Extracto pages of alifo.app (GitHub Pages repository, default ~/Downloads/alifo-site).

Writes /extracto/ (English), /extracto/fr/, /extracto/es/, their images (WebP + PNG fallback, 640 / 1280 / 1920 px,
from captures/appstore), the 1200 × 630 share images, the Support and Privacy pages' header and footer, sitemap.xml
and robots.txt. No script, no tracker, no external font: CSS in each page, system font.

The Mac App Store link: while APP_STORE_URL is None the pages say "Coming soon on the Mac App Store" (plain text, no
badge: Apple's badge must link to the app's App Store page). Once the app is live, set APP_STORE_URL to its product
page (https://apps.apple.com/app/id…) and run again: the official badge (extracto/img/badges, downloaded unmodified
from Apple's marketing tools, black on light, white on dark) appears and links there. See docs/SITE.md.

Run from the tooling worktree (branch "tooling"), with its own environment (docs/SITE.md):
  .venv/bin/python tools/make_site.py
"""
import html, json, os, re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter



def site_dir():
    """The site's working tree (branch main): $ALIFO_SITE, else the alifo-site folder next to this tooling worktree."""
    env = os.environ.get("ALIFO_SITE")
    site = Path(env).expanduser() if env else Path(__file__).resolve().parents[2] / "alifo-site"
    if not (site / "CNAME").exists():
        raise SystemExit(f"not the site's working tree: {site} (set ALIFO_SITE)")
    return site


SITE = site_dir()
EXTRACTO = Path.home() / "Developer" / "Extracto"              # screenshots and icon are read from the app's repository
SHOTS = EXTRACTO / "captures" / "appstore"
ICON = EXTRACTO / "Extracto" / "Resources" / "Assets.xcassets" / "AppIcon.appiconset" / "icon_512x512@2x.png"
BASE = "https://alifo.app"
APP_STORE_URL = None            # set when the app is live, e.g. "https://apps.apple.com/app/id0000000000"
WIDTHS = [640, 1280, 1920]
NAMES = ["1-tables", "2-text", "3-languages", "4-batch", "5-export", "6-private"]
LANGS = ["en", "fr", "es"]
PATH = {"en": "/extracto/", "fr": "/extracto/fr/", "es": "/extracto/es/"}
BADGE_LOCALE = {"en": "en-us", "fr": "fr-fr", "es": "es-es"}
LASTMOD = "2026-11-01"

# The 17 validated languages (docs/LANGUAGES.md), each in its own language.
VALIDATED = [("en", "English"), ("fr", "Français"), ("es", "Español"), ("de", "Deutsch"), ("it", "Italiano"),
             ("pt", "Português"), ("pl", "Polski"), ("tr", "Türkçe"), ("vi", "Tiếng Việt"), ("ru", "Русский"),
             ("uk", "Українська"), ("ar", "العربية"), ("th", "ไทย"), ("ko", "한국어"), ("ja", "日本語"),
             ("zh-Hans", "简体中文"), ("zh-Hant", "繁體中文")]

T = {
    "en": {
        "title": "Extracto — PDF to Excel on Mac, offline OCR for text and tables",
        "description": "Extract text from images and PDFs on your Mac and turn tables into Excel. Offline OCR in 17 "
                       "languages: nothing leaves your Mac. Text is free.",
        "nav": ["Features", "Pricing", "FAQ", "Support"],
        "langs_label": "Language",
        "h1": "Drop any PDF or image. Get text, tables and data.",
        "promise": "Nothing leaves your Mac.",
        "soon": "Coming soon on the Mac App Store",
        "badge_alt": "Download on the Mac App Store",
        "hero_alt": "Extracto on a Mac: a stock count PDF on the left, its table extracted on the right, and the "
                    "Excel file Extracto wrote, with the same rows and numbers.",
        "stats": ["17 languages", "Works offline", "6 MB", "One-time purchase"],
        "features_label": "Features",
        "features": [
            ("Tables straight to Excel.",
             "Extracto finds the rows and columns of a table in a PDF, a scan or a photo, and writes a real .xlsx: one "
             "value per cell, numbers stored as numbers. CSV and Word too.", "Pro",
             "A table in a PDF, the same table in Extracto's Tables tab, and the .xlsx file it produced."),
            ("Text is free. Forever.",
             "Every word, in reading order, columns included. The page and the text side by side: click a paragraph on "
             "one side and it lights up on the other. Copy it all with ⇧⌘C. No page limit, no account.", "Free",
             "A two-column document on the left and its extracted text on the right, the same paragraph highlighted "
             "on both sides."),
            ("Reads 17 languages.",
             "Latin and Cyrillic scripts, Arabic from right to left, Chinese, Japanese, Korean and Thai. Each language "
             "was measured on PDFs, scans, photos and tables before being listed. A page in a script Extracto can't "
             "read yet says so, instead of showing wrong text.", "Free",
             "Three pages read by Extracto, in Arabic, Chinese and Japanese, each with its extracted text, and the "
             "names of the 17 languages."),
            ("A whole folder in one go.",
             "Drop a folder: every PDF and image inside is read, each with its status in the list. Export All writes "
             "one file per document into the folder you choose.", "Free",
             "Eight documents in Extracto's list, all marked done, and the folder of Word files written by Export All."),
            ("Copy, or export to Word.",
             "Word, Markdown, plain text and JSON for the text; Excel and CSV for tables. Right-to-left documents keep "
             "their direction in Word and Excel.", "Free",
             "Extracto's Export menu open, with Word, Excel, CSV, Markdown, Plain Text and JSON, next to the Word "
             "document it wrote."),
            ("Nothing leaves your Mac.",
             "Text recognition runs on your Mac with Apple's on-device frameworks. No account, no server, no "
             "analytics, and Extracto has no network access: it works offline.", "Free",
             "A photo of a page read by Extracto on the Mac, with a padlock and the words Works offline, No upload."),
        ],
        "compare_label": "macOS alone vs Extracto",
        "compare_intro": "macOS already copies text from images with Live Text. Extracto adds what comes after: "
                         "tables, folders, reading order and files.",
        "compare_head": ["", "macOS alone", "Extracto"],
        "compare": [
            ("Copy the text of an image", "Yes, with Live Text", "Yes"),
            ("Save a table as an Excel file (.xlsx)", "Not built in", "Yes (Pro)"),
            ("A whole folder in one go", "With a shortcut you build", "Yes, drop the folder"),
            ("Multi-column pages in reading order", "Depends on your selection", "Yes, column by column"),
            ("Export to Word, CSV, JSON", "Copy, then paste into an app", "Yes, one click"),
        ],
        "pricing_label": "Pricing",
        "free_name": "Free", "free_price": "Free, with no limit",
        "free_items": ["Unlimited text: pages, files and folders", "Copy All in reading order",
                       "Text exports: Word, Markdown, plain text, JSON", "A preview of every table: header and 3 rows"],
        "pro_name": "Extracto Pro", "pro_price": "One-time purchase on the Mac App Store",
        "pro_items": ["Tables straight to Excel and CSV", "Real tables in Word and JSON exports",
                      "One purchase, no subscription", "Shared with your family (Family Sharing)"],
        "languages_label": "Languages",
        "languages_intro": "Measured before being listed. Interface in English, French and Spanish.",
        "faq_label": "FAQ",
        "faq": [
            ("Is Extracto free?",
             "Yes for text: read any number of pages, files and folders, copy everything, and export the text to Word, "
             "Markdown, plain text and JSON, with no limit and no account. Extracto Pro, a one-time purchase, unlocks "
             "tables."),
            ("Are my documents sent anywhere?",
             "No. Text recognition runs on your Mac with Apple's on-device frameworks (Vision and PDFKit). Extracto has "
             "no network access: your documents, their text and their tables never leave your Mac. See the "
             "<a href=\"/extracto/privacy/\">privacy policy</a>."),
            ("Which languages does it read?",
             "17: English, French, Spanish, German, Italian, Portuguese, Polish, Turkish, Vietnamese, Russian, "
             "Ukrainian, Arabic, Thai, Korean, Japanese and Chinese (Simplified and Traditional). A scan or a photo in a "
             "script it can't read yet, such as Hebrew, Greek or Hindi, shows a clear message instead of wrong text."),
            ("How does it handle tables?",
             "It finds rows and columns in PDFs, scans and photos, with or without ruling lines, and keeps numbers as "
             "numbers in Excel. Without Pro you see each table's header and first three rows. Very irregular tables, "
             "or merged cells, may come out as text."),
            ("Does it work on Intel Macs?",
             "Yes. Extracto runs on Apple silicon and Intel Macs with macOS 14 Sonoma or later."),
            ("Which files can I open?",
             "PDF, PNG, JPEG, HEIC, TIFF and WebP. Drop them, choose them or paste them with ⌘V. A password-protected "
             "PDF needs to be unlocked in Preview first."),
            ("Can I use Pro on several Macs, or share it with my family?",
             "Yes. Extracto Pro works on every Mac signed in with your Apple Account (Settings › Extracto Pro › Restore "
             "Purchases), and is shared with your family through Family Sharing."),
            ("Can I get a refund?",
             "Purchases are made through Apple, so refunds are too: request one at "
             "<a href=\"https://reportaproblem.apple.com\">reportaproblem.apple.com</a>."),
        ],
        "final_title": "Text, tables and data from any PDF or image.",
        "final_text": "Read on your Mac, in 17 languages. Nothing leaves your Mac.",
        "footer": ["Support", "Privacy"],
        "footer_note": "This page loads no scripts, no external fonts and no trackers.",
        "privacy_link": "Privacy",
    },
    "fr": {
        "title": "Extracto — PDF vers Excel sur Mac, OCR hors ligne pour le texte et les tableaux",
        "description": "Extrayez le texte d'une image ou d'un PDF sur votre Mac et transformez les tableaux en Excel. "
                       "OCR hors ligne en 17 langues : rien ne quitte votre Mac. Le texte est gratuit.",
        "nav": ["Fonctions", "Tarifs", "FAQ", "Assistance"],
        "langs_label": "Langue",
        "h1": "Déposez un PDF ou une image. Obtenez texte, tableaux et données.",
        "promise": "Rien ne quitte votre Mac.",
        "soon": "Bientôt sur le Mac App Store",
        "badge_alt": "Télécharger dans le Mac App Store",
        "hero_alt": "Extracto sur un Mac : un PDF d'inventaire à gauche, son tableau extrait à droite, et le fichier "
                    "Excel produit par Extracto, avec les mêmes lignes et les mêmes nombres.",
        "stats": ["17 langues", "Fonctionne hors ligne", "6 Mo", "Achat unique"],
        "features_label": "Fonctions",
        "features": [
            ("Vos tableaux, direct dans Excel.",
             "Extracto repère les lignes et les colonnes d'un tableau dans un PDF, un scan ou une photo, et écrit un "
             "vrai .xlsx : une valeur par cellule, des nombres enregistrés comme des nombres. Aussi en CSV et Word.",
             "Pro", "Un tableau dans un PDF, le même tableau dans l'onglet Tableaux d'Extracto, et le fichier .xlsx "
                    "produit."),
            ("Le texte est gratuit. Pour toujours.",
             "Chaque mot, dans l'ordre de lecture, colonnes comprises. La page et le texte côte à côte : cliquez sur un "
             "paragraphe d'un côté, il s'allume de l'autre. Tout copier avec ⇧⌘C. Sans limite de pages, sans compte.",
             "Gratuit", "Un document sur deux colonnes à gauche et son texte extrait à droite, le même paragraphe "
                        "surligné des deux côtés."),
            ("Lit 17 langues.",
             "Alphabets latin et cyrillique, arabe de droite à gauche, chinois, japonais, coréen et thaï. Chaque langue "
             "a été mesurée sur des PDF, des scans, des photos et des tableaux avant d'être annoncée. Une page dans une "
             "écriture qu'Extracto ne lit pas encore le dit, au lieu d'afficher un texte faux.", "Gratuit",
             "Trois pages lues par Extracto, en arabe, chinois et japonais, chacune avec son texte extrait, et le nom "
             "des 17 langues."),
            ("Un dossier entier d'un coup.",
             "Déposez un dossier : chaque PDF et chaque image qu'il contient est lu, avec son état dans la liste. Tout "
             "exporter écrit un fichier par document dans le dossier de votre choix.", "Gratuit",
             "Huit documents dans la liste d'Extracto, tous terminés, et le dossier de fichiers Word écrit par Tout "
             "exporter."),
            ("Copiez, ou exportez vers Word.",
             "Word, Markdown, texte brut et JSON pour le texte ; Excel et CSV pour les tableaux. Les documents de "
             "droite à gauche gardent leur sens dans Word et Excel.", "Gratuit",
             "Le menu Exporter d'Extracto ouvert, avec Word, Excel, CSV, Markdown, Texte brut et JSON, à côté du "
             "document Word produit."),
            ("Rien ne quitte votre Mac.",
             "La reconnaissance du texte se fait sur votre Mac, avec les outils intégrés d'Apple. Pas de compte, pas de "
             "serveur, pas de mesure d'audience, et Extracto n'a pas accès au réseau : il fonctionne hors ligne.",
             "Gratuit", "La photo d'une page lue par Extracto sur le Mac, avec un cadenas et les mots Fonctionne hors "
                        "ligne, Aucun envoi."),
        ],
        "compare_label": "macOS seul ou Extracto",
        "compare_intro": "macOS copie déjà le texte des images avec Texte en direct. Extracto ajoute la suite : "
                         "tableaux, dossiers, ordre de lecture et fichiers.",
        "compare_head": ["", "macOS seul", "Extracto"],
        "compare": [
            ("Copier le texte d'une image", "Oui, avec Texte en direct", "Oui"),
            ("Enregistrer un tableau en fichier Excel (.xlsx)", "Non intégré", "Oui (Pro)"),
            ("Un dossier entier d'un coup", "Avec un raccourci à créer", "Oui, déposez le dossier"),
            ("Pages sur plusieurs colonnes, dans l'ordre de lecture", "Selon votre sélection", "Oui, colonne par colonne"),
            ("Export Word, CSV, JSON", "Copier, puis coller dans une app", "Oui, en un clic"),
        ],
        "pricing_label": "Tarifs",
        "free_name": "Gratuit", "free_price": "Gratuit, sans limite",
        "free_items": ["Texte illimité : pages, fichiers et dossiers", "Tout copier dans l'ordre de lecture",
                       "Exports du texte : Word, Markdown, texte brut, JSON",
                       "Un aperçu de chaque tableau : en-tête et 3 lignes"],
        "pro_name": "Extracto Pro", "pro_price": "Achat unique sur le Mac App Store",
        "pro_items": ["Tableaux direct dans Excel et CSV", "De vrais tableaux dans les exports Word et JSON",
                      "Un seul achat, sans abonnement", "Partagé avec votre famille (Partage familial)"],
        "languages_label": "Langues",
        "languages_intro": "Mesurées avant d'être annoncées. Interface en français, anglais et espagnol.",
        "faq_label": "FAQ",
        "faq": [
            ("Extracto est-il gratuit ?",
             "Oui pour le texte : lisez autant de pages, de fichiers et de dossiers que vous voulez, copiez tout et "
             "exportez le texte en Word, Markdown, texte brut et JSON, sans limite et sans compte. Extracto Pro, un "
             "achat unique, débloque les tableaux."),
            ("Mes documents sont-ils envoyés quelque part ?",
             "Non. La reconnaissance du texte se fait sur votre Mac avec les outils intégrés d'Apple (Vision et "
             "PDFKit). Extracto n'a pas accès au réseau : vos documents, leur texte et leurs tableaux ne quittent "
             "jamais votre Mac. Voir la <a href=\"/extracto/privacy/#fr\">politique de confidentialité</a>."),
            ("Quelles langues lit-il ?",
             "17 : français, anglais, espagnol, allemand, italien, portugais, polonais, turc, vietnamien, russe, "
             "ukrainien, arabe, thaï, coréen, japonais et chinois (simplifié et traditionnel). Un scan ou une photo dans "
             "une écriture qu'il ne lit pas encore, comme l'hébreu, le grec ou l'hindi, affiche un message clair au "
             "lieu d'un texte faux."),
            ("Comment gère-t-il les tableaux ?",
             "Il repère les lignes et les colonnes dans les PDF, les scans et les photos, avec ou sans filets, et garde "
             "les nombres comme des nombres dans Excel. Sans Pro, vous voyez l'en-tête et les trois premières lignes de "
             "chaque tableau. Les tableaux très irréguliers, ou à cellules fusionnées, peuvent sortir en texte."),
            ("Fonctionne-t-il sur les Mac Intel ?",
             "Oui. Extracto fonctionne sur les Mac Apple silicon et Intel, sous macOS 14 Sonoma ou ultérieur."),
            ("Quels fichiers puis-je ouvrir ?",
             "PDF, PNG, JPEG, HEIC, TIFF et WebP. Déposez-les, choisissez-les ou collez-les avec ⌘V. Un PDF protégé par "
             "un mot de passe doit d'abord être déverrouillé dans Aperçu."),
            ("Puis-je utiliser Pro sur plusieurs Mac, ou le partager avec ma famille ?",
             "Oui. Extracto Pro fonctionne sur chaque Mac connecté avec votre compte Apple (Réglages › Extracto Pro › "
             "Restaurer les achats), et il est partagé avec votre famille grâce au Partage familial."),
            ("Puis-je être remboursé ?",
             "Les achats passent par Apple, les remboursements aussi : faites la demande sur "
             "<a href=\"https://reportaproblem.apple.com\">reportaproblem.apple.com</a>."),
        ],
        "final_title": "Le texte, les tableaux et les données de n'importe quel PDF ou image.",
        "final_text": "Lus sur votre Mac, en 17 langues. Rien ne quitte votre Mac.",
        "footer": ["Assistance", "Confidentialité"],
        "footer_note": "Cette page ne charge aucun script, aucune police externe et aucun traceur.",
        "privacy_link": "Confidentialité",
    },
    "es": {
        "title": "Extracto — PDF a Excel en Mac, OCR sin conexión para texto y tablas",
        "description": "Extrae el texto de imágenes y PDF en tu Mac y convierte las tablas en Excel. OCR sin conexión "
                       "en 17 idiomas: nada sale de tu Mac. El texto es gratis.",
        "nav": ["Funciones", "Precio", "FAQ", "Soporte"],
        "langs_label": "Idioma",
        "h1": "Suelta un PDF o una imagen. Obtén texto, tablas y datos.",
        "promise": "Nada sale de tu Mac.",
        "soon": "Próximamente en el Mac App Store",
        "badge_alt": "Descárgalo en el Mac App Store",
        "hero_alt": "Extracto en un Mac: un PDF de inventario a la izquierda, su tabla extraída a la derecha y el "
                    "archivo de Excel que escribió Extracto, con las mismas filas y números.",
        "stats": ["17 idiomas", "Funciona sin conexión", "6 MB", "Compra única"],
        "features_label": "Funciones",
        "features": [
            ("Tus tablas, directo a Excel.",
             "Extracto encuentra las filas y columnas de una tabla en un PDF, un escaneo o una foto, y escribe un .xlsx "
             "de verdad: un valor por celda, números guardados como números. También CSV y Word.", "Pro",
             "Una tabla en un PDF, la misma tabla en la pestaña Tablas de Extracto y el archivo .xlsx que produjo."),
            ("El texto es gratis. Para siempre.",
             "Cada palabra, en orden de lectura, con columnas incluidas. La página y el texto lado a lado: haz clic en "
             "un párrafo de un lado y se ilumina en el otro. Cópialo todo con ⇧⌘C. Sin límite de páginas, sin cuenta.",
             "Gratis", "Un documento a dos columnas a la izquierda y su texto extraído a la derecha, con el mismo "
                       "párrafo resaltado en ambos lados."),
            ("Lee 17 idiomas.",
             "Alfabetos latino y cirílico, árabe de derecha a izquierda, chino, japonés, coreano y tailandés. Cada "
             "idioma se midió en PDF, escaneos, fotos y tablas antes de anunciarlo. Una página en una escritura que "
             "Extracto aún no lee lo indica, en lugar de mostrar texto erróneo.", "Gratis",
             "Tres páginas leídas por Extracto, en árabe, chino y japonés, cada una con su texto extraído, y los "
             "nombres de los 17 idiomas."),
            ("Una carpeta entera de una vez.",
             "Suelta una carpeta: cada PDF e imagen que contiene se lee, con su estado en la lista. Exportar todo "
             "escribe un archivo por documento en la carpeta que elijas.", "Gratis",
             "Ocho documentos en la lista de Extracto, todos terminados, y la carpeta de archivos de Word escrita por "
             "Exportar todo."),
            ("Copia o exporta a Word.",
             "Word, Markdown, texto sin formato y JSON para el texto; Excel y CSV para las tablas. Los documentos de "
             "derecha a izquierda conservan su dirección en Word y Excel.", "Gratis",
             "El menú Exportar de Extracto abierto, con Word, Excel, CSV, Markdown, Texto sin formato y JSON, junto al "
             "documento de Word que escribió."),
            ("Nada sale de tu Mac.",
             "El reconocimiento de texto se hace en tu Mac, con las herramientas integradas de Apple. Sin cuenta, sin "
             "servidor, sin analítica, y Extracto no tiene acceso a la red: funciona sin conexión.", "Gratis",
             "La foto de una página leída por Extracto en el Mac, con un candado y las palabras Funciona sin conexión, "
             "Sin subidas."),
        ],
        "compare_label": "macOS solo o Extracto",
        "compare_intro": "macOS ya copia el texto de las imágenes con Texto en vivo. Extracto añade lo que viene "
                         "después: tablas, carpetas, orden de lectura y archivos.",
        "compare_head": ["", "macOS solo", "Extracto"],
        "compare": [
            ("Copiar el texto de una imagen", "Sí, con Texto en vivo", "Sí"),
            ("Guardar una tabla como archivo de Excel (.xlsx)", "No integrado", "Sí (Pro)"),
            ("Una carpeta entera de una vez", "Con un atajo que creas tú", "Sí, suelta la carpeta"),
            ("Páginas a varias columnas, en orden de lectura", "Según tu selección", "Sí, columna por columna"),
            ("Exportar a Word, CSV, JSON", "Copiar y pegar en una app", "Sí, con un clic"),
        ],
        "pricing_label": "Precio",
        "free_name": "Gratis", "free_price": "Gratis, sin límite",
        "free_items": ["Texto ilimitado: páginas, archivos y carpetas", "Copiar todo en orden de lectura",
                       "Exportar el texto: Word, Markdown, texto sin formato, JSON",
                       "Una vista previa de cada tabla: encabezado y 3 filas"],
        "pro_name": "Extracto Pro", "pro_price": "Compra única en el Mac App Store",
        "pro_items": ["Tablas directo a Excel y CSV", "Tablas reales en las exportaciones de Word y JSON",
                      "Una sola compra, sin suscripción", "Compartido con tu familia (En familia)"],
        "languages_label": "Idiomas",
        "languages_intro": "Medidos antes de anunciarlos. Interfaz en español, inglés y francés.",
        "faq_label": "FAQ",
        "faq": [
            ("¿Extracto es gratis?",
             "Sí para el texto: lee todas las páginas, archivos y carpetas que quieras, cópialo todo y exporta el texto "
             "a Word, Markdown, texto sin formato y JSON, sin límite y sin cuenta. Extracto Pro, una compra única, "
             "desbloquea las tablas."),
            ("¿Se envían mis documentos a algún sitio?",
             "No. El reconocimiento de texto se hace en tu Mac con las herramientas integradas de Apple (Vision y "
             "PDFKit). Extracto no tiene acceso a la red: tus documentos, su texto y sus tablas nunca salen de tu Mac. "
             "Consulta la <a href=\"/extracto/privacy/#es\">política de privacidad</a>."),
            ("¿Qué idiomas lee?",
             "17: español, inglés, francés, alemán, italiano, portugués, polaco, turco, vietnamita, ruso, ucraniano, "
             "árabe, tailandés, coreano, japonés y chino (simplificado y tradicional). Un escaneo o una foto en una "
             "escritura que aún no lee, como el hebreo, el griego o el hindi, muestra un mensaje claro en lugar de "
             "texto erróneo."),
            ("¿Cómo trata las tablas?",
             "Encuentra filas y columnas en PDF, escaneos y fotos, con o sin líneas, y mantiene los números como "
             "números en Excel. Sin Pro ves el encabezado y las tres primeras filas de cada tabla. Las tablas muy "
             "irregulares, o con celdas combinadas, pueden salir como texto."),
            ("¿Funciona en Mac con Intel?",
             "Sí. Extracto funciona en Mac con Apple silicon e Intel, con macOS 14 Sonoma o posterior."),
            ("¿Qué archivos puedo abrir?",
             "PDF, PNG, JPEG, HEIC, TIFF y WebP. Suéltalos, elígelos o pégalos con ⌘V. Un PDF protegido con contraseña "
             "debe desbloquearse antes en Vista Previa."),
            ("¿Puedo usar Pro en varios Mac o compartirlo con mi familia?",
             "Sí. Extracto Pro funciona en cada Mac con tu cuenta de Apple (Ajustes › Extracto Pro › Restaurar "
             "compras) y se comparte con tu familia mediante En familia."),
            ("¿Puedo pedir un reembolso?",
             "Las compras se hacen a través de Apple, y los reembolsos también: solicítalo en "
             "<a href=\"https://reportaproblem.apple.com\">reportaproblem.apple.com</a>."),
        ],
        "final_title": "Texto, tablas y datos de cualquier PDF o imagen.",
        "final_text": "Leídos en tu Mac, en 17 idiomas. Nada sale de tu Mac.",
        "footer": ["Soporte", "Privacidad"],
        "footer_note": "Esta página no carga scripts, fuentes externas ni rastreadores.",
        "privacy_link": "Privacidad",
    },
}

CSS = """
:root {
  color-scheme: light dark;
  --bg: #f8f6f1; --surface: #ffffff; --surface-2: #eef3f2; --ink: #0f2430; --muted: #4c606b; --line: #dde4e4;
  --accent: #2bb3a6; --accent-ink: #0b6f69; --on-accent: #ffffff;
  --hero-1: #0a3e42; --hero-2: #09122c; --hero-ink: #ffffff; --hero-muted: #b2cdd6;
  --shadow: 0 18px 50px rgba(9, 30, 44, .22), 0 2px 8px rgba(9, 30, 44, .10);
  --sans: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #08121f; --surface: #0f1d2a; --surface-2: #122634; --ink: #e9f2f2; --muted: #a6b9c0; --line: #1f3341;
    --accent-ink: #5fd0c4; --on-accent: #062226;
    --shadow: 0 18px 50px rgba(0, 0, 0, .55), 0 2px 8px rgba(0, 0, 0, .35);
  }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 17px/1.6 var(--sans); }
img { max-width: 100%; height: auto; display: block; }
a { color: var(--accent-ink); }
.container { max-width: 1180px; margin: 0 auto; padding: 0 24px; }
.skip { position: absolute; left: -999px; }
.skip:focus { left: 16px; top: 12px; background: var(--surface); padding: 8px 12px; border-radius: 8px; z-index: 2; }

/* Header */
.site-header { background: var(--hero-1); color: var(--hero-ink); }
.site-header .container { display: flex; align-items: center; gap: 22px; flex-wrap: wrap; padding-top: 14px; padding-bottom: 14px; }
.brand { display: flex; align-items: center; gap: 10px; color: var(--hero-ink); text-decoration: none; font-weight: 700; font-size: 19px; }
.brand img { width: 34px; height: 34px; }
.nav { display: flex; gap: 20px; margin-left: auto; font-size: 15px; }
.nav a, .langs a { color: var(--hero-muted); text-decoration: none; }
.nav a:hover, .langs a:hover, .nav a:focus-visible, .langs a:focus-visible { color: var(--hero-ink); }
.langs { display: flex; gap: 2px; font-size: 14px; border: 1px solid rgba(255,255,255,.22); border-radius: 999px; padding: 3px; }
.langs a { padding: 2px 10px; border-radius: 999px; }
.langs a[aria-current="true"] { background: rgba(255,255,255,.16); color: var(--hero-ink); }

/* Hero */
.hero { background: linear-gradient(170deg, var(--hero-1) 0%, var(--hero-2) 100%); color: var(--hero-ink); text-align: center; padding: 56px 0 0; overflow: hidden; }
.hero h1 { font-size: clamp(34px, 5.2vw, 62px); line-height: 1.07; letter-spacing: -.025em; font-weight: 750; margin: 0 auto 14px; max-width: 19ch; text-wrap: balance; }
.hero .promise { font-size: clamp(19px, 2.2vw, 25px); color: var(--hero-muted); margin: 0 0 30px; }
.store { display: flex; justify-content: center; align-items: center; gap: 14px; flex-wrap: wrap; margin-bottom: 44px; }
.store .badge img { height: 54px; width: auto; }
.soon { display: inline-block; border: 1px solid rgba(255,255,255,.35); border-radius: 12px; padding: 12px 20px; font-weight: 600; font-size: 17px; color: var(--hero-ink); }
.hero picture img { margin: 0 auto; border-radius: 14px 14px 0 0; box-shadow: 0 -10px 60px rgba(0,0,0,.35); width: min(1100px, 100%); }

/* Stats */
.stats { background: var(--surface); border-bottom: 1px solid var(--line); }
.stats ul { list-style: none; margin: 0 auto; padding: 22px 24px; max-width: 1180px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; text-align: center; }
.stats li { font-weight: 650; font-size: 18px; }
.stats li + li { border-left: 1px solid var(--line); }

/* Sections */
section { padding: 84px 0; }
.eyebrow { font-size: 14px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--accent-ink); margin: 0 0 10px; }
h2 { font-size: clamp(28px, 3.4vw, 42px); line-height: 1.12; letter-spacing: -.02em; margin: 0 0 16px; }
.intro { color: var(--muted); font-size: 19px; max-width: 62ch; margin: 0 0 36px; }
.feature { display: grid; grid-template-columns: 1.45fr 1fr; gap: 56px; align-items: center; padding: 44px 0; }
.feature.flip picture { order: 2; }
.feature picture img { border-radius: 14px; box-shadow: var(--shadow); }
.feature h3 { font-size: clamp(24px, 2.6vw, 34px); line-height: 1.15; letter-spacing: -.015em; margin: 0 0 12px; }
.feature p { color: var(--muted); margin: 0 0 14px; }
.tag { display: inline-block; font-size: 13px; font-weight: 700; letter-spacing: .04em; border-radius: 999px; padding: 3px 11px; background: var(--surface-2); color: var(--accent-ink); }
.alt-bg { background: var(--surface); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }

/* Comparison */
.table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); }
table { border-collapse: collapse; width: 100%; min-width: 560px; }
th, td { text-align: left; padding: 15px 18px; border-bottom: 1px solid var(--line); vertical-align: top; }
tr:last-child td { border-bottom: 0; }
thead th { font-size: 15px; color: var(--muted); }
td.yes { color: var(--accent-ink); font-weight: 650; }
td.no { color: var(--muted); }

/* Pricing */
.plans { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.plan { background: var(--surface); border: 1px solid var(--line); border-radius: 18px; padding: 30px 30px 26px; }
.plan.pro { border: 2px solid var(--accent); }
.plan h3 { margin: 0; font-size: 24px; }
.plan .price { color: var(--muted); margin: 4px 0 18px; font-weight: 600; }
.plan ul { margin: 0; padding: 0; list-style: none; }
.plan li { padding: 8px 0 8px 30px; position: relative; border-top: 1px solid var(--line); }
.plan li::before { content: ""; position: absolute; left: 4px; top: 15px; width: 12px; height: 7px; border-left: 2.5px solid var(--accent); border-bottom: 2.5px solid var(--accent); transform: rotate(-45deg); }

/* Languages */
.pills { display: flex; flex-wrap: wrap; gap: 10px; list-style: none; padding: 0; margin: 0; }
.pills li { border: 1px solid var(--line); background: var(--surface); border-radius: 999px; padding: 6px 16px; font-size: 17px; }

/* FAQ */
.faq details { border-bottom: 1px solid var(--line); padding: 4px 0; }
.faq summary { cursor: pointer; font-weight: 650; font-size: 19px; padding: 14px 0; list-style-position: outside; }
.faq details p { color: var(--muted); margin: 0 0 18px; max-width: 70ch; }

/* Final call */
.final { background: linear-gradient(170deg, var(--hero-1) 0%, var(--hero-2) 100%); color: var(--hero-ink); text-align: center; }
.final h2 { max-width: 22ch; margin: 0 auto 12px; }
.final p { color: var(--hero-muted); font-size: 20px; margin: 0 0 30px; }
.final .store { margin-bottom: 0; }

/* Footer */
.site-footer { padding: 30px 0 44px; color: var(--muted); font-size: 14.5px; }
.site-footer .container { display: flex; flex-wrap: wrap; gap: 6px 18px; }
.site-footer a { color: var(--muted); }
.site-footer .note { flex-basis: 100%; font-size: 13px; }

/* Support and privacy pages */
.doc { max-width: 760px; margin: 0 auto; padding: 54px 24px 20px; }
.doc h1 { font-size: clamp(32px, 4vw, 44px); letter-spacing: -.02em; line-height: 1.1; margin: 0 0 10px; }
.doc .lede { font-size: 20px; color: var(--muted); margin: 0 0 28px; }
.doc h2 { font-size: 14px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--accent-ink); margin: 42px 0 12px; }
.doc p, .doc dd { color: var(--muted); }
.doc dt { font-weight: 650; margin-top: 22px; }
.doc dd { margin: 6px 0 0; }
.contact { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 20px 22px; margin-bottom: 36px; }
.contact .label { font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--accent-ink); margin-bottom: 6px; }
.contact a { font-size: 19px; font-weight: 600; text-decoration: none; }
.contact .meta { font-size: 14px; color: var(--muted); margin-top: 6px; }

@media (max-width: 900px) {
  .feature { grid-template-columns: 1fr; gap: 26px; padding: 30px 0; }
  .feature.flip picture { order: 0; }
  .plans { grid-template-columns: 1fr; }
  .stats ul { grid-template-columns: repeat(2, 1fr); row-gap: 14px; }
  .stats li:nth-child(3) { border-left: 0; }
  section { padding: 60px 0; }
}
@media (max-width: 600px) {
  .nav { order: 3; margin-left: 0; width: 100%; justify-content: space-between; gap: 10px; font-size: 15px; }
  .langs { margin-left: auto; }
  .hero { padding-top: 38px; }
  .hero picture img { border-radius: 10px 10px 0 0; }
  .store .badge img { height: 48px; }
  body { font-size: 16px; }
  table { min-width: 0; font-size: 15px; }
  th, td { padding: 12px 10px; }
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
"""


# ---------------------------------------------------------------- images
def save_set(img, stem, widths=WIDTHS):
    """WebP and PNG at each width (Lanczos), into extracto/img/…"""
    out = SITE / "extracto" / "img"
    (out / stem).parent.mkdir(parents=True, exist_ok=True)
    for w in widths:
        im = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
        im.save(out / f"{stem}-{w}.webp", "WEBP", quality=80, method=6)
        im.save(out / f"{stem}-{w}.png", optimize=True)


def make_images():
    for lang in LANGS:
        for name in NAMES:
            save_set(Image.open(SHOTS / f"mac-{lang}" / f"{name}.png").convert("RGB"), f"shots/{lang}/{name}")
        og(lang)
    icon = Image.open(ICON).convert("RGBA")
    for s in (64, 128, 256):
        im = icon.resize((s, s), Image.LANCZOS)
        im.save(SITE / "extracto" / "img" / f"icon-{s}.png", optimize=True)
        im.save(SITE / "extracto" / "img" / f"icon-{s}.webp", "WEBP", quality=90, method=6)


def og(lang):
    """1200 × 630 share image from the "Tables straight to Excel" screenshot, on its own background colours."""
    shot = Image.open(SHOTS / f"mac-{lang}" / "1-tables.png").convert("RGB")
    h = 630
    w = round(shot.width * h / shot.height)
    small = shot.resize((w, h), Image.LANCZOS)
    canvas = Image.new("RGB", (1200, h))
    # The screenshot's left and right columns, stretched, so the extension matches its gradient.
    canvas.paste(small.crop((0, 0, 2, h)).resize(((1200 - w) // 2 + 2, h)), (0, 0))
    canvas.paste(small.crop((w - 2, 0, w, h)).resize((1200 - w - (1200 - w) // 2 + 2, h)), ((1200 - w) // 2 + w - 2, 0))
    canvas.paste(small, ((1200 - w) // 2, 0))
    canvas.save(SITE / "extracto" / "img" / f"og-{lang}.png", optimize=True)


# ---------------------------------------------------------------- HTML
def esc(s):
    return html.escape(s, quote=True)


def picture(stem, alt, sizes, eager=False):
    img = f"/extracto/img/{stem}"
    webp = ", ".join(f"{img}-{w}.webp {w}w" for w in WIDTHS)
    png = ", ".join(f"{img}-{w}.png {w}w" for w in WIDTHS)
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture><source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img src="{img}-1280.png" srcset="{png}" sizes="{sizes}" width="1280" height="800" alt="{esc(alt)}" {load}>'
            f'</picture>')


def store_cta(lang):
    t = T[lang]
    if APP_STORE_URL is None:
        # Not live yet: plain text, no badge (Apple's badge must link to the app's App Store page). See docs/SITE.md.
        return f'<div class="store"><span class="soon">{esc(t["soon"])}</span></div>'
    loc = BADGE_LOCALE[lang]
    return (f'<div class="store"><a class="badge" href="{APP_STORE_URL}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="/extracto/img/badges/mac-app-store-white-{loc}.svg">'
            f'<img src="/extracto/img/badges/mac-app-store-black-{loc}.svg" width="156" height="40" alt="{esc(t["badge_alt"])}">'
            f'</picture></a></div>')


def head(lang, title, description, path, alternates=True, og_image=True):
    links = ""
    if alternates:
        links = "".join(f'<link rel="alternate" hreflang="{l}" href="{BASE}{PATH[l]}">\n' for l in LANGS)
        links += f'<link rel="alternate" hreflang="x-default" href="{BASE}{PATH["en"]}">\n'
    share = ""
    if og_image:
        locale = {"en": "en_US", "fr": "fr_FR", "es": "es_ES"}[lang]
        share = (f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="Alifo">\n'
                 f'<meta property="og:title" content="{esc(title)}">\n<meta property="og:description" content="{esc(description)}">\n'
                 f'<meta property="og:url" content="{BASE}{path}">\n<meta property="og:locale" content="{locale}">\n'
                 f'<meta property="og:image" content="{BASE}/extracto/img/og-{lang}.png">\n'
                 f'<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
                 f'<meta property="og:image:alt" content="{esc(T[lang]["hero_alt"])}">\n'
                 f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="{esc(title)}">\n'
                 f'<meta name="twitter:description" content="{esc(description)}">\n'
                 f'<meta name="twitter:image" content="{BASE}/extracto/img/og-{lang}.png">\n')
    return (f'<!DOCTYPE html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{esc(title)}</title>\n<meta name="description" content="{esc(description)}">\n'
            f'<link rel="canonical" href="{BASE}{path}">\n{links}'
            f'<link rel="icon" type="image/png" href="/extracto/img/icon-64.png">\n'
            f'<link rel="apple-touch-icon" href="/extracto/img/icon-256.png">\n'
            f'<meta name="theme-color" content="#0a3e42">\n{share}'
            f'<style>{CSS}</style>\n')


def header(lang, current, home=PATH, anchors=True):
    """Icon, Extracto, Features · Pricing · FAQ · Support, and the language switch (to `home[lang]`)."""
    t = T[lang]
    base = PATH[lang]
    ids = ["features", "pricing", "faq"]
    nav = "".join(f'<a href="{"" if anchors else base}#{i}">{esc(n)}</a>' for i, n in zip(ids, t["nav"][:3]))
    nav += f'<a href="/extracto/support/">{esc(t["nav"][3])}</a>'
    langs = "".join(f'<a href="{home[l]}" hreflang="{l}" lang="{l}"{" aria-current=\"true\"" if l == current else ""}>{l.upper()}</a>'
                    for l in LANGS)
    skip = {"en": "Skip to content", "fr": "Aller au contenu", "es": "Ir al contenido"}[lang]
    return (f'<a class="skip" href="#main">{skip}</a>\n<header class="site-header"><div class="container">'
            f'<a class="brand" href="{base}"><img src="/extracto/img/icon-64.png" width="34" height="34" alt="">Extracto</a>'
            f'<nav class="nav" aria-label="Extracto">{nav}</nav>'
            f'<nav class="langs" aria-label="{esc(t["langs_label"])}">{langs}</nav>'
            f'</div></header>\n')


def footer(lang, extra=""):
    t = T[lang]
    return (f'<footer class="site-footer"><div class="container">'
            f'<span>© 2026 <a href="/">Alifo</a></span><a href="/extracto/support/">{esc(t["footer"][0])}</a>'
            f'<a href="/extracto/privacy/">{esc(t["footer"][1])}</a><a href="mailto:support@alifo.app">support@alifo.app</a>'
            f'<span class="note">{esc(t["footer_note"])}</span></div></footer>\n')


def json_ld(lang):
    t = T[lang]
    data = {
        "@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Extracto",
        "operatingSystem": "macOS 14 or later", "applicationCategory": "BusinessApplication",
        "description": t["description"], "url": BASE + PATH[lang], "inLanguage": lang,
        "image": f"{BASE}/extracto/img/og-{lang}.png",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "publisher": {"@type": "Organization", "name": "Alifo", "url": BASE + "/"},
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>\n'


def page(lang):
    t = T[lang]
    sizes_hero = "(min-width: 1180px) 1100px, 94vw"
    sizes_feat = "(min-width: 1180px) 650px, (min-width: 900px) 56vw, 92vw"
    out = [head(lang, t["title"], t["description"], PATH[lang]), json_ld(lang), "</head>\n<body>\n", header(lang, lang)]
    out.append('<main id="main">\n')
    out.append(f'<div class="hero"><div class="container"><h1>{esc(t["h1"])}</h1><p class="promise">{esc(t["promise"])}</p>'
               f'{store_cta(lang)}{picture(f"shots/{lang}/1-tables", t["hero_alt"], sizes_hero, eager=True)}</div></div>\n')
    out.append('<div class="stats"><ul>' + "".join(f"<li>{esc(s)}</li>" for s in t["stats"]) + "</ul></div>\n")
    out.append(f'<section id="features"><div class="container"><p class="eyebrow">{esc(t["features_label"])}</p>')
    for i, (title, body, tag, alt) in enumerate(t["features"]):
        out.append(f'<div class="feature{" flip" if i % 2 else ""}">{picture(f"shots/{lang}/{NAMES[i]}", alt, sizes_feat)}'
                   f'<div><h3>{esc(title)}</h3><p>{esc(body)}</p><span class="tag">{esc(tag)}</span></div></div>')
    out.append("</div></section>\n")
    out.append(f'<section class="alt-bg" id="compare"><div class="container"><h2>{esc(t["compare_label"])}</h2>'
               f'<p class="intro">{esc(t["compare_intro"])}</p><div class="table-wrap"><table><thead><tr>'
               + "".join(f'<th scope="col">{esc(h)}</th>' for h in t["compare_head"]) + "</tr></thead><tbody>"
               + "".join(f'<tr><th scope="row">{esc(r)}</th><td class="no">{esc(m)}</td><td class="yes">{esc(e)}</td></tr>'
                         for r, m, e in t["compare"]) + "</tbody></table></div></div></section>\n")
    out.append(f'<section id="pricing"><div class="container"><h2>{esc(t["pricing_label"])}</h2><div class="plans">'
               f'<div class="plan"><h3>{esc(t["free_name"])}</h3><p class="price">{esc(t["free_price"])}</p><ul>'
               + "".join(f"<li>{esc(x)}</li>" for x in t["free_items"]) + "</ul></div>"
               f'<div class="plan pro"><h3>{esc(t["pro_name"])}</h3><p class="price">{esc(t["pro_price"])}</p><ul>'
               + "".join(f"<li>{esc(x)}</li>" for x in t["pro_items"]) + "</ul></div></div></div></section>\n")
    out.append(f'<section class="alt-bg" id="languages"><div class="container"><h2>{esc(t["languages_label"])}</h2>'
               f'<p class="intro">{esc(t["languages_intro"])}</p><ul class="pills">'
               + "".join(f'<li lang="{c}"{" dir=\"rtl\"" if c == "ar" else ""}>{esc(n)}</li>' for c, n in VALIDATED)
               + "</ul></div></section>\n")
    out.append(f'<section class="faq" id="faq"><div class="container"><h2>{esc(t["faq_label"])}</h2>'
               + "".join(f"<details><summary>{esc(q)}</summary><p>{a}</p></details>" for q, a in t["faq"])
               + "</div></section>\n")
    out.append(f'<section class="final"><div class="container"><h2>{esc(t["final_title"])}</h2><p>{esc(t["final_text"])}</p>'
               f'{store_cta(lang)}</div></section>\n')
    out.append("</main>\n")
    out.append(footer(lang))
    out.append("</body>\n</html>\n")
    return "".join(out)


def rewrap(path, own_path):
    """Support and Privacy: the same header, footer and styles as the product pages, content unchanged. Their
    French and Spanish sections get anchors (#fr, #es), which the language switch points to."""
    src = path.read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", src, re.S).group(1)
    desc = re.search(r'<meta name="description" content="(.*?)">', src, re.S).group(1)
    body = re.search(r'</header>\s*(.*?)\s*<footer class="site-footer">', src, re.S).group(1)
    body = re.sub(r'^<main[^>]*>\s*|\s*</main>$', "", body.strip())        # already rewrapped: keep the content only
    body = re.sub(r'<h2( id="fr")?>En français</h2>', '<h2 id="fr" lang="fr">En français</h2>', body)
    body = re.sub(r'<h2( id="es")?>En español</h2>', '<h2 id="es" lang="es">En español</h2>', body)
    home = {"en": own_path, "fr": own_path + "#fr", "es": own_path + "#es"}
    html_ = (head("en", html.unescape(title), html.unescape(desc), own_path, alternates=False, og_image=False)
             + "</head>\n<body>\n" + header("en", "en", home=home, anchors=False)
             + f'<main id="main" class="doc">\n{body}\n</main>\n' + footer("en") + "</body>\n</html>\n")
    path.write_text(html_, encoding="utf-8")


def sitemap():
    urls = ["/", "/aftershot/", "/aftershot/support/", "/aftershot/privacy/", "/alwah/", "/alwah/support/",
            "/alwah/privacy/", "/keytoons/", "/keytoons/support/", "/keytoons/privacy/",
            "/extracto/support/", "/extracto/privacy/", "/grandio/support/", "/grandio/privacy/"]
    alt = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{BASE}{PATH[l]}"/>' for l in LANGS)
    alt += f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{PATH["en"]}"/>'
    rows = [f"<url><loc>{BASE}{PATH[l]}</loc><lastmod>{LASTMOD}</lastmod>{alt}</url>" for l in LANGS]
    # Grandio's three language pages (tools/make_grandio.py), with their own alternates, once generated.
    grandio = {"en": "/grandio/", "fr": "/grandio/fr/", "es": "/grandio/es/"}
    if all((SITE / p.strip("/") / "index.html").exists() for p in grandio.values()):
        ralt = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{BASE}{grandio[l]}"/>' for l in LANGS)
        ralt += f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{grandio["en"]}"/>'
        rows += [f"<url><loc>{BASE}{grandio[l]}</loc><lastmod>2026-11-02</lastmod>{ralt}</url>" for l in LANGS]
    rows += [f"<url><loc>{BASE}{u}</loc></url>" for u in urls if (SITE / u.strip("/") / "index.html").exists() or u == "/"]
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")


def main():
    make_images()
    for lang in LANGS:
        d = SITE / PATH[lang].strip("/")
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page(lang), encoding="utf-8")
        print("wrote", PATH[lang])
    rewrap(SITE / "extracto" / "support" / "index.html", "/extracto/support/")
    rewrap(SITE / "extracto" / "privacy" / "index.html", "/extracto/privacy/")
    sitemap()
    print("support, privacy, sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
