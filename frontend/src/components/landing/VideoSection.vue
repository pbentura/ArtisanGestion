<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useLazyVideo } from '@/composables/useLazyVideo'
import { Play, Pause, Volume2, VolumeX } from 'lucide-vue-next'

import { revealWhenVisible } from '@/composables/useReveal'

gsap.registerPlugin(ScrollTrigger)

const sectionRef = ref<HTMLElement | null>(null)
const videoRef = ref<HTMLVideoElement | null>(null)
const isPlaying = ref(false)

// Cette section se regarde sur décision de l'artisan : on prépare la source
// sans lancer la lecture, l'affiche et le bouton « lire » font le reste.
useLazyVideo(videoRef, '/ArtisanGestionPromo.mp4', { autoPlay: false })
const isMuted = ref(true)
const showOverlay = ref(true)

function togglePlay() {
  if (!videoRef.value) return
  if (videoRef.value.paused) {
    videoRef.value.play()
    isPlaying.value = true
    isMuted.value = false
    videoRef.value.muted = false
    showOverlay.value = false
  } else {
    videoRef.value.pause()
    isPlaying.value = false
    showOverlay.value = true
  }
}

function toggleMute() {
  if (!videoRef.value) return
  videoRef.value.muted = !videoRef.value.muted
  isMuted.value = videoRef.value.muted
}

let nettoyerReveal: (() => void) | null = null

onMounted(() => {
  if (!sectionRef.value) return

  // Contenu visible en CSS : on n'anime qu'une fois la page affichée (useReveal).
  nettoyerReveal = revealWhenVisible(() => {
    nextTick(() => {
      setTimeout(() => {
        gsap.from('.video-header', {
          scrollTrigger: { trigger: sectionRef.value, start: 'top 80%', once: true },
          y: 30, opacity: 0, duration: 0.6, ease: 'power3.out'
        })
        gsap.from('.video-frame', {
          scrollTrigger: { trigger: '.video-frame', start: 'top 85%', once: true },
          y: 50, opacity: 0, scale: 0.96, duration: 0.8, ease: 'power3.out'
        })

        ScrollTrigger.refresh()
      }, 150)
    })
  })
})

onUnmounted(() => nettoyerReveal?.())
</script>

<template>
  <section id="video-section" ref="sectionRef" class="py-24 lg:py-32 bg-muted/30 relative overflow-hidden">
    <!-- Bg -->
    <div class="absolute inset-0 -z-10">
      <div class="absolute top-[50%] left-[50%] -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-[150px]" />
    </div>

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-5xl">
      <!-- Header -->
      <div class="video-header text-center mb-12">
        <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-4">
          <Play class="h-4 w-4" />
          Démo
        </span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-foreground mb-4 tracking-tight">
          Découvrez ArtisanGestion en 40 secondes
        </h2>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Du rapport d'intervention à la facture envoyée — voyez comment tout s'enchaîne.
        </p>
      </div>

      <!-- Video Frame (Glassmorphism browser) -->
      <div class="video-frame relative group">
        <!-- Glow -->
        <div class="absolute -inset-4 bg-gradient-to-r from-primary/15 via-blue-400/10 to-primary/15 rounded-[2rem] blur-2xl opacity-40 group-hover:opacity-60 transition-opacity duration-700" />

        <div class="relative rounded-2xl lg:rounded-3xl overflow-hidden border border-border/50 bg-card shadow-2xl shadow-primary/5 backdrop-blur-sm">
          <!-- Browser bar -->
          <div class="flex items-center justify-between px-4 lg:px-5 py-3 bg-muted/50 border-b border-border/50">
            <div class="flex items-center gap-2">
              <div class="flex gap-1.5">
                <div class="w-3 h-3 rounded-full bg-red-400/70" />
                <div class="w-3 h-3 rounded-full bg-yellow-400/70" />
                <div class="w-3 h-3 rounded-full bg-green-400/70" />
              </div>
              <div class="hidden sm:block ml-3 bg-background/80 rounded-lg px-3 py-1.5 text-xs text-muted-foreground min-w-[200px]">
                🔒 artisangestion.com
              </div>
            </div>
            <!-- Controls -->
            <div class="flex items-center gap-2">
              <button @click="toggleMute" class="p-1.5 rounded-lg hover:bg-muted transition-colors" :title="isMuted ? 'Activer le son' : 'Couper le son'">
                <VolumeX v-if="isMuted" class="h-4 w-4 text-muted-foreground" />
                <Volume2 v-else class="h-4 w-4 text-foreground" />
              </button>
            </div>
          </div>

          <!-- Video -->
          <div class="relative cursor-pointer" @click="togglePlay">
            <!-- Lecture à la demande : la source n'est posée qu'à
                 l'approche de la section (cf. useLazyVideo). -->
            <video
              ref="videoRef"
              poster="/poster-promo.jpg"
              muted
              playsinline
              loop
              preload="none"
              class="w-full aspect-video object-cover"
            />

            <!-- Play overlay -->
            <Transition
              enter-active-class="transition-all duration-300"
              enter-from-class="opacity-0 scale-110"
              enter-to-class="opacity-100 scale-100"
              leave-active-class="transition-all duration-300"
              leave-from-class="opacity-100 scale-100"
              leave-to-class="opacity-0 scale-95"
            >
              <div v-if="showOverlay" class="absolute inset-0 flex items-center justify-center bg-black/20 backdrop-blur-[2px]">
                <div class="w-20 h-20 lg:w-24 lg:h-24 rounded-full bg-white/90 dark:bg-white/20 backdrop-blur-md flex items-center justify-center shadow-2xl hover:scale-110 transition-transform duration-300 cursor-pointer">
                  <Play class="h-8 w-8 lg:h-10 lg:w-10 text-primary ml-1" />
                </div>
              </div>
            </Transition>

            <!-- Pause button (visible when playing) -->
            <Transition
              enter-active-class="transition-opacity duration-200"
              enter-from-class="opacity-0"
              enter-to-class="opacity-100"
              leave-active-class="transition-opacity duration-200"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
            >
              <div v-if="isPlaying && !showOverlay" class="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <button @click.stop="togglePlay" class="p-2 rounded-full bg-black/50 backdrop-blur-md text-white hover:bg-black/70 transition-colors">
                  <Pause class="h-5 w-5" />
                </button>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
