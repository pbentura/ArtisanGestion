# ArtisanGestion — Chemin vers 10 000 € de MRR

> Document de travail. Complète `marketing_strategy_google_ads.md`.
> Dernière mise à jour : 7 septembre 2026.

---

## 1. Le calcul réel (avant de parler tactique)

Ton raisonnement « 3M d'artisans, il y aura bien 500 gars » est le bon ordre de grandeur
en **volume de clients**, mais il oublie la variable qui tue la plupart des SaaS TPE : le **churn**.

| Hypothèse | Valeur |
|---|---|
| Mix réaliste 19 € / 39 € | ~70/30 → **ARPU ≈ 25 €** |
| Clients payants nécessaires | **400** |
| Churn mensuel SaaS TPE (typique) | 5 à 8 % |
| Clients perdus /mois à 400 clients | **20 à 32** |

**Ce que ça veut dire concrètement.** À 400 clients, tu dois recruter ~25 clients par mois
*juste pour rester à 10k*. La question n'est donc pas « comment trouver 400 clients »,
c'est « **comment installer une machine qui produit 30 à 50 nouveaux clients par mois, tous les mois** ».

Un canal one-shot (une campagne de cold email) ne répond pas à cette question.
Un canal composé (SEO, produit, prescripteurs) oui.

**Timeline honnête : 18 à 30 mois.** Quiconque te promet 6 mois te vend quelque chose.

### Le vrai levier n°1 : réduire le churn

Passer de 8 % à 4 % de churn **double ta LTV** et divise par deux le nombre de clients à
acquérir pour tenir 10k. C'est moins sexy que le growth hacking, c'est 10x plus rentable.

- LTV à 19 € / churn 8 % = **237 €**
- LTV à 19 € / churn 4 % = **475 €**

Instrumente ça avant tout le reste : à quel moment un artisan arrête-t-il d'ouvrir l'app ?
S'il n'a pas créé son **3e devis** dans les 14 jours d'essai, il ne convertira pas. C'est ta
métrique d'activation, et c'est là qu'il faut mettre l'onboarding (import du logo, RIB, un
premier devis pré-rempli).

---

## 2. La fenêtre à ne pas rater : la facturation électronique

C'est de loin l'information la plus importante de ce document.

| Échéance | Qui | Quoi |
|---|---|---|
| **1er sept. 2026** (fait, il y a 6 jours) | **Toutes** les entreprises assujetties à la TVA | Obligation de **recevoir** des factures électroniques |
| **1er sept. 2026** | Grandes entreprises + ETI | Obligation d'**émettre** |
| **1er sept. 2027** | **TPE et PME — tes clients** | Obligation d'**émettre** |

Les factures doivent transiter par le **Portail Public de Facturation (PPF)** ou par une
**Plateforme Agréée (PA)** — terminologie officielle qui a remplacé « PDP ».

**Pourquoi c'est ton canal n°1 :** tu as exactement **12 mois** pendant lesquels 3 millions
d'artisans français vont, un par un, se rendre compte qu'ils sont obligés de changer d'outil.
Ils ne cherchent pas « un logiciel de devis » (besoin mou, ils s'en sortent avec Word).
Ils vont chercher « **comment faire mes factures électroniques en 2027** » (besoin dur, deadline légale, sanction à la clé).

Tu as déjà `FacturationElectroniqueLanding.vue`. Ce n'est pas *une* landing parmi d'autres,
c'est **la porte d'entrée principale du produit pour les 12 prochains mois**.

**À faire, dans cet ordre :**

1. **Trancher la question PA.** Es-tu Plateforme Agréée, ou passes-tu par une PA partenaire
   (Chorus Pro / un opérateur) ? Tu dois pouvoir répondre en une phrase sur ta page d'accueil.
   Sans réponse claire, tu perds face à Tolteck/Obat/Henrri qui l'afficheront.
   → Vérifie la liste officielle sur `impots.gouv.fr`, et le calendrier (il a déjà été décalé deux fois).
2. **Un compte à rebours visible** sur la landing : « Plus que X mois avant l'obligation ».
3. **Un contenu qui capte la panique** : « Facture électronique 2027 : le guide de l'artisan »,
   « Suis-je concerné ? » (mini-quiz en 3 questions → email → essai).
4. **Repositionner le message** : tu n'es plus « un logiciel de devis », tu es
   « **le moyen le plus simple pour un artisan d'être en règle en 2027** ».

---

## 3. Les canaux, classés par ROI réel sur cette niche

### 🥇 1. Le produit comme canal : un outil gratuit sans inscription

**C'est ce qui manque à ton acquisition.** Un artisan ne s'inscrit pas à un essai de 14 jours
pour « voir ». Il a un devis à sortir ce soir à 21h.

**Construis un générateur de devis gratuit, en ligne, sans compte.**
Il remplit → il voit son devis en PDF → **pour le télécharger ou l'envoyer, il crée un compte**.

Tu as déjà tout le moteur (`NouveauDevis.vue`, la génération PDF). C'est quelques jours de
travail pour la boucle d'acquisition la plus rentable que tu auras jamais :
coût marginal nul, ça alimente le SEO, et ça convertit 10 à 20x mieux qu'une page de pricing.

C'est exactement comme ça que Tolteck et Obat ont démarré.

**Variantes à décliner** (une page par métier, énorme volume de recherche) :
`modèle de devis plomberie`, `modèle devis peinture`, `modèle devis électricité`,
`modèle facture auto-entrepreneur bâtiment`, `calculateur de TVA travaux 10 % / 5,5 %`.

### 🥈 2. SEO — le seul canal qui compose

Tu as commencé (`54023e2 début SEO`, `5276d6d ajout articles blog`). Continue, c'est le bon pari.

Trois familles de requêtes, par ordre d'intention :

| Famille | Exemples | Intention |
|---|---|---|
| **Réglementaire** (urgent) | `facture électronique artisan 2027`, `plateforme agréée obligatoire`, `mentions obligatoires devis bâtiment` | Très chaude |
| **Outil** (comparaison) | `logiciel devis facture artisan`, `alternative Tolteck`, `logiciel devis gratuit bâtiment` | Chaude |
| **Modèle** (volume) | `modèle devis plombier`, `exemple facture artisan`, `devis travaux word` | Tiède → capte par l'outil gratuit |

**Le format qui marche sur cette cible :** pas des articles de blog génériques. Des pages
outil + des réponses ultra-concrètes avec un modèle téléchargeable. L'artisan ne lit pas, il télécharge.

### 🥉 3. Prescripteurs — le canal le plus sous-exploité

Un **expert-comptable** a entre 100 et 300 clients TPE, et il est **la personne qui décide**
de l'outil de facturation de ses clients. Surtout maintenant, avec la réforme : les cabinets
sont en train d'équiper leurs clients en masse.

**10 cabinets partenaires = accès à ~2 000 artisans, avec une recommandation de confiance.**
Le taux de conversion est sans commune mesure avec du cold email.

Ce qu'il leur faut (et que tu peux construire) :
- Un **accès multi-clients** gratuit pour le cabinet (voir les factures de tous ses artisans)
- Un **export compatible** avec leur logiciel de production
- Une **commission récurrente** (20 % à vie, ou 3 mois offerts par client apporté)

Autres prescripteurs, dans l'ordre : **CMA** (chambres de métiers, elles font des permanences
« numérique »), **CAPEB** et **FFB** départementales, **grossistes** (Rexel, Cedeo, Point.P —
ils ont les mailing lists de tous les artisans du département), **centres de formation** (CFA du bâtiment).

C'est du travail de terrain, pas de l'automatisation. C'est aussi pour ça que personne ne le fait.

### 4. Facebook — tu n'as pas de compte, c'est une erreur à corriger cette semaine

Tu dis ne pas avoir de compte Facebook. **C'est là que sont les artisans français.**
Des groupes comme « Artisans du bâtiment — entraide », « Plombiers chauffagistes de France »,
« Auto-entrepreneurs du bâtiment » rassemblent des dizaines de milliers de membres qui
posent, tous les jours, exactement les questions auxquelles ton produit répond.

**Créer un compte : 15 minutes. Coût : 0 €.**

La règle : **tu ne postes jamais de pub**. Tu réponds aux questions paperasse / devis /
facturation électronique, en donnant la vraie réponse. Ton nom apparaît. Au bout de quelques
semaines, on te demande « tu utilises quoi, toi ? ».

Même logique sur **TikTok / YouTube Shorts** : le contenu artisan y est énorme en France
(« la mention obligatoire que 90 % des artisans oublient sur leurs devis » = 30 secondes, filmé au téléphone).

### 5. Parrainage — les artisans se parlent sur les chantiers

1 mois offert pour le parrain **et** le filleul. À intégrer directement dans l'app, visible
après le 5e devis créé (donc quand l'artisan est content). Coût d'acquisition : ~19 €.

### 6. Google Ads — oui, mais uniquement sur le plan Équipe

Faisons le calcul avec les hypothèses de ton doc Ads :

- CPC sur `logiciel devis artisan` : **2 à 4 €**
- Conversion landing → essai : **5 à 10 %**
- Conversion essai → payant : **15 à 25 %**
- → **CAC ≈ 150 à 250 €**

Face à une LTV de **237 €** sur le plan 19 €, c'est **à perte ou à l'équilibre**.
Face à une LTV de **~490 €** sur le plan 39 €, c'est rentable.

**Conclusion : garde Ads, mais sur les mots-clés « équipe / impayés / multi-utilisateurs »
et sur les requêtes réglementaires**, pas sur le générique « logiciel devis ».
Et démarre à 15 €/jour comme prévu, pas plus, tant que tu n'as pas mesuré ton essai→payant réel.

### 7. Cold email — le canal que tu demandes

Voir section 4 ci-dessous. **Utile, mais ne peut pas être ta stratégie principale.**

---

## 4. Cold email : ce que ça donne vraiment

### Le funnel, avec des chiffres réalistes (B2B France, données scrapées, secteur artisanat)

| Étape | Taux | Sur 1 000 emails |
|---|---|---|
| Délivrabilité (boîte de réception) | 80–90 % | 850 |
| Taux de réponse | 1–3 % | 10–25 |
| Réponses positives | 20–30 % des réponses | 3–7 |
| → essai gratuit | | 3–7 |
| → **client payant** | 30–50 % des essais | **1 à 3** |

**Donc : ~1 à 3 clients pour 1 000 emails envoyés.**

Pour atteindre 400 clients par ce seul canal, il faudrait **150 000 à 400 000 emails**.
À 30–40 emails/jour/boîte (au-delà, tu grilles ton domaine), c'est **10 à 20 boîtes pendant 2 à 3 ans**.

Coût : ~150–300 €/mois d'infra (domaines secondaires + boîtes + Instantly/Smartlead).
→ **CAC ≈ 50 à 120 €**. C'est rentable, c'est juste **lent et plafonné**.

**Verdict : monte-le, mais comme canal n°3.** Sa vraie valeur pour toi maintenant n'est pas
le volume — c'est **d'aller parler à 100 artisans en 3 semaines** pour comprendre leurs mots,
leurs objections, et ce qui les fait payer. Cette information vaut plus que les 2 clients gagnés.

### Le cadre légal (à ne pas prendre à la légère)

Le B2B est **beaucoup plus permissif** que le B2C en France, mais pas libre :

✅ **Pas de consentement préalable requis** en B2B — un régime d'**opposition (opt-out)** suffit, **à quatre conditions** :
1. Le message porte sur l'**activité professionnelle** de la personne contactée (c'est ton cas : un logiciel de gestion pour artisan)
2. La donnée a été **collectée loyalement** (base SIRENE open data + coordonnées publiées sur le site pro : OK)
3. L'**identité de l'expéditeur** est claire (nom, société, adresse)
4. Un moyen **simple et gratuit de désinscription** figure dans **chaque** message

⚠️ **Obligations supplémentaires, souvent oubliées :**
- **Information de la personne** : la donnée étant collectée indirectement (art. 14 RGPD), tu dois l'informer — le **premier email** peut porter cette mention, avec un lien vers ta politique de confidentialité.
- **Traçabilité de la source** : tu dois pouvoir prouver l'origine de chaque contact. → Le workflow enregistre le champ `source` et `collecte_le` pour ça.
- **Opt-out respecté sous 30 jours max** (vise **48 h**). Le droit d'opposition est absolu, sans justification.
- **Privilégie les adresses génériques** (`contact@`, `devis@`) aux adresses nominatives (`jean.dupont@`) : moins intrusif, et régime juridique plus confortable. → Le workflow les priorise automatiquement.

