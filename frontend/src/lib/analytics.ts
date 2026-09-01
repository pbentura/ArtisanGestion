/**
 * Mesure du tunnel d'acquisition : Google Analytics 4 + Google Ads.
 *
 * Les identifiants viennent de l'environnement (.env.development /
 * .env.production). Tant qu'ils sont vides, tout ce module est inerte : aucun
 * script n'est chargé, aucun cookie n'est posé. Cela permet de livrer le code
 * avant d'avoir créé les comptes.
 *
 *   VITE_GA4_ID                       G-XXXXXXXXXX
 *   VITE_GOOGLE_ADS_ID                AW-XXXXXXXXX
 *   VITE_ADS_LABEL_SIGN_UP            étiquette de l'action de conversion
 *   VITE_ADS_LABEL_SOCIETE_CREATED    idem
 *   VITE_ADS_LABEL_FIRST_DOCUMENT     idem
 *   VITE_ADS_LABEL_SUBSCRIPTION       idem
 *
 * Les étiquettes se récupèrent dans Google Ads : Objectifs > Conversions >
 * l'action > « Configurer avec Google Tag » ; l'extrait contient un
 * send_to de la forme "AW-123456789/AbC-D_efGh". La partie après la barre
 * oblique est l'étiquette.
 */

const GA4_ID = import.meta.env.VITE_GA4_ID || ''
const ADS_ID = import.meta.env.VITE_GOOGLE_ADS_ID || ''

export type ConversionKey =
  | 'sign_up'
  | 'societe_created'
  | 'first_document_created'
  | 'subscription_started'

const ADS_LABELS: Record<ConversionKey, string> = {
  sign_up: import.meta.env.VITE_ADS_LABEL_SIGN_UP || '',
  societe_created: import.meta.env.VITE_ADS_LABEL_SOCIETE_CREATED || '',
  first_document_created: import.meta.env.VITE_ADS_LABEL_FIRST_DOCUMENT || '',
  subscription_started: import.meta.env.VITE_ADS_LABEL_SUBSCRIPTION || '',
}

declare global {
  interface Window {
    dataLayer: any[]
    gtag: (...args: any[]) => void
  }
}

let initialise = false

export function isAnalyticsEnabled(): boolean {
  return Boolean(GA4_ID || ADS_ID)
}

// ── Consentement ────────────────────────────────────────────────────
//
// Rien n'est chargé tant que l'utilisateur n'a pas explicitement accepté :
// aucun script Google, aucun cookie. C'est plus strict que le seul « Consent
// Mode denied » (qui charge gtag.js et envoie des pings sans cookie), et cela
// évite toute discussion sur l'article 82 de la loi Informatique et Libertés.
// Contrepartie assumée : les événements survenus avant la décision sont perdus.

const CONSENT_KEY = 'ag_consent_analytics_v1'

export type ConsentState = 'granted' | 'denied'

export function getStoredConsent(): ConsentState | null {
  try {
    const valeur = localStorage.getItem(CONSENT_KEY)
    return valeur === 'granted' || valeur === 'denied' ? valeur : null
  } catch {
    return null
  }
}

/** Vrai quand il y a une décision à demander : mesure configurée, choix absent. */
export function needsConsentDecision(): boolean {
  return isAnalyticsEnabled() && getStoredConsent() === null
}

export function setAnalyticsConsent(etat: ConsentState): void {
  try {
    localStorage.setItem(CONSENT_KEY, etat)
  } catch {
    // Stockage bloqué : le choix ne survivra pas à la session, on le respecte
    // quand même pour la navigation en cours.
  }

  if (etat === 'granted') {
    initAnalytics()
    // La vue courante n'a pas pu partir avant la décision : on la rattrape.
    trackPageView(window.location.pathname + window.location.search)
  } else if (typeof window.gtag === 'function') {
    // gtag était déjà chargé (l'utilisateur revient sur son accord) : on coupe
    // la collecte immédiatement, le rechargement fera le reste.
    window.gtag('consent', 'update', {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'denied',
    })
  }
}

/** Charge gtag.js une seule fois, et seulement avec le consentement. */
export function initAnalytics(): void {
  if (initialise || !isAnalyticsEnabled()) return
  if (getStoredConsent() !== 'granted') return
  initialise = true

  window.dataLayer = window.dataLayer || []
  window.gtag = function gtag() {
    window.dataLayer.push(arguments)
  }
  // Consent Mode v2 : l'état est déclaré avant toute configuration.
  window.gtag('consent', 'default', {
    ad_storage: 'granted',
    ad_user_data: 'granted',
    ad_personalization: 'granted',
    analytics_storage: 'granted',
  })
  window.gtag('js', new Date())

  const script = document.createElement('script')
  script.async = true
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA4_ID || ADS_ID}`
  document.head.appendChild(script)

  // L'app est une SPA : gtag ne verrait qu'un seul chargement de page.
  // Les vues sont donc envoyées à la main depuis le routeur.
  if (GA4_ID) window.gtag('config', GA4_ID, { send_page_view: false })
  if (ADS_ID) window.gtag('config', ADS_ID)
}

export function trackPageView(path: string, title?: string): void {
  if (!GA4_ID || typeof window.gtag !== 'function') return
  window.gtag('event', 'page_view', {
    page_path: path,
    page_title: title || document.title,
    page_location: window.location.href,
  })
}

export function trackEvent(nom: string, params: Record<string, any> = {}): void {
  if (typeof window.gtag !== 'function') return
  window.gtag('event', nom, params)
}

/**
 * Envoie une étape du tunnel.
 * L'événement GA4 part toujours (c'est lui qui alimente tes rapports) ;
 * la conversion Google Ads ne part que si l'étiquette est renseignée.
 */
export function trackConversion(cle: ConversionKey, params: Record<string, any> = {}): void {
  if (typeof window.gtag !== 'function') return

  window.gtag('event', cle, params)

  const etiquette = ADS_LABELS[cle]
  if (ADS_ID && etiquette) {
    window.gtag('event', 'conversion', {
      send_to: `${ADS_ID}/${etiquette}`,
      ...params,
    })
  }
}

/**
 * Variante pour les conversions qui ne doivent partir qu'une fois par
 * utilisateur (première inscription, premier document).
 *
 * Le garde-fou est local à l'appareil : un artisan qui change de téléphone
 * peut la déclencher une seconde fois. À 300 € de budget, la source de vérité
 * pour tes propres chiffres reste la base ; ceci sert à alimenter Google.
 */
export function trackConversionOnce(
  cle: ConversionKey,
  identifiant: string | number,
  params: Record<string, any> = {}
): void {
  const memoire = `ag_conv_${cle}_${identifiant}`
  try {
    if (localStorage.getItem(memoire)) return
    localStorage.setItem(memoire, '1')
  } catch {
    // Navigation privée ou stockage bloqué : on envoie sans garde-fou plutôt
    // que de perdre la conversion.
  }
  trackConversion(cle, params)
}
