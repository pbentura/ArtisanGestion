<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, CheckCircle2, Play, Shield } from 'lucide-vue-next'
import { useLazyVideo } from '@/composables/useLazyVideo'

const router = useRouter()
const heroVideoRef = ref<HTMLVideoElement | null>(null)

// Le conteneur est masqué sous 1024 px (hidden lg:block) : l'observateur ne se
// déclenche donc jamais sur mobile, où la vidéo n'est de toute façon pas vue.
useLazyVideo(heroVideoRef, '/ArtisanGestionPromo.mp4')
const isVisible = ref(false)

function navigateToAuth() {
  router.push('/auth')
}

function scrollToVideo() {
  const el = document.getElementById('video-section')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  isVisible.value = true
})
</script>

<template>
  <!-- Le bandeau de consentement est fixé en bas de l'écran et recouvrait le
       bouton « Créer mon compte ». On réserve sa hauteur réelle en marge
       basse (--consent-h, publiée par ConsentBanner.vue) : le contenu remonte
       d'autant, quelle que soit la taille du bandeau ou de l'écran. -->
  <section class="relative min-h-screen flex items-center overflow-hidden pt-20 sm:pt-24 pb-[calc(4rem+var(--consent-h,0px))] lg:pt-32 lg:pb-[calc(6rem+var(--consent-h,0px))]">
    <!-- Background -->
    <div class="absolute inset-0 -z-10">
      <!-- Base gradient -->
      <div class="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-background" />

      <!-- Animated beams -->
      <div class="beam-1 faisceau-h absolute top-[20%] -left-[50%] w-[200%] h-[1px] bg-gradient-to-r from-transparent via-primary/20 to-transparent rotate-[-15deg]" />
      <div class="beam-2 faisceau-h-inverse absolute top-[50%] -right-[50%] w-[200%] h-[1px] bg-gradient-to-r from-transparent via-primary/10 to-transparent rotate-[10deg]" />
      <div class="beam-3 faisceau-v absolute -top-[50%] left-[30%] w-[1px] h-[200%] bg-gradient-to-b from-transparent via-primary/15 to-transparent" />

      <!-- Glowing orbs -->
      <div class="absolute top-[-10%] left-[-5%] w-[500px] h-[500px] bg-primary/8 rounded-full blur-[120px]" />
      <div class="absolute bottom-[-10%] right-[-5%] w-[400px] h-[400px] bg-blue-400/5 rounded-full blur-[100px]" />
      <div class="absolute top-[40%] right-[10%] w-[300px] h-[300px] bg-primary/5 rounded-full blur-[80px] animate-pulse" style="animation-duration: 6s" />

      <!-- Grid pattern -->
      <div class="absolute inset-0 opacity-[0.02]" style="background-image: radial-gradient(circle, currentColor 1px, transparent 1px); background-size: 40px 40px;" />
    </div>

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <div class="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
        <!-- Content -->
        <div class="text-center lg:text-left">
          <!-- Badge -->
          <div v-apparait class="hero-badge inline-flex items-center gap-2.5 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-5 sm:mb-8 max-[359px]:hidden">
            <Shield class="h-4 w-4" />
            <span>Conforme facturation électronique 2026</span>
          </div>

          <!-- Headline -->
          <h1 ref="headlineRef" v-apparait class="hero-headline text-3xl max-[359px]:text-2xl sm:text-5xl lg:text-6xl xl:text-[3.5rem] font-extrabold tracking-tight text-foreground mb-4 sm:mb-6 leading-[1.1]">
            <span class="word inline-block">Gagnez&nbsp;</span>
            <span class="word inline-block text-primary relative">
              5h par semaine
              <svg class="absolute -bottom-1 left-0 w-full" viewBox="0 0 200 8" fill="none"><path d="M1 5.5Q50 1 100 4T199 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="opacity-30" /></svg>
            </span>
            <br class="hidden sm:block" />
            <span class="word inline-block">sur votre&nbsp;</span>
            <span class="word inline-block">administratif</span>
          </h1>

          <!-- Subtitle -->
          <p v-apparait class="hero-subtitle text-base max-[359px]:text-sm sm:text-xl text-muted-foreground max-w-xl mx-auto lg:mx-0 mb-6 sm:mb-10 leading-relaxed">
            Rapports d'intervention générés par IA, devis et factures en 2 clics, conformité automatique — pour que vous puissiez vous concentrer sur votre métier d'artisan.
          </p>

          <!-- CTAs -->
          <div v-apparait class="hero-cta flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center lg:justify-start mb-6 sm:mb-10">
            <button
              @click="navigateToAuth"
              class="group relative inline-flex items-center justify-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-2xl text-lg font-semibold shadow-xl shadow-primary/25 hover:shadow-primary/40 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] overflow-hidden"
            >
              <span class="relative z-10">Créer mon compte gratuitement</span>
              <ArrowRight class="relative z-10 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              <div class="absolute inset-0 bg-gradient-to-r from-primary to-blue-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </button>
            <button
              @click="scrollToVideo"
              class="group inline-flex items-center justify-center gap-2 px-8 py-4 bg-card border-2 border-border rounded-2xl text-lg font-semibold text-foreground hover:border-primary/30 hover:bg-muted transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
            >
              <Play class="h-5 w-5 text-primary" />
              Voir la démo
            </button>
          </div>

          <!-- Social proof -->
          <div v-apparait class="hero-proof max-[359px]:hidden flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-6 text-sm text-muted-foreground">
            <div class="flex -space-x-2.5">
              <div class="w-9 h-9 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 border-2 border-background ring-2 ring-background" />
              <div class="w-9 h-9 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 border-2 border-background ring-2 ring-background" />
              <div class="w-9 h-9 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 border-2 border-background ring-2 ring-background" />
              <div class="w-9 h-9 rounded-full bg-gradient-to-br from-violet-400 to-violet-600 border-2 border-background ring-2 ring-background" />
              <div class="w-9 h-9 rounded-full bg-muted flex items-center justify-center text-xs font-semibold border-2 border-background ring-2 ring-background">+</div>
            </div>
            <div class="flex items-center gap-5">
              <span class="flex items-center gap-1.5"><CheckCircle2 class="h-4 w-4 text-success" />Essai gratuit</span>
              <span class="flex items-center gap-1.5"><CheckCircle2 class="h-4 w-4 text-success" />Sans carte bancaire</span>
            </div>
          </div>
        </div>

        <!-- Video Visual -->
        <div v-apparait class="hero-visual relative group hidden lg:block">
          <!-- Glow -->
          <div class="absolute -inset-6 bg-gradient-to-r from-primary/20 via-blue-400/10 to-primary/20 rounded-3xl blur-3xl opacity-40 group-hover:opacity-70 transition-opacity duration-1000" />

          <!-- Browser frame -->
          <div class="relative bg-card rounded-2xl shadow-2xl border border-border/50 overflow-hidden shadow-primary/10 hover:shadow-primary/20 transition-all duration-700 hover:scale-[1.01]">
            <!-- Browser bar -->
            <div class="flex items-center gap-2 px-4 py-3 bg-muted/50 border-b border-border">
              <div class="flex gap-1.5">
                <div class="w-3 h-3 rounded-full bg-red-400/80" />
                <div class="w-3 h-3 rounded-full bg-yellow-400/80" />
                <div class="w-3 h-3 rounded-full bg-green-400/80" />
              </div>
              <div class="flex-1 mx-4">
                <div class="bg-background/80 rounded-lg px-3 py-1.5 text-xs text-muted-foreground flex items-center gap-2">
                  <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                  artisangestion.com
                </div>
              </div>
            </div>

            <!-- L'affiche s'affiche instantanément ; la vidéo n'est
                 téléchargée qu'une fois le hero à l'écran. Sans cela, 7 Mo
                 partaient sur le chemin critique avant même que le visiteur
                 ait lu le titre. -->
            <video
              ref="heroVideoRef"
              poster="/poster-promo.jpg"
              preload="none"
              loop
              muted
              playsinline
              class="w-full h-auto aspect-video object-cover"
            >
              Votre navigateur ne supporte pas la lecture de vidéos.
            </video>

            <!-- Inner border overlay -->
            <div class="absolute inset-0 pointer-events-none ring-1 ring-inset ring-white/10 rounded-2xl" />
          </div>

          <!-- Floating badges -->
          <div class="absolute -top-4 -right-4 bg-card rounded-xl shadow-xl border border-border/50 p-3 animate-bounce-slow" style="animation-duration: 4s">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 rounded-lg bg-success/20 flex items-center justify-center">
                <CheckCircle2 class="h-4 w-4 text-success" />
              </div>
              <div>
                <div class="text-xs font-semibold text-foreground">Rapport généré</div>
                <div class="text-[10px] text-muted-foreground">par l'IA en 3s</div>
              </div>
            </div>
          </div>

          <!-- Bottom floating -->
          <div class="absolute -bottom-3 -left-3 bg-card rounded-xl shadow-xl border border-border/50 p-3">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                <Shield class="h-4 w-4 text-primary" />
              </div>
              <div>
                <div class="text-xs font-semibold text-foreground">Factur-X</div>
                <div class="text-[10px] text-muted-foreground">Conforme 2026</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
