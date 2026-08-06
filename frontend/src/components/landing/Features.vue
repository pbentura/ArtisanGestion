<script setup lang="ts">
import { ref, onMounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { Sparkles, FileText, Shield, ArrowRight } from 'lucide-vue-next'

gsap.registerPlugin(ScrollTrigger)

const sectionRef = ref<HTMLElement | null>(null)

// AI typing animation
const aiText = ref('')
const aiFullText = 'Remplacement du robinet mitigeur de la cuisine. Ancien robinet défectueux présentant une fuite au niveau de la base...'
const aiTypingActive = ref(false)

function startTyping() {
  if (aiTypingActive.value) return
  aiTypingActive.value = true
  aiText.value = ''
  let i = 0
  const interval = setInterval(() => {
    if (i < aiFullText.length) {
      aiText.value += aiFullText[i]
      i++
    } else {
      clearInterval(interval)
      setTimeout(() => {
        aiTypingActive.value = false
        aiText.value = ''
      }, 3000)
    }
  }, 30)
}

onMounted(() => {
  if (!sectionRef.value) return

  gsap.from('.bento-header', {
    scrollTrigger: { trigger: sectionRef.value, start: 'top 80%', once: true },
    y: 30, opacity: 0, duration: 0.6, ease: 'power3.out'
  })

  gsap.from('.bento-card', {
    scrollTrigger: { trigger: '.bento-grid', start: 'top 80%', once: true },
    y: 40, opacity: 0, duration: 0.6, stagger: 0.1, ease: 'power3.out'
  })

  // Start AI typing when card is visible
  ScrollTrigger.create({
    trigger: '.bento-ai-card',
    start: 'top 70%',
    once: true,
    onEnter: () => startTyping()
  })
})
</script>

<template>
  <section id="features" ref="sectionRef" class="py-24 lg:py-32 relative overflow-hidden">
    <!-- Subtle bg -->
    <div class="absolute inset-0 -z-10">
      <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/3 rounded-full blur-[120px]" />
      <div class="absolute bottom-0 left-0 w-[400px] h-[400px] bg-blue-400/3 rounded-full blur-[100px]" />
    </div>

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <!-- Header -->
      <div class="bento-header text-center mb-16">
        <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-4">
          <Sparkles class="h-4 w-4" />
          Fonctionnalités
        </span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-foreground mb-6 tracking-tight">
          Tout ce dont vous avez besoin,<br class="hidden sm:block" /> rien de superflu
        </h2>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Des outils pensés pour le quotidien des artisans — pas un logiciel de comptable déguisé.
        </p>
      </div>

      <!-- Bento Grid -->
      <div class="bento-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-5">

        <!-- Card 1: AI Reports -->
        <div class="bento-card bento-ai-card group relative rounded-3xl bg-gradient-to-br from-primary/5 via-card to-card border border-border/50 p-7 overflow-hidden hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5 transition-all duration-500 cursor-default flex flex-col">
          <div class="w-12 h-12 rounded-2xl bg-primary/15 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
            <Sparkles class="h-6 w-6 text-primary" />
          </div>
          <h3 class="text-xl font-bold text-foreground mb-3">Rapports d'intervention</h3>
          <p class="text-muted-foreground text-sm mb-6 leading-relaxed flex-grow">
            Fini les rapports de fin de journée. Décrivez l'intervention en quelques mots sur le chantier, notre IA rédige un compte-rendu professionnel instantanément.
          </p>
          
          <!-- AI Demo Mini -->
          <div class="bg-background rounded-2xl border border-border p-4 shadow-sm w-full">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-2 h-2 rounded-full bg-success animate-pulse" />
              <span class="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Génération IA en cours</span>
            </div>
            <div class="bg-primary/5 rounded-xl p-3 min-h-[80px] border border-primary/10">
              <p class="text-xs text-foreground leading-relaxed">
                {{ aiText }}<span v-if="aiTypingActive" class="inline-block w-0.5 h-3 bg-primary animate-pulse ml-0.5 align-middle" />
              </p>
              <p v-if="!aiTypingActive && !aiText" class="text-xs text-muted-foreground italic">Générer le rapport détaillé...</p>
            </div>
          </div>
        </div>

        <!-- Card 2: Devis -->
        <div class="bento-card group relative rounded-3xl bg-card border border-border/50 p-7 overflow-hidden hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5 transition-all duration-500 cursor-default flex flex-col">
          <div class="w-12 h-12 rounded-2xl bg-emerald-500/15 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
            <FileText class="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
          </div>
          <h3 class="text-xl font-bold text-foreground mb-3">Devis ultra-rapides</h3>
          <p class="text-muted-foreground text-sm leading-relaxed mb-6 flex-grow">
            Créez des devis précis directement chez le client. Utilisez votre catalogue de prestations pré-enregistrées et faites signer immédiatement sur l'écran.
          </p>
          
          <!-- Mini visual -->
          <div class="bg-muted/30 rounded-2xl p-4 border border-border/50 w-full mt-auto">
            <div class="flex items-center justify-between mb-3">
              <span class="text-xs font-bold text-foreground">Devis #2026-089</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-success/15 text-success font-medium">Accepté & Signé</span>
            </div>
            <div class="space-y-2 mb-4">
              <div class="flex justify-between items-center text-xs">
                <span class="text-muted-foreground">Fourniture & Pose</span>
                <span class="font-medium text-foreground">3 200 €</span>
              </div>
              <div class="flex justify-between items-center text-xs">
                <span class="text-muted-foreground">Main d'œuvre (8h)</span>
                <span class="font-medium text-foreground">480 €</span>
              </div>
            </div>
            <div class="h-px bg-border/80 w-full mb-2"></div>
            <div class="flex justify-between items-center">
              <span class="text-xs font-bold text-foreground">Total TTC</span>
              <span class="text-sm font-black text-primary">4 416,00 €</span>
            </div>
          </div>
        </div>

        <!-- Card 3: Factures -->
        <div class="bento-card group relative rounded-3xl bg-card border border-border/50 p-7 overflow-hidden hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5 transition-all duration-500 cursor-default flex flex-col">
          <div class="absolute top-4 right-4">
            <span class="text-[10px] px-2 py-1 rounded-full bg-amber-500/15 text-amber-600 dark:text-amber-400 font-bold">Prêt 2026</span>
          </div>
          <div class="w-12 h-12 rounded-2xl bg-amber-500/15 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
            <Shield class="h-6 w-6 text-amber-600 dark:text-amber-400" />
          </div>
          <h3 class="text-xl font-bold text-foreground mb-3">Facturation & Suivi</h3>
          <p class="text-muted-foreground text-sm leading-relaxed mb-6 flex-grow">
            Transformez un devis en facture en un clic. Suivez les paiements, relancez les impayés et soyez 100% conforme avec la norme obligatoire Factur-X 2026.
          </p>

          <!-- Mini chart / visual -->
          <div class="bg-muted/30 rounded-2xl p-4 border border-border/50 w-full mt-auto">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <ArrowRight class="w-4 h-4 text-primary" />
              </div>
              <div>
                <p class="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Conversion 1-Clic</p>
                <p class="text-xs font-medium text-foreground">Devis → Facture</p>
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-2">
              <div class="bg-background rounded-xl p-2 border border-border flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-success"></span>
                <span class="text-[10px] font-semibold">XML CII (Factur-X)</span>
              </div>
              <div class="bg-background rounded-xl p-2 border border-border flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-success"></span>
                <span class="text-[10px] font-semibold">TVA conforme</span>
              </div>
              <div class="bg-background rounded-xl p-2 border border-border flex items-center gap-2 col-span-2">
                <span class="w-1.5 h-1.5 rounded-full bg-success"></span>
                <span class="text-[10px] font-semibold">Suivi d'encaissement temps réel</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
