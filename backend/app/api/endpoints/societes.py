from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, Optional, Dict, List

from app.api.deps import get_db, get_current_user, is_admin, get_user_societe_id, require_permission, resoudre_acces_equipe
from app.models.societe import Societe
from app.models.user import User
from app.schemas.societe import SocieteCreate, SocieteRead, SocieteUpdate

router = APIRouter()

# Colonnes déclarées NOT NULL en base : elles ne doivent jamais recevoir None
# depuis une mise à jour partielle déguisée en objet complet.
COLONNES_NON_NULLABLES = {"nom", "relances_actives", "relances_jours"}


@router.get("/me", response_model=SocieteRead)
async def get_my_societe(
    db: AsyncSession = Depends(get_db),
    societe_id: int = Depends(get_user_societe_id),
) -> Any:
    """
    Récupérer la société de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Societe).where(Societe.id == societe_id)
    )
    societe = result.scalars().first()
    
    if not societe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune société trouvée pour cet utilisateur"
        )
    
    return societe

@router.put("/me", response_model=SocieteRead)
async def update_my_societe(
    societe_update: SocieteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("can_edit_societe")),
    societe_id: int = Depends(get_user_societe_id),
) -> Any:
    """
    Mettre à jour la société de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Societe).where(Societe.id == societe_id)
    )
    societe = result.scalars().first()
    
    if not societe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune société trouvée pour cet utilisateur"
        )
    
    # Mettre à jour tous les champs.
    # Ce PUT envoie l'objet complet : un client qui ignore un champ le
    # transmet à None. Pour les colonnes NOT NULL, on conserve alors la
    # valeur existante plutôt que de tenter d'y écrire NULL.
    for field, value in societe_update.model_dump().items():
        if value is None and field in COLONNES_NON_NULLABLES:
            continue
        setattr(societe, field, value)

    await db.commit()
    await db.refresh(societe)
    
    from app.core.websockets import manager
    await manager.broadcast_to_user(current_user.id, {
        "type": "SYNC_SOCIETE",
    })
    
    return societe

@router.patch("/me", response_model=SocieteRead)
async def patch_my_societe(
    societe_update: SocieteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("can_edit_societe")),
    societe_id: int = Depends(get_user_societe_id),
) -> Any:
    """
    Mettre à jour partiellement la société de l'utilisateur connecté.
    """
    result = await db.execute(
        select(Societe).where(Societe.id == societe_id)
    )
    societe = result.scalars().first()
    
    if not societe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune société trouvée pour cet utilisateur"
        )
    
    # Mettre à jour uniquement les champs fournis
    update_data = societe_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(societe, field, value)
    
    await db.commit()
    await db.refresh(societe)
    
    from app.core.websockets import manager
    await manager.broadcast_to_user(current_user.id, {
        "type": "SYNC_SOCIETE",
    })
    
    return societe

@router.post("", response_model=SocieteRead, status_code=status.HTTP_201_CREATED)
async def create_societe(
    societe_in: SocieteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Créer une nouvelle société pour l'utilisateur connecté.
    """
    from app.core.config import settings
    import httpx
    from sqlalchemy import func
    
    # Vérifier le nombre d'entreprises pour restreindre au plan Équipe
    result_count = await db.execute(select(func.count(Societe.id)).where(Societe.id_user == current_user.id))
    societe_count = result_count.scalar()
    
    # L'essai de 14 jours ouvre les fonctions Équipe : le rôle seul refusait la
    # deuxième entreprise à un artisan en train d'essayer le plan.
    if societe_count >= 1 and not await resoudre_acces_equipe(current_user, db):
        raise HTTPException(
            status_code=403,
            detail="Le plan Équipe est requis pour créer plusieurs entreprises."
        )
    
    if settings.ENVIRONMENT == "production" and current_user.role != "ADMIN":
        import re
        if not societe_in.siret:
            raise HTTPException(status_code=400, detail="Le SIRET est obligatoire en production.")
            
        siret_clean = societe_in.siret.replace(" ", "")
        if not re.match(r"^\d{14}$", siret_clean):
            raise HTTPException(status_code=400, detail="Le SIRET doit contenir exactement 14 chiffres.")
            
        async with httpx.AsyncClient() as client:
            res = await client.get(f"https://recherche-entreprises.api.gouv.fr/search?q={siret_clean}")
            if res.status_code != 200:
                raise HTTPException(status_code=400, detail="Erreur lors de la vérification du SIRET.")
            
            data = res.json()
            results = data.get("results", [])
            
            # Vérifier qu'au moins un résultat correspond exactement à ce SIRET (soit le siège, soit un établissement)
            siret_found = False
            for r in results:
                if r.get("siege", {}).get("siret") == siret_clean:
                    siret_found = True
                    break
                # Parcourir les établissements correspondants (matching_etablissements)
                for etablissement in r.get("matching_etablissements", []):
                    if etablissement.get("siret") == siret_clean:
                        siret_found = True
                        break
                if siret_found:
                    break
                    
            if not siret_found:
                raise HTTPException(status_code=400, detail="Ce SIRET est introuvable dans la base INSEE.")

    new_societe = Societe(
        id_user=current_user.id,
        **societe_in.model_dump()
    )
    db.add(new_societe)
    await db.commit()
    await db.refresh(new_societe)
    
    # Mettre à jour l'entreprise active de l'utilisateur
    current_user.active_societe_id = new_societe.id
    
    # Si c'est la première entreprise qu'il crée (ex: ancien collaborateur qui se lance),
    # on réinitialise sa date_inscription pour que ses 14 jours d'essai commencent maintenant.
    if societe_count == 0:
        from datetime import datetime, timezone
        current_user.date_inscription = datetime.now(timezone.utc)
        
    db.add(current_user)
    await db.commit()
    
    from app.core.websockets import manager
    await manager.broadcast_to_user(current_user.id, {
        "type": "SYNC_SOCIETE",
    })
    
    return new_societe

@router.get("/search-sirene")
async def search_sirene(
    q: str,
    code_postal: Optional[str] = None,
    per_page: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Rechercher des entreprises par nom commercial, raison sociale, nom du dirigeant ou SIRET/SIREN.
    """
    import httpx
    
    q_clean = q.strip()
    if len(q_clean) < 2:
        return {"results": [], "total_results": 0}
        
    # Si la recherche est un numéro avec des espaces (SIREN ou SIRET)
    clean_digits = q_clean.replace(" ", "")
    if clean_digits.isdigit() and len(clean_digits) in [9, 14]:
        q_search = clean_digits
    else:
        q_search = q_clean

    params: dict[str, Any] = {
        "q": q_search,
        "per_page": min(max(per_page, 1), 25)
    }
    
    if code_postal and code_postal.strip():
        cp_clean = code_postal.strip().replace(" ", "")
        if len(cp_clean) == 2:
            params["departement"] = cp_clean
        elif len(cp_clean) >= 4:
            params["code_postal"] = cp_clean

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"User-Agent": "ArtisanGestion/1.0"}
            res = await client.get(
                "https://recherche-entreprises.api.gouv.fr/search",
                params=params,
                headers=headers
            )
            
            if res.status_code != 200:
                return {"results": [], "total_results": 0}
                
            data = res.json()
            raw_results = data.get("results", [])
            total_results = data.get("total_results", len(raw_results))
            
            formatted_results = []
            for r in raw_results:
                siege = r.get("siege") or {}
                nom = r.get("nom_complet") or r.get("nom_raison_sociale") or r.get("sigle") or ""
                siren = r.get("siren") or ""
                siret = siege.get("siret") or ""
                
                # Si le siret n'est pas sur le siège mais dans matching_etablissements
                if not siret and r.get("matching_etablissements"):
                    siret = r["matching_etablissements"][0].get("siret", "")
                    
                # Adresse
                num_voie = siege.get("numero_voie") or ""
                type_voie = siege.get("type_voie") or ""
                libelle_voie = siege.get("libelle_voie") or ""
                adresse = siege.get("adresse") or f"{num_voie} {type_voie} {libelle_voie}".strip()
                code_postal_res = siege.get("code_postal") or ""
                ville_res = siege.get("libelle_commune") or ""
                
                # Forme juridique déduite
                nj = str(r.get("nature_juridique") or "")
                nom_lower = nom.lower()
                forme_juridique = "Auto-entrepreneur"
                
                if nj in ["5720"] or "sasu" in nom_lower or ("sas" in nom_lower and "unipersonnelle" in nom_lower):
                    forme_juridique = "SASU"
                elif nj in ["5710"] or "sas" in nom_lower or "actions simplifiée" in nom_lower:
                    forme_juridique = "SAS"
                elif nj in ["5498"] or "eurl" in nom_lower or ("sarl" in nom_lower and "unipersonnelle" in nom_lower):
                    forme_juridique = "EURL"
                elif nj in ["5499"] or "sarl" in nom_lower or "responsabilité limitée" in nom_lower:
                    forme_juridique = "SARL"
                elif nj in ["1000"] or r.get("complements", {}).get("est_entrepreneur_individuel") or "entrepreneur individuel" in nom_lower or "artisan" in nom_lower or "ei" in nom_lower:
                    forme_juridique = "Auto-entrepreneur"
                else:
                    forme_juridique = "Auto-entrepreneur"

                # Dirigeants
                dirigeants_raw = r.get("dirigeants") or []
                dirigeants_list = []
                for d in dirigeants_raw:
                    nom_d = f"{(d.get('prenoms') or '')} {(d.get('nom') or '')}".strip()
                    qualite = d.get("qualite") or ""
                    if nom_d:
                        dirigeants_list.append({"nom": nom_d, "qualite": qualite})
                        
                # TVA
                tva = None
                if r.get("tva") and len(r.get("tva")) > 0:
                    tva = r.get("tva")[0]
                    
                formatted_results.append({
                    "nom": nom,
                    "siren": siren,
                    "siret": siret,
                    "adresse": adresse,
                    "code_postal": code_postal_res,
                    "ville": ville_res,
                    "forme_juridique": forme_juridique,
                    "nature_juridique": nj,
                    "etat_administratif": r.get("etat_administratif") or siege.get("etat_administratif") or "A",
                    "activite_principale": r.get("activite_principale") or siege.get("activite_principale") or "",
                    "dirigeants": dirigeants_list,
                    "tva_intracommunautaire": tva,
                    "raw": r
                })
                
            return {
                "results": formatted_results,
                "total_results": total_results
            }
    except Exception as e:
        return {"results": [], "total_results": 0, "error": str(e)}

