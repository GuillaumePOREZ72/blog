from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from typing import AsyncGenerator

from .services.database import database
from .routes import post_routes, user_routes, image_routes

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Gestionnaire de cycle de vie de l'application"""
    #Startup
    logger.info("🚀 Démarrage de l'application Blog API")

    try:
        # Connexion à MongoDB
        await database.connect_to_mongo()
        logger.info("✅ Base de données connectée")

        yield

    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage: {e}")
        raise
    finally:
        logger.info("🛑 Arrêt de l'application")
        await database.close_mongo_connection()
        logger.info("✅ Connexions fermées proprement")

# Création de l'application FastAPI
app = FastAPI(
    title="Blog API",
    description="API REST pour application de blog avec authentification Clerk",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware de gestion d'erreurs globales
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire d'erreurs global"""
    logger.error(f"Erreur non gérée: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erreur interne du serveur",
            "type": "internal_server_error"
        }
    )

# Middleware de logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log toutes les requêtes HTTP"""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    return response

# Route de santé
@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de vérification de santé"""
    try:
        #Vérifier la connexion MongoDB
        db = database.get_database()
        await db.command('ping')

        return {
            "status": "healthy",
            "message": "Blog API opérationnelle",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "Service indisponible",
                "database": "disconnected",
                "error": str(e)
            }
        )

# Route racine
@app.get("/", tags=["Root"])
async def root():
    """Endpoint racine de l'API"""
    return {
        "message": "Bienvenue sur l'API Blog",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

# Inclusion des routers
app.include_router(post_routes.router, prefix="/api/v1")
app.include_router(user_routes.router, prefix="/api/v1")
app.include_router(image_routes.router, prefix="/api/v1")

# Import nécessaire pour le middleware de timing
import time

if __name__ == "__main__":
    import uvicorn

    # Configuration pour le développement
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )