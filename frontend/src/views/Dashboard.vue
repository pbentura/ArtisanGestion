<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMobile } from '@/composables/useMobile'
import {
  TrendingUp, TrendingDown, Minus,
  Receipt, FileText, Users, AlertTriangle,
  Clock, CheckCircle2, ArrowRight, Plus,
  Wallet, BarChart3, Target, ClipboardList,
  Camera, Calendar, RefreshCw
} from 'lucide-vue-next'
import { dataStore, uiStore } from '@/lib/store'

const router = useRouter()
const loading = computed(() => dataStore.dashboard.loading)
const error = ref(false)
const userName = computed(() => dataStore.user.data?.prenom || '')
const companyName = computed(() => dataStore.user.data?.societes?.[0]?.nom || '')
const canCreateDevis = computed(() => dataStore.user.data?.can_create_devis !== false)
const canCreateFactures = computed(() => dataStore.user.data?.can_create_factures !== false)
const canCreateClients = computed(() => dataStore.user.data?.can_create_clients !== false)
const canCreateRapports = computed(() => dataStore.user.data?.can_create_rapports !== false)

interface DashboardData {
  ca_mois_ht: number
  ca_mois_ttc: number
  ca_mois_precedent_ht: number
  ca_mois_precedent_ttc: number
  encours_client_ttc: number
  factures_en_retard_count: number
  factures_en_retard_montant: number
  pipeline_devis_ttc: number
  rapports_30_jours: number
  rapports_en_cours: number
  rapports_termines: number
  derniers_rapports: any[]
  top_clients: { id: number; nom: string; ca_ttc: number }[]
  total_devis: number
  devis_convertis: number
  taux_conversion: number
  factures_a_relancer: any[]
  devis_expirant: any[]
  evolution_ca: { mois: string; label: string; ca_ht: number; ca_ttc: number }[]
  factures_impayees: any[]
}

const data = computed<DashboardData | null>(() => dataStore.dashboard.data)
const trialEnded = computed(() => dataStore.user.data?.trial_days_remaining === 0)
const { isMobileView } = useMobile()

function formatMoney(value: number): string {
  return Number(value).toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + ' €'
}

function formatMoneyFull(value: number): string {
  return Number(value).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €'
}

function formatDate(dateString: string): string {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

function formatShortDate(dateString: string): string {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short'
  })
}

function daysOverdue(dateString: string): number {
  if (!dateString) return 0
  const diff = new Date().getTime() - new Date(dateString).getTime()
  return Math.max(0, Math.floor(diff / (1000 * 60 * 60 * 24)))
}

const caVariation = computed(() => {
  if (!data.value) return { percent: 0, direction: 'neutral' }
  const current = data.value.ca_mois_ttc
  const previous = data.value.ca_mois_precedent_ttc
  if (previous === 0) return { percent: current > 0 ? 100 : 0, direction: current > 0 ? 'up' : 'neutral' }
  const pct = Math.round(((current - previous) / previous) * 100)
  return {
    percent: Math.abs(pct),
    direction: pct > 0 ? 'up' : pct < 0 ? 'down' : 'neutral'
  }
})

const maxEvolutionCA = computed(() => {
  if (!data.value) return 1
  return Math.max(...data.value.evolution_ca.map((e: any) => e.ca_ttc), 1)
})

const maxTopClientCA = computed(() => {
  if (!data.value || data.value.top_clients.length === 0) return 1
  return Math.max(...data.value.top_clients.map((c: any) => c.ca_ttc), 1)
})

const monthLabels = computed(() => {
  if (!data.value) return []
  return data.value.evolution_ca.map((e: any) => {
    const d = new Date(e.mois + '-01')
    return d.toLocaleDateString('fr-FR', { month: 'short' })
  })
})

async function fetchDashboard() {
  error.value = false
  try {
    await Promise.all([
      dataStore.fetchUser(),
      dataStore.fetchDashboard()
    ])
    if (!dataStore.dashboard.data) {
      error.value = true
    }
  } catch (e) {
    console.error('Dashboard fetch error:', e)
    error.value = true
  }
}

