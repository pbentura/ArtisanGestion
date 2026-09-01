<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Cookie } from 'lucide-vue-next'
import { needsConsentDecision, setAnalyticsConsent } from '@/lib/analytics'

const visible = ref(false)

onMounted(() => {
  visible.value = needsConsentDecision()
  // Permet de rouvrir le bandeau depuis la politique de confidentialité.
  window.addEventListener('ag:open-consent', ouvrir)
})

onUnmounted(() => {
  window.removeEventListener('ag:open-consent', ouvrir)
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
      <div
        v-if="visible"
        class="fixed inset-x-0 bottom-0 z-[200] p-3 sm:p-4"
        role="dialog"
        aria-label="Gestion des cookies de mesure d'audience"
      >
        <div class="mx-auto w-full max-w-3xl rounded-2xl border border-border bg-background shadow-2xl p-5 sm:p-6">
          <div class="flex items-start gap-4">
            <div class="hidden sm:flex flex-shrink-0 items-center justify-center w-11 h-11 rounded-xl bg-primary/10 text-primary">
              <Cookie class="w-5 h-5" />
            </div>

            <div class="flex-1 min-w-0">
              <h2 class="text-base font-semibold text-foreground mb-1.5">
                Cookies de mesure d'audience
              </h2>
              <p class="text-sm text-muted-foreground leading-relaxed">
                Nous aimerions mesurer la fréquentation du site avec Google Analytics et Google Ads,
                afin de savoir quelles pages sont utiles aux artisans. Ces cookies ne sont déposés
                qu'avec votre accord. Refuser n'enlève rien au fonctionnement d'ArtisanGestion.
                <RouterLink to="/legal/privacy" class="text-primary underline underline-offset-2 hover:opacity-80">
                  En savoir plus
                </RouterLink>
              </p>

              <!-- Le refus doit être aussi simple et visible que l'acceptation
                   (recommandation CNIL) : mêmes dimensions, même hiérarchie. -->
              <div class="flex flex-col sm:flex-row gap-2.5 mt-4">
                <button
                  type="button"
                  @click="choisir(false)"
                  class="flex-1 h-11 rounded-xl border border-border bg-background text-sm font-semibold text-foreground hover:bg-muted transition-colors"
                >
                  Refuser
                </button>
                <button
                  type="button"
                  @click="choisir(true)"
                  class="flex-1 h-11 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity"
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
