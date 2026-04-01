<script setup lang="ts">
import { Card, CardContent } from '@/components/ui/card'
import { 
  LayoutDashboard, 
  FileText, 
  Receipt, 
  ClipboardList,
  Users,
  Target,
  ArrowUpRight
} from 'lucide-vue-next'

const features = [
  {
    icon: LayoutDashboard,
    title: 'Dashboard clair',
    description: 'Visualisez en un coup d\'œil l\'état de votre activité : CA, devis en cours, interventions à venir.',
    color: 'bg-blue-500/10 text-blue-600'
  },
  {
    icon: FileText,
    title: 'Gestion des devis',
    description: 'Créez des devis professionnels en quelques clics. Suivez leur statut et convertissez-les en factures.',
    color: 'bg-green-500/10 text-green-600'
  },
  {
    icon: Receipt,
    title: 'Facturation automatique',
    description: 'Générez vos factures automatiquement, envoyez-les par email et suivez les paiements.',
    color: 'bg-purple-500/10 text-purple-600'
  },
  {
    icon: ClipboardList,
    title: 'Rapports d\'intervention',
    description: 'Documentez chaque intervention avec photos, signatures et commentaires pour un suivi complet.',
    color: 'bg-orange-500/10 text-orange-600'
  },
  {
    icon: Users,
    title: 'Suivi client',
    description: 'Retrouvez facilement l\'historique de chaque client, ses devis, factures et interventions.',
    color: 'bg-pink-500/10 text-pink-600'
  },
  {
    icon: Target,
    title: 'Objectifs de CA',
    description: 'Définissez vos objectifs et suivez votre progression en temps réel pour atteindre vos targets.',
    color: 'bg-cyan-500/10 text-cyan-600'
  }
]
</script>

<template>
  <section class="py-24 lg:py-32">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <!-- Section Header -->
      <div class="text-center mb-16">
        <span class="text-primary font-semibold text-sm uppercase tracking-wider">Fonctionnalités</span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mt-4 mb-6">
          Tout ce dont vous avez besoin
        </h2>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Une suite complète d'outils pensée pour simplifier le quotidien des artisans et PME.
        </p>
      </div>

      <!-- Features Grid -->
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card
          v-for="(feature, index) in features"
          :key="index"
          class="group border-border/50 hover:border-primary/30 transition-all duration-300 hover:shadow-lg hover:-translate-y-1 cursor-pointer"
        >
          <CardContent class="p-6">
            <div class="flex items-start gap-4">
              <div
                :class="[
                  'w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0',
                  feature.color,
                  'group-hover:scale-110 transition-transform duration-300'
                ]"
              >
                <component :is="feature.icon" class="h-6 w-6" />
              </div>
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <h3 class="text-lg font-semibold text-foreground">{{ feature.title }}</h3>
                  <ArrowUpRight class="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <p class="text-muted-foreground text-sm leading-relaxed">{{ feature.description }}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </section>
</template>
