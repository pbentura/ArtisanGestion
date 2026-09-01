 <script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '@/lib/api'
import { useWebSocket } from '@/composables/useWebSocket'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { 
  Building2, MapPin, Landmark, CheckCircle2, Search,
  ChevronRight, ArrowLeft, Upload, Loader2, X, RefreshCw, Hash
} from 'lucide-vue-next'

import { Capacitor } from '@capacitor/core'
import { App } from '@capacitor/app'

const router = useRouter()
const { wsEvents } = useWebSocket()

const steps = [
  { id: 1, title: 'Recherche', subtitle: 'Trouvez votre entreprise', icon: Search },
  { id: 2, title: 'Identité', subtitle: 'Parlons de votre entreprise', icon: Building2 },
  { id: 3, title: 'Coordonnées', subtitle: 'Pour vous joindre facilement', icon: MapPin },
  { id: 4, title: 'Banque & Paramètres', subtitle: 'Pour vos paiements et factures', icon: Landmark },
  { id: 5, title: 'Récapitulatif', subtitle: 'Vérifiez avant de valider', icon: CheckCircle2 }
]

const currentStep = ref(1)
const isLoading = ref(false)

const formeJuridiques = ['Auto-entrepreneur', 'SASU', 'SAS', 'SARL', 'EURL', 'EI']

const form = ref({
  nom: '',
  forme_juridique: 'Auto-entrepreneur',
  logo: '',
  adresse: '',
  code_postal: '',
  ville: '',
  telephone: '',
  email: '',
  siret: '',
  rcs: '',
  tva_intracommunautaire: '',
  capital_social: '',
  tva_defaut: '',
  iban: '',
  bic: '',
  nom_banque: '',
  objectif_mensuel_ca: '',
  texte_pied_page: ''
})

const isFooterManuallyEdited = ref(false)

function generateDefaultFooter() {
  const parts = []
  if (form.value.nom) parts.push(form.value.nom)
  
  const adresseLines = []
  if (form.value.adresse) adresseLines.push(form.value.adresse)
  const cpVille = [form.value.code_postal, form.value.ville].filter(Boolean).join(' ')
  if (cpVille) adresseLines.push(cpVille)
  if (adresseLines.length > 0) parts.push(adresseLines.join(', '))

  const contact = []
  if (form.value.telephone) contact.push(`Tél : ${form.value.telephone}`)
  if (form.value.email) contact.push(`Email : ${form.value.email}`)
  if (contact.length > 0) parts.push(contact.join(' - '))

  if (form.value.siret) parts.push(`SIRET : ${form.value.siret}`)

  return parts.join('\n')
}

watch(
  () => [
    form.value.nom, 
    form.value.adresse, 
    form.value.code_postal, 
    form.value.ville, 
    form.value.telephone, 
    form.value.email, 
    form.value.siret
  ],
  () => {
    if (!isFooterManuallyEdited.value) {
      form.value.texte_pied_page = generateDefaultFooter()
    }
  }
)

let saveTimeout: ReturnType<typeof setTimeout> | null = null

let isUpdatingFromWS = false

onMounted(async () => {
  try {
    const res = await apiFetch('users/me')
    if (res.ok) {
      const data = await res.json()
      if (data.onboarding_draft) {
        isUpdatingFromWS = true
        form.value = { ...form.value, ...data.onboarding_draft }
        if (form.value.siret && form.value.nom) {
          siretFound.value = true
        }
        setTimeout(() => { isUpdatingFromWS = false }, 100)
      }
    }
  } catch (e) {
    console.error('Failed to fetch draft from API.', e)
  }

  // Écoute de la synchronisation du brouillon
  wsEvents.on('SYNC_DRAFT', (newDraft: any) => {
    if (newDraft) {
      isUpdatingFromWS = true
      form.value = { ...form.value, ...newDraft }
      if (form.value.siret && form.value.nom) {
        siretFound.value = true
      }
      // Désactiver le flag après que le watcher ait pu ignorer cette modification
      setTimeout(() => { isUpdatingFromWS = false }, 100)
    }
  })

  // Écoute de la validation finale depuis un autre appareil
  wsEvents.on('SYNC_SOCIETE', () => {
    // Si la société a été créée sur un autre appareil, on redirige vers l'app
    router.push('/app')
  })

  // Synchronisation au retour au premier plan (si l'app était en arrière-plan)
  const syncState = async () => {
    try {
      const res = await apiFetch('users/me')
      if (res.ok) {
        const data = await res.json()
        
        // Vérifier si la société a été créée entre temps
        if (data.societes && data.societes.length > 0) {
          router.push('/app')
          return
        }
        
        // Sinon, récupérer le dernier brouillon
        if (data.onboarding_draft) {
          isUpdatingFromWS = true
          form.value = { ...form.value, ...data.onboarding_draft }
          if (form.value.siret && form.value.nom) {
            siretFound.value = true
          }
          setTimeout(() => { isUpdatingFromWS = false }, 100)
        }
      }
    } catch (e) {
      console.error('Failed to sync state.', e)
    }
  }

  if (Capacitor.isNativePlatform()) {
    App.addListener('appStateChange', ({ isActive }) => {
      if (isActive) syncState()
    })
  } else {
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') syncState()
    })
  }
})

