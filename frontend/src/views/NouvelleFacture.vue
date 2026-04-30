<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiFetch } from '@/lib/api'
import { ArrowLeft, Save, FileDown, Plus, Trash2, Loader2, X, Eye, Lock, CheckCircle2, FileCheck2, CreditCard, Undo2, Share2 } from 'lucide-vue-next'
import { useMobile } from '@/composables/useMobile'
import { useSwipe } from '@vueuse/core'

const router = useRouter()
const route = useRoute()
const { sharePDF, triggerHaptic, isNative } = useMobile()

const mainContainer = ref<HTMLElement | null>(null)
useSwipe(mainContainer, {
  onSwipeEnd(_e: TouchEvent, direction) {
    if (direction === 'right' && isNative) {
      router.push('/app/factures')
    }
  }
})

const isSaving = ref(false)
const isGeneratingPDF = ref(false)
const isLoading = ref(false)
const showPDFModal = ref(false)
const previewHTML = ref('')
const pdfUrl = ref('')
const showValidateConfirm = ref(false)
const isDownloadingFacturX = ref(false)
const isUpdatingPayment = ref(false)
const isCreatingAvoir = ref(false)

// Mode édition
const isEditMode = computed(() => !!route.params.id)
const factureId = computed(() => route.params.id ? Number(route.params.id) : null)
const fromDevisId = computed(() => route.query.fromDevis ? Number(route.query.fromDevis) : null)

interface LigneFacture {
  id?: number
  description: string
  quantite: number
  prix_unite_ht: number
  taux_tva: number
  total_ht: number
}

interface FactureForm {
  id?: number
  date_facture: string
  numero_facture: string
  titre_document_pdf: string
  objet_facture: string
  nomClient: string
  clientSiret: string
  adresseIntervention: string
  clientCodePostal: string
  clientVille: string
  contactClient: string
  clientEmail: string
  conditions_particulieres: string
  nb_jours_echeance: number
  date_echeance: string
  statut: string
  est_payee: boolean
  est_avoir: boolean
  lignes: LigneFacture[]
  id_devis?: number | null
}

const now = new Date()

const facture = ref<FactureForm>({
  date_facture: now.toISOString().split('T')[0],
  numero_facture: `FAC-${now.toISOString().split('T')[0].replace(/-/g, '')}-${now.getHours().toString().padStart(2, '0')}${now.getMinutes().toString().padStart(2, '0')}`,
  titre_document_pdf: "FACTURE",
  objet_facture: '',
  nomClient: '',
  clientSiret: '',
  adresseIntervention: '',
  clientCodePostal: '',
  clientVille: '',
  contactClient: '',
  clientEmail: '',
  conditions_particulieres: "Paiement à réception de la facture.",
  nb_jours_echeance: 30,
  date_echeance: '',
  statut: 'brouillon',
  est_payee: false,
  est_avoir: false,
  lignes: [],
  id_devis: null
})

// Statut original chargé depuis le serveur (pour verrouillage)
const originalStatut = ref<string>('')

// Facture verrouillée si le statut sauvegardé en BDD est 'validée'
const isLocked = computed(() => originalStatut.value === 'validée')

function requestValidation() {
  showValidateConfirm.value = true
}

function closeValidateModal() {
  showValidateConfirm.value = false
}

function confirmValidation() {
  facture.value.statut = 'validée'
  showValidateConfirm.value = false
  // Si on est en mode édition, on sauvegarde immédiatement le changement de statut
  if (isEditMode.value) {
    saveFacture()
  }
}

async function togglePayment() {
  if (!factureId.value || isUpdatingPayment.value) return
  
  isUpdatingPayment.value = true
  try {
    const res = await apiFetch(`factures/${factureId.value}`, {
      method: 'PUT',
      body: JSON.stringify({ est_payee: !facture.value.est_payee })
    })
    
    if (res.ok) {
      const updated = await res.json()
      facture.value.est_payee = updated.est_payee
    }
  } catch (e) {
    console.error(e)
  } finally {
    isUpdatingPayment.value = false
  }
}

async function creerAvoir() {
  if (!factureId.value || isCreatingAvoir.value) return
  
  if (!confirm(`Voulez-vous vraiment créer un avoir pour la facture ${facture.value.numero_facture} ?`)) return
  
  isCreatingAvoir.value = true
  try {
    const res = await apiFetch(`factures/${factureId.value}/avoir`, {
      method: 'POST'
    })
    
    if (res.ok) {
      const nouvelAvoir = await res.json()
      router.push(`/app/factures/${nouvelAvoir.id}`)
    } else {
      const errorData = await res.json()
      alert(`Erreur : ${errorData.detail || 'Impossible de créer un avoir'}`)
    }
  } catch (e) {
    console.error(e)
  } finally {
    isCreatingAvoir.value = false
  }
}

async function shareFacture() {
  if (!factureId.value || isDownloadingFacturX.value) return
  
  isDownloadingFacturX.value = true
  try {
    // On utilise Factur-X pour le partage car c'est le format le plus complet
    const res = await apiFetch(`factures/${factureId.value}/facturx`)
    if (!res.ok) throw new Error('Erreur génération PDF')
    
    const blob = await res.blob()
    const filename = `Facture_${facture.value.numero_facture}.pdf`
    
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
    }
  } catch (e) {
    console.error(e)
    alert('Erreur lors du partage')
  } finally {
    isDownloadingFacturX.value = false
  }
}

// Auto-calcul de la date d'échéance
watch(
  () => [facture.value.date_facture, facture.value.nb_jours_echeance],
  () => {
    if (facture.value.date_facture && facture.value.nb_jours_echeance) {
      const d = new Date(facture.value.date_facture)
      d.setDate(d.getDate() + facture.value.nb_jours_echeance)
      facture.value.date_echeance = d.toISOString().split('T')[0]
    }
  },
  { immediate: true }
)

// Variables liées à l'entreprise de l'utilisateur
const societe = ref({
  nom: '',
  siret: '',
  logo: '',
  adresse: '',
  code_postal: '',
  ville: '',
  telephone: '',
  email: '',
  texte_pied_page: ''
})

// Autocomplete du client
const clients = ref<any[]>([])
const selectedClientId = ref<number | null>(null)
const showSuggestions = ref(false)
const focusedIndex = ref(-1)

