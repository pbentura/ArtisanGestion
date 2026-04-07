<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowLeft, Shield, Lock, Eye, Database, Mail } from 'lucide-vue-next'
const router = useRouter()
const lastUpdated = '7 avril 2026'
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <img src="/logo.svg" alt="Logo" class="w-8 h-8" />
          <span class="font-bold text-lg">Ventura</span>
        </div>
        <button
          @click="router.push('/')"
          class="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft class="w-4 h-4" />
          Retour à l'accueil
        </button>
      </div>
    </header>

    <!-- Hero -->
    <div class="bg-gradient-to-br from-primary/8 via-background to-background border-b border-border">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl py-16">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center">
            <Shield class="w-7 h-7 text-primary" />
          </div>
          <div>
            <h1 class="text-3xl sm:text-4xl font-bold text-foreground">Politique de confidentialité</h1>
            <p class="text-muted-foreground text-sm mt-1">Dernière mise à jour : {{ lastUpdated }}</p>
          </div>
        </div>
        <p class="text-muted-foreground text-lg leading-relaxed max-w-3xl">
          Chez Ventura, la protection de vos données personnelles est une priorité. Ce document vous explique quelles données nous collectons, pourquoi, et quels sont vos droits conformément au Règlement Général sur la Protection des Données (RGPD – Règlement UE 2016/679).
        </p>
      </div>
    </div>

    <!-- Content -->
    <main class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl py-12">
      <div class="prose-legal space-y-12">

        <!-- 1 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Database class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">1. Responsable du traitement</h2>
          </div>
          <div class="section-body">
            <p>Le responsable du traitement des données personnelles collectées via la plateforme Ventura est :</p>
            <div class="info-box">
              <p><strong>Ventura SAS</strong><br />
              Siège social : Paris, France<br />
              Email de contact : <a href="mailto:pinhasbent@gmail.com" class="text-primary hover:underline">pinhasbent@gmail.com</a>
              </p>
            </div>
          </div>
        </section>

        <!-- 2 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Eye class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">2. Données collectées</h2>
          </div>
          <div class="section-body space-y-6">
            <p>Nous collectons les catégories de données suivantes dans le cadre de l'utilisation de la plateforme Ventura :</p>

            <div class="data-category">
              <h3 class="data-category-title">2.1 Données de compte utilisateur</h3>
              <ul class="data-list">
                <li>Nom et prénom</li>
                <li>Adresse e-mail</li>
                <li>Mot de passe (hashé avec bcrypt, non lisible)</li>
                <li>Rôle dans la plateforme (USER / ADMIN)</li>
                <li>Identifiant Google (lors d'une connexion OAuth, aucun mot de passe stocké)</li>
              </ul>
            </div>

            <div class="data-category">
              <h3 class="data-category-title">2.2 Données de votre entreprise (Société)</h3>
              <ul class="data-list">
                <li>Nom commercial, forme juridique, adresse complète, code postal, ville</li>
                <li>Numéro SIRET, numéro RCS, numéro de TVA intracommunautaire</li>
                <li>Coordonnées (téléphone, e-mail)</li>
                <li>Informations financières : IBAN, BIC, nom de la banque, capital social, taux de TVA par défaut, objectif mensuel de chiffre d'affaires</li>
                <li>Logo de l'entreprise (image téléversée)</li>
                <li>Texte de pied de page des documents PDF générés</li>
              </ul>
            </div>

            <div class="data-category">
              <h3 class="data-category-title">2.3 Données de vos clients</h3>
              <ul class="data-list">
                <li>Nom / Raison sociale</li>
                <li>Adresse postale complète (rue, code postal, ville)</li>
                <li>Téléphone, e-mail</li>
                <li>Numéro SIRET (optionnel)</li>
              </ul>
              <p class="data-note">⚠️ Ces données appartiennent à vos clients finaux. En tant qu'utilisateur professionnel, vous êtes co-responsable de traitement pour ces données. Vous devez disposer d'une base légale pour les traiter.</p>
            </div>

            <div class="data-category">
              <h3 class="data-category-title">2.4 Données des rapports d'intervention</h3>
              <ul class="data-list">
                <li>Titre du document, date d'intervention, contenu textuel</li>
                <li>Statut du rapport (en cours / terminée)</li>
                <li>Photos d'intervention (images téléversées, potentiellement géolocalisées selon les métadonnées EXIF)</li>
                <li>Documents PDF générés</li>
              </ul>
            </div>

            <div class="data-category">
              <h3 class="data-category-title">2.5 Données techniques</h3>
              <ul class="data-list">
                <li>Tokens d'authentification JWT (stockés localement dans votre navigateur)</li>
                <li>Adresse IP (lors des requêtes API)</li>
                <li>Métadonnées de connexion (date/heure de création des ressources)</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- 3 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Lock class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">3. Finalités et bases légales des traitements</h2>
          </div>
          <div class="section-body">
            <div class="table-wrapper">
              <table class="legal-table">
                <thead>
                  <tr>
                    <th>Finalité</th>
                    <th>Base légale (RGPD)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Création et gestion de votre compte</td>
                    <td>Exécution du contrat (Art. 6.1.b)</td>
                  </tr>
                  <tr>
                    <td>Authentification (email/mdp ou Google OAuth)</td>
                    <td>Exécution du contrat (Art. 6.1.b)</td>
                  </tr>
                  <tr>
                    <td>Gestion de vos clients, rapports, devis, factures</td>
                    <td>Exécution du contrat (Art. 6.1.b)</td>
                  </tr>
                  <tr>
                    <td>Génération de documents PDF professionnels</td>
                    <td>Exécution du contrat (Art. 6.1.b)</td>
                  </tr>
                  <tr>
                    <td>Stockage des informations bancaires (IBAN/BIC)</td>
                    <td>Exécution du contrat + Obligation légale (Art. 6.1.b / 6.1.c)</td>
                  </tr>
                  <tr>
                    <td>Sécurité, lutte contre la fraude</td>
                    <td>Intérêt légitime (Art. 6.1.f)</td>
                  </tr>
                  <tr>
                    <td>Amélioration des services</td>
                    <td>Intérêt légitime (Art. 6.1.f)</td>
                  </tr>
                  <tr>
                    <td>Envoi de communications (pannes, mise à jour)</td>
                    <td>Intérêt légitime / Consentement (Art. 6.1.a/f)</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <!-- 4 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Shield class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">4. Durée de conservation</h2>
          </div>
          <div class="section-body space-y-4">
            <ul class="data-list">
              <li><strong>Données de compte :</strong> conservées pendant toute la durée de votre abonnement actif, puis 3 ans après résiliation sauf obligation légale contraire.</li>
              <li><strong>Données de clients, rapports, devis, factures :</strong> conservées pendant la durée du contrat + 10 ans (obligations comptables françaises).</li>
              <li><strong>Photos d'intervention :</strong> conservées jusqu'à suppression manuelle ou clôture du compte.</li>
              <li><strong>Données bancaires (IBAN/BIC) :</strong> conservées pendant la durée du contrat, puis 5 ans (preuve comptable).</li>
              <li><strong>Logs techniques :</strong> conservés 12 mois maximum.</li>
            </ul>
          </div>
        </section>

        <!-- 5 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Lock class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">5. Sécurité des données</h2>
          </div>
          <div class="section-body space-y-4">
            <p>Nous mettons en œuvre des mesures techniques et organisationnelles appropriées :</p>
            <ul class="data-list">
              <li>Chiffrement TLS/HTTPS sur toutes les communications entre le navigateur et nos serveurs</li>
              <li>Mots de passe hachés avec <strong>bcrypt</strong> (irréversible, aucun accès en clair)</li>
              <li>Authentification par <strong>tokens JWT</strong> à durée limitée</li>
              <li>Isolation stricte des données : chaque utilisateur n'accède qu'à ses propres données</li>
              <li>Accès administrateur restreint aux utilisateurs disposant du rôle ADMIN</li>
              <li>Hébergement sur des infrastructures sécurisées en UE</li>
            </ul>
          </div>
        </section>

        <!-- 6 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Eye class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">6. Partage et transfert des données</h2>
          </div>
          <div class="section-body space-y-4">
            <p>Vos données ne sont <strong>jamais vendues</strong> à des tiers. Elles peuvent être partagées avec :</p>
            <ul class="data-list">
              <li><strong>Google LLC</strong> : dans le cadre de l'authentification OAuth Google (uniquement votre nom, prénom et e-mail Google). Voir la <a href="https://policies.google.com/privacy" target="_blank" class="text-primary hover:underline">politique de confidentialité Google</a>.</li>
              <li><strong>Prestataires d'hébergement</strong> : serveurs hébergés dans l'Union Européenne, soumis aux garanties RGPD.</li>
              <li><strong>Autorités légales</strong> : uniquement sur réquisition judiciaire.</li>
            </ul>
            <p>Aucun transfert de données hors UE n'est effectué, à l'exception du service Google OAuth qui dispose des garanties adéquates (clauses contractuelles types).</p>
          </div>
        </section>

        <!-- 7 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Shield class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">7. Vos droits (RGPD)</h2>
          </div>
          <div class="section-body">
            <p class="mb-4">Conformément au RGPD, vous disposez des droits suivants sur vos données personnelles :</p>
            <div class="rights-grid">
              <div class="right-card">
                <div class="right-title">Droit d'accès</div>
                <p>Obtenir une copie de toutes les données que nous détenons sur vous.</p>
              </div>
              <div class="right-card">
                <div class="right-title">Droit de rectification</div>
                <p>Corriger des données inexactes ou incomplètes directement depuis votre espace.</p>
              </div>
              <div class="right-card">
                <div class="right-title">Droit à l'effacement</div>
                <p>Demander la suppression de votre compte et de toutes vos données (« droit à l'oubli »).</p>
              </div>
              <div class="right-card">
                <div class="right-title">Droit à la portabilité</div>
                <p>Recevoir vos données dans un format structuré et lisible par machine.</p>
              </div>
              <div class="right-card">
                <div class="right-title">Droit d'opposition</div>
                <p>Vous opposer à certains traitements fondés sur l'intérêt légitime.</p>
              </div>
              <div class="right-card">
                <div class="right-title">Droit de limitation</div>
                <p>Demander la suspension temporaire d'un traitement.</p>
              </div>
            </div>
            <div class="info-box mt-6">
              <p>Pour exercer vos droits, contactez-nous à : <a href="mailto:pinhasbent@gmail.com" class="text-primary hover:underline font-medium">pinhasbent@gmail.com</a>. Nous répondrons dans un délai maximum de <strong>30 jours</strong>. Vous avez également le droit d'introduire une réclamation auprès de la <strong>CNIL</strong> (<a href="https://www.cnil.fr" target="_blank" class="text-primary hover:underline">www.cnil.fr</a>).</p>
            </div>
          </div>
        </section>

        <!-- 8 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Database class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">8. Cookies et stockage local</h2>
          </div>
          <div class="section-body space-y-4">
            <p>Ventura utilise le <strong>stockage local du navigateur (localStorage)</strong>, et non des cookies de tracking, pour :</p>
            <ul class="data-list">
              <li>Conserver votre token d'authentification JWT afin de maintenir votre session active</li>
            </ul>
            <p>Aucun cookie publicitaire ou de traçage tiers n'est déposé sur votre navigateur. Si nous intégrons à l'avenir des outils d'analyse, un bandeau de consentement conforme à la réglementation CNIL sera mis en place.</p>
          </div>
        </section>

        <!-- 9 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Mail class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">9. Modifications de cette politique</h2>
          </div>
          <div class="section-body">
            <p>Nous pouvons mettre à jour cette politique de confidentialité. En cas de modification substantielle, vous serez informé par e-mail ou via une notification dans l'application au moins 30 jours avant l'entrée en vigueur des changements. La date de dernière mise à jour est toujours visible en haut de cette page.</p>
          </div>
        </section>

        <!-- 10 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Mail class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">10. Contact</h2>
          </div>
          <div class="section-body">
            <div class="info-box">
              <p>Pour toute question relative à cette politique ou à vos données personnelles :<br />
              📧 <a href="mailto:privacy@ventura.app" class="text-primary hover:underline font-medium">privacy@ventura.app</a><br />
              📍 Ventura SAS, Paris, France
              </p>
            </div>
          </div>
        </section>

      </div>

      <!-- Footer nav -->
      <div class="mt-16 pt-8 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
        <p>© {{ new Date().getFullYear() }} Ventura. Tous droits réservés.</p>
        <div class="flex items-center gap-6">
          <router-link to="/legal/terms" class="hover:text-primary transition-colors">Conditions d'utilisation</router-link>
          <router-link to="/" class="hover:text-primary transition-colors">Retour à l'accueil</router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.legal-section {
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border);
}
.legal-section:last-child {
  border-bottom: none;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1.25rem;
}

