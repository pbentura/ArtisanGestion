<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowLeft, Scale } from 'lucide-vue-next'
const router = useRouter()
const lastUpdated = '7 août 2026'
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <img src="/logo.svg" alt="Logo" class="w-8 h-8" />
          <span class="font-bold text-lg">Ventura</span>
        </div>
        <button
          @click="router.push('/')"
          class="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft class="w-4 h-4" />
          Retour à l'accueil
        </button>
      </div>
    </header>

    <!-- Hero -->
    <div class="bg-gradient-to-br from-primary/8 via-background to-background border-b border-border">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl py-16">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center">
            <Scale class="w-7 h-7 text-primary" />
          </div>
          <div>
            <h1 class="text-3xl sm:text-4xl font-bold text-foreground">Mentions Légales</h1>
            <p class="text-muted-foreground text-sm mt-1">Dernière mise à jour : {{ lastUpdated }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <main class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl py-12">
      <div class="space-y-12">
        <section class="legal-section">
          <h2 class="text-xl font-bold mb-4 text-foreground">Éditeur du site et de l'application</h2>
          <div class="info-box space-y-2">
            <p><strong>Dénomination :</strong> Pinhas BENTURA</p>
            <p><strong>Forme juridique :</strong> Entrepreneur individuel</p>
            <p><strong>Adresse postale :</strong> 19 BOULEVARD JACQUES COPEAU, 95200 SARCELLES</p>
            <p><strong>SIREN :</strong> 105 578 900</p>
            <p><strong>SIRET du siège social :</strong> 105 578 900 00018</p>
            <p><strong>Code NAF/APE :</strong> 62.01Z / 62.10Y (Activités de programmation informatique)</p>
            <p><strong>Date de création :</strong> 27/05/2026</p>
            <p><strong>Email de contact :</strong> <a href="mailto:pinhasbent@gmail.com" class="text-primary hover:underline">pinhasbent@gmail.com</a></p>
          </div>
        </section>

        <section class="legal-section">
          <h2 class="text-xl font-bold mb-4 text-foreground">Directeur de la publication</h2>
          <p class="text-muted-foreground">Le directeur de la publication est Monsieur Pinhas BENTURA.</p>
        </section>

        <section class="legal-section">
          <h2 class="text-xl font-bold mb-4 text-foreground">Hébergement</h2>
          <p class="text-muted-foreground">
            L'hébergement du site et de l'application est assuré par des prestataires garantissant un stockage des données au sein de l'Union Européenne, conformément à la législation en vigueur.
          </p>
        </section>
      </div>

      <!-- Footer nav -->
      <div class="mt-16 pt-8 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
        <p>© {{ new Date().getFullYear() }} Ventura. Tous droits réservés.</p>
        <div class="flex items-center gap-6">
          <router-link to="/legal/terms" class="hover:text-primary transition-colors">CGU</router-link>
          <router-link to="/legal/privacy" class="hover:text-primary transition-colors">Politique de confidentialité</router-link>
          <router-link to="/" class="hover:text-primary transition-colors">Retour à l'accueil</router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.legal-section {
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border);
}
.legal-section:last-child {
  border-bottom: none;
}
.info-box {
  background: hsl(var(--primary) / 0.05);
  border: 1px solid hsl(var(--primary) / 0.15);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  font-size: 0.95rem;
  color: var(--muted-foreground);
}
.info-box strong {
  color: var(--foreground);
}
</style>