const filteredClients = computed(() => {
  const query = facture.value.nomClient.toLowerCase().trim()
  if (!query || query.length < 1) return []
  return clients.value.filter(c => 
    c.nom.toLowerCase().includes(query) || 
    (c.ville && c.ville.toLowerCase().includes(query))
  ).slice(0, 8)
})

function selectClient(c: any) {
  facture.value.nomClient = c.nom
  facture.value.clientSiret = c.siret || ''
  facture.value.adresseIntervention = c.adresse || ''
  facture.value.clientCodePostal = c.code_postal || ''
  facture.value.clientVille = c.ville || ''
  facture.value.contactClient = c.telephone || ''
  facture.value.clientEmail = c.email || ''
  selectedClientId.value = c.id
  showSuggestions.value = false
  focusedIndex.value = -1
}

function handleKeyDown(e: KeyboardEvent) {
  if (!showSuggestions.value || filteredClients.value.length === 0) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    focusedIndex.value = (focusedIndex.value + 1) % filteredClients.value.length
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    focusedIndex.value = (focusedIndex.value - 1 + filteredClients.value.length) % filteredClients.value.length
  } else if (e.key === 'Enter') {
    if (focusedIndex.value >= 0) {
      e.preventDefault()
      selectClient(filteredClients.value[focusedIndex.value])
    }
  } else if (e.key === 'Escape') {
    showSuggestions.value = false
  }
}

function handleBlur() {
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

// Calculs de la facture
const TAUX_TVA = [0, 2.1, 5.5, 10, 20]

function ajouterLigne() {
  facture.value.lignes.push({
    description: '',
    quantite: 1,
    prix_unite_ht: 0,
    taux_tva: 20,
    total_ht: 0
  })
}

function supprimerLigne(index: number) {
  facture.value.lignes.splice(index, 1)
}

function updateLigneTotal(ligne: LigneFacture) {
  ligne.total_ht = Number((ligne.quantite * ligne.prix_unite_ht).toFixed(2))
}

const sous_total_ht = computed(() => {
  return facture.value.lignes.reduce((sum, ligne) => sum + ligne.total_ht, 0)
})

const total_tva = computed(() => {
  return facture.value.lignes.reduce((sum, ligne) => {
    return sum + (ligne.total_ht * (ligne.taux_tva / 100))
  }, 0)
})

const total_ttc = computed(() => {
  return sous_total_ht.value + total_tva.value
})

const formattedSousTotalHt = computed(() => sous_total_ht.value.toFixed(2))
const formattedTotalTva = computed(() => total_tva.value.toFixed(2))
const formattedTotalTtc = computed(() => total_ttc.value.toFixed(2))

const isValid = computed(() => {
  return facture.value.date_facture && facture.value.numero_facture && facture.value.nomClient.trim() && facture.value.adresseIntervention.trim()
})

// Autocomplete lignes
const pastDescriptions = ref<any[]>([])
const activeLineIndex = ref<number | null>(null)
const focusedLineIndex = ref(-1)

const lineSuggestions = computed(() => {
  if (activeLineIndex.value === null) return []
  const ligne = facture.value.lignes[activeLineIndex.value]
  if (!ligne || !ligne.description) return []
  const query = ligne.description.trim()
  if (query.length < 1) return []
  const lowerQuery = query.toLowerCase()
  return pastDescriptions.value.filter(d => (d.description || '').toLowerCase().includes(lowerQuery)).slice(0, 8)
})

function selectDescription(idx: number, suggestion: any) {
  facture.value.lignes[idx].description = suggestion.description
  facture.value.lignes[idx].quantite = Number(suggestion.quantite) || 1
  facture.value.lignes[idx].prix_unite_ht = Number(suggestion.prix_unite_ht) || 0
  facture.value.lignes[idx].taux_tva = Number(suggestion.taux_tva) || 20
  
  updateLigneTotal(facture.value.lignes[idx])
  activeLineIndex.value = null
  focusedLineIndex.value = -1
}

function handleLineKeyDown(e: KeyboardEvent, idx: number) {
  if (activeLineIndex.value !== idx) return
  const suggestions = lineSuggestions.value
  if (suggestions.length === 0) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    focusedLineIndex.value = (focusedLineIndex.value + 1) % suggestions.length
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    focusedLineIndex.value = (focusedLineIndex.value - 1 + suggestions.length) % suggestions.length
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (focusedLineIndex.value >= 0 && suggestions[focusedLineIndex.value]) {
      selectDescription(idx, suggestions[focusedLineIndex.value])
    }
  } else if (e.key === 'Escape') {
    activeLineIndex.value = null
    focusedLineIndex.value = -1
  }
}

function handleLineBlur() {
  setTimeout(() => {
    activeLineIndex.value = null
    focusedLineIndex.value = -1
  }, 200)
}

// Chargement des données
async function loadLineDescriptions() {
  try {
    const res = await apiFetch('devis/lignes/descriptions')
    if (res.ok) {
      pastDescriptions.value = await res.json()
    }
  } catch (e) {
    console.error('Erreur lors du chargement des descriptions:', e)
  }
}

async function loadClients() {
  try {
    const res = await apiFetch('clients')
    if (res.ok) {
      clients.value = await res.json()
    }
  } catch (e) {
    console.error('Erreur lors du chargement des clients:', e)
  }
}

async function loadSociete() {
  try {
    const res = await apiFetch('societes/me')
    if (res.ok) {
      const data = await res.json()
      societe.value = data
    }
  } catch (e) {
    console.error('Erreur lors du chargement de la société:', e)
  }
}

