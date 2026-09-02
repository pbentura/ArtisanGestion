<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { Cookie } from 'lucide-vue-next'
import { needsConsentDecision, setAnalyticsConsent } from '@/lib/analytics'

const visible = ref(false)
const banniereRef = ref<HTMLElement | null>(null)

// Le hero fait la hauteur de l'écran : un bandeau fixé en bas recouvrira son
// bouton « Créer mon compte » quelle que soit sa taille. On publie donc sa
// hauteur réelle, et le hero s'ampute d'autant (cf. HeroSection.vue).
let observateur: ResizeObserver | null = null

function publierHauteur() {
  const h = banniereRef.value?.getBoundingClientRect().height ?? 0
  document.documentElement.style.setProperty('--consent-h', `${Math.ceil(h)}px`)
}

function oublierHauteur() {
  observateur?.disconnect()
  observateur = null
  document.documentElement.style.removeProperty('--consent-h')
}

watch(visible, async (affiche) => {
  if (!affiche) {
    oublierHauteur()
    return
  }
  await nextTick()
  if (!banniereRef.value) return
  publierHauteur()
  // La hauteur dépend du retour à la ligne du texte : elle change avec la
  // largeur de l'écran et à la rotation du téléphone.
  observateur = new ResizeObserver(publierHauteur)
  observateur.observe(banniereRef.value)
})

onMounted(() => {
  visible.value = needsConsentDecision()
  // Permet de rouvrir le bandeau depuis la politique de confidentialité.
  window.addEventListener('ag:open-consent', ouvrir)
})

onUnmounted(() => {
  window.removeEventListener('ag:open-consent', ouvrir)
  oublierHauteur()
})

function ouvrir() {
  visible.value = true
}

function choisir(accepte: boolean) {
  setAnalyticsConsent(accepte ? 'granted' : 'denied')
  visible.value = false
}
</script>

<template>
  <Teleport to="body">
    <Transition name="consent-slide">
      <!-- Ancré en bas à gauche et volontairement compact : centré et pleine
           largeur, ce bandeau recouvrait le bouton « Créer mon compte » du
           hero — le visiteur venu d'une annonce ne voyait plus le CTA. -->
      <div
        v-if="visible"
        ref="banniereRef"
        class="fixed bottom-0 left-0 right-0 sm:right-auto z-[200] p-3 sm:p-4"
        role="dialog"
        aria-label="Gestion des cookies de mesure d'audience"
      >
        <div class="w-full sm:max-w-sm rounded-2xl border border-border bg-background shadow-2xl p-3.5">
          <div class="flex items-start gap-3">
            <!-- Masquée sur mobile : 48 px de largeur en moins, donc une ligne
                 de texte en moins, donc autant de hero qui reste visible. -->
            <div class="hidden sm:flex flex-shrink-0 items-center justify-center w-9 h-9 rounded-xl bg-primary/10 text-primary">
              <Cookie class="w-4 h-4" />
            </div>

            <div class="flex-1 min-w-0">
              <h2 class="text-sm font-semibold text-foreground mb-0.5">
                Cookies de mesure d'audience
              </h2>
              <!-- Volontairement bref : ce bandeau est fixé au-dessus du hero,
                   chaque ligne de texte en plus masque le CTA d'inscription.
                   Le détail complet est dans la politique de confidentialité. -->
              <p class="text-xs text-muted-foreground leading-snug">
                Refuser n'enlève rien au service.
                <RouterLink to="/legal/privacy" class="text-primary underline underline-offset-2 hover:opacity-80">
                  En savoir plus
                </RouterLink>
              </p>

              <!-- Le refus doit être aussi simple et visible que l'acceptation
                   (recommandation CNIL) : mêmes dimensions, même hiérarchie. -->
              <div class="flex flex-row gap-2 mt-2.5">
                <button
                  type="button"
                  @click="choisir(false)"
                  class="flex-1 h-9 rounded-lg border border-border bg-background text-sm font-semibold text-foreground hover:bg-muted transition-colors"
                >
                  Refuser
                </button>
                <button
                  type="button"
                  @click="choisir(true)"
                  class="flex-1 h-9 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity"
                >
                  Accepter
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.consent-slide-enter-active,
.consent-slide-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.consent-slide-enter-from,
.consent-slide-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