.section-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: hsl(var(--primary) / 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--foreground);
}

.section-body {
  color: var(--muted-foreground);
  line-height: 1.75;
  font-size: 0.95rem;
}

.section-body p {
  margin-bottom: 0.75rem;
}

.section-body strong {
  color: var(--foreground);
}

.section-body a {
  color: var(--primary);
}

.info-box {
  background: hsl(var(--primary) / 0.05);
  border: 1px solid hsl(var(--primary) / 0.15);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  font-size: 0.9rem;
  color: var(--foreground);
}

.data-category {
  background: var(--muted);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
}

.data-category-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--foreground);
  margin-bottom: 0.75rem;
}

.data-list {
  list-style: none;
  padding: 0;
  margin: 0 0 0.5rem 0;
}

.data-list li {
  display: flex;
  gap: 8px;
  padding: 4px 0;
  color: var(--muted-foreground);
  font-size: 0.9rem;
}

.data-list li::before {
  content: '→';
  color: var(--primary);
  flex-shrink: 0;
  font-weight: bold;
}

.data-note {
  margin-top: 0.75rem;
  padding: 0.75rem 1rem;
  background: hsl(38 92% 50% / 0.1);
  border: 1px solid hsl(38 92% 50% / 0.25);
  border-radius: 8px;
  font-size: 0.85rem;
  color: var(--foreground) !important;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid var(--border);
}

.legal-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.legal-table th {
  background: var(--muted);
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 700;
  color: var(--foreground);
  border-bottom: 1px solid var(--border);
}

.legal-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
  color: var(--muted-foreground);
  vertical-align: top;
}

.legal-table tr:last-child td {
  border-bottom: none;
}

.legal-table tr:nth-child(even) td {
  background: hsl(var(--muted) / 0.4);
}

.rights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.right-card {
  background: var(--muted);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  font-size: 0.875rem;
  color: var(--muted-foreground);
}

.right-title {
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.375rem;
  font-size: 0.9rem;
}
</style>
