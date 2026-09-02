import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/index.css'
import { initAnalytics } from './lib/analytics'
import { capturerAttribution } from './lib/attribution'

// Avant que le routeur ne touche à l'URL : le gclid et les utm_* n'y sont
// présents qu'au tout premier chargement.
capturerAttribution()

// Ne charge rien tant que le consentement n'a pas été donné, ni tant que
// VITE_GA4_ID / VITE_GOOGLE_ADS_ID ne sont pas renseignés.
initAnalytics()

const app = createApp(App)
app.use(router)
app.mount('#app')
