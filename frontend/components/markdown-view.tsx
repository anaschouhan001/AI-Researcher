"use client";

import ReactMarkdown from "react-markdown";
import { cn } from "@/lib/utils";

export interface MarkdownViewProps {
  markdown: string;
  className?: string;
}

export function MarkdownView({ markdown, className }: MarkdownViewProps) {
  if (!markdown.trim()) {
    return <p className="text-sm text-pink-400">No report content available.</p>;
  }
  return (
    <div className={cn("markdown-body", className)}>
      <ReactMarkdown
        components={{
          a: ({ href, children, node: _node, ...props }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
              {children}
            </a>
          ),
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}
