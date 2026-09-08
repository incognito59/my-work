import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RedCart // Command Center",
  description: "Premium commerce and live network intelligence.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
