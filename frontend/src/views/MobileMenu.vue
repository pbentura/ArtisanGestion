<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Building2, Settings, ShieldCheck, LogOut, ChevronRight, Users } from 'lucide-vue-next'
import { apiFetch } from '@/lib/api'

const router = useRouter()
const user = ref({ prenom: '', nom: '', email: '', role: '', is_owner: true, can_edit_societe: true, can_invite: true })
const societe = ref({ nom: '' })

onMounted(async () => {
  try {
    const res = await apiFetch('users/me')
    if (res.ok) {
      const data = await res.json()
      user.value = { 
        prenom: data.prenom, 
        nom: data.nom, 
        email: data.email, 
        role: data.role || 'USER',
        is_owner: data.is_owner !== false,
        can_edit_societe: data.can_edit_societe === true,
        can_invite: data.can_invite === true
      }
      if (data.societes?.length > 0) {
        societe.value = data.societes[0]
      }
    }
  } catch (e) {
    console.error('Failed to fetch user data', e)
  }
})

function handleLogout() {
  localStorage.removeItem('token')
  router.push('/auth')
}
</script>

<template>
  <div class="mobile-menu-page">
    <!-- User Profile Header -->
    <div class="profile-section">
      <div class="avatar-large">
        {{ user.prenom ? user.prenom.charAt(0).toUpperCase() : 'U' }}
      </div>
      <h2 class="user-name">{{ user.prenom }} {{ user.nom }}</h2>
      <p class="user-email">{{ user.email }}</p>
    </div>

    <!-- Menu List -->
    <div class="menu-group">
      <h3 class="group-title">Général</h3>
      <div class="menu-list">
        <button v-if="user.is_owner || user.can_edit_societe" class="menu-item" @click="router.push('/app/entreprise')">
          <div class="item-left">
            <div class="icon-box bg-blue-100 text-blue-600">
              <Building2 class="w-5 h-5" />
            </div>
            <span>Entreprise</span>
          </div>
          <ChevronRight class="w-5 h-5 text-muted-foreground" />
        </button>
        
        <button class="menu-item" @click="router.push('/app/settings')">
          <div class="item-left">
            <div class="icon-box bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400">
              <Settings class="w-5 h-5" />
            </div>
            <span>Paramètres</span>
          </div>
          <ChevronRight class="w-5 h-5 text-muted-foreground" />
        </button>

        <button v-if="user.is_owner || user.can_invite" class="menu-item" @click="router.push('/app/collaborateurs')">
          <div class="item-left">
            <div class="icon-box bg-indigo-100 text-indigo-600">
              <Users class="w-5 h-5" />
            </div>
            <span>Collaborateurs</span>
          </div>
          <ChevronRight class="w-5 h-5 text-muted-foreground" />
        </button>
      </div>
    </div>

    <div v-if="user.role === 'ADMIN'" class="menu-group">
      <h3 class="group-title">Administration</h3>
      <div class="menu-list">
        <button class="menu-item" @click="router.push('/app/admin')">
          <div class="item-left">
            <div class="icon-box bg-purple-100 text-purple-600">
              <ShieldCheck class="w-5 h-5" />
            </div>
            <span>Panneau Admin</span>
          </div>
          <ChevronRight class="w-5 h-5 text-muted-foreground" />
        </button>
      </div>
    </div>

    <div class="menu-group mt-8">
      <div class="menu-list">
        <button class="menu-item text-destructive" @click="handleLogout">
          <div class="item-left">
            <div class="icon-box bg-red-100 text-red-600">
              <LogOut class="w-5 h-5" />
            </div>
            <span class="font-semibold">Déconnexion</span>
          </div>
        </button>
      </div>
    </div>
    
    <div class="app-version text-center text-xs text-muted-foreground mt-8 pb-8">
      ArtisanGestion v1.0.0
    </div>
  </div>
</template>

<style scoped>
.mobile-menu-page {
  padding: 16px;
  max-width: 600px;
  margin: 0 auto;
}

.profile-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 0;
  text-align: center;
}

.avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 40px;
  background: var(--primary);
  color: var(--primary-foreground);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.user-name {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0;
  color: var(--foreground);
}

.user-email {
  font-size: 0.9rem;
  color: var(--muted-foreground);
  margin-top: 4px;
}

.menu-group {
  margin-bottom: 24px;
}

.group-title {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted-foreground);
  margin-bottom: 8px;
  padding-left: 16px;
}

.menu-list {
  background: var(--card);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid var(--border);
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 16px;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:active {
  background: var(--muted);
}

.item-left {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 1rem;
  font-weight: 500;
}

.icon-box {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
