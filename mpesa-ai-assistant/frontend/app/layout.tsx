import type { Metadata } from "next";
import { Sora, IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import { AuthProvider } from "@/lib/auth-context";
import "./globals.css";

const sora = Sora({ subsets: ["latin"], weight: ["500", "600", "700"], variable: "--font-sora" });
const plexSans = IBM_Plex_Sans({ subsets: ["latin"], weight: ["400", "500", "600"], variable: "--font-plex-sans" });
const plexMono = IBM_Plex_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-plex-mono" });

export const metadata: Metadata = {
  title: "Fidika — Admin Panel",
  description: "Admin dashboard for the M-Pesa AI Assistant platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sora.variable} ${plexSans.variable} ${plexMono.variable}`}>
      <head>
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.47.0/tabler-icons.min.css"
        />
      </head>
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
