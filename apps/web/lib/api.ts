import type {
  CompanyCard,
  CompanyDetail,
  CompanyQuery,
  Job,
  Paginated,
  SavedView,
  ScrapeRun,
  Source,
  Stats,
} from "./types";

const API_BASE = "/backend/api/v1";

function toParams(query: CompanyQuery = {}) {
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value === undefined || value === "" || value === false) return;
    params.set(key, String(value));
  });
  return params.toString();
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchCompanies(query: CompanyQuery = {}) {
  const qs = toParams(query);
  return get<Paginated<CompanyCard>>(`${API_BASE}/companies${qs ? `?${qs}` : ""}`);
}

export async function fetchCompany(slug: string) {
  return get<CompanyDetail>(`${API_BASE}/companies/${slug}`);
}

export async function fetchJobs(query: CompanyQuery = {}) {
  const qs = toParams(query);
  return get<Paginated<Job>>(`${API_BASE}/jobs${qs ? `?${qs}` : ""}`);
}

export async function fetchStats() {
  return get<Stats>(`${API_BASE}/stats`);
}

export async function fetchSources() {
  return get<Source[]>(`${API_BASE}/sources`);
}

export async function fetchScrapeRuns() {
  return get<ScrapeRun[]>(`${API_BASE}/scrape-runs`);
}

export async function runScraper(source: string) {
  const response = await fetch(`${API_BASE}/scrape-runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source }),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Scrape failed");
  }
  return response.json() as Promise<ScrapeRun>;
}

export async function fetchSavedViews() {
  return get<SavedView[]>(`${API_BASE}/saved-views`);
}

export function isoDaysAgo(days: number) {
  const date = new Date();
  date.setHours(0, 0, 0, 0);
  const offset = Number.isFinite(days) ? days : 0;
  date.setDate(date.getDate() - offset);
  return date.toISOString();
}

export function dateDaysAgo(days: number) {
  const date = new Date();
  const offset = Number.isFinite(days) ? days : 0;
  date.setDate(date.getDate() - offset);
  return date.toISOString().slice(0, 10);
}