onMounted(fetchDashboard)
</script>

<template>
  <div class="dashboard-root">
    <!-- Loading Skeleton -->
    <div v-if="loading" class="dashboard-skeleton">
      <div class="skeleton-header"></div>
      <div class="skeleton-shortcuts"></div>
      <div class="skeleton-kpis">
        <div v-for="i in 4" :key="i" class="skeleton-kpi"></div>
      </div>
      <div class="skeleton-charts">
        <div class="skeleton-chart-lg"></div>
        <div class="skeleton-chart-sm"></div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="dashboard-error">
      <AlertTriangle class="w-12 h-12 text-amber-500 mb-4" />
      <h3>Impossible de charger le tableau de bord</h3>
      <p>Vérifiez votre connexion et réessayez.</p>
      <button @click="fetchDashboard" class="retry-btn">
        <RefreshCw class="w-4 h-4" /> Réessayer
      </button>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="data" class="dashboard-content">

      <!-- Header + Shortcuts -->
      <div v-if="!isMobileView" class="dashboard-header">
        <div class="header-text">
          <h1 class="header-title">Bienvenue, {{ userName }}</h1>
          <p class="header-subtitle">
            Vue d'ensemble de <strong>{{ companyName || 'votre entreprise' }}</strong>
          </p>
        </div>
        <div class="shortcuts">
          <button v-if="canCreateDevis" @click="trialEnded ? uiStore.openSubscriptionModal() : router.push('/app/devis/new')" class="btn-primary" title="Nouveau Devis">
            <Plus class="w-4 h-4" /> Nouveau Devis
          </button>
          <button v-if="canCreateFactures" @click="trialEnded ? uiStore.openSubscriptionModal() : router.push('/app/factures/new')" class="btn-primary" title="Nouvelle Facture">
            <Plus class="w-4 h-4" /> Nouvelle Facture
          </button>
          <button v-if="canCreateClients" @click="router.push('/app/clients')" class="btn-primary">
            <Users class="w-4 h-4" /> Ajouter Client
          </button>
        </div>
      </div>

      <!-- KPI Cards -->
      <div class="kpi-grid">
        <!-- CA Mois -->
        <div class="kpi-card kpi-ca" style="--delay: 0">
          <div class="kpi-icon-box kpi-icon-blue">
            <Wallet class="w-5 h-5" />
          </div>
          <div class="kpi-info">
            <span class="kpi-label">CA du mois (TTC)</span>
            <span class="kpi-value">{{ formatMoney(data.ca_mois_ttc) }}</span>
            <span class="kpi-sub" :class="[
              caVariation.direction === 'up' ? 'kpi-up' : 
              caVariation.direction === 'down' ? 'kpi-down' : 'kpi-neutral'
            ]">
              <TrendingUp v-if="caVariation.direction === 'up'" class="w-3.5 h-3.5" />
              <TrendingDown v-else-if="caVariation.direction === 'down'" class="w-3.5 h-3.5" />
              <Minus v-else class="w-3.5 h-3.5" />
              {{ caVariation.percent }}% vs mois précédent
            </span>
          </div>
        </div>

        <!-- Encours -->
        <div class="kpi-card" style="--delay: 1">
          <div class="kpi-icon-box kpi-icon-blue">
            <Receipt class="w-5 h-5" />
          </div>
          <div class="kpi-info">
            <span class="kpi-label">Encours client</span>
            <span class="kpi-value">{{ formatMoney(data.encours_client_ttc) }}</span>
            <span class="kpi-sub kpi-neutral">
              Factures non encaissées
            </span>
          </div>
        </div>

        <!-- Retards -->
        <div class="kpi-card" style="--delay: 2">
          <div class="kpi-icon-box kpi-icon-red">
            <AlertTriangle class="w-5 h-5" />
          </div>
          <div class="kpi-info">
            <span class="kpi-label">Factures en retard</span>
            <span class="kpi-value">{{ data.factures_en_retard_count }}</span>
            <span class="kpi-sub kpi-down">
              {{ formatMoney(data.factures_en_retard_montant) }} à recouvrer
            </span>
          </div>
        </div>

        <!-- Pipeline -->
        <div class="kpi-card" style="--delay: 3">
          <div class="kpi-icon-box kpi-icon-blue">
            <Target class="w-5 h-5" />
          </div>
          <div class="kpi-info">
            <span class="kpi-label">Pipeline devis</span>
            <span class="kpi-value">{{ formatMoney(data.pipeline_devis_ttc) }}</span>
            <span class="kpi-sub kpi-neutral">
              En attente de conversion
            </span>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="charts-row">
        <!-- Évolution CA 6 mois -->
        <div class="chart-card chart-large" style="--delay: 4">
          <h3 class="chart-title">
            <BarChart3 class="w-5 h-5 text-primary" />
            Évolution du CA (6 mois)
          </h3>
          <div class="bar-chart-container">
            <svg class="bar-chart" viewBox="0 0 420 200" preserveAspectRatio="xMidYMid meet">
              <defs>
                <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="var(--primary)" stop-opacity="0.9"/>
                  <stop offset="100%" stop-color="var(--primary)" stop-opacity="0.4"/>
                </linearGradient>
              </defs>
              <!-- Grid lines -->
              <line v-for="i in 4" :key="'grid-'+i"
                :x1="40" :x2="410"
                :y1="10 + (i - 1) * 50" :y2="10 + (i - 1) * 50"
                stroke="var(--border)" stroke-width="0.5" stroke-dasharray="4,4"
              />
              <!-- Bars -->
              <g v-for="(month, idx) in data.evolution_ca" :key="month.mois">
                <rect
                  :x="55 + idx * 62"
                  :y="170 - (month.ca_ttc / maxEvolutionCA) * 155"
                  :width="36"
                  :height="(month.ca_ttc / maxEvolutionCA) * 155"
                  rx="4"
                  fill="url(#barGrad)"
                  class="bar-rect"
                  :style="{ animationDelay: (idx * 0.1) + 's' }"
                />
                <!-- Value on top -->
                <text
                  :x="55 + idx * 62 + 18"
                  :y="165 - (month.ca_ttc / maxEvolutionCA) * 155"
                  text-anchor="middle"
                  class="bar-value-text"
                  fill="var(--muted-foreground)"
                  font-size="9"
                >
                  {{ month.ca_ttc > 0 ? formatMoney(month.ca_ttc) : '' }}
                </text>
                <!-- Month label -->
                <text
                  :x="55 + idx * 62 + 18"
                  y="188"
                  text-anchor="middle"
                  fill="var(--muted-foreground)"
                  font-size="11"
                  font-weight="600"
                >
                  {{ monthLabels[idx] }}
                </text>
              </g>
            </svg>
          </div>
        </div>

        <!-- Top Clients -->
        <div class="chart-card chart-small" style="--delay: 5">
          <h3 class="chart-title">
            <Users class="w-5 h-5 text-primary" />
            Top 5 Clients
          </h3>
          <div v-if="data.top_clients.length === 0" class="empty-chart-msg">
            <p>Aucune donnée client disponible</p>
          </div>
          <div v-else class="top-clients-list">
            <div v-for="(client, idx) in data.top_clients" :key="client.id" class="top-client-row">
              <div class="top-client-rank">{{ idx + 1 }}</div>
              <div class="top-client-info">
                <span class="top-client-name">{{ client.nom }}</span>
                <div class="top-client-bar-track">
                  <div
                    class="top-client-bar-fill"
                    :style="{ width: (client.ca_ttc / maxTopClientCA * 100) + '%', animationDelay: (idx * 0.12) + 's' }"
                  ></div>
                </div>
              </div>
              <span class="top-client-amount">{{ formatMoney(client.ca_ttc) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Second Row: Factures Impayées + Conversion/Rapports -->
      <div class="charts-row">
        <!-- Factures Impayées -->
        <div class="chart-card chart-large" style="--delay: 6">
          <h3 class="chart-title">
            <Receipt class="w-5 h-5 text-red-500" />
            Factures impayées
          </h3>
          <div v-if="data.factures_impayees.length === 0" class="empty-chart-msg">
            <CheckCircle2 class="w-8 h-8 text-green-500 mb-2" />
            <p>Toutes vos factures sont payées 🎉</p>
          </div>
          <div v-else class="impayees-list">
            <div
              v-for="facture in data.factures_impayees"
              :key="facture.id"
              class="impayee-row"
              @click="router.push(`/app/factures/${facture.id}`)"
            >
              <div class="impayee-left">
                <span class="impayee-numero">{{ facture.numero_facture }}</span>
                <span class="impayee-client">{{ facture.client_nom }}</span>
              </div>
              <div class="impayee-right">
                <span class="impayee-amount">{{ formatMoneyFull(facture.total_ttc) }}</span>
                <span
                  class="impayee-badge"
                  :class="daysOverdue(facture.date_echeance) > 0 ? 'badge-overdue' : 'badge-pending'"
                >
                  {{ daysOverdue(facture.date_echeance) > 0
                    ? daysOverdue(facture.date_echeance) + 'j de retard'
                    : 'Éch. ' + formatShortDate(facture.date_echeance) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Conversion + Rapports -->
        <div class="chart-card chart-small" style="--delay: 7">
          <h3 class="chart-title">
            <Target class="w-5 h-5 text-primary" />
            Taux de conversion
          </h3>
          <!-- Donut Chart -->
          <div class="donut-container">
            <svg viewBox="0 0 120 120" class="donut-chart">
              <circle
                cx="60" cy="60" r="48"
                fill="none"
                stroke="var(--border)"
                stroke-width="12"
              />
              <circle
                cx="60" cy="60" r="48"
                fill="none"
                stroke="var(--primary)"
                stroke-width="12"
                stroke-linecap="round"
                :stroke-dasharray="(data.taux_conversion / 100) * 301.6 + ' 301.6'"
                stroke-dashoffset="0"
                transform="rotate(-90 60 60)"
                class="donut-progress"
              />
              <text x="60" y="55" text-anchor="middle" class="donut-value" fill="var(--foreground)" font-size="22" font-weight="800">
                {{ data.taux_conversion }}%
              </text>
              <text x="60" y="72" text-anchor="middle" fill="var(--muted-foreground)" font-size="9">
                {{ data.devis_convertis }}/{{ data.total_devis }} devis
              </text>
            </svg>
          </div>
          <!-- Rapports Stats -->
          <div class="rapport-stats">
            <div class="rapport-stat-item">
              <ClipboardList class="w-4 h-4 text-primary" />
              <span class="rapport-stat-label">30 derniers jours</span>
              <span class="rapport-stat-value">{{ data.rapports_30_jours }}</span>
            </div>
            <div class="rapport-stat-item">
              <Clock class="w-4 h-4 text-amber-500" />
              <span class="rapport-stat-label">En cours</span>
              <span class="rapport-stat-value">{{ data.rapports_en_cours }}</span>
            </div>
            <div class="rapport-stat-item">
              <CheckCircle2 class="w-4 h-4 text-green-500" />
              <span class="rapport-stat-label">Terminés</span>
              <span class="rapport-stat-value">{{ data.rapports_termines }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Alerts Section -->
      <div v-if="data.factures_a_relancer.length > 0 || data.devis_expirant.length > 0" class="alerts-section" style="--delay: 8">
        <h3 class="section-title">
          <AlertTriangle class="w-5 h-5 text-amber-500" />
          Alertes & Actions requises
        </h3>
        <div class="alerts-grid">
          <!-- Factures à relancer -->
          <div v-if="data.factures_a_relancer.length > 0" class="alert-group alert-red">
            <h4 class="alert-group-title">
              <Receipt class="w-4 h-4" />
              Factures à relancer ({{ data.factures_a_relancer.length }})
            </h4>
            <div
              v-for="f in data.factures_a_relancer.slice(0, 5)"
              :key="'rel-' + f.id"
              class="alert-item"
              @click="router.push(`/app/factures/${f.id}`)"
            >
              <div class="alert-item-left">
                <span class="alert-item-title">{{ f.numero_facture }}</span>
                <span class="alert-item-sub">{{ f.client_nom }} — {{ daysOverdue(f.date_echeance) }}j de retard</span>
              </div>
              <span class="alert-item-amount">{{ formatMoneyFull(f.total_ttc) }}</span>
            </div>
          </div>

          <!-- Devis expirant -->
          <div v-if="data.devis_expirant.length > 0" class="alert-group alert-amber">
            <h4 class="alert-group-title">
              <FileText class="w-4 h-4" />
              Devis expirant bientôt ({{ data.devis_expirant.length }})
            </h4>
            <div
              v-for="d in data.devis_expirant.slice(0, 5)"
              :key="'exp-' + d.id"
              class="alert-item"
              @click="router.push(`/app/devis/${d.id}`)"
            >
              <div class="alert-item-left">
                <span class="alert-item-title">{{ d.numero_devis }}</span>
                <span class="alert-item-sub">{{ d.client_nom }} — Expire le {{ formatDate(d.date_expiration) }}</span>
              </div>
              <span class="alert-item-amount">{{ formatMoneyFull(d.total_ttc) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Derniers Rapports -->
      <div class="reports-section" style="--delay: 9">
        <div class="section-header">
          <h3 class="section-title">
            <ClipboardList class="w-5 h-5 text-primary" />
            Dernières interventions
          </h3>
          <button @click="router.push('/app/rapports')" class="see-all-btn">
            Voir tout <ArrowRight class="w-4 h-4" />
          </button>
        </div>
        <div v-if="data.derniers_rapports.length === 0" class="empty-chart-msg" style="padding: 32px">
          <ClipboardList class="w-8 h-8 text-muted-foreground mb-2" />
          <p>Aucun rapport d'intervention récent</p>
        </div>
        <div v-else class="reports-feed">
          <div
            v-for="rapport in data.derniers_rapports"
            :key="rapport.id"
            class="report-card"
            @click="router.push(`/app/rapports/${rapport.id}`)"
          >
            <!-- Photo thumbnail -->
            <div class="report-thumbnail">
              <img
                v-if="rapport.photos && rapport.photos.length > 0"
                :src="rapport.photos[0]"
                :alt="rapport.titre_document_pdf"
                class="report-thumb-img"
              />
              <img
                v-else-if="rapport.photo_url"
                :src="rapport.photo_url"
                :alt="rapport.titre_document_pdf"
                class="report-thumb-img"
              />
              <div v-else class="report-thumb-placeholder">
                <Camera class="w-5 h-5" />
              </div>
            </div>
            <div class="report-info">
              <span class="report-title">{{ rapport.titre_document_pdf }}</span>
              <span class="report-meta">
                <Calendar class="w-3.5 h-3.5" />
                {{ formatDate(rapport.date_intervention) }}
                · {{ rapport.client_nom }}
              </span>
              <span
                class="report-status-badge"
                :class="rapport.statut === 'terminé' ? 'status-done' : 'status-progress'"
              >
                {{ rapport.statut }}
              </span>
            </div>
            <div v-if="rapport.photos && rapport.photos.length > 1" class="report-photos-count">
              <Camera class="w-3.5 h-3.5" /> {{ rapport.photos.length }}
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* ── Base ── */
.dashboard-root {
  max-width: 1200px;
  margin: 0 auto;
}

/* ── Skeleton ── */
.dashboard-skeleton {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.skeleton-header {
  height: 80px;
  background: var(--muted);
  border-radius: 16px;
  animation: pulse 1.5s ease-in-out infinite;
}
.skeleton-shortcuts {
  height: 44px;
  background: var(--muted);
  border-radius: 12px;
  width: 60%;
  animation: pulse 1.5s ease-in-out 0.15s infinite;
}
.skeleton-kpis {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.skeleton-kpi {
  height: 130px;
  background: var(--muted);
  border-radius: 16px;
  animation: pulse 1.5s ease-in-out 0.3s infinite;
}
.skeleton-charts {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 16px;
}
.skeleton-chart-lg, .skeleton-chart-sm {
  height: 300px;
  background: var(--muted);
  border-radius: 16px;
  animation: pulse 1.5s ease-in-out 0.45s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@media (max-width: 768px) {
  .skeleton-kpis { grid-template-columns: 1fr 1fr; }
  .skeleton-charts { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .skeleton-kpis { grid-template-columns: 1fr; }
}

/* ── Error ── */
.dashboard-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
}
.dashboard-error h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--foreground);
  margin-bottom: 8px;
}
.dashboard-error p {
  color: var(--muted-foreground);
  margin-bottom: 24px;
}
.retry-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--primary);
  color: var(--primary-foreground);
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.retry-btn:hover { opacity: 0.9; }

/* ── Content ── */
.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── Header ── */
.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  animation: fadeSlideUp 0.5s ease-out;
}
.header-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--foreground);
  letter-spacing: -0.02em;
}
.header-subtitle {
  color: var(--muted-foreground);
  font-size: 0.95rem;
  margin-top: 4px;
}
.header-subtitle strong {
  color: var(--foreground);
}

.shortcuts {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.shortcut-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--foreground);
}
.shortcut-btn:hover {
  border-color: var(--primary);
  background: var(--accent);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
/*.shortcut-devis:hover { border-color: #3b82f6; color: #3b82f6; }
.shortcut-facture:hover { border-color: #16a34a; color: #16a34a; }
.shortcut-client:hover { border-color: #8b5cf6; color: #8b5cf6; }*/

/* ── KPI Grid ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
@media (max-width: 1024px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .kpi-grid { grid-template-columns: 1fr; } }

.kpi-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  transition: all 0.3s;
  animation: fadeSlideUp 0.5s ease-out both;
  animation-delay: calc(var(--delay, 0) * 0.08s);
}
.kpi-card:hover {
  border-color: var(--primary);
  box-shadow: 0 8px 30px rgba(37, 99, 235, 0.08);
  transform: translateY(-2px);
}
@media (max-width: 768px) {
  .kpi-card {
    border: none;
    border-radius: 20px;
    box-shadow:
      0 1px 2px rgba(0, 0, 0, 0.04),
      0 4px 16px rgba(0, 0, 0, 0.04);
  }
  .kpi-card:hover {
    border-color: transparent;
    box-shadow:
      0 1px 2px rgba(0, 0, 0, 0.04),
      0 4px 16px rgba(0, 0, 0, 0.04);
    transform: none;
  }
  .kpi-card:active {
    transform: scale(0.985);
  }
}

.kpi-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.kpi-icon-blue { background: rgba(37, 99, 235, 0.1); color: #2563eb; }
.kpi-icon-amber { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.kpi-icon-red { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.kpi-icon-purple { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }

.kpi-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.kpi-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--muted-foreground);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.kpi-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--foreground);
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.kpi-sub {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  font-weight: 500;
  margin-top: 2px;
}
.kpi-up { color: #16a34a; }
.kpi-down { color: #ef4444; }
.kpi-neutral { color: var(--muted-foreground); }

/* ── Chart Cards ── */
.charts-row {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 16px;
}
@media (max-width: 768px) { .charts-row { grid-template-columns: 1fr; } }

.chart-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 24px;
  animation: fadeSlideUp 0.5s ease-out both;
  animation-delay: calc(var(--delay, 0) * 0.08s);
  transition: border-color 0.3s;
}
.chart-card:hover {
  border-color: var(--primary);
}
@media (max-width: 768px) {
  .chart-card {
    border: none;
    border-radius: 20px;
    box-shadow:
      0 1px 2px rgba(0, 0, 0, 0.04),
      0 4px 16px rgba(0, 0, 0, 0.04);
  }
  .chart-card:hover {
    border-color: transparent;
  }
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--foreground);
  margin-bottom: 20px;
}

.empty-chart-msg {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--muted-foreground);
  font-size: 0.9rem;
  text-align: center;
}

/* ── Bar Chart ── */
.bar-chart-container {
  width: 100%;
  overflow: hidden;
}
.bar-chart {
  width: 100%;
  height: auto;
}
.bar-rect {
  animation: barGrow 0.6s ease-out both;
}
.bar-value-text {
  font-weight: 600;
}

@keyframes barGrow {
  from {
    transform: scaleY(0);
    transform-origin: bottom;
  }
  to {
    transform: scaleY(1);
    transform-origin: bottom;
  }
}

/* ── Top Clients ── */
.top-clients-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.top-client-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.top-client-rank {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--accent);
  color: var(--foreground);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 800;
  flex-shrink: 0;
}
.top-client-info {
  flex: 1;
  min-width: 0;
}
.top-client-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--foreground);
  display: block;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.top-client-bar-track {
  width: 100%;
  height: 6px;
  background: var(--muted);
  border-radius: 3px;
  overflow: hidden;
}
.top-client-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), #8b5cf6);
  border-radius: 3px;
  animation: barFillGrow 0.8s ease-out both;
  animation-delay: var(--delay, 0s);
}
@keyframes barFillGrow {
  from { width: 0 !important; }
}

