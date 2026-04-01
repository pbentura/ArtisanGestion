<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { 
  ArrowRight, 
  CheckCircle2,
  Sparkles
} from 'lucide-vue-next'

const router = useRouter()

function navigateToAuth() {
  router.push('/auth')
}
</script>

<template>
  <section class="py-24 lg:py-32 relative overflow-hidden">
    <!-- Background -->
    <div class="absolute inset-0 -z-10">
      <div class="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-background" />
      <div class="absolute bottom-0 left-0 w-[600px] h-[600px] bg-primary/10 rounded-full blur-3xl" />
      <div class="absolute top-0 right-0 w-[400px] h-[400px] bg-primary/5 rounded-full blur-3xl" />
    </div>

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
      <Card class="border-primary/20 bg-gradient-to-br from-card via-card to-primary/5 shadow-2xl">
        <CardContent class="p-8 lg:p-16">
          <div class="grid lg:grid-cols-2 gap-12 items-center">
            <!-- Left: Content -->
            <div class="text-center lg:text-left">
              <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
                <Sparkles class="h-4 w-4" />
                Commencer dès maintenant
              </div>

              <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-6">
                Prêt à transformer votre gestion ?
              </h2>

              <p class="text-lg text-muted-foreground mb-8 leading-relaxed">
                Rejoignez plus de 500 artisans et PME qui gagnent du temps chaque jour avec Ventura. Essai gratuit de 14 jours, sans engagement.
              </p>

              <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Button 
                  size="lg" 
                  class="rounded-full px-8 py-6 text-lg font-semibold shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all"
                  @click="navigateToAuth"
                >
                  Commencer gratuitement
                  <ArrowRight class="ml-2 h-5 w-5" />
                </Button>
              </div>

              <!-- Trust indicators -->
              <div class="flex flex-wrap items-center justify-center lg:justify-start gap-6 mt-8 text-sm text-muted-foreground">
                <div class="flex items-center gap-2">
                  <CheckCircle2 class="h-4 w-4 text-success" />
                  <span>14 jours gratuits</span>
                </div>
                <div class="flex items-center gap-2">
                  <CheckCircle2 class="h-4 w-4 text-success" />
                  <span>Sans carte bancaire</span>
                </div>
                <div class="flex items-center gap-2">
                  <CheckCircle2 class="h-4 w-4 text-success" />
                  <span>Annulation facile</span>
                </div>
              </div>
            </div>

            <!-- Right: Visual -->
            <div class="relative">
              <div class="relative bg-muted/50 rounded-2xl p-8">
                <!-- Mock signup form -->
                <div class="space-y-4">
                  <div class="text-center mb-6">
                    <div class="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                      <Sparkles class="h-8 w-8 text-primary" />
                    </div>
                    <h3 class="text-xl font-semibold text-foreground">Créez votre compte</h3>
                    <p class="text-sm text-muted-foreground">En 30 secondes, c'est parti !</p>
                  </div>

                  <div class="space-y-3">
                    <div class="h-12 bg-card rounded-xl border border-border px-4 flex items-center text-muted-foreground text-sm">
                      Votre adresse email
                    </div>
                    <div class="h-12 bg-card rounded-xl border border-border px-4 flex items-center text-muted-foreground text-sm">
                      Votre mot de passe
                    </div>
                    <div class="h-12 bg-primary rounded-xl flex items-center justify-center text-primary-foreground font-semibold shadow-lg shadow-primary/25">
                      Créer mon compte gratuit
                    </div>
                  </div>

                  <div class="text-center pt-4">
                    <p class="text-xs text-muted-foreground">
                      En vous inscrivant, vous acceptez nos conditions d'utilisation
                    </p>
                  </div>
                </div>

                <!-- Floating success badge -->
                <div class="absolute -top-4 -right-4 bg-success/10 border border-success/20 rounded-xl p-3 shadow-lg">
                  <div class="flex items-center gap-2">
                    <CheckCircle2 class="h-5 w-5 text-success" />
                    <span class="text-sm font-medium text-success">Setup instantané</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </section>
</template>
