"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { Input } from "@/components/ui/input";
import { fetchSavedViews } from "@/lib/api";
import { cn } from "@/lib/utils";

const DISCOVERED = [
  { label: "Today", value: "0" },
  { label: "7 days", value: "7" },
  { label: "30 days", value: "30" },
];
const FUNDED = [
  { label: "7 days", value: "7" },
  { label: "30 days", value: "30" },
  { label: "90 days", value: "90" },
  { label: "1 year", value: "365" },
];
const STAGES = [
  { label: "Pre-Seed", value: "pre_seed" },
  { label: "Seed", value: "seed" },
  { label: "Series A", value: "series_a" },
  { label: "Series B", value: "series_b" },
  { label: "Series C+", value: "series_c,series_d_plus" },
];
const FOUNDED = [
  { label: "2026", value: "2026" },
  { label: "2025", value: "2025" },
  { label: "Last 1 year", value: "1y" },
  { label: "Last 2 years", value: "2y" },
  { label: "Last 3 years", value: "3y" },
];
const EMPLOYEES = ["1-10", "11-50", "51-100", "101-200", "201-500"];
const REMOTE = [
  { label: "Global Remote", value: "GLOBAL_REMOTE" },
  { label: "Remote First", value: "REMOTE_FIRST" },
  { label: "Europe", value: "EUROPE_REMOTE" },
  { label: "EMEA", value: "EMEA_REMOTE" },
  { label: "US", value: "US_REMOTE" },
  { label: "Hybrid", value: "HYBRID" },
];
const TECH = ["React", "Next.js", "Node.js", "Python", "Rails", "Go", "Rust", "AWS", "AI"];
const INDUSTRIES = ["AI", "Developer Tools", "SaaS", "FinTech", "HealthTech", "Infrastructure", "Security"];

function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full border px-2.5 py-1 text-xs",
        active ? "border-emerald-300 bg-emerald-50 text-emerald-800" : "bg-white text-slate-600 hover:bg-slate-50"
      )}
    >
      {children}
    </button>
  );
}

export function CompanyFilters() {
  const router = useRouter();
  const params = useSearchParams();
  const views = useQuery({ queryKey: ["saved-views"], queryFn: fetchSavedViews });

  function set(key: string, value?: string) {
    const next = new URLSearchParams(params.toString());
    if (!value) next.delete(key);
    else next.set(key, value);
    next.delete("page");
    router.push(`?${next.toString()}`);
  }

  function toggle(key: string, value: string) {
    set(key, params.get(key) === value ? undefined : value);
  }

  return (
    <aside className="w-full shrink-0 space-y-5 rounded-xl border bg-white p-4 lg:w-72">
      <div>
        <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Search</div>
        <Input
          placeholder="Name, domain, tech, investor..."
          defaultValue={params.get("search") || ""}
          onKeyDown={(event) => {
            if (event.key === "Enter") set("search", event.currentTarget.value);
          }}
        />
      </div>
      <div>
        <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Saved views</div>
        <div className="flex flex-col gap-1">
          {(views.data || []).map((view) => (
            <button
              key={view.id}
              className="rounded-md px-2 py-1 text-left text-sm hover:bg-slate-50"
              onClick={() => {
                const next = new URLSearchParams();
                Object.entries(view.filters || {}).forEach(([key, value]) => next.set(key, String(value)));
                router.push(`?${next.toString()}`);
              }}
            >
              {view.name}
            </button>
          ))}
        </div>
      </div>
      <section>
        <h4 className="mb-2 text-xs font-semibold uppercase text-slate-400">Discovered</h4>
        <div className="flex flex-wrap gap-1.5">
          {DISCOVERED.map((item) => (
            <Chip key={item.value} active={params.get("discovered") === item.value} onClick={() => toggle("discovered", item.value)}>
              {item.label}
            </Chip>
          ))}
        </div>
      </section>
      <section>
        <h4 className="mb-2 text-xs font-semibold uppercase text-slate-400">Funding date</h4>
        <div className="flex flex-wrap gap-1.5">
          {FUNDED.map((item) => (
            <Chip key={item.value} active={params.get("funded") === item.value} onClick={() => toggle("funded", item.value)}>
              {item.label}
            </Chip>
          ))}
        </div>
      </section>
      <section>
        <h4 className="mb-2 text-xs font-semibold uppercase text-slate-400">Funding</h4>
        <div className="flex flex-wrap gap-1.5">
          {STAGES.map((item) => (
            <Chip key={item.value} active={params.get("funding_stage") === item.value} onClick={() => toggle("funding_stage", item.value)}>
              {item.label}
            </Chip>
          ))}
        </div>
      </section>
      <section>
        <h4 className="mb-2 text-xs font-semibold uppercase text-slate-400">Founded</h4>
        <div className="flex flex-wrap gap-1.5">
          {FOUNDED.map((item) => (
            <Chip key={item.value} active={params.get("founded") === item.value} onClick={() => toggle("founded", item.value)}>
              {item.label}
            </Chip>
          ))}
        </div>
      </section>
      <section>
        <h4 className="mb-2 text-xs font-semibold uppercase text-slate-400">Employee size</h4>
        <div className="flex flex-wrap gap-1.5">
          {EMPLOYEES.map((item) => (
            <Chip key={item} active={params.get("employee_range") === item} onClick={() => toggle("employee_range", item)}>
              {item}
            </Chip>
          ))}
        </div>
      </section>
      <section>
        <h4 className="mb-2 text-xs font-semibold uppercase text-slate-400">Remote</h4>
        <div className="flex flex-wrap gap-1.5">
          {REMOTE.map((item) => (
            <Chip key={item.value} active={params.get("remote_policy") === item.value} onClick={() => toggle("remote_policy", item.value)}>
              {item.label}
            </Chip>
          ))}
        </div>
      </section>
      <section>
        <h4 className="mb-2 text-xs font-semibold uppercase text-slate-400">Hiring</h4>
        <div className="flex flex-wrap gap-1.5">
          <Chip active={params.get("is_hiring") === "true"} onClick={() => toggle("is_hiring", "true")}>
            Hiring
          </Chip>
          <Chip active={params.get("hiring_engineers") === "true"} onClick={() => toggle("hiring_engineers", "true")}>
            Hiring engineers
          </Chip>
          <Chip
            active={params.get("has_remote_engineering_jobs") === "true"}
            onClick={() => toggle("has_remote_engineering_jobs", "true")}
          >
            Remote eng jobs
          </Chip>
        </div>
      </section>
      <section>
        <h4 className="mb-2 text-xs font-semibold uppercase text-slate-400">Technology</h4>
        <div className="flex flex-wrap gap-1.5">
          {TECH.map((item) => (
            <Chip key={item} active={params.get("technology") === item} onClick={() => toggle("technology", item)}>
              {item}
            </Chip>
          ))}
        </div>
      </section>
      <section>
        <h4 className="mb-2 text-xs font-semibold uppercase text-slate-400">Industry</h4>
        <div className="flex flex-wrap gap-1.5">
          {INDUSTRIES.map((item) => (
            <Chip key={item} active={params.get("industry") === item} onClick={() => toggle("industry", item)}>
              {item}
            </Chip>
          ))}
        </div>
      </section>
      <section>
        <h4 className="mb-2 text-xs font-semibold uppercase text-slate-400">Investor</h4>
        <Input
          placeholder="Sequoia, YC, Accel..."
          defaultValue={params.get("investor") || ""}
          onKeyDown={(event) => {
            if (event.key === "Enter") set("investor", event.currentTarget.value);
          }}
        />
      </section>
    </aside>
  );
}
