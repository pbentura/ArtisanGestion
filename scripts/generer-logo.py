#!/usr/bin/env python3
"""
Génère le logo horizontal ArtisanGestion : marque hexagonale + nom.

Le texte est converti en tracés vectoriels : le fichier ne dépend d'aucune
police installée et s'affiche à l'identique chez Stripe, dans les emails et
partout ailleurs. C'est aussi pour cela qu'il ne suffit pas d'écrire du
<text> dans un SVG — la police de rendu varierait d'une machine à l'autre.

Prérequis :
    pip install fonttools
    macOS (utilise Avenir Next, et sips pour la rasterisation)

Utilisation :
    python3 scripts/generer-logo.py frontend/public/logo-horizontal.svg
    sips -s format png frontend/public/logo-horizontal.svg \
         --out frontend/public/logo-horizontal.png

Les couleurs sont celles du thème : --foreground pour « Artisan »,
--primary pour « Gestion » (cf. frontend/src/assets/index.css).
"""
import re, sys
from fontTools.ttLib import TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

POLICE   = "/System/Library/Fonts/Avenir Next.ttc"
INDEX    = 8            # Avenir Next Heavy — proche du font-weight 800 de la navbar
TAILLE   = 132          # hauteur de police, en unités du dessin final
INTERLET = 0            # ajustement d'approche si besoin

SOMBRE = "#0F172A"      # --foreground : « Artisan »
BLEU   = "#2563EB"      # --primary    : « Gestion »

def tracer(texte, police, taille, x, y, couleur):
    """Retourne (chemins SVG, largeur occupée) pour un texte donné."""
    glyphes = police.getGlyphSet()
    cmap = police.getBestCmap()
    upem = police["head"].unitsPerEm
    echelle = taille / upem
    morceaux, avance = [], 0.0
    for car in texte:
        nom = cmap.get(ord(car))
        if nom is None:
            continue
        g = glyphes[nom]
        stylo = SVGPathPen(glyphes)
        # y inversé : l'axe des polices monte, celui de SVG descend.
        g.draw(TransformPen(stylo, Transform(echelle, 0, 0, -echelle,
                                             x + avance, y)))
        d = stylo.getCommands()
        if d:
            morceaux.append(f'<path d="{d}" fill="{couleur}"/>')
        avance += g.width * echelle + INTERLET
    return "\n    ".join(morceaux), avance

col = TTCollection(POLICE)
police = col.fonts[INDEX]
print("police :", police["name"].getDebugName(4))

# ── Marque hexagonale, reprise telle quelle du logo carré ──
source = open("public/logo.svg").read()
defs = re.search(r"<defs>.*?</defs>", source, re.S).group(0)
corps = source[source.index("</defs>") + len("</defs>"):source.rindex("</svg>")]

MARQUE = 240                     # côté de la marque dans le logo final
MARGE  = 28
ECART  = 40                      # espace entre la marque et le nom
LIGNE_BASE = MARGE + MARQUE * 0.5 + TAILLE * 0.36   # centrage optique du texte

x = MARGE + MARQUE + ECART
p1, l1 = tracer("Artisan", police, TAILLE, x, LIGNE_BASE, SOMBRE)
p2, l2 = tracer("Gestion", police, TAILLE, x + l1, LIGNE_BASE, BLEU)

largeur = int(x + l1 + l2 + MARGE)
hauteur = int(MARQUE + MARGE * 2)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largeur} {hauteur}" width="{largeur}" height="{hauteur}">
  {defs}
  <g transform="translate({MARGE}, {MARGE}) scale({MARQUE / 512:.6f})">
    {corps.strip()}
  </g>
  <g>
    {p1}
    {p2}
  </g>
</svg>
'''
open(sys.argv[1], "w").write(svg)
print(f"logo écrit : {largeur}x{hauteur}")
