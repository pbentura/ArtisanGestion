<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import GoogleAuthButton from '@/components/auth/GoogleAuthButton.vue'
import { API_BASE_URL } from '@/lib/api'
import { 
  ArrowLeft,
  Loader2,
  Eye,
  EyeOff,
  Mail,
  Lock,
  User
} from 'lucide-vue-next'

const router = useRouter()
const activeTab = ref('login')
const isLoading = ref(false)
const showPassword = ref(false)

// Form data
const loginForm = ref({
  email: '',
  password: ''
})

const signupForm = ref({
  firstName: '',
  lastName: '',
  email: '',
  password: ''
})

const errorMessage = ref('')
const successMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''
  successMessage.value = ''
  isLoading.value = true
  
  try {
    const formData = new URLSearchParams()
    formData.append('username', loginForm.value.email)
    formData.append('password', loginForm.value.password)

    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })
    
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(errorData.detail || "Erreur de connexion")
    }
    
    const data = await res.json()
    localStorage.setItem('token', data.access_token)
    router.push('/app')
  } catch (error: any) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}

async function handleSignup() {
  errorMessage.value = ''
  successMessage.value = ''
  isLoading.value = true

  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nom: signupForm.value.lastName,
        prenom: signupForm.value.firstName,
        email: signupForm.value.email,
        mdp: signupForm.value.password
      })
    })

    if (!res.ok) {
      const errorData = await res.json()
      // Fallback for different FastAPI ValidationError structures
      const errorText = Array.isArray(errorData.detail) 
        ? errorData.detail[0]?.msg 
        : (errorData.detail || "Erreur lors de l'inscription")
      throw new Error(errorText)
    }

    successMessage.value = "Votre compte a bien été créé ! Vous pouvez maintenant vous connecter."
    activeTab.value = 'login'
    loginForm.value.email = signupForm.value.email
    loginForm.value.password = ''
  } catch (error: any) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}

function goBack() {
  router.push('/')
}

