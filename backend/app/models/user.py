from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
import re

class PyObjectId(ObjectId):
    """Custom ObjectId field pour Pydantic compatible MongoDB"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class User(BaseModel):
    """Modèle utilisateur synchronisé avec Clerk"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    clerk_id: str = Field(..., description="ID unique Clerk", min_length=10)
    email: str = Field(..., min_length=3, max_length=254)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    profile_image: Optional[str] = Field(None, regex=r'^https?://')
    is_active: bool = Field(default=True)
    role: str = Field(default="user", regex=r'^(admin|author|user)$')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    @validator('email')
    def email_must_be_valid(cls, v):
        """Validation de l'email"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Format email invalide')
        return v.lower()

    @validator('username')
    def username_must_be_valid(cls, v):
        """Validation du nom d'utilisateur"""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError("Username must contain only letters, numbers, hyphens and undrscores")
        return v
    
    @validator('clerk_id')
    def clerk_id_must_be_valid(cls, v):
        """Validation de l'ID Clerk"""
        if not v.startwith('user_'):
            raise ValueError("Clerk ID must start with user_")
        return v
    
    @validator('updated_at', always=True)
    def set_updated_at(cls, v):
        """Met à jour automatiquement updated_at"""
        return datetime.utcnow()

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}
        schema_extra = {
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

class UserCreate(BaseModel):
    """Modèle pour la création d'utilisateur via webhook Clerk"""
    clerk_id: str = Field(..., description="ID unique Clerk", min_length=10)
    email: str = Field(..., min_length=3, max_length=254)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    profile_image: Optional[str] = Field(None, regex=r'^https?://')

    @validator('email')
    def email_must_be_valid(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Format email invalide')
        return v.lower()

    @validator('clerk_id')
    def clerk_id_must_be_valid(cls, v):
        if not v.startswith('user_'):
            raise ValueError('Clerk ID must start with user_')
        return v

    class Config:
        schema_extra = {
            "example": {
                "clerk_id": "user_2new123user456",
                "email": "newuser@example.com",
                "username": "newuser",
                "first_name": "Nouveau",
                "last_name": "Utilisateur",
                "profile_image": "https://img.clerk.com/newuser.jpg"
            }
        }

class UserUpdate(BaseModel):
    """Modèle pour la mise à jour d'utilisateur"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    profile_image: Optional[str] = Field(None, regex=r'^https?://')
    role: Optional[str] = Field(None, regex=r'^(admin|author|user)$')
    is_active: Optional[bool] = None

    @validator('username')
    def username_must_be_valid(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError('Username must contain only letters, numbers, hyphens and underscores')
        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "nouveau_username",
                "first_name": "Prénom Modifié",
                "role": "author",
                "is_active": True
            }
        }

class UserResponse(BaseModel):
    """Modèle de réponse pour les utilisateurs"""
    id: str = Field(alias="_id")
    clerk_id: str
    email: str
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    profile_image: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        allow_population_by_field_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}

class UserLogin(BaseModel):
    """Modèle pour tracer les connexions"""
    clerk_id: str = Field(..., description="ID utilisateur Clerk")
    
    @validator('clerk_id')
    def clerk_id_must_be_valid(cls, v):
        if not v.startswith('user_'):
            raise ValueError('Clerk ID must start with user_')
        return v