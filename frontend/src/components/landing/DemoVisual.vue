<script setup lang="ts">
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  LayoutDashboard, 
  FileText, 
  Receipt,
  TrendingUp,
  Users,
  CheckCircle2,
  Clock,
  Search,
  Bell,
  Settings,
  Plus
} from 'lucide-vue-next'
</script>

<template>
  <section class="py-24 lg:py-32 bg-muted/30 overflow-hidden">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <!-- Section Header -->
      <div class="text-center mb-16">
        <span class="text-primary font-semibold text-sm uppercase tracking-wider">Aperçu</span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mt-4 mb-6">
          Une interface pensée pour vous
        </h2>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Découvrez un aperçu de l'interface Ventura : moderne, intuitive et optimisée pour votre productivité.
        </p>
      </div>

      <!-- Dashboard Mockup -->
      <div class="relative">
        <!-- Main Dashboard Card -->
        <Card class="rounded-2xl shadow-2xl border border-border/50 overflow-hidden bg-card">
          <CardContent class="p-0">
            <!-- App Header -->
            <div class="bg-card border-b border-border px-6 py-4 flex items-center justify-between">
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                  <TrendingUp class="h-5 w-5 text-white" />
                </div>
                <div class="hidden sm:flex items-center gap-1 text-sm font-medium text-muted-foreground">
                  <span class="text-foreground">Dashboard</span>
                  <span>/</span>
                  <span>Vue d'ensemble</span>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <div class="hidden sm:flex items-center gap-2 bg-muted rounded-lg px-3 py-2">
                  <Search class="h-4 w-4 text-muted-foreground" />
                  <span class="text-sm text-muted-foreground">Rechercher...</span>
                </div>
                <button class="w-9 h-9 rounded-lg hover:bg-muted flex items-center justify-center">
                  <Bell class="h-5 w-5 text-muted-foreground" />
                </button>
                <button class="w-9 h-9 rounded-lg hover:bg-muted flex items-center justify-center">
                  <Settings class="h-5 w-5 text-muted-foreground" />
                </button>
                <div class="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
                  <span class="text-sm font-semibold text-primary">JD</span>
                </div>
              </div>
            </div>

            <!-- Dashboard Content -->
            <div class="p-6 grid lg:grid-cols-4 gap-6">
              <!-- Sidebar -->
              <div class="hidden lg:block space-y-1">
                <div class="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/10 text-primary">
                  <LayoutDashboard class="h-5 w-5" />
                  <span class="text-sm font-medium">Dashboard</span>
                </div>
                <div class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-muted text-muted-foreground transition-colors">
                  <FileText class="h-5 w-5" />
                  <span class="text-sm font-medium">Devis</span>
                </div>
                <div class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-muted text-muted-foreground transition-colors">
                  <Receipt class="h-5 w-5" />
                  <span class="text-sm font-medium">Factures</span>
                </div>
                <div class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-muted text-muted-foreground transition-colors">
                  <Users class="h-5 w-5" />
                  <span class="text-sm font-medium">Clients</span>
                </div>
              </div>

              <!-- Main Content -->
              <div class="lg:col-span-3 space-y-6">
                <!-- Welcome + Quick Action -->
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <h3 class="text-2xl font-bold text-foreground">Bonjour, Jean </h3>
                    <p class="text-muted-foreground">Voici ce qui se passe aujourd'hui</p>
                  </div>
                  <button class="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors">
                    <Plus class="h-4 w-4" />
                    Nouveau devis
                  </button>
                </div>

                <!-- Stats Cards -->
                <div class="grid sm:grid-cols-3 gap-4">
                  <div class="bg-gradient-to-br from-primary/10 to-primary/5 rounded-xl p-5 border border-primary/20">
                    <div class="flex items-center justify-between mb-3">
                      <span class="text-sm text-muted-foreground">CA ce mois</span>
                      <TrendingUp class="h-4 w-4 text-primary" />
                    </div>
                    <div class="text-2xl font-bold text-foreground">24 580 €</div>
                    <div class="flex items-center gap-1 mt-1">
                      <span class="text-xs text-success font-medium">+12%</span>
                      <span class="text-xs text-muted-foreground">vs mois dernier</span>
                    </div>
                  </div>
                  <div class="bg-muted/50 rounded-xl p-5">
                    <div class="flex items-center justify-between mb-3">
                      <span class="text-sm text-muted-foreground">Devis en cours</span>
                      <FileText class="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div class="text-2xl font-bold text-foreground">8</div>
                    <div class="flex items-center gap-1 mt-1">
                      <span class="text-xs text-warning font-medium">3 en attente</span>
                    </div>
                  </div>
                  <div class="bg-muted/50 rounded-xl p-5">
                    <div class="flex items-center justify-between mb-3">
                      <span class="text-sm text-muted-foreground">Factures impayées</span>
                      <Receipt class="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div class="text-2xl font-bold text-foreground">4</div>
                    <div class="flex items-center gap-1 mt-1">
                      <span class="text-xs text-destructive font-medium">8 450 €</span>
                    </div>
                  </div>
                </div>

                <!-- Recent Activity + Chart -->
                <div class="grid lg:grid-cols-2 gap-6">
                  <!-- Activity -->
                  <div class="bg-muted/30 rounded-xl p-5">
                    <div class="flex items-center justify-between mb-4">
                      <h4 class="font-semibold text-foreground">Activité récente</h4>
                      <button class="text-sm text-primary hover:underline">Voir tout</button>
                    </div>
                    <div class="space-y-3">
                      <div class="flex items-center gap-3 p-3 bg-card rounded-lg shadow-sm">
                        <div class="w-8 h-8 rounded-full bg-success/20 flex items-center justify-center">
                          <CheckCircle2 class="h-4 w-4 text-success" />
                        </div>
                        <div class="flex-1 min-w-0">
                          <div class="text-sm font-medium text-foreground truncate">Facture #2024-156 payée</div>
                          <div class="text-xs text-muted-foreground">Dupont SARL • 1 250 €</div>
                        </div>
                        <span class="text-xs text-muted-foreground whitespace-nowrap">2h</span>
                      </div>
                      <div class="flex items-center gap-3 p-3 bg-card rounded-lg shadow-sm">
                        <div class="w-8 h-8 rounded-full bg-warning/20 flex items-center justify-center">
                          <Clock class="h-4 w-4 text-warning" />
                        </div>
                        <div class="flex-1 min-w-0">
                          <div class="text-sm font-medium text-foreground truncate">Devis #2024-89 en attente</div>
                          <div class="text-xs text-muted-foreground">Martin Electricité • 3 800 €</div>
                        </div>
                        <Badge variant="outline" class="text-xs">En attente</Badge>
                      </div>
                      <div class="flex items-center gap-3 p-3 bg-card rounded-lg shadow-sm">
                        <div class="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                          <FileText class="h-4 w-4 text-primary" />
                        </div>
                        <div class="flex-1 min-w-0">
                          <div class="text-sm font-medium text-foreground truncate">Nouvelle intervention</div>
                          <div class="text-xs text-muted-foreground">Durand Plomberie • Demain 14h</div>
                        </div>
                        <span class="text-xs text-muted-foreground whitespace-nowrap">5h</span>
                      </div>
                    </div>
                  </div>

                  <!-- Mini Chart -->
                  <div class="bg-muted/30 rounded-xl p-5">
                    <div class="flex items-center justify-between mb-4">
                      <h4 class="font-semibold text-foreground">Évolution du CA</h4>
                      <div class="flex gap-2">
                        <Badge variant="secondary" class="text-xs">7 jours</Badge>
                      </div>
                    </div>
                    <div class="flex items-end gap-2 h-32">
                      <div class="flex-1 flex flex-col items-center gap-1">
                        <div class="w-full bg-primary/20 rounded-t" style="height: 30%" />
                        <span class="text-xs text-muted-foreground">L</span>
                      </div>
                      <div class="flex-1 flex flex-col items-center gap-1">
                        <div class="w-full bg-primary/30 rounded-t" style="height: 50%" />
                        <span class="text-xs text-muted-foreground">M</span>
                      </div>
                      <div class="flex-1 flex flex-col items-center gap-1">
                        <div class="w-full bg-primary/40 rounded-t" style="height: 40%" />
                        <span class="text-xs text-muted-foreground">M</span>
                      </div>
                      <div class="flex-1 flex flex-col items-center gap-1">
                        <div class="w-full bg-primary/50 rounded-t" style="height: 70%" />
                        <span class="text-xs text-muted-foreground">J</span>
                      </div>
                      <div class="flex-1 flex flex-col items-center gap-1">
                        <div class="w-full bg-primary/60 rounded-t" style="height: 55%" />
                        <span class="text-xs text-muted-foreground">V</span>
                      </div>
                      <div class="flex-1 flex flex-col items-center gap-1">
                        <div class="w-full bg-primary/80 rounded-t" style="height: 85%" />
                        <span class="text-xs text-muted-foreground">S</span>
                      </div>
                      <div class="flex-1 flex flex-col items-center gap-1">
                        <div class="w-full bg-primary rounded-t" style="height: 100%" />
                        <span class="text-xs text-muted-foreground">D</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Floating UI Elements -->
        <div class="absolute -top-6 -right-6 bg-card rounded-xl shadow-xl border border-border p-4 hidden xl:block">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-success/20 flex items-center justify-center">
              <CheckCircle2 class="h-5 w-5 text-success" />
            </div>
            <div>
              <div class="text-sm font-semibold">Paiement reçu</div>
              <div class="text-xs text-muted-foreground">+2 500 €</div>
            </div>
          </div>
        </div>

        <div class="absolute -bottom-6 -left-6 bg-card rounded-xl shadow-xl border border-border p-4 hidden xl:block">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
              <TrendingUp class="h-5 w-5 text-primary" />
            </div>
            <div>
              <div class="text-sm font-semibold">Objectif atteint</div>
              <div class="text-xs text-muted-foreground">105% du CA mensuel</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
