<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiFetch } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  User, Settings, CreditCard, Receipt, LifeBuoy, Loader2, Save, CheckCircle2,
  LogOut, Trash2, AlertTriangle, X
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const activeTab = ref((route.query.tab as string) || 'compte')
const isLoading = ref(true)
const isSaving = ref(false)
const isDeleting = ref(false)
const showSuccess = ref(false)
const confirmDelete = ref(false)

const user = ref({
  nom: '',
  prenom: '',
  email: '',
  role: ''
})

const form = ref({
  nom: '',
  prenom: '',
  email: ''
})

const initials = computed(() => {
  const f = form.value.prenom?.charAt(0) || ''
  const l = form.value.nom?.charAt(0) || ''
  return (f + l).toUpperCase() || '?'
})

async function fetchUser() {
  isLoading.value = true
  try {
    const res = await apiFetch('users/me')
    if (res.ok) {
      const data = await res.json()
      user.value = data
      form.value = {
        nom: data.nom || '',
        prenom: data.prenom || '',
        email: data.email || ''
      }
    }
  } catch (error) {
    console.error('Error fetching user:', error)
  } finally {
    isLoading.value = false
  }
}

async function handleSave() {
  isSaving.value = true
  try {
    const res = await apiFetch('users/me', {
      method: 'PATCH',
      body: JSON.stringify({
        nom: form.value.nom,
        prenom: form.value.prenom
      })
    })

    if (res.ok) {
      const updatedUser = await res.json()
      user.value = updatedUser
      showSuccess.value = true
      setTimeout(() => {
        showSuccess.value = false
      }, 3000)
    } else {
      const errorData = await res.json()
      alert(errorData.detail || "Erreur lors de la sauvegarde")
    }
  } catch (error) {
    console.error('Error saving user:', error)
    alert("Une erreur est survenue")
  } finally {
    isSaving.value = false
  }
}

function handleLogout() {
  localStorage.removeItem('token')
  router.push('/auth')
}

async function handleDeleteAccount() {
  isDeleting.value = true
  try {
    const res = await apiFetch('users/me', {
      method: 'DELETE'
    })

    if (res.ok) {
      handleLogout()
    } else {
      const errorData = await res.json()
      alert(errorData.detail || "Erreur lors de la suppression du compte")
    }
  } catch (error) {
    console.error('Error deleting account:', error)
    alert("Une erreur est survenue")
  } finally {
    isDeleting.value = false
    confirmDelete.value = false
  }
}

