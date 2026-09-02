<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import LandingNavbar from '@/components/landing/LandingNavbar.vue'
import Footer from '@/components/landing/Footer.vue'
import MockupIphone from '@/components/landing/MockupIphone.vue'
import { Camera, Sparkles, PenTool, CheckCircle2, ArrowRight, Smartphone } from 'lucide-vue-next'

import { revealWhenVisible } from '@/composables/useReveal'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()
const activeScreen = ref(0)
const heroRef = ref<HTMLElement | null>(null)
const featuresRef = ref<HTMLElement | null>(null)

const screens = [
  {
    title: 'Votre planning du jour',
    subtitle: 'Toutes vos interventions au même endroit',
    visualType: 'planning'
  },
  {
    title: 'Rapport par IA',
    subtitle: 'L\'IA rédige pour vous en 30 secondes',
    visualType: 'ai-report'
  },
  {
    title: 'Photos du chantier',
    subtitle: 'Prenez et attachez des photos directement',
    visualType: 'camera'
  },
  {
    title: 'Signature sur place',
    subtitle: 'Faites signer le devis ou le rapport',
    visualType: 'signature'
  }
]

const usages = [
  { icon: Camera, title: 'Photos sur le vif', desc: 'Sauvegardées dans le dossier client, sans polluer votre galerie perso.' },
  { icon: PenTool, title: 'Signature tactile', desc: 'Validation immédiate par le client, pas besoin d\'imprimer.' },
  { icon: Sparkles, title: 'IA hors-ligne', desc: 'Dictez vos notes même sans réseau, le rapport se génère plus tard.' },
]

function navigateToAuth() {
  router.push('/auth')
}

let nettoyerReveal: (() => void) | null = null

onMounted(() => {
  if (!heroRef.value || !featuresRef.value) return

  // Contenu visible en CSS : on n'anime qu'une fois la page affichée (useReveal).
  nettoyerReveal = revealWhenVisible(() => {
    // Hero animations
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
    tl.from('.mobile-hero-text', { y: 30, opacity: 0, duration: 0.8, stagger: 0.2 })
      .from('.iphone-mockup', { y: 100, opacity: 0, duration: 1 }, '-=0.4')

    // Scroll storytelling for iPhone
    ScrollTrigger.create({
      trigger: '.scroll-story-container',
      start: 'top top',
      end: '+=200%',
      pin: true,
      onUpdate: (self) => {
        // Calculate which screen should be active based on progress (0 to 1)
        let index = Math.floor(self.progress * screens.length)
        if (index >= screens.length) index = screens.length - 1
        activeScreen.value = index
      }
    })
  })
})

onUnmounted(() => nettoyerReveal?.())
</script>

