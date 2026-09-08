import type { Metadata, Viewport } from "next";
import { Suspense } from "react";
import { Geist, JetBrains_Mono } from "next/font/google";
import { Providers } from "./providers";
import { AppChrome } from "@/components/AppChrome";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin", "cyrillic"],
});

const jetbrains = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin", "cyrillic"],
});

export const metadata: Metadata = {
  title: "Сборная — готовность",
  description: "Операционный дашборд готовности",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="ru"
      data-theme="light"
      className={`${geistSans.variable} ${jetbrains.variable} h-full antialiased`}
    >
      <body className="min-h-full">
        <Providers>
          <Suspense>
            <AppChrome>{children}</AppChrome>
          </Suspense>
        </Providers>
      </body>
    </html>
  );
}