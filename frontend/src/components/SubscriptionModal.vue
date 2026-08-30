<script setup lang="ts">
import { ref } from 'vue'
import { Check, Sparkles, X, CreditCard, Loader2 } from 'lucide-vue-next'
import { uiStore } from '@/lib/store'
import { apiFetch } from '@/lib/api'

const isAnnual = ref(false)
const loadingPlan = ref<string | null>(null)

const plans = [
  {
    name: 'Indépendant',
    description: 'Pour l\'artisan seul',
    priceMonthly: '19',
    priceAnnual: '15.50',
    features: [
      '1 Utilisateur',
      'Accès IA pour les rapports',
      'Clients, rapports, devis & factures illimités',
      'Signature électronique sur place',
      'PDF avec logo et thème ArtisanGestion',
      'Dashboard complet',
    ],
    cta: 'S\'abonner',
    popular: false,
    gradient: '',
  },
  {
    name: 'Équipe',
    description: 'Pour vous et vos collaborateurs',
    priceMonthly: '39',
    priceAnnual: '32.50',
    features: [
      'Équipe avec gestion des droits',
      'Signature électronique à distance (lien envoyé au client)',
      'Personnalisation des PDF (couleurs et sans logo)',
      'Relances impayés automatiques et paramétrables',
    ],
    cta: 'S\'abonner',
    popular: true,
    gradient: 'from-primary to-blue-700',
  }
]

async function handleSubscribe(plan: any) {
  loadingPlan.value = plan.name
  try {
    const res = await apiFetch('subscriptions/create-checkout-session', {
      method: 'POST',
      // Le montant est fixé côté serveur à partir du plan : ne rien envoyer ici.
      body: JSON.stringify({
        plan_name: plan.name,
        is_annual: isAnnual.value
      })
    })

    if (res.ok) {
      const data = await res.json()
      if (data.checkout_url) {
        window.location.href = data.checkout_url
      }
    } else {
      const errorData = await res.json()
      alert(errorData.detail || "Erreur lors de la création de la session de paiement")
    }
  } catch (error) {
    console.error('Error creating checkout session:', error)
    alert("Une erreur est survenue")
  } finally {
    loadingPlan.value = null
  }
}

function close() {
  uiStore.closeSubscriptionModal()
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="uiStore.showSubscriptionModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-background/80 backdrop-blur-sm" @click="close" />
        
        <div class="relative w-full max-w-5xl bg-background rounded-3xl shadow-2xl border border-border/50 max-h-[90vh] overflow-y-auto">
          <button @click="close" class="absolute top-4 right-4 p-2 rounded-full bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors z-10">
            <X class="w-6 h-6" />
          </button>

          <div class="p-8 sm:p-12">
            <!-- Header -->
            <div class="text-center mb-10">
              <span v-if="!uiStore.subscriptionModalContext.hideTrialBadge" class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-4">
                <CreditCard class="h-4 w-4" />
                {{ uiStore.subscriptionModalContext.badge }}
              </span>
              <h2 class="text-3xl font-bold text-foreground mb-4">
                {{ uiStore.subscriptionModalContext.title }}
              </h2>
              <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
                {{ uiStore.subscriptionModalContext.description }}
              </p>
            </div>

            <!-- Toggle -->
            <div class="flex justify-center mb-10">
              <div class="relative flex items-center p-1 bg-muted/50 rounded-full border border-border/50">
                <button
                  @click="isAnnual = false"
                  class="relative w-36 py-2.5 text-sm font-medium rounded-full transition-colors z-10"
                  :class="!isAnnual ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'"
                >
                  Mensuel
                </button>
                <button
                  @click="isAnnual = true"
                  class="relative w-36 py-2.5 text-sm font-medium rounded-full transition-colors z-10 flex items-center justify-center gap-2"
                  :class="isAnnual ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'"
                >
                  Annuel
                  <span class="text-[10px] font-bold bg-primary/10 text-primary px-1.5 py-0.5 rounded-full">-18%</span>
                </button>
                <div
                  class="absolute left-1 top-1 bottom-1 w-36 bg-background shadow-sm rounded-full transition-transform duration-300 ease-in-out border border-border/50"
                  :class="isAnnual ? 'translate-x-full' : 'translate-x-0'"
                />
              </div>
            </div>

            <!-- Cards -->
            <div class="grid md:grid-cols-2 gap-6 lg:gap-8 max-w-4xl mx-auto items-start">
              <div
                v-for="(plan, i) in plans"
                :key="i"
                class="relative transition-all duration-300"
                :class="plan.popular ? 'lg:scale-105 z-10' : ''"
              >
                <div v-if="plan.popular" class="absolute -top-3.5 left-1/2 -translate-x-1/2 z-20">
                  <span class="inline-flex items-center gap-1 px-4 py-1.5 rounded-full bg-primary text-primary-foreground text-xs font-bold shadow-lg shadow-primary/30">
                    <Sparkles class="h-3 w-3" />
                    Recommandé
                  </span>
                </div>

                <div 
                  class="h-full rounded-3xl overflow-hidden transition-all duration-300 flex flex-col"
                  :class="[
                    plan.popular
                      ? 'bg-card border-2 border-primary/50 shadow-2xl shadow-primary/10'
                      : 'bg-card border border-border/50 hover:border-primary/20 hover:shadow-xl hover:shadow-primary/5'
                  ]"
                >
                  <div v-if="plan.popular" class="h-1 w-full bg-gradient-to-r" :class="plan.gradient" />

                  <div class="p-6 lg:p-8 flex-grow">
                    <div class="mb-6" :class="plan.popular ? 'pt-4' : ''">
                      <h3 class="text-xl font-bold text-foreground mb-1">{{ plan.name }}</h3>
                      <p class="text-sm text-muted-foreground">{{ plan.description }}</p>
                    </div>

                    <div class="mb-8">
                      <div class="flex items-baseline gap-1">
                        <span class="text-5xl font-extrabold text-foreground">{{ isAnnual ? plan.priceAnnual : plan.priceMonthly }}€</span>
                        <span class="text-muted-foreground text-sm">/mois</span>
                      </div>
                      <p class="text-xs text-muted-foreground mt-1">
                        {{ isAnnual ? 'HT, facturé annuellement' : 'HT, sans engagement' }}
                      </p>
                    </div>

                    <ul class="space-y-3 mb-8">
                      <li v-for="(feature, fi) in plan.features" :key="fi" class="flex items-start gap-3">
                        <div class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" :class="plan.popular ? 'bg-primary/15' : 'bg-primary/10'">
                          <Check class="h-3 w-3 text-primary" />
                        </div>
                        <span class="text-sm text-muted-foreground">{{ feature }}</span>
                      </li>
                    </ul>
                  </div>
                  
                  <div class="p-6 pt-0 mt-auto">
                    <button
                      @click="handleSubscribe(plan)"
                      :disabled="loadingPlan === plan.name"
                      class="w-full py-3 px-4 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center gap-2"
                      :class="plan.popular ? 'bg-primary text-primary-foreground hover:shadow-lg hover:shadow-primary/25' : 'bg-muted text-foreground hover:bg-muted/80'"
                    >
                      <Loader2 v-if="loadingPlan === plan.name" class="w-5 h-5 animate-spin" />
                      <span v-else>{{ plan.cta }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}
</style>
