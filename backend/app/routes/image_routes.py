from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import cloudinary
import cloudinary.uploader
import cloudinary.api
import cloudinary.search
import os
from ..middleware.auth import get_current_user
from ..services.image_service import cloudinary_service
from ..models.user import UserResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/images", tags=["🖼️ Images"])
security = HTTPBearer()

# Configuration Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    folder: Optional[str] = Form(default="blog"),
    current_user: dict = Depends(get_current_user)
):
    """
    🖼️ Upload d'image vers Cloudinary
    
    - **Authentification requise** 🔐
    - **Formats supportés** : JPG, PNG, WebP, GIF
    - **Taille max** : 10MB
    """
    try:
        logger.info(f"🖼️ Upload image par: {current_user.get('clerk_id')}")
        
        result = await cloudinary_service.upload_image(
            file=file,
            folder=f"{folder}/{current_user.get('clerk_id')}",
            public_id=None
        )
        
        logger.info(f"✅ Image uploadée: {result['public_id']}")
    
        return {
            "success": True,
            "message": "Image uploadée avec succès",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur upload image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur upload: {str(e)}"
        )

@router.delete("/delete/{public_id:path}")
async def delete_image(
    public_id: str,
    current_user: dict = Depends(get_current_user)
):
    """🗑️ Supprime une image de Cloudinary"""
    try:
        user_id = current_user.get('clerk_id')
        user_role = current_user.get('role')

        # Vérifier les permissions
        if user_id not in public_id and user_role != "admin":
            raise HTTPException(
                    status_code=403,
                    detail="Vous n'avez pas le droit de supprimer cette image."
                )

        deleted = await cloudinary_service.delete_image(public_id)

        if not deleted:
                raise HTTPException(
                    status_code=404,
                    detail="Image non trouvée ou déjà supprimée"
                )

        return {
                "success": True,
                "message": "Image supprimée avec succès",
                "public_id": public_id
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur suppression: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

@router.get("/transform/{public_id:path}")
async def get_transformed_image(
    public_id: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    quality: str = "auto",
):
    """🔧 Génère une URL d'image transformée"""
    try:
        url = cloudinary_service.get_optimized_url(
                public_id=public_id,
                width=width,
                height=height,
                quality=quality
            )

        if not url:
            raise HTTPException(status_code=404, detail="Image non trouvée")
        
        return {
            "success": True,
            "original_public_id": public_id,
            "transformed_url": url,
            "parameters": {
                "width": width,
                "height": height,
                "quality": quality
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur transformation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur transformation: {str(e)}"
        )

@router.get("/list")
async def list_user_images(
    current_user: dict = Depends(get_current_user),
    max_results: int = 50
):
    """📋 Liste les images de l'utilisateur connecté"""
    try:
        user_id = current_user.get('clerk_id')
        
        # Recherche des images de l'utilisateur
        result = cloudinary.Search() \
            .expression(f"public_id:*{clerk_id}*") \
            .sort_by([("created_at", "desc")]) \
            .max_results(max_results) \
            .execute()
        
        images = []
        for resource in result.get("resources", []):
            images.append({
                "public_id": resource["public_id"],
                "secure_url": resource["secure_url"],
                "width": resource["width"],
                "height": resource["height"],
                "format": resource["format"],
                "bytes": resource["bytes"],
                "created_at": resource["created_at"]
            })
        
        return {
            "success": True,
            "total_count": result.get("total_count", 0),
            "images": images,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur liste images: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération: {str(e)}"
        )