onMounted(() => {
  fetchUser()
})
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-12">
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-foreground">Paramètres</h1>
        <p class="text-muted-foreground mt-1">Gérez votre compte, vos préférences et vos abonnements.</p>
      </div>
    </div>

    <Tabs v-model="activeTab" defaultValue="compte" class="space-y-6">
      <div class="overflow-x-auto pb-2 -mx-4 px-4 md:mx-0 md:px-0 scrollbar-hide">
        <TabsList class="bg-muted/50 p-1 rounded-xl w-full md:w-auto h-auto inline-flex min-w-max">
          <TabsTrigger value="compte" class="rounded-lg py-2 px-4 transition-all data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <User class="w-4 h-4 mr-2" /> Compte
          </TabsTrigger>
          <TabsTrigger value="preferences" class="rounded-lg py-2 px-4 transition-all data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <Settings class="w-4 h-4 mr-2" /> Préférences
          </TabsTrigger>
          <TabsTrigger value="abonnement" class="rounded-lg py-2 px-4 transition-all data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <CreditCard class="w-4 h-4 mr-2" /> Abonnement
          </TabsTrigger>
          <TabsTrigger value="facturation" class="rounded-lg py-2 px-4 transition-all data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <Receipt class="w-4 h-4 mr-2" /> Facturation
          </TabsTrigger>
          <TabsTrigger value="support" class="rounded-lg py-2 px-4 transition-all data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <LifeBuoy class="w-4 h-4 mr-2" /> Support
          </TabsTrigger>
        </TabsList>
      </div>

      <!-- Compte Tab -->
      <TabsContent value="compte" class="mt-0">
        <div v-if="isLoading" class="flex items-center justify-center p-12">
          <Loader2 class="w-8 h-8 animate-spin text-primary" />
        </div>
        
        <div v-else class="space-y-6">
          <!-- Information Personnelle -->
          <Card class="border-border/50 shadow-sm overflow-hidden">
            <CardHeader class="pb-4">
              <CardTitle>Mon Compte</CardTitle>
              <CardDescription>Gérez vos informations personnelles et de connexion.</CardDescription>
            </CardHeader>
            <CardContent class="space-y-8">
              <!-- Avatar Section -->
              <div class="flex items-center gap-6 pb-6 border-b border-border/50">
                <div class="relative group">
                  <div class="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center text-primary text-2xl font-bold border-2 border-primary/20 shadow-inner group-hover:scale-105 transition-transform duration-300">
                    {{ initials }}
                  </div>
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-foreground mb-1">Photo de profil</h4>
                  <p class="text-xs text-muted-foreground mb-3">Utilisée pour personnaliser votre interface.</p>
                  <Button variant="outline" size="sm" class="h-8 text-xs disabled:opacity-50" disabled>
                    Changer l'image
                  </Button>
                </div>
              </div>

              <!-- Form Section -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2">
                  <Label for="prenom" class="text-xs uppercase tracking-wider font-bold text-muted-foreground/70">Prénom</Label>
                  <Input 
                    id="prenom" 
                    v-model="form.prenom" 
                    placeholder="Votre prénom" 
                    class="h-11 bg-muted/20 focus:bg-background transition-all"
                  />
                </div>
                <div class="space-y-2">
                  <Label for="nom" class="text-xs uppercase tracking-wider font-bold text-muted-foreground/70">Nom</Label>
                  <Input 
                    id="nom" 
                    v-model="form.nom" 
                    placeholder="Votre nom" 
                    class="h-11 bg-muted/20 focus:bg-background transition-all"
                  />
                </div>
                <div class="space-y-2 md:col-span-2">
                  <Label for="email" class="text-xs uppercase tracking-wider font-bold text-muted-foreground/70">E-mail</Label>
                  <Input 
                    id="email" 
                    v-model="form.email" 
                    type="email" 
                    disabled 
                    class="h-11 bg-muted/10 opacity-70 cursor-not-allowed"
                  />
                  <p class="text-[10px] text-muted-foreground italic">L'e-mail est utilisé pour l'identification et ne peut pas être modifié ici.</p>
                </div>
              </div>

              <div class="flex items-center justify-between pt-4">
                <div class="flex items-center gap-2">
                  <transition name="fade">
                    <div v-if="showSuccess" class="flex items-center text-sm text-green-600 bg-green-50 px-3 py-1.5 rounded-full border border-green-200">
                      <CheckCircle2 class="w-4 h-4 mr-2" />
                      Profil mis à jour !
                    </div>
                  </transition>
                </div>
                <button 
                  @click="handleSave" 
                  :disabled="isSaving"
                  class="btn-primary min-w-[160px]"
                >
                  <template v-if="isSaving">
                    <Loader2 class="w-4 h-4 mr-2 animate-spin" />
                    Enregistrement...
                  </template>
                  <template v-else>
                    <Save class="w-4 h-4 mr-2" />
                    Enregistrer
                  </template>
                </button>
              </div>
            </CardContent>
          </Card>

          <!-- Actions du compte -->
          <Card class="border-border/50 shadow-sm">
            <CardHeader class="pb-4">
              <CardTitle class="text-lg">Actions du compte</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium">Session</p>
                  <p class="text-xs text-muted-foreground italic">Déconnectez-vous de cet appareil.</p>
                </div>
                <Button variant="outline" @click="handleLogout" class="border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700 hover:border-red-300">
                  <LogOut class="w-4 h-4 mr-2" />
                  Déconnexion
                </Button>
              </div>
            </CardContent>
          </Card>

          <!-- Zone de Danger -->
          <Card class="border-destructive/20 bg-destructive/[0.02] shadow-sm">
            <CardHeader class="pb-4">
              <CardTitle class="text-lg text-destructive flex items-center gap-2">
                <AlertTriangle class="w-5 h-5" />
                Zone de Danger
              </CardTitle>
              <CardDescription>Ces actions sont irréversibles.</CardDescription>
            </CardHeader>
            <CardContent>
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-semibold">Supprimer mon compte</p>
                  <p class="text-xs text-muted-foreground max-w-sm mt-1">
                    Supprime définitivement votre accès et toutes vos données (devis, rapports, clients).
                  </p>
                </div>
                <Button variant="destructive" @click="confirmDelete = true">
                  <Trash2 class="w-4 h-4 mr-2" />
                  Supprimer
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </TabsContent>

      <!-- Placeholder content for other tabs -->
      <TabsContent v-for="tab in ['preferences', 'abonnement', 'facturation', 'support']" :key="tab" :value="tab">
        <Card class="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle class="capitalize">{{ tab }}</CardTitle>
            <CardDescription>Cette section est en cours de développement.</CardDescription>
          </CardHeader>
          <CardContent class="py-12 flex flex-col items-center justify-center text-center">
            <div class="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
              <Settings v-if="tab === 'preferences'" class="w-8 h-8 text-muted-foreground" />
              <CreditCard v-if="tab === 'abonnement'" class="w-8 h-8 text-muted-foreground" />
              <Receipt v-if="tab === 'facturation'" class="w-8 h-8 text-muted-foreground" />
              <LifeBuoy v-if="tab === 'support'" class="w-8 h-8 text-muted-foreground" />
            </div>
            <p class="text-muted-foreground max-w-xs">Nous travaillons activement sur cette fonctionnalité pour vous offrir la meilleure expérience possible.</p>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>

    <!-- Modal de confirmation de suppression -->
    <transition name="modal">
      <div v-if="confirmDelete" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-background/80 backdrop-blur-sm" @click="confirmDelete = false"></div>
        
        <Card class="relative w-full max-w-md border-destructive/20 shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-300">
          <CardHeader class="pb-4">
            <div class="w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center text-destructive mb-4">
              <AlertTriangle class="w-6 h-6" />
            </div>
            <CardTitle class="text-xl">Supprimer le compte ?</CardTitle>
            <CardDescription class="text-base text-foreground/80 mt-2">
              Cette action est <span class="font-bold text-destructive underline">irréversible</span>. Toutes vos données seront définitivement effacées.
            </CardDescription>
          </CardHeader>
          <CardContent class="pb-6">
            <div class="p-3 rounded-lg bg-muted/50 mb-6">
              <p class="text-xs text-muted-foreground leading-relaxed uppercase tracking-wider font-bold mb-2">Sont inclus dans la suppression :</p>
              <ul class="text-xs space-y-1.5 text-muted-foreground">
                <li class="flex items-center gap-2"><div class="w-1 h-1 rounded-full bg-muted-foreground"></div> Votre société et son profil</li>
                <li class="flex items-center gap-2"><div class="w-1 h-1 rounded-full bg-muted-foreground"></div> Tous vos rapports d'intervention</li>
                <li class="flex items-center gap-2"><div class="w-1 h-1 rounded-full bg-muted-foreground"></div> L'historique de vos devis et factures</li>
                <li class="flex items-center gap-2"><div class="w-1 h-1 rounded-full bg-muted-foreground"></div> Votre carnet de clients</li>
              </ul>
            </div>
            
            <div class="flex flex-col sm:flex-row gap-3">
              <Button variant="outline" @click="confirmDelete = false" :disabled="isDeleting" class="flex-1 order-2 sm:order-1 h-12">
                Annuler
              </Button>
              <Button variant="destructive" @click="handleDeleteAccount" :disabled="isDeleting" class="flex-1 order-1 sm:order-2 h-12 shadow-lg shadow-destructive/10">
                <template v-if="isDeleting">
                  <Loader2 class="w-4 h-4 mr-2 animate-spin" />
                  Suppression...
                </template>
                <template v-else>
                  <Trash2 class="w-4 h-4 mr-2" />
                  Confirmer
                </template>
              </Button>
            </div>
          </CardContent>
          <button @click="confirmDelete = false" class="absolute top-4 right-4 text-muted-foreground hover:text-foreground transition-colors p-2 rounded-md hover:bg-muted">
            <X class="w-4 h-4" />
          </button>
        </Card>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(5px);
}

.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
