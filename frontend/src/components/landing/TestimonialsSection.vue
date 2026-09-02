<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { Star, Quote, MessageSquare } from 'lucide-vue-next'

import { revealWhenVisible } from '@/composables/useReveal'

gsap.registerPlugin(ScrollTrigger)

const sectionRef = ref<HTMLElement | null>(null)

const testimonials = [
  {
    name: '[À REMPLACER] Jean-Pierre Durand',
    role: 'Plombier indépendant',
    avatar: 'JP',
    avatarGradient: 'from-blue-500 to-blue-700',
    quote: 'Avant, je passais mes soirées à rédiger des rapports. Maintenant, l\'IA me génère un rapport pro en 30 secondes sur le chantier. J\'ai récupéré mes soirées.',
    stars: 5,
  },
  {
    name: '[À REMPLACER] Sophie Martin',
    role: 'Gérante — Martin Électricité',
    avatar: 'SM',
    avatarGradient: 'from-emerald-500 to-emerald-700',
    quote: 'La conversion devis → facture en un clic, c\'est un game-changer. On est passé de 15 jours à 2 jours de délai de facturation en moyenne.',
    stars: 5,
  },
  {
    name: '[À REMPLACER] Marc Leblanc',
    role: 'Artisan peintre — SASU',
    avatar: 'ML',
    avatarGradient: 'from-amber-500 to-orange-600',
    quote: 'Je n\'y connaissais rien à la facturation électronique. Avec ArtisanGestion, je suis déjà conforme pour 2026 sans avoir rien fait de spécial.',
    stars: 5,
  }
]

let nettoyerReveal: (() => void) | null = null

onMounted(() => {
  if (!sectionRef.value) return

  // Contenu visible en CSS : on n'anime qu'une fois la page affichée (useReveal).
  nettoyerReveal = revealWhenVisible(() => {
    gsap.from('.testimonials-header', {
      scrollTrigger: { trigger: sectionRef.value, start: 'top 80%', once: true },
      y: 30, opacity: 0, duration: 0.6
    })
    gsap.from('.testimonial-card', {
      scrollTrigger: { trigger: '.testimonials-grid', start: 'top 85%', once: true },
      y: 40, opacity: 0, duration: 0.6, stagger: 0.15, ease: 'power3.out'
    })
  })
})

onUnmounted(() => nettoyerReveal?.())
</script>

<template>
  <section ref="sectionRef" class="py-24 lg:py-32 bg-muted/30 relative overflow-hidden">
    <div class="absolute inset-0 -z-10">
      <div class="absolute bottom-0 left-[20%] w-[400px] h-[400px] bg-primary/3 rounded-full blur-[120px]" />
    </div>

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <!-- Header -->
      <div class="testimonials-header text-center mb-16">
        <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-4">
          <MessageSquare class="h-4 w-4" />
          Témoignages
        </span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-foreground mb-6 tracking-tight">
          Ils ont transformé leur gestion
        </h2>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Des artisans comme vous qui ont gagné du temps et de la sérénité.
        </p>
      </div>

      <!-- Grid -->
      <div class="testimonials-grid grid md:grid-cols-3 gap-6">
        <div
          v-for="(t, i) in testimonials"
          :key="i"
          class="testimonial-card group relative rounded-3xl bg-card border border-border/50 p-7 hover:border-primary/20 hover:shadow-xl hover:shadow-primary/5 transition-all duration-500"
        >
          <!-- Quote icon -->
          <Quote class="absolute top-6 right-6 h-8 w-8 text-primary/10 group-hover:text-primary/20 transition-colors" />

          <!-- Stars -->
          <div class="flex gap-0.5 mb-5">
            <Star v-for="s in t.stars" :key="s" class="h-4 w-4 fill-amber-400 text-amber-400" />
          </div>

          <!-- Quote text -->
          <p class="text-foreground leading-relaxed mb-6 relative z-10">
            « {{ t.quote }} »
          </p>

          <!-- Author -->
          <div class="flex items-center gap-3">
            <div :class="['w-11 h-11 rounded-full bg-gradient-to-br flex items-center justify-center text-white font-bold text-sm', t.avatarGradient]">
              {{ t.avatar }}
            </div>
            <div>
              <div class="text-sm font-semibold text-foreground">{{ t.name }}</div>
              <div class="text-xs text-muted-foreground">{{ t.role }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
