import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '@/views/LandingPage.vue'
import AuthPage from '@/views/AuthPage.vue'
import NotFound from '@/views/NotFound.vue'
import PrivacyPolicy from '@/views/PrivacyPolicy.vue'
import TermsOfService from '@/views/TermsOfService.vue'

import { API_BASE_URL } from '@/lib/api'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: LandingPage,
    meta: { 
      title: 'Ventura | Gérez vos devis, factures et interventions sereinement',
      description: 'Ventura est la plateforme tout-en-un pour les artisans et PME. Gérez vos devis, factures et rapports d\'intervention avec l\'aide de l\'IA.'
    }
  },
  {
    path: '/auth',
    name: 'auth',
    component: AuthPage,
    meta: { 
      title: 'Connexion | Ventura',
      description: 'Connectez-vous à votre espace Ventura pour gérer votre activité.'
    }
  },
  {
    path: '/onboarding',
    name: 'onboarding',
    component: () => import('@/views/OnboardingSociete.vue'),
    meta: { requiresAuth: true, requiresNoSociete: true }
  },
  {
    path: '/dashboard',
    redirect: '/app'
  },
  {
    path: '/app',
    component: () => import('@/views/DashboardLayout.vue'),
    meta: { requiresAuth: true, requiresSociete: true, title: 'Ventura | App' },
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
        path: 'rapports/:id',
        name: 'edit-rapport',
        component: () => import('@/views/NouveauRapport.vue'),
        props: true
      },
      {
        path: 'settings',
        name: 'Paramètres',
        component: () => import('@/views/Settings.vue')
      },
      {
        path: 'entreprise',
        name: 'entreprise',
        component: () => import('@/views/SocieteInfo.vue')
      },
      {
        path: 'clients',
        name: 'clients',
        component: () => import('@/views/ClientsList.vue')
      },
      {
        path: 'admin',
        name: 'admin',
        component: () => import('@/views/AdminPanel.vue'),
        meta: { requiresAdmin: true }
      }
    ]
  },
  // Legal pages
  {
    path: '/legal/privacy',
    name: 'privacy',
    component: PrivacyPolicy,
    meta: { title: 'Politique de Confidentialité | Ventura' }
  },
  {
    path: '/legal/terms',
    name: 'terms',
    component: TermsOfService,
    meta: { title: 'Conditions Générales d\'Utilisation | Ventura' }
  },
  // 404 catch-all
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, _from, next) => {
  // 1. Capture du token depuis l'URL (Google OAuth)
  const tokenFromUrl = to.query.token as string
  if (tokenFromUrl) {
    localStorage.setItem('token', tokenFromUrl)
    
    // Nettoyer l'URL en restant sur la même route mais sans le token dans l'URL
    const { token: _, ...remainingQuery } = to.query
    return next({ 
      path: to.path, 
      query: remainingQuery, 
      replace: true 
    })
  }

  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    return next('/auth')
  }

  if (token && (to.meta.requiresSociete || to.meta.requiresNoSociete || to.matched.some(r => r.meta.requiresAdmin))) {
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
        return next('/app')
      }

      // Block /admin for non-ADMIN users → page forbidden
      if (to.matched.some(r => r.meta.requiresAdmin) && user.role !== 'ADMIN') {
        return next({ name: 'not-found', params: { pathMatch: to.path.split('/').slice(1) }, query: { forbidden: '1' } })
      }
    } catch (error) {
      console.error('Router guard error:', error)
      return next('/auth')
    }
  }

  // Mise à jour du titre et de la meta description
  const meta = to.matched.slice().reverse().find(r => r.meta?.title || r.meta?.description)?.meta
  document.title = (meta?.title as string) || 'Ventura | Gestion simplifiée pour artisans & PME'
  
  const descriptionTag = document.querySelector('meta[name="description"]')
  if (descriptionTag) {
    descriptionTag.setAttribute('content', (meta?.description as string) || 'Ventura — La solution tout-en-un pour les artisans et PME.')
  }

  next()
})

export default router
