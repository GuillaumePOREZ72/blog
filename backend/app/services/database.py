import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service de gestion de la base de données MongoDB"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        # Ne pas initialiser immédiatement, attendre le premier appel
    
    def _initialize_connection(self):
        """Initialise la connexion à MongoDB"""
        if self.client is not None:
            return  # Déjà initialisé
            
        try:
            # Récupération de l'URL depuis les variables d'environnement
            mongodb_url = os.getenv("MONGODB_URL")
            database_name = os.getenv("DATABASE_NAME", "blog_db")
            
            # ✅ Debug des variables d'environnement
            logger.info(f"MONGODB_URL loaded: {'✓' if mongodb_url else '✗'}")
            logger.info(f"DATABASE_NAME: {database_name}")
            
            if not mongodb_url:
                logger.error("MONGODB_URL environment variable is required")
                raise ValueError("MONGODB_URL environment variable is required")
            
            # ✅ Log de l'URL (masquée pour la sécurité)
            masked_url = mongodb_url.replace(mongodb_url.split('@')[0].split('//')[1], "***:***")
            logger.info(f"Connecting to MongoDB: {masked_url}")
            
            # Création du client MongoDB
            self.client = AsyncIOMotorClient(
                mongodb_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                retryWrites=True,
                w="majority"
            )
            
            # Sélection de la base de données
            self.database = self.client[database_name]
            
            logger.info(f"✅ Database connection initialized: {database_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database connection: {str(e)}")
            raise
    
    async def connect_to_mongo(self):
        """Connecte à MongoDB"""
        try:
            # Initialiser si ce n'est pas fait
            if self.client is None:
                self._initialize_connection()
            
            # Test de la connexion
            logger.info("🔄 Testing MongoDB connection...")
            await self.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    async def close_mongo_connection(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            logger.info("🔒 MongoDB connection closed")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Retourne l'instance de la base de données"""
        if self.database is None:
            self._initialize_connection()
        
        if self.database is None:
            raise RuntimeError("Database connection failed")
        
        return self.database
    
    def get_collection(self, collection_name: str):
        """Retourne une collection spécifique"""
        db = self.get_database()
        return db[collection_name]
    
    async def health_check(self) -> dict:
        """Vérifie la santé de la base de données"""
        try:
            if self.client is None:
                self._initialize_connection()
            
            if self.client is None:
                return {"status": "error", "message": "No database connection"}
            
            # Test ping
            await self.client.admin.command('ping')
            
            # Informations sur la base de données
            db_stats = await self.database.command("dbStats")
            
            return {
                "status": "healthy",
                "database": self.database.name,
                "collections": db_stats.get("collections", 0),
                "data_size": db_stats.get("dataSize", 0),
                "storage_size": db_stats.get("storageSize", 0)
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

# Instance globale (sans initialisation immédiate)
database = DatabaseService()