Ordre de grandeur des sanctions CNIL en prospection : Cdiscount 525 000 € (2024), Free 300 000 € (2023), Brico Privé 50 000 €.

❌ **À ne pas faire :** scraper Pages Jaunes (interdit par leurs CGU et déjà sanctionné),
acheter des fichiers dont tu ne peux pas tracer l'origine, ignorer une demande de désinscription.

📞 **Note sur le téléphone :** Bloctel ne concerne **que les particuliers**. Le démarchage
téléphonique **B2B est légal**. Or les artisans **répondent au téléphone** (c'est leur métier
de prendre des appels de clients) et lisent peu leurs mails. **20 appels/jour convertiront
probablement mieux que 500 emails.** À tester en priorité — et le workflow récupère déjà le
numéro via Google Places.

### Les séquences

Voir `sequences-cold-email.md`.

---

## 5. Plan à 90 jours

### Mois 1 — Poser les fondations

- [ ] **Instrumenter** : événement d'activation (« 3e devis créé »), taux essai→payant, churn mensuel. Sans ça tu pilotes à l'aveugle.
- [ ] **Trancher la question Plateforme Agréée** et l'afficher clairement sur le site.
- [ ] **Compte à rebours + guide « facture électronique 2027 »** sur la landing dédiée.
- [ ] **Créer un compte Facebook**, rejoindre 10 groupes d'artisans, ne rien vendre, juste répondre.
- [ ] **Infra cold email** : 2 domaines secondaires (`getartisangestion.fr`…), 4 boîtes, SPF/DKIM/DMARC, **3 semaines de warm-up avant le premier envoi**.
- [ ] Lancer le workflow n8n sur 3 départements → viser ~500 prospects qualifiés.

### Mois 2 — Tester et écouter

- [ ] **Cold email : 40 envois/jour**, 2 séquences A/B. Objectif : **20 conversations**, pas 20 clients.
- [ ] **Cold call : 20 appels/jour pendant 2 semaines.** C'est inconfortable, c'est le plus instructif.
- [ ] Publier **8 pages SEO** : 4 réglementaires + 4 « modèle de devis <métier> ».
- [ ] Démarcher **10 experts-comptables** en local (physiquement, pas par mail).
- [ ] Google Ads : campagne « Chasse aux impayés » (plan 39 €) uniquement, 15 €/jour.

### Mois 3 — Doubler sur ce qui marche

- [ ] **Livrer le générateur de devis gratuit sans inscription.** Priorité produit n°1.
- [ ] Mettre le **parrainage** dans l'app.
- [ ] Couper les canaux à CAC > LTV. Réinvestir sur les 2 meilleurs.
- [ ] Attaquer le **churn** avec ce que les 100 conversations t'ont appris.

**Objectif réaliste à 90 jours : 30 à 60 clients payants (600–1 500 € de MRR)** et, surtout,
la certitude de savoir **quel canal scaler**.

---

## 6. Le tableau de bord

Cinq chiffres, une fois par semaine. Si tu n'en suis qu'un, suis le troisième.

| Métrique | Cible |
|---|---|
| Nouveaux essais / semaine | ↗ |
| **Taux d'activation** (3e devis créé pendant l'essai) | **> 40 %** |
| **Churn mensuel** | **< 5 %** |
| Essai → payant | > 20 % |
| CAC par canal | < LTV / 3 |

---

## Sources

- [Calendrier facturation électronique 2026-2027 — Cegid](https://www.cegid.com/fr/facture-electronique-obligatoire/calendrier-facture-electronique/)
- [Calendrier facture électronique — Pennylane](https://www.pennylane.com/fr/fiches-pratiques/facture-electronique/facturation-electronique-dates-cles-et-calendrier)
- [Facturation électronique : calendrier officiel 2026-2027 — AEON Systems](https://aeon-systems.fr/blog/calendrier-facturation-electronique-2026-2027/)
- [CNIL et prospection B2B : ce qui est légal en 2026](https://fichierb2b.fr/articles/cnil-prospection-b2b-legal-2026/)
- [B2B cold email France : guide RGPD + CNIL — Overloop](https://overloop.com/fr/blog/b2b-cold-email-france-cnil-rgpd)
- [API Recherche d'Entreprises — data.gouv.fr](https://www.data.gouv.fr/dataservices/api-recherche-dentreprises)
