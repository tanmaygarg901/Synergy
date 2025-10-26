import { Inter } from "next/font/google";
import "./globals.css";
import "react-chatbot-kit/build/main.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Synergy - AI Collaborator Finder",
  description: "Find your perfect co-founder with AI",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
