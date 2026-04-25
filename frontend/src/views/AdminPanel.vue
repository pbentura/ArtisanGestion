<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { Database, Table2, Plus, Pencil, Trash2, X, Save, AlertTriangle, Search, RefreshCw } from 'lucide-vue-next'
import { API_BASE_URL } from '@/lib/api'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface ColumnSchema {
  name: string
  type: string
  nullable: boolean
  primary_key: boolean
  default: string | null
}

// Table display names
const TABLE_LABELS: Record<string, string> = {
  users: 'Utilisateurs',
  societe: 'Sociétés',
  clients: 'Clients',
  rapports: 'Rapports',
  devis: 'Devis',
  lignes_devis: 'Lignes de devis',
  factures: 'Factures',
  lignes_facture: 'Lignes de facture',
}

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const tables = ref<string[]>([])
const selectedTable = ref('')
const columns = ref<ColumnSchema[]>([])
const rows = ref<Record<string, any>[]>([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')

// Modal state
const showModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const formData = ref<Record<string, any>>({})
const saving = ref(false)

// Delete modal state
const showDeleteModal = ref(false)
const deleteTarget = ref<Record<string, any> | null>(null)
const deleting = ref(false)

// ---------------------------------------------------------------------------
// Auth helper
// ---------------------------------------------------------------------------
function getToken() {
  return localStorage.getItem('token')
}

function authHeaders(): Record<string, string> {
  return {
    'Authorization': `Bearer ${getToken()}`,
    'Content-Type': 'application/json',
  }
}

// ---------------------------------------------------------------------------
// Computed
// ---------------------------------------------------------------------------
const filteredRows = computed(() => {
  if (!searchQuery.value.trim()) return rows.value
  const q = searchQuery.value.toLowerCase()
  return rows.value.filter(row =>
    Object.values(row).some(v =>
      v !== null && String(v).toLowerCase().includes(q)
    )
  )
})

const editableColumns = computed(() =>
  columns.value.filter(c => !c.primary_key && c.name !== 'created_at')
)

// ---------------------------------------------------------------------------
// Data fetching
// ---------------------------------------------------------------------------
async function fetchTables() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/admin/tables`, {
      headers: authHeaders(),
    })
    if (!res.ok) throw new Error('Erreur')
    tables.value = await res.json()
    if (tables.value.length > 0 && !selectedTable.value) {
      selectedTable.value = tables.value[0]
    }
  } catch (e) {
    error.value = 'Impossible de charger les tables'
  }
}

async function fetchSchema() {
  if (!selectedTable.value) return
  try {
    const res = await fetch(`${API_BASE_URL}/api/admin/tables/${selectedTable.value}/schema`, {
      headers: authHeaders(),
    })
    if (!res.ok) throw new Error('Erreur')
    columns.value = await res.json()
  } catch (e) {
    error.value = 'Erreur de chargement du schéma'
  }
}

async function fetchRows() {
  if (!selectedTable.value) return
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${API_BASE_URL}/api/admin/tables/${selectedTable.value}`, {
      headers: authHeaders(),
    })
    if (!res.ok) throw new Error('Erreur')
    rows.value = await res.json()
  } catch (e) {
    error.value = 'Erreur de chargement des données'
  } finally {
    loading.value = false
  }
}

async function loadTable(tableName: string) {
  selectedTable.value = tableName
  searchQuery.value = ''
}

watch(selectedTable, async () => {
  await fetchSchema()
  await fetchRows()
})

// ---------------------------------------------------------------------------
// CRUD
// ---------------------------------------------------------------------------
function openCreate() {
  modalMode.value = 'create'
  const data: Record<string, any> = {}
  for (const col of editableColumns.value) {
    if (col.type.toUpperCase().includes('BOOL')) {
      data[col.name] = col.default === 'true' || col.default === '1'
    } else {
      data[col.name] = col.default ?? ''
    }
  }
  formData.value = data
  showModal.value = true
}

function openEdit(row: Record<string, any>) {
  modalMode.value = 'edit'
  formData.value = { ...row }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  formData.value = {}
}

