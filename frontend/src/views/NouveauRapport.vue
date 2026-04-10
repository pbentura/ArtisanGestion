<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { API_BASE_URL } from '@/lib/api'
import { ArrowLeft, Save, FileDown, Bold, Italic, Underline, List, ListOrdered, Image as ImageIcon, X, Camera, Sparkles, Loader2 } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const isSaving = ref(false)
const isGeneratingPDF = ref(false)
const isLoading = ref(false)

// AI Generation
const showAIModal = ref(false)
const isGeneratingAI = ref(false)
const isStreamingAI = ref(false)
const aiForm = ref({
  type_intervention: '',
  description: ''
})
const aiError = ref('')
const showPDFModal = ref(false)
const pdfUrl = ref('')
const previewHTML = ref('')


const aiInterventionTypes = [
  'Plomberie',
  'Électricité',
  'Climatisation / CVC',
  'Menuiserie',
  'Peinture',
  'Maçonnerie',
  'Toiture / Couverture',
  'Serrurerie',
  'Nettoyage',
  'Dépannage informatique',
  'Maintenance industrielle',
  'Inspection / Contrôle',
  'Autre'
]

// Mode édition
const isEditMode = computed(() => !!route.params.id)
const rapportId = computed(() => route.params.id ? Number(route.params.id) : null)

interface Rapport {
  id?: number
  dateIntervention: string
  titre: string
  nomClient: string
  clientSiret: string
  adresseIntervention: string
  clientCodePostal: string
  clientVille: string
  contactClient: string
  contenu: string
  photos: string[]
  statut: string
  createdAt: string
}

const rapport = ref<Rapport>({
  dateIntervention: new Date().toISOString().split('T')[0],
  titre: "RAPPORT D'INTERVENTION",
  nomClient: '',
  clientSiret: '',
  adresseIntervention: '',
  clientCodePostal: '',
  clientVille: '',
  contactClient: '',
  contenu: '',
  photos: [],
  statut: 'en cours',
  createdAt: new Date().toISOString()
})

// Données de la société
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

const clients = ref<any[]>([])
const selectedClientId = ref<number | null>(null)
const isCameraActive = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
let stream: MediaStream | null = null

// Autocomplete logic
const showSuggestions = ref(false)
const focusedIndex = ref(-1)
const filteredClients = computed(() => {
  const query = rapport.value.nomClient.toLowerCase().trim()
  if (!query || query.length < 1) return []
  return clients.value.filter(c => 
    c.nom.toLowerCase().includes(query) || 
    (c.ville && c.ville.toLowerCase().includes(query))
  ).slice(0, 8)
})

function selectClient(c: any) {
  rapport.value.nomClient = c.nom
  rapport.value.clientSiret = c.siret || ''
  rapport.value.adresseIntervention = c.adresse || ''
  rapport.value.clientCodePostal = c.code_postal || ''
  rapport.value.clientVille = c.ville || ''
  rapport.value.contactClient = c.telephone || ''
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
  // Delay closing to allow mousedown on suggestions to trigger first
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
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

async function openCamera() {
  isCameraActive.value = true
  try {
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'environment' },
      audio: false 
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
  } catch (err) {
    console.error("Erreur accès caméra:", err)
    alert("Impossible d'accéder à la caméra. Vérifiez les autorisations.")
    isCameraActive.value = false
  }
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  isCameraActive.value = false
}

function capturePhoto() {
  if (!videoRef.value) return
  
  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  const ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.drawImage(videoRef.value, 0, 0)
    rapport.value.photos.push(canvas.toDataURL('image/jpeg'))
    stopCamera()
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

// Rich Editor ref
const editorRef = ref<HTMLElement | null>(null)

onMounted(async () => {
  loadSociete()
  loadClients()
  
  // Si mode édition, charger le rapport existant
  if (isEditMode.value && rapportId.value) {
    await loadExistingRapport(rapportId.value)
  }
  
  // Initialize editor content once (don't use v-html)
  if (editorRef.value) {
    editorRef.value.innerHTML = rapport.value.contenu
  }
})

async function loadExistingRapport(id: number) {
  isLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/rapports/${id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) {
      alert('Rapport introuvable')
      router.push('/app/rapports')
      return
    }
    const data = await res.json()
    
    rapport.value = {
      id: data.id,
      dateIntervention: data.date_intervention,
      titre: data.titre_document_pdf || "RAPPORT D'INTERVENTION",
      nomClient: data.client?.nom || '',
      clientSiret: data.client?.siret || '',
      adresseIntervention: data.client?.adresse || '',
      clientCodePostal: data.client?.code_postal || '',
      clientVille: data.client?.ville || '',
      contactClient: data.client?.telephone || '',
      contenu: data.contenu || '',
      photos: data.photos && data.photos.length > 0 ? data.photos : (data.photo_url ? [data.photo_url] : []),
      statut: data.statut || 'en cours',
      createdAt: data.created_at
    }
    
    // Set selected client
    if (data.client?.id) {
      selectedClientId.value = data.client.id
    }
    
    // Update editor content
    if (editorRef.value) {
      editorRef.value.innerHTML = rapport.value.contenu
    }
  } catch (e) {
    console.error('Erreur lors du chargement du rapport:', e)
  } finally {
    isLoading.value = false
  }
}

