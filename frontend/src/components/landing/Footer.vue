<script setup lang="ts">
import { Mail, MapPin } from 'lucide-vue-next'

const currentYear = new Date().getFullYear()

const footerSections = [
  {
    title: 'Produit',
    links: [
      { label: 'Rapports d\'intervention', href: '/rapport-intervention' },
      { label: 'Devis & factures', href: '/devis-factures' },
      { label: 'Sur mobile', href: '/mobile' },
      { label: 'Tarifs', href: '/#pricing' },
    ]
  },
  {
    title: 'Légal',
    links: [
      { label: 'Mentions Légales', href: '/legal/mentions-legales' },
      { label: 'CGU', href: '/legal/terms' },
      { label: 'Confidentialité', href: '/legal/privacy' },
      { label: 'Cookies', href: '/legal/privacy#8' },
      { label: 'RGPD', href: '/legal/privacy#7' },
    ]
  }
]
</script>

<template>
  <footer class="bg-secondary text-secondary-foreground relative overflow-hidden">
    <!-- Subtle top glow -->
    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[1px] bg-gradient-to-r from-transparent via-primary/30 to-transparent" />

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <div class="py-16 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-10">
        <!-- Brand -->
        <div class="col-span-2">
          <div class="flex items-center gap-3 mb-5">
            <img src="/logo.svg" alt="Logo ArtisanGestion" class="w-10 h-10" />
            <span class="text-xl font-bold">Artisan<span class="text-primary">Gestion</span></span>
          </div>
          <p class="text-secondary-foreground/60 text-sm mb-6 max-w-xs leading-relaxed">
            L'outil tout-en-un pour gérer votre activité d'artisan et PME. Rapports, devis, factures — simplement.
          </p>
          <div class="space-y-2.5 text-sm">
            <a href="mailto:contact@artisangestion.com" class="flex items-center gap-2.5 text-secondary-foreground/60 hover:text-primary transition-colors">
              <Mail class="h-4 w-4" />
              contact@artisangestion.com
            </a>
            <div class="flex items-center gap-2.5 text-secondary-foreground/60">
              <MapPin class="h-4 w-4" />
              19 Bd Jacques Copeau, 95200 Sarcelles
            </div>
          </div>
        </div>

        <!-- Link columns -->
        <div v-for="section in footerSections" :key="section.title">
          <h4 class="font-semibold mb-4 text-sm text-secondary-foreground/90">{{ section.title }}</h4>
          <ul class="space-y-2.5">
            <li v-for="link in section.links" :key="link.label">
              <!-- Navigation interne : router-link évite un rechargement complet
                   de l'application à chaque clic dans le pied de page. -->
              <router-link
                :to="link.href"
                class="text-sm text-secondary-foreground/60 hover:text-primary transition-colors"
              >
                {{ link.label }}
              </router-link>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom -->
      <div class="border-t border-secondary-foreground/10 py-6">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p class="text-sm text-secondary-foreground/40">
            © {{ currentYear }} ArtisanGestion. Tous droits réservés.
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>
