<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Building2, Loader2, ArrowRight, Search, MapPin, 
  CheckCircle2, RefreshCw, Hash, ChevronRight, ChevronDown, ChevronUp
} from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { uiStore, dataStore } from '@/lib/store'
import { apiFetch } from '@/lib/api'
import { trackConversion } from '@/lib/analytics'

const router = useRouter()

const searchMode = ref<'nom' | 'siret'>('nom')
const searchNameQuery = ref('')
const searchPostalCode = ref('')
const isSearching = ref(false)
const searchResults = ref<any[]>([])
const searchError = ref('')
const hasSearched = ref(false)
const enterpriseSelected = ref(false)
const manualEntry = ref(false)
const showDetails = ref(false)

const form = ref({
  nom: '',
  forme_juridique: 'Auto-entrepreneur',
  siret: '',
  adresse: '',
  code_postal: '',
  ville: '',
  rcs: '',
  tva_intracommunautaire: '',
  telephone: '',
  email: '',
  texte_pied_page: ''
})

const isFooterManuallyEdited = ref(false)
const formeJuridiques = ['Auto-entrepreneur', 'SASU', 'SAS', 'SARL', 'EURL', 'EI']

const isLoading = ref(false)
const erreur = ref('')

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

function resetModal() {
  form.value = {
    nom: '',
    forme_juridique: 'Auto-entrepreneur',
    siret: '',
    adresse: '',
    code_postal: '',
    ville: '',
    rcs: '',
    tva_intracommunautaire: '',
    telephone: '',
    email: '',
    texte_pied_page: ''
  }
  searchNameQuery.value = ''
  searchPostalCode.value = ''
  searchResults.value = []
  searchError.value = ''
  hasSearched.value = false
  enterpriseSelected.value = false
  manualEntry.value = false
  showDetails.value = false
  isFooterManuallyEdited.value = false
  erreur.value = ''
  searchMode.value = 'nom'
}

watch(() => uiStore.showSocieteModal, (val) => {
  if (val) {
    resetModal()
  }
})

let debounceTimer: ReturnType<typeof setTimeout> | null = null

function onNameInput() {
  searchError.value = ''
  if (debounceTimer) clearTimeout(debounceTimer)
  
  const query = searchNameQuery.value.trim()
  if (query.length >= 3) {
    debounceTimer = setTimeout(() => {
      searchByName()
    }, 400)
  } else {
    searchResults.value = []
    hasSearched.value = false
  }
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
    const params = new URLSearchParams({ q: query, per_page: '8' })
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
      searchError.value = "Aucune entreprise trouvée avec ces critères. Vous pouvez saisir vos informations manuellement."
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
      enterpriseSelected.value = false
    }
  } catch (e: any) {
    searchError.value = e.message || "Impossible de contacter l'API Sirene."
    enterpriseSelected.value = false
  } finally {
    isSearching.value = false
  }
}

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

  enterpriseSelected.value = true
  manualEntry.value = false
  searchError.value = ''
  searchResults.value = []
}

function resetSelection() {
  enterpriseSelected.value = false
  form.value.nom = ''
  form.value.siret = ''
  form.value.adresse = ''
  form.value.code_postal = ''
  form.value.ville = ''
  form.value.rcs = ''
  form.value.tva_intracommunautaire = ''
  searchNameQuery.value = ''
}

function startManualEntry() {
  manualEntry.value = true
  enterpriseSelected.value = false
  searchError.value = ''
  searchResults.value = []
  if (!form.value.nom && searchNameQuery.value) {
    form.value.nom = searchNameQuery.value.trim()
  }
}

const peutValider = computed(() => {
  if (enterpriseSelected.value) return !!form.value.nom.trim()
  if (manualEntry.value) return !!form.value.nom.trim()
  return !!form.value.nom.trim() || !!searchNameQuery.value.trim()
})

