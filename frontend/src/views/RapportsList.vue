<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, FileText, Calendar, Download, Trash2 } from 'lucide-vue-next'

import { API_BASE_URL } from '@/lib/api'

interface Client {
  nom: string
}

interface Rapport {
  id: number
  titre_document_pdf: string
  date_intervention: string
  client?: Client
  created_at: string
}

const router = useRouter()
const rapports = ref<Rapport[]>([])
const loading = ref(true)
const showDeleteConfirm = ref(false)
const idToDelete = ref<number | null>(null)
const isDeleting = ref(false)

function openDeleteModal(id: number) {
  idToDelete.value = id
  showDeleteConfirm.value = true
}

function closeDeleteModal() {
  idToDelete.value = null
  showDeleteConfirm.value = false
}

async function fetchRapports() {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/rapports/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (res.ok) {
      rapports.value = await res.json()
    } else {
      console.error('Erreur API rapports', await res.text())
    }
  } catch (e) {
    console.error('Erreur lors du chargement des rapports', e)
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
    const res = await fetch(`${API_BASE_URL}/api/rapports/${idToDelete.value}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      rapports.value = rapports.value.filter(r => r.id !== idToDelete.value)
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



async function generateFullPDF(rapport: Rapport) {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/rapports/${rapport.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) return
    const r = await res.json()
    
    // Fetch societe information
    const societeRes = await fetch(`${API_BASE_URL}/api/societes/me`, {
       headers: { 'Authorization': `Bearer ${token}` }
    })
    let societe = { nom: '', adresse: '', code_postal: '', ville: '', telephone: '', email: '', siret: '' }
    if (societeRes.ok) {
       societe = await societeRes.json()
    }
  
  const printWindow = window.open('', '_blank')
  if (!printWindow) return

  const formatDate = (dateString: string) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit', month: '2-digit', year: 'numeric'
    })
  }

  const adresseSociete = [societe.adresse, societe.code_postal, societe.ville]
    .filter(Boolean)
    .join(' ')
    
  const photoHtml = r.photo_url
    ? `<div class="section"><h2>Photo</h2><img src="${r.photo_url}" class="photo" /></div>`
    : ''

  const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <title>${r.titre_document_pdf}</title>
  <style>
    @page { margin: 15mm; size: A4; }
    body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; max-width: 210mm; margin: 0 auto; padding: 15px; background: white; font-size: 12px; }
    .header { text-align: center; margin-bottom: 20px; border-bottom: 3px solid #2563eb; padding-bottom: 15px; }
    .header h1 { color: #1f2937; margin: 0; font-size: 22px; font-weight: 700; }
    .section { margin-bottom: 20px; page-break-inside: avoid; }
    .section h2 { color: #2563eb; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; margin-bottom: 10px; font-size: 13px; font-weight: 600; text-transform: uppercase; }
    .info-group { margin-bottom: 10px; }
    .info-label { font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600; }
    .info-value { font-size: 12px; color: #1f2937; }
    .photo { max-width: 100%; max-height: 400px; object-fit: contain; border-radius: 4px; border: 1px solid #e5e7eb; }
    .text-content { font-size: 12px; line-height: 1.8; }
    .text-content p { margin: 0 0 10px 0; }
    .text-content li { margin: 5px 0; }
    .societe-info { margin-bottom: 15px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>${r.titre_document_pdf}</h1>
  </div>

  <div class="section societe-info">
    <div class="grid-2">
      <div>
        <div class="info-group">
          <div class="info-label">Entreprise</div>
          <div class="info-value">${societe.nom || '-'}${societe.siret ? ` (SIRET: ${societe.siret})` : ''}</div>
        </div>
        <div class="info-group">
          <div class="info-label">Coordonnées</div>
          <div class="info-value">
            ${adresseSociete || '-'}<br/>
            ${societe.telephone ? `Tél: ${societe.telephone}<br/>` : ''}
            ${societe.email ? `Email: ${societe.email}` : ''}
          </div>
        </div>
      </div>
      <div>
        <div class="info-group">
          <div class="info-label">Client</div>
          <div class="info-value"><strong>${r.client?.nom || '-'}</strong></div>
        </div>
        <div class="info-group">
          <div class="info-label">Adresse d'intervention</div>
          <div class="info-value">
            ${r.client?.adresse || '-'}<br/>
            ${[r.client?.code_postal, r.client?.ville].filter(Boolean).join(' ')}${[r.client?.code_postal, r.client?.ville].filter(Boolean).length > 0 ? '<br/>' : ''}
            ${r.client?.telephone ? `Tél: ${r.client.telephone}` : ''}
          </div>
        </div>
        ${r.client?.siret ? `
        <div class="info-group">
          <div class="info-label">SIRET / SIREN</div>
          <div class="info-value">${r.client.siret}</div>
        </div>
        ` : ''}
      </div>
    </div>
  </div>

  <div class="section">
    <div class="info-group">
      <div class="info-label">Date d'intervention</div>
      <div class="info-value">${formatDate(r.date_intervention)}</div>
    </div>
  </div>

  <div class="section">
    <h2>Rapport d'intervention</h2>
    <div class="text-content">${r.contenu || '<p>Aucun contenu</p>'}</div>
  </div>

  ${photoHtml}
</body>
</html>`

  printWindow.document.write(htmlContent)
  printWindow.document.close()

  setTimeout(() => {
    printWindow.print()
  }, 500)
  } catch (e) {
    console.error('Erreur lors de la génération du PDF', e)
  }
}