async function saveRow() {
  saving.value = true
  error.value = ''
  try {
    const payload: Record<string, any> = {}
    for (const col of editableColumns.value) {
      const val = formData.value[col.name]
      payload[col.name] = val === '' ? null : val
    }

    let url: string
    let method: string
    if (modalMode.value === 'create') {
      url = `${API_BASE_URL}/api/admin/tables/${selectedTable.value}`
      method = 'POST'
    } else {
      url = `${API_BASE_URL}/api/admin/tables/${selectedTable.value}/${formData.value.id}`
      method = 'PUT'
    }

    const res = await fetch(url, {
      method,
      headers: authHeaders(),
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Erreur lors de la sauvegarde')
    }

    await fetchRows()
    closeModal()
  } catch (e: any) {
    error.value = e.message || 'Erreur lors de la sauvegarde'
  } finally {
    saving.value = false
  }
}

function openDelete(row: Record<string, any>) {
  deleteTarget.value = row
  showDeleteModal.value = true
}

function closeDeleteModal() {
  deleteTarget.value = null
  showDeleteModal.value = false
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  error.value = ''
  try {
    const res = await fetch(
      `${API_BASE_URL}/api/admin/tables/${selectedTable.value}/${deleteTarget.value.id}`,
      { method: 'DELETE', headers: authHeaders() }
    )
    if (!res.ok) throw new Error('Erreur lors de la suppression')
    await fetchRows()
    closeDeleteModal()
  } catch (e: any) {
    error.value = e.message || 'Erreur de suppression'
  } finally {
    deleting.value = false
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function getInputType(colType: string): string {
  const t = colType.toUpperCase()
  if (t.includes('INT')) return 'number'
  if (t.includes('NUMERIC') || t.includes('DECIMAL') || t.includes('FLOAT') || t.includes('REAL')) return 'number'
  if (t.includes('DATE') && !t.includes('DATETIME') && !t.includes('TIMESTAMP')) return 'date'
  if (t.includes('DATETIME') || t.includes('TIMESTAMP')) return 'datetime-local'
  if (t.includes('BOOL')) return 'checkbox'
  return 'text'
}

function truncate(value: any, maxLen = 50): string {
  if (value === null || value === undefined) return '—'
  const s = String(value)
  return s.length > maxLen ? s.slice(0, maxLen) + '…' : s
}

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------
onMounted(async () => {
  await fetchTables()
})
</script>

<template>
  <div class="admin-page">
    <!-- Page Header -->
    <div class="admin-header">
      <div class="admin-title-group">
        <div class="admin-icon-wrap">
          <Database class="w-6 h-6" />
        </div>
        <div>
          <h1 class="admin-title">Administration</h1>
          <p class="admin-subtitle">Gestion complète de la base de données</p>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="alert-error">
      <AlertTriangle class="w-4 h-4" />
      <span>{{ error }}</span>
      <button @click="error = ''" class="alert-close"><X class="w-4 h-4" /></button>
    </div>

    <div class="admin-content">
      <!-- Table Tabs -->
      <div class="table-tabs">
        <button
          v-for="table in tables"
          :key="table"
          class="table-tab"
          :class="{ active: selectedTable === table }"
          @click="loadTable(table)"
        >
          <Table2 class="w-4 h-4" />
          <span>{{ TABLE_LABELS[table] || table }}</span>
          <span v-if="selectedTable === table" class="tab-count">{{ rows.length }}</span>
        </button>
      </div>

      <!-- Toolbar -->
      <div class="toolbar" v-if="selectedTable">
        <div class="toolbar-left">
          <div class="search-box">
            <Search class="w-4 h-4 search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher…"
              class="search-input"
            />
          </div>
        </div>
        <div class="toolbar-right">
          <button @click="fetchRows" class="btn-ghost" title="Rafraîchir">
            <RefreshCw class="w-4 h-4" />
          </button>
          <button @click="openCreate" class="btn-primary">
            <Plus class="w-4 h-4" />
            <span>Nouvelle ligne</span>
          </button>
        </div>
      </div>

      <!-- Data Table -->
      <div class="table-wrapper" v-if="selectedTable">
        <div v-if="loading" class="table-loading">
          <div class="spinner-lg"></div>
          <span>Chargement des données…</span>
        </div>

        <div v-else-if="filteredRows.length === 0" class="table-empty">
          <Table2 class="w-12 h-12" />
          <p v-if="searchQuery">Aucun résultat pour « {{ searchQuery }} »</p>
          <p v-else>Aucune donnée dans cette table</p>
          <button @click="openCreate" class="btn-link" v-if="!searchQuery">Créer une entrée</button>
        </div>

        <table v-else class="data-table">
          <thead>
            <tr>
              <th v-for="col in columns" :key="col.name" :class="{ 'col-pk': col.primary_key }">
                {{ col.name }}
                <span class="col-type">{{ col.type }}</span>
              </th>
              <th class="col-actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filteredRows" :key="row.id">
              <td v-for="col in columns" :key="col.name" :class="{ 'col-pk': col.primary_key }">
                <span class="cell-value" :title="String(row[col.name] ?? '')">
                  {{ truncate(row[col.name]) }}
                </span>
              </td>
              <td class="col-actions">
                <button @click="openEdit(row)" class="btn-icon-sm" title="Modifier">
                  <Pencil class="w-3.5 h-3.5" />
                </button>
                <button @click="openDelete(row)" class="btn-icon-sm btn-icon-danger" title="Supprimer">
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="table-footer" v-if="selectedTable && filteredRows.length > 0">
        <span class="row-count">{{ filteredRows.length }} ligne{{ filteredRows.length > 1 ? 's' : '' }}</span>
      </div>
    </div>

    <!-- Create / Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <div class="modal-title-group">
            <div class="modal-icon" :class="modalMode === 'create' ? 'icon-create' : 'icon-edit'">
              <Plus v-if="modalMode === 'create'" class="w-5 h-5" />
              <Pencil v-else class="w-5 h-5" />
            </div>
            <div>
              <h2>{{ modalMode === 'create' ? 'Nouvelle ligne' : 'Modifier la ligne' }}</h2>
              <p class="modal-subtitle">Table : {{ TABLE_LABELS[selectedTable] || selectedTable }}</p>
            </div>
          </div>
          <button @click="closeModal" class="btn-icon-sm"><X class="w-5 h-5" /></button>
        </div>

        <form @submit.prevent="saveRow" class="modal-body">
          <div v-if="modalMode === 'edit'" class="form-group id-display">
            <label>ID</label>
            <div class="id-badge">{{ formData.id }}</div>
          </div>

          <div v-for="col in editableColumns" :key="col.name" class="form-group">
            <label :for="'field-' + col.name">
              {{ col.name }}
              <span v-if="!col.nullable" class="required-marker">*</span>
              <span class="col-type-badge">{{ col.type }}</span>
            </label>

            <textarea
              v-if="col.type.toUpperCase() === 'TEXT' || col.type.toUpperCase().includes('JSON')"
              :id="'field-' + col.name"
              v-model="formData[col.name]"
              class="input"
              rows="3"
              :required="!col.nullable"
              :placeholder="col.name"
            />
            <input
              v-else
              :id="'field-' + col.name"
              v-model="formData[col.name]"
              :type="getInputType(col.type)"
              class="input"
              :required="!col.nullable"
              :placeholder="col.name"
              :step="getInputType(col.type) === 'number' ? 'any' : undefined"
            />
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn-secondary" :disabled="saving">
              Annuler
            </button>
            <button type="submit" class="btn-primary" :disabled="saving">
              <span v-if="saving" class="spinner-sm"></span>
              <Save v-else class="w-4 h-4" />
              <span>{{ saving ? 'Enregistrement…' : (modalMode === 'create' ? 'Créer' : 'Enregistrer') }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal delete-modal" @click.stop>
        <div class="modal-body delete-body">
          <div class="delete-icon-wrap">
            <AlertTriangle class="w-8 h-8" />
          </div>
          <h3>Supprimer cette ligne ?</h3>
          <p>
            Vous allez supprimer la ligne <strong>#{{ deleteTarget?.id }}</strong> de la table
            <strong>{{ TABLE_LABELS[selectedTable] || selectedTable }}</strong>.
            Cette action est irréversible.
          </p>
          <div class="delete-actions">
            <button @click="closeDeleteModal" class="btn-secondary" :disabled="deleting">
              Annuler
            </button>
            <button @click="confirmDelete" class="btn-danger" :disabled="deleting">
              <span v-if="deleting" class="spinner-sm"></span>
              <Trash2 v-else class="w-4 h-4" />
              <span>{{ deleting ? 'Suppression…' : 'Supprimer' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* =========================================================================
   Admin Page
   ========================================================================= */
.admin-page {
  max-width: 1400px;
}

/* Header */
.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.admin-title-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-icon-wrap {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
}

.admin-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--foreground);
  margin: 0;
}

.admin-subtitle {
  font-size: 0.85rem;
  color: var(--muted-foreground);
  margin: 2px 0 0 0;
}

/* Error alert */
.alert-error {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(239, 68, 68, 0.06));
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: #ef4444;
  border-radius: 12px;
  margin-bottom: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.alert-close {
  margin-left: auto;
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  opacity: 0.6;
}

.alert-close:hover {
  opacity: 1;
}

/* Content */
.admin-content {
  background: var(--card);
  border-radius: 16px;
  border: 1px solid var(--border);
  overflow: hidden;
}

/* Table Tabs */
.table-tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--border);
  overflow-x: auto;
  padding: 0 8px;
}

.table-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  border: none;
  background: none;
  color: var(--muted-foreground);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  white-space: nowrap;
}

.table-tab:hover {
  color: var(--foreground);
  background: var(--accent);
}

.table-tab.active {
  color: #6366f1;
  border-bottom-color: #6366f1;
}

.tab-count {
  background: rgba(99, 102, 241, 0.12);
  color: #6366f1;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 700;
}

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  gap: 16px;
  flex-wrap: wrap;
}

