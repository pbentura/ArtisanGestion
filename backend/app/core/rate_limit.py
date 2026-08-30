"""
Limitation de débit.

Protège les routes coûteuses ou sensibles : authentification (force brute),
envoi d'emails (quota Resend) et génération IA (crédit Mistral).

Le compteur est en mémoire : il est donc propre à chaque processus. C'est
suffisant tant que l'API tourne en un seul worker uvicorn. Si vous passez à
plusieurs workers ou plusieurs conteneurs, renseignez REDIS_URL pour que les
compteurs soient partagés.
"""

import os

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def _cle_client(request: Request) -> str:
    """
    Identifie l'appelant par son jeton quand il est authentifié, sinon par IP.
    Évite qu'un réseau d'entreprise partageant une IP publique soit limité
    globalement à cause d'un seul utilisateur.
    """
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return f"tok:{auth[7:][-32:]}"
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(
    key_func=_cle_client,
    storage_uri=os.getenv("REDIS_URL") or "memory://",
    headers_enabled=True,
)
