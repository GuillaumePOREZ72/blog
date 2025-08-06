import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">📝 Mon Blog</h1>
          <p className="text-xl text-gray-600 mb-8">
            Plateforme moderne de blog avec Next.js 15, TypeScript et TipTap
          </p>

          {/* Navigation Auth pour tests */}
          <div className="flex justify-center gap-4 mb-8">
            <Link 
              href="/auth/sign-in"
              className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
            >
              🔐 Connexion
            </Link>
            <Link 
              href="/auth/sign-up"
              className="px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-colors" 
            >
              ✨ Inscription
            </Link>
          </div>

          <div className="flex justify-center gap-4">
            <Link 
              href="/blog"
              className="px-6 py-3 bg-gray-600 text-white rounded-xl hover:bg-gray-700 transition-colors"
            >
              📚 Voir les articles
            </Link>
            <Link 
              href="/create"
              className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors"
            >
              ✍️ Écrire un article
            </Link>
          </div>
        </div>

        {/* Features grid */}
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h3 className="text-xl font-semibold mb-3">🚀 Next.js 15</h3>
            <p className="text-gray-600">Framework React moderne avec App Router et Turbopack</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h3 className="text-xl font-semibold mb-3">🔐 Clerk Auth</h3>
            <p className="text-gray-600">Authentification sécurisée avec gestion des rôles</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h3 className="text-xl font-semibold mb-3">📝 TipTap</h3>
            <p className="text-gray-600">Éditeur riche et moderne pour créer du contenu</p>
          </div>
        </div>
      </div>
    </div>
  );
}