import { onUnmounted } from 'vue'

onUnmounted(() => {
  wsEvents.off('SYNC_DRAFT')
  wsEvents.off('SYNC_SOCIETE')
  document.removeEventListener('visibilitychange', () => {})
})

watch(form, (newVal) => {
  if (isUpdatingFromWS) return // Ne pas renvoyer les données si on vient de les recevoir via WS

  if (saveTimeout) clearTimeout(saveTimeout)
  saveTimeout = setTimeout(async () => {
    try {
      const res = await apiFetch('users/me', {
        method: 'PATCH',
        body: JSON.stringify({ onboarding_draft: newVal })
      })
      if (res.ok) {
        const data = await res.json()
        if (data.societes && data.societes.length > 0) {
          router.push('/app')
        }
      }
    } catch (e) {
      console.error('Failed to save draft to API.', e)
    }
  }, 1000)
}, { deep: true })

const isAutoEntrepreneur = computed(() => form.value.forme_juridique === 'Auto-entrepreneur')

const searchMode = ref<'nom' | 'siret'>('nom')
const searchNameQuery = ref('')
const searchPostalCode = ref('')
const isSearching = ref(false)
const searchResults = ref<any[]>([])
const searchError = ref('')
const hasSearched = ref(false)
const siretFound = ref(false)

function selectEnterprise(item: any) {
  form.value.nom = item.nom || ''
  form.value.siret = item.siret || ''
  form.value.adresse = item.adresse || ''
  form.value.code_postal = item.code_postal || ''
  form.value.ville = item.ville || ''
  
  if (item.forme_juridique) {
    form.value.forme_juridique = item.forme_juridique
  }
  if (item.ville && item.forme_juridique !== 'Auto-entrepreneur') {
    form.value.rcs = `RCS ${item.ville}`
  }
  if (item.tva_intracommunautaire) {
    form.value.tva_intracommunautaire = item.tva_intracommunautaire
  }
  
  siretFound.value = true
  searchError.value = ''
}

function resetSelection() {
  siretFound.value = false
}

async function searchByName() {
  const query = searchNameQuery.value.trim()
  if (query.length < 2) {
    searchError.value = "Veuillez saisir au moins 2 caractères pour le nom d'entreprise."
    return
  }
  
  isSearching.value = true
  searchError.value = ''
  hasSearched.value = true
  searchResults.value = []
  
  try {
    const params = new URLSearchParams({ q: query, per_page: '10' })
    if (searchPostalCode.value.trim()) {
      params.append('code_postal', searchPostalCode.value.trim())
    }
    
    const response = await apiFetch(`societes/search-sirene?${params.toString()}`)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || "Erreur lors de la recherche des entreprises")
    }
    
    const data = await response.json()
    searchResults.value = data.results || []
    if (searchResults.value.length === 0) {
      searchError.value = "Aucune entreprise trouvée avec ces critères. Vérifiez l'orthographe ou essayez avec votre code postal ou votre numéro SIRET."
    }
  } catch (e: any) {
    searchError.value = e.message || "Impossible de joindre le service Sirene."
  } finally {
    isSearching.value = false
  }
}

