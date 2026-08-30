<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import { Check, Sparkles, Zap, ArrowRight, CreditCard } from 'lucide-vue-next'
import { useIntersectionObserver } from '@vueuse/core'

const router = useRouter()
const sectionRef = ref<HTMLElement | null>(null)
const isAnnual = ref(false)

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
    cta: 'Essai gratuit 14 jours',
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
    cta: 'Essai gratuit 14 jours',
    popular: true,
    gradient: 'from-primary to-blue-700',
  }
]

function handleCTA() {
  router.push('/auth')
}

onMounted(() => {
  if (!sectionRef.value) return

  // État initial (invisible)
  gsap.set('.pricing-header', { y: 30, opacity: 0 })
  gsap.set('.pricing-card', { y: 40, opacity: 0 })

  // Utiliser l'IntersectionObserver natif via VueUse (beaucoup plus robuste au refresh)
  const { stop } = useIntersectionObserver(
    sectionRef,
    ([{ isIntersecting }]) => {
      if (isIntersecting) {
        gsap.to('.pricing-header', { y: 0, opacity: 1, duration: 0.6 })
        gsap.to('.pricing-card', { y: 0, opacity: 1, duration: 0.6, stagger: 0.12, ease: 'power3.out' })
        
        stop() // Ne jouer qu'une seule fois
      }
    },
    { threshold: 0.15 } // Se déclenche quand 15% de la section est visible
  )
})
</script>

<template>
  <section id="pricing" ref="sectionRef" class="py-24 lg:py-32 relative overflow-hidden">
    <div class="absolute inset-0 -z-10">
      <div class="absolute top-[30%] right-0 w-[400px] h-[400px] bg-primary/3 rounded-full blur-[120px]" />
    </div>

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <!-- Header -->
      <div class="pricing-header text-center mb-16">
        <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-4">
          <CreditCard class="h-4 w-4" />
          Tarifs
        </span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-foreground mb-6 tracking-tight">
          Des prix simples et transparents
        </h2>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Choisissez le plan qui correspond à vos besoins. Sans engagement, annulez à tout moment.
        </p>
      </div>

      <!-- Toggle -->
      <div class="flex justify-center mb-12">
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
          <!-- Sliding indicator -->
          <div
            class="absolute left-1 top-1 bottom-1 w-36 bg-background shadow-sm rounded-full transition-transform duration-300 ease-in-out border border-border/50"
            :class="isAnnual ? 'translate-x-full' : 'translate-x-0'"
          />
        </div>
      </div>

      <!-- Cards -->
      <div class="pricing-grid grid md:grid-cols-2 gap-6 lg:gap-8 max-w-4xl mx-auto items-start">
        <div
          v-for="(plan, i) in plans"
          :key="i"
          class="pricing-card relative transition-all duration-500"
          :class="plan.popular ? 'lg:scale-105 z-10' : ''"
        >
          <div v-if="plan.popular" class="absolute -top-3.5 left-1/2 -translate-x-1/2 z-20">
            <span class="inline-flex items-center gap-1 px-4 py-1.5 rounded-full bg-primary text-primary-foreground text-xs font-bold shadow-lg shadow-primary/30">
              <Sparkles class="h-3 w-3" />
              Recommandé
            </span>
          </div>

          <div 
            class="h-full rounded-3xl overflow-hidden transition-all duration-500"
            :class="[
              plan.popular
                ? 'bg-card border-2 border-primary/50 shadow-2xl shadow-primary/10'
                : 'bg-card border border-border/50 hover:border-primary/20 hover:shadow-xl hover:shadow-primary/5'
            ]"
          >
            <div v-if="plan.popular" class="h-1 w-full bg-gradient-to-r" :class="plan.gradient" />

            <div class="p-7 lg:p-8">
            <!-- Plan info -->
            <div class="mb-6" :class="plan.popular ? 'pt-4' : ''">
              <h3 class="text-xl font-bold text-foreground mb-1">{{ plan.name }}</h3>
              <p class="text-sm text-muted-foreground">{{ plan.description }}</p>
            </div>

            <!-- Price -->
            <div class="mb-8">
              <div class="flex items-baseline gap-1">
                <span class="text-5xl font-extrabold text-foreground">{{ isAnnual ? plan.priceAnnual : plan.priceMonthly }}€</span>
                <span class="text-muted-foreground text-sm">/mois</span>
              </div>
              <p class="text-xs text-muted-foreground mt-1">
                {{ isAnnual ? 'HT, facturé annuellement' : 'HT, sans engagement' }}
              </p>
            </div>

            <!-- Features -->
            <ul class="space-y-3 mb-8">
              <li v-for="(feature, fi) in plan.features" :key="fi" class="flex items-start gap-3">
                <div class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" :class="plan.popular ? 'bg-primary/15' : 'bg-primary/10'">
                  <Check class="h-3 w-3 text-primary" />
                </div>
                <span class="text-sm text-muted-foreground">{{ feature }}</span>
              </li>
            </ul>
          </div>
          </div>
        </div>
      </div>

      <!-- Single CTA -->
      <div class="mt-12 flex justify-center">
        <button
          @click="handleCTA"
          class="px-10 py-4 rounded-2xl font-bold text-base bg-primary text-primary-foreground shadow-xl shadow-primary/25 hover:shadow-primary/40 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 flex items-center justify-center gap-2"
        >
          <Zap class="h-5 w-5" />
          Essai gratuit 14 jours
          <ArrowRight class="h-5 w-5" />
        </button>
      </div>

      <!-- Trust badges -->
      <div class="mt-16 flex flex-wrap items-center justify-center gap-8 text-muted-foreground">
        <div class="flex items-center gap-2">
          <Check class="h-5 w-5 text-success" />
          <span class="text-sm">Sans engagement</span>
        </div>
        <div class="flex items-center gap-2">
          <Check class="h-5 w-5 text-success" />
          <span class="text-sm">Annulation à tout moment</span>
        </div>
        <div class="flex items-center gap-2">
          <Check class="h-5 w-5 text-success" />
          <span class="text-sm">14 jours d'essai gratuit</span>
        </div>
        <div class="flex items-center gap-2">
          <Check class="h-5 w-5 text-success" />
          <span class="text-sm">Données hébergées en France</span>
        </div>
      </div>
    </div>
  </section>
</template>
