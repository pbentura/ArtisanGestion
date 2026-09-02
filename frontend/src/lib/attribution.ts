/**
 * Attribution de l'acquisition.
 *
 * Sans ceci, impossible de savoir quel mot-clé ou quelle campagne a produit un
 * artisan qui paie : Google Ads sait compter les conversions, mais il ne sait
 * pas vous dire lesquelles sont devenues des abonnements six semaines plus
 * tard. On capture donc la provenance au tout premier chargement, on la garde
 * localement, et on la rattache au compte dès qu'il est authentifié.
 *
 * Deux principes :
 *
 * 1. **Premier contact.** Ce qui compte, c'est la source qui a fait découvrir
 *    le produit, pas la dernière visite. Une fois enregistrée, la provenance
 *    n'est plus écrasée — ni ici, ni côté serveur.
 * 2. **Aucune donnée personnelle.** Uniquement des paramètres de campagne et
 *    l'origine du référent (le domaine, pas l'URL complète). Rien qui
 *    identifie la personne, donc rien qui relève du consentement cookies :
 *    c'est du stockage nécessaire au service demandé (créer le compte), et
 *    l'information n'est transmise qu'avec le compte lui-même.
 */

const CLE_STOCKAGE = 'ag_attribution_v1'
const CLE_ENVOYEE = 'ag_attribution_envoyee_v1'

/** Identifiants de clic publicitaire posés par Google sur l'URL de destination. */
const PARAMS_CLIC = ['gclid', 'gbraid', 'wbraid'] as const

const PARAMS_UTM = [
  'utm_source',
  'utm_medium',
  'utm_campaign',
  'utm_term',
  'utm_content',
] as const

export interface Attribution {
  gclid?: string
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
  utm_term?: string
  utm_content?: string
  landing_page?: string
  referrer?: string
}

/** Tronque : une valeur anormalement longue vient d'un bot ou d'une injection. */
function propre(valeur: string | null): string | undefined {
  if (!valeur) return undefined
  const v = valeur.trim().slice(0, 255)
  return v || undefined
}

/** Domaine du référent uniquement — l'URL complète n'apporte rien et en dit trop. */
function origineReferent(): string | undefined {
  try {
    if (!document.referrer) return undefined
    const url = new URL(document.referrer)
    // Une navigation interne n'est pas une source d'acquisition.
    if (url.hostname === window.location.hostname) return undefined
    return url.hostname
  } catch {
    return undefined
  }
}

function lire(cle: string): Attribution | null {
  try {
    const brut = localStorage.getItem(cle)
    return brut ? (JSON.parse(brut) as Attribution) : null
  } catch {
    return null
  }
}

/**
 * Enregistre la provenance si elle n'a pas déjà été capturée.
 * À appeler une fois au démarrage, avant que le routeur ne nettoie l'URL.
 */
export function capturerAttribution(): void {
  try {
    if (localStorage.getItem(CLE_STOCKAGE)) return // premier contact déjà connu

    const params = new URLSearchParams(window.location.search)

    const attribution: Attribution = {}
    for (const p of PARAMS_CLIC) {
      const v = propre(params.get(p))
      if (v) {
        attribution.gclid = v
        break
      }
    }
    for (const p of PARAMS_UTM) {
      const v = propre(params.get(p))
      if (v) attribution[p] = v
    }

    const referent = origineReferent()
    if (referent) attribution.referrer = referent

    // Rien d'exploitable : on ne fige pas un « direct » qui empêcherait de
    // capturer la vraie source lors d'une visite ultérieure via une annonce.
    if (Object.keys(attribution).length === 0) return

    attribution.landing_page = window.location.pathname.slice(0, 255)

    localStorage.setItem(CLE_STOCKAGE, JSON.stringify(attribution))
  } catch {
    // Stockage bloqué (navigation privée) : on perd l'attribution, tant pis.
  }
}

/**
 * Rattache la provenance au compte connecté.
 *
 * Idempotent des deux côtés : un drapeau local évite la requête inutile, et le
 * serveur refuse d'écraser une provenance déjà enregistrée.
 */
export async function envoyerAttribution(
  apiFetch: (endpoint: string, options?: RequestInit) => Promise<Response>
): Promise<void> {
  try {
    if (localStorage.getItem(CLE_ENVOYEE)) return

    const attribution = lire(CLE_STOCKAGE)
    if (!attribution) return

    const res = await apiFetch('users/me/attribution', {
      method: 'POST',
      body: JSON.stringify(attribution),
    })

    // 409 = le serveur a déjà une provenance pour ce compte : c'est un succès
    // du point de vue du client, inutile de réessayer à chaque session.
    if (res.ok || res.status === 409) {
      localStorage.setItem(CLE_ENVOYEE, '1')
    }
  } catch {
    // Réseau indisponible : on retentera à la prochaine session.
  }
}