async function searchSiret() {
  const siretClean = form.value.siret.replace(/\s+/g, '')
  if (siretClean.length !== 14) {
    searchError.value = "Le SIRET doit contenir exactement 14 chiffres."
    return
  }
  
  isSearching.value = true
  searchError.value = ''
  hasSearched.value = true
  
  try {
    const response = await apiFetch(`societes/search-sirene?q=${siretClean}`)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || "Erreur réseau")
    }
    
    const data = await response.json()
    const results = data.results || []
    
    if (results.length > 0) {
      selectEnterprise(results[0])
    } else {
      searchError.value = "Ce SIRET est introuvable dans la base INSEE."
      siretFound.value = false
    }
  } catch (e: any) {
    searchError.value = e.message || "Impossible de contacter l'API Sirene."
    siretFound.value = false
  } finally {
    isSearching.value = false
  }
}

const isStepValid = computed(() => {
  if (currentStep.value === 1) return siretFound.value
  if (currentStep.value === 2) return !!form.value.nom.trim()
  if (currentStep.value === 3) return !!form.value.email.trim() && !!form.value.adresse.trim() && !!form.value.ville.trim()
  if (currentStep.value === 4) return true // Optional fields
  return true
})

function nextStep() {
  // Optionnel : vérifier manuellement si la société a été créée entre temps
  apiFetch('users/me').then(res => {
    if (res.ok) {
      res.json().then(data => {
        if (data.societes && data.societes.length > 0) router.push('/app')
      })
    }
  }).catch(() => {})

  if (currentStep.value < 5 && isStepValid.value) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--
  } else {
    router.push('/')
  }
}

async function submitForm() {
  isLoading.value = true
  const token = localStorage.getItem('token')
  
  if (!token) {
    router.push('/auth')
    return
  }

  const sanitizedForm = Object.fromEntries(
    Object.entries(form.value).map(([key, value]) => [key, value === '' ? null : value])
  )

  try {
    const res = await apiFetch('societes', {
      method: 'POST',
      body: JSON.stringify(sanitizedForm)
    })

    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(errorData.detail || "Erreur lors de la création de l'entreprise")
    }

    // Clear draft on backend
    try {
      await apiFetch('users/me', {
        method: 'PATCH',
        body: JSON.stringify({ onboarding_draft: null })
      })
    } catch(e) {
      console.error('Failed to clear draft on API.', e)
    }

    router.push('/app')
  } catch (error: any) {
    alert(error.message)
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const fileInput = ref<HTMLInputElement | null>(null)

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]
    if (file.size > 2 * 1024 * 1024) {
      alert("Le fichier est trop volumineux (max 2MB)")
      return
    }
    const reader = new FileReader()
    reader.onload = (e) => {
      form.value.logo = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    const file = event.dataTransfer.files[0]
    if (file.type.startsWith('image/')) {
      if (file.size > 2 * 1024 * 1024) {
        alert("Le fichier est trop volumineux (max 2MB)")
        return
      }
      const reader = new FileReader()
      reader.onload = (e) => {
        form.value.logo = e.target?.result as string
      }
      reader.readAsDataURL(file)
    }
  }
}

