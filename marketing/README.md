# marketing/

| Fichier | Contenu |
|---|---|
| [`strategie-acquisition-10k-mrr.md`](strategie-acquisition-10k-mrr.md) | Le plan complet : calcul du churn, fenêtre facture électronique 2027, canaux classés par ROI, plan 90 jours |
| [`sequences-cold-email.md`](sequences-cold-email.md) | Séquences d'emails + script téléphone + checklist de conformité |
| [`n8n-prospection-artisans.json`](n8n-prospection-artisans.json) | Workflow n8n de constitution de la base de prospects |
| [`../marketing_strategy_google_ads.md`](../marketing_strategy_google_ads.md) | Stratégie Google Ads (existant) |

---

## Workflow n8n — prospection artisans

Construit une base d'artisans du bâtiment qualifiée dans **Notion**, à partir de sources
**publiques et légales**, à **coût zéro** (aucune carte bancaire requise).

```
Branche A — collecte (7h, lun-ven)
  Déclencheur quotidien
    └─ Config ...................... codes NAF × départements × pages
       └─ API Recherche Entreprises  base SIRENE, open data, sans clé
          └─ Normaliser et filtrer . TPE 0-9 salariés, > 6 mois, métier du bâtiment
             └─ Dédoublonner (SIREN)  une fiche par entreprise, à vie
                └─ Préparer la fiche  variables de perso (prénom, accroche, métier…)
                   └─ Notion : créer la fiche ........ Statut = « À enrichir »

Branche B — enrichissement (8h, tous les jours, 100 fiches max)
  Déclencheur enrichissement
    └─ Notion : fiches à enrichir .. 100 pages avec Statut = « À enrichir »
       └─ Trouver le site web ...... Tavily (1 000 recherches/mois gratuites)
          └─ Extraire email et téléphone  pages contact / mentions légales du site
             └─ Qualifier le prospect  liste de suppression, concurrents → statut
                └─ Notion : mettre à jour la fiche  Email, Tél, Site, Statut
```

**Notion est la file d'attente** : toutes les entreprises du département sont dans la base dès
le premier passage (utilisables tout de suite pour du téléphone / courrier), puis l'enrichissement
avance de 100 fiches par jour. Statuts : `À enrichir` → `A contacter` (email trouvé) /
`Sans site` / `Sans email` / `Désinscrit` (liste de suppression), puis ton pipeline
commercial : `Contacté`, `Répondu`, `RDV`, `Client`, `Pas intéressé`.

### Installation

1. Dans n8n : **Workflows → Import from File** → `n8n-prospection-artisans.json`
2. **Credential Notion** : *Notion API* (intégration interne, clé `ntn_…`), à sélectionner sur
   les 3 nœuds Notion. La base cible est renseignée par son ID
   (`3d8515c2-a75a-817b-8492-e3e0fdccb04b`, base « Prospects ArtisanGestion »). L'intégration
   doit avoir accès à la page parente de la base (menu `…` → *Connexions* dans Notion).
3. **Tavily** (recherche web, gratuit, sans carte bancaire — 1 000 recherches/mois) :
   - [app.tavily.com](https://app.tavily.com) → *Sign in with Google* → la clé API (`tvly-…`)
     s'affiche sur le tableau de bord
   - Coller la clé en haut du nœud **Trouver le site web** (`TAVILY_KEY_EN_DUR`), ou l'exposer
     en variable d'environnement `TAVILY_API_KEY` (n8n bloque `$env` par défaut :
     `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`).
   - Sans clé, la branche B s'arrête en erreur et **ne touche à rien** : les fiches restent
     « À enrichir ».
   - *Pourquoi pas Google Custom Search ?* L'option « Rechercher sur l'ensemble du Web » est
     dépréciée et ne peut plus être activée sur un nouveau moteur (2026) ; et Google Places
     exige un compte de facturation.
