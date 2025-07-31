import React, { useState, useRef, useCallback } from "react";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Image from "@tiptap/extension-image";
import Heading from "@tiptap/extension-heading";
import Underline from "@tiptap/extension-underline";
import CodeBlock from "@tiptap/extension-code-block";
import Link from "@tiptap/extension-link";
import Placeholder from "@tiptap/extension-placeholder";
import "./WriteBlog.css";
import { uploadImage } from "../utils/cloudinary";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { IoIosCloseCircleOutline } from "react-icons/io";
import BackButton from '../components/BackButton';

export default function WriteBlog(
  isEdit = false,
  idData,
  titleData,
  descData,
  contentData,
  slugData,
  imgData,
  onClickEdit
) {
  const [title, setTitle] = useState(isEdit ? titleData : "");
  const [desc, setDesc] = useState(isEdit ? descData : "");
  const [slug, setSlug] = useState(isEdit ? slugData : "");
  const [media, setMedia] = useState(isEdit ? imgData : "");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const [editorContent, setEditorContent] = useState(
    isEdit ? contentData : "<p>Type Here...</p>"
  );
  const fileInputRef = useRef(null);

  const navigate = useNavigate();

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
      }),
      Image,
      Link.configure({
        autolink: true,
        openOnClick: true,
      }),
      Underline,
      Placeholder.configure({
        placeholder: "Type here...",
      }),
    ],
    content: isEdit ? contentData : "<p>Type Here...</p>",
    onUpdate: ({ editor }) => {
      setEditorContent(editor.getHTML());
    },
  });

  const addImage = useCallback(
    async (e) => {
      const selectedFile = e.target.files[0];
      try {
        const fileUrl = await uploadImage(selectedFile);
        if (fileUrl && editor) {
          editor.chain().focus().setImage({ src: fileUrl }).run();
          setMedia(fileUrl);
        }
      } catch (error) {
        console.error("Error uploading image:", error);
      }
    },
    [editor]
  );

  const handleImageClick = (e) => {
    e.preventDefault();
    fileInputRef.current.click();
  };

  const handleSubmit = async (e) => {
    console.log("handleSubmit called");
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const slug = title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");
      const postData = {
        title,
        slug,
        desc,
        content: editorContent,
        img: media,
      };
      console.log("Sending post data:", postData);
      const response = await axios.post(
        "http://localhost:8000/api/v1/posts",
        postData
      );
      console.log("Server Response:", response.data);
      if (response.status === 201) {
        // Reset form fields and state
        setTitle("");
        setDesc("");
        setEditorContent("");
        setMedia("");
        if (editor) {
          editor.commands.clearContent();
        }
        navigate("/");
        console.log("Post created successfully!");
      }
    } catch (error) {
      console.error("Error submitting blog:", error.response || error);
      setError("Failed to publish blog. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 py-12">
      <div className="flex flex-col w-[740px] md:w-[560px]">
        <div className="flex flex-row justify-between items-center mb-6">
          <div className="flex items-center gap-4">
            <BackButton />
            <h1 className="text-2xl font-bold">
              {isEdit ? "Modifier" : "Écrire"} un article
            </h1>
          </div>
          {/* back button to cancel edit */}
          {isEdit && (
            <button
              onClick={onClickEdit}
              className="bg-gray-300 border rounded-md p-3 shadow-sm hover:shadow-lg hover:bg-gray-400 transition"
              aria-label="Annuler la modification"
            >
              <IoIosCloseCircleOutline className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
          <input
            className="py-4 h-[60px] text-4xl border-none outline-none bg-transparent placeholder:text-[#b3b3b1]"
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <input
            className="py-4 h-[60px] text-xl border-none outline-none bg-transparent placeholder:text-[#b3b3b1]"
            type="text"
            placeholder="Description"
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
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
                type="button"
                onClick={handleImageClick}
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
          <EditorContent editor={editor} />
          <div className="text-left">
            <button type="submit" className="px-5 py-2.5 bg-[#1a8917] text-white cursor-pointer hover:shadow-lg hover:scale-105 rounded disabled:opacity-50">
              {isEdit ? "Update" : "Publish"}
            </button>
          </div>
        </form >
      </div >
    </div >
  );
}
