<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Capacitor } from '@capacitor/core'
import { Browser } from '@capacitor/browser'
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
  User,
  X
} from 'lucide-vue-next'

import { App } from '@capacitor/app'

const router = useRouter()
const activeTab = ref('login')
const isLoading = ref(false)
const showPassword = ref(false)
const isNative = Capacitor.isNativePlatform()

// Mobile ChatGPT-style flow
const showAuthSheet = ref(false)
const sheetVisible = ref(false) // Controls CSS animation

// Swipe-to-dismiss gesture
const sheetRef = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const dragOffset = ref(0)
let touchStartY = 0
let touchStartTime = 0
let sheetHeight = 0

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

// Forgot password flow
const showForgotPassword = ref(false)
const forgotEmail = ref('')
const forgotLoading = ref(false)
const forgotMessage = ref('')
const forgotError = ref('')

let waitingSocket: WebSocket | null = null
let appStateListener: any = null

onMounted(async () => {
  if (localStorage.getItem('token')) {
    router.push('/app')
  }
  
  const handleVisibility = () => {
    // Si on a l'email et le mot de passe en mémoire, on essaye de se connecter
    // au cas où l'utilisateur aurait vérifié son email sur un autre appareil
    // pendant que l'app était en arrière-plan
    if (signupForm.value.email && signupForm.value.password) {
       loginForm.value.email = signupForm.value.email
       loginForm.value.password = signupForm.value.password
       handleLogin().catch(() => {})
    }
  }

  if (isNative) {
    appStateListener = await App.addListener('appStateChange', ({ isActive }) => {
      if (isActive) {
        handleVisibility()
      }
    })
  } else {
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        handleVisibility()
      }
    })
  }
})

function openAuthSheet() {
  showAuthSheet.value = true
  // Trigger animation on next frame
  nextTick(() => {
    requestAnimationFrame(() => {
      sheetVisible.value = true
    })
  })
}

function closeAuthSheet() {
  sheetVisible.value = false
  dragOffset.value = 0
  isDragging.value = false
  // Wait for animation to finish before removing from DOM
  setTimeout(() => {
    showAuthSheet.value = false
    errorMessage.value = ''
    successMessage.value = ''
  }, 350)
}

// ── Swipe-to-dismiss touch handlers ──
function onSheetTouchStart(e: TouchEvent) {
  // Only handle if touch starts on the handle area or sheet top
  const target = e.target as HTMLElement
  const sheet = sheetRef.value
  if (!sheet) return

  // Check if the touch point is in a scrollable area that has scroll content
  const scrollableParent = findScrollableParent(target, sheet)
  if (scrollableParent && scrollableParent.scrollTop > 0) {
    return // Let the scroll happen naturally
  }

  touchStartY = e.touches[0].clientY
  touchStartTime = Date.now()
  sheetHeight = sheet.offsetHeight
  isDragging.value = false
  dragOffset.value = 0
}

function onSheetTouchMove(e: TouchEvent) {
  if (touchStartY === 0) return

  const currentY = e.touches[0].clientY
  const delta = currentY - touchStartY

  // Only allow dragging downward
  if (delta < 0) {
    dragOffset.value = 0
    return
  }

  // Check if we're in a scrollable area that hasn't reached top
  const target = e.target as HTMLElement
  const sheet = sheetRef.value
  if (sheet) {
    const scrollableParent = findScrollableParent(target, sheet)
    if (scrollableParent && scrollableParent.scrollTop > 0) {
      return
    }
  }

  // Start dragging after a small threshold (5px) to avoid conflicts with taps
  if (delta > 5) {
    isDragging.value = true
    dragOffset.value = delta
    e.preventDefault() // Prevent scroll while dragging sheet
  }
}

