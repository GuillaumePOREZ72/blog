# test_auth.py - Fichier temporaire pour les tests
from fastapi import Depends, HTTPException
from ..models.user import UserResponse
from datetime import datetime

async def get_test_user() -> UserResponse:
    """Utilisateur de test pour Postman"""
    return UserResponse(
        id="507f1f77bcf86cd799439011",
        clerk_id="user_test123",
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        profile_image="https://images.clerk.dev/test.jpg",
        role="author",
        is_active=True,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )