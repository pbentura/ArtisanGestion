<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { API_BASE_URL } from '@/lib/api'

const userName = ref('')
const companyName = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/api/users/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      const data = await res.json()
      userName.value = data.prenom
      if (data.societes && data.societes.length > 0) {
        companyName.value = data.societes[0].nom
      }
    }
  } catch(e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div v-if="loading" class="animate-pulse flex space-x-4">
      <div class="flex-1 space-y-4 py-1">
        <div class="h-8 bg-muted rounded w-3/4"></div>
        <div class="space-y-3">
          <div class="h-4 bg-muted rounded"></div>
          <div class="h-4 bg-muted rounded w-5/6"></div>
        </div>
      </div>
    </div>
    <div v-else>
      <h1 class="text-3xl font-bold tracking-tight mb-2">Bienvenue, {{ userName }} 👋</h1>
      <p class="text-muted-foreground mb-8 text-lg">
        Votre espace de gestion pour <strong class="text-foreground">{{ companyName || 'votre entreprise' }}</strong>.
      </p>

      <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <!-- Quick Stats placeholder -->
        <div class="bg-card border border-border rounded-xl p-6 shadow-sm">
          <h3 class="text-sm font-medium text-muted-foreground mb-2">Chiffre d'affaires ce mois</h3>
          <p class="text-3xl font-bold text-foreground">0,00 €</p>
        </div>
        <div class="bg-card border border-border rounded-xl p-6 shadow-sm">
          <h3 class="text-sm font-medium text-muted-foreground mb-2">Factures en attente</h3>
          <p class="text-3xl font-bold text-foreground">0</p>
        </div>
        <div class="bg-card border border-border rounded-xl p-6 shadow-sm">
          <h3 class="text-sm font-medium text-muted-foreground mb-2">Devis envoyés</h3>
          <p class="text-3xl font-bold text-foreground">0</p>
        </div>
      </div>
    </div>
  </div>
</template>
