<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { FileText, ClipboardList, Clock, TrendingUp } from 'lucide-vue-next'

import { revealWhenVisible } from '@/composables/useReveal'

gsap.registerPlugin(ScrollTrigger)

const sectionRef = ref<HTMLElement | null>(null)

const stats = [
  { icon: FileText, value: 12500, suffix: '+', label: 'Devis & factures générés', prefix: '' },
  { icon: ClipboardList, value: 8200, suffix: '+', label: 'Rapports d\'intervention', prefix: '' },
  { icon: Clock, value: 5, suffix: 'h', label: 'Gagnées par semaine', prefix: '' },
  { icon: TrendingUp, value: 98, suffix: '%', label: 'De satisfaction client', prefix: '' },
]

const animatedValues = ref(stats.map(() => 0))

let nettoyerReveal: (() => void) | null = null

onMounted(() => {
  if (!sectionRef.value) return

  // Contenu visible en CSS : on n'anime qu'une fois la page affichée (useReveal).
  nettoyerReveal = revealWhenVisible(() => {
    ScrollTrigger.create({
      trigger: sectionRef.value,
      start: 'top 80%',
      once: true,
      onEnter: () => {
        stats.forEach((stat, i) => {
          const obj = { val: 0 }
          gsap.to(obj, {
            val: stat.value,
            duration: 2,
            ease: 'power2.out',
            onUpdate: () => {
              animatedValues.value[i] = Math.round(obj.val)
            }
          })
        })
        gsap.from('.stat-card', {
          y: 30,
          opacity: 0,
          duration: 0.6,
          stagger: 0.12,
          ease: 'power3.out'
        })
      }
    })
  })
})

onUnmounted(() => nettoyerReveal?.())
</script>

<template>
  <section ref="sectionRef" class="py-16 lg:py-20 border-y border-border/50 bg-muted/30">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <div class="text-center mb-8">
        <p class="text-sm font-medium text-muted-foreground uppercase tracking-wider">[À REMPLACER] Chiffres basés sur les données réelles d'utilisation</p>
      </div>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
        <div
          v-for="(stat, index) in stats"
          :key="index"
          class="stat-card text-center group"
        >
          <div class="w-12 h-12 mx-auto mb-4 rounded-2xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 group-hover:scale-110 transition-all duration-300">
            <component :is="stat.icon" class="h-6 w-6 text-primary" />
          </div>
          <div class="text-3xl sm:text-4xl font-extrabold text-foreground mb-1 tabular-nums">
            {{ stat.prefix }}{{ animatedValues[index].toLocaleString('fr-FR') }}{{ stat.suffix }}
          </div>
          <div class="text-sm text-muted-foreground font-medium">{{ stat.label }}</div>
        </div>
      </div>
    </div>
  </section>
</template>
