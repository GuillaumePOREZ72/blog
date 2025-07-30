from fastapi import APIRouter, Request
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["🎣 Webhooks"])

@router.post("/clerk")
async def clerk_webhook(request: Request):
    """🎣 Webhook Clerk - Version DEBUG"""
    try:
        # Log TOUT ce qui arrive
        print("🎣 WEBHOOK REÇU !")
        print(f"🎣 Method: {request.method}")
        print(f"🎣 URL: {request.url}")
        print(f"🎣 Headers: {dict(request.headers)}")
        
        # Lire le body
        body = await request.body()
        print(f"🎣 Body length: {len(body)}")
        print(f"🎣 Body: {body.decode('utf-8') if body else 'EMPTY'}")
        
        # Log dans les logs FastAPI aussi
        logger.info("🎣 WEBHOOK CLERK REÇU AVEC SUCCÈS !")
        
        return {"status": "OK", "received": True}
        
    except Exception as e:
        print(f"❌ ERREUR WEBHOOK: {str(e)}")
        logger.error(f"❌ Erreur webhook: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@router.get("/test")
async def test_webhook():
    """🧪 Test endpoint"""
    print("🧪 ENDPOINT TEST APPELÉ")
    logger.info("🧪 Test endpoint appelé")
    return {
        "status": "webhook endpoint actif",
        "timestamp": "2025-01-29",
        "debug": True
    }