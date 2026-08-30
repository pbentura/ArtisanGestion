#!/usr/bin/env bash
#
# Sauvegarde de la base de production ArtisanGestion.
#
# Produit un dump compressé horodaté, vérifie qu'il n'est pas vide, puis
# supprime les sauvegardes plus anciennes que RETENTION_JOURS.
#
# Installation sur le VPS (exécution quotidienne à 3h15) :
#   chmod +x scripts/backup-db.sh
#   crontab -e
#   15 3 * * * cd /chemin/vers/ArtisanGestion && ./scripts/backup-db.sh >> /var/log/artisangestion-backup.log 2>&1
#
# IMPORTANT : une sauvegarde qui vit sur le même disque que la base ne protège
# que des erreurs humaines, pas d'une panne matérielle. Voir la section
# "Copie hors-serveur" en bas de ce fichier.

set -euo pipefail

RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RACINE"

DEST="${BACKUP_DIR:-$RACINE/backups}"
RETENTION_JOURS="${RETENTION_JOURS:-14}"
CONTENEUR="${DB_CONTAINER:-artisangestion-db}"
FICHIER_ENV="${ENV_FILE:-.env.production}"

if [[ ! -f "$FICHIER_ENV" ]]; then
  echo "ERREUR : $FICHIER_ENV introuvable depuis $RACINE" >&2
  exit 1
fi

# Lit POSTGRES_USER / POSTGRES_DB sans exporter tout le fichier
lire_var() {
  grep -E "^$1=" "$FICHIER_ENV" | tail -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | xargs
}

PG_USER="$(lire_var POSTGRES_USER)"
PG_DB="$(lire_var POSTGRES_DB)"

if [[ -z "$PG_USER" || -z "$PG_DB" ]]; then
  echo "ERREUR : POSTGRES_USER ou POSTGRES_DB absent de $FICHIER_ENV" >&2
  exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTENEUR"; then
  echo "ERREUR : conteneur '$CONTENEUR' non démarré" >&2
  exit 1
fi

mkdir -p "$DEST"
HORODATAGE="$(date +%Y%m%d-%H%M%S)"
CIBLE="$DEST/artisangestion-$HORODATAGE.sql.gz"

echo "[$(date '+%F %T')] Sauvegarde de $PG_DB vers $CIBLE"

# --clean --if-exists : le dump peut être rejoué sur une base existante
docker exec "$CONTENEUR" pg_dump \
  -U "$PG_USER" -d "$PG_DB" \
  --clean --if-exists --no-owner --no-privileges \
  | gzip -9 > "$CIBLE"

# Un pg_dump qui échoue en cours de route peut laisser un fichier tronqué :
# on vérifie l'intégrité gzip et une taille plancher.
if ! gzip -t "$CIBLE" 2>/dev/null; then
  echo "ERREUR : archive corrompue, suppression de $CIBLE" >&2
  rm -f "$CIBLE"
  exit 1
fi

TAILLE=$(wc -c < "$CIBLE")
if (( TAILLE < 1024 )); then
  echo "ERREUR : sauvegarde suspecte ($TAILLE octets), suppression" >&2
  rm -f "$CIBLE"
  exit 1
fi

echo "[$(date '+%F %T')] OK — $(du -h "$CIBLE" | cut -f1)"

# Purge des anciennes sauvegardes
SUPPRIMEES=$(find "$DEST" -name 'artisangestion-*.sql.gz' -mtime "+$RETENTION_JOURS" -print -delete | wc -l)
if (( SUPPRIMEES > 0 )); then
  echo "[$(date '+%F %T')] $SUPPRIMEES sauvegarde(s) de plus de $RETENTION_JOURS jours supprimée(s)"
fi

echo "[$(date '+%F %T')] Sauvegardes présentes : $(ls -1 "$DEST"/artisangestion-*.sql.gz 2>/dev/null | wc -l)"

# ---------------------------------------------------------------------------
# Restauration
#
#   gunzip -c backups/artisangestion-AAAAMMJJ-HHMMSS.sql.gz \
#     | docker exec -i artisangestion-db psql -U <POSTGRES_USER> -d <POSTGRES_DB>
#
# Testez la restauration au moins une fois sur une base jetable. Une sauvegarde
# jamais restaurée n'est pas une sauvegarde.
#
# ---------------------------------------------------------------------------
# Copie hors-serveur (à faire en plus)
#
# Vos clients ont une obligation de conservation de 6 ans sur leurs factures.
# Ajoutez une copie vers un stockage distinct, par exemple avec rclone :
#
#   rclone copy "$DEST" distant:artisangestion-backups --max-age 24h
#
# ou, plus simplement, depuis une autre machine :
#
#   rsync -az vps:/chemin/vers/ArtisanGestion/backups/ ./backups-artisangestion/
