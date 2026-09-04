<script setup lang="ts">
/**
 * Onglet Abonnement, pour un artisan déjà abonné.
 *
 * L'écran affichait la grille des plans avec des boutons « S'abonner » à
 * quelqu'un qui payait déjà — au mieux déroutant, au pire une seconde
 * souscription. On montre ici l'abonnement en cours, puis une seule
 * proposition, choisie selon la formule détenue.
 */
import { ref, computed, onMounted } from 'vue'
import {
  CheckCircle2, CreditCard, Calendar, AlertTriangle, ArrowRight,
  Users, PenTool, Bell, Sparkles, TrendingUp, Loader2,
} from 'lucide-vue-next'
import { apiFetch } from '@/lib/api'
import { dataStore } from '@/lib/store'

const emit = defineEmits<{
  (e: 'demander', sujet: string, message: string, categorie: string): void
}>()

const abonnement = ref<any>(null)
const chargement = ref(true)
const ouvertureportail = ref(false)

const role = computed(() => dashboardUser.value?.role || 'USER')
const dashboardUser = computed(() => dataStore.user.data)
const estEquipe = computed(() => role.value === 'TEAM')
const stats = computed(() => dataStore.dashboard.data || {})

// Catalogue serveur (subscriptions.py). L'économie annuelle est calculée,
// jamais écrite en dur : elle resterait fausse au premier changement de prix.
const TARIFS = {
  Indépendant: { mensuel: 19, annuel: 186 },
  Équipe: { mensuel: 39, annuel: 390 },
}

const planCourant = computed(() => (estEquipe.value ? 'Équipe' : 'Indépendant'))

const economieAnnuelle = computed(() => {
  const t = TARIFS[planCourant.value as keyof typeof TARIFS]
  return t.mensuel * 12 - t.annuel
})

const montantAffiche = computed(() => {
  const c = abonnement.value?.montant_centimes
  if (!c) return null
  return (c / 100).toFixed(2).replace('.', ',') + ' €'
})

const periodeAffichee = computed(() => (abonnement.value?.annuel ? 'par an' : 'par mois'))

const echeanceAffichee = computed(() => {
  const d = abonnement.value?.echeance
  if (!d) return null
  return new Date(d).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric',
  })
})

const impayes = computed(() => Number(stats.value.factures_en_retard_count) || 0)
const montantImpaye = computed(() => {
  const m = Number(stats.value.factures_en_retard_montant) || 0
  return m.toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' €'
})

async function charger() {
  try {
    const res = await apiFetch('subscriptions/me')
    if (res.ok) abonnement.value = await res.json()
  } catch {
    // L'écran reste utilisable sans le détail Stripe : le récapitulatif
    // retombe sur le rôle connu en base.
  } finally {
    chargement.value = false
  }
}

async function ouvrirPortail() {
  ouvertureportail.value = true
  try {
    const res = await apiFetch('subscriptions/create-portal-session', { method: 'POST' })
    const data = await res.json()
    if (data.portal_url) window.location.href = data.portal_url
  } finally {
    ouvertureportail.value = false
  }
}

// ── Changement de formule ──
//
// Deux temps : on demande d'abord au serveur ce qui serait dû, on l'affiche,
// et on n'applique qu'après confirmation. Personne ne doit découvrir un
// prélèvement après coup.
const cible = ref<{ plan: string; annuel: boolean } | null>(null)
const apercu = ref<any>(null)
const calculEnCours = ref(false)
const applicationEnCours = ref(false)
const erreur = ref('')

const montantDu = computed(() => {
  const c = apercu.value?.montant_du_centimes
  if (c === null || c === undefined) return null
  return (c / 100).toFixed(2).replace('.', ',') + ' €'
})

