<script setup lang="ts">
/** Bloc d'appel à l'action de fin de page, commun aux 4 pages. */
import { useRouter } from 'vue-router'
import { ArrowRight, CheckCircle2, Sparkles } from 'lucide-vue-next'

withDefaults(defineProps<{
  badge?: string
  titre: string
  accroche: string
  cta?: string
  preuves?: string[]
}>(), {
  cta: 'Essayer gratuitement 14 jours',
  preuves: () => ['Sans carte bancaire', 'Sans engagement', 'Données hébergées en France'],
})

const router = useRouter()
</script>

<template>
  <section class="py-20 lg:py-28 relative overflow-hidden">
    <div class="absolute inset-0 -z-10">
      <div class="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-primary/5" />
      <div class="absolute bottom-0 left-0 w-[600px] h-[600px] bg-primary/10 rounded-full blur-[150px]" />
    </div>

    <div v-apparait class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-3xl text-center">
      <div
        v-if="badge"
        class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-semibold mb-6"
      >
        <Sparkles class="h-4 w-4" />
        {{ badge }}
      </div>

      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-foreground mb-5 tracking-tight leading-tight">
        {{ titre }}
      </h2>
      <p class="text-lg text-muted-foreground mb-9 leading-relaxed">{{ accroche }}</p>

      <button
        type="button"
        class="group inline-flex items-center justify-center gap-3 px-8 sm:px-10 py-4 sm:py-5 bg-primary text-primary-foreground rounded-2xl text-base sm:text-lg font-bold shadow-2xl shadow-primary/30 hover:shadow-primary/50 transition-all duration-300 hover:scale-[1.03] active:scale-[0.98]"
        @click="router.push('/auth')"
      >
        {{ cta }}
        <ArrowRight class="h-5 w-5 group-hover:translate-x-1 transition-transform" />
      </button>

      <div class="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 mt-8 text-sm text-muted-foreground">
        <span v-for="p in preuves" :key="p" class="flex items-center gap-1.5">
          <CheckCircle2 class="h-4 w-4 text-success flex-shrink-0" />{{ p }}
        </span>
      </div>
    </div>
  </section>
</template>
