import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { cookies } from "next/headers";
import {
  ClerkProvider,
} from "@clerk/nextjs";
import Authenticate from "./aunthenticate";
import { Toaster } from 'react-hot-toast';

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "SchedulEase",
  description: "SchedulEase",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const defaultOpen = cookieStore.get("sidebar:state")?.value === "true";

  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex`}
      >
        <ClerkProvider>
          <SidebarProvider defaultOpen={defaultOpen}>
            <div className="dark">
              <AppSidebar />
            </div>
            <main className="flex-1">
              <SidebarTrigger />
              <Authenticate />
              {children}
            </main>
          </SidebarProvider>
        </ClerkProvider>
        <Toaster />
      </body>
    </html>
  );
}