.top-client-amount {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--foreground);
  white-space: nowrap;
}

/* ── Factures Impayées ── */
.impayees-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.impayee-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}
.impayee-row:hover {
  background: var(--accent);
}
.impayee-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.impayee-numero {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--foreground);
}
.impayee-client {
  font-size: 0.75rem;
  color: var(--muted-foreground);
}
.impayee-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}
.impayee-amount {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--foreground);
}
.impayee-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
}
.badge-overdue {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}
.badge-pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

/* ── Donut ── */
.donut-container {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}
.donut-chart {
  width: 120px;
  height: 120px;
}
.donut-progress {
  transition: stroke-dasharray 1s ease-out;
}
.donut-value {
  font-family: inherit;
}

/* ── Rapport Stats ── */
.rapport-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}
.rapport-stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
}
.rapport-stat-label {
  flex: 1;
  color: var(--muted-foreground);
  font-weight: 500;
}
.rapport-stat-value {
  font-weight: 800;
  color: var(--foreground);
}

/* ── Alerts ── */
.alerts-section {
  animation: fadeSlideUp 0.5s ease-out both;
  animation-delay: calc(var(--delay, 0) * 0.08s);
}
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 700;
  color: var(--foreground);
  margin-bottom: 16px;
}
.alerts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}
.alert-group {
  border-radius: 14px;
  padding: 18px;
  border: 1px solid;
}
.alert-red {
  background: rgba(239, 68, 68, 0.04);
  border-color: rgba(239, 68, 68, 0.15);
}
.alert-amber {
  background: rgba(245, 158, 11, 0.04);
  border-color: rgba(245, 158, 11, 0.15);
}
.alert-group-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  font-weight: 700;
  margin-bottom: 12px;
}
.alert-red .alert-group-title { color: #ef4444; }
.alert-amber .alert-group-title { color: #f59e0b; }

.alert-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
}
.alert-item:hover {
  background: rgba(0,0,0,0.03);
}
.alert-item-left {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.alert-item-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--foreground);
}
.alert-item-sub {
  font-size: 0.7rem;
  color: var(--muted-foreground);
}
.alert-item-amount {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--foreground);
  white-space: nowrap;
}

/* ── Reports Feed ── */
.reports-section {
  animation: fadeSlideUp 0.5s ease-out both;
  animation-delay: calc(var(--delay, 0) * 0.08s);
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.see-all-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--primary);
  background: none;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s;
}
.see-all-btn:hover { opacity: 0.8; }

.reports-feed {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}
.report-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.report-card:hover {
  border-color: var(--primary);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.report-thumbnail {
  width: 56px;
  height: 56px;
  border-radius: 10px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--muted);
}
.report-thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.report-thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--muted-foreground);
}

.report-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.report-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--foreground);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.report-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  color: var(--muted-foreground);
}
.report-status-badge {
  display: inline-flex;
  align-self: flex-start;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 0.65rem;
  font-weight: 700;
  margin-top: 2px;
}
.status-done {
  background: rgba(22, 163, 74, 0.1);
  color: #16a34a;
}
.status-progress {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.report-photos-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--muted-foreground);
  background: var(--muted);
  padding: 4px 8px;
  border-radius: 8px;
  white-space: nowrap;
}

</style>
