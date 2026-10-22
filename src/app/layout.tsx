import type { CSSProperties, ReactNode } from "react";
import type { Metadata } from "next";
import { Fraunces, Noto_Sans_SC, Noto_Serif_SC } from "next/font/google";
import "./globals.css";

const display = Fraunces({
  variable: "--font-display-latin",
  subsets: ["latin"],
  axes: ["SOFT", "WONK", "opsz"],
});

const serifSc = Noto_Serif_SC({
  variable: "--font-display-sc",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

const body = Noto_Sans_SC({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "每日菜单 · Daily Menu",
  description: "为今天的三餐排好序，少纠结、多吃好。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  const fontStyle = {
    "--font-display":
      "var(--font-display-latin), var(--font-display-sc), serif",
  } as CSSProperties;

  return (
    <html
      lang="zh-CN"
      className={`${display.variable} ${serifSc.variable} ${body.variable} h-full antialiased`}
      style={fontStyle}
    >
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
