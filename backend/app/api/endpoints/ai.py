from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import json

from app.api import deps
from app.models.user import User
from app.core.config import settings

router = APIRouter()

async def validate_input_with_ai(type_intervention: str, description: str) -> str | None:
    """
    Vérifie si la saisie a du sens. Retourne une erreur (str) si invalide, ou None si valide.
    """
    if not settings.MISTRAL_API_KEY:
        return None
        
    prompt = f"""Tu es un assistant strict chargé de vérifier la validité d'une saisie utilisateur pour un rapport d'intervention technique.
Type d'intervention : {type_intervention}
Description : {description}

Si la description est du charabia (ex: "azeaze"), n'a aucun sens, contient des insultes, ou n'a manifestement aucun rapport avec une intervention technique de type "{type_intervention}", tu dois IMPÉRATIVEMENT répondre par : "INVALIDE: [Raison concise expliquant pourquoi la description est refusée, destinée à l'utilisateur final]".
Sinon, si la description est pertinente, réponds uniquement "VALIDE".
Ne génère rien d'autre.
"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-small-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 100
                }
            )
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"].strip()
                if content.startswith("INVALIDE"):
                    return content.replace("INVALIDE:", "").replace("INVALIDE :", "").strip()
    except Exception:
        pass
    return None

class GenerateRapportRequest(BaseModel):
    type_intervention: str
    description: str
    longueur: str = "normal"  # "court", "normal", "long"
    nom_client: str | None = None
    adresse: str | None = None
    date_intervention: str | None = None


def build_rapport_prompt(request: GenerateRapportRequest) -> str:
    """
    Construit le prompt IA en fonction de la longueur choisie,
    avec des instructions strictes anti-hallucination.
    """
    context_parts = []
    if request.nom_client:
        context_parts.append(f"- Client : {request.nom_client}")
    if request.adresse:
        context_parts.append(f"- Adresse d'intervention : {request.adresse}")
    if request.date_intervention:
        context_parts.append(f"- Date : {request.date_intervention}")
    context = "\n".join(context_parts) if context_parts else ""

    # Instructions anti-hallucination (communes à toutes les longueurs)
    anti_hallucination = """RÈGLES STRICTES ANTI-INVENTION :
