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
  LogOut, Trash2, AlertTriangle, X, Check, Sparkles, Zap, Palette,
  Lock, RotateCcw, Eye, EyeOff, ShieldCheck, KeyRound, Info, ChevronDown
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const activeTab = ref((route.query.tab as string) || 'compte')
const isMobileMenuOpen = ref(false)
const isLoading = ref(true)
const isSaving = ref(false)
const isDeleting = ref(false)
const showSuccess = ref(false)
const confirmDelete = ref(false)
const isAnnual = ref(false)
const loadingPlan = ref<string | null>(null)

const allTabs = [
  { value: 'compte', label: 'Mon Compte', icon: User, description: 'Profil, sécurité & mot de passe', ownerOnly: false },
  { value: 'preferences', label: 'Préférences', icon: Settings, description: 'Personnalisation des devis & PDF', ownerOnly: false },
  { value: 'abonnement', label: 'Abonnement', icon: CreditCard, description: 'Forfait & gestion des accès', ownerOnly: true },
  { value: 'facturation', label: 'Facturation', icon: Receipt, description: 'Historique & coordonnées bancaires', ownerOnly: false },
  { value: 'support', label: 'Support & Aide', icon: LifeBuoy, description: 'Centre d\'aide & assistance', ownerOnly: false },
]

const availableTabs = computed(() => {
  return allTabs.filter(tab => !tab.ownerOnly || user.value.is_owner)
})

const currentTabInfo = computed(() => {
  return availableTabs.value.find(tab => tab.value === activeTab.value) || availableTabs.value[0] || {
    value: 'compte',
    label: 'Mon Compte',
    icon: User,
    description: 'Profil, sécurité & mot de passe'
  }
})

function selectTab(val: string) {
  activeTab.value = val
  isMobileMenuOpen.value = false
  router.replace({ query: { ...route.query, tab: val } })
}

// Préférences documents
const societe = ref<any>(null)
const selectedColor = ref('#2563eb')
const isSavingPreferences = ref(false)
const showPreferencesSuccess = ref(false)
const previewDocType = ref<'facture' | 'devis' | 'rapport'>('facture')

const colorPalettes = [
  {
    name: 'Bleus & Océan',
    colors: ['#2563eb', '#1d4ed8', '#0284c7', '#0ea5e9', '#06b6d4', '#0891b2']
  },
  {
    name: 'Verts & Nature',
    colors: ['#059669', '#10b981', '#16a34a', '#22c55e', '#15803d', '#84cc16']
  },
  {
    name: 'Violets & Élégance',
    colors: ['#4f46e5', '#6366f1', '#7c3aed', '#8b5cf6', '#9333ea', '#a855f7']
  },
  {
    name: 'Rouges & Passion',
    colors: ['#dc2626', '#ef4444', '#e11d48', '#be123c', '#ec4899', '#db2777']
  },
  {
    name: 'Oranges & Chaleur',
    colors: ['#ea580c', '#f97316', '#d97706', '#f59e0b', '#eab308', '#ca8a04']
  },
  {
    name: 'Neutres & Moderne',
    colors: ['#0f172a', '#1e293b', '#334155', '#475569', '#374151', '#78716c']
  }
]

const plans = [
  {
    name: 'Indépendant',
    description: 'Pour l\'artisan seul',
    priceMonthly: '19',
    priceAnnual: '15.50',
    features: [
      '1 Utilisateur',
      'Accès IA pour les rapports',
      'Clients, rapports, devis & factures illimités',
      'Signature électronique sur place',
      'PDF avec logo et thème ArtisanGestion',
      'Dashboard complet',
    ],
    cta: 'S\'abonner',
    popular: false,
    gradient: '',
  },
  {
    name: 'Équipe',
    description: 'Pour vous et vos collaborateurs',
    priceMonthly: '39',
    priceAnnual: '32.50',
    features: [
      'Équipe avec gestion des droits',
      'Signature électronique à distance',
      'Personnalisation des PDF (couleurs et sans logo)',
      'Relances impayés automatiques',
    ],
    cta: 'S\'abonner',
    popular: true,
    gradient: 'from-primary to-blue-700',
  }
]

async function handleSubscribe(plan: any) {
  loadingPlan.value = plan.name
  try {
    const res = await apiFetch('subscriptions/create-checkout-session', {
      method: 'POST',
      body: JSON.stringify({
        plan_name: plan.name,
        is_annual: isAnnual.value,
        price: isAnnual.value ? parseFloat(plan.priceAnnual) * 12 : parseFloat(plan.priceMonthly)
      })
    })

    if (res.ok) {
      const data = await res.json()
      if (data.checkout_url) {
        window.location.href = data.checkout_url
      }
    } else {
      const errorData = await res.json()
      alert(errorData.detail || "Erreur lors de la création de la session de paiement")
    }
  } catch (error) {
    console.error('Error creating checkout session:', error)
    alert("Une erreur est survenue")
  } finally {
    loadingPlan.value = null
  }
}

async function handleManageSubscription() {
  try {
    const res = await apiFetch('subscriptions/create-portal-session', {
      method: 'POST'
    })

    if (res.ok) {
      const data = await res.json()
      if (data.portal_url) {
        window.location.href = data.portal_url
      }
    } else {
      const errorData = await res.json()
      alert(errorData.detail || "Erreur lors de la création de la session de portail")
    }
  } catch (error) {
    console.error('Error opening portal:', error)
    alert("Une erreur est survenue")
  }
}

const user = ref({
  nom: '',
  prenom: '',
  email: '',
  role: '',
  trial_days_remaining: 0,
  is_owner: true,
  has_password: false
})

const form = ref({
  nom: '',
  prenom: '',
  email: ''
})

// Gestion du mot de passe
const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const isSavingPassword = ref(false)
const passwordError = ref('')
const showPasswordSuccess = ref(false)

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