onMounted(fetchRapports)
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold text-foreground">Rapports d'intervention</h1>
        <p class="text-muted-foreground mt-1">Gérez vos rapports d'intervention et créez-en de nouveaux</p>
      </div>
      <button
        @click="router.push('/dashboard/rapports/new')"
        class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors"
      >
        <Plus class="w-5 h-5" />
        Nouveau rapport
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
    <div v-else-if="rapports.length === 0" class="bg-card border border-border rounded-xl p-12 text-center">
      <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
        <FileText class="w-8 h-8 text-primary" />
      </div>
      <h3 class="text-lg font-semibold text-foreground mb-2">Aucun rapport</h3>
      <p class="text-muted-foreground mb-6">Vous n'avez pas encore créé de rapport d'intervention.</p>
      <button
        @click="router.push('/dashboard/rapports/new')"
        class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
      >
        <Plus class="w-4 h-4" />
        Créer mon premier rapport
      </button>
    </div>

    <!-- Rapports List -->
    <div v-else class="grid gap-4">
      <div
        v-for="rapport in rapports"
        :key="rapport.id"
        class="bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-colors"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-foreground truncate">{{ rapport.titre_document_pdf || "Rapport d'intervention" }}</h3>
              <span class="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-medium">
                Terminée
              </span>
            </div>
            <div class="flex items-center gap-4 text-sm text-muted-foreground">
              <span class="flex items-center gap-1">
                <Calendar class="w-4 h-4" />
                {{ formatDate(rapport.date_intervention) }}
              </span>
              <span>{{ rapport.client?.nom || 'Client inconnu' }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2 ml-4">
            <button
              @click="generateFullPDF(rapport)"
              class="p-2 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-lg transition-colors"
              title="Télécharger PDF"
            >
              <Download class="w-5 h-5" />
            </button>
            <button
              @click="openDeleteModal(rapport.id)"
              class="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
              title="Supprimer"
            >
              <Trash2 class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-background/80 backdrop-blur-sm" @click="closeDeleteModal"></div>
      <div class="relative bg-card border border-border rounded-xl shadow-lg max-w-sm w-full p-6 animate-in fade-in zoom-in duration-200">
        <h3 class="text-lg font-semibold text-foreground mb-2">Confirmer la suppression</h3>
        <p class="text-muted-foreground mb-6">Voulez-vous vraiment supprimer ce rapport ? Cette action est irréversible.</p>
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
