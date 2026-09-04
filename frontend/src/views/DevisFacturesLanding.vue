<script setup lang="ts">
/**
 * Page d'atterrissage — devis et factures.
 *
 * Cible : « logiciel devis artisan », « logiciel facturation bâtiment ».
 * L'angle n'est pas la liste des fonctionnalités mais le trajet complet :
 * du chiffrage à l'argent encaissé. Devis et facture y sont présentés comme
 * un seul flux, pas deux outils.
 */
import { useRouter } from 'vue-router'
import {
  FileText, Receipt, PenTool, Shield, Bell, Users, BarChart3,
  Palette, Clock, FolderOpen, AlertTriangle, ArrowRight, Sparkles, CreditCard,
} from 'lucide-vue-next'

import LandingHero from '@/components/landing/LandingHero.vue'
import SectionTitre from '@/components/landing/SectionTitre.vue'
import PointsForts from '@/components/landing/PointsForts.vue'
import LandingCTA from '@/components/landing/LandingCTA.vue'
import Pricing from '@/components/landing/Pricing.vue'
import FAQSection from '@/components/landing/FAQSection.vue'
import Footer from '@/components/landing/Footer.vue'

const router = useRouter()

const titre = [
  { texte: 'Du devis au paiement,' },
  { texte: 'sans ressaisir une ligne', accent: true },
]

const douleurs = [
  {
    icone: Clock,
    titre: 'Un devis qui traîne',
    texte: 'Le client attend trois jours son chiffrage. Pendant ce temps, un confrère a répondu.',
  },
  {
    icone: FolderOpen,
    titre: 'Le devis retapé en facture',
    texte: 'Les mêmes lignes, les mêmes montants, saisis deux fois. Et une erreur de TVA qui se glisse.',
  },
  {
    icone: AlertTriangle,
    titre: 'Des impayés qu’on n’ose pas relancer',
    texte: 'La facture est partie il y a six semaines. Personne n’a relancé, et la trésorerie encaisse.',
  },
]

/** Le parcours complet, présenté comme une seule continuité. */
const parcours = [
  {
    icone: FileText,
    etiquette: 'Devis',
    titre: 'Chiffrez sur place',
    texte: 'Lignes, quantités, TVA et totaux calculés à mesure. Le devis part par email avant que vous ne quittiez le chantier.',
  },
  {
    icone: PenTool,
    etiquette: 'Signature',
    titre: 'Faites signer',
    texte: 'Le client signe du doigt sur votre écran, ou à distance par un lien. Le devis signé est horodaté et conservé.',
  },
  {
    icone: Receipt,
    etiquette: 'Facture',
    titre: 'Convertissez en un clic',
    texte: 'Le devis accepté devient une facture : mêmes lignes, même client, numérotation continue. Rien à retaper.',
  },
  {
    icone: CreditCard,
    etiquette: 'Paiement',
    titre: 'Encaissez, puis relancez',
    texte: 'Le client règle par carte depuis la facture. S’il oublie, les relances partent toutes seules.',
  },
]

const points = [
  {
    icone: Shield,
    titre: 'Conforme à la facturation 2026',
    texte: 'Vos factures sont générées au format Factur-X, conforme au standard européen EN 16931. Vous n’avez rien à faire de plus.',
  },
  {
    icone: Palette,
    titre: 'Des documents à votre image',
    texte: 'Logo, coordonnées, mentions légales et pied de page repris automatiquement. Couleurs personnalisables.',
  },
  {
    icone: Bell,
    titre: 'Relances automatiques',
    texte: 'Trois paliers paramétrables. Vos clients sont relancés à 3, 10 et 21 jours de retard, sans que vous ayez à y penser.',
  },
  {
    icone: Users,
    titre: 'Vos clients en fiche',
    texte: 'Coordonnées, TVA intracommunautaire, historique des documents. Un client se sélectionne, il ne se ressaisit pas.',
  },
  {
    icone: BarChart3,
    titre: 'Ce que vous devez savoir',
    texte: 'Chiffre d’affaires du mois, encours client, factures en retard, taux de conversion des devis — en un écran.',
  },
  {
    icone: Sparkles,
    titre: 'Acomptes et avoirs',
    texte: 'Facture d’acompte sur un chantier long, avoir en cas d’erreur : les cas réels sont prévus.',
  },
]
</script>

