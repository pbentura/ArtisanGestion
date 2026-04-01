<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { 
  Building2, MapPin, Scale, Landmark, CheckCircle2,
  ChevronRight, ArrowLeft, Upload, Loader2, Info, X
} from 'lucide-vue-next'

const router = useRouter()

const steps = [
  { id: 1, title: 'Identité', subtitle: 'Parlons de votre entreprise', icon: Building2 },
  { id: 2, title: 'Coordonnées', subtitle: 'Pour vous joindre facilement', icon: MapPin },
  { id: 3, title: 'Légal & Fiscal', subtitle: 'Les informations administratives', icon: Scale },
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

// Local Storage for saving drafts logically
const STORAGE_KEY = 'ventura_draft_societe'

onMounted(() => {
  const savedDraft = localStorage.getItem(STORAGE_KEY)
  if (savedDraft) {
    try {
      const parsed = JSON.parse(savedDraft)
      if (parsed) form.value = { ...form.value, ...parsed }
    } catch (e) {
      console.error('Failed to parse draft from local storage.')
    }
  }
})

watch(form, (newVal) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(newVal))
}, { deep: true })

const isAutoEntrepreneur = computed(() => form.value.forme_juridique === 'Auto-entrepreneur')

const isStepValid = computed(() => {
  if (currentStep.value === 1) return !!form.value.nom.trim()
  if (currentStep.value === 2) return !!form.value.email.trim() && !!form.value.adresse.trim() && !!form.value.ville.trim()
  if (currentStep.value === 3) return !!form.value.siret.trim()
  if (currentStep.value === 4) return true // Optional fields
  return true
})

function nextStep() {
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

  try {
    const res = await fetch('http://localhost:8000/api/societes/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(form.value)
    })

    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(errorData.detail || "Erreur lors de la création de l'entreprise")
    }

    localStorage.removeItem(STORAGE_KEY)
    router.push('/dashboard')
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
  <div class="min-h-screen bg-background flex flex-col items-center py-6 px-4 sm:px-6 lg:px-8">
    
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
            <!-- Step 1: Identité -->
            <div v-if="currentStep === 1" key="step1" class="space-y-6">
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

              <div class="space-y-2 pt-2">
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

            <!-- Step 2: Coordonnées -->
            <div v-else-if="currentStep === 2" key="step2" class="space-y-6">
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

            <!-- Step 3: Légal & Fiscal -->
            <div v-else-if="currentStep === 3" key="step3" class="space-y-6">
              
              <div v-if="isAutoEntrepreneur" class="flex items-start bg-blue-500/10 text-blue-600 dark:text-blue-400 p-4 rounded-xl border border-blue-500/20 mb-6">
                <Info class="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
                <p class="text-sm">En tant qu'auto-entrepreneur, certains champs comme le capital social et la TVA ne sont pas requis. Nous avons allégé le formulaire pour vous !</p>
              </div>

              <div class="grid gap-6 grid-cols-1 md:grid-cols-2">
                <div class="space-y-2">
                  <Label for="siret">Numéro SIRET <span class="text-destructive">*</span></Label>
                  <Input id="siret" v-model="form.siret" placeholder="Ex: 123 456 789 00012" class="h-12 text-base" />
                </div>
                
                <template v-if="!isAutoEntrepreneur">
                  <div class="space-y-2">
                    <Label for="rcs">RCS (Ville)</Label>
                    <Input id="rcs" v-model="form.rcs" placeholder="Ex: RCS Paris" class="h-12 text-base" />
                  </div>
                  <div class="space-y-2">
                    <Label for="tva">Numéro de TVA Intracommunautaire</Label>
                    <Input id="tva" v-model="form.tva_intracommunautaire" placeholder="Ex: FR 12 345678900" class="h-12 text-base uppercase" />
                  </div>
                  <div class="space-y-2">
                    <Label for="capital">Capital Social (€)</Label>
                    <Input id="capital" type="number" v-model="form.capital_social" placeholder="Ex: 1000" class="h-12 text-base" />
                  </div>
                  <div class="space-y-2">
                    <Label for="tva_defaut">Taux de TVA par défaut (%)</Label>
                    <Input id="tva_defaut" type="number" step="0.1" v-model="form.tva_defaut" placeholder="Ex: 20.0" class="h-12 text-base" />
                  </div>
                </template>
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
                  <Input id="pied" v-model="form.texte_pied_page" placeholder="Ex: Paiement à 30 jours, pas d'escompte." class="h-12 text-base" />
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
