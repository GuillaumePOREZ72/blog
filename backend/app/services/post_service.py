from typing import Optional, List, Dict, Any
from ..models.post import PostCreate, PostUpdate, PostResponse
from .database import get_database
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PostService:
    """Service de gestion des posts - Version simplifiée"""
    
    async def create_post(self, post_data: PostCreate) -> PostResponse:
        """Crée un nouveau post"""
        try:
            db = await get_database()
            posts_collection = db["posts"]
            
            # Convertir en dict et ajouter les timestamps
            post_dict = post_data.model_dump()
            post_dict["created_at"] = datetime.now()
            post_dict["updated_at"] = datetime.now()
            post_dict["is_published"] = post_dict.get("is_published", False)
            
            # Insérer en base
            result = await posts_collection.insert_one(post_dict)
            
            # Récupérer le post créé
            created_post = await posts_collection.find_one({"_id": result.inserted_id})
            
            logger.info(f"✅ Post créé: {created_post.get('title')}")
            return self._convert_to_response(created_post)
            
        except Exception as e:
            logger.error(f"❌ Erreur création post: {str(e)}")
            raise e
    
    async def get_post_by_id(self, post_id: str) -> Optional[PostResponse]:
        """Récupère un post par son ID"""
        try:
            if not ObjectId.is_valid(post_id):
                return None
            
            db = await get_database()
            posts_collection = db["posts"]
            
            post = await posts_collection.find_one({"_id": ObjectId(post_id)})
            
            if post:
                return self._convert_to_response(post)
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération post: {str(e)}")
            return None
    
    async def get_post_by_slug(self, slug: str) -> Optional[PostResponse]:
        """Récupère un post par son slug"""
        try:
            db = await get_database()
            posts_collection = db["posts"]
            
            post = await posts_collection.find_one({"slug": slug})
            
            if post:
                return self._convert_to_response(post)
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération post par slug: {str(e)}")
            return None
    
    async def get_posts(
        self,
        skip: int = 0,
        limit: int = 10,
        is_published: Optional[bool] = None,
        tag: Optional[str] = None,
        author_id: Optional[str] = None,
        current_user_id: Optional[str] = None
    ) -> List[PostResponse]:
        """Récupère les posts avec filtres"""
        try:
            db = await get_database()
            posts_collection = db["posts"]
            
            # Construire le filtre
            filter_dict = {}
            
            if is_published is not None:
                filter_dict["is_published"] = is_published
            
            if tag:
                filter_dict["tags"] = {"$in": [tag]}
            
            if author_id:
                filter_dict["author_id"] = author_id
            
            # Si pas d'utilisateur connecté, ne montrer que les posts publiés
            if not current_user_id and is_published is None:
                filter_dict["is_published"] = True
            
            cursor = posts_collection.find(filter_dict).sort("created_at", -1).skip(skip).limit(limit)
            posts = await cursor.to_list(length=limit)
            
            result = [self._convert_to_response(post) for post in posts]
            
            logger.info(f"✅ {len(result)} posts récupérés")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération posts: {str(e)}")
            return []
    
    async def get_posts_by_tag(self, tag: str, skip: int = 0, limit: int = 10) -> List[PostResponse]:
        """Récupère les posts par tag"""
        try:
            db = await get_database()
            posts_collection = db["posts"]
            
            cursor = posts_collection.find({
                "tags": {"$in": [tag]},
                "is_published": True
            }).sort("created_at", -1).skip(skip).limit(limit)
            
            posts = await cursor.to_list(length=limit)
            result = [self._convert_to_response(post) for post in posts]
            
            logger.info(f"✅ {len(result)} posts trouvés pour le tag '{tag}'")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération posts par tag: {str(e)}")
            return []
    
    async def update_post(self, post_id: str, post_update: PostUpdate) -> Optional[PostResponse]:
        """Met à jour un post"""
        try:
            if not ObjectId.is_valid(post_id):
                return None
            
            db = await get_database()
            posts_collection = db["posts"]
            
            # Préparer les données de mise à jour
            update_data = {k: v for k, v in post_update.model_dump().items() if v is not None}
            update_data["updated_at"] = datetime.now()
            
            # Mettre à jour
            result = await posts_collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                updated_post = await posts_collection.find_one({"_id": ObjectId(post_id)})
                return self._convert_to_response(updated_post)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour post: {str(e)}")
            return None
    
    async def delete_post(self, post_id: str) -> bool:
        """Supprime un post"""
        try:
            if not ObjectId.is_valid(post_id):
                return False
            
            db = await get_database()
            posts_collection = db["posts"]
            
            result = await posts_collection.delete_one({"_id": ObjectId(post_id)})
            
            logger.info(f"✅ Post supprimé: {post_id}")
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur suppression post: {str(e)}")
            return False
    
    def _convert_to_response(self, post_doc: dict) -> PostResponse:
        """Convertit un document MongoDB en PostResponse"""
        try:
            response_data = {
                "id": str(post_doc["_id"]),
                "title": post_doc["title"],
                "content": post_doc["content"],
                "slug": post_doc["slug"],
                "excerpt": post_doc.get("excerpt"),
                "tags": post_doc.get("tags", []),
                "is_published": post_doc.get("is_published", False),
                "author_id": post_doc["author_id"],
                "author_email": post_doc.get("author_email"),
                "featured_image": post_doc.get("featured_image"),
                "created_at": post_doc.get("created_at"),
                "updated_at": post_doc.get("updated_at")
            }
            
            return PostResponse(**response_data)
            
        except Exception as e:
            logger.error(f"❌ Erreur conversion document: {str(e)}")
            raise e

# Instance globale
post_service = PostService()