function onSheetTouchEnd() {
  if (!isDragging.value) {
    touchStartY = 0
    return
  }

  const velocity = dragOffset.value / (Date.now() - touchStartTime)
  const threshold = sheetHeight * 0.3

  // Dismiss if dragged past 30% or with enough velocity
  if (dragOffset.value > threshold || velocity > 0.5) {
    closeAuthSheet()
  } else {
    // Snap back
    isDragging.value = false
    dragOffset.value = 0
  }

  touchStartY = 0
}

function findScrollableParent(el: HTMLElement, boundary: HTMLElement): HTMLElement | null {
  let current: HTMLElement | null = el
  while (current && current !== boundary) {
    if (current.scrollHeight > current.clientHeight) {
      const style = window.getComputedStyle(current)
      const overflowY = style.overflowY
      if (overflowY === 'auto' || overflowY === 'scroll') {
        return current
      }
    }
    current = current.parentElement
  }
  return null
}

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

    const data = await res.json()

    successMessage.value = "Votre compte a bien été créé ! Un email de vérification vous a été envoyé. Vérifiez votre boîte mail (et vos spams) pour activer votre compte."
    activeTab.value = 'login'
    loginForm.value.email = signupForm.value.email
    
    // Connect WebSocket to listen for verification from another device
    if (data.waiting_token) {
      let wsUrl = ''
      if (API_BASE_URL.startsWith('http')) {
        const url = new URL(API_BASE_URL)
        const wsProtocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
        wsUrl = `${wsProtocol}//${url.host}/api/ws?token=${data.waiting_token}`
      } else {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        wsUrl = `${wsProtocol}//${window.location.host}/api/ws?token=${data.waiting_token}`
      }
      
      if (waitingSocket) {
        waitingSocket.close()
      }
      
      waitingSocket = new WebSocket(wsUrl)
      waitingSocket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          if (msg.type === 'EMAIL_VERIFIED') {
             // Auto login since we still have the password in memory!
             loginForm.value.password = signupForm.value.password
             handleLogin()
             
             if (waitingSocket) {
               waitingSocket.close()
               waitingSocket = null
             }
          }
        } catch (e) {}
      }
    }
    
    loginForm.value.password = ''
  } catch (error: any) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}

function goBack() {
  if (isNative) return
  router.push('/')
}

async function handleForgotPassword() {
  forgotError.value = ''
  forgotMessage.value = ''

  if (!forgotEmail.value) {
    forgotError.value = 'Veuillez entrer votre adresse email.'
    return
  }

  forgotLoading.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: forgotEmail.value })
    })

    if (res.ok) {
      forgotMessage.value = 'Si un compte existe avec cet email, un lien de réinitialisation vous a été envoyé. Vérifiez votre boîte mail.'
    } else {
      forgotError.value = 'Une erreur est survenue. Veuillez réessayer.'
    }
  } catch {
    forgotError.value = 'Erreur réseau. Veuillez réessayer.'
  } finally {
    forgotLoading.value = false
  }
}

function openForgotPassword() {
  showForgotPassword.value = true
  forgotEmail.value = loginForm.value.email
  forgotError.value = ''
  forgotMessage.value = ''
}

function closeForgotPassword() {
  showForgotPassword.value = false
  forgotError.value = ''
  forgotMessage.value = ''
}

let authMessageListener: ((event: MessageEvent) => void) | null = null

