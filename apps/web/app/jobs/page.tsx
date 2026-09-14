"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchJobs } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatDate, remoteLabel } from "@/lib/utils";

export default function JobsPage() {
  const jobs = useQuery({ queryKey: ["jobs"], queryFn: () => fetchJobs({ page_size: 50 }) });
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Jobs</h1>
        <p className="text-sm text-muted-foreground">Open engineering roles discovered across company career pages and directories.</p>
      </div>
      <div className="space-y-3">
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
    </div>
  );
}
