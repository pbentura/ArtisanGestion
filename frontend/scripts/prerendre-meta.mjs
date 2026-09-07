/**
 * Prérendu des métadonnées, après `vite build`.
 *
 * L'application est une SPA : le titre et la description sont posés par le
 * routeur, donc par JavaScript. Google exécute le JavaScript et les verra,
 * mais les robots d'aperçu de lien — LinkedIn, WhatsApp, Slack, Messenger —
 * ne le font pas. Sans ce script, un lien vers /devis-factures partagé dans
 * une conversation affiche le titre et la description de la page d'accueil.
 *
 * On écrit donc un index.html par page, identique au bundle mais dont les
 * balises meta sont déjà remplies. Firebase Hosting sert le fichier statique
 * quand il existe, et retombe sur la réécriture SPA sinon.
 *
 * Le corps de page reste rendu côté client : ces robots ne lisent que le
 * <head>, et Google rend le JavaScript. Un prérendu complet imposerait un
 * navigateur sans interface dans la CI pour un gain nul ici.
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const racine = join(dirname(fileURLToPath(import.meta.url)), '..')
const dist = join(racine, 'dist')
const SITE = 'https://artisangestion.com'

const pages = JSON.parse(readFileSync(join(racine, 'src/lib/pages-seo.json'), 'utf8'))
const gabarit = readFileSync(join(dist, 'index.html'), 'utf8')

/**
 * Questions/réponses, relues depuis le module TypeScript.
 *
 * Le fichier n'est pas du JSON : plutôt que d'ajouter une étape de compilation
 * pour trois expressions régulières, on extrait les paires directement. Si le
 * format de faq.ts change, l'extraction rend zéro question et le build échoue
 * plus bas — c'est voulu, un balisage FAQ vide passerait autrement inaperçu.
 */
