<script setup lang="ts">
/** En-tête de section : pastille, titre, accroche. Uniformise les 4 pages. */
import type { Component } from 'vue'

defineProps<{
  badge?: string
  icone?: Component
  titre: string
  accroche?: string
  aligne?: 'centre' | 'gauche'
}>()
</script>

<template>
  <div v-apparait class="mb-12 lg:mb-16" :class="aligne === 'gauche' ? 'text-left' : 'text-center max-w-3xl mx-auto'">
    <span
      v-if="badge"
      class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-4"
    >
      <component :is="icone" v-if="icone" class="h-4 w-4" />
      {{ badge }}
    </span>
    <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-foreground tracking-tight">
      <slot name="titre">{{ titre }}</slot>
    </h2>
    <p v-if="accroche || $slots.accroche" class="text-lg text-muted-foreground mt-5 leading-relaxed"
       :class="aligne === 'gauche' ? '' : 'mx-auto'">
      <slot name="accroche">{{ accroche }}</slot>
    </p>
  </div>
</template>
