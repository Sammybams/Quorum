import "./globals.css";
import type { ReactNode } from "react";

const APP_URL = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";

export const metadata = {
  metadataBase: new URL(APP_URL),
  title: "Quorum",
  description: "Student body operating system",
  icons: {
    icon: "/brand/quorum-favicon.svg",
    shortcut: "/brand/quorum-favicon.svg",
  },
  openGraph: {
    title: "Quorum",
    description: "Where student bodies get things done.",
    images: ["/brand/quorum-icon.svg"],
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
