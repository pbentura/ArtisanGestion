<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, FileText, Calendar, Download, Trash2, Search, CheckCircle2, Clock, MoreVertical, Share2 } from 'lucide-vue-next'
import MobileFAB from '@/components/mobile/MobileFAB.vue'
import MobileBottomSheet from '@/components/mobile/MobileBottomSheet.vue'
import { useMobile } from '@/composables/useMobile'

import { apiFetch } from '@/lib/api'
import { dataStore } from '@/lib/store'

interface Client {
  nom: string
}

interface Rapport {
  id: number
  titre_document_pdf: string
  date_intervention: string
  client?: Client
  statut: string
  photo_url?: string
  photos?: string[]
  created_at: string
}

const router = useRouter()
const { sharePDF, triggerHaptic, isNative } = useMobile()
const isBottomSheetOpen = ref(false)
const selectedRapport = ref<Rapport | null>(null)

function openBottomSheet(rapport: Rapport) {
  selectedRapport.value = rapport
  isBottomSheetOpen.value = true
}

function closeBottomSheet() {
  isBottomSheetOpen.value = false
  setTimeout(() => {
    selectedRapport.value = null
  }, 300)
}
const rapports = computed(() => dataStore.rapports.data)
const loading = computed(() => dataStore.rapports.loading)
const showDeleteConfirm = ref(false)
const idToDelete = ref<number | null>(null)
const isDeleting = ref(false)
const isUpdatingStatus = ref<number | null>(null)

const searchQuery = ref('')

