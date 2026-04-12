<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { API_BASE_URL } from '@/lib/api'
import { ArrowLeft, Save, FileDown, Plus, Trash2, Loader2 } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const isSaving = ref(false)
const isGeneratingPDF = ref(false)
const isLoading = ref(false)

// Mode édition
const isEditMode = computed(() => !!route.params.id)
const devisId = computed(() => route.params.id ? Number(route.params.id) : null)

// interface Client {
//   id?: number
//   nom: string
// }

interface LigneDevis {
  id?: number
  description: string
  quantite: number
  prix_unite_ht: number
  taux_tva: number
  total_ht: number
}

interface DevisForm {
  id?: number
  date_devis: string
  numero_devis: string
  titre_document_pdf: string
  objet_devis: string
  nomClient: string
  clientSiret: string
  adresseIntervention: string
  clientCodePostal: string
  clientVille: string
  contactClient: string
  clientEmail: string
  conditions_particulieres: string
  nb_jours_validite: number
  statut: string
  lignes: LigneDevis[]
}

const devis = ref<DevisForm>({
  date_devis: new Date().toISOString().split('T')[0],
  numero_devis: `DEV-${new Date().toISOString().split('T')[0].replace(/-/g, '')}`,
  titre_document_pdf: "DEVIS",
  objet_devis: '',
  nomClient: '',
  clientSiret: '',
  adresseIntervention: '',
  clientCodePostal: '',
  clientVille: '',
  contactClient: '',
  clientEmail: '',
  conditions_particulieres: "Paiement à réception de la facture. Acompte de 30% à la commande.",
  nb_jours_validite: 30,
  statut: 'brouillon',
  lignes: []
})

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
  const query = devis.value.nomClient.toLowerCase().trim()
  if (!query || query.length < 1) return []
  return clients.value.filter(c => 
    c.nom.toLowerCase().includes(query) || 
    (c.ville && c.ville.toLowerCase().includes(query))
  ).slice(0, 8)
})

function selectClient(c: any) {
  devis.value.nomClient = c.nom
  devis.value.clientSiret = c.siret || ''
  devis.value.adresseIntervention = c.adresse || ''
  devis.value.clientCodePostal = c.code_postal || ''
  devis.value.clientVille = c.ville || ''
  devis.value.contactClient = c.telephone || ''
  devis.value.clientEmail = c.email || ''
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

// Calculs du devis
const TAUX_TVA = [0, 2.1, 5.5, 10, 20]

function ajouterLigne() {
  devis.value.lignes.push({
    description: '',
    quantite: 1,
    prix_unite_ht: 0,
    taux_tva: 20,
    total_ht: 0
  })
}

function supprimerLigne(index: number) {
  devis.value.lignes.splice(index, 1)
}

function updateLigneTotal(ligne: LigneDevis) {
  ligne.total_ht = Number((ligne.quantite * ligne.prix_unite_ht).toFixed(2))
}

const sous_total_ht = computed(() => {
  return devis.value.lignes.reduce((sum, ligne) => sum + ligne.total_ht, 0)
})

const total_tva = computed(() => {
  return devis.value.lignes.reduce((sum, ligne) => {
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
  return devis.value.date_devis && devis.value.numero_devis && devis.value.nomClient.trim() && devis.value.adresseIntervention.trim()
})

const pastDescriptions = ref<string[]>([])
const activeLineIndex = ref<number | null>(null)

function getFilteredDescriptions(query: string) {
  if (!query || query.trim().length < 1) return []
  const lowerQuery = query.toLowerCase().trim()
  return pastDescriptions.value.filter(d => d.toLowerCase().includes(lowerQuery)).slice(0, 8)
}

function selectDescription(idx: number, desc: string) {
  devis.value.lignes[idx].description = desc
  activeLineIndex.value = null
}

function handleLineBlur() {
  setTimeout(() => {
    activeLineIndex.value = null
  }, 200)
}

// Chargement des données
async function loadLineDescriptions() {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/devis/lignes/descriptions`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      pastDescriptions.value = await res.json()
    }
  } catch (e) {
    console.error('Erreur lors du chargement des descriptions:', e)
  }
}

async function loadClients() {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/clients`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      clients.value = await res.json()
    }
  } catch (e) {
    console.error('Erreur lors du chargement des clients:', e)
  }
}

async function loadSociete() {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/societes/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      const data = await res.json()
      societe.value = data
    }
  } catch (e) {
    console.error('Erreur lors du chargement de la société:', e)
  }
}

