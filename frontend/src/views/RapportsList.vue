<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, FileText, Calendar, Download, Trash2 } from 'lucide-vue-next'

interface Rapport {
  id: number
  titre: string
  nomEntreprise: string
  nomClient: string
  dateIntervention: string
  nomTechnicien: string
  statut: 'terminee' | 'partielle' | 'aSuivre'
  totalTTC: number
  createdAt: string
}

const router = useRouter()
const rapports = ref<Rapport[]>([])
const loading = ref(true)

function fetchRapports() {
  try {
    const stored = localStorage.getItem('rapports')
    rapports.value = stored ? JSON.parse(stored) : []
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

function deleteRapport(id: number) {
  if (!confirm('Êtes-vous sûr de vouloir supprimer ce rapport ?')) return
  
  rapports.value = rapports.value.filter(r => r.id !== id)
  localStorage.setItem('rapports', JSON.stringify(rapports.value))
}

function getStatutLabel(statut: string) {
  const labels: Record<string, string> = {
    terminee: 'Terminée',
    partielle: 'Partielle',
    aSuivre: 'À suivre'
  }
  return labels[statut] || statut
}

function getStatutClass(statut: string) {
  const classes: Record<string, string> = {
    terminee: 'bg-green-100 text-green-700',
    partielle: 'bg-yellow-100 text-yellow-700',
    aSuivre: 'bg-red-100 text-red-700'
  }
  return classes[statut] || 'bg-gray-100 text-gray-700'
}

function generateFullPDF(rapport: Rapport) {
  // Récupérer le rapport complet depuis localStorage
  const stored = localStorage.getItem('rapports')
  const allRapports = stored ? JSON.parse(stored) : []
  const fullRapport = allRapports.find((r: any) => r.id === rapport.id)
  
  if (!fullRapport) return
  
  const printWindow = window.open('', '_blank')
  if (!printWindow) return

  const formatDate = (dateString: string) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit', month: '2-digit', year: 'numeric'
    })
  }

  const statutLabel = {
    terminee: 'Terminée',
    partielle: 'Partielle',
    aSuivre: 'À suivre'
  }

  const r = fullRapport
  const photosHtml = r.photos?.length > 0
    ? `<div class="section"><h2>Photos</h2><div class="photos-grid">${r.photos.map((photo: string) => `<img src="${photo}" class="photo" />`).join('')}</div></div>`
    : ''

  const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <title>${r.titre}</title>
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
    <h1>${r.titre || "RAPPORT D'INTERVENTION"}</h1>
    <span class="badge badge-${r.statut}">${statutLabel[r.statut as keyof typeof statutLabel] || r.statut}</span>
  </div>

  <div class="section">
    <h2>Informations générales</h2>
    <div class="grid-2">
      <div>
        <div class="info-group"><div class="info-label">Entreprise / Artisan</div><div class="info-value">${r.nomEntreprise || '-'}</div></div>
        <div class="info-group"><div class="info-label">SIRET</div><div class="info-value">${r.siret || '-'}</div></div>
        <div class="info-group"><div class="info-label">Coordonnées</div><div class="info-value">${r.coordonneesAdresse || '-'}<br/>${r.coordonneesTelephone || ''}<br/>${r.coordonneesEmail || ''}</div></div>
      </div>
      <div>
        <div class="info-group"><div class="info-label">Client</div><div class="info-value">${r.nomClient || '-'}</div></div>
        <div class="info-group"><div class="info-label">Adresse d'intervention</div><div class="info-value">${r.adresseIntervention || '-'}</div></div>
        <div class="info-group"><div class="info-label">Contact client</div><div class="info-value">${r.contactClient || '-'}</div></div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Détails de l'intervention</h2>
    <div class="grid-2">
      <div>
        <div class="info-group"><div class="info-label">Date</div><div class="info-value">${formatDate(r.dateIntervention)}</div></div>
        <div class="info-group"><div class="info-label">Heures</div><div class="info-value">De ${r.heureDebut || '--:--'} à ${r.heureFin || '--:--'}</div></div>
        <div class="info-group"><div class="info-label">Durée totale</div><div class="info-value">${r.dureeTotale || '-'}</div></div>
      </div>
      <div>
        <div class="info-group"><div class="info-label">Technicien</div><div class="info-value">${r.nomTechnicien || '-'}</div></div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Motif de l'intervention</h2>
    <div class="text-content">${r.motifIntervention || 'Non spécifié'}</div>
  </div>

  <div class="section">
    <h2>Diagnostic</h2>
    <div class="text-content">${r.diagnostic || 'Non spécifié'}</div>
  </div>

  <div class="section">
    <h2>Travaux réalisés</h2>
    <div class="text-content">${r.travauxRealises || 'Non spécifié'}</div>
  </div>

  <div class="section">
    <h2>Matériel utilisé</h2>
    <div class="text-content">${r.materielUtilise || 'Non spécifié'}</div>
  </div>

  <div class="section">
    <h2>Facturation</h2>
    <table class="facture-table">
      <tr><th>Description</th><th style="text-align:right">Montant</th></tr>
      <tr><td>Main d'œuvre</td><td style="text-align:right">${(r.mainOeuvre || 0).toFixed(2)} €</td></tr>
      <tr><td>Déplacement</td><td style="text-align:right">${(r.deplacement || 0).toFixed(2)} €</td></tr>
      <tr><td>Matériel</td><td style="text-align:right">${(r.materielFacturation || 0).toFixed(2)} €</td></tr>
      <tr><td><strong>Total HT</strong></td><td style="text-align:right"><strong>${(r.totalHT || 0).toFixed(2)} €</strong></td></tr>
      <tr><td>TVA (${r.tva || 20}%)</td><td style="text-align:right">${((r.totalTTC || 0) - (r.totalHT || 0)).toFixed(2)} €</td></tr>
      <tr class="total-row"><td><strong>Total TTC</strong></td><td style="text-align:right"><strong>${(r.totalTTC || 0).toFixed(2)} €</strong></td></tr>
    </table>
  </div>

  ${photosHtml}

  <div class="section">
    <h2>Observations & Recommandations</h2>
    <div class="text-content">${r.observations || 'Aucune observation'}</div>
  </div>

  <div class="signatures">
    <div>
      <div class="signature-box">${r.signatureClient ? `<img src="${r.signatureClient}" style="max-height:70px" />` : 'Signature client'}</div>
      <div class="signature-label">Signature du client</div>
    </div>
    <div>
      <div class="signature-box">${r.signatureTechnicien ? `<img src="${r.signatureTechnicien}" style="max-height:70px" />` : 'Signature technicien'}</div>
      <div class="signature-label">Signature du technicien</div>
    </div>
  </div>
</body>
</html>`

  printWindow.document.write(htmlContent)
  printWindow.document.close()

  setTimeout(() => {
    printWindow.print()
  }, 500)
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
              <h3 class="text-lg font-semibold text-foreground truncate">{{ rapport.titre || "Rapport d'intervention" }}</h3>
              <span :class="getStatutClass(rapport.statut)" class="px-2 py-1 rounded-full text-xs font-medium">
                {{ getStatutLabel(rapport.statut) }}
              </span>
            </div>
            <div class="flex items-center gap-4 text-sm text-muted-foreground">
              <span class="flex items-center gap-1">
                <Calendar class="w-4 h-4" />
                {{ formatDate(rapport.dateIntervention) }}
              </span>
              <span>{{ rapport.nomClient }}</span>
              <span>{{ rapport.nomTechnicien }}</span>
            </div>
            <div class="mt-2 text-sm font-medium">
              Total: {{ (rapport.totalTTC || 0).toFixed(2) }} € TTC
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
              @click="deleteRapport(rapport.id)"
              class="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
              title="Supprimer"
            >
              <Trash2 class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
