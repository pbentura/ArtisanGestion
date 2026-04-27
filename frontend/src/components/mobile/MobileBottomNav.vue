<script setup lang="ts">
import { useRoute } from 'vue-router'
import { Home, BarChart3, Receipt, Users, Menu } from 'lucide-vue-next'

const route = useRoute()

// Fonction pour déterminer si un onglet est actif
function isActive(paths: string[]) {
  return paths.some(path => {
    if (path === '/app') {
      return route.path === '/app' || route.path === '/app/'
    }
    return route.path.startsWith(path)
  })
}
</script>

<template>
  <nav class="mobile-bottom-nav">
    <div class="nav-container">
      <router-link to="/app" class="nav-item" :class="{ active: isActive(['/app']) && !route.path.includes('rapports') && !route.path.includes('factures') && !route.path.includes('devis') && !route.path.includes('clients') && !route.path.includes('menu') }">
        <Home class="icon" />
        <span class="label">Accueil</span>
      </router-link>
      
      <router-link to="/app/rapports" class="nav-item" :class="{ active: isActive(['/app/rapports']) }">
        <BarChart3 class="icon" />
        <span class="label">Rapports</span>
      </router-link>
      
      <!-- L'onglet Facturation pointe vers les factures, où le SegmentedControl gèrera le switch avec Devis -->
      <router-link to="/app/factures" class="nav-item" :class="{ active: isActive(['/app/factures', '/app/devis']) }">
        <Receipt class="icon" />
        <span class="label">Ventes</span>
      </router-link>
      
      <router-link to="/app/clients" class="nav-item" :class="{ active: isActive(['/app/clients']) }">
        <Users class="icon" />
        <span class="label">Clients</span>
      </router-link>
      
      <router-link to="/app/menu" class="nav-item" :class="{ active: isActive(['/app/menu', '/app/settings', '/app/entreprise', '/app/admin']) }">
        <Menu class="icon" />
        <span class="label">Menu</span>
      </router-link>
    </div>
  </nav>
</template>

<style scoped>
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: calc(64px + env(safe-area-inset-bottom, 0px));
  background-color: color-mix(in srgb, var(--card), transparent 10%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--border);
  z-index: 50;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.nav-container {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 64px;
  padding: 0 8px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex: 1;
  height: 100%;
  color: var(--muted-foreground);
  text-decoration: none;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  -webkit-tap-highlight-color: transparent;
}

.nav-item .icon {
  width: 24px;
  height: 24px;
  transition: transform 0.2s, stroke-width 0.2s;
  stroke-width: 1.5px;
}

.nav-item .label {
  font-size: 0.65rem;
  font-weight: 500;
  letter-spacing: 0.02em;
}

.nav-item.active {
  color: var(--primary);
}

.nav-item.active .icon {
  transform: translateY(-2px);
  stroke-width: 2.5px;
}

.nav-item.active .label {
  font-weight: 700;
}
</style>