<template>
  <div class="overflow-x-hidden min-h-screen flex flex-col bg-background">
    <LandingNavbar />

    <!-- Hero Mobile App -->
    <section ref="heroRef" class="pt-32 pb-12 lg:pt-40 lg:pb-20 relative overflow-hidden">
      <!-- Bg -->
      <div class="absolute inset-0 -z-10">
        <div class="absolute inset-0 bg-gradient-to-b from-primary/5 via-background to-background" />
        <div class="absolute top-[-10%] right-[-5%] w-[400px] h-[400px] bg-primary/10 rounded-full blur-[100px]" />
      </div>

      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div class="grid lg:grid-cols-2 gap-12 lg:gap-8 items-center">
          <!-- Text Content -->
          <div class="text-center lg:text-left max-w-3xl mx-auto lg:mx-0">
            <div class="mobile-hero-text inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-6">
              <Smartphone class="h-4 w-4" />
              Application iOS & Android
            </div>
            <h1 class="mobile-hero-text text-4xl sm:text-5xl lg:text-6xl font-extrabold text-foreground mb-6 tracking-tight leading-tight">
              Votre bureau dans<br />
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500">votre poche</span>
            </h1>
            <p class="mobile-hero-text text-lg text-muted-foreground mb-8">
              Prenez des photos de chantier, générez vos rapports par IA et faites signer vos clients — directement depuis votre smartphone.
            </p>
            <div class="mobile-hero-text flex flex-col sm:flex-row justify-center lg:justify-start gap-4">
              <div class="h-12 px-6 rounded-xl bg-secondary text-secondary-foreground flex items-center justify-center font-medium opacity-50 cursor-not-allowed" title="Bientôt disponible">
                App Store [Bientôt]
              </div>
              <div class="h-12 px-6 rounded-xl bg-secondary text-secondary-foreground flex items-center justify-center font-medium opacity-50 cursor-not-allowed" title="Bientôt disponible">
                Google Play [Bientôt]
              </div>
            </div>
          </div>

          <!-- Hero iPhone Mockup -->
          <div class="flex justify-center lg:justify-end relative perspective-[1000px]">
            <!-- Decorative glow -->
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-primary/30 blur-[100px] rounded-full z-0"></div>
            
            <div class="relative z-10 rotate-y-[-15deg] rotate-x-[5deg] transform-style-3d hover:rotate-y-0 hover:rotate-x-0 transition-transform duration-700 shadow-2xl shadow-primary/20 rounded-[3.5rem]">
              <MockupIphone src="/mobile-app-screenshot.png" alt="App mobile ArtisanGestion" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Storytelling Pinned Section -->
    <section class="scroll-story-container h-screen relative bg-muted/20 border-y border-border/50">
      <div class="container mx-auto h-full flex items-center px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div class="grid lg:grid-cols-2 gap-12 lg:gap-20 w-full items-center">
          <!-- Left: Story Text -->
          <div class="relative h-[200px] lg:h-[300px]">
            <TransitionGroup 
              name="story-text" 
              tag="div"
              enter-active-class="transition-all duration-500 absolute inset-0"
              enter-from-class="opacity-0 translate-y-8"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition-all duration-500 absolute inset-0"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 -translate-y-8"
            >
              <div v-for="(screen, i) in screens" :key="i" v-show="activeScreen === i" class="w-full">
                <div class="text-primary font-semibold mb-2">0{{ i + 1 }} / 04</div>
                <h2 class="text-3xl lg:text-4xl font-bold text-foreground mb-4">{{ screen.title }}</h2>
                <p class="text-xl text-muted-foreground">{{ screen.subtitle }}</p>
              </div>
            </TransitionGroup>
          </div>

          <!-- Right: iPhone Mockup -->
          <div class="flex justify-center perspective-[1000px]">
            <div class="iphone-mockup relative w-[280px] h-[580px] lg:w-[320px] lg:h-[660px] bg-black rounded-[3rem] p-3 shadow-2xl shadow-primary/20 border-4 border-gray-800 rotate-y-[-10deg] rotate-x-[5deg] transform-style-3d">
              <!-- Notch -->
              <div class="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-7 bg-black rounded-b-3xl z-20"></div>
              
              <!-- Screen content -->
              <div class="relative w-full h-full bg-background rounded-[2.25rem] overflow-hidden flex flex-col pt-10">
                <!-- Transition logic for screen content -->
                <div class="absolute inset-0 pt-10 bg-muted/10 transition-opacity duration-300">
                  <!-- screen 1: Planning -->
                  <div v-if="activeScreen === 0" class="p-4 space-y-3">
                    <div class="h-10 bg-card rounded-xl border border-border flex items-center px-4 mb-6">
                      <span class="text-sm font-semibold">Aujourd'hui, 14 Juin</span>
                    </div>
                    <div class="bg-card p-4 rounded-2xl border border-border shadow-sm">
                      <div class="text-xs text-primary font-medium mb-1">09:00 - 11:30</div>
                      <div class="text-sm font-bold mb-1">Plomberie - Fuite Cuisine</div>
                      <div class="text-xs text-muted-foreground">Mme Dubois • Paris 15</div>
                    </div>
                    <div class="bg-card p-4 rounded-2xl border border-border shadow-sm opacity-50">
                      <div class="text-xs text-primary font-medium mb-1">14:00 - 16:00</div>
                      <div class="text-sm font-bold mb-1">Électricité - Tableau</div>
                    </div>
                  </div>

                  <!-- screen 2: AI Report -->
                  <div v-else-if="activeScreen === 1" class="p-4 flex flex-col h-full">
                    <div class="h-10 mb-4 flex items-center justify-between">
                      <span class="font-bold text-sm">Nouveau Rapport</span>
                      <Sparkles class="h-4 w-4 text-primary" />
                    </div>
                    <div class="bg-card p-3 rounded-xl border border-primary/20 mb-3 shadow-sm shadow-primary/5">
                      <p class="text-[10px] text-muted-foreground mb-1">Description (dictée)</p>
                      <p class="text-xs font-medium">J'ai remplacé le siphon de l'évier. Joint défectueux.</p>
                    </div>
                    <div class="flex-1 bg-primary/5 rounded-2xl p-4 border border-primary/10">
                      <div class="w-20 h-2 bg-primary/20 rounded-full mb-3"></div>
                      <div class="space-y-2">
                        <div class="w-full h-1.5 bg-primary/10 rounded-full"></div>
                        <div class="w-5/6 h-1.5 bg-primary/10 rounded-full"></div>
                        <div class="w-full h-1.5 bg-primary/10 rounded-full"></div>
                        <div class="w-4/5 h-1.5 bg-primary/10 rounded-full"></div>
                      </div>
                      <div class="mt-4 flex justify-center">
                        <div class="w-6 h-6 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
                      </div>
                    </div>
                  </div>

                  <!-- screen 3: Camera -->
                  <div v-else-if="activeScreen === 2" class="p-4 h-full relative">
                    <div class="h-full bg-slate-800 rounded-2xl overflow-hidden relative">
                      <div class="absolute inset-0 flex items-center justify-center opacity-30">
                        <Camera class="h-16 w-16 text-white" />
                      </div>
                      <div class="absolute bottom-6 left-0 right-0 flex justify-center gap-6 items-center">
                        <div class="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-md"></div>
                        <div class="w-16 h-16 rounded-full border-4 border-white flex items-center justify-center">
                          <div class="w-12 h-12 bg-white rounded-full"></div>
                        </div>
                        <div class="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-md flex items-center justify-center text-white"><CheckCircle2 class="h-5 w-5" /></div>
                      </div>
                    </div>
                  </div>

                  <!-- screen 4: Signature -->
                  <div v-else-if="activeScreen === 3" class="p-4 h-full flex flex-col">
                    <div class="text-center mb-6 mt-4">
                      <h3 class="font-bold text-sm">Signature requise</h3>
                      <p class="text-[10px] text-muted-foreground">Devis #2026-089</p>
                    </div>
                    <div class="flex-1 bg-card rounded-2xl border-2 border-dashed border-border flex items-center justify-center mb-4">
                      <span class="text-muted-foreground text-xs opacity-50">Signez ici</span>
                      <!-- Pretend signature line -->
                      <svg class="absolute w-3/4 h-1/2 opacity-80" viewBox="0 0 100 50" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10 25 Q 30 10 50 30 T 90 20" stroke-linecap="round" />
                      </svg>
                    </div>
                    <div class="h-12 rounded-xl bg-primary flex items-center justify-center text-primary-foreground text-sm font-bold shadow-lg shadow-primary/30">
                      Valider & Envoyer
                    </div>
                  </div>
                </div>

                <!-- Fake Mobile Bottom Bar -->
                <div class="absolute bottom-1 left-1/2 -translate-x-1/2 w-1/3 h-1 bg-foreground/20 rounded-full"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- App Screenshots Galerie -->
    <section class="py-24 bg-background relative overflow-hidden">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div class="text-center mb-16">
          <h2 class="text-3xl lg:text-4xl font-bold mb-4">Une interface pensée pour vous</h2>
          <p class="text-muted-foreground max-w-2xl mx-auto">Gérez vos documents et suivez vos performances d'un simple coup d'œil, où que vous soyez.</p>
        </div>

        <div class="grid md:grid-cols-2 gap-12 lg:gap-16 items-center justify-center max-w-5xl mx-auto">
          
          <!-- Screenshot 2 -->
          <div class="flex flex-col items-center">
            <div class="relative mb-8 perspective-[1000px]">
              <div class="transform-style-3d hover:scale-105 transition-transform duration-500 shadow-2xl shadow-primary/10 rounded-[3.5rem]">
                <MockupIphone src="/screenshot-facture.png" alt="Vue Facturation" />
              </div>
            </div>
            <h3 class="text-xl font-bold mb-2 text-center">Facturation express</h3>
            <p class="text-center text-muted-foreground text-sm max-w-xs">Générez vos factures en un instant, directement depuis le chantier.</p>
          </div>

          <!-- Screenshot 3 -->
          <div class="flex flex-col items-center">
            <div class="relative mb-8 perspective-[1000px]">
              <div class="transform-style-3d hover:scale-105 transition-transform duration-500 shadow-2xl shadow-primary/10 rounded-[3.5rem]">
                <MockupIphone src="/screenshot-rapport.png" alt="Vue Rapport" />
              </div>
            </div>
            <h3 class="text-xl font-bold mb-2 text-center">Rapports d'intervention</h3>
            <p class="text-center text-muted-foreground text-sm max-w-xs">Consultez et signez vos rapports structurés de manière fluide.</p>
          </div>

        </div>
      </div>
    </section>

    <!-- Usages Terrain -->
    <section class="py-24 bg-background">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div class="text-center mb-16">
          <h2 class="text-3xl font-bold mb-4">Pensé pour le terrain</h2>
        </div>
        <div class="grid md:grid-cols-3 gap-8">
          <div v-for="(usage, i) in usages" :key="i" class="p-8 rounded-3xl bg-card border border-border shadow-sm text-center">
            <div class="w-14 h-14 mx-auto bg-primary/10 rounded-2xl flex items-center justify-center mb-6">
              <component :is="usage.icon" class="h-7 w-7 text-primary" />
            </div>
            <h3 class="text-xl font-bold mb-3">{{ usage.title }}</h3>
            <p class="text-muted-foreground">{{ usage.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Mobile CTA -->
    <section class="py-24 bg-primary/5">
      <div class="container mx-auto px-4 text-center">
        <h2 class="text-3xl font-bold mb-6">Prêt à emporter votre bureau ?</h2>
        <p class="text-muted-foreground mb-8">L'application mobile est incluse dans l'essai gratuit de 14 jours.</p>
        <button
          @click="navigateToAuth"
          class="inline-flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-2xl font-bold shadow-lg shadow-primary/25 hover:scale-105 transition-transform"
        >
          Créer un compte <ArrowRight class="h-5 w-5" />
        </button>
      </div>
    </section>

    <Footer />
  </div>
</template>

<style scoped>
.perspective-\[1000px\] {
  perspective: 1000px;
}
.transform-style-3d {
  transform-style: preserve-3d;
}
</style>
