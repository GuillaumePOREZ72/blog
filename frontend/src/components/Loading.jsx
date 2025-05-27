import React from "react";

export default function Loading() {
  return (
    <div
      className="flex items-center justify-center fixed left-0 bottom-0 w-full h-full"
      style={{ backgroundColor: "rgb(185,185,185,0.4)" }}
    >
      <div className="flex flex-col items-center bg-white py-2 px-5 border border-gray-100 shadow-xl cursor-default">
        <div className="relative w-20 h-8 flex justify-center items-center">
          <div className="absolute w-2 h-2 rounded-full bg-black left-2 animate-loaderDots1"></div>
          <div className="absolute w-2 h-2 rounded-full bg-black left-2 animate-loaderDots2"></div>
          <div className="absolute w-2 h-2 rounded-full bg-black left-8 animate-loaderDots2"></div>
          <div className="absolute w-2 h-2 rounded-full bg-black left-14 animate-loaderDots3"></div>
        </div>
        <div className="text-black text-xs font-light mt-2 text-center">
          Please wait...
        </div>
      </div>
    </div>
  );
}
