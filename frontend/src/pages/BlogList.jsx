import React from "react";
import { useState, useEffect } from "react";
import { HiOutlinePencilAlt } from "react-icons/hi";
import BlogCard from "../components/BlogCard";
import Loading from "../components/Loading";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function BlogList() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [blogs, setBlogs] = useState([
    {
      id: "1",
      title: "Hello World",
      desc: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
      image: "https://picsum.photos/200",
      slug: "hello-world",
    },
  ]);

  // Fetch data from API
  const fetchBlogs = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get("http://localhost:8000/api/v1/posts");
      console.log(response.data.result);
      setBlogs(response.data.result);
      setIsLoading(false);
    } catch (error) {
      console.log(error);
      setIsLoading(false);
    } finally {
      setTimeout(() => {
        setIsLoading(false);
      }, 1000);
      console.log("done");
    }
  };

  useEffect(() => {
    fetchBlogs();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      {isLoading ? <Loading/> : null}
      <div className="flex flex-col w-[740px] md:w-[560px]">
        <div className="flex flex-row justify-between">
          <h1 className="text-2xl font-bold mb-4">Blog List</h1>
          <button className="border rounded-md p-3 shadow-sm hover:shadow-lg hover:bg-gray-100 transition"
            onClick={() => navigate("/write")}
          >
            <HiOutlinePencilAlt className="w-4 h-4 hover:text-white" />
          </button>
        </div>
        <div className="grid gap-4 m-3">
          {blogs && blogs.length > 0 ? (
            blogs.map((item, index) => (
              <BlogCard
                key={item.id || index}
                title={item.title}
                desc={item.desc}
                image={item.image}
                onClick={() => navigate(`/blog/${item.id}`)}
              />
            ))
          ) : (
            <div className="text-center text-gray-500">Aucun blog trouvé</div>
          )}
        </div>
      </div>
    </div>
  );
}