function onEditorInput() {
  if (editorRef.value) {
    rapport.value.contenu = editorRef.value.innerHTML
  }
}


// onClientSelect is no longer used by the old dropdown but we might keep it or remove it.
// Removing it as selectClient handles it now.

const fileInput = ref<HTMLInputElement | null>(null)

function openGallery() {
  fileInput.value?.click()
}

function handlePhotoUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const files = Array.from(target.files)
    files.forEach(file => {
      const reader = new FileReader()
      reader.onload = (e) => {
        rapport.value.photos.push(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    })
    if (fileInput.value) fileInput.value.value = ''
  }
}

function removePhoto(index: number) {
  rapport.value.photos.splice(index, 1)
}

const isValid = computed(() => {
  return rapport.value.dateIntervention && rapport.value.titre.trim() && rapport.value.nomClient.trim() && rapport.value.adresseIntervention.trim()
})

const activeFormats = ref({
  bold: false,
  italic: false,
  underline: false,
  insertUnorderedList: false,
  insertOrderedList: false
})

function execCommand(command: string, value: string | undefined = undefined) {
  document.execCommand(command, false, value)
  updateActiveFormats()
}

function updateActiveFormats() {
  activeFormats.value = {
    bold: document.queryCommandState('bold'),
    italic: document.queryCommandState('italic'),
    underline: document.queryCommandState('underline'),
    insertUnorderedList: document.queryCommandState('insertUnorderedList'),
    insertOrderedList: document.queryCommandState('insertOrderedList')
  }
}

async function saveClientToDatabase(): Promise<number | null> {
  // Si un client est déjà sélectionné et que le nom correspond toujours, on utilise cet ID
  if (selectedClientId.value) {
    const c = clients.value.find(cl => cl.id === selectedClientId.value)
    if (c && c.nom === rapport.value.nomClient) {
      return selectedClientId.value
    }
  }

  try {
    const token = localStorage.getItem('token')
    const clientData = {
      nom: rapport.value.nomClient,
      siret: rapport.value.clientSiret,
      adresse: rapport.value.adresseIntervention,
      code_postal: rapport.value.clientCodePostal,
      ville: rapport.value.clientVille,
      telephone: rapport.value.contactClient
    }
    
    const res = await fetch(`${API_BASE_URL}/api/clients`, {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(clientData)
    })
    
    if (!res.ok) {
      console.error('Erreur API Client:', await res.text())
      return null
    }
    const data = await res.json()
    return data.id
  } catch (e) {
    console.error('Erreur lors de la sauvegarde du client en base:', e)
    return null
  }
}

async function saveRapportToDatabase(clientId: number) {
  const token = localStorage.getItem('token')
  const rapportData = {
    date_intervention: rapport.value.dateIntervention,
    titre_document_pdf: rapport.value.titre,
    id_client: clientId,
    contenu: rapport.value.contenu || null,
    photos: rapport.value.photos,
    statut: rapport.value.statut
  }
  
  const url = isEditMode.value && rapportId.value
    ? `${API_BASE_URL}/api/rapports/${rapportId.value}`
    : `${API_BASE_URL}/api/rapports`
  
  const method = isEditMode.value ? 'PUT' : 'POST'
  
  const res = await fetch(url, {
    method,
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(rapportData)
  })
  
  if (!res.ok) {
    throw new Error('Erreur API Rapport: ' + await res.text())
  }
  return await res.json()
}

async function saveRapport() {
  if (!isValid.value) {
    alert('Veuillez remplir les informations obligatoires (Date, Titre, Client, Adresse)')
    return
  }

  isSaving.value = true
  try {
    const clientId = await saveClientToDatabase()
    if (!clientId) throw new Error("Impossible de créer le client")
    
    const savedRapport = await saveRapportToDatabase(clientId)
    console.log("Rapport sauvegardé avec statut:", savedRapport.statut)
    
    await generatePDF()
    router.push('/app/rapports')
  } catch (e: any) {
    console.error(e)
    alert('Erreur lors de la sauvegarde du rapport : ' + e.message)
  } finally {
    isSaving.value = false
  }
}

