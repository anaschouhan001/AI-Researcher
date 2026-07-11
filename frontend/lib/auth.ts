/** Tiny localStorage-backed JWT store. Safe to import from server components
 *  (every accessor guards on `typeof window`). */

const TOKEN_KEY = "researchgpt_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // Storage may be unavailable (private mode / quota); auth simply won't persist.
  }
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    // ignore
  }
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}
