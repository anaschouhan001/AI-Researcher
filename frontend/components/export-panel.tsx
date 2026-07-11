"use client";

import { useState } from "react";
import {
  Download,
  FileCode2,
  FileText,
  FileType2,
  Loader2,
  type LucideIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";
import type { ReportFormat } from "@/lib/types";

interface ExportOption {
  format: ReportFormat;
  label: string;
  description: string;
  icon: LucideIcon;
}

const EXPORT_OPTIONS: ExportOption[] = [
  { format: "markdown", label: "Markdown", description: "Plain .md for wikis and repos", icon: FileCode2 },
  { format: "pdf", label: "PDF", description: "Print-ready document", icon: FileText },
  { format: "docx", label: "Word (DOCX)", description: "Editable Microsoft Word file", icon: FileType2 },
  { format: "html", label: "HTML", description: "Standalone web page", icon: FileCode2 },
];

export interface ExportPanelProps {
  jobId: string;
}

export function ExportPanel({ jobId }: ExportPanelProps) {
  const [downloading, setDownloading] = useState<ReportFormat | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleDownload(format: ReportFormat) {
    setDownloading(format);
    setError(null);
    try {
      await api.downloadReport(jobId, format);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : `Could not download the ${format} report. Please try again.`
      );
    } finally {
      setDownloading(null);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <Download className="h-4 w-4 text-pink-400" aria-hidden="true" />
          Export report 💌
        </CardTitle>
        <CardDescription>Download the full research report in your preferred format.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {EXPORT_OPTIONS.map((option) => (
            <div
              key={option.format}
              className="flex flex-col justify-between gap-3 rounded-2xl border-2 border-pink-200 bg-pink-50/70 p-4 transition-transform duration-300 hover:-translate-y-0.5"
            >
              <div>
                <option.icon className="mb-2 h-6 w-6 text-pink-400" aria-hidden="true" />
                <p className="text-sm font-semibold text-pink-800">{option.label}</p>
                <p className="mt-0.5 text-xs text-pink-400">{option.description}</p>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => handleDownload(option.format)}
                disabled={downloading !== null}
              >
                {downloading === option.format ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
                ) : (
                  <Download className="h-3.5 w-3.5" aria-hidden="true" />
                )}
                {downloading === option.format ? "Preparing…" : "Download"}
              </Button>
            </div>
          ))}
        </div>

        {error && (
          <p role="alert" className="mt-4 rounded-2xl border-2 border-rose-300 bg-rose-50 px-3 py-2 text-sm text-rose-600">
            {error}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
