<script setup lang="ts">
import { 
  Mail,
  MapPin,
  Twitter,
  Linkedin,
  Github
} from 'lucide-vue-next'

const footerLinks = {
  product: {
    title: 'Produit',
    links: [
      { label: 'Fonctionnalités', href: '#features' },
      { label: 'Tarifs', href: '#pricing' },
      { label: 'Démo', href: '#demo' },
      { label: 'Roadmap', href: '#' },
      { label: 'Intégrations', href: '#' }
    ]
  },
  resources: {
    title: 'Ressources',
    links: [
      { label: 'Documentation', href: '#' },
      { label: 'Centre d\'aide', href: '#' },
      { label: 'Blog', href: '#' },
      { label: 'Tutoriels', href: '#' },
      { label: 'API', href: '#' }
    ]
  },
  company: {
    title: 'Entreprise',
    links: [
      { label: 'À propos', href: '#' },
      { label: 'Carrières', href: '#' },
      { label: 'Contact', href: '#' },
      { label: 'Presse', href: '#' },
      { label: 'Partenaires', href: '#' }
    ]
  },
  legal: {
    title: 'Légal',
    links: [
      { label: 'Mentions légales', href: '#' },
      { label: 'CGU', href: '#' },
      { label: 'Confidentialité', href: '#' },
      { label: 'Cookies', href: '#' },
      { label: 'RGPD', href: '#' }
    ]
  }
}

const socialLinks = [
  { icon: Twitter, href: '#', label: 'Twitter' },
  { icon: Linkedin, href: '#', label: 'LinkedIn' },
  { icon: Github, href: '#', label: 'GitHub' }
]
</script>

<template>
  <footer class="bg-secondary text-secondary-foreground">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <!-- Main Footer -->
      <div class="py-16 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">
        <!-- Brand Column -->
        <div class="col-span-2">
          <div class="flex items-center gap-3 mb-4">
            <img src="/logo.svg" alt="Logo" class="w-10 h-10" />
            <span class="text-xl font-bold">Ventura</span>
          </div>
          <p class="text-secondary-foreground/70 text-sm mb-6 max-w-xs leading-relaxed">
            La solution moderne de gestion pour artisans et PME. Simplifiez votre quotidien, concentrez-vous sur votre métier.
          </p>
          
          <!-- Contact -->
          <div class="space-y-2 text-sm">
            <a href="mailto:contact@ventura.app" class="flex items-center gap-2 text-secondary-foreground/70 hover:text-primary transition-colors">
              <Mail class="h-4 w-4" />
              contact@ventura.app
            </a>
            <div class="flex items-center gap-2 text-secondary-foreground/70">
              <MapPin class="h-4 w-4" />
              Paris, France
            </div>
          </div>
        </div>

        <!-- Links Columns -->
        <div v-for="(section, key) in footerLinks" :key="key">
          <h4 class="font-semibold mb-4 text-sm">{{ section.title }}</h4>
          <ul class="space-y-2">
            <li v-for="link in section.links" :key="link.label">
              <a 
                :href="link.href" 
                class="text-sm text-secondary-foreground/70 hover:text-primary transition-colors"
              >
                {{ link.label }}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="border-t border-secondary-foreground/10 py-6">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p class="text-sm text-secondary-foreground/60">
            © {{ new Date().getFullYear() }} Ventura. Tous droits réservés.
          </p>
          
          <!-- Social Links -->
          <div class="flex items-center gap-4">
            <a
              v-for="social in socialLinks"
              :key="social.label"
              :href="social.href"
              :aria-label="social.label"
              class="w-9 h-9 rounded-lg bg-secondary-foreground/10 flex items-center justify-center hover:bg-primary hover:text-primary-foreground transition-all"
            >
              <component :is="social.icon" class="h-4 w-4" />
            </a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>
