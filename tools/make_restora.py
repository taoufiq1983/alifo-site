"""Generate the Restora pages of alifo.app (derived from tools/make_site.py, Extracto's generator: same template).
Generate the Restora pages of alifo.app (GitHub Pages repository, default ~/Downloads/alifo-site).

Writes /restora/ (English), /restora/fr/, /restora/es/, their images (WebP + PNG fallback, 640 / 1280 / 1920 px,
from captures/appstore), the 1200 × 630 share images, the Support and Privacy pages' header and footer, sitemap.xml
and robots.txt. No script, no tracker, no external font: CSS in each page, system font.

The Mac App Store link: while APP_STORE_URL is None the pages say "Coming soon on the Mac App Store" (plain text, no
badge: Apple's badge must link to the app's App Store page). Once the app is live, set APP_STORE_URL to its product
page (https://apps.apple.com/app/id…) and run again: the official badge (restora/img/badges, downloaded unmodified
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
RESTORA = Path.home() / "Developer" / "Restora"                # screenshots and icon are read from the app's repository
SHOTS = RESTORA / "captures" / "appstore"
ICON = RESTORA / "Restora" / "Resources" / "Assets.xcassets" / "AppIcon.appiconset" / "icon_512x512@2x.png"
BASE = "https://alifo.app"
APP_STORE_URL = None            # set when the app is live, e.g. "https://apps.apple.com/app/id0000000000"
WIDTHS = [640, 1280, 1920]
NAMES = ["1-print", "2-etsy", "3-oldphoto", "4-detail", "5-batch", "6-private"]
LANGS = ["en", "fr", "es"]
PATH = {"en": "/restora/", "fr": "/restora/fr/", "es": "/restora/es/"}
BADGE_LOCALE = {"en": "en-us", "fr": "fr-fr", "es": "es-es"}
LASTMOD = "2026-11-02"

# File formats Restora reads (the "formats" section).
FORMATS = ["JPEG", "PNG", "HEIC", "TIFF 8/16-bit", "WebP", "GIF", "BMP"]

T = {
    "en": {
        "title": "Restora — AI photo upscaler for Mac: enlarge and restore photos offline",
        "description": "Print any photo big and sharp: Print Studio at 300 dpi, Etsy print pack, old photo restoration and "
                       "batches on your Mac. The AI runs on your Mac: nothing is uploaded. ×2 is free.",
        "nav": ["Features", "Pricing", "FAQ", "Support"],
        "langs_label": "Language",
        "h1": "Print anything big. Keep it sharp.",
        "promise": "Nothing leaves your Mac.",
        "soon": "Coming soon on the Mac App Store",
        "badge_alt": "Download on the Mac App Store",
        "hero_alt": "Restora's Print Studio on a Mac: a 1940 poster framed for an 18 × 24 in print at 300 dpi, with "
                    "the quality rated Good.",
        "stats": ["Prints up to 24 × 36 in at 300 dpi", "Etsy print pack", "Works offline", "One-time purchase"],
        "features_label": "Features",
        "features": [
            ("Print it big. Keep it sharp.",
             "Print Studio turns any photo, poster or drawing into a print file: A4 to A2, Letter, Tabloid, 4×6 to "
             "24×36 in, 60×90 cm or your own size, at 150, 240 or 300 dpi. Restora computes the enlargement, rates the "
             "quality (Excellent, Good or Limit) before you print, and lets you drag the crop or add margins.", "Pro",
             "A 1940 poster in Restora's Print Studio, framed for 18 × 24 in at 300 dpi, quality Good."),
            ("The Etsy print pack, in one click.",
             "Five 300 dpi JPEGs for the 2:3, 3:4, 4:5, ISO and 11×14 ratios, clearly named, the resolution written in "
             "each file, every file under Etsy's 20 MB limit, in one folder.", "Pro",
             "Restora after exporting an Etsy print pack, next to the five files with their sizes and 300 dpi."),
            ("Bring old photos back.",
             "Old Photo mode cleans the grain of scanned prints and brings back the detail. Restora recognises old "
             "photos, drawings and screenshots and suggests the right mode.", "Pro",
             "A photograph of the Brooklyn Bridge from around 1900, before and after Old Photo mode."),
            ("Up to 4× bigger.",
             "×2 is free, in Auto mode, with no watermark. ×4, or the exact size you need up to 16,384 pixels, with "
             "Restora Pro. Shown at 100 %: real detail, not just bigger pixels.", "Free ×2 · Pro ×4",
             "A neon sign at 100 % in Restora, before and after ×4: soft on the left, crisp on the right."),
            ("A whole folder in one go.",
             "Drop a folder, or right-click in the Finder › Services › Upscale with Restora: every image is listed with "
             "its status and the time left. Your originals are never overwritten.", "Pro",
             "Eight images in Restora's list, two exported, one in progress, with the time left."),
            ("Nothing leaves your Mac.",
             "The AI models are inside the app and run on your Mac's Neural Engine. No account, no upload, no "
             "analytics, and Restora has no network access: it works offline.", "Free",
             "A night sky photo in Restora with a padlock and the words Works offline, No upload."),
        ],
        "compare_label": "Preview vs Restora",
        "compare_intro": "macOS can already resize an image. Restora adds detail instead of stretching pixels.",
        "compare_head": ["", "Resize in Preview", "Restora"],
        "compare": [
            ("Make an image bigger", "Yes, by interpolation: softer", "Yes, with AI: sharper"),
            ("Clean grain and JPEG artefacts", "No", "Yes"),
            ("Before/after comparison", "No", "Yes, with a slider"),
            ("A whole folder in one go", "With a shortcut you build", "Yes, drop the folder (Pro)"),
            ("Keep metadata, colour profile, transparency", "Yes", "Yes"),
        ],
        "pricing_label": "Pricing",
        "free_name": "Free", "free_price": "Free, with no limit",
        "free_items": ["×2 enlargement in Auto mode, no watermark, no quota", "Before/after comparator, one image at a time",
                       "JPEG and PNG export, metadata kept", "Preview of every Pro feature on the visible area"],
        "pro_name": "Restora Pro", "pro_price": "One-time purchase on the Mac App Store",
        "pro_items": ["Print Studio: print formats at 300 dpi, quality checked", "Etsy print pack in one click",
                      "Old Photo mode and denoising, ×4 and sizes up to 16,384 px", "Folders and batches, Finder service, "
                      "HEIC and 16-bit TIFF; shared with your family"],
        "languages_label": "Formats",
        "languages_intro": "Colour profiles, transparency, 16-bit depth and orientation are kept. Interface in English, "
                           "French and Spanish.",
        "faq_label": "FAQ",
        "faq": [
            ("Is Restora free?",
             "Yes for ×2: enlarge any number of images ×2 in Auto mode and export them in JPEG or PNG, with no watermark, "
             "no quota and no account. Restora Pro, a one-time purchase, unlocks Print Studio, the Etsy print pack, Old "
             "Photo mode and denoising, ×4 and custom sizes, batches, HEIC and TIFF."),
            ("Will my print be sharp?",
             "Print Studio tells you before you print. It computes the enlargement the print needs: up to 2× is rated "
             "Excellent, up to 4× Good, beyond Limit. Lower the size or the resolution (240 or 150 dpi suit posters "
             "seen from a distance) to improve the rating."),
            ("Are my photos sent anywhere?",
             "No. The enhancement runs on your Mac with models included in the app. Restora has no network access: your "
             "photos never leave your Mac. See the <a href=\"/restora/privacy/\">privacy policy</a>."),
            ("How does it work?",
             "Restora uses Real-ESRGAN neural networks (by Xintao Wang, BSD licence), converted to Core ML. They were "
             "measured against classic resizing on photos, old prints, drawings and screenshots before being chosen."),
            ("Does it restore faces?",
             "Not specifically: Restora sharpens and cleans the whole image. It has no dedicated face model, and it does "
             "not invent or change people's features on purpose."),
            ("How big can the result be?",
             "Up to 16,384 pixels per side and 256 megapixels. Restora tells you before starting if a size is too large."),
            ("Does it work on Intel Macs?",
             "Yes. Restora runs on Apple silicon and Intel Macs with macOS 14 Sonoma or later. It is fastest on Apple "
             "silicon, where it uses the Neural Engine."),
            ("Can I use Pro on several Macs, or share it with my family?",
             "Yes. Restora Pro works on every Mac signed in with your Apple Account (Restora › Restore Purchases), and "
             "is shared with your family through Family Sharing."),
            ("Can I get a refund?",
             "Purchases are made through Apple, so refunds are too: request one at "
             "<a href=\"https://reportaproblem.apple.com\">reportaproblem.apple.com</a>."),
        ],
        "final_title": "Print anything big, and sharp.",
        "final_text": "Print Studio, Etsy print pack, old photos, batches. Nothing leaves your Mac.",
        "footer": ["Support", "Privacy"],
        "footer_note": "This page loads no scripts, no external fonts and no trackers.",
        "privacy_link": "Privacy",
    },
    "fr": {
        "title": "Restora — agrandir et restaurer vos photos sur Mac avec l’IA, hors ligne",
        "description": "Rendez vos photos plus nettes et plus grandes, restaurez les vieux clichés et agrandissez des "
                       "dossiers entiers sur votre Mac. L’IA tourne sur votre Mac : rien n’est envoyé. Le ×2 est gratuit.",
        "nav": ["Fonctions", "Tarifs", "FAQ", "Assistance"],
        "langs_label": "Langue",
        "h1": "Imprimez grand. Gardez la netteté.",
        "promise": "Rien ne quitte votre Mac.",
        "soon": "Bientôt sur le Mac App Store",
        "badge_alt": "Télécharger dans le Mac App Store",
        "hero_alt": "Le Print Studio de Restora sur un Mac : une affiche de 1940 cadrée pour une impression 18 × 24 "
                    "pouces à 300 dpi, qualité Bonne.",
        "stats": ["Jusqu’au 60 × 90 cm à 300 dpi", "Pack d’impression Etsy", "Hors ligne", "Achat unique"],
        "features_label": "Fonctions",
        "features": [
            ("Imprimez grand. Gardez la netteté.",
             "Print Studio transforme une photo, une affiche ou un dessin en fichier d’impression : de l’A4 à l’A2, "
             "Letter, Tabloid, du 4×6 au 24×36 pouces, 60×90 cm ou votre propre taille, à 150, 240 ou 300 dpi. Restora "
             "calcule l’agrandissement, note la qualité (Excellente, Bonne ou Limite) avant l’impression et vous laisse "
             "déplacer le recadrage ou ajouter des marges.", "Pro",
             "Une affiche de 1940 dans le Print Studio de Restora, cadrée en 18 × 24 pouces à 300 dpi, qualité Bonne."),
            ("Le pack d’impression Etsy, en un clic.",
             "Cinq JPEG à 300 dpi aux rapports 2:3, 3:4, 4:5, ISO et 11×14, clairement nommés, la résolution écrite dans "
             "chaque fichier, chacun sous la limite Etsy de 20 Mo, dans un dossier.", "Pro",
             "Restora après l’export d’un pack Etsy, à côté des cinq fichiers avec leurs tailles et 300 dpi."),
            ("Redonnez vie aux vieilles photos.",
             "Le mode Vieille photo nettoie le grain des tirages numérisés et retrouve les détails, avec un débruitage "
             "réglable. Le mode Auto reconnaît photos, dessins et captures d’écran.", "Pro",
             "Une photographie du pont de Brooklyn vers 1900, avant et après le mode Vieille photo."),
            ("Jusqu’à 4× plus grand.",
             "Le ×2 est gratuit, en mode Auto, sans filigrane. Le ×4, ou la taille exacte voulue jusqu’à 16 384 pixels, "
             "avec Restora Pro. Affiché à 100 % : du vrai détail, pas des pixels plus gros.", "Gratuit ×2 · Pro ×4",
             "Une enseigne lumineuse à 100 % dans Restora, avant et après ×4 : floue à gauche, nette à droite."),
            ("Un dossier entier d’un coup.",
             "Déposez un dossier, ou faites un clic droit dans le Finder › Services › Agrandir avec Restora : chaque "
             "image est listée avec son état et le temps restant. Vos originaux ne sont jamais écrasés.", "Pro",
             "Huit images dans la liste de Restora, deux exportées, une en cours, avec le temps restant."),
            ("Rien ne quitte votre Mac.",
             "Les modèles d’IA sont dans l’app et tournent sur le Neural Engine de votre Mac. Sans compte, sans envoi, "
             "sans mesure d’audience, et Restora n’a pas accès au réseau : il fonctionne hors ligne.", "Gratuit",
             "Une photo de ciel nocturne dans Restora, avec un cadenas et les mots Fonctionne hors ligne, Aucun envoi."),
        ],
        "compare_label": "Aperçu ou Restora",
        "compare_intro": "macOS sait déjà redimensionner une image. Restora ajoute du détail au lieu d’étirer les pixels.",
        "compare_head": ["", "Redimensionner dans Aperçu", "Restora"],
        "compare": [
            ("Agrandir une image", "Oui, par interpolation : plus flou", "Oui, avec l’IA : plus net"),
            ("Nettoyer le grain et les artefacts JPEG", "Non", "Oui"),
            ("Comparer avant/après", "Non", "Oui, avec un curseur"),
            ("Un dossier entier d’un coup", "Avec un raccourci à construire", "Oui, déposez le dossier (Pro)"),
            ("Garder métadonnées, profil couleur, transparence", "Oui", "Oui"),
        ],
        "pricing_label": "Tarifs",
        "free_name": "Gratuit", "free_price": "Gratuit, sans limite",
        "free_items": ["Agrandissement ×2 en mode Auto, sans filigrane ni quota", "Comparateur avant/après, une image à la fois",
                       "Export JPEG et PNG, métadonnées conservées", "Aperçu de chaque fonction Pro sur la zone visible"],
        "pro_name": "Restora Pro", "pro_price": "Achat unique sur le Mac App Store",
        "pro_items": ["Print Studio : formats d’impression à 300 dpi, qualité vérifiée", "Pack d’impression Etsy en un clic",
                      "Mode Vieille photo et débruitage, ×4 et tailles jusqu’à 16 384 px", "Dossiers et lots, service du Finder, "
                      "HEIC et TIFF 16 bits ; partagé en famille"],
        "languages_label": "Formats",
        "languages_intro": "Profils couleur, transparence, 16 bits et orientation conservés. Interface en anglais, "
                           "français et espagnol.",
        "faq_label": "FAQ",
        "faq": [
            ("Restora est-il gratuit ?",
             "Oui pour le ×2 : agrandissez autant d’images que vous voulez ×2 en mode Auto et exportez-les en JPEG ou "
             "PNG, sans filigrane, sans quota et sans compte. Restora Pro, un achat unique, débloque Print Studio, le "
             "pack d’impression Etsy, le mode Vieille photo et le débruitage, le ×4 et les tailles sur mesure, les lots, "
             "le HEIC et le TIFF."),
            ("Mon impression sera-t-elle nette ?",
             "Print Studio vous le dit avant d’imprimer. Il calcule l’agrandissement nécessaire : jusqu’à 2× c’est "
             "Excellent, jusqu’à 4× Bon, au-delà Limite. Réduisez la taille ou la résolution (240 ou 150 dpi conviennent "
             "aux affiches vues de loin) pour améliorer la note."),
            ("Mes photos sont-elles envoyées quelque part ?",
             "Non. L’amélioration se fait sur votre Mac avec des modèles inclus dans l’app. Restora n’a pas accès au "
             "réseau : vos photos ne quittent jamais votre Mac. Voir la <a href=\"/restora/privacy/#fr\">politique de "
             "confidentialité</a>."),
            ("Comment ça marche ?",
             "Restora utilise les réseaux de neurones Real-ESRGAN (de Xintao Wang, licence BSD), convertis pour Core ML. "
             "Ils ont été mesurés face au redimensionnement classique sur des photos, de vieux tirages, des dessins et "
             "des captures d’écran avant d’être retenus."),
            ("Restaure-t-il les visages ?",
             "Pas spécifiquement : Restora rend toute l’image plus nette et plus propre. Il n’a pas de modèle dédié aux "
             "visages et ne cherche pas à inventer ou modifier les traits des personnes."),
            ("Jusqu’à quelle taille ?",
             "Jusqu’à 16 384 pixels de côté et 256 mégapixels. Restora prévient avant de commencer si une taille est "
             "trop grande."),
            ("Fonctionne-t-il sur les Mac Intel ?",
             "Oui. Restora fonctionne sur les Mac à puce Apple et Intel avec macOS 14 Sonoma ou ultérieur. Il est plus "
             "rapide sur puce Apple, où il utilise le Neural Engine."),
            ("Puis-je utiliser Pro sur plusieurs Mac, ou le partager en famille ?",
             "Oui. Restora Pro fonctionne sur chaque Mac connecté avec votre compte Apple (Restora › Restaurer les "
             "achats), et se partage avec votre famille via le Partage familial."),
            ("Puis-je être remboursé ?",
             "Les achats passent par Apple, les remboursements aussi : demandez-le sur "
             "<a href=\"https://reportaproblem.apple.com\">reportaproblem.apple.com</a>."),
        ],
        "final_title": "Imprimez tout en grand, et net.",
        "final_text": "Print Studio, pack Etsy, vieilles photos, lots. Rien ne quitte votre Mac.",
        "footer": ["Assistance", "Confidentialité"],
        "footer_note": "Cette page ne charge ni script, ni police externe, ni traceur.",
        "privacy_link": "Confidentialité",
    },
    "es": {
        "title": "Restora — amplía y restaura fotos en el Mac con IA, sin conexión",
        "description": "Haz tus fotos más nítidas y grandes, restaura las antiguas y amplía carpetas enteras en tu Mac. "
                       "La IA funciona en tu Mac: nada se sube. El ×2 es gratis.",
        "nav": ["Funciones", "Precios", "Preguntas", "Soporte"],
        "langs_label": "Idioma",
        "h1": "Imprime en grande. Siempre nítido.",
        "promise": "Nada sale de tu Mac.",
        "soon": "Muy pronto en el Mac App Store",
        "badge_alt": "Descargar en el Mac App Store",
        "hero_alt": "El Print Studio de Restora en un Mac: un cartel de 1940 encuadrado para imprimir a 18 × 24 "
                    "pulgadas a 300 ppp, calidad Buena.",
        "stats": ["Hasta 60 × 90 cm a 300 ppp", "Pack de impresión Etsy", "Sin conexión", "Compra única"],
        "features_label": "Funciones",
        "features": [
            ("Imprime en grande. Siempre nítido.",
             "Print Studio convierte una foto, un cartel o un dibujo en un archivo de impresión: de A4 a A2, Letter, "
             "Tabloid, de 4×6 a 24×36 pulgadas, 60×90 cm o tu propio tamaño, a 150, 240 o 300 ppp. Restora calcula la "
             "ampliación, califica la calidad (Excelente, Buena o Límite) antes de imprimir y te deja mover el recorte "
             "o añadir márgenes.", "Pro",
             "Un cartel de 1940 en el Print Studio de Restora, encuadrado a 18 × 24 pulgadas a 300 ppp, calidad Buena."),
            ("El pack de impresión Etsy, en un clic.",
             "Cinco JPEG a 300 ppp en las proporciones 2:3, 3:4, 4:5, ISO y 11×14, con nombres claros, la resolución "
             "escrita en cada archivo, todos por debajo del límite de 20 MB de Etsy, en una carpeta.", "Pro",
             "Restora tras exportar un pack Etsy, junto a los cinco archivos con sus tamaños y 300 ppp."),
            ("Devuelve la vida a tus fotos antiguas.",
             "El modo Foto antigua limpia el grano de las copias escaneadas y recupera los detalles, con reducción de "
             "ruido ajustable. El modo Auto reconoce fotos, dibujos y capturas de pantalla.", "Pro",
             "Una fotografía del puente de Brooklyn hacia 1900, antes y después del modo Foto antigua."),
            ("Hasta 4× más grande.",
             "El ×2 es gratis, en modo Auto, sin marca de agua. El ×4, o el tamaño exacto que necesites hasta 16.384 "
             "píxeles, con Restora Pro. Al 100 %: detalle real, no solo píxeles más grandes.", "Gratis ×2 · Pro ×4",
             "Un letrero de neón al 100 % en Restora, antes y después de ×4: borroso a la izquierda, nítido a la derecha."),
            ("Una carpeta entera de una vez.",
             "Suelta una carpeta, o haz clic derecho en el Finder › Servicios › Ampliar con Restora: cada imagen aparece "
             "con su estado y el tiempo restante. Tus originales nunca se sobrescriben.", "Pro",
             "Ocho imágenes en la lista de Restora, dos exportadas, una en curso, con el tiempo restante."),
            ("Nada sale de tu Mac.",
             "Los modelos de IA están dentro de la app y funcionan en el Neural Engine de tu Mac. Sin cuenta, sin "
             "subidas, sin analítica, y Restora no tiene acceso a la red: funciona sin conexión.", "Gratis",
             "Una foto de un cielo nocturno en Restora, con un candado y las palabras Funciona sin conexión, Sin subidas."),
        ],
        "compare_label": "Vista Previa o Restora",
        "compare_intro": "macOS ya sabe cambiar el tamaño de una imagen. Restora añade detalle en lugar de estirar los píxeles.",
        "compare_head": ["", "Ajustar tamaño en Vista Previa", "Restora"],
        "compare": [
            ("Ampliar una imagen", "Sí, por interpolación: más borrosa", "Sí, con IA: más nítida"),
            ("Limpiar el grano y los artefactos JPEG", "No", "Sí"),
            ("Comparar antes y después", "No", "Sí, con un control deslizante"),
            ("Una carpeta entera de una vez", "Con un atajo que construyes", "Sí, suelta la carpeta (Pro)"),
            ("Conservar metadatos, perfil de color y transparencia", "Sí", "Sí"),
        ],
        "pricing_label": "Precios",
        "free_name": "Gratis", "free_price": "Gratis, sin límite",
        "free_items": ["Ampliación ×2 en modo Auto, sin marca de agua ni cupos", "Comparador antes/después, una imagen cada vez",
                       "Exportación JPEG y PNG, con los metadatos", "Vista previa de cada función Pro en la zona visible"],
        "pro_name": "Restora Pro", "pro_price": "Compra única en el Mac App Store",
        "pro_items": ["Print Studio: formatos de impresión a 300 ppp, calidad comprobada", "Pack de impresión Etsy en un clic",
                      "Modo Foto antigua y reducción de ruido, ×4 y tamaños de hasta 16.384 px", "Carpetas y lotes, servicio del "
                      "Finder, HEIC y TIFF de 16 bits; compartido en familia"],
        "languages_label": "Formatos",
        "languages_intro": "Se conservan los perfiles de color, la transparencia, los 16 bits y la orientación. Interfaz "
                           "en inglés, francés y español.",
        "faq_label": "Preguntas",
        "faq": [
            ("¿Restora es gratis?",
             "Sí para el ×2: amplía todas las imágenes que quieras ×2 en modo Auto y expórtalas en JPEG o PNG, sin marca "
             "de agua, sin cupos y sin cuenta. Restora Pro, una compra única, desbloquea Print Studio, el pack de "
             "impresión Etsy, el modo Foto antigua y la reducción de ruido, el ×4 y los tamaños a medida, los lotes, HEIC "
             "y TIFF."),
            ("¿Mi impresión será nítida?",
             "Print Studio te lo dice antes de imprimir. Calcula la ampliación necesaria: hasta 2× es Excelente, hasta "
             "4× Buena, más allá Límite. Reduce el tamaño o la resolución (240 o 150 ppp sirven para carteles vistos de "
             "lejos) para mejorar la calificación."),
            ("¿Se envían mis fotos a algún sitio?",
             "No. La mejora se hace en tu Mac con modelos incluidos en la app. Restora no tiene acceso a la red: tus "
             "fotos nunca salen de tu Mac. Consulta la <a href=\"/restora/privacy/#es\">política de privacidad</a>."),
            ("¿Cómo funciona?",
             "Restora usa las redes neuronales Real-ESRGAN (de Xintao Wang, licencia BSD), convertidas a Core ML. Se "
             "midieron frente al redimensionado clásico en fotos, copias antiguas, dibujos y capturas antes de elegirlas."),
            ("¿Restaura las caras?",
             "No de forma específica: Restora hace más nítida y limpia toda la imagen. No tiene un modelo dedicado a las "
             "caras y no pretende inventar ni cambiar los rasgos de las personas."),
            ("¿Hasta qué tamaño?",
             "Hasta 16.384 píxeles por lado y 256 megapíxeles. Restora avisa antes de empezar si un tamaño es demasiado "
             "grande."),
            ("¿Funciona en los Mac con Intel?",
             "Sí. Restora funciona en los Mac con chip de Apple e Intel con macOS 14 Sonoma o posterior. Es más rápida "
             "con chip de Apple, donde usa el Neural Engine."),
            ("¿Puedo usar Pro en varios Mac o compartirlo con mi familia?",
             "Sí. Restora Pro funciona en todos los Mac con tu cuenta de Apple (Restora › Restaurar compras) y se "
             "comparte con tu familia mediante En familia."),
            ("¿Puedo pedir un reembolso?",
             "Las compras se hacen a través de Apple, y los reembolsos también: solicítalo en "
             "<a href=\"https://reportaproblem.apple.com\">reportaproblem.apple.com</a>."),
        ],
        "final_title": "Imprime lo que quieras en grande, y nítido.",
        "final_text": "Print Studio, pack Etsy, fotos antiguas, lotes. Nada sale de tu Mac.",
        "footer": ["Soporte", "Privacidad"],
        "footer_note": "Esta página no carga scripts, ni fuentes externas, ni rastreadores.",
        "privacy_link": "Privacidad",
    },
}

SUPPORT = ("Restora Support", "Help for Restora, the AI photo upscaler for Mac: questions, problems and contact.", """<h1>Restora Support</h1>
  <p class="lede">Write to <a href="mailto:support@alifo.app">support@alifo.app</a>: we answer within two working days.</p>

  <h2>Getting started</h2>
  <dl>
    <dt>Enlarge a photo</dt>
    <dd>Drop a photo on the window (or click Choose Photos…, or paste with ⌘V). The result appears in the comparator: drag the divider, zoom with a pinch or ⌘ + scroll, press Space to see the original. Click Export (⌘E).</dd>
    <dt>Try it without your own photos</dt>
    <dd>Click Try a Sample: four public-domain images open (an old photo, a small photo, a drawing and a screenshot).</dd>
    <dt>A whole folder</dt>
    <dd>Drop a folder (Restora Pro). Every image is listed; Export All, at the bottom of the list, writes them into the folder you choose.</dd>
    <dt>From the Finder</dt>
    <dd>Select images, right-click › Services › Upscale with Restora. If the item is missing, enable it in System Settings › Keyboard › Keyboard Shortcuts › Services.</dd>
  </dl>

  <h2>Common questions</h2>
  <dl>
    <dt>“The result would be … pixels”</dt>
    <dd>Restora creates images up to 16,384 pixels per side and 256 megapixels. Choose ×2, or a smaller custom size.</dd>
    <dt>The export does not replace my file</dt>
    <dd>On purpose: Restora never overwrites. It names the result “photo@2x.jpg”, “photo@4x.jpg”, and adds a number if that name exists.</dd>
    <dt>“Restora cannot save in …”</dt>
    <dd>The folder is read-only or on a locked disk. Choose another folder.</dd>
    <dt>Faces look different</dt>
    <dd>Restora has no face-specific model; on very small faces the AI may smooth details. Try ×2, Photo mode, or a lower denoise.</dd>
    <dt>Restore my purchase</dt>
    <dd>Restora › Restore Purchases, or Settings › Restora Pro › Restore Purchases, signed in with the Apple Account used to buy.</dd>
    <dt>Refunds</dt>
    <dd>Purchases are made through Apple: <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a>.</dd>
  </dl>

  <h2 id="fr" lang="fr">En français</h2>
  <dl lang="fr">
    <dt>Agrandir une photo</dt>
    <dd>Déposez une photo sur la fenêtre (ou Choisir des photos…, ou ⌘V). Le résultat s’affiche dans le comparateur ; cliquez sur Exporter (⌘E). Pour essayer sans vos photos : Essayer un exemple.</dd>
    <dt>Depuis le Finder</dt>
    <dd>Clic droit sur des images › Services › Agrandir avec Restora.</dd>
    <dt>Restaurer l’achat</dt>
    <dd>Restora › Restaurer les achats. Remboursements : <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a>.</dd>
    <dt>Contact</dt>
    <dd><a href="mailto:support@alifo.app">support@alifo.app</a></dd>
  </dl>

  <h2 id="es" lang="es">En español</h2>
  <dl lang="es">
    <dt>Ampliar una foto</dt>
    <dd>Suelta una foto en la ventana (o Elegir fotos…, o ⌘V). El resultado aparece en el comparador; haz clic en Exportar (⌘E). Para probar sin tus fotos: Probar un ejemplo.</dd>
    <dt>Desde el Finder</dt>
    <dd>Clic derecho en imágenes › Servicios › Ampliar con Restora.</dd>
    <dt>Restaurar la compra</dt>
    <dd>Restora › Restaurar compras. Reembolsos: <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a>.</dd>
    <dt>Contacto</dt>
    <dd><a href="mailto:support@alifo.app">support@alifo.app</a></dd>
  </dl>""")

PRIVACY = ("Restora Privacy Policy", "Restora collects nothing: your photos are enhanced on your Mac and never leave it.", """<h1>Privacy Policy</h1>
  <p class="lede">Restora collects nothing. Effective November 2, 2026.</p>

  <h2>The short version</h2>
  <p>No account, no servers, no ads, no tracking. Your photos are enhanced on your Mac and never leave it.</p>

  <h2>Details</h2>
  <dl>
    <dt>Your photos</dt>
    <dd>Restora opens only the images you choose, drop, paste or send from the Finder. The enhancement runs on your Mac with AI models included in the app. Images and results are never uploaded anywhere.</dd>
    <dt>What stays on your Mac</dt>
    <dd>Your exports are saved where you choose. Restora keeps only its settings and whether Restora Pro is unlocked. Images are not kept after you quit.</dd>
    <dt>Metadata</dt>
    <dd>Exports keep your photos’ metadata (date, camera, copyright) unless you turn it off; an option removes the location (GPS). This happens on your Mac.</dd>
    <dt>Network</dt>
    <dd>Restora does not connect to the internet. It has no permission to do so (App Sandbox, no network access).</dd>
    <dt>Data we collect</dt>
    <dd>None. Restora does not collect personal data, usage data, diagnostics or identifiers.</dd>
    <dt>Purchases</dt>
    <dd>Restora Pro is sold through the Mac App Store. Apple processes the payment; we do not receive your name, email or payment details.</dd>
    <dt>Tracking</dt>
    <dd>Restora does not track you across apps or websites, and contains no third-party code.</dd>
    <dt>Children</dt>
    <dd>Restora suits all ages. No personal data, from a child or an adult, is collected.</dd>
    <dt>Changes</dt>
    <dd>If this policy changes, the new version will be posted on this page with a new effective date.</dd>
    <dt>Contact</dt>
    <dd><a href="mailto:support@alifo.app">support@alifo.app</a> · <a href="/restora/support/">alifo.app/restora/support</a></dd>
  </dl>

  <h2 id="fr" lang="fr">En français</h2>
  <dl lang="fr">
    <dt>Vos photos</dt>
    <dd>Restora n’ouvre que les images que vous choisissez, déposez, collez ou envoyez depuis le Finder. L’amélioration se fait sur votre Mac, avec des modèles d’IA inclus dans l’app. Rien n’est envoyé nulle part.</dd>
    <dt>Réseau</dt>
    <dd>Restora ne se connecte pas à Internet et n’en a pas l’autorisation.</dd>
    <dt>Données collectées</dt>
    <dd>Aucune. Pas de compte, pas de publicité, pas de mesure d’audience, pas de pistage.</dd>
    <dt>L’achat</dt>
    <dd>L’achat de Restora Pro est géré par Apple. Nous ne voyons jamais vos informations de paiement.</dd>
    <dt>Contact</dt>
    <dd><a href="mailto:support@alifo.app">support@alifo.app</a></dd>
  </dl>

  <h2 id="es" lang="es">En español</h2>
  <dl lang="es">
    <dt>Tus fotos</dt>
    <dd>Restora solo abre las imágenes que eliges, sueltas, pegas o envías desde el Finder. La mejora se hace en tu Mac, con modelos de IA incluidos en la app. No se envía nada a ningún sitio.</dd>
    <dt>Red</dt>
    <dd>Restora no se conecta a internet y no tiene permiso para hacerlo.</dd>
    <dt>Datos recopilados</dt>
    <dd>Ninguno. Sin cuenta, sin publicidad, sin analítica, sin rastreo.</dd>
    <dt>La compra</dt>
    <dd>La compra de Restora Pro la gestiona Apple. Nunca vemos tus datos de pago.</dd>
    <dt>Contacto</dt>
    <dd><a href="mailto:support@alifo.app">support@alifo.app</a></dd>
  </dl>""")


CSS = """
:root {
  color-scheme: light dark;
  --bg: #fbf7f3; --surface: #ffffff; --surface-2: #f4ebe5; --ink: #2a1712; --muted: #6a4f45; --line: #ead9cf;
  --accent: #c2410c; --accent-ink: #b23a0b; --on-accent: #ffffff;
  --hero-1: #2c1a28; --hero-2: #100e1a; --hero-ink: #ffffff; --hero-muted: #d6c4ce;
  --shadow: 0 18px 50px rgba(44, 20, 12, .20), 0 2px 8px rgba(44, 20, 12, .10);
  --sans: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #120d14; --surface: #1c151d; --surface-2: #241a24; --ink: #f4ece8; --muted: #c4b2ae; --line: #33262f;
    --accent-ink: #ff9a62; --on-accent: #2a1208;
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
    """WebP and PNG at each width (Lanczos), into restora/img/…"""
    out = SITE / "restora" / "img"
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
        im.save(SITE / "restora" / "img" / f"icon-{s}.png", optimize=True)
        im.save(SITE / "restora" / "img" / f"icon-{s}.webp", "WEBP", quality=90, method=6)


def og(lang):
    """1200 × 630 share image from the "Sharper. Bigger. Instantly." screenshot, on its own background colours."""
    shot = Image.open(SHOTS / f"mac-{lang}" / "1-print.png").convert("RGB")
    h = 630
    w = round(shot.width * h / shot.height)
    small = shot.resize((w, h), Image.LANCZOS)
    canvas = Image.new("RGB", (1200, h))
    # The screenshot's left and right columns, stretched, so the extension matches its gradient.
    canvas.paste(small.crop((0, 0, 2, h)).resize(((1200 - w) // 2 + 2, h)), (0, 0))
    canvas.paste(small.crop((w - 2, 0, w, h)).resize((1200 - w - (1200 - w) // 2 + 2, h)), ((1200 - w) // 2 + w - 2, 0))
    canvas.paste(small, ((1200 - w) // 2, 0))
    canvas.save(SITE / "restora" / "img" / f"og-{lang}.png", optimize=True)


# ---------------------------------------------------------------- HTML
def esc(s):
    return html.escape(s, quote=True)


def picture(stem, alt, sizes, eager=False):
    img = f"/restora/img/{stem}"
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
            f'<source media="(prefers-color-scheme: dark)" srcset="/restora/img/badges/mac-app-store-white-{loc}.svg">'
            f'<img src="/restora/img/badges/mac-app-store-black-{loc}.svg" width="156" height="40" alt="{esc(t["badge_alt"])}">'
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
                 f'<meta property="og:image" content="{BASE}/restora/img/og-{lang}.png">\n'
                 f'<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
                 f'<meta property="og:image:alt" content="{esc(T[lang]["hero_alt"])}">\n'
                 f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="{esc(title)}">\n'
                 f'<meta name="twitter:description" content="{esc(description)}">\n'
                 f'<meta name="twitter:image" content="{BASE}/restora/img/og-{lang}.png">\n')
    return (f'<!DOCTYPE html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{esc(title)}</title>\n<meta name="description" content="{esc(description)}">\n'
            f'<link rel="canonical" href="{BASE}{path}">\n{links}'
            f'<link rel="icon" type="image/png" href="/restora/img/icon-64.png">\n'
            f'<link rel="apple-touch-icon" href="/restora/img/icon-256.png">\n'
            f'<meta name="theme-color" content="#2c1a28">\n{share}'
            f'<style>{CSS}</style>\n')


def header(lang, current, home=PATH, anchors=True):
    """Icon, Restora, Features · Pricing · FAQ · Support, and the language switch (to `home[lang]`)."""
    t = T[lang]
    base = PATH[lang]
    ids = ["features", "pricing", "faq"]
    nav = "".join(f'<a href="{"" if anchors else base}#{i}">{esc(n)}</a>' for i, n in zip(ids, t["nav"][:3]))
    nav += f'<a href="/restora/support/">{esc(t["nav"][3])}</a>'
    langs = "".join(f'<a href="{home[l]}" hreflang="{l}" lang="{l}"{" aria-current=\"true\"" if l == current else ""}>{l.upper()}</a>'
                    for l in LANGS)
    skip = {"en": "Skip to content", "fr": "Aller au contenu", "es": "Ir al contenido"}[lang]
    return (f'<a class="skip" href="#main">{skip}</a>\n<header class="site-header"><div class="container">'
            f'<a class="brand" href="{base}"><img src="/restora/img/icon-64.png" width="34" height="34" alt="">Restora</a>'
            f'<nav class="nav" aria-label="Restora">{nav}</nav>'
            f'<nav class="langs" aria-label="{esc(t["langs_label"])}">{langs}</nav>'
            f'</div></header>\n')


def footer(lang, extra=""):
    t = T[lang]
    return (f'<footer class="site-footer"><div class="container">'
            f'<span>© 2026 <a href="/">Alifo</a></span><a href="/restora/support/">{esc(t["footer"][0])}</a>'
            f'<a href="/restora/privacy/">{esc(t["footer"][1])}</a><a href="mailto:support@alifo.app">support@alifo.app</a>'
            f'<span class="note">{esc(t["footer_note"])}</span></div></footer>\n')


def json_ld(lang):
    t = T[lang]
    data = {
        "@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Restora",
        "operatingSystem": "macOS 14 or later", "applicationCategory": "MultimediaApplication",
        "description": t["description"], "url": BASE + PATH[lang], "inLanguage": lang,
        "image": f"{BASE}/restora/img/og-{lang}.png",
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
               f'{store_cta(lang)}{picture(f"shots/{lang}/1-print", t["hero_alt"], sizes_hero, eager=True)}</div></div>\n')
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
    out.append(f'<section class="alt-bg" id="formats"><div class="container"><h2>{esc(t["languages_label"])}</h2>'
               f'<p class="intro">{esc(t["languages_intro"])}</p><ul class="pills">'
               + "".join(f'<li>{esc(n)}</li>' for n in FORMATS)
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
            "/restora/support/", "/restora/privacy/"]
    alt = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{BASE}{PATH[l]}"/>' for l in LANGS)
    alt += f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{PATH["en"]}"/>'
    rows = [f"<url><loc>{BASE}{PATH[l]}</loc><lastmod>{LASTMOD}</lastmod>{alt}</url>" for l in LANGS]
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
    for slug, body in (("support", SUPPORT), ("privacy", PRIVACY)):
        p = SITE / "restora" / slug / "index.html"
        p.parent.mkdir(parents=True, exist_ok=True)
        title, desc, content = body
        # Skeleton in the shape rewrap() expects, then the common header, footer and styles.
        p.write_text(f'<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"></header>\n<main>\n{content}\n</main>\n<footer class="site-footer"></footer>', encoding="utf-8")
        rewrap(p, f"/restora/{slug}/")
    print("support, privacy (sitemap.xml: run tools/make_site.py, which lists Restora's pages)")


if __name__ == "__main__":
    main()
