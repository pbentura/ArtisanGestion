<script setup lang="ts">
import { ref, onMounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { X, Check, AlertTriangle, Clock, FileX, FolderOpen, Sparkles, FileCheck2, Smartphone, Shield, BarChart3 } from 'lucide-vue-next'

gsap.registerPlugin(ScrollTrigger)

const sectionRef = ref<HTMLElement | null>(null)
const sliderPosition = ref(50)
const isDragging = ref(false)
const containerRef = ref<HTMLElement | null>(null)

const beforeItems = [
  { icon: FileX, text: 'Rapports bâclés sur papier', color: 'text-destructive' },
  { icon: FolderOpen, text: 'Infos éparpillées dans Excel', color: 'text-destructive' },
  { icon: Clock, text: 'Relances de paiement oubliées', color: 'text-destructive' },
  { icon: AlertTriangle, text: 'Non-conforme facturation 2026', color: 'text-warning' },
]

const afterItems = [
  { icon: Sparkles, text: 'Rapports pro générés par l\'IA', color: 'text-success' },
  { icon: FileCheck2, text: 'Tout centralisé en un clic', color: 'text-success' },
  { icon: Smartphone, text: 'Factures envoyées depuis le terrain', color: 'text-success' },
  { icon: Shield, text: 'Factur-X conforme automatiquement', color: 'text-success' },
]

function handleMove(e: MouseEvent | TouchEvent) {
  if (!isDragging.value || !containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
  const x = clientX - rect.left
  const pct = Math.max(10, Math.min(90, (x / rect.width) * 100))
  sliderPosition.value = pct
}

function startDrag() { isDragging.value = true }
function endDrag() { isDragging.value = false }

onMounted(() => {
  document.addEventListener('mousemove', handleMove)
  document.addEventListener('mouseup', endDrag)
  document.addEventListener('touchmove', handleMove)
  document.addEventListener('touchend', endDrag)

  if (!sectionRef.value) return
  gsap.from('.compare-header', {
    scrollTrigger: { trigger: sectionRef.value, start: 'top 80%', once: true },
    y: 30, opacity: 0, duration: 0.6
  })
  gsap.from('.compare-container', {
    scrollTrigger: { trigger: '.compare-container', start: 'top 85%', once: true },
    y: 40, opacity: 0, duration: 0.8, ease: 'power3.out'
  })
})
</script>

<template>
  <section ref="sectionRef" class="py-24 lg:py-32 relative overflow-hidden">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-5xl">
      <!-- Header -->
      <div class="compare-header text-center mb-16">
        <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-4">
          <BarChart3 class="h-4 w-4" />
          Avant / Après
        </span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-foreground mb-6 tracking-tight">
          Dites adieu au chaos administratif
        </h2>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Faites glisser pour comparer votre quotidien avant et après ArtisanGestion.
        </p>
      </div>

      <!-- Compare Container -->
      <div
        ref="containerRef"
        class="compare-container relative rounded-3xl overflow-hidden border border-border/50 shadow-2xl select-none"
        @mousedown.prevent="startDrag"
        @touchstart.prevent="startDrag"
      >
        <div class="flex min-h-[400px] lg:min-h-[450px]">
          <!-- BEFORE side -->
          <div class="flex-1 bg-gradient-to-br from-destructive/5 via-card to-card p-8 lg:p-12" :style="{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }">
            <div class="min-w-[280px] lg:min-w-[400px]">
              <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-destructive/10 text-destructive text-xs font-semibold mb-6">
                <X class="h-3 w-3" />
                Sans ArtisanGestion
              </div>
              <h3 class="text-2xl font-bold text-foreground mb-6">Le quotidien galère</h3>
              <div class="space-y-4">
                <div v-for="(item, i) in beforeItems" :key="i" class="flex items-start gap-3">
                  <div class="w-8 h-8 rounded-lg bg-destructive/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <component :is="item.icon" class="h-4 w-4 text-destructive" />
                  </div>
                  <div>
                    <p class="text-foreground font-medium">{{ item.text }}</p>
                  </div>
                </div>
              </div>
              <div class="mt-8 p-4 rounded-xl bg-destructive/5 border border-destructive/10">
                <p class="text-sm text-destructive font-medium">😩 Résultat : 10h/semaine perdues en administratif</p>
              </div>
            </div>
          </div>

          <!-- AFTER side (overlaid with clip) -->
          <div class="absolute inset-0 bg-gradient-to-br from-success/5 via-card to-card p-8 lg:p-12 flex justify-end" :style="{ clipPath: `inset(0 0 0 ${sliderPosition}%)` }">
            <div class="min-w-[280px] lg:min-w-[400px]">
              <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-success/10 text-success text-xs font-semibold mb-6">
                <Check class="h-3 w-3" />
                Avec ArtisanGestion
              </div>
              <h3 class="text-2xl font-bold text-foreground mb-6">Le quotidien serein</h3>
              <div class="space-y-4">
                <div v-for="(item, i) in afterItems" :key="i" class="flex items-start gap-3">
                  <div class="w-8 h-8 rounded-lg bg-success/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <component :is="item.icon" class="h-4 w-4 text-success" />
                  </div>
                  <div>
                    <p class="text-foreground font-medium">{{ item.text }}</p>
                  </div>
                </div>
              </div>
              <div class="mt-8 p-4 rounded-xl bg-success/5 border border-success/10">
                <p class="text-sm text-success font-medium">🎉 Résultat : 5h/semaine récupérées, zéro stress</p>
              </div>
            </div>
          </div>

          <!-- Slider handle -->
          <div
            class="absolute top-0 bottom-0 w-1 bg-primary z-20 cursor-col-resize"
            :style="{ left: sliderPosition + '%' }"
          >
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-primary shadow-xl shadow-primary/30 flex items-center justify-center cursor-col-resize">
              <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M8 6l-4 6 4 6M16 6l4 6-4 6" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
