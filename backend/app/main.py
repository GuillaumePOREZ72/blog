from fastapi import FastAPI
from app.routes.post_routes import router as post_router
from fastapi.middleware.cors import CORSMiddleware
from app.config.cloudinary import cloudinary

app = FastAPI()

origins = [
    "http://localhost:5173"
]

@app.on_event("startup")
async def startup_event():
    if not cloudinary.config().cloud_name:
        raise ValueError("Cloudinary configuration is not set")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Add posts router
app.include_router(post_router, prefix="/api/v1/posts", tags=["Posts"])