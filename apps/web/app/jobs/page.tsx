"use client";

import { Suspense } from "react";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { fetchJobs } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Pagination, parsePage } from "@/components/ui/pagination";
import { formatDate, remoteLabel } from "@/lib/utils";

const PAGE_SIZE = 24;

function JobsBrowser() {
  const params = useSearchParams();
  const query = { page: parsePage(params.get("page")), page_size: PAGE_SIZE };
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

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Jobs</h1>
        <p className="text-sm text-muted-foreground">
          Open engineering roles discovered across company career pages and directories.
        </p>
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
              <Card key={job.id}>
                <CardContent className="flex flex-wrap items-center justify-between gap-3 pt-5">
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
