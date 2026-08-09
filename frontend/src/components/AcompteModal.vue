<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { X, Loader2, Euro, Percent } from 'lucide-vue-next'
import { apiFetch } from '@/lib/api'
import { useRouter } from 'vue-router'

const props = defineProps<{
  isOpen: boolean
  devis: any
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'success', factureId: number): void
}>()

const router = useRouter()
const isSubmitting = ref(false)
const typeSaisie = ref<'pourcentage' | 'montant'>('pourcentage')
const valeurSaisie = ref<number | null>(30)

// Reset form when modal opens
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    typeSaisie.value = 'pourcentage'
    valeurSaisie.value = 30
    isSubmitting.value = false
  }
})

const totalDevisTTC = computed(() => {
  const total = props.devis?.lignes?.reduce((acc: number, l: any) => acc + (Number(l.total_ht) * (1 + Number(l.taux_tva) / 100)), 0) || Number(props.devis?.total_ttc) || 0
  return Number(total)
})

const montantAcompte = computed(() => {
  if (typeSaisie.value === 'pourcentage') {
    return Number((valeurSaisie.value || 0) * totalDevisTTC.value / 100)
  } else {
    return Number(valeurSaisie.value || 0)
  }
})

async function genererAcompte() {
  if (montantAcompte.value <= 0 || montantAcompte.value > totalDevisTTC.value) {
    alert("Le montant de l'acompte doit être supérieur à 0 et inférieur ou égal au total du devis.")
    return
  }

  isSubmitting.value = true
  try {
    const now = new Date()
    // Approximation du HT avec une TVA à 20% par défaut pour l'acompte (idéalement il faudrait faire un prorata)
    const prixUniteHt = montantAcompte.value / 1.2
    
    const factureData = {
      id_devis: props.devis.id,
      date_facture: now.toISOString().split('T')[0],
      numero_facture: `FAC-${now.toISOString().split('T')[0].replace(/-/g, '')}-${now.getHours().toString().padStart(2, '0')}${now.getMinutes().toString().padStart(2, '0')}`,
      titre_document_pdf: "FACTURE D'ACOMPTE",
      id_client: props.devis.client?.id || props.devis.id_client,
      objet_facture: `Acompte sur devis ${props.devis.numero_devis}`,
      nb_jours_echeance: 0,
      statut: 'brouillon',
      est_acompte: true,
      lignes: [
        {
          description: `Acompte de ${typeSaisie.value === 'pourcentage' ? valeurSaisie.value + '%' : valeurSaisie.value + '€'} sur le devis ${props.devis.numero_devis}`,
          quantite: 1,
          prix_unite_ht: prixUniteHt,
          taux_tva: 20, // Default 20%
          total_ht: prixUniteHt
        }
      ]
    }

    const res = await apiFetch('factures', {
      method: 'POST',
      body: JSON.stringify(factureData)
    })

    if (res.ok) {
      const created = await res.json()
      emit('success', created.id)
      emit('close')
      router.push(`/app/factures/${created.id}`)
    } else {
      const errorData = await res.json()
      alert(errorData.detail || "Erreur lors de la création de la facture d'acompte")
    }
  } catch (error) {
    console.error('Error generating acompte:', error)
    alert("Une erreur réseau est survenue.")
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-background/80 backdrop-blur-sm" @click="$emit('close')"></div>
    <div class="relative bg-card border border-border rounded-xl shadow-lg w-full max-w-md animate-in fade-in zoom-in duration-200">
      
      <!-- Header -->
      <div class="flex items-center justify-between p-4 sm:p-6 border-b border-border">
        <h2 class="text-xl font-bold text-foreground">Générer un acompte</h2>
        <button 
          @click="$emit('close')"
          class="p-2 text-muted-foreground hover:bg-muted rounded-full transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-4 sm:p-6 grid gap-6">
        <div>
          <p class="text-sm text-muted-foreground mb-4">
            Total du devis : <strong class="text-foreground">{{ totalDevisTTC.toFixed(2) }} € TTC</strong>
          </p>

          <!-- Segmented Control -->
          <div class="flex bg-muted rounded-lg p-1 mb-4">
            <button
              @click="typeSaisie = 'pourcentage'"
              class="flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-md text-sm font-medium transition-all"
              :class="typeSaisie === 'pourcentage' ? 'bg-background text-foreground shadow' : 'text-muted-foreground hover:text-foreground'"
            >
              <Percent class="w-4 h-4" />
              Pourcentage
            </button>
            <button
              @click="typeSaisie = 'montant'"
              class="flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-md text-sm font-medium transition-all"
              :class="typeSaisie === 'montant' ? 'bg-background text-foreground shadow' : 'text-muted-foreground hover:text-foreground'"
            >
              <Euro class="w-4 h-4" />
              Montant fixe
            </button>
          </div>

          <div class="grid gap-2">
            <label class="text-sm font-medium text-foreground">
              {{ typeSaisie === 'pourcentage' ? 'Pourcentage (%)' : 'Montant (€ TTC)' }}
            </label>
            <input 
              v-model.number="valeurSaisie" 
              type="number" 
              min="0"
              :max="typeSaisie === 'pourcentage' ? 100 : totalDevisTTC"
              class="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
            />
          </div>
        </div>

        <div class="bg-primary/5 border border-primary/20 rounded-lg p-4">
          <div class="flex justify-between items-center text-sm mb-1">
            <span class="text-muted-foreground">Montant de l'acompte :</span>
            <span class="font-semibold text-foreground">{{ montantAcompte.toFixed(2) }} € TTC</span>
          </div>
          <div class="flex justify-between items-center text-sm">
            <span class="text-muted-foreground">Reste à facturer (solde) :</span>
            <span class="text-muted-foreground">{{ (totalDevisTTC - montantAcompte).toFixed(2) }} € TTC</span>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end gap-3 p-4 sm:p-6 border-t border-border bg-muted/30">
        <button 
          @click="$emit('close')"
          class="px-4 py-2 text-sm font-medium border border-border rounded-lg hover:bg-muted transition-colors"
          :disabled="isSubmitting"
        >
          Annuler
        </button>
        <button 
          @click="genererAcompte"
          class="btn-primary"
          :disabled="isSubmitting"
        >
          <Loader2 v-if="isSubmitting" class="w-4 h-4 mr-2 animate-spin" />
          Créer la facture
        </button>
      </div>
      
    </div>
  </div>
</template>