.toolbar-left {
  flex: 1;
  min-width: 200px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-box {
  position: relative;
  max-width: 320px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted-foreground);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 9px 12px 9px 36px;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 0.875rem;
  background: var(--background);
  color: var(--foreground);
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.btn-ghost {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  background: var(--background);
  color: var(--muted-foreground);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-ghost:hover {
  background: var(--accent);
  color: var(--foreground);
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 18px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Data Table */
.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table thead {
  background: var(--muted);
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted-foreground);
  white-space: nowrap;
  border-bottom: 1px solid var(--border);
}

.col-type {
  display: inline-block;
  margin-left: 6px;
  font-weight: 500;
  font-size: 0.65rem;
  text-transform: none;
  letter-spacing: 0;
  opacity: 0.5;
}

.data-table td {
  padding: 12px 16px;
  color: var(--foreground);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.data-table tbody tr {
  transition: background 0.15s;
}

.data-table tbody tr:hover {
  background: var(--accent);
}

.col-pk {
  color: var(--muted-foreground);
  font-weight: 700;
}

.col-pk td {
  font-variant-numeric: tabular-nums;
}

.cell-value {
  display: block;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-actions {
  width: 100px;
  text-align: right;
}

.col-actions .btn-icon-sm + .btn-icon-sm {
  margin-left: 6px;
}

.btn-icon-sm {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  background: var(--accent);
  color: var(--muted-foreground);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon-sm:hover {
  background: var(--muted);
  color: var(--foreground);
}

.btn-icon-danger:hover {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

/* Table loading / empty */
.table-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 20px;
  color: var(--muted-foreground);
}

.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 20px;
  color: var(--muted-foreground);
}

.table-empty p {
  margin: 0;
  font-size: 0.95rem;
}

.btn-link {
  background: none;
  border: none;
  color: #6366f1;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
  font-size: 0.9rem;
}

/* Table Footer */
.table-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--border);
  text-align: right;
}

.row-count {
  font-size: 0.8rem;
  color: var(--muted-foreground);
  font-weight: 600;
}

/* =========================================================================
   Modals
   ========================================================================= */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  background: var(--card);
  border-radius: 20px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: modalIn 0.25s ease-out;
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--border);
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 14px;
}

