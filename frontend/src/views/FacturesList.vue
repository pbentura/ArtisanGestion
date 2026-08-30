<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Calendar, Download, Trash2, Search, CheckCircle2, CreditCard, Receipt, Undo2, FileCheck2, MoreVertical, Share2, Mail, Link, BellRing } from 'lucide-vue-next'
import { useMobile } from '@/composables/useMobile'
import MobileSegmentedControl from '@/components/mobile/MobileSegmentedControl.vue'
import MobileFAB from '@/components/mobile/MobileFAB.vue'
import MobileBottomSheet from '@/components/mobile/MobileBottomSheet.vue'
import EmailModal from '@/components/EmailModal.vue'

import { apiFetch } from '@/lib/api'
import { dataStore, uiStore } from '@/lib/store'

const canCreate = computed(() => dataStore.user.data?.can_create_factures !== false)

interface Client {
  nom: string
  email?: string
}

interface Facture {
  id: number
  titre_document_pdf: string
  date_facture: string
  numero_facture: string
  date_echeance: string
  client?: Client
  statut: string
  est_payee: boolean
  est_avoir: boolean
  total_ttc: number
  id_devis?: number
  created_at: string
}

const router = useRouter()
const { sharePDF, triggerHaptic, isNative, isMobileView } = useMobile()
const facturesList = computed(() => dataStore.factures.data)
const trialEnded = computed(() => dataStore.user.data?.trial_days_remaining === 0)
const loading = computed(() => dataStore.factures.loading)
const showDeleteConfirm = ref(false)
const idToDelete = ref<number | null>(null)
const isDeleting = ref(false)
const isUpdatingStatus = ref<number | null>(null)
const showValidateConfirm = ref(false)
const factureToValidate = ref<Facture | null>(null)
const isUpdatingPayment = ref<number | null>(null)
const isCreatingAvoir = ref<number | null>(null)
const isDownloadingFacturX = ref<number | null>(null)
const isGeneratingPaymentLink = ref<number | null>(null)
const copiedPaymentLink = ref<number | null>(null)

const searchQuery = ref('')
const statusFilter = ref('tous') // tous, brouillon, validée
const paymentFilter = ref('tous') // tous, payee, impayee, retard
const typeFilter = ref('tous') // tous, facture, avoir

const activeTab = ref('factures')
const isBottomSheetOpen = ref(false)
const selectedFacture = ref<Facture | null>(null)

const showEmailModal = ref(false)
const emailDocumentId = ref<number | null>(null)
const emailDocumentRef = ref('')
const emailClientEmail = ref('')

function openEmailModal(facture: Facture) {
  emailDocumentId.value = facture.id
  emailDocumentRef.value = facture.numero_facture
  emailClientEmail.value = facture.client?.email || ''
  showEmailModal.value = true
}

function openBottomSheet(facture: Facture) {
  selectedFacture.value = facture
  isBottomSheetOpen.value = true
}

function closeBottomSheet() {
  isBottomSheetOpen.value = false
  setTimeout(() => {
    selectedFacture.value = null
  }, 300)
}

function handleTabChange(val: string) {
  if (val === 'devis') {
    router.push('/app/devis')
  }
}

const filteredFactures = computed(() => {
  let result = facturesList.value

  // Filtrage par texte
  const query = searchQuery.value.toLowerCase().trim()
  if (query) {
    result = result.filter(f => 
      (f.titre_document_pdf?.toLowerCase() || '').includes(query) ||
      (f.numero_facture?.toLowerCase() || '').includes(query) ||
      (f.client?.nom?.toLowerCase() || '').includes(query)
    )
  }

  // Filtrage par statut
  if (statusFilter.value !== 'tous') {
    result = result.filter(f => f.statut === statusFilter.value)
  }

  // Filtrage par type
  if (typeFilter.value === 'facture') {
    result = result.filter(f => !f.est_avoir)
  } else if (typeFilter.value === 'avoir') {
    result = result.filter(f => f.est_avoir)
  }

  // Filtrage par paiement
  if (paymentFilter.value !== 'tous') {
    if (paymentFilter.value === 'payee') {
      result = result.filter(f => f.est_payee)
    } else if (paymentFilter.value === 'impayee') {
      result = result.filter(f => !f.est_payee)
    } else if (paymentFilter.value === 'retard') {
      result = result.filter(f => isOverdue(f) && !f.est_payee)
    }
  }

  return result
})

