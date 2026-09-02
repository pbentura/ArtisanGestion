<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { ChevronDown, HelpCircle } from 'lucide-vue-next'

import { revealWhenVisible } from '@/composables/useReveal'

gsap.registerPlugin(ScrollTrigger)

const sectionRef = ref<HTMLElement | null>(null)
const openIndex = ref<number | null>(null)

function toggle(i: number) {
  openIndex.value = openIndex.value === i ? null : i
}

const faqs = [
  {
    question: 'Mes données sont-elles sécurisées ?',
    answer: 'Oui. Vos données sont hébergées en France, sur un serveur situé à Paris. Les échanges sont chiffrés (SSL/TLS) et l\'accès protégé par authentification. Nous ne partageons jamais vos données avec des tiers. Vous en restez propriétaire et pouvez supprimer votre compte et vos données à tout moment.'
  },
  {
    question: 'Combien de temps avant de créer mon premier document ?',
    answer: 'Quelques minutes. Vous créez votre compte, et vous pouvez commencer directement — rien n\'est bloqué par un long formulaire. Les informations de votre entreprise vous sont demandées au moment où vous créez votre premier document, et nous les pré-remplissons automatiquement à partir de votre SIRET ou du nom de votre société.'
  },
  {
    question: 'Comment migrer depuis Excel ou mon logiciel actuel ?',
    answer: 'Il n\'y a rien à migrer. Pas besoin d\'importer votre historique : vous commencez simplement vos prochains devis, factures et rapports sur ArtisanGestion. Vos anciens documents restent là où ils sont.'
  },
  {
    question: 'Qu\'est-ce que la facturation électronique 2026 ?',
    answer: 'À partir de 2026, les entreprises françaises devront émettre et recevoir leurs factures au format électronique structuré. ArtisanGestion génère vos factures au format Factur-X, conforme au standard européen EN 16931. Vous n\'avez rien à faire de plus, c\'est intégré.'
  },
  {
    question: 'L\'essai gratuit est-il vraiment gratuit ?',
    answer: 'Oui. Vous disposez de 14 jours pour utiliser toutes les fonctionnalités, sans aucune limite et sans carte bancaire à l\'inscription. À la fin de l\'essai, rien ne vous est prélevé : vous choisissez de vous abonner ou non. Sans abonnement, vous ne pouvez plus créer de nouveaux documents, mais vous gardez l\'accès à ceux déjà créés.'
  },
  {
    question: 'Puis-je l\'utiliser depuis mon téléphone, sur le chantier ?',
    answer: 'Oui. ArtisanGestion s\'utilise directement depuis le navigateur de votre téléphone, sans rien installer : créez vos rapports d\'intervention, ajoutez des photos et faites signer votre client sur l\'écran, depuis le chantier. Les applications iOS et Android sont en cours de finalisation.'
  },
  {
    question: 'Comment fonctionne la génération de rapports par IA ?',
    answer: 'Vous choisissez le type d\'intervention (plomberie, électricité, etc.) et décrivez en quelques mots ce que vous avez fait. L\'IA rédige un rapport professionnel structuré en une dizaine de secondes. Vous choisissez la longueur : court, normal ou détaillé. Des garde-fous empêchent l\'IA d\'inventer des détails que vous n\'avez pas mentionnés — et vous relisez toujours avant d\'envoyer.'
  },
  {
    question: 'Puis-je personnaliser mes documents ?',
    answer: 'Oui. Votre logo, vos coordonnées, vos mentions légales et votre pied de page sont repris automatiquement sur tous vos devis, factures et rapports. Vous pouvez les modifier à tout moment dans les paramètres. La couleur de vos documents et le retrait de la mention ArtisanGestion sont inclus pendant l\'essai, puis avec le forfait Équipe.'
  },
  {
    question: 'Puis-je annuler mon abonnement ?',
    answer: 'À tout moment, en deux clics depuis vos paramètres. Il n\'y a aucun engagement de durée et aucun frais de résiliation. Votre abonnement reste actif jusqu\'à la fin de la période déjà payée.'
  }
]

let nettoyerReveal: (() => void) | null = null

onMounted(() => {
  if (!sectionRef.value) return
  // Contenu visible en CSS : on n'anime qu'une fois la page affichée (useReveal).
  nettoyerReveal = revealWhenVisible(() => {
    gsap.from('.faq-header', {
      scrollTrigger: { trigger: sectionRef.value, start: 'top 80%', once: true },
      y: 30, opacity: 0, duration: 0.6
    })
    gsap.from('.faq-item', {
      scrollTrigger: { trigger: '.faq-list', start: 'top 85%', once: true },
      y: 20, opacity: 0, duration: 0.4, stagger: 0.08, ease: 'power3.out'
    })
  })
})

onUnmounted(() => nettoyerReveal?.())
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
