from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging
from ..services.clerk_service import clerk_service

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    🔐 Middleware d'authentification Clerk
    
    Valide le token et retourne les infos utilisateur
    """
    try:
        token = credentials.credentials
        logger.info(f"🔐 Validation token: {token[:20]}...")

        user_info = await clerk_service.verify_token(token)

        logger.info(f"✅ Utilisateur authentifié: {user_info.get('email', 'unknown')}")
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur authentification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """🔐 Middleware admin uniquement"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            deyail="Accès administrateur requis"
        )

    return current_user

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """🔓 Middleware optionnel - peut être None"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_info = await clerk_service.verify_token(token)
        return user_info
    except HTTPException:
        return None
