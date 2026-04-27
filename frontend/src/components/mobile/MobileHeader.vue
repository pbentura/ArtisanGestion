<script setup lang="ts">
import { useRoute } from 'vue-router'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { Bell } from 'lucide-vue-next'

const route = useRoute()
</script>

<template>
  <header class="mobile-header">
    <div class="header-left">
      <!-- On peut afficher le logo ou juste le titre de la page -->
      <h1 class="page-title">{{ route.meta.title || route.name }}</h1>
    </div>
    
    <div class="header-right">
      <button class="icon-btn">
        <Bell class="w-5 h-5" />
      </button>
      <ThemeToggle />
    </div>
  </header>
</template>

<style scoped>
.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: calc(56px + env(safe-area-inset-top, 0px));
  padding-top: env(safe-area-inset-top, 0px);
  padding-left: 16px;
  padding-right: 16px;
  background: color-mix(in srgb, var(--background), transparent 5%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
  z-index: 40;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--foreground);
  margin: 0;
  letter-spacing: -0.02em;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn {
  background: none;
  border: none;
  color: var(--muted-foreground);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-radius: 50%;
  -webkit-tap-highlight-color: transparent;
}
</style>
