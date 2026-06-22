<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Home, ArrowLeft, ShieldOff } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const isForbidden = computed(() => route.query.forbidden === '1')

// Animation counter
const displayCode = ref('000')
onMounted(() => {
  const target = isForbidden.value ? 403 : 404
  let current = 0
  const step = Math.ceil(target / 40)
  const interval = setInterval(() => {
    current = Math.min(current + step, target)
    displayCode.value = String(current).padStart(3, '0')
    if (current >= target) clearInterval(interval)
  }, 20)
})
</script>

<template>
  <div class="not-found-wrapper">
    <!-- Animated background orbs -->
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>

    <div class="content-card">
      <!-- Icon -->
      <div class="icon-ring" :class="{ forbidden: isForbidden }">
        <ShieldOff v-if="isForbidden" class="icon" />
        <span v-else class="icon-emoji">🔍</span>
      </div>

      <!-- Error code -->
      <div class="error-code">
        <span class="digit">{{ displayCode[0] }}</span>
        <span class="digit accent">{{ displayCode[1] }}</span>
        <span class="digit">{{ displayCode[2] }}</span>
      </div>

      <!-- Title & description -->
      <h1 class="title" v-if="!isForbidden">Page introuvable</h1>
      <h1 class="title" v-else>Accès refusé</h1>

      <p class="description" v-if="!isForbidden">
        La page que vous cherchez n'existe pas ou a été déplacée.
        Vérifiez l'URL ou revenez au tableau de bord.
      </p>
      <p class="description" v-else>
        Vous n'avez pas les permissions nécessaires pour accéder à cette section.
        Cette zone est réservée aux administrateurs.
      </p>

      <!-- Actions -->
      <div class="actions">
        <button class="btn-primary" @click="router.push('/app/dashboard')">
          <Home class="w-4 h-4" />
          Tableau de bord
        </button>
        <button class="btn-ghost" @click="router.back()">
          <ArrowLeft class="w-4 h-4" />
          Retour
        </button>
      </div>

      <!-- Decorative line -->
      <div class="divider-line">
        <span class="divider-text">Ventura</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found-wrapper {
  min-height: 100vh;
  width: 100%;
  background: var(--background);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 24px;
}

/* ---- Orbs ---- */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  animation: float 8s ease-in-out infinite;
}
.orb-1 {
  width: 420px;
  height: 420px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.18), transparent 70%);
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}
.orb-2 {
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.15), transparent 70%);
  bottom: -80px;
  right: -60px;
  animation-delay: -3s;
}
.orb-3 {
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.12), transparent 70%);
  top: 50%;
  left: 60%;
  animation-delay: -5s;
}
@keyframes float {
  0%, 100% { transform: translateY(0px) scale(1); }
  50%       { transform: translateY(-20px) scale(1.04); }
}

/* ---- Card ---- */
.content-card {
  position: relative;
  z-index: 1;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 28px;
  padding: 56px 48px;
  max-width: 520px;
  width: 100%;
  text-align: center;
  box-shadow:
    0 0 0 1px rgba(255,255,255,0.04),
    0 24px 64px rgba(0,0,0,0.25);
  animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(32px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ---- Icon ring ---- */
.icon-ring {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(37,99,235,0.12), rgba(99,102,241,0.12));
  border: 2px solid rgba(37,99,235,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 32px;
  font-size: 2rem;
  animation: pulse-ring 3s ease-in-out infinite;
}
.icon-ring.forbidden {
  background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(220,38,38,0.1));
  border-color: rgba(239,68,68,0.25);
}
.icon-ring .icon {
  width: 36px;
  height: 36px;
  color: #ef4444;
}
.icon-emoji {
  font-size: 2.2rem;
  line-height: 1;
}
@keyframes pulse-ring {
  0%, 100% { box-shadow: 0 0 0 0 rgba(37,99,235,0.1); }
  50%       { box-shadow: 0 0 0 12px rgba(37,99,235,0); }
}

/* ---- Error code ---- */
.error-code {
  display: flex;
  justify-content: center;
  gap: 4px;
  margin-bottom: 24px;
}
.digit {
  font-size: 5rem;
  font-weight: 900;
  line-height: 1;
  color: var(--muted-foreground);
  font-variant-numeric: tabular-nums;
  letter-spacing: -4px;
  opacity: 0.4;
}
.digit.accent {
  background: linear-gradient(135deg, #2563eb, #6366f1, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  opacity: 1;
}

/* ---- Title ---- */
.title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--foreground);
  margin: 0 0 12px;
}

/* ---- Description ---- */
.description {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--muted-foreground);
  margin: 0 0 36px;
  max-width: 380px;
  margin-left: auto;
  margin-right: auto;
}

/* ---- Actions ---- */
.actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 36px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #2563eb, #6366f1);
  color: white;
  font-weight: 700;
  font-size: 0.9rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3);
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.4);
}
.btn-primary:active {
  transform: translateY(0);
}

.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--accent);
  color: var(--muted-foreground);
  font-weight: 600;
  font-size: 0.9rem;
  border: 1px solid var(--border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-ghost:hover {
  background: var(--border);
  color: var(--foreground);
}

/* ---- Divider ---- */
.divider-line {
  display: flex;
  align-items: center;
  gap: 16px;
  color: var(--muted-foreground);
  font-size: 0.75rem;
  opacity: 0.5;
}
.divider-line::before,
.divider-line::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}
.divider-text {
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

@media (max-width: 480px) {
  .content-card {
    padding: 36px 24px;
  }
  .digit {
    font-size: 3.5rem;
  }
  .title {
    font-size: 1.3rem;
  }
}
</style>
