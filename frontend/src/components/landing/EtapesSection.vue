<script setup lang="ts">
/** « Comment ça marche » en 3 étapes numérotées. */
import type { Component } from 'vue'

defineProps<{
  etapes: { titre: string; texte: string; icone: Component }[]
}>()
</script>

<template>
  <div class="grid md:grid-cols-3 gap-6 lg:gap-8">
    <div
      v-for="(etape, i) in etapes"
      :key="i"
      v-apparait="i * 100"
      class="relative rounded-3xl bg-card border border-border/50 p-7 hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5 transition-all duration-500"
    >
      <!-- Trait de liaison entre les cartes, uniquement sur grand écran -->
      <div
        v-if="i < etapes.length - 1"
        class="hidden md:block absolute top-12 -right-4 w-8 h-px bg-border"
        aria-hidden="true"
      />
      <div class="flex items-center gap-3 mb-4">
        <div class="w-11 h-11 rounded-2xl bg-primary/10 flex items-center justify-center flex-shrink-0">
          <component :is="etape.icone" class="h-5 w-5 text-primary" />
        </div>
        <span class="text-4xl font-extrabold text-primary/15 leading-none select-none">{{ i + 1 }}</span>
      </div>
      <h3 class="text-lg font-bold text-foreground mb-2">{{ etape.titre }}</h3>
      <p class="text-sm text-muted-foreground leading-relaxed">{{ etape.texte }}</p>
    </div>
  </div>
</template>
