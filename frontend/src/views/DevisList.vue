<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, FileText, Calendar, Download, Trash2, Search, CheckCircle2, Clock, Receipt } from 'lucide-vue-next'

import { API_BASE_URL } from '@/lib/api'

interface Client {
  nom: string
}

interface Devis {
  id: number
  titre_document_pdf: string
  date_devis: string
  numero_devis: string
  client?: Client
  statut: string
  created_at: string
}

const router = useRouter()
const devisList = ref<Devis[]>([])
const loading = ref(true)
const showDeleteConfirm = ref(false)
const idToDelete = ref<number | null>(null)
const isDeleting = ref(false)
const isUpdatingStatus = ref<number | null>(null)

const searchQuery = ref('')
const statusFilter = ref('tous') // tous, brouillon, envoyé

const filteredDevis = computed(() => {
  let result = devisList.value

  // Filtrage par texte
  const query = searchQuery.value.toLowerCase().trim()
  if (query) {
    result = result.filter(d => 
      (d.titre_document_pdf?.toLowerCase() || '').includes(query) ||
      (d.numero_devis?.toLowerCase() || '').includes(query) ||
      (d.client?.nom?.toLowerCase() || '').includes(query)
    )
  }

  // Filtrage par statut
  if (statusFilter.value !== 'tous') {
    result = result.filter(d => d.statut === statusFilter.value)
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

async function fetchDevis() {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/devis/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (res.ok) {
      devisList.value = await res.json()
    } else {
      console.error('Erreur API devis', await res.text())
    }
  } catch (e) {
    console.error('Erreur lors du chargement des devis', e)
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

async function confirmDelete() {
  if (idToDelete.value === null) return
  
  isDeleting.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/devis/${idToDelete.value}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      devisList.value = devisList.value.filter(d => d.id !== idToDelete.value)
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

async function toggleStatus(devis: Devis) {
  if (isUpdatingStatus.value !== null) return
  
  const newStatut = devis.statut === 'brouillon' ? 'envoyé' : 'brouillon'
  isUpdatingStatus.value = devis.id
  
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/devis/${devis.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ statut: newStatut })
    })
    
    if (res.ok) {
      const updatedDevis = await res.json()
      const index = devisList.value.findIndex(d => d.id === devis.id)
      if (index !== -1) {
        devisList.value[index] = updatedDevis
      }
    } else {
      console.error('Erreur lors du changement de statut')
    }
  } catch (e) {
    console.error('Erreur réseau lors du changement de statut', e)
  } finally {
    isUpdatingStatus.value = null
  }
}

onMounted(fetchDevis)
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-foreground">Devis</h1>
        <p class="text-sm sm:text-base text-muted-foreground mt-1">Gérez vos devis et créez-en de nouveaux</p>
      </div>
      <button
        @click="router.push('/app/devis/new')"
        class="inline-flex items-center justify-center gap-2 bg-primary text-primary-foreground px-4 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors shrink-0 w-full sm:w-auto"
      >
        <Plus class="w-5 h-5" />
        Nouveau devis
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
    <div v-else-if="devisList.length === 0" class="bg-card border border-border rounded-xl p-12 text-center">
      <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
        <FileText class="w-8 h-8 text-primary" />
      </div>
      <h3 class="text-lg font-semibold text-foreground mb-2">Aucun devis</h3>
      <p class="text-muted-foreground mb-6">Vous n'avez pas encore créé de devis.</p>
      <button
        @click="router.push('/app/devis/new')"
        class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
      >
        <Plus class="w-4 h-4" />
        Créer mon premier devis
      </button>
    </div>

    <!-- Devis List -->
    <div v-else-if="devisList.length > 0" class="grid gap-4">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher un devis par titre, numéro ou client..."
            class="w-full pl-10 pr-4 py-2.5 bg-card border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
          />
        </div>
        
        <div class="flex items-center gap-3">
          <select 
            v-model="statusFilter"
            class="bg-card border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            <option value="tous">Tous les statuts</option>
            <option value="brouillon">Brouillon</option>
            <option value="envoyé">Envoyé</option>
          </select>

          <button 
            v-if="searchQuery || statusFilter !== 'tous'"
            @click="searchQuery = ''; statusFilter = 'tous'"
            class="text-xs font-medium text-primary hover:underline"
          >
            Réinitialiser
          </button>
        </div>
      </div>
      <div
        v-for="devis in filteredDevis"
        :key="devis.id"
        class="bg-card border border-border rounded-xl p-4 sm:p-6 hover:border-primary/50 transition-colors cursor-pointer"
        @click="router.push(`/app/devis/${devis.id}`)"
      >
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 sm:gap-3 mb-2">
              <h3 class="text-base sm:text-lg font-semibold text-foreground truncate">{{ devis.titre_document_pdf || "Devis" }} - {{ devis.numero_devis }}</h3>
              <span 
                :class="[
                  'px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap',
                  devis.statut === 'envoyé' 
                    ? 'bg-green-100 text-green-700 font-bold border border-green-200' 
                    : 'bg-blue-100 text-blue-700 font-bold border border-blue-200'
                ]"
              >
                {{ devis.statut }}
              </span>
            </div>
            <div class="flex flex-wrap items-center gap-2 sm:gap-4 text-sm text-muted-foreground">
              <span class="flex items-center gap-1">
                <Calendar class="w-4 h-4" />
                {{ formatDate(devis.date_devis) }}
              </span>
              <span>{{ devis.client?.nom || 'Client inconnu' }}</span>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2 sm:ml-4">
            <button
              @click.stop="toggleStatus(devis)"
              class="inline-flex items-center gap-2 px-3 py-1.5 transition-colors rounded-lg group border border-transparent"
              :class="[
                devis.statut === 'envoyé' 
                  ? 'text-green-600 hover:bg-green-50 hover:border-green-200' 
                  : 'text-blue-600 hover:bg-blue-50 hover:border-blue-200'
              ]"
              :title="devis.statut === 'envoyé' ? 'Marquer comme brouillon' : 'Marquer comme envoyé'"
              :disabled="isUpdatingStatus === devis.id"
            >
              <template v-if="isUpdatingStatus === devis.id">
                <span class="block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              </template>
              <template v-else>
                <CheckCircle2 v-if="devis.statut === 'brouillon'" class="w-4 h-4 group-hover:scale-110 transition-transform" />
                <Clock v-else class="w-4 h-4 group-hover:scale-110 transition-transform" />
              </template>
              <span class="text-xs font-semibold">{{ devis.statut === 'envoyé' ? 'Envoyé' : 'Envoyer' }}</span>
            </button>

            <button
              @click.stop="router.push(`/app/factures/new?fromDevis=${devis.id}`)"
              class="inline-flex items-center gap-2 px-3 py-1.5 text-muted-foreground hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors border border-transparent hover:border-emerald-200"
              title="Facturer ce devis"
            >
              <Receipt class="w-4 h-4" />
              <span class="text-xs font-semibold">Facturer</span>
            </button>

            <button
              @click.stop="router.push(`/app/devis/${devis.id}/pdf`)"
              class="inline-flex items-center gap-2 px-3 py-1.5 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-lg transition-colors border border-transparent hover:border-primary/20"
              title="Télécharger PDF"
            >
              <Download class="w-4 h-4" />
              <span class="text-xs font-semibold">PDF</span>
            </button>

            <button
              @click.stop="openDeleteModal(devis.id)"
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

    <!-- Search Empty State -->
    <div v-else-if="searchQuery" class="bg-card border border-border rounded-xl p-12 text-center">
      <div class="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
        <Search class="w-8 h-8 text-muted-foreground" />
      </div>
      <h3 class="text-lg font-semibold text-foreground mb-2">Aucun résultat</h3>
      <p class="text-muted-foreground mb-6">Aucun devis ne correspond à vos filtres actuels.</p>
      <button
        @click="searchQuery = ''; statusFilter = 'tous'"
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
        <p class="text-muted-foreground mb-6">Voulez-vous vraiment supprimer ce devis ? Cette action est irréversible.</p>
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
  </div>
</template>
