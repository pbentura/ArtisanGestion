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

let ecrites = 0
for (const [chemin, meta] of Object.entries(pages)) {
  const url = chemin === '/' ? `${SITE}/` : `${SITE}${chemin}`
  const html = remplacer(gabarit, { ...meta, url })

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
console.log(`\n${ecrites} page(s) prérendue(s).`)
