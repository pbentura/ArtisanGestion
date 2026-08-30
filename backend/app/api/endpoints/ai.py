# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel
# import httpx
# import json
#
# from app.api import deps
# from app.models.user import User
# from app.core.config import settings
#
# router = APIRouter()
#
# async def validate_input_with_ai(type_intervention: str, description: str) -> str | None:
#     """
#     Vérifie si la saisie a du sens. Retourne une erreur (str) si invalide, ou None si valide.
#     """
#     if not settings.MISTRAL_API_KEY:
#         return None
#
#     prompt = f"""Tu es un assistant strict chargé de vérifier la validité d'une saisie utilisateur pour un rapport d'intervention technique.
# Type d'intervention : {type_intervention}
# Description : {description}
#
# Si la description est du charabia (ex: "azeaze"), n'a aucun sens, contient des insultes, ou n'a manifestement aucun rapport avec une intervention technique de type "{type_intervention}", tu dois IMPÉRATIVEMENT répondre par : "INVALIDE: [Raison concise expliquant pourquoi la description est refusée, destinée à l'utilisateur final]".
# Sinon, si la description est pertinente, réponds uniquement "VALIDE".
# Ne génère rien d'autre.
# """
#     try:
#         async with httpx.AsyncClient(timeout=10.0) as client:
#             response = await client.post(
#                 "https://api.mistral.ai/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "model": "mistral-small-latest",
#                     "messages": [{"role": "user", "content": prompt}],
#                     "temperature": 0.1,
#                     "max_tokens": 100
#                 }
#             )
#             if response.status_code == 200:
#                 content = response.json()["choices"][0]["message"]["content"].strip()
#                 if content.startswith("INVALIDE"):
#                     return content.replace("INVALIDE:", "").replace("INVALIDE :", "").strip()
#     except Exception:
#         pass
#     return None
#
# class GenerateRapportRequest(BaseModel):
#     type_intervention: str
#     description: str
#     longueur: str = "normal"  # "court", "normal", "long"
#     nom_client: str | None = None
#     adresse: str | None = None
#     date_intervention: str | None = None
#
#
# def build_rapport_prompt(request: GenerateRapportRequest) -> str:
#     """
#     Construit le prompt IA en fonction de la longueur choisie,
#     avec des instructions strictes anti-hallucination.
#     """
#     context_parts = []
#     if request.nom_client:
#         context_parts.append(f"- Client : {request.nom_client}")
#     if request.adresse:
#         context_parts.append(f"- Adresse d'intervention : {request.adresse}")
#     if request.date_intervention:
#         context_parts.append(f"- Date : {request.date_intervention}")
#     context = "\n".join(context_parts) if context_parts else ""
#
#     # Instructions anti-hallucination (communes à toutes les longueurs)
#     anti_hallucination = """RÈGLES ABSOLUES — INTERDICTION D'INVENTER :
# - Tu dois UNIQUEMENT reformuler ce que l'utilisateur a écrit dans sa description. Rien de plus.
# - N'ajoute JAMAIS d'étapes, d'actions ou de détails qui ne sont PAS explicitement écrits dans la description, même s'ils semblent logiques ou habituels pour ce type d'intervention.
# - Par exemple, si l'utilisateur dit "remplacement du robinet", tu ne dois PAS ajouter "diagnostic de l'installation", "recherche de la fuite", "raccordement", "contrôle d'étanchéité", "vérification du bon fonctionnement", etc. Tu ne mentionnes QUE "remplacement du robinet".
# - N'invente JAMAIS de marques, modèles, numéros de série, références, dimensions, mesures ou valeurs techniques.
# - N'invente JAMAIS de noms de techniciens, numéros de bon d'intervention ou références internes.
# - Si l'utilisateur donne peu de détails, le rapport doit être court. Ne comble JAMAIS le manque d'information par des détails inventés."""
#
#     longueur = request.longueur if request.longueur in ("court", "normal", "long") else "normal"
#
#     if longueur == "court":
#         instructions_longueur = """LONGUEUR : TRÈS COURT. Maximum 50 à 80 mots au total. Sois extrêmement bref et concis.
#
# RAPPEL CRITIQUE AVANT DE RÉDIGER :
# - Tu ne dois écrire QUE ce qui est explicitement dans la description ci-dessus.
# - N'ajoute AUCUNE étape, AUCUN diagnostic, AUCUNE vérification qui n'est pas mentionnée.
# - Si tu hésites entre ajouter un détail ou non : NE L'AJOUTE PAS.
#
# Format STRICT (3 paragraphes courts, PAS de listes à puces) :
#
# <strong>OBJET DE L'INTERVENTION :</strong>
# <p>[1 phrase reprenant le motif décrit par l'utilisateur]</p>
#
# <strong>TRAVAUX EFFECTUÉS :</strong>
# <p>[1 phrase résumant UNIQUEMENT les actions décrites par l'utilisateur, rien de plus]</p>
#
# <strong>RÉSULTAT :</strong>
# <p>[1 phrase simple confirmant la fin de l'intervention]</p>
#
# STOP. Rien d'autre. Pas d'observations, pas de recommandations, pas de listes détaillées."""
#
#     elif longueur == "long":
#         instructions_longueur = """Le rapport doit être TRÈS DÉTAILLÉ et COMPLET (environ 600-900 mots).
# Chaque section doit être développée avec précision. Ajoute des sous-sections si pertinent.
#
# Le rapport doit contenir ces sections avec des titres en <strong> et majuscules :
#
# <strong>MOTIF DE L'INTERVENTION :</strong>
# <p>[Description détaillée du problème signalé, contexte de la demande, basé uniquement sur la description fournie]</p>
#
# <strong>CONSTATATIONS SUR SITE :</strong>
# <p>[État des lieux à l'arrivée, observations visuelles, conditions d'accès — uniquement ce qui peut raisonnablement être déduit de la description]</p>
#
# <strong>DIAGNOSTIC :</strong>
# <p>[Analyse technique détaillée, cause identifiée du problème — basé sur la description fournie, sans inventer de mesures ou valeurs]</p>
#
# <strong>TRAVAUX RÉALISÉS :</strong>
# <ul>
# <li>[Action détaillée avec méthode employée]</li>
# <li>[...]</li>
# </ul>
#
# <strong>MATÉRIEL ET FOURNITURES :</strong>
# <p>[Mentionner uniquement le matériel explicitement cité dans la description. Si aucun matériel n'est mentionné, écrire "Matériel standard utilisé selon les besoins de l'intervention."]</p>
#
# <strong>TESTS ET VÉRIFICATIONS :</strong>
# <p>[Tests pertinents qui auraient logiquement été effectués pour ce type d'intervention, sans inventer de valeurs numériques]</p>
#
# <strong>RÉSULTAT ET ÉTAT FINAL :</strong>
# <p>[Description de l'état après intervention, validation du résultat]</p>
#
# <strong>OBSERVATIONS ET RECOMMANDATIONS :</strong>
# <p>[Conseils de maintenance préventive génériques et adaptés au type d'intervention, points de vigilance]</p>"""
#
#     else:  # normal
#         instructions_longueur = """Le rapport doit avoir une longueur NORMALE et ÉQUILIBRÉE (environ 300-500 mots).
#
# Le rapport doit contenir ces sections avec des titres en <strong> et majuscules :
#
# <strong>MOTIF DE L'INTERVENTION :</strong>
# <p>[Explication claire du problème signalé, basée uniquement sur la description fournie]</p>
#
# <strong>DIAGNOSTIC :</strong>
# <p>[Analyse technique, cause identifiée — basé sur la description, sans inventer de valeurs ou mesures]</p>
#
# <strong>TRAVAUX RÉALISÉS :</strong>
# <ul>
# <li>[Action effectuée avec détails basés sur la description]</li>
# <li>[...]</li>
# </ul>
#
# <strong>RÉSULTAT ET ÉTAT FINAL :</strong>
# <p>[Description de l'état après intervention]</p>
#
# <strong>OBSERVATIONS ET RECOMMANDATIONS :</strong>
# <p>[Conseils de maintenance préventive adaptés au type d'intervention]</p>"""
#
#     prompt = f"""Tu es un technicien expert rédigeant un rapport d'intervention professionnel en français.
#
# Informations sur l'intervention :
# - Type d'intervention : {request.type_intervention}
# - Description : {request.description}
# {context}
#
# {anti_hallucination}
#
# Génère un rapport d'intervention professionnel et structuré en HTML (sans balises <html>, <head>, <body>).
# Utilise uniquement des balises HTML inline simples : <p>, <strong>, <em>, <ul>, <ol>, <li>, <br>.
#
# IMPORTANT : Ne génère PAS d'en-tête ou de titre de rapport. Ne répète PAS les informations suivantes car elles sont déjà affichées dans le document : nom du client, adresse, date d'intervention, nom du technicien, nom de la société. Commence directement par les sections de contenu.
#
# {instructions_longueur}
#
# Adapte le vocabulaire technique au type d'intervention "{request.type_intervention}".
# Ne génère QUE le contenu HTML des sections ci-dessus, sans aucun texte avant ou après, sans blocs de code markdown, sans en-tête."""
#
#     return prompt
#
#
# def get_max_tokens_for_longueur(longueur: str) -> int:
#     """Retourne le max_tokens adapté à la longueur demandée."""
#     if longueur == "court":
#         return 150
#     elif longueur == "long":
#         return 4096
#     else:
#         return 2048
#
#
# class GenerateRapportResponse(BaseModel):
#     contenu: str
#
#
# @router.post("/generate-rapport", response_model=GenerateRapportResponse)
# async def generate_rapport(
#     request: GenerateRapportRequest,
#     current_user: User = Depends(deps.get_current_user)
# ):
#     """
#     Génère le contenu d'un rapport d'intervention via l'API Mistral AI.
#     """
#     if not settings.MISTRAL_API_KEY:
#         raise HTTPException(status_code=500, detail="Clé API Mistral non configurée")
#
#     # --- Validation de la saisie ---
#     validation_error = await validate_input_with_ai(request.type_intervention, request.description)
#     if validation_error:
#         raise HTTPException(status_code=400, detail=validation_error)
#
#     prompt = build_rapport_prompt(request)
#     max_tokens = get_max_tokens_for_longueur(request.longueur)
#
#     try:
#         async with httpx.AsyncClient(timeout=60.0) as client:
#             response = await client.post(
#                 "https://api.mistral.ai/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "model": "mistral-large-latest",
#                     "messages": [
#                         {
#                             "role": "user",
#                             "content": prompt
#                         }
#                     ],
#                     "temperature": 0.4,
#                     "max_tokens": max_tokens
#                 }
#             )
#
#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=502,
#                 detail=f"Erreur API Mistral : {response.text}"
#             )
#
#         data = response.json()
#         contenu = data["choices"][0]["message"]["content"].strip()
#
#         # Nettoyer les blocs de code markdown si présents
#         if contenu.startswith("```html"):
#             contenu = contenu[7:]
#         if contenu.startswith("```"):
#             contenu = contenu[3:]
#         if contenu.endswith("```"):
#             contenu = contenu[:-3]
#         contenu = contenu.strip()
#
#         return GenerateRapportResponse(contenu=contenu)
#
#     except httpx.TimeoutException:
#         raise HTTPException(status_code=504, detail="Délai d'attente dépassé lors de la génération IA")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {str(e)}")
#
#
# @router.post("/generate-rapport-stream")
# async def generate_rapport_stream(
#     request: GenerateRapportRequest,
#     current_user: User = Depends(deps.get_current_user)
# ):
#     """
#     Génère le contenu d'un rapport via Mistral AI en streaming SSE.
#     Chaque token est retransmis immédiatement au client via Server-Sent Events.
#     """
#     if not settings.MISTRAL_API_KEY:
#         raise HTTPException(status_code=500, detail="Clé API Mistral non configurée")
#
#     # --- Validation de la saisie ---
#     validation_error = await validate_input_with_ai(request.type_intervention, request.description)
#     if validation_error:
#         raise HTTPException(status_code=400, detail=validation_error)
#
#     prompt = build_rapport_prompt(request)
#     max_tokens = get_max_tokens_for_longueur(request.longueur)
#
#     async def event_stream():
#         try:
#             async with httpx.AsyncClient(timeout=120.0) as client:
#                 async with client.stream(
#                     "POST",
#                     "https://api.mistral.ai/v1/chat/completions",
#                     headers={
#                         "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": "mistral-large-latest",
#                         "messages": [{"role": "user", "content": prompt}],
#                         "temperature": 0.4,
#                         "max_tokens": max_tokens,
#                         "stream": True
#                     }
#                 ) as response:
#                     if response.status_code != 200:
#                         error_body = await response.aread()
#                         yield f"event: error\ndata: {error_body.decode()}\n\n"
#                         return
#
#                     async for line in response.aiter_lines():
#                         if not line.startswith("data: "):
#                             continue
#                         raw = line[6:]
#                         if raw == "[DONE]":
#                             yield "data: [DONE]\n\n"
#                             return
#                         try:
#                             chunk = json.loads(raw)
#                             delta = chunk["choices"][0]["delta"].get("content", "")
#                             if delta:
#                                 # Encoder le delta en JSON pour éviter les problèmes de sauts de ligne
#                                 yield f"data: {json.dumps(delta)}\n\n"
#                         except (json.JSONDecodeError, KeyError, IndexError):
#                             continue
#
#         except httpx.TimeoutException:
#             yield "event: error\ndata: timeout\n\n"
#         except Exception as e:
#             yield f"event: error\ndata: {str(e)}\n\n"
#
#     return StreamingResponse(
#         event_stream(),
#         media_type="text/event-stream",
#         headers={
#             "Cache-Control": "no-cache",
#             "X-Accel-Buffering": "no",
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import httpx
import json