function removeLogo() {
  form.value.logo = ''
  if (fileInput.value) fileInput.value.value = ''
}
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col items-center pb-6 px-4 sm:px-6 lg:px-8 pt-20 sm:pt-24">
    
    <!-- Top Header Navigation -->
    <div class="w-full max-w-3xl flex justify-between items-center mb-8">
      <Button variant="ghost" size="sm" @click="prevStep" class="text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft class="w-4 h-4 mr-2" />
        {{ currentStep === 1 ? 'Annuler' : 'Retour' }}
      </Button>
      <div class="text-sm font-medium text-muted-foreground">
        Étape {{ currentStep }} sur 5
      </div>
    </div>

    <!-- Main Container -->
    <div class="w-full max-w-2xl flex-1 flex flex-col justify-center pb-24 lg:pb-12">
      
      <!-- Progress Bar -->
      <div class="mb-10 w-full bg-secondary/30 h-1.5 rounded-full overflow-hidden">
        <div 
          class="h-full bg-primary transition-all duration-500 ease-out rounded-full"
          :style="{ width: `${(currentStep / 5) * 100}%` }" />
      </div>

      <!-- Header area depends on step -->
      <div class="mb-8 text-center sm:text-left">
        <div class="inline-flex items-center justify-center p-3 sm:p-4 rounded-xl bg-primary/10 text-primary mb-4 shadow-inner shadow-primary/20">
          <component :is="steps[currentStep - 1].icon" class="w-6 h-6 sm:w-8 sm:h-8" />
        </div>
        <h1 class="text-3xl sm:text-4xl font-extrabold text-foreground tracking-tight mb-2">
          {{ steps[currentStep - 1].title }}
        </h1>
        <p class="text-base sm:text-lg text-muted-foreground">
          {{ steps[currentStep - 1].subtitle }}
        </p>
      </div>

      <!-- Form Content -->
      <Card class="border-border/50 shadow-xl overflow-hidden focus-within:ring-1 focus-within:ring-primary/20 transition-all">
        <CardContent class="p-6 sm:p-8">
          <transition name="slide-fade" mode="out-in">
            <!-- Step 1: Recherche -->
            <div v-if="currentStep === 1" key="step1" class="space-y-6">
              
              <!-- Si entreprise trouvée / sélectionnée -->
              <div v-if="siretFound" class="space-y-4">
                <div class="p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 dark:bg-emerald-950/20 dark:border-emerald-800/40 text-foreground transition-all">
                  <div class="flex items-start justify-between gap-3">
                    <div class="flex items-start gap-3.5">
                      <div class="p-2.5 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0">
                        <CheckCircle2 class="w-6 h-6" />
                      </div>
                      <div class="space-y-1">
                        <div class="flex items-center gap-2 flex-wrap">
                          <span class="text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                            Entreprise sélectionnée
                          </span>
                          <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/20 text-emerald-700 dark:text-emerald-300">
                            {{ form.forme_juridique || 'Entreprise' }}
                          </span>
                        </div>
                        <h3 class="text-xl font-bold text-foreground">
                          {{ form.nom }}
                        </h3>
                        <p v-if="form.adresse || form.ville" class="text-sm text-muted-foreground flex items-center gap-1.5 pt-0.5">
                          <MapPin class="w-4 h-4 flex-shrink-0 text-muted-foreground" />
                          <span>{{ [form.adresse, [form.code_postal, form.ville].filter(Boolean).join(' ')].filter(Boolean).join(', ') }}</span>
                        </p>
                        <div class="pt-2 flex items-center gap-2 flex-wrap text-xs text-muted-foreground">
                          <span class="font-mono bg-background/80 px-2.5 py-1 rounded-md border border-border/60">
                            SIRET : {{ form.siret }}
                          </span>
                          <span v-if="form.rcs" class="bg-background/80 px-2.5 py-1 rounded-md border border-border/60">
                            {{ form.rcs }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
                  <p class="text-xs text-muted-foreground">
                    Vos informations sont prêtes. Cliquez sur <strong>Continuer</strong> pour vérifier l'identité et les coordonnées.
                  </p>
                  <Button variant="outline" size="sm" @click="resetSelection" class="flex-shrink-0 text-xs">
                    <RefreshCw class="w-3.5 h-3.5 mr-1.5" />
                    Changer d'entreprise
                  </Button>
                </div>
              </div>

              <!-- Si aucune entreprise sélectionnée : Interface de recherche -->
              <div v-else class="space-y-5">
                <!-- Sélecteur de mode de recherche -->
                <div class="flex p-1 bg-muted/60 rounded-xl border border-border/40">
                  <button 
                    type="button"
                    @click="searchMode = 'nom'; searchError = ''"
                    class="flex-1 py-2 px-3 text-sm font-medium rounded-lg transition-all flex items-center justify-center gap-2"
                    :class="searchMode === 'nom' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
                  >
                    <Building2 class="w-4 h-4" />
                    <span>Recherche par nom</span>
                  </button>
                  <button 
                    type="button"
                    @click="searchMode = 'siret'; searchError = ''"
                    class="flex-1 py-2 px-3 text-sm font-medium rounded-lg transition-all flex items-center justify-center gap-2"
                    :class="searchMode === 'siret' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
                  >
                    <Hash class="w-4 h-4" />
                    <span>Recherche par SIRET</span>
                  </button>
                </div>

                <!-- Mode 1: Recherche par Nom -->
                <div v-if="searchMode === 'nom'" class="space-y-4">
                  <div class="space-y-2">
                    <Label for="searchName" class="text-foreground font-medium">
                      Nom de l'entreprise ou votre nom d'artisan <span class="text-destructive">*</span>
                    </Label>
                    <Input 
                      id="searchName"
                      v-model="searchNameQuery" 
                      placeholder="Ex : Menuiserie Martin, Dupont Plomberie..." 
                      class="h-12 text-base bg-background hover:bg-muted/20 focus:bg-background transition-all" 
                      @keyup.enter="searchByName"
                    />
                  </div>

                  <div class="space-y-2">
                    <Label for="searchCP" class="text-foreground font-medium flex items-center justify-between">
                      <span>Code postal ou ville <span class="text-xs font-normal text-muted-foreground">(optionnel, affine les résultats)</span></span>
                    </Label>
                    <div class="flex flex-col sm:flex-row gap-3">
                      <Input 
                        id="searchCP"
                        v-model="searchPostalCode" 
                        placeholder="Ex : 75011, Toulouse, 33..." 
                        class="h-12 text-base bg-background hover:bg-muted/20 focus:bg-background flex-1" 
                        @keyup.enter="searchByName"
                      />
                      <Button 
                        @click="searchByName" 
                        :disabled="isSearching || searchNameQuery.trim().length < 2" 
                        class="h-12 px-6 sm:w-auto w-full font-medium"
                      >
                        <Loader2 v-if="isSearching" class="w-4 h-4 mr-2 animate-spin" />
                        <Search v-else class="w-4 h-4 mr-2" />
                        Rechercher
                      </Button>
                    </div>
                  </div>

                  <!-- Message d'erreur -->
                  <p v-if="searchError" class="text-sm text-destructive mt-2">{{ searchError }}</p>

                  <!-- État de chargement -->
                  <div v-if="isSearching" class="py-8 flex flex-col items-center justify-center space-y-3 text-center">
                    <Loader2 class="w-8 h-8 animate-spin text-primary" />
                    <p class="text-sm text-muted-foreground">Recherche en cours dans la base officielle INSEE Sirene...</p>
                  </div>

                  <!-- Liste des propositions d'entreprises -->
                  <div v-else-if="searchResults.length > 0" class="space-y-3 pt-2">
                    <div class="flex items-center justify-between pb-1">
                      <p class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                        {{ searchResults.length }} résultat{{ searchResults.length > 1 ? 's trouvés' : ' trouvé' }} — Cliquez sur le vôtre :
                      </p>
                    </div>

                    <div class="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
                      <div 
                        v-for="(item, idx) in searchResults" 
                        :key="item.siret || idx"
                        @click="selectEnterprise(item)"
                        class="group p-4 rounded-xl border border-border/70 hover:border-primary/60 bg-card hover:bg-primary/5 cursor-pointer transition-all duration-200 shadow-sm hover:shadow flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                      >
                        <div class="space-y-1.5 flex-1 min-w-0">
                          <div class="flex items-center gap-2 flex-wrap">
                            <span class="font-bold text-foreground group-hover:text-primary transition-colors text-base truncate">
                              {{ item.nom }}
                            </span>
                            <span 
                              v-if="item.etat_administratif === 'A'"
                              class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium bg-emerald-500/15 text-emerald-700 dark:text-emerald-400"
                            >
                              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                              Actif
                            </span>
                            <span 
                              v-else
                              class="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium bg-muted text-muted-foreground"
                            >
                              Fermé
                            </span>
                            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-secondary text-secondary-foreground">
                              {{ item.forme_juridique }}
                            </span>
                          </div>

                          <div class="flex items-center gap-1 text-xs text-muted-foreground truncate">
                            <MapPin class="w-3.5 h-3.5 flex-shrink-0 text-muted-foreground" />
                            <span class="truncate">{{ [item.adresse, [item.code_postal, item.ville].filter(Boolean).join(' ')].filter(Boolean).join(', ') }}</span>
                          </div>

                          <div class="flex items-center gap-3 text-xs text-muted-foreground flex-wrap pt-0.5">
                            <span class="font-mono bg-muted/60 px-1.5 py-0.5 rounded text-[11px]">
                              SIRET : {{ item.siret }}
                            </span>
                            <span v-if="item.dirigeants && item.dirigeants.length > 0" class="text-[11px] text-muted-foreground">
                              Dirigeant : {{ item.dirigeants[0].nom }}
                            </span>
                          </div>
                        </div>

                        <Button 
                          size="sm" 
                          variant="outline" 
                          class="group-hover:bg-primary group-hover:text-primary-foreground group-hover:border-primary transition-all flex-shrink-0 self-end sm:self-center text-xs font-medium"
                        >
                          Sélectionner
                          <ChevronRight class="w-4 h-4 ml-1" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Mode 2: Recherche par SIRET -->
                <div v-else-if="searchMode === 'siret'" class="space-y-4">
                  <div class="space-y-2">
                    <Label for="siret" class="text-foreground font-medium">
                      Numéro SIRET (14 chiffres) <span class="text-destructive">*</span>
                    </Label>
                    <div class="flex flex-col sm:flex-row gap-3">
                      <Input 
                        id="siret" 
                        v-model="form.siret" 
                        placeholder="Ex : 123 456 789 00012" 
                        class="h-12 text-base transition-all bg-background hover:bg-muted/20 focus:bg-background flex-1" 
                        @keyup.enter="searchSiret"
                        @input="siretFound = false"
                      />
                      <Button 
                        @click="searchSiret" 
                        :disabled="isSearching || form.siret.replace(/\s+/g, '').length < 14" 
                        class="h-12 px-6 sm:w-auto w-full font-medium"
                      >
                        <Loader2 v-if="isSearching" class="w-4 h-4 mr-2 animate-spin" />
                        <Search v-else class="w-4 h-4 mr-2" />
                        Rechercher
                      </Button>
                    </div>
                    <p v-if="searchError" class="text-sm text-destructive mt-2">{{ searchError }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 2: Identité -->
            <div v-else-if="currentStep === 2" key="step2" class="space-y-6">
              <div class="space-y-2">
                <Label for="nom" class="text-foreground">Nom de l'entreprise <span class="text-destructive">*</span></Label>
                <Input id="nom" v-model="form.nom" placeholder="Ex: Menuiserie Dupont" class="h-12 text-base transition-all bg-background hover:bg-muted/20 focus:bg-background" />
              </div>
              
              <div class="space-y-3">
                <Label class="text-foreground">Forme juridique <span class="text-destructive">*</span></Label>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                  <div 
                    v-for="fj in formeJuridiques" :key="fj"
                    @click="form.forme_juridique = fj"
                    class="border rounded-xl p-3 text-center cursor-pointer transition-all duration-200"
                    :class="form.forme_juridique === fj ? 'bg-primary/10 border-primary text-primary font-semibold ring-1 ring-primary/20 shadow-sm' : 'border-border text-muted-foreground hover:bg-muted/50 hover:border-muted-foreground/30'"
                  >
                    {{ fj }}
                  </div>
                </div>
              </div>

              <div class="grid gap-6 grid-cols-1 md:grid-cols-2 pt-4 border-t border-border/50">
                <div v-if="!isAutoEntrepreneur" class="space-y-2">
                  <Label for="rcs">RCS (Ville)</Label>
                  <Input id="rcs" v-model="form.rcs" placeholder="Ex: RCS Paris" class="h-12 text-base" />
                </div>
                <div v-if="!isAutoEntrepreneur" class="space-y-2">
                  <Label for="tva">Numéro de TVA Intra.</Label>
                  <Input id="tva" v-model="form.tva_intracommunautaire" placeholder="Ex: FR 12 345678900" class="h-12 text-base uppercase" />
                </div>
                <div v-if="!isAutoEntrepreneur" class="space-y-2">
                  <Label for="capital">Capital Social (€)</Label>
                  <Input id="capital" type="number" v-model="form.capital_social" placeholder="Ex: 1000" class="h-12 text-base" />
                </div>
                <div v-if="!isAutoEntrepreneur" class="space-y-2">
                  <Label for="tva_defaut">Taux de TVA par défaut (%)</Label>
                  <Input id="tva_defaut" type="number" step="0.1" v-model="form.tva_defaut" placeholder="Ex: 20.0" class="h-12 text-base" />
                </div>
              </div>

              <div class="space-y-2 pt-4 border-t border-border/50">
                <Label class="text-foreground">Logo (optionnel)</Label>
                <div 
                  v-if="!form.logo"
                  @click="triggerFileInput"
                  @dragover.prevent
                  @drop.prevent="handleDrop"
                  class="border-2 border-dashed border-border/60 hover:border-primary/50 transition-colors rounded-xl p-8 flex flex-col items-center justify-center bg-muted/10 cursor-pointer group"
                >
                  <div class="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                    <Upload class="w-5 h-5" />
                  </div>
                  <p class="text-sm font-medium text-foreground">Cliquez ou glissez votre logo</p>
                  <p class="text-xs text-muted-foreground mt-1">PNG, JPG, SVG jusqu'à 2MB</p>
                </div>
                <div v-else class="relative w-32 h-32 rounded-xl border border-border overflow-hidden group">
                  <img :src="form.logo" alt="Logo preview" class="w-full h-full object-contain bg-muted/20 p-2" />
                  <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <Button variant="destructive" size="icon" @click="removeLogo" class="rounded-full h-8 w-8">
                      <X class="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                <input type="file" ref="fileInput" class="hidden" accept="image/png, image/jpeg, image/svg+xml" @change="handleFileUpload" />
              </div>
            </div>

            <!-- Step 3: Coordonnées -->
            <div v-else-if="currentStep === 3" key="step3" class="space-y-6">
              <div class="grid gap-6 grid-cols-1 md:grid-cols-2">
                <div class="space-y-2 md:col-span-2">
                  <Label for="adresse">Adresse complète <span class="text-destructive">*</span></Label>
                  <Input id="adresse" v-model="form.adresse" placeholder="Ex: 12 rue de la Paix" class="h-12 text-base" />
                </div>
                <div class="space-y-2">
                  <Label for="code_postal">Code postal <span class="text-destructive">*</span></Label>
                  <Input id="code_postal" v-model="form.code_postal" placeholder="Ex: 75000" class="h-12 text-base" />
                </div>
                <div class="space-y-2">
                  <Label for="ville">Ville <span class="text-destructive">*</span></Label>
                  <Input id="ville" v-model="form.ville" placeholder="Ex: Paris" class="h-12 text-base" />
                </div>
              </div>

              <div class="grid gap-6 grid-cols-1 md:grid-cols-2 pt-4 border-t border-border/50">
                <div class="space-y-2">
                  <Label for="email">E-mail professionnel <span class="text-destructive">*</span></Label>
                  <Input id="email" type="email" v-model="form.email" placeholder="Ex: contact@entreprise.fr" class="h-12 text-base" />
                </div>
                <div class="space-y-2">
                  <Label for="telephone">Téléphone</Label>
                  <Input id="telephone" type="tel" v-model="form.telephone" placeholder="Ex: 06 12 34 56 78" class="h-12 text-base" />
                </div>
              </div>
            </div>

            <!-- Step 4: Banque -->
            <div v-else-if="currentStep === 4" key="step4" class="space-y-6">
              <div class="grid gap-6 grid-cols-1 md:grid-cols-2">
                <div class="space-y-2 md:col-span-2">
                  <Label for="iban">IBAN</Label>
                  <Input id="iban" v-model="form.iban" placeholder="Ex: FR76 1234 5678 ..." class="h-12 text-base uppercase tracking-widest font-mono text-sm" />
                </div>
                <div class="space-y-2">
                  <Label for="bic">BIC / SWIFT</Label>
                  <Input id="bic" v-model="form.bic" placeholder="Ex: ABCEFR01XXXX" class="h-12 text-base uppercase" />
                </div>
                <div class="space-y-2">
                  <Label for="banque">Nom de la banque</Label>
                  <Input id="banque" v-model="form.nom_banque" placeholder="Ex: Qonto ou BNP" class="h-12 text-base" />
                </div>
              </div>

              <div class="grid gap-6 grid-cols-1 pt-4 border-t border-border/50">
                <div class="space-y-2">
                  <Label for="ca">Objectif de CA Mensuel (€) - Optionnel</Label>
                  <Input id="ca" type="number" v-model="form.objectif_mensuel_ca" placeholder="Ex: 5000" class="h-12 text-base" />
                </div>
                <div class="space-y-2">
                  <Label for="pied">Texte pied de page par défaut (devis/factures)</Label>
                  <textarea 
                    id="pied" 
                    v-model="form.texte_pied_page" 
                    @input="isFooterManuallyEdited = true"
                    rows="3"
                    class="flex min-h-[80px] w-full rounded-xl border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all focus:border-primary/50"
                    placeholder="Ex: Paiement à 30 jours, pas d'escompte."></textarea>
                </div>
              </div>
            </div>

            <!-- Step 5: Récapitulatif -->
            <div v-else-if="currentStep === 5" key="step5" class="space-y-6">
              
              <div class="bg-muted/30 rounded-2xl p-6 border border-border">
                <div class="flex items-center gap-4 mb-6 pb-6 border-b border-border/50">
                  <div class="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center text-primary text-2xl font-bold overflow-hidden border border-border">
                    <img v-if="form.logo" :src="form.logo" class="w-full h-full object-cover" />
                    <span v-else>{{ form.nom.charAt(0).toUpperCase() }}</span>
                  </div>
                  <div>
                    <h3 class="text-xl font-bold text-foreground">{{ form.nom }}</h3>
                    <p class="text-muted-foreground">{{ form.forme_juridique }}</p>
                  </div>
                </div>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-8 text-sm">
                  <div>
                    <span class="block text-muted-foreground mb-1">Email professionnel</span>
                    <span class="font-medium text-foreground">{{ form.email }}</span>
                  </div>
                  <div>
                    <span class="block text-muted-foreground mb-1">Siège social</span>
                    <span class="font-medium text-foreground">{{ form.adresse }}, {{ form.code_postal }} {{ form.ville }}</span>
                  </div>
                  <div>
                    <span class="block text-muted-foreground mb-1">SIRET</span>
                    <span class="font-medium text-foreground">{{ form.siret }}</span>
                  </div>
                  <div v-if="!isAutoEntrepreneur && form.tva_intracommunautaire">
                    <span class="block text-muted-foreground mb-1">TVA Intra.</span>
                    <span class="font-medium text-foreground">{{ form.tva_intracommunautaire }}</span>
                  </div>
                </div>
              </div>

              <div class="flex items-start bg-green-500/10 text-green-600 dark:text-green-400 p-4 rounded-xl border border-green-500/20">
                <CheckCircle2 class="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
                <p class="text-sm">Tout semble parfait ! Vous pouvez modifier vos informations plus tard depuis les paramètres.</p>
              </div>

            </div>
          </transition>
        </CardContent>
      </Card>
      
    </div>

    <!-- Sticky Mobile Follow Button / Standard Desktop Button -->
    <div class="fixed bottom-0 left-0 right-0 p-4 bg-background/80 backdrop-blur-xl border-t border-border/50 lg:static lg:bg-transparent lg:border-none lg:p-0 lg:w-full lg:max-w-2xl lg:mt-4 z-50 transition-all">
      <Button 
        class="w-full h-14 rounded-2xl text-lg font-semibold shadow-lg shadow-primary/20 transition-all active:scale-[0.98]"
        :disabled="!isStepValid || isLoading"
        @click="currentStep === 5 ? submitForm() : nextStep()"
      >
        <template v-if="isLoading">
          <Loader2 class="w-5 h-5 mr-3 animate-spin" />
          Création en cours...
        </template>
        <template v-else>
          {{ currentStep === 5 ? "Confirmer et démarrer" : "Continuer" }}
          <ChevronRight v-if="currentStep < 5" class="w-5 h-5 ml-2" />
        </template>
      </Button>
      <p v-if="!isStepValid && currentStep < 5" class="text-center text-xs text-muted-foreground mt-3 animate-pulse">
        Veuillez remplir les champs obligatoires pour continuer
      </p>
    </div>

  </div>
</template>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(10px) scale(0.98);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-10px) scale(0.98);
}
</style>