async function preparer(plan: string, annuel: boolean) {
  cible.value = { plan, annuel }
  apercu.value = null
  erreur.value = ''
  calculEnCours.value = true
  try {
    const res = await apiFetch('subscriptions/change-plan', {
      method: 'POST',
      body: JSON.stringify({ plan_name: plan, is_annual: annuel, confirmer: false }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Calcul impossible.')
    apercu.value = data
  } catch (e: any) {
    erreur.value = e.message
  } finally {
    calculEnCours.value = false
  }
}

async function appliquer() {
  if (!cible.value) return
  applicationEnCours.value = true
  erreur.value = ''
  try {
    const res = await apiFetch('subscriptions/change-plan', {
      method: 'POST',
      body: JSON.stringify({
        plan_name: cible.value.plan, is_annual: cible.value.annuel, confirmer: true,
      }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Changement impossible.')
    // Le rôle a changé côté serveur : on recharge pour que toute
    // l'application en tienne compte, pas seulement cet écran.
    await dataStore.fetchUser(true)
    cible.value = null
    apercu.value = null
    await charger()
  } catch (e: any) {
    erreur.value = e.message
  } finally {
    applicationEnCours.value = false
  }
}

function annuler() {
  cible.value = null
  apercu.value = null
  erreur.value = ''
}

onMounted(() => {
  charger()
  dataStore.fetchDashboard?.()
})
</script>

<template>
  <div class="space-y-5">
    <!-- ── Abonnement en cours ── -->
    <div class="rounded-2xl border border-primary/25 bg-primary/5 p-6">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div class="inline-flex items-center gap-2 text-primary text-sm font-semibold mb-2">
            <CheckCircle2 class="w-4 h-4" />
            Abonnement actif
          </div>
          <h3 class="text-2xl font-bold text-foreground">Plan {{ planCourant }}</h3>

          <p v-if="montantAffiche" class="text-muted-foreground mt-1">
            {{ montantAffiche }} HT {{ periodeAffichee }}
          </p>

          <div v-if="chargement" class="flex items-center gap-2 text-sm text-muted-foreground mt-3">
            <Loader2 class="w-4 h-4 animate-spin" /> Chargement du détail…
          </div>

          <!-- Une résiliation programmée doit se voir : c'est l'information
               que l'artisan vient chercher en priorité. -->
          <div
            v-else-if="abonnement?.resiliation_programmee && echeanceAffichee"
            class="flex items-start gap-2 mt-3 text-sm text-amber-700 dark:text-amber-500"
          >
            <AlertTriangle class="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>Résiliation programmée — votre accès prend fin le {{ echeanceAffichee }}.</span>
          </div>
          <div
            v-else-if="echeanceAffichee"
            class="flex items-center gap-2 mt-3 text-sm text-muted-foreground"
          >
            <Calendar class="w-4 h-4" />
            Prochain prélèvement le {{ echeanceAffichee }}
          </div>
        </div>

        <button
          type="button"
          class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-border bg-background text-sm font-semibold hover:bg-muted transition-colors"
          :disabled="ouvertureportail"
          @click="ouvrirPortail"
        >
          <Loader2 v-if="ouvertureportail" class="w-4 h-4 animate-spin" />
          <CreditCard v-else class="w-4 h-4" />
          Factures et résiliation
        </button>
      </div>
    </div>

    <!-- ── Économie annuelle, seulement si la facturation est mensuelle ── -->
    <div
      v-if="abonnement && !abonnement.annuel && !abonnement.resiliation_programmee"
      class="rounded-2xl border border-border bg-card p-5 flex flex-wrap items-center justify-between gap-4"
    >
      <div class="flex items-start gap-3">
        <div class="w-9 h-9 rounded-xl bg-success/15 flex items-center justify-center flex-shrink-0">
          <TrendingUp class="w-4 h-4 text-success" />
        </div>
        <div>
          <p class="font-semibold text-foreground">
            Économisez {{ economieAnnuelle }} € par an
          </p>
          <p class="text-sm text-muted-foreground">
            En facturation annuelle, votre plan {{ planCourant }} revient à
            {{ (TARIFS[planCourant].annuel / 12).toFixed(2).replace('.', ',') }} € HT par mois.
          </p>
        </div>
      </div>
      <button
        type="button"
        class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity"
        @click="preparer(planCourant, true)"
      >
        Passer à l'annuel <ArrowRight class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- ── Indépendant : une seule proposition, chiffrée quand c'est possible ── -->
    <div v-if="!estEquipe" class="rounded-2xl border border-border bg-card p-6">
      <div class="flex items-center gap-2 mb-3">
        <Sparkles class="w-4 h-4 text-primary" />
        <span class="text-sm font-semibold text-primary">Plan Équipe — 39 € HT / mois</span>
      </div>

      <!-- Parler de ses impayés à lui est plus convaincant qu'énumérer des
           fonctionnalités. On n'affiche ce message que s'il est vrai. -->
      <p v-if="impayes > 0" class="text-foreground mb-4">
        Vous avez <strong>{{ impayes }} facture{{ impayes > 1 ? 's' : '' }} en retard</strong>,
        soit <strong>{{ montantImpaye }}</strong> à recouvrer. Le plan Équipe relance vos clients
        automatiquement, sans que vous ayez à y penser.
      </p>
      <p v-else class="text-foreground mb-4">
        Faites signer vos devis à distance, travaillez à plusieurs et retirez la mention
        ArtisanGestion de vos documents.
      </p>

      <ul class="grid sm:grid-cols-2 gap-3 mb-5">
        <li class="flex items-start gap-2.5 text-sm text-muted-foreground">
          <Bell class="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
          Relances d'impayés automatiques et paramétrables
        </li>
        <li class="flex items-start gap-2.5 text-sm text-muted-foreground">
          <PenTool class="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
          Signature à distance, par lien envoyé au client
        </li>
        <li class="flex items-start gap-2.5 text-sm text-muted-foreground">
          <Users class="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
          Collaborateurs, avec gestion des droits
        </li>
        <li class="flex items-start gap-2.5 text-sm text-muted-foreground">
          <Sparkles class="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
          Documents à vos couleurs, sans mention externe
        </li>
      </ul>

      <button
        type="button"
        class="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity"
        @click="preparer('équipe', abonnement?.annuel ?? false)"
      >
        Passer à Équipe <ArrowRight class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- ── Équipe : plus rien à vendre, on rappelle la valeur reçue ── -->
    <div v-else class="rounded-2xl border border-border bg-card p-6">
      <h4 class="font-semibold text-foreground mb-1">Votre mois avec ArtisanGestion</h4>
      <p class="text-sm text-muted-foreground mb-5">
        Vous avez la formule la plus complète. Voici ce qu'elle vous a permis de faire.
      </p>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div>
          <p class="text-2xl font-bold text-foreground">{{ stats.rapports_termines ?? 0 }}</p>
          <p class="text-xs text-muted-foreground">rapports terminés</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-foreground">{{ stats.devis_convertis ?? 0 }}</p>
          <p class="text-xs text-muted-foreground">devis convertis</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-foreground">{{ stats.taux_conversion ?? 0 }} %</p>
          <p class="text-xs text-muted-foreground">taux de conversion</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-foreground">
            {{ Number(stats.ca_mois_ttc ?? 0).toLocaleString('fr-FR', { maximumFractionDigits: 0 }) }} €
          </p>
          <p class="text-xs text-muted-foreground">facturé ce mois-ci</p>
        </div>
      </div>
      <p class="text-sm text-muted-foreground mt-5">
        Une fonctionnalité vous manque&nbsp;?
        <button type="button" class="text-primary underline underline-offset-2"
                @click="emit('demander', 'Suggestion de fonctionnalité', 'Bonjour,\n\nIl me manque :\n\n', 'Suggestion')">
          Dites-le nous
        </button> — les retours des abonnés Équipe orientent nos priorités.
      </p>
    </div>
    <!-- ── Confirmation du changement de formule ── -->
    <Teleport to="body">
      <div
        v-if="cible"
        class="fixed inset-0 z-[300] flex items-center justify-center p-4 bg-black/50"
        @click.self="annuler"
      >
        <div class="w-full max-w-md rounded-2xl bg-background border border-border shadow-2xl p-6">
          <h3 class="text-lg font-bold text-foreground mb-1">
            Passer au plan {{ cible.plan === 'équipe' ? 'Équipe' : 'Indépendant' }}
            {{ cible.annuel ? 'annuel' : 'mensuel' }}
          </h3>

          <div v-if="calculEnCours" class="flex items-center gap-2 text-sm text-muted-foreground py-6">
            <Loader2 class="w-4 h-4 animate-spin" /> Calcul du montant…
          </div>

          <div v-else-if="erreur" class="flex items-start gap-2 text-sm text-destructive py-4">
            <AlertTriangle class="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{{ erreur }}</span>
          </div>

          <template v-else-if="apercu">
            <!-- Le prorata est calculé par Stripe : on affiche le montant
                 réel, jamais une estimation faite ici. -->
            <p v-if="montantDu" class="text-muted-foreground mt-2 mb-5">
              <template v-if="apercu.montee_en_gamme">
                Vous serez prélevé de <strong class="text-foreground">{{ montantDu }}</strong>
                aujourd'hui — la différence au prorata du temps restant. Le nouveau tarif
                s'appliquera ensuite à chaque échéance.
              </template>
              <template v-else>
                Le temps déjà payé vous est crédité sur votre prochaine facture.
                Aucun prélèvement aujourd'hui.
              </template>
            </p>
            <p v-else class="text-muted-foreground mt-2 mb-5">
              Le montant exact sera calculé par Stripe au prorata du temps restant sur
              votre période en cours.
            </p>
          </template>

          <div class="flex gap-2 justify-end">
            <button
              type="button" class="px-4 py-2 rounded-xl border border-border text-sm font-semibold hover:bg-muted"
              :disabled="applicationEnCours" @click="annuler"
            >
              Annuler
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 disabled:opacity-60"
              :disabled="calculEnCours || applicationEnCours || !!erreur"
              @click="appliquer"
            >
              <Loader2 v-if="applicationEnCours" class="w-4 h-4 animate-spin" />
              Confirmer
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
