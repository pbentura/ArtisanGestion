import { reactive } from 'vue'
import { apiFetch } from './api'

interface CollectionState<T> {
  data: T[]
  loading: boolean
  lastFetched: number | null
}

export const uiStore = reactive({
  showSubscriptionModal: false,
  subscriptionModalContext: {
    badge: "Période d'essai terminée",
    title: "Passez à la vitesse supérieure",
    description: "Votre essai gratuit est arrivé à son terme. Choisissez un abonnement pour continuer à profiter de toutes les fonctionnalités de Ventura.",
    hideTrialBadge: false
  },
  openSubscriptionModal(context?: { badge?: string, title?: string, description?: string, hideTrialBadge?: boolean }) {
    if (context) {
      this.subscriptionModalContext = {
        badge: context.badge || "Période d'essai terminée",
        title: context.title || "Passez à la vitesse supérieure",
        description: context.description || "Votre essai gratuit est arrivé à son terme. Choisissez un abonnement pour continuer à profiter de toutes les fonctionnalités de Ventura.",
        hideTrialBadge: context.hideTrialBadge || false
      }
    } else {
      this.subscriptionModalContext = {
        badge: "Période d'essai terminée",
        title: "Passez à la vitesse supérieure",
        description: "Votre essai gratuit est arrivé à son terme. Choisissez un abonnement pour continuer à profiter de toutes les fonctionnalités de Ventura.",
        hideTrialBadge: false
      }
    }
    this.showSubscriptionModal = true
  },
  closeSubscriptionModal() {
    this.showSubscriptionModal = false
  }
})

export const dataStore = reactive({
  rapports: {
    data: [] as any[],
    loading: false,
    lastFetched: null as number | null
  } as CollectionState<any>,
  
  devis: {
    data: [] as any[],
    loading: false,
    lastFetched: null as number | null
  } as CollectionState<any>,
  
  factures: {
    data: [] as any[],
    loading: false,
    lastFetched: null as number | null
  } as CollectionState<any>,

  clients: {
    data: [] as any[],
    loading: false,
    lastFetched: null as number | null
  } as CollectionState<any>,
  
  user: {
    data: null as any,
    loading: false,
    lastFetched: null as number | null
  },

  dashboard: {
    data: null as any,
    loading: false,
    lastFetched: null as number | null
  },

  async fetchRapports(force = false) {
    if (!force && this.rapports.data.length > 0 && this.rapports.lastFetched && (Date.now() - this.rapports.lastFetched < 30000)) {
      return
    }
    this.rapports.loading = this.rapports.data.length === 0
    try {
      const res = await apiFetch('rapports')
      if (res.ok) {
        this.rapports.data = await res.json()
        this.rapports.lastFetched = Date.now()
      }
    } catch (e) {
      console.error('Store fetch error (rapports):', e)
    } finally {
      this.rapports.loading = false
    }
  },

  async fetchDevis(force = false) {
    if (!force && this.devis.data.length > 0 && this.devis.lastFetched && (Date.now() - this.devis.lastFetched < 30000)) {
      return
    }
    this.devis.loading = this.devis.data.length === 0
    try {
      const res = await apiFetch('devis')
      if (res.ok) {
        this.devis.data = await res.json()
        this.devis.lastFetched = Date.now()
      }
    } catch (e) {
      console.error('Store fetch error (devis):', e)
    } finally {
      this.devis.loading = false
    }
  },

  async fetchFactures(force = false) {
    if (!force && this.factures.data.length > 0 && this.factures.lastFetched && (Date.now() - this.factures.lastFetched < 30000)) {
      return
    }
    this.factures.loading = this.factures.data.length === 0
    try {
      const res = await apiFetch('factures')
      if (res.ok) {
        this.factures.data = await res.json()
        this.factures.lastFetched = Date.now()
      }
    } catch (e) {
      console.error('Store fetch error (factures):', e)
    } finally {
      this.factures.loading = false
    }
  },

  async fetchClients(force = false) {
    if (!force && this.clients.data.length > 0 && this.clients.lastFetched && (Date.now() - this.clients.lastFetched < 60000)) {
      return
    }
    this.clients.loading = this.clients.data.length === 0
    try {
      const res = await apiFetch('clients')
      if (res.ok) {
        this.clients.data = await res.json()
        this.clients.lastFetched = Date.now()
      }
    } catch (e) {
      console.error('Store fetch error (clients):', e)
    } finally {
      this.clients.loading = false
    }
  },

  async fetchUser(force = false) {
    if (!force && this.user.data && this.user.lastFetched && (Date.now() - this.user.lastFetched < 300000)) {
      return
    }
    this.user.loading = true
    try {
      const res = await apiFetch('users/me')
      if (res.ok) {
        this.user.data = await res.json()
        this.user.lastFetched = Date.now()
      }
    } catch (e) {
      console.error('Store fetch error (user):', e)
    } finally {
      this.user.loading = false
    }
  },

  async fetchDashboard(force = false) {
    if (!force && this.dashboard.data && this.dashboard.lastFetched && (Date.now() - this.dashboard.lastFetched < 60000)) {
      return
    }
    this.dashboard.loading = !this.dashboard.data
    try {
      const res = await apiFetch('dashboard')
      if (res.ok) {
        this.dashboard.data = await res.json()
        this.dashboard.lastFetched = Date.now()
      }
    } catch (e) {
      console.error('Store fetch error (dashboard):', e)
    } finally {
      this.dashboard.loading = false
    }
  },

  prefetchAll() {
    this.fetchUser()
    this.fetchDashboard()
    this.fetchRapports()
    this.fetchDevis()
    this.fetchFactures()
    this.fetchClients()
  },

  // Helper to update locally after a mutation
  updateItem(collection: 'rapports' | 'devis' | 'factures' | 'clients', id: number, data: any) {
    const index = this[collection].data.findIndex((item: any) => item.id === id)
    if (index !== -1) {
      this[collection].data[index] = { ...this[collection].data[index], ...data }
    }
  },

  removeItem(collection: 'rapports' | 'devis' | 'factures' | 'clients', id: number) {
    this[collection].data = this[collection].data.filter((item: any) => item.id !== id)
  }
})
