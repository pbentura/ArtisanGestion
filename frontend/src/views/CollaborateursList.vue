<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { apiFetch } from '@/lib/api'
import { dataStore, uiStore } from '@/lib/store'
import { 
  Users, UserPlus, Copy, Check, Trash2, Loader2, Shield, 
  FileText, Receipt, Building2, ClipboardList, X
} from 'lucide-vue-next'

const isLoading = ref(true)
const collaborateurs = ref<any[]>([])
const invitations = ref<any[]>([])
const showInviteModal = ref(false)
const showPermissionsModal = ref(false)
const selectedCollab = ref<any>(null)
const linkCopied = ref(false)
const generatedLink = ref('')
const isCreatingInvite = ref(false)

const currentUser = computed(() => dataStore.user.data)

const inviteForm = ref({
  email: '',
  can_create_rapports: true,
  can_create_clients: true,
  can_create_devis: false,
  can_create_factures: false,
  can_invite: false,
  can_edit_societe: false,
})

const permissionsForm = ref({
  can_create_rapports: true,
  can_create_clients: true,
  can_create_devis: false,
  can_create_factures: false,
  can_invite: false,
  can_edit_societe: false,
})

const permissions = [
  { key: 'can_create_rapports', label: 'Rapports d\'intervention', icon: ClipboardList, desc: 'Créer et modifier des rapports' },
  { key: 'can_create_clients', label: 'Gestion des clients', icon: Users, desc: 'Ajouter de nouveaux clients' },
  { key: 'can_create_devis', label: 'Devis', icon: FileText, desc: 'Créer et modifier des devis' },
  { key: 'can_create_factures', label: 'Factures', icon: Receipt, desc: 'Créer et modifier des factures' },
  { key: 'can_invite', label: 'Inviter des collaborateurs', icon: UserPlus, desc: 'Inviter de nouveaux membres' },
  { key: 'can_edit_societe', label: 'Modifier l\'entreprise', icon: Building2, desc: 'Modifier les informations de l\'entreprise' },
]

