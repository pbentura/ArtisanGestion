<script setup lang="ts">
import { ref } from 'vue'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { 
  User, Settings, CreditCard, Receipt, LifeBuoy 
} from 'lucide-vue-next'

const activeTab = ref('compte')
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-12">
    <div>
      <h1 class="text-3xl font-bold tracking-tight text-foreground">Paramètres</h1>
      <p class="text-muted-foreground mt-1">Gérez votre compte, vos préférences et vos abonnements.</p>
    </div>

    <Tabs v-model="activeTab" defaultValue="compte" class="space-y-6">
      <TabsList class="bg-muted/50 p-1 rounded-xl w-full md:w-auto h-auto grid grid-cols-2 md:inline-flex">
        <TabsTrigger value="compte" class="rounded-lg py-2 px-4">
          <User class="w-4 h-4 mr-2" /> Compte
        </TabsTrigger>
        <TabsTrigger value="preferences" class="rounded-lg py-2 px-4">
          <Settings class="w-4 h-4 mr-2" /> Préférences
        </TabsTrigger>
        <TabsTrigger value="abonnement" class="rounded-lg py-2 px-4">
          <CreditCard class="w-4 h-4 mr-2" /> Abonnement
        </TabsTrigger>
        <TabsTrigger value="facturation" class="rounded-lg py-2 px-4">
          <Receipt class="w-4 h-4 mr-2" /> Facturation
        </TabsTrigger>
        <TabsTrigger value="support" class="rounded-lg py-2 px-4">
          <LifeBuoy class="w-4 h-4 mr-2" /> Support
        </TabsTrigger>
      </TabsList>

      <!-- Compte Tab -->
      <TabsContent value="compte">
        <Card class="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle>Mon Compte</CardTitle>
            <CardDescription>Gérez vos informations personnelles et de connexion.</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <p class="text-sm text-muted-foreground">Section en cours de développement...</p>
          </CardContent>
        </Card>
      </TabsContent>

      <!-- Préférences Tab -->
      <TabsContent value="preferences">
        <Card class="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle>Préférences</CardTitle>
            <CardDescription>Personnalisez votre interface et vos notifications.</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <p class="text-sm text-muted-foreground">Section en cours de développement...</p>
          </CardContent>
        </Card>
      </TabsContent>

      <!-- Abonnement Tab -->
      <TabsContent value="abonnement">
        <Card class="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle>Abonnement</CardTitle>
            <CardDescription>Gérez votre forfait et vos limites d'utilisation.</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <p class="text-sm text-muted-foreground">Section en cours de développement...</p>
          </CardContent>
        </Card>
      </TabsContent>

      <!-- Facturation Tab -->
      <TabsContent value="facturation">
        <Card class="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle>Facturation</CardTitle>
            <CardDescription>Consultez vos factures et gérez vos méthodes de paiement.</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <p class="text-sm text-muted-foreground">Section en cours de développement...</p>
          </CardContent>
        </Card>
      </TabsContent>

      <!-- Support Tab -->
      <TabsContent value="support">
        <Card class="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle>Support & Aide</CardTitle>
            <CardDescription>Besoin d'aide ? Contactez notre équipe technique.</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <p class="text-sm text-muted-foreground">Section en cours de développement...</p>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  </div>
</template>
