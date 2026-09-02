#!/usr/bin/env bash
#
# Prépare le déploiement automatique (.github/workflows/deploiement-backend.yml).
#
# Le script :
#   1. crée une paire de clés SSH dédiée au déploiement ;
#   2. installe la clé publique sur le VPS ;
#   3. relève l'empreinte du serveur ;
#   4. enregistre les secrets sur GitHub (via `gh`) ou les affiche à recopier ;
#   5. vérifie que la connexion automatisée fonctionne.
#
# Utilisation :
#   chmod +x scripts/configurer-deploiement.sh
#   ./scripts/configurer-deploiement.sh
#
# Variables optionnelles :
#   VPS_HOTE=178.16.130.160 VPS_UTILISATEUR=root \
#   VPS_CHEMIN=/root/projects/Ventura ./scripts/configurer-deploiement.sh
#
# POURQUOI UNE CLÉ DÉDIÉE plutôt que votre clé personnelle : elle ne sert qu'à
# ce dépôt, elle est révocable en supprimant une ligne d'authorized_keys sur le
# VPS, et votre clé personnelle ne quitte jamais votre machine.

set -euo pipefail

RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RACINE"

HOTE="${VPS_HOTE:-178.16.130.160}"
UTILISATEUR="${VPS_UTILISATEUR:-root}"
CHEMIN="${VPS_CHEMIN:-/root/projects/Ventura}"
CLE="$HOME/.ssh/artisangestion_deploiement"

demander() {
  local invite="$1" defaut="$2" reponse
  read -r -p "$invite [$defaut] : " reponse
  echo "${reponse:-$defaut}"
}

echo "=== Configuration du déploiement automatique ==="
echo
HOTE="$(demander "Adresse du VPS" "$HOTE")"
UTILISATEUR="$(demander "Utilisateur SSH" "$UTILISATEUR")"
CHEMIN="$(demander "Chemin du dépôt sur le VPS" "$CHEMIN")"
echo

# ── 1. Clé dédiée ──────────────────────────────────────────────────────
if [[ -f "$CLE" ]]; then
  echo "Clé existante réutilisée : $CLE"
else
  echo "Génération d'une clé dédiée au déploiement…"
  ssh-keygen -t ed25519 -N '' -C "deploiement-github-artisangestion" -f "$CLE"
fi
echo

# ── 2. Installation sur le VPS ─────────────────────────────────────────
echo "Installation de la clé publique sur $UTILISATEUR@$HOTE"
echo "(votre mot de passe ou votre clé habituelle vous sera demandé une fois)"
if command -v ssh-copy-id > /dev/null; then
  ssh-copy-id -i "$CLE.pub" "$UTILISATEUR@$HOTE"
else
  ssh "$UTILISATEUR@$HOTE" \
    "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys" \
    < "$CLE.pub"
fi
echo

# ── 3. Empreinte du serveur ────────────────────────────────────────────
# Sans elle, le workflow devrait accepter n'importe quel serveur répondant à
# cette adresse. On la fige donc explicitement.
echo "Relevé de l'empreinte SSH du serveur…"
EMPREINTES="$(ssh-keyscan -t rsa,ecdsa,ed25519 "$HOTE" 2>/dev/null | grep -v '^#')"
if [[ -z "$EMPREINTES" ]]; then
  echo "ERREUR : impossible de relever l'empreinte de $HOTE" >&2
  exit 1
fi
echo "$(echo "$EMPREINTES" | wc -l | xargs) empreinte(s) relevée(s)."
echo

# ── 4. Vérification avant enregistrement ───────────────────────────────
echo "Test de la connexion automatisée…"
FICHIER_HOTES="$(mktemp)"
printf '%s\n' "$EMPREINTES" > "$FICHIER_HOTES"
if ssh -i "$CLE" -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$FICHIER_HOTES" \
       -o BatchMode=yes -o ConnectTimeout=15 \
       "$UTILISATEUR@$HOTE" "test -d '$CHEMIN/.git'"; then
  echo "OK — connexion établie et dépôt trouvé dans $CHEMIN"
else
  echo "ERREUR : connexion impossible, ou $CHEMIN n'est pas un dépôt git." >&2
  echo "Vérifiez le chemin avec : ssh $UTILISATEUR@$HOTE 'ls -d $CHEMIN/.git'" >&2
  rm -f "$FICHIER_HOTES"
  exit 1
fi
rm -f "$FICHIER_HOTES"
echo

# Le VPS doit pouvoir récupérer le code sans intervention.
echo "Vérification de l'accès au dépôt depuis le VPS…"
if ssh -i "$CLE" -o BatchMode=yes "$UTILISATEUR@$HOTE" \
     "cd '$CHEMIN' && git fetch --dry-run origin" 2>&1 | head -3; then
  echo "OK — le VPS peut lire le dépôt."
else
  echo "ATTENTION : le VPS ne peut pas récupérer le dépôt."
  echo "Vérifiez la clé de déploiement GitHub configurée sur le serveur."
fi

# Le dépôt a été renommé Ventura -> ArtisanGestion. GitHub redirige encore
# l'ancienne URL, mais cette redirection ne durera pas éternellement.
URL_DISTANTE="$(ssh -i "$CLE" -o BatchMode=yes "$UTILISATEUR@$HOTE" \
  "cd '$CHEMIN' && git remote get-url origin" 2>/dev/null || echo '')"
if [[ "$URL_DISTANTE" == *Ventura* ]]; then
  echo
  echo "Note : le VPS pointe encore sur l'ancienne URL du dépôt"
  echo "  $URL_DISTANTE"
  echo "Elle fonctionne par redirection, mais mieux vaut la corriger :"
  echo "  ssh $UTILISATEUR@$HOTE \"cd $CHEMIN && git remote set-url origin git@github.com:pbentura/ArtisanGestion.git\""
fi
echo

# ── 5. Enregistrement des secrets ──────────────────────────────────────
if command -v gh > /dev/null && gh auth status > /dev/null 2>&1; then
  echo "Enregistrement des secrets sur GitHub via gh…"
  gh secret set VPS_HOTE --body "$HOTE"
  gh secret set VPS_UTILISATEUR --body "$UTILISATEUR"
  gh secret set VPS_CLE_SSH < "$CLE"
  gh secret set VPS_KNOWN_HOSTS --body "$EMPREINTES"
  gh variable set VPS_CHEMIN_PROJET --body "$CHEMIN"
  echo
  echo "Terminé. Le prochain push sur main déclenchera le déploiement."
else
  cat <<INSTRUCTIONS
gh n'est pas installé ou pas connecté : à recopier à la main.

  GitHub > Settings > Secrets and variables > Actions

  Onglet « Secrets » — New repository secret :

    VPS_HOTE          $HOTE
    VPS_UTILISATEUR   $UTILISATEUR
    VPS_KNOWN_HOSTS   (les $(echo "$EMPREINTES" | wc -l | xargs) lignes ci-dessous)

$EMPREINTES

    VPS_CLE_SSH       le contenu intégral de $CLE
                      lignes BEGIN et END comprises :

                        pbcopy < $CLE      (macOS, copie dans le presse-papier)

  Onglet « Variables » — New repository variable :

    VPS_CHEMIN_PROJET $CHEMIN

Ne collez jamais cette clé privée ailleurs que dans les secrets GitHub.
Pour la révoquer : supprimez la ligne « deploiement-github-artisangestion »
de ~/.ssh/authorized_keys sur le VPS.
INSTRUCTIONS
fi
