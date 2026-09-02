/**
 * Garde-fou pour les animations d'entrée de la landing.
 *
 * GSAP avance sur `requestAnimationFrame`. Dans un onglet d'arrière-plan, rAF
 * ne tourne pas : `gsap.from()` (et `gsap.set(..., { opacity: 0 })`) posent
 * l'état de départ immédiatement, puis plus rien ne progresse. Le titre, le
 * sous-titre et les boutons restent figés à `opacity: 0` — la page est vide.
 *
 * Or c'est exactement le cas d'un clic publicitaire ouvert dans un nouvel
 * onglet (clic molette, « ouvrir dans un nouvel onglet ») ou d'un
 * préchargement Chrome. On paie le clic pour une page blanche.
 *
 * Règle appliquée ici : le HTML est visible par défaut, et on ne pose l'état
 * de départ de l'animation qu'une fois la page réellement affichée. Si elle ne
 * l'est jamais, ou si GSAP échoue, le contenu reste simplement lisible.
 */

/** Vrai si l'utilisateur a demandé à limiter les animations (OS / navigateur). */
export function prefersReducedMotion(): boolean {
  try {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  } catch {
    return false
  }
}

/**
 * Exécute `animer` dès que la page est visible, une seule fois.
 *
 * - Page déjà visible : exécution immédiate.
 * - Page masquée (onglet d'arrière-plan, préchargement) : on attend
 *   `visibilitychange`. Le contenu reste affiché normalement en attendant.
 * - `prefers-reduced-motion` : on n'anime pas du tout.
 *
 * Toute erreur est avalée : une animation ratée ne doit jamais coûter
 * l'affichage du contenu.
 *
 * @returns une fonction de nettoyage à appeler dans `onUnmounted`.
 */
export function revealWhenVisible(animer: () => void): () => void {
  if (prefersReducedMotion()) return () => {}

  let fait = false

  const executer = () => {
    if (fait) return
    fait = true
    document.removeEventListener('visibilitychange', surChangement)
    try {
      animer()
    } catch (e) {
      // Le contenu est déjà visible : on se contente de le signaler.
      console.error('[reveal] animation ignorée', e)
    }
  }

  const surChangement = () => {
    if (document.visibilityState === 'visible') executer()
  }

  if (document.visibilityState === 'visible') {
    executer()
  } else {
    document.addEventListener('visibilitychange', surChangement)
  }

  return () => document.removeEventListener('visibilitychange', surChangement)
}
