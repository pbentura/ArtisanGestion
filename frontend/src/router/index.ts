import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '@/views/LandingPage.vue'
import AuthPage from '@/views/AuthPage.vue'
import NotFound from '@/views/NotFound.vue'
import PrivacyPolicy from '@/views/PrivacyPolicy.vue'
import TermsOfService from '@/views/TermsOfService.vue'
import MentionsLegales from '@/views/MentionsLegales.vue'

import { API_BASE_URL } from '@/lib/api'
import { trackPageView, trackConversion } from '@/lib/analytics'
import { Capacitor } from '@capacitor/core'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: LandingPage,
    meta: { 
      title: 'ArtisanGestion | Gérez vos devis, factures et interventions sereinement',
      description: 'ArtisanGestion est la plateforme tout-en-un pour les artisans et PME. Gérez vos devis, factures et rapports d\'intervention avec l\'aide de l\'IA.'
    }
  },
  {
    path: '/mobile',
    name: 'mobile-landing',
    component: () => import('@/views/MobileLandingPage.vue'),
    meta: { 
      title: 'ArtisanGestion Mobile | L\'app tout-en-un pour les artisans',
      description: 'Découvrez l\'application mobile ArtisanGestion. Facturez et créez vos rapports d\'intervention directement sur le chantier.'
    }
  },
  {
    path: '/auth',
    name: 'auth',
    component: AuthPage,
    meta: { 
      title: 'Connexion',
      description: 'Connectez-vous à votre espace ArtisanGestion pour gérer votre activité.'
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
    redirect: '/app/dashboard'
  },
  {
    path: '/app',
    component: () => import('@/views/DashboardLayout.vue'),
    meta: { requiresAuth: true, title: 'Application' },
    redirect: '/app/rapports',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: 'Tableau de bord' }
      },
      {
        path: 'devis',
        name: 'devis',
        component: () => import('@/views/DevisList.vue'),
        meta: { title: 'Devis', permission: 'can_create_devis' }
      },
      {
        path: 'devis/new',
        name: 'nouveau-devis',
        component: () => import('@/views/NouveauDevis.vue'),
        meta: { title: 'Devis', hideMobileHeader: true, hideMobileNav: true, permission: 'can_create_devis' }
      },
      {
        path: 'devis/:id',
        name: 'edit-devis',
        component: () => import('@/views/NouveauDevis.vue'),
        props: true,
        meta: { title: 'Devis', hideMobileHeader: true, hideMobileNav: true, permission: 'can_create_devis' }
      },
      {
        path: 'devis/:id/pdf',
        name: 'devis-pdf',
        component: () => import('@/views/NouveauDevis.vue'),
        props: true,
        meta: { title: 'Aperçu PDF', hideMobileHeader: true, hideMobileNav: true, permission: 'can_create_devis' }
      },
      {
        path: 'factures',
        name: 'factures',
        component: () => import('@/views/FacturesList.vue'),
        meta: { title: 'Factures', permission: 'can_create_factures' }
      },
      {
        path: 'factures/new',
        name: 'nouvelle-facture',
        component: () => import('@/views/NouvelleFacture.vue'),
        meta: { title: 'Nouvelle Facture', hideMobileHeader: true, hideMobileNav: true, permission: 'can_create_factures' }
      },
      {
        path: 'factures/:id',
        name: 'edit-facture',
        component: () => import('@/views/NouvelleFacture.vue'),
        props: true,
        meta: { title: 'Facture', hideMobileHeader: true, hideMobileNav: true, permission: 'can_create_factures' }
      },
      {
        path: 'factures/:id/pdf',
        name: 'facture-pdf',
        component: () => import('@/views/NouvelleFacture.vue'),
        props: true,
        meta: { title: 'Aperçu PDF', hideMobileHeader: true, hideMobileNav: true, permission: 'can_create_factures' }
      },
      {
        path: 'rapports',
        name: 'rapports',
        component: () => import('@/views/RapportsList.vue'),
        meta: { title: 'Rapports', permission: 'can_create_rapports' }
      },
      {
        path: 'rapports/new',
        name: 'nouveau-rapport',
        component: () => import('@/views/NouveauRapport.vue'),
        meta: { title: 'Nouveau Rapport', hideMobileHeader: true, hideMobileNav: true, permission: 'can_create_rapports' }
      },
      {
        path: 'rapports/:id',
        name: 'edit-rapport',
        component: () => import('@/views/NouveauRapport.vue'),
        props: true,
        meta: { title: 'Rapport', hideMobileHeader: true, hideMobileNav: true, permission: 'can_create_rapports' }
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
        meta: { title: 'Mon Entreprise', permission: 'can_edit_societe' }
      },
      {
        path: 'nouvelle-entreprise',
        name: 'nouvelle-entreprise',
        component: () => import('@/views/NouvelleEntreprise.vue'),
        meta: { title: 'Nouvelle Entreprise', hideMobileHeader: true, hideMobileNav: true }
      },
      {
        path: 'clients',
        name: 'clients',
        component: () => import('@/views/ClientsList.vue'),
        meta: { title: 'Clients' }
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
        path: 'collaborateurs',
        name: 'collaborateurs',
        component: () => import('@/views/CollaborateursList.vue'),
        meta: { title: 'Collaborateurs', permission: 'can_invite' }
      },
      {
        path: 'menu',
        name: 'menu',
        component: () => import('@/views/MobileMenu.vue'),
        meta: { title: 'Menu' }
      },
      {
        path: 'stripe-connect/return',
        name: 'stripe-connect-return',
        component: () => import('@/views/StripeConnectReturn.vue'),
        meta: { title: 'Stripe Connect', hideMobileHeader: true, hideMobileNav: true }
      }
    ]
  },
  // Inscription collaborateur (magic link)
  {
    path: '/join/:token',
    name: 'join',
    component: () => import('@/views/RegisterCollaborateur.vue'),
    meta: { 
      title: 'Rejoindre une équipe',
      description: 'Rejoignez l\'équipe de votre entreprise sur ArtisanGestion.'
    }
  },
  // Signature d'un devis à distance (accès public par jeton, sans compte)
  {
    path: '/signer/:token',
    name: 'signer-devis',
    component: () => import('@/views/SignerDevis.vue'),
    meta: {
      title: 'Signer un devis',
      description: 'Consultez et signez électroniquement le devis de votre artisan.'
    }
  },
  // Email verification & password reset
  {
    path: '/verify-email',
    name: 'verify-email',
    component: () => import('@/views/VerifyEmail.vue'),
    meta: { 
      title: 'Vérification de l\'email',
      description: 'Vérifiez votre adresse email pour finaliser votre inscription ArtisanGestion.'
    }
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: () => import('@/views/ResetPassword.vue'),
    meta: { 
      title: 'Réinitialisation du mot de passe',
      description: 'Réinitialisez votre mot de passe ArtisanGestion.'
    }
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
  {
    path: '/legal/mentions-legales',
    name: 'mentions-legales',
    component: MentionsLegales,
    meta: { title: 'Mentions Légales' }
  },
  // 404 catch-all
  {
    path: '/pay/success',
    name: 'pay-success',
    component: () => import('@/views/PayFacture.vue'),
    meta: { title: 'Paiement réussi' }
  },
  {
    path: '/pay/cancel',
    name: 'pay-cancel',
    component: () => import('@/views/PayFacture.vue'),
    meta: { title: 'Paiement annulé' }
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
  if (tokenFromUrl && to.path !== '/verify-email' && to.path !== '/reset-password') {
    localStorage.setItem('token', tokenFromUrl)

    // Repli du flux Google sans popup : le backend signale ici une création de
    // compte, à comptabiliser avant de nettoyer l'URL.
    if (to.query.nouveau === '1') {
      trackConversion('sign_up', { method: 'google' })
    }

    // Nettoyer l'URL en restant sur la même route mais sans le token dans l'URL
    const { token: _, nouveau: __, ...remainingQuery } = to.query
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
      const hasSociete = (user.societes && user.societes.length > 0) || !!user.id_societe

      if (to.meta.requiresSociete && !hasSociete) {
        return next('/onboarding')
      }
      
      if (to.meta.requiresNoSociete && hasSociete) {
        return next('/app')
      }

      // Block requiresOwner for non-owners
      if (to.matched.some(r => r.meta.requiresOwner) && user.is_owner === false) {
        return next({ name: 'dashboard' })
      }

      // Block restricted routes for collaborators without permission
      const requiredPermission = to.meta.permission as string
      if (requiredPermission && user.is_owner === false && user[requiredPermission] !== true) {
        return next({ name: 'dashboard' })
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
      document.title = `ArtisanGestion | ${title}`
    }
  } else {
    document.title = 'ArtisanGestion | Gestion simplifiée pour artisans & PME'
  }
  
  const descriptionTag = document.querySelector('meta[name="description"]')
  if (descriptionTag) {
    descriptionTag.setAttribute('content', (meta?.description as string) || 'ArtisanGestion — La solution tout-en-un pour les artisans et PME.')
  }

  next()
})

// SPA : gtag ne verrait qu'un seul chargement de page. Le titre venant d'être
// posé par la garde ci-dessus, la vue est envoyée après la navigation.
router.afterEach((to) => {
  trackPageView(to.fullPath)
})

export default router
