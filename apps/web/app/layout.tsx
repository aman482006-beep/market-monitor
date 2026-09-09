import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Market Monitor", description: "Indian equity market intelligence terminal" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