async function loadExistingDevis(id: number) {
  isLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/devis/${id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) {
      alert('Devis introuvable')
      router.push('/app/devis')
      return
    }
    const data = await res.json()
    
    devis.value = {
      id: data.id,
      date_devis: data.date_devis,
      numero_devis: data.numero_devis,
      titre_document_pdf: data.titre_document_pdf || "DEVIS",
      objet_devis: data.objet_devis || '',
      nomClient: data.client?.nom || '',
      clientSiret: data.client?.siret || '',
      adresseIntervention: data.client?.adresse || '',
      clientCodePostal: data.client?.code_postal || '',
      clientVille: data.client?.ville || '',
      contactClient: data.client?.telephone || '',
      clientEmail: data.client?.email || '',
      conditions_particulieres: data.conditions_particulieres || '',
      nb_jours_validite: data.nb_jours_validite || 30,
      statut: data.statut || 'brouillon',
      lignes: data.lignes ? data.lignes.map((l: any) => ({
        id: l.id,
        description: l.description,
        quantite: Number(l.quantite),
        prix_unite_ht: Number(l.prix_unite_ht),
        taux_tva: Number(l.taux_tva),
        total_ht: Number(l.total_ht)
      })) : []
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
  if (isEditMode.value && devisId.value) {
    await loadExistingDevis(devisId.value)
  } else {
    // Ajouter une ligne vide par défaut pour un nouveau devis
    ajouterLigne()
  }
})

