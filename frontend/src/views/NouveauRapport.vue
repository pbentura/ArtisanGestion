<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { API_BASE_URL } from '@/lib/api'
import { ArrowLeft, Save, FileDown, Bold, Italic, Underline, List, ListOrdered, Image as ImageIcon, X, Camera } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const isSaving = ref(false)
const isGeneratingPDF = ref(false)
const isLoading = ref(false)

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
      router.push('/dashboard/rapports')
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


function onClientSelect() {
  if (selectedClientId.value) {
    const c = clients.value.find(cl => cl.id === selectedClientId.value)
    if (c) {
      rapport.value.nomClient = c.nom
      rapport.value.clientSiret = c.siret || ''
      rapport.value.adresseIntervention = c.adresse || ''
      rapport.value.clientCodePostal = c.code_postal || ''
      rapport.value.clientVille = c.ville || ''
      rapport.value.contactClient = c.telephone || ''
    }
  } else {
    // Si on désélectionne, on peut soit laisser, soit vider. 
    // Ici on laisse l'utilisateur vider lui-même ou on peut vider.
  }
}

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
    router.push('/dashboard/rapports')
  } catch (e: any) {
    console.error(e)
    alert('Erreur lors de la sauvegarde du rapport : ' + e.message)
  } finally {
    isSaving.value = false
  }
}

async function generatePDF(download = true) {
  isGeneratingPDF.value = true

  try {
    const pdfFormatDate = (dateString: string) => {
      return new Date(dateString).toLocaleDateString('fr-FR', {
        day: '2-digit', month: '2-digit', year: 'numeric'
      })
    }

    const adresseSociete = [societe.value.adresse, societe.value.code_postal, societe.value.ville]
      .filter(Boolean)
      .join(' ')

    const footerText = societe.value.texte_pied_page || ''

    const container = document.createElement('div')
    container.innerHTML = `
    <div style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; padding: 15px; background: white; font-size: 12px;">
      <div style="text-align: center; margin-bottom: 20px; border-bottom: 3px solid #2563eb; padding-bottom: 15px;">
        <h1 style="color: #1f2937; margin: 0; font-size: 22px; font-weight: 700;">${rapport.value.titre}</h1>
      </div>

      <div style="margin-bottom: 15px;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
          <div>
            <div style="margin-bottom: 10px;">
              <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Entreprise</div>
              <div style="font-size: 12px; color: #1f2937;">${societe.value.nom || '-'}${societe.value.siret ? ` (SIRET: ${societe.value.siret})` : ''}</div>
            </div>
            <div style="margin-bottom: 10px;">
              <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Coordonnées</div>
              <div style="font-size: 12px; color: #1f2937;">
                ${adresseSociete || '-'}<br/>
                ${societe.value.telephone ? `Tél: ${societe.value.telephone}<br/>` : ''}
                ${societe.value.email ? `Email: ${societe.value.email}` : ''}
              </div>
            </div>
          </div>
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
              <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">SIRET / SIREN</div>
              <div style="font-size: 12px; color: #1f2937;">${rapport.value.clientSiret}</div>
            </div>
            ` : ''}
          </div>
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <div style="margin-bottom: 10px;">
          <div style="font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Date d'intervention</div>
          <div style="font-size: 12px; color: #1f2937;">${pdfFormatDate(rapport.value.dateIntervention)}</div>
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
        const startY = pdf.internal.pageSize.getHeight() - 10
        lines.forEach((line: string, idx: number) => {
          pdf.text(line, pageWidth / 2, startY + (idx * 3.5), { align: 'center' })
        })
      }
    }

    if (download) {
      await worker.save()
    } else {
      const blob = await worker.output('blob')
      const url = URL.createObjectURL(blob)
      window.open(url, '_blank')
    }

    document.body.removeChild(container)
  } catch (e) {
    console.error('Erreur lors de la génération du PDF', e)
  } finally {
    isGeneratingPDF.value = false
  }
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
    router.push('/dashboard/rapports')
  } catch (e: any) {
    console.error(e)
    alert('Erreur lors de la sauvegarde du rapport : ' + e.message)
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto pb-20">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6 sticky top-0 bg-background/95 backdrop-blur z-10 py-4 border-b">
      <button @click="router.push('/dashboard/rapports')" class="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft class="w-5 h-5" /> Retour
      </button>
      <div class="flex items-center gap-3">
        <button @click="generatePDF(false)" :disabled="!isValid || isGeneratingPDF" class="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium border border-border bg-background text-foreground hover:bg-muted transition-colors disabled:opacity-50">
          <FileDown class="w-5 h-5" /> {{ isGeneratingPDF ? 'Génération...' : 'Aperçu PDF' }}
        </button>
        <button @click="saveAndGeneratePDF" :disabled="!isValid || isSaving" class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50">
          <Save class="w-5 h-5" /> {{ isSaving ? 'Sauvegarde...' : 'Sauvegarder & PDF' }}
        </button>
      </div>
    </div>

    <h1 class="text-2xl font-bold text-foreground mb-6">{{ isEditMode ? 'Modifier le Rapport' : 'Nouveau Rapport d\'Intervention' }}</h1>

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
        
        <div>
          <label class="block text-sm font-medium text-foreground mb-2">Choisir un client existant (Optionnel)</label>
          <select 
            v-model="selectedClientId" 
            @change="onClientSelect"
            class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none text-foreground"
          >
            <option :value="null">-- Nouveau client --</option>
            <option v-for="c in clients" :key="c.id" :value="c.id">
              {{ c.nom }} {{ c.ville ? `(${c.ville})` : '' }}
            </option>
          </select>
          <p class="text-[10px] text-muted-foreground mt-1">Sélectionnez un client pour remplir automatiquement ses informations</p>
        </div>

        <div class="h-px bg-border my-4"></div>

        <div>
          <label class="block text-sm font-medium text-foreground mb-2">Nom complet du client *</label>
          <input v-model="rapport.nomClient" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Nom du client" />
        </div>
        <div>
          <label class="block text-sm font-medium text-foreground mb-2">SIRET / SIREN</label>
          <input v-model="rapport.clientSiret" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Numéro SIRET ou SIREN" />
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
        <div>
          <label class="block text-sm font-medium text-foreground mb-2">Numéro de téléphone</label>
          <input v-model="rapport.contactClient" type="tel" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="06 XX XX XX XX" />
        </div>
      </section>

      <!-- Rich Editor complet -->
      <section class="bg-card border border-border rounded-xl p-6">
        <label class="block text-sm font-medium text-foreground mb-4">Contenu du rapport *</label>
        <div class="border border-border rounded-lg overflow-hidden bg-background">
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
            class="min-h-[400px] max-h-[600px] overflow-y-auto p-4 outline-none prose prose-sm max-w-none"
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
      <button @click="router.push('/dashboard/rapports')" class="px-4 py-2.5 rounded-lg font-medium text-muted-foreground hover:text-foreground transition-colors">Annuler</button>
      <button @click="saveRapport" :disabled="!isValid || isSaving" class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50">
        <Save class="w-5 h-5" /> {{ isSaving ? 'Sauvegarde...' : (isEditMode ? 'Mettre à jour' : 'Sauvegarder le rapport') }}
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
</style>
