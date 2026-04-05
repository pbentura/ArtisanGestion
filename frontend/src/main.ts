import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/index.css'
import './lib/firebase'

const app = createApp(App)
app.use(router)
app.mount('#app')
