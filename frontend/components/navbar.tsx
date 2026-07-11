"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { LogIn, LogOut, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { clearToken, isAuthenticated } from "@/lib/auth";

export function Navbar() {
  const router = useRouter();
  // Auth state only exists client-side; render a neutral navbar until mounted
  // to keep server and client markup identical.
  const [mounted, setMounted] = useState(false);
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setMounted(true);
    setAuthed(isAuthenticated());
  }, []);

  function handleLogout() {
    clearToken();
    setAuthed(false);
    router.push("/login");
  }

  return (
    <header className="sticky top-0 z-40 border-b-2 border-pink-200/70 bg-white/70 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="group flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-pink-400 to-fuchsia-400 shadow-candy text-lg animate-heartbeat">
            🎀
          </span>
          <span className="text-lg font-bold tracking-tight group-hover:opacity-80 transition-opacity">
            <span className="text-gradient font-cute text-xl">Research</span>
          </span>
        </Link>

        <nav className="flex items-center gap-2">
          {mounted && authed && (
            <>
              <Button variant="ghost" size="sm" onClick={() => router.push("/")}>
                <Plus className="h-4 w-4" aria-hidden="true" />
                <span className="hidden sm:inline">New research</span>
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4" aria-hidden="true" />
                <span className="hidden sm:inline">Sign out</span>
              </Button>
            </>
          )}
          {mounted && !authed && (
            <>
              <Button variant="ghost" size="sm" onClick={() => router.push("/login")}>
                <LogIn className="h-4 w-4" aria-hidden="true" />
                Sign in
              </Button>
              <Button size="sm" onClick={() => router.push("/register")}>
                Get started ✨
              </Button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
