<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Calendar, Download, Trash2, Search, CheckCircle2, CreditCard, Receipt, Undo2 } from 'lucide-vue-next'

import { API_BASE_URL } from '@/lib/api'

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

const searchQuery = ref('')

const filteredFactures = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return facturesList.value
  return facturesList.value.filter(f => 
    (f.titre_document_pdf?.toLowerCase() || '').includes(query) ||
    (f.numero_facture?.toLowerCase() || '').includes(query) ||
    (f.client?.nom?.toLowerCase() || '').includes(query)
  )
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
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/factures/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (res.ok) {
      facturesList.value = await res.json()
    } else {
      console.error('Erreur API factures', await res.text())
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
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/factures/${idToDelete.value}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
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
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/factures/${facture.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
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
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/factures/${facture.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
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
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/factures/${facture.id}/avoir`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      }
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
    console.error('Erreur réseau lors de la création de l\\'avoir', e)
    alert('Erreur réseau lors de la création de l\\'avoir')
  } finally {
    isCreatingAvoir.value = null
  }
}

function isOverdue(facture: Facture): boolean {
  if (facture.est_payee || !facture.date_echeance) return false
  return new Date(facture.date_echeance) < new Date()
}

onMounted(fetchFactures)
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-foreground">Factures</h1>
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
      <div class="relative">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Rechercher une facture par titre, numéro ou client..."
          class="w-full pl-10 pr-4 py-2.5 bg-card border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
        />
      </div>
      <div
        v-for="facture in filteredFactures"
        :key="facture.id"
        class="bg-card border border-border rounded-xl p-4 sm:p-6 hover:border-primary/50 transition-colors cursor-pointer"
        @click="router.push(`/app/factures/${facture.id}`)"
      >
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 sm:gap-3 mb-2">
              <h3 class="text-base sm:text-lg font-semibold text-foreground truncate">{{ facture.titre_document_pdf || "Facture" }} - {{ facture.numero_facture }}</h3>
              <span 
                :class="[
                  'px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap',
                  facture.statut === 'validée' 
                    ? 'bg-green-100 text-green-700 font-bold border border-green-200' 
                    : 'bg-blue-100 text-blue-700 font-bold border border-blue-200'
                ]"
              >
                {{ facture.statut }}
              </span>
              <span 
                v-if="facture.est_avoir"
                class="px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap bg-purple-100 text-purple-700 font-bold border border-purple-200"
              >
                Avoir
              </span>
              <span 
                :class="[
                  'px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap',
                  facture.est_payee 
                    ? 'bg-emerald-100 text-emerald-700 font-bold border border-emerald-200' 
                    : isOverdue(facture)
                      ? 'bg-red-100 text-red-700 font-bold border border-red-200'
                      : 'bg-amber-100 text-amber-700 font-bold border border-amber-200'
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
          <div class="flex items-center gap-2 sm:ml-4">
            <button
              v-if="facture.statut === 'validée' && !facture.est_avoir"
              @click.stop="creerAvoir(facture)"
              class="p-2 transition-colors rounded-lg group text-purple-600 hover:bg-purple-50"
              title="Créer un avoir"
              :disabled="isCreatingAvoir === facture.id"
            >
              <template v-if="isCreatingAvoir === facture.id">
                <span class="block w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              </template>
              <template v-else>
                <Undo2 class="w-5 h-5 group-hover:scale-110 transition-transform" />
              </template>
            </button>
            <button
              v-if="facture.statut === 'brouillon'"
              @click.stop="requestValidation(facture)"
              class="p-2 transition-colors rounded-lg group text-blue-600 hover:bg-blue-50"
              title="Valider cette facture"
              :disabled="isUpdatingStatus === facture.id"
            >
              <template v-if="isUpdatingStatus === facture.id">
                <span class="block w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              </template>
              <template v-else>
                <CheckCircle2 class="w-5 h-5 group-hover:scale-110 transition-transform" />
              </template>
            </button>
            <button
              @click.stop="togglePayment(facture)"
              class="p-2 transition-colors rounded-lg group"
              :class="[
                facture.est_payee 
                  ? 'text-emerald-600 hover:bg-emerald-50' 
                  : 'text-amber-600 hover:bg-amber-50'
              ]"
              :title="facture.est_payee ? 'Marquer comme non payée' : 'Marquer comme payée'"
              :disabled="isUpdatingPayment === facture.id"
            >
              <template v-if="isUpdatingPayment === facture.id">
                <span class="block w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              </template>
              <template v-else>
                <CreditCard class="w-5 h-5 group-hover:scale-110 transition-transform" />
              </template>
            </button>
            <button
              @click.stop="router.push(`/app/factures/${facture.id}/pdf`)"
              class="p-2 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-lg transition-colors"
              title="Télécharger PDF"
            >
              <Download class="w-5 h-5" />
            </button>
            <button
              v-if="facture.statut !== 'validée'"
              @click.stop="openDeleteModal(facture.id)"
              class="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
              title="Supprimer"
            >
              <Trash2 class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Empty State -->
    <div v-else-if="searchQuery" class="bg-card border border-border rounded-xl p-12 text-center">
      <div class="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
        <Search class="w-8 h-8 text-muted-foreground" />
      </div>
      <h3 class="text-lg font-semibold text-foreground mb-2">Aucun résultat</h3>
      <p class="text-muted-foreground mb-6">Aucune facture ne correspond à votre recherche.</p>
      <button
        @click="searchQuery = ''"
        class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
      >
        Effacer la recherche
      </button>
    </div>

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
