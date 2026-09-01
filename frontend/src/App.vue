<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { App as CapApp } from '@capacitor/app'
import { Browser } from '@capacitor/browser'
import LandingNavbar from '@/components/landing/LandingNavbar.vue'
import SubscriptionModal from '@/components/SubscriptionModal.vue'
import SocieteRequiredModal from '@/components/SocieteRequiredModal.vue'
import ConsentBanner from '@/components/ConsentBanner.vue'

const router = useRouter()

onMounted(() => {
  // Écouter les liens personnalisés (ex: com.artisangestion.app://auth?token=...)
  CapApp.addListener('appUrlOpen', data => {
    console.log('App opened with URL:', data.url)
    try {
      const url = new URL(data.url)
      // On accepte à la fois le format artisangestion://auth et com.artisangestion.app://auth
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
    <LandingNavbar v-if="$route.path === '/'" />

    <!-- Main Content -->
    <main>
      <RouterView />
    </main>

    <!-- Global Modals -->
    <SubscriptionModal />
    <SocieteRequiredModal />
    <ConsentBanner />
  </div>
</template>
