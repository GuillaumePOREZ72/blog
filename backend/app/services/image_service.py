import cloudinary
import cloudinary.uploader
import cloudinary.api   
from fastapi import UploadFile, HTTPException
import os
from typing import Optional, Dict, Any
import logging
from io import BytesIO

logger = logging.getLogger(__name__)


class CloudinaryService:
    """Service de gestion des images avec Cloudinary"""

    def __init__(self):
        # Configuration Cloudinary
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            secure=True
        )

        self.upload_preset = os.getenv("CLOUDINARY_UPLOAD_PRESET", "GUIGUIBLOG")

        logger.info(f"🔧 Cloudinary configuré: {os.getenv('CLOUDINARY_CLOUD_NAME')}")

    async def upload_image(
        self,
        file: UploadFile,
        folder: str = "blog_posts",
        public_id: Optional[str] = None
    ) -> dict:
        """Upload une image vers Cloudinary"""
        try:
            logger.info(f"🖼️ Upload image: {file.filename}")
            
            # Vérifier le type de fichier
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="Le fichier doit être une image")

            # Lire le contenu du fichier
            file_content = await file.read()

            # Vérifier la taille (max 10MB)
            if len(file_content) > 10 * 1024 *1024:
                raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 10MB)")

            # Configuration d'upload
            upload_options = {
                "folder": folder,
                "resource_type": "image",
                "format": "webp",
                "quality": "auto:good",
                "fetch_format": "auto"
            }

            # Ajout conditionnel: Upload preset ou pblic_id
            if self.upload_preset and not public_id:
                upload_options["upload_preset"] = self.upload_preset
            elif public_id:
                upload_options["public_id"] = public_id

            # Upload vers Cloudinary
            result = cloudinary.uploader.upload(
                file_content,
                **upload_options
            )

            logger.info(f"✅ Image uploadée: {result['public_id']}")

            return {
                "public_id": result["public_id"],
                "url": result["secure_url"],
                "width": result["width"],
                "height": result["height"],
                "format": result["format"],
                "bytes": result["bytes"]
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erreur upload Cloudinary: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erreur upload image: {str(e)}")


    async def delete_image(self, public_id: str) -> bool:
        """Supprime une image de Cloudinary"""
        try:
            logger.info(f"🗑️ Suppression image: {public_id}")
            
            result = cloudinary.uploader.destroy(public_id)
            success = result.get("result") == "ok"

            if success:
                logger.info(f"✅ Image supprimée: {public_id}")
            else:
                logger.warning(f"⚠️ Echec suppression image: {public_id}")

            return success

        except Exception as e:
            logger.error(f"❌ Erreur suppression Cloudinary: {str(e)}")
            return False
        
    def get_optimized_url(
        self,
        public_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        quality: str = "auto:good"
    ) -> str:
        """Génère une URL optimisée pour l'image"""
        try:
            transformations = {
                "quality": quality,
                "fetch_format": "auto"
            }

            if width:
                transformations["width"] = width
            if height:
                transformations["height"] = height
                # Crop intelligent si dimensions spécifiées
                if width:
                    transformations["crop"] = "fill"

            return cloudinary.CloudinaryImage(public_id).build_url(**transformations)
        except Exception as e:
            logger.error(f"❌ Erreur génération URL: {str(e)}")
            return ""
    
# Instance globale
cloudinary_service = CloudinaryService()