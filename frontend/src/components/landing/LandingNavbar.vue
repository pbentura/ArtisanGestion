<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Menu, X } from 'lucide-vue-next'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const route = useRoute()
const isMenuOpen = ref(false)

// Les pages spécialisées reçoivent le trafic publicitaire : elles doivent
// être atteignables depuis n'importe quelle page vitrine.
const pages = [
  { to: '/rapport-intervention', label: 'Rapports IA' },
  { to: '/devis-factures', label: 'Devis & factures' },
  { to: '/mobile', label: 'Sur mobile' },
]
const isScrolled = ref(false)

function navigateToAuth() {
  isMenuOpen.value = false
  router.push('/auth')
}

function scrollTo(id: string) {
  isMenuOpen.value = false
  // Les ancres n'existent que sur l'accueil : depuis une page spécialisée,
  // on y renvoie plutôt que de laisser le clic sans effet.
  if (route.path !== '/') {
    router.push({ path: '/', hash: `#${id}` })
    return
  }
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function handleScroll() {
  isScrolled.value = window.scrollY > 20
}

onMounted(() => window.addEventListener('scroll', handleScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', handleScroll))
</script>

<template>
  <nav
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 pt-safe"
    :class="isScrolled ? 'bg-background/80 backdrop-blur-xl border-b border-border shadow-sm' : 'bg-transparent'"
  >
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-3 group">
          <img src="/logo.svg" alt="Logo" class="w-9 h-9 group-hover:scale-105 transition-transform" />
          <span class="text-xl font-bold text-foreground">Artisan<span class="text-primary">Gestion</span></span>
        </router-link>

        <!-- Desktop Nav -->
        <div class="hidden md:flex items-center gap-8">
          <router-link
            v-for="p in pages" :key="p.to" :to="p.to"
            class="text-sm font-medium transition-colors"
            :class="route.path === p.to ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'"
          >{{ p.label }}</router-link>
          <button @click="scrollTo('pricing')" class="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Tarifs</button>
        </div>

        <!-- Desktop Actions -->
        <div class="flex items-center gap-3">
          <ThemeToggle />
          <button
            @click="navigateToAuth"
            class="hidden lg:inline-flex text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Connexion
          </button>
          <button
            @click="navigateToAuth"
            class="hidden sm:inline-flex px-5 py-2.5 bg-primary text-primary-foreground rounded-full text-sm font-semibold hover:bg-primary/90 transition-all hover:shadow-lg hover:shadow-primary/25 active:scale-95"
          >
            Essayer gratuitement
          </button>

          <!-- Mobile toggle -->
          <button @click="isMenuOpen = !isMenuOpen" class="md:hidden p-2 text-muted-foreground hover:text-foreground transition-colors" aria-label="Menu">
            <Menu v-if="!isMenuOpen" class="w-6 h-6" />
            <X v-else class="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Menu -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-4"
    >
      <div v-if="isMenuOpen" class="fixed inset-0 z-40 bg-background/98 backdrop-blur-2xl md:hidden pt-20 px-6 pb-safe overflow-y-auto">
        <div class="flex flex-col gap-6 py-8">
          <router-link
            v-for="p in pages" :key="p.to" :to="p.to" @click="isMenuOpen = false"
            class="text-lg font-medium text-foreground border-b border-border pb-4"
          >{{ p.label }}</router-link>
          <button @click="scrollTo('pricing')" class="text-left text-lg font-medium text-foreground border-b border-border pb-4">Tarifs</button>
          <button
            @click="navigateToAuth"
            class="w-full px-4 py-3.5 bg-primary text-primary-foreground rounded-2xl text-base font-semibold hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20 mt-4"
          >
            Créer mon compte gratuitement
          </button>
        </div>
      </div>
    </Transition>
  </nav>
</template>
