<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { apiFetch } from '@/lib/api'
import { dataStore } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { 
  Building2, MapPin, Scale, Landmark, Save, 
  Upload, Loader2, CheckCircle2, X, Info
} from 'lucide-vue-next'

const loading = ref(true)
const saving = ref(false)
const message = ref({ text: '', type: '' })
const fileInput = ref<HTMLInputElement | null>(null)

const form = ref({
  nom: '',
  forme_juridique: '',
  logo: '',
  adresse: '',
  code_postal: '',
  ville: '',
  telephone: '',
  email: '',
  siret: '',
  rcs: '',
  tva_intracommunautaire: '',
  capital_social: undefined as number | undefined,
  tva_defaut: undefined as number | undefined,
  iban: '',
  bic: '',
  nom_banque: '',
  objectif_mensuel_ca: undefined as number | undefined,
  texte_pied_page: ''
})

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

function resetFooterToDefault() {
  form.value.texte_pied_page = generateDefaultFooter()
}

const formeJuridiques = ['Auto-entrepreneur', 'SASU', 'SAS', 'SARL', 'EURL', 'EI']
const isAutoEntrepreneur = computed(() => form.value.forme_juridique === 'Auto-entrepreneur')

async function fetchSociete() {
  loading.value = true
  try {
    const res = await apiFetch('societes/me')
    if (res.ok) {
      const data = await res.json()
      // Map data to form
      Object.keys(form.value).forEach(key => {
        if (key in data) {
          (form.value as any)[key] = data[key]
        }
      })
    }
  } catch (e) {
    console.error('Failed to fetch societe', e)
    message.value = { text: 'Erreur lors du chargement des données.', type: 'error' }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  message.value = { text: '', type: '' }
  
  try {
    // Sanitize numbers and empty strings
    const sanitizedForm = Object.fromEntries(
      Object.entries(form.value).map(([key, value]) => {
        if (value === '') return [key, null]
        return [key, value]
      })
    )

    const res = await apiFetch('societes/me', {
      method: 'PUT',
      body: JSON.stringify(sanitizedForm)
    })

    if (res.ok) {
      message.value = { text: 'Modifications enregistrées avec succès !', type: 'success' }
      setTimeout(() => { message.value = { text: '', type: '' } }, 5000)
    } else {
      const error = await res.json()
      throw new Error(error.detail || 'Erreur lors de la sauvegarde')
    }
  } catch (e: any) {
    console.error('Failed to save societe', e)
    message.value = { text: e.message, type: 'error' }
  } finally {
    saving.value = false
  }
}

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

function removeLogo() {
  form.value.logo = ''
  if (fileInput.value) fileInput.value.value = ''
}

const canEdit = computed(() => {
  const d = dataStore.user.data
  if (!d) return true
  return d.is_owner || d.can_edit_societe !== false
})

onMounted(fetchSociete)
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-12">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-foreground">Entreprise</h1>
        <p class="text-muted-foreground mt-1">Gérez les informations légales et facturation de votre structure.</p>
      </div>
      <button v-if="canEdit" @click="handleSave" :disabled="saving" class="btn-primary h-12">
        <template v-if="saving">
          <Loader2 class="w-5 h-5 mr-2 animate-spin" />
          Enregistrement...
        </template>
        <template v-else>
          <Save class="w-5 h-5 mr-2" />
          Enregistrer les modifications
        </template>
      </button>
    </div>

    <!-- Feedback Message -->
    <transition name="fade">
      <div v-if="message.text" 
        :class="[
          'p-4 rounded-xl border flex items-center gap-3',
          message.type === 'success' ? 'bg-green-500/10 text-green-600 border-green-500/20' : 'bg-destructive/10 text-destructive border-destructive/20'
        ]">
        <CheckCircle2 v-if="message.type === 'success'" class="w-5 h-5" />
        <Info v-else class="w-5 h-5" />
        <p class="text-sm font-medium">{{ message.text }}</p>
      </div>
    </transition>

    <div v-if="loading" class="flex flex-col items-center justify-center h-64 text-muted-foreground">
      <Loader2 class="w-10 h-10 animate-spin mb-4 text-primary" />
      <p>Chargement des informations...</p>
    </div>

    <fieldset v-else :disabled="!canEdit" class="border-0 p-0 m-0">
      <Tabs defaultValue="identity" class="space-y-6">
        <TabsList class="bg-muted/50 p-1 rounded-xl w-full md:w-auto h-auto grid grid-cols-2 md:inline-flex">
          <TabsTrigger value="identity" class="rounded-lg py-2 px-4">
            <Building2 class="w-4 h-4 mr-2" /> Identité
          </TabsTrigger>
          <TabsTrigger value="address" class="rounded-lg py-2 px-4">
            <MapPin class="w-4 h-4 mr-2" /> Coordonnées
          </TabsTrigger>
          <TabsTrigger value="legal" class="rounded-lg py-2 px-4">
            <Scale class="w-4 h-4 mr-2" /> Légal & Fiscal
          </TabsTrigger>
          <TabsTrigger value="bank" class="rounded-lg py-2 px-4">
            <Landmark class="w-4 h-4 mr-2" /> Banque
          </TabsTrigger>
          <TabsTrigger value="settings" class="rounded-lg py-2 px-4">
            <Info class="w-4 h-4 mr-2" /> Paramètres
          </TabsTrigger>
        </TabsList>

        <!-- Identity Tab -->
        <TabsContent value="identity">
          <Card class="border-border/50 shadow-sm overflow-hidden">
            <CardHeader>
              <CardTitle>Identité de l'entreprise</CardTitle>
              <CardDescription>Informations générales et visuelles.</CardDescription>
            </CardHeader>
            <CardContent class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2">
                  <Label for="nom">Nom de l'entreprise</Label>
                  <Input id="nom" v-model="form.nom" placeholder="Ex: Mon Entreprise SAS" class="h-11" />
                </div>
                <div class="space-y-2">
                  <Label>Forme juridique</Label>
                  <div class="grid grid-cols-2 gap-2">
                    <div 
                      v-for="fj in formeJuridiques" :key="fj"
                      @click="form.forme_juridique = fj"
                      class="border rounded-lg p-2 text-center text-sm cursor-pointer transition-all"
                      :class="form.forme_juridique === fj ? 'bg-primary/10 border-primary text-primary font-semibold' : 'border-border text-muted-foreground hover:bg-muted/50'"
                    >
                      {{ fj }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="space-y-3 pt-2">
                <Label>Logo de l'entreprise</Label>
                <div class="flex items-center gap-6">
                  <div class="relative w-32 h-32 rounded-xl border border-border overflow-hidden bg-muted/20 flex items-center justify-center group">
                    <img v-if="form.logo" :src="form.logo" alt="Logo" class="w-full h-full object-contain p-2" />
                    <Building2 v-else class="w-10 h-10 text-muted-foreground/40" />
                    <div v-if="form.logo" class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <Button variant="destructive" size="icon" @click="removeLogo" class="rounded-full h-8 w-8">
                        <X class="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <div class="space-y-2">
                    <Button variant="outline" size="sm" @click="triggerFileInput">
                      <Upload class="w-4 h-4 mr-2" /> Changer le logo
                    </Button>
                    <p class="text-xs text-muted-foreground">PNG, JPG ou SVG. Max 2MB.</p>
                  </div>
                  <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleFileUpload" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- Address Tab -->
        <TabsContent value="address">
          <Card class="border-border/50 shadow-sm">
            <CardHeader>
              <CardTitle>Coordonnées</CardTitle>
              <CardDescription>Où vous trouver et comment vous contacter.</CardDescription>
            </CardHeader>
            <CardContent class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2 md:col-span-2">
                  <Label for="adresse">Adresse du siège</Label>
                  <Input id="adresse" v-model="form.adresse" placeholder="123 rue de la Paix" class="h-11" />
                </div>
                <div class="space-y-2">
                  <Label for="code_postal">Code postal</Label>
                  <Input id="code_postal" v-model="form.code_postal" placeholder="75000" class="h-11" />
                </div>
                <div class="space-y-2">
                  <Label for="ville">Ville</Label>
                  <Input id="ville" v-model="form.ville" placeholder="Paris" class="h-11" />
                </div>
                <div class="space-y-2">
                  <Label for="email">E-mail professionnel</Label>
                  <Input id="email" v-model="form.email" placeholder="contact@entreprise.com" class="h-11" />
                </div>
                <div class="space-y-2">
                  <Label for="telephone">Téléphone</Label>
                  <Input id="telephone" v-model="form.telephone" placeholder="01 23 45 67 89" class="h-11" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- Legal Tab -->
        <TabsContent value="legal">
          <Card class="border-border/50 shadow-sm">
            <CardHeader>
              <CardTitle>Informations Légales & Fiscales</CardTitle>
              <CardDescription>Requis pour la conformité de vos documents.</CardDescription>
            </CardHeader>
            <CardContent class="space-y-6">
              <div v-if="isAutoEntrepreneur" class="flex items-start bg-blue-500/10 text-blue-600 dark:text-blue-400 p-4 rounded-xl border border-blue-500/20">
                <Info class="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
                <p class="text-xs">En tant qu'auto-entrepreneur, certains champs (TVA, Capital) sont optionnels ou non applicables.</p>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2">
                  <Label for="siret">Numéro SIRET</Label>
                  <Input id="siret" v-model="form.siret" placeholder="123 456 789 00001" class="h-11" />
                </div>
                <div class="space-y-2">
                  <Label for="rcs">RCS / RM (Ville)</Label>
                  <Input id="rcs" v-model="form.rcs" placeholder="RCS Paris" class="h-11" />
                </div>
                <div class="space-y-2">
                  <Label for="tva">Numéro de TVA Intracommunautaire</Label>
                  <Input id="tva" v-model="form.tva_intracommunautaire" placeholder="FR 12 123456789" class="h-11 uppercase" />
                </div>
                <div class="space-y-2">
                  <Label for="capital">Capital Social (€)</Label>
                  <Input id="capital" type="number" v-model="form.capital_social" placeholder="1000" class="h-11" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- Banking Tab -->
        <TabsContent value="bank">
          <Card class="border-border/50 shadow-sm">
            <CardHeader>
              <CardTitle>Informations Bancaires & Facturation</CardTitle>
              <CardDescription>Détails pour recevoir vos paiements.</CardDescription>
            </CardHeader>
            <CardContent class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2 md:col-span-2">
                  <Label for="iban">IBAN</Label>
                  <Input id="iban" v-model="form.iban" placeholder="FR76 1234 ..." class="h-11 font-mono uppercase tracking-wider" />
                </div>
                <div class="space-y-2">
                  <Label for="bic">BIC / SWIFT</Label>
                  <Input id="bic" v-model="form.bic" placeholder="ABCEFR..." class="h-11 uppercase" />
                </div>
                <div class="space-y-2">
                  <Label for="bank">Nom de la banque</Label>
                  <Input id="bank" v-model="form.nom_banque" placeholder="Qonto, BNP..." class="h-11" />
                </div>
              </div>

              <div class="pt-6 border-t border-border/50 space-y-4">
                <div class="space-y-2">
                  <Label for="ca">Objectif de Chiffre d'affaires Mensuel (€)</Label>
                  <Input id="ca" type="number" v-model="form.objectif_mensuel_ca" placeholder="5000" class="h-11" />
                </div>
                <div class="space-y-2">
                  <div class="flex items-center justify-between">
                    <Label for="footer">Texte pied de page (Devis / Factures)</Label>
                    <Button variant="ghost" size="sm" @click="resetFooterToDefault" class="h-8 text-xs text-primary hover:text-primary hover:bg-primary/10 px-2 rounded-lg">
                      Réinitialiser par défaut
                    </Button>
                  </div>
                  <textarea 
                    id="footer" 
                    v-model="form.texte_pied_page" 
                    rows="4"
                    class="flex min-h-[100px] w-full rounded-xl border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all focus:border-primary/50"
                    placeholder="Ex: Auto-entrepreneur, TVA non applicable, art. 293 B du CGI."></textarea>
                  <p class="text-[10px] text-muted-foreground">Ce texte apparaîtra en bas de vos rapports PDF (Devis, Factures, Interventions).</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </fieldset>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
