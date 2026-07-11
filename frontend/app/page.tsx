"use client";

import Image from "next/image";
import { motion, type Variants } from "framer-motion";
import {
  AudioLines,
  BarChart3,
  BookOpenCheck,
  FileText,
  GitBranch,
  Network,
  Scale,
  ShieldCheck,
} from "lucide-react";
import { HistoryList } from "@/components/history-list";
import { ResearchForm } from "@/components/research-form";

const FEATURES = [
  {
    icon: GitBranch,
    title: "Multi-agent pipeline 🤝",
    description: "Planner, researcher, retriever, fact-checker and writer agents collaborate on every topic.",
  },
  {
    icon: BookOpenCheck,
    title: "Papers, news & code 📚",
    description: "arXiv, news outlets, GitHub, Hugging Face and public datasets — gathered and cited.",
  },
  {
    icon: ShieldCheck,
    title: "Confidence scoring 💯",
    description: "Every claim is scored against its sources so you know exactly what to trust.",
  },
  {
    icon: Scale,
    title: "Conflict detection ⚖️",
    description: "Contradictory sources are surfaced side by side with the most likely correct position.",
  },
  {
    icon: BarChart3,
    title: "Auto visualizations 📊",
    description: "Charts, timelines and statistics generated straight from the evidence.",
  },
  {
    icon: Network,
    title: "Knowledge graphs 🕸️",
    description: "Interactive entity graphs and mind maps reveal how concepts connect.",
  },
  {
    icon: AudioLines,
    title: "Research podcasts 🎧",
    description: "Listen to your findings as a narrated podcast in English or Hindi.",
  },
  {
    icon: FileText,
    title: "Export anywhere 💌",
    description: "One-click Markdown, PDF, DOCX and HTML exports for sharing and archiving.",
  },
] as const;

const gridVariants: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.06 } },
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: "easeOut" } },
};

export default function HomePage() {
  return (
    <div className="space-y-16">
      {/* Hero — sized to fit one viewport for clean screenshots */}
      <section className="mx-auto max-w-6xl pt-2 sm:pt-4">
        <div className="grid items-center gap-6 lg:grid-cols-[1.15fr_0.85fr] lg:gap-10">
          <motion.div
            className="text-center lg:text-left"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          >
            <p className="mb-3 inline-flex items-center gap-1.5 rounded-full border-2 border-pink-300/60 bg-pink-100/80 px-4 py-1 text-xs font-bold text-pink-600 shadow-candy">
              <span className="animate-sparkle inline-block">✨</span>
              Autonomous AI research, end to end
              <span className="animate-sparkle inline-block" style={{ animationDelay: "1.2s" }}>✨</span>
            </p>
            <h1 className="text-3xl font-bold tracking-tight text-pink-800 sm:text-4xl xl:text-5xl">
              Ask once. Get a{" "}
              <span className="text-gradient font-cute">full research dossier</span>
              <span className="inline-block animate-heartbeat">💖</span>
            </h1>
            <p className="mx-auto mt-3 max-w-2xl text-sm text-pink-500 sm:text-base lg:mx-0">
              A pipeline of adorable-but-serious agents reads papers, scans the news,
              mines repositories, verifies claims and delivers a cited, visualized
              report — with a podcast to go. 🎀
            </p>

            <motion.div
              className="mt-6 text-left"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.15, ease: "easeOut" }}
            >
              <ResearchForm />
            </motion.div>
          </motion.div>

          <motion.div
            className="relative mx-auto hidden max-w-[380px] lg:block"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
          >
            <div className="animate-float">
              <Image
                src="/cute-robot.jpg"
                alt="Cute research robot mascot"
                width={380}
                height={380}
                priority
                className="h-auto w-full rounded-[2.5rem] border-4 border-white object-cover shadow-candy-lg"
              />
            </div>
            <span className="absolute -left-4 top-6 text-3xl animate-sparkle">🌸</span>
            <span className="absolute -right-2 top-16 text-2xl animate-sparkle" style={{ animationDelay: "0.6s" }}>
              ✨
            </span>
            <span className="absolute -bottom-2 -left-2 text-3xl animate-sparkle" style={{ animationDelay: "1s" }}>
              💖
            </span>
            <span className="absolute -bottom-4 right-8 rounded-full border-2 border-pink-200 bg-white/90 px-4 py-1.5 text-xs font-bold text-pink-600 shadow-candy animate-bounce-soft">
              Hi! I&apos;ll research it for you 💕
            </span>
          </motion.div>
        </div>
      </section>

      {/* Feature grid */}
      <section aria-labelledby="features-heading">
        <h2
          id="features-heading"
          className="mb-6 text-center text-sm font-bold uppercase tracking-wider text-pink-500"
        >
          🌷 What every research run includes 🌷
        </h2>
        <motion.div
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
          variants={gridVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
        >
          {FEATURES.map((feature) => (
            <motion.div
              key={feature.title}
              variants={itemVariants}
              whileHover={{ y: -6, rotate: -1 }}
              className="glass rounded-3xl p-5 transition-colors hover:border-pink-400/60"
            >
              <span className="mb-3 flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-pink-200 to-fuchsia-100 border-2 border-pink-200">
                <feature.icon className="h-5 w-5 text-pink-500" aria-hidden="true" />
              </span>
              <h3 className="text-sm font-bold text-pink-700">{feature.title}</h3>
              <p className="mt-1.5 text-xs leading-5 text-pink-500/90">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* History */}
      <HistoryList />
    </div>
  );
}
