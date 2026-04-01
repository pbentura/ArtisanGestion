<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { 
  ArrowRight, 
  Play, 
  BarChart3, 
  FileText, 
  Users, 
  TrendingUp,
  Clock,
  CheckCircle2
} from 'lucide-vue-next'

const router = useRouter()

function navigateToAuth() {
  router.push('/auth')
}
</script>

<template>
  <section class="relative overflow-hidden pt-20 pb-32 lg:pt-32 lg:pb-40">
    <!-- Background gradient -->
    <div class="absolute inset-0 -z-10">
      <div class="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-background" />
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-primary/10 rounded-full blur-3xl" />
    </div>

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <div class="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
        <!-- Left: Content -->
        <div class="text-center lg:text-left">
          <!-- Badge -->
          <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
              <span class="relative inline-flex rounded-full h-2 w-2 bg-primary" />
            </span>
            Nouveau : Gestion des interventions disponible
          </div>

          <!-- Title -->
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-foreground mb-6">
            Gérez vos
            <span class="text-primary">devis</span>,
            <span class="text-primary">factures</span>
            et
            <span class="text-primary">interventions</span>
            en toute simplicité
          </h1>

          <!-- Subtitle -->
          <p class="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto lg:mx-0 mb-8 leading-relaxed">
            Ventura simplifie la gestion quotidienne des artisans et PME. Gagnez du temps, organisez votre activité et suivez votre chiffre d'affaires en un seul endroit.
          </p>

          <!-- CTAs -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start mb-12">
            <Button 
              size="lg" 
              class="rounded-full px-8 py-6 text-lg font-semibold shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all"
              @click="navigateToAuth"
            >
              Commencer gratuitement
              <ArrowRight class="ml-2 h-5 w-5" />
            </Button>
            <Button variant="outline" size="lg" class="rounded-full px-8 py-6 text-lg font-semibold border-2">
              <Play class="mr-2 h-5 w-5" />
              Voir une démo
            </Button>
          </div>

          <!-- Social proof -->
          <div class="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-6 text-sm text-muted-foreground">
            <div class="flex -space-x-2">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 border-2 border-background" />
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-green-600 border-2 border-background" />
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 border-2 border-background" />
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 border-2 border-background" />
              <div class="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-medium border-2 border-background">
                +500
              </div>
            </div>
            <div class="flex items-center gap-4">
              <div class="flex items-center gap-1">
                <CheckCircle2 class="h-4 w-4 text-success" />
                <span>Essai gratuit</span>
              </div>
              <div class="flex items-center gap-1">
                <CheckCircle2 class="h-4 w-4 text-success" />
                <span>Sans carte bancaire</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Dashboard Mockup -->
        <div class="relative">
          <Card class="rounded-2xl shadow-2xl border border-border/50 overflow-hidden bg-card">
            <CardContent class="p-0">
              <!-- Mock Header -->
              <div class="bg-gradient-to-r from-secondary to-secondary/90 px-6 py-4 flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                    <TrendingUp class="h-5 w-5 text-white" />
                  </div>
                  <span class="text-white font-semibold">Ventura Dashboard</span>
                </div>
                <div class="flex gap-2">
                  <div class="w-3 h-3 rounded-full bg-red-400" />
                  <div class="w-3 h-3 rounded-full bg-yellow-400" />
                  <div class="w-3 h-3 rounded-full bg-green-400" />
                </div>
              </div>

              <!-- Mock Content -->
              <div class="p-6 space-y-6">
                <!-- Stats Row -->
                <div class="grid grid-cols-3 gap-4">
                  <div class="bg-muted/50 rounded-xl p-4">
                    <div class="flex items-center gap-2 mb-2">
                      <BarChart3 class="h-4 w-4 text-primary" />
                      <span class="text-xs text-muted-foreground">CA ce mois</span>
                    </div>
                    <div class="text-xl font-bold text-foreground">24 580 €</div>
                    <div class="text-xs text-success">+12% vs mois dernier</div>
                  </div>
                  <div class="bg-muted/50 rounded-xl p-4">
                    <div class="flex items-center gap-2 mb-2">
                      <FileText class="h-4 w-4 text-primary" />
                      <span class="text-xs text-muted-foreground">Devis en cours</span>
                    </div>
                    <div class="text-xl font-bold text-foreground">8</div>
                    <div class="text-xs text-muted-foreground">3 en attente</div>
                  </div>
                  <div class="bg-muted/50 rounded-xl p-4">
                    <div class="flex items-center gap-2 mb-2">
                      <Users class="h-4 w-4 text-primary" />
                      <span class="text-xs text-muted-foreground">Clients actifs</span>
                    </div>
                    <div class="text-xl font-bold text-foreground">42</div>
                    <div class="text-xs text-success">+5 ce mois</div>
                  </div>
                </div>

                <!-- Chart Mock -->
                <div class="bg-muted/30 rounded-xl p-4">
                  <div class="flex items-center justify-between mb-4">
                    <span class="text-sm font-medium text-foreground">Évolution du CA</span>
                    <div class="flex gap-2">
                      <div class="px-2 py-1 bg-primary/10 rounded text-xs text-primary font-medium">7 jours</div>
                      <div class="px-2 py-1 bg-muted rounded text-xs text-muted-foreground">30 jours</div>
                    </div>
                  </div>
                  <div class="flex items-end gap-2 h-24">
                    <div class="flex-1 bg-primary/20 rounded-t" style="height: 40%" />
                    <div class="flex-1 bg-primary/30 rounded-t" style="height: 60%" />
                    <div class="flex-1 bg-primary/40 rounded-t" style="height: 45%" />
                    <div class="flex-1 bg-primary/50 rounded-t" style="height: 80%" />
                    <div class="flex-1 bg-primary/60 rounded-t" style="height: 65%" />
                    <div class="flex-1 bg-primary/70 rounded-t" style="height: 90%" />
                    <div class="flex-1 bg-primary rounded-t" style="height: 100%" />
                  </div>
                </div>

                <!-- Recent Activity -->
                <div class="space-y-3">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-foreground">Activité récente</span>
                    <Clock class="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div class="space-y-2">
                    <div class="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
                      <div class="w-8 h-8 rounded-full bg-success/20 flex items-center justify-center">
                        <CheckCircle2 class="h-4 w-4 text-success" />
                      </div>
                      <div class="flex-1">
                        <div class="text-sm font-medium text-foreground">Facture #2024-156 payée</div>
                        <div class="text-xs text-muted-foreground">Client: Dupont SARL - 1 250 €</div>
                      </div>
                      <span class="text-xs text-muted-foreground">Il y a 2h</span>
                    </div>
                    <div class="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
                      <div class="w-8 h-8 rounded-full bg-warning/20 flex items-center justify-center">
                        <FileText class="h-4 w-4 text-warning" />
                      </div>
                      <div class="flex-1">
                        <div class="text-sm font-medium text-foreground">Nouveau devis créé</div>
                        <div class="text-xs text-muted-foreground">Client: Martin Electricité - 3 800 €</div>
                      </div>
                      <span class="text-xs text-muted-foreground">Il y a 4h</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Floating elements -->
          <div class="absolute -top-4 -right-4 bg-card rounded-xl shadow-lg border border-border p-3 animate-pulse">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 rounded-full bg-success/20 flex items-center justify-center">
                <TrendingUp class="h-4 w-4 text-success" />
              </div>
              <div>
                <div class="text-xs text-muted-foreground">CA +23%</div>
                <div class="text-sm font-bold">Ce mois</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