- Tu ne dois JAMAIS inventer ou fabriquer des informations qui ne sont pas explicitement mentionnées dans la description fournie.
- N'invente JAMAIS de marques, modèles, numéros de série, références produit, dimensions, mesures, valeurs techniques (pression, tension, ampérage, etc.) qui ne figurent pas dans la description.
- Si un détail technique n'est pas précisé dans la description, utilise des formulations génériques comme "l'équipement existant", "le matériel en place", "selon les normes en vigueur".
- Ne mentionne JAMAIS de noms de techniciens, de numéros de bon d'intervention, ou de références internes inventés.
- Base-toi UNIQUEMENT sur les informations fournies par l'utilisateur. Reformule et structure ces informations de manière professionnelle sans rien ajouter de factuel."""

    longueur = request.longueur if request.longueur in ("court", "normal", "long") else "normal"

    if longueur == "court":
        instructions_longueur = """LONGUEUR : ULTRA-COURT. Maximum 80 à 120 mots au total. Sois extrêmement bref.
UNE SEULE phrase par section. Pas de liste à puces, pas de détails superflus.

Format EXACT à respecter :

<strong>MOTIF :</strong>
<p>[1 seule phrase courte décrivant le problème]</p>

<strong>TRAVAUX :</strong>
<p>[1 seule phrase résumant ce qui a été fait]</p>

<strong>RÉSULTAT :</strong>
<p>[1 seule phrase sur l'état final]</p>

C'est TOUT. Ne dépasse JAMAIS 120 mots. Pas d'observations ni de recommandations."""

    elif longueur == "long":
        instructions_longueur = """Le rapport doit être TRÈS DÉTAILLÉ et COMPLET (environ 600-900 mots).
Chaque section doit être développée avec précision. Ajoute des sous-sections si pertinent.

Le rapport doit contenir ces sections avec des titres en <strong> et majuscules :

<strong>MOTIF DE L'INTERVENTION :</strong>
<p>[Description détaillée du problème signalé, contexte de la demande, basé uniquement sur la description fournie]</p>

<strong>CONSTATATIONS SUR SITE :</strong>
<p>[État des lieux à l'arrivée, observations visuelles, conditions d'accès — uniquement ce qui peut raisonnablement être déduit de la description]</p>

<strong>DIAGNOSTIC :</strong>
<p>[Analyse technique détaillée, cause identifiée du problème — basé sur la description fournie, sans inventer de mesures ou valeurs]</p>

<strong>TRAVAUX RÉALISÉS :</strong>
<ul>
<li>[Action détaillée avec méthode employée]</li>
<li>[...]</li>
</ul>

<strong>MATÉRIEL ET FOURNITURES :</strong>
<p>[Mentionner uniquement le matériel explicitement cité dans la description. Si aucun matériel n'est mentionné, écrire "Matériel standard utilisé selon les besoins de l'intervention."]</p>

<strong>TESTS ET VÉRIFICATIONS :</strong>
<p>[Tests pertinents qui auraient logiquement été effectués pour ce type d'intervention, sans inventer de valeurs numériques]</p>

<strong>RÉSULTAT ET ÉTAT FINAL :</strong>
<p>[Description de l'état après intervention, validation du résultat]</p>

<strong>OBSERVATIONS ET RECOMMANDATIONS :</strong>
<p>[Conseils de maintenance préventive génériques et adaptés au type d'intervention, points de vigilance]</p>"""

    else:  # normal
        instructions_longueur = """Le rapport doit avoir une longueur NORMALE et ÉQUILIBRÉE (environ 300-500 mots).

Le rapport doit contenir ces sections avec des titres en <strong> et majuscules :

<strong>MOTIF DE L'INTERVENTION :</strong>
<p>[Explication claire du problème signalé, basée uniquement sur la description fournie]</p>

<strong>DIAGNOSTIC :</strong>
<p>[Analyse technique, cause identifiée — basé sur la description, sans inventer de valeurs ou mesures]</p>

<strong>TRAVAUX RÉALISÉS :</strong>
<ul>
<li>[Action effectuée avec détails basés sur la description]</li>
<li>[...]</li>
</ul>

<strong>RÉSULTAT ET ÉTAT FINAL :</strong>
<p>[Description de l'état après intervention]</p>

<strong>OBSERVATIONS ET RECOMMANDATIONS :</strong>
<p>[Conseils de maintenance préventive adaptés au type d'intervention]</p>"""

    prompt = f"""Tu es un technicien expert rédigeant un rapport d'intervention professionnel en français.

Informations sur l'intervention :
- Type d'intervention : {request.type_intervention}
- Description : {request.description}
{context}

{anti_hallucination}

Génère un rapport d'intervention professionnel et structuré en HTML (sans balises <html>, <head>, <body>).
Utilise uniquement des balises HTML inline simples : <p>, <strong>, <em>, <ul>, <ol>, <li>, <br>.

IMPORTANT : Ne génère PAS d'en-tête ou de titre de rapport. Ne répète PAS les informations suivantes car elles sont déjà affichées dans le document : nom du client, adresse, date d'intervention, nom du technicien, nom de la société. Commence directement par les sections de contenu.

{instructions_longueur}

Adapte le vocabulaire technique au type d'intervention "{request.type_intervention}".
Ne génère QUE le contenu HTML des sections ci-dessus, sans aucun texte avant ou après, sans blocs de code markdown, sans en-tête."""

    return prompt


def get_max_tokens_for_longueur(longueur: str) -> int:
    """Retourne le max_tokens adapté à la longueur demandée."""
    if longueur == "court":
        return 400
    elif longueur == "long":
        return 4096
    else:
        return 2048


def get_model_for_longueur(longueur: str) -> str:
    """Retourne le modèle Mistral adapté. Small = plus rapide pour les rapports courts."""
    if longueur == "court":
        return "mistral-small-latest"
    else:
        return "mistral-large-latest"


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

    # --- Validation de la saisie (sautée en mode court pour la rapidité) ---
    if request.longueur != "court":
        validation_error = await validate_input_with_ai(request.type_intervention, request.description)
        if validation_error:
            raise HTTPException(status_code=400, detail=validation_error)

    prompt = build_rapport_prompt(request)
    max_tokens = get_max_tokens_for_longueur(request.longueur)
    model = get_model_for_longueur(request.longueur)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.4,
                    "max_tokens": max_tokens
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

    # --- Validation de la saisie (sautée en mode court pour la rapidité) ---
    if request.longueur != "court":
        validation_error = await validate_input_with_ai(request.type_intervention, request.description)
        if validation_error:
            raise HTTPException(status_code=400, detail=validation_error)

    prompt = build_rapport_prompt(request)
    max_tokens = get_max_tokens_for_longueur(request.longueur)
    model = get_model_for_longueur(request.longueur)

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
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.4,
                        "max_tokens": max_tokens,
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