// Sauvegarde
async function saveClientToDatabase(): Promise<number | null> {
  if (selectedClientId.value) {
    const c = clients.value.find(cl => cl.id === selectedClientId.value)
    if (c && c.nom === devis.value.nomClient) {
      return selectedClientId.value
    }
  }

  try {
    const token = localStorage.getItem('token')
    const clientData = {
      nom: devis.value.nomClient,
      siret: devis.value.clientSiret,
      adresse: devis.value.adresseIntervention,
      code_postal: devis.value.clientCodePostal,
      ville: devis.value.clientVille,
      telephone: devis.value.contactClient,
      email: devis.value.clientEmail
    }
    
    const res = await fetch(`${API_BASE_URL}/api/clients`, {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
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

async function saveDevisToDatabase(clientId: number) {
  const token = localStorage.getItem('token')
  const devisData = {
    date_devis: devis.value.date_devis,
    numero_devis: devis.value.numero_devis,
    titre_document_pdf: devis.value.titre_document_pdf,
    objet_devis: devis.value.objet_devis || null,
    id_client: clientId,
    sous_total_ht: parseFloat(formattedSousTotalHt.value),
    total_tva: parseFloat(formattedTotalTva.value),
    total_ttc: parseFloat(formattedTotalTtc.value),
    nb_jours_validite: devis.value.nb_jours_validite,
    conditions_particulieres: devis.value.conditions_particulieres || null,
    statut: devis.value.statut,
    lignes: devis.value.lignes.map(l => ({
      description: l.description,
      quantite: l.quantite,
      prix_unite_ht: l.prix_unite_ht,
      taux_tva: l.taux_tva,
      total_ht: l.total_ht
    }))
  }
  
  const url = isEditMode.value && devisId.value
    ? `${API_BASE_URL}/api/devis/${devisId.value}`
    : `${API_BASE_URL}/api/devis`
  
  const method = isEditMode.value ? 'PUT' : 'POST'
  
  const res = await fetch(url, {
    method,
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(devisData)
  })
  
  if (!res.ok) {
    throw new Error('Erreur API Devis: ' + await res.text())
  }
  return await res.json()
}

async function saveDevis() {
  if (!isValid.value) {
    alert('Veuillez remplir les informations obligatoires (Date, Numéro, Client, Adresse)')
    return
  }
  
  if (devis.value.lignes.length === 0) {
    alert('Votre devis doit contenir au moins une ligne.')
    return
  }

  isSaving.value = true
  try {
    const clientId = await saveClientToDatabase()
    if (!clientId) throw new Error("Impossible de créer/récupérer le client")
    
    await saveDevisToDatabase(clientId)
    router.push('/app/devis')
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
    
  const adresseClient = [devis.value.clientCodePostal, devis.value.clientVille]
    .filter(Boolean)
    .join(' ')

  const lignesHtml = devis.value.lignes.map(l => `
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
          <div style="font-weight: 700; color: #0f172a; font-size: 13px;">${devis.value.nomClient}</div>
          <div style="color: #475569; font-size: 11px; margin-top: 4px;">
            ${devis.value.adresseIntervention}<br/>
            ${adresseClient}
          </div>
          ${devis.value.clientSiret ? `<div style="color: #64748b; font-size: 10px; margin-top: 5px;">SIRET: ${devis.value.clientSiret}</div>` : ''}
          ${devis.value.contactClient ? `<div style="color: #475569; font-size: 11px; margin-top: 5px;">Tél: ${devis.value.contactClient}</div>` : ''}
        </div>
      </div>

      <!-- TITRE FACTURE/DEVIS & INFOS -->
      <div style="margin-bottom: 30px; display: flex; justify-content: space-between; border-bottom: 2px solid #e2e8f0; padding-bottom: 15px;">
        <div>
          <h1 style="color: #0f172a; margin: 0; font-size: 22px; font-weight: 800; letter-spacing: 0.5px;">${devis.value.titre_document_pdf}</h1>
          ${devis.value.objet_devis ? `<div style="color: #475569; font-weight: 600; margin-top: 5px;">Objet : ${devis.value.objet_devis}</div>` : ''}
        </div>
        <div style="text-align: right;">
          <div style="display: flex; justify-content: flex-end; gap: 20px;">
            <div>
              <div style="font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase;">Référence</div>
              <div style="font-weight: 600; color: #0f172a;">${devis.value.numero_devis}</div>
            </div>
            <div>
              <div style="font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase;">Date</div>
              <div style="font-weight: 600; color: #0f172a;">${pdfFormatDate(devis.value.date_devis)}</div>
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

      <!-- PIED DE PAGE : Validité & Conditions -->
      <div style="margin-top: auto; page-break-inside: avoid;">
        <div style="margin-bottom: 10px;">
          <strong style="color: #0f172a; font-size: 11px;">Conditions particulières et informations :</strong>
          <div style="font-size: 10px; color: #475569; line-height: 1.4; white-space: pre-wrap;">${devis.value.conditions_particulieres}</div>
        </div>
        <div style="font-size: 10px; color: #475569; font-weight: 600;">Valable jusqu'au : ${pdfFormatDate(new Date(new Date(devis.value.date_devis).getTime() + devis.value.nb_jours_validite * 24 * 60 * 60 * 1000).toISOString())} (${devis.value.nb_jours_validite} jours)</div>
      </div>
    </div>`
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
    
    // On sauvegarde d'abord
    const saved = await saveDevisToDatabase(clientId)
    devis.value.id = saved.id
    devis.value.numero_devis = saved.numero_devis // S'assurer qu'on utilise le numéro finalisé
    
    const footerText = societe.value.texte_pied_page || ''
    const container = document.createElement('div')
    container.innerHTML = getReportHTML()

    document.body.appendChild(container)

    const filename = (devis.value.titre_document_pdf + '_' + devis.value.numero_devis).replace(/[^a-zA-Z0-9_-]/g, '')

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

    const pdf: any = await worker.get('pdf')
    if (footerText && pdf) {
      const totalPages = pdf.internal.getNumberOfPages()
      const pageWidth = pdf.internal.pageSize.getWidth()
      for (let i = 1; i <= totalPages; i++) {
        pdf.setPage(i)
        pdf.setFontSize(8)
        pdf.setTextColor(107, 114, 128)
        const lines = pdf.splitTextToSize(footerText, pageWidth - 30)
        const startY = pdf.internal.pageSize.getHeight() - 15
        lines.forEach((line: string, idx: number) => {
          pdf.text(line, pageWidth / 2, startY + (idx * 4), { align: 'center' })
        })
      }
    }

    await worker.save()
    document.body.removeChild(container)
    
    // Après téléchargement on retourne à la liste
    router.push('/app/devis')
  } catch (e: any) {
    console.error(e)
    alert('Erreur lors de la génération PDF : ' + e.message)
  } finally {
    isGeneratingPDF.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto pb-20">
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20 gap-4">
      <Loader2 class="w-8 h-8 text-primary animate-spin" />
      <span class="text-muted-foreground font-medium">Chargement du devis...</span>
    </div>

    <div v-else class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6 sticky top-0 bg-background/95 backdrop-blur z-10 py-4 border-b">
        <button
          @click="router.push('/app/devis')"
          class="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground font-medium transition-colors"
        >
          <ArrowLeft class="w-5 h-5" />
          Retour
        </button>
        <div class="flex gap-3">
          <button
            @click="saveDevis"
            :disabled="isSaving || isGeneratingPDF"
            class="hidden sm:inline-flex items-center gap-2 px-4 py-2.5 bg-background text-foreground border border-border rounded-lg font-medium hover:bg-muted transition-colors disabled:opacity-50"
          >
            <Loader2 v-if="isSaving" class="w-5 h-5 animate-spin" />
            <Save v-else class="w-5 h-5" />
            Sauvegarder Brouillon
          </button>
          <button
            @click="saveAndGeneratePDF"
            :disabled="isSaving || isGeneratingPDF"
            class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors shadow-sm disabled:opacity-50"
          >
            <Loader2 v-if="isGeneratingPDF" class="w-5 h-5 animate-spin" />
            <FileDown v-else class="w-5 h-5" />
            <span class="hidden sm:inline">{{ isSaving ? 'Sauvegarde...' : 'Sauvegarder & PDF' }}</span>
            <span class="sm:hidden">Créer PDF</span>
          </button>
        </div>
      </div>

      <h1 class="text-2xl font-bold text-foreground mb-4">{{ isEditMode ? 'Modifier le Devis' : 'Nouveau Devis' }}</h1>

      <div class="space-y-6">
        <!-- Informations Générales -->
        <section class="bg-card border border-border rounded-xl p-6">
          <h3 class="text-lg font-semibold text-foreground mb-4">Informations du document</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Date du document <span class="text-destructive">*</span></label>
              <input type="date" v-model="devis.date_devis" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" required />
            </div>
            <div>
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-1.5">
                <label class="block text-sm font-medium text-foreground">Numéro du devis <span class="text-destructive">*</span></label>
                <div class="flex items-center bg-muted rounded-lg p-1">
                  <button 
                    @click="devis.statut = 'brouillon'"
                    type="button"
                    :class="[
                      'px-3 py-1.5 text-xs font-medium rounded-md transition-all',
                      devis.statut === 'brouillon' 
                        ? 'bg-primary text-primary-foreground shadow-sm' 
                        : 'text-muted-foreground hover:text-foreground'
                    ]"
                  >
                    Brouillon
                  </button>
                  <button 
                    @click="devis.statut = 'envoyé'"
                    type="button"
                    :class="[
                      'px-3 py-1.5 text-xs font-medium rounded-md transition-all',
                      devis.statut === 'envoyé' 
                        ? 'bg-green-600 text-white shadow-sm' 
                        : 'text-muted-foreground hover:text-foreground'
                    ]"
                  >
                    Envoyé
                  </button>
                </div>
              </div>
              <input type="text" v-model="devis.numero_devis" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Ex: DEV-2023001" required />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Titre du PDF <span class="text-destructive">*</span></label>
              <input type="text" v-model="devis.titre_document_pdf" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="DEVIS" required />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Objet du devis</label>
              <input type="text" v-model="devis.objet_devis" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Ex: Rénovation salle de bain" />
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
                v-model="devis.nomClient" 
                @focus="showSuggestions = true"
                @blur="handleBlur"
                @keydown="handleKeyDown"
                class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" 
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
              <input type="text" v-model="devis.clientSiret" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-sm font-medium text-foreground mb-1.5">Adresse <span class="text-destructive">*</span></label>
              <input type="text" v-model="devis.adresseIntervention" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" required />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Code Postal</label>
              <input type="text" v-model="devis.clientCodePostal" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Ville</label>
              <input type="text" v-model="devis.clientVille" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Téléphone</label>
              <input type="tel" v-model="devis.contactClient" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1.5">Email</label>
              <input type="email" v-model="devis.clientEmail" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" />
            </div>
          </div>
        </section>

        <!-- Lignes du devis -->
        <section class="bg-card border border-border rounded-xl p-6">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <h3 class="text-lg font-semibold text-foreground">Détail du devis <span class="text-destructive">*</span></h3>
              <p class="text-sm text-muted-foreground">Ajoutez les prestations ou produits à facturer</p>
            </div>
            <button @click="ajouterLigne" class="inline-flex items-center gap-1.5 text-sm font-medium bg-primary/10 text-primary hover:bg-primary/20 px-3 py-1.5 rounded-lg transition-colors">
              <Plus class="w-4 h-4" /> Ajouter une ligne
            </button>
          </div>
          
          <div class="space-y-4 mb-8">
            <div v-for="(ligne, idx) in devis.lignes" :key="idx" class="bg-background border border-border rounded-xl p-4 sm:p-5 transition-all shadow-sm hover:shadow-md hover:border-primary/30">
              <div class="flex flex-col sm:flex-row gap-4 items-end">
                <div class="flex-1 w-full relative">
                  <label class="block text-xs font-semibold text-muted-foreground uppercase mb-2">Description</label>
                  <input type="text" v-model="ligne.description" @focus="activeLineIndex = idx" @blur="handleLineBlur" class="w-full px-3 py-2 bg-background border border-input rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none text-foreground" placeholder="Ex: Main d'œuvre" required autocomplete="off" />
                  <div v-if="activeLineIndex === idx && getFilteredDescriptions(ligne.description).length > 0" class="absolute z-50 w-full mt-1 bg-card border border-border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                    <ul class="py-1">
                      <li v-for="d in getFilteredDescriptions(ligne.description)" :key="d" @mousedown.prevent="selectDescription(idx, d)" class="px-4 py-2 cursor-pointer text-sm text-foreground hover:bg-muted transition-colors">
                        {{ d }}
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="w-full sm:w-24">
                  <label class="block text-xs font-semibold text-muted-foreground uppercase mb-2">Qté</label>
                  <input type="number" v-model="ligne.quantite" @input="updateLigneTotal(ligne)" min="0" step="0.5" class="w-full px-3 py-2 bg-background border border-input rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none text-foreground" required />
                </div>
                <div class="w-full sm:w-32">
                  <label class="block text-xs font-semibold text-muted-foreground uppercase mb-2">Prix U. HT</label>
                  <div class="relative">
                    <input type="number" v-model="ligne.prix_unite_ht" @input="updateLigneTotal(ligne)" min="0" step="0.01" class="w-full px-3 py-2 pr-8 bg-background border border-input rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none text-foreground" required />
                    <span class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm font-medium">€</span>
                  </div>
                </div>
                <div class="w-full sm:w-28">
                  <label class="block text-xs font-semibold text-muted-foreground uppercase mb-2">TVA</label>
                  <select v-model="ligne.taux_tva" @change="updateLigneTotal(ligne)" class="w-full px-3 py-2 bg-background border border-input rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none text-foreground">
                    <option v-for="t in TAUX_TVA" :key="t" :value="t">{{ t }}%</option>
                  </select>
                </div>
                <div class="w-full sm:w-32">
                  <label class="block text-xs font-semibold text-muted-foreground uppercase mb-2">Total HT</label>
                  <div class="px-3 py-2 bg-muted border border-border rounded-lg text-sm font-medium text-foreground text-right w-full">
                    {{ ligne.total_ht.toFixed(2) }} €
                  </div>
                </div>
                <button @click="supprimerLigne(idx)" v-if="devis.lignes.length > 1" class="p-2.5 text-muted-foreground hover:bg-destructive shadow-sm border border-border hover:border-destructive hover:text-white rounded-lg flex-shrink-0 transition-all" title="Supprimer la ligne">
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div v-if="devis.lignes.length === 0" class="text-center py-8 bg-muted/20 border border-border border-dashed rounded-lg">
              <p class="text-sm text-muted-foreground mb-3">Aucune ligne dans ce devis.</p>
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
          <h3 class="text-lg font-semibold text-foreground mb-4">Modalités et Conditions</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="md:col-span-1">
              <label class="block text-sm font-medium text-foreground mb-1.5">Validité du devis (jours)</label>
              <input type="number" v-model="devis.nb_jours_validite" min="1" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-foreground mb-1.5">Conditions particulières</label>
              <textarea v-model="devis.conditions_particulieres" rows="3" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none resize-y text-sm"></textarea>
            </div>
          </div>
        </section>

      </div>
    </div>
  </div>
</template>
