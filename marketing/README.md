# marketing/

| Fichier | Contenu |
|---|---|
| [`strategie-acquisition-10k-mrr.md`](strategie-acquisition-10k-mrr.md) | Le plan complet : calcul du churn, fenêtre facture électronique 2027, canaux classés par ROI, plan 90 jours |
| [`sequences-cold-email.md`](sequences-cold-email.md) | Séquences d'emails + script téléphone + checklist de conformité |
| [`n8n-prospection-artisans.json`](n8n-prospection-artisans.json) | Workflow n8n de constitution de la base de prospects |
| [`../marketing_strategy_google_ads.md`](../marketing_strategy_google_ads.md) | Stratégie Google Ads (existant) |

---

## Workflow n8n — prospection artisans

Construit une liste d'artisans du bâtiment qualifiée, à partir de sources **publiques et légales**.

```
Déclencheur quotidien (7h, lun-ven)
  └─ Config .......................... codes NAF × départements × pages
     └─ API Recherche Entreprises .... base SIRENE, open data, sans clé
        └─ Normaliser et filtrer ..... TPE 0-9 salariés, > 6 mois, métier du bâtiment
           └─ Dédoublonner ........... mémoire entre exécutions (par SIREN)
              └─ Trouver le site web . Google Places (optionnel)
                 └─ Extraire l'email . page contact / mentions légales
                    └─ Préparer ...... variables de perso + liste de suppression
                       └─ Google Sheets
```

### Installation

1. Dans n8n : **Workflows → Import from File** → `n8n-prospection-artisans.json`
2. Ouvrir le nœud **Config** et régler `DEPARTEMENTS` (démarre avec 2-3) et `NAF`.
3. Nœud **Enregistrer (Google Sheets)** : brancher tes credentials et remplacer
   `REMPLACE_PAR_TON_ID_DE_SHEET`. *(Ou remplace ce nœud par un HTTP Request vers
   l'API Instantly / Smartlead / Lemlist pour pousser directement dans la campagne.)*
4. *(Optionnel mais recommandé)* Variable d'environnement `GOOGLE_PLACES_API_KEY`.
   Sans elle, l'étape site web est ignorée et tu ne récupères ni email ni téléphone —
   tu gardes néanmoins la liste des entreprises (utile pour du démarchage terrain ou téléphone).

   n8n bloque l'accès à `$env` par défaut : lance-le avec `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`,
   ou colle la clé en dur dans le nœud **Trouver le site web**.

### Sources de données

| Source | Statut | Ce qu'elle donne |
|---|---|---|
| [API Recherche d'Entreprises](https://recherche-entreprises.api.gouv.fr) | Open data, gratuite, **sans clé** | SIREN/SIRET, raison sociale, dirigeant, NAF, effectif, adresse, RGE |
| [Google Places API (New)](https://developers.google.com/maps/documentation/places/web-service) | Payante, quota gratuit mensuel | Site web, téléphone |
| Site web de l'entreprise | Coordonnées pro publiées volontairement | Email de contact |

**Pages Jaunes n'est volontairement pas utilisé** : le scraping y est interdit par les CGU
et a déjà donné lieu à des condamnations.

### Réglages

Tout est en haut du nœud **Config** :

| Réglage | Défaut | Note |
|---|---|---|
| `NAF` | 15 métiers du bâtiment | Nomenclature INSEE rév. 2 |
| `DEPARTEMENTS` | `69, 38, 01` | Élargis quand la séquence convertit |
| `EFFECTIFS` | `00,01,02,03` (0-9 salariés) | `00` = artisan seul → plan 19 € ; `02`/`03` → plan 39 € |
| `PAGES` | 4 | 4 × 25 = 100 entreprises max par (NAF × département) |

Filtres appliqués dans **Normaliser et filtrer** : entreprise active, créée il y a > 6 mois,
≤ 3 établissements, catégorie PME, code NAF réellement dans la liste cible.

Segments exploitables en sortie : `est_rge` (rénovation énergétique, gros volume de devis)
et `est_entrepreneur_individuel` (artisan seul → cible naturelle du plan 19 €).

### Volumétrie

Compte **~35 % des entreprises retenues** après filtrage, puis **~30 à 40 % avec un email
exploitable** (beaucoup d'artisans n'ont pas de site). Sur 3 départements et 15 métiers,
prévois **200 à 500 prospects contactables**.

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
*Extraire l'email pro*. Ces deux nœuds appellent le réseau depuis du code parce qu'ils doivent
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
