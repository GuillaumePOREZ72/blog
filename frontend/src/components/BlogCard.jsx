import React from "react";

export default function BlogCard({title, desc, image, onClick}) {
  return (
    <div>
      <button
        onClick={onClick}
        className="border rounded-md p-8 shadow-sm hover:shadow-lg transition"
      >
        <div className="flex flex-row justify-between">
          <div className="text-left">
            <h2 className="text-xl font-semibold mb-2">{title}</h2>
            <p className="text-gray-700">{desc.slice(0,100)}</p>
          </div>
          <img src={image} alt={title} className="w-[100px] h-[100px]" />
        </div>
      </button>
    </div>
  );
}
