from fastapi import APIRouter, Request, HTTPException
import logging
import json
from datetime import datetime

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
            for email_obj in email_addressess:
                if email_obj.get('id') == primary_email_id:
                    primary_email = email_obj.get('email_address')
                    break

        # Si pas trouvé, prendre le premier email
        if not primary_email and email_addresses:
            primary_email = email_addresses[0].get('email_address')
        

        print(f"🆕 NOUVEL UTILISATEUR CRÉÉ")
        print(f"🆔 ID: {user_id}")
        print(f"📧 Email: {primary_email}")
        print(f"📧 Primary Email ID: {primary_email_id}")
        print(f"📧 Tous les emails: {[e.get('email_address') for e in email_addresses]}")
        print(f"👤 Nom: {user_data.get('first_name')} {user_data.get('last_name')}")
        print(f"👤 Username: {user_data.get('username')}")
        print(f"🖼️ Avatar: {user_data.get('profile_image_url')}")

        # TODO: Sauvegarder en base de données
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

        print(f"💾 Prêt à sauvegarder: {json.dumps(user_doc, indent=2)}")

        logger.info(f"🆕 Utilisateur créé: {primary_email or 'Email non trouvé'}")

    except Exception as e:
        logger.error(f"❌ Erreur création utilisateur: {str(e)}")
        print(f"❌ Erreur détaillée: {str(e)}")

async def handle_user_updated(user_data: dict):
    """Traite la mise à jour d'un utilisateur"""
    user_id = user_data.get('id')
    print(f"🔄 UTILISATEUR MIS À JOUR: {user_id}")
    logger.info(f"🔄 Utilisateur mis à jour: {user_id}")

    # TODO: Mettre à jour en base de données


async def handle_user_deleted(user_data: dict):
    user_id = user_data.get('id')
    print(f"🗑️ UTILISATEUR SUPPRIMÉ: {user_id}")
    logger.info(f"🗑️ Utilisateur supprimé: {user_id}")
    
    # TODO: Marquer comme supprimé en base de données


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