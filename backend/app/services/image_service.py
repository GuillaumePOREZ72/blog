import cloudinary
import cloudinary.uploader
import cloudinary.api   
from fastapi import UploadFile, HTTPException
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CloudinaryService:
    """Service de gestion des images avec Cloudinary"""

    def __init__(self):
        # Configuration Cloudinary
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET")
        )

        self.upload_preset = os.getenv("CLOUDINARY_UPLOAD_PRESET", "GUIGUIBLOG")

    async def upload_image(
        self,
        file: UploadFile,
        folder: str = "blog_posts",
        public_id: Optional[str] = None
    ) -> dict:
        """Upload une image vers Cloudinary"""
        try:
            # Vérifier le type de fichier
            if not file.content_type.startwith('image/'):
                raise HTTPException(status_code=400, detail="Le fichier doit être une image")

            # Lire le contenu du fichier
            file_content = await file.read()

            # Configuration d'upload
            upload_options = {
                "folder": folder,
                "upload_preset": self.upload_preset,
                "resource_type": "image",
                "format": "webp",
                "quality": "auto:good",
                "fetch_format": "auto"
            }

            if public_id:
                upload_options["public_id"] = public_id

            # Upload vers Cloudinary
            result = cloudinary.uploader.upload(
                file_content,
                **upload_options
            )

            logger.info(f"Image uploadée avec succès: {result['public_id']}")

            return {
                "public_id": result["public_id"],
                "url": result["secure_url"],
                "width": result["width"],
                "height": result["height"],
                "format": result["format"],
                "bytes": result["bytes"]
            }

        except Exception as e:
            logger.error(f"Erreur upload Cloudibnary: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erreur upload image: {str(e)}")


    async def delete_image(self, public_id: str) -> bool:
        """Supprime une image de Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id)
            success = result.get("result") == "ok"

            if success:
                logger.info(f"Image supprimée: {public_id}")
            else:
                logger.warning(f"Echec suppression image: {public_id}")

            return success

        except Exception as e:
            logger.error(f"Erreur supression Cloudinary: {str(e)}")
            return False
        
    def get_optimized_url(
        self,
        public_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        quality: str = "auto:good"
    ) -> str:
        """Génère une URL optimisée pour l'image"""
        transformations = {
            "quality": quality,
            "fetch_format": "auto"
        }

        if width:
            transformations["width"] = width
        if height:
            transformations["height"] = height

        return cloudinary.CloudinaryImage(public_id).build_url(**transformations)

# Instance globale
cloudinary_service = CloudinaryService()