.modal-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.icon-create {
  background: linear-gradient(135deg, #22c55e, #16a34a);
}

.icon-edit {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--foreground);
}

.modal-subtitle {
  margin: 2px 0 0 0;
  font-size: 0.8rem;
  color: var(--muted-foreground);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  max-height: calc(90vh - 160px);
}

/* Form */
.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--foreground);
}

.required-marker {
  color: #ef4444;
  font-weight: 700;
}

.col-type-badge {
  font-size: 0.65rem;
  background: var(--muted);
  color: var(--muted-foreground);
  padding: 1px 6px;
  border-radius: 6px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.id-display {
  margin-bottom: 20px;
}

.id-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 16px;
  background: var(--muted);
  color: var(--muted-foreground);
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.9rem;
  font-variant-numeric: tabular-nums;
}

.input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 0.9rem;
  background: var(--background);
  color: var(--foreground);
  transition: all 0.2s;
  box-sizing: border-box;
}

.input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
}

.btn-secondary {
  padding: 10px 18px;
  background: var(--muted);
  color: var(--muted-foreground);
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: var(--accent);
  color: var(--foreground);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Delete Modal */
.delete-modal {
  max-width: 420px;
}

.delete-body {
  text-align: center;
  padding: 32px 24px !important;
}

.delete-icon-wrap {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(239, 68, 68, 0.06));
  color: #ef4444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.delete-body h3 {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  color: var(--foreground);
}

.delete-body p {
  margin: 0 0 24px 0;
  color: var(--muted-foreground);
  font-size: 0.9rem;
  line-height: 1.5;
}

.delete-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.btn-danger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.25);
}

.btn-danger:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35);
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Spinners */
.spinner-lg {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 640px) {
  .table-tabs {
    padding: 0 4px;
  }

  .table-tab {
    padding: 12px 14px;
    font-size: 0.8rem;
  }

  .table-tab span:first-of-type {
    display: none;
  }

  .toolbar {
    padding: 12px 16px;
  }

  .data-table th,
  .data-table td {
    padding: 10px 12px;
  }

  .btn-primary span {
    display: none;
  }
}
</style>
