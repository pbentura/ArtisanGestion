from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import json

from app.api import deps
from app.models.user import User
from app.core.config import settings

router = APIRouter()


class GenerateRapportRequest(BaseModel):
    type_intervention: str
    description: str
    nom_client: str | None = None
    adresse: str | None = None
    date_intervention: str | None = None


class GenerateRapportResponse(BaseModel):
    contenu: str


@router.post("/generate-rapport", response_model=GenerateRapportResponse)
async def generate_rapport(
    request: GenerateRapportRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Génère le contenu d'un rapport d'intervention via l'API Mistral AI.
    """
    if not settings.MISTRAL_API_KEY:
        raise HTTPException(status_code=500, detail="Clé API Mistral non configurée")

    # Construire le prompt
    context_parts = []
    if request.nom_client:
        context_parts.append(f"- Client : {request.nom_client}")
    if request.adresse:
        context_parts.append(f"- Adresse d'intervention : {request.adresse}")
    if request.date_intervention:
        context_parts.append(f"- Date : {request.date_intervention}")

    context = "\n".join(context_parts) if context_parts else ""

    prompt = f"""Tu es un technicien expert rédigeant un rapport d'intervention professionnel en français.

Informations sur l'intervention :
- Type d'intervention : {request.type_intervention}
- Description : {request.description}
{context}

Génère un rapport d'intervention professionnel, structuré et complet en HTML (sans balises <html>, <head>, <body>).
Utilise uniquement des balises HTML inline simples : <p>, <strong>, <em>, <ul>, <ol>, <li>, <br>.

IMPORTANT : Ne génère PAS d'en-tête ou de titre de rapport. Ne répète PAS les informations suivantes car elles sont déjà affichées dans le document : nom du client, adresse, date d'intervention, nom du technicien, nom de la société. Commence directement par les sections de contenu.

Le rapport doit obligatoirement contenir ces sections avec des titres en <strong> et majuscules :

<strong>MOTIF DE L'INTERVENTION :</strong>
<p>[Explication claire du problème signalé ou de la demande du client, basée sur la description fournie]</p>

<strong>DIAGNOSTIC :</strong>
<p>[Analyse technique, cause identifiée du problème, état des équipements constatés]</p>

<strong>TRAVAUX RÉALISÉS :</strong>
<ul>
<li>[Action 1 effectuée avec détails techniques]</li>
<li>[Action 2]</li>
<li>[...]</li>
</ul>

<strong>RÉSULTAT ET ÉTAT FINAL :</strong>
<p>[Description de l'état après intervention, tests effectués, validation du résultat]</p>

<strong>OBSERVATIONS ET RECOMMANDATIONS :</strong>
<p>[Conseils de maintenance préventive, recommandations pour le client, points de vigilance]</p>

Rends le rapport réaliste, détaillé et très professionnel. Adapte le vocabulaire technique au type d'intervention.
Ne génère QUE le contenu HTML des sections ci-dessus, sans aucun texte avant ou après, sans blocs de code markdown, sans en-tête."""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-large-latest",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2048
                }
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Erreur API Mistral : {response.text}"
            )

        data = response.json()
        contenu = data["choices"][0]["message"]["content"].strip()

        # Nettoyer les blocs de code markdown si présents
        if contenu.startswith("```html"):
            contenu = contenu[7:]
        if contenu.startswith("```"):
            contenu = contenu[3:]
        if contenu.endswith("```"):
            contenu = contenu[:-3]
        contenu = contenu.strip()

        return GenerateRapportResponse(contenu=contenu)

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Délai d'attente dépassé lors de la génération IA")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {str(e)}")


@router.post("/generate-rapport-stream")
async def generate_rapport_stream(
    request: GenerateRapportRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Génère le contenu d'un rapport via Mistral AI en streaming SSE.
    Chaque token est retransmis immédiatement au client via Server-Sent Events.
    """
    if not settings.MISTRAL_API_KEY:
        raise HTTPException(status_code=500, detail="Clé API Mistral non configurée")

    # Construire le prompt (identique à l'endpoint non-streaming)
    context_parts = []
    if request.nom_client:
        context_parts.append(f"- Client : {request.nom_client}")
    if request.adresse:
        context_parts.append(f"- Adresse d'intervention : {request.adresse}")
    if request.date_intervention:
        context_parts.append(f"- Date : {request.date_intervention}")

    context = "\n".join(context_parts) if context_parts else ""

    prompt = f"""Tu es un technicien expert rédigeant un rapport d'intervention professionnel en français.

Informations sur l'intervention :
- Type d'intervention : {request.type_intervention}
- Description : {request.description}
{context}

Génère un rapport d'intervention professionnel, structuré et complet en HTML (sans balises <html>, <head>, <body>).
Utilise uniquement des balises HTML inline simples : <p>, <strong>, <em>, <ul>, <ol>, <li>, <br>.

IMPORTANT : Ne génère PAS d'en-tête ou de titre de rapport. Ne répète PAS les informations suivantes car elles sont déjà affichées dans le document : nom du client, adresse, date d'intervention, nom du technicien, nom de la société. Commence directement par les sections de contenu.

Le rapport doit obligatoirement contenir ces sections avec des titres en <strong> et majuscules :

<strong>MOTIF DE L'INTERVENTION :</strong>
<p>[Explication claire du problème signalé ou de la demande du client, basée sur la description fournie]</p>

<strong>DIAGNOSTIC :</strong>
<p>[Analyse technique, cause identifiée du problème, état des équipements constatés]</p>

<strong>TRAVAUX RÉALISÉS :</strong>
<ul>
<li>[Action 1 effectuée avec détails techniques]</li>
<li>[Action 2]</li>
<li>[...]</li>
</ul>

<strong>RÉSULTAT ET ÉTAT FINAL :</strong>
<p>[Description de l'état après intervention, tests effectués, validation du résultat]</p>

<strong>OBSERVATIONS ET RECOMMANDATIONS :</strong>
<p>[Conseils de maintenance préventive, recommandations pour le client, points de vigilance]</p>

Rends le rapport réaliste, détaillé et très professionnel. Adapte le vocabulaire technique au type d'intervention.
Ne génère QUE le contenu HTML des sections ci-dessus, sans aucun texte avant ou après, sans blocs de code markdown, sans en-tête."""

    async def event_stream():
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistral-large-latest",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 2048,
                        "stream": True
                    }
                ) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        yield f"event: error\ndata: {error_body.decode()}\n\n"
                        return

                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        raw = line[6:]
                        if raw == "[DONE]":
                            yield "data: [DONE]\n\n"
                            return
                        try:
                            chunk = json.loads(raw)
                            delta = chunk["choices"][0]["delta"].get("content", "")
                            if delta:
                                # Encoder le delta en JSON pour éviter les problèmes de sauts de ligne
                                yield f"data: {json.dumps(delta)}\n\n"
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue

        except httpx.TimeoutException:
            yield "event: error\ndata: timeout\n\n"
        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
