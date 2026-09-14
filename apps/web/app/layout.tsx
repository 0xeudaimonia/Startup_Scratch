import { Inter } from "next/font/google";
import { Sidebar } from "@/components/layout/sidebar";
import { Providers } from "@/components/providers";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Startup Radar",
  description: "Discover newly funded and remote-friendly startups hiring engineers.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <div className="flex min-h-screen">
            <Sidebar />
            <main className="min-w-0 flex-1 overflow-auto p-6 lg:p-8">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
