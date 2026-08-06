<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { ArrowRight, CheckCircle2, Sparkles } from 'lucide-vue-next'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()
const sectionRef = ref<HTMLElement | null>(null)

function navigateToAuth() {
  router.push('/auth')
}

onMounted(() => {
  if (!sectionRef.value) return
  nextTick(() => {
    setTimeout(() => {
      gsap.from('.cta-content', {
        scrollTrigger: { trigger: sectionRef.value, start: 'top 80%', once: true },
        y: 40, opacity: 0, duration: 0.8, ease: 'power3.out'
      })

      ScrollTrigger.refresh()
    }, 150)
  })
})
</script>

<template>
  <section ref="sectionRef" class="py-24 lg:py-32 relative overflow-hidden">
    <!-- Animated background -->
    <div class="absolute inset-0 -z-10">
      <div class="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-primary/3" />
      <div class="absolute bottom-0 left-0 w-[700px] h-[700px] bg-primary/10 rounded-full blur-[150px] animate-pulse" style="animation-duration: 8s" />
      <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-400/5 rounded-full blur-[120px] animate-pulse" style="animation-duration: 6s; animation-delay: 2s" />
    </div>

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
      <div class="cta-content text-center">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-semibold mb-8">
          <Sparkles class="h-4 w-4" />
          Prêt à simplifier votre quotidien ?
        </div>

        <!-- Headline -->
        <h2 class="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-foreground mb-6 tracking-tight leading-tight">
          Rejoignez les artisans qui ont déjà<br class="hidden sm:block" />
          <span class="text-primary">gagné 5 heures par semaine</span>
        </h2>

        <!-- Subtitle -->
        <p class="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
          Essai gratuit de 14 jours, sans carte bancaire. Votre premier rapport IA en 30 secondes après l'inscription.
        </p>

        <!-- CTA -->
        <button
          @click="navigateToAuth"
          class="group relative inline-flex items-center justify-center gap-3 px-10 py-5 bg-primary text-primary-foreground rounded-2xl text-lg font-bold shadow-2xl shadow-primary/30 hover:shadow-primary/50 transition-all duration-300 hover:scale-[1.03] active:scale-[0.98] overflow-hidden"
        >
          <span class="relative z-10">Créer mon compte gratuitement</span>
          <ArrowRight class="relative z-10 h-5 w-5 group-hover:translate-x-1 transition-transform" />
          <div class="absolute inset-0 bg-gradient-to-r from-primary via-blue-600 to-primary bg-[length:200%_100%] group-hover:animate-shimmer" />
        </button>

        <!-- Trust -->
        <div class="flex flex-wrap items-center justify-center gap-6 mt-10 text-sm text-muted-foreground">
          <span class="flex items-center gap-1.5"><CheckCircle2 class="h-4 w-4 text-success" />14 jours gratuits</span>
          <span class="flex items-center gap-1.5"><CheckCircle2 class="h-4 w-4 text-success" />Sans carte bancaire</span>
          <span class="flex items-center gap-1.5"><CheckCircle2 class="h-4 w-4 text-success" />Setup en 2 minutes</span>
        </div>
      </div>
    </div>
  </section>
</template>