function openDeleteModal(id: number) {
  idToDelete.value = id
  showDeleteConfirm.value = true
}

function closeDeleteModal() {
  idToDelete.value = null
  showDeleteConfirm.value = false
}

function fetchFactures() {
  dataStore.fetchFactures()
}

function formatDate(dateString: string): string {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

function formatMoney(value: number | string): string {
  return Number(value).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €'
}

async function confirmDelete() {
  if (idToDelete.value === null) return
  
  isDeleting.value = true
  try {
    const res = await apiFetch(`factures/${idToDelete.value}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      dataStore.removeItem('factures', idToDelete.value)
      closeDeleteModal()
    } else {
      alert("Erreur lors de la suppression.")
    }
  } catch (e) {
    console.error(e)
  } finally {
    isDeleting.value = false
  }
}

function requestValidation(facture: Facture) {
  // Valider → modale de confirmation irréversible
  factureToValidate.value = facture
  showValidateConfirm.value = true
}

function closeValidateModal() {
  factureToValidate.value = null
  showValidateConfirm.value = false
}

async function confirmValidation() {
  if (!factureToValidate.value) return
  
  const facture = factureToValidate.value
  isUpdatingStatus.value = facture.id
  
  try {
    const res = await apiFetch(`factures/${facture.id}`, {
      method: 'PUT',
      body: JSON.stringify({ statut: 'validée' })
    })
    
    if (res.ok) {
      const updatedFacture = await res.json()
      dataStore.updateItem('factures', facture.id, updatedFacture)
      closeValidateModal()
    } else {
      console.error('Erreur lors de la validation')
    }
  } catch (e) {
    console.error('Erreur réseau lors de la validation', e)
  } finally {
    isUpdatingStatus.value = null
  }
}

async function togglePayment(facture: Facture) {
  if (isUpdatingPayment.value !== null) return
  
  isUpdatingPayment.value = facture.id
  
  try {
    const res = await apiFetch(`factures/${facture.id}`, {
      method: 'PUT',
      body: JSON.stringify({ est_payee: !facture.est_payee })
    })
    
    if (res.ok) {
      const updatedFacture = await res.json()
      dataStore.updateItem('factures', facture.id, updatedFacture)
    } else {
      console.error('Erreur lors du changement de paiement')
    }
  } catch (e) {
    console.error('Erreur réseau lors du changement de paiement', e)
  } finally {
    isUpdatingPayment.value = null
  }
}

async function creerAvoir(facture: Facture) {
  if (isCreatingAvoir.value !== null) return
  
  if (!confirm(`Voulez-vous vraiment créer un avoir pour la facture ${facture.numero_facture} ?`)) return
  
  isCreatingAvoir.value = facture.id
  
  try {
    const res = await apiFetch(`factures/${facture.id}/avoir`, {
      method: 'POST'
    })
    
    if (res.ok) {
      const nouvelAvoir = await res.json()
      // Rediriger vers l'édition de ce nouvel avoir
      router.push(`/app/factures/${nouvelAvoir.id}`)
    } else {
      const errorData = await res.json()
      alert(`Erreur : ${errorData.detail || 'Impossible de créer un avoir'}`)
    }
  } catch (e) {
    console.error("Erreur réseau lors de la création de l'avoir", e)
    alert("Erreur réseau lors de la création de l'avoir")
  } finally {
    isCreatingAvoir.value = null
  }
}

function isOverdue(facture: Facture): boolean {
  if (facture.est_payee || !facture.date_echeance) return false
  return new Date(facture.date_echeance) < new Date()
}

async function downloadFacturX(facture: Facture) {
  if (isDownloadingFacturX.value !== null) return
  
  isDownloadingFacturX.value = facture.id
  
  try {
    const res = await apiFetch(`factures/${facture.id}/facturx`)
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Erreur inconnue' }))
      alert(`Erreur : ${errorData.detail || 'Impossible de générer le Factur-X'}`)
      return
    }
    
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `FacturX_${facture.numero_facture}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Erreur lors du téléchargement Factur-X', e)
    alert('Erreur réseau lors du téléchargement du Factur-X')
  } finally {
    isDownloadingFacturX.value = null
  }
}

async function copyPaymentLink(facture: Facture) {
  if (isGeneratingPaymentLink.value !== null) return
  
  // Si un lien existe déjà, on le copie directement
  if ((facture as any).stripe_payment_url) {
    try {
      await navigator.clipboard.writeText((facture as any).stripe_payment_url)
      copiedPaymentLink.value = facture.id
      setTimeout(() => { copiedPaymentLink.value = null }, 2000)
    } catch {
      alert('Impossible de copier le lien.')
    }
    return
  }
  
  // Sinon, on le génère d'abord
  isGeneratingPaymentLink.value = facture.id
  try {
    const res = await apiFetch(`factures/${facture.id}/payment-link`, { method: 'POST' })
    if (res.ok) {
      const data = await res.json()
      // Mettre à jour la facture dans le store
      dataStore.updateItem('factures', facture.id, { ...facture, stripe_payment_url: data.payment_url })
      // Copier dans le presse-papier
      await navigator.clipboard.writeText(data.payment_url)
      copiedPaymentLink.value = facture.id
      setTimeout(() => { copiedPaymentLink.value = null }, 2000)
    } else {
      const error = await res.json()
      alert(error.detail || 'Erreur lors de la génération du lien de paiement')
    }
  } catch (e) {
    console.error('Erreur génération lien de paiement:', e)
    alert('Erreur réseau')
  } finally {
    isGeneratingPaymentLink.value = null
  }
}

async function shareFacture(facture: Facture) {
  if (isDownloadingFacturX.value !== null) return
  
  isDownloadingFacturX.value = facture.id
  
  try {
    const res = await apiFetch(`factures/${facture.id}/facturx`)
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Erreur inconnue' }))
      alert(`Erreur : ${errorData.detail || 'Impossible de générer le Factur-X'}`)
      return
    }
    
    const blob = await res.blob()
    const filename = `Facture_${facture.numero_facture}.pdf`
    
    if (isNative) {
      await sharePDF(blob, filename)
      await triggerHaptic()
    } else {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }
  } catch (e) {
    console.error('Erreur lors du partage Factur-X', e)
    alert('Erreur réseau lors du partage du Factur-X')
  } finally {
    isDownloadingFacturX.value = null
  }
}

// ── Relance d'une facture impayée ──

const relanceEnCours = ref<number | null>(null)

function estEchue(f: Facture): boolean {
  if (!f.date_echeance || f.est_payee || f.est_avoir || f.statut !== 'validée') return false
  const echeance = new Date(f.date_echeance)
  echeance.setHours(0, 0, 0, 0)
  const aujourdhui = new Date()
  aujourdhui.setHours(0, 0, 0, 0)
  return echeance < aujourdhui
}

function joursDeRetard(f: Facture): number {
  if (!f.date_echeance) return 0
  const ms = Date.now() - new Date(f.date_echeance).getTime()
  return Math.max(0, Math.floor(ms / 86400000))
}

async function relancerFacture(facture: Facture) {
  if (!facture.client?.email) {
    alert(`Renseignez l'email de ${facture.client?.nom || 'ce client'} dans sa fiche pour pouvoir le relancer.`)
    return
  }

  const retard = joursDeRetard(facture)
  if (!confirm(`Envoyer une relance à ${facture.client.email} pour la facture ${facture.numero_facture} (${retard} jours de retard) ?`)) {
    return
  }

  relanceEnCours.value = facture.id
  try {
    const res = await apiFetch(`factures/${facture.id}/relancer`, { method: 'POST' })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      alert(data.detail || "La relance n'a pas pu être envoyée.")
      return
    }
    alert(`Relance n°${data.niveau} envoyée à ${data.destinataire}.`)
  } catch {
    alert('Erreur réseau. Vérifiez votre connexion et réessayez.')
  } finally {
    relanceEnCours.value = null
  }
}

