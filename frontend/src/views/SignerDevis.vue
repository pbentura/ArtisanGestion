<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { API_BASE_URL } from '@/lib/api'
import { Loader2, CheckCircle2, AlertCircle, Eraser, PenLine } from 'lucide-vue-next'

const route = useRoute()
const token = route.params.token as string

const chargement = ref(true)
const erreur = ref<string | null>(null)
const devis = ref<any>(null)
const envoi = ref(false)

const nomSignataire = ref('')
const emailSignataire = ref('')
const conditionsAcceptees = ref(false)
const erreurFormulaire = ref<string | null>(null)

// ── Zone de signature ──
const canvas = ref<HTMLCanvasElement | null>(null)
let ctx: CanvasRenderingContext2D | null = null
let dessine = false
const aSigne = ref(false)

const dejaSigne = computed(() => devis.value?.deja_signe === true)
const couleur = computed(() => devis.value?.societe?.couleur_document || '#2563eb')

function formatEuros(v: number | string) {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' })
    .format(Number(v ?? 0))
}

function formatDate(d: string | null) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })
}

async function charger() {
  chargement.value = true
  erreur.value = null
  try {
    const res = await fetch(`${API_BASE_URL}/api/devis/public/${token}`)
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      erreur.value = data.detail || "Ce lien de signature n'est pas valide."
      return
    }
    devis.value = await res.json()
  } catch {
    erreur.value = "Impossible de charger le devis. Vérifiez votre connexion."
  } finally {
    chargement.value = false
  }

  // Le canvas n'existe dans le DOM qu'une fois `chargement` repassé à false :
  // l'initialiser plus tôt le laisserait à sa taille par défaut (300x150) et
  // le tracé partirait complètement à côté du curseur.
  if (devis.value && !dejaSigne.value) {
    await nextTick()
    initCanvas()
  }
}

function initCanvas() {
  const el = canvas.value
  if (!el) return
  // Rendu net sur écrans haute densité
  const ratio = window.devicePixelRatio || 1
  const rect = el.getBoundingClientRect()
  el.width = rect.width * ratio
  el.height = rect.height * ratio
  ctx = el.getContext('2d')
  if (!ctx) return
  ctx.scale(ratio, ratio)
  ctx.lineWidth = 2.2
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  ctx.strokeStyle = '#111827'
}

function positionOf(e: MouseEvent | TouchEvent) {
  const el = canvas.value!
  const rect = el.getBoundingClientRect()
  const p = 'touches' in e ? e.touches[0] : e
  return { x: p.clientX - rect.left, y: p.clientY - rect.top }
}

function commencer(e: MouseEvent | TouchEvent) {
  if (!ctx) return
  e.preventDefault()
  dessine = true
  const { x, y } = positionOf(e)
  ctx.beginPath()
  ctx.moveTo(x, y)
}

function tracer(e: MouseEvent | TouchEvent) {
  if (!dessine || !ctx) return
  e.preventDefault()
  const { x, y } = positionOf(e)
  ctx.lineTo(x, y)
  ctx.stroke()
  aSigne.value = true
}

function terminer() {
  dessine = false
}

function effacer() {
  const el = canvas.value
  if (!el || !ctx) return
  ctx.clearRect(0, 0, el.width, el.height)
  aSigne.value = false
}

async function signer() {
  erreurFormulaire.value = null

  if (nomSignataire.value.trim().length < 2) {
    erreurFormulaire.value = 'Merci d\'indiquer votre nom complet.'
    return
  }
  if (!aSigne.value) {
    erreurFormulaire.value = 'Merci de tracer votre signature dans le cadre prévu.'
    return
  }
  if (!conditionsAcceptees.value) {
    erreurFormulaire.value = 'Vous devez accepter les conditions du devis pour le signer.'
    return
  }

  envoi.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/api/devis/public/${token}/signer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        signature: canvas.value!.toDataURL('image/png'),
        nom_signataire: nomSignataire.value.trim(),
        email_signataire: emailSignataire.value.trim() || null,
        accepte_conditions: conditionsAcceptees.value,
      }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      erreurFormulaire.value = data.detail || "La signature n'a pas pu être enregistrée."
      return
    }
    devis.value = data
  } catch {
    erreurFormulaire.value = "Échec de l'envoi. Vérifiez votre connexion et réessayez."
  } finally {
    envoi.value = false
  }
}

// Une rotation d'écran ou un redimensionnement change la taille CSS du canvas
// sans toucher à son buffer : sans réinitialisation, le tracé se décale du
// curseur. On réinstalle le buffer et on y replace le tracé existant.
let minuteurResize: ReturnType<typeof setTimeout> | null = null

function surRedimensionnement() {
  if (!canvas.value || dejaSigne.value) return
  if (minuteurResize) clearTimeout(minuteurResize)
  minuteurResize = setTimeout(() => {
    const el = canvas.value
    if (!el) return
    const rect = el.getBoundingClientRect()
    if (el.width === Math.round(rect.width * (window.devicePixelRatio || 1))) return

    const precedent = aSigne.value ? el.toDataURL('image/png') : null
    initCanvas()
    if (precedent && ctx) {
      const img = new Image()
      img.onload = () => ctx?.drawImage(img, 0, 0, rect.width, rect.height)
      img.src = precedent
    }
  }, 150)
}

