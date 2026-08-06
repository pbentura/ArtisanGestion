<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { Check, Sparkles, Zap, ArrowRight, CreditCard } from 'lucide-vue-next'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()
const sectionRef = ref<HTMLElement | null>(null)

const plans = [
  {
    name: 'Gratuit',
    description: 'Pour découvrir et tester',
    price: '0',
    features: [
      'Jusqu\'à 3 clients',
      '5 devis par mois',
      '5 factures par mois',
      '3 rapports IA par mois',
      'Tableau de bord basique',
      'Support par email',
    ],
    cta: 'Commencer gratuitement',
    popular: false,
    gradient: '',
  },
  {
    name: 'Pro',
    description: 'Pour les artisans indépendants',
    price: '19',
    features: [
      'Clients illimités',
      'Devis & factures illimités',
      'Rapports IA illimités',
      'Factur-X conforme 2026',
      'Dashboard complet & objectifs CA',
      'App mobile native',
      'Envoi par email intégré',
      'Export des données',
      'Support prioritaire',
    ],
    cta: 'Essai gratuit 14 jours',
    popular: true,
    gradient: 'from-primary to-blue-700',
  },
  {
    name: 'Business',
    description: 'Pour les petites équipes',
    price: '49',
    features: [
      'Tout du plan Pro',
      'Jusqu\'à 5 utilisateurs',
      'Gestion des permissions',
      'Personnalisation avancée',
      'API d\'intégration',
      'Support téléphonique',
      'Formation incluse',
      'SLA garanti 99.9%',
    ],
    cta: 'Nous contacter',
    popular: false,
    gradient: '',
  }
]

function handleCTA() {
  router.push('/auth')
}

onMounted(() => {
  if (!sectionRef.value) return

  gsap.from('.pricing-header', {
    scrollTrigger: { trigger: sectionRef.value, start: 'top 80%', once: true },
    y: 30, opacity: 0, duration: 0.6
  })
  gsap.from('.pricing-card', {
    scrollTrigger: { trigger: '.pricing-grid', start: 'top 85%', once: true },
    y: 40, opacity: 0, duration: 0.6, stagger: 0.12, ease: 'power3.out'
  })
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

      <!-- Cards -->
      <div class="pricing-grid grid md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto items-start">
        <div
          v-for="(plan, i) in plans"
          :key="i"
          class="pricing-card relative rounded-3xl overflow-hidden transition-all duration-500"
          :class="[
            plan.popular
              ? 'bg-card border-2 border-primary/50 shadow-2xl shadow-primary/10 lg:scale-105 z-10'
              : 'bg-card border border-border/50 hover:border-primary/20 hover:shadow-xl hover:shadow-primary/5'
          ]"
        >
          <!-- Popular badge -->
          <div v-if="plan.popular" class="absolute -top-px left-0 right-0 h-1 bg-gradient-to-r" :class="plan.gradient" />
          <div v-if="plan.popular" class="absolute -top-3.5 left-1/2 -translate-x-1/2 z-10">
            <span class="inline-flex items-center gap-1 px-4 py-1.5 rounded-full bg-primary text-primary-foreground text-xs font-bold shadow-lg shadow-primary/30">
              <Sparkles class="h-3 w-3" />
              Recommandé
            </span>
          </div>

          <div class="p-7 lg:p-8">
            <!-- Plan info -->
            <div class="mb-6" :class="plan.popular ? 'pt-4' : ''">
              <h3 class="text-xl font-bold text-foreground mb-1">{{ plan.name }}</h3>
              <p class="text-sm text-muted-foreground">{{ plan.description }}</p>
            </div>

            <!-- Price -->
            <div class="mb-8">
              <div class="flex items-baseline gap-1">
                <span class="text-5xl font-extrabold text-foreground">{{ plan.price }}€</span>
                <span class="text-muted-foreground text-sm">/mois</span>
              </div>
              <p class="text-xs text-muted-foreground mt-1">HT, sans engagement</p>
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

            <!-- CTA -->
            <button
              @click="handleCTA"
              class="w-full py-4 rounded-2xl font-semibold text-sm transition-all duration-300 flex items-center justify-center gap-2"
              :class="plan.popular
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-primary/40 hover:scale-[1.02] active:scale-[0.98]'
                : 'bg-muted text-foreground hover:bg-primary/10 hover:text-primary'"
            >
              <Zap v-if="plan.popular" class="h-4 w-4" />
              {{ plan.cta }}
              <ArrowRight class="h-4 w-4" />
            </button>
          </div>
        </div>
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
