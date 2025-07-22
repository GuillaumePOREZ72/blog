from app.config.cloudinary import cloudinary # type: ignore


def main():
    print("Cloudinary Configuration:")
    print(f"Cloud Name: {cloudinary.config().cloud_name}")
    print(f"API Key: {cloudinary.config().api_key}")
    print(f"API Secret: {'*' * len(cloudinary.config().api_secret)}")

if __name__ == "__main__":
    main()

