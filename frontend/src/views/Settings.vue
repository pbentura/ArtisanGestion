<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { API_BASE_URL } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  User, Settings, CreditCard, Receipt, LifeBuoy, Loader2, Save, CheckCircle2
} from 'lucide-vue-next'

const activeTab = ref('compte')
const isLoading = ref(true)
const isSaving = ref(false)
const showSuccess = ref(false)

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
  const token = localStorage.getItem('token')
  try {
    const res = await fetch(`${API_BASE_URL}/api/users/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
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
  const token = localStorage.getItem('token')
  try {
    const res = await fetch(`${API_BASE_URL}/api/users/me`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
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
                <Button 
                  @click="handleSave" 
                  :disabled="isSaving"
                  class="min-w-[160px] shadow-lg shadow-primary/10"
                >
                  <template v-if="isSaving">
                    <Loader2 class="w-4 h-4 mr-2 animate-spin" />
                    Enregistrement...
                  </template>
                  <template v-else>
                    <Save class="w-4 h-4 mr-2" />
                    Enregistrer
                  </template>
                </Button>
              </div>
            </CardContent>
          </Card>

          <!-- Security Section Placeholder -->
          <Card class="border-border/50 shadow-sm opacity-60">
            <CardHeader class="pb-2">
              <CardTitle class="text-lg">Sécurité</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium">Mot de passe</p>
                  <p class="text-xs text-muted-foreground">Dernière modification il y a 3 mois</p>
                </div>
                <Button variant="outline" size="sm" disabled>Modifier</Button>
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

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