async function loadData() {
  isLoading.value = true
  try {
    const [collabRes, invitRes] = await Promise.all([
      apiFetch('collaborateurs/'),
      apiFetch('collaborateurs/invitations'),
    ])
    if (collabRes.ok) collaborateurs.value = await collabRes.json()
    if (invitRes.ok) invitations.value = await invitRes.json()
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const getFrontendUrl = () => {
  return import.meta.env.VITE_FRONTEND_URL || (import.meta.env.DEV ? 'http://localhost:5173' : 'https://artisangestion.com')
}

async function createInvitation() {
  isCreatingInvite.value = true
  try {
    const res = await apiFetch('collaborateurs/invite', {
      method: 'POST',
      body: JSON.stringify(inviteForm.value),
    })
    if (res.ok) {
      const data = await res.json()
      generatedLink.value = `${getFrontendUrl()}/join/${data.token}`
      await loadData()
    }
  } catch (e) {
    console.error(e)
  } finally {
    isCreatingInvite.value = false
  }
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(generatedLink.value)
    linkCopied.value = true
    setTimeout(() => { linkCopied.value = false }, 2000)
  } catch (e) {
    console.error(e)
  }
}

async function cancelInvitation(id: number) {
  try {
    const res = await apiFetch(`collaborateurs/invitation/${id}`, { method: 'DELETE' })
    if (res.ok) await loadData()
  } catch (e) {
    console.error(e)
  }
}

async function copyInvitationLink(token: string) {
  try {
    await navigator.clipboard.writeText(`${getFrontendUrl()}/join/${token}`)
  } catch (e) {
    console.error(e)
  }
}

function openPermissions(collab: any) {
  selectedCollab.value = collab
  permissionsForm.value = {
    can_create_rapports: collab.can_create_rapports,
    can_create_clients: collab.can_create_clients,
    can_create_devis: collab.can_create_devis,
    can_create_factures: collab.can_create_factures,
    can_invite: collab.can_invite,
    can_edit_societe: collab.can_edit_societe,
  }
  showPermissionsModal.value = true
}

async function savePermissions() {
  if (!selectedCollab.value) return
  try {
    const res = await apiFetch(`collaborateurs/${selectedCollab.value.id}/permissions`, {
      method: 'PATCH',
      body: JSON.stringify(permissionsForm.value),
    })
    if (res.ok) {
      showPermissionsModal.value = false
      await loadData()
    }
  } catch (e) {
    console.error(e)
  }
}

async function removeCollab(id: number) {
  if (!confirm('Êtes-vous sûr de vouloir supprimer le compte de ce collaborateur ?')) return
  try {
    const res = await apiFetch(`collaborateurs/${id}`, { method: 'DELETE' })
    if (res.ok) await loadData()
  } catch (e) {
    console.error(e)
  }
}

function resetInviteModal() {
  // `acces_equipe` inclut l'essai en cours (cf. schemas/user.py).
  if (currentUser.value?.acces_equipe !== true) {
    uiStore.openSubscriptionModal({
      title: 'Passez au plan Équipe',
      description: 'Pour inviter des collaborateurs et travailler en équipe, vous devez passer au plan Équipe.',
      hideTrialBadge: true
    })
    return
  }
  showInviteModal.value = true
  generatedLink.value = ''
  linkCopied.value = false
  inviteForm.value = {
    email: '',
    can_create_rapports: true,
    can_create_clients: true,
    can_create_devis: false,
    can_create_factures: false,
    can_invite: false,
    can_edit_societe: false,
  }
}

onMounted(loadData)
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-12">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-foreground">Équipe</h1>
        <p class="text-muted-foreground mt-1">Gérez vos collaborateurs et leurs permissions.</p>
      </div>
      <button @click="resetInviteModal" class="btn-primary inline-flex items-center gap-2">
        <UserPlus class="w-5 h-5" />
        Inviter un collaborateur
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex items-center justify-center p-12">
      <Loader2 class="w-8 h-8 animate-spin text-primary" />
    </div>

    <template v-else>
      <!-- Membres -->
      <div class="space-y-4">
        <h2 class="text-lg font-semibold text-foreground">Membres ({{ collaborateurs.length }})</h2>
        
        <div class="grid gap-4">
          <div 
            v-for="collab in collaborateurs" 
            :key="collab.id" 
            class="bg-card border border-border rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold" :class="collab.is_owner ? 'bg-primary/15 text-primary' : 'bg-muted text-muted-foreground'">
                {{ collab.prenom?.charAt(0)?.toUpperCase() || 'U' }}
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <p class="font-semibold text-foreground">{{ collab.prenom }} {{ collab.nom }}</p>
                  <span v-if="collab.is_owner" class="px-2 py-0.5 bg-primary/10 text-primary text-xs font-medium rounded-full">Propriétaire</span>
                  <span v-else class="px-2 py-0.5 bg-muted text-muted-foreground text-xs font-medium rounded-full">Collaborateur</span>
                </div>
                <p class="text-sm text-muted-foreground">{{ collab.email }}</p>
                <!-- Permission badges -->
                <div v-if="!collab.is_owner" class="flex flex-wrap gap-1.5 mt-2">
                  <span v-for="perm in permissions" :key="perm.key" class="px-2 py-0.5 rounded-full text-xs font-medium" :class="collab[perm.key] ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-400 border border-red-100 line-through opacity-50'">
                    {{ perm.label }}
                  </span>
                </div>
              </div>
            </div>
            
            <div v-if="!collab.is_owner && currentUser?.is_owner" class="flex items-center gap-2 shrink-0">
              <button @click="openPermissions(collab)" class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-muted text-foreground rounded-lg hover:bg-muted/80 transition-colors">
                <Shield class="w-4 h-4" /> Droits
              </button>
              <button @click="removeCollab(collab.id)" class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
                <Trash2 class="w-4 h-4" /> Supprimer
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Invitations en attente -->
      <div v-if="invitations.filter(i => i.status === 'pending').length > 0" class="space-y-4">
        <h2 class="text-lg font-semibold text-foreground">Invitations en attente</h2>
        <div class="grid gap-3">
          <div 
            v-for="inv in invitations.filter(i => i.status === 'pending')" 
            :key="inv.id"
            class="bg-amber-50/50 border border-amber-200/50 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
          >
            <div>
              <p class="text-sm font-medium text-foreground">{{ inv.email || 'Lien ouvert (sans email)' }}</p>
              <p class="text-xs text-muted-foreground mt-0.5">Expire le {{ new Date(inv.expires_at).toLocaleDateString('fr-FR') }}</p>
            </div>
            <div class="flex items-center gap-2">
              <button @click="copyInvitationLink(inv.token)" class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-colors">
                <Copy class="w-4 h-4" /> Copier le lien
              </button>
              <button @click="cancelInvitation(inv.id)" class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state si seul -->
      <div v-if="collaborateurs.length <= 1 && invitations.filter(i => i.status === 'pending').length === 0" class="text-center py-12 bg-card border border-border rounded-2xl">
        <Users class="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
        <h3 class="text-lg font-semibold text-foreground mb-2">Vous travaillez seul pour l'instant</h3>
        <p class="text-muted-foreground text-sm max-w-md mx-auto mb-6">
          Invitez vos collaborateurs pour qu'ils puissent créer des rapports, gérer les clients et bien plus encore.
        </p>
        <button @click="resetInviteModal" class="btn-primary inline-flex items-center gap-2">
          <UserPlus class="w-5 h-5" />
          Inviter un collaborateur
        </button>
      </div>
    </template>

    <!-- Modal d'invitation -->
    <Teleport to="body">
      <div v-if="showInviteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showInviteModal = false"></div>
        <div class="relative bg-card border border-border rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-bold text-foreground">Inviter un collaborateur</h3>
              <button @click="showInviteModal = false" class="p-1 rounded-lg hover:bg-muted"><X class="w-5 h-5" /></button>
            </div>

            <template v-if="!generatedLink">
              <!-- Email optionnel -->
              <div class="mb-6">
                <label class="block text-sm font-medium text-foreground mb-1.5">Email du collaborateur <span class="text-muted-foreground font-normal">(optionnel)</span></label>
                <input v-model="inviteForm.email" type="email" placeholder="nom@email.com" class="w-full px-3 py-2 bg-background border border-input rounded-lg focus:ring-2 focus:ring-primary outline-none text-sm" />
              </div>

              <!-- Permissions -->
              <div class="mb-6">
                <label class="block text-sm font-medium text-foreground mb-3">Permissions</label>
                <div class="space-y-3">
                  <label v-for="perm in permissions" :key="perm.key" class="flex items-center gap-3 p-3 bg-muted/30 rounded-xl cursor-pointer hover:bg-muted/50 transition-colors">
                    <input type="checkbox" v-model="(inviteForm as any)[perm.key]" class="w-4 h-4 rounded accent-primary" />
                    <component :is="perm.icon" class="w-5 h-5 text-muted-foreground" />
                    <div>
                      <p class="text-sm font-medium text-foreground">{{ perm.label }}</p>
                      <p class="text-xs text-muted-foreground">{{ perm.desc }}</p>
                    </div>
                  </label>
                </div>
              </div>

              <button @click="createInvitation" :disabled="isCreatingInvite" class="btn-primary w-full flex items-center justify-center gap-2">
                <Loader2 v-if="isCreatingInvite" class="w-5 h-5 animate-spin" />
                <UserPlus v-else class="w-5 h-5" />
                Générer le lien d'invitation
              </button>
            </template>

            <!-- Lien généré -->
            <template v-else>
              <div class="text-center mb-6">
                <div class="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <Check class="w-8 h-8 text-green-600" />
                </div>
                <h4 class="text-lg font-semibold text-foreground mb-2">Lien d'invitation créé !</h4>
                <p class="text-sm text-muted-foreground">Envoyez ce lien à votre collaborateur par SMS, WhatsApp ou email.</p>
              </div>
              
              <div class="flex items-center gap-2 p-3 bg-muted rounded-xl mb-4">
                <input :value="generatedLink" readonly class="flex-1 bg-transparent border-none outline-none text-sm font-mono text-foreground truncate" />
                <button @click="copyLink" class="shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg transition-colors" :class="linkCopied ? 'bg-green-100 text-green-700' : 'bg-primary text-white hover:bg-primary/90'">
                  <Check v-if="linkCopied" class="w-4 h-4" />
                  <Copy v-else class="w-4 h-4" />
                  {{ linkCopied ? 'Copié !' : 'Copier' }}
                </button>
              </div>

              <p class="text-xs text-muted-foreground text-center">Ce lien expire dans 7 jours.</p>
            </template>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal permissions -->
    <Teleport to="body">
      <div v-if="showPermissionsModal && selectedCollab" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showPermissionsModal = false"></div>
        <div class="relative bg-card border border-border rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <div>
                <h3 class="text-xl font-bold text-foreground">Permissions</h3>
                <p class="text-sm text-muted-foreground">{{ selectedCollab.prenom }} {{ selectedCollab.nom }}</p>
              </div>
              <button @click="showPermissionsModal = false" class="p-1 rounded-lg hover:bg-muted"><X class="w-5 h-5" /></button>
            </div>

            <div class="space-y-3 mb-6">
              <label v-for="perm in permissions" :key="perm.key" class="flex items-center gap-3 p-3 bg-muted/30 rounded-xl cursor-pointer hover:bg-muted/50 transition-colors">
                <input type="checkbox" v-model="(permissionsForm as any)[perm.key]" class="w-4 h-4 rounded accent-primary" />
                <component :is="perm.icon" class="w-5 h-5 text-muted-foreground" />
                <div>
                  <p class="text-sm font-medium text-foreground">{{ perm.label }}</p>
                  <p class="text-xs text-muted-foreground">{{ perm.desc }}</p>
                </div>
              </label>
            </div>

            <div class="flex gap-3">
              <button @click="showPermissionsModal = false" class="flex-1 px-4 py-2.5 bg-muted text-foreground rounded-xl font-medium hover:bg-muted/80 transition-colors">Annuler</button>
              <button @click="savePermissions" class="flex-1 btn-primary">Enregistrer</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

