<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronDown, HelpCircle } from 'lucide-vue-next'
import { TOUTES_QUESTIONS } from '@/lib/faq'



const props = withDefaults(defineProps<{
  /** Clés de TOUTES_QUESTIONS à afficher, dans cet ordre. Vide = tout. */
  cles?: string[]
  titre?: string
}>(), { titre: 'Questions fréquentes' })

// Chaque page d'atterrissage ne montre que ce qui concerne son intention :
// une question sur la facturation électronique n'a rien à faire sur la page
// dédiée aux rapports d'intervention.
const faqs = computed(() =>
  (props.cles?.length ? props.cles : Object.keys(TOUTES_QUESTIONS))
    .map((c) => TOUTES_QUESTIONS[c])
    .filter(Boolean)
)

const openIndex = ref<number | null>(null)

function toggle(i: number) {
  openIndex.value = openIndex.value === i ? null : i
}



</script>

<template>
  <section class="py-24 lg:py-32 bg-muted/30 relative overflow-hidden">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-3xl">
      <!-- Header -->
      <div v-apparait class="faq-header text-center mb-16">
        <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-4">
          <HelpCircle class="h-4 w-4" />
          FAQ
        </span>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-foreground mb-6 tracking-tight">
          Vos questions fréquentes
        </h2>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Tout ce que vous devez savoir avant de vous lancer.
        </p>
      </div>

      <!-- FAQ List -->
      <div class="faq-list space-y-3">
        <div
          v-for="(faq, i) in faqs"
          :key="i"
          v-apparait class="faq-item rounded-2xl border border-border/50 bg-card overflow-hidden transition-all duration-300"
          :class="openIndex === i ? 'shadow-lg shadow-primary/5 border-primary/20' : 'hover:border-primary/10'"
        >
          <button
            @click="toggle(i)"
            class="w-full flex items-center justify-between gap-4 p-6 text-left transition-colors"
          >
            <span class="font-semibold text-foreground">{{ faq.question }}</span>
            <ChevronDown
              class="h-5 w-5 text-muted-foreground flex-shrink-0 transition-transform duration-300"
              :class="openIndex === i ? 'rotate-180 text-primary' : ''"
            />
          </button>

          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="max-h-0 opacity-0"
            enter-to-class="max-h-[300px] opacity-100"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="max-h-[300px] opacity-100"
            leave-to-class="max-h-0 opacity-0"
          >
            <div v-if="openIndex === i" class="overflow-hidden">
              <div class="px-6 pb-6 pt-0">
                <p class="text-muted-foreground leading-relaxed">{{ faq.answer }}</p>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </section>
</template>
