<script setup lang="ts">
/**
 * Page d'atterrissage — usage sur le terrain, depuis le téléphone.
 *
 * Réécrite pour trois raisons :
 *
 *  1. la page ne proposait aucune inscription. Ses seuls boutons étaient deux
 *     pastilles « App Store / Google Play » désactivées : un visiteur venu
 *     d'une annonce n'avait littéralement rien à faire ;
 *  2. elle annonçait une « IA hors-ligne » qui n'existe pas — la génération
 *     appelle un service distant et exige une connexion ;
 *  3. son récit reposait sur une section épinglée en ScrollTrigger de deux
 *     écrans de haut, lourde et fragile sur mobile. Sur une page qui vend
 *     précisément l'usage mobile, c'était le pire endroit où la placer.
 */
import { useRouter } from 'vue-router'
import {
  Smartphone, Camera, PenTool, Wifi, Truck, Coffee, HardHat,
  Sparkles, Receipt, ArrowRight, Download, CheckCircle2,
} from 'lucide-vue-next'

import LandingHero from '@/components/landing/LandingHero.vue'
import SectionTitre from '@/components/landing/SectionTitre.vue'
import PointsForts from '@/components/landing/PointsForts.vue'
import LandingCTA from '@/components/landing/LandingCTA.vue'
import FAQSection from '@/components/landing/FAQSection.vue'
import Footer from '@/components/landing/Footer.vue'
import MockupIphone from '@/components/landing/MockupIphone.vue'

const router = useRouter()

const titre = [
  { texte: 'Votre bureau tient dans' },
  { texte: 'votre poche', accent: true },
]

/** Des moments de la journée, pas des fonctionnalités. */
const moments = [
  {
    icone: Truck,
    quand: 'Juste après l’intervention',
    titre: 'Le rapport est écrit avant de démarrer',
    texte: 'Vous décrivez ce que vous avez fait en une phrase, l’IA rédige le compte rendu. Vous relisez, vous envoyez, vous partez.',
  },
  {
    icone: HardHat,
    quand: 'Chez le client',
    titre: 'Le devis se signe sur place',
    texte: 'Vous chiffrez devant lui, il signe du doigt sur votre écran. L’accord est acté avant que vous ne quittiez les lieux.',
  },
  {
    icone: Coffee,
    quand: 'Entre deux chantiers',
    titre: 'La facture part du camion',
    texte: 'Le devis accepté devient une facture en un geste. Elle est envoyée pendant la pause, pas le dimanche soir.',
  },
]

const ecrans = [
  {
    src: '/screenshot-rapport.png',
    titre: 'La saisie d’un rapport',
    texte: 'Date, client, contenu — puis l’export PDF, à portée de pouce.',
  },
  {
    src: '/screenshot-facture.png',
    titre: 'Vos devis et vos factures',
    texte: 'Tout l’historique, filtrable, consultable sur le chantier.',
  },
]

const points = [
  {
    icone: Download,
    titre: 'Rien à installer',
    texte: 'ArtisanGestion s’ouvre dans le navigateur de votre téléphone. Pas de magasin d’applications, pas de mise à jour à surveiller.',
  },
  {
    icone: Camera,
    titre: 'Les photos au bon endroit',
    texte: 'Prises depuis l’application, elles sont rattachées au rapport et au client — pas noyées dans votre galerie personnelle.',
  },
  {
    icone: PenTool,
    titre: 'Signature au doigt',
    texte: 'Le client signe directement sur l’écran. Rien à imprimer, rien à scanner, rien à ranger.',
  },
  {
    icone: Wifi,
    titre: 'Tout est déjà synchronisé',
    texte: 'Ce que vous saisissez sur le chantier est sur votre ordinateur en rentrant. Il n’y a rien à transférer.',
  },
  {
    icone: Sparkles,
    titre: 'L’IA rédige pour vous',
    texte: 'La corvée du soir disparaît : le rapport professionnel se génère en une dizaine de secondes à partir de quelques mots.',
  },
  {
    icone: Receipt,
    titre: 'Devis et factures inclus',
    texte: 'Le même compte, les mêmes clients. Vous n’avez pas un outil pour le terrain et un autre pour le bureau.',
  },
]
</script>