from app.api import deps
from app.models.user import User
from app.core.config import settings
from app.core.rate_limit import limiter

router = APIRouter()

async def validate_input_with_ai(type_intervention: str, description: str) -> Optional[str]:
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
    nom_client: Optional[str] = None
    adresse: Optional[str] = None
    date_intervention: Optional[str] = None
    nom_technicien: Optional[str] = None


def build_rapport_prompt(request: GenerateRapportRequest) -> str:
    """
    Construit le prompt IA en fonction de la longueur choisie,
    avec des instructions anti-hallucination adaptées à chaque mode.
    """
    context_parts = []
    if request.nom_client:
        context_parts.append(f"- Client : {request.nom_client}")
    if request.adresse:
        context_parts.append(f"- Adresse d'intervention : {request.adresse}")
    if request.date_intervention:
        context_parts.append(f"- Date : {request.date_intervention}")
    if request.nom_technicien:
        context_parts.append(f"- Technicien : {request.nom_technicien}")
    context = "\n".join(context_parts) if context_parts else ""

    longueur = request.longueur if request.longueur in ("court", "normal", "long") else "normal"

    # --- Instructions anti-hallucination : version stricte (normal / long) ---
    anti_hallucination_strict = """RÈGLES ABSOLUES — INTERDICTION D'INVENTER :
- Tu dois UNIQUEMENT reformuler ce que l'utilisateur a écrit dans sa description. Rien de plus.
- N'ajoute JAMAIS d'étapes, d'actions ou de détails qui ne sont PAS explicitement écrits dans la description, même s'ils semblent logiques ou habituels pour ce type d'intervention.
- Par exemple, si l'utilisateur dit "remplacement du robinet", tu ne dois PAS ajouter "diagnostic de l'installation", "recherche de la fuite", "raccordement", "contrôle d'étanchéité", "vérification du bon fonctionnement", etc. Tu ne mentionnes QUE "remplacement du robinet".
- N'invente JAMAIS de marques, modèles, numéros de série, références, dimensions, mesures ou valeurs techniques.
- N'invente JAMAIS de noms de techniciens, numéros de bon d'intervention ou références internes.
- Si l'utilisateur donne peu de détails, le rapport doit être court. Ne comble JAMAIS le manque d'information par des détails inventés."""

    # --- Instructions anti-hallucination : version "déroulé métier" (mode court) ---
    anti_hallucination_metier = """RÈGLES — DÉROULÉ MÉTIER AUTORISÉ, DÉTAILS INVENTÉS INTERDITS :
- Tu peux décomposer l'action décrite par l'utilisateur en étapes logiques standards du métier pour ce type d'intervention (ex : "remplacement du robinet" peut donner diagnostic → dépose → pose → raccordement → contrôle).
- Ces étapes doivent rester GÉNÉRIQUES et correspondre au déroulé normal d'une telle action. Tu ne dois PAS aller au-delà de ce que l'action décrite implique logiquement (ex : ne mentionne pas un "remplacement de tuyauterie" si seul un robinet a été changé).
- En revanche, tu n'inventes JAMAIS de détails SPÉCIFIQUES non fournis : aucune marque, modèle, référence, dimension, mesure, durée précise, numéro de série.
- N'invente JAMAIS de noms de techniciens, numéros de bon d'intervention ou références internes autres que ceux fournis dans le contexte.
- Si la description est très vague ou ne correspond à aucune action métier reconnaissable, reste minimal plutôt que d'inventer un déroulé."""

    anti_hallucination = anti_hallucination_metier if longueur == "court" else anti_hallucination_strict

    if longueur == "court":
        instructions_longueur = """LONGUEUR : COURT. Le rapport doit rester concis (environ 80-150 mots), mais la section "Travaux effectués" doit lister les étapes métier du déroulé logique (voir règles ci-dessus), pas une seule ligne.

Le rapport doit contenir EXACTEMENT ces sections, avec des titres en <h3> :

<h3>Objet de l'intervention</h3>
<p>[1 phrase reprenant le motif décrit par l'utilisateur]</p>

<h3>Travaux effectués</h3>
<ul>
<li>[Étape 1 du déroulé métier]</li>
<li>[Étape 2 du déroulé métier]</li>
<li>[...]</li>
</ul>

<h3>Résultat de l'intervention</h3>
<p>[1 à 2 phrases confirmant la fin de l'intervention et son résultat, sans inventer de mesures]</p>

<h3>Observations</h3>
<p>[Soit "Aucune réserve particulière à signaler à l'issue de l'intervention." soit une remarque brève si pertinente. N'invente pas de recommandation détaillée.]</p>"""

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

    balises_autorisees = "<p>, <strong>, <em>, <ul>, <ol>, <li>, <br>, <h3>" if longueur == "court" else "<p>, <strong>, <em>, <ul>, <ol>, <li>, <br>"

    format_instructions = f"""Génère un rapport d'intervention professionnel et structuré en HTML (sans balises <html>, <head>, <body>).
Utilise uniquement des balises HTML inline simples : {balises_autorisees}.

IMPORTANT : Ne génère PAS d'en-tête ou de titre de rapport (pas de "RAPPORT D'INTERVENTION" en titre). Ne répète PAS les informations suivantes car elles sont déjà affichées ailleurs dans le document : nom du client, adresse, date d'intervention, nom du technicien, nom de la société. Ne génère AUCUN champ vide du type "Client :", "Adresse :", "Technicien :" — ces informations ne font pas partie du contenu à générer. Ne génère pas non plus de ligne de signature ou d'heure de fin, elles sont gérées séparément par le document. Commence directement par la première section de contenu."""

    prompt = f"""Tu es un technicien expert rédigeant un rapport d'intervention professionnel en français.

Informations sur l'intervention :
- Type d'intervention : {request.type_intervention}
- Description : {request.description}
{context}

{anti_hallucination}

{format_instructions}

{instructions_longueur}

Adapte le vocabulaire technique au type d'intervention "{request.type_intervention}".
Ne génère QUE le contenu demandé ci-dessus, sans aucun texte avant ou après, sans blocs de code markdown (pas de ```), sans commentaire."""

    return prompt


