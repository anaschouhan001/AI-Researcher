"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api, ApiError } from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const res = await api.register(email.trim(), password);
      setToken(res.access_token);
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto mt-8 grid w-full max-w-4xl items-center gap-8 lg:grid-cols-2">
      {/* Retro pink computer illustration */}
      <div className="relative mx-auto hidden max-w-sm lg:block">
        <div className="animate-float overflow-hidden rounded-3xl border-4 border-white shadow-candy-lg rotate-2">
          <Image
            src="/retro-computer.jpg"
            alt="Retro pink computer illustration"
            width={380}
            height={676}
            priority
            className="h-auto w-full object-cover"
          />
        </div>
        <span className="absolute -left-3 -top-3 text-3xl animate-sparkle">🌷</span>
        <span className="absolute -bottom-3 -right-3 text-3xl animate-sparkle" style={{ animationDelay: "1.2s" }}>
          💕
        </span>
      </div>

      <Card className="w-full max-w-md justify-self-center">
        <CardHeader className="items-center text-center">
          <span className="mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-pink-200 to-fuchsia-100 border-2 border-pink-200 text-xl animate-bounce-soft">
            🎀
          </span>
          <CardTitle className="text-xl">Join the girl gang!</CardTitle>
          <CardDescription>Start running deep, multi-agent research in minutes. 💅</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <div className="space-y-1.5">
              <label htmlFor="email" className="text-sm font-semibold text-pink-700">
                Email 💌
              </label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                required
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="password" className="text-sm font-semibold text-pink-700">
                Password 🔐
              </label>
              <Input
                id="password"
                type="password"
                autoComplete="new-password"
                required
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="confirm" className="text-sm font-semibold text-pink-700">
                Confirm password 💝
              </label>
              <Input
                id="confirm"
                type="password"
                autoComplete="new-password"
                required
                placeholder="Repeat your password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
            </div>

            {error && (
              <p role="alert" className="rounded-2xl border-2 border-rose-300 bg-rose-50 px-3 py-2 text-sm text-rose-600">
                {error}
              </p>
            )}

            <Button
              type="submit"
              className="w-full"
              disabled={loading || !email || !password || !confirm}
            >
              {loading && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
              {loading ? "Creating account…" : "Create account 🌸"}
            </Button>
          </form>

          <p className="mt-5 text-center text-sm text-pink-500">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-fuchsia-600 hover:text-fuchsia-500">
              Sign in ✨
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
