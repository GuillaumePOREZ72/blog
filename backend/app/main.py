from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# ✅ CHARGER L'ENV EN PREMIER
load_dotenv()

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ✅ IMPORT APRÈS CHARGEMENT ENV
from .services.database import db_service
from .routes import post_routes, user_routes, image_routes, webhook_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    
    # 🚀 STARTUP
    try:
        logger.info("🚀 Starting up application Blog API")
        
        # Environment check
        logger.info("📊 Environment check:")
        logger.info(f"  - MONGODB_URL: {'✓' if os.getenv('MONGODB_URL') else '✗'}")
        logger.info(f"  - CLERK_SECRET_KEY: {'✓' if os.getenv('CLERK_SECRET_KEY') else '✗'}")
        logger.info(f"  - CLOUDINARY_CLOUD_NAME: {'✓' if os.getenv('CLOUDINARY_CLOUD_NAME') else '✗'}")
        
        # ✅ CONNEXION AVEC GESTION D'ERREUR AMÉLIORÉE
        try:
            await db_service.connect()
            logger.info("✅ Application startup complete")
        except Exception as db_error:
            logger.error(f"❌ Database connection failed: {str(db_error)}")
            logger.info("⚠️ Application will continue without database")
            # On ne lève pas l'exception pour permettre au serveur de démarrer
        
        yield  # L'application fonctionne ici
        
    except Exception as e:
        logger.error(f"❌ Critical startup error: {str(e)}")
        raise e
    
    # 🛑 SHUTDOWN
    try:
        logger.info("🛑 Shutting down application")
        await db_service.disconnect()
        logger.info("✅ Application shutdown complete")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {str(e)}")

# ✅ CRÉATION APP AVEC LIFESPAN
app = FastAPI(
    title="🚀 Blog API",
    description="""
    ## API complète pour un blog moderne
    
    ### 🔐 Authentification
    Pour tester les endpoints protégés :
    1. Cliquez sur **"Authorize"** 🔓
    2. Entrez : `Bearer test_postman_token`
    3. Cliquez sur **"Authorize"**
    
    ### 📝 Fonctionnalités
    - **Users** : Gestion des utilisateurs avec Clerk
    - **Posts** : CRUD complet des articles
    - **Images** : Upload et gestion via Cloudinary
    
    ### 🧪 Mode Test
    Utilisez le token `test_postman_token` pour vos tests en développement.
    
    ### 📚 Collections disponibles
    - **Users** : Création, lecture, mise à jour
    - **Posts** : Blog posts avec tags et images  
    - **Images** : Upload Cloudinary avec transformations
    """,
    version="1.0.0",
    lifespan=lifespan,
    # Configuration de l'authentification dans Swagger
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "persistAuthorization": True,  # Garde l'auth entre les tests
        "displayRequestDuration": True,
        "filter": True,
        "syntaxHighlight.theme": "arta"
    }
)

# Configuration CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(post_routes.router)
app.include_router(user_routes.router)
app.include_router(image_routes.router)
app.include_router(webhook_routes.router)

# Routes de base
@app.get("/")
async def root():
    """🏠 Page d'accueil de l'API"""
    return {
        "message": "🚀 Blog API is running",
        "version": "1.0.0",
        "docs": "📚 /docs",
        "environment": {
            "mongodb_configured": bool(os.getenv("MONGODB_URL")),
            "clerk_configured": bool(os.getenv("CLERK_SECRET_KEY")),
            "cloudinary_configured": bool(os.getenv("CLOUDINARY_CLOUD_NAME"))
        }
    }

@app.get("/health")
async def health_check():
    """🏥 Vérification de santé de l'API"""
    try:
        # Test connexion MongoDB
        if db_service.database is not None:
            await db_service.database.command("ping")
            db_status = "connected"
        else:
            db_status = "disconnected"
    except:
        db_status = "error"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": "2025-07-31T11:34:14.956Z"
    }

# Gestionnaire d'erreurs global
@app.exception_handler(500)
async def internal_server_error(request, exc):
    logger.error(f"❌ Erreur serveur: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )