import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Quorum",
  description: "Student body operating system",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
