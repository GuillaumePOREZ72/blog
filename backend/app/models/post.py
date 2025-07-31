from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class PostBase(BaseModel):
    """Modèle de base pour les posts"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    slug: str = Field(..., min_length=1, max_length=100)
    excerpt: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_published: bool = Field(default=False)
    featured_image: Optional[str] = None

class PostCreate(PostBase):
    """Modèle pour la création de posts"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Mon Nouvel Article",
                "content": "Contenu de l'article...",
                "slug": "mon-nouvel-article",
                "excerpt": "Description courte",
                "is_published": False,
                "tags": ["tech", "blog"],
                "featured_image": "https://example.com/image.jpg"
            }       
        }
    )

class PostUpdate(BaseModel):
    """Modèle pour la mise à jour de posts"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    excerpt: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    featured_image: Optional[str] = None

class PostResponse(BaseModel):
    """Modèle de réponse pour les posts"""
    id: str
    title: str
    content: str
    slug: str
    excerpt: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_published: bool = Field(default=False)
    author_id: str
    author_email: Optional[str] = None
    featured_image: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes = True,
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    )
