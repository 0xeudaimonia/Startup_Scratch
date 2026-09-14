import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatMoney(amount?: number | null, currency = "USD") {
  if (amount == null) return "—";
  if (amount >= 1_000_000_000) return `${currency} ${(amount / 1_000_000_000).toFixed(1)}B`;
  if (amount >= 1_000_000) return `${currency} ${(amount / 1_000_000).toFixed(1)}M`;
  if (amount >= 1_000) return `${currency} ${(amount / 1_000).toFixed(0)}K`;
  return `${currency} ${amount}`;
}

export function formatDate(value?: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function remoteLabel(policy?: string | null) {
  const labels: Record<string, string> = {
    GLOBAL_REMOTE: "Global remote",
    REMOTE_FIRST: "Remote first",
    EUROPE_REMOTE: "Europe remote",
    EMEA_REMOTE: "EMEA remote",
    US_REMOTE: "US remote",
    COUNTRY_REMOTE: "Country remote",
    HYBRID: "Hybrid",
    ONSITE: "On-site",
    UNKNOWN: "Unknown",
  };
  return labels[policy || "UNKNOWN"] || policy || "Unknown";
}

export function stageLabel(stage?: string | null) {
  const labels: Record<string, string> = {
    bootstrapped: "Bootstrapped",
    pre_seed: "Pre-Seed",
    seed: "Seed",
    series_a: "Series A",
    series_b: "Series B",
    series_c: "Series C",
    series_d_plus: "Series C+",
    growth: "Growth",
    unknown: "Unknown",
  };
  return labels[stage || "unknown"] || stage || "Unknown";
}

export function scoreTone(score: number) {
  if (score >= 75) return "text-emerald-700 bg-emerald-50 border-emerald-200";
  if (score >= 50) return "text-amber-700 bg-amber-50 border-amber-200";
  return "text-slate-600 bg-slate-50 border-slate-200";
}

export function daysAgo(iso?: string | null) {
  if (!iso) return null;
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 86400000);
  if (diff <= 0) return "Today";
  if (diff === 1) return "Yesterday";
  return `${diff}d ago`;
}