const filteredRapports = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return rapports.value
  return rapports.value.filter(r => 
    (r.titre_document_pdf?.toLowerCase() || '').includes(query) ||
    (r.client?.nom?.toLowerCase() || '').includes(query)
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

function fetchRapports() {
  dataStore.fetchRapports()
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
    const res = await apiFetch(`rapports/${idToDelete.value}`, {
      method: 'DELETE',
    })
    if (res.ok) {
      dataStore.removeItem('rapports', idToDelete.value)
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

async function toggleStatus(rapport: Rapport) {
  if (isUpdatingStatus.value !== null) return
  
  const newStatut = rapport.statut === 'terminée' ? 'en cours' : 'terminée'
  isUpdatingStatus.value = rapport.id
  
  try {
    const res = await apiFetch(`rapports/${rapport.id}`, {
      method: 'PUT',
      body: JSON.stringify({ statut: newStatut })
    })
    
    if (res.ok) {
      const updatedRapport = await res.json()
      dataStore.updateItem('rapports', rapport.id, updatedRapport)
    } else {
      console.error('Erreur lors du changement de statut')
    }
  } catch (e) {
    console.error('Erreur réseau lors du changement de statut', e)
  } finally {
    isUpdatingStatus.value = null
  }
}



async function generateFullPDF(rapport: Rapport) {
  try {
    const res = await apiFetch(`rapports/${rapport.id}`)
    if (!res.ok) return
    const r = await res.json()
    
    // Fetch societe information
    const societeRes = await apiFetch('societes/me')
    let societe: Record<string, string> = { nom: '', logo: '', adresse: '', code_postal: '', ville: '', telephone: '', email: '', siret: '', texte_pied_page: '' }
    if (societeRes.ok) {
       societe = await societeRes.json()
    }
  
  const pdfFormatDate = (dateString: string) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit', month: '2-digit', year: 'numeric'
    })
  }

  const adresseSociete = [societe.adresse, societe.code_postal, societe.ville]
    .filter(Boolean)
    .join(' ')
  const photos = r.photos && r.photos.length > 0 ? r.photos : (r.photo_url ? [r.photo_url] : [])
  const photosHtml = photos.length > 0 ? `
    <div style="margin-top: 20px;">
      <h2 style="color: #2563eb; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; margin-bottom: 15px; font-size: 13px; font-weight: 600; text-transform: uppercase;">Photos (${photos.length})</h2>
      <div style="display: grid; grid-template-columns: 1fr; gap: 15px;">
        ${photos.map((p: string) => `
          <div style="margin-bottom: 10px; page-break-inside: avoid;">
            <img src="${p}" style="max-width: 100%; max-height: 500px; object-fit: contain; border-radius: 4px; border: 1px solid #e5e7eb;" />
          </div>
        `).join('')}
      </div>
    </div>
  ` : ''

  const footerText = societe.texte_pied_page || ''

  const container = document.createElement('div')
  container.innerHTML = `
  <div style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; padding: 15px; background: white; font-size: 12px;">

    <!-- EN-TÊTE : Logo + Infos société -->
    <div style="display: flex; align-items: flex-start; justify-content: space-between; padding-bottom: 15px; border-bottom: 3px solid #2563eb; margin-bottom: 15px;">
      <!-- Logo -->
      <div style="flex-shrink: 0; width: 120px; height: 70px; display: flex; align-items: center; justify-content: flex-start;">
        ${societe.logo
          ? `<img src="${societe.logo}" style="max-width: 120px; max-height: 70px; object-fit: contain;" />`
          : `<div style="width: 70px; height: 70px; background: #2563eb; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
              <span style="color: white; font-size: 24px; font-weight: 700;">${(societe.nom || 'E').charAt(0).toUpperCase()}</span>
             </div>`
        }
      </div>
      <!-- Infos société -->
      <div style="text-align: right; flex: 1; padding-left: 15px;">
        <div style="font-size: 16px; font-weight: 700; color: #1f2937; margin-bottom: 4px;">${societe.nom || ''}</div>
        ${adresseSociete ? `<div style="font-size: 10px; color: #6b7280;">${adresseSociete}</div>` : ''}
        ${societe.telephone ? `<div style="font-size: 10px; color: #6b7280;">Tél : ${societe.telephone}</div>` : ''}
        ${societe.email ? `<div style="font-size: 10px; color: #6b7280;">${societe.email}</div>` : ''}
        ${societe.siret ? `<div style="font-size: 9px; color: #9ca3af; margin-top: 3px;">SIRET : ${societe.siret}</div>` : ''}
      </div>
    </div>

    <!-- TITRE DU RAPPORT -->
    <div style="text-align: center; margin-bottom: 20px; padding: 10px; background: #f1f5f9; border-radius: 6px;">
      <h1 style="color: #1e3a5f; margin: 0; font-size: 18px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">${r.titre_document_pdf}</h1>
    </div>

    <div style="margin-bottom: 15px;">
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
        <div>
          <div style="margin-bottom: 10px;">
            <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Client</div>
            <div style="font-size: 12px; color: #1f2937;"><strong>${r.client?.nom || '-'}</strong></div>
          </div>
          <div style="margin-bottom: 10px;">
            <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Adresse d'intervention</div>
            <div style="font-size: 12px; color: #1f2937;">
              ${r.client?.adresse || '-'}<br/>
              ${[r.client?.code_postal, r.client?.ville].filter(Boolean).join(' ')}${[r.client?.code_postal, r.client?.ville].filter(Boolean).length > 0 ? '<br/>' : ''}
              ${r.client?.telephone ? `Tél: ${r.client.telephone}` : ''}
            </div>
          </div>
          ${r.client?.siret ? `
          <div style="margin-bottom: 10px;">
            <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">SIRET / SIREN client</div>
            <div style="font-size: 12px; color: #1f2937;">${r.client.siret}</div>
          </div>
          ` : ''}
        </div>
        <div>
          <div style="margin-bottom: 10px;">
            <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Date d'intervention</div>
            <div style="font-size: 13px; font-weight: 600; color: #1f2937;">${pdfFormatDate(r.date_intervention)}</div>
          </div>
        </div>
      </div>
    </div>

    <div style="margin-bottom: 20px;">
      <h2 style="color: #2563eb; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; margin-bottom: 10px; font-size: 13px; font-weight: 600; text-transform: uppercase;">Rapport d'intervention</h2>
      <div style="font-size: 12px; line-height: 1.8;">${r.contenu || '<p>Aucun contenu</p>'}</div>
    </div>

    ${photosHtml}
  </div>`

  document.body.appendChild(container)

  const filename = (r.titre_document_pdf || 'rapport').replace(/[^a-zA-Z0-9àâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ _-]/g, '').replace(/\s+/g, '_')

  const { default: html2pdf } = await import('html2pdf.js')

  const worker = html2pdf()
    .set({
      margin: [15, 15, footerText ? 25 : 15, 15],
      filename: `${filename}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
    } as any)
    .from(container)
    .toPdf()

  // Get the jsPDF instance to add footer text
  const pdf: any = await worker.get('pdf')
  if (footerText && pdf) {
    const totalPages = pdf.internal.getNumberOfPages()
    const pageWidth = pdf.internal.pageSize.getWidth()
    for (let i = 1; i <= totalPages; i++) {
      pdf.setPage(i)
      pdf.setFontSize(8)
      pdf.setTextColor(107, 114, 128)
      const lines = pdf.splitTextToSize(footerText, pageWidth - 30)
      const startY = pdf.internal.pageSize.getHeight() - (lines.length * 4) - 8
      lines.forEach((line: string, idx: number) => {
        pdf.text(line, pageWidth / 2, startY + (idx * 4), { align: 'center' })
      })
    }
  }

    if (isNative) {
      const blob = await worker.output('blob')
      await sharePDF(blob, `${filename}.pdf`)
      await triggerHaptic()
    } else {
      await worker.save()
    }

  document.body.removeChild(container)

  } catch (e) {
    console.error('Erreur lors de la génération du PDF', e)
  }
}

onMounted(fetchRapports)
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 hidden lg:flex animate-fade-slide-up">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-foreground">Rapports d'intervention</h1>
        <p class="text-sm sm:text-base text-muted-foreground mt-1">Gérez vos rapports d'intervention et créez-en de nouveaux</p>
      </div>
      <button
        @click="router.push('/app/rapports/new')"
        class="inline-flex items-center justify-center gap-2 bg-primary text-primary-foreground px-4 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors shrink-0 w-full sm:w-auto"
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
        @click="router.push('/app/rapports/new')"
        class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
      >
        <Plus class="w-4 h-4" />
        Créer mon premier rapport
      </button>
    </div>

    <!-- Rapports List -->
    <div v-else-if="rapports.length > 0" class="grid gap-4">
      <div class="relative animate-fade-slide-up" style="animation-delay: 0.1s">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Rechercher un rapport par titre ou client..."
          class="w-full pl-10 pr-4 py-2.5 bg-card border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
        />
      </div>
      <div
        v-for="(rapport, idx) in filteredRapports"
        :key="rapport.id"
        class="bg-card border border-border rounded-xl p-4 sm:p-6 hover:border-primary/50 transition-colors cursor-pointer animate-fade-slide-up"
        :style="{ animationDelay: (0.15 + idx * 0.05) + 's' }"
        @click="router.push(`/app/rapports/${rapport.id}`)"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 sm:gap-3 mb-2">
              <h3 class="text-base sm:text-lg font-semibold text-foreground truncate">{{ rapport.titre_document_pdf || "Rapport d'intervention" }}</h3>
              <span 
                :class="[
                  'px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap',
                  rapport.statut === 'terminée' 
                    ? 'bg-green-100 text-green-700 font-bold border border-green-200' 
                    : 'bg-blue-100 text-blue-700 font-bold border border-blue-200'
                ]"
              >
                {{ rapport.statut === 'terminée' ? 'Terminée' : 'En cours' }}
              </span>
            </div>
            <div class="flex flex-wrap items-center gap-2 sm:gap-4 text-sm text-muted-foreground">
              <span class="flex items-center gap-1">
                <Calendar class="w-4 h-4" />
                {{ formatDate(rapport.date_intervention) }}
              </span>
              <span>{{ rapport.client?.nom || 'Client inconnu' }}</span>
            </div>
          </div>
            <div class="sm:hidden flex items-center justify-center">
              <button 
                class="p-2 text-muted-foreground hover:bg-muted rounded-full transition-colors"
                @click.stop="openBottomSheet(rapport)"
              >
                <MoreVertical class="w-5 h-5" />
              </button>
            </div>

            <div class="hidden sm:flex flex-wrap items-center gap-2 sm:ml-4">
            <button
              @click.stop="toggleStatus(rapport)"
              class="inline-flex items-center gap-2 px-3 py-1.5 transition-colors rounded-lg group border border-transparent"
              :class="[
                rapport.statut === 'terminée' 
                  ? 'text-green-600 hover:bg-green-50 hover:border-green-200' 
                  : 'text-blue-600 hover:bg-blue-50 hover:border-blue-200'
              ]"
              :title="rapport.statut === 'terminée' ? 'Marquer comme en cours' : 'Marquer comme terminée'"
              :disabled="isUpdatingStatus === rapport.id"
            >
              <template v-if="isUpdatingStatus === rapport.id">
                <span class="block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              </template>
              <template v-else>
                <CheckCircle2 v-if="rapport.statut === 'en cours'" class="w-4 h-4 group-hover:scale-110 transition-transform" />
                <Clock v-else class="w-4 h-4 group-hover:scale-110 transition-transform" />
              </template>
              <span class="text-xs font-semibold">{{ rapport.statut === 'terminée' ? 'Terminé' : 'Terminer' }}</span>
            </button>

            <button
              @click.stop="generateFullPDF(rapport)"
              class="inline-flex items-center gap-2 px-3 py-1.5 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-lg transition-colors border border-transparent hover:border-primary/20"
              title="Télécharger PDF"
            >
              <Download class="w-4 h-4" />
              <span class="text-xs font-semibold">PDF</span>
            </button>

            <button
              @click.stop="openDeleteModal(rapport.id)"
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
      <p class="text-muted-foreground mb-6">Aucun rapport ne correspond à votre recherche.</p>
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
    <!-- Mobile FAB -->
    <MobileFAB v-if="isNative" class="lg:hidden" @click="router.push('/app/rapports/new')" />

    <!-- Mobile Bottom Sheet for Actions -->
    <MobileBottomSheet 
      :is-open="isBottomSheetOpen" 
      :title="selectedRapport ? `Rapport d'intervention` : ''"
      @close="closeBottomSheet"
    >
      <div v-if="selectedRapport" class="flex flex-col gap-2 mt-4">
        <button
          @click="toggleStatus(selectedRapport); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl transition-colors text-left"
          :class="[
            selectedRapport.statut === 'terminée' 
              ? 'text-green-600 bg-green-50' 
              : 'text-blue-600 bg-blue-50'
          ]"
        >
          <CheckCircle2 v-if="selectedRapport.statut === 'en cours'" class="w-5 h-5" />
          <Clock v-else class="w-5 h-5" />
          <span class="font-medium">{{ selectedRapport.statut === 'terminée' ? 'Marquer comme en cours' : 'Marquer comme terminée' }}</span>
        </button>

        <button
          @click="generateFullPDF(selectedRapport); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-teal-600 bg-teal-50 transition-colors text-left"
        >
          <Share2 class="w-5 h-5" />
          <span class="font-medium">Partager le rapport (PDF)</span>
        </button>

        <button
          @click="openDeleteModal(selectedRapport.id); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-destructive bg-destructive/10 transition-colors text-left mt-4"
        >
          <Trash2 class="w-5 h-5" />
          <span class="font-medium">Supprimer le rapport</span>
        </button>
      </div>
    </MobileBottomSheet>
  </div>
</template>
