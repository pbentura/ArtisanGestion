<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiFetch } from '@/lib/api'
import { ArrowLeft, Save, FileDown, Plus, Trash2, Loader2, X, Eye, CheckCircle2, Receipt, Share2 } from 'lucide-vue-next'
import { useMobile } from '@/composables/useMobile'
import { useSwipe } from '@vueuse/core'

const router = useRouter()
const route = useRoute()
const { sharePDF, triggerHaptic, isNative } = useMobile()

const mainContainer = ref<HTMLElement | null>(null)
useSwipe(mainContainer, {
  onSwipeEnd(_e: TouchEvent, direction) {
    if (direction === 'right' && isNative) {
      router.push('/app/devis')
    }
  }
})

const isSaving = ref(false)
const isGeneratingPDF = ref(false)
const isLoading = ref(false)
const showPDFModal = ref(false)
const previewHTML = ref('')
const pdfUrl = ref('')
const isUpdatingStatus = ref(false)

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
  numero_devis: `DEV-${new Date().toISOString().split('T')[0].replace(/-/g, '')}-${new Date().getHours().toString().padStart(2, '0')}${new Date().getMinutes().toString().padStart(2, '0')}`,
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

const pastDescriptions = ref<any[]>([])
const activeLineIndex = ref<number | null>(null)
const focusedLineIndex = ref(-1)

const lineSuggestions = computed(() => {
  if (activeLineIndex.value === null) return []
  const ligne = devis.value.lignes[activeLineIndex.value]
  if (!ligne || !ligne.description) return []
  const query = ligne.description.trim()
  if (query.length < 1) return []
  const lowerQuery = query.toLowerCase()
  return pastDescriptions.value.filter(d => (d.description || '').toLowerCase().includes(lowerQuery)).slice(0, 8)
})

