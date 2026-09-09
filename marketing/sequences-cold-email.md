# Séquences de prospection — ArtisanGestion

Variables produites par `n8n-prospection-artisans.json` :
`{{var_prenom}}` `{{var_societe}}` `{{var_metier}}` `{{var_ville}}`

## Les 6 règles pour cette cible

1. **3 à 5 lignes maximum.** L'artisan lit sur son téléphone, entre deux chantiers, en 4 secondes.
2. **Zéro jargon SaaS.** Jamais « solution », « optimiser vos process », « digitaliser ». Il dit « devis », « facture », « paperasse », « impayés ».
3. **Pas de lien dans le premier email.** Ça abîme la délivrabilité et ça sent la pub.
4. **Une seule question à la fin**, à laquelle on peut répondre par oui/non.
5. **Objet en minuscules, 2-4 mots**, comme un mail entre collègues. Jamais d'emoji ni de MAJUSCULES.
6. **40 emails/jour/boîte maximum.** Au-delà, tu grilles le domaine.

---

## Séquence A — « Facture électronique 2027 » (à privilégier)

C'est l'angle le plus fort des 12 prochains mois : deadline légale, pas un confort.

### A1 — J+0

> **Objet :** question facture électronique
>
> Bonjour {{var_prenom}},
>
> Je contacte les {{var_metier}}s du côté de {{var_ville}} au sujet de l'obligation de facture
> électronique qui tombe en septembre 2027.
>
> Vous avez déjà regardé comment {{var_societe}} allait s'y mettre, ou c'est encore le truc
> qu'on repousse ?
>
> Pinhas
> ArtisanGestion — [adresse postale]
> *Vous recevez ce message à votre adresse professionnelle. [Me retirer de la liste](#) — [Données personnelles](#)*

### A2 — J+3

> **Objet :** Re: question facture électronique
>
> Bonjour {{var_prenom}},
>
> Pour info, les 2 points qui coincent le plus chez les artisans que j'ai eus au téléphone :
>
> — la facture papier ou le PDF par mail ne seront plus valables entre pros
> — il faut passer par une plateforme agréée, ce n'est plus au choix
>
> Je vous envoie le récap en 1 page si ça vous est utile ?

### A3 — J+8

> **Objet :** Re: question facture électronique
>
> {{var_prenom}}, je me suis peut-être trompé de personne — c'est bien vous qui gérez
> les devis et les factures chez {{var_societe}} ?
>
> Si c'est votre comptable, dites-le moi, j'arrête de vous embêter.

### A4 — J+15 (rupture)

> **Objet :** je ferme
>
> Pas de souci {{var_prenom}}, je ne relance plus.
>
> Si un jour la paperasse du soir vous gonfle, vous savez où me trouver.
> Bon courage sur les chantiers.

---

## Séquence B — « Le devis du soir »

Angle douleur quotidienne. Marche mieux sur les artisans seuls (`est_entrepreneur_individuel = true`).

### B1 — J+0

> **Objet :** vos devis
>
> Bonjour {{var_prenom}},
>
> Je bosse avec des {{var_metier}}s sur {{var_ville}}. Celui qui me disait passer ses
> dimanches soir sur ses devis les fait maintenant depuis son téléphone, sur le chantier,
> et le client signe sur l'écran avant qu'il reparte.
>
> C'est un sujet chez {{var_societe}}, les devis qui traînent ?
>
> Pinhas
> ArtisanGestion — [adresse postale]
> *Vous recevez ce message à votre adresse professionnelle. [Me retirer de la liste](#) — [Données personnelles](#)*

### B2 — J+3

> Bonjour {{var_prenom}},
>
> Le truc concret : vous dictez ce que vous avez fait, l'appli rédige le rapport
> d'intervention à votre place. Plus de compte-rendu à taper le soir.
>
> Je vous fais voir en 5 minutes au téléphone cette semaine ?

### B3 — J+8

> {{var_prenom}}, une dernière question et je vous laisse :
>
> aujourd'hui vos devis, c'est Word, Excel, ou un logiciel ?
>
> Je demande parce que la réponse change complètement ce que je peux vous proposer.

### B4 — J+15 (rupture)

> Je ne relance plus, {{var_prenom}}. Bon courage.

---

## Script téléphone (à tester en priorité)

Le démarchage **B2B est légal** — Bloctel ne concerne que les particuliers.
Les artisans **décrochent** (c'est leur métier) et lisent peu leurs mails.
**20 appels ≈ 500 emails**, en beaucoup plus rapide et beaucoup plus instructif.

> « Bonjour, {{var_prenom}} ? Pinhas, d'ArtisanGestion. Je vous prends 30 secondes,
> vous êtes sur un chantier là ?
>
> *(s'il dit oui : « Je vous rappelle quand ? » et on raccroche — on rappelle vraiment.)*
>
> Je fais le tour des {{var_metier}}s du secteur sur l'obligation de facture électronique
> de 2027. Vous en avez entendu parler ?
>
> *(quelle que soit la réponse)* En gros à partir de septembre 2027, les factures entre
> pros devront passer par une plateforme agréée. Le PDF par mail, c'est fini.
>
> Vous faites vos devis comment aujourd'hui ? »

**Le seul objectif de l'appel : le faire parler de sa paperasse.** Pas de vendre.
Note ses mots exacts — ce sont eux qui iront dans tes pages SEO et tes pubs.

### Les 3 objections que tu vas entendre

| Objection | Réponse |
|---|---|
| « J'ai déjà un logiciel » | « Lequel ? … Et il gère la facture électronique 2027 ? » |
| « C'est mon comptable qui fait ça » | « Il fait la compta, mais les devis sur le chantier ? » |
| « J'ai pas le temps » | « C'est exactement pour ça que j'appelle. Je vous rappelle jeudi 19h ? » |

---

## Conformité — à faire avant le premier envoi

- [ ] Pied de page dans **chaque** message : identité complète (nom, société, **adresse postale**), lien de désinscription en 1 clic, lien vers la politique de confidentialité.
- [ ] Mention d'information art. 14 RGPD dans le **premier** email (la donnée vient d'une source publique, pas de la personne).
- [ ] Désinscription traitée **sous 48 h** et reportée dans `SUPPRESSION_EMAILS` du workflow.
- [ ] Registre des traitements à jour (le champ `source` du workflow te sert de preuve).
- [ ] SPF, DKIM et DMARC configurés sur les domaines d'envoi.
- [ ] **Warm-up de 3 semaines** avant le premier envoi réel. Non négociable.
- [ ] Jamais depuis `artisangestion.com` : utilise des domaines secondaires dédiés.