async function creerSociete() {
  if (!peutValider.value || isLoading.value) return
  isLoading.value = true
  erreur.value = ''

  // Si l'utilisateur n'a pas explicitement sélectionné mais a saisi un nom dans la recherche
  if (!form.value.nom.trim() && searchNameQuery.value.trim()) {
    form.value.nom = searchNameQuery.value.trim()
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
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || "Impossible de créer votre entreprise.")
    }

    trackConversion('societe_created', { source: 'document' })

    await dataStore.fetchUser(true)
    const callback = uiStore.onSocieteCreated
    uiStore.closeSocieteModal()
    if (callback) callback()
  } catch (e: any) {
    erreur.value = e.message || "Une erreur est survenue."
  } finally {
    isLoading.value = false
  }
}

function annuler() {
  uiStore.closeSocieteModal()
  router.push('/app/dashboard')
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="uiStore.showSocieteModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-background/80 backdrop-blur-sm" @click="annuler" />

        <div class="relative w-full max-w-xl bg-background rounded-3xl shadow-2xl border border-border/60 max-h-[92vh] overflow-y-auto z-10">
          <div class="p-6 sm:p-8 space-y-6">

            <!-- Modal Header -->
            <div class="text-center">
              <div class="inline-flex items-center justify-center p-3.5 rounded-2xl bg-primary/10 text-primary mb-3 shadow-inner shadow-primary/20">
                <Building2 class="w-7 h-7" />
              </div>
              <h2 class="text-2xl font-bold text-foreground mb-1.5">
                Créons votre entreprise
              </h2>
              <p class="text-muted-foreground text-sm leading-relaxed max-w-md mx-auto">
                Votre {{ uiStore.societeModalDocument }} sera édité aux coordonnées officielles de votre entreprise.
              </p>
            </div>

            <!-- STATE 1: Entreprise sélectionnée depuis Sirene -->
            <div v-if="enterpriseSelected" class="space-y-4">
              <div class="p-4 sm:p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 dark:bg-emerald-950/25 dark:border-emerald-800/40 text-foreground transition-all">
                <div class="flex items-start gap-3.5">
                  <div class="p-2 rounded-xl bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0">
                    <CheckCircle2 class="w-5 h-5" />
                  </div>
                  <div class="space-y-1.5 flex-1 min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                      <span class="text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                        Entreprise sélectionnée
                      </span>
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/20 text-emerald-700 dark:text-emerald-300">
                        {{ form.forme_juridique || 'Entreprise' }}
                      </span>
                    </div>
                    <h3 class="text-lg font-bold text-foreground truncate">
                      {{ form.nom }}
                    </h3>
                    <p v-if="form.adresse || form.ville" class="text-sm text-muted-foreground flex items-center gap-1.5">
                      <MapPin class="w-4 h-4 flex-shrink-0 text-muted-foreground" />
                      <span class="truncate">{{ [form.adresse, [form.code_postal, form.ville].filter(Boolean).join(' ')].filter(Boolean).join(', ') }}</span>
                    </p>
                    <div class="pt-1.5 flex items-center gap-2 flex-wrap text-xs text-muted-foreground">
                      <span class="font-mono bg-background/90 px-2 py-0.5 rounded-md border border-border/60 text-[11px]">
                        SIRET : {{ form.siret }}
                      </span>
                      <span v-if="form.rcs" class="bg-background/90 px-2 py-0.5 rounded-md border border-border/60 text-[11px]">
                        {{ form.rcs }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Options: Changer ou Voir/Modifier les détails -->
              <div class="flex items-center justify-between text-xs text-muted-foreground pt-0.5">
                <button 
                  type="button" 
                  @click="showDetails = !showDetails" 
                  class="inline-flex items-center gap-1 text-primary hover:underline font-medium"
                >
                  <span>{{ showDetails ? 'Masquer les informations' : 'Vérifier / modifier les détails' }}</span>
                  <component :is="showDetails ? ChevronUp : ChevronDown" class="w-3.5 h-3.5" />
                </button>

                <Button variant="ghost" size="sm" @click="resetSelection" class="h-8 text-xs text-muted-foreground hover:text-foreground">
                  <RefreshCw class="w-3.5 h-3.5 mr-1" />
                  Changer
                </Button>
              </div>

              <!-- Section déroulante d'édition des détails -->
              <div v-if="showDetails" class="p-4 rounded-2xl bg-muted/40 border border-border/50 space-y-4 text-left">
                <div class="space-y-2">
                  <Label class="text-xs font-semibold text-foreground">Forme juridique</Label>
                  <div class="grid grid-cols-3 gap-2">
                    <div
                      v-for="fj in formeJuridiques" :key="fj"
                      @click="form.forme_juridique = fj"
                      class="border rounded-lg py-1.5 px-2 text-center text-xs cursor-pointer transition-all"
                      :class="form.forme_juridique === fj
                        ? 'bg-primary/15 border-primary text-primary font-semibold ring-1 ring-primary/20'
                        : 'border-border text-muted-foreground hover:bg-muted/50'"
                    >
                      {{ fj }}
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div class="space-y-1">
                    <Label class="text-xs text-muted-foreground">Adresse</Label>
                    <Input v-model="form.adresse" class="h-9 text-xs" />
                  </div>
                  <div class="space-y-1">
                    <Label class="text-xs text-muted-foreground">Code postal & Ville</Label>
                    <div class="flex gap-2">
                      <Input v-model="form.code_postal" placeholder="CP" class="h-9 text-xs w-24" />
                      <Input v-model="form.ville" placeholder="Ville" class="h-9 text-xs flex-1" />
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div class="space-y-1">
                    <Label class="text-xs text-muted-foreground">Téléphone professionnel</Label>
                    <Input v-model="form.telephone" placeholder="06 12 34 56 78" class="h-9 text-xs" />
                  </div>
                  <div class="space-y-1">
                    <Label class="text-xs text-muted-foreground">Email professionnel</Label>
                    <Input v-model="form.email" placeholder="contact@entreprise.fr" class="h-9 text-xs" />
                  </div>
                </div>
              </div>
            </div>

            <!-- STATE 2: Saisie manuelle -->
            <div v-else-if="manualEntry" class="space-y-4">
              <div class="space-y-2">
                <Label for="manual-nom" class="text-foreground font-medium">Nom de l'entreprise <span class="text-destructive">*</span></Label>
                <Input
                  id="manual-nom"
                  v-model="form.nom"
                  placeholder="Ex : Menuiserie Dupont"
                  class="h-12 text-base"
                  autofocus
                  @keyup.enter="creerSociete"
                />
              </div>

              <div class="space-y-2">
                <Label class="text-foreground font-medium">Forme juridique</Label>
                <div class="grid grid-cols-3 gap-2">
                  <div
                    v-for="fj in formeJuridiques" :key="fj"
                    @click="form.forme_juridique = fj"
                    class="border rounded-xl py-2 px-2 text-center text-xs sm:text-sm cursor-pointer transition-all duration-200"
                    :class="form.forme_juridique === fj
                      ? 'bg-primary/10 border-primary text-primary font-semibold ring-1 ring-primary/20'
                      : 'border-border text-muted-foreground hover:bg-muted/50'"
                  >
                    {{ fj }}
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                <div class="space-y-1.5">
                  <Label for="manual-siret" class="text-xs text-muted-foreground">SIRET (optionnel)</Label>
                  <Input id="manual-siret" v-model="form.siret" placeholder="14 chiffres" class="h-10 text-sm" />
                </div>
                <div class="space-y-1.5">
                  <Label for="manual-ville" class="text-xs text-muted-foreground">Ville</Label>
                  <Input id="manual-ville" v-model="form.ville" placeholder="Ex: Lyon" class="h-10 text-sm" />
                </div>
              </div>

              <div class="text-center pt-2">
                <button
                  type="button"
                  @click="manualEntry = false"
                  class="text-xs text-primary underline underline-offset-4 hover:opacity-80 transition-opacity"
                >
                  <Search class="w-3.5 h-3.5 inline mr-1" />
                  Revenir à la recherche automatique
                </button>
              </div>
            </div>

            <!-- STATE 3: Recherche d'entreprise (Nom / SIRET) -->
            <div v-else class="space-y-4">
              <!-- Mode selector -->
              <div class="flex p-1 bg-muted/70 rounded-xl border border-border/40">
                <button 
                  type="button"
                  @click="searchMode = 'nom'; searchError = ''; searchResults = []"
                  class="flex-1 py-2 px-3 text-xs sm:text-sm font-medium rounded-lg transition-all flex items-center justify-center gap-1.5"
                  :class="searchMode === 'nom' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
                >
                  <Building2 class="w-4 h-4" />
                  <span>Par nom d'entreprise</span>
                </button>
                <button 
                  type="button"
                  @click="searchMode = 'siret'; searchError = ''; searchResults = []"
                  class="flex-1 py-2 px-3 text-xs sm:text-sm font-medium rounded-lg transition-all flex items-center justify-center gap-1.5"
                  :class="searchMode === 'siret' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
                >
                  <Hash class="w-4 h-4" />
                  <span>Par SIRET (14 chiffres)</span>
                </button>
              </div>

              <!-- Mode 1: Recherche par Nom -->
              <div v-if="searchMode === 'nom'" class="space-y-3">
                <div class="space-y-1.5">
                  <Label for="modal-search-nom" class="text-foreground font-medium">
                    Nom de votre entreprise ou votre nom
                  </Label>
                  <div class="relative">
                    <Input
                      id="modal-search-nom"
                      v-model="searchNameQuery"
                      placeholder="Ex : Menuiserie Martin, Plomberie Dupont..."
                      class="h-12 text-base pr-10 bg-background"
                      autofocus
                      @input="onNameInput"
                      @keyup.enter="searchByName"
                    />
                    <div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 text-muted-foreground">
                      <Loader2 v-if="isSearching" class="w-4 h-4 animate-spin text-primary" />
                      <Search v-else class="w-4 h-4 cursor-pointer hover:text-foreground" @click="searchByName" />
                    </div>
                  </div>
                </div>

                <div class="flex flex-col sm:flex-row gap-2 pt-0.5">
                  <Input
                    v-model="searchPostalCode"
                    placeholder="Code postal ou ville (optionnel)"
                    class="h-10 text-sm bg-background flex-1"
                    @keyup.enter="searchByName"
                  />
                  <Button 
                    variant="secondary"
                    size="sm"
                    @click="searchByName" 
                    :disabled="isSearching || searchNameQuery.trim().length < 2"
                    class="h-10 px-4 font-medium text-xs sm:text-sm flex-shrink-0"
                  >
                    <Loader2 v-if="isSearching" class="w-3.5 h-3.5 mr-1.5 animate-spin" />
                    <Search v-else class="w-3.5 h-3.5 mr-1.5" />
                    Rechercher
                  </Button>
                </div>

                <!-- Message d'erreur -->
                <p v-if="searchError" class="text-xs text-destructive mt-1">{{ searchError }}</p>

                <!-- Liste des propositions d'entreprises -->
                <div v-if="searchResults.length > 0" class="space-y-2 pt-2">
                  <p class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    {{ searchResults.length }} résultat{{ searchResults.length > 1 ? 's trouvés' : ' trouvé' }} — Cliquez sur le vôtre :
                  </p>

                  <div class="space-y-2 max-h-[260px] overflow-y-auto pr-1">
                    <div
                      v-for="(item, idx) in searchResults"
                      :key="item.siret || idx"
                      @click="selectEnterprise(item)"
                      class="group p-3 sm:p-3.5 rounded-xl border border-border/70 hover:border-primary/60 bg-card hover:bg-primary/5 cursor-pointer transition-all duration-150 shadow-sm flex items-center justify-between gap-3"
                    >
                      <div class="space-y-1 min-w-0 flex-1">
                        <div class="flex items-center gap-2 flex-wrap">
                          <span class="font-bold text-foreground group-hover:text-primary transition-colors text-sm truncate">
                            {{ item.nom }}
                          </span>
                          <span
                            v-if="item.etat_administratif === 'A'"
                            class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-emerald-500/15 text-emerald-700 dark:text-emerald-400"
                          >
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            Actif
                          </span>
                          <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-secondary text-secondary-foreground">
                            {{ item.forme_juridique }}
                          </span>
                        </div>

                        <div class="flex items-center gap-1 text-xs text-muted-foreground truncate">
                          <MapPin class="w-3.5 h-3.5 flex-shrink-0 text-muted-foreground" />
                          <span class="truncate">{{ [item.adresse, [item.code_postal, item.ville].filter(Boolean).join(' ')].filter(Boolean).join(', ') }}</span>
                        </div>

                        <div class="flex items-center gap-2 text-[11px] text-muted-foreground pt-0.5">
                          <span class="font-mono bg-muted/60 px-1.5 py-0.5 rounded text-[10px]">
                            SIRET : {{ item.siret }}
                          </span>
                        </div>
                      </div>

                      <Button
                        size="sm"
                        variant="outline"
                        class="group-hover:bg-primary group-hover:text-primary-foreground group-hover:border-primary transition-all flex-shrink-0 text-xs h-8 px-2.5 font-medium"
                      >
                        Sélectionner
                        <ChevronRight class="w-3.5 h-3.5 ml-1" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Mode 2: Recherche par SIRET -->
              <div v-else-if="searchMode === 'siret'" class="space-y-3">
                <div class="space-y-1.5">
                  <Label for="modal-search-siret" class="text-foreground font-medium">
                    Numéro SIRET (14 chiffres)
                  </Label>
                  <div class="flex gap-2">
                    <Input
                      id="modal-search-siret"
                      v-model="form.siret"
                      placeholder="Ex : 123 456 789 00012"
                      class="h-12 text-base flex-1 bg-background"
                      autofocus
                      @keyup.enter="searchSiret"
                    />
                    <Button
                      @click="searchSiret"
                      :disabled="isSearching || form.siret.replace(/\s+/g, '').length < 14"
                      class="h-12 px-5 font-medium flex-shrink-0"
                    >
                      <Loader2 v-if="isSearching" class="w-4 h-4 mr-1.5 animate-spin" />
                      <Search v-else class="w-4 h-4 mr-1.5" />
                      Rechercher
                    </Button>
                  </div>
                  <p v-if="searchError" class="text-xs text-destructive mt-1">{{ searchError }}</p>
                </div>
              </div>

              <!-- Issue de secours : Saisie manuelle -->
              <div class="pt-2 text-center">
                <button
                  type="button"
                  @click="startManualEntry"
                  class="text-xs text-muted-foreground underline underline-offset-4 hover:text-foreground transition-colors"
                >
                  Je ne trouve pas mon entreprise — saisir manuellement
                </button>
              </div>
            </div>

            <!-- Global Error -->
            <p v-if="erreur" class="text-sm text-destructive text-center font-medium">{{ erreur }}</p>

            <!-- Actions buttons -->
            <div class="space-y-2.5 pt-2">
              <Button
                class="w-full h-12 sm:h-13 rounded-2xl text-base font-semibold shadow-lg shadow-primary/20 transition-all active:scale-[0.99]"
                :disabled="!peutValider || isLoading"
                @click="creerSociete"
              >
                <template v-if="isLoading">
                  <Loader2 class="w-5 h-5 mr-2 animate-spin" /> Création en cours...
                </template>
                <template v-else>
                  Créer et continuer <ArrowRight class="w-4 h-4 ml-2" />
                </template>
              </Button>

              <button
                type="button"
                @click="annuler"
                class="w-full py-2 text-xs sm:text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Retour au tableau de bord
              </button>
            </div>

          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>

