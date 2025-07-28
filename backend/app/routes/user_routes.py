from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import List, Optional
import logging
import hmac
import hashlib

from ..models.user import UserCreate, UserUpdate, UserResponse, UserLogin
from ..services.user_service import user_service
from ..middleware.auth import (
    get_current_user,
    require_admin,
    get_optional_user
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/webhook", status_code=200)
async def clerk_webhook(request: Request):
    """Webhook Clerk pour synchroniser les utilisateurs"""
    try:
        # Récupérer la signature Clerk
        signature = request.headers.get("svix-signature")
        if not signature:
            raise HTTPException(status_code=400, detail="Signature manquante")
        
        # Récupérer le body de la requête
        body = await request.body()
        
        # TODO: Vérifier la signature Clerk (implémentation sécurisée)
        # webhook_secret = os.getenv("CLERK_WEBHOOK_SECRET")
        # if not verify_webhook_signature(body, signature, webhook_secret):
        #     raise HTTPException(status_code=400, detail="Signature invalide")
        
        # Parser les données JSON
        import json
        event_data = json.loads(body)
        
        event_type = event_data.get("type")
        user_data = event_data.get("data")
        
        if event_type == "user.created":
            # Créer l'utilisateur en base
            user_create = UserCreate(
                clerk_id=user_data["id"],
                email=user_data["email_addresses"][0]["email_address"],
                username=user_data.get("username"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                profile_image=user_data.get("profile_image_url")
            )
            
            new_user = await user_service.create_user(user_create)
            logger.info(f"Utilisateur créé via webhook: {new_user.clerk_id}")
            
        elif event_type == "user.updated":
            # Mettre à jour l'utilisateur
            user_update = UserUpdate(
                username=user_data.get("username"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                profile_image=user_data.get("profile_image_url")
            )
            
            updated_user = await user_service.update_user(user_data["id"], user_update)
            if updated_user:
                logger.info(f"Utilisateur mis à jour via webhook: {updated_user.clerk_id}")
            
        elif event_type == "user.deleted":
            # Désactiver l'utilisateur (soft delete)
            deactivated = await user_service.deactivate_user(user_data["id"])
            if deactivated:
                logger.info(f"Utilisateur désactivé via webhook: {user_data['id']}")
        
        return {"status": "success"}
        
    except json.JSONDecodeError:
        logger.error("Erreur parsing JSON webhook")
        raise HTTPException(status_code=400, detail="JSON invalide")
    except Exception as e:
        logger.error(f"Erreur webhook Clerk: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """Récupère le profil de l'utilisateur connecté"""
    try:
        user = await user_service.get_user_by_clerk_id(current_user["clerk_id"])
        
        if not user:
            # Créer l'utilisateur s'il n'existe pas en base
            user_create = UserCreate(
                clerk_id=current_user["clerk_id"],
                email=current_user["email"],
                username=current_user.get("username"),
                first_name=current_user.get("first_name"),
                last_name=current_user.get("last_name"),
                profile_image=current_user.get("profile_image")
            )
            user = await user_service.create_user(user_create)
            logger.info(f"Utilisateur créé automatiquement: {user.clerk_id}")
        
        # Mettre à jour la dernière connexion
        await user_service.update_last_login(current_user["clerk_id"])
        
        logger.info(f"Profil récupéré pour: {user.clerk_id}")
        return user
        
    except Exception as e:
        logger.error(f"Erreur récupération profil: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Met à jour le profil de l'utilisateur connecté"""
    try:
        updated_user = await user_service.update_user(
            clerk_id=current_user["clerk_id"],
            user_update=user_update
        )
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        logger.info(f"Profil mis à jour pour: {updated_user.clerk_id}")
        return updated_user
        
    except ValueError as e:
        logger.error(f"Erreur validation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur mise à jour profil: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="Nombre d'utilisateurs à ignorer"),
    limit: int = Query(50, ge=1, le=100, description="Nombre maximum d'utilisateurs"),
    current_user: dict = Depends(require_admin)
):
    """Liste tous les utilisateurs (admin uniquement)"""
    try:
        users = await user_service.get_all_users(skip=skip, limit=limit)
        logger.info(f"Liste utilisateurs récupérée: {len(users)} utilisateurs")
        return users
        
    except Exception as e:
        logger.error(f"Erreur récupération utilisateurs: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(require_admin)
):
    """Récupère un utilisateur par son ID (admin uniquement)"""
    try:
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        logger.info(f"Utilisateur récupéré: {user_id}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération utilisateur: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_by_admin(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(require_admin)
):
    """Met à jour un utilisateur (admin uniquement)"""
    try:
        # Récupérer l'utilisateur d'abord
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Mettre à jour
        updated_user = await user_service.update_user(
            clerk_id=user.clerk_id,
            user_update=user_update
        )
        
        logger.info(f"Utilisateur mis à jour par admin: {user_id}")
        return updated_user
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erreur validation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur mise à jour utilisateur: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/{user_id}", status_code=204)
async def deactivate_user_by_admin(
    user_id: str,
    current_user: dict = Depends(require_admin)
):
    """Désactive un utilisateur (admin uniquement)"""
    try:
        # Récupérer l'utilisateur d'abord
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Désactiver
        deactivated = await user_service.deactivate_user(user.clerk_id)
        
        if not deactivated:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        logger.info(f"Utilisateur désactivé par admin: {user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur désactivation utilisateur: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/login", status_code=200)
async def track_user_login(
    login_data: UserLogin,
    current_user: dict = Depends(get_current_user)
):
    """Trace une connexion utilisateur"""
    try:
        # Vérifier que l'utilisateur connecté correspond
        if current_user["clerk_id"] != login_data.clerk_id:
            raise HTTPException(status_code=403, detail="Non autorisé")
        
        # Mettre à jour la dernière connexion
        updated = await user_service.update_last_login(login_data.clerk_id)
        
        if updated:
            logger.info(f"Connexion tracée pour: {login_data.clerk_id}")
        
        return {"status": "success", "message": "Connexion tracée"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur trace connexion: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")