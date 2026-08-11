<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CheckCircle2, XCircle, Loader2, ShieldCheck } from 'lucide-vue-next'

import { apiFetch } from '@/lib/api'

const route = useRoute()
const router = useRouter()
const status = ref<'loading' | 'success' | 'cancelled'>('loading')
const countdown = ref(5)

onMounted(async () => {
  // Détecter le statut depuis l'URL
  if (route.path.includes('success')) {
    const sessionId = route.query.session_id as string | undefined
    if (sessionId) {
      try {
        await apiFetch(`factures/verify-payment?session_id=${sessionId}`, { method: 'POST' })
      } catch (e) {
        console.error("Erreur lors de la vérification du paiement", e)
      }
    }
    status.value = 'success'
    
    // Décompte et redirection automatique
    const interval = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(interval)
        router.push('/app/factures')
      }
    }, 1000)
    
  } else {
    status.value = 'cancelled'
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4">
    <div class="max-w-lg w-full">
      <!-- Success State -->
      <div v-if="status === 'success'" class="text-center space-y-6">
        <div class="relative mx-auto w-24 h-24">
          <div class="absolute inset-0 bg-green-500/20 rounded-full animate-ping"></div>
          <div class="relative w-24 h-24 rounded-full bg-green-500/10 border-2 border-green-500/30 flex items-center justify-center">
            <CheckCircle2 class="w-12 h-12 text-green-600" />
          </div>
        </div>

        <div class="space-y-2">
          <h1 class="text-2xl font-bold text-foreground">Paiement réussi ! 🎉</h1>
          <p class="text-muted-foreground max-w-sm mx-auto">
            Votre paiement a été traité avec succès. L'artisan sera notifié et votre facture sera marquée comme payée.
          </p>
        </div>

        <div class="bg-card border border-border rounded-xl p-4 max-w-sm mx-auto">
          <div class="flex items-center gap-3 text-left">
            <ShieldCheck class="w-5 h-5 text-green-600 flex-shrink-0" />
            <p class="text-sm text-muted-foreground">
              Votre paiement est sécurisé par <strong class="text-foreground">Stripe</strong>. Vous recevrez un reçu par email.
            </p>
          </div>
        </div>

        <p class="text-xs text-muted-foreground">
          Redirection automatique dans {{ countdown }} seconde{{ countdown > 1 ? 's' : '' }}...
        </p>
      </div>

      <!-- Cancelled State -->
      <div v-else-if="status === 'cancelled'" class="text-center space-y-6">
        <div class="w-20 h-20 mx-auto rounded-full bg-muted flex items-center justify-center">
          <XCircle class="w-10 h-10 text-muted-foreground" />
        </div>

        <div class="space-y-2">
          <h1 class="text-2xl font-bold text-foreground">Paiement annulé</h1>
          <p class="text-muted-foreground max-w-sm mx-auto">
            Le paiement n'a pas été effectué. Aucun montant n'a été débité de votre compte.
          </p>
        </div>

        <p class="text-xs text-muted-foreground">Vous pouvez fermer cette page ou réessayer via le lien de paiement.</p>
      </div>

      <!-- Loading State -->
      <div v-else class="text-center space-y-4">
        <div class="w-16 h-16 mx-auto rounded-full bg-primary/10 flex items-center justify-center">
          <Loader2 class="w-8 h-8 text-primary animate-spin" />
        </div>
        <p class="text-muted-foreground">Chargement...</p>
      </div>
    </div>
  </div>
</template>