function getReportHTML() {
  const pdfFormatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit', month: '2-digit', year: 'numeric'
    })
  }

  const adresseSociete = [societe.value.adresse, societe.value.code_postal, societe.value.ville]
    .filter(Boolean)
    .join(' ')

  return `
    <div style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; padding: 15px; background: white; font-size: 12px;">

      <!-- EN-TÊTE : Logo + Infos société -->
      <div style="display: flex; align-items: flex-start; justify-content: space-between; padding-bottom: 15px; border-bottom: 3px solid #2563eb; margin-bottom: 15px;">
        <!-- Logo -->
        <div style="flex-shrink: 0; width: 120px; height: 70px; display: flex; align-items: center; justify-content: flex-start;">
          ${societe.value.logo
            ? `<img src="${societe.value.logo}" style="max-width: 120px; max-height: 70px; object-fit: contain;" />`
            : `<div style="width: 70px; height: 70px; background: #2563eb; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-size: 24px; font-weight: 700;">${(societe.value.nom || 'E').charAt(0).toUpperCase()}</span>
               </div>`
          }
        </div>
        <!-- Infos société -->
        <div style="text-align: right; flex: 1; padding-left: 15px;">
          <div style="font-size: 16px; font-weight: 700; color: #1f2937; margin-bottom: 4px;">${societe.value.nom || ''}</div>
          ${adresseSociete ? `<div style="font-size: 10px; color: #6b7280;">${adresseSociete}</div>` : ''}
          ${societe.value.telephone ? `<div style="font-size: 10px; color: #6b7280;">Tél : ${societe.value.telephone}</div>` : ''}
          ${societe.value.email ? `<div style="font-size: 10px; color: #6b7280;">${societe.value.email}</div>` : ''}
          ${societe.value.siret ? `<div style="font-size: 9px; color: #9ca3af; margin-top: 3px;">SIRET : ${societe.value.siret}</div>` : ''}
        </div>
      </div>

      <!-- TITRE DU RAPPORT -->
      <div style="text-align: center; margin-bottom: 20px; padding: 10px; background: #f1f5f9; border-radius: 6px;">
        <h1 style="color: #1e3a5f; margin: 0; font-size: 18px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">${rapport.value.titre}</h1>
      </div>

      <div style="margin-bottom: 15px;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
          <div>
            <div style="margin-bottom: 10px;">
              <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Client</div>
              <div style="font-size: 12px; color: #1f2937;"><strong>${rapport.value.nomClient || '-'}</strong></div>
            </div>
            <div style="margin-bottom: 10px;">
              <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Adresse d'intervention</div>
              <div style="font-size: 12px; color: #1f2937;">
                ${rapport.value.adresseIntervention || '-'}<br/>
                ${[rapport.value.clientCodePostal, rapport.value.clientVille].filter(Boolean).join(' ')}${[rapport.value.clientCodePostal, rapport.value.clientVille].filter(Boolean).length > 0 ? '<br/>' : ''}
                ${rapport.value.contactClient ? `Tél: ${rapport.value.contactClient}` : ''}
              </div>
            </div>
            ${rapport.value.clientSiret ? `
            <div style="margin-bottom: 10px;">
              <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">SIRET / SIREN client</div>
              <div style="font-size: 12px; color: #1f2937;">${rapport.value.clientSiret}</div>
            </div>
            ` : ''}
          </div>
          <div>
            <div style="margin-bottom: 10px;">
              <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Date d'intervention</div>
              <div style="font-size: 13px; font-weight: 600; color: #1f2937;">${pdfFormatDate(rapport.value.dateIntervention)}</div>
            </div>
          </div>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <h2 style="color: #2563eb; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; margin-bottom: 10px; font-size: 13px; font-weight: 600; text-transform: uppercase;">Rapport d'intervention</h2>
        <div style="font-size: 12px; line-height: 1.8;">${rapport.value.contenu || '<p>Aucun contenu</p>'}</div>
      </div>

      ${rapport.value.photos && rapport.value.photos.length > 0 ? `
      <div style="margin-top: 20px;">
        <h2 style="color: #2563eb; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; margin-bottom: 15px; font-size: 13px; font-weight: 600; text-transform: uppercase;">Photos (${rapport.value.photos.length})</h2>
        <div style="display: grid; grid-template-columns: 1fr; gap: 15px;">
          ${rapport.value.photos.map(p => `
            <div style="margin-bottom: 10px; page-break-inside: avoid;">
              <img src="${p}" style="max-width: 100%; max-height: 500px; object-fit: contain; border-radius: 4px; border: 1px solid #e5e7eb;" />
            </div>
          `).join('')}
        </div>
      </div>
      ` : ''}
    </div>`
}

