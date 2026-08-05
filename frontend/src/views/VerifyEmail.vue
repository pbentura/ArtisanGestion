<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { API_BASE_URL } from '@/lib/api'
import { CheckCircle2, XCircle, Loader2, ArrowLeft } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

const route = useRoute()
const router = useRouter()

const status = ref<'loading' | 'success' | 'already' | 'error'>('loading')
const message = ref('')

onMounted(async () => {
  const token = route.query.token as string

  if (!token) {
    status.value = 'error'
    message.value = 'Aucun token de vérification fourni.'
    return
  }

  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/verify-email?token=${encodeURIComponent(token)}`)
    const data = await res.json()

    if (res.ok) {
      if (data.message?.includes('déjà')) {
        status.value = 'already'
      } else {
        status.value = 'success'
      }
      message.value = data.message
    } else {
      status.value = 'error'
      message.value = data.detail || 'Le lien de vérification est invalide ou a expiré.'
    }
  } catch {
    status.value = 'error'
    message.value = 'Une erreur réseau est survenue. Veuillez réessayer.'
  }
})

function goToLogin() {
  router.push('/auth')
}
</script>

<template>
  <div class="verify-page">
    <div class="verify-card">
      <!-- Loading -->
      <template v-if="status === 'loading'">
        <div class="icon-wrapper loading">
          <Loader2 class="icon spin" />
        </div>
        <h1>Vérification en cours…</h1>
        <p class="subtitle">Nous vérifions votre adresse email, patientez un instant.</p>
      </template>

      <!-- Success -->
      <template v-if="status === 'success'">
        <div class="icon-wrapper success">
          <CheckCircle2 class="icon" />
        </div>
        <h1>Email vérifié !</h1>
        <p class="subtitle">{{ message }}</p>
        <p class="subtitle">Vous pouvez maintenant vous connecter et accéder à toutes les fonctionnalités.</p>
        <Button class="cta-btn" @click="goToLogin">
          <ArrowLeft :size="16" />
          Se connecter
        </Button>
      </template>

      <!-- Already verified -->
      <template v-if="status === 'already'">
        <div class="icon-wrapper info">
          <CheckCircle2 class="icon" />
        </div>
        <h1>Déjà vérifié</h1>
        <p class="subtitle">{{ message }}</p>
        <Button class="cta-btn" @click="goToLogin">
          <ArrowLeft :size="16" />
          Se connecter
        </Button>
      </template>

      <!-- Error -->
      <template v-if="status === 'error'">
        <div class="icon-wrapper error">
          <XCircle class="icon" />
        </div>
        <h1>Vérification échouée</h1>
        <p class="subtitle">{{ message }}</p>
        <p class="hint">Le lien a peut-être expiré. Vous pouvez demander un nouveau lien depuis la page de connexion.</p>
        <Button class="cta-btn" @click="goToLogin">
          <ArrowLeft :size="16" />
          Retour à la connexion
        </Button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.verify-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8ecf7 50%, #f4f4f7 100%);
  padding: 20px;
}

.verify-card {
  background: white;
  border-radius: 16px;
  padding: 48px 40px;
  max-width: 440px;
  width: 100%;
  text-align: center;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.04);
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.icon-wrapper.loading {
  background: #eff6ff;
}

.icon-wrapper.success {
  background: #ecfdf5;
}

.icon-wrapper.info {
  background: #eff6ff;
}

.icon-wrapper.error {
  background: #fef2f2;
}

.icon {
  width: 32px;
  height: 32px;
}

.loading .icon {
  color: #3b82f6;
}

.success .icon {
  color: #10b981;
}

.info .icon {
  color: #3b82f6;
}

.error .icon {
  color: #ef4444;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

h1 {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 12px 0;
}

.subtitle {
  font-size: 15px;
  color: #6b7280;
  line-height: 1.5;
  margin: 0 0 8px 0;
}

.hint {
  font-size: 13px;
  color: #9ca3af;
  margin: 12px 0 0 0;
  line-height: 1.5;
}

.cta-btn {
  margin-top: 28px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  padding: 12px 28px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cta-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

@media (max-width: 480px) {
  .verify-card {
    padding: 36px 24px;
  }
}
</style>