4. Nœud **Config** : `DEPARTEMENTS` démarre à `['69']` (~1 100 entreprises ≈ 1 mois
   d'enrichissement au rythme gratuit). Ajoute les départements un par un.
5. **Execute workflow** (menu du bouton : *from Déclencheur quotidien*) pour un premier
   passage, vérifier les fiches dans Notion, puis **Publish**.

### Quota, mémoire et bonnes pratiques

- **Tavily : 1 000 recherches/mois** (100 fiches max par exécution). Quota atteint → le nœud
  s'arrête proprement, les fiches restantes gardent « À enrichir » et sont reprises plus tard.
- **Dédoublonner (SIREN)** mémorise les entreprises déjà créées dans Notion. Pour repartir
  de zéro : ouvrir le nœud → *Operation* → **Clear Deduplication History**, exécuter, puis
  remettre *Remove Items Processed in Previous Executions* (et vider la base Notion).
- **Opt-out RGPD** : passe la fiche en `Désinscrit` dans Notion (ou ajoute l'email à
  `SUPPRESSION_EMAILS` dans « Qualifier le prospect »). Une fiche qui n'est plus « À enrichir »
  n'est jamais retouchée par le workflow.
- Sur la branche A, utiliser **Execute workflow** plutôt que *Execute step* sur un nœud isolé :
  les données SIRENE (1 000+ entreprises) dépassent la taille acceptée par n8n pour une
  exécution partielle (« Existing execution data is too large »).

### Sources de données

| Source | Statut | Ce qu'elle donne |
|---|---|---|
| [API Recherche d'Entreprises](https://recherche-entreprises.api.gouv.fr) | Open data, gratuite, **sans clé** | SIREN/SIRET, raison sociale, dirigeant, NAF, effectif, adresse, RGE |
| [Tavily Search API](https://tavily.com) | Gratuite, 1 000 req/mois, sans carte | Site web de l'entreprise |
| Site web de l'entreprise | Coordonnées pro publiées volontairement | Email de contact, téléphone |

**Pages Jaunes n'est volontairement pas utilisé** : le scraping y est interdit par les CGU
et a déjà donné lieu à des condamnations.

### Réglages

Tout est en haut du nœud **Config** :

| Réglage | Défaut | Note |
|---|---|---|
| `NAF` | 15 métiers du bâtiment | Nomenclature INSEE rév. 2 |
| `DEPARTEMENTS` | `69` | Ajoute les départements un par un (100 fiches enrichies/jour) |
| `EFFECTIFS` | `00,01,02,03` (0-9 salariés) | `00` = artisan seul → plan 19 € ; `02`/`03` → plan 39 € |
| `PAGES` | 4 | 4 × 25 = 100 entreprises max par (NAF × département) |

Filtres appliqués dans **Normaliser et filtrer** : entreprise active, créée il y a > 6 mois,
≤ 3 établissements, catégorie PME, code NAF réellement dans la liste cible.

Segments exploitables en sortie : `est_rge` (rénovation énergétique, gros volume de devis)
et `est_entrepreneur_individuel` (artisan seul → cible naturelle du plan 19 €).

### Volumétrie

Compte **~35 % des entreprises retenues** après filtrage, puis **~30 à 40 % avec un email
exploitable** (beaucoup d'artisans n'ont pas de site). Sur le Rhône et 15 métiers, prévois
**~1 100 fiches** dans Notion dès le premier passage, enrichies en ~1 mois, soit
**300 à 400 prospects contactables**.

Rythme des requêtes : 400 ms entre chaque appel (l'API tolère 7 req/s — on reste large).

### Dépannage

**`ReferenceError: URLSearchParams is not defined`** (ou `setTimeout`, `fetch`, `Buffer`)

Le sandbox du **task runner** n8n n'expose que les intrinsèques ECMAScript — pas les globals
Node. Les nœuds Code de ce workflow en tiennent compte : la query string est construite à la
main avec `encodeURIComponent`, et les pauses passent par un helper qui se dégrade
silencieusement si `setTimeout` est absent.

Si tu as importé une version antérieure du fichier, réimporte celle-ci.

**`this.helpers.httpRequest indisponible dans ce runtime n8n`**

Ce message vient d'un garde volontaire, dans les nœuds *Trouver le site web* et
*Extraire email et telephone*. Ces deux nœuds appellent le réseau depuis du code parce qu'ils doivent
**fusionner** le résultat avec la fiche entreprise en cours — ce qu'un nœud HTTP Request seul
ne sait pas faire (il remplace l'item au lieu de l'enrichir).

Si ton runtime ne fournit pas ce helper : remplace chaque nœud Code par un **HTTP Request**
suivi d'un **Merge** en mode *Combine by position*. Le reste du workflow ne bouge pas.

### ⚠️ Avant de lancer une campagne

Le workflow constitue une base, il n'envoie rien. La conformité se joue à l'envoi :
lis la checklist en fin de [`sequences-cold-email.md`](sequences-cold-email.md).

L'essentiel : le B2B autorise l'**opt-out** (pas besoin de consentement préalable), à condition
que le message porte sur l'activité professionnelle, que la source soit traçable, que
l'expéditeur soit identifiable et qu'un lien de désinscription figure dans **chaque** message.
Les désinscriptions se reportent dans `SUPPRESSION_EMAILS`, nœud **Préparer le prospect**.
