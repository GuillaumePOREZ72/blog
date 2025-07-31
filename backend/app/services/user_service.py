from typing import Optional, List
from ..services.database import get_database
from ..models.user import UserCreate, UserUpdate, UserResponse
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service de gestion des utilisateurs - Version simplifiée"""
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Crée un nouvel utilisateur"""
        try:
            db = await get_database()
            users_collection = db["users"]
            
            # Convertir en dict et ajouter les timestamps
            user_dict = user_data.model_dump()
            user_dict["created_at"] = datetime.now()
            user_dict["updated_at"] = datetime.now()
            user_dict["is_active"] = True
            
            # Insérer en base
            result = await users_collection.insert_one(user_dict)
            
            # Récupérer l'utilisateur créé
            created_user = await users_collection.find_one({"_id": result.inserted_id})
            
            logger.info(f"✅ Utilisateur créé: {created_user.get('email')}")
            return self._convert_to_response(created_user)
            
        except Exception as e:
            logger.error(f"❌ Erreur création utilisateur: {str(e)}")
            raise e
    
    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[UserResponse]:
        """Récupère un utilisateur par son clerk_id"""
        try:
            db = await get_database()
            users_collection = db["users"]
            
            user = await users_collection.find_one({"clerk_id": clerk_id})
            
            if user:
                return self._convert_to_response(user)
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération utilisateur par clerk_id: {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Récupère un utilisateur par son ID MongoDB"""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            db = await get_database()
            users_collection = db["users"]
            
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
            
            if user:
                return self._convert_to_response(user)
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération utilisateur par ID: {str(e)}")
            return None
    
    async def update_user(self, clerk_id: str, user_update: UserUpdate) -> Optional[UserResponse]:
        """Met à jour un utilisateur par clerk_id"""
        try:
            db = await get_database()
            users_collection = db["users"]
            
            # Préparer les données de mise à jour
            update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
            update_data["updated_at"] = datetime.now()
            
            # Mettre à jour
            result = await users_collection.update_one(
                {"clerk_id": clerk_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Récupérer l'utilisateur mis à jour
                updated_user = await users_collection.find_one({"clerk_id": clerk_id})
                return self._convert_to_response(updated_user)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour utilisateur: {str(e)}")
            return None
    
    async def deactivate_user(self, clerk_id: str) -> bool:
        """Désactive un utilisateur"""
        try:
            db = await get_database()
            users_collection = db["users"]
            
            result = await users_collection.update_one(
                {"clerk_id": clerk_id},
                {"$set": {"is_active": False, "updated_at": datetime.now()}}
            )
            
            logger.info(f"✅ Utilisateur désactivé: {clerk_id}")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur désactivation utilisateur: {str(e)}")
            return False
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Récupère tous les utilisateurs avec pagination"""
        try:
            db = await get_database()
            users_collection = db["users"]
            
            cursor = users_collection.find({"is_active": True}).skip(skip).limit(limit)
            users = await cursor.to_list(length=limit)
            
            result = [self._convert_to_response(user) for user in users]
            
            logger.info(f"✅ {len(result)} utilisateurs récupérés")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération utilisateurs: {str(e)}")
            return []
    
    def _convert_to_response(self, user_doc: dict) -> UserResponse:
        """Convertit un document MongoDB en UserResponse"""
        try:
            # Préparer les données pour UserResponse
            response_data = {
                "id": str(user_doc["_id"]),
                "clerk_id": user_doc["clerk_id"],
                "email": user_doc["email"],
                "username": user_doc.get("username"),
                "first_name": user_doc.get("first_name"),
                "last_name": user_doc.get("last_name"),
                "profile_image": user_doc.get("profile_image"),
                "role": user_doc.get("role", "user"),
                "is_active": user_doc.get("is_active", True),
                "created_at": user_doc.get("created_at"),
                "updated_at": user_doc.get("updated_at")
            }
            
            return UserResponse(**response_data)
            
        except Exception as e:
            logger.error(f"❌ Erreur conversion document: {str(e)}")
            raise e

# Instance globale
user_service = UserService()