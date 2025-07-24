from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

from ..models.post import Post, PostCreate, PostUpdate, PostResponse
from .database import database

class PostService:
    """Service de gestion des posts"""
    
    def __init__(self):
        self.collection: AsyncIOMotorCollection = database.get_database()["posts"]
    
    async def create_post(self, post_data: PostCreate, author_id: str) -> PostResponse:
        """Crée un nouveau post"""
        # Vérifier l'unicité du slug
        existing_post = await self.collection.find_one({"slug": post_data.slug})
        if existing_post:
            raise ValueError(f"Un post avec le slug '{post_data.slug}' existe déjà")
        
        # Créer le post
        post_dict = post_data.dict()
        post_dict["author_id"] = author_id
        post_dict["created_at"] = datetime.utcnow()
        post_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(post_dict)
        
        # Récupérer le post créé
        created_post = await self.collection.find_one({"_id": result.inserted_id})
        return self._to_post_response(created_post)
    
    async def get_post_by_id(self, post_id: str) -> Optional[PostResponse]:
        """Récupère un post par son ID"""
        if not ObjectId.is_valid(post_id):
            return None
            
        post = await self.collection.find_one({"_id": ObjectId(post_id)})
        return self._to_post_response(post) if post else None
    
    async def get_post_by_slug(self, slug: str) -> Optional[PostResponse]:
        """Récupère un post par son slug"""
        post = await self.collection.find_one({"slug": slug})
        return self._to_post_response(post) if post else None
    
    async def get_posts(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        published_only: bool = True,
        author_id: Optional[str] = None
    ) -> List[PostResponse]:
        """Récupère les posts avec pagination et filtres"""
        query = {}
        
        if published_only:
            query["is_published"] = True
            
        if author_id:
            query["author_id"] = author_id
        
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        posts = await cursor.to_list(length=limit)
        return [self._to_post_response(post) for post in posts]
    
    async def update_post(
        self, 
        post_id: str, 
        post_update: PostUpdate, 
        author_id: str
    ) -> Optional[PostResponse]:
        """Met à jour un post"""
        if not ObjectId.is_valid(post_id):
            return None
        
        # Vérifier que le post existe et appartient à l'auteur
        existing_post = await self.collection.find_one({
            "_id": ObjectId(post_id),
            "author_id": author_id
        })
        
        if not existing_post:
            return None
        
        # Vérifier l'unicité du slug si modifié
        if post_update.slug and post_update.slug != existing_post["slug"]:
            slug_exists = await self.collection.find_one({
                "slug": post_update.slug,
                "_id": {"$ne": ObjectId(post_id)}
            })
            if slug_exists:
                raise ValueError(f"Un post avec le slug '{post_update.slug}' existe déjà")
        
        # Préparer les données de mise à jour
        update_data = {k: v for k, v in post_update.dict().items() if v is not None}
        
        if not update_data:
            return self._to_post_response(existing_post)
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Effectuer la mise à jour
        await self.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )
        
        # Récupérer le post mis à jour
        updated_post = await self.collection.find_one({"_id": ObjectId(post_id)})
        return self._to_post_response(updated_post)
    
    async def delete_post(self, post_id: str, author_id: str) -> bool:
        """Supprime un post"""
        if not ObjectId.is_valid(post_id):
            return False
        
        result = await self.collection.delete_one({
            "_id": ObjectId(post_id),
            "author_id": author_id
        })
        
        return result.deleted_count > 0
    
    async def get_posts_by_tag(self, tag: str, skip: int = 0, limit: int = 10) -> List[PostResponse]:
        """Récupère les posts par tag"""
        cursor = self.collection.find({
            "tags": tag,
            "is_published": True
        }).sort("created_at", -1).skip(skip).limit(limit)
        
        posts = await cursor.to_list(length=limit)
        return [self._to_post_response(post) for post in posts]
    
    def _to_post_response(self, post_doc: dict) -> PostResponse:
        """Convertit un document MongoDB en PostResponse"""
        if not post_doc:
            return None
            
        post_doc["id"] = str(post_doc["_id"])
        return PostResponse(**post_doc)

# Instance globale
post_service = PostService()