async function loadExistingFacture(id: number) {
  isLoading.value = true
  try {
    const res = await apiFetch(`factures/${id}`)
    if (!res.ok) {
      alert('Facture introuvable')
      router.push('/app/factures')
      return
    }
    const data = await res.json()
    
    // Mémoriser le statut serveur pour le verrouillage
    originalStatut.value = data.statut || 'brouillon'
    
    facture.value = {
      id: data.id,
      date_facture: data.date_facture,
      numero_facture: data.numero_facture,
      titre_document_pdf: data.titre_document_pdf || "FACTURE",
      objet_facture: data.objet_facture || '',
      nomClient: data.client?.nom || '',
      clientSiret: data.client?.siret || '',
      adresseIntervention: data.client?.adresse || '',
      clientCodePostal: data.client?.code_postal || '',
      clientVille: data.client?.ville || '',
      contactClient: data.client?.telephone || '',
      clientEmail: data.client?.email || '',
      conditions_particulieres: data.conditions_particulieres || '',
      nb_jours_echeance: data.nb_jours_echeance || 30,
      date_echeance: data.date_echeance || '',
      statut: data.statut || 'brouillon',
      est_payee: data.est_payee || false,
      est_avoir: data.est_avoir || false,
      lignes: data.lignes ? data.lignes.map((l: any) => ({
        id: l.id,
        description: l.description,
        quantite: Number(l.quantite),
        prix_unite_ht: Number(l.prix_unite_ht),
        taux_tva: Number(l.taux_tva),
        total_ht: Number(l.total_ht)
      })) : [],
      id_devis: data.id_devis || null
    }
    
    if (data.client?.id) {
      selectedClientId.value = data.client.id
    }
  } catch (e) {
    console.error('Erreur lors du chargement de la facture:', e)
  } finally {
    isLoading.value = false
  }
}

async function loadDevisForConversion(devisId: number) {
  isLoading.value = true
  try {
    const res = await apiFetch(`devis/${devisId}`)
    if (!res.ok) {
      alert('Devis introuvable')
      return
    }
    const data = await res.json()
    
    facture.value = {
      date_facture: now.toISOString().split('T')[0],
      numero_facture: `FAC-${now.toISOString().split('T')[0].replace(/-/g, '')}-${now.getHours().toString().padStart(2, '0')}${now.getMinutes().toString().padStart(2, '0')}`,
      titre_document_pdf: "FACTURE",
      objet_facture: data.objet_devis || '',
      nomClient: data.client?.nom || '',
      clientSiret: data.client?.siret || '',
      adresseIntervention: data.client?.adresse || '',
      clientCodePostal: data.client?.code_postal || '',
      clientVille: data.client?.ville || '',
      contactClient: data.client?.telephone || '',
      clientEmail: data.client?.email || '',
      conditions_particulieres: data.conditions_particulieres || "Paiement à réception de la facture.",
      nb_jours_echeance: 30,
      date_echeance: '',
      statut: 'brouillon',
      est_payee: false,
      est_avoir: false,
      lignes: data.lignes ? data.lignes.map((l: any) => ({
        description: l.description,
        quantite: Number(l.quantite),
        prix_unite_ht: Number(l.prix_unite_ht),
        taux_tva: Number(l.taux_tva),
        total_ht: Number(l.total_ht)
      })) : [],
      id_devis: devisId
    }
    
    if (data.client?.id) {
      selectedClientId.value = data.client.id
    }
  } catch (e) {
    console.error('Erreur lors du chargement du devis:', e)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  loadSociete()
  loadClients()
  loadLineDescriptions()
  if (isEditMode.value && factureId.value) {
    await loadExistingFacture(factureId.value)
  } else if (fromDevisId.value) {
    await loadDevisForConversion(fromDevisId.value)
  } else {
    // Ajouter une ligne vide par défaut
    ajouterLigne()
  }
})

// Sauvegarde
async function saveClientToDatabase(): Promise<number | null> {
  if (selectedClientId.value) {
    const c = clients.value.find(cl => cl.id === selectedClientId.value)
    if (c && c.nom === facture.value.nomClient) {
      return selectedClientId.value
    }
  }

  try {
    const clientData = {
      nom: facture.value.nomClient,
      siret: facture.value.clientSiret,
      adresse: facture.value.adresseIntervention,
      code_postal: facture.value.clientCodePostal,
      ville: facture.value.clientVille,
      telephone: facture.value.contactClient,
      email: facture.value.clientEmail
    }
    
    const res = await apiFetch('clients', {
      method: 'POST',
      body: JSON.stringify(clientData)
    })
    
    if (!res.ok) return null
    const data = await res.json()
    return data.id
  } catch (e) {
    console.error('Erreur sauvegarde client:', e)
    return null
  }
}

async function saveFactureToDatabase(clientId: number) {
  const factureData = {
    date_facture: facture.value.date_facture,
    numero_facture: facture.value.numero_facture,
    titre_document_pdf: facture.value.titre_document_pdf,
    objet_facture: facture.value.objet_facture || null,
    id_client: clientId,
    sous_total_ht: parseFloat(formattedSousTotalHt.value),
    total_tva: parseFloat(formattedTotalTva.value),
    total_ttc: parseFloat(formattedTotalTtc.value),
    nb_jours_echeance: facture.value.nb_jours_echeance,
    date_echeance: facture.value.date_echeance || null,
    conditions_particulieres: facture.value.conditions_particulieres || null,
    statut: facture.value.statut,
    est_payee: facture.value.est_payee,
    est_avoir: facture.value.est_avoir,
    id_devis: facture.value.id_devis || null,
    lignes: facture.value.lignes.map(l => ({
      description: l.description,
      quantite: l.quantite,
      prix_unite_ht: l.prix_unite_ht,
      taux_tva: l.taux_tva,
      total_ht: l.total_ht
    }))
  }
  
  const endpoint = isEditMode.value && factureId.value
    ? `factures/${factureId.value}`
    : 'factures'
  
  const method = isEditMode.value ? 'PUT' : 'POST'
  
  const res = await apiFetch(endpoint, {
    method,
    body: JSON.stringify(factureData)
  })
  
  if (!res.ok) {
    throw new Error('Erreur API Facture: ' + await res.text())
  }
  return await res.json()
}

async function saveFacture() {
  if (!isValid.value) {
    alert('Veuillez remplir les informations obligatoires (Date, Numéro, Client, Adresse)')
    return
  }
  
  if (facture.value.lignes.length === 0) {
    alert('Votre facture doit contenir au moins une ligne.')
    return
  }

  isSaving.value = true
  try {
    const clientId = await saveClientToDatabase()
    if (!clientId) throw new Error("Impossible de créer/récupérer le client")
    
    await saveFactureToDatabase(clientId)
    router.push('/app/factures')
  } catch (e: any) {
    alert('Erreur lors de la sauvegarde : ' + e.message)
  } finally {
    isSaving.value = false
  }
}

