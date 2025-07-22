import os
import cloudinary
import cloudinary.uploader # type: ignore
import cloudinary.api # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()

required_env_vars = ["CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
      raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
)

def upload_image(file_path: str, options: dict = None) -> dict:
      """
      Upload an image to Cloudinary
      
      Args:
            file_path: Path to the image file
            options: Optional dictionary of upload options

      Returns:
            Dictionary containing the uploaded image details
      """
      if options is None:
            options = {}
      return cloudinary.uploader.upload(file_path, **options)

def delete_image(public_id: str) -> dict:
      """
      Delete an image from Cloudinary

      Args:
            public_id: Cloudinary public ID of the image

      Returns:
            Dictionary containing the deletion response
      """
      return cloudinary.uploader.destroy(public_id)