function lireFaq() {
  const source = readFileSync(join(racine, 'src/lib/faq.ts'), 'utf8')
  const entrees = {}
  const bloc = /^ {2}([a-zA-Z0-9_]+):\s*\{\s*\n\s*question:\s*'((?:[^'\\]|\\.)*)',\s*\n\s*answer:\s*'((?:[^'\\]|\\.)*)',/gm
  for (const [, cle, q, r] of source.matchAll(bloc)) {
    // Les apostrophes sont échappées dans le source TypeScript.
    const denormaliser = (t) => t.replace(/\\'/g, "'").replace(/\\\\/g, '\\')
    entrees[cle] = { question: denormaliser(q), reponse: denormaliser(r) }
  }
  return entrees
}

const faq = lireFaq()
if (Object.keys(faq).length === 0) {
  throw new Error("Aucune question extraite de faq.ts — le format a changé.")
}

/** Échappe le texte inséré dans un attribut HTML. */
const attr = (t) =>
  String(t).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

function remplacer(html, { title, description, image, url }) {
  const paires = [
    [/<title>.*?<\/title>/s, `<title>${attr(title)}</title>`],
    [/<meta name="description" content="[^"]*"\s*\/>/, `<meta name="description" content="${attr(description)}" />`],
    [/<link rel="canonical" href="[^"]*"\s*\/>/, `<link rel="canonical" href="${url}" />`],
    [/<meta property="og:url" content="[^"]*"\s*\/>/, `<meta property="og:url" content="${url}" />`],
    [/<meta property="og:title" content="[^"]*"\s*\/>/, `<meta property="og:title" content="${attr(title)}" />`],
    [/<meta property="og:description" content="[^"]*"\s*\/>/, `<meta property="og:description" content="${attr(description)}" />`],
    [/<meta property="og:image" content="[^"]*"\s*\/>/, `<meta property="og:image" content="${SITE}${image}" />`],
    [/<meta name="twitter:title" content="[^"]*"\s*\/>/, `<meta name="twitter:title" content="${attr(title)}" />`],
    [/<meta name="twitter:description" content="[^"]*"\s*\/>/, `<meta name="twitter:description" content="${attr(description)}" />`],
    [/<meta name="twitter:image" content="[^"]*"\s*\/>/, `<meta name="twitter:image" content="${SITE}${image}" />`],
  ]

  for (const [motif, remplacement] of paires) {
    if (!motif.test(html)) {
      // Une balise absente signifie que index.html a changé sans que ce script
      // suive : mieux vaut échouer le build que déployer des aperçus faux.
      throw new Error(`Balise introuvable dans index.html : ${motif}`)
    }
    html = html.replace(motif, remplacement)
  }
  return html
}

/**
 * Données structurées de la page, injectées avant </head>.
 *
 * Elles sont écrites dans le HTML statique et non posées par le routeur :
 * les robots les lisent alors sans exécuter de JavaScript, et surtout le
 * balisage reste identique à ce que la page affiche — pages-seo.json commande
 * les deux.
 */
function donneesStructurees(chemin, meta, url) {
  const blocs = []

  // L'éditeur, déclaré une fois sur l'accueil et référencé ailleurs.
  if (chemin === '/') {
    blocs.push({
      '@context': 'https://schema.org',
      '@type': 'Organization',
      '@id': `${SITE}/#organisation`,
      name: 'ArtisanGestion',
      url: `${SITE}/`,
      logo: `${SITE}/logo-horizontal.png`,
      areaServed: 'FR',
    })
    blocs.push({
      '@context': 'https://schema.org',
      '@type': 'SoftwareApplication',
      name: 'ArtisanGestion',
      applicationCategory: 'BusinessApplication',
      operatingSystem: 'Web, iOS, Android',
      inLanguage: 'fr-FR',
      url: `${SITE}/`,
      publisher: { '@id': `${SITE}/#organisation` },
      description: meta.description,
      offers: [
        {
          '@type': 'Offer',
          name: 'Indépendant',
          price: '19.00',
          priceCurrency: 'EUR',
          // Une offre par mois : sans cela, Google lit « 19 € » comme un prix
          // d'achat unique et l'affiche ainsi dans les résultats.
          priceSpecification: {
            '@type': 'UnitPriceSpecification',
            price: '19.00',
            priceCurrency: 'EUR',
            billingIncrement: 1,
            unitCode: 'MON',
          },
        },
        {
          '@type': 'Offer',
          name: 'Équipe',
          price: '39.00',
          priceCurrency: 'EUR',
          priceSpecification: {
            '@type': 'UnitPriceSpecification',
            price: '39.00',
            priceCurrency: 'EUR',
            billingIncrement: 1,
            unitCode: 'MON',
          },
        },
      ],
    })
  }

  // Les questions réellement affichées par cette page, et elles seules.
  const cles = meta.faq || []
  if (cles.length) {
    blocs.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      '@id': `${url}#faq`,
      mainEntity: cles.map((cle) => {
        const item = faq[cle]
        if (!item) throw new Error(`Question inconnue dans pages-seo.json : « ${cle} »`)
        return {
          '@type': 'Question',
          name: item.question,
          acceptedAnswer: { '@type': 'Answer', text: item.reponse },
        }
      }),
    })
  }

  return blocs
    .map((b) => `<script type="application/ld+json">${JSON.stringify(b).replace(/</g, '\\u003c')}</script>`)
    .join('\n    ')
}

let ecrites = 0
const entreesSitemap = []

for (const [chemin, meta] of Object.entries(pages)) {
  const url = chemin === '/' ? `${SITE}/` : `${SITE}${chemin}`
  let html = remplacer(gabarit, { ...meta, url })
  html = html.replace('</head>', `  ${donneesStructurees(chemin, meta, url)}\n  </head>`)
  entreesSitemap.push({ url, priorite: meta.priorite ?? 0.5 })

  // Fichier plat (/mobile.html) plutôt que dossier (/mobile/index.html) :
  // avec cleanUrls, Firebase sert /mobile depuis /mobile.html sans redirection,
  // là où un dossier provoque un 301 de /mobile vers /mobile/ — une URL qui ne
  // correspondrait plus à celle déclarée dans Google Ads ni au canonical.
  const cible = chemin === '/' ? join(dist, 'index.html') : join(dist, `${chemin.slice(1)}.html`)
  mkdirSync(dirname(cible), { recursive: true })
  writeFileSync(cible, html)
  ecrites++
  console.log(`  ${chemin.padEnd(24)} ${meta.title}`)
}

// ── sitemap.xml ─────────────────────────────────────────────────────
//
// Généré ici plutôt que posé en fichier statique : la liste des pages vit
// déjà dans pages-seo.json, et un sitemap écrit à la main finirait par citer
// une page supprimée ou en oublier une nouvelle. Seules les pages vitrines y
// figurent — l'application et les URL à jeton sont exclues par robots.txt.
const jour = new Date().toISOString().slice(0, 10)
const sitemap =
  '<?xml version="1.0" encoding="UTF-8"?>\n' +
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
  entreesSitemap
    .map(
      ({ url, priorite }) =>
        `  <url>\n` +
        `    <loc>${url}</loc>\n` +
        `    <lastmod>${jour}</lastmod>\n` +
        `    <changefreq>weekly</changefreq>\n` +
        `    <priority>${priorite.toFixed(1)}</priority>\n` +
        `  </url>`
    )
    .join('\n') +
  '\n</urlset>\n'

writeFileSync(join(dist, 'sitemap.xml'), sitemap)

console.log(`\n${ecrites} page(s) prérendue(s), sitemap.xml et données structurées écrits.`)
