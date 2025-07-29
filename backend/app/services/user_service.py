from motor.motor_asyncio import AsyncIOMotorCollection
from ..services.database import database
from ..models.user import User, UserCreate, UserUpdate, UserResponse
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service de gestion des utilisateurs"""

    def __init__(self):
        # La collection sera récupérée dynamiquement
        pass

    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Récupère la collection users"""
        return database.get_collection("users")

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Crée un nouvel utilisateur"""
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = await self.collection.find_one({"clerk_id": user_data.clerk_id})
            if existing_user:
                raise ValueError(f"Utilisateur avec clerk_id {user_data.clerk_id} existe déjà.")
            
            # Créer l'utilisateur
            user_dict = user_data.model_dump()
            user_dict["created_at"] = datetime.utcnow()
            user_dict["updated_at"] = datetime.utcnow()
            user_dict["is_active"] = True
            user_dict["role"] = "user" # rôle par défaut

            result = await self.collection.insert_one(user_dict)

            # Récupérer l'utilisateur créé
            created_user = await self.collection.find_one({"_id": result.inserted_id})
            return self._to_user_response(created_user)
    
        except DuplicateKeyError:
            raise ValueError("Utilisateur déjà existant")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
        
    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[UserResponse]:
        """Récupère un utilisateur par son clerk_id"""
        try:
            user = await self.collection.find_one({"clerk_id": clerk_id})
            return self._to_user_response(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by clerk_id: {str(e)}")
            return None
    
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Récupère un utilisateur par son ID MongoDB"""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            return self._to_user_response(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by id: {str(e)}")
            return None
    
    async def update_user(self, clerk_id: str, user_update: UserUpdate) -> Optional[UserResponse]:
        """Met à jour un utilisateur"""
        try:
            update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}  # ✅ model_dump()
            
            if not update_data:
                # Rien à mettre à jour
                return await self.get_user_by_clerk_id(clerk_id)
            
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"clerk_id": clerk_id},
                {"$set": update_data}
            )
            
            if result.modified_count:
                return await self.get_user_by_clerk_id(clerk_id)
            return None
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return None
    
    async def update_last_login(self, clerk_id: str) -> bool:
        """Met à jour la dernière connexion"""
        try:
            result = await self.collection.update_one(
                {"clerk_id": clerk_id},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            return False
    
    
    async def deactivate_user(self, clerk_id: str) -> bool:
        """Désactive un utilisateur"""
        try:
            result = await self.collection.update_one(
                {"clerk_id": clerk_id},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            return False
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Récupère tous les utilisateurs avec pagination"""
        try:
            cursor = self.collection.find().skip(skip).limit(limit)
            users = await cursor.to_list(length=limit)
            return [self._to_user_response(user) for user in users]
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []
    
    def _to_user_response(self, user_doc: dict) -> Optional[UserResponse]:
        """Convertit un document MongoDB en UserResponse"""
        if not user_doc:
            return None
        
        try:
            user_doc["id"] = str(user_doc["_id"])
            return UserResponse(**user_doc)
        except Exception as e:
            logger.error(f"Error converting user document: {str(e)}")
            return None

# Instance globale
user_service = UserService()