async function handleGoogleAuth() {
  const isNative = Capacitor.isNativePlatform()
  const platform = isNative ? 'mobile' : 'web'
  // On transmet notre origine : le backend la valide puis s'en sert comme cible
  // du postMessage de retour, au lieu de diffuser le jeton à tout le monde.
  const loginUrl = `${API_BASE_URL}/api/auth/google/login?platform=${platform}`
    + `&origin=${encodeURIComponent(window.location.origin)}`

  if (isNative) {
    // Sur mobile natif, on utilise le plugin Browser pour ouvrir une modale In-App
    await Browser.open({ url: loginUrl, windowName: '_blank' })
    return
  }

  // Logique pour le web (popup)
  const width = 500
  const height = 600
  const left = window.screenX + (window.outerWidth - width) / 2
  const top = window.screenY + (window.outerHeight - height) / 2
  
  // Supprimer l'ancien écouteur si présent
  if (authMessageListener) {
    window.removeEventListener('message', authMessageListener)
  }

  authMessageListener = (event: MessageEvent) => {
    // Vérifier l'origine du message par sécurité
    let isAllowed = false
    try {
      const apiOrigin = new URL(API_BASE_URL).origin
      isAllowed =
        event.origin === window.location.origin ||
        event.origin === apiOrigin ||
        (import.meta.env.DEV && (
          event.origin.includes('localhost') ||
          event.origin.includes('127.0.0.1')
        ))
    } catch {
      isAllowed = false
    }

    if (!isAllowed) return

    if (event.data?.type === 'google-auth-success' && event.data?.token) {
      const token = event.data.token
      localStorage.setItem('token', token)
      router.push('/app')
      
      if (authMessageListener) {
        window.removeEventListener('message', authMessageListener)
        authMessageListener = null
      }
    }
  }

  window.addEventListener('message', authMessageListener)

  const popup = window.open(
    loginUrl,
    'google-login',
    `width=${width},height=${height},top=${top},left=${left},status=no,menubar=no,toolbar=no`
  )

  if (!popup) {
    // Si la popup est bloquée, on se rabat sur la redirection classique
    window.location.href = loginUrl
    return
  }
}

