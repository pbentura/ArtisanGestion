<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, FileText, Calendar, Download, Trash2, Search, CheckCircle2, Clock, Receipt, MoreVertical, Share2, Mail, PenLine, Copy, Check, X } from 'lucide-vue-next'
import { useMobile } from '@/composables/useMobile'
import MobileSegmentedControl from '@/components/mobile/MobileSegmentedControl.vue'
import MobileFAB from '@/components/mobile/MobileFAB.vue'
import MobileBottomSheet from '@/components/mobile/MobileBottomSheet.vue'
import EmailModal from '@/components/EmailModal.vue'
import AcompteModal from '@/components/AcompteModal.vue'

import { apiFetch } from '@/lib/api'
import { dataStore, uiStore } from '@/lib/store'

const canCreate = computed(() => dataStore.user.data?.can_create_devis !== false)

interface Client {
  nom: string
  email?: string
}

interface Devis {
  id: number
  titre_document_pdf: string
  date_devis: string
  numero_devis: string
  client?: Client
  statut: string
  created_at: string
  signature_nom?: string | null
  signature_le?: string | null
  est_en_attente_signature?: boolean
}

const router = useRouter()
const { isNative, isMobileView } = useMobile()
const devisList = computed(() => dataStore.devis.data)
const trialEnded = computed(() => dataStore.user.data?.trial_days_remaining === 0)
const loading = computed(() => dataStore.devis.loading)
const showDeleteConfirm = ref(false)
const idToDelete = ref<number | null>(null)
const isDeleting = ref(false)
const isUpdatingStatus = ref<number | null>(null)

const searchQuery = ref('')
const statusFilter = ref('tous') // tous, brouillon, envoyé
const activeTab = ref('devis')
const isBottomSheetOpen = ref(false)
const selectedDevis = ref<Devis | null>(null)

const showEmailModal = ref(false)
const emailDocumentId = ref<number | null>(null)
const emailDocumentRef = ref('')
const emailClientEmail = ref('')

const showAcompteModal = ref(false)
const acompteDevis = ref<Devis | null>(null)

function openEmailModal(devis: Devis) {
  emailDocumentId.value = devis.id
  emailDocumentRef.value = devis.numero_devis
  emailClientEmail.value = devis.client?.email || ''
  showEmailModal.value = true
}

function openBottomSheet(devis: Devis) {
  selectedDevis.value = devis
  isBottomSheetOpen.value = true
}

function openAcompteModal(devis: Devis) {
  acompteDevis.value = devis
  showAcompteModal.value = true
}

function closeBottomSheet() {
  isBottomSheetOpen.value = false
  setTimeout(() => {
    selectedDevis.value = null
  }, 300)
}

function handleTabChange(val: string) {
  if (val === 'factures') {
    router.push('/app/factures')
  }
}

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

function fetchDevis() {
  dataStore.fetchDevis()
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
    const res = await apiFetch(`devis/${idToDelete.value}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      dataStore.removeItem('devis', idToDelete.value)
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
    const res = await apiFetch(`devis/${devis.id}`, {
      method: 'PUT',
      body: JSON.stringify({ statut: newStatut })
    })
    
    if (res.ok) {
      const updatedDevis = await res.json()
      dataStore.updateItem('devis', devis.id, updatedDevis)
    } else {
      console.error('Erreur lors du changement de statut')
    }
  } catch (e) {
    console.error('Erreur réseau lors du changement de statut', e)
  } finally {
    isUpdatingStatus.value = null
  }
}

async function shareDevis(devis: Devis) {
  // Logic to generate and share devis PDF
  // Similar to generateFullPDF in RapportsList
  // For now we'll just redirect to the PDF preview if not native
  if (!isNative) {
    router.push(`/app/devis/${devis.id}/pdf`)
    return
  }
  
  // If native, we should ideally have a common PDF generator utility
  // But for now, we'll use the same logic as in NouveauDevis if possible
  // Or just trigger the download and let Filesystem/Share handle it if it was a blob
  // Since we don't have a backend PDF endpoint yet for Devis, we might need to skip or implement it.
  // Let's assume there's a need for a backend endpoint.
  alert("Le partage direct sera disponible bientôt. Utilisez l'aperçu PDF.")
}

// ── Signature électronique à distance ──

const envoiSignature = ref<number | null>(null)
const lienSignature = ref<{ url: string; email: string | null } | null>(null)

const lienCopie = ref(false)

async function demanderSignature(devis: Devis) {
  if (devis.signature_le) return

  if (!devis.client?.email) {
    alert(`Renseignez l'email de ${devis.client?.nom || 'ce client'} dans sa fiche pour lui envoyer le devis à signer.`)
    return
  }

  envoiSignature.value = devis.id
  lienSignature.value = null
  try {
    const res = await apiFetch(`devis/${devis.id}/demande-signature`, {
      method: 'POST',
      body: JSON.stringify({}),
    })
    const data = await res.json().catch(() => ({}))

    if (!res.ok) {
      alert(data.detail || "La demande de signature n'a pas pu être envoyée.")
      return
    }

    lienSignature.value = { url: data.url, email: data.email_envoye_a }
    lienCopie.value = false
    // force : le store met les devis en cache 30 s, sinon le statut et le
    // bouton resteraient sur leur état d'avant la demande.
    await dataStore.fetchDevis(true)
  } catch {
    alert('Erreur réseau. Vérifiez votre connexion et réessayez.')
  } finally {
    envoiSignature.value = null
  }
}

