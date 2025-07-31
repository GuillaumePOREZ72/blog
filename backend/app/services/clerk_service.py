import os
import jwt
import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import logging
from datetime import datetime


logger = logging.getLogger(__name__)

class ClerkService:
    """Service d'authentification Clerk - Version simplifiée pour développement"""

    def __init__(self):
        self.secret_key = os.getenv("CLERK_SECRET_KEY")
        self.publishable_key = os.getenv("CLERK_PUBLISHABLE_KEY")

        if not self.secret_key:
            logger.warning("⚠️ CLERK_SECRET_KEY manquante")

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Vérifie un token JWT Clerk - Version développement"""
        try:
            # Tokens de test acceptés en mode développement
            if token.startswith("test"):
                logger.info("🧪 Mode développement - Token de test")
                return {
                    "clerk_id": "user_test_123",
                    "email": "test@example.com",
                    "username": "testuser",
                    "first_name": "Test",
                    "last_name": "User",
                    "role": "admin" if "admin" in token else "user",
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                }

            # Validation basique pour vrais tokens Clerk
            if not self.secret_key:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Configuration Clerk manquante"
                )

            # Pour l'instant, validation simplifiée
            # TODO: Implémenter validation JWT complète plus tard
            try:
                # Décoder sans vérification pour récupérer l'ID utilisateur
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get("sub")

                if user_id:
                    # Récupérer infos depuis API Clerk
                    user_info = await self.get_user_from_api(user_id)
                    return user_info
                else:
                    raise HTTPException(status_code=401, detail="Token invalide")

            except Exception:
                raise HTTPException(status_code=401, detail="Token invalide")

        except HTTPException:
            raise
        except Exception as e:
            logger.info(f"❌ Erreur validation token: {str(e)}")
            raise HTTPException(status_code=401, detail="Erreur authentification")

    async def get_user_from_api(self, clerk_user_id: str) -> Dict[str, Any]:
        """Récupère utilisateur depuis API Clerk"""
        try:
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            }

            response = requests.get(
                f"https://api.clerk.dev/v1/users/{clerk_user_id}",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                user_data = response.json()

                # Extraire email primaire
                email_addresses = user_data.get("email_addresses", [])
                primary_email = email_addresses[0]["email_address"] if email_addresses else None

                return {
                    "clerk_id": user_data["id"],
                    "email": primary_email,
                    "username": user_data.get("username"),
                    "first_name": user_data.get("first_name"),
                    "last_name": user_data.get("last_name"),
                    "profile_image": user_data.get("profile_image_url"),
                    "role": "user",  # Par défaut
                    "is_active": True
                }
            else:
                raise HTTPException(status_code=401, detail="Utilisateur non trouvé")

        except requests.RequestException:
            raise HTTPException(status_code=500, detail="Erreur service Clerk")

# Instance globale
clerk_service = ClerkService()