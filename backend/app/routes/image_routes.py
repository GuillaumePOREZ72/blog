from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import cloudinary
import cloudinary.uploader
import os
import uuid
from ..middleware.auth import get_current_user
from ..models.user import UserResponse

router = APIRouter(prefix="/images", tags=["Images"])
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
    folder: str = Form(default="blog"),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload une image vers Cloudinary"""
    try:
        # Validation du type de fichier
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Type de fichier non autorisé. Utilisez JPEG, PNG, GIF ou WebP."
            )
        
        # Validation de la taille (max 10MB)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Fichier trop volumineux. Taille maximale: 10MB."
            )
        
        # Génération d'un nom unique pour l'image
        # ✅ Correction de la f-string avec échappement des crochets
        clerk_id = current_user.clerk_id
        unique_id = uuid.uuid4().hex[:8]
        public_id = f"{folder}/{clerk_id}_{unique_id}"
        
        # Upload vers Cloudinary
        result = cloudinary.uploader.upload(
            file.file,
            public_id=public_id,
            folder=folder,
            resource_type="image",
            format="auto",  # Auto-détection du format optimal
            quality="auto",  # Optimisation automatique de la qualité
            fetch_format="auto"  # Format optimal selon le navigateur
        )
        
        return {
            "success": True,
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "width": result["width"],
            "height": result["height"],
            "format": result["format"],
            "bytes": result["bytes"],
            "created_at": result["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )

@router.delete("/delete/{public_id:path}")
async def delete_image(
    public_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Supprime une image de Cloudinary"""
    try:
        # Vérifier que l'utilisateur a le droit de supprimer cette image
        # (l'image doit contenir son clerk_id dans le public_id)
        if current_user.clerk_id not in public_id and current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Vous n'avez pas le droit de supprimer cette image."
            )
        
        # Suppression de Cloudinary
        result = cloudinary.uploader.destroy(public_id)
        
        if result["result"] == "ok":
            return {
                "success": True,
                "message": "Image supprimée avec succès",
                "public_id": public_id
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="Image non trouvée ou déjà supprimée"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

@router.get("/transform/{public_id:path}")
async def get_transformed_image(
    public_id: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    crop: str = "fill",
    quality: str = "auto",
    format: str = "auto"
):
    """Génère une URL d'image transformée"""
    try:
        # Construction des paramètres de transformation
        transformation_params = {
            "quality": quality,
            "fetch_format": format
        }
        
        if width:
            transformation_params["width"] = width
        if height:
            transformation_params["height"] = height
        if width or height:
            transformation_params["crop"] = crop
        
        # Génération de l'URL transformée
        url = cloudinary.CloudinaryImage(public_id).build_url(**transformation_params)
        
        return {
            "success": True,
            "original_public_id": public_id,
            "transformed_url": url,
            "transformations": transformation_params
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la transformation: {str(e)}"
        )

@router.get("/list")
async def list_user_images(
    current_user: UserResponse = Depends(get_current_user),
    max_results: int = 50
):
    """Liste les images de l'utilisateur connecté"""
    try:
        # Recherche des images de l'utilisateur
        result = cloudinary.Search() \
            .expression(f"public_id:*{current_user.clerk_id}*") \
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
            "images": images
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des images: {str(e)}"
        )