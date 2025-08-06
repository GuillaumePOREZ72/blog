import { SignUp } from "@clerk/nextjs";
import { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Inscription - Mon Blog",
  description: "Rejoignez notre communauté de créateurs",
  robots: "noindex, nofollow",
};

export default function SigUpPage() {
  return (
    <div className="min-h-screen flex flex-col justify-center bg-gradient-to-br from-green-50 to-emerald-100">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Navigation retour */}
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            ✨ Rejoignez-nous
          </h1>
          <p className="text-gray-600">
            Créez votre compte et commencez à publier
          </p>
        </div>
        {/* Clerk Component */}
        <div className="flex justify-center">
          <SignUp
            appearance={{
              elements: {
               headerTitle: "hidden",
               headerSubtitle: "hidden",
               footerAction: "hidden",
               badge: "hidden",
               formButtonPrimary: "bg-green-600 hover:bg-green-700"
              },
            }}
          />
        </div>
        {/* Lien connexion */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Déjà un compte ?{"  "}
            <Link
              href="/auth/sign-in"
              className="text-green-600 hover:text-green-500 font-medium"
            >
              Se connecter
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
