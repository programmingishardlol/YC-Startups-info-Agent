import type { Metadata } from "next";

import "@/app/globals.css";

export const metadata: Metadata = {
  title: "YC Startup Research Agent",
  description: "Clean report UI for the latest YC startup research output.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
