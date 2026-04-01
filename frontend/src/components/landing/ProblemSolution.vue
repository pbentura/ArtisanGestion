<script setup lang="ts">
import { Card, CardContent } from '@/components/ui/card'
import { 
  Clock, 
  FolderOpen, 
  FileX, 
  CheckCircle2,
  ArrowRight
} from 'lucide-vue-next'

const painPoints = [
  {
    icon: Clock,
    title: 'Perte de temps',
    description: 'Des heures perdues sur des tâches administratives répétitives au lieu de vous concentrer sur votre métier.',
    color: 'text-warning',
    bgColor: 'bg-warning/10'
  },
  {
    icon: FolderOpen,
    title: 'Mauvaise organisation',
    description: 'Informations éparpillées entre emails, papier et Excel. Difficile de tout retrouver rapidement.',
    color: 'text-destructive',
    bgColor: 'bg-destructive/10'
  },
  {
    icon: FileX,
    title: 'Facturation compliquée',
    description: 'Créer des factures professionnelles prend trop de temps, et les relances sont oubliées.',
    color: 'text-muted-foreground',
    bgColor: 'bg-muted'
  }
]

const solutions = [
  'Tout centralisé en un seul endroit',
  'Devis et factures générés en 2 clics',
  'Relances automatiques programmées',
  'Tableau de bord clair et intuitif'
]
</script>

<template>
  <section class="py-24 lg:py-32 bg-muted/30">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <!-- Section Header -->
      <div class="text-center mb-16">
        <span class="text-primary font-semibold text-sm uppercase tracking-wider">Le problème</span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mt-4 mb-6">
          Vous reconnaissez-vous ?
        </h2>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Les artisans et PME perdent chaque jour un temps précieux à cause d'outils inadaptés.
        </p>
      </div>

      <!-- Pain Points Grid -->
      <div class="grid md:grid-cols-3 gap-6 mb-16">
        <Card
          v-for="(point, index) in painPoints"
          :key="index"
          class="group border-border/50 hover:border-primary/50 transition-all duration-300 hover:shadow-lg"
        >
          <CardContent class="p-6 text-center">
            <div
              :class="[
                'w-14 h-14 rounded-2xl mx-auto mb-4 flex items-center justify-center',
                point.bgColor,
                'group-hover:scale-110 transition-transform duration-300'
              ]"
            >
              <component :is="point.icon" :class="['h-7 w-7', point.color]" />
            </div>
            <h3 class="text-xl font-semibold text-foreground mb-3">{{ point.title }}</h3>
            <p class="text-muted-foreground leading-relaxed">{{ point.description }}</p>
          </CardContent>
        </Card>
      </div>

      <!-- Solution Arrow -->
      <div class="flex justify-center mb-16">
        <div class="flex items-center gap-4 bg-primary/10 rounded-full px-6 py-3">
          <span class="text-primary font-semibold">La solution Ventura</span>
          <ArrowRight class="h-5 w-5 text-primary animate-bounce" />
        </div>
      </div>

      <!-- Solution Card -->
      <Card class="border-primary/20 bg-gradient-to-br from-card to-primary/5">
        <CardContent class="p-8 lg:p-12">
          <div class="grid lg:grid-cols-2 gap-8 items-center">
            <div>
              <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-success/10 text-success text-sm font-medium mb-6">
                <CheckCircle2 class="h-4 w-4" />
                Solution complète
              </div>
              <h3 class="text-2xl lg:text-3xl font-bold text-foreground mb-4">
                Centralisez, simplifiez, accélérez
              </h3>
              <p class="text-muted-foreground text-lg mb-6 leading-relaxed">
                Ventura remplace vos feuilles Excel, vos notes papier et vos emails éparpillés par un outil unique, pensé pour les artisans et PME.
              </p>
              <ul class="space-y-3">
                <li
                  v-for="(solution, index) in solutions"
                  :key="index"
                  class="flex items-center gap-3"
                >
                  <div class="w-6 h-6 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0">
                    <CheckCircle2 class="h-4 w-4 text-success" />
                  </div>
                  <span class="text-foreground">{{ solution }}</span>
                </li>
              </ul>
            </div>
            <div class="relative">
              <div class="aspect-square rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                <div class="text-center">
                  <div class="w-24 h-24 rounded-2xl bg-primary shadow-xl shadow-primary/30 flex items-center justify-center mx-auto mb-4">
                    <CheckCircle2 class="h-12 w-12 text-white" />
                  </div>
                  <p class="text-foreground font-semibold text-lg">Votre activité sous contrôle</p>
                  <p class="text-muted-foreground text-sm mt-1">Enfin simple et efficace</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </section>
</template>
