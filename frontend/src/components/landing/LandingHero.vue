<script setup lang="ts">
/**
 * Hero commun aux pages d'atterrissage.
 *
 * Le contenu est écrit en clair dans le DOM et visible sans JavaScript :
 * ces pages reçoivent du trafic payant, un titre qui ne s'affiche pas est un
 * clic perdu. L'animation est ajoutée par-dessus, jamais indispensable.
 */
import { useRouter } from 'vue-router'
import { ArrowRight, CheckCircle2 } from 'lucide-vue-next'
import type { Component } from 'vue'

withDefaults(defineProps<{
  badge?: string
  icone?: Component
  /** Segments du titre ; `accent: true` colore en bleu. */
  titre: { texte: string; accent?: boolean }[]
  sousTitre: string
  cta?: string
  preuves?: string[]
  /** Colonne visuelle absente : le texte occupe alors toute la largeur. */
  large?: boolean
}>(), {
  cta: 'Essayer gratuitement 14 jours',
  preuves: () => ['Essai gratuit 14 jours', 'Sans carte bancaire', 'Sans engagement'],
})

const router = useRouter()
</script>

<template>
  <section class="relative overflow-hidden pt-28 sm:pt-32 lg:pt-36 pb-16 lg:pb-24">
    <!-- Fond : reprend exactement celui de la page d'accueil -->
    <div class="absolute inset-0 -z-10">
      <div class="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-background" />
      <div class="absolute top-[-10%] left-[-5%] w-[500px] h-[500px] bg-primary/8 rounded-full blur-[120px]" />
      <div class="absolute bottom-[-10%] right-[-5%] w-[400px] h-[400px] bg-blue-400/5 rounded-full blur-[100px]" />
      <div
        class="absolute inset-0 opacity-[0.02]"
        style="background-image: radial-gradient(circle, currentColor 1px, transparent 1px); background-size: 40px 40px;"
      />
    </div>

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <div class="grid gap-12 lg:gap-16 items-center" :class="large ? '' : 'lg:grid-cols-2'">
        <div :class="large ? 'text-center max-w-3xl mx-auto' : 'text-center lg:text-left'">
          <div
            v-if="badge"
            v-apparait
            class="inline-flex items-center gap-2.5 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-6"
          >
            <component :is="icone" v-if="icone" class="h-4 w-4" />
            <span>{{ badge }}</span>
          </div>

          <h1
            v-apparait="60"
            class="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-foreground mb-5 sm:mb-6 leading-[1.1]"
          >
            <template v-for="(part, i) in titre" :key="i">
              <span :class="part.accent ? 'text-primary' : ''">{{ part.texte }}</span>
              <!-- Interpolation explicite : un simple espace entre deux balises
                   est supprimé à la compilation du gabarit. -->
              <template v-if="i < titre.length - 1">{{ ' ' }}</template>
            </template>
          </h1>

          <p
            v-apparait="120"
            class="text-base sm:text-xl text-muted-foreground max-w-xl mb-8 leading-relaxed"
            :class="large ? 'mx-auto' : 'mx-auto lg:mx-0'"
          >
            {{ sousTitre }}
          </p>

          <div
            v-apparait="180"
            class="flex flex-col sm:flex-row gap-3 sm:gap-4 mb-8"
            :class="large ? 'justify-center' : 'justify-center lg:justify-start'"
          >
            <button
              type="button"
              class="group inline-flex items-center justify-center gap-2 px-7 py-4 bg-primary text-primary-foreground rounded-2xl text-base sm:text-lg font-semibold shadow-xl shadow-primary/25 hover:shadow-primary/40 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
              @click="router.push('/auth?mode=signup')"
            >
              {{ cta }}
              <ArrowRight class="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <slot name="cta-secondaire" />
          </div>

          <div
            v-apparait="240"
            class="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-muted-foreground"
            :class="large ? 'justify-center' : 'justify-center lg:justify-start'"
          >
            <span v-for="p in preuves" :key="p" class="flex items-center gap-1.5">
              <CheckCircle2 class="h-4 w-4 text-success flex-shrink-0" />{{ p }}
            </span>
          </div>
        </div>

        <div v-if="!large" v-apparait="200" class="relative">
          <slot name="visuel" />
        </div>
      </div>
    </div>
  </section>
</template>
