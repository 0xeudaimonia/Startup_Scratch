"use client";

import { useSearchParams } from "next/navigation";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { dateDaysAgo, fetchCompanies, isoDaysAgo } from "@/lib/api";
import type { CompanyQuery } from "@/lib/types";
import { CompanyFilters } from "@/components/companies/company-filters";
import { CompanyGrid } from "@/components/companies/company-card";
import { CompanyTable } from "@/components/companies/company-table";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Pagination, parsePage } from "@/components/ui/pagination";

export function queryFromSearch(params: URLSearchParams, extra: CompanyQuery = {}): CompanyQuery {
  const query: CompanyQuery = {
    page_size: 24,
    sort: params.get("sort") || extra.sort || "newest_discovered",
    ...extra,
  };
  query.page = parsePage(params.get("page"));
  const search = params.get("search");
  if (search) query.search = search;
  const discovered = params.get("discovered") || (extra.discovered as string | undefined);
  if (discovered) query.discovered_after = isoDaysAgo(Number(discovered));
  const funded = params.get("funded");
  if (funded) query.funded_after = dateDaysAgo(Number(funded));
  const founded = params.get("founded") || (typeof extra.founded === "string" ? extra.founded : undefined);
  if (founded === "2026" || founded === "2025") {
    query.founded_after = `${founded}-01-01`;
    query.founded_before = `${founded}-12-31`;
  } else if (founded && /^(\d+)y$/.test(founded)) {
    const years = Number(founded.slice(0, -1));
    query.founded_after = dateDaysAgo(years * 365);
  }
  delete query.founded;
  for (const key of [
    "funding_stage",
    "remote_policy",
    "industry",
    "technology",
    "investor",
    "employee_range",
    "country",
  ]) {
    const value = params.get(key);
    if (value) query[key] = value;
  }
  if (params.get("is_hiring") === "true") query.is_hiring = true;
  if (params.get("hiring_engineers") === "true") query.hiring_engineers = true;
  if (params.get("has_remote_engineering_jobs") === "true") query.has_remote_engineering_jobs = true;
  if (params.get("employee_max")) query.employee_max = Number(params.get("employee_max"));
  if (params.get("minimum_opportunity_score")) {
    query.minimum_opportunity_score = Number(params.get("minimum_opportunity_score"));
  }
  return query;
}

export function CompanyBrowser({
  title,
  description,
  preset = {},
  hideFilters = false,
}: {
  title: string;
  description: string;
  preset?: CompanyQuery;
  hideFilters?: boolean;
}) {
  const params = useSearchParams();
  const [view, setView] = useState<"cards" | "table">("cards");
  const query = queryFromSearch(params, preset);
  const companies = useQuery({
    queryKey: ["companies", query],
    queryFn: () => fetchCompanies(query),
    placeholderData: keepPreviousData,
  });
  const total = companies.data?.total ?? 0;
  const pageSize = companies.data?.page_size || Number(query.page_size) || 24;
  const page = companies.data?.page || Number(query.page) || 1;
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
        <div className="flex gap-2">
          <Button variant={view === "cards" ? "default" : "outline"} size="sm" onClick={() => setView("cards")}>
            Cards
          </Button>
          <Button variant={view === "table" ? "default" : "outline"} size="sm" onClick={() => setView("table")}>
            Table
          </Button>
        </div>
      </div>
      <div className={hideFilters ? "" : "flex flex-col gap-5 lg:flex-row"}>
        {hideFilters ? null : <CompanyFilters />}
        <div className="min-w-0 flex-1 space-y-4">
          <div className="text-sm text-muted-foreground">
            {companies.isLoading && !companies.data
              ? "Loading companies…"
              : total === 0
                ? "0 companies"
                : `Showing ${from}–${to} of ${total} companies`}
          </div>
          {companies.isLoading && !companies.data ? (
            <div className="rounded-xl border bg-white p-10 text-sm text-muted-foreground">Loading companies…</div>
          ) : companies.isError && !companies.data ? (
            <div className="rounded-xl border border-red-200 bg-red-50 p-10 text-sm text-red-700">
              Could not load companies. {companies.error instanceof Error ? companies.error.message : ""}
            </div>
          ) : (
            <>
              <div className={companies.isFetching ? "opacity-60 transition-opacity" : ""}>
                {view === "table" ? (
                  <CompanyTable companies={companies.data?.items || []} />
                ) : (
                  <CompanyGrid companies={companies.data?.items || []} />
                )}
              </div>
              <Pagination page={page} pageSize={pageSize} total={total} label="Company pagination" />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
