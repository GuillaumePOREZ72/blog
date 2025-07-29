from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from typing import Optional, List
from datetime import datetime
import logging

from ..models.post import Post, PostCreate, PostUpdate, PostResponse
from .database import database


logger = logging.getLogger(__name__
                           )
class PostService:
    """Service de gestion des posts"""
    
    def __init__(self):
        pass

    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Récupère la collection posts"""
        return database.get_collection("posts")
    
    async def create_post(self, post_data: PostCreate, author_id: str) -> PostResponse:
        """Crée un nouveau post"""
        try:
            logger.info(f"🆕 Création post slug: {post_data.slug} par {author_id}")
            # Vérifier l'unicité du slug
            existing_post = await self.collection.find_one({"slug": post_data.slug})
            if existing_post:
                raise ValueError(f"Un post avec le slug '{post_data.slug}' existe déjà")
            
            # Créer le document post
            post_dict = post_data.model_dump()
            post_dict["author_id"] = author_id
            post_dict["created_at"] = datetime.utcnow()
            post_dict["updated_at"] = datetime.utcnow()
            post_dict["views"] = 0

            logger.info(f"📝 Insertion post en base: {post_dict['slug']}")
            result = await self.collection.insert_one(post_dict)
            
            # Récupérer le post créé
            created_post = await self.collection.find_one({"_id": result.inserted_id})
            logger.info(f"✅ Post créé avec ID: {result.inserted_id}")
            
            return self._to_post_response(created_post)
        
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"❌ Error creating post: {str(e)}")
            raise
    
    async def get_post_by_id(self, post_id: str) -> Optional[PostResponse]:
        """Récupère un post par son ID"""
        if not ObjectId.is_valid(post_id):
            return None
            
        post = await self.collection.find_one({"_id": ObjectId(post_id)})
        return self._to_post_response(post) if post else None
    
    async def get_post_by_slug(self, slug: str) -> Optional[PostResponse]:
        """Récupère un post par son slug"""
        try:
            post = await self.collection.find_one({"slug": slug})
            return self._to_post_response(post) if post else None
        
        except Exception as e:
            logger.error(f"Error getting post by slug: {str(e)}")
            return None    
    async def get_posts(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        is_published: Optional[bool] = None,
        tag: Optional[str] = None,
        author_id: Optional[str] = None,
        current_user_id: Optional[str] = None
    ) -> List[PostResponse]:
        """Récupère les posts avec pagination et filtres"""
        try:
            query = {}

            # Filtrer par statut de publication
            if is_published is not None:
                query["is_published"] = is_published

            # Filtrer par auteur
            if author_id:
                query["author_id"] = author_id

            # Filtrer par tag
            if tag:
                query["tags"] = {"$in": [tag]}

            logger.info(f"🔍 Recherche posts avec query: {query}")
            
            cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
            posts = await cursor.to_list(length=limit)
            
            logger.info(f"📋 {len(posts)} posts trouvés")
            return [self._to_post_response(post) for post in posts if self._to_post_response(post)]

        except Exception as e:
            logger.error(f"Error getting posts: {str(e)}")
            return []
    
    async def update_post(
        self, 
        slug: str, 
        post_update: PostUpdate, 
        author_id: str
    ) -> Optional[PostResponse]:
        """Met à jour un post par son slug"""
        try:
            # Vérifier que le post existe et appartient à l'auteur
            existing_post = await self.collection.find_one({
                "slug": slug
            })
            if not existing_post:
                return None
            
            # Vérifier l'unicité du slug si modifié
            if post_update.slug and post_update.slug != slug:
                slug_exists = await self.collection.find_one({
                    "slug": post_update.slug,
                    "_id": {"$ne": existing_post["_id"]}
                })
                if slug_exists:
                    raise ValueError(f"Un post avec le slug '{post_update.slug}' existe déjà")
            
            # Préparer les données de mise à jour
            update_data = {k: v for k, v in post_update.model_dump().items() if v is not None}
            
            if not update_data:
                return self._to_post_response(existing_post)
            
            update_data["updated_at"] = datetime.utcnow()
            
            # Effectuer la mise à jour
            await self.collection.update_one(
                {"slug": slug},
                {"$set": update_data}
            )
            
            # Récupérer le post mis à jour
            updated_post = await self.collection.find_one({"slug": post_update.slug or slug})
            return self._to_post_response(updated_post)
        
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating post: {str(e)}")
            return None
    
    async def update_post_by_id(self, post_id: str, post_update: PostUpdate) -> Optional[PostResponse]:
        """Met à jour un post par son ID"""
        try:
            if not ObjectId.is_valid(post_id):
                return None
                
            # Vérifier que le post existe
            existing_post = await self.collection.find_one({"_id": ObjectId(post_id)})
            if not existing_post:
                return None
            
            # Vérifier l'unicité du nouveau slug si modifié
            if post_update.slug and post_update.slug != existing_post.get("slug"):
                slug_exists = await self.collection.find_one({
                    "slug": post_update.slug,
                    "_id": {"$ne": ObjectId(post_id)}
                })
                if slug_exists:
                    raise ValueError(f"Un post avec le slug '{post_update.slug}' existe déjà")
            
            # Préparer les données de mise à jour
            update_data = {k: v for k, v in post_update.model_dump().items() if v is not None}
            
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
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating post by ID: {str(e)}")
            return None

    async def delete_post(self, slug: str) -> bool:
        """Supprime un post par son slug"""
        try:
            result = await self.collection.delete_one({
                "slug": slug
            })
            return result.deleted_count > 0

        except Exception as e:
            logger.error(f"Error deleting post: {str(e)}")
            return False
    
    async def delete_post_by_id(self, post_id: str) -> bool:
        """Supprime un post par son ID"""
        try:
            if not ObjectId.is_valid(post_id):
                return False
                
            result = await self.collection.delete_one({"_id": ObjectId(post_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting post by ID: {str(e)}")
            return False
    
    async def get_posts_by_tag(self, tag: str, skip: int = 0, limit: int = 10) -> List[PostResponse]:
        """Récupère les posts par tag"""
        try:
            cursor = self.collection.find({
                "tags": {"$in": [tag]},
                "is_published": True
            }).sort("created_at", -1).skip(skip).limit(limit)
            
            posts = await cursor.to_list(length=limit)
            return [self._to_post_response(post) for post in posts if self._to_post_response(post)]
            
        except Exception as e:
            logger.error(f"Error getting posts by tag: {str(e)}")
            return []
    
    def _to_post_response(self, post_doc: dict) -> Optional[PostResponse]:
        """Convertit un document MongoDB en PostResponse"""
        if not post_doc:
            return None

        try:
            # Créer une copie propre du document
            clean_doc = post_doc.copy()
            
            # Supprimer _id et ajouter id
            clean_doc["id"] = str(clean_doc.pop("_id"))
            
            # Gestion des champs optionnels
            if "tags" not in clean_doc:
                clean_doc["tags"] = []
            if "views" not in clean_doc:
                clean_doc["views"] = 0
            if "is_published" not in clean_doc:
                clean_doc["is_published"] = True
            
            return PostResponse(**clean_doc)
            
        except Exception as e:
            logger.error(f"Error converting post document: {str(e)}")
            logger.error(f"Document content: {post_doc}")
            return None

# Instance globale
post_service = PostService()