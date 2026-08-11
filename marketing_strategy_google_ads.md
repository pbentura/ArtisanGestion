# Stratégie d'Acquisition Google Ads : ArtisanGestion

> [!NOTE]
> Cette stratégie a été élaborée après une analyse approfondie du code source de votre SaaS (Web & Mobile), en extrayant vos véritables avantages concurrentiels pour maximiser le ROI de vos campagnes publicitaires.

---

## 1. Analyse des Forces de l'Application (Vos USPs)

Après analyse du code (`NouveauDevis.vue`, `ai.py`, `Pricing.vue`, etc.), voici les **Unique Selling Propositions** (Arguments Uniques de Vente) qu'il faut absolument mettre en avant dans vos publicités :

1.  **L'IA Anti-Hallucination pour les Rapports (`ai.py`)** : C'est votre "Killer Feature". Les artisans détestent faire de la paperasse. Votre intégration Mistral AI avec ses directives strictes permet de générer des rapports parfaits, courts ou longs, juste à partir d'une brève description.
2.  **Signature Tactile sur Chantier (`signatureCanvas`)** : Le client signe directement sur le smartphone de l'artisan. C'est un argument de vente majeur pour la version mobile.
3.  **L'Expérience Mobile First (`MobileLandingPage.vue`)** : Beaucoup d'artisans n'ont pas d'ordinateur de bureau. Votre SaaS est pensé pour le terrain.
4.  **Essai Gratuit de 14 Jours & Sans Engagement** : Abaisse la barrière à l'entrée et favorise l'inscription impulsive.
5.  **Gestion d'Équipe & Relances Automatiques (Plan Équipe)** : Répond à la douleur critique des retards de paiement (impayés) et de la collaboration.

---

## 2. Structure de la Campagne Google Ads

> [!WARNING]
> Ne créez **jamais** une seule campagne "fourre-tout". Vous allez gaspiller votre budget. Segmentez vos campagnes par "Intention" (Pain point).

### Campagne 1 : Le Gain de Temps (Cible : Indépendants)
- **Objectif** : Vendre la création rapide de devis/factures et la signature sur mobile.
- **Mots-clés (Ciblage Exact et Expression)** : 
  - `"logiciel devis artisan"`
  - `"application facturation batiment"`
  - `"faire devis sur chantier"`
  - `"application devis mobile"`
- **Annonce Type** :
  - **Titre 1** : Logiciel Devis & Facture Artisan
  - **Titre 2** : Faites signer sur le chantier
  - **Description** : Éditez vos devis en 2 min depuis votre mobile. Signature tactile intégrée. Essai gratuit 14j.

### Campagne 2 : L'Intelligence Artificielle (Cible : Techniciens, Dépannage)
- **Objectif** : Promouvoir la génération de rapports d'intervention par l'IA.
- **Mots-clés** :
  - `"logiciel rapport d'intervention"`
  - `"application fiche d'intervention"`
  - `"rédiger compte rendu chantier"`
- **Annonce Type** :
  - **Titre 1** : L'IA rédige vos rapports 
  - **Titre 2** : Fini la paperasse le soir
  - **Description** : Dictez l'intervention, notre IA rédige un rapport professionnel parfait. Testez gratuitement !

### Campagne 3 : La Chasse aux Impayés (Cible : Petites Équipes / PME)
- **Objectif** : Vendre le plan "Équipe" à 39€ via la fonctionnalité de relance.
- **Mots-clés** :
  - `"logiciel relance client impayé"`
  - `"automatiser relance facture"`
  - `"logiciel gestion PME batiment"`
- **Annonce Type** :
  - **Titre 1** : Ne laissez plus traîner vos factures
  - **Titre 2** : Relances automatiques intégrées
  - **Description** : Améliorez votre trésorerie. Notre logiciel relance vos clients automatiquement. Sans engagement.

---

## 3. Optimisation du Tunnel de Conversion (À appliquer à la lettre)

> [!IMPORTANT]
> Avoir de bonnes publicités ne sert à rien si la page d'atterrissage (Landing Page) ne convertit pas. Voici comment configurer votre entonnoir.

1.  **Lien de redirection (URL Finale)** : Ne renvoyez pas sur la page d'accueil générique. Si la pub parle d'IA, renvoyez vers une section de votre site (ou une landing page dédiée) qui explique l'IA (`/features/ia-rapports`).
2.  **Appel à l'Action (CTA)** : Le bouton de votre page d'accueil doit être **exclusivement** centré sur l'essai : "Démarrer mon essai de 14 jours".
3.  **Le Suivi des Conversions (Pixel)** : Configurez l'action de conversion Google Ads sur l'événement : **"Création de compte réussie"** (lorsque le formulaire de `AuthPage.vue` renvoie un succès). L'algorithme de Google apprendra ainsi quel type de profil s'inscrit le plus.

---

## 4. Stratégie de Budget et d'Enchères (Pour commencer)

*   **Budget Quotidien** : Commencez avec 15€ à 20€ par jour (soit ~450-600€/mois). C'est suffisant pour obtenir de la data pertinente sans se ruiner.
*   **Stratégie d'enchères (Semaine 1-2)** : *Maximiser les clics*. L'objectif est d'amener du trafic pour voir quels mots-clés cliquent le plus.
*   **Stratégie d'enchères (Semaine 3+)** : Passez en *Maximiser les conversions* (ou CPA Cible) dès que vous avez enregistré au moins 15 inscriptions gratuites. Google cherchera alors uniquement les profils susceptibles de s'inscrire.
*   **Mots-clés à exclure (Dès le jour 1)** : Ajoutez ces termes en exclusion pour ne pas payer pour des curieux : `gratuit`, `crack`, `excel`, `word`, `modele`, `etudiant`, `stage`.

---

## 5. Le Plan d'Action "Semaine 1"

1.  [ ] **Installer le Tag Google (gtag.js)** dans le `<head>` de votre frontend (ex: `index.html`).
2.  [ ] **Configurer l'événement de conversion** sur le clic ou la validation du formulaire de création de compte.
3.  [ ] **Créer la Campagne 1 (Gain de Temps)** avec 3 variantes d'annonces.
4.  [ ] **Activer l'extension "Liens annexes"** dans Google Ads pour afficher vos tarifs (Indépendant 19€ / Équipe 39€) directement sous l'annonce.
5.  [ ] **Lancer la campagne** et vérifier tous les jours les "Termes de recherche" (ce que les gens tapent vraiment) pour exclure les requêtes non pertinentes.
