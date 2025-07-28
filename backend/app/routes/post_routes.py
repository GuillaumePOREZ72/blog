from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from ..models.post import PostCreate, PostUpdate, PostResponse
from ..services.post_service import post_service
from ..middleware.auth import (
    get_current_user,
    require_author_or_admin,
    get_optional_user
)


# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["posts"])

# Create Post
@router.post("/", response_model=PostResponse, status_code=201)
async def create_post(
    post_data: PostCreate, 
    current_user: dict = Depends(require_author_or_admin)
):
    """Crée un nouveau post (authentification requise)"""
    try:
        logger.info(f"Création post par utilisateur: {current_user['clerk_id']}")
        new_post = await post_service.create_post(
            post_data=post_data,
            author_id=current_user["clerk_id"]
        )
        logger.info(f"Post créé avec succès: {new_post.id}")
        return new_post
    
    except ValueError as e:
        logger.error(f"Erreur validation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur création post: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne au serveur")


@router.get("/", response_model=List[PostResponse])
async def list_posts(
    skip: int = Query(0, ge=0, description="Nombre de posts à ignorer"),
    limit: int = Query(10, ge=1, le=100, description="Nombre maximum de posts"),
    published_only: bool = Query(True, description="Afficher seulement les posts publiés"),
    author_id: Optional[str] = Query(None, description="Filtrer par auteur"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Liste tous les posts avec pagination et filtres"""
    try:
        # Si utilisateur connecté et demande ses propres posts
        if current_user and not author_id:
            # Peut voir ses brouillons
            published_only = False
            author_id = current_user["clerk_id"]

        posts = await post_service.get_posts(
            skip=skip,
            limit=limit,
            published_only=published_only,
            author_id=author_id
        )
        logger.info(f"Récupération de {len(posts)} posts")
        return posts
    
    except Exception as e:
        logger.error(f"Erreur récupération posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.get("/slug/{slug}", response_model=PostResponse)
async def get_post_by_slug(
    slug: str,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Récupère un post par son slug"""
    try:
        post = await post_service.get_post_by_slug(slug)

        if not post:
            raise HTTPException(status_code=404, detail="Post non trouvé")

        # Vérifier si le post est publié ou si l'utilisateur est l'auteur
        if not post.is_published:
            if not current_user or current_user["clerk_id"] != post.author_id:
                raise HTTPException(status_code=404, detail="Post non trouvé")

        logger.info(f"Post récupéré: {post.slug}")
        return post

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération post: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.get("/{post_id}", response_model=PostResponse)
async def get_post_by_id(
    post_id: str,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Récupère un post par son ID"""
    try:
        post = await post_service.get_post_by_id(post_id)

        if not post:
            raise HTTPException(status_code=404, detail="Post non trouvé")

        # Vérifier les permissions pour les brouillons
        if not post.is_published:
            if not current_user or current_user["clerk_id"] != post.author_id:
                raise HTTPException(status_code=404, detail="Post non trouvé")

        logger.info(f"Post récupéré: {post_id}")
        return post

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération post: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str, 
    post_update: PostUpdate,
    current_user: dict = Depends(require_author_or_admin)
):
    """Met à jour un post (seul l'auteur peut modifier)"""
    try:
        updated_post = await post_service.update_post(
            post_id=post_id,
            post_update=post_update,
            author_id=current_user["clerk_id"]
        )

        if not updated_post:
            raise HTTPException(
                status_code=404,
                detail="Post non trouvé ou non autorisé"
            )

        logger.info(f"Post mis à jour: {post_id}")
        return updated_post

    except ValueError as e:
        logger.error(f"Erreur validation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur mise à jour post: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: str,
    current_user: dict = Depends(require_author_or_admin)
):
    """Supprime un post (seul l'auteur peut supprimer)"""
    try:
        deleted = await post_service.delete_post(
            post_id=post_id,
            author_id=current_user["clerk_id"]
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Post non trouvé ou non autorisé"
            )

        logger.info(f"Post supprimé: {post_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression post: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.get("/tags/{tag}", response_model=List[PostResponse])
async def get_posts_by_tag(
    tag: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Récupère les posts par tag"""
    try:
        posts = await post_service.get_posts_by_tag(
            tag=tag,
            skip=skip,
            limit=limit
        )

        logger.info(f"Récupération posts tag '{tag}': {len(posts)} trouvés")
        return posts

    except Exception as e:
        logger.error(f"Erreur récupération posts par tag: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
