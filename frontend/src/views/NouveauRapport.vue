<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '@/lib/api'
import { ArrowLeft, Save, FileDown, Bold, Italic, Underline, List, ListOrdered, Image as ImageIcon, X, Camera } from 'lucide-vue-next'

const router = useRouter()
const isSaving = ref(false)
const isGeneratingPDF = ref(false)

// Données de la société
const societe = ref({
  nom: '',
  siret: '',
  adresse: '',
  code_postal: '',
  ville: '',
  telephone: '',
  email: ''
})

const clients = ref<any[]>([])
const selectedClientId = ref<number | null>(null)
const isCameraActive = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
let stream: MediaStream | null = null

async function loadClients() {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/clients/`, {
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
    rapport.value.photo = canvas.toDataURL('image/jpeg')
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

onMounted(() => {
  loadSociete()
  loadClients()
  // Initialize editor content once (don't use v-html)
  if (editorRef.value) {
    editorRef.value.innerHTML = rapport.value.contenu
  }
})

function onEditorInput() {
  if (editorRef.value) {
    rapport.value.contenu = editorRef.value.innerHTML
  }
}

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
  photo: string | null
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
  photo: null,
  createdAt: new Date().toISOString()
})

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
  if (target.files && target.files[0]) {
    const file = target.files[0]
    const reader = new FileReader()
    reader.onload = (e) => {
      rapport.value.photo = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

function removePhoto() {
  rapport.value.photo = null
  if (fileInput.value) fileInput.value.value = ''
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
    
    const res = await fetch(`${API_BASE_URL}/api/clients/`, {
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
    photo_url: rapport.value.photo || null,
    url_pdf: null
  }
  
  const res = await fetch(`${API_BASE_URL}/api/rapports/`, {
    method: 'POST',
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
    console.log("Rapport sauvegardé avec url_pdf (si présent):", savedRapport.url_pdf)
    
    generatePDF()
    router.push('/dashboard/rapports')
  } catch (e: any) {
    console.error(e)
    alert('Erreur lors de la sauvegarde du rapport : ' + e.message)
  } finally {
    isSaving.value = false
  }
}

function generatePDF() {
  isGeneratingPDF.value = true

  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    isGeneratingPDF.value = false
    return
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit', month: '2-digit', year: 'numeric'
    })
  }

  const adresseSociete = [societe.value.adresse, societe.value.code_postal, societe.value.ville]
    .filter(Boolean)
    .join(' ')

  const photoHtml = rapport.value.photo
    ? `<div class="section"><h2>Photo</h2><img src="${rapport.value.photo}" class="photo" /></div>`
    : ''

  const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <title>${rapport.value.titre}</title>
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
    <h1>${rapport.value.titre}</h1>
  </div>

  <div class="section societe-info">
    <div class="grid-2">
      <div>
        <div class="info-group">
          <div class="info-label">Entreprise</div>
          <div class="info-value">${societe.value.nom || '-'}${societe.value.siret ? ` (SIRET: ${societe.value.siret})` : ''}</div>
        </div>
        <div class="info-group">
          <div class="info-label">Coordonnées</div>
          <div class="info-value">
            ${adresseSociete || '-'}<br/>
            ${societe.value.telephone ? `Tél: ${societe.value.telephone}<br/>` : ''}
            ${societe.value.email ? `Email: ${societe.value.email}` : ''}
          </div>
        </div>
      </div>
      <div>
        <div class="info-group">
          <div class="info-label">Client</div>
          <div class="info-value"><strong>${rapport.value.nomClient || '-'}</strong></div>
        </div>
        <div class="info-group">
          <div class="info-label">Adresse d'intervention</div>
          <div class="info-value">
            ${rapport.value.adresseIntervention || '-'}<br/>
            ${[rapport.value.clientCodePostal, rapport.value.clientVille].filter(Boolean).join(' ')}${[rapport.value.clientCodePostal, rapport.value.clientVille].filter(Boolean).length > 0 ? '<br/>' : ''}
            ${rapport.value.contactClient ? `Tél: ${rapport.value.contactClient}` : ''}
          </div>
        </div>
        ${rapport.value.clientSiret ? `
        <div class="info-group">
          <div class="info-label">SIRET / SIREN</div>
          <div class="info-value">${rapport.value.clientSiret}</div>
        </div>
        ` : ''}
      </div>
    </div>
  </div>

  <div class="section">
    <div class="info-group">
      <div class="info-label">Date d'intervention</div>
      <div class="info-value">${formatDate(rapport.value.dateIntervention)}</div>
    </div>
  </div>

  <div class="section">
    <h2>Rapport d'intervention</h2>
    <div class="text-content">${rapport.value.contenu || '<p>Aucun contenu</p>'}</div>
  </div>

  ${photoHtml}
</body>
</html>`

  printWindow.document.write(htmlContent)
  printWindow.document.close()

  setTimeout(() => {
    printWindow.print()
    isGeneratingPDF.value = false
  }, 500)
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
    console.log("Rapport sauvegardé avec url_pdf (si présent):", savedRapport.url_pdf)
    
    generatePDF()
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
        <button @click="generatePDF" :disabled="!isValid || isGeneratingPDF" class="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium border border-border bg-background text-foreground hover:bg-muted transition-colors disabled:opacity-50">
          <FileDown class="w-5 h-5" /> {{ isGeneratingPDF ? 'Génération...' : 'Aperçu PDF' }}
        </button>
        <button @click="saveAndGeneratePDF" :disabled="!isValid || isSaving" class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50">
          <Save class="w-5 h-5" /> {{ isSaving ? 'Sauvegarde...' : 'Sauvegarder & PDF' }}
        </button>
      </div>
    </div>

    <h1 class="text-2xl font-bold text-foreground mb-6">Nouveau Rapport d'Intervention</h1>

    <div class="space-y-6">
      <!-- Date d'intervention -->
      <section class="bg-card border border-border rounded-xl p-6">
        <label class="block text-sm font-medium text-foreground mb-2">Date d'intervention *</label>
        <input v-model="rapport.dateIntervention" type="date" class="w-full max-w-xs px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" />
      </section>

      <!-- Titre du document PDF -->
      <section class="bg-card border border-border rounded-xl p-6">
        <label class="block text-sm font-medium text-foreground mb-2">Titre du document PDF *</label>
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

      <!-- Photo (Galerie + Caméra) -->
      <section class="bg-card border border-border rounded-xl p-6">
        <label class="block text-sm font-medium text-foreground mb-4">Photo</label>

        <!-- Hidden inputs -->
        <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handlePhotoUpload" />

        <!-- Camera interface -->
        <div v-if="isCameraActive" class="space-y-4">
          <div class="relative bg-black rounded-lg overflow-hidden aspect-video border border-border shadow-inner">
            <video ref="videoRef" autoplay playsinline class="w-full h-full object-cover"></video>
          </div>
          <div class="flex gap-3">
            <button @click="capturePhoto" class="flex-1 bg-primary text-primary-foreground py-3 rounded-lg font-bold shadow-lg hover:shadow-primary/20 transition-all flex items-center justify-center gap-2">
              <Camera class="w-5 h-5" /> Capturer la photo
            </button>
            <button @click="stopCamera" class="px-4 py-3 border border-border rounded-lg text-muted-foreground hover:bg-muted transition-colors">
              Annuler
            </button>
          </div>
        </div>

        <!-- Buttons -->
        <div v-else-if="!rapport.photo" class="flex flex-wrap gap-3">
          <button @click="openGallery" class="inline-flex items-center gap-2 px-4 py-3 border border-border rounded-lg hover:bg-muted transition-colors">
            <ImageIcon class="w-5 h-5" />
            <span>Choisir depuis la galerie</span>
          </button>
          <button @click="openCamera" class="inline-flex items-center gap-2 px-4 py-3 border border-border rounded-lg hover:bg-muted transition-colors bg-blue-50/50 border-blue-200">
            <Camera class="w-5 h-5 text-blue-600" />
            <span class="text-blue-700">Prendre une photo</span>
          </button>
        </div>

        <!-- Photo preview -->
        <div v-else class="relative inline-block">
          <img :src="rapport.photo" class="max-w-full max-h-80 object-contain rounded-lg border border-border" />
          <button @click="removePhoto" class="absolute -top-2 -right-2 w-8 h-8 bg-destructive text-destructive-foreground rounded-full flex items-center justify-center hover:bg-destructive/90 transition-colors shadow-md">
            <X class="w-4 h-4" />
          </button>
        </div>

        <p class="text-xs text-muted-foreground mt-2">Ajoutez une photo de l'intervention ou du matériel installé</p>
      </section>
    </div>

    <!-- Footer actions -->
    <div class="flex items-center justify-between mt-8 pt-6 border-t sticky bottom-0 bg-background py-4">
      <button @click="router.push('/dashboard/rapports')" class="px-4 py-2.5 rounded-lg font-medium text-muted-foreground hover:text-foreground transition-colors">Annuler</button>
      <button @click="saveRapport" :disabled="!isValid || isSaving" class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50">
        <Save class="w-5 h-5" /> {{ isSaving ? 'Sauvegarde...' : 'Sauvegarder le rapport' }}
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
