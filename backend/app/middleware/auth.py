from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import httpx
import os
from datetime import datetime

# Configuration Clerk
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_API_URL = "https://api.clerk.com/v1"

security = HTTPBearer()

class ClerkAuth:
    """Middleware d'authentification Clerk"""

    def __init__(self):
        if not CLERK_SECRET_KEY:
            raise ValueError("CLERK_SECRET_KEY environment variable is required")

    async def verify_token(self, token: str) -> dict:
        """Vérifie et décode le token Clerk"""
        headers = {
            "Authorization": f"Bearer {CLERK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{CLERK_API_URL}/sessions/{token}/verify",
                    headers=headers
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token invalide ou expiré"
                    )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erreur de connexion avec Clerk"
            )
    
    async def get_user_from_token(self, token: str) -> dict:
        """Récupère les informations utilisateur depuis le token"""
        session_data = await self.verify_token(token)
        user_id = session_data.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )

        headers = {
            "Authorization": f"Bearer {CLERK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{CLERK_API_URL}/users/{user_id}",
                    headers=headers
                )

                if response.status_code ==200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Utilisateur non trouvé"
                    )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erreur de connexion avec Clerk"
            )

# Instance globale du middleware
clerk_auth = ClerkAuth()

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Dépendance FastAPI pour récupérer l'utilisateur actuel"""
    token = credentials.credentials
    user_data = await clerk_auth.get_user_from_token(token)

    return {
        "clerk_id": user_data["id"],
        "email": user_data["email_addresses"][0]["email_address"],
        "username": user_data.get("username"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "profile_image": user_data.get("profile_image_url"),
        "last_sign_in": user_data.get("last_sign_in_at")
    }

async def get_current_active_user(
        current_user: dict = Depends(get_current_user)
) -> dict:
        """Dépendance pour récupérer uniquement les utilisateurs actifs"""
        return current_user

async def require_admin(
        current_user: dict = Depends(get_current_user)
) -> dict:
        """Dépendance pour les routes nécessitant des droits d'admin"""
        user_metadata = current_user.get("public_metadata", {})
        user_role = user_metadata.get("role", "user")

        if user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Droits administrateur requis"
            )
        return current_user

async def require_author_or_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Dépendance pour les routes nécessitant des droits auteur ou admin"""
    user_metadata = current_user.get("public_metadata", {})
    user_role = user_metadata.get("role", "user")

    if user_role not in ["author", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits auteur ou administrateur requis"
        )
    return current_user

async def get_optional_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """Dépendance optionnelle pour les routes publiques"""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

class SessionManager:
    """Gestionnaire de sessions pour optimiser les apples à Clerk"""

    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300 # 5 minutes

    async def get_cached_user(self, token: str) -> Optional[dict]:
        """Récupère un utilisateur depuis le cache"""
        cache_entry = self._cache.get(token)
        if cache_entry:
            timestamp, user_data = cache_entry
            if (datetime.utcnow().timestamp() - timestamp) < self._cache_ttl:
                return user_data
        return None
    
    async def cache_user(self, token: str, user_data: dict):
        """Met en cache les données utilisateur"""
        self._cache[token] = (datetime.utcnow().timestamp(), user_data)

    def clear_cache(self):
        """Vide le cache des sessions"""
        self._cache.clear()

# Instance du gestionnaire de sessions
session_manager = SessionManager()
