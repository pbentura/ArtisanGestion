<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Pencil, Trash2, X, Building2, MoreVertical } from 'lucide-vue-next'
import MobileFAB from '@/components/mobile/MobileFAB.vue'
import MobileBottomSheet from '@/components/mobile/MobileBottomSheet.vue'
import { apiFetch } from '@/lib/api'
import { useMobile } from '@/composables/useMobile'
import { dataStore } from '@/lib/store'
import { computed } from 'vue'

interface Client {
  id: number
  nom: string
  adresse: string | null
  code_postal: string | null
  ville: string | null
  telephone: string | null
  email: string | null
  siret: string | null
}

const clients = computed(() => dataStore.clients.data)
const loading = computed(() => dataStore.clients.loading)
const error = ref('')
const showModal = ref(false)
const editingClient = ref<Client | null>(null)
const showDeleteConfirm = ref(false)
const clientToDelete = ref<Client | null>(null)
const isDeleting = ref(false)
const isBottomSheetOpen = ref(false)
const selectedClient = ref<Client | null>(null)
const {  isMobileView } = useMobile()

function openBottomSheet(client: Client) {
  selectedClient.value = client
  isBottomSheetOpen.value = true
}

function closeBottomSheet() {
  isBottomSheetOpen.value = false
  setTimeout(() => {
    selectedClient.value = null
  }, 300)
}

const form = ref({
  nom: '',
  adresse: '',
  code_postal: '',
  ville: '',
  telephone: '',
  email: '',
  siret: ''
})


function fetchClients() {
  dataStore.fetchClients()
}

function openCreateModal() {
  editingClient.value = null
  form.value = { nom: '', adresse: '', code_postal: '', ville: '', telephone: '', email: '', siret: '' }
  showModal.value = true
}