async function copierLien() {
  if (!lienSignature.value) return
  try {
    await navigator.clipboard.writeText(lienSignature.value.url)
    lienCopie.value = true
    setTimeout(() => { lienCopie.value = false }, 2000)
  } catch {
    /* le lien reste affiché et sélectionnable à la main */
  }
}

onMounted(fetchDevis)
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <!-- Lien de signature généré : l'artisan peut le transmettre lui-même -->
    <div v-if="lienSignature"
         class="mb-6 rounded-xl border border-violet-200 bg-violet-50 p-4 flex flex-wrap items-start gap-3">
      <PenLine class="w-5 h-5 text-violet-600 shrink-0 mt-0.5" />
      <div class="flex-1 min-w-[220px]">
        <p class="text-sm font-semibold text-violet-900">
          {{ lienSignature.email
             ? `Demande de signature envoyée à ${lienSignature.email}`
             : "Lien de signature prêt — l'email n'a pas pu partir, transmettez-le vous-même" }}
        </p>
        <p class="text-xs text-violet-700/80 mt-1 break-all font-mono">{{ lienSignature.url }}</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="copierLien"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-violet-700 bg-white border border-violet-200 hover:bg-violet-100 transition-colors">
          <Check v-if="lienCopie" class="w-3.5 h-3.5" />
          <Copy v-else class="w-3.5 h-3.5" />
          {{ lienCopie ? 'Copié' : 'Copier' }}
        </button>
        <button @click="lienSignature = null"
                class="p-1.5 rounded-lg text-violet-500 hover:bg-violet-100 transition-colors"
                title="Masquer">
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

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

    <!-- FAB pour mobile -->
    <MobileFAB 
      v-if="canCreate"
      icon="plus" 
      @click="trialEnded ? uiStore.openSubscriptionModal() : router.push('/app/devis/new')" 
    />

    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 hidden lg:flex animate-fade-slide-up">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-foreground">Devis</h1>
        <p class="text-sm sm:text-base text-muted-foreground mt-1">Gérez vos devis et créez-en de nouveaux</p>
      </div>
      <button
        v-if="canCreate"
        @click="trialEnded ? uiStore.openSubscriptionModal() : router.push('/app/devis/new')"
        class="btn-primary"
        title="Nouveau devis"
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
        v-if="canCreate"
        @click="trialEnded ? uiStore.openSubscriptionModal() : router.push('/app/devis/new')"
        class="btn-primary w-full sm:w-auto"
        title="Nouveau devis"
      >
        <Plus class="w-4 h-4" />
        Créer mon premier devis
      </button>
    </div>

    <!-- Devis List -->
    <div v-else-if="devisList.length > 0" class="grid gap-4">
      <div class="flex flex-col md:flex-row gap-4 animate-fade-slide-up" style="animation-delay: 0.1s">
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
        v-for="(devis, idx) in filteredDevis"
        :key="devis.id"
        class="bg-card border border-border rounded-xl p-4 sm:p-6 hover:border-primary/50 transition-colors cursor-pointer animate-fade-slide-up"
        :style="{ animationDelay: (0.15 + idx * 0.05) + 's' }"
        @click="router.push(`/app/devis/${devis.id}`)"
      >
        <div class="flex items-start justify-between gap-3">
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
          
          <!-- Mobile Actions Trigger -->
          <div class="sm:hidden flex items-center justify-center">
            <button 
              class="p-2 text-muted-foreground hover:bg-muted rounded-full transition-colors"
              @click.stop="openBottomSheet(devis)"
            >
              <MoreVertical class="w-5 h-5" />
            </button>
          </div>

          <!-- Desktop Inline Actions -->
          <div class="hidden sm:flex flex-wrap items-center gap-2 sm:ml-4">
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

            <!-- Signature électronique à distance -->
            <span
              v-if="devis.signature_le"
              class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-emerald-700 bg-emerald-50 border border-emerald-200"
              :title="`Signé par ${devis.signature_nom} le ${new Date(devis.signature_le).toLocaleDateString('fr-FR')}`"
            >
              <PenLine class="w-4 h-4" />
              <span class="text-xs font-semibold">Signé</span>
            </span>

            <button
              v-else-if="devis.statut !== 'facturé' && canCreate"
              @click.stop="demanderSignature(devis)"
              :disabled="envoiSignature === devis.id"
              class="inline-flex items-center gap-2 px-3 py-1.5 transition-colors rounded-lg group border border-transparent text-violet-600 hover:bg-violet-50 hover:border-violet-200 disabled:opacity-60"
              :title="devis.est_en_attente_signature
                ? 'Renvoyer la demande de signature au client'
                : 'Envoyer au client pour signature en ligne'"
            >
              <span v-if="envoiSignature === devis.id"
                    class="block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
              <PenLine v-else class="w-4 h-4 group-hover:scale-110 transition-transform" />
              <span class="text-xs font-semibold">
                {{ devis.est_en_attente_signature ? 'Relancer' : 'Faire signer' }}
              </span>
            </button>

            <button
              v-if="devis.statut !== 'facturé'"
              @click.stop="trialEnded ? uiStore.openSubscriptionModal() : router.push(`/app/factures/new?fromDevis=${devis.id}`)"
              class="inline-flex items-center gap-2 px-3 py-1.5 text-muted-foreground hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors border border-transparent hover:border-emerald-200"
              title="Facturer ce devis"
            >
              <Receipt class="w-4 h-4" />
              <span class="text-xs font-semibold">Facturer</span>
            </button>
            
            <button
              @click.stop="trialEnded ? uiStore.openSubscriptionModal() : openAcompteModal(devis)"
              class="inline-flex items-center gap-2 px-3 py-1.5 text-muted-foreground hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors border border-transparent hover:border-purple-200"
              title="Générer un acompte"
            >
              <Euro class="w-4 h-4" />
              <span class="text-xs font-semibold">Acompte</span>
            </button>

            <button
              @click.stop="trialEnded ? uiStore.openSubscriptionModal() : openEmailModal(devis)"
              class="inline-flex items-center gap-2 px-3 py-1.5 text-muted-foreground hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors border border-transparent hover:border-blue-200"
              title="Envoyer par e-mail"
            >
              <Mail class="w-4 h-4" />
              <span class="text-xs font-semibold">E-mail</span>
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
        class="btn-primary"
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

    <!-- Mobile FAB -->
    <MobileFAB v-if="isMobileView" class="lg:hidden" @click="router.push('/app/devis/new')" />

    <!-- Mobile Bottom Sheet for Actions -->
    <MobileBottomSheet 
      :is-open="isBottomSheetOpen" 
      :title="selectedDevis ? `Devis ${selectedDevis.numero_devis}` : ''"
      @close="closeBottomSheet"
    >
      <div v-if="selectedDevis" class="flex flex-col gap-2 mt-4">
        <button
          @click="toggleStatus(selectedDevis); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl transition-colors text-left"
          :class="[
            selectedDevis.statut === 'envoyé' 
              ? 'text-green-600 bg-green-50' 
              : 'text-blue-600 bg-blue-50'
          ]"
        >
          <CheckCircle2 v-if="selectedDevis.statut === 'brouillon'" class="w-5 h-5" />
          <Clock v-else class="w-5 h-5" />
          <span class="font-medium">{{ selectedDevis.statut === 'envoyé' ? 'Marquer comme brouillon' : 'Marquer comme envoyé' }}</span>
        </button>

        <div v-if="selectedDevis.signature_le"
             class="flex items-center gap-3 p-4 rounded-xl text-emerald-700 bg-emerald-50">
          <PenLine class="w-5 h-5" />
          <span class="font-medium">
            Signé par {{ selectedDevis.signature_nom }}
            le {{ formatDate(selectedDevis.signature_le) }}
          </span>
        </div>

        <button
          v-else-if="selectedDevis.statut !== 'facturé' && canCreate"
          @click="demanderSignature(selectedDevis); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl transition-colors text-left text-violet-600 bg-violet-50"
        >
          <PenLine class="w-5 h-5" />
          <span class="font-medium">
            {{ selectedDevis.est_en_attente_signature ? 'Relancer pour signature' : 'Faire signer le devis' }}
          </span>
        </button>

        <button
          @click="trialEnded ? uiStore.openSubscriptionModal() : router.push(`/app/factures/new?fromDevis=${selectedDevis.id}`); closeBottomSheet()"
          class="w-full text-left px-4 py-3 flex items-center gap-3 active:bg-muted transition-colors"
        >
          <Receipt class="w-5 h-5 text-foreground" />
          <span class="font-medium">Transformer en facture <span v-if="trialEnded" class="text-xs text-red-500">(Essai terminé)</span></span>
        </button>
        
        <button 
          @click="trialEnded ? uiStore.openSubscriptionModal() : openAcompteModal(selectedDevis); closeBottomSheet()"
          class="w-full text-left px-4 py-3 flex items-center gap-3 active:bg-muted transition-colors"
        >
          <Euro class="w-5 h-5 text-purple-600" />
          <span class="font-medium text-purple-700">Générer un acompte <span v-if="trialEnded" class="text-xs text-red-500">(Essai terminé)</span></span>
        </button>

        <button
          @click="shareDevis(selectedDevis); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-teal-600 bg-teal-50 transition-colors text-left"
        >
          <Share2 class="w-5 h-5" />
          <span class="font-medium">Partager le devis</span>
        </button>

        <button 
          @click="trialEnded ? uiStore.openSubscriptionModal() : openEmailModal(selectedDevis); closeBottomSheet()"
          class="w-full text-left px-4 py-3 flex items-center gap-3 active:bg-muted transition-colors"
        >
          <Mail class="w-5 h-5 text-foreground" />
          <span class="font-medium">Envoyer par e-mail <span v-if="trialEnded" class="text-xs text-red-500">(Essai terminé)</span></span>
        </button>

        <button
          @click="router.push(`/app/devis/${selectedDevis.id}/pdf`); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-primary bg-primary/10 transition-colors text-left"
        >
          <Download class="w-5 h-5" />
          <span class="font-medium">Aperçu PDF</span>
        </button>

        <button
          @click="openDeleteModal(selectedDevis.id); closeBottomSheet()"
          class="flex items-center gap-3 p-4 rounded-xl text-destructive bg-destructive/10 transition-colors text-left mt-4"
        >
          <Trash2 class="w-5 h-5" />
          <span class="font-medium">Supprimer le devis</span>
        </button>
      </div>
    </MobileBottomSheet>
    <EmailModal
      :is-open="showEmailModal"
      :document-id="emailDocumentId"
      document-type="devis"
      :document-ref="emailDocumentRef"
      :client-email="emailClientEmail"
      @close="showEmailModal = false"
      @success="fetchDevis"
    />
    <AcompteModal
      :is-open="showAcompteModal"
      :devis="acompteDevis"
      @close="showAcompteModal = false"
      @success="() => { showAcompteModal = false; fetchDevis(); }"
    />
  </div>
</template>
