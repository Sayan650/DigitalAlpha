import type { Metadata } from "next";
import { QueryProvider } from "../components/query-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "Coinwise | Spend smarter",
  description: "Transactions, spending analytics, and rewards in one place.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body><QueryProvider>{children}</QueryProvider></body>
    </html>
  );
}

