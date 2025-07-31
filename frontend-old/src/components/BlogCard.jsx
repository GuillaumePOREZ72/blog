import React from "react";

export default function BlogCard({ title, desc, image, onClick }) {
  // Function to get an optimized image URL, falling back to a placeholder
  const getImageUrl = (url) => {
    if (!url) {
      // Use a reliable placeholder or a local fallback
      // For now, let's return null or a simple placeholder to avoid the failing via.placeholder
      return null; // Or a path to a local placeholder image
    }

    // If it's already a Cloudinary URL, use it directly
    if (url.includes('res.cloudinary.com')) {
      return url;
    }

    // If it's another valid URL type you want to support, handle it here
    // For now, treat non-Cloudinary URLs as needing a fallback if not valid
    return null; // Fallback for non-Cloudinary or invalid URLs
  };

  const imageUrl = getImageUrl(image);

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition cursor-pointer overflow-hidden border mb-4">
      <div
        onClick={onClick}
        className="flex flex-row justify-between items-center p-4 gap-4"
      >
        <div className="flex-1 text-left">
          <h2 className="text-xl font-semibold mb-2">{title}</h2>
          <p className="text-gray-700">{desc?.slice(0, 100)}</p>
        </div>
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={title}
            className="w-[100px] h-[100px] object-cover rounded-md bg-gray-100"
          // Remove the onError handler since getImageUrl handles fallbacks
          />
        ) : (
          // Display a fallback element when there's no valid image URL
          <div className="w-[100px] h-[100px] bg-gray-200 rounded-md flex items-center justify-center text-gray-500 text-sm">
            No Image
          </div>
        )}
      </div>
    </div>
  );
}
