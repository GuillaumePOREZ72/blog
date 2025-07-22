import React from "react";

export default function Modal({ onClickNo, onClickYes }) {
  return (
    <div
      className="flex items-center justify-center fixed left-0 bottom-0 w-full h-full"
      style={{ backgroundColor: "rgba(185, 185, 185, 0.4)" }}
    >
      <div className="bg-white rounded-md p-12">
        <h1 className="text-[16px] font-semibold">
          Are you sure you want to delete this blog ?{" "}
        </h1>
        <div className="flex flex-row items-center my-4 justify-center gap-x-3">
          <button
            onClick={onClickNo}
            className="bg-gray-300 border rounded-full cursor-pointer p-3 shadow-sm hover:shadow-lg hover:bg-gray-400 transition"
          >
            No
          </button>
          <button
            onClick={onClickYes}
            className="bg-blue-300 border rounded-full cursor-pointer p-3 shadow-sm hover:shadow-lg hover:bg-blue-400 transition"
          >
            Yes
          </button>
        </div>
      </div>
    </div>
  );
}
