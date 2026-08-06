<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { Sparkles, AlignLeft, AlignCenter, AlignJustify } from 'lucide-vue-next'

gsap.registerPlugin(ScrollTrigger)

const sectionRef = ref<HTMLElement | null>(null)
const videoRef = ref<HTMLVideoElement | null>(null)

onMounted(() => {
  if (videoRef.value) {
    // Play video faster as requested
    videoRef.value.playbackRate = 1.5
  }

  if (!sectionRef.value) return
  nextTick(() => {
    setTimeout(() => {
      gsap.from('.ai-rapport-header', {
        scrollTrigger: { trigger: sectionRef.value, start: 'top 80%', once: true },
        y: 30, opacity: 0, duration: 0.6
      })

      gsap.from('.ai-rapport-ui', {
        scrollTrigger: { trigger: sectionRef.value, start: 'top 70%', once: true },
        x: -40, opacity: 0, duration: 0.8, ease: 'power3.out'
      })

      gsap.from('.ai-rapport-video', {
        scrollTrigger: { trigger: sectionRef.value, start: 'top 70%', once: true },
        x: 40, opacity: 0, duration: 0.8, ease: 'power3.out', delay: 0.2
      })

      ScrollTrigger.refresh()
    }, 150)
  })
})
</script>

<template>
  <section ref="sectionRef" class="py-24 lg:py-32 bg-muted/20 relative overflow-hidden">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      
      <!-- Header -->
      <div class="ai-rapport-header text-center mb-16 max-w-3xl mx-auto">
        <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-4 border border-primary/20">
          <Sparkles class="h-4 w-4" />
          Intelligence Artificielle
        </span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-foreground mb-6 tracking-tight">
          L'IA rédige pour vous. <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500">En 10 secondes.</span>
        </h2>
        <p class="text-lg text-muted-foreground">
          Fini la corvée des rapports en fin de journée. Dictez ou tapez quelques mots-clés, et notre IA se charge de générer un rapport professionnel structuré, prêt à être envoyé.
        </p>
      </div>

      <!-- Content Grid -->
      <div class="grid lg:grid-cols-12 gap-8 lg:gap-12 items-center">
        
        <!-- Left: UI Replica -->
        <div class="ai-rapport-ui lg:col-span-5 w-full max-w-md mx-auto lg:max-w-none">
          <!-- Fake Modal card -->
          <div class="relative w-full bg-card border border-border rounded-2xl shadow-xl overflow-hidden transform rotate-[-2deg] hover:rotate-0 transition-transform duration-500">
            <!-- Header -->
            <div class="px-6 pt-6 pb-4 bg-gradient-to-br from-primary/5 via-card to-card border-b border-border">
              <div class="flex items-start gap-3">
                <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Sparkles class="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 class="text-lg font-bold text-foreground">Générer avec l'IA</h3>
                  <p class="text-sm text-muted-foreground leading-snug">Quelques informations suffisent pour rédiger un rapport professionnel</p>
                </div>
              </div>
            </div>

            <!-- Form -->
            <div class="px-6 py-5 space-y-5">
              <!-- Type -->
              <div>
                <label class="block text-sm font-medium text-foreground mb-1.5">Type d'intervention <span class="text-destructive">*</span></label>
                <div class="w-full px-3 py-2.5 bg-background border border-input rounded-lg flex justify-between items-center text-foreground text-sm cursor-default opacity-80">
                  <span>Plomberie</span>
                  <svg class="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </div>
              </div>

              <!-- Description -->
              <div>
                <label class="block text-sm font-medium text-foreground mb-1.5">Description rapide <span class="text-destructive">*</span></label>
                <div class="w-full h-24 px-3 py-2.5 bg-background border border-primary/50 ring-2 ring-primary/20 rounded-lg text-foreground text-sm cursor-default">
                  Remplacement du chauffe-eau défectueux chez Mme Dupont. Fuite au niveau du raccord réparée, installation du nouveau modèle 150L, test de pression OK.
                  <span class="inline-block w-[2px] h-[1em] bg-primary animate-pulse align-middle ml-1"></span>
                </div>
              </div>

              <!-- Longueur -->
              <div>
                <label class="block text-sm font-medium text-foreground mb-2">Longueur du rapport</label>
                <div class="grid grid-cols-3 gap-2 pointer-events-none">
                  <div class="flex flex-col items-center gap-1.5 p-2 rounded-xl border-2 border-border opacity-50">
                    <AlignLeft class="w-4 h-4 text-muted-foreground" />
                    <span class="text-[10px] font-semibold text-foreground">Court</span>
                  </div>
                  <div class="flex flex-col items-center gap-1.5 p-2 rounded-xl border-2 border-primary bg-primary/5 shadow-sm">
                    <AlignCenter class="w-4 h-4 text-primary" />
                    <span class="text-[10px] font-semibold text-primary">Normal</span>
                  </div>
                  <div class="flex flex-col items-center gap-1.5 p-2 rounded-xl border-2 border-border opacity-50">
                    <AlignJustify class="w-4 h-4 text-muted-foreground" />
                    <span class="text-[10px] font-semibold text-foreground">Long détaillé</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="px-6 pb-6 pt-2">
              <div class="w-full py-3 bg-primary text-primary-foreground rounded-xl text-sm font-bold flex items-center justify-center gap-2 shadow-lg shadow-primary/30 opacity-90">
                <Sparkles class="w-4 h-4" />
                Générer le rapport
              </div>
            </div>
          </div>
          
          <!-- Decor elements -->
          <div class="absolute -z-10 top-1/2 left-0 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-primary/20 blur-[80px] rounded-full"></div>
        </div>

        <!-- Right: Video -->
        <div class="ai-rapport-video lg:col-span-7">
          <div class="relative rounded-2xl overflow-hidden border border-border/50 shadow-2xl bg-black">
            <!-- Browser-like header -->
            <div class="absolute top-0 left-0 right-0 h-10 bg-black/60 backdrop-blur-md flex items-center px-4 gap-2 z-10 border-b border-white/10">
              <div class="w-3 h-3 rounded-full bg-red-500/80"></div>
              <div class="w-3 h-3 rounded-full bg-yellow-500/80"></div>
              <div class="w-3 h-3 rounded-full bg-green-500/80"></div>
              <div class="ml-4 text-xs text-white/50 font-medium">Rédaction en cours...</div>
            </div>
            
            <video
              ref="videoRef"
              src="/demo-ia-rapport.mov"
              autoplay
              loop
              muted
              playsinline
              class="w-full h-auto mt-10 rounded-b-2xl object-cover"
            ></video>
            
            <!-- Shimmer effect overlay -->
            <div class="absolute inset-0 pointer-events-none rounded-2xl ring-1 ring-inset ring-white/10"></div>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>
