<script setup lang="ts">
/**
 * Page d'atterrissage — facturation électronique pour les artisans.
 *
 * Cible : « facturation électronique artisan », « facture électronique
 * bâtiment », « facturation électronique auto-entrepreneur ». Volontairement
 * pas « facturation électronique 2026 » seul : sur ce terme générique, la
 * première page de Google est tenue par les éditeurs comptables et les
 * cabinets, hors d'atteinte d'un site neuf. La longue traîne métier est
 * gagnable, et bien mieux qualifiée.
 *
 * L'angle est informatif avant d'être commercial : quelqu'un qui tape cette
 * requête cherche à comprendre s'il est concerné et à quelle date, pas à
 * acheter un logiciel. La page répond d'abord, propose ensuite.
 *
 * Deux exigences d'exactitude, parce que la page énonce du droit :
 *
 *  — les dates distinguent réception (1er sept. 2026, en vigueur) et émission
 *    (1er sept. 2027 pour les PME et micro-entreprises, donc les artisans) ;
 *  — ArtisanGestion n'est pas une plateforme agréée. La page le dit
 *    explicitement plutôt que de laisser croire que l'abonnement suffit.
 */
import {
  FileCheck2, Inbox, Send, CalendarClock, ShieldCheck, HelpCircle,
  FileWarning, Building2, UserRound,
} from 'lucide-vue-next'

import LandingHero from '@/components/landing/LandingHero.vue'
import SectionTitre from '@/components/landing/SectionTitre.vue'
import PointsForts from '@/components/landing/PointsForts.vue'
import LandingCTA from '@/components/landing/LandingCTA.vue'
import Pricing from '@/components/landing/Pricing.vue'
import FAQSection from '@/components/landing/FAQSection.vue'
// Source unique, partagée avec le balisage FAQPage du prérendu.
import pagesSeo from '@/lib/pages-seo.json'
import Footer from '@/components/landing/Footer.vue'

const titre = [
  { texte: 'Facturation électronique :' },
  { texte: 'ce qui change pour vous', accent: true },
]

/** Les deux échéances, dans l'ordre où elles concernent un artisan. */
const echeances = [
  {
    date: '1er septembre 2026',
    etat: 'En vigueur',
    enCours: true,
    icone: Inbox,
    titre: 'Vous devez pouvoir recevoir une facture électronique',
    texte:
      "Cette étape s'applique à toutes les entreprises, quelle que soit leur taille — y compris les auto-entrepreneurs. Concrètement : vos fournisseurs et vos donneurs d'ordre peuvent désormais vous adresser leurs factures par voie électronique, et vous devez être en mesure de les recevoir.",
  },
  {
    date: '1er septembre 2027',
    etat: 'À préparer',
    enCours: false,
    icone: Send,
    titre: 'Vous devrez émettre vos factures au format électronique',
    texte:
      "C'est l'échéance qui vous concerne directement en tant qu'artisan : elle vise les PME et les micro-entreprises. Un PDF envoyé par email ne suffira plus — la facture devra porter des données structurées, lisibles par une machine.",
  },
]

const aRetenir = [
  {
    icone: FileCheck2,
    titre: 'Un PDF classique ne suffira plus',
    texte:
      "Une facture électronique n'est pas un PDF scanné ou imprimé en PDF. Elle contient des données structurées que les logiciels lisent directement. Les formats admis sont Factur-X, UBL et CII.",
  },
  {
    icone: Building2,
    titre: 'Le portail de l\'État ne transmet plus les factures',
    texte:
      "Le portail public sert désormais d'annuaire : il indique à quelle plateforme chaque entreprise est rattachée. L'envoi et la réception passent par une plateforme agréée, que vous choisissez.",
  },
  {
    icone: UserRound,
    titre: 'Vos clients particuliers ne sont pas oubliés',
    texte:
      "L'obligation de facture électronique vise les échanges entre entreprises. Pour vos chantiers chez des particuliers, c'est la transmission des données de vente qui s'applique. Votre comptable saura vous situer.",
  },
  {
    icone: FileWarning,
    titre: 'Votre numérotation devra tenir',
    texte:
      "Séquence continue, sans trou ni doublon, mentions obligatoires complètes. Ce qui passait sur un tableur devient contrôlable automatiquement.",
  },
]

const cequonFait = [
  {
    icone: FileCheck2,
    titre: 'Vos factures sont déjà au bon format',
    texte:
      'Chaque facture est générée en Factur-X — un PDF lisible par votre client, avec les données structurées intégrées, conforme à la norme européenne EN 16931.',
  },
  {
    icone: CalendarClock,
    titre: 'Votre numérotation est tenue par le logiciel',
    texte:
      "Séquence continue, mentions légales, pénalités de retard et indemnité de recouvrement figurent automatiquement sur chaque facture.",
  },
  {
    icone: ShieldCheck,
    titre: 'Vos données restent en France',
    texte:
      'Hébergement sur un serveur situé à Paris, échanges chiffrés. Vous restez propriétaire de vos documents et pouvez les exporter à tout moment.',
  },
]
</script>