function handleGoogleAuth() {
  window.location.href = `${API_BASE_URL}/api/auth/google/login`
}
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col lg:flex-row">
    <!-- Left side - Branding (hidden on mobile) -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary/10 via-primary/5 to-background flex-col justify-between p-12 relative overflow-hidden">
      <!-- Background decoration -->
      <div class="absolute inset-0 -z-10">
        <div class="absolute top-0 left-0 w-[500px] h-[500px] bg-primary/10 rounded-full blur-3xl" />
        <div class="absolute bottom-0 right-0 w-[400px] h-[400px] bg-primary/5 rounded-full blur-3xl" />
      </div>

      <!-- Header -->
      <div class="flex items-center gap-3">
        <img src="/logo.svg" alt="Logo" class="w-12 h-12" />
        <span class="text-2xl font-bold text-foreground">Ventura</span>
      </div>

      <!-- Content -->
      <div class="space-y-6 max-w-md">
        <h2 class="text-4xl font-bold text-foreground leading-tight">
          Simplifiez la gestion de votre activité
        </h2>
        <p class="text-lg text-muted-foreground">
          Rejoignez plus de 500 artisans et PME qui gagnent du temps chaque jour avec Ventura.
        </p>
        
        <!-- Testimonial -->
        <div class="bg-card/50 backdrop-blur-sm rounded-2xl p-6 border border-border/50">
          <p class="text-foreground mb-4 italic">
            "Ventura a transformé notre façon de travailler. Nous gagnons 10 heures par semaine sur l'administratif."
          </p>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600" />
            <div>
              <p class="text-sm font-semibold text-foreground">Marc Dupont</p>
              <p class="text-xs text-muted-foreground">Dupont Electricité</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-sm text-muted-foreground">
        © {{ new Date().getFullYear() }} Ventura. Tous droits réservés.
      </div>
    </div>

    <!-- Right side - Auth forms -->
    <div class="flex-1 flex flex-col justify-center items-center p-6 lg:p-12">
      <!-- Mobile header -->
      <div class="lg:hidden flex items-center justify-between w-full mb-8 pt-safe mt-4">
        <div class="flex items-center gap-2">
          <img src="/logo.svg" alt="Logo" class="w-9 h-9" />
          <span class="text-xl font-bold">Ventura</span>
        </div>
        <Button variant="ghost" size="sm" @click="goBack">
          <ArrowLeft class="h-4 w-4 mr-1" />
          Retour
        </Button>
      </div>

      <!-- Desktop back button -->
      <div class="hidden lg:flex absolute top-8 right-8">
        <Button variant="ghost" @click="goBack">
          <ArrowLeft class="h-4 w-4 mr-1" />
          Retour à l'accueil
        </Button>
      </div>

      <!-- Auth Card -->
      <Card class="w-full max-w-md border-border/50 shadow-xl">
        <CardHeader class="space-y-1 text-center pb-4">
          <CardTitle class="text-2xl font-bold">
            {{ activeTab === 'login' ? 'Connexion' : 'Créer un compte' }}
          </CardTitle>
          <CardDescription>
            {{ activeTab === 'login' 
              ? 'Connectez-vous pour accéder à votre espace' 
              : 'Inscrivez-vous gratuitement en 30 secondes' 
            }}
          </CardDescription>
        </CardHeader>

        <CardContent class="space-y-4">
          <!-- Google Auth Button -->
          <GoogleAuthButton @click="handleGoogleAuth" />

          <!-- Divider -->
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <span class="w-full border-t border-border" />
            </div>
            <div class="relative flex justify-center text-xs uppercase">
              <span class="bg-card px-2 text-muted-foreground">
                Ou continuer avec email
              </span>
            </div>
          </div>

          <!-- Messages -->
          <div v-if="errorMessage" class="p-3 bg-red-500/10 border border-red-500/50 rounded-xl text-red-500 text-sm text-center">
            {{ errorMessage }}
          </div>
          
          <div v-if="successMessage" class="p-3 bg-green-500/10 border border-green-500/50 rounded-xl text-green-500 text-sm text-center">
            {{ successMessage }}
          </div>

          <!-- Tabs -->
          <Tabs v-model="activeTab" class="w-full">
            <TabsList class="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="login">Connexion</TabsTrigger>
              <TabsTrigger value="signup">Inscription</TabsTrigger>
            </TabsList>

            <!-- Login Form -->
            <TabsContent value="login" class="space-y-4">
              <form @submit.prevent="handleLogin" class="space-y-4">
                <div class="space-y-2">
                  <Label for="login-email">Email</Label>
                  <div class="relative">
                    <Mail class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="login-email" 
                      v-model="loginForm.email"
                      type="email" 
                      placeholder="vous@exemple.fr"
                      class="pl-10"
                      required
                    />
                  </div>
                </div>

                <div class="space-y-2">
                  <div class="flex items-center justify-between">
                    <Label for="login-password">Mot de passe</Label>
                    <a href="#" class="text-xs text-primary hover:underline">
                      Mot de passe oublié ?
                    </a>
                  </div>
                  <div class="relative">
                    <Lock class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="login-password" 
                      v-model="loginForm.password"
                      :type="showPassword ? 'text' : 'password'" 
                      placeholder="••••••••"
                      class="pl-10 pr-10"
                      required
                    />
                    <button 
                      type="button"
                      @click="showPassword = !showPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      <Eye v-if="!showPassword" class="h-4 w-4" />
                      <EyeOff v-else class="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  class="w-full rounded-xl py-6 font-semibold"
                  :disabled="isLoading"
                >
                  <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
                  {{ isLoading ? 'Connexion...' : 'Se connecter' }}
                </Button>
              </form>
            </TabsContent>

            <!-- Signup Form -->
            <TabsContent value="signup" class="space-y-4">
              <form @submit.prevent="handleSignup" class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                  <div class="space-y-2">
                    <Label for="signup-firstname">Prénom</Label>
                    <div class="relative">
                      <User class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input 
                        id="signup-firstname" 
                        v-model="signupForm.firstName"
                        placeholder="Jean"
                        class="pl-10"
                        required
                      />
                    </div>
                  </div>
                  <div class="space-y-2">
                    <Label for="signup-lastname">Nom</Label>
                    <div class="relative">
                      <User class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input 
                        id="signup-lastname" 
                        v-model="signupForm.lastName"
                        placeholder="Dupont"
                        class="pl-10"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div class="space-y-2">
                  <Label for="signup-email">Email</Label>
                  <div class="relative">
                    <Mail class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="signup-email" 
                      v-model="signupForm.email"
                      type="email" 
                      placeholder="vous@exemple.fr"
                      class="pl-10"
                      required
                    />
                  </div>
                </div>

                <div class="space-y-2">
                  <Label for="signup-password">Mot de passe</Label>
                  <div class="relative">
                    <Lock class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="signup-password" 
                      v-model="signupForm.password"
                      :type="showPassword ? 'text' : 'password'" 
                      placeholder="••••••••"
                      class="pl-10 pr-10"
                      required
                    />
                    <button 
                      type="button"
                      @click="showPassword = !showPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      <Eye v-if="!showPassword" class="h-4 w-4" />
                      <EyeOff v-else class="h-4 w-4" />
                    </button>
                  </div>
                  <p class="text-xs text-muted-foreground">
                    Au moins 8 caractères, avec une majuscule et un chiffre
                  </p>
                </div>

                <Button 
                  type="submit" 
                  class="w-full rounded-xl py-6 font-semibold"
                  :disabled="isLoading"
                >
                  <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
                  {{ isLoading ? 'Création du compte...' : 'Créer mon compte' }}
                </Button>
              </form>

              <p class="text-xs text-center text-muted-foreground">
                En vous inscrivant, vous acceptez nos 
                <router-link to="/legal/terms" class="text-primary hover:underline">Conditions d'utilisation</router-link> 
                et notre 
                <router-link to="/legal/privacy" class="text-primary hover:underline">Politique de confidentialité</router-link>
              </p>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