function selectDescription(idx: number, suggestion: any) {
  devis.value.lignes[idx].description = suggestion.description
  devis.value.lignes[idx].quantite = Number(suggestion.quantite) || 1
  devis.value.lignes[idx].prix_unite_ht = Number(suggestion.prix_unite_ht) || 0
  devis.value.lignes[idx].taux_tva = Number(suggestion.taux_tva) || 20
  
  updateLigneTotal(devis.value.lignes[idx])
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

async function loadExistingDevis(id: number) {
  isLoading.value = true
  try {
    const res = await apiFetch(`devis/${id}`)
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
    const clientData = {
      nom: devis.value.nomClient,
      siret: devis.value.clientSiret,
      adresse: devis.value.adresseIntervention,
      code_postal: devis.value.clientCodePostal,
      ville: devis.value.clientVille,
      telephone: devis.value.contactClient,
      email: devis.value.clientEmail
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

async function saveDevisToDatabase(clientId: number) {
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
  
  const endpoint = isEditMode.value && devisId.value
    ? `devis/${devisId.value}`
    : 'devis'
  
  const method = isEditMode.value ? 'PUT' : 'POST'
  
  const res = await apiFetch(endpoint, {
    method,
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
    if (pdf) {
      const totalPages = pdf.internal.getNumberOfPages()
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()

      for (let i = 1; i <= totalPages; i++) {
        pdf.setPage(i)
        
        // 1. Ligne de séparation élégante (Bleu Primaire #2563eb)
        pdf.setDrawColor(37, 99, 235)
        pdf.setLineWidth(0.4)
        pdf.line(15, pageHeight - 20, pageWidth - 15, pageHeight - 20)

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
        pdf.text(`Page ${i} / ${totalPages}`, pageWidth - 15, pageHeight - 10, { align: 'right' })

        // 4. Petit branding (Bas Gauche)
        pdf.setFontSize(6)
        pdf.setTextColor(156, 163, 175) // COLOR_LIGHT_MUTED
        pdf.setFont('helvetica', 'italic')
        pdf.text("Généré via Ventura", 15, pageHeight - 10)
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
    
    // Après téléchargement on retourne à la liste
    router.push('/app/devis')
  } catch (e: any) {
    console.error(e)
    alert('Erreur lors de la génération PDF : ' + e.message)
  } finally {
    isGeneratingPDF.value = false
  }
}
async function toggleStatus() {
  if (!devisId.value || isUpdatingStatus.value) return
  
  const newStatut = devis.value.statut === 'brouillon' ? 'envoyé' : 'brouillon'
  isUpdatingStatus.value = true
  
  try {
    const res = await apiFetch(`devis/${devisId.value}`, {
      method: 'PUT',
      body: JSON.stringify({ statut: newStatut })
    })
    
    if (res.ok) {
      const updated = await res.json()
      devis.value.statut = updated.statut
    }
  } catch (e) {
    console.error(e)
  } finally {
    isUpdatingStatus.value = false
  }
}

function shareDevis() {
  if (!isNative) {
    openPreview()
    return
  }
  alert("Le partage direct sera disponible bientôt. Utilisez l'aperçu PDF.")
}
</script>

<template>
  <div ref="mainContainer" class="max-w-4xl mx-auto pb-20">
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20 gap-4">
      <Loader2 class="w-8 h-8 text-primary animate-spin" />
      <span class="text-muted-foreground font-medium">Chargement du devis...</span>
    </div>

    <div v-else class="space-y-6">
      <!-- Header -->
      <div class="sticky top-0 bg-background/95 backdrop-blur z-20 border-b pt-safe px-4 -mx-4 mb-6">
        <!-- Première ligne : Retour + Actions Primaires -->
        <div class="flex items-center justify-between py-3">
          <button
            @click="router.push('/app/devis')"
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

            <!-- Toujours visible : Sauvegarder (si brouillon) -->
            <button
              v-if="devis.statut === 'brouillon'"
              @click="saveDevis"
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

            <!-- Desktop only : Actions spécifiques -->
            <div v-if="isEditMode" class="hidden sm:flex items-center gap-2 ml-2 pl-2 border-l border-border">
              <button @click="toggleStatus" :disabled="isUpdatingStatus" class="inline-flex items-center gap-2 px-3 py-2 rounded-lg font-medium border shadow-sm" :class="devis.statut === 'envoyé' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-blue-50 text-blue-700 border-blue-200'">
                <template v-if="isUpdatingStatus"><Loader2 class="w-4 h-4 animate-spin" /></template>
                <template v-else><CheckCircle2 class="w-4 h-4" /></template>
                <span>{{ devis.statut === 'envoyé' ? 'Brouillon' : 'Envoyer' }}</span>
              </button>
              <button @click="router.push(`/app/factures/new?fromDevis=${devisId}`)" class="inline-flex items-center gap-2 px-3 py-2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg font-medium">
                <Receipt class="w-5 h-5" />
                <span>Facturer</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Deuxième ligne (Mobile uniquement) : Actions Spécifiques -->
        <div v-if="isEditMode" class="flex sm:hidden items-center gap-2 pb-3 overflow-x-auto no-scrollbar">
          <button
            @click="toggleStatus"
            :disabled="isUpdatingStatus"
            class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 rounded-lg font-medium border shadow-sm whitespace-nowrap"
            :class="devis.statut === 'envoyé' 
              ? 'bg-green-50 text-green-700 border-green-200' 
              : 'bg-blue-50 text-blue-700 border-blue-200'"
          >
            <CheckCircle2 class="w-4 h-4" />
            <span class="text-xs">{{ devis.statut === 'envoyé' ? 'Marquer brouillon' : 'Marquer envoyé' }}</span>
          </button>

          <button
            @click="router.push(`/app/factures/new?fromDevis=${devisId}`)"
            class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg font-medium whitespace-nowrap"
          >
            <Receipt class="w-4 h-4" />
            <span class="text-xs">Facturer</span>
          </button>

          <button
            v-if="isNative"
            @click="shareDevis"
            class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 bg-teal-50 text-teal-700 border border-teal-200 rounded-lg font-medium whitespace-nowrap"
          >
            <Share2 class="w-4 h-4" />
            <span class="text-xs">Partager</span>
          </button>
        </div>
      </div>

      <h1 class="text-2xl font-bold text-foreground mb-4 hidden sm:block">{{ isEditMode ? 'Modifier le Devis' : 'Nouveau Devis' }}</h1>

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
                  <input type="text" v-model="ligne.description" 
                    @focus="activeLineIndex = idx; focusedLineIndex = -1" 
                    @blur="handleLineBlur" 
                    @keydown="handleLineKeyDown($event, idx)"
                    class="w-full px-3 py-2 bg-background border border-input rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none text-foreground" 
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
                <h2 class="text-sm font-bold text-foreground">Aperçu du Devis</h2>
                <p class="text-[10px] text-muted-foreground">{{ devis.titre_document_pdf }} • {{ devis.numero_devis }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <a 
                :href="pdfUrl" 
                :download="`${devis.titre_document_pdf.replace(/\s+/g, '_')}_${devis.numero_devis}.pdf`"
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

          <!-- Mobile Footer (always show download on HTML preview) -->
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