<template>
  <div class="overflow-x-hidden">
    <LandingHero
      badge="Facturation électronique"
      :icone="FileCheck2"
      :titre="titre"
      sous-titre="Depuis le 1er septembre 2026, toute entreprise doit pouvoir recevoir une facture électronique. Au 1er septembre 2027, les artisans devront aussi les émettre. Voici ce que cela implique, sans jargon."
      :preuves="['Format Factur-X intégré', 'Norme européenne EN 16931', 'Essai gratuit 14 jours']"
      large
    />

    <!-- ── Le calendrier ─────────────────────────────────────── -->
    <section class="py-20 lg:py-28">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
        <SectionTitre
          badge="Les deux dates"
          :icone="CalendarClock"
          titre="Suis-je concerné, et à partir de quand ?"
          accroche="La réforme se déroule en deux temps. La première étape est déjà passée."
        />

        <ol class="space-y-6">
          <li
            v-for="(e, i) in echeances"
            :key="e.date"
            v-apparait="i * 110"
            class="relative rounded-3xl border p-6 sm:p-8"
            :class="e.enCours
              ? 'border-primary/40 bg-primary/[0.04]'
              : 'border-border bg-card'"
          >
            <div class="flex flex-wrap items-center gap-3 mb-4">
              <span class="inline-flex items-center justify-center w-10 h-10 rounded-2xl bg-primary/10 text-primary flex-shrink-0">
                <component :is="e.icone" class="w-5 h-5" />
              </span>
              <span class="text-lg font-extrabold text-foreground">{{ e.date }}</span>
              <span
                class="text-xs font-semibold px-2.5 py-1 rounded-full"
                :class="e.enCours
                  ? 'bg-primary/15 text-primary'
                  : 'bg-muted text-muted-foreground'"
              >{{ e.etat }}</span>
            </div>
            <h3 class="text-xl font-bold text-foreground mb-2">{{ e.titre }}</h3>
            <p class="text-muted-foreground leading-relaxed">{{ e.texte }}</p>
          </li>
        </ol>

        <p class="text-sm text-muted-foreground mt-8 leading-relaxed">
          Cette page résume la réforme telle qu'elle s'applique aux artisans. Elle ne
          remplace pas l'avis de votre comptable, et le calendrier officiel fait foi —
          il est publié sur
          <a
            href="https://www.impots.gouv.fr/facturation-electronique"
            target="_blank"
            rel="noopener noreferrer"
            class="text-primary font-medium hover:underline"
          >impots.gouv.fr</a>.
        </p>
      </div>
    </section>

    <!-- ── Ce qu'il faut retenir ─────────────────────────────── -->
    <section class="py-20 lg:py-28 bg-muted/30">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl">
        <SectionTitre
          badge="L'essentiel"
          :icone="HelpCircle"
          titre="Quatre choses à savoir avant 2027"
          accroche="Ce qui revient le plus souvent dans les questions d'artisans."
        />
        <PointsForts :points="aRetenir" :colonnes="2" />
      </div>
    </section>

    <!-- ── Ce que fait ArtisanGestion, et ce qu'il ne fait pas ── -->
    <section class="py-20 lg:py-28">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl">
        <SectionTitre
          badge="Où nous intervenons"
          :icone="FileCheck2"
          titre="Vos factures sont déjà au format attendu"
          accroche="Vous n'aurez pas à changer d'outil ni à reprendre votre historique le jour venu."
        />
        <PointsForts :points="cequonFait" />

        <!-- Le point que la plupart des pages concurrentes passent sous
             silence. Le dire clairement évite une déception après l'achat, et
             c'est aussi ce qui rend le reste de la page crédible. -->
        <div
          v-apparait
          class="mt-10 rounded-3xl border border-amber-500/30 bg-amber-500/[0.06] p-6 sm:p-8"
        >
          <div class="flex items-start gap-4">
            <span class="inline-flex items-center justify-center w-11 h-11 rounded-2xl bg-amber-500/15 text-amber-600 dark:text-amber-400 flex-shrink-0">
              <FileWarning class="w-5 h-5" />
            </span>
            <div>
              <h3 class="text-lg font-bold text-foreground mb-2">
                Ce qu'ArtisanGestion ne fait pas
              </h3>
              <p class="text-muted-foreground leading-relaxed">
                Nous ne sommes pas une plateforme agréée. ArtisanGestion produit la
                facture au bon format ; l'acheminement vers votre client passera par une
                plateforme agréée que vous choisirez — c'est vrai de tout logiciel de
                facturation, et le choix reste le vôtre. Nous préférons vous le dire
                maintenant plutôt qu'en 2027.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <FAQSection
      :cles="pagesSeo['/facturation-electronique-artisan'].faq"
      titre="Ce qu'on nous demande souvent"
    />

    <Pricing />

    <LandingCTA
      badge="Prenez de l'avance"
      titre="Vos factures au bon format, dès aujourd'hui"
      accroche="Rien à migrer, rien à reprendre : vos prochaines factures sortent en Factur-X. Il vous reste un an avant l'échéance, autant ne pas s'y prendre la veille."
      cta="Essayer gratuitement 14 jours"
      :preuves="['Sans carte bancaire', 'Sans engagement', 'Données hébergées en France']"
    />

    <Footer />
  </div>
</template>