onUnmounted(() => {
  if (authMessageListener) {
    window.removeEventListener('message', authMessageListener)
  }
  if (waitingSocket) {
    waitingSocket.close()
    waitingSocket = null
  }
  if (appStateListener) {
    appStateListener.remove()
  }
  document.removeEventListener('visibilitychange', () => {})
})
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col lg:flex-row">

    <!-- ════════════════════════════════════════════════════════ -->
    <!-- MOBILE NATIVE: ChatGPT-style Welcome Screen            -->
    <!-- ════════════════════════════════════════════════════════ -->
    <template v-if="isNative">
      <!-- Welcome Screen -->
      <div class="auth-welcome-screen">
        <!-- Background gradient decoration -->
        <div class="auth-welcome-bg">
          <div class="auth-welcome-orb auth-welcome-orb--1" />
          <div class="auth-welcome-orb auth-welcome-orb--2" />
          <div class="auth-welcome-orb auth-welcome-orb--3" />
        </div>

        <!-- Centered Logo & Text -->
        <div class="auth-welcome-content">
          <div class="auth-welcome-logo-wrapper">
            <img src="/logo.svg" alt="ArtisanGestion" class="auth-welcome-logo" />
          </div>
          <h1 class="auth-welcome-title">Artisan<span class="text-primary">Gestion</span></h1>
          <p class="auth-welcome-subtitle">Votre assistant de gestion intelligent</p>
        </div>

        <!-- Bottom Action Area -->
        <div class="auth-welcome-actions">
          <div class="auth-welcome-actions-inner">
            <!-- Google Button -->
            <button 
              class="auth-welcome-btn auth-welcome-btn--google"
              @click="handleGoogleAuth"
            >
              <svg class="auth-welcome-btn-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Continuer avec Google
            </button>

            <!-- Se connecter ou s'inscrire -->
            <button 
              class="auth-welcome-btn auth-welcome-btn--primary"
              @click="openAuthSheet"
            >
              Se connecter ou s'inscrire
            </button>
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════ -->
      <!-- Bottom Sheet Overlay                                 -->
      <!-- ════════════════════════════════════════════════════ -->
      <Teleport to="body">
        <div v-if="showAuthSheet" class="auth-sheet-overlay" :class="{ 'auth-sheet-overlay--visible': sheetVisible }" @click.self="closeAuthSheet">
          <div 
            ref="sheetRef"
            class="auth-sheet" 
            :class="{ 'auth-sheet--visible': sheetVisible, 'auth-sheet--dragging': isDragging }"
            :style="isDragging ? { transform: `translateY(${dragOffset}px)` } : undefined"
            @touchstart.passive="onSheetTouchStart"
            @touchmove="onSheetTouchMove"
            @touchend.passive="onSheetTouchEnd"
          >
            <!-- Handle bar -->
            <div class="auth-sheet-handle">
              <div class="auth-sheet-handle-bar" />
            </div>

            <!-- Close button -->
            <button class="auth-sheet-close" @click="closeAuthSheet">
              <X class="w-5 h-5" />
            </button>

            <!-- Sheet Header -->
            <div class="auth-sheet-header">
              <div class="auth-sheet-logo-wrapper">
                <img src="/logo.svg" alt="ArtisanGestion" class="auth-sheet-logo" />
              </div>
              <h2 class="auth-sheet-title">Se connecter ou s'inscrire</h2>
              <p class="auth-sheet-description">
                Gérez vos devis, factures et rapports en toute simplicité
              </p>
            </div>

            <!-- Sheet Content -->
            <div class="auth-sheet-content">
              <!-- Messages -->
              <div v-if="errorMessage" class="auth-sheet-message auth-sheet-message--error">
                {{ errorMessage }}
              </div>
              <div v-if="successMessage" class="auth-sheet-message auth-sheet-message--success">
                {{ successMessage }}
              </div>

              <!-- Tabs -->
              <Tabs v-model="activeTab" class="w-full">
                <TabsList class="grid w-full grid-cols-2 mb-5">
                  <TabsTrigger value="login">Connexion</TabsTrigger>
                  <TabsTrigger value="signup">Inscription</TabsTrigger>
                </TabsList>

                <!-- Login Form -->
                <TabsContent value="login" class="space-y-4 mt-0">
                  <form @submit.prevent="handleLogin" class="space-y-4">
                    <div class="space-y-2">
                      <Label for="sheet-login-email">Adresse e-mail</Label>
                      <div class="relative">
                        <Mail class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input 
                          id="sheet-login-email" 
                          v-model="loginForm.email"
                          type="email" 
                          placeholder="vous@exemple.fr"
                          class="pl-10 auth-sheet-input"
                          required
                        />
                      </div>
                    </div>

                    <div class="space-y-2">
                      <div class="flex items-center justify-between">
                        <Label for="sheet-login-password">Mot de passe</Label>
                        <button type="button" class="text-xs text-primary hover:underline" @click="openForgotPassword">
                          Mot de passe oublié ?
                        </button>
                      </div>
                      <div class="relative">
                        <Lock class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input 
                          id="sheet-login-password" 
                          v-model="loginForm.password"
                          :type="showPassword ? 'text' : 'password'" 
                          placeholder="••••••••"
                          class="pl-10 pr-10 auth-sheet-input"
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

                    <button 
                      type="submit"
                      class="auth-sheet-submit"
                      :disabled="isLoading"
                    >
                      <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
                      {{ isLoading ? 'Connexion...' : 'Continuer' }}
                    </button>
                  </form>
                </TabsContent>

                <!-- Signup Form -->
                <TabsContent value="signup" class="space-y-4 mt-0">
                  <form @submit.prevent="handleSignup" class="space-y-4">
                    <div class="grid grid-cols-2 gap-3">
                      <div class="space-y-2">
                        <Label for="sheet-signup-firstname">Prénom</Label>
                        <div class="relative">
                          <User class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                          <Input 
                            id="sheet-signup-firstname" 
                            v-model="signupForm.firstName"
                            placeholder="Jean"
                            class="pl-10 auth-sheet-input"
                            required
                          />
                        </div>
                      </div>
                      <div class="space-y-2">
                        <Label for="sheet-signup-lastname">Nom</Label>
                        <div class="relative">
                          <User class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                          <Input 
                            id="sheet-signup-lastname" 
                            v-model="signupForm.lastName"
                            placeholder="Dupont"
                            class="pl-10 auth-sheet-input"
                            required
                          />
                        </div>
                      </div>
                    </div>

                    <div class="space-y-2">
                      <Label for="sheet-signup-email">Adresse e-mail</Label>
                      <div class="relative">
                        <Mail class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input 
                          id="sheet-signup-email" 
                          v-model="signupForm.email"
                          type="email" 
                          placeholder="vous@exemple.fr"
                          class="pl-10 auth-sheet-input"
                          required
                        />
                      </div>
                    </div>

                    <div class="space-y-2">
                      <Label for="sheet-signup-password">Mot de passe</Label>
                      <div class="relative">
                        <Lock class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input 
                          id="sheet-signup-password" 
                          v-model="signupForm.password"
                          :type="showPassword ? 'text' : 'password'" 
                          placeholder="••••••••"
                          class="pl-10 pr-10 auth-sheet-input"
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

                    <button 
                      type="submit"
                      class="auth-sheet-submit"
                      :disabled="isLoading"
                    >
                      <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
                      {{ isLoading ? 'Création du compte...' : 'Créer mon compte' }}
                    </button>
                  </form>

                  <p class="text-xs text-center text-muted-foreground">
                    En vous inscrivant, vous acceptez nos 
                    <router-link to="/legal/terms" class="text-primary hover:underline">Conditions d'utilisation</router-link> 
                    et notre 
                    <router-link to="/legal/privacy" class="text-primary hover:underline">Politique de confidentialité</router-link>
                  </p>
                </TabsContent>
              </Tabs>

              <!-- Divider -->
              <div class="auth-sheet-divider">
                <span class="auth-sheet-divider-line" />
                <span class="auth-sheet-divider-text">ou</span>
                <span class="auth-sheet-divider-line" />
              </div>

              <!-- Google Auth in sheet -->
              <button 
                class="auth-sheet-google-btn"
                @click="handleGoogleAuth"
              >
                <svg class="auth-welcome-btn-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                Continuer avec Google
              </button>
            </div>

            <!-- Forgot password overlay inside sheet -->
            <div v-if="showForgotPassword" class="auth-sheet-forgot">
              <button class="auth-sheet-forgot-back" @click="closeForgotPassword">
                <ArrowLeft :size="16" />
                Retour
              </button>
              <h3 class="auth-sheet-forgot-title">Mot de passe oublié</h3>
              <p class="auth-sheet-forgot-desc">Entrez votre adresse email. Si un compte existe, nous vous enverrons un lien de réinitialisation.</p>

              <div v-if="forgotError" class="auth-sheet-message auth-sheet-message--error">{{ forgotError }}</div>
              <div v-if="forgotMessage" class="auth-sheet-message auth-sheet-message--success">{{ forgotMessage }}</div>

              <form v-if="!forgotMessage" @submit.prevent="handleForgotPassword" class="auth-sheet-forgot-form">
                <div class="relative">
                  <Mail class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    v-model="forgotEmail"
                    type="email"
                    placeholder="vous@exemple.fr"
                    class="pl-10 auth-sheet-input"
                    required
                  />
                </div>
                <button type="submit" class="auth-sheet-submit" :disabled="forgotLoading">
                  <Loader2 v-if="forgotLoading" class="mr-2 h-4 w-4 animate-spin" />
                  {{ forgotLoading ? 'Envoi...' : 'Envoyer le lien' }}
                </button>
              </form>
              <button v-else class="auth-sheet-submit" @click="closeForgotPassword">Retour à la connexion</button>
            </div>
          </div>
        </div>
      </Teleport>
    </template>

    <!-- ════════════════════════════════════════════════════════ -->
    <!-- DESKTOP / WEB: Original Layout (unchanged)             -->
    <!-- ════════════════════════════════════════════════════════ -->
    <template v-else>
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
          <span class="text-2xl font-bold text-foreground">Artisan<span class="text-primary">Gestion</span></span>
        </div>

        <!-- Content -->
        <div class="space-y-6 max-w-md">
          <h2 class="text-4xl font-bold text-foreground leading-tight">
            Simplifiez la gestion de votre activité
          </h2>
          <p class="text-lg text-muted-foreground">
            Rejoignez plus de 500 artisans et PME qui gagnent du temps chaque jour avec ArtisanGestion.
          </p>
          
          <!-- Testimonial -->
          <div class="bg-card/50 backdrop-blur-sm rounded-2xl p-6 border border-border/50">
            <p class="text-foreground mb-4 italic">
              "ArtisanGestion a transformé notre façon de travailler. Nous gagnons 10 heures par semaine sur l'administratif."
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
          © {{ new Date().getFullYear() }} ArtisanGestion. Tous droits réservés.
        </div>
      </div>

      <!-- Right side - Auth forms -->
      <div class="flex-1 flex flex-col justify-center items-center p-6 lg:p-12">
        <!-- Mobile header -->
        <div class="lg:hidden flex items-center justify-between w-full mb-8 pt-safe mt-4">
          <div class="flex items-center gap-2">
            <img src="/logo.svg" alt="Logo" class="w-9 h-9" />
            <span class="text-xl font-bold">Artisan<span class="text-primary">Gestion</span></span>
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
                      <button type="button" class="text-xs text-primary hover:underline bg-transparent border-none cursor-pointer" @click="openForgotPassword">
                        Mot de passe oublié ?
                      </button>
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

            <!-- Forgot password form (Desktop) -->
            <div v-if="showForgotPassword" class="forgot-password-overlay">
              <div class="forgot-password-card">
                <button class="forgot-back-btn" @click="closeForgotPassword">
                  <ArrowLeft :size="16" />
                  Retour
                </button>
                <h3 class="forgot-title">Mot de passe oublié</h3>
                <p class="forgot-desc">Entrez votre adresse email et nous vous enverrons un lien pour réinitialiser votre mot de passe.</p>

                <div v-if="forgotError" class="p-3 bg-red-500/10 border border-red-500/50 rounded-xl text-red-500 text-sm text-center mb-4">
                  {{ forgotError }}
                </div>
                <div v-if="forgotMessage" class="p-3 bg-green-500/10 border border-green-500/50 rounded-xl text-green-500 text-sm text-center mb-4">
                  {{ forgotMessage }}
                </div>

                <form v-if="!forgotMessage" @submit.prevent="handleForgotPassword" class="space-y-4">
                  <div class="space-y-2">
                    <Label for="forgot-email">Email</Label>
                    <div class="relative">
                      <Mail class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="forgot-email"
                        v-model="forgotEmail"
                        type="email"
                        placeholder="vous@exemple.fr"
                        class="pl-10"
                        required
                      />
                    </div>
                  </div>
                  <Button type="submit" class="w-full rounded-xl py-6 font-semibold" :disabled="forgotLoading">
                    <Loader2 v-if="forgotLoading" class="mr-2 h-4 w-4 animate-spin" />
                    {{ forgotLoading ? 'Envoi en cours...' : 'Envoyer le lien de réinitialisation' }}
                  </Button>
                </form>
                <Button v-else class="w-full rounded-xl py-6 font-semibold" @click="closeForgotPassword">
                  Retour à la connexion
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* ══════════════════════════════════════════════════════════════
   WELCOME SCREEN (ChatGPT-inspired)
   ══════════════════════════════════════════════════════════════ */
