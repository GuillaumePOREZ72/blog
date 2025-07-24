from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from ..models.post import PostCreate, PostUpdate, PostResponse
from ..services.post_service import post_service
from ..middleware.auth import (
    get_current_user,
    require_author_or_admin,
    get_optional_user
)


# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Create Post
@router.post("/", response_model=PostResponse, status_code=201)
async def create_post(
    post_data: PostCreate, 
    current_user: dict = Depends(require_author_or_admin)
):
    """Crée un nouveau post (authentification requise)"""
    try:
        logger.info(f"Création post par utilisateur: {current_user['clerk_id']}")
        new_post = await post_service.create_post(
            post_data=post_data,
            author_id=current_user["clerk_id"]
        )
        logger.info(f"Post créé avec succès: {new_post.id}")
        return new_post
    
    except ValueError as e:
        logger.error(f"Erreur validation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur création post: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne au serveur")


# Read All Posts
@router.get("/", response_description="List all posts")
async def list_post():
    try:
        posts = await db.posts.find().to_list(100)
        logger.info(f"Found {len(posts)} posts")
        return {"status": 200, "result": [post_helper(post) for post in posts]}
    except Exception as e:
        logger.error(f"Error fetching posts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Read Single Post by Id
@router.get("/{id}", response_description="Get a single post")
async def read_post(id: str):
    if(post := await db.posts.find_one({"_id":id})) is not None:
        return {"status": 200, "result": [post_helper(post)]}
    raise HTTPException(status_code=404, detail=f"Post {id} not found")


# Update Post
@router.put("/{id}", response_description="Update a post")
async def update_post(id:str, post: PostUpdate):
    post_dict = {k: v for k, v in post.dict(by_alias=True).items() if v is not None}
    if len(post_dict) >= 1:
        update_result = await db.posts.update_one(
            {"_id": id}, {"$set": post_dict}
        )
        if update_result.modified_count == 1:
            if(updated_post := await db.posts.find_one({"_id": id})) is not None:
                return {"status":200, "result": post_helper(updated_post)}
    if (existing_post := await db.posts.find_one({"_id": id})) is not None:
        return {"status":200, "result": post_helper(existing_post)}
    raise HTTPException(status_code=404, detail=f"Post {id} not found")


# Delete Post
@router.delete("/{id}", response_description="Delete a post")
async def delete_post(id:str):
    delete_result = await db.posts.delete_one({"_id": id})
    if delete_result.deleted_count == 1:
        return {"status":200, "result": f"Post {id} deleted"}
    raise HTTPException(status_code=404, detail=f"Post {id} not found")

