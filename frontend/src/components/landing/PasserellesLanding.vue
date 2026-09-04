<script setup lang="ts">
/**
 * Renvois de la page d'accueil vers les trois pages spécialisées.
 *
 * Remplace l'ancienne section détaillée sur les rapports IA, déplacée sur
 * /rapport-intervention. La page d'accueil s'adresse à un visiteur qui ne
 * connaît pas encore le produit : elle doit donner la vue d'ensemble et
 * l'orienter, pas dérouler un seul cas d'usage en pleine longueur.
 */
import { useRouter } from 'vue-router'
import { Sparkles, Receipt, Smartphone, ArrowRight } from 'lucide-vue-next'
import SectionTitre from './SectionTitre.vue'

const router = useRouter()

const passerelles = [
  {
    to: '/rapport-intervention',
    icone: Sparkles,
    titre: 'Rapports d’intervention',
    accroche: 'Une phrase suffit : l’IA rédige le compte rendu professionnel en une dizaine de secondes.',
    lien: 'Voir comment l’IA rédige',
  },
  {
    to: '/devis-factures',
    icone: Receipt,
    titre: 'Devis & factures',
    accroche: 'Du chiffrage sur le chantier au paiement encaissé, sans jamais ressaisir une ligne.',
    lien: 'Voir le parcours complet',
  },
  {
    to: '/mobile',
    icone: Smartphone,
    titre: 'Sur le terrain',
    accroche: 'Photos, signature client et documents depuis votre téléphone. Rien à installer.',
    lien: 'Voir l’usage mobile',
  },
]
</script>

<template>
  <section class="py-20 lg:py-28 bg-muted/30 border-y border-border/50">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <SectionTitre
        badge="Trois usages, un seul compte"
        :icone="Sparkles"
        titre="Par quoi voulez-vous commencer&nbsp;?"
        accroche="Chaque partie du logiciel se suffit à elle-même — et elles communiquent toutes entre elles."
      />

      <div class="grid md:grid-cols-3 gap-6">
        <button
          v-for="(p, i) in passerelles"
          :key="p.to"
          v-apparait="i * 100"
          type="button"
          class="group text-left rounded-3xl bg-card border border-border/50 p-7 hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5 transition-all duration-500"
          @click="router.push(p.to)"
        >
          <div class="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mb-5">
            <component :is="p.icone" class="h-6 w-6 text-primary" />
          </div>
          <h3 class="text-xl font-bold text-foreground mb-2.5">{{ p.titre }}</h3>
          <p class="text-sm text-muted-foreground leading-relaxed mb-5">{{ p.accroche }}</p>
          <span class="inline-flex items-center gap-1.5 text-sm font-semibold text-primary">
            {{ p.lien }}
            <ArrowRight class="h-4 w-4 group-hover:translate-x-1 transition-transform" />
          </span>
        </button>
      </div>
    </div>
  </section>
</template>