.auth-welcome-screen {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--background);
  z-index: 10;
}

.auth-welcome-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.auth-welcome-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: orbFloat 8s ease-in-out infinite;
}

.auth-welcome-orb--1 {
  width: 300px;
  height: 300px;
  background: #2563EB;
  top: -60px;
  right: -40px;
  animation-delay: 0s;
}

.auth-welcome-orb--2 {
  width: 250px;
  height: 250px;
  background: #3B82F6;
  bottom: 20%;
  left: -60px;
  animation-delay: 2s;
}

.auth-welcome-orb--3 {
  width: 200px;
  height: 200px;
  background: #1D4ED8;
  top: 40%;
  right: 10%;
  opacity: 0.2;
  animation-delay: 4s;
}

@keyframes orbFloat {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

.auth-welcome-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  z-index: 1;
  animation: fadeSlideUp 0.8s ease-out both;
  animation-delay: 0.2s;
  padding: 0 32px;
}

.auth-welcome-logo-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(59, 130, 246, 0.08));
  backdrop-filter: blur(12px);
  box-shadow: 
    0 0 0 1px rgba(37, 99, 235, 0.15),
    0 8px 32px rgba(37, 99, 235, 0.12);
}

.auth-welcome-logo {
  width: 52px;
  height: 52px;
  filter: drop-shadow(0 4px 12px rgba(37, 99, 235, 0.3));
}

