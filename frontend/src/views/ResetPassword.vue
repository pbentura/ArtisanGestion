<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { API_BASE_URL } from '@/lib/api'
import { Lock, Eye, EyeOff, CheckCircle2, Loader2, ArrowLeft } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const route = useRoute()
const router = useRouter()

const isLoading = ref(false)
const showPassword = ref(false)
const showConfirm = ref(false)
const isSuccess = ref(false)
const errorMessage = ref('')

const form = ref({
  password: '',
  confirmPassword: ''
})

async function handleReset() {
  errorMessage.value = ''

  if (form.value.password.length < 6) {
    errorMessage.value = 'Le mot de passe doit contenir au moins 6 caractères.'
    return
  }

  if (form.value.password !== form.value.confirmPassword) {
    errorMessage.value = 'Les mots de passe ne correspondent pas.'
    return
  }

  const token = route.query.token as string
  if (!token) {
    errorMessage.value = 'Token de réinitialisation manquant.'
    return
  }

  isLoading.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token,
        new_password: form.value.password
      })
    })

    const data = await res.json()

    if (res.ok) {
      isSuccess.value = true
    } else {
      errorMessage.value = data.detail || 'Une erreur est survenue.'
    }
  } catch {
    errorMessage.value = 'Erreur réseau. Veuillez réessayer.'
  } finally {
    isLoading.value = false
  }
}

function goToLogin() {
  router.push('/auth')
}
</script>

<template>
  <div class="reset-page">
    <div class="reset-card">
      <!-- Success state -->
      <template v-if="isSuccess">
        <div class="icon-wrapper success">
          <CheckCircle2 class="icon" />
        </div>
        <h1>Mot de passe réinitialisé !</h1>
        <p class="subtitle">Votre mot de passe a été modifié avec succès. Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.</p>
        <Button class="cta-btn" @click="goToLogin">
          <ArrowLeft :size="16" />
          Se connecter
        </Button>
      </template>

      <!-- Form state -->
      <template v-else>
        <div class="icon-wrapper form-icon">
          <Lock class="icon" />
        </div>
        <h1>Nouveau mot de passe</h1>
        <p class="subtitle">Choisissez un nouveau mot de passe pour votre compte ArtisanGestion.</p>

        <form class="reset-form" @submit.prevent="handleReset">
          <!-- Error message -->
          <div v-if="errorMessage" class="error-banner">
            {{ errorMessage }}
          </div>

          <div class="field">
            <Label for="new-password" class="field-label">Nouveau mot de passe</Label>
            <div class="input-wrapper">
              <Lock :size="16" class="input-icon" />
              <Input
                id="new-password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Minimum 6 caractères"
                required
                class="input-field"
              />
              <button type="button" class="toggle-vis" @click="showPassword = !showPassword">
                <Eye v-if="!showPassword" :size="16" />
                <EyeOff v-else :size="16" />
              </button>
            </div>
          </div>

          <div class="field">
            <Label for="confirm-password" class="field-label">Confirmer le mot de passe</Label>
            <div class="input-wrapper">
              <Lock :size="16" class="input-icon" />
              <Input
                id="confirm-password"
                v-model="form.confirmPassword"
                :type="showConfirm ? 'text' : 'password'"
                placeholder="Retapez le mot de passe"
                required
                class="input-field"
              />
              <button type="button" class="toggle-vis" @click="showConfirm = !showConfirm">
                <Eye v-if="!showConfirm" :size="16" />
                <EyeOff v-else :size="16" />
              </button>
            </div>
          </div>

          <Button type="submit" class="submit-btn" :disabled="isLoading">
            <Loader2 v-if="isLoading" :size="16" class="spin" />
            {{ isLoading ? 'Réinitialisation...' : 'Réinitialiser le mot de passe' }}
          </Button>
        </form>

        <button class="back-link" @click="goToLogin">
          <ArrowLeft :size="14" />
          Retour à la connexion
        </button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.reset-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8ecf7 50%, #f4f4f7 100%);
  padding: 20px;
}

.reset-card {
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

.icon-wrapper.form-icon {
  background: #eff6ff;
}

.icon-wrapper.success {
  background: #ecfdf5;
}

.icon {
  width: 28px;
  height: 28px;
}

.form-icon .icon {
  color: #3b82f6;
}

.success .icon {
  color: #10b981;
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

.reset-form {
  text-align: left;
  margin-top: 28px;
}

.field {
  margin-bottom: 20px;
}

.field-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  color: #9ca3af;
  pointer-events: none;
  z-index: 1;
}

.input-field {
  padding-left: 36px;
  padding-right: 40px;
  height: 44px;
  border-radius: 10px;
  font-size: 14px;
  width: 100%;
}

.toggle-vis {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.toggle-vis:hover {
  color: #6b7280;
}

.error-banner {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 13px;
  color: #dc2626;
  margin-bottom: 20px;
  text-align: center;
}

.submit-btn {
  width: 100%;
  height: 46px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
  margin-top: 4px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: #6b7280;
  font-size: 13px;
  cursor: pointer;
  margin-top: 24px;
  transition: color 0.2s;
}

.back-link:hover {
  color: #3b82f6;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 480px) {
  .reset-card {
    padding: 36px 24px;
  }
}
</style>
