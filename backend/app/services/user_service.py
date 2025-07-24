from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

from ..models.user import User, UserCreate, UserUpdate, UserResponse
from .database import database


class UserService:
    """Service de gestion des utilisateurs"""

    def __init__(self):
        self.collection: AsyncIOMotorCollection = database.get_database()["users"]

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Crée un nouvel utilisateur"""
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = await self.collection.find_one({"clerk_id": user_data.clerk_id})
            if existing_user:
                raise ValueError(f"Utilisateur avec clerk_id {user_data.clerk_id} existe déjà.")
            
            # Créer l'utilisateur
            user_dict = user_data.dict()
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
        
    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[UserResponse]:
        """Récupère un utilisateur par son clerk_id"""
        user = await self.collection.find_one({"clerk_id": clerk_id})
        return self._to_user_response(user) if user else None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Récupère un utilisateur par son ID MongoDB"""
        if not ObjectId.is_valid(user_id):
            return None
        
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return self._to_user_response(user) if user else None
    
     async def update_user(self, clerk_id: str, user_update: UserUpdate) -> Optional[UserResponse]:
        """Met à jour un utilisateur"""
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        
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
    
    async def update_last_login(self, clerk_id: str) -> bool:
        """Met à jour la dernière connexion"""
        result = await self.collection.update_one(
            {"clerk_id": clerk_id},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    async def deactivate_user(self, clerk_id: str) -> bool:
        """Désactive un utilisateur"""
        result = await self.collection.update_one(
            {"clerk_id": clerk_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Récupère tous les utilisateurs avec pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        return [self._to_user_response(user) for user in users]
    
    def _to_user_response(self, user_doc: dict) -> UserResponse:
        """Convertit un document MongoDB en UserResponse"""
        if not user_doc:
            return None
        
        user_doc["id"] = str(user_doc["_id"])
        return UserResponse(**user_doc)

# Instance globale
user_service = UserService()