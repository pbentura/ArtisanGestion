<script setup lang="ts">
import { Card, CardContent } from '@/components/ui/card'
import { 
  Zap, 
  FolderKanban, 
  TrendingUp,
  Award,
  CheckCircle2
} from 'lucide-vue-next'

const benefits = [
  {
    icon: Zap,
    title: 'Gain de temps',
    description: 'Réduisez de 80% le temps passé sur vos tâches administratives. Générez vos documents en quelques secondes.',
    stat: '-80%',
    statLabel: 'temps admin',
    color: 'from-yellow-500 to-orange-500'
  },
  {
    icon: FolderKanban,
    title: 'Organisation centralisée',
    description: 'Finis les dossiers éparpillés. Toutes vos informations clients, rapports, devis et factures au même endroit.',
    stat: '100%',
    statLabel: 'centralisé',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    icon: TrendingUp,
    title: 'Suivi du chiffre d\'affaires',
    description: 'Visualisez votre CA en temps réel, identifiez vos meilleurs clients et prenez les bonnes décisions.',
    stat: '+25%',
    statLabel: 'visibilité',
    color: 'from-green-500 to-emerald-500'
  },
  {
    icon: Award,
    title: 'Image professionnelle',
    description: 'Envoyez des devis et factures modernes et personnalisés qui impressionnent vos clients.',
    stat: '5★',
    statLabel: 'satisfaction',
    color: 'from-purple-500 to-pink-500'
  }
]
</script>

<template>
  <section class="py-24 lg:py-32">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <!-- Section Header -->
      <div class="text-center mb-16">
        <span class="text-primary font-semibold text-sm uppercase tracking-wider">Avantages</span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mt-4 mb-6">
          Pourquoi choisir ArtisanGestion ?
        </h2>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Des bénéfices concrets et mesurables pour votre activité, dès le premier jour.
        </p>
      </div>

      <!-- Benefits Grid -->
      <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card
          v-for="(benefit, index) in benefits"
          :key="index"
          class="group border-border/50 hover:border-primary/30 transition-all duration-500 hover:shadow-xl overflow-hidden"
        >
          <CardContent class="p-0">
            <!-- Top gradient bar -->
            <div :class="['h-1 bg-gradient-to-r', benefit.color]" />
            
            <div class="p-6">
              <!-- Icon + Stat -->
              <div class="flex items-start justify-between mb-4">
                <div :class="[
                  'w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br',
                  benefit.color,
                  'opacity-90 group-hover:opacity-100 group-hover:scale-110 transition-all duration-300'
                ]">
                  <component :is="benefit.icon" class="h-6 w-6 text-white" />
                </div>
                <div class="text-right">
                  <div :class="['text-2xl font-bold bg-gradient-to-r bg-clip-text text-transparent', benefit.color]">
                    {{ benefit.stat }}
                  </div>
                  <div class="text-xs text-muted-foreground">{{ benefit.statLabel }}</div>
                </div>
              </div>

              <!-- Content -->
              <h3 class="text-lg font-semibold text-foreground mb-2 group-hover:text-primary transition-colors">
                {{ benefit.title }}
              </h3>
              <p class="text-sm text-muted-foreground leading-relaxed">
                {{ benefit.description }}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Bottom CTA -->
      <div class="mt-16 text-center">
        <div class="inline-flex flex-col sm:flex-row items-center gap-4 bg-muted/50 rounded-2xl px-8 py-6">
          <div class="flex -space-x-3">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 border-2 border-background" />
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-green-400 to-green-600 border-2 border-background" />
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 border-2 border-background" />
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 border-2 border-background" />
          </div>
          <div class="text-center sm:text-left">
            <p class="text-foreground font-semibold">Rejoignez 500+ artisans et PME</p>
            <p class="text-sm text-muted-foreground">qui gagnent du temps chaque jour avec ArtisanGestion</p>
          </div>
          <div class="flex items-center gap-1 text-sm font-medium text-success">
            <CheckCircle2 class="h-4 w-4" />
            Essai gratuit de 14 jours
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
