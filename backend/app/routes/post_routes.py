from fastapi import APIRouter, HTTPException
from app.models.post import Post, PostUpdate
from app.config import db
from uuid import uuid4


router = APIRouter()


# Helper to convert MongoDB ObjectId to string
def post_helper(post) -> dict:
    return {
        "id": str(post["_id"]),
        "created_at": str(post["created_at"]),
        "slug": str(post["slug"]),
        "title": str(post["title"]),
        "desc": str(post["desc"]),
        "content": str(post["content"]),
        "img": str(post["img"]),
    }

# Create Post
@router.post("/", response_description="Add new post")
async def create_post(post:Post):
    post_dict = post.dict(by_alias=True)
    post_dict["_id"] = str(uuid4()) #generate random uuid for id
    result = await db.posts.insert_one(post_dict)
    new_post = await db.posts.find_one({"_id": result.inserted_id})
    return {"status":201, "result": post_helper(new_post)}


# Read All Posts
@router.get("/", response_description="List all posts")
async def list_post():
    posts = await db.posts.find().to_list(100)
    return {"status":201, "result": [post_helper(post) for post in posts]}


# Read Single Post by Id
@router.get("/{id}", response_description="Get a single post")
async def read_post(id: str):
    if(post := await db.posts.find_one({"_id":id})) is not None:
        return {"status": 200, "result": post_helper(post)}
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

