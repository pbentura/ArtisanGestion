<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Check,
  Sparkles,
  Zap
} from 'lucide-vue-next'

const plans = [
  {
    name: 'Free',
    description: 'Pour démarrer et tester',
    price: '0',
    period: '/mois',
    badge: null,
    features: [
      'Jusqu\'à 3 clients',
      '5 devis par mois',
      '5 factures par mois',
      'Tableau de bord basique',
      'Support par email'
    ],
    cta: 'Commencer gratuitement',
    variant: 'outline' as const,
    popular: false
  },
  {
    name: 'Pro',
    description: 'Pour les indépendants',
    price: '19',
    period: '/mois',
    badge: 'Plus populaire',
    features: [
      'Clients illimités',
      'Devis illimités',
      'Factures illimitées',
      'Tableau de bord complet',
      'Rapports d\'intervention',
      'Suivi du CA et objectifs',
      'Support prioritaire',
      'Export des données'
    ],
    cta: 'Essai gratuit 14 jours',
    variant: 'default' as const,
    popular: true
  },
  {
    name: 'Business',
    description: 'Pour les équipes',
    price: '49',
    period: '/mois',
    badge: null,
    features: [
      'Tout du plan Pro',
      'Jusqu\'à 5 utilisateurs',
      'Permissions avancées',
      'API d\'intégration',
      'Personnalisation avancée',
      'Support téléphonique',
      'Formation incluse',
      'SLA garanti'
    ],
    cta: 'Contacter l\'équipe',
    variant: 'outline' as const,
    popular: false
  }
]
</script>

<template>
  <section class="py-24 lg:py-32 bg-muted/30">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <!-- Section Header -->
      <div class="text-center mb-16">
        <span class="text-primary font-semibold text-sm uppercase tracking-wider">Tarifs</span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mt-4 mb-6">
          Des prix simples et transparents
        </h2>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Choisissez le plan qui correspond à vos besoins. Sans engagement, annulez à tout moment.
        </p>
      </div>

      <!-- Pricing Cards -->
      <div class="grid md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto">
        <Card
          v-for="(plan, index) in plans"
          :key="index"
          :class="[
            'relative border-border/50 transition-all duration-300',
            plan.popular 
              ? 'border-primary/50 shadow-xl shadow-primary/10 scale-105 z-10' 
              : 'hover:border-primary/30 hover:shadow-lg'
          ]"
        >
          <!-- Popular Badge -->
          <div
            v-if="plan.badge"
            class="absolute -top-4 left-1/2 -translate-x-1/2"
          >
            <Badge class="bg-primary text-primary-foreground px-4 py-1">
              <Sparkles class="h-3 w-3 mr-1" />
              {{ plan.badge }}
            </Badge>
          </div>

          <CardHeader class="pb-4 pt-8">
            <div class="text-center">
              <h3 class="text-xl font-bold text-foreground mb-1">{{ plan.name }}</h3>
              <p class="text-sm text-muted-foreground">{{ plan.description }}</p>
            </div>
          </CardHeader>

          <CardContent class="pt-0">
            <!-- Price -->
            <div class="text-center mb-6">
              <div class="flex items-baseline justify-center gap-1">
                <span class="text-4xl font-bold text-foreground">{{ plan.price }}€</span>
                <span class="text-muted-foreground">{{ plan.period }}</span>
              </div>
              <p class="text-xs text-muted-foreground mt-1">HT, sans engagement</p>
            </div>

            <!-- Features -->
            <ul class="space-y-3 mb-8">
              <li
                v-for="(feature, featureIndex) in plan.features"
                :key="featureIndex"
                class="flex items-start gap-3"
              >
                <div class="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Check class="h-3 w-3 text-primary" />
                </div>
                <span class="text-sm text-muted-foreground">{{ feature }}</span>
              </li>
            </ul>

            <!-- CTA -->
            <Button
              :variant="plan.variant"
              class="w-full rounded-xl py-6 font-semibold"
              :class="plan.popular ? 'shadow-lg shadow-primary/25' : ''"
            >
              <Zap v-if="plan.popular" class="mr-2 h-4 w-4" />
              {{ plan.cta }}
            </Button>
          </CardContent>
        </Card>
      </div>

      <!-- Trust badges -->
      <div class="mt-16 flex flex-wrap items-center justify-center gap-8 text-muted-foreground">
        <div class="flex items-center gap-2">
          <Check class="h-5 w-5 text-success" />
          <span class="text-sm">Sans engagement</span>
        </div>
        <div class="flex items-center gap-2">
          <Check class="h-5 w-5 text-success" />
          <span class="text-sm">Annulation à tout moment</span>
        </div>
        <div class="flex items-center gap-2">
          <Check class="h-5 w-5 text-success" />
          <span class="text-sm">14 jours d'essai gratuit</span>
        </div>
        <div class="flex items-center gap-2">
          <Check class="h-5 w-5 text-success" />
          <span class="text-sm">Support réactif</span>
        </div>
      </div>
    </div>
  </section>
</template>
