from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re

class Post(BaseModel):
    """Modèle principal pour les posts"""
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
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
    )
    
    id: Optional[str] = Field(None, alias="_id")  # ✅ String au lieu de PyObjectId
    slug: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    desc: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    img: Optional[str] = Field(None, pattern=r'^https?://')
    author_id: Optional[str] = Field(None, description="ID utilisateur Clerk")
    is_published: bool = Field(default=False)
    tags: Optional[List[str]] = Field(default_factory=list)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator('slug')
    @classmethod
    def slug_must_be_valid(cls, v: str) -> str:
        """Validation du slug pour URL"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError("Slug must contain only lowercase letters, numbers and hyphens")
        return v

    @field_validator('updated_at')
    @classmethod
    def set_updated_at(cls, v: datetime) -> datetime:
        """Met à jour automatiquement updated_at"""
        return datetime.utcnow()

class PostCreate(BaseModel):
    """Modèle pour la création de posts"""
    model_config = ConfigDict(
        json_schema_extra={
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
    )
    
    slug: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    desc: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    img: Optional[str] = Field(None, pattern=r'^https?://')
    is_published: bool = Field(default=False)
    tags: Optional[List[str]] = Field(default_factory=list)

    @field_validator('slug')
    @classmethod
    def slug_must_be_valid(cls, v: str) -> str:
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError("Slug must contain only lowercase letters, numbers and hyphens")
        return v

class PostUpdate(BaseModel):
    """Modèle pour la mise à jour de posts"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated title",
                "desc": "Updated description",
                "is_published": True,
                "tags": ["mise-à-jour", "blog"]
            }
        }
    )
    
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    desc: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    img: Optional[str] = Field(None, pattern=r'^https?://')
    is_published: Optional[bool] = None
    tags: Optional[List[str]] = None

    @field_validator('slug')
    @classmethod
    def slug_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        """Validation du slug pour URL"""
        if v is not None:
            if not re.match(r'^[a-z0-9-]+$', v):
                raise ValueError("Slug must contain only lowercase letters, numbers and hyphens")
        return v

class PostResponse(BaseModel):
    """Modèle de réponse pour les posts"""
    model_config = ConfigDict(populate_by_name=True)
    
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