onMounted(fetchFactures)
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <!-- Mobile Segmented Control for Facturation -->
    <div class="mobile-component lg:hidden mb-6">
      <MobileSegmentedControl 
        v-model="activeTab"
        :options="[
          { label: 'Devis', value: 'devis' },
          { label: 'Factures', value: 'factures' }
        ]"
        @update:modelValue="handleTabChange"
      />
    </div>

    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 hidden lg:flex animate-fade-slide-up">
      <div>
        <div class="flex items-center gap-3">
          <h1 class="text-2xl sm:text-3xl font-bold text-foreground">Factures</h1>
          <span v-if="!loading && facturesList.length > 0" class="px-2.5 py-1 rounded-full text-xs font-semibold bg-muted text-muted-foreground">{{ facturesList.length }}</span>
        </div>
        <p class="text-sm sm:text-base text-muted-foreground mt-1">Gérez vos factures et créez-en de nouvelles</p>
      </div>
      <button
        v-if="canCreate"
        @click="trialEnded ? uiStore.openSubscriptionModal() : router.push('/app/factures/new')"
        class="btn-primary"
        title="Nouvelle facture"
      >
        <Plus class="w-5 h-5" />
        Nouvelle facture
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid gap-4">
      <div v-for="i in 3" :key="i" class="bg-card border border-border rounded-xl p-6 animate-pulse">
        <div class="h-6 bg-muted rounded w-1/3 mb-4"></div>
        <div class="h-4 bg-muted rounded w-1/4 mb-2"></div>
        <div class="h-4 bg-muted rounded w-full"></div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="facturesList.length === 0" class="bg-card border border-border rounded-xl p-12 text-center">
      <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
        <Receipt class="w-8 h-8 text-primary" />
      </div>
      <h3 class="text-lg font-semibold text-foreground mb-2">Aucune facture</h3>
      <p class="text-muted-foreground mb-6">Vous n'avez pas encore créé de facture.</p>
      <button
        v-if="canCreate"
        @click="trialEnded ? uiStore.openSubscriptionModal() : router.push('/app/factures/new')"
        class="btn-primary w-full sm:w-auto"
        title="Nouvelle facture"
      >
        <Plus class="w-4 h-4" />
        Créer ma première facture
      </button>
    </div>

    <!-- Factures List -->
    <div v-else-if="facturesList.length > 0" class="grid gap-4">
      <div class="flex flex-col md:flex-row gap-4 animate-fade-slide-up" style="animation-delay: 0.1s">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher une facture par titre, numéro ou client..."
            class="w-full pl-10 pr-4 py-2.5 bg-card border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
          />
        </div>
        
        <div class="flex flex-wrap items-center gap-3">
          <select 
            v-model="statusFilter"
            class="bg-card border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            <option value="tous">Tous les statuts</option>
            <option value="brouillon">Brouillon</option>
            <option value="validée">Validée</option>
          </select>

          <select 
            v-model="paymentFilter"
            class="bg-card border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            <option value="tous">Tous les paiements</option>
            <option value="payee">Payées</option>
            <option value="impayee">Non payées</option>
            <option value="retard">En retard</option>
          </select>

          <select 
            v-model="typeFilter"
            class="bg-card border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            <option value="tous">Tous les types</option>
            <option value="facture">Factures</option>
            <option value="avoir">Avoirs</option>
          </select>

          <button 
            v-if="searchQuery || statusFilter !== 'tous' || paymentFilter !== 'tous' || typeFilter !== 'tous'"
            @click="searchQuery = ''; statusFilter = 'tous'; paymentFilter = 'tous'; typeFilter = 'tous'"
            class="text-xs font-medium text-primary hover:underline"
          >
            Réinitialiser
          </button>
        </div>
      </div>
      <!-- No results -->
      <div v-if="filteredFactures.length === 0 && searchQuery" class="bg-card border border-border rounded-xl p-12 text-center">
        <div class="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
          <Search class="w-8 h-8 text-muted-foreground" />
        </div>
        <h3 class="text-lg font-semibold text-foreground mb-2">Aucun résultat</h3>
        <p class="text-muted-foreground mb-6">Aucune facture ne correspond à vos filtres actuels.</p>
        <button
          @click="searchQuery = ''; statusFilter = 'tous'; paymentFilter = 'tous'; typeFilter = 'tous'"
          class="btn-primary"
        >
          Effacer la recherche
        </button>
      </div>

      <div
        v-for="(facture, idx) in filteredFactures"
        :key="facture.id"
        class="bg-card border border-border rounded-xl p-4 sm:p-6 hover:border-primary/50 transition-all cursor-pointer animate-fade-slide-up"
        :style="{ animationDelay: (0.15 + idx * 0.05) + 's' }"
        @click="router.push(`/app/factures/${facture.id}`)"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 sm:gap-3 mb-2">
              <h3 class="text-base sm:text-lg font-semibold text-foreground truncate">{{ facture.titre_document_pdf || "Facture" }} - {{ facture.numero_facture }}</h3>
              <span 
                :class="[
                  'px-2 py-1 rounded-full text-xs font-semibold whitespace-nowrap',
                  facture.statut === 'validée' 
                    ? 'bg-green-100 text-green-700 border border-green-200' 
                    : 'bg-blue-100 text-blue-700 border border-blue-200'
                ]"
              >
                {{ facture.statut === 'validée' ? 'Validée' : 'Brouillon' }}
              </span>
              <span 
                v-if="facture.est_avoir"
                class="px-2 py-1 rounded-full text-xs font-semibold whitespace-nowrap bg-purple-100 text-purple-700 border border-purple-200"
              >
                Avoir
              </span>
              <span 
                v-if="facture.statut === 'validée'"
                :class="[
                  'px-2 py-1 rounded-full text-xs font-semibold whitespace-nowrap',
                  facture.est_payee 
                    ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' 
                    : isOverdue(facture)
                      ? 'bg-red-100 text-red-700 border border-red-200'
                      : 'bg-amber-100 text-amber-700 border border-amber-200'
                ]"
              >
                {{ facture.est_payee ? 'Payée' : isOverdue(facture) ? 'En retard' : 'Non payée' }}
              </span>
            </div>
            <div class="flex flex-wrap items-center gap-2 sm:gap-4 text-sm text-muted-foreground">
              <span class="flex items-center gap-1">
                <Calendar class="w-4 h-4" />
                {{ formatDate(facture.date_facture) }}
              </span>
              <span>{{ facture.client?.nom || 'Client inconnu' }}</span>
              <span class="font-semibold text-foreground">{{ formatMoney(facture.total_ttc) }}</span>
              <span v-if="facture.date_echeance" class="text-xs" :class="isOverdue(facture) && !facture.est_payee ? 'text-red-500 font-medium' : ''">
                Échéance: {{ formatDate(facture.date_echeance) }}
              </span>
            </div>
          </div>
          
          <!-- Mobile Actions Trigger -->
          <div class="sm:hidden flex items-center justify-center">
            <button 
              class="p-2 text-muted-foreground hover:bg-muted rounded-full transition-colors"
              @click.stop="openBottomSheet(facture)"
            >
              <MoreVertical class="w-5 h-5" />
            </button>
          </div>

          <div class="hidden sm:flex flex-wrap items-center gap-2 sm:ml-4">
            <!-- Actions principales -->
            <button
              v-if="facture.statut === 'brouillon'"
              @click.stop="requestValidation(facture)"
              class="inline-flex items-center gap-2 px-3 py-1.5 transition-colors rounded-lg group text-green-600 hover:bg-green-50 border border-transparent hover:border-green-200"
              title="Valider cette facture"
              :disabled="isUpdatingStatus === facture.id"
            >
              <template v-if="isUpdatingStatus === facture.id">
                <span class="block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              </template>
              <template v-else>
                <CheckCircle2 class="w-4 h-4 group-hover:scale-110 transition-transform" />
              </template>
              <span class="text-xs font-semibold">Valider</span>
            </button>

            <!-- Relance d'un impayé -->
            <button
              v-if="estEchue(facture) && canCreate"
              @click.stop="relancerFacture(facture)"
              :disabled="relanceEnCours === facture.id"
              class="inline-flex items-center gap-2 px-3 py-1.5 transition-colors rounded-lg group text-orange-600 hover:bg-orange-50 border border-transparent hover:border-orange-200 disabled:opacity-60"
              :title="`Relancer le client — ${joursDeRetard(facture)} jours de retard`"
            >
              <span v-if="relanceEnCours === facture.id"
                    class="block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              <BellRing v-else class="w-4 h-4 group-hover:scale-110 transition-transform" />
              <span class="text-xs font-semibold">Relancer</span>
            </button>

            <button
              v-if="facture.statut === 'validée'"
              @click.stop="togglePayment(facture)"
              class="inline-flex items-center gap-2 px-3 py-1.5 transition-colors rounded-lg group border border-transparent"
              :class="[
                facture.est_payee 
                  ? 'text-emerald-600 hover:bg-emerald-50 hover:border-emerald-200' 
                  : 'text-amber-600 hover:bg-amber-50 hover:border-amber-200'
              ]"
              :title="facture.est_payee ? 'Marquer comme non payée' : 'Marquer comme payée'"
              :disabled="isUpdatingPayment === facture.id"
            >
              <template v-if="isUpdatingPayment === facture.id">
                <span class="block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              </template>
              <template v-else>
                <CreditCard class="w-4 h-4 group-hover:scale-110 transition-transform" />
              </template>
              <span class="text-xs font-semibold">{{ facture.est_payee ? 'Payée' : 'Payer' }}</span>
            </button>

            <button
              v-if="facture.statut === 'validée' && !facture.est_avoir && canCreate"
              @click.stop="creerAvoir(facture)"
              class="inline-flex items-center gap-2 px-3 py-1.5 transition-colors rounded-lg group text-purple-600 hover:bg-purple-50 border border-transparent hover:border-purple-200"
              title="Créer un avoir"
              :disabled="isCreatingAvoir === facture.id"
            >
              <template v-if="isCreatingAvoir === facture.id">
                <span class="block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              </template>
              <template v-else>
                <Undo2 class="w-4 h-4 group-hover:scale-110 transition-transform" />
              </template>
              <span class="text-xs font-semibold">Avoir</span>
            </button>

            <!-- Séparateur -->
            <div class="w-px h-5 bg-border mx-1 hidden lg:block"></div>

            <!-- Téléchargements -->
            <button
              v-if="facture.statut === 'validée'"
              @click.stop="downloadFacturX(facture)"
              class="inline-flex items-center gap-2 px-3 py-1.5 transition-colors rounded-lg group text-teal-600 hover:bg-teal-50 border border-transparent hover:border-teal-200"
              title="Télécharger Factur-X (PDF/A-3 + XML)"
              :disabled="isDownloadingFacturX === facture.id"
            >
              <template v-if="isDownloadingFacturX === facture.id">
                <span class="block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              </template>
              <template v-else>
                <FileCheck2 class="w-4 h-4 group-hover:scale-110 transition-transform" />
              </template>
              <span class="text-xs font-semibold">Factur-X</span>
            </button>

            <button
              v-if="facture.statut === 'validée' && !facture.est_payee && !facture.est_avoir"
              @click.stop="copyPaymentLink(facture)"
              class="inline-flex items-center gap-2 px-3 py-1.5 transition-colors rounded-lg group border border-transparent"
              :class="[
                copiedPaymentLink === facture.id 
                  ? 'text-green-600 bg-green-50 border-green-200' 
                  : 'text-indigo-600 hover:bg-indigo-50 hover:border-indigo-200'
              ]"
              :title="copiedPaymentLink === facture.id ? 'Lien copié !' : 'Copier le lien de paiement'"
              :disabled="isGeneratingPaymentLink === facture.id"
            >
              <template v-if="isGeneratingPaymentLink === facture.id">
                <span class="block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              </template>
              <template v-else-if="copiedPaymentLink === facture.id">
                <CheckCircle2 class="w-4 h-4" />
              </template>
              <template v-else>
                <Link class="w-4 h-4 group-hover:scale-110 transition-transform" />
              </template>
              <span class="text-xs font-semibold">{{ copiedPaymentLink === facture.id ? 'Copié !' : 'Lien paiement' }}</span>
            </button>

            <button
              v-if="facture.statut === 'validée'"
              @click.stop="trialEnded ? uiStore.openSubscriptionModal() : openEmailModal(facture)"
              class="inline-flex items-center gap-2 px-3 py-1.5 text-muted-foreground hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors border border-transparent hover:border-blue-200"
              title="Envoyer par e-mail"
            >
              <Mail class="w-4 h-4 group-hover:scale-110 transition-transform" />
              <span class="text-xs font-semibold">E-mail</span>
            </button>

            <button
              @click.stop="router.push(`/app/factures/${facture.id}/pdf`)"
              class="inline-flex items-center gap-2 px-3 py-1.5 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-lg transition-colors border border-transparent hover:border-primary/20"
              title="Aperçu PDF"
            >
              <Download class="w-4 h-4" />
              <span class="text-xs font-semibold">PDF</span>
            </button>

            <!-- Suppression (brouillons uniquement) -->
            <button
              v-if="facture.statut !== 'validée'"
              @click.stop="openDeleteModal(facture.id)"
              class="inline-flex items-center gap-2 px-3 py-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors border border-transparent hover:border-destructive/20"
              title="Supprimer"
            >
              <Trash2 class="w-4 h-4" />
              <span class="text-xs font-semibold">Suppr.</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Empty State (inside the list block) -->

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-background/80 backdrop-blur-sm" @click="closeDeleteModal"></div>
      <div class="relative bg-card border border-border rounded-xl shadow-lg max-w-sm w-full p-6 animate-in fade-in zoom-in duration-200">
        <h3 class="text-lg font-semibold text-foreground mb-2">Confirmer la suppression</h3>
        <p class="text-muted-foreground mb-6">Voulez-vous vraiment supprimer cette facture ? Cette action est irréversible.</p>
        <div class="flex justify-end gap-3">
          <button 
            @click="closeDeleteModal" 
            class="px-4 py-2 text-sm font-medium border border-border rounded-lg hover:bg-muted transition-colors"
            :disabled="isDeleting"
          >
            Annuler
          </button>
          <button 
            @click="confirmDelete" 
            class="px-4 py-2 text-sm font-medium bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors flex items-center gap-2"
            :disabled="isDeleting"
          >
            <span v-if="isDeleting" class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
            Supprimer
          </button>
        </div>
      </div>
    </div>

    <!-- Validate Confirmation Modal -->
    <div v-if="showValidateConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-background/80 backdrop-blur-sm" @click="closeValidateModal"></div>
      <div class="relative bg-card border border-border rounded-xl shadow-lg max-w-sm w-full p-6 animate-in fade-in zoom-in duration-200">
        <div class="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle2 class="w-6 h-6 text-amber-600" />
        </div>
        <h3 class="text-lg font-semibold text-foreground mb-2 text-center">Valider cette facture ?</h3>
        <p class="text-muted-foreground mb-2 text-center text-sm">Une fois validée, cette facture ne pourra plus être modifiée ni supprimée.</p>
        <p class="text-destructive font-medium mb-6 text-center text-sm">Cette action est irréversible.</p>
        <div class="flex justify-end gap-3">
          <button 
            @click="closeValidateModal" 
            class="px-4 py-2 text-sm font-medium border border-border rounded-lg hover:bg-muted transition-colors"
            :disabled="isUpdatingStatus !== null"
          >
            Annuler
          </button>
          <button 
            @click="confirmValidation" 
            class="px-4 py-2 text-sm font-medium bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
            :disabled="isUpdatingStatus !== null"
          >
            <span v-if="isUpdatingStatus !== null" class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
            Valider définitivement
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile FAB -->
    <MobileFAB v-if="isMobileView && canCreate" @click="router.push('/app/factures/new')" />

    <!-- Mobile Bottom Sheet for Actions -->
    <MobileBottomSheet 
      :is-open="isBottomSheetOpen" 
      :title="selectedFacture ? `Facture ${selectedFacture.numero_facture}` : ''"
      @close="closeBottomSheet"
    >
      <div v-if="selectedFacture" class="flex flex-col gap-2 mt-4">
        
        <button
          v-if="selectedFacture.statut === 'brouillon'"
          @click="requestValidation(selectedFacture); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-foreground bg-muted/50 hover:bg-muted transition-colors text-left"
        >
          <CheckCircle2 class="w-5 h-5" />
          <span class="font-medium">Valider cette facture</span>
        </button>

        <button
          v-if="selectedFacture.statut === 'validée'"
          @click="togglePayment(selectedFacture); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-foreground bg-muted/50 hover:bg-muted transition-colors text-left"
        >
          <CreditCard class="w-5 h-5" />
          <span class="font-medium">{{ selectedFacture.est_payee ? 'Marquer comme non payée' : 'Marquer comme payée' }}</span>
        </button>

        <button
          v-if="selectedFacture.statut === 'validée' && !selectedFacture.est_avoir && canCreate"
          @click="creerAvoir(selectedFacture); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-foreground bg-muted/50 hover:bg-muted transition-colors text-left"
        >
          <Undo2 class="w-5 h-5" />
          <span class="font-medium">Créer un avoir</span>
        </button>

        <button
          v-if="selectedFacture.statut === 'validée'"
          @click="shareFacture(selectedFacture); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-foreground bg-muted/50 hover:bg-muted transition-colors text-left"
        >
          <Share2 class="w-5 h-5" />
          <span class="font-medium">Partager la facture (PDF)</span>
        </button>

        <button 
          v-if="selectedFacture.statut === 'validée'"
          @click="trialEnded ? uiStore.openSubscriptionModal() : openEmailModal(selectedFacture); closeBottomSheet()"
          class="w-full text-left px-4 py-3 flex items-center gap-3 active:bg-muted transition-colors"
        >
          <Mail class="w-5 h-5 text-foreground" />
          <span class="font-medium">Envoyer par e-mail <span v-if="trialEnded" class="text-xs text-red-500">(Essai terminé)</span></span>
        </button>

        <button
          v-if="selectedFacture.statut === 'validée'"
          @click="downloadFacturX(selectedFacture); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-foreground bg-muted/50 hover:bg-muted transition-colors text-left"
        >
          <FileCheck2 class="w-5 h-5" />
          <span class="font-medium">Télécharger Factur-X</span>
        </button>

        <button
          @click="router.push(`/app/factures/${selectedFacture.id}/pdf`); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-foreground bg-muted/50 hover:bg-muted transition-colors text-left"
        >
          <Download class="w-5 h-5" />
          <span class="font-medium">Aperçu PDF</span>
        </button>

        <button
          v-if="selectedFacture.statut !== 'validée'"
          @click="openDeleteModal(selectedFacture.id); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-destructive bg-destructive/10 transition-colors text-left mt-4"
        >
          <Trash2 class="w-5 h-5" />
          <span class="font-medium">Supprimer la facture</span>
        </button>

      </div>
    </MobileBottomSheet>

    <EmailModal
      :is-open="showEmailModal"
      :document-id="emailDocumentId"
      document-type="facture"
      :document-ref="emailDocumentRef"
      :client-email="emailClientEmail"
      @close="showEmailModal = false"
      @success="fetchFactures"
    />
  </div>
</template>
