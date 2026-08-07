<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Loader2, Building2, CheckCircle2, AlertTriangle, UserPlus, Eye, EyeOff } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const token = route.params.token as string
const isLoading = ref(true)
const isSubmitting = ref(false)
const invitation = ref<any>(null)
const error = ref('')
const success = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const form = ref({
  nom: '',
  prenom: '',
  email: '',
  mdp: '',
  confirmMdp: '',
})

import { API_BASE_URL } from '@/lib/api'

async function loadInvitation() {
  isLoading.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/api/collaborateurs/invitation/${token}`)
    if (!res.ok) {
      const data = await res.json()
      error.value = data.detail || 'Invitation invalide ou expirée.'
      return
    }
    invitation.value = await res.json()
    if (invitation.value.email) {
      form.value.email = invitation.value.email
    }
  } catch (e) {
    error.value = 'Impossible de vérifier l\'invitation.'
  } finally {
    isLoading.value = false
  }
}

async function handleSubmit() {
  error.value = ''

  if (!form.value.nom || !form.value.prenom || !form.value.email || !form.value.mdp) {
    error.value = 'Veuillez remplir tous les champs.'
    return
  }
  if (form.value.mdp !== form.value.confirmMdp) {
    error.value = 'Les mots de passe ne correspondent pas.'
    return
  }
  if (form.value.mdp.length < 6) {
    error.value = 'Le mot de passe doit contenir au moins 6 caractères.'
    return
  }

  isSubmitting.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/register-collaborateur`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token: token,
        nom: form.value.nom,
        prenom: form.value.prenom,
        email: form.value.email,
        mdp: form.value.mdp,
      }),
    })

    if (!res.ok) {
      const data = await res.json()
      error.value = data.detail || 'Erreur lors de l\'inscription.'
      return
    }

    const data = await res.json()
    localStorage.setItem('token', data.access_token)
    success.value = true

    setTimeout(() => {
      router.push('/app/dashboard')
    }, 2000)
  } catch (e) {
    error.value = 'Erreur réseau. Veuillez réessayer.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(loadInvitation)
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-white dark:from-slate-950 dark:via-blue-950/20 dark:to-slate-900 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Loading -->
      <div v-if="isLoading" class="text-center py-12">
        <Loader2 class="w-10 h-10 animate-spin text-primary mx-auto mb-4" />
        <p class="text-muted-foreground">Vérification de l'invitation...</p>
      </div>

      <!-- Erreur (lien invalide) -->
      <div v-else-if="error && !invitation" class="text-center py-12 bg-card border border-border rounded-2xl p-8 shadow-lg">
        <AlertTriangle class="w-16 h-16 text-destructive mx-auto mb-4" />
        <h2 class="text-xl font-bold text-foreground mb-2">Invitation invalide</h2>
        <p class="text-muted-foreground mb-6">{{ error }}</p>
        <button @click="router.push('/auth')" class="btn-primary">Se connecter</button>
      </div>

      <!-- Succès -->
      <div v-else-if="success" class="text-center py-12 bg-card border border-border rounded-2xl p-8 shadow-lg">
        <div class="w-20 h-20 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-6">
          <CheckCircle2 class="w-10 h-10 text-green-600" />
        </div>
        <h2 class="text-xl font-bold text-foreground mb-2">Bienvenue dans l'équipe ! 🎉</h2>
        <p class="text-muted-foreground">Redirection vers votre espace de travail...</p>
      </div>

      <!-- Formulaire d'inscription -->
      <div v-else-if="invitation" class="bg-card border border-border rounded-2xl shadow-lg overflow-hidden">
        <!-- Header avec info entreprise -->
        <div class="bg-primary/5 border-b border-border p-6 text-center">
          <div class="w-16 h-16 mx-auto bg-primary/15 rounded-2xl flex items-center justify-center mb-4">
            <Building2 class="w-8 h-8 text-primary" />
          </div>
          <h2 class="text-xl font-bold text-foreground mb-1">Rejoindre {{ invitation.societe_nom }}</h2>
          <p class="text-sm text-muted-foreground">
            {{ invitation.invited_by_name }} vous invite à rejoindre son équipe sur ArtisanGestion.
          </p>
        </div>

        <!-- Formulaire -->
        <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
          <div v-if="error" class="p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-sm text-destructive">
            {{ error }}
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-foreground mb-1">Prénom</label>
              <input v-model="form.prenom" type="text" placeholder="Jean" class="w-full px-3 py-2.5 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-foreground mb-1">Nom</label>
              <input v-model="form.nom" type="text" placeholder="Dupont" class="w-full px-3 py-2.5 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none text-sm" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-foreground mb-1">Email</label>
            <input v-model="form.email" type="email" placeholder="jean@email.com" :disabled="!!invitation.email" class="w-full px-3 py-2.5 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none text-sm disabled:opacity-50" />
          </div>

          <div>
            <label class="block text-sm font-medium text-foreground mb-1">Mot de passe</label>
            <div class="relative">
              <input v-model="form.mdp" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" class="w-full px-3 py-2.5 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none text-sm pr-10" />
              <button type="button" @click="showPassword = !showPassword" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors p-1">
                <EyeOff v-if="showPassword" class="w-4 h-4" />
                <Eye v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-foreground mb-1">Confirmer le mot de passe</label>
            <div class="relative">
              <input v-model="form.confirmMdp" :type="showConfirmPassword ? 'text' : 'password'" placeholder="••••••••" class="w-full px-3 py-2.5 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none text-sm pr-10" />
              <button type="button" @click="showConfirmPassword = !showConfirmPassword" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors p-1">
                <EyeOff v-if="showConfirmPassword" class="w-4 h-4" />
                <Eye v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <button type="submit" :disabled="isSubmitting" class="w-full btn-primary flex items-center justify-center gap-2 py-3">
            <Loader2 v-if="isSubmitting" class="w-5 h-5 animate-spin" />
            <UserPlus v-else class="w-5 h-5" />
            Créer mon compte et rejoindre l'équipe
          </button>

          <p class="text-xs text-muted-foreground text-center">
            Vous avez déjà un compte ? <router-link to="/auth" class="text-primary font-medium hover:underline">Se connecter</router-link>
          </p>
        </form>
      </div>
    </div>
  </div>
</template>
