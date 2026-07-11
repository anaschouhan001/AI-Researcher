import type { Metadata } from "next";
import { Pacifico, Quicksand } from "next/font/google";
import { Navbar } from "@/components/navbar";
import "./globals.css";

const quicksand = Quicksand({
  subsets: ["latin"],
  variable: "--font-quicksand",
});

const pacifico = Pacifico({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-pacifico",
});

export const metadata: Metadata = {
  title: {
    default: "Research 🎀 AI Research Platform",
    template: "%s · Research 🎀",
  },
  description:
    "Autonomous multi-agent deep research: reports, sources, knowledge graphs, fact-checking and podcasts — with extra sparkle.",
};

function FloatingHearts() {
  const hearts = [
    { left: "5%", delay: "0s", size: "1rem", emoji: "💕" },
    { left: "16%", delay: "3.5s", size: "1.3rem", emoji: "🌸" },
    { left: "28%", delay: "7s", size: "0.9rem", emoji: "💖" },
    { left: "42%", delay: "1.8s", size: "1.1rem", emoji: "✨" },
    { left: "57%", delay: "5.2s", size: "1rem", emoji: "🎀" },
    { left: "69%", delay: "9s", size: "1.2rem", emoji: "💗" },
    { left: "81%", delay: "2.6s", size: "0.9rem", emoji: "🌷" },
    { left: "92%", delay: "6.4s", size: "1.1rem", emoji: "💝" },
  ];
  return (
    <div className="hearts-bg" aria-hidden="true">
      {hearts.map((h, i) => (
        <span key={i} style={{ left: h.left, animationDelay: h.delay, fontSize: h.size }}>
          {h.emoji}
        </span>
      ))}
    </div>
  );
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${quicksand.variable} ${pacifico.variable}`}>
      <body className="flex min-h-screen flex-col font-sans font-medium">
        <FloatingHearts />
        <Navbar />
        <main className="relative z-10 mx-auto w-full max-w-7xl flex-1 px-4 pb-12 pt-6 sm:px-6 lg:px-8">
          {children}
        </main>
        <footer className="relative z-10 border-t-2 border-pink-200/70 bg-white/50 py-6 backdrop-blur-sm">
          <div className="mx-auto max-w-7xl px-4 text-center text-xs text-pink-400 sm:px-6 lg:px-8">
            Made with 💖 · Research — autonomous multi-agent research. Verify
            critical findings against primary sources.
          </div>
        </footer>
      </body>
    </html>
  );
}
