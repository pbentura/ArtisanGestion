<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
// import { Card, CardContent } from '@/components/ui/card'
import { 
  ArrowRight, 
  // BarChart3,
  // FileText,
  // Users,
  // Clock,
  CheckCircle2,
  // TrendingUp
} from 'lucide-vue-next'

const router = useRouter()

function navigateToAuth() {
  router.push('/auth')
}

function scrollToFeatures() {
  const element = document.getElementById('features')
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<template>
  <section class="relative overflow-hidden pt-20 pb-32 lg:pt-32 lg:pb-40">
    <!-- Background decoration -->
    <div class="absolute inset-0 -z-10 overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-background" />
      
      <!-- Animated blobs -->
      <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[120px] animate-pulse-slow" />
      <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary/10 rounded-full blur-[120px] animate-pulse-slow" style="animation-delay: -2s" />
      <div class="absolute top-[20%] right-[10%] w-[30%] h-[30%] bg-primary/5 rounded-full blur-[100px] animate-float" />
      
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-primary/10 rounded-full blur-3xl opacity-50" />
    </div>

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <div class="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
        <!-- Left: Content -->
        <div class="text-center lg:text-left">
          <!-- Badge -->
          <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6 animate-fade-in" style="animation-delay: 0.1s">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
              <span class="relative inline-flex rounded-full h-2 w-2 bg-primary" />
            </span>
            Nouveau : Gestion des interventions disponible
          </div>

          <!-- Title -->
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-foreground mb-6 animate-slide-up" style="animation-delay: 0.2s">
            Gérez vos
            <span class="text-primary relative inline-block">
              devis
              <div class="absolute -bottom-1 left-0 w-full h-1 bg-primary/20 rounded-full" />
            </span>,
            <span class="text-primary relative inline-block">
              factures
              <div class="absolute -bottom-1 left-0 w-full h-1 bg-primary/20 rounded-full" />
            </span>
            et
            <span class="text-primary relative inline-block">
              interventions
              <div class="absolute -bottom-1 left-0 w-full h-1 bg-primary/20 rounded-full" />
            </span>
            en toute simplicité
          </h1>

          <!-- Subtitle -->
          <p class="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto lg:mx-0 mb-8 leading-relaxed animate-slide-up" style="animation-delay: 0.3s">
            ArtisanGestion simplifie la gestion quotidienne des artisans et PME. Gagnez du temps, organisez votre activité et suivez votre chiffre d'affaires en un seul endroit.
          </p>

          <!-- CTAs -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start mb-12 animate-slide-up" style="animation-delay: 0.4s">
            <Button 
              size="lg" 
              class="rounded-full px-8 py-6 text-lg font-semibold shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all hover:scale-105 active:scale-95"
              @click="navigateToAuth"
            >
              Commencer gratuitement
              <ArrowRight class="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button 
              variant="outline" 
              size="lg" 
              class="rounded-full px-8 py-6 text-lg font-semibold border-2 hover:bg-muted transition-all hover:scale-105 active:scale-95"
              @click="scrollToFeatures"
            >
              <ArrowRight class="mr-2 h-5 w-5 rotate-90" />
              Voir les fonctionnalités
            </Button>
          </div>

          <!-- Social proof -->
          <div class="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-6 text-sm text-muted-foreground animate-fade-in" style="animation-delay: 0.5s">
            <div class="flex -space-x-2">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 border-2 border-background hover:translate-y-[-4px] transition-transform cursor-help" />
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-green-600 border-2 border-background hover:translate-y-[-4px] transition-transform cursor-help" style="transition-delay: 0.05s" />
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 border-2 border-background hover:translate-y-[-4px] transition-transform cursor-help" style="transition-delay: 0.1s" />
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 border-2 border-background hover:translate-y-[-4px] transition-transform cursor-help" style="transition-delay: 0.15s" />
              <div class="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-medium border-2 border-background">
                +500
              </div>
            </div>
            <div class="flex items-center gap-4">
              <div class="flex items-center gap-1 group cursor-default">
                <CheckCircle2 class="h-4 w-4 text-success group-hover:scale-125 transition-transform" />
                <span>Essai gratuit</span>
              </div>
              <div class="flex items-center gap-1 group cursor-default">
                <CheckCircle2 class="h-4 w-4 text-success group-hover:scale-125 transition-transform" />
                <span>Sans carte bancaire</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Video Demo -->
        <div class="relative group animate-reveal" style="animation-delay: 0.3s">
          <!-- Background Glow -->
          <div class="absolute -inset-4 bg-gradient-to-r from-primary/30 to-secondary/30 rounded-3xl blur-2xl opacity-50 group-hover:opacity-80 transition duration-1000 group-hover:duration-500 animate-pulse-slow" />
          
          <div class="relative bg-card rounded-2xl shadow-2xl border border-border/50 overflow-hidden shadow-primary/20 hover:shadow-primary/40 transition-all duration-500 hover:scale-[1.02]">
            <video 
              src="/video.mov" 
              autoplay 
              loop 
              muted 
              playsinline
              class="w-full h-auto aspect-video object-cover"
            >
              Votre navigateur ne supporte pas la lecture de vidéos.
            </video>
            
            <!-- Video Overlay for depth -->
            <div class="absolute inset-0 pointer-events-none ring-1 ring-inset ring-white/20 rounded-2xl" />
            
            <!-- Reflection effect -->
            <div class="absolute inset-0 bg-gradient-to-tr from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
          </div>

          <!-- Bottom decoration -->
          <div class="absolute -bottom-6 -left-6 w-32 h-32 bg-primary/20 rounded-full blur-3xl animate-float -z-10" />
          <div class="absolute -top-6 -right-6 w-24 h-24 bg-secondary/20 rounded-full blur-2xl animate-float -z-10" style="animation-delay: -3s" />
        </div>
      </div>
    </div>
  </section>
</template>