.auth-welcome-title {
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--foreground);
  line-height: 1;
}

.auth-welcome-subtitle {
  font-size: 16px;
  color: var(--muted-foreground);
  text-align: center;
  max-width: 260px;
  line-height: 1.5;
}

/* ── Bottom Action Area ── */
.auth-welcome-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 2;
  padding: 24px 20px;
  padding-bottom: calc(24px + env(safe-area-inset-bottom, 0px));
  animation: fadeSlideUp 0.6s ease-out both;
  animation-delay: 0.6s;
}

.auth-welcome-actions-inner {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
  margin: 0 auto;
}

.auth-welcome-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 16px 24px;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  -webkit-tap-highlight-color: transparent;
}

.auth-welcome-btn:active {
  transform: scale(0.98);
}

.auth-welcome-btn-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.auth-welcome-btn--google {
  background: var(--card);
  color: var(--foreground);
  border: 1.5px solid var(--border);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.auth-welcome-btn--google:active {
  background: var(--muted);
}

.auth-welcome-btn--primary {
  background: #2563EB;
  color: #FFFFFF;
  box-shadow: 
    0 2px 8px rgba(37, 99, 235, 0.3),
    0 0 0 1px rgba(37, 99, 235, 0.1);
}

.auth-welcome-btn--primary:active {
  background: #1D4ED8;
}

/* ══════════════════════════════════════════════════════════════
   BOTTOM SHEET
   ══════════════════════════════════════════════════════════════ */
.auth-sheet-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0);
  transition: background 0.35s ease;
  display: flex;
  align-items: flex-end;
}

