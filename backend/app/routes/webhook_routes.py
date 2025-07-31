from fastapi import APIRouter, Request, HTTPException
import logging
import json
from datetime import datetime
from ..services.database import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["🎣 Webhooks"])

@router.post("/clerk")
async def clerk_webhook(request: Request):
    """🎣 Webhook Clerk pour synchronisation utilisateurs"""
    try:
        # Log de réception
        print("🎣 WEBHOOK CLERK REÇU !")
        logger.info("🎣 Webhook Clerk reçu")
        
        # Lire et parser le payload
        body = await request.body()
        payload = json.loads(body.decode('utf-8'))
        
        # Extraire les informations importantes
        event_type = payload.get("type")
        user_data = payload.get("data", {})
        event_id = request.headers.get("svix-id")
        timestamp = request.headers.get("svix-timestamp")

        # Log des informations clés
        print(f"🎯 Event Type: {event_type}")
        print(f"🆔 Event ID: {event_id}")
        print(f"👤 User ID: {user_data.get('id')}")

        # Traitement selon le type d'événement
        if event_type == "user.created":
            await handle_user_created(user_data)
        elif event_type == "user.updated":
            await handle_user_updated(user_data)
        elif event_type == "user.deleted":
            await handle_user_deleted(user_data)
        else:
            print(f"ℹ️ Événement non traité: {event_type}")

        logger.info(f"✅ Webhook {event_type} traité avec succès")

        return {
            "success": True,
            "event_type": event_type,
            "event_id": event_id,
            "user_id": user_data.get('id'),
            "processed_at": datetime.now().isoformat()
        }

    except json.JSONDecodeError:
        logger.error("❌ Payload JSON invalide")
        raise HTTPException(status_code=400, detail="JSON invalide")
    except Exception as e:
        print(f"❌ ERREUR WEBHOOK: {str(e)}")
        logger.error(f"❌ Erreur webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_user_created(user_data: dict):
    """Traite la création d'un nouvel utilisateur"""
    try:
        user_id = user_data.get('id')
        email_addresses = user_data.get('email_addresses', [])
        primary_email_id = user_data.get('primary_email_address_id')

        # Trouver l'email primaire
        primary_email = None
        if primary_email_id:
            for email_obj in email_addresses:
                if email_obj.get('id') == primary_email_id:
                    primary_email = email_obj.get('email_address')
                    break

        # Si pas trouvé, prendre le premier email
        if not primary_email and email_addresses:
            primary_email = email_addresses[0].get('email_address')
        

        print(f"🆕 NOUVEL UTILISATEUR CRÉÉ")
        print(f"🆔 ID: {user_id}")
        print(f"📧 Email: {primary_email}")
        
        # Document MongoDB
        user_doc = {
            "clerk_id": user_id,
            "email": primary_email,
            "username": user_data.get('username'),
            "first_name": user_data.get('first_name'),
            "last_name": user_data.get('last_name'),
            "profile_image": user_data.get('profile_image_url'),
            "created_at": user_data.get('created_at'),
            "updated_at": user_data.get('updated_at'),
            "is_active": True,
            "role": "user"
        }

        # Sauvegarde MongoDB
        try:
            db = await get_database()
            users_collection = db["users"]

            # Vérifier si existe déjà
            existing_user = await users_collection.find_one({"clerk_id: user_id"})

            if existing_user:
                print(f"⚠️ Utilisateur déjà existant: {user_id}")
            else:
                result = await users_collection.insert_one(user_doc)
                print(f"💾 ✅ Utilisateur sauvegardé MongoDB: {result.inserted_id}")
                logger.info(f"💾 Utilisateur sauvegardé: {primary_email}")

        except Exception as db_error:
            print(f"❌ Erreur MongoDB: {str(db_error)}")
            logger.error(f"❌ Erreur MongoDB: {str(db_error)}")

        logger.info(f"🆕 Utilisateur créé: {primary_email or user_id}")

    except Exception as e:
        logger.error(f"❌ Erreur création utilisateur: {str(e)}")

async def handle_user_updated(user_data: dict):
    """Traite la mise à jour d'un utilisateur"""
    try:
        user_id = user_data.get('id')
        print(f"🔄 UTILISATEUR MIS À JOUR: {user_id}")

        # mise à jour MongoDB
        db = await get_database()
        users_collection = db["users"]

        update_doc = {
            "username": user_data.get('username'),
            "first_name": user_data.get('first_name'),
            "last_name": user_data.get('last_name'),
            "profile_image": user_data.get('profile_image_url'),
            "updated_at": user_data.get('updated_at')
        }

        result = await users_collection.update_one(
            {"clerk_id": user_id},
            {"$set": update_doc}
        )

        print(f"🔄 ✅ Utilisateur mis à jour: {result.modified_count} doc(s)")
        logger.info(f"🔄 Utilisateur mis à jour: {user_id}")

    except Exception as e:
        logger.error(f"❌ Erreur mise à jour: {str(e)}")


async def handle_user_deleted(user_data: dict):
    """Traite la suppression d'un utilisateur"""
    try:
        user_id = user_data.get('id')
        print(f"🗑️ UTILISATEUR SUPPRIMÉ: {user_id}")

        # Suppression MongoDB (soft delete)
        db = await get_database()
        users_collection = db["users"]

        result = await users_collection.update_one(
            {"clerk_id": user_id},
            {"$set": {"is_active": False, "deleted_at": datetime.now().isoformat()}}
        )

        print(f"🗑️ ✅ Utilisateur désactivé: {result.modified_count} doc(s)")
        logger.info(f"🗑️ Utilisateur supprimé: {user_id}")

    except Exception as e:
        logger.error(f"❌ Erreur suppression: {str(e)}")

@router.get("/test")
async def test_webhook():
    """🧪 Test endpoint"""
    print("🧪 ENDPOINT TEST APPELÉ")
    logger.info("🧪 Test endpoint appelé")
    return {
        "status": "webhook endpoint actif",
        "timestamp": datetime.now().isoformat(),
        "debug": True,
        "ngrok_operational": True
    }