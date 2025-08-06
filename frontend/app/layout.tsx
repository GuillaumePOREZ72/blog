import { ClerkProvider } from "@clerk/nextjs";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Mon Blog - Plateforme de publication moderne",
  description: "Créez et partagez vos articles avec sécurité et modernité",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="fr">
        <body className={inter.className}>
          <div className="min-h-screen bg-gray-50">
            <main className="flex-1">
              {children}
            </main>
          </div>
        </body>
      </html>
    </ClerkProvider>
  )
}