// PDF Generation
function getReportHTML() {
  const pdfFormatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit', month: '2-digit', year: 'numeric'
    })
  }

  const adresseSociete = [societe.value.adresse, societe.value.code_postal, societe.value.ville]
    .filter(Boolean)
    .join(' ')
    
  const adresseClient = [facture.value.clientCodePostal, facture.value.clientVille]
    .filter(Boolean)
    .join(' ')

  const lignesHtml = facture.value.lignes.map(l => `
    <tr>
      <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">${l.description}</td>
      <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">${l.quantite}</td>
      <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">${l.prix_unite_ht.toFixed(2)} €</td>
      <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">${l.taux_tva}%</td>
      <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">${l.total_ht.toFixed(2)} €</td>
    </tr>
  `).join('')

  return `
    <div style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; padding: 15px; background: white; font-size: 12px;">

      <!-- EN-TÊTE : Logo + Infos société / Client -->
      <div style="display: flex; justify-content: space-between; margin-bottom: 30px;">
        <div style="flex: 1;">
          <div style="margin-bottom: 15px;">
           ${societe.value.logo
              ? `<img src="${societe.value.logo}" style="max-width: 150px; max-height: 80px; object-fit: contain;" />`
              : `<div style="font-size: 24px; font-weight: 800; color: #2563eb;">${societe.value.nom || 'Entreprise'}</div>`
            }
          </div>
          <div style="font-weight: 700; color: #1f2937;">${societe.value.nom}</div>
          <div style="color: #6b7280; font-size: 11px;">${adresseSociete}</div>
          <div style="color: #6b7280; font-size: 11px;">Tél: ${societe.value.telephone || '-'}</div>
          <div style="color: #6b7280; font-size: 11px;">Email: ${societe.value.email || '-'}</div>
          ${societe.value.siret ? `<div style="color: #6b7280; font-size: 10px; margin-top: 5px;">SIRET: ${societe.value.siret}</div>` : ''}
        </div>
        
        <div style="width: 250px; padding: 15px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; height: fit-content;">
          <div style="font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 5px;">Facturé à</div>
          <div style="font-weight: 700; color: #0f172a; font-size: 13px;">${facture.value.nomClient}</div>
          <div style="color: #475569; font-size: 11px; margin-top: 4px;">
            ${facture.value.adresseIntervention}<br/>
            ${adresseClient}
          </div>
          ${facture.value.clientSiret ? `<div style="color: #64748b; font-size: 10px; margin-top: 5px;">SIRET: ${facture.value.clientSiret}</div>` : ''}
          ${facture.value.contactClient ? `<div style="color: #475569; font-size: 11px; margin-top: 5px;">Tél: ${facture.value.contactClient}</div>` : ''}
        </div>
      </div>

      <!-- TITRE FACTURE & INFOS -->
      <div style="margin-bottom: 30px; display: flex; justify-content: space-between; border-bottom: 2px solid #e2e8f0; padding-bottom: 15px;">
        <div>
          <h1 style="color: #0f172a; margin: 0; font-size: 22px; font-weight: 800; letter-spacing: 0.5px;">${facture.value.titre_document_pdf}</h1>
          ${facture.value.objet_facture ? `<div style="color: #475569; font-weight: 600; margin-top: 5px;">Objet : ${facture.value.objet_facture}</div>` : ''}
        </div>
        <div style="text-align: right;">
          <div style="display: flex; justify-content: flex-end; gap: 20px;">
            <div>
              <div style="font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase;">Référence</div>
              <div style="font-weight: 600; color: #0f172a;">${facture.value.numero_facture}</div>
            </div>
            <div>
              <div style="font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase;">Date</div>
              <div style="font-weight: 600; color: #0f172a;">${pdfFormatDate(facture.value.date_facture)}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- TABLEAU DES LIGNES -->
      <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 11px;">
        <thead>
          <tr>
            <th style="padding: 10px; text-align: left; background: #f8fafc; border-bottom: 2px solid #cbd5e1; font-weight: 700; color: #334155; width: 45%;">Description</th>
            <th style="padding: 10px; text-align: right; background: #f8fafc; border-bottom: 2px solid #cbd5e1; font-weight: 700; color: #334155; min-width: 60px;">Qté</th>
            <th style="padding: 10px; text-align: right; background: #f8fafc; border-bottom: 2px solid #cbd5e1; font-weight: 700; color: #334155; min-width: 80px;">Prix U. HT</th>
            <th style="padding: 10px; text-align: right; background: #f8fafc; border-bottom: 2px solid #cbd5e1; font-weight: 700; color: #334155; min-width: 60px;">TVA</th>
            <th style="padding: 10px; text-align: right; background: #f8fafc; border-bottom: 2px solid #cbd5e1; font-weight: 700; color: #334155; min-width: 80px;">Total HT</th>
          </tr>
        </thead>
        <tbody>
          ${lignesHtml}
        </tbody>
      </table>

      <!-- ENCART DES TOTAUX -->
      <div style="display: flex; justify-content: flex-end; margin-bottom: 40px; page-break-inside: avoid;">
        <div style="width: 250px; background: #f8fafc; border-radius: 6px; padding: 15px;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #475569; font-weight: 600;">Total HT</span>
            <span style="font-weight: 600;">${formattedSousTotalHt.value} €</span>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <span style="color: #475569; font-weight: 600;">Total TVA</span>
            <span style="font-weight: 600;">${formattedTotalTva.value} €</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding-top: 12px; border-top: 1px solid #cbd5e1;">
            <span style="color: #0f172a; font-weight: 800; font-size: 14px;">Net à Payer (TTC)</span>
            <span style="color: #2563eb; font-weight: 800; font-size: 14px;">${formattedTotalTtc.value} €</span>
          </div>
        </div>
      </div>

      <!-- PIED DE PAGE : Échéance & Conditions -->
      <div style="margin-top: auto; page-break-inside: avoid;">
        <div style="margin-bottom: 10px;">
          <strong style="color: #0f172a; font-size: 11px;">Conditions particulières et informations :</strong>
          <div style="font-size: 10px; color: #475569; line-height: 1.4; white-space: pre-wrap;">${facture.value.conditions_particulieres}</div>
        </div>
        ${facture.value.date_echeance ? `<div style="font-size: 10px; color: #475569; font-weight: 600;">Date d'échéance : ${pdfFormatDate(facture.value.date_echeance)} (${facture.value.nb_jours_echeance} jours)</div>` : ''}
      </div>
    </div>`
}

function openPreview() {
  previewHTML.value = getReportHTML()
  showPDFModal.value = true
}

function closePDFModal() {
  showPDFModal.value = false
  previewHTML.value = ''
}

async function saveAndGeneratePDF() {
  if (!isValid.value) {
    alert('Veuillez remplir les champs obligatoires.')
    return
  }

  isGeneratingPDF.value = true
  try {
    const clientId = await saveClientToDatabase()
    if (!clientId) throw new Error("Impossible de créer le client")
    
    const saved = await saveFactureToDatabase(clientId)
    facture.value.id = saved.id
    facture.value.numero_facture = saved.numero_facture
    
    const footerText = societe.value.texte_pied_page || ''
    const container = document.createElement('div')
    container.innerHTML = getReportHTML()

    document.body.appendChild(container)

    const filename = (facture.value.titre_document_pdf + '_' + facture.value.numero_facture).replace(/[^a-zA-Z0-9_-]/g, '')

    const { default: html2pdf } = await import('html2pdf.js')

    const worker = html2pdf()
      .set({
        margin: [25, 25, footerText ? 35 : 25, 25],
        filename: `${filename}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
      } as any)
      .from(container)
      .toPdf()

    const pdf: any = await worker.get('pdf')
    if (pdf) {
      const totalPages = pdf.internal.getNumberOfPages()
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()

      for (let i = 1; i <= totalPages; i++) {
        pdf.setPage(i)
        
        // 1. Ligne de séparation élégante (Bleu Primaire #2563eb)
        pdf.setDrawColor(37, 99, 235)
        pdf.setLineWidth(0.4)
        pdf.line(25, pageHeight - 20, pageWidth - 25, pageHeight - 20)

        // 2. Informations société (Centrées)
        if (footerText) {
          pdf.setFontSize(7)
          pdf.setTextColor(107, 114, 128) // COLOR_GRAY
          const lines = pdf.splitTextToSize(footerText, pageWidth - 60)
          const startY = pageHeight - 15
          lines.forEach((line: string, idx: number) => {
            pdf.text(line, pageWidth / 2, startY + (idx * 3.5), { align: 'center' })
          })
        }

        // 3. Numérotation de page (Bas Droite)
        pdf.setFontSize(8)
        pdf.setTextColor(37, 99, 235) // COLOR_PRIMARY
        pdf.setFont('helvetica', 'bold')
        pdf.text(`Page ${i} / ${totalPages}`, pageWidth - 25, pageHeight - 10, { align: 'right' })

        // 4. Petit branding (Bas Gauche)
        pdf.setFontSize(6)
        pdf.setTextColor(156, 163, 175) // COLOR_LIGHT_MUTED
        pdf.setFont('helvetica', 'italic')
        pdf.text("Généré via Ventura", 25, pageHeight - 10)
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
    
    router.push('/app/factures')
  } catch (e: any) {
    console.error(e)
    alert('Erreur lors de la génération PDF : ' + e.message)
  } finally {
    isGeneratingPDF.value = false
  }
}
async function downloadFacturX() {
  if (!factureId.value || isDownloadingFacturX.value) return
  
  isDownloadingFacturX.value = true
  
  try {
    const res = await apiFetch(`factures/${factureId.value}/facturx`)
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Erreur inconnue' }))
      alert(`Erreur : ${errorData.detail || 'Impossible de générer le Factur-X'}`)
      return
    }
    
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `FacturX_${facture.value.numero_facture}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Erreur lors du téléchargement Factur-X', e)
    alert('Erreur réseau lors du téléchargement du Factur-X')
  } finally {
    isDownloadingFacturX.value = false
  }
}
</script>

<template>
  <div ref="mainContainer" class="max-w-4xl mx-auto pb-20">
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20 gap-4">
      <Loader2 class="w-8 h-8 text-primary animate-spin" />
      <span class="text-muted-foreground font-medium">Chargement de la facture...</span>
    </div>

    <div v-else class="space-y-6">
      <!-- Header -->
      <div class="sticky top-0 bg-background/95 backdrop-blur z-20 border-b pt-safe px-4 -mx-4 mb-6">
        <!-- Première ligne : Retour + Actions Primaires -->
        <div class="flex items-center justify-between py-3">
          <button
            @click="router.push('/app/factures')"
            class="inline-flex items-center gap-1.5 text-foreground font-semibold transition-colors"
          >
            <ArrowLeft class="w-5 h-5" />
            Retour
          </button>
          
          <div class="flex items-center gap-2">
            <!-- Toujours visible : Aperçu -->
            <button
              @click="openPreview"
              :disabled="isSaving || isGeneratingPDF"
              class="inline-flex items-center gap-2 px-3 py-2 bg-background text-foreground border border-border rounded-lg font-medium hover:bg-muted transition-colors disabled:opacity-50"
              title="Aperçu PDF"
            >
              <Eye class="w-5 h-5" />
              <span class="hidden sm:inline">Aperçu</span>
            </button>

            <!-- Toujours visible : Sauvegarder (si non verrouillé) -->
            <button
              v-if="!isLocked"
              @click="saveFacture"
              :disabled="isSaving || isGeneratingPDF"
              class="inline-flex items-center gap-2 px-3 py-2 bg-background text-foreground border border-border rounded-lg font-medium hover:bg-muted transition-colors disabled:opacity-50"
              title="Sauvegarder Brouillon"
            >
              <Loader2 v-if="isSaving" class="w-5 h-5 animate-spin" />
              <Save v-else class="w-5 h-5" />
              <span class="hidden sm:inline">Sauvegarder</span>
            </button>

            <!-- Toujours visible : Sauvegarder & PDF -->
            <button
              @click="saveAndGeneratePDF"
              :disabled="isSaving || isGeneratingPDF"
              class="inline-flex items-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors shadow-sm disabled:opacity-50"
            >
              <Loader2 v-if="isGeneratingPDF" class="w-5 h-5 animate-spin" />
              <FileDown v-else class="w-5 h-5" />
              <span class="hidden sm:inline">Enreg. & PDF</span>
              <span class="sm:hidden">PDF</span>
            </button>

            <!-- Desktop only : Actions spécifiques sur la même ligne -->
            <div class="hidden sm:flex items-center gap-2 ml-2 pl-2 border-l border-border">
              <template v-if="isLocked">
                <button @click="togglePayment" :disabled="isUpdatingPayment" class="inline-flex items-center gap-2 px-3 py-2 rounded-lg font-medium border shadow-sm" :class="facture.est_payee ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200'">
                  <CreditCard class="w-5 h-5" />
                  <span>{{ facture.est_payee ? 'Payée' : 'Payer' }}</span>
                </button>
                <button v-if="!facture.est_avoir" @click="creerAvoir" :disabled="isCreatingAvoir" class="inline-flex items-center gap-2 px-3 py-2 bg-purple-50 text-purple-700 border border-purple-200 rounded-lg font-medium">
                  <Undo2 class="w-5 h-5" />
                  <span>Avoir</span>
                </button>
                <button v-if="isNative" @click="shareFacture" :disabled="isDownloadingFacturX" class="inline-flex items-center gap-2 px-3 py-2 bg-teal-50 text-teal-700 border border-teal-200 rounded-lg font-medium">
                  <Share2 class="w-5 h-5" />
                  <span>Partager</span>
                </button>
              </template>
              <template v-else>
                <button @click="requestValidation" :disabled="isSaving || isGeneratingPDF" class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 shadow-sm">
                  <CheckCircle2 class="w-5 h-5" />
                  <span>Valider</span>
                </button>
              </template>
            </div>
          </div>
        </div>

        <!-- Deuxième ligne (Mobile uniquement) : Actions Spécifiques -->
        <div class="flex sm:hidden items-center gap-2 pb-3 overflow-x-auto no-scrollbar">
          <template v-if="isLocked">
            <button
              @click="togglePayment"
              :disabled="isUpdatingPayment"
              class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 rounded-lg font-medium border shadow-sm whitespace-nowrap"
              :class="facture.est_payee 
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                : 'bg-amber-50 text-amber-700 border-amber-200'"
            >
              <CreditCard class="w-4 h-4" />
              <span class="text-xs">{{ facture.est_payee ? 'Payée' : 'Payer' }}</span>
            </button>

            <button
              v-if="!facture.est_avoir"
              @click="creerAvoir"
              :disabled="isCreatingAvoir"
              class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 bg-purple-50 text-purple-700 border border-purple-200 rounded-lg font-medium whitespace-nowrap"
            >
              <Undo2 class="w-4 h-4" />
              <span class="text-xs">Avoir</span>
            </button>

            <button
              v-if="isNative"
              @click="shareFacture"
              :disabled="isDownloadingFacturX"
              class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 bg-teal-50 text-teal-700 border border-teal-200 rounded-lg font-medium whitespace-nowrap"
            >
              <Share2 class="w-4 h-4" />
              <span class="text-xs">Partager</span>
            </button>

            <button
              @click="downloadFacturX"
              :disabled="isDownloadingFacturX"
              class="inline-flex items-center justify-center p-2 bg-background text-foreground border border-border rounded-lg"
            >
              <FileCheck2 class="w-4 h-4" />
            </button>
          </template>

          <template v-else>
            <button
              @click="requestValidation"
              :disabled="isSaving || isGeneratingPDF"
              class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-green-600 text-white rounded-lg font-bold shadow-sm"
            >
              <CheckCircle2 class="w-5 h-5" />
              <span>Valider la facture</span>
            </button>
          </template>
        </div>
      </div>

      <h1 class="text-2xl font-bold text-foreground mb-4">
        <template v-if="isEditMode">
          <template v-if="isLocked">{{ facture.est_avoir ? 'Avoir' : 'Facture' }} <span class="text-muted-foreground font-normal text-lg">(lecture seule)</span></template>
          <template v-else>{{ facture.est_avoir ? "Modifier l'Avoir" : 'Modifier la Facture' }}</template>
        </template>
        <template v-else>
          <template v-if="fromDevisId">Facturer le Devis</template>
          <template v-else>{{ facture.est_avoir ? 'Nouvel Avoir' : 'Nouvelle Facture' }}</template>
        </template>
      </h1>

      <!-- Locked banner -->
      <div v-if="isLocked" class="flex items-center gap-3 px-4 py-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl mb-4">
        <Lock class="w-5 h-5 flex-shrink-0" />
        <div>
          <p class="text-sm font-semibold">Facture validée — modification impossible</p>
          <p class="text-xs text-amber-600">Cette facture est verrouillée. Vous pouvez générer le PDF ou télécharger le Factur-X.</p>
        </div>
      </div>

      <!-- Devis source badge -->
      <div v-if="facture.id_devis" class="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-50 border border-blue-200 text-blue-700 rounded-lg text-sm font-medium mb-2">
        <FileDown class="w-4 h-4" />
        Générée depuis le devis #{{ facture.id_devis }}
      </div>

      <div class="space-y-6">
        <!-- Informations Générales -->
        <section class="bg-card border border-border rounded-xl p-6">
          <h3 class="text-lg font-semibold text-foreground mb-4">Informations du document</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Date de la facture <span class="text-destructive">*</span></label>
              <input type="date" v-model="facture.date_facture" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" required />
            </div>
            <div>
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-1.5">
                <label class="block text-sm font-medium text-foreground">Numéro de facture <span class="text-destructive">*</span></label>
                <div class="flex items-center bg-muted rounded-lg p-1">
                  <button 
                    @click="facture.statut = 'brouillon'"
                    type="button"
                    :disabled="isLocked"
                    :class="[
                      'px-3 py-1.5 text-xs font-medium rounded-md transition-all',
                      facture.statut === 'brouillon' 
                        ? 'bg-primary text-primary-foreground shadow-sm' 
                        : 'text-muted-foreground hover:text-foreground',
                      isLocked ? 'opacity-50 cursor-not-allowed' : ''
                    ]"
                  >
                    Brouillon
                  </button>
                  <button 
                    @click="isLocked ? null : (facture.statut === 'validée' ? null : requestValidation())"
                    type="button"
                    :class="[
                      'px-3 py-1.5 text-xs font-medium rounded-md transition-all',
                      facture.statut === 'validée' 
                        ? 'bg-green-600 text-white shadow-sm' 
                        : 'text-muted-foreground hover:text-foreground hover:bg-background/50',
                      isLocked ? 'opacity-50 cursor-not-allowed' : ''
                    ]"
                  >
                    Validée
                  </button>
                </div>
              </div>
              <input type="text" v-model="facture.numero_facture" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" placeholder="Ex: FAC-2023001" required />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Titre du PDF <span class="text-destructive">*</span></label>
              <input type="text" v-model="facture.titre_document_pdf" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" placeholder="FACTURE" required />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Objet de la facture</label>
              <input type="text" v-model="facture.objet_facture" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" placeholder="Ex: Rénovation salle de bain" />
            </div>
          </div>
        </section>

        <!-- Informations Client -->
        <section class="bg-card border border-border rounded-xl p-6">
          <h3 class="text-lg font-semibold text-foreground mb-4">Informations Client</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <!-- Autocomplete Field -->
            <div class="relative">
              <label class="block text-sm font-medium text-foreground mb-1.5">Nom du client <span class="text-destructive">*</span></label>
              <input 
                type="text" 
                v-model="facture.nomClient" 
                @focus="showSuggestions = true"
                @blur="handleBlur"
                @keydown="handleKeyDown"
                :disabled="isLocked"
                class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" 
                placeholder="Rechercher ou saisir un nom..."
                required
              />
              <div v-if="showSuggestions && filteredClients.length > 0" class="absolute z-50 w-full mt-1 bg-card border border-border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                <ul class="py-1">
                  <li
                    v-for="(c, idx) in filteredClients"
                    :key="c.id"
                    @mousedown.prevent="selectClient(c)"
                    class="px-4 py-2 cursor-pointer transition-colors"
                    :class="idx === focusedIndex ? 'bg-primary/10 text-primary font-medium' : 'text-foreground hover:bg-muted'"
                  >
                    <div class="font-medium">{{ c.nom }}</div>
                    <div v-if="c.ville || c.telephone" class="text-xs text-muted-foreground">{{ [c.ville, c.telephone].filter(Boolean).join(' • ') }}</div>
                  </li>
                </ul>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">SIRET client</label>
              <input type="text" v-model="facture.clientSiret" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-sm font-medium text-foreground mb-1.5">Adresse <span class="text-destructive">*</span></label>
              <input type="text" v-model="facture.adresseIntervention" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" required />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Code Postal</label>
              <input type="text" v-model="facture.clientCodePostal" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Ville</label>
              <input type="text" v-model="facture.clientVille" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Téléphone</label>
              <input type="tel" v-model="facture.contactClient" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Email</label>
              <input type="email" v-model="facture.clientEmail" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
          </div>
        </section>

        <!-- Lignes de la facture -->
        <section class="bg-card border border-border rounded-xl p-6">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <h3 class="text-lg font-semibold text-foreground">Détail de la facture <span class="text-destructive">*</span></h3>
              <p class="text-sm text-muted-foreground">Ajoutez les prestations ou produits à facturer</p>
            </div>
            <button v-if="!isLocked" @click="ajouterLigne" class="inline-flex items-center gap-1.5 text-sm font-medium bg-primary/10 text-primary hover:bg-primary/20 px-3 py-1.5 rounded-lg transition-colors">
              <Plus class="w-4 h-4" /> Ajouter une ligne
            </button>
          </div>
          
          <div class="space-y-4 mb-8">
            <div v-for="(ligne, idx) in facture.lignes" :key="idx" class="bg-background border border-border rounded-xl p-4 sm:p-5 transition-all shadow-sm hover:shadow-md hover:border-primary/30">
              <div class="flex flex-col sm:flex-row gap-4 items-end">
                <div class="flex-1 w-full relative">
                  <label class="block text-xs font-semibold text-muted-foreground uppercase mb-2">Description</label>
                  <input type="text" v-model="ligne.description" 
                    @focus="activeLineIndex = idx; focusedLineIndex = -1" 
                    @blur="handleLineBlur" 
                    @keydown="handleLineKeyDown($event, idx)"
                    :disabled="isLocked"
                    class="w-full px-3 py-2 bg-background border border-input rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none text-foreground disabled:opacity-50 disabled:cursor-not-allowed" 
                    placeholder="Ex: Main d'œuvre" required autocomplete="off" />
                  <div v-if="activeLineIndex === idx && lineSuggestions.length > 0" class="absolute z-50 w-full mt-1 bg-card border border-border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                    <ul class="py-1">
                      <li v-for="(d, dIdx) in lineSuggestions" :key="d.id" @mousedown.prevent="selectDescription(idx, d)" 
                        class="px-4 py-2 cursor-pointer text-sm transition-colors flex justify-between items-center group"
                        :class="dIdx === focusedLineIndex ? 'bg-primary/10 text-primary font-medium' : 'text-foreground hover:bg-muted'"
                      >
                        <span class="font-medium">{{ d.description }}</span>
                        <span class="text-xs text-muted-foreground group-hover:text-primary transition-colors opacity-0 sm:opacity-100">{{ Number(d.prix_unite_ht).toFixed(2) }}€ (TVA {{ Number(d.taux_tva) }}%)</span>
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="w-full sm:w-24">
                  <label class="block text-xs font-semibold text-muted-foreground uppercase mb-2">Qté</label>
                  <input type="number" v-model="ligne.quantite" @input="updateLigneTotal(ligne)" min="0" step="0.5" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none text-foreground disabled:opacity-50 disabled:cursor-not-allowed" required />
                </div>
                <div class="w-full sm:w-32">
                  <label class="block text-xs font-semibold text-muted-foreground uppercase mb-2">Prix U. HT</label>
                  <div class="relative">
                    <input type="number" v-model="ligne.prix_unite_ht" @input="updateLigneTotal(ligne)" min="0" step="0.01" :disabled="isLocked" class="w-full px-3 py-2 pr-8 bg-background border border-input rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none text-foreground disabled:opacity-50 disabled:cursor-not-allowed" required />
                    <span class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm font-medium">€</span>
                  </div>
                </div>
                <div class="w-full sm:w-28">
                  <label class="block text-xs font-semibold text-muted-foreground uppercase mb-2">TVA</label>
                  <select v-model="ligne.taux_tva" @change="updateLigneTotal(ligne)" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none text-foreground disabled:opacity-50 disabled:cursor-not-allowed">
                    <option v-for="t in TAUX_TVA" :key="t" :value="t">{{ t }}%</option>
                  </select>
                </div>
                <div class="w-full sm:w-32">
                  <label class="block text-xs font-semibold text-muted-foreground uppercase mb-2">Total HT</label>
                  <div class="px-3 py-2 bg-muted border border-border rounded-lg text-sm font-medium text-foreground text-right w-full">
                    {{ ligne.total_ht.toFixed(2) }} €
                  </div>
                </div>
                <button @click="supprimerLigne(idx)" v-if="facture.lignes.length > 1 && !isLocked" class="p-2.5 text-muted-foreground hover:bg-destructive shadow-sm border border-border hover:border-destructive hover:text-white rounded-lg flex-shrink-0 transition-all" title="Supprimer la ligne">
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div v-if="facture.lignes.length === 0" class="text-center py-8 bg-muted/20 border border-border border-dashed rounded-lg">
              <p class="text-sm text-muted-foreground mb-3">Aucune ligne dans cette facture.</p>
              <button @click="ajouterLigne" class="inline-flex items-center justify-center bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90">
                <Plus class="w-4 h-4 mr-2" /> Ajouter la première ligne
              </button>
            </div>
          </div>

          <!-- Totaux -->
          <div class="flex justify-end pt-6 border-t border-border">
            <div class="w-full max-w-sm bg-muted/30 border border-border rounded-xl p-5 shadow-sm">
              <div class="flex justify-between items-center mb-3 text-sm">
                <span class="text-muted-foreground font-medium">Total HT</span>
                <span class="font-semibold text-foreground">{{ formattedSousTotalHt }} €</span>
              </div>
              <div class="flex justify-between items-center mb-4 text-sm">
                <span class="text-muted-foreground font-medium">Total TVA</span>
                <span class="font-semibold text-foreground">{{ formattedTotalTva }} €</span>
              </div>
              <div class="flex justify-between items-center pt-4 border-t border-border">
                <span class="font-bold text-foreground">Total TTC</span>
                <span class="text-xl font-bold text-primary">{{ formattedTotalTtc }} €</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Paramètres annexes -->
        <section class="bg-card border border-border rounded-xl p-6">
          <h3 class="text-lg font-semibold text-foreground mb-4">Échéance et Conditions</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Échéance (jours)</label>
              <input type="number" v-model="facture.nb_jours_echeance" min="0" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Date d'échéance</label>
              <input type="date" v-model="facture.date_echeance" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <div class="flex items-end">
              <label class="inline-flex items-center gap-3 cursor-pointer select-none">
                <input type="checkbox" v-model="facture.est_payee" :disabled="isLocked" class="w-5 h-5 rounded border-border text-primary focus:ring-primary" />
                <span class="text-sm font-medium text-foreground">Facture payée</span>
              </label>
            </div>
            <div class="md:col-span-3">
              <label class="block text-sm font-medium text-foreground mb-1.5">Conditions particulières</label>
              <textarea v-model="facture.conditions_particulieres" rows="3" :disabled="isLocked" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none resize-y text-sm disabled:opacity-50 disabled:cursor-not-allowed"></textarea>
            </div>
          </div>
        </section>

      </div>
    </div>
  </div>

  <!-- PDF Preview Modal -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="showPDFModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6" @click.self="closePDFModal">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/70 backdrop-blur-md"></div>

        <!-- Modal card -->
        <div class="relative w-full max-w-5xl h-[90vh] bg-card border border-border rounded-2xl shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in duration-300">
          
          <!-- Header -->
          <div class="px-6 py-4 border-b border-border flex items-center justify-between bg-muted/30">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <FileDown class="w-4 h-4 text-primary" />
              </div>
              <div>
                <h2 class="text-sm font-bold text-foreground">Aperçu de la Facture</h2>
                <p class="text-[10px] text-muted-foreground">{{ facture.titre_document_pdf }} • {{ facture.numero_facture }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <a 
                :href="pdfUrl" 
                :download="`${facture.titre_document_pdf.replace(/\s+/g, '_')}_${facture.numero_facture}.pdf`"
                class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors"
                v-if="pdfUrl"
              >
                <FileDown class="w-4 h-4" />
                <span class="hidden sm:inline">Télécharger</span>
              </a>
              <button
                @click="closePDFModal"
                class="p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- Content (Viewer) -->
          <div class="flex-1 bg-muted/20 relative overflow-y-auto overflow-x-hidden p-4 sm:p-8 flex justify-center pdf-preview-container">
            <div 
              v-if="previewHTML" 
              class="max-w-[210mm] bg-white shadow-xl min-h-[297mm] h-fit p-[15mm] pdf-preview-content"
              v-html="previewHTML"
            ></div>
            <div v-else class="absolute inset-0 flex flex-col items-center justify-center gap-4">
              <Loader2 class="w-10 h-10 text-primary animate-spin" />
              <p class="text-sm text-muted-foreground">Chargement du document...</p>
            </div>
          </div>

          <!-- Mobile Footer -->
          <div class="p-4 border-t border-border bg-card">
            <div class="max-w-xs mx-auto space-y-2">
              <p class="text-[10px] text-muted-foreground text-center">
                Ceci est un aperçu interactif. Pour obtenir le fichier final :
              </p>
              <button 
                @click="saveAndGeneratePDF"
                class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
                :disabled="!isValid || isGeneratingPDF"
              >
                <Loader2 v-if="isGeneratingPDF" class="w-5 h-5 animate-spin" />
                <FileDown v-else class="w-5 h-5" />
                Générer et sauvegarder le PDF final
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- Validate Confirmation Modal -->
  <Teleport to="body">
    <Transition name="modal-fade">
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
            >
              Annuler
            </button>
            <button 
              @click="confirmValidation" 
              class="px-4 py-2 text-sm font-medium bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
            >
              Valider définitivement
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Modal transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-active .relative,
.modal-fade-leave-active .relative {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.modal-fade-enter-from .relative {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}

/* PDF Preview Scaling for Mobile */
@media (max-width: 768px) {
  .pdf-preview-container {
    padding: 1rem 0.5rem !important;
    display: block !important;
    overflow-x: hidden;
  }
  
  .pdf-preview-content {
    transform: scale(0.42);
    transform-origin: top center;
    width: 210mm !important;
    min-width: 210mm !important;
    position: relative;
    left: 50%;
    margin-left: -105mm;
    margin-bottom: -160mm !important;
  }
}

@media (max-width: 480px) {
  .pdf-preview-content {
    transform: scale(0.35);
    margin-bottom: -180mm !important;
  }
}
</style>
