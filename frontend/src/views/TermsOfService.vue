<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowLeft, FileText, CheckCircle2, AlertTriangle, Scale, Ban, RefreshCw, Mail } from 'lucide-vue-next'
const router = useRouter()
const lastUpdated = '7 avril 2026'
const effectiveDate = '7 avril 2026'
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
            <Scale class="w-7 h-7 text-primary" />
          </div>
          <div>
            <h1 class="text-3xl sm:text-4xl font-bold text-foreground">Conditions Générales d'Utilisation</h1>
            <p class="text-muted-foreground text-sm mt-1">Dernière mise à jour : {{ lastUpdated }} · En vigueur depuis le {{ effectiveDate }}</p>
          </div>
        </div>
        <div class="highlight-box">
          <AlertTriangle class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <p class="text-sm text-foreground leading-relaxed">
            En créant un compte ou en utilisant la plateforme Ventura, vous acceptez sans réserve les présentes Conditions Générales d'Utilisation. Veuillez les lire attentivement avant toute utilisation du service.
          </p>
        </div>
      </div>
    </div>

    <!-- Content -->
    <main class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl py-12">
      <div class="space-y-12">

        <!-- 1 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><FileText class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">1. Présentation du service</h2>
          </div>
          <div class="section-body space-y-3">
            <p><strong>Ventura</strong> est une plateforme SaaS (Software as a Service) de gestion d'entreprise destinée aux artisans, indépendants et petites et moyennes entreprises (PME) établis principalement en France.</p>
            <p>La plateforme permet notamment :</p>
            <ul class="data-list">
              <li>La création et gestion de rapports d'intervention (avec photos, statut, génération de PDF)</li>
              <li>La gestion d'un fichier clients (nom, adresse, SIRET, coordonnées)</li>
              <li>La configuration de votre profil entreprise (informations légales, bancaires, comptables)</li>
              <li>La génération de documents professionnels (rapports, devis, factures)</li>
              <li>Le suivi de l'activité commerciale (chiffre d'affaires, objectif mensuel)</li>
            </ul>
            <p>L'éditeur du service est <strong>Ventura SAS</strong>, société par actions simplifiée, dont le siège est à Paris, France. Contact : <a href="mailto:pinhasbent@gmail.com" class="text-primary hover:underline">pinhasbent@gmail.com</a>.</p>
          </div>
        </section>

        <!-- 2 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><CheckCircle2 class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">2. Accès et inscription</h2>
          </div>
          <div class="section-body space-y-4">
            <h3 class="sub-title">2.1 Conditions d'accès</h3>
            <p>L'accès à Ventura est réservé aux personnes physiques ou morales :</p>
            <ul class="data-list">
              <li>Âgées d'au moins 18 ans ou disposant de la capacité juridique pour s'engager</li>
              <li>Exerçant une activité professionnelle (artisan, commerçant, prestataire de services, PME)</li>
              <li>Disposant d'un accès internet et d'un navigateur web compatible</li>
            </ul>

            <h3 class="sub-title">2.2 Création de compte</h3>
            <p>Vous pouvez créer un compte de deux manières :</p>
            <ul class="data-list">
              <li><strong>Inscription email/mot de passe :</strong> en fournissant votre nom, prénom, adresse e-mail et un mot de passe sécurisé (minimum 8 caractères).</li>
              <li><strong>Connexion via Google OAuth :</strong> en autorisant Ventura à accéder aux informations de base de votre compte Google (nom, prénom, e-mail).</li>
            </ul>
            <p>Vous êtes responsable de la confidentialité de vos identifiants. Toute utilisation du service avec vos identifiants vous est imputable. En cas de compromission, vous devez nous prévenir immédiatement à <a href="mailto:security@ventura.app" class="text-primary hover:underline">security@ventura.app</a>.</p>

            <h3 class="sub-title">2.3 Onboarding entreprise</h3>
            <p>Après inscription, vous êtes invité à renseigner les informations de votre société (nom, SIRET, adresse, coordonnées bancaires, etc.). Ces données sont nécessaires à l'utilisation complète du service. L'accès au tableau de bord est conditionné à l'enregistrement d'une société.</p>
          </div>
        </section>

        <!-- 3 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Scale class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">3. Description des fonctionnalités</h2>
          </div>
          <div class="section-body">
            <div class="features-grid">
              <div class="feature-item">
                <div class="feature-name">Rapports d'intervention</div>
                <p>Création, édition, suivi de statut (en cours / terminée) et génération de rapports PDF. Possibilité d'attacher plusieurs photos par rapport.</p>
              </div>
              <div class="feature-item">
                <div class="feature-name">Gestion des clients</div>
                <p>Fichier clients complet avec coordonnées, adresse et numéro SIRET. Isolation des données par utilisateur.</p>
              </div>
              <div class="feature-item">
                <div class="feature-name">Profil entreprise</div>
                <p>Configuration complète : forme juridique, IBAN/BIC, TVA, RCS, logo, texte de pied de page sur les documents.</p>
              </div>
              <div class="feature-item">
                <div class="feature-name">Génération de PDF</div>
                <p>Export automatisé de documents à en-tête professionnels incluant les informations de l'entreprise, du client et du rapport.</p>
              </div>
              <div class="feature-item">
                <div class="feature-name">Tableau de bord</div>
                <p>Visualisation des indicateurs clés : chiffre d'affaires, nombre de rapports, clients actifs, objectif mensuel.</p>
              </div>
              <div class="feature-item">
                <div class="feature-name">Administration</div>
                <p>Les utilisateurs disposant du rôle ADMIN bénéficient d'un accès étendu à la gestion de l'ensemble des données de la plateforme.</p>
              </div>
            </div>
            <p class="mt-4 text-sm text-muted-foreground">Les fonctionnalités de devis et de facturation sont en cours de développement et seront disponibles prochainement.</p>
          </div>
        </section>

        <!-- 4 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><CheckCircle2 class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">4. Obligations de l'utilisateur</h2>
          </div>
          <div class="section-body space-y-4">
            <p>En utilisant Ventura, vous vous engagez à :</p>
            <ul class="data-list">
              <li>Fournir des informations exactes, complètes et à jour lors de votre inscription et de l'utilisation du service</li>
              <li>N'utiliser le service qu'à des fins professionnelles légales et légitimes</li>
              <li>Ne pas tenter de contourner les mécanismes de sécurité ou d'authentification</li>
              <li>Ne pas accéder aux données d'autres utilisateurs sans autorisation</li>
              <li>Respecter la législation applicable aux données de vos propres clients (RGPD, Code civil)</li>
              <li>Conserver la confidentialité de vos identifiants de connexion</li>
              <li>Ne pas utiliser Ventura pour des activités frauduleuses, illégales ou contraires à l'ordre public</li>
              <li>Ne pas surcharger intentionnellement les infrastructures du service (attaques DDoS, scraping massif…)</li>
            </ul>
            <div class="warning-box">
              <AlertTriangle class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <p class="text-sm">En tant qu'utilisateur professionnel, vous êtes responsable de la licéité du traitement des données personnelles de vos propres clients. Ventura agit en tant que <strong>sous-traitant</strong> au sens du RGPD pour ces données.</p>
            </div>
          </div>
        </section>

        <!-- 5 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Ban class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">5. Utilisations interdites</h2>
          </div>
          <div class="section-body">
            <p>Il est strictement interdit d'utiliser Ventura pour :</p>
            <ul class="data-list">
              <li>La collecte de données personnelles à des fins non liées à l'exercice de votre activité professionnelle déclarée</li>
              <li>La transmission de contenus illicites, diffamatoires, obscènes ou portant atteinte aux droits de tiers</li>
              <li>Toute tentative d'ingénierie inverse, de décompilation ou d'extraction du code source de la plateforme</li>
              <li>La revente, la sous-licence ou la mise à disposition du service à des tiers non autorisés</li>
              <li>L'utilisation d'outils automatisés (bots, scrapers) pour interagir avec l'API sans autorisation écrite préalable</li>
              <li>Toute action visant à compromettre la disponibilité, l'intégrité ou la confidentialité des données d'autres utilisateurs</li>
            </ul>
            <p class="mt-3">Le non-respect de ces interdictions entraîne la suspension immédiate du compte, sans préavis ni remboursement, et peut donner lieu à des poursuites judiciaires.</p>
          </div>
        </section>

        <!-- 6 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Scale class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">6. Propriété intellectuelle</h2>
          </div>
          <div class="section-body space-y-3">
            <p>L'ensemble des éléments composant la plateforme Ventura (code source, design, interface, logos, marques, documentation) est la propriété exclusive de Ventura SAS et est protégé par les lois françaises et européennes relatives à la propriété intellectuelle.</p>
            <p>L'utilisation de la plateforme ne vous confère aucun droit de propriété sur ces éléments. Toute reproduction, représentation, modification ou exploitation non autorisée est formellement interdite.</p>
            <p><strong>Vos données restent les vôtres.</strong> Ventura revendique aucun droit de propriété sur les données que vous créez (rapports, clients, documents). Vous nous accordez uniquement une licence limitée pour héberger, traiter et restituer ces données dans le cadre du service.</p>
          </div>
        </section>

        <!-- 7 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><RefreshCw class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">7. Disponibilité et niveaux de service</h2>
          </div>
          <div class="section-body space-y-3">
            <p>Ventura s'efforce de maintenir la plateforme accessible <strong>24h/24 et 7j/7</strong>. Cependant, des interruptions peuvent survenir pour :</p>
            <ul class="data-list">
              <li>Maintenances programmées (annoncées à l'avance, de préférence en dehors des heures ouvrées)</li>
              <li>Mises à jour, correctifs de sécurité ou évolutions fonctionnelles</li>
              <li>Incidents techniques indépendants de notre volonté (pannes réseau, force majeure)</li>
            </ul>
            <p>Ventura SAS ne saurait être tenu responsable de préjudices résultant d'une interruption de service temporaire. Nous nous engageons à communiquer sur tout incident majeur via l'adresse e-mail de votre compte.</p>
          </div>
        </section>

        <!-- 8 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Scale class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">8. Responsabilité et garanties</h2>
          </div>
          <div class="section-body space-y-4">
            <h3 class="sub-title">8.1 Limitation de responsabilité</h3>
            <p>Dans les limites autorisées par la loi, Ventura SAS ne saurait être tenu responsable :</p>
            <ul class="data-list">
              <li>Des pertes de données résultant d'une utilisation incorrecte du service par l'utilisateur</li>
              <li>Des dommages indirects, pertes de chiffre d'affaires, manque à gagner ou préjudices commerciaux</li>
              <li>Des conséquences d'une utilisation non conforme aux présentes CGU</li>
              <li>Des actions ou omissions de services tiers (notamment Google OAuth, hébergeurs)</li>
            </ul>

            <h3 class="sub-title">8.2 Responsabilité de l'utilisateur</h3>
            <p>Vous êtes seul responsable :</p>
            <ul class="data-list">
              <li>De l'exactitude des informations saisies (données entreprise, clients, montants financiers)</li>
              <li>De la conformité fiscale et comptable de vos documents (devis, factures, rapports)</li>
              <li>De la licéité du traitement des données de vos propres clients</li>
              <li>De la sauvegarde de vos propres données (export PDF, archives)</li>
            </ul>

            <div class="warning-box">
              <AlertTriangle class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <p class="text-sm">Ventura n'est pas un logiciel de comptabilité certifié. Les documents générés (devis, factures) doivent être vérifiés par un expert-comptable pour garantir leur conformité fiscale et légale.</p>
            </div>
          </div>
        </section>

        <!-- 9 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><RefreshCw class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">9. Tarifs et facturation</h2>
          </div>
          <div class="section-body space-y-3">
            <p>Ventura propose actuellement une période d'essai gratuite de <strong>14 jours</strong>, sans engagement et sans carte bancaire requise.</p>
            <p>Les conditions tarifaires détaillées (plans, prix, modalités de paiement) sont disponibles sur la page <router-link to="/#pricing" class="text-primary hover:underline">Tarifs</router-link> de la plateforme. En cas d'évolution tarifaire, vous serez notifié au moins <strong>30 jours</strong> à l'avance par e-mail.</p>
            <p>Vous pouvez résilier votre abonnement à tout moment depuis votre espace compte. La résiliation prend effet à la fin de la période en cours. Aucun remboursement au prorata n'est accordé pour les périodes déjà facturées, sauf erreur de notre part.</p>
          </div>
        </section>

        <!-- 10 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Ban class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">10. Suspension et résiliation</h2>
          </div>
          <div class="section-body space-y-4">
            <h3 class="sub-title">10.1 Résiliation par l'utilisateur</h3>
            <p>Vous pouvez supprimer votre compte à tout moment en contactant notre support à <a href="mailto:pinhasbent@gmail.com" class="text-primary hover:underline">pinhasbent@gmail.com</a>. La suppression entraîne l'effacement de toutes vos données dans les délais prévus par notre politique de confidentialité, sous réserve des obligations légales de conservation.</p>

            <h3 class="sub-title">10.2 Suspension par Ventura</h3>
            <p>Ventura SAS se réserve le droit de suspendre ou résilier votre compte, avec ou sans préavis selon la gravité, en cas de :</p>
            <ul class="data-list">
              <li>Violation des présentes CGU</li>
              <li>Non-paiement des sommes dues</li>
              <li>Activité frauduleuse ou illégale avérée</li>
              <li>Atteinte à la sécurité ou aux droits d'autres utilisateurs</li>
            </ul>
          </div>
        </section>

        <!-- 11 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><RefreshCw class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">11. Évolution des CGU</h2>
          </div>
          <div class="section-body space-y-3">
            <p>Ventura SAS se réserve le droit de modifier les présentes Conditions Générales d'Utilisation à tout moment. En cas de modification substantielle, vous serez informé par e-mail <strong>au moins 30 jours avant</strong> l'entrée en vigueur des nouvelles conditions.</p>
            <p>La poursuite de l'utilisation du service après cette date vaut acceptation des nouvelles conditions. Si vous refusez les nouvelles CGU, vous devez cesser d'utiliser le service et supprimer votre compte.</p>
          </div>
        </section>

        <!-- 12 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Scale class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">12. Droit applicable et juridiction</h2>
          </div>
          <div class="section-body space-y-3">
            <p>Les présentes CGU sont régies par le <strong>droit français</strong>. En cas de litige, les parties s'engagent à rechercher une solution amiable dans un délai de 30 jours.</p>
            <p>À défaut d'accord amiable, tout litige relatif à l'interprétation ou à l'exécution des présentes CGU sera soumis à la compétence exclusive des <strong>tribunaux compétents de Paris</strong>, nonobstant pluralité de défendeurs ou appel en garantie.</p>
            <p>En tant que consommateur professionnel, vous pouvez également recourir à la médiation via la plateforme européenne de résolution des litiges en ligne : <a href="https://ec.europa.eu/consumers/odr" target="_blank" class="text-primary hover:underline">ec.europa.eu/consumers/odr</a>.</p>
          </div>
        </section>

        <!-- 13 -->
        <section class="legal-section">
          <div class="section-header">
            <div class="section-icon"><Mail class="w-5 h-5 text-primary" /></div>
            <h2 class="section-title">13. Contact et support</h2>
          </div>
          <div class="section-body">
            <div class="info-box">
              <p>Pour toute question relative aux présentes CGU ou à l'utilisation du service :<br /><br />
              📧 Support général : <a href="mailto:pinhasbent@gmail.com" class="text-primary hover:underline font-medium">pinhasbent@gmail.com</a><br />
              🔒 Questions juridiques / RGPD : <a href="mailto:pinhasbent@gmail.com" class="text-primary hover:underline font-medium">pinhasbent@gmail.com</a><br />
<!--              🛡️ Signalement de sécurité : <a href="mailto:security@ventura.app" class="text-primary hover:underline font-medium">security@ventura.app</a><br />-->
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
          <router-link to="/legal/privacy" class="hover:text-primary transition-colors">Politique de confidentialité</router-link>
          <router-link to="/" class="hover:text-primary transition-colors">Retour à l'accueil</router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.highlight-box {
  display: flex;
  gap: 12px;
  background: hsl(38 92% 50% / 0.08);
  border: 1px solid hsl(38 92% 50% / 0.2);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  margin-top: 1rem;
}

.warning-box {
  display: flex;
  gap: 12px;
  background: hsl(38 92% 50% / 0.08);
  border: 1px solid hsl(38 92% 50% / 0.2);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  margin-top: 0.75rem;
}

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

.sub-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--foreground);
  margin-bottom: 0.5rem;
  margin-top: 1rem;
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

.data-list {
  list-style: none;
  padding: 0;
  margin: 0 0 0.75rem 0;
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

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.feature-item {
  background: var(--muted);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  font-size: 0.875rem;
  color: var(--muted-foreground);
}

.feature-name {
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.375rem;
  font-size: 0.9rem;
}
</style>