async function openPreview() {
  previewHTML.value = getReportHTML()
  showPDFModal.value = true
}

async function generatePDF() {
  isGeneratingPDF.value = true

  try {
    const footerText = societe.value.texte_pied_page || ''
    const container = document.createElement('div')
    container.innerHTML = getReportHTML()

    document.body.appendChild(container)

    const filename = (rapport.value.titre || 'rapport').replace(/[^a-zA-Z0-9àâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ _-]/g, '').replace(/\s+/g, '_')

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
        const startY = pdf.internal.pageSize.getHeight() - 15 // Start slightly higher (15mm from bottom)
        lines.forEach((line: string, idx: number) => {
          pdf.text(line, pageWidth / 2, startY + (idx * 4), { align: 'center' }) // 4mm line spacing
        })
      }
    }

    await worker.save()
    document.body.removeChild(container)
  } catch (e) {
    console.error('Erreur lors de la génération du PDF', e)
  } finally {
    isGeneratingPDF.value = false
  }
}

function closePDFModal() {
  showPDFModal.value = false
  previewHTML.value = ''
}

async function saveAndGeneratePDF() {
  if (!isValid.value) {
    alert('Veuillez remplir les informations obligatoires (Date, Titre, Client, Adresse)')
    return
  }

  isSaving.value = true
  try {
    const clientId = await saveClientToDatabase()
    if (!clientId) throw new Error("Impossible de créer le client")
    
    const savedRapport = await saveRapportToDatabase(clientId)
    console.log("Rapport sauvegardé avec statut:", savedRapport.statut)
    
    await generatePDF()
    router.push('/app/rapports')
  } catch (e: any) {
    console.error(e)
    alert('Erreur lors de la sauvegarde du rapport : ' + e.message)
  } finally {
    isSaving.value = false
  }
}

