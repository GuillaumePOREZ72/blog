import React, { useState, useRef, useCallback } from "react";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Image from "@tiptap/extension-image";
import Heading from "@tiptap/extension-heading";
import Bold from "@tiptap/extension-bold";
import Italic from "@tiptap/extension-italic";
import Underline from "@tiptap/extension-underline";
import CodeBlock from "@tiptap/extension-code-block";
import Link from "@tiptap/extension-link";
import "./WriteBlog.css";

export default function WriteBlog() {
  const [editorContent, setEditorContent] = useState("<p>Type here...</p>");
  const fileInputRef = useRef(null);
  const [media, setMedia] = useState("");

  const editor = useEditor({
    extensions: [
      StarterKit,
      Image,
      Link.configure({
        autolink: true,
        openOnClick: true,
      }),
      Heading.configure({
        levels: [1, 2, 3],
      }),
      Bold,
      Italic,
      Underline,
      CodeBlock,
    ],
    content: "<p>Type here...</p>",
    onUpdate: ({ editor }) => {
      setEditorContent(editor.getHTML());
    },
  });

  const addImage = useCallback(
    async (e) => {
      const selectedFile = e.target.files[0];
      // upload file to firebase
      const fileFormat = new Date().getTime() + selectedFile.name + "_";
      const folderName = "write_blog/";
      const fileUrl = await firebase.uploadFileAsync(
        folderName,
        selectedFile,
        fileFormat,
        2
      );
      if (fileUrl) {
        if (editor) {
          editor.chain().focus().setImage({ src: fileUrl }).run();
          setMedia(fileUrl);
        }
      }
    },
    [editor]
  );

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 py-12">
      <div className="flex flex-col w-[740px] md:w-[560px]">
        <div className="flex flex-row justify-between">
          <h1 className="text-2xl font-bold mb-4">Write Blog</h1>
        </div>
        {/* Form */}
        <form action="" className="flex flex-col space-y-4">
          <input
            className="py-4 h-[60px] text-4xl border-none outline-none bg-transparent placeholder:text-[#b3b3b1]"
            type="text"
            placeholder="Title"
          />
          <input
            className="py-4 h-[60px] text-xl border-none outline-none bg-transparent placeholder:text-[#b3b3b1]"
            type="text"
            placeholder="Description"
          />
          {/* Button group options */}
          <div className="flex flex-row gap-x-3">
            <button
              type="button"
              disabled={!editor.can().chain().focus().toggleBold().run()}
              onClick={() => editor.chain().focus().toggleBold().run()}
              className={
                editor.isActive("bold")
                  ? "px-3 bg-black text-white"
                  : "px-3 bg-[#b3b3b1] text-white"
              }
            >
              Bold
            </button>
            <button
              type="button"
              onClick={() => editor.chain().focus().toggleItalic().run()}
              disabled={!editor.can().chain().focus().toggleItalic().run()}
              className={
                editor.isActive("italic")
                  ? "px-3 bg-black text-white"
                  : "px-3 bg-[#b3b3b1] text-white"
              }
            >
              Italic
            </button>
            <button
              type="button"
              onClick={() => editor.chain().focus().toggleStrike().run()}
              disabled={!editor.can().chain().focus().toggleStrike().run()}
              className={
                editor.isActive("strike")
                  ? "px-3 bg-black text-white"
                  : "px-3 bg-[#b3b3b1] text-white"
              }
            >
              Strike
            </button>
            <button
              type="button"
              onClick={() => editor.chain().focus().toggleCode().run()}
              disabled={!editor.can().chain().focus().toggleCode().run()}
              className={
                editor.isActive("code")
                  ? "px-3 bg-black text-white"
                  : "px-3 bg-[#b3b3b1] text-white"
              }
            >
              Code
            </button>
            {/* upload image button */}
            <div>
              <button
                onClick={() => {
                  e.preventDefault();
                  fileInputRef.current.click();
                }}
                className="px-3 text-white bg-[#b3b3b1]"
              >
                Image
              </button>
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: "none" }}
                onChange={addImage}
                accept="image/*"
              />
            </div>
          </div>
          <EditorContent
            editor={editor}
            className="min-h-[300px] border rounded p-4"
          />
          <div className="text-left">
            <button
              className="px-5 py-2.5 bg-[#1a8917] text-white cursor-pointer hover:shadow-lg hover:scale-105 rounded"
              type="submit"
            >
              Publish
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
