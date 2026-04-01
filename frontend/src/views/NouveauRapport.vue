<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Save, FileDown, Bold, Italic, Underline, List, Plus, Trash2, Camera } from 'lucide-vue-next'

const router = useRouter()
const isSaving = ref(false)
const isGeneratingPDF = ref(false)

interface Rapport {
  id?: number
  nomEntreprise: string
  siret: string
  coordonneesAdresse: string
  coordonneesTelephone: string
  coordonneesEmail: string
  nomClient: string
  adresseIntervention: string
  contactClient: string
  dateIntervention: string
  heureDebut: string
  heureFin: string
  dureeTotale: string
  nomTechnicien: string
  motifIntervention: string
  diagnostic: string
  travauxRealises: string
  materielUtilise: string
  mainOeuvre: number
  deplacement: number
  materielFacturation: number
  totalHT: number
  tva: number
  totalTTC: number
  photos: string[]
  observations: string
  signatureClient: string
  signatureTechnicien: string
  statut: 'terminee' | 'partielle' | 'aSuivre'
  titre: string
  createdAt: string
}

const rapport = ref<Rapport>({
  nomEntreprise: '',
  siret: '',
  coordonneesAdresse: '',
  coordonneesTelephone: '',
  coordonneesEmail: '',
  nomClient: '',
  adresseIntervention: '',
  contactClient: '',
  dateIntervention: new Date().toISOString().split('T')[0],
  heureDebut: '',
  heureFin: '',
  dureeTotale: '',
  nomTechnicien: '',
  motifIntervention: '',
  diagnostic: '',
  travauxRealises: '',
  materielUtilise: '',
  mainOeuvre: 0,
  deplacement: 0,
  materielFacturation: 0,
  totalHT: 0,
  tva: 20,
  totalTTC: 0,
  photos: [],
  observations: '',
  signatureClient: '',
  signatureTechnicien: '',
  statut: 'terminee',
  titre: "RAPPORT D'INTERVENTION",
  createdAt: new Date().toISOString()
})

function calculerTotal() {
  const ht = rapport.value.mainOeuvre + rapport.value.deplacement + rapport.value.materielFacturation
  const tvaAmount = ht * (rapport.value.tva / 100)
  rapport.value.totalHT = ht
  rapport.value.totalTTC = ht + tvaAmount
}

const fileInput = ref<HTMLInputElement | null>(null)

function triggerFileUpload() {
  fileInput.value?.click()
}

function handlePhotoUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    Array.from(target.files).forEach(file => {
      const reader = new FileReader()
      reader.onload = (e) => {
        rapport.value.photos.push(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    })
  }
}

function removePhoto(index: number) {
  rapport.value.photos.splice(index, 1)
}

const isValid = computed(() => {
  return rapport.value.nomEntreprise.trim() &&
         rapport.value.nomClient.trim() &&
         rapport.value.dateIntervention &&
         rapport.value.nomTechnicien.trim()
})

const activeFormats = ref({ bold: false, italic: false, underline: false })

function execCommand(command: string, value: string | undefined = undefined) {
  document.execCommand(command, false, value)
  updateActiveFormats()
}

function updateActiveFormats() {
  activeFormats.value = {
    bold: document.queryCommandState('bold'),
    italic: document.queryCommandState('italic'),
    underline: document.queryCommandState('underline')
  }
}

function saveToLocalStorage() {
  const rapports = JSON.parse(localStorage.getItem('rapports') || '[]')
  const newRapport = { ...rapport.value, id: Date.now() }
  rapports.push(newRapport)
  localStorage.setItem('rapports', JSON.stringify(rapports))
  return newRapport
}

