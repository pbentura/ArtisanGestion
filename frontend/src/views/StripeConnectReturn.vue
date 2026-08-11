<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '@/lib/api'
import { CheckCircle2, AlertTriangle, Loader2 } from 'lucide-vue-next'

const router = useRouter()
const status = ref<'loading' | 'success' | 'pending' | 'error'>('loading')
const message = ref('')

onMounted(async () => {
  try {
    const res = await apiFetch('stripe-connect/onboarding/return')
    if (res.ok) {
      const data = await res.json()
      if (data.stripe_connect_enabled) {
        status.value = 'success'
        message.value = 'Votre compte Stripe Connect est actif ! Vos clients pourront désormais payer vos factures en ligne par carte bancaire.'
      } else {
        status.value = 'pending'
        message.value = 'Votre inscription Stripe a été soumise. La vérification peut prendre quelques minutes. Vous serez notifié dès que votre compte sera opérationnel.'
      }
    } else {
      status.value = 'error'
      message.value = 'Une erreur est survenue lors de la vérification de votre compte.'
    }
  } catch (e) {
    status.value = 'error'
    message.value = 'Impossible de contacter le serveur.'
  }

  // Redirection automatique après 5 secondes
  setTimeout(() => {
    router.push('/app/entreprise?tab=settings')
  }, 5000)
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-background p-4">
    <div class="max-w-md w-full text-center space-y-6">
      <!-- Loading -->
      <div v-if="status === 'loading'" class="space-y-4">
        <div class="w-16 h-16 mx-auto rounded-full bg-primary/10 flex items-center justify-center">
          <Loader2 class="w-8 h-8 text-primary animate-spin" />
        </div>
        <h1 class="text-xl font-bold text-foreground">Vérification en cours...</h1>
        <p class="text-muted-foreground">Nous vérifions le statut de votre compte Stripe.</p>
      </div>

      <!-- Success -->
      <div v-else-if="status === 'success'" class="space-y-4">
        <div class="w-16 h-16 mx-auto rounded-full bg-green-500/10 flex items-center justify-center">
          <CheckCircle2 class="w-8 h-8 text-green-600" />
        </div>
        <h1 class="text-xl font-bold text-foreground">Paiement en ligne activé ! 🎉</h1>
        <p class="text-muted-foreground">{{ message }}</p>
      </div>

      <!-- Pending -->
      <div v-else-if="status === 'pending'" class="space-y-4">
        <div class="w-16 h-16 mx-auto rounded-full bg-amber-500/10 flex items-center justify-center">
          <Loader2 class="w-8 h-8 text-amber-600 animate-spin" />
        </div>
        <h1 class="text-xl font-bold text-foreground">Vérification en cours</h1>
        <p class="text-muted-foreground">{{ message }}</p>
      </div>

      <!-- Error -->
      <div v-else class="space-y-4">
        <div class="w-16 h-16 mx-auto rounded-full bg-destructive/10 flex items-center justify-center">
          <AlertTriangle class="w-8 h-8 text-destructive" />
        </div>
        <h1 class="text-xl font-bold text-foreground">Problème rencontré</h1>
        <p class="text-muted-foreground">{{ message }}</p>
      </div>

      <p class="text-xs text-muted-foreground mt-8">
        Redirection automatique vers Mon Entreprise dans 5 secondes...
      </p>
      <button 
        @click="router.push('/app/entreprise?tab=settings')" 
        class="btn-primary mx-auto"
      >
        Retour à Mon Entreprise
      </button>
    </div>
  </div>
</template>
