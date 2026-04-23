import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
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