.auth-sheet-overlay--visible {
  background: rgba(0, 0, 0, 0.5);
}

.auth-sheet {
  position: relative;
  width: 100%;
  max-height: 92vh;
  overflow-y: auto;
  overscroll-behavior: contain;
  background: var(--card);
  border-radius: 24px 24px 0 0;
  padding: 12px 24px 24px;
  padding-bottom: calc(24px + env(safe-area-inset-bottom, 0px));
  transform: translateY(100%);
  transition: transform 0.35s cubic-bezier(0.32, 0.72, 0, 1);
  box-shadow: 
    0 -4px 32px rgba(0, 0, 0, 0.12),
    0 -1px 6px rgba(0, 0, 0, 0.06);
}

.auth-sheet--visible {
  transform: translateY(0);
}

.auth-sheet--dragging {
  transition: none !important;
  will-change: transform;
}

.auth-sheet-handle {
  display: flex;
  justify-content: center;
  padding: 8px 0 16px;
}

.auth-sheet-handle-bar {
  width: 36px;
  height: 5px;
  border-radius: 3px;
  background: var(--border);
}

.auth-sheet-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--muted);
  color: var(--muted-foreground);
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
  -webkit-tap-highlight-color: transparent;
}

.auth-sheet-close:active {
  background: var(--border);
  transform: scale(0.92);
}

