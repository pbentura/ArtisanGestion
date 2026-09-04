<script setup lang="ts">
/** Grille de bénéfices : icône, titre, explication. */
import type { Component } from 'vue'

withDefaults(defineProps<{
  points: { titre: string; texte: string; icone: Component }[]
  colonnes?: 2 | 3
}>(), { colonnes: 3 })
</script>

<template>
  <div
    class="grid gap-5 lg:gap-6"
    :class="colonnes === 2 ? 'sm:grid-cols-2' : 'sm:grid-cols-2 lg:grid-cols-3'"
  >
    <div
      v-for="(point, i) in points"
      :key="i"
      v-apparait="(i % 3) * 90"
      class="rounded-3xl bg-card border border-border/50 p-6 hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5 transition-all duration-500"
    >
      <div class="w-11 h-11 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
        <component :is="point.icone" class="h-5 w-5 text-primary" />
      </div>
      <h3 class="font-bold text-foreground mb-2">{{ point.titre }}</h3>
      <p class="text-sm text-muted-foreground leading-relaxed">{{ point.texte }}</p>
    </div>
  </div>
</template>