<template>
  <div class="overflow-x-hidden">
    <LandingHero
      badge="Devis et factures pour artisans"
      :icone="Receipt"
      :titre="titre"
      sous-titre="Chiffrez sur le chantier, faites signer, convertissez en facture et encaissez. Un seul outil pour toute la chaîne, conforme à la facturation électronique 2026."
      :preuves="['Essai gratuit 14 jours', 'Sans carte bancaire', 'Factur-X conforme 2026']"
    >
      <!-- Aperçu de facture reconstruit en HTML : net sur tout écran, aucune
           image à télécharger, et il suit le thème clair comme sombre. -->
      <template #visuel>
        <div class="relative max-w-md mx-auto lg:max-w-none">
          <div class="absolute -inset-6 bg-gradient-to-r from-primary/20 via-blue-400/10 to-primary/20 rounded-3xl blur-3xl opacity-40" />
          <div class="relative bg-card border border-border rounded-2xl shadow-2xl overflow-hidden">
            <div class="px-6 py-5 border-b border-border flex items-start justify-between gap-4">
              <div>
                <p class="text-lg font-extrabold text-foreground">FACTURE</p>
                <p class="text-xs text-muted-foreground mt-0.5">F-2026-0038</p>
              </div>
              <div class="text-right">
                <p class="text-xs text-muted-foreground">Martin Plomberie</p>
                <p class="text-xs text-muted-foreground">SIRET 812 345 678</p>
              </div>
            </div>

            <div class="px-6 py-4 space-y-2.5">
              <div v-for="l in [
                { d: 'Remplacement chauffe-eau 150 L', m: '890,00' },
                { d: 'Main-d’œuvre — 3 h', m: '195,00' },
                { d: 'Déplacement', m: '45,00' },
              ]" :key="l.d" class="flex items-center justify-between text-sm">
                <span class="text-muted-foreground truncate pr-3">{{ l.d }}</span>
                <span class="text-foreground font-medium whitespace-nowrap">{{ l.m }} €</span>
              </div>
            </div>

            <div class="px-6 py-4 border-t border-border space-y-1.5">
              <div class="flex justify-between text-sm text-muted-foreground">
                <span>Total HT</span><span>1 130,00 €</span>
              </div>
              <div class="flex justify-between text-sm text-muted-foreground">
                <span>TVA 20 %</span><span>226,00 €</span>
              </div>
              <div class="flex justify-between text-base font-bold text-foreground pt-1.5 border-t border-border">
                <span>Total TTC</span><span>1 356,00 €</span>
              </div>
            </div>

            <div class="px-6 py-4 bg-primary/5 border-t border-border flex items-center gap-2.5">
              <Shield class="h-4 w-4 text-primary flex-shrink-0" />
              <span class="text-xs text-foreground font-medium">Format Factur-X — conforme 2026</span>
            </div>
          </div>
        </div>
      </template>
    </LandingHero>

    <!-- ── Le problème ── -->
    <section class="py-20 lg:py-24 bg-muted/30 border-y border-border/50">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <SectionTitre
          badge="Là où ça coince"
          :icone="AlertTriangle"
          titre="Le chantier est fini, l’argent n’est pas rentré"
          accroche="Entre le devis, la facture et la relance, il se perd des jours — et parfois des règlements."
        />
        <div class="grid md:grid-cols-3 gap-6">
          <div
            v-for="(d, i) in douleurs"
            :key="i"
            v-apparait="i * 100"
            class="rounded-3xl bg-card border border-border/50 p-7"
          >
            <div class="w-11 h-11 rounded-2xl bg-destructive/10 flex items-center justify-center mb-4">
              <component :is="d.icone" class="h-5 w-5 text-destructive" />
            </div>
            <h3 class="font-bold text-foreground mb-2">{{ d.titre }}</h3>
            <p class="text-sm text-muted-foreground leading-relaxed">{{ d.texte }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Le parcours complet ── -->
    <section class="py-20 lg:py-28">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <SectionTitre
          badge="Un seul flux"
          :icone="FileText"
          titre="Le devis, la signature, la facture, le paiement"
          accroche="Quatre étapes, un seul enchaînement. Aucune information n’est saisie deux fois."
        />

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 lg:gap-6">
          <div
            v-for="(e, i) in parcours"
            :key="i"
            v-apparait="i * 90"
            class="relative rounded-3xl bg-card border border-border/50 p-6 hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5 transition-all duration-500"
          >
            <div
              v-if="i < parcours.length - 1"
              class="hidden lg:block absolute top-11 -right-3.5 w-7 h-px bg-border"
              aria-hidden="true"
            />
            <div class="flex items-center justify-between mb-4">
              <div class="w-11 h-11 rounded-2xl bg-primary/10 flex items-center justify-center">
                <component :is="e.icone" class="h-5 w-5 text-primary" />
              </div>
              <span class="text-[11px] uppercase tracking-wider font-bold text-primary/70">{{ e.etiquette }}</span>
            </div>
            <h3 class="font-bold text-foreground mb-2">{{ e.titre }}</h3>
            <p class="text-sm text-muted-foreground leading-relaxed">{{ e.texte }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Conformité 2026 ── -->
    <section class="py-16 lg:py-20 bg-muted/30 border-y border-border/50">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
        <div v-apparait class="rounded-3xl bg-card border border-primary/20 p-7 sm:p-10">
          <div class="flex flex-col sm:flex-row items-start gap-6">
            <div class="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center flex-shrink-0">
              <Shield class="h-7 w-7 text-primary" />
            </div>
            <div>
              <h2 class="text-2xl sm:text-3xl font-extrabold text-foreground mb-3">
                La facturation électronique arrive en 2026
              </h2>
              <p class="text-muted-foreground leading-relaxed mb-4">
                Les entreprises françaises devront émettre et recevoir leurs factures au format
                électronique structuré. ArtisanGestion génère déjà vos factures au format
                <strong class="text-foreground">Factur-X</strong>, conforme au standard européen
                EN&nbsp;16931.
              </p>
              <p class="text-sm text-muted-foreground">
                Concrètement : vous ne changerez rien à vos habitudes le jour venu.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Ce qui est inclus ── -->
    <section class="py-20 lg:py-28">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <SectionTitre
          badge="Dans l’outil"
          :icone="Receipt"
          titre="Ce qui vous fait gagner des heures"
          accroche="Pas une liste de cases à cocher : ce que vous n’aurez plus à faire à la main."
        />
        <PointsForts :points="points" />
      </div>
    </section>

    <!-- ── Passerelle vers les rapports ── -->
    <section class="py-16 lg:py-20 bg-muted/30 border-y border-border/50">
      <div v-apparait class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-3xl text-center">
        <h2 class="text-2xl sm:text-3xl font-extrabold text-foreground mb-4">
          Et vos rapports d’intervention, l’IA les écrit
        </h2>
        <p class="text-muted-foreground mb-7 leading-relaxed">
          Le même compte gère vos comptes rendus d’intervention : vous décrivez en une phrase,
          le rapport professionnel est rédigé en une dizaine de secondes.
        </p>
        <button
          type="button"
          class="inline-flex items-center gap-2 px-6 py-3 rounded-2xl border-2 border-border bg-card font-semibold text-foreground hover:border-primary/30 hover:bg-muted transition-all"
          @click="router.push('/rapport-intervention')"
        >
          Découvrir les rapports par IA
          <ArrowRight class="h-4 w-4" />
        </button>
      </div>
    </section>

    <FAQSection
      :cles="['facturation2026', 'personnalisation', 'migration', 'essai', 'resiliation']"
      titre="Ce qu’on nous demande souvent"
    />

    <Pricing />

    <LandingCTA
      badge="Votre premier devis en 5 minutes"
      titre="Le prochain devis, faites-le depuis le chantier"
      accroche="Créez votre compte et éditez votre premier devis immédiatement. Vos informations d’entreprise sont pré-remplies à partir de votre SIRET."
    />

    <Footer />
  </div>
</template>
