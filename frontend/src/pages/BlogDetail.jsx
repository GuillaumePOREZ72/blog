import React from "react";
import { useState, useEffect } from "react";
import { IoIosCloseCircleOutline } from "react-icons/io";
import { HiOutlinePencilAlt } from "react-icons/hi";
import { FaTrashAlt } from "react-icons/fa";
import Modal from "../components/Modal";
import Loading from "../components/Loading";
import { useNavigate, useParams } from "react-router-dom";
import WriteBlog from './WriteBlog'
import BackButton from '../components/BackButton'

export default function BlogDetail() {
  // Utilisation de useParams pour récupérer l'ID
  const { id: idUrl } = useParams()
  const navigate = useNavigate()

  // États
  const [isEdit, setIsEdit] = useState(false);
  const [isDelete, setIsDelete] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null)
  const [blog, setBlog] = useState(null);

  // Fonction de récupération des données
  const fetchData = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Ajout de logs pour le débogage
      console.log("Fetching blog with ID:", idUrl);

      const response = await fetch(
        `http://localhost:8000/api/v1/posts/${idUrl}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      // Log de la réponse brute
      console.log("Raw response:", response);

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`)
      }

      const data = await response.json();
      // Log des données reçues
      console.log("Received data:", data);

      // Vérification de la structure de la réponse
      if (!data || !data.result) {
        throw new Error('Format de réponse invalide');
      }

      const { result } = data;

      // Vérification si result est un tableau et contient des données
      if (!Array.isArray(result) || result.length === 0) {
        throw new Error('Aucun article trouvé');
      }

      const [blogData] = result;

      // Vérification des données de l'article
      if (!blogData || !blogData.id || !blogData.title) {
        throw new Error('Données de l\'article incomplètes');
      }

      setBlog({
        id: blogData.id,
        title: blogData.title,
        desc: blogData.description || '',
        content: blogData.content || '',
        img: blogData.image || '',
        slug: blogData.slug || '',
      });
    } catch (error) {
      console.error("Erreur détaillée:", error);
      setError(error.message || 'Une erreur est survenue lors du chargement de l\'article');
      setBlog(null);
    } finally {
      setIsLoading(false)
    }
  };

  // Fonction de suppression
  const handleDelete = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await fetch(`http://localhost:8000/api/v1/posts/${idUrl}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) {
        throw new Error(`Erreur lors de la suppression: ${response.status}`)
      }
      navigate("/");
    } catch (error) {
      console.error("Erreur lors de la suppression:", error)
      setError(error.message || 'Une erreur est survenue lors de la suppression')
    } finally {
      setIsLoading(false)
      setIsDelete(false)
    }
  };

  useEffect(() => {
    if (idUrl) {
      fetchData();
    }
  }, [idUrl]);

  // Rendu conditionnel du contenu
  const renderContent = () => {
    if (isLoading) {
      return <Loading />;
    }

    if (error) {
      return (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4">
          {error}
        </div>
      );
    }

    if (!blog) {
      return (
        <div className="text-gray-500">
          Aucun article trouvé
        </div>
      );
    }

    if (isEdit) {
      return (
        <WriteBlog
          isEdit={true}
          idData={idUrl}
          titleData={blog.title}
          descData={blog.desc}
          contentData={blog.content}
          slugData={blog.slug}
          imgData={blog.img}
          onClickEdit={() => setIsEdit(false)}
        />
      );
    }

    return (
      <div id="content">

        <div className="flex flex-row justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">{blog.title}</h1>
          <div className="flex gap-3">
            <button
              onClick={() => setIsEdit(true)}
              className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-md transition-colors"
              aria-label="Modifier l'article"
            >
              <HiOutlinePencilAlt className="h-4 w-4" />
            </button>
            <button
              onClick={() => setIsDelete(true)}
              className="bg-red-500 hover:bg-red-600 text-white p-3 rounded-md transition-colors"
              aria-label="Supprimer l'article"
            >
              <FaTrashAlt className="h-4 w-4" />
            </button>
          </div>
        </div>

        <h2 className="text-xl text-gray-700 mb-6">
          {blog.desc}
        </h2>

        <div className="prose max-w-none">
          <div
            className="text-lg text-gray-800"
            dangerouslySetInnerHTML={{ __html: blog.content }}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-6">
          <BackButton />
        </div>

        {isDelete && (
          <Modal
            onClickNo={() => setIsDelete(false)}
            onClickYes={handleDelete}
            title="Confirmer la suppression"
            message="Êtes-vous sûr de vouloir supprimer cet article ?"
          />
        )}

        {renderContent()}
      </div>
    </div>
  );
}
