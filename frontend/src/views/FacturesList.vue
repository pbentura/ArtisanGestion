<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Calendar, Download, Trash2, Search, CheckCircle2, CreditCard, Receipt, Undo2, FileCheck2 } from 'lucide-vue-next'

import { apiFetch } from '@/lib/api'

interface Client {
  nom: string
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
const facturesList = ref<Facture[]>([])
const loading = ref(true)
const showDeleteConfirm = ref(false)
const idToDelete = ref<number | null>(null)
const isDeleting = ref(false)
const isUpdatingStatus = ref<number | null>(null)
const showValidateConfirm = ref(false)
const factureToValidate = ref<Facture | null>(null)
const isUpdatingPayment = ref<number | null>(null)
const isCreatingAvoir = ref<number | null>(null)
const isDownloadingFacturX = ref<number | null>(null)

const searchQuery = ref('')
const statusFilter = ref('tous') // tous, brouillon, validée
const paymentFilter = ref('tous') // tous, payee, impayee, retard
const typeFilter = ref('tous') // tous, facture, avoir

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

async function fetchFactures() {
  loading.value = true
  try {
    const res = await apiFetch('factures')
    if (res.ok) {
      facturesList.value = await res.json()
    } else {
      const errorText = await res.text()
      console.error('Erreur API factures:', errorText)
      if (res.status === 401) {
        localStorage.removeItem('token')
        router.push('/auth')
      }
    }
  } catch (e) {
    console.error('Erreur lors du chargement des factures', e)
  } finally {
    loading.value = false
  }
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
      facturesList.value = facturesList.value.filter(f => f.id !== idToDelete.value)
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
      const index = facturesList.value.findIndex(f => f.id === facture.id)
      if (index !== -1) {
        facturesList.value[index] = updatedFacture
      }
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
      const index = facturesList.value.findIndex(f => f.id === facture.id)
      if (index !== -1) {
        facturesList.value[index] = updatedFacture
      }
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

onMounted(fetchFactures)
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <div class="flex items-center gap-3">
          <h1 class="text-2xl sm:text-3xl font-bold text-foreground">Factures</h1>
          <span v-if="!loading && facturesList.length > 0" class="px-2.5 py-1 rounded-full text-xs font-semibold bg-muted text-muted-foreground">{{ facturesList.length }}</span>
        </div>
        <p class="text-sm sm:text-base text-muted-foreground mt-1">Gérez vos factures et créez-en de nouvelles</p>
      </div>
      <button
        @click="router.push('/app/factures/new')"
        class="inline-flex items-center justify-center gap-2 bg-primary text-primary-foreground px-4 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors shrink-0 w-full sm:w-auto"
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
        @click="router.push('/app/factures/new')"
        class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
      >
        <Plus class="w-4 h-4" />
        Créer ma première facture
      </button>
    </div>

    <!-- Factures List -->
    <div v-else-if="facturesList.length > 0" class="grid gap-4">
      <div class="flex flex-col md:flex-row gap-4">
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
          class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
        >
          Effacer la recherche
        </button>
      </div>

      <div
        v-for="facture in filteredFactures"
        :key="facture.id"
        class="bg-card border border-border rounded-xl p-4 sm:p-6 hover:border-primary/50 transition-all cursor-pointer"
        @click="router.push(`/app/factures/${facture.id}`)"
      >
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
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
          <div class="flex flex-wrap items-center gap-2 sm:ml-4">
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
              v-if="facture.statut === 'validée' && !facture.est_avoir"
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
  </div>
</template>
