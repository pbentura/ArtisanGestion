import { onMounted, onUnmounted, type Ref } from 'vue'
import { prefersReducedMotion } from './useReveal'

/**
 * Ne télécharge une vidéo décorative que lorsqu'elle arrive à l'écran.
 *
 * Un `<video autoplay>` est téléchargé dès le chargement de la page, même
 * masqué en CSS. Sur la landing, cela mettait plusieurs mégaoctets sur le
 * chemin critique d'un visiteur venu d'une annonce, avant même qu'il ait lu le
 * titre — et sur mobile, pour une vidéo qu'il ne verra jamais.
 *
 * Le principe : `preload="none"` + une affiche (poster) affichée
 * instantanément, et la source n'est posée qu'au moment où la section entre
 * dans le champ de vision. Le poster reste visible si la lecture échoue.
 */
export function useLazyVideo(
  videoRef: Ref<HTMLVideoElement | null>,
  source: string,
  options: { autoPlay?: boolean; playbackRate?: number } = {}
) {
  const { autoPlay = true, playbackRate } = options
  let observateur: IntersectionObserver | null = null

  /**
   * Attend que la page ait fini de se charger, puis un moment de calme.
   *
   * Le hero est visible dès l'arrivée : sans cette temporisation, sa vidéo
   * entrerait en concurrence avec le CSS et les polices pour la bande passante,
   * et retarderait l'affichage du titre. L'affiche, elle, est déjà là.
   */
  function quandDisponible(action: () => void) {
    const planifier = () => {
      const ric = (window as any).requestIdleCallback
      if (typeof ric === 'function') ric(action, { timeout: 2000 })
      else setTimeout(action, 300)
    }
    if (document.readyState === 'complete') planifier()
    else window.addEventListener('load', planifier, { once: true })
  }

  function charger(video: HTMLVideoElement) {
    if (video.dataset.chargee === '1') return
    video.dataset.chargee = '1'
    quandDisponible(() => {
      video.src = source
      if (playbackRate) video.playbackRate = playbackRate
      // Une vidéo qui démarre seule et tourne en boucle est du mouvement :
      // on la laisse à l'arrêt sur son affiche si l'utilisateur l'a demandé.
      if (!autoPlay || prefersReducedMotion()) {
        video.controls = true
        return
      }
      // Une lecture automatique refusée (économie de données, réglage système)
      // n'est pas une erreur : l'affiche reste à l'écran.
      video.play().catch(() => {})
    })
  }

  onMounted(() => {
    const video = videoRef.value
    if (!video) return

    // Sans IntersectionObserver, on charge tout de suite plutôt que jamais.
    if (typeof IntersectionObserver === 'undefined') {
      charger(video)
      return
    }

    observateur = new IntersectionObserver(
      (entrees) => {
        for (const entree of entrees) {
          if (!entree.isIntersecting) continue
          charger(video)
          observateur?.disconnect()
          observateur = null
        }
      },
      // Un peu d'avance pour que la vidéo soit prête à l'arrivée.
      { rootMargin: '200px' }
    )
    observateur.observe(video)
  })

  onUnmounted(() => {
    observateur?.disconnect()
    observateur = null
  })
}