async function saveRapport() {
  if (!isValid.value) {
    alert('Veuillez remplir les champs obligatoires : Entreprise, Client, Date, Technicien')
    return
  }

  isSaving.value = true
  try {
    calculerTotal()
    saveToLocalStorage()
    router.push('/dashboard/rapports')
  } catch (e) {
    alert('Erreur lors de la sauvegarde')
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

  const statutLabel = {
    terminee: 'Terminée',
    partielle: 'Partielle',
    aSuivre: 'À suivre'
  }

  const photosHtml = rapport.value.photos.length > 0
    ? `<div class="section"><h2>Photos</h2><div class="photos-grid">${rapport.value.photos.map(photo => `<img src="${photo}" class="photo" />`).join('')}</div></div>`
    : ''

  const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <title>${rapport.value.titre}</title>
  <style>
    @page { margin: 15mm; size: A4; }
    body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.5; color: #1f2937; max-width: 210mm; margin: 0 auto; padding: 15px; background: white; font-size: 12px; }
    .header { text-align: center; margin-bottom: 20px; border-bottom: 3px solid #2563eb; padding-bottom: 15px; }
    .header h1 { color: #1f2937; margin: 0; font-size: 22px; font-weight: 700; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-top: 8px; }
    .badge-terminee { background: #dcfce7; color: #166534; }
    .badge-partielle { background: #fef3c7; color: #92400e; }
    .badge-aSuivre { background: #fee2e2; color: #991b1b; }
    .section { margin-bottom: 15px; page-break-inside: avoid; }
    .section h2 { color: #2563eb; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; margin-bottom: 8px; font-size: 13px; font-weight: 600; text-transform: uppercase; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .info-group { margin-bottom: 8px; }
    .info-label { font-size: 10px; color: #6b7280; text-transform: uppercase; font-weight: 600; }
    .info-value { font-size: 12px; color: #1f2937; }
    .facture-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    .facture-table th, .facture-table td { border: 1px solid #e5e7eb; padding: 6px 10px; text-align: left; font-size: 11px; }
    .facture-table th { background: #f3f4f6; font-weight: 600; }
    .facture-table .total-row { font-weight: 700; background: #f3f4f6; }
    .photos-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    .photo { width: 100%; height: 100px; object-fit: cover; border-radius: 4px; border: 1px solid #e5e7eb; }
    .signatures { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb; }
    .signature-box { border: 1px dashed #d1d5db; min-height: 80px; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #9ca3af; font-size: 11px; }
    .signature-label { text-align: center; margin-top: 8px; font-size: 11px; color: #6b7280; }
    .text-content { white-space: pre-wrap; font-size: 11px; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="header">
    <h1>${rapport.value.titre}</h1>
    <span class="badge badge-${rapport.value.statut}">${statutLabel[rapport.value.statut]}</span>
  </div>

  <div class="section">
    <h2>Informations générales</h2>
    <div class="grid-2">
      <div>
        <div class="info-group"><div class="info-label">Entreprise / Artisan</div><div class="info-value">${rapport.value.nomEntreprise || '-'}</div></div>
        <div class="info-group"><div class="info-label">SIRET</div><div class="info-value">${rapport.value.siret || '-'}</div></div>
        <div class="info-group"><div class="info-label">Coordonnées</div><div class="info-value">${rapport.value.coordonneesAdresse || '-'}<br/>${rapport.value.coordonneesTelephone || ''}<br/>${rapport.value.coordonneesEmail || ''}</div></div>
      </div>
      <div>
        <div class="info-group"><div class="info-label">Client</div><div class="info-value">${rapport.value.nomClient || '-'}</div></div>
        <div class="info-group"><div class="info-label">Adresse d'intervention</div><div class="info-value">${rapport.value.adresseIntervention || '-'}</div></div>
        <div class="info-group"><div class="info-label">Contact client</div><div class="info-value">${rapport.value.contactClient || '-'}</div></div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Détails de l'intervention</h2>
    <div class="grid-2">
      <div>
        <div class="info-group"><div class="info-label">Date</div><div class="info-value">${formatDate(rapport.value.dateIntervention)}</div></div>
        <div class="info-group"><div class="info-label">Heures</div><div class="info-value">De ${rapport.value.heureDebut || '--:--'} à ${rapport.value.heureFin || '--:--'}</div></div>
        <div class="info-group"><div class="info-label">Durée totale</div><div class="info-value">${rapport.value.dureeTotale || '-'}</div></div>
      </div>
      <div>
        <div class="info-group"><div class="info-label">Technicien</div><div class="info-value">${rapport.value.nomTechnicien || '-'}</div></div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Motif de l'intervention</h2>
    <div class="text-content">${rapport.value.motifIntervention || 'Non spécifié'}</div>
  </div>

  <div class="section">
    <h2>Diagnostic</h2>
    <div class="text-content">${rapport.value.diagnostic || 'Non spécifié'}</div>
  </div>

  <div class="section">
    <h2>Travaux réalisés</h2>
    <div class="text-content">${rapport.value.travauxRealises || 'Non spécifié'}</div>
  </div>

  <div class="section">
    <h2>Matériel utilisé</h2>
    <div class="text-content">${rapport.value.materielUtilise || 'Non spécifié'}</div>
  </div>

  <div class="section">
    <h2>Facturation</h2>
    <table class="facture-table">
      <tr><th>Description</th><th style="text-align:right">Montant</th></tr>
      <tr><td>Main d'œuvre</td><td style="text-align:right">${rapport.value.mainOeuvre.toFixed(2)} €</td></tr>
      <tr><td>Déplacement</td><td style="text-align:right">${rapport.value.deplacement.toFixed(2)} €</td></tr>
      <tr><td>Matériel</td><td style="text-align:right">${rapport.value.materielFacturation.toFixed(2)} €</td></tr>
      <tr><td><strong>Total HT</strong></td><td style="text-align:right"><strong>${rapport.value.totalHT.toFixed(2)} €</strong></td></tr>
      <tr><td>TVA (${rapport.value.tva}%)</td><td style="text-align:right">${(rapport.value.totalTTC - rapport.value.totalHT).toFixed(2)} €</td></tr>
      <tr class="total-row"><td><strong>Total TTC</strong></td><td style="text-align:right"><strong>${rapport.value.totalTTC.toFixed(2)} €</strong></td></tr>
    </table>
  </div>

  ${photosHtml}

  <div class="section">
    <h2>Observations & Recommandations</h2>
    <div class="text-content">${rapport.value.observations || 'Aucune observation'}</div>
  </div>

  <div class="signatures">
    <div>
      <div class="signature-box">${rapport.value.signatureClient ? `<img src="${rapport.value.signatureClient}" style="max-height:70px" />` : 'Signature client'}</div>
      <div class="signature-label">Signature du client</div>
    </div>
    <div>
      <div class="signature-box">${rapport.value.signatureTechnicien ? `<img src="${rapport.value.signatureTechnicien}" style="max-height:70px" />` : 'Signature technicien'}</div>
      <div class="signature-label">Signature du technicien</div>
    </div>
  </div>
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
    alert('Veuillez remplir les champs obligatoires')
    return
  }

  isSaving.value = true
  try {
    calculerTotal()
    saveToLocalStorage()
    generatePDF()
    router.push('/dashboard/rapports')
  } catch (e) {
    alert('Erreur lors de la sauvegarde')
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto pb-20">
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

    <div class="space-y-8">
      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">1. Informations de base *</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><label class="block text-sm font-medium text-foreground mb-1">Nom de l'entreprise / Artisan *</label><input v-model="rapport.nomEntreprise" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Votre entreprise" /></div>
          <div><label class="block text-sm font-medium text-foreground mb-1">SIRET</label><input v-model="rapport.siret" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="123 456 789 00012" /></div>
          <div><label class="block text-sm font-medium text-foreground mb-1">Adresse entreprise</label><input v-model="rapport.coordonneesAdresse" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="123 rue Example, 75000 Paris" /></div>
          <div class="grid grid-cols-2 gap-2">
            <div><label class="block text-sm font-medium text-foreground mb-1">Téléphone</label><input v-model="rapport.coordonneesTelephone" type="tel" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="01 23 45 67 89" /></div>
            <div><label class="block text-sm font-medium text-foreground mb-1">Email</label><input v-model="rapport.coordonneesEmail" type="email" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="contact@entreprise.fr" /></div>
          </div>
          <div><label class="block text-sm font-medium text-foreground mb-1">Nom du client *</label><input v-model="rapport.nomClient" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Nom du client" /></div>
          <div><label class="block text-sm font-medium text-foreground mb-1">Adresse d'intervention *</label><input v-model="rapport.adresseIntervention" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Adresse où l'intervention a lieu" /></div>
          <div class="md:col-span-2"><label class="block text-sm font-medium text-foreground mb-1">Contact client (tél/email)</label><input v-model="rapport.contactClient" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Contact direct du client" /></div>
        </div>
      </section>

      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">2. Détails de l'intervention</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div><label class="block text-sm font-medium text-foreground mb-1">Date *</label><input v-model="rapport.dateIntervention" type="date" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" /></div>
          <div><label class="block text-sm font-medium text-foreground mb-1">Heure début</label><input v-model="rapport.heureDebut" type="time" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" /></div>
          <div><label class="block text-sm font-medium text-foreground mb-1">Heure fin</label><input v-model="rapport.heureFin" type="time" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" /></div>
          <div><label class="block text-sm font-medium text-foreground mb-1">Durée totale</label><input v-model="rapport.dureeTotale" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="2h30" /></div>
          <div class="md:col-span-4"><label class="block text-sm font-medium text-foreground mb-1">Nom du technicien *</label><input v-model="rapport.nomTechnicien" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="Nom du technicien intervenant" /></div>
        </div>
      </section>

      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">11. Statut de l'intervention</h2>
        <div class="flex gap-4">
          <label class="flex items-center gap-2 cursor-pointer"><input v-model="rapport.statut" type="radio" value="terminee" class="w-4 h-4 text-primary" /><span class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">Terminée</span></label>
          <label class="flex items-center gap-2 cursor-pointer"><input v-model="rapport.statut" type="radio" value="partielle" class="w-4 h-4 text-primary" /><span class="px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700">Partielle</span></label>
          <label class="flex items-center gap-2 cursor-pointer"><input v-model="rapport.statut" type="radio" value="aSuivre" class="w-4 h-4 text-primary" /><span class="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">À suivre</span></label>
        </div>
      </section>

      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">3. Motif de l'intervention</h2>
        <textarea v-model="rapport.motifIntervention" rows="3" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none resize-none" placeholder="Fuite sous évier, Canalisation bouchée, Installation chauffe-eau..."></textarea>
      </section>

      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">4. Diagnostic (TRÈS important)</h2>
        <div class="border border-border rounded-lg overflow-hidden bg-background">
          <div class="flex items-center gap-1 p-2 border-b border-border bg-muted/50">
            <button @click="execCommand('bold')" :class="{ 'bg-primary/20 text-primary': activeFormats.bold }" class="p-2 rounded hover:bg-muted transition-colors"><Bold class="w-4 h-4" /></button>
            <button @click="execCommand('italic')" :class="{ 'bg-primary/20 text-primary': activeFormats.italic }" class="p-2 rounded hover:bg-muted transition-colors"><Italic class="w-4 h-4" /></button>
            <button @click="execCommand('underline')" :class="{ 'bg-primary/20 text-primary': activeFormats.underline }" class="p-2 rounded hover:bg-muted transition-colors"><Underline class="w-4 h-4" /></button>
            <div class="w-px h-6 bg-border mx-1"></div>
            <button @click="execCommand('insertUnorderedList')" class="p-2 rounded hover:bg-muted transition-colors"><List class="w-4 h-4" /></button>
          </div>
          <div contenteditable="true" v-html="rapport.diagnostic" @input="rapport.diagnostic = ($event.target as HTMLElement).innerHTML" @mouseup="updateActiveFormats" @keyup="updateActiveFormats" class="min-h-[120px] p-4 outline-none prose prose-sm max-w-none" placeholder="Cause du problème, état de l'installation, risques éventuels..."></div>
        </div>
      </section>

      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">5. Travaux réalisés</h2>
        <textarea v-model="rapport.travauxRealises" rows="4" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none resize-none" placeholder="Démontage, remplacement, nettoyage... Soyez précis : 'Remplacement du joint siphon Ø40 mm'"></textarea>
      </section>

      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">6. Matériel utilisé</h2>
        <textarea v-model="rapport.materielUtilise" rows="3" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none resize-none" placeholder="Pièces remplacées, produits utilisés..."></textarea>
      </section>

      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">7. Détail de la facturation</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div><label class="block text-sm font-medium text-foreground mb-1">Main d'œuvre (€)</label><input v-model.number="rapport.mainOeuvre" @input="calculerTotal" type="number" min="0" step="0.01" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" /></div>
          <div><label class="block text-sm font-medium text-foreground mb-1">Déplacement (€)</label><input v-model.number="rapport.deplacement" @input="calculerTotal" type="number" min="0" step="0.01" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" /></div>
          <div><label class="block text-sm font-medium text-foreground mb-1">Matériel (€)</label><input v-model.number="rapport.materielFacturation" @input="calculerTotal" type="number" min="0" step="0.01" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" /></div>
          <div><label class="block text-sm font-medium text-foreground mb-1">TVA (%)</label><input v-model.number="rapport.tva" @input="calculerTotal" type="number" min="0" max="100" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" /></div>
        </div>
        <div class="mt-4 p-4 bg-muted rounded-lg">
          <div class="flex justify-between items-center"><span class="text-sm text-muted-foreground">Total HT:</span><span class="font-semibold">{{ rapport.totalHT.toFixed(2) }} €</span></div>
          <div class="flex justify-between items-center mt-1"><span class="text-sm text-muted-foreground">TVA ({{ rapport.tva }}%):</span><span class="font-semibold">{{ (rapport.totalTTC - rapport.totalHT).toFixed(2) }} €</span></div>
          <div class="flex justify-between items-center mt-2 pt-2 border-t border-border"><span class="font-semibold">Total TTC:</span><span class="text-xl font-bold text-primary">{{ rapport.totalTTC.toFixed(2) }} €</span></div>
        </div>
      </section>

      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">8. Preuves (Photos)</h2>
        <input ref="fileInput" type="file" accept="image/*" multiple class="hidden" @change="handlePhotoUpload" />
        <button @click="triggerFileUpload" class="inline-flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"><Camera class="w-5 h-5" /> Ajouter des photos</button>
        <div v-if="rapport.photos.length > 0" class="grid grid-cols-3 md:grid-cols-4 gap-4 mt-4">
          <div v-for="(photo, index) in rapport.photos" :key="index" class="relative group">
            <img :src="photo" class="w-full h-24 object-cover rounded-lg border border-border" />
            <button @click="removePhoto(index)" class="absolute -top-2 -right-2 w-6 h-6 bg-destructive text-destructive-foreground rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"><Trash2 class="w-3 h-3" /></button>
          </div>
        </div>
      </section>

      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">9. Observations & Recommandations</h2>
        <textarea v-model="rapport.observations" rows="3" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none resize-none" placeholder="Installation vieillissante, réparation temporaire, remplacement conseillé..."></textarea>
      </section>

      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">10. Signatures</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div><label class="block text-sm font-medium text-foreground mb-2">Signature client (base64)</label><textarea v-model="rapport.signatureClient" rows="3" class="w-full px-3 py-2 bg-background border border-dashed border-input rounded-lg focus:ring-2 focus:ring-primary outline-none text-xs" placeholder="Collez une image base64 ou décrivez"></textarea></div>
          <div><label class="block text-sm font-medium text-foreground mb-2">Signature technicien (base64)</label><textarea v-model="rapport.signatureTechnicien" rows="3" class="w-full px-3 py-2 bg-background border border-dashed border-input rounded-lg focus:ring-2 focus:ring-primary outline-none text-xs" placeholder="Collez une image base64 ou décrivez"></textarea></div>
        </div>
      </section>

      <section class="bg-card border border-border rounded-xl p-6">
        <h2 class="text-lg font-semibold text-foreground mb-4">Titre du document PDF</h2>
        <input v-model="rapport.titre" type="text" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none" placeholder="RAPPORT D'INTERVENTION" />
        <p class="text-xs text-muted-foreground mt-1">Personnalisez le titre qui apparaîtra sur le PDF</p>
      </section>
    </div>

    <div class="flex items-center justify-between mt-8 pt-6 border-t sticky bottom-0 bg-background py-4">
      <button @click="router.push('/dashboard/rapports')" class="px-4 py-2.5 rounded-lg font-medium text-muted-foreground hover:text-foreground transition-colors">Annuler</button>
      <button @click="saveRapport" :disabled="!isValid || isSaving" class="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50">
        <Save class="w-5 h-5" /> {{ isSaving ? 'Sauvegarde...' : 'Sauvegarder le rapport' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
[contenteditable]:empty:before { content: attr(placeholder); color: #9ca3af; pointer-events: none; }
</style>
