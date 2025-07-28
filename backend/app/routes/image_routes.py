from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ..services.image_service import cloudinary_service
from ..middleware.auth import require_author_or_admin, get_current_user

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    folder: str = "blog_posts",
    current_user: dict = Depends(require_author_or_admin)
):
    """Upload une image vers Cloudinary"""
    try:
        # Générer un public_id unique
        import uuid
        public_id = f"{folder}/{current_user["clerk_id"]}_{uuid.uuid4().hex[:8]}"

        result = await cloudinary_service.upload_image(
            file=file,
            folder=folder,
            public_id=public_id
        )

        return {
            "success": True,
            "data": result,
            "message": "Image uploadée avec succès"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{public_id:path}")
async def delete_image(
    public_id: str,
    current_user: dict = Depends(require_author_or_admin)
):
    """Supprime une image de Cloudinary"""
    try:
        success = await cloudinary_service.delete_image(public_id)

        if success:
            return {"success": True, "message": "Image supprimée avec succès"}
        else:
            raise HTTPException(status_code=404, detail="Image non trouvée")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimize/{public_id:path}")
async def get_optimized_url(
    public_id: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    quality: str = "auto:good"
):
    """Génère une URL d'image optimisée"""
    try:
        url = cloudinary_service.get_optimized_url(
            public_id=public_id,
            width=width,
            height=height,
            quality=quality
        )

        return {"optimized_url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))