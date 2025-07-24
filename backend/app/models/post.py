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

class Post(BaseModel):
    """Modèle principal pour les posts"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    slug: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    desc: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    img: Optional[str] = Field(None, regex=r'^https?://')
    author_id: Optional[str] = Field(None, description="ID utilisateur Clerk")
    is_published: bool = Field(default=False)
    tags: Optional[List[str]] = Field(default_factory=list)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @validator('slug')
    def slug_must_be_valid(cls, v):
        """Validation du slug pour URL"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError("Slug must contain only lowercase letters, numbers and hyphens")
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
                "slug": "my-post",
                "title": "My Post",
                "desc": "This is my post description",
                "content": "This is the entire content of my post",
                "img": "https://res.cloudinary.com/example/image.jpg",
                "author_id": "user_2abc123def456",
                "is_published": True,
                "tags": ["tech", "Python", "fastapi", "mongodb"]
            }
        }


class PostCreate(BaseModel):
    """Modèle pour la création de posts"""
    slug: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    desc: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    img: Optional[str] = Field(None, regex=r'^https?://')
    is_published: bool = Field(default=False)
    tags: Optional[List[str]] = Field(default_factory=list)

    @validator('slug')
    def slug_must_be_valid(cls, v):
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError("Slug must contain only lowercase letters, numbers and hyphens")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "slug": "new-post",
                "title": "New Post",
                "desc": "New post description",
                "content": "Content of the post...",
                "img": "https://res.cloudinary.com/example/image.jpg",
                "is_published": False,
                "tags": ["nouveauté", "blog"]
            }        
        }

class PostUpdate(BaseModel):
    """Modèle pour la mise à jour de posts"""
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    desc: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    img: Optional[str] = Field(None, regex=r'^https?://')
    is_published: Optional[bool] = None
    tags: Optional[List[str]] = None

    @validator('slug')
    def slug_must_be_valid(cls, v):
        """Validation du slug pour URL"""
        if v is not None:
            if not re.match(r'^[a-z0-9-]+$', v):
                raise ValueError("Slug must contain only lowercase letters, numbers and hyphen")
        return v

    class Config:
        schema_extra = {
            "example": {
                "title": "updated title",
                "desc": "updtaed description",
                "is_published": True,
                "tags": ["mise-à-jour", "blog"]
            }
        }

class PostResponse(BaseModel):
    """Modèle de réponse pour les posts"""
    id: str = Field(alias="_id")
    slug: str
    title: str
    desc: str
    content: str
    img: Optional[str]
    author_id: Optional[str]
    is_published: bool
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
