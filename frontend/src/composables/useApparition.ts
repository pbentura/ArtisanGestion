import type { Directive } from 'vue'
import { prefersReducedMotion } from './useReveal'

/**
 * Directive `v-apparait` : révèle un élément quand il entre à l'écran.
 *
 * Volontairement sans GSAP. Sur les pages d'atterrissage publicitaire, le
 * contenu doit être lisible même si le JavaScript n'a pas tourné : la classe
 * de base laisse l'élément visible, et l'animation n'est qu'une surcouche
 * ajoutée si — et seulement si — la directive s'exécute réellement.
 *
 * C'est l'inverse de l'ancien hero, dont le titre était masqué par défaut et
 * restait invisible dès que l'onglet démarrait en arrière-plan.
 *
 * Usage :
 *   <div v-apparait>…</div>
 *   <div v-apparait="150">…</div>   (retard en millisecondes)
 */
export const vApparait: Directive<HTMLElement, number | undefined> = {
  mounted(el, binding) {
    if (prefersReducedMotion() || typeof IntersectionObserver === 'undefined') return

    const retard = binding.value ?? 0
    el.style.transitionDelay = retard ? `${retard}ms` : ''
    el.classList.add('apparait--arme')

    const observateur = new IntersectionObserver(
      (entrees) => {
        for (const entree of entrees) {
          if (!entree.isIntersecting) continue
          el.classList.add('apparait--vu')
          observateur.disconnect()
        }
      },
      // Déclenche un peu avant l'entrée réelle : l'élément est déjà révélé
      // quand l'utilisateur arrive dessus, l'animation ne le fait pas attendre.
      { rootMargin: '0px 0px -80px 0px', threshold: 0.01 }
    )
    observateur.observe(el)
    ;(el as any).__observateurApparition = observateur
  },

  unmounted(el) {
    ;(el as any).__observateurApparition?.disconnect()
  },
}