@router.get("/lookup-siret")
async def lookup_siret(
    siret: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Rechercher une entreprise par son SIRET via l'API INSEE.
    """
    import httpx
    import re
    
    siret_clean = siret.replace(" ", "")
    if not re.match(r"^\d{14}$", siret_clean):
        raise HTTPException(status_code=400, detail="Le SIRET doit contenir exactement 14 chiffres.")
        
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://recherche-entreprises.api.gouv.fr/search?q={siret_clean}")
        if res.status_code != 200:
            raise HTTPException(status_code=400, detail="Erreur lors de la vérification du SIRET.")
        
        data = res.json()
        results = data.get("results", [])
        
        # Trouver la correspondance exacte
        found = False
        result_match = None
        for r in results:
            if r.get("siege", {}).get("siret") == siret_clean:
                found = True
                result_match = r
                break
            for etablissement in r.get("matching_etablissements", []):
                if etablissement.get("siret") == siret_clean:
                    found = True
                    result_match = r
                    break
            if found:
                break
                
        if not found:
            raise HTTPException(status_code=400, detail="Ce SIRET est introuvable dans la base INSEE.")
            
        return {"results": [result_match]}


@router.delete("/me")
async def delete_my_societe(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    societe_id: int = Depends(get_user_societe_id),
) -> Any:
    """
    Supprimer la société active et toutes ses données associées (seulement si le compte est propriétaire et sans factures validées).
    """
    from sqlalchemy import delete, update
    from app.models.invitation import Invitation
    from app.models.client import Client
    from app.models.devis import Devis
    from app.models.facture import Facture
    from app.models.rapport import Rapport
    from app.models.ligne_facture import LigneFacture
    from app.models.ligne_devis import LigneDevis

    # 1. Vérifier que la société existe
    result = await db.execute(select(Societe).where(Societe.id == societe_id))
    societe = result.scalars().first()
    
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable.")
        
    # 2. Vérifier que l'utilisateur est le propriétaire (c'est lui qui l'a créée)
    if societe.id_user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Seul le propriétaire de l'entreprise peut la supprimer."
        )

    # 3. Conformité Légale : vérifier l'absence de factures validées/payées
    factures_validees_result = await db.execute(
        select(Facture.id).where(
            Facture.id_societe == societe_id,
            Facture.statut != "brouillon"
        ).limit(1)
    )
    has_valid_factures = factures_validees_result.scalars().first()
    if has_valid_factures:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer cette entreprise : des factures ont déjà été validées ou payées. Conformément à la loi anti-fraude à la TVA, ces documents comptables ne peuvent pas être détruits."
        )

    # --- SUPPRESSION EN CASCADE ---
    
    # 4. Détacher tous les utilisateurs (collaborateurs et propriétaires) ayant cette société en active_societe_id ou id_societe
    await db.execute(
        update(User).where(User.active_societe_id == societe_id).values(active_societe_id=None)
    )
    await db.execute(
        update(User).where(User.id_societe == societe_id).values(id_societe=None, is_owner=False)
    )
    if current_user.active_societe_id == societe_id:
        current_user.active_societe_id = None
    if current_user.id_societe == societe_id:
        current_user.id_societe = None
    
    # 5. Supprimer les invitations en attente
    await db.execute(delete(Invitation).where(Invitation.id_societe == societe_id))

    # 6. Supprimer les factures brouillons, leurs relances et leurs lignes
    factures_result = await db.execute(select(Facture.id).where(Facture.id_societe == societe_id))
    factures_ids = factures_result.scalars().all()
    if factures_ids:
        from app.models.relance import RelanceFacture
        await db.execute(delete(RelanceFacture).where(RelanceFacture.id_facture.in_(factures_ids)))
        await db.execute(delete(LigneFacture).where(LigneFacture.id_facture.in_(factures_ids)))
        await db.execute(delete(Facture).where(Facture.id_societe == societe_id))
        
    # 7. Supprimer les devis et leurs lignes
    devis_result = await db.execute(select(Devis.id).where(Devis.id_societe == societe_id))
    devis_ids = devis_result.scalars().all()
    if devis_ids:
        await db.execute(delete(LigneDevis).where(LigneDevis.id_devis.in_(devis_ids)))
        await db.execute(delete(Devis).where(Devis.id_societe == societe_id))

    # 8. Supprimer les autres documents
    await db.execute(delete(Rapport).where(Rapport.id_societe == societe_id))
    await db.execute(delete(Client).where(Client.id_societe == societe_id))
    
    # 9. Supprimer la société elle-même
    await db.execute(delete(Societe).where(Societe.id == societe_id))

    # 10. Re-assigner l'utilisateur actif à une autre société s'il en a une
    result_autres = await db.execute(
        select(Societe).where(Societe.id_user == current_user.id).order_by(Societe.id.desc())
    )
    autre_societe = result_autres.scalars().first()
    
    current_user.active_societe_id = autre_societe.id if autre_societe else None
    current_user.id_societe = autre_societe.id if autre_societe else None
    current_user.is_owner = True
    db.add(current_user)

    await db.commit()
    
    from app.core.websockets import manager
    await manager.broadcast_to_user(current_user.id, {
        "type": "SYNC_SOCIETE",
    })

    return {"status": "success", "message": "Entreprise supprimée avec succès."}
