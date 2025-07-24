from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os
from typing import Optional

class Database:
    """Service de connexion MongoDB avec Motor (async)"""

    client: Optional[AsyncIOMotorClient] = None
    database = None

    @classmethod
    async def connect_to_mongo(cls):
        """Etablit la connexion à MongoDB"""
        MONGODB_URL = os.getenv("MONGODB_URL")
        DATABASE_NAME = os.getenv("DATABASE_NAME", "blog_db")

        if not MONGODB_URL:
            raise ValueError("MONGO_URL environment variable is required")
        
        try: 
            cls.client = AsyncIOMotorClient(
                MONGODB_URL,
                server_api=ServerApi('1'),
                maxPoolSize=10,
                minPoolSize=5
            )

            # Test de connexion
            await cls.client.admin.command('ping')
            cls.database = cls.client[DATABASE_NAME]

            print(f"✅ Connexion MongoDB établie - Base: {DATABASE_NAME}")

        except Exception as e:
            print(f"❌ Erreur de connexion MongoDB: {e}")
            raise

    @classmethod
    async def close_mongo_connection(cls):
        """Ferme la connexion MongoDB"""
        if cls.client:
            cls.client.close()
            print("✅ Connexion MongoDB fermée")

    @classmethod
    def get_database(cls):
        """Retourne l'instance de la base de données"""
        if cls.database is None:
            raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
        return cls.database
    
# Instance globale
database = Database()