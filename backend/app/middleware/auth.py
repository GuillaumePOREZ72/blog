from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Récupère l'utilisateur connecté via token"""
    
    try:
        token = credentials.credentials
        logger.info(f"🔐 Token reçu: {token[:20]}...")
        
        # ✅ MODE TEST POUR DÉVELOPPEMENT
        if os.getenv("ENV") == "development" and token.startswith("test_"):
            logger.info("🧪 Using test token for development")
            return {
                "clerk_id": "user_swagger_test_123",
                "email": "swagger@test.com",
                "username": "swaggeruser",
                "first_name": "Swagger",
                "last_name": "Tester",
                "profile_image": "https://images.clerk.dev/swagger.jpg",
                "role": "admin",  # ✅ Rôle pour créer des posts
                "is_active": True
            }
        
        # TODO: Intégration avec Clerk pour les vrais tokens
        logger.warning(f"⚠️ Token non reconnu: {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide - Utilisez 'test_postman_token' pour le développement",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error validating token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erreur d'authentification",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Nécessite un rôle admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé - Droits admin requis"
        )
    return current_user

async def require_author_or_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Nécessite un rôle author ou admin pour créer des posts"""
    if current_user.get("role") not in ["author", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé - Droits author ou admin requis"
        )
    return current_user

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """Récupère l'utilisateur connecté (optionnel)"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
