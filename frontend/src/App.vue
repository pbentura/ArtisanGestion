<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { App as CapApp } from '@capacitor/app'
import { Browser } from '@capacitor/browser'
import { Menu, X } from 'lucide-vue-next'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const isMenuOpen = ref(false)

function navigateToAuth() {
  isMenuOpen.value = false
  router.push('/auth')
}

function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value
}

onMounted(() => {
  // Écouter les liens personnalisés (ex: com.pinhasbentura.ventura://auth?token=...)
  CapApp.addListener('appUrlOpen', data => {
    console.log('App opened with URL:', data.url)
    try {
      const url = new URL(data.url)
      // On accepte à la fois le format ventura://auth et com.pinhasbentura.ventura://auth
      if (url.host === 'auth') {
        const token = url.searchParams.get('token')
        if (token) {
          localStorage.setItem('token', token)
          // Fermer le navigateur In-App s'il est ouvert
          Browser.close()
          // Rediriger vers l'application
          router.push('/app')
        }
      }
    } catch (e) {
      console.error('Erreur lors du traitement de l\'URL:', e)
    }
  })
})
</script>

<template>
  <div class="min-h-screen bg-background text-foreground font-sans">
    <!-- Navigation (only show on landing page) -->
    <nav 
      v-if="$route.path === '/'" 
      class="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border pt-safe"
    >
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center gap-3">
            <img src="/logo.svg" alt="Logo" class="w-9 h-9" />
            <span class="text-xl font-bold text-foreground">Ventura</span>
          </div>

          <!-- Nav Links -->
          <div class="hidden md:flex items-center gap-8">
            <a href="#features" class="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Fonctionnalités</a>
            <a href="#demo" class="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Démo</a>
            <a href="#pricing" class="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Tarifs</a>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 sm:gap-4">
            <ThemeToggle />
            <button 
              @click="navigateToAuth"
              class="hidden sm:inline-flex px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors"
            >
              Connexion
            </button>
            
            <!-- Mobile Menu Button -->
            <button 
              @click="toggleMenu"
              class="md:hidden p-2 text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Menu"
            >
              <Menu v-if="!isMenuOpen" class="w-6 h-6" />
              <X v-else class="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile Menu Overlay -->
      <div 
        v-if="isMenuOpen"
        class="fixed inset-0 z-40 bg-background/95 backdrop-blur-md md:hidden pt-20 px-6 pb-safe overflow-y-auto"
      >
        <div class="flex flex-col gap-6 py-8">
          <a href="#features" @click="isMenuOpen = false" class="text-lg font-medium text-foreground border-b border-border pb-4">Fonctionnalités</a>
          <a href="#demo" @click="isMenuOpen = false" class="text-lg font-medium text-foreground border-b border-border pb-4">Démo</a>
          <a href="#pricing" @click="isMenuOpen = false" class="text-lg font-medium text-foreground border-b border-border pb-4">Tarifs</a>
          <button 
            @click="navigateToAuth"
            class="w-full px-4 py-3 bg-primary text-primary-foreground rounded-xl text-base font-semibold hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20 mt-4"
          >
            Connexion
          </button>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main>
      <RouterView />
    </main>
  </div>
</template>
