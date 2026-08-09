<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Building2, Plus, ChevronDown, Check } from 'lucide-vue-next'
import { dataStore, uiStore } from '@/lib/store'
import { apiFetch } from '@/lib/api'

const router = useRouter()

const isDropdownOpen = ref(false)
const isSwitching = ref(false)

const user = computed(() => dataStore.user.data)
const societes = computed(() => user.value?.societes || [])
const activeSociete = computed(() => {
  const targetId = user.value?.active_societe_id || user.value?.id_societe
  if (targetId) {
    return societes.value.find((s: any) => s.id === targetId)
  }
  return societes.value[0]
})

async function switchSociete(societeId: number) {
  if (activeSociete.value?.id === societeId) {
    isDropdownOpen.value = false
    return
  }
  
  isSwitching.value = true
  try {
    const res = await apiFetch(`users/me/switch-societe/${societeId}`, {
      method: 'POST'
    })
    if (res.ok) {
      // Reload the entire page to ensure clean state for the new company
      window.location.reload()
    } else {
      console.error('Erreur lors du changement de société')
    }
  } catch (e) {
    console.error(e)
  } finally {
    isSwitching.value = false
    isDropdownOpen.value = false
  }
}

function handleCreateClick() {
  isDropdownOpen.value = false
  const ownedSocietes = societes.value.filter((s: any) => s.id_user === user.value?.id)
  if (ownedSocietes.length >= 1 && user.value?.role !== 'TEAM' && user.value?.role !== 'ADMIN') {
    uiStore.openSubscriptionModal({
      title: 'Passez au plan Équipe',
      description: 'Pour créer et gérer plusieurs entreprises, vous devez posséder le plan Équipe.',
      hideTrialBadge: true
    })
  } else {
    router.push('/app/nouvelle-entreprise')
  }
}
</script>

<template>
  <div class="relative">
    <button 
      @click="isDropdownOpen = !isDropdownOpen" 
      class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-muted transition-colors border border-border bg-card"
      :disabled="isSwitching"
    >
      <div class="w-7 h-7 rounded bg-primary/10 text-primary flex items-center justify-center shrink-0">
        <Building2 class="w-4 h-4" />
      </div>
      <div class="flex flex-col items-start hidden sm:flex">
        <span class="text-sm font-semibold leading-tight max-w-[120px] truncate">
          {{ activeSociete?.nom || 'Mon Entreprise' }}
        </span>
      </div>
      <ChevronDown class="w-4 h-4 text-muted-foreground ml-1" />
    </button>

    <div v-if="isDropdownOpen" class="fixed inset-0 z-40" @click="isDropdownOpen = false"></div>

    <div v-if="isDropdownOpen" class="absolute right-0 top-full mt-2 w-64 bg-card border border-border rounded-xl shadow-lg z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-200 origin-top-right">
      <div class="p-2">
        <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-2 pt-1">
          Vos entreprises
        </div>
        
        <div class="space-y-1">
          <button 
            v-for="societe in societes" 
            :key="societe.id"
            @click="switchSociete(societe.id)"
            class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-muted transition-colors"
            :class="activeSociete?.id === societe.id ? 'bg-primary/5' : ''"
          >
            <div class="flex items-center gap-3 truncate">
              <div class="w-8 h-8 rounded bg-muted flex items-center justify-center shrink-0">
                <Building2 class="w-4 h-4 text-muted-foreground" />
              </div>
              <span class="text-sm font-medium truncate" :class="activeSociete?.id === societe.id ? 'text-primary' : 'text-foreground'">
                {{ societe.nom }}
              </span>
            </div>
            <Check v-if="activeSociete?.id === societe.id" class="w-4 h-4 text-primary shrink-0 ml-2" />
          </button>
        </div>
      </div>

      <div class="p-2 border-t border-border bg-muted/30">
        <button 
          @click="handleCreateClick"
          class="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg hover:bg-muted text-primary transition-colors text-sm font-medium"
        >
          <Plus class="w-4 h-4" />
          Créer une organisation
        </button>
      </div>
    </div>
  </div>
</template>