.auth-sheet-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
}

.auth-sheet-logo-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(59, 130, 246, 0.06));
  margin-bottom: 4px;
}

.auth-sheet-logo {
  width: 32px;
  height: 32px;
}

.auth-sheet-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--foreground);
  letter-spacing: -0.01em;
}

.auth-sheet-description {
  font-size: 14px;
  color: var(--muted-foreground);
  text-align: center;
  line-height: 1.5;
  max-width: 280px;
}

.auth-sheet-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.auth-sheet-input {
  border-radius: 12px !important;
  padding-top: 12px !important;
  padding-bottom: 12px !important;
  height: 48px !important;
  font-size: 16px !important;
}

.auth-sheet-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 14px 24px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  background: #2563EB;
  color: #FFFFFF;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: transparent;
  box-shadow: 
    0 2px 8px rgba(37, 99, 235, 0.25);
}

.auth-sheet-submit:active {
  background: #1D4ED8;
  transform: scale(0.98);
}

.auth-sheet-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-sheet-divider {
  display: flex;
  align-items: center;
  gap: 12px;
}

.auth-sheet-divider-line {
  flex: 1;
  height: 1px;
  background: var(--border);
}

.auth-sheet-divider-text {
  font-size: 13px;
  color: var(--muted-foreground);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

.auth-sheet-google-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px 24px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  background: var(--background);
  color: var(--foreground);
  border: 1.5px solid var(--border);
  cursor: pointer;
  transition: all 0.15s ease;
  -webkit-tap-highlight-color: transparent;
}

.auth-sheet-google-btn:active {
  background: var(--muted);
  transform: scale(0.98);
}

.auth-sheet-message {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  text-align: center;
}

.auth-sheet-message--error {
  background: rgba(220, 38, 38, 0.08);
  border: 1px solid rgba(220, 38, 38, 0.3);
  color: #DC2626;
}

.auth-sheet-message--success {
  background: rgba(22, 163, 74, 0.08);
  border: 1px solid rgba(22, 163, 74, 0.3);
  color: #16A34A;
}

/* Animation from index.css referenced here */
@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ══════════════════════════════════════════════════════════════
   FORGOT PASSWORD — Mobile Sheet Overlay
   ══════════════════════════════════════════════════════════════ */
.auth-sheet-forgot {
  position: absolute;
  inset: 0;
  background: var(--background);
  padding: 24px;
  display: flex;
  flex-direction: column;
  animation: fadeSlideUp 0.25s ease-out;
  z-index: 10;
  border-radius: 20px 20px 0 0;
}

.auth-sheet-forgot-back {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: var(--primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
  margin-bottom: 24px;
  -webkit-tap-highlight-color: transparent;
}

.auth-sheet-forgot-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--foreground);
  margin: 0 0 8px 0;
}

.auth-sheet-forgot-desc {
  font-size: 14px;
  color: var(--muted-foreground);
  line-height: 1.5;
  margin: 0 0 24px 0;
}

.auth-sheet-forgot-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ══════════════════════════════════════════════════════════════
   FORGOT PASSWORD — Desktop Overlay
   ══════════════════════════════════════════════════════════════ */
.forgot-password-overlay {
  position: absolute;
  inset: 0;
  background: var(--card);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: inherit;
  animation: fadeSlideUp 0.25s ease-out;
}

.forgot-password-card {
  width: 100%;
  padding: 8px;
}

.forgot-back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: var(--primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
  margin-bottom: 20px;
  transition: opacity 0.15s;
}

.forgot-back-btn:hover {
  opacity: 0.8;
}

.forgot-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--foreground);
  margin: 0 0 8px 0;
}

.forgot-desc {
  font-size: 14px;
  color: var(--muted-foreground);
  line-height: 1.5;
  margin: 0 0 24px 0;
}
</style>
