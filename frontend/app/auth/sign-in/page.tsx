import { SignIn, SignInButton } from "@clerk/nextjs";
import { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Connexion - Mon Blog",
  description: "Connectez-vous pour accéder à votre espace personnel",
  robots: "noindex, nofollow",
};

export default function SigInPage() {
  return (
    <div className="min-h-screen flex flex-col justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Navigation retour*/}
        <div className="mb-6">
          <Link
            href="/"
            className="flex items-center text-sm text-gray-600 hover:text-gray-800 transition-colors"
          >
            <ArrowLeft size={16} className="mr-2" />
            Retour accueil
          </Link>
        </div>
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🔐Connexion</h1>
          <p className="text-gray-600">Accédez à votre espace de création</p>
        </div>
        {/* Clerk Component */}
        <div className="flex justify-center">
          <SignIn
            appearance={{
              elements: {
                headerTitle: "hidden",
                headerSubtitle: "hidden",
                footerAction: "hidden",
                badge: "hidden",
                formButtonPrimary: "bg-blue-600 hover:bg-blue-700",
              },
            }}
          />
        </div>
        {/* Lien connexion */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Pas encore de compte ?{"   "}
            <Link
              href="/auth/sign-up"
              className="text-blue-600 hover:text-blue-500 font-medium"
            >
              Créer un compte
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