def get_max_tokens_for_longueur(longueur: str) -> int:
    """Retourne le max_tokens adapté à la longueur demandée."""
    if longueur == "court":
        return 350
    elif longueur == "long":
        return 4096
    else:
        return 2048


class GenerateRapportResponse(BaseModel):
    contenu: str


@router.post("/generate-rapport", response_model=GenerateRapportResponse)
@limiter.limit("20/hour")
async def generate_rapport(
    request: Request,
    payload: GenerateRapportRequest,
    current_user: User = Depends(deps.check_trial_active)
):
    """
    Génère le contenu d'un rapport d'intervention via l'API Mistral AI.
    """
    if not settings.MISTRAL_API_KEY:
        raise HTTPException(status_code=500, detail="Clé API Mistral non configurée")

    # --- Validation de la saisie ---
    validation_error = await validate_input_with_ai(payload.type_intervention, payload.description)
    if validation_error:
        raise HTTPException(status_code=400, detail=validation_error)

    prompt = build_rapport_prompt(payload)
    max_tokens = get_max_tokens_for_longueur(payload.longueur)

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

        # Nettoyer les blocs de code si le modèle en a quand même ajouté
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
@limiter.limit("20/hour")
async def generate_rapport_stream(
    request: Request,
    payload: GenerateRapportRequest,
    current_user: User = Depends(deps.check_trial_active)
):
    """
    Génère le contenu d'un rapport via Mistral AI en streaming SSE.
    Chaque token est retransmis immédiatement au client via Server-Sent Events.
    """
    if not settings.MISTRAL_API_KEY:
        raise HTTPException(status_code=500, detail="Clé API Mistral non configurée")

    # --- Validation de la saisie ---
    validation_error = await validate_input_with_ai(payload.type_intervention, payload.description)
    if validation_error:
        raise HTTPException(status_code=400, detail=validation_error)

    prompt = build_rapport_prompt(payload)
    max_tokens = get_max_tokens_for_longueur(payload.longueur)

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