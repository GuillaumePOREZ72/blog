import motor.motor_asyncio
import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service de gestion de la base de données MongoDB"""
    
    def __init__(self):
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.database = None

        # DEBUG - Afficher la variable
        self.mongodb_url = os.getenv("MONGODB_URL")
        self.database_name = os.getenv("DATABASE_NAME", "blog_db")

        print(f"🔍 DEBUG - MONGODB_URL présente: {bool(self.mongodb_url)}")
        if self.mongodb_url:
            print(f"🔍 DEBUG - URL: {self.mongodb_url[:50]}...")
        
        if not self.mongodb_url:
            raise ValueError("❌ MONGODB_URL manquante dans les variables d'environnement")
    
    async def connect(self):
        """Se connecter à MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodb_url)
            self.database = self.client[self.database_name]
            
            # Test de connexion
            await self.client.admin.command('ping')
            logger.info(f"✅ Connexion MongoDB réussie: {self.database_name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion MongoDB: {str(e)}")
            raise e
    
    async def disconnect(self):
        """Se déconnecter de MongoDB"""
        if self.client is not None:
            self.client.close()
            logger.info("✅ Déconnexion MongoDB")
    
    async def get_database(self):
        """Retourner l'instance de la base de données"""
        if self.database is None:
            await self.connect()
        return self.database

# Instance globale
db_service = DatabaseService()

# FONCTION HELPER OPTIONNELLE
async def get_database():
    """Fonction helper pour récupérer la DB"""
    try:
        logger.info(f"🔍 Debug - database is None: {db_service.database is None}")
        
        if db_service.database is None:
            logger.info("🔄 Connexion à la base de données...")
            await db_service.connect()
        
        logger.info("✅ Base de données récupérée")
        return db_service.database
        
    except Exception as e:
        logger.error(f"❌ Erreur get_database: {str(e)}")
        raise e