import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '@/views/LandingPage.vue'
import AuthPage from '@/views/AuthPage.vue'
import NotFound from '@/views/NotFound.vue'
import PrivacyPolicy from '@/views/PrivacyPolicy.vue'
import TermsOfService from '@/views/TermsOfService.vue'

import { API_BASE_URL } from '@/lib/api'
import { Capacitor } from '@capacitor/core'

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
      title: 'Connexion',
      description: 'Connectez-vous à votre espace Ventura pour gérer votre activité.'
    }
  },
  {
    path: '/onboarding',
    name: 'onboarding',
    component: () => import('@/views/OnboardingSociete.vue'),
    meta: { 
      requiresAuth: true, 
      requiresNoSociete: true,
      title: 'Configuration de votre entreprise'
    }
  },
  {
    path: '/dashboard',
    redirect: '/app'
  },
  {
    path: '/app',
    component: () => import('@/views/DashboardLayout.vue'),
    meta: { requiresAuth: true, requiresSociete: true, title: 'Application' },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: 'Tableau de bord' }
      },
      {
        path: 'devis',
        name: 'devis',
        component: () => import('@/views/DevisList.vue'),
        meta: { title: 'Devis' }
      },
      {
        path: 'devis/new',
        name: 'nouveau-devis',
        component: () => import('@/views/NouveauDevis.vue'),
        meta: { title: 'Devis', hideMobileHeader: true, hideMobileNav: true }
      },
      {
        path: 'devis/:id',
        name: 'edit-devis',
        component: () => import('@/views/NouveauDevis.vue'),
        props: true,
        meta: { title: 'Devis', hideMobileHeader: true, hideMobileNav: true }
      },
      {
        path: 'factures',
        name: 'factures',
        component: () => import('@/views/FacturesList.vue'),
        meta: { title: 'Factures' }
      },
      {
        path: 'factures/new',
        name: 'nouvelle-facture',
        component: () => import('@/views/NouvelleFacture.vue'),
        meta: { title: 'Factures', hideMobileHeader: true, hideMobileNav: true }
      },
      {
        path: 'factures/:id',
        name: 'edit-facture',
        component: () => import('@/views/NouvelleFacture.vue'),
        props: true,
        meta: { title: 'Factures', hideMobileHeader: true, hideMobileNav: true }
      },
      {
        path: 'rapports',
        name: 'rapports',
        component: () => import('@/views/RapportsList.vue'),
        meta: { title: 'Rapports' }
      },
      {
        path: 'rapports/new',
        name: 'nouveau-rapport',
        component: () => import('@/views/NouveauRapport.vue'),
        meta: { title: 'Rapports', hideMobileHeader: true, hideMobileNav: true }
      },
      {
        path: 'rapports/:id',
        name: 'edit-rapport',
        component: () => import('@/views/NouveauRapport.vue'),
        props: true,
        meta: { title: 'Rapports', hideMobileHeader: true, hideMobileNav: true }
      },
      {
        path: 'settings',
        name: 'Paramètres',
        component: () => import('@/views/Settings.vue'),
        meta: { title: 'Paramètres' }
      },
      {
        path: 'entreprise',
        name: 'entreprise',
        component: () => import('@/views/SocieteInfo.vue'),
        meta: { title: 'Mon entreprise' }
      },
      {
        path: 'clients',
        name: 'clients',
        component: () => import('@/views/ClientsList.vue'),
        meta: { title: 'Mes clients' }
      },
      {
        path: 'admin',
        name: 'admin',
        component: () => import('@/views/AdminPanel.vue'),
        meta: { 
          requiresAdmin: true,
          title: 'Administration'
        }
      },
      {
        path: 'menu',
        name: 'menu',
        component: () => import('@/views/MobileMenu.vue'),
        meta: { title: 'Menu' }
      }
    ]
  },
  // Legal pages
  {
    path: '/legal/privacy',
    name: 'privacy',
    component: PrivacyPolicy,
    meta: { title: 'Politique de Confidentialité' }
  },
  {
    path: '/legal/terms',
    name: 'terms',
    component: TermsOfService,
    meta: { title: 'Conditions Générales d\'Utilisation' }
  },
  // 404 catch-all
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound,
    meta: { title: 'Page non trouvée' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, _from, next) => {
  // Redirection automatique de la landing vers l'auth sur mobile natif
  if (to.path === '/' && Capacitor.isNativePlatform()) {
    return next('/auth')
  }

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
  const title = meta?.title as string
  
  if (title) {
    if (to.name === 'landing') {
      document.title = title // Conserver le titre complet pour la landing
    } else {
      document.title = `Ventura | ${title}`
    }
  } else {
    document.title = 'Ventura | Gestion simplifiée pour artisans & PME'
  }
  
  const descriptionTag = document.querySelector('meta[name="description"]')
  if (descriptionTag) {
    descriptionTag.setAttribute('content', (meta?.description as string) || 'Ventura — La solution tout-en-un pour les artisans et PME.')
  }

  next()
})

export default router
