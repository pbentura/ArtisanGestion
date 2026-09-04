<script setup lang="ts">
/**
 * Page d'atterrissage — rapports d'intervention.
 *
 * Cible : un artisan qui cherche « logiciel rapport intervention ». Il doit
 * comprendre en une seconde que l'IA rédige le rapport à sa place. Tout ce qui
 * ne sert pas cette intention (facturation électronique, tableau de bord,
 * collaborateurs) est resté sur les autres pages.
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Sparkles, Clock, FileX, Moon, Camera, PenTool, FolderSearch,
  ShieldCheck, Smartphone, ListChecks, MessageSquareText, Play, ArrowRight,
} from 'lucide-vue-next'

import LandingHero from '@/components/landing/LandingHero.vue'
import SectionTitre from '@/components/landing/SectionTitre.vue'
import EtapesSection from '@/components/landing/EtapesSection.vue'
import PointsForts from '@/components/landing/PointsForts.vue'
import LandingCTA from '@/components/landing/LandingCTA.vue'
import Pricing from '@/components/landing/Pricing.vue'
import FAQSection from '@/components/landing/FAQSection.vue'
import Footer from '@/components/landing/Footer.vue'
import { useLazyVideo } from '@/composables/useLazyVideo'

const router = useRouter()
const videoRef = ref<HTMLVideoElement | null>(null)
useLazyVideo(videoRef, '/demo-ia-rapport.mp4', { playbackRate: 1.5 })

const titre = [
  { texte: 'Vos rapports d’intervention' },
  { texte: 'rédigés par l’IA', accent: true },
]

const douleurs = [
  {
    icone: Moon,
    titre: 'Le soir, il reste les rapports',
    texte: 'La journée est finie depuis longtemps et il faut encore raconter chaque intervention, de mémoire.',
  },
  {
    icone: FileX,
    titre: 'Des comptes rendus bâclés',
    texte: 'Trois lignes griffonnées sur un carnet, que le client ne comprend pas et qui ne prouvent rien en cas de litige.',
  },
  {
    icone: Clock,
    titre: 'Du temps qui ne se facture pas',
    texte: 'Chaque heure passée sur la paperasse est une heure qui ne rapporte rien.',
  },
]

const etapes = [
  {
    icone: ListChecks,
    titre: 'Choisissez le type d’intervention',
    texte: 'Plomberie, électricité, chauffage, maçonnerie… La liste couvre les métiers du bâtiment et de la maintenance.',
  },
  {
    icone: MessageSquareText,
    titre: 'Décrivez en quelques mots',
    texte: '« Remplacement du chauffe-eau, fuite au raccord réparée, test de pression OK. » Ça suffit.',
  },
  {
    icone: Sparkles,
    titre: 'Relisez et envoyez',
    texte: 'Le rapport structuré arrive en une dizaine de secondes. Vous le relisez, vous l’envoyez.',
  },
]

const points = [
  {
    icone: ShieldCheck,
    titre: 'L’IA n’invente rien',
    texte: 'Des garde-fous l’empêchent d’ajouter des détails que vous n’avez pas mentionnés. Un rapport doit rester exact.',
  },
  {
    icone: Camera,
    titre: 'Photos du chantier',
    texte: 'Ajoutez vos photos avant / après depuis le téléphone. Elles sont jointes au rapport, pas perdues dans la galerie.',
  },
  {
    icone: PenTool,
    titre: 'Signature du client sur place',
    texte: 'Le client signe du doigt sur votre écran. Le rapport est validé avant même que vous ne remontiez en voiture.',
  },
  {
    icone: FolderSearch,
    titre: 'Tout est retrouvable',
    texte: 'Chaque rapport est rattaché à son client et à sa date. Une recherche, et vous ressortez l’intervention d’il y a huit mois.',
  },
  {
    icone: Smartphone,
    titre: 'Depuis le chantier',
    texte: 'Rien à installer : le rapport se rédige depuis le navigateur du téléphone, dans la camionnette.',
  },
  {
    icone: Sparkles,
    titre: 'Trois niveaux de détail',
    texte: 'Court pour un dépannage, détaillé pour un chantier à enjeu. Vous choisissez à chaque rapport.',
  },
]
</script>

<template>
  <div class="overflow-x-hidden">
    <LandingHero
      badge="Rapports d’intervention par IA"
      :icone="Sparkles"
      :titre="titre"
      sous-titre="Décrivez votre intervention en une phrase. L’IA rédige un rapport professionnel, structuré et prêt à envoyer — en une dizaine de secondes, depuis le chantier."
      :preuves="['Essai gratuit 14 jours', 'Sans carte bancaire', 'Rapport prêt en 10 secondes']"
    >
      <template #cta-secondaire>
        <a
          href="#demonstration"
          class="group inline-flex items-center justify-center gap-2 px-7 py-4 bg-card border-2 border-border rounded-2xl text-base sm:text-lg font-semibold text-foreground hover:border-primary/30 hover:bg-muted transition-all duration-300"
        >
          <Play class="h-5 w-5 text-primary" />
          Voir la démo
        </a>
      </template>

      <!-- Réplique de l'écran réel : plus léger qu'une capture, net sur tout
           écran, et cohérent avec le thème clair comme sombre. -->
      <template #visuel>
        <div class="relative max-w-md mx-auto lg:max-w-none">
          <div class="absolute -inset-6 bg-gradient-to-r from-primary/20 via-blue-400/10 to-primary/20 rounded-3xl blur-3xl opacity-40" />
          <div class="relative bg-card border border-border rounded-2xl shadow-2xl overflow-hidden">
            <div class="px-5 sm:px-6 pt-5 pb-4 bg-gradient-to-br from-primary/5 via-card to-card border-b border-border">
              <div class="flex items-start gap-3">
                <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Sparkles class="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p class="text-base font-bold text-foreground">Générer avec l’IA</p>
                  <p class="text-sm text-muted-foreground leading-snug">
                    Quelques informations suffisent
                  </p>
                </div>
              </div>
            </div>

            <div class="px-5 sm:px-6 py-5 space-y-4">
              <div>
                <span class="block text-sm font-medium text-foreground mb-1.5">Type d’intervention</span>
                <div class="w-full px-3 py-2.5 bg-background border border-input rounded-lg text-foreground text-sm">
                  Plomberie
                </div>
              </div>
              <div>
                <span class="block text-sm font-medium text-foreground mb-1.5">Description rapide</span>
                <div class="w-full px-3 py-2.5 bg-background border border-primary/50 ring-2 ring-primary/20 rounded-lg text-foreground text-sm leading-relaxed">
                  Remplacement du chauffe-eau défectueux chez Mme Dupont. Fuite au raccord
                  réparée, installation du modèle 150 L, test de pression OK.
                </div>
              </div>
              <div class="flex items-center gap-2 pt-1">
                <div class="flex-1 h-10 rounded-lg bg-primary text-primary-foreground text-sm font-semibold flex items-center justify-center gap-2">
                  <Sparkles class="w-4 h-4" />
                  Générer le rapport
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </LandingHero>

    <!-- ── Le problème ── -->
    <section class="py-20 lg:py-24 bg-muted/30 border-y border-border/50">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <SectionTitre
          badge="Le vrai coût des rapports"
          :icone="Clock"
          titre="Ce n’est pas l’intervention qui prend du temps"
          accroche="C’est ce qu’il faut écrire après. Et c’est presque toujours repoussé au soir, ou au dimanche."
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

    <!-- ── Comment ça marche ── -->
    <section class="py-20 lg:py-28">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <SectionTitre
          badge="En trois gestes"
          :icone="ListChecks"
          titre="De la description au rapport fini"
          accroche="Pas de modèle à remplir, pas de mise en page à refaire. Vous racontez, le rapport s’écrit."
        />
        <EtapesSection :etapes="etapes" />
      </div>
    </section>

    <!-- ── Démonstration ── -->
    <section id="demonstration" class="py-20 lg:py-28 bg-muted/30 border-y border-border/50">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-5xl">
        <SectionTitre
          badge="En conditions réelles"
          :icone="Play"
          titre="Regardez-le écrire"
          accroche="Aucun montage : c’est l’écran de l’application, à vitesse réelle."
        />
        <div v-apparait class="relative rounded-2xl overflow-hidden border border-border shadow-2xl bg-black">
          <div class="absolute top-0 left-0 right-0 h-9 bg-black/60 backdrop-blur-md flex items-center px-4 gap-2 z-10 border-b border-white/10">
            <div class="w-2.5 h-2.5 rounded-full bg-red-500/80" />
            <div class="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
            <div class="w-2.5 h-2.5 rounded-full bg-green-500/80" />
            <span class="ml-3 text-xs text-white/50 font-medium">Rédaction en cours…</span>
          </div>
          <!-- L'affiche s'affiche tout de suite ; la vidéo n'est téléchargée
               qu'à l'approche de la section. -->
          <video
            ref="videoRef"
            poster="/poster-demo-ia.jpg"
            preload="none"
            loop
            muted
            playsinline
            class="w-full h-auto mt-9 object-cover"
          />
        </div>
      </div>
    </section>

    <!-- ── Ce que ça change ── -->
    <section class="py-20 lg:py-28">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <SectionTitre
          badge="Sur le terrain"
          :icone="Smartphone"
          titre="Un rapport qui tient debout"
          accroche="Photos, signature, historique : de quoi prouver ce que vous avez fait, des mois plus tard."
        />
        <PointsForts :points="points" />
      </div>
    </section>

    <!-- ── Continuité avec le reste ── -->
    <section class="py-16 lg:py-20 bg-muted/30 border-y border-border/50">
      <div v-apparait class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-3xl text-center">
        <h2 class="text-2xl sm:text-3xl font-extrabold text-foreground mb-4">
          Et l’intervention devient un devis, puis une facture
        </h2>
        <p class="text-muted-foreground mb-7 leading-relaxed">
          Le rapport n’est pas un outil isolé. Le client, l’intervention et les documents
          vivent au même endroit : vous transformez un constat en devis, puis en facture,
          sans ressaisir quoi que ce soit.
        </p>
        <button
          type="button"
          class="inline-flex items-center gap-2 px-6 py-3 rounded-2xl border-2 border-border bg-card font-semibold text-foreground hover:border-primary/30 hover:bg-muted transition-all"
          @click="router.push('/devis-factures')"
        >
          Voir les devis et factures
          <ArrowRight class="h-4 w-4" />
        </button>
      </div>
    </section>

    <FAQSection :cles="['ia', 'mobile', 'essai', 'securite']" titre="Ce qu’on nous demande souvent" />

    <Pricing />

    <LandingCTA
      badge="Votre premier rapport dans 2 minutes"
      titre="Ce soir, vos rapports seront déjà écrits"
      accroche="Créez votre compte et générez votre premier rapport d’intervention immédiatement. Aucune information d’entreprise n’est exigée pour commencer."
      :preuves="['Sans carte bancaire', 'Sans engagement', 'Données hébergées en France']"
    />

    <Footer />
  </div>
</template>