<template>
  <div class="overflow-x-hidden">
    <LandingHero
      badge="Conçu pour le chantier"
      :icone="Smartphone"
      :titre="titre"
      sous-titre="Rapports, devis, factures et signature client — depuis votre téléphone, sur le chantier. Rien à installer : ouvrez ArtisanGestion dans votre navigateur et commencez."
      cta="Essayer depuis mon téléphone"
      :preuves="['Aucune installation', 'Essai gratuit 14 jours', 'Sans carte bancaire']"
    >
      <template #visuel>
        <div class="flex justify-center lg:justify-end relative">
          <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-primary/25 blur-[100px] rounded-full" />
          <div class="relative">
            <MockupIphone src="/screenshot-rapport.png" alt="Saisie d’un rapport d’intervention sur téléphone" />
          </div>
        </div>
      </template>
    </LandingHero>

    <!-- ── Trois moments de la journée ── -->
    <section class="py-20 lg:py-28 bg-muted/30 border-y border-border/50">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <SectionTitre
          badge="Une journée type"
          :icone="Truck"
          titre="L’administratif se fait là où il naît"
          accroche="Pas le soir, pas au bureau : au moment même où l’information est fraîche."
        />

        <div class="space-y-5 lg:space-y-6 max-w-4xl mx-auto">
          <div
            v-for="(m, i) in moments"
            :key="i"
            v-apparait="i * 100"
            class="rounded-3xl bg-card border border-border/50 p-6 sm:p-8 flex flex-col sm:flex-row gap-5 sm:gap-7 hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5 transition-all duration-500"
          >
            <div class="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center flex-shrink-0">
              <component :is="m.icone" class="h-6 w-6 text-primary" />
            </div>
            <div>
              <span class="text-xs uppercase tracking-wider font-bold text-primary/70">{{ m.quand }}</span>
              <h3 class="text-lg sm:text-xl font-bold text-foreground mt-1.5 mb-2">{{ m.titre }}</h3>
              <p class="text-muted-foreground leading-relaxed">{{ m.texte }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Les écrans réels ── -->
    <section class="py-20 lg:py-28">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <SectionTitre
          badge="À quoi ça ressemble"
          :icone="Smartphone"
          titre="Les écrans, tels quels"
          accroche="Aucune maquette embellie : ce sont les captures de l’application."
        />

        <div class="grid sm:grid-cols-2 gap-10 lg:gap-14 justify-items-center max-w-3xl mx-auto">
          <div v-for="(e, i) in ecrans" :key="i" v-apparait="i * 110" class="text-center">
            <div class="scale-[0.78] sm:scale-90 lg:scale-100 origin-top">
              <MockupIphone :src="e.src" :alt="e.titre" />
            </div>
            <h3 class="font-bold text-foreground mt-2 sm:mt-4">{{ e.titre }}</h3>
            <p class="text-sm text-muted-foreground mt-1">{{ e.texte }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Ce que ça change sur le terrain ── -->
    <section class="py-20 lg:py-28 bg-muted/30 border-y border-border/50">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <SectionTitre
          badge="Sur le chantier"
          :icone="HardHat"
          titre="Pensé pour des mains sales et une seule barre de réseau"
          accroche="Des écrans simples, de gros boutons, et rien à configurer avant de s’en servir."
        />
        <PointsForts :points="points" />
      </div>
    </section>

    <!-- ── Applications natives : dire les choses telles qu'elles sont ── -->
    <section class="py-16 lg:py-20">
      <div v-apparait class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-3xl">
        <div class="rounded-3xl bg-card border border-border/50 p-7 sm:p-9 text-center">
          <div class="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-5">
            <Download class="h-6 w-6 text-primary" />
          </div>
          <h2 class="text-xl sm:text-2xl font-bold text-foreground mb-3">
            Et les applications iOS et Android&nbsp;?
          </h2>
          <p class="text-muted-foreground leading-relaxed mb-5">
            Elles arrivent. En attendant, ArtisanGestion fonctionne déjà entièrement depuis le
            navigateur de votre téléphone — photos, signature et génération de rapports compris.
            Ajoutez le site à votre écran d’accueil et vous ne verrez pas la différence.
          </p>
          <div class="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
            <span class="flex items-center gap-1.5">
              <CheckCircle2 class="h-4 w-4 text-success" />Toutes les fonctionnalités disponibles
            </span>
            <span class="flex items-center gap-1.5">
              <CheckCircle2 class="h-4 w-4 text-success" />Aucune mise à jour à installer
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Passerelles ── -->
    <section class="py-16 lg:py-20 bg-muted/30 border-y border-border/50">
      <div v-apparait class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
        <div class="grid sm:grid-cols-2 gap-5">
          <button
            type="button"
            class="rounded-3xl bg-card border border-border/50 p-6 text-left hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5 transition-all group"
            @click="router.push('/rapport-intervention')"
          >
            <Sparkles class="h-5 w-5 text-primary mb-3" />
            <h3 class="font-bold text-foreground mb-1.5">Les rapports par IA</h3>
            <p class="text-sm text-muted-foreground mb-3">Comment une phrase devient un compte rendu professionnel.</p>
            <span class="inline-flex items-center gap-1.5 text-sm font-semibold text-primary">
              En savoir plus <ArrowRight class="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
            </span>
          </button>

          <button
            type="button"
            class="rounded-3xl bg-card border border-border/50 p-6 text-left hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5 transition-all group"
            @click="router.push('/devis-factures')"
          >
            <Receipt class="h-5 w-5 text-primary mb-3" />
            <h3 class="font-bold text-foreground mb-1.5">Les devis et factures</h3>
            <p class="text-sm text-muted-foreground mb-3">Du chiffrage au paiement, sans ressaisir une ligne.</p>
            <span class="inline-flex items-center gap-1.5 text-sm font-semibold text-primary">
              En savoir plus <ArrowRight class="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
            </span>
          </button>
        </div>
      </div>
    </section>

    <FAQSection :cles="['mobile', 'ia', 'essai', 'securite']" titre="Ce qu’on nous demande souvent" />

    <LandingCTA
      badge="Depuis votre téléphone, maintenant"
      titre="Essayez-le sur votre prochain chantier"
      accroche="Créez votre compte en une minute et générez votre premier rapport depuis le téléphone que vous tenez."
      cta="Créer mon compte gratuitement"
      :preuves="['Aucune installation', 'Sans carte bancaire', 'Sans engagement']"
    />

    <Footer />
  </div>
</template>
