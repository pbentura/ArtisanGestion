<script setup lang="ts">
import { useRouter } from 'vue-router'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()

function navigateToAuth() {
  router.push('/auth')
}
</script>

<template>
  <div class="min-h-screen bg-background text-foreground font-sans">
    <!-- Navigation (only show on landing page) -->
    <nav 
      v-if="$route.path === '/'" 
      class="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border"
    >
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-primary flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <span class="text-xl font-bold text-foreground">Ventura</span>
          </div>

          <!-- Nav Links -->
          <div class="hidden md:flex items-center gap-8">
            <a href="#features" class="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Fonctionnalités</a>
            <a href="#demo" class="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Démo</a>
            <a href="#pricing" class="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Tarifs</a>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-4">
            <ThemeToggle />
            <button 
              @click="navigateToAuth"
              class="hidden sm:inline-flex px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors"
            >
              Connexion
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main>
      <RouterView />
    </main>
  </div>
</template>
