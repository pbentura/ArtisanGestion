/**
 * Catalogue des questions fréquentes.
 *
 * Centralisé ici pour que chaque page d'atterrissage n'affiche que celles qui
 * concernent son intention de recherche, sans dupliquer les réponses.
 * Les formulations décrivent le produit tel qu'il est réellement : pas de plan
 * gratuit illimité, pas d'application native encore publiée.
 */
export const TOUTES_QUESTIONS: Record<string, { question: string; answer: string }> = {
  securite: {
    question: 'Mes données sont-elles sécurisées ?',
    answer: 'Oui. Vos données sont hébergées en France, sur un serveur situé à Paris. Les échanges sont chiffrés (SSL/TLS) et l\'accès protégé par authentification. Nous ne partageons jamais vos données avec des tiers. Vous en restez propriétaire et pouvez supprimer votre compte et vos données à tout moment.',
  },
  demarrage: {
    question: 'Combien de temps avant de créer mon premier document ?',
    answer: 'Quelques minutes. Vous créez votre compte, et vous pouvez commencer directement — rien n\'est bloqué par un long formulaire. Les informations de votre entreprise vous sont demandées au moment où vous créez votre premier document, et nous les pré-remplissons automatiquement à partir de votre SIRET ou du nom de votre société.',
  },
  migration: {
    question: 'Comment migrer depuis Excel ou mon logiciel actuel ?',
    answer: 'Il n\'y a rien à migrer. Pas besoin d\'importer votre historique : vous commencez simplement vos prochains devis, factures et rapports sur ArtisanGestion. Vos anciens documents restent là où ils sont.',
  },
  facturation2026: {
    question: 'Qu\'est-ce que la facturation électronique 2026 ?',
    answer: 'À partir de 2026, les entreprises françaises devront émettre et recevoir leurs factures au format électronique structuré. ArtisanGestion génère vos factures au format Factur-X, conforme au standard européen EN 16931. Vous n\'avez rien à faire de plus, c\'est intégré.',
  },
  essai: {
    question: 'L\'essai gratuit est-il vraiment gratuit ?',
    answer: 'Oui. Vous disposez de 14 jours pour utiliser toutes les fonctionnalités, sans aucune limite et sans carte bancaire à l\'inscription. À la fin de l\'essai, rien ne vous est prélevé : vous choisissez de vous abonner ou non. Sans abonnement, vous ne pouvez plus créer de nouveaux documents, mais vous gardez l\'accès à ceux déjà créés.',
  },
  mobile: {
    question: 'Puis-je l\'utiliser depuis mon téléphone, sur le chantier ?',
    answer: 'Oui. ArtisanGestion s\'utilise directement depuis le navigateur de votre téléphone, sans rien installer : créez vos rapports d\'intervention, ajoutez des photos et faites signer votre client sur l\'écran, depuis le chantier. Les applications iOS et Android sont en cours de finalisation.',
  },
  ia: {
    question: 'Comment fonctionne la génération de rapports par IA ?',
    answer: 'Vous choisissez le type d\'intervention (plomberie, électricité, etc.) et décrivez en quelques mots ce que vous avez fait. L\'IA rédige un rapport professionnel structuré en une dizaine de secondes. Vous choisissez la longueur : court, normal ou détaillé. Des garde-fous empêchent l\'IA d\'inventer des détails que vous n\'avez pas mentionnés — et vous relisez toujours avant d\'envoyer.',
  },
  personnalisation: {
    question: 'Puis-je personnaliser mes documents ?',
    answer: 'Oui. Votre logo, vos coordonnées, vos mentions légales et votre pied de page sont repris automatiquement sur tous vos devis, factures et rapports. Vous pouvez les modifier à tout moment dans les paramètres. La couleur de vos documents et le retrait de la mention ArtisanGestion sont inclus pendant l\'essai, puis avec le forfait Équipe.',
  },
  resiliation: {
    question: 'Puis-je annuler mon abonnement ?',
    answer: 'À tout moment, en deux clics depuis vos paramètres. Il n\'y a aucun engagement de durée et aucun frais de résiliation. Votre abonnement reste actif jusqu\'à la fin de la période déjà payée.',
  },
}
