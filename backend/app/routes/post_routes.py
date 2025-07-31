from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from ..services.post_service import post_service
from ..services.database import get_database
from ..models.post import PostCreate, PostUpdate, PostResponse
from ..middleware.auth import get_current_user, get_admin_user, get_optional_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["📝 Posts"])

# =====================================
# 🔐 ROUTES PROTÉGÉES (CRUD)
# =====================================

@router.post("/", response_model=dict)
async def create_post(
    post: PostCreate,
    current_user: dict = Depends(get_current_user)
):
    """✅ Créer un nouveau post - AUTHENTIFICATION REQUISE"""
    try:
        # Ajouter l'auteur automatiquement
        post_data = post.model_dump()
        post_data["author_id"] = current_user.get("clerk_id")
        post_data["author_email"] = current_user.get("email")
        post_data["created_at"] = datetime.now()
        post_data["updated_at"] = datetime.now()

        db = await get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Base de données non disponible")
        
        posts_collection = db["posts"]

        result = await posts_collection.insert_one(post_data)

        return {
            "success": True,
            "message": "Post créé avec succès",
            "post_id": str(result.inserted_id),
            "author": current_user.get("email")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur création post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{post_id}")
async def update_post(
    post_id: str, 
    post_update: PostUpdate,
    current_user: dict = Depends(get_current_user)
):
    """🔄 Mettre à jour un post - AUTHENTIFICATION REQUISE"""
    try:
        db = await get_database()
        posts_collection = db["posts"]
        
        # Vérifier que le post existe et que l'utilisateur est propriétaire
        existing_post = await posts_collection.find_one({"_id": ObjectId(post_id)})
        
        if not existing_post:
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        # Vérifier les permissions (auteur ou admin)
        if existing_post.get("author_id") != current_user.get("clerk_id"):
            raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres posts")

        update_data = {k: v for k, v in post_update.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.now()

        await posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )      
        
        logger.info(f"✅ Post mis à jour: {post_id}")
        return {"success": True, "message": "Post mis à jour"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{post_id}")  # ✅ /posts/{id} au lieu de /posts/posts/{id}
async def delete_post(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    """🗑️ Supprimer un post - AUTHENTIFICATION REQUISE"""
    try:
        db = await get_database()
        posts_collection = db["posts"]
        
        # Vérifier propriétaire
        existing_post = await posts_collection.find_one({"_id": ObjectId(post_id)})
        
        if not existing_post:
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        if existing_post.get("author_id") != current_user.get("clerk_id"):
            raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres posts")
        
        await posts_collection.delete_one({"_id": ObjectId(post_id)})
        
        logger.info(f"✅ Post supprimé: {post_id}")
        return {"success": True, "message": "Post supprimé"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur suppression post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================
# 📖 ROUTES PUBLIQUES (LECTURE)
# =====================================

@router.get("/", response_model=List[PostResponse])
async def list_posts(
    skip: int = Query(0, ge=0, description="Nombre de posts à ignorer"),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum de posts"),
    is_published: Optional[bool] = Query(None, description="Filtrer par statut de publication"),
    tag: Optional[str] = Query(None, description="Filtrer par tag"),
    author_id: Optional[str] = Query(None, description="Filtrer par auteur"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """📋 Lister les posts avec filtres"""
    try:
        logger.info(f"📋 Liste posts demandée par: {current_user.get('clerk_id') if current_user else 'Anonymous'}")
        
        # Si utilisateur non connecté, ne montrer que les posts publiés
        if not current_user:
            is_published = True
        
        posts = await post_service.get_posts(
            skip=skip,
            limit=limit,
            is_published=is_published,
            tag=tag,
            author_id=author_id,
            current_user_id=current_user.get("clerk_id") if current_user else None
        )
        
        logger.info(f"✅ {len(posts)} posts récupérés")
        return posts
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@router.get("/slug/{slug}", response_model=PostResponse)
async def get_post_by_slug(
    slug: str,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """📖 Récupère un post par son slug"""
    try:
        logger.info(f"🔍 Récupération post slug: {slug}")
        
        post = await post_service.get_post_by_slug(slug)

        if not post:
            raise HTTPException(status_code=404, detail="Post non trouvé")

        # Vérifier si le post est publié ou si l'utilisateur est l'auteur
        if not post.is_published:
            if not current_user or current_user["clerk_id"] != post.author_id:
                raise HTTPException(status_code=404, detail="Post non trouvé")

        logger.info(f"✅ Post récupéré: {post.slug}")
        return post

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur récupération post: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/{post_id}", response_model=PostResponse)
async def get_post_by_id(
    post_id: str,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """📖 Récupère un post par son ID"""
    try:
        logger.info(f"🔍 Récupération post ID: {post_id}")
        
        post = await post_service.get_post_by_id(post_id)

        if not post:
            raise HTTPException(status_code=404, detail="Post non trouvé")

        # Vérifier les permissions pour les brouillons
        if not post.is_published:
            if not current_user or current_user["clerk_id"] != post.author_id:
                raise HTTPException(status_code=404, detail="Post non trouvé")

        logger.info(f"✅ Post récupéré: {post.id}")
        return post

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur récupération post: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/tags/{tag}", response_model=List[PostResponse])
async def get_posts_by_tag(
    tag: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """📋 Récupère les posts par tag"""
    try:
        posts = await post_service.get_posts_by_tag(
            tag=tag,
            skip=skip,
            limit=limit
        )

        logger.info(f"✅ Récupération posts tag '{tag}': {len(posts)} trouvés")
        return posts

    except Exception as e:
        logger.error(f"❌ Erreur récupération posts par tag: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