async function handleUpdatePassword() {
  passwordError.value = ''
  showPasswordSuccess.value = false

  if (user.value.has_password && !passwordForm.value.current_password) {
    passwordError.value = "Veuillez saisir votre mot de passe actuel."
    return
  }

  if (!passwordForm.value.new_password) {
    passwordError.value = "Veuillez saisir un nouveau mot de passe."
    return
  }

  if (passwordForm.value.new_password.length < 6) {
    passwordError.value = "Le mot de passe doit contenir au moins 6 caractères."
    return
  }

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = "Les mots de passe ne correspondent pas."
    return
  }

  isSavingPassword.value = true
  try {
    const res = await apiFetch('users/me/password', {
      method: 'PUT',
      body: JSON.stringify({
        current_password: user.value.has_password ? passwordForm.value.current_password : null,
        new_password: passwordForm.value.new_password
      })
    })

    if (res.ok) {
      user.value.has_password = true
      passwordForm.value = {
        current_password: '',
        new_password: '',
        confirm_password: ''
      }
      showPasswordSuccess.value = true
      setTimeout(() => {
        showPasswordSuccess.value = false
      }, 4000)
    } else {
      const errorData = await res.json()
      passwordError.value = errorData.detail || "Erreur lors de la mise à jour du mot de passe."
    }
  } catch (error) {
    console.error('Error updating password:', error)
    passwordError.value = "Une erreur inattendue est survenue."
  } finally {
    isSavingPassword.value = false
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

const isTeamOrAdmin = computed(() => ['TEAM', 'ADMIN'].includes(user.value.role))
const isInTrial = computed(() => (user.value.trial_days_remaining ?? 0) > 0)
const hasAccessToCustomization = computed(() => isTeamOrAdmin.value || isInTrial.value)

function darkenHex(hex: string, amount = 25): string {
  const h = hex.replace('#', '')
  if (h.length !== 6) return hex
  const r = parseInt(h.substring(0, 2), 16)
  const g = parseInt(h.substring(2, 4), 16)
  const b = parseInt(h.substring(4, 6), 16)
  const clamp = (v: number) => Math.max(0, Math.min(255, v - amount))
  return `#${clamp(r).toString(16).padStart(2, '0')}${clamp(g).toString(16).padStart(2, '0')}${clamp(b).toString(16).padStart(2, '0')}`
}

function selectColor(color: string) {
  selectedColor.value = color
}

function resetToDefaultColor() {
  selectedColor.value = '#2563eb'
}

async function fetchSociete() {
  try {
    const res = await apiFetch('societes/me')
    if (res.ok) {
      const data = await res.json()
      societe.value = data
      selectedColor.value = data.couleur_document || '#2563eb'
    }
  } catch (error) {
    console.error('Error fetching societe:', error)
  }
}

async function handleSavePreferences() {
  if (!hasAccessToCustomization.value) {
    activeTab.value = 'abonnement'
    return
  }

  isSavingPreferences.value = true
  try {
    const res = await apiFetch('societes/me', {
      method: 'PATCH',
      body: JSON.stringify({
        couleur_document: selectedColor.value
      })
    })

    if (res.ok) {
      const updated = await res.json()
      societe.value = updated
      showPreferencesSuccess.value = true
      setTimeout(() => {
        showPreferencesSuccess.value = false
      }, 3000)
    } else {
      const errorData = await res.json()
      alert(errorData.detail || "Erreur lors de la sauvegarde")
    }
  } catch (error) {
    console.error('Error saving preferences:', error)
    alert("Une erreur est survenue")
  } finally {
    isSavingPreferences.value = false
  }
}

onMounted(() => {
  fetchUser()
  fetchSociete()
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
      <!-- Mobile Dropdown Selector (< md) -->
      <div class="block md:hidden relative">
        <!-- Backdrop -->
        <div 
          v-if="isMobileMenuOpen" 
          class="fixed inset-0 z-30 bg-background/50 backdrop-blur-xs transition-opacity" 
          @click="isMobileMenuOpen = false"
        />

        <!-- Trigger Button Card -->
        <button
          type="button"
          @click="isMobileMenuOpen = !isMobileMenuOpen"
          class="w-full relative z-40 flex items-center justify-between p-3.5 bg-card border border-border/80 rounded-2xl shadow-xs active:scale-[0.99] transition-all duration-200 text-left focus:outline-none focus:ring-2 focus:ring-primary/20"
          :class="{ 'ring-2 ring-primary/20 border-primary/50 shadow-md': isMobileMenuOpen }"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0 border border-primary/20">
              <component :is="currentTabInfo.icon" class="w-5 h-5" />
            </div>
            <div class="min-w-0">
              <div class="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Onglet actif</div>
              <div class="text-sm font-bold text-foreground truncate">{{ currentTabInfo.label }}</div>
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0 ml-2">
            <span class="text-xs font-medium text-primary bg-primary/10 px-2.5 py-1 rounded-full">Changer</span>
            <ChevronDown 
              class="w-4 h-4 text-muted-foreground transition-transform duration-300"
              :class="{ 'rotate-180 text-primary': isMobileMenuOpen }" 
            />
          </div>
        </button>

        <!-- Dropdown Popup Menu -->
        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="transform scale-95 opacity-0 -translate-y-2"
          enter-to-class="transform scale-100 opacity-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="transform scale-100 opacity-100 translate-y-0"
          leave-to-class="transform scale-95 opacity-0 -translate-y-2"
        >
          <div 
            v-if="isMobileMenuOpen" 
            class="absolute z-40 left-0 right-0 mt-2 p-1.5 bg-card/95 backdrop-blur-xl border border-border/80 rounded-2xl shadow-xl space-y-1 overflow-hidden ring-1 ring-black/5 dark:ring-white/5"
          >
            <button
              v-for="item in availableTabs"
              :key="item.value"
              type="button"
              @click="selectTab(item.value)"
              class="w-full flex items-center justify-between p-2.5 rounded-xl transition-all text-left group"
              :class="activeTab === item.value 
                ? 'bg-primary/10 text-primary font-medium' 
                : 'hover:bg-muted/70 text-muted-foreground hover:text-foreground active:bg-muted'"
            >
              <div class="flex items-center gap-3 min-w-0">
                <div 
                  class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-colors"
                  :class="activeTab === item.value ? 'bg-primary text-primary-foreground shadow-xs' : 'bg-muted text-muted-foreground group-hover:text-foreground'"
                >
                  <component :is="item.icon" class="w-4 h-4" />
                </div>
                <div class="min-w-0">
                  <div class="text-sm font-semibold truncate" :class="activeTab === item.value ? 'text-primary' : 'text-foreground'">
                    {{ item.label }}
                  </div>
                  <div class="text-xs text-muted-foreground line-clamp-1">
                    {{ item.description }}
                  </div>
                </div>
              </div>
              <div v-if="activeTab === item.value" class="w-5 h-5 rounded-full bg-primary/20 text-primary flex items-center justify-center shrink-0 ml-2">
                <Check class="w-3 h-3 stroke-[2.5]" />
              </div>
            </button>
          </div>
        </Transition>
      </div>

      <!-- Desktop TabsList (md+) -->
      <div class="hidden md:block">
        <TabsList class="bg-muted/50 p-1 rounded-xl w-auto h-auto inline-flex border border-border/40">
          <TabsTrigger value="compte" class="rounded-lg py-2 px-4 transition-all data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <User class="w-4 h-4 mr-2" /> Compte
          </TabsTrigger>
          <TabsTrigger value="preferences" class="rounded-lg py-2 px-4 transition-all data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <Settings class="w-4 h-4 mr-2" /> Préférences
          </TabsTrigger>
          <TabsTrigger v-if="user.is_owner" value="abonnement" class="rounded-lg py-2 px-4 transition-all data-[state=active]:bg-background data-[state=active]:shadow-sm">
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

              <!-- Section Sécurité & Mot de passe -->
              <div class="border-t border-border/50 pt-8 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary shrink-0">
                      <KeyRound class="w-5 h-5" />
                    </div>
                    <div>
                      <h4 class="text-sm font-semibold text-foreground">
                        {{ user.has_password ? 'Modifier mon mot de passe' : 'Définir un mot de passe' }}
                      </h4>
                      <p class="text-xs text-muted-foreground mt-0.5">
                        {{ user.has_password 
                          ? 'Mettez à jour votre mot de passe pour sécuriser l\'accès à votre compte.' 
                          : 'Ajoutez un mot de passe pour pouvoir vous connecter avec votre email sans passer par Google.' 
                        }}
                      </p>
                    </div>
                  </div>
                  
                  <div v-if="!user.has_password" class="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-full text-xs font-medium border border-amber-500/20 self-start sm:self-auto shrink-0">
                    <Sparkles class="w-3.5 h-3.5" />
                    Compte Google sans mot de passe
                  </div>
                  <div v-else class="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-full text-xs font-medium border border-emerald-500/20 self-start sm:self-auto shrink-0">
                    <ShieldCheck class="w-3.5 h-3.5" />
                    Mot de passe actif
                  </div>
                </div>

                <div v-if="!user.has_password" class="p-3.5 rounded-xl bg-blue-50/60 dark:bg-blue-950/20 border border-blue-200/60 dark:border-blue-800/40 flex items-start gap-3">
                  <Info class="w-4 h-4 text-blue-600 dark:text-blue-400 mt-0.5 shrink-0" />
                  <p class="text-xs text-blue-800 dark:text-blue-300 leading-relaxed">
                    Votre compte a été initialisé via Google OAuth. En définissant un mot de passe ici, vous pourrez vous connecter au choix avec Google ou avec votre identifiant email et mot de passe.
                  </p>
                </div>

                <form @submit.prevent="handleUpdatePassword" class="space-y-4">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Ancien mot de passe (si mot de passe existant) -->
                    <div v-if="user.has_password" class="space-y-2 md:col-span-2">
                      <Label for="current_password" class="text-xs uppercase tracking-wider font-bold text-muted-foreground/70">
                        Ancien mot de passe
                      </Label>
                      <div class="relative">
                        <Input 
                          id="current_password" 
                          v-model="passwordForm.current_password" 
                          :type="showCurrentPassword ? 'text' : 'password'" 
                          placeholder="Saisissez votre ancien mot de passe" 
                          class="h-11 bg-muted/20 focus:bg-background transition-all pr-10"
                          autocomplete="current-password"
                        />
                        <button 
                          type="button" 
                          @click="showCurrentPassword = !showCurrentPassword" 
                          class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors p-1"
                          tabindex="-1"
                        >
                          <EyeOff v-if="showCurrentPassword" class="w-4 h-4" />
                          <Eye v-else class="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <!-- Nouveau mot de passe -->
                    <div class="space-y-2" :class="{ 'md:col-span-1': true }">
                      <Label for="new_password" class="text-xs uppercase tracking-wider font-bold text-muted-foreground/70">
                        Nouveau mot de passe
                      </Label>
                      <div class="relative">
                        <Input 
                          id="new_password" 
                          v-model="passwordForm.new_password" 
                          :type="showNewPassword ? 'text' : 'password'" 
                          placeholder="Au moins 6 caractères" 
                          class="h-11 bg-muted/20 focus:bg-background transition-all pr-10"
                          autocomplete="new-password"
                        />
                        <button 
                          type="button" 
                          @click="showNewPassword = !showNewPassword" 
                          class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors p-1"
                          tabindex="-1"
                        >
                          <EyeOff v-if="showNewPassword" class="w-4 h-4" />
                          <Eye v-else class="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <!-- Confirmer le mot de passe -->
                    <div class="space-y-2" :class="{ 'md:col-span-1': true }">
                      <Label for="confirm_password" class="text-xs uppercase tracking-wider font-bold text-muted-foreground/70">
                        Confirmer le mot de passe
                      </Label>
                      <div class="relative">
                        <Input 
                          id="confirm_password" 
                          v-model="passwordForm.confirm_password" 
                          :type="showConfirmPassword ? 'text' : 'password'" 
                          placeholder="Confirmez le mot de passe" 
                          class="h-11 bg-muted/20 focus:bg-background transition-all pr-10"
                          autocomplete="new-password"
                        />
                        <button 
                          type="button" 
                          @click="showConfirmPassword = !showConfirmPassword" 
                          class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors p-1"
                          tabindex="-1"
                        >
                          <EyeOff v-if="showConfirmPassword" class="w-4 h-4" />
                          <Eye v-else class="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- Message d'erreur -->
                  <div v-if="passwordError" class="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs flex items-center gap-2">
                    <AlertTriangle class="w-4 h-4 shrink-0" />
                    <span>{{ passwordError }}</span>
                  </div>

                  <!-- Actions et succès -->
                  <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2">
                    <div>
                      <transition name="fade">
                        <div v-if="showPasswordSuccess" class="flex items-center text-sm text-green-600 bg-green-50 px-3 py-1.5 rounded-full border border-green-200">
                          <CheckCircle2 class="w-4 h-4 mr-2" />
                          {{ user.has_password ? 'Mot de passe mis à jour !' : 'Mot de passe créé avec succès !' }}
                        </div>
                      </transition>
                    </div>

                    <Button 
                      type="submit" 
                      :disabled="isSavingPassword || !passwordForm.new_password || !passwordForm.confirm_password"
                      class="min-w-[190px]"
                    >
                      <template v-if="isSavingPassword">
                        <Loader2 class="w-4 h-4 mr-2 animate-spin" />
                        Enregistrement...
                      </template>
                      <template v-else>
                        <Lock class="w-4 h-4 mr-2" />
                        {{ user.has_password ? 'Modifier le mot de passe' : 'Définir le mot de passe' }}
                      </template>
                    </Button>
                  </div>
                </form>
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

      <!-- Abonnement Tab -->
      <TabsContent v-if="user.is_owner" value="abonnement">
        <div class="space-y-6">
          <div class="pricing-header text-center mb-8 mt-4">
            <h2 class="text-2xl font-bold text-foreground mb-4">
              Gérer mon abonnement
            </h2>
            <div v-if="user.role === 'ADMIN'" class="inline-flex items-center gap-2 px-4 py-2 bg-purple-50 text-purple-700 rounded-full text-sm font-semibold mb-4 border border-purple-200">
              <CheckCircle2 class="w-4 h-4" />
              Plan Max Actif (Administrateur)
            </div>
            <div v-else-if="user.role === 'PREMIUM' || user.role === 'TEAM'" class="inline-flex flex-col items-center gap-2 mb-4">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-full text-sm font-semibold border border-primary/20">
                <CheckCircle2 class="w-4 h-4" />
                Plan {{ user.role === 'PREMIUM' ? 'Indépendant' : 'Équipe' }} Actif
              </div>
              <Button variant="outline" size="sm" @click="handleManageSubscription" class="mt-2">
                <CreditCard class="w-4 h-4 mr-2" />
                Gérer mon abonnement (Factures, Annulation)
              </Button>
            </div>
            <div v-else-if="user.trial_days_remaining > 0" class="inline-flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-full text-sm font-semibold mb-4 border border-green-200">
              <CheckCircle2 class="w-4 h-4" />
              Il vous reste {{ user.trial_days_remaining }} jours d'essai gratuit
            </div>
            <div v-else class="inline-flex items-center gap-2 px-4 py-2 bg-destructive/10 text-destructive rounded-full text-sm font-semibold mb-4 border border-destructive/20">
              <AlertTriangle class="w-4 h-4" />
              Votre période d'essai est terminée. Passez à un plan supérieur pour continuer à créer des documents.
            </div>
            <p class="text-sm text-muted-foreground max-w-xl mx-auto">
              Choisissez le plan qui correspond le mieux à vos besoins actuels.
            </p>
          </div>

          <!-- Toggle -->
          <div class="flex justify-center mb-8">
            <div class="relative flex items-center p-1 bg-muted/50 rounded-full border border-border/50">
              <button
                @click="isAnnual = false"
                class="relative w-32 py-2 text-sm font-medium rounded-full transition-colors z-10"
                :class="!isAnnual ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'"
              >
                Mensuel
              </button>
              <button
                @click="isAnnual = true"
                class="relative w-32 py-2 text-sm font-medium rounded-full transition-colors z-10 flex items-center justify-center gap-2"
                :class="isAnnual ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'"
              >
                Annuel
                <span class="text-[10px] font-bold bg-primary/10 text-primary px-1.5 py-0.5 rounded-full">-18%</span>
              </button>
              <!-- Sliding indicator -->
              <div
                class="absolute left-1 top-1 bottom-1 w-32 bg-background shadow-sm rounded-full transition-transform duration-300 ease-in-out border border-border/50"
                :class="isAnnual ? 'translate-x-full' : 'translate-x-0'"
              />
            </div>
          </div>

          <!-- Cards -->
          <div class="pricing-grid grid md:grid-cols-2 gap-6 items-start">
            <div
              v-for="(plan, i) in plans"
              :key="i"
              class="pricing-card relative transition-all duration-500"
              :class="plan.popular ? 'z-10' : ''"
            >
              <div v-if="plan.popular" class="absolute -top-3 left-1/2 -translate-x-1/2 z-20">
                <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-primary text-primary-foreground text-[10px] uppercase font-bold shadow-sm">
                  <Sparkles class="h-3 w-3" />
                  Recommandé
                </span>
              </div>

              <div 
                class="h-full rounded-2xl overflow-hidden transition-all duration-300 bg-card border"
                :class="[
                  plan.popular
                    ? 'border-primary/50 shadow-md'
                    : 'border-border/50'
                ]"
              >
                <div v-if="plan.popular" class="h-1 w-full bg-gradient-to-r" :class="plan.gradient" />

                <div class="p-6">
                  <!-- Plan info -->
                  <div class="mb-4" :class="plan.popular ? 'pt-2' : ''">
                    <h3 class="text-lg font-bold text-foreground">{{ plan.name }}</h3>
                    <p class="text-xs text-muted-foreground">{{ plan.description }}</p>
                  </div>

                  <!-- Price -->
                  <div class="mb-6">
                    <div class="flex items-baseline gap-1">
                      <span class="text-4xl font-extrabold text-foreground">{{ isAnnual ? plan.priceAnnual : plan.priceMonthly }}€</span>
                      <span class="text-muted-foreground text-xs">/mois</span>
                    </div>
                    <p class="text-[10px] text-muted-foreground mt-1">
                      {{ isAnnual ? 'HT, facturé annuellement' : 'HT, sans engagement' }}
                    </p>
                  </div>

                  <!-- Features -->
                  <ul class="space-y-2.5 mb-6">
                    <li v-for="(feature, fi) in plan.features" :key="fi" class="flex items-start gap-2.5">
                      <div class="w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" :class="plan.popular ? 'bg-primary/15' : 'bg-primary/10'">
                        <Check class="h-2.5 w-2.5 text-primary" />
                      </div>
                      <span class="text-xs text-muted-foreground">{{ feature }}</span>
                    </li>
                  </ul>

                  <!-- CTA -->
                  <button
                    @click="handleSubscribe(plan)"
                    :disabled="loadingPlan !== null"
                    class="w-full py-2.5 rounded-xl font-semibold text-sm transition-all duration-300 flex items-center justify-center gap-2"
                    :class="plan.popular
                      ? 'bg-primary text-primary-foreground hover:opacity-90'
                      : 'bg-muted text-foreground hover:bg-primary/10 hover:text-primary'"
                  >
                    <Loader2 v-if="loadingPlan === plan.name" class="w-4 h-4 animate-spin" />
                    <template v-else>
                      <Zap v-if="plan.popular" class="h-3.5 w-3.5" />
                      {{ plan.cta }}
                    </template>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </TabsContent>

      <!-- Préférences Tab -->
      <TabsContent value="preferences" class="mt-0 space-y-6">
        <!-- 1. Plan Équipe Subscribed -->
        <div v-if="isTeamOrAdmin" class="flex items-center gap-3 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-400">
          <ShieldCheck class="w-5 h-5 shrink-0 text-emerald-600 dark:text-emerald-400" />
          <p class="text-xs md:text-sm font-medium">
            <strong>Plan Équipe actif</strong> : vos documents reflètent votre identité visuelle et la mention ArtisanGestion est automatiquement retirée.
          </p>
        </div>

        <!-- 2. Active Trial (Included for 14 days) -->
        <div v-else-if="isInTrial" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-green-500/10 border border-green-500/20 text-green-800 dark:text-green-300">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg bg-green-500/20 flex items-center justify-center shrink-0 text-green-600 dark:text-green-400">
              <Sparkles class="w-5 h-5" />
            </div>
            <div>
              <div class="text-xs md:text-sm font-bold flex items-center gap-2">
                <span>Période d'essai gratuit active</span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-600 text-white">
                  {{ user.trial_days_remaining }} jours restants
                </span>
              </div>
              <p class="text-xs text-muted-foreground mt-0.5">
                La personnalisation de vos documents (couleurs & sans mention externe) est <strong>incluse</strong> pendant votre essai de 14 jours !
              </p>
            </div>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            @click="activeTab = 'abonnement'"
            class="border-green-300 text-green-700 hover:bg-green-100 dark:border-green-700 dark:text-green-300 text-xs shrink-0"
          >
            Voir les abonnements
          </Button>
        </div>

        <!-- 3. Trial Ended - Upgrade Required -->
        <div 
          v-else
          class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600/10 via-indigo-600/10 to-purple-600/10 border border-blue-500/20 p-6 md:p-8"
        >
          <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
            <div class="space-y-2">
              <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary text-primary-foreground text-xs font-bold uppercase tracking-wider shadow-sm">
                <Sparkles class="w-3.5 h-3.5" />
                Exclusivité Plan Équipe (39€/mois)
              </div>
              <h3 class="text-xl font-bold text-foreground">Votre période d'essai est terminée</h3>
              <p class="text-sm text-muted-foreground max-w-2xl">
                Passez au <strong>Plan Équipe (39€/mois)</strong> pour continuer à personnaliser vos devis, factures et rapports d'intervention avec vos couleurs et retirer la mention "Généré via ArtisanGestion".
              </p>
            </div>
            <Button 
              @click="activeTab = 'abonnement'" 
              class="btn-primary shrink-0 shadow-lg shadow-primary/20 gap-2 h-11 px-6 text-sm font-semibold"
            >
              <Zap class="w-4 h-4" />
              Passer au Plan Équipe
            </Button>
          </div>
        </div>

        <!-- Main Customization Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <!-- Left Column: Color Pickers & Controls -->
          <div class="lg:col-span-6 space-y-6">
            <Card class="border-border/50 shadow-sm overflow-hidden">
              <CardHeader class="pb-4">
                <div class="flex items-center justify-between">
                  <div class="space-y-1">
                    <CardTitle class="text-lg flex items-center gap-2">
                      <Palette class="w-5 h-5 text-primary" />
                      Couleur des documents
                    </CardTitle>
                    <CardDescription>
                      Sélectionnez la couleur d'accentuation appliquée sur l'ensemble de vos documents (factures, devis, rapports).
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>

              <CardContent class="space-y-6">
                <!-- Color Palettes by theme -->
                <div class="space-y-4">
                  <div 
                    v-for="(palette, pIdx) in colorPalettes" 
                    :key="pIdx" 
                    class="space-y-2"
                  >
                    <span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      {{ palette.name }}
                    </span>
                    <div class="grid grid-cols-6 gap-2">
                      <button
                        v-for="color in palette.colors"
                        :key="color"
                        type="button"
                        @click="selectColor(color)"
                        class="group relative h-10 w-full rounded-xl transition-all duration-200 flex items-center justify-center shadow-sm hover:scale-105 active:scale-95 focus:outline-none"
                        :style="{ backgroundColor: color }"
                        :title="color"
                      >
                        <span 
                          v-if="selectedColor.toLowerCase() === color.toLowerCase()"
                          class="w-5 h-5 rounded-full bg-white/90 shadow-md flex items-center justify-center animate-in zoom-in-50 duration-150"
                        >
                          <Check class="w-3.5 h-3.5 text-gray-900 stroke-[3]" />
                        </span>
                        <span 
                          v-else
                          class="opacity-0 group-hover:opacity-100 transition-opacity w-2 h-2 rounded-full bg-white/60"
                        />
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Custom Hex & Reset -->
                <div class="pt-4 border-t border-border/50 space-y-4">
                  <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
                    <div class="flex items-center gap-3">
                      <div class="relative flex items-center">
                        <input 
                          type="color" 
                          v-model="selectedColor"
                          class="w-11 h-11 p-1 rounded-xl border border-border bg-background cursor-pointer shadow-sm transition-transform hover:scale-105"
                          title="Choisir une couleur libre"
                        />
                      </div>
                      <div class="space-y-1">
                        <Label class="text-xs uppercase font-bold text-muted-foreground">Code Hex</Label>
                        <div class="flex items-center gap-1.5">
                          <Input 
                            v-model="selectedColor" 
                            placeholder="#2563eb"
                            class="h-9 w-28 font-mono text-xs uppercase"
                            maxlength="7"
                          />
                        </div>
                      </div>
                    </div>

                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      @click="resetToDefaultColor"
                      class="h-9 text-xs text-muted-foreground hover:text-foreground gap-1.5 self-end sm:self-auto"
                    >
                      <RotateCcw class="w-3.5 h-3.5" />
                      Bleu par défaut
                    </Button>
                  </div>
                </div>

                <!-- Save Action -->
                <div class="pt-4 border-t border-border/50 flex items-center justify-between gap-4">
                  <div>
                    <transition name="fade">
                      <div v-if="showPreferencesSuccess" class="flex items-center text-xs text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 dark:text-emerald-400 px-3 py-1.5 rounded-full border border-emerald-200 dark:border-emerald-800">
                        <CheckCircle2 class="w-3.5 h-3.5 mr-1.5" />
                        Couleur enregistrée avec succès !
                      </div>
                    </transition>
                  </div>

                  <div class="flex items-center gap-2">
                    <Button 
                      v-if="!hasAccessToCustomization"
                      @click="activeTab = 'abonnement'"
                      class="btn-primary h-10 px-5 text-xs font-semibold gap-2"
                    >
                      <Lock class="w-3.5 h-3.5" />
                      Débloquer (Plan Équipe)
                    </Button>
                    <Button 
                      v-else
                      @click="handleSavePreferences" 
                      :disabled="isSavingPreferences"
                      class="btn-primary min-w-[150px] h-10 text-xs font-semibold gap-2"
                    >
                      <template v-if="isSavingPreferences">
                        <Loader2 class="w-3.5 h-3.5 animate-spin" />
                        Enregistrement...
                      </template>
                      <template v-else>
                        <Save class="w-3.5 h-3.5" />
                        Enregistrer
                      </template>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <!-- Right Column: Live Interactive Document Preview with Logo -->
          <div class="lg:col-span-6 space-y-4 lg:sticky lg:top-6">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-1">
              <div class="flex items-center gap-2 text-sm font-semibold text-foreground">
                <Eye class="w-4 h-4 text-primary" />
                Aperçu en temps réel
              </div>
              
              <!-- Document Type Selector -->
              <div class="inline-flex p-0.5 rounded-lg bg-muted/80 border border-border/50 text-xs">
                <button
                  type="button"
                  @click="previewDocType = 'facture'"
                  class="px-2.5 py-1 rounded-md transition-all font-medium"
                  :class="previewDocType === 'facture' ? 'bg-background shadow-xs text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'"
                >
                  Facture
                </button>
                <button
                  type="button"
                  @click="previewDocType = 'devis'"
                  class="px-2.5 py-1 rounded-md transition-all font-medium"
                  :class="previewDocType === 'devis' ? 'bg-background shadow-xs text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'"
                >
                  Devis
                </button>
                <button
                  type="button"
                  @click="previewDocType = 'rapport'"
                  class="px-2.5 py-1 rounded-md transition-all font-medium"
                  :class="previewDocType === 'rapport' ? 'bg-background shadow-xs text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'"
                >
                  Rapport
                </button>
              </div>
            </div>

            <!-- Status Indicator -->
            <div class="flex items-center justify-between text-[11px] px-1 text-muted-foreground">
              <span class="flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: selectedColor }"></span>
                <span>Couleur active : <strong class="font-mono text-foreground uppercase">{{ selectedColor }}</strong></span>
              </span>
              <span 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium border"
                :class="hasAccessToCustomization ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-400' : 'bg-muted text-muted-foreground border-border'"
              >
                <span class="w-1.5 h-1.5 rounded-full" :class="hasAccessToCustomization ? 'bg-emerald-500' : 'bg-muted-foreground'"></span>
                {{ hasAccessToCustomization ? 'Sans badge ArtisanGestion' : 'Avec badge (Plan standard)' }}
              </span>
            </div>

            <!-- Miniature Document Card Preview -->
            <div class="bg-white text-slate-900 rounded-2xl shadow-xl border border-slate-200/80 p-5 md:p-6 text-[11px] leading-relaxed transition-all duration-300 font-sans select-none overflow-hidden">
              
              <!-- ══════════════════ FACTURE & DEVIS PREVIEW ══════════════════ -->
              <template v-if="previewDocType === 'facture' || previewDocType === 'devis'">
                <!-- Header with Logo and Company info -->
                <div class="flex justify-between items-start gap-4 pb-4 border-b border-slate-100">
                  <div class="space-y-2">
                    <!-- Artisan's Logo -->
                    <div class="flex items-center gap-2">
                      <div v-if="societe?.logo" class="max-w-[130px] max-h-[55px] p-1 bg-slate-50 border border-slate-100 rounded-lg flex items-center justify-center">
                        <img :src="societe.logo" alt="Logo entreprise" class="max-w-full max-h-[46px] object-contain" />
                      </div>
                      <div 
                        v-else 
                        class="h-10 px-3 rounded-lg flex items-center justify-center font-black text-sm tracking-tight text-white transition-colors duration-200 shadow-xs"
                        :style="{ backgroundColor: selectedColor }"
                      >
                        {{ (societe?.nom || 'ENTREPRISE').toUpperCase() }}
                      </div>
                    </div>

                    <div>
                      <div 
                        class="font-extrabold text-sm tracking-tight transition-colors duration-200"
                        :style="{ color: selectedColor }"
                      >
                        {{ societe?.nom || 'Votre Entreprise' }}
                      </div>
                      <div class="text-[10px] text-slate-500 mt-0.5">
                        {{ societe?.adresse || '19 Boulevard Jacques Copeau' }}, {{ societe?.code_postal || '95200' }} {{ societe?.ville || 'Sarcelles' }}
                      </div>
                      <div class="text-[9.5px] text-slate-500">
                        Tél : {{ societe?.telephone || '07 82 75 97 59' }} • {{ societe?.email || 'contact@artisan.fr' }}
                      </div>
                      <div class="text-[9px] text-slate-400">
                        SIRET : {{ societe?.siret || '891 234 567 00012' }}
                      </div>
                    </div>
                  </div>

                  <!-- Client box -->
                  <div class="bg-slate-50 border border-slate-200/70 rounded-lg p-2.5 text-right shrink-0 min-w-[135px]">
                    <div class="text-[8.5px] font-bold uppercase tracking-wider text-slate-400">
                      {{ previewDocType === 'facture' ? 'Facturé à' : 'Destinataire' }}
                    </div>
                    <div class="font-bold text-slate-800 text-[11px] mt-0.5">M. Dupont Jean</div>
                    <div class="text-[9px] text-slate-500">12 Rue des Lilas<br/>75011 Paris</div>
                    <div class="text-[8.5px] text-slate-400 mt-1">Tél : 06 12 34 56 78</div>
                  </div>
                </div>

                <!-- Document Title & Meta -->
                <div class="flex justify-between items-center py-3 border-b border-slate-100">
                  <div>
                    <div class="text-xs font-black text-slate-900 uppercase tracking-wide">
                      {{ previewDocType === 'facture' ? 'FACTURE N° F-2026-0042' : 'DEVIS N° D-2026-0018' }}
                    </div>
                    <div class="text-[9px] text-slate-500">
                      Objet : {{ previewDocType === 'facture' ? 'Rénovation tableau électrique' : 'Installation pompe à chaleur' }}
                    </div>
                  </div>
                  <div class="text-right">
                    <div class="text-[9px] font-bold uppercase tracking-wider text-slate-400">Date</div>
                    <div class="font-semibold text-slate-700 text-[10px]">17 Août 2026</div>
                  </div>
                </div>

                <!-- Table Preview -->
                <div class="my-3.5 rounded-lg overflow-hidden border border-slate-200">
                  <table class="w-full text-left text-[10px]">
                    <thead>
                      <tr 
                        class="text-white font-bold transition-colors duration-200"
                        :style="{ 
                          backgroundColor: selectedColor,
                          borderBottom: `2px solid ${darkenHex(selectedColor)}`
                        }"
                      >
                        <th class="p-2">Description</th>
                        <th class="p-2 text-right">Qté</th>
                        <th class="p-2 text-right">Prix U. HT</th>
                        <th class="p-2 text-right">TVA</th>
                        <th class="p-2 text-right">Total HT</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 bg-white">
                      <tr>
                        <td class="p-2 text-slate-700">Remplacement tableau électrique NF</td>
                        <td class="p-2 text-right text-slate-600">1</td>
                        <td class="p-2 text-right text-slate-600">850.00 €</td>
                        <td class="p-2 text-right text-slate-600">20%</td>
                        <td class="p-2 text-right font-medium text-slate-800">850.00 €</td>
                      </tr>
                      <tr class="bg-slate-50/50">
                        <td class="p-2 text-slate-700">Mise en conformité différentiels</td>
                        <td class="p-2 text-right text-slate-600">3</td>
                        <td class="p-2 text-right text-slate-600">120.00 €</td>
                        <td class="p-2 text-right text-slate-600">20%</td>
                        <td class="p-2 text-right font-medium text-slate-800">360.00 €</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- Conditions and Totals Section -->
                <div class="flex flex-col sm:flex-row justify-between items-start gap-4 my-3.5">
                  <!-- Info note with accent bar -->
                  <div class="relative overflow-hidden rounded-lg bg-slate-50 border border-slate-200 p-2.5 pl-3.5 text-[9.5px] flex-1">
                    <div 
                      class="absolute top-0 left-0 bottom-0 w-1 transition-colors duration-200"
                      :style="{ backgroundColor: selectedColor }"
                    />
                    <div class="font-bold text-slate-500 uppercase tracking-wider text-[8px] mb-0.5">Conditions & Informations</div>
                    <div v-if="previewDocType === 'facture'" class="text-slate-600">
                      Règlement sous 30 jours. Aucun escompte accordé.
                    </div>
                    <div v-else class="text-slate-600">
                      Devis valable 30 jours. Acompte de 30% à la commande.
                    </div>
                    <div class="text-slate-400 mt-1 font-mono text-[8px]">
                      IBAN : FR76 3000 4000 0001 2345 6789 012
                    </div>
                  </div>

                  <!-- Totals Box -->
                  <div 
                    class="w-full sm:w-48 rounded-lg overflow-hidden border transition-colors duration-200 shrink-0"
                    :style="{ borderColor: selectedColor }"
                  >
                    <div class="p-2 space-y-1 bg-white text-[10px]">
                      <div class="flex justify-between text-slate-600">
                        <span>Total HT</span>
                        <span class="font-medium">1 210.00 €</span>
                      </div>
                      <div class="flex justify-between text-slate-600">
                        <span>Total TVA</span>
                        <span class="font-medium">242.00 €</span>
                      </div>
                    </div>
                    <div 
                      class="flex justify-between items-center p-2 text-white font-bold text-[11px] transition-colors duration-200"
                      :style="{ backgroundColor: selectedColor }"
                    >
                      <span>Net à Payer</span>
                      <span>1 452.00 €</span>
                    </div>
                  </div>
                </div>
              </template>

              <!-- ══════════════════ RAPPORT D'INTERVENTION PREVIEW ══════════════════ -->
              <template v-else>
                <!-- Top Header: Logo on left, Company on right (matching Rapport template) -->
                <div 
                  class="flex justify-between items-start gap-4 pb-3 transition-colors duration-200"
                  :style="{ borderBottom: `3px solid ${selectedColor}` }"
                >
                  <!-- Logo -->
                  <div class="shrink-0 flex items-center">
                    <div v-if="societe?.logo" class="w-16 h-14 bg-slate-50 border border-slate-100 rounded-lg flex items-center justify-center p-1">
                      <img :src="societe.logo" alt="Logo" class="max-w-full max-h-full object-contain" />
                    </div>
                    <div 
                      v-else 
                      class="w-14 h-14 rounded-lg flex items-center justify-center text-white font-black text-xl shadow-xs transition-colors duration-200"
                      :style="{ backgroundColor: selectedColor }"
                    >
                      {{ (societe?.nom || 'E').charAt(0).toUpperCase() }}
                    </div>
                  </div>

                  <!-- Company Info -->
                  <div class="text-right">
                    <div 
                      class="font-black text-sm uppercase tracking-wide transition-colors duration-200"
                      :style="{ color: selectedColor }"
                    >
                      {{ societe?.nom || 'PINHAS BENTURA' }}
                    </div>
                    <div class="text-[9.5px] text-slate-500 mt-0.5">
                      {{ societe?.adresse || '19 BOULEVARD JACQUES COPEAU' }} {{ societe?.code_postal || '95200' }} {{ societe?.ville || 'SARCELLES' }}
                    </div>
                    <div class="text-[9px] text-slate-500">
                      Tél : {{ societe?.telephone || '0782759759' }} • {{ societe?.email || 'pinhasbent@gmail.com' }}
                    </div>
                    <div class="text-[8.5px] text-slate-400">
                      SIRET : {{ societe?.siret || '10557890000018' }}
                    </div>
                  </div>
                </div>

                <!-- Title Banner -->
                <div class="text-center my-3 py-2 bg-slate-100/90 rounded-lg border border-slate-200/50">
                  <h4 class="text-xs font-black text-slate-800 tracking-wider uppercase m-0">
                    RAPPORT D'INTERVENTION
                  </h4>
                </div>

                <!-- Client & Date Grid -->
                <div class="grid grid-cols-2 gap-4 pb-3 border-b border-slate-100 text-[10px]">
                  <div>
                    <span class="text-[8.5px] uppercase font-bold text-slate-400 block">Client</span>
                    <strong class="text-slate-800 text-[11px]">Pinhas Bentura</strong>
                    <div class="text-slate-500 text-[9px] mt-0.5">19 Boulevard Jacques Copeau, Sarcelles</div>
                  </div>
                  <div>
                    <span class="text-[8.5px] uppercase font-bold text-slate-400 block">Date d'intervention</span>
                    <strong class="text-slate-800 text-[11px]">17/08/2026</strong>
                  </div>
                </div>

                <!-- Rapport Content Section Title -->
                <div class="my-3">
                  <h5 
                    class="font-bold text-[10.5px] uppercase pb-1 mb-2 border-b border-slate-200 transition-colors duration-200"
                    :style="{ color: selectedColor }"
                  >
                    Rapport d'intervention
                  </h5>
                  <p class="text-[9.5px] text-slate-600 leading-relaxed">
                    Vérification complète de l'installation, remplacement des disjoncteurs divisionnaires et test de déclenchement différentiel 30mA conforme aux normes.
                  </p>
                </div>

                <!-- Photos Section Title -->
                <div class="my-2">
                  <h5 
                    class="font-bold text-[10.5px] uppercase pb-1 mb-2 border-b border-slate-200 transition-colors duration-200"
                    :style="{ color: selectedColor }"
                  >
                    Photos (2)
                  </h5>
                  <div class="grid grid-cols-2 gap-2">
                    <div class="h-12 rounded bg-slate-100 border border-slate-200 flex items-center justify-center text-[9px] text-slate-400">
                      Photo avant intervention
                    </div>
                    <div class="h-12 rounded bg-slate-100 border border-slate-200 flex items-center justify-center text-[9px] text-slate-400">
                      Photo après intervention
                    </div>
                  </div>
                </div>
              </template>

              <!-- Document Footer Preview -->
              <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-[8.5px] text-slate-400 mt-2">
                <!-- Colored separation line preview -->
                <div class="flex items-center gap-2">
                  <span 
                    class="w-2.5 h-0.5 rounded-full transition-colors duration-200"
                    :style="{ backgroundColor: selectedColor }"
                  />
                  <span>Page 1 / 1</span>
                </div>

                <!-- Branding or team plan badge -->
                <div v-if="!hasAccessToCustomization" class="flex items-center gap-1 text-[8.5px] text-slate-400">
                  <span>Généré via</span>
                  <span class="font-bold text-blue-600">ArtisanGestion</span>
                </div>
                <div v-else class="text-[8px] text-emerald-600 font-semibold flex items-center gap-1">
                  <Check class="w-2.5 h-2.5" />
                  Document sans mention externe
                </div>
              </div>
            </div>

            <!-- Logo upload hint if no logo -->
            <p v-if="!societe?.logo" class="text-[11px] text-muted-foreground text-center pt-1">
              💡 <em>Astuce : Vous pouvez ajouter le logo de votre entreprise dans l'onglet <strong>Mon Entreprise</strong> pour qu'il apparaisse automatiquement sur vos documents.</em>
            </p>
          </div>
        </div>
      </TabsContent>

      <!-- Placeholder content for remaining tabs -->
      <TabsContent v-for="tab in ['facturation', 'support']" :key="tab" :value="tab">
        <Card class="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle class="capitalize">{{ tab }}</CardTitle>
            <CardDescription>Cette section est en cours de développement.</CardDescription>
          </CardHeader>
          <CardContent class="py-12 flex flex-col items-center justify-center text-center">
            <div class="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
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
