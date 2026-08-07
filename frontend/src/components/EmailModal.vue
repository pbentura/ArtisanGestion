<script setup lang="ts">
import { ref, watch } from 'vue'
import { X, Send, Loader2 } from 'lucide-vue-next'
import { apiFetch } from '@/lib/api'

const props = defineProps<{
  isOpen: boolean
  documentId: number | null
  documentType: 'devis' | 'facture' | 'rapport'
  documentRef: string
  clientEmail?: string
}>()

const emit = defineEmits(['close', 'success'])

const toEmail = ref('')
const subject = ref('')
const message = ref('')
const isSending = ref(false)
const statusMessage = ref('')
const statusType = ref<'success' | 'error' | ''>('')

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    toEmail.value = props.clientEmail || ''
    subject.value = `Votre ${props.documentType} ${props.documentRef}`
    message.value = `Bonjour,\n\nVeuillez trouver ci-joint votre ${props.documentType} ${props.documentRef}.\n\nCordialement,`
    statusMessage.value = ''
    statusType.value = ''
  }
})

async function sendEmail() {
  statusMessage.value = ''
  statusType.value = ''
  
  if (!toEmail.value) {
    statusMessage.value = "Veuillez renseigner l'email du destinataire"
    statusType.value = 'error'
    return
  }
  if (!props.documentId) {
    statusMessage.value = "Erreur: Document non sélectionné"
    statusType.value = 'error'
    return
  }
  
  isSending.value = true
  try {
    const res = await apiFetch('emails/send-document', {
      method: 'POST',
      body: JSON.stringify({
        to_email: toEmail.value,
        subject: subject.value,
        message: message.value,
        document_id: props.documentId,
        document_type: props.documentType
      })
    })

    if (res.ok) {
      statusMessage.value = "Email envoyé avec succès !"
      statusType.value = 'success'
      setTimeout(() => {
        emit('success')
        emit('close')
      }, 1500)
    } else {
      const err = await res.json()
      statusMessage.value = err.detail || "Erreur lors de l'envoi"
      statusType.value = 'error'
    }
  } catch (error) {
    console.error('Erreur:', error)
    statusMessage.value = "Erreur de connexion"
    statusType.value = 'error'
  } finally {
    isSending.value = false
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-background/80 backdrop-blur-sm" @click="emit('close')"></div>
    <div class="relative bg-card border border-border rounded-xl shadow-lg max-w-md w-full p-6 animate-in fade-in zoom-in duration-200">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-bold text-foreground">Envoyer par e-mail</h3>
        <button @click="emit('close')" class="p-2 -mr-2 text-muted-foreground hover:bg-muted rounded-full transition-colors">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div v-if="statusMessage" :class="[
        'mb-6 p-3 rounded-lg text-sm flex items-center gap-2',
        statusType === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'
      ]">
        <span>{{ statusMessage }}</span>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-foreground mb-1">Destinataire</label>
          <input 
            v-model="toEmail" 
            type="email" 
            class="w-full px-3 py-2 bg-muted/50 border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
            placeholder="client@exemple.com"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-foreground mb-1">Objet</label>
          <input 
            v-model="subject" 
            type="text" 
            class="w-full px-3 py-2 bg-muted/50 border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-foreground mb-1">Message</label>
          <textarea 
            v-model="message" 
            rows="5"
            class="w-full px-3 py-2 bg-muted/50 border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
          ></textarea>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button 
            @click="emit('close')" 
            class="px-4 py-2 text-sm font-medium border border-border rounded-lg hover:bg-muted transition-colors"
            :disabled="isSending"
          >
            Annuler
          </button>
          <button 
            @click="sendEmail" 
            class="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2"
            :disabled="isSending"
          >
            <template v-if="isSending">
              <Loader2 class="w-4 h-4 animate-spin" />
              Envoi...
            </template>
            <template v-else>
              <Send class="w-4 h-4" />
              Envoyer
            </template>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
