import { clearToken, getToken } from "@/lib/auth";
import type {
  ReportFormat,
  ResearchDepth,
  ResearchJob,
  ResearchLanguage,
  StartResearchResponse,
  TokenResponse,
} from "@/lib/types";

const API_ROOT =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") ?? "http://localhost:8000";
const API_BASE = `${API_ROOT}/api/v1`;

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function redirectToLogin(): void {
  if (typeof window !== "undefined" && window.location.pathname !== "/login") {
    window.location.href = "/login";
  }
}

async function extractErrorMessage(res: Response): Promise<string> {
  try {
    const body: unknown = await res.json();
    if (body && typeof body === "object" && "detail" in body) {
      const detail = (body as { detail: unknown }).detail;
      if (typeof detail === "string") return detail;
      if (Array.isArray(detail)) {
        const msgs = detail
          .map((d) =>
            d && typeof d === "object" && "msg" in d
              ? String((d as { msg: unknown }).msg)
              : null
          )
          .filter((m): m is string => m !== null);
        if (msgs.length > 0) return msgs.join("; ");
      }
    }
  } catch {
    // Non-JSON error body; fall through to the generic message.
  }
  return `Request failed with status ${res.status}`;
}

interface RequestOptions {
  method?: "GET" | "POST" | "DELETE";
  body?: unknown;
  /** Attach the Bearer token (default true). */
  auth?: boolean;
  /** On 401, clear the token and bounce to /login (default true when auth). */
  redirectOn401?: boolean;
  signal?: AbortSignal;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = true, redirectOn401 = auth, signal } = options;

  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") throw err;
    throw new ApiError(0, "Cannot reach the ResearchGPT API. Is the backend running?");
  }

  if (res.status === 401 && redirectOn401) {
    clearToken();
    redirectToLogin();
    throw new ApiError(401, "Session expired. Please sign in again.");
  }

  if (!res.ok) {
    throw new ApiError(res.status, await extractErrorMessage(res));
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

/** Fetch a protected binary endpoint and return it as a Blob. */
async function requestBlob(path: string, signal?: AbortSignal): Promise<Blob> {
  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, { headers, signal });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") throw err;
    throw new ApiError(0, "Cannot reach the ResearchGPT API. Is the backend running?");
  }

  if (res.status === 401) {
    clearToken();
    redirectToLogin();
    throw new ApiError(401, "Session expired. Please sign in again.");
  }
  if (!res.ok) {
    throw new ApiError(res.status, await extractErrorMessage(res));
  }
  return res.blob();
}

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

const REPORT_EXTENSIONS: Record<ReportFormat, string> = {
  markdown: "md",
  pdf: "pdf",
  docx: "docx",
  html: "html",
};

export const api = {
  register(email: string, password: string): Promise<TokenResponse> {
    return request<TokenResponse>("/auth/register", {
      method: "POST",
      body: { email, password },
      auth: false,
    });
  },

  login(email: string, password: string): Promise<TokenResponse> {
    return request<TokenResponse>("/auth/login", {
      method: "POST",
      body: { email, password },
      auth: false,
    });
  },

  startResearch(
    topic: string,
    depth: ResearchDepth,
    language: ResearchLanguage
  ): Promise<StartResearchResponse> {
    return request<StartResearchResponse>("/research", {
      method: "POST",
      body: { topic, depth, language },
    });
  },

  getJob(jobId: string, signal?: AbortSignal): Promise<ResearchJob> {
    return request<ResearchJob>(`/research/${encodeURIComponent(jobId)}`, { signal });
  },

  async listJobs(signal?: AbortSignal): Promise<ResearchJob[]> {
    const data = await request<unknown>("/research", { signal });
    if (Array.isArray(data)) return data as ResearchJob[];
    if (data && typeof data === "object" && "jobs" in data) {
      const jobs = (data as { jobs: unknown }).jobs;
      if (Array.isArray(jobs)) return jobs as ResearchJob[];
    }
    return [];
  },

  /** Download the report in the given format (authenticated blob download). */
  async downloadReport(jobId: string, format: ReportFormat): Promise<void> {
    const blob = await requestBlob(
      `/research/${encodeURIComponent(jobId)}/report?format=${format}`
    );
    triggerDownload(blob, `research-${jobId}.${REPORT_EXTENSIONS[format]}`);
  },

  /** Fetch the podcast audio and return an object URL (caller revokes it). */
  async fetchPodcastUrl(jobId: string, language: ResearchLanguage): Promise<string> {
    const blob = await requestBlob(
      `/research/${encodeURIComponent(jobId)}/podcast?language=${language}`
    );
    return URL.createObjectURL(blob);
  },
};
