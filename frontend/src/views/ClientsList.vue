<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Pencil, Trash2, X, Building2 } from 'lucide-vue-next'
import { API_BASE_URL } from '@/lib/api'

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

const clients = ref<Client[]>([])
const loading = ref(false)
const error = ref('')
const showModal = ref(false)
const editingClient = ref<Client | null>(null)
const showDeleteConfirm = ref(false)
const clientToDelete = ref<Client | null>(null)
const isDeleting = ref(false)

const form = ref({
  nom: '',
  adresse: '',
  code_postal: '',
  ville: '',
  telephone: '',
  email: '',
  siret: ''
})

const API_URL = `${API_BASE_URL}/api/clients`

function getToken() {
  return localStorage.getItem('token')
}

async function fetchClients() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(API_URL, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    })
    if (!res.ok) throw new Error('Erreur lors du chargement')
    clients.value = await res.json()
  } catch (e) {
    error.value = 'Impossible de charger les clients'
  } finally {
    loading.value = false
  }
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
  const url = editingClient.value ? `${API_URL}/${editingClient.value.id}` : API_URL
  const method = editingClient.value ? 'PUT' : 'POST'
  
  try {
    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify(form.value)
    })
    
    if (!res.ok) throw new Error('Erreur lors de la sauvegarde')
    
    await fetchClients()
    closeModal()
  } catch (e) {
    error.value = 'Erreur lors de la sauvegarde'
  }
}

async function confirmDelete() {
  if (!clientToDelete.value) return
  
  isDeleting.value = true
  try {
    const res = await fetch(`${API_URL}/${clientToDelete.value.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${getToken()}` }
    })
    
    if (!res.ok) throw new Error('Erreur lors de la suppression')
    await fetchClients()
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
    <div class="page-header">
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
      <div v-for="client in clients" :key="client.id" class="client-card">
        <div class="card-header">
          <h3 class="client-name">{{ client.nom }}</h3>
          <div class="card-actions">
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
    <div v-if="showDeleteConfirm" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal delete-modal" @click.stop>
        <div class="modal-body p-6 text-center">
          <div class="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Trash2 class="w-8 h-8" />
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">Supprimer le client</h3>
          <p class="text-gray-500 mb-6">
            Êtes-vous sûr de vouloir supprimer <strong>{{ clientToDelete?.nom }}</strong> ? 
            Cette action est irréversible.
          </p>
          <div class="flex justify-center gap-3">
            <button 
              @click="closeDeleteModal" 
              class="btn-secondary" 
              :disabled="isDeleting"
            >
              Annuler
            </button>
            <button 
              @click="confirmDelete" 
              class="btn-danger-confirm" 
              :disabled="isDeleting"
            >
              <span v-if="isDeleting" class="spinner mr-2"></span>
              {{ isDeleting ? 'Suppression...' : 'Supprimer' }}
            </button>
          </div>
        </div>
      </div>
    </div>
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

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--primary);
  color: var(--primary-foreground);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: var(--primary);
  opacity: 0.9;
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
  ring: 2px solid var(--primary);
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

.delete-modal {
  max-width: 400px;
}

.btn-danger-confirm {
  padding: 10px 24px;
  background: var(--destructive);
  color: var(--primary-foreground);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.2s;
}

.btn-danger-confirm:hover {
  opacity: 0.9;
}

.btn-danger-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-t-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
