from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional
from bson import ObjectId
from ..services.post_service import post_service
from ..models.post import PostCreate, PostUpdate, PostResponse
from ..middleware.auth import get_current_user, require_author_or_admin, get_optional_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["📝 Posts"])

# Create Post
@router.post("/", response_model=PostResponse, status_code=201)
async def create_post(
    post_data: PostCreate,
    current_user: dict = Depends(require_author_or_admin)
):
    """
    🆕 Créer un nouveau post
    
    - **Authentification requise** 🔐
    - **Rôle** : author ou admin
    - **Slug** : unique et URL-friendly
    """
    try:
        logger.info(f"📝 Tentative création post par: {current_user.get('clerk_id')}")
        
        # Ajouter l'auteur au post
        post_dict = post_data.model_dump()
        post_dict["author_id"] = current_user["clerk_id"]
        
        # Créer le post
        new_post = await post_service.create_post(
            post_data=post_data,
            author_id=current_user["clerk_id"]
        )
        
        logger.info(f"✅ Post créé avec succès: {new_post.slug}")
        return new_post
        
    except ValueError as e:
        logger.error(f"❌ Erreur validation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Erreur création post: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@router.get("/", response_model=List[PostResponse])
async def list_posts(
    skip: int = Query(0, ge=0, description="Nombre de posts à ignorer"),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum de posts"),
    is_published: Optional[bool] = Query(None, description="Filtrer par statut de publication"),
    tag: Optional[str] = Query(None, description="Filtrer par tag"),
    author_id: Optional[str] = Query(None, description="Filtrer par auteur"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    📋 Lister les posts avec filtres
    
    - **Public** : Posts publiés uniquement
    - **Authentifié** : Voit aussi ses brouillons
    - **Admin** : Voit tous les posts
    """
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
    """Récupère un post par son slug"""
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


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str, 
    post_update: PostUpdate,
    current_user: dict = Depends(require_author_or_admin)
):
    """🔄 Mettre à jour un post"""
    try:
        logger.info(f"🔄 Mise à jour post: {post_id} par {current_user.get('clerk_id')}")
        
        # Vérifier que le post existe et que l'utilisateur a les droits
        existing_post = await post_service.get_post_by_id(post_id)
        if not existing_post:
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        # Vérifier les permissions (auteur ou admin)
        if current_user["role"] != "admin" and current_user["clerk_id"] != existing_post.author_id:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        updated_post = await post_service.update_post_by_id(post_id, post_update)
        if not updated_post:
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        logger.info(f"✅ Post mis à jour: {post_id}")
        return updated_post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour post: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur serveur")


@router.delete("/{post_id}", status_code=204)
async def delete_post_by_id(
    post_id: str = Path(
        ...,
        description="ID MongoDB du post (24 caractères hexadécimaux)",
        example="6888a4ace2ff811da8dcfcbc"
    ),
    current_user: dict = Depends(require_author_or_admin)
):
    """🗑️ Supprimer un post par son ID"""
    try:
        logger.info(f"🗑️ Suppression post ID: {post_id} par {current_user.get('clerk_id')}")

        # Vérifier si c'est un ObjectId valide
        if not ObjectId.is_valid(post_id):
           raise HTTPException(
                status_code=400, 
                detail=f"ID MongoDB invalide: {post_id}. Utilisez un ObjectId valide (24 caractères hexadécimaux)"
            )

        # Vérifier que le post existe
        existing_post = await post_service.get_post_by_id(post_id)
        if not existing_post:
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        # Vérifier les permissions (auteur ou admin)
        if current_user["role"] != "admin" and current_user["clerk_id"] != existing_post.author_id:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        deleted = await post_service.delete_post_by_id(post_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        logger.info(f"✅ Post supprimé: {post_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur suppression post: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur serveur")


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


@router.delete("/slug/{slug}", status_code=204)
async def delete_post_by_slug(
    slug: str,
    current_user: dict = Depends(require_author_or_admin)
):
    """🗑️ Supprimer un post par son slug"""
    try:
        logger.info(f"🗑️ Suppression post slug: {slug} par {current_user.get('clerk_id')}")
        
        # Vérifier que le post existe
        existing_post = await post_service.get_post_by_slug(slug)
        if not existing_post:
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        # Vérifier les permissions (auteur ou admin)
        if current_user["role"] != "admin" and current_user["clerk_id"] != existing_post.author_id:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        # Supprimer le post
        deleted = await post_service.delete_post(slug)
        if not deleted:
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        logger.info(f"✅ Post supprimé par slug: {slug}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur suppression post: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
