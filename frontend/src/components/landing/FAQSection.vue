<script setup lang="ts">
import { ref, onMounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { ChevronDown, HelpCircle } from 'lucide-vue-next'

gsap.registerPlugin(ScrollTrigger)

const sectionRef = ref<HTMLElement | null>(null)
const openIndex = ref<number | null>(null)

function toggle(i: number) {
  openIndex.value = openIndex.value === i ? null : i
}

const faqs = [
  {
    question: 'Mes données sont-elles sécurisées ?',
    answer: 'Oui. Vos données sont hébergées en France sur des serveurs sécurisés. L\'accès est protégé par chiffrement SSL/TLS et authentification sécurisée. Nous ne partageons jamais vos données avec des tiers. Vous restez propriétaire de toutes vos données et pouvez les exporter à tout moment.'
  },
  {
    question: 'Comment migrer depuis Excel ou mon logiciel actuel ?',
    answer: 'C\'est simple : créez votre compte, renseignez vos informations d\'entreprise en 2 minutes grâce à notre onboarding guidé, et commencez à créer vos documents. Pas besoin d\'importer d\'historique — commencez simplement vos prochains devis et factures sur ArtisanGestion.'
  },
  {
    question: 'Qu\'est-ce que la facturation électronique 2026 ?',
    answer: 'À partir de 2026, toutes les entreprises françaises devront émettre et recevoir des factures au format électronique structuré (Factur-X). ArtisanGestion génère automatiquement vos factures au format Factur-X conforme au standard européen EN 16931. Vous n\'avez rien à faire de plus — c\'est intégré nativement.'
  },
  {
    question: 'L\'essai gratuit est-il vraiment gratuit ?',
    answer: 'Absolument. Aucune carte bancaire n\'est demandée à l\'inscription. Vous avez accès au plan gratuit sans limite de durée (3 clients, 5 devis/factures par mois), ou vous pouvez essayer le plan Pro pendant 14 jours gratuitement, sans engagement.'
  },
  {
    question: 'L\'application fonctionne-t-elle sur mobile ?',
    answer: 'Oui ! ArtisanGestion dispose d\'une application mobile native pour iOS et Android. Vous pouvez créer vos rapports d\'intervention directement sur le chantier, prendre des photos, faire signer vos clients et générer vos factures — tout depuis votre téléphone.'
  },
  {
    question: 'Comment fonctionne la génération de rapports par IA ?',
    answer: 'Vous sélectionnez le type d\'intervention (plomberie, électricité, etc.) et décrivez brièvement ce que vous avez fait. Notre IA (Mistral AI) génère instantanément un rapport d\'intervention professionnel et structuré. Vous pouvez choisir entre 3 niveaux de détail : court, normal ou détaillé. Le système inclut un anti-hallucination qui empêche l\'IA d\'inventer des détails.'
  },
  {
    question: 'Puis-je personnaliser mes documents ?',
    answer: 'Oui. Lors de l\'onboarding, vous renseignez votre logo, vos coordonnées, vos mentions légales et votre pied de page. Ces informations apparaissent automatiquement sur tous vos devis, factures et rapports. Vous pouvez les modifier à tout moment dans les paramètres.'
  }
]

onMounted(() => {
  if (!sectionRef.value) return
  gsap.from('.faq-header', {
    scrollTrigger: { trigger: sectionRef.value, start: 'top 80%', once: true },
    y: 30, opacity: 0, duration: 0.6
  })
  gsap.from('.faq-item', {
    scrollTrigger: { trigger: '.faq-list', start: 'top 85%', once: true },
    y: 20, opacity: 0, duration: 0.4, stagger: 0.08, ease: 'power3.out'
  })
})
</script>

<template>
  <section ref="sectionRef" class="py-24 lg:py-32 bg-muted/30 relative overflow-hidden">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-3xl">
      <!-- Header -->
      <div class="faq-header text-center mb-16">
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
          class="faq-item rounded-2xl border border-border/50 bg-card overflow-hidden transition-all duration-300"
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
