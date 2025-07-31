from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import List, Optional
import logging
import json

from ..models.user import UserCreate, UserUpdate, UserResponse
from ..services.user_service import user_service
from ..middleware.auth import get_current_user, get_optional_user, get_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["👥 Users"])

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate):
    """✅ Créer un nouvel utilisateur"""
    try:
        logger.info(f"Création utilisateur: {user_data.clerk_id}")

        # Vérifier si l'utilisateur existe déjà
        existing_user = await user_service.get_user_by_clerk_id(user_data.clerk_id)
        if existing_user:
            logger.warning(f"Utilisateur déjà existant: {user_data.clerk_id}")
            raise HTTPException(status_code=409, detail="Utilisateur existe déjà")

        # Créer l'utilisateur
        new_user = await user_service.create_user(user_data)
        logger.info(f"✅ Utilisateur créé: {new_user.id}")
        return new_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur création: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """📱 Récupère le profil de l'utilisateur connecté"""
    try:
        logger.info(f"🔍 Profil demandé: {current_user.get('clerk_id')}")
        
        user = await user_service.get_user_by_clerk_id(current_user["clerk_id"])
        
        if not user:
            # Créer l'utilisateur s'il n'existe pas
            user_create = UserCreate(
                clerk_id=current_user["clerk_id"],
                email=current_user["email"],
                username=current_user.get("username"),
                first_name=current_user.get("first_name"),
                last_name=current_user.get("last_name"),
                profile_image=current_user.get("profile_image")
            )
            user = await user_service.create_user(user_create)
            logger.info(f"✅ Utilisateur créé automatiquement: {user.clerk_id}")
        
        logger.info(f"✅ Profil récupéré: {user.clerk_id}")
        return user
        
    except Exception as e:
        logger.error(f"❌ Erreur profil: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """🔄 Met à jour le profil de l'utilisateur connecté"""
    try:
        logger.info(f"🔄 Mise à jour profil: {current_user.get('clerk_id')}")
        
        updated_user = await user_service.update_user(
            clerk_id=current_user["clerk_id"],
            user_update=user_update
        )
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        logger.info(f"✅ Profil mis à jour: {updated_user.clerk_id}")
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# =====================================
# 👑 ROUTES ADMIN
# =====================================

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="Nombre d'utilisateurs à ignorer"),
    limit: int = Query(50, ge=1, le=100, description="Nombre maximum d'utilisateurs"),
    current_user: dict = Depends(get_admin_user)
):
    """👑 Liste tous les utilisateurs (admin uniquement)"""
    try:
        logger.info(f"📋 Liste demandée par admin: {current_user.get('clerk_id')}")
        
        users = await user_service.get_all_users(skip=skip, limit=limit)
        logger.info(f"✅ {len(users)} utilisateurs récupérés")
        return users
        
    except Exception as e:
        logger.error(f"❌ Erreur liste: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """👑 Récupère un utilisateur par ID (admin uniquement)"""
    try:
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        logger.info(f"✅ Utilisateur récupéré: {user_id}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur récupération: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@router.delete("/{user_id}", status_code=204)
async def deactivate_user_by_admin(
    user_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """👑 Désactive un utilisateur (admin uniquement)"""
    try:
        logger.info(f"🗑️ Désactivation par admin: {user_id}")
        
        # Récupérer l'utilisateur d'abord
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Désactiver
        deactivated = await user_service.deactivate_user(user.clerk_id)
        
        if not deactivated:
            raise HTTPException(status_code=404, detail="Erreur désactivation")
        
        logger.info(f"✅ Utilisateur désactivé: {user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur désactivation: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur serveur")