<script setup lang="ts">
/**
 * Compte à rebours de la période d'essai.
 *
 * Il n'existait nulle part ailleurs que dans les paramètres : l'artisan
 * découvrait la fin de son essai le jour où il se retrouvait bloqué. Un rappel
 * discret mais permanent, qui se fait pressant sur la fin, évite la surprise
 * et donne une raison de s'abonner avant l'échéance.
 */
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Clock, AlertTriangle, ArrowRight } from 'lucide-vue-next'
import { dataStore, uiStore } from '@/lib/store'

const router = useRouter()

// 9999 = abonnement actif (cf. schemas/user.py) : aucun compte à rebours.
const ESSAI_ILLIMITE = 9999

const jours = computed<number | null>(() => {
  const v = dataStore.user.data?.trial_days_remaining
  return typeof v === 'number' ? v : null
})

const abonne = computed(() => jours.value !== null && jours.value >= ESSAI_ILLIMITE)
const termine = computed(() => jours.value === 0)
const urgent = computed(() => jours.value !== null && jours.value > 0 && jours.value <= 3)

const visible = computed(() => jours.value !== null && !abonne.value)

const message = computed(() => {
  if (termine.value) return "Votre période d'essai est terminée"
  const n = jours.value as number
  return n === 1
    ? "Dernier jour d'essai gratuit"
    : `Il vous reste ${n} jours d'essai gratuit`
})

function voirLesOffres() {
  if (termine.value) {
    uiStore.openSubscriptionModal()
    return
  }
  router.push('/app/settings?tab=abonnement')
}
</script>

<template>
  <div
    v-if="visible"
    class="trial-banner"
    :class="{ 'trial-banner--urgent': urgent, 'trial-banner--termine': termine }"
    role="status"
  >
    <component :is="termine ? AlertTriangle : Clock" class="w-4 h-4 flex-shrink-0" />
    <span class="trial-banner__texte">
      {{ message }}
      <span class="trial-banner__detail">
        {{ termine
          ? '— abonnez-vous pour créer de nouveaux documents.'
          : '— vos devis, factures et rapports restent illimités.' }}
      </span>
    </span>
    <button type="button" class="trial-banner__cta" @click="voirLesOffres">
      {{ termine ? "S'abonner" : 'Voir les offres' }}
      <ArrowRight class="w-3.5 h-3.5" />
    </button>
  </div>
</template>

<style scoped>
.trial-banner {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 500;
  background: color-mix(in srgb, var(--primary) 10%, var(--background));
  color: var(--foreground);
  border-bottom: 1px solid color-mix(in srgb, var(--primary) 25%, transparent);
}

.trial-banner--urgent {
  background: color-mix(in srgb, #f59e0b 14%, var(--background));
  border-bottom-color: color-mix(in srgb, #f59e0b 35%, transparent);
}

.trial-banner--termine {
  background: color-mix(in srgb, var(--destructive) 12%, var(--background));
  border-bottom-color: color-mix(in srgb, var(--destructive) 30%, transparent);
}

.trial-banner__texte {
  flex: 1;
  min-width: 0;
}

/* Sur mobile, seul le décompte compte : le reste passerait sur trois lignes. */
.trial-banner__detail {
  color: var(--muted-foreground);
  font-weight: 400;
}

@media (max-width: 640px) {
  .trial-banner__detail {
    display: none;
  }
}

.trial-banner__cta {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
  padding: 0.3125rem 0.75rem;
  border-radius: 0.5rem;
  background: var(--primary);
  color: var(--primary-foreground);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.trial-banner__cta:hover {
  opacity: 0.9;
}
</style>
