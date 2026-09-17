"use client";

import { Suspense, type ReactNode } from "react";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { fetchJobs } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { JobCheckToggle } from "@/components/checked-toggle";
import { Pagination, parsePage } from "@/components/ui/pagination";
import { cn, formatDate, remoteLabel } from "@/lib/utils";

const PAGE_SIZE = 24;

function StatusChip({
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

function JobsBrowser() {
  const router = useRouter();
  const params = useSearchParams();
  const checked = params.get("checked");
  const query = {
    page: parsePage(params.get("page")),
    page_size: PAGE_SIZE,
    ...(checked === "true" ? { is_checked: true } : {}),
    ...(checked === "false" ? { is_checked: false } : {}),
  };
  const jobs = useQuery({
    queryKey: ["jobs", query],
    queryFn: () => fetchJobs(query),
    placeholderData: keepPreviousData,
  });
  const total = jobs.data?.total ?? 0;
  const pageSize = jobs.data?.page_size || PAGE_SIZE;
  const page = jobs.data?.page || query.page;
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);

  function setChecked(value?: string) {
    const next = new URLSearchParams(params.toString());
    if (!value) next.delete("checked");
    else next.set("checked", value);
    next.delete("page");
    router.push(`?${next.toString()}`);
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Jobs</h1>
        <p className="text-sm text-muted-foreground">
          Open engineering roles discovered across company career pages and directories.
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-1.5">
        <span className="mr-1 text-xs font-semibold uppercase tracking-wide text-slate-400">Check status</span>
        <StatusChip active={!checked} onClick={() => setChecked(undefined)}>
          All
        </StatusChip>
        <StatusChip active={checked === "true"} onClick={() => setChecked("true")}>
          Checked
        </StatusChip>
        <StatusChip active={checked === "false"} onClick={() => setChecked("false")}>
          Unchecked
        </StatusChip>
      </div>
      <div className="text-sm text-muted-foreground">
        {jobs.isLoading && !jobs.data
          ? "Loading jobs…"
          : total === 0
            ? "0 jobs"
            : `Showing ${from}–${to} of ${total} jobs`}
      </div>
      {jobs.isLoading && !jobs.data ? (
        <div className="rounded-xl border bg-white p-10 text-sm text-muted-foreground">Loading jobs…</div>
      ) : jobs.isError && !jobs.data ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-10 text-sm text-red-700">
          Could not load jobs. {jobs.error instanceof Error ? jobs.error.message : ""}
        </div>
      ) : (
        <>
          <div className={`space-y-3 ${jobs.isFetching ? "opacity-60 transition-opacity" : ""}`}>
            {(jobs.data?.items || []).map((job) => (
              <Card key={job.id} className={job.is_checked ? "border-emerald-200 bg-emerald-50/40" : ""}>
                <CardContent className="flex flex-wrap items-center justify-between gap-3 pt-5">
                  <div className="flex items-start gap-3">
                    <JobCheckToggle jobId={job.id} checked={job.is_checked} />
                    <div>
                      <div className="font-medium">{job.title}</div>
                      <div className="text-sm text-muted-foreground">
                        {job.company_slug ? (
                          <Link className="hover:underline" href={`/companies/${job.company_slug}`}>
                            {job.company_name}
                          </Link>
                        ) : (
                          job.company_name
                        )}
                        {job.location ? ` · ${job.location}` : ""}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {job.role_category ? <Badge>{job.role_category}</Badge> : null}
                    {job.remote_type ? <Badge>{remoteLabel(job.remote_type.toUpperCase())}</Badge> : null}
                    <span className="text-xs text-muted-foreground">{formatDate(job.posted_date)}</span>
                    {job.job_url ? (
                      <a className="text-sm text-emerald-700 hover:underline" href={job.job_url} target="_blank" rel="noreferrer">
                        Apply
                      </a>
                    ) : null}
                  </div>
                </CardContent>
              </Card>
            ))}
            {(jobs.data?.items || []).length === 0 ? (
              <div className="rounded-xl border bg-white p-10 text-center text-sm text-muted-foreground">
                No jobs match these filters.
              </div>
            ) : null}
          </div>
          <Pagination page={page} pageSize={pageSize} total={total} label="Job pagination" />
        </>
      )}
    </div>
  );
}

export default function JobsPage() {
  return (
    <Suspense fallback={<div className="text-sm text-muted-foreground">Loading jobs…</div>}>
      <JobsBrowser />
    </Suspense>
  );
}
