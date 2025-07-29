from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re

class User(BaseModel):
    """Modèle utilisateur synchronisé avec Clerk"""
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "clerk_id": "user_2abc123def456",
                "email": "john.doe@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "profile_image": "https://img.clerk.com/profile.jpg",
                "role": "author",
                "is_active": True
            }
        }
    )
    
    id: Optional[str] = Field(None, alias="_id") 
    clerk_id: str = Field(..., description="ID unique Clerk", min_length=10)
    email: str = Field(..., min_length=3, max_length=254)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    profile_image: Optional[str] = Field(None, pattern=r'^https?://')
    is_active: bool = Field(default=True)
    role: str = Field(default="user", pattern=r'^(admin|author|user)$')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        """Validation de l'email"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Format email invalide')
        return v.lower()

    @field_validator('username')
    @classmethod
    def username_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        """Validation du nom d'utilisateur"""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError("Username must contain only letters, numbers, hyphens and underscores")
        return v
    
    @field_validator('clerk_id')
    @classmethod
    def clerk_id_must_be_valid(cls, v: str) -> str:
        """Validation de l'ID Clerk"""
        if not v.startswith('user_'):
            raise ValueError("Clerk ID must start with user_")
        return v
    
    @field_validator('updated_at')
    @classmethod
    def set_updated_at(cls, v: datetime) -> datetime:
        """Met à jour automatiquement updated_at"""
        return datetime.utcnow()

class UserCreate(BaseModel):
    """Modèle pour la création d'utilisateur via webhook Clerk"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "clerk_id": "user_2new123user456",
                "email": "newuser@example.com",
                "username": "newuser",
                "first_name": "Nouveau",
                "last_name": "Utilisateur",
                "profile_image": "https://img.clerk.com/newuser.jpg"
            }
        }
    )
    
    clerk_id: str = Field(..., description="ID unique Clerk", min_length=10)
    email: str = Field(..., min_length=3, max_length=254)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    profile_image: Optional[str] = Field(None, pattern=r'^https?://')

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Format email invalide')
        return v.lower()

    @field_validator('clerk_id')
    @classmethod
    def clerk_id_must_be_valid(cls, v: str) -> str:
        if not v.startswith('user_'):
            raise ValueError('Clerk ID must start with user_')
        return v

class UserUpdate(BaseModel):
    """Modèle pour la mise à jour d'utilisateur"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "nouveau_username",
                "first_name": "Prénom Modifié",
                "role": "author",
                "is_active": True
            }
        }
    )
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    profile_image: Optional[str] = Field(None, pattern=r'^https?://')
    role: Optional[str] = Field(None, pattern=r'^(admin|author|user)$')
    is_active: Optional[bool] = None

    @field_validator('username')
    @classmethod
    def username_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError('Username must contain only letters, numbers, hyphens and underscores')
        return v

class UserResponse(BaseModel):
    """Modèle de réponse pour les utilisateurs"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(alias="_id")
    clerk_id: str
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class UserLogin(BaseModel):
    """Modèle pour tracer les connexions"""
    clerk_id: str = Field(..., description="ID utilisateur Clerk")
    
    @field_validator('clerk_id')
    @classmethod
    def clerk_id_must_be_valid(cls, v: str) -> str:
        if not v.startswith('user_'):
            raise ValueError('Clerk ID must start with user_')
        return v