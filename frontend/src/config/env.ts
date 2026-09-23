/**
 * Environment configuration — single source of truth for env vars.
 * Uses Vite's import.meta.env and falls back to sensible dev defaults.
 */
export const env = {
  /** Full base URL of the backend API including the /api prefix, e.g. http://localhost:8000/api */
  VITE_API_URL: (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000/api',
};
