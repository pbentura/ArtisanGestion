<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  Building2, Home, FileText, Settings, LogOut, 
  Receipt, Menu, X, Bell, BarChart3, Users, ShieldCheck
} from 'lucide-vue-next'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { apiFetch } from '@/lib/api'

const router = useRouter()
const route = useRoute()
const isMobileMenuOpen = ref(false)
const user = ref({ prenom: '', nom: '', email: '', role: '' })
const societe = ref({ nom: '' })

onMounted(async () => {
  try {
    const res = await apiFetch('users/me')
    if (res.ok) {
      const data = await res.json()
      user.value = { prenom: data.prenom, nom: data.nom, email: data.email, role: data.role || 'USER' }
      if (data.societes?.length > 0) {
        societe.value = data.societes[0]
      }
    } else {
      console.error('Erreur API me:', await res.text())
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
  <div class="layout-wrapper">
    <!-- Overlay Mobile -->
    <div 
      v-if="isMobileMenuOpen" 
      class="mobile-overlay"
      @click="isMobileMenuOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'is-open': isMobileMenuOpen }">
      <div class="sidebar-header">
        <div class="logo-box">
          <img src="/logo.svg" alt="Logo" class="w-8 h-8" />
          <span class="logo-name">Ventura</span>
        </div>
        <button class="close-btn lg:hidden" @click="isMobileMenuOpen = false">
          <X class="w-5 h-5" />
        </button>
      </div>

      <nav class="sidebar-nav">
        <p class="nav-section-title">Menu Principal</p>
        <router-link to="/app" class="nav-link" @click="isMobileMenuOpen = false">
          <Home class="w-5 h-5" /> Tableau de bord
        </router-link>
        <router-link to="/app/rapports" class="nav-link" @click="isMobileMenuOpen = false">
          <BarChart3 class="w-5 h-5" /> Rapports
        </router-link>
        <router-link to="/app/devis" class="nav-link" @click="isMobileMenuOpen = false">
          <FileText class="w-5 h-5" /> Devis
        </router-link>
        <router-link to="/app/factures" class="nav-link" @click="isMobileMenuOpen = false">
          <Receipt class="w-5 h-5" /> Factures
        </router-link>

        <p class="nav-section-title mt-8">Administration</p>
        <router-link to="/app/entreprise" class="nav-link" @click="isMobileMenuOpen = false">
          <Building2 class="w-5 h-5" /> Mon entreprise
        </router-link>
        <router-link to="/app/clients" class="nav-link" @click="isMobileMenuOpen = false">
          <Users class="w-5 h-5" /> Mes clients
        </router-link>

        <template v-if="user.role === 'ADMIN'">
          <p class="nav-section-title mt-8">Système</p>
          <router-link to="/app/admin" class="nav-link admin-link" @click="isMobileMenuOpen = false">
            <ShieldCheck class="w-5 h-5" /> Admin
          </router-link>
        </template>

        <p class="nav-section-title mt-8">Configuration</p>
        <router-link to="/app/settings" class="nav-link" @click="isMobileMenuOpen = false">
          <Settings class="w-5 h-5" /> Paramètres
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar text-xs">
            {{ user.prenom ? user.prenom.charAt(0).toUpperCase() : 'U' }}
          </div>
          <div class="user-details">
            <p class="user-name">{{ user.prenom }} {{ user.nom }}</p>
            <p class="user-company">{{ societe.nom || 'Chargement...' }}</p>
          </div>
        </div>
        <button @click="handleLogout" class="logout-link">
          <LogOut class="w-4 h-4 ml-1" /> <span>Déconnexion</span>
        </button>
      </div>
    </aside>

    <!-- Content Area -->
    <div class="main-container">
      <header class="main-header">
        <div class="header-left">
          <button class="menu-trigger lg:hidden" @click="isMobileMenuOpen = true">
            <Menu class="w-6 h-6" />
          </button>
          <h1 class="current-page-title">{{ route.meta.title || route.name }}</h1>
        </div>
        
        <div class="header-right">
          <button class="icon-btn"><Bell class="w-5 h-5" /></button>
          <ThemeToggle />
          <div class="user-pill">Mon compte</div>
        </div>
      </header>

      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout-wrapper {
  display: flex;
  height: 100vh;
  height: 100dvh;
  width: 100%;
  background-color: var(--background);
  font-family: sans-serif;
  overflow: hidden;
}

.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  z-index: 40;
}

/* Sidebar Styling */
.sidebar {
  width: 280px;
  background: var(--card);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: sticky;
  top: 0;
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    left: 0;
    z-index: 50;
    transform: translateX(-100%);
  }
  .sidebar.is-open {
    transform: translateX(0);
  }
}

.sidebar-header {
  height: calc(76px + env(safe-area-inset-top, 0px));
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: calc(12px + env(safe-area-inset-top, 0px)) 24px 0 24px;
  border-bottom: 1px solid var(--border);
  background: var(--card);
}

.logo-box {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: #2563eb;
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-name {
  font-weight: 800;
  font-size: 1.25rem;
  color: var(--foreground);
}

.sidebar-nav {
  flex: 1;
  padding: 32px 16px;
  overflow-y: auto;
}

.nav-section-title {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted-foreground);
  margin-bottom: 12px;
  padding-left: 12px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  color: var(--muted-foreground);
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.nav-link:hover {
  background: var(--accent);
  color: var(--primary);
}

.nav-link.router-link-exact-active {
  background: var(--primary);
  color: var(--primary-foreground);
}

.nav-link.router-link-active:not([href="/app"]) {
  background: var(--primary);
  color: var(--primary-foreground);
}

.sidebar-footer {
  padding: 24px;
  padding-bottom: calc(24px + env(safe-area-inset-bottom, 0px));
  border-top: 1px solid var(--border);
  background: var(--muted);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #2563eb;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.user-name {
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--foreground);
  margin: 0;
}

.user-company {
  font-size: 0.75rem;
  color: var(--muted-foreground);
  margin: 0;
}

.logout-link {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px;
  background: none;
  border: none;
  color: #ef4444;
  font-weight: 700;
  cursor: pointer;
  font-size: 0.85rem;
}

/* Main Content Styling */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.main-header {
  position: sticky;
  top: 0;
  z-index: 40;
  height: calc(76px + env(safe-area-inset-top, 0px));
  background: color-mix(in srgb, var(--card), transparent 10%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: calc(12px + env(safe-area-inset-top, 0px)) 24px 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.current-page-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--foreground);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-btn {
  background: none;
  border: none;
  color: var(--muted-foreground);
  cursor: pointer;
}

.user-pill {
  padding: 8px 16px;
  background: var(--accent);
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--muted-foreground);
}

.page-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}

@media (max-width: 640px) {
  .main-header {
    padding: calc(12px + env(safe-area-inset-top, 0px)) 16px 0 16px;
  }
  .page-content {
    padding: 16px;
  }
}
.mt-8 {
  margin-top: 32px;
}

.admin-link {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.08));
  border: 1px solid rgba(99, 102, 241, 0.15);
}

.admin-link:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15)) !important;
  color: #6366f1 !important;
}

.admin-link.router-link-active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  color: white !important;
  border-color: transparent;
}
</style>