onMounted(() => {
  charger()
  window.addEventListener('resize', surRedimensionnement)
})

onUnmounted(() => {
  window.removeEventListener('resize', surRedimensionnement)
  if (minuteurResize) clearTimeout(minuteurResize)
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-6 px-4 sm:py-12">
    <!-- Chargement -->
    <div v-if="chargement" class="flex flex-col items-center justify-center min-h-[60vh] gap-3">
      <Loader2 class="w-8 h-8 animate-spin text-slate-400" />
      <p class="text-slate-500 text-sm">Chargement du devis…</p>
    </div>

    <!-- Lien invalide -->
    <div v-else-if="erreur" class="max-w-md mx-auto mt-16 bg-white rounded-2xl shadow-sm border border-slate-200 p-8 text-center">
      <div class="w-14 h-14 rounded-full bg-red-50 flex items-center justify-center mx-auto mb-4">
        <AlertCircle class="w-7 h-7 text-red-500" />
      </div>
      <h1 class="text-xl font-bold text-slate-900 mb-2">Lien indisponible</h1>
      <p class="text-slate-600 text-sm leading-relaxed">{{ erreur }}</p>
    </div>

    <div v-else class="max-w-3xl mx-auto">
      <!-- Confirmation -->
      <div v-if="dejaSigne" class="bg-white rounded-2xl shadow-sm border border-emerald-200 p-8 text-center mb-6">
        <div class="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-4">
          <CheckCircle2 class="w-8 h-8 text-emerald-600" />
        </div>
        <h1 class="text-2xl font-bold text-slate-900 mb-2">Devis signé</h1>
        <p class="text-slate-600">
          Signé par <strong>{{ devis.signature_nom }}</strong>
          le {{ formatDate(devis.signature_le) }}.
        </p>
        <p class="text-slate-500 text-sm mt-3">
          {{ devis.societe.nom }} a été prévenu. Vous pouvez fermer cette page.
        </p>
      </div>

      <!-- Devis -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden mb-6">
        <div class="h-1.5" :style="{ backgroundColor: couleur }"></div>

        <div class="p-6 sm:p-8">
          <div class="flex flex-wrap items-start justify-between gap-4 mb-8">
            <div>
              <img v-if="devis.societe.logo" :src="devis.societe.logo" alt=""
                   class="h-12 mb-3 object-contain" />
              <p class="font-bold text-slate-900 text-lg">{{ devis.societe.nom }}</p>
              <p v-if="devis.societe.adresse" class="text-sm text-slate-500">{{ devis.societe.adresse }}</p>
              <p v-if="devis.societe.ville" class="text-sm text-slate-500">
                {{ devis.societe.code_postal }} {{ devis.societe.ville }}
              </p>
              <p v-if="devis.societe.siret" class="text-xs text-slate-400 mt-1">
                SIRET {{ devis.societe.siret }}
              </p>
            </div>
            <div class="text-right">
              <p class="text-xs uppercase tracking-wide text-slate-400 font-semibold">
                {{ devis.titre_document_pdf }}
              </p>
              <p class="text-xl font-bold text-slate-900">{{ devis.numero_devis }}</p>
              <p class="text-sm text-slate-500 mt-1">{{ formatDate(devis.date_devis) }}</p>
              <p class="text-sm text-slate-500">Client : {{ devis.client_nom }}</p>
            </div>
          </div>

          <p v-if="devis.objet_devis" class="text-slate-700 mb-6">
            <span class="font-semibold">Objet :</span> {{ devis.objet_devis }}
          </p>

          <!-- Lignes -->
          <div class="overflow-x-auto -mx-2 px-2">
            <table class="w-full text-sm min-w-[480px]">
              <thead>
                <tr class="border-b border-slate-200 text-slate-500 text-xs uppercase tracking-wide">
                  <th class="text-left py-2 font-semibold">Désignation</th>
                  <th class="text-right py-2 font-semibold w-16">Qté</th>
                  <th class="text-right py-2 font-semibold w-24">P.U. HT</th>
                  <th class="text-right py-2 font-semibold w-16">TVA</th>
                  <th class="text-right py-2 font-semibold w-28">Total HT</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ligne in devis.lignes" :key="ligne.id" class="border-b border-slate-100">
                  <td class="py-3 text-slate-800 pr-4">{{ ligne.description }}</td>
                  <td class="py-3 text-right text-slate-600 tabular-nums">{{ ligne.quantite }}</td>
                  <td class="py-3 text-right text-slate-600 tabular-nums">{{ formatEuros(ligne.prix_unite_ht) }}</td>
                  <td class="py-3 text-right text-slate-600 tabular-nums">{{ ligne.taux_tva }}%</td>
                  <td class="py-3 text-right text-slate-800 font-medium tabular-nums">{{ formatEuros(ligne.total_ht) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Totaux -->
          <div class="flex justify-end mt-6">
            <div class="w-full sm:w-72 space-y-2 text-sm">
              <div class="flex justify-between text-slate-600">
                <span>Total HT</span>
                <span class="tabular-nums">{{ formatEuros(devis.sous_total_ht) }}</span>
              </div>
              <div class="flex justify-between text-slate-600">
                <span>TVA</span>
                <span class="tabular-nums">{{ formatEuros(devis.total_tva) }}</span>
              </div>
              <div class="flex justify-between text-lg font-bold text-slate-900 pt-2 border-t border-slate-200">
                <span>Total TTC</span>
                <span class="tabular-nums">{{ formatEuros(devis.total_ttc) }}</span>
              </div>
            </div>
          </div>

          <div v-if="devis.conditions_particulieres" class="mt-8 pt-6 border-t border-slate-200">
            <p class="text-xs uppercase tracking-wide text-slate-400 font-semibold mb-2">
              Conditions particulières
            </p>
            <p class="text-sm text-slate-600 whitespace-pre-line">{{ devis.conditions_particulieres }}</p>
          </div>

          <p class="text-xs text-slate-400 mt-6">
            Devis valable {{ devis.nb_jours_validite }} jours à compter du {{ formatDate(devis.date_devis) }}.
          </p>
        </div>
      </div>

      <!-- Signature -->
      <div v-if="!dejaSigne" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
        <div class="flex items-center gap-2 mb-1">
          <PenLine class="w-5 h-5" :style="{ color: couleur }" />
          <h2 class="text-lg font-bold text-slate-900">Signer le devis</h2>
        </div>
        <p class="text-sm text-slate-500 mb-6">
          Votre signature vaut acceptation du devis et de son montant.
        </p>

        <div class="grid sm:grid-cols-2 gap-4 mb-5">
          <div>
            <label for="nom" class="block text-sm font-medium text-slate-700 mb-1.5">
              Nom et prénom <span class="text-red-500">*</span>
            </label>
            <input id="nom" v-model="nomSignataire" type="text" autocomplete="name"
                   placeholder="Marie Dupont"
                   class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-offset-0 focus:border-transparent"
                   :style="{ '--tw-ring-color': couleur }" />
          </div>
          <div>
            <label for="email" class="block text-sm font-medium text-slate-700 mb-1.5">
              Email <span class="text-slate-400 font-normal">(facultatif)</span>
            </label>
            <input id="email" v-model="emailSignataire" type="email" autocomplete="email"
                   placeholder="marie@exemple.fr"
                   class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:border-transparent"
                   :style="{ '--tw-ring-color': couleur }" />
          </div>
        </div>

        <div class="mb-5">
          <div class="flex items-center justify-between mb-1.5">
            <label class="block text-sm font-medium text-slate-700">
              Votre signature <span class="text-red-500">*</span>
            </label>
            <button type="button" @click="effacer"
                    class="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 transition-colors">
              <Eraser class="w-3.5 h-3.5" /> Effacer
            </button>
          </div>
          <canvas
            ref="canvas"
            class="w-full h-44 rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 touch-none cursor-crosshair"
            @mousedown="commencer" @mousemove="tracer" @mouseup="terminer" @mouseleave="terminer"
            @touchstart="commencer" @touchmove="tracer" @touchend="terminer"
          ></canvas>
          <p class="text-xs text-slate-400 mt-1.5">
            Signez avec votre souris, ou directement au doigt sur mobile.
          </p>
        </div>

        <label class="flex items-start gap-2.5 mb-5 cursor-pointer">
          <input v-model="conditionsAcceptees" type="checkbox"
                 class="mt-0.5 w-4 h-4 rounded border-slate-300 shrink-0" />
          <span class="text-sm text-slate-600">
            J'accepte le devis {{ devis.numero_devis }} pour un montant de
            <strong>{{ formatEuros(devis.total_ttc) }} TTC</strong> et ses conditions.
          </span>
        </label>

        <p v-if="erreurFormulaire" class="text-sm text-red-600 mb-4 flex items-start gap-1.5">
          <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" /> {{ erreurFormulaire }}
        </p>

        <button type="button" @click="signer" :disabled="envoi"
                class="w-full rounded-lg py-3.5 text-white font-semibold transition-opacity disabled:opacity-60 flex items-center justify-center gap-2"
                :style="{ backgroundColor: couleur }">
          <Loader2 v-if="envoi" class="w-5 h-5 animate-spin" />
          {{ envoi ? 'Enregistrement…' : 'Signer et accepter le devis' }}
        </button>

        <p class="text-xs text-slate-400 text-center mt-4 leading-relaxed">
          En signant, vous acceptez que la date, votre adresse IP et votre navigateur soient
          enregistrés à titre de preuve. Signature électronique simple au sens du règlement eIDAS.
        </p>
      </div>

      <p class="text-center text-xs text-slate-400 mt-6">
        Document transmis via ArtisanGestion
      </p>
    </div>
  </div>
</template>
