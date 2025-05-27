from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Post(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    slug: str
    title: str
    desc: str
    content: str
    img: Optional[str] = None

    class Config:
        #allow alias mapping (e.g., "_id" to "id")
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "slug": "my-post",
                "title": "My Post",
                "desc": "This is my post",
                "content": "This is the content of my post",
                "img": "https://example.com/img.jpg",
            }
        }

class PostUpdate(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    slug: str=None
    title: Optional[str] = None
    desc: Optional[str] = None
    content: Optional[str] = None
    img: Optional[str] = None

  
