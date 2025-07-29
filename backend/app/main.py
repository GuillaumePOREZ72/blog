# ✅ CHARGER .ENV EN TOUT PREMIER
import os
from dotenv import load_dotenv

# Chargement immédiat des variables d'environnement
load_dotenv()

# Puis imports FastAPI et services
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .services.database import database
from .routes import post_routes, user_routes, image_routes

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Startup
    logger.info("🚀 Starting up application Blog API")
    
    # ✅ Vérification des variables d'environnement
    mongodb_url = os.getenv("MONGODB_URL")
    if not mongodb_url:
        logger.error("❌ MONGODB_URL not found in environment variables")
        raise Exception("MONGODB_URL environment variable is required")
    
    logger.info(f"📊 Environment check:")
    logger.info(f"  - MONGODB_URL: {'✓' if mongodb_url else '✗'}")
    logger.info(f"  - CLERK_SECRET_KEY: {'✓' if os.getenv('CLERK_SECRET_KEY') else '✗'}")
    logger.info(f"  - CLOUDINARY_CLOUD_NAME: {'✓' if os.getenv('CLOUDINARY_CLOUD_NAME') else '✗'}")
    
    # Test de connexion à la base de données
    connection_success = await database.connect_to_mongo()
    if not connection_success:
        logger.error("❌ Failed to connect to database during startup")
        raise Exception("Database connection failed")
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🔒 Shutting down application...")
    await database.close_mongo_connection()
    logger.info("✅ Application shutdown complete")

# Création de l'application FastAPI
app = FastAPI(
    title="Blog API",
    description="API pour un blog avec authentification Clerk et gestion d'images Cloudinary",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Routes de base
@app.get("/")
async def root():
    """Route racine"""
    return {
        "message": "Blog API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "environment": {
            "mongodb_configured": bool(os.getenv("MONGODB_URL")),
            "clerk_configured": bool(os.getenv("CLERK_SECRET_KEY")),
            "cloudinary_configured": bool(os.getenv("CLOUDINARY_CLOUD_NAME"))
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de la santé de l'API"""
    try:
        db_health = await database.health_check()
        
        return {
            "status": "healthy",
            "api": "running",
            "database": db_health,
            "environment": {
                "mongodb_configured": bool(os.getenv("MONGODB_URL")),
                "clerk_configured": bool(os.getenv("CLERK_SECRET_KEY")),
                "cloudinary_configured": bool(os.getenv("CLOUDINARY_CLOUD_NAME"))
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Inclusion des routers
app.include_router(post_routes.router, prefix="/api/v1")
app.include_router(user_routes.router, prefix="/api/v1")
app.include_router(image_routes.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )