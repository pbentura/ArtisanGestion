import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '@/views/LandingPage.vue'
import AuthPage from '@/views/AuthPage.vue'

import { API_BASE_URL } from '@/lib/api'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: LandingPage
  },
  {
    path: '/auth',
    name: 'auth',
    component: AuthPage
  },
  {
    path: '/onboarding',
    name: 'onboarding',
    component: () => import('@/views/OnboardingSociete.vue'),
    meta: { requiresAuth: true, requiresNoSociete: true }
  },
  {
    path: '/dashboard',
    component: () => import('@/views/DashboardLayout.vue'),
    meta: { requiresAuth: true, requiresSociete: true },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'devis',
        name: 'devis',
        component: { template: '<div>Page Devis (Bientôt disponible)</div>' }
      },
      {
        path: 'factures',
        name: 'factures',
        component: { template: '<div>Page Factures (Bientôt disponible)</div>' }
      },
      {
        path: 'rapports',
        name: 'rapports',
        component: () => import('@/views/RapportsList.vue')
      },
      {
        path: 'rapports/new',
        name: 'nouveau-rapport',
        component: () => import('@/views/NouveauRapport.vue')
      },
      {
        path: 'settings',
        name: 'settings',
        component: { template: '<div>Page Paramètres (Bientôt disponible)</div>' }
      },
      {
        path: 'entreprise',
        name: 'entreprise',
        component: { template: '<div>Page Mon entreprise (Bientôt disponible)</div>' }
      },
      {
        path: 'clients',
        name: 'clients',
        component: () => import('@/views/ClientsList.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, _from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    return next('/auth')
  }

  if (token && (to.meta.requiresSociete || to.meta.requiresNoSociete)) {
    try {
      const res = await fetch(`${API_BASE_URL}/api/users/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!res.ok) {
        localStorage.removeItem('token')
        return next('/auth')
      }
      
      const user = await res.json()
      const hasSociete = user.societes && user.societes.length > 0

      if (to.meta.requiresSociete && !hasSociete) {
        return next('/onboarding')
      }
      
      if (to.meta.requiresNoSociete && hasSociete) {
        return next('/dashboard')
      }
    } catch (error) {
      console.error('Router guard error:', error)
      return next('/auth')
    }
  }

  next()
})

export default router
