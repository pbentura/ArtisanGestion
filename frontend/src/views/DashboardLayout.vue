<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  Building2, Home, FileText, Settings, LogOut, 
  Receipt, Bell, BarChart3, Users, ShieldCheck, Menu
} from 'lucide-vue-next'
import ThemeToggle from '@/components/ThemeToggle.vue'
import MobileHeader from '@/components/mobile/MobileHeader.vue'
import MobileBottomNav from '@/components/mobile/MobileBottomNav.vue'
import { useMobile } from '@/composables/useMobile'
import { dataStore } from '@/lib/store'

const router = useRouter()
const route = useRoute()
const { isMobileView } = useMobile()
const isSidebarOpen = ref(false)
const user = computed(() => {
  const d = dataStore.user.data
  if (!d) return { prenom: '', nom: '', email: '', role: '', is_owner: true, can_create_rapports: true, can_create_devis: true, can_create_factures: true, can_create_clients: true, can_edit_societe: true, can_invite: true }
  return { 
    prenom: d.prenom, 
    nom: d.nom, 
    email: d.email, 
    role: d.role || 'USER', 
    is_owner: d.is_owner !== false,
    can_create_rapports: d.can_create_rapports !== false,
    can_create_devis: d.can_create_devis !== false,
    can_create_factures: d.can_create_factures !== false,
    can_create_clients: d.can_create_clients !== false,
    can_edit_societe: d.can_edit_societe === true,
    can_invite: d.can_invite === true
  }
})

const societe = computed(() => {
  const d = dataStore.user.data
  if (d && d.societes?.length > 0) return d.societes[0]
  return { nom: '' }
})

onMounted(() => {
  // Prefetch everything including user data
  dataStore.prefetchAll()
})

function handleLogout() {
  localStorage.removeItem('token')
  router.push('/auth')
}
</script>

<template>
  <div class="layout-wrapper" :class="{ 'is-native': isMobileView, 'is-browser': !isMobileView }">
    <!-- Mobile overlay for drawer in browser mode -->
    <div 
      v-if="!isMobileView && isSidebarOpen" 
      class="mobile-overlay"
      @click="isSidebarOpen = false"
    ></div>

    <!-- Desktop Sidebar (Hidden on native app, becomes drawer on small browser screens) -->
    <aside 
      v-if="!isMobileView" 
      class="sidebar"
      :class="{ 'sidebar-open': isSidebarOpen }"
    >
      <div class="sidebar-header">
        <div class="logo-box">
          <img src="/logo.svg" alt="Logo" class="w-8 h-8" />
          <span class="logo-name">Artisan<span class="text-primary">Gestion</span></span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <p class="nav-section-title">Menu Principal</p>
        <router-link to="/app/dashboard" class="nav-link">
          <Home class="w-5 h-5" /> Tableau de bord
        </router-link>
        <router-link v-if="user.is_owner || user.can_create_rapports !== false" to="/app/rapports" class="nav-link">
          <BarChart3 class="w-5 h-5" /> Rapports
        </router-link>
        <router-link v-if="user.is_owner || user.can_create_devis !== false" to="/app/devis" class="nav-link">
          <FileText class="w-5 h-5" /> Devis
        </router-link>
        <router-link v-if="user.is_owner || user.can_create_factures !== false" to="/app/factures" class="nav-link">
          <Receipt class="w-5 h-5" /> Factures
        </router-link>

        <p class="nav-section-title mt-8">Administration</p>
        <router-link v-if="user.is_owner || user.can_edit_societe" to="/app/entreprise" class="nav-link">
          <Building2 class="w-5 h-5" /> Entreprise
        </router-link>
        <router-link to="/app/clients" class="nav-link">
          <Users class="w-5 h-5" /> Clients
        </router-link>
        <router-link v-if="user.is_owner || user.can_invite" to="/app/collaborateurs" class="nav-link">
          <Users class="w-5 h-5" /> Collaborateurs
        </router-link>

        <template v-if="user.role === 'ADMIN'">
          <p class="nav-section-title mt-8">Système</p>
          <router-link to="/app/admin" class="nav-link admin-link">
            <ShieldCheck class="w-5 h-5" /> Admin
          </router-link>
        </template>

        <p class="nav-section-title mt-8">Configuration</p>
        <router-link to="/app/settings" class="nav-link">
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
      <!-- Desktop Header (Hidden on native app) -->
      <header v-if="!isMobileView" class="main-header">
        <div class="header-left">
          <button 
            class="hamburger-btn mr-4" 
            @click="isSidebarOpen = true"
          >
            <Menu class="w-6 h-6" />
          </button>
          <h1 class="current-page-title">{{ route.meta.title || route.name }}</h1>
        </div>
        
        <div class="header-right">
          <button class="icon-btn"><Bell class="w-5 h-5" /></button>
          <ThemeToggle />
          <button class="user-pill cursor-pointer hover:bg-muted/50 transition-colors" @click="router.push('/app/settings?tab=compte')">Mon compte</button>
        </div>
      </header>

      <!-- Mobile Header (Visible only on native app) -->
      <div v-if="isMobileView && !route.meta.hideMobileHeader" class="mobile-component">
        <MobileHeader />
      </div>

      <main 
        class="page-content" 
        :class="{ 
          'no-mobile-header': route.meta.hideMobileHeader,
          'no-mobile-nav': route.meta.hideMobileNav 
        }"
      >
        <router-view />
      </main>

      <!-- Mobile Bottom Nav (Visible only on native app) -->
      <div v-if="isMobileView && !route.meta.hideMobileNav" class="mobile-component">
        <MobileBottomNav />
      </div>
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
  z-index: 50;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@media (max-width: 1024px) {
  .is-browser .sidebar {
    position: fixed;
    transform: translateX(-100%);
  }
  .is-browser .sidebar.sidebar-open {
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

.nav-link.router-link-active:not([href="/app"]):not([href="/app/dashboard"]) {
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

.page-content.no-mobile-header {
  padding-top: 0;
}

.hamburger-btn {
  background: none;
  border: none;
  color: var(--foreground);
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
}

@media (max-width: 1024px) {
  .hamburger-btn {
    display: flex;
  }
}

@media (max-width: 1024px) {
  .is-native .main-container {
    padding-left: 0;
  }

  .is-browser .page-content {
    padding: 24px 16px;
  }
  
  .is-browser .page-content.no-mobile-header {
    padding-top: 0;
  }

  .is-native .page-content {
    /* Reduced padding to avoid the huge gap */
    padding: calc(56px + env(safe-area-inset-top, 0px) + 8px) 16px calc(80px + env(safe-area-inset-bottom, 0px) + 8px) 16px;
  }

  .is-native .page-content.no-mobile-header {
    padding-top: 0;
  }

  .is-native .page-content.no-mobile-nav {
    padding-bottom: env(safe-area-inset-bottom, 0px);
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