async function generateWithAI() {
  if (!aiForm.value.type_intervention || !aiForm.value.description.trim()) {
    aiError.value = 'Veuillez renseigner le type d\'intervention et une description.'
    return
  }
  aiError.value = ''
  isGeneratingAI.value = true

  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/ai/generate-rapport-stream`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        type_intervention: aiForm.value.type_intervention,
        description: aiForm.value.description,
        nom_client: rapport.value.nomClient || undefined,
        adresse: rapport.value.adresseIntervention || undefined,
        date_intervention: rapport.value.dateIntervention || undefined
      })
    })

    if (!res.ok || !res.body) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Erreur lors de la génération')
    }

    // Le stream est ouvert — on ferme la modale et on démarre l'écriture en direct
    showAIModal.value = false
    isGeneratingAI.value = false
    isStreamingAI.value = true
    rapport.value.contenu = ''
    await nextTick()
    if (editorRef.value) {
      editorRef.value.innerHTML = ''
    }

    aiForm.value = { type_intervention: '', description: '' }

    // Lecture du stream SSE
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let accumulatedHTML = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const raw = line.slice(6).trim()
        if (raw === '[DONE]') {
          isStreamingAI.value = false
          // Synchroniser le state final avec le DOM
          if (editorRef.value) {
            rapport.value.contenu = editorRef.value.innerHTML
          }
          return
        }
        if (raw === '') continue
        try {
          const delta: string = JSON.parse(raw)
          accumulatedHTML += delta
          // Nettoyer les balises markdown ```html ... ``` avant d'afficher
          let displayHTML = accumulatedHTML
          if (displayHTML.startsWith('```html')) {
            displayHTML = displayHTML.slice(7)
          } else if (displayHTML.startsWith('```')) {
            displayHTML = displayHTML.slice(3)
          }
          if (displayHTML.endsWith('```')) {
            displayHTML = displayHTML.slice(0, -3)
          }
          displayHTML = displayHTML.trimStart()
          // Mettre à jour l'éditeur avec le HTML nettoyé
          if (editorRef.value) {
            editorRef.value.innerHTML = displayHTML
            // Auto-scroll vers le bas
            editorRef.value.scrollTop = editorRef.value.scrollHeight
          }
        } catch {
          // Ignore les chunks mal formés
        }
      }
    }

    // Fin de stream sans [DONE]
    isStreamingAI.value = false
    if (editorRef.value) {
      rapport.value.contenu = editorRef.value.innerHTML
    }

  } catch (e: any) {
    isGeneratingAI.value = false
    isStreamingAI.value = false
    aiError.value = e.message || 'Une erreur est survenue'
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto pb-20">
    <!-- AI Modal Overlay -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="showAIModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="!isGeneratingAI && (showAIModal = false)">
          <!-- Backdrop -->
          <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>

          <!-- Modal card -->
          <div class="relative w-full max-w-lg bg-card border border-border rounded-2xl shadow-2xl overflow-hidden">

            <!-- Generating overlay -->
            <Transition name="fade">
              <div v-if="isGeneratingAI" class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-card/95 backdrop-blur-sm gap-6">
                <div class="relative">
                  <div class="w-20 h-20 rounded-full border-4 border-primary/20 border-t-primary animate-spin"></div>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <Sparkles class="w-8 h-8 text-primary animate-pulse" />
                  </div>
                </div>
                <div class="text-center">
                  <p class="text-lg font-semibold text-foreground">L'IA rédige votre rapport...</p>
                  <p class="text-sm text-muted-foreground mt-1">Cela prend généralement 5 à 15 secondes</p>
                </div>
                <!-- Animated dots -->
                <div class="flex gap-1.5">
                  <span class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                  <span class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                  <span class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 300ms"></span>
                </div>
              </div>
            </Transition>

            <!-- Header -->
            <div class="relative px-6 pt-6 pb-4 bg-gradient-to-br from-primary/5 via-card to-card border-b border-border">
              <div class="flex items-start gap-3">
                <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Sparkles class="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 class="text-lg font-bold text-foreground">Générer avec l'IA</h2>
                  <p class="text-sm text-muted-foreground">Quelques informations suffisent pour rédiger un rapport professionnel</p>
                </div>
                <button
                  @click="showAIModal = false"
                  :disabled="isGeneratingAI"
                  class="ml-auto p-1.5 rounded-lg hover:bg-muted transition-colors disabled:opacity-50"
                >
                  <X class="w-4 h-4 text-muted-foreground" />
                </button>
              </div>
            </div>

            <!-- Form -->
            <div class="px-6 py-5 space-y-4">
              <!-- Type d'intervention -->
              <div>
                <label class="block text-sm font-medium text-foreground mb-1.5">Type d'intervention <span class="text-destructive">*</span></label>
                <select
                  v-model="aiForm.type_intervention"
                  :disabled="isGeneratingAI"
                  class="w-full px-3 py-2.5 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none text-foreground transition-shadow disabled:opacity-50"
                >
                  <option value="" disabled>Sélectionner un type...</option>
                  <option v-for="t in aiInterventionTypes" :key="t" :value="t">{{ t }}</option>
                </select>
              </div>

              <!-- Description courte -->
              <div>
                <label class="block text-sm font-medium text-foreground mb-1.5">Description rapide <span class="text-destructive">*</span></label>
                <textarea
                  v-model="aiForm.description"
                  :disabled="isGeneratingAI"
                  rows="4"
                  placeholder="Ex: Remplacement du chauffe-eau défectueux, fuite au niveau du raccord, installation du nouveau modèle 150L..."
                  class="w-full px-3 py-2.5 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none resize-none text-foreground text-sm transition-shadow disabled:opacity-50"
                ></textarea>
                <p class="text-xs text-muted-foreground mt-1">Plus vous êtes précis, meilleur sera le rapport généré.</p>
              </div>

              <!-- Info client pré-remplie -->
              <div v-if="rapport.nomClient" class="flex items-center gap-2 bg-primary/5 border border-primary/20 rounded-lg px-3 py-2">
                <Sparkles class="w-4 h-4 text-primary flex-shrink-0" />
                <p class="text-xs text-foreground">
                  L'IA utilisera les infos du client <strong>{{ rapport.nomClient }}</strong> pour personnaliser le rapport.
                </p>
              </div>

              <!-- Error -->
              <div v-if="aiError" class="flex items-center gap-2 bg-destructive/10 border border-destructive/30 rounded-lg px-3 py-2">
                <p class="text-xs text-destructive">{{ aiError }}</p>
              </div>
            </div>

            <!-- Footer -->
            <div class="px-6 pb-6 flex items-center gap-3">
              <button
                @click="showAIModal = false"
                :disabled="isGeneratingAI"
                class="flex-1 px-4 py-2.5 rounded-lg border border-border text-sm font-medium text-muted-foreground hover:bg-muted transition-colors disabled:opacity-50"
              >
                Annuler
              </button>
              <button
                @click="generateWithAI"
                :disabled="isGeneratingAI || !aiForm.type_intervention || !aiForm.description.trim()"
                class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                <Loader2 v-if="isGeneratingAI" class="w-4 h-4 animate-spin" />
                <Sparkles v-else class="w-4 h-4" />
                {{ isGeneratingAI ? 'Génération...' : 'Générer le rapport' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

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
                  <h2 class="text-sm font-bold text-foreground">Aperçu du Rapport</h2>
                  <p class="text-[10px] text-muted-foreground">{{ rapport.titre }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <a 
                  :href="pdfUrl" 
                  :download="`${rapport.titre.replace(/\s+/g, '_')}.pdf`"
                  class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors"
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
            <div class="flex-1 bg-muted/20 relative overflow-y-auto overflow-x-hidden p-4 sm:p-8 flex justify-center">
              <div 
                v-if="previewHTML" 
                class="w-full max-w-[210mm] bg-white shadow-xl min-h-[297mm] h-fit p-[15mm] origin-top"
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
                  @click="generatePDF"
                  class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
                >
                  <FileDown class="w-5 h-5" />
                  Générer le PDF final
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>


    <!-- Header -->
    <div class="flex items-center justify-between mb-6 sticky top-0 bg-background/95 backdrop-blur z-10 py-4 border-b">
      <button @click="router.push('/app/rapports')" class="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft class="w-5 h-5" /> Retour
      </button>
      <div class="flex items-center gap-3">
        <button @click="openPreview" :disabled="!isValid" class="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium border border-border bg-background text-foreground hover:bg-muted transition-colors disabled:opacity-50">
          <FileDown class="w-5 h-5" /> Aperçu Rapport
        </button>
        <button @click="saveAndGeneratePDF" :disabled="!isValid || isSaving" class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50">
          <Save class="w-5 h-5" /> {{ isSaving ? 'Sauvegarde...' : 'Sauvegarder & PDF' }}
        </button>
      </div>
    </div>

    <h1 class="text-2xl font-bold text-foreground mb-4">{{ isEditMode ? 'Modifier le Rapport' : 'Nouveau Rapport d\'Intervention' }}</h1>

    <!-- Loading state for edit mode -->
    <div v-if="isLoading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else class="space-y-6">
      <!-- Date d'intervention -->
      <section class="bg-card border border-border rounded-xl p-6">
        <label class="block text-sm font-medium text-foreground mb-2">Date d'intervention *</label>
        <input v-model="rapport.dateIntervention" type="date" class="w-full max-w-xs px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" />
      </section>

      <!-- Titre du document PDF -->
      <section class="bg-card border border-border rounded-xl p-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <label class="block text-sm font-medium text-foreground">Titre du document PDF *</label>
          <div class="flex items-center bg-muted rounded-lg p-1">
            <button 
              @click="rapport.statut = 'en cours'"
              type="button"
              :class="[
                'px-3 py-1.5 text-xs font-medium rounded-md transition-all',
                rapport.statut === 'en cours' 
                  ? 'bg-primary text-primary-foreground shadow-sm' 
                  : 'text-muted-foreground hover:text-foreground'
              ]"
            >
              En cours
            </button>
            <button 
              @click="rapport.statut = 'terminée'"
              type="button"
              :class="[
                'px-3 py-1.5 text-xs font-medium rounded-md transition-all',
                rapport.statut === 'terminée' 
                  ? 'bg-green-600 text-white shadow-sm' 
                  : 'text-muted-foreground hover:text-foreground'
              ]"
            >
              Terminée
            </button>
          </div>
        </div>
        <input v-model="rapport.titre" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="RAPPORT D'INTERVENTION" />
        <p class="text-xs text-muted-foreground mt-1">Ce titre apparaîtra en haut du document PDF généré</p>
      </section>

      <!-- Client Infos -->
      <section class="bg-card border border-border rounded-xl p-6 space-y-4">
        <h3 class="text-lg font-semibold text-foreground mb-4">Informations du Client</h3>
        
        <div class="relative">
          <label class="block text-sm font-medium text-foreground mb-2">Nom complet du client *</label>
          <div class="relative">
            <input 
              v-model="rapport.nomClient" 
              type="text" 
              @input="showSuggestions = true; focusedIndex = -1"
              @focus="showSuggestions = true"
              @blur="handleBlur"
              @keydown="handleKeyDown"
              class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" 
              placeholder="Saisissez le nom du client..." 
              autocomplete="off"
            />
            
            <!-- Suggestions Dropdown -->
            <Transition name="fade">
              <div v-if="showSuggestions && filteredClients.length > 0" class="absolute z-50 w-full mt-1 bg-card border border-border rounded-lg shadow-xl overflow-hidden max-h-60 overflow-y-auto backdrop-blur-sm bg-card/95">
                <div 
                  v-for="(c, index) in filteredClients" 
                  :key="c.id"
                  @mousedown.prevent="selectClient(c)"
                  @mouseenter="focusedIndex = index"
                  :class="[
                    'px-4 py-3 cursor-pointer transition-colors border-b border-border/50 last:border-0',
                    focusedIndex === index ? 'bg-primary/10 text-primary' : 'text-foreground hover:bg-muted'
                  ]"
                >
                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-medium text-sm">{{ c.nom }}</div>
                      <div class="text-[10px] text-muted-foreground">{{ c.adresse || '' }} {{ c.ville ? ` - ${c.ville}` : '' }}</div>
                    </div>
                    <div v-if="c.siret" class="text-[10px] bg-muted px-1.5 py-0.5 rounded opacity-70">
                      SIRET: {{ c.siret }}
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
          <p class="text-[10px] text-muted-foreground mt-1">Saisissez les premières lettres pour rechercher un client existant</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-foreground mb-2">SIRET / SIREN</label>
            <input v-model="rapport.clientSiret" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Numéro SIRET ou SIREN" />
          </div>
          <div>
            <label class="block text-sm font-medium text-foreground mb-2">Numéro de téléphone</label>
            <input v-model="rapport.contactClient" type="tel" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="06 XX XX XX XX" />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-foreground mb-2">Adresse d'intervention *</label>
          <input v-model="rapport.adresseIntervention" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Adresse (N° et rue)" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-foreground mb-2">Code Postal</label>
            <input v-model="rapport.clientCodePostal" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Code postal" />
          </div>
          <div>
            <label class="block text-sm font-medium text-foreground mb-2">Ville</label>
            <input v-model="rapport.clientVille" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Ville" />
          </div>
        </div>
      </section>

      <!-- AI Generation Banner (creation only) -->
    <div v-if="!isEditMode" class="mb-6">
      <div class="relative overflow-hidden bg-gradient-to-r from-primary/10 via-primary/5 to-transparent border border-primary/20 rounded-xl p-4">
        <div class="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-2xl"></div>
        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div class="flex items-center gap-3 flex-1">
            <div class="w-10 h-10 rounded-xl bg-primary/15 flex items-center justify-center flex-shrink-0">
              <Sparkles class="w-5 h-5 text-primary" />
            </div>
            <div>
              <p class="font-semibold text-foreground text-sm">Générer le rapport avec l'IA</p>
              <p class="text-xs text-muted-foreground">Mistral AI rédige un rapport professionnel et structuré en quelques secondes</p>
            </div>
          </div>
          <button
            @click="showAIModal = true"
            class="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-all hover:shadow-lg hover:shadow-primary/20 flex-shrink-0"
          >
            <Sparkles class="w-4 h-4" />
            Générer avec l'IA
          </button>
        </div>
      </div>
    </div>

      <!-- Rich Editor complet -->
      <section class="bg-card border border-border rounded-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <label class="block text-sm font-medium text-foreground">Contenu du rapport *</label>
          <!-- Badge streaming IA -->
          <Transition name="fade">
            <div v-if="isStreamingAI" class="flex items-center gap-2 px-3 py-1.5 bg-primary/10 border border-primary/25 rounded-full">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              <Sparkles class="w-3.5 h-3.5 text-primary" />
              <span class="text-xs font-medium text-primary">L'IA rédige...</span>
            </div>
          </Transition>
        </div>
        <div class="border border-border rounded-lg overflow-hidden bg-background" :class="{ 'ring-2 ring-primary/30 border-primary/40': isStreamingAI }">
          <!-- Toolbar -->
          <div class="flex flex-wrap items-center gap-1 p-3 border-b border-border bg-muted/50">
            <button @mousedown.prevent="execCommand('bold')" :class="{ 'bg-primary/20 text-primary': activeFormats.bold }" class="p-2 rounded hover:bg-muted transition-colors" title="Gras">
              <Bold class="w-4 h-4" />
            </button>
            <button @mousedown.prevent="execCommand('italic')" :class="{ 'bg-primary/20 text-primary': activeFormats.italic }" class="p-2 rounded hover:bg-muted transition-colors" title="Italique">
              <Italic class="w-4 h-4" />
            </button>
            <button @mousedown.prevent="execCommand('underline')" :class="{ 'bg-primary/20 text-primary': activeFormats.underline }" class="p-2 rounded hover:bg-muted transition-colors" title="Souligné">
              <Underline class="w-4 h-4" />
            </button>
            <div class="w-px h-6 bg-border mx-1"></div>
            <button @mousedown.prevent="execCommand('insertUnorderedList')" :class="{ 'bg-primary/20 text-primary': activeFormats.insertUnorderedList }" class="p-2 rounded hover:bg-muted transition-colors" title="Liste à puces">
              <List class="w-4 h-4" />
            </button>
            <button @mousedown.prevent="execCommand('insertOrderedList')" :class="{ 'bg-primary/20 text-primary': activeFormats.insertOrderedList }" class="p-2 rounded hover:bg-muted transition-colors" title="Liste numérotée">
              <ListOrdered class="w-4 h-4" />
            </button>
          </div>
          <!-- Editor -->
          <div
            ref="editorRef"
            contenteditable="true"
            @input="onEditorInput"
            @mouseup="updateActiveFormats"
            @keyup="updateActiveFormats"
            class="min-h-[400px] max-h-[600px] overflow-y-auto p-4 outline-none prose prose-sm max-w-none transition-all"
            :class="{ 'cursor-not-allowed pointer-events-none': isStreamingAI }"
            placeholder="Rédigez ici votre rapport d'intervention complet...

Exemple de structure :

MOTIF DE L'INTERVENTION :
[Description du problème signalé par le client]

DIAGNOSTIC :
[Analyse technique et cause identifiée du problème]

TRAVAUX RÉALISÉS :
[Liste détaillée des actions effectuées]

MATÉRIEL UTILISÉ :
[Pièces remplacées, produits utilisés, etc.]

OBSERVATIONS ET RECOMMANDATIONS :
[Conseils au client, maintenance préventive suggérée, etc.]"
          ></div>
        </div>
      </section>

      <!-- Photos (Galerie + Caméra) -->
      <section class="bg-card border border-border rounded-xl p-6">
        <label class="block text-sm font-medium text-foreground mb-4">Photos d'intervention</label>

        <!-- Hidden inputs -->
        <input ref="fileInput" type="file" accept="image/*" multiple class="hidden" @change="handlePhotoUpload" />

        <!-- Camera interface -->
        <div v-if="isCameraActive" class="space-y-4 mb-6">
          <div class="relative bg-black rounded-lg overflow-hidden aspect-video border border-border shadow-inner">
            <video ref="videoRef" autoplay playsinline class="w-full h-full object-cover"></video>
          </div>
          <div class="flex gap-3">
            <button @click="capturePhoto" class="flex-1 bg-primary text-primary-foreground py-3 rounded-lg font-bold shadow-lg hover:shadow-primary/20 transition-all flex items-center justify-center gap-2">
              <Camera class="w-5 h-5" /> Capturer
            </button>
            <button @click="stopCamera" class="px-4 py-3 border border-border rounded-lg text-muted-foreground hover:bg-muted transition-colors">
              Annuler
            </button>
          </div>
        </div>

        <!-- Photo preview grid -->
        <div v-if="rapport.photos.length > 0" class="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
          <div v-for="(p, index) in rapport.photos" :key="index" class="relative group aspect-square bg-muted rounded-lg overflow-hidden border border-border">
            <img :src="p" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
            <button 
              @click="removePhoto(index)" 
              class="absolute top-2 right-2 w-7 h-7 bg-destructive text-white rounded-full flex items-center justify-center opacity-90 hover:opacity-100 hover:scale-110 transition-all shadow-lg"
              title="Supprimer cette photo"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="flex flex-wrap gap-3">
          <button @click="openGallery" class="inline-flex items-center gap-2 px-4 py-3 border border-border rounded-lg hover:bg-muted transition-colors">
            <ImageIcon class="w-5 h-5" />
            <span>{{ rapport.photos.length > 0 ? 'Ajouter une autre photo' : 'Choisir depuis la galerie' }}</span>
          </button>
          <button @click="openCamera" class="inline-flex items-center gap-2 px-4 py-3 border border-border rounded-lg hover:bg-muted transition-colors bg-blue-50/50 border-blue-200">
            <Camera class="w-5 h-5 text-blue-600" />
            <span class="text-blue-700">Prendre une photo</span>
          </button>
        </div>

        <p class="text-xs text-muted-foreground mt-4">
          Vous pouvez ajouter plusieurs photos de l'intervention. Elles apparaîtront à la fin du document PDF.
        </p>
      </section>
    </div>

    <!-- Footer actions -->
    <div v-if="!isLoading" class="flex items-center justify-between mt-8 pt-6 border-t sticky bottom-0 bg-background py-4">
      <button @click="router.push('/app/rapports')" class="px-4 py-2.5 rounded-lg font-medium text-muted-foreground hover:text-foreground transition-colors">Annuler</button>
      <button @click="saveRapport" :disabled="!isValid || isSaving || isStreamingAI" class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50">
        <Loader2 v-if="isStreamingAI" class="w-5 h-5 animate-spin" />
        <Save v-else class="w-5 h-5" />
        {{ isStreamingAI ? 'Génération en cours...' : isSaving ? 'Sauvegarde...' : (isEditMode ? 'Mettre à jour' : 'Sauvegarder le rapport') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
[contenteditable]:empty:before {
  content: attr(placeholder);
  color: #9ca3af;
  pointer-events: none;
  white-space: pre-wrap;
}
[contenteditable]:focus:empty:before {
  content: attr(placeholder);
}

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

/* Fade overlay transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