function openEditModal(client: Client) {
  editingClient.value = client
  form.value = {
    nom: client.nom,
    adresse: client.adresse || '',
    code_postal: client.code_postal || '',
    ville: client.ville || '',
    telephone: client.telephone || '',
    email: client.email || '',
    siret: client.siret || ''
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingClient.value = null
}

function openDeleteModal(client: Client) {
  clientToDelete.value = client
  showDeleteConfirm.value = true
}

function closeDeleteModal() {
  clientToDelete.value = null
  showDeleteConfirm.value = false
}

async function saveClient() {
  const endpoint = editingClient.value ? `clients/${editingClient.value.id}` : 'clients'
  const method = editingClient.value ? 'PUT' : 'POST'
  
  try {
    const res = await apiFetch(endpoint, {
      method,
      body: JSON.stringify(form.value)
    })
    
    if (!res.ok) throw new Error('Erreur lors de la sauvegarde')
    
    dataStore.fetchClients(true)
    closeModal()
  } catch (e) {
    error.value = 'Erreur lors de la sauvegarde'
  }
}

async function confirmDelete() {
  if (!clientToDelete.value) return
  
  isDeleting.value = true
  try {
    const res = await apiFetch(`clients/${clientToDelete.value.id}`, {
      method: 'DELETE'
    })
    
    if (!res.ok) throw new Error('Erreur lors de la suppression')
    dataStore.fetchClients(true)
    closeDeleteModal()
  } catch (e) {
    error.value = 'Erreur lors de la suppression'
  } finally {
    isDeleting.value = false
  }
}

onMounted(fetchClients)
</script>

<template>
  <div class="clients-page">
    <div class="page-header hidden lg:flex animate-fade-slide-up">
      <h1 class="page-title">Mes clients</h1>
      <button @click="openCreateModal" class="btn-primary">
        <Plus class="w-4 h-4" /> Nouveau client
      </button>
    </div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <div v-if="loading" class="loading">Chargement...</div>

    <div v-else-if="clients.length === 0" class="empty-state">
      <Building2 class="w-16 h-16 text-gray-300" />
      <p>Aucun client pour le moment</p>
      <button @click="openCreateModal" class="btn-link">Ajouter un client</button>
    </div>

    <div v-else class="clients-grid">
      <div 
        v-for="(client, idx) in clients" 
        :key="client.id" 
        class="client-card animate-fade-slide-up"
        :style="{ animationDelay: (idx * 0.05) + 's' }"
      >
        <div class="card-header">
          <h3 class="client-name">{{ client.nom }}</h3>
          
          <!-- Mobile Actions Trigger -->
          <div class="sm:hidden">
            <button @click="openBottomSheet(client)" class="btn-icon">
              <MoreVertical class="w-5 h-5" />
            </button>
          </div>
          
          <!-- Desktop Actions -->
          <div class="card-actions hidden sm:flex">
            <button @click="openEditModal(client)" class="btn-icon" title="Modifier">
              <Pencil class="w-4 h-4" />
            </button>
            <button @click="openDeleteModal(client)" class="btn-icon btn-danger" title="Supprimer">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <div class="card-body">
          <p v-if="client.adresse" class="info-row">
            <span class="label">Adresse:</span> {{ client.adresse }}
          </p>
          <p v-if="client.code_postal || client.ville" class="info-row">
            <span class="label">Ville:</span> {{ client.code_postal }} {{ client.ville }}
          </p>
          <p v-if="client.telephone" class="info-row">
            <span class="label">Tél:</span> {{ client.telephone }}
          </p>
          <p v-if="client.email" class="info-row">
            <span class="label">Email:</span> {{ client.email }}
          </p>
          <p v-if="client.siret" class="info-row">
            <span class="label">SIRET:</span> {{ client.siret }}
          </p>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>{{ editingClient ? 'Modifier' : 'Nouveau' }} client</h2>
          <button @click="closeModal" class="btn-icon">
            <X class="w-5 h-5" />
          </button>
        </div>
        
        <form @submit.prevent="saveClient" class="modal-body">
          <div class="form-group">
            <label>Nom *</label>
            <input v-model="form.nom" required class="input" placeholder="Nom du client" />
          </div>
          
          <div class="form-group">
            <label>Adresse</label>
            <textarea v-model="form.adresse" class="input" rows="2" placeholder="Adresse" />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Code postal</label>
              <input v-model="form.code_postal" class="input" placeholder="Code postal" />
            </div>
            <div class="form-group">
              <label>Ville</label>
              <input v-model="form.ville" class="input" placeholder="Ville" />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Téléphone</label>
              <input v-model="form.telephone" class="input" placeholder="Téléphone" />
            </div>
            <div class="form-group">
              <label>Email</label>
              <input v-model="form.email" type="email" class="input" placeholder="Email" />
            </div>
          </div>
          
          <div class="form-group">
            <label>SIRET</label>
            <input v-model="form.siret" class="input" placeholder="Numéro SIRET" />
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn-secondary">Annuler</button>
            <button type="submit" class="btn-primary">{{ editingClient ? 'Modifier' : 'Créer' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-background/80 backdrop-blur-sm" @click="closeDeleteModal"></div>
      <div class="relative bg-card border border-border rounded-xl shadow-lg max-w-sm w-full p-6 animate-in fade-in zoom-in duration-200">
        <h3 class="text-lg font-semibold text-foreground mb-2">Confirmer la suppression</h3>
        <p class="text-muted-foreground mb-6">
          Voulez-vous vraiment supprimer le client <strong>{{ clientToDelete?.nom }}</strong> ? 
          Cette action est irréversible.
        </p>
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

    <!-- Mobile FAB -->
    <MobileFAB v-if="isMobileView" class="lg:hidden" @click="openCreateModal" />

    <!-- Mobile Bottom Sheet for Actions -->
    <MobileBottomSheet 
      :is-open="isBottomSheetOpen" 
      :title="selectedClient ? selectedClient.nom : ''"
      @close="closeBottomSheet"
    >
      <div v-if="selectedClient" class="flex flex-col gap-2 mt-4">
        <button
          @click="openEditModal(selectedClient); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-foreground bg-muted transition-colors text-left"
        >
          <Pencil class="w-5 h-5" />
          <span class="font-medium">Modifier le client</span>
        </button>

        <button
          @click="openDeleteModal(selectedClient); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-destructive bg-destructive/10 transition-colors text-left mt-4"
        >
          <Trash2 class="w-5 h-5" />
          <span class="font-medium">Supprimer le client</span>
        </button>
      </div>
    </MobileBottomSheet>
  </div>
</template>

<style scoped>
.clients-page {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--foreground);
}



.btn-secondary {
  padding: 10px 16px;
  background: var(--muted);
  color: var(--muted-foreground);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary:hover {
  background: var(--accent);
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--accent);
  border: none;
  border-radius: 6px;
  color: var(--muted-foreground);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--muted);
  color: var(--foreground);
}

.btn-danger:hover {
  background: var(--destructive);
  color: var(--primary-foreground);
}

.alert-error {
  padding: 12px 16px;
  background: var(--destructive);
  color: var(--primary-foreground);
  border-radius: 8px;
  margin-bottom: 16px;
  opacity: 0.9;
}

.loading {
  text-align: center;
  color: var(--muted-foreground);
  padding: 40px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--muted-foreground);
}

.empty-state p {
  margin: 16px 0;
}

.btn-link {
  color: var(--primary);
  background: none;
  border: none;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}

.clients-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.client-card {
  background: var(--card);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.client-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--foreground);
  margin: 0;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  margin: 0;
  font-size: 0.9rem;
  color: var(--muted-foreground);
}

.label {
  color: var(--muted-foreground);
  font-size: 0.85rem;
  opacity: 0.7;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  background: var(--card);
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--foreground);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  max-height: calc(90vh - 140px);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--foreground);
}

.input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
  box-sizing: border-box;
  background: var(--background);
  color: var(--foreground);
}

.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px var(--